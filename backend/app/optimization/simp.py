"""SIMP (Solid Isotropic Material with Penalization) topology optimization."""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
from scipy import ndimage
from scipy.sparse import csc_matrix, lil_matrix
from scipy.sparse.linalg import spsolve


@dataclass
class SIMPConfig:
    """Configuration for SIMP optimization."""

    nelx: int  # Number of elements in x direction
    nely: int  # Number of elements in y direction
    nelz: int = 1  # Number of elements in z direction (for 3D)
    volume_fraction: float = 0.3
    penalty: float = 3.0
    filter_radius: float = 1.5
    move_limit: float = 0.2
    max_iterations: int = 200
    convergence_tolerance: float = 0.01
    youngs_modulus: float = 1.0
    poissons_ratio: float = 0.3
    min_density: float = 1e-3


@dataclass
class OptimizationResult:
    """Result of topology optimization."""

    densities: np.ndarray
    compliance: float
    volume_fraction: float
    iterations: int
    converged: bool
    convergence_history: List[float]
    constraint_violations: Dict[str, float]


class SIMPOptimizer:
    """SIMP topology optimization solver for 2D and 3D problems."""

    def __init__(self, config: SIMPConfig):
        """Initialize SIMP optimizer.

        Args:
            config: SIMP configuration parameters
        """
        self.config = config
        self.nelx = config.nelx
        self.nely = config.nely
        self.nelz = config.nelz
        self.is_3d = config.nelz > 1

        # Material properties
        self.E0 = config.youngs_modulus
        self.Emin = config.min_density * self.E0
        self.nu = config.poissons_ratio
        self.penal = config.penalty

        # Initialize density field
        self.x = np.ones(self._num_elements) * config.volume_fraction

        # Build filter
        self.H, self.Hs = self._build_filter()

        # Build element stiffness matrix
        self.KE = self._element_stiffness_matrix()

        # Build DOF connectivity
        self.edofMat = self._build_dof_connectivity()

        # Initialize sparse stiffness matrix structure
        self.iK, self.jK = self._build_sparse_indices()

    @property
    def _num_elements(self) -> int:
        """Total number of elements."""
        return self.nelx * self.nely * self.nelz

    @property
    def _num_nodes(self) -> int:
        """Total number of nodes."""
        if self.is_3d:
            return (self.nelx + 1) * (self.nely + 1) * (self.nelz + 1)
        return (self.nelx + 1) * (self.nely + 1)

    @property
    def _num_dofs(self) -> int:
        """Total number of degrees of freedom."""
        if self.is_3d:
            return 3 * self._num_nodes
        return 2 * self._num_nodes

    def _build_filter(self) -> Tuple[np.ndarray, np.ndarray]:
        """Build density filter for mesh-independence."""
        rmin = self.config.filter_radius

        if self.is_3d:
            # 3D filter
            nfilter = int(
                self._num_elements * ((2 * int(np.ceil(rmin)) + 1) ** 3)
            )
            iH = np.zeros(nfilter, dtype=int)
            jH = np.zeros(nfilter, dtype=int)
            sH = np.zeros(nfilter)
            cc = 0

            for k1 in range(self.nelz):
                for i1 in range(self.nelx):
                    for j1 in range(self.nely):
                        e1 = k1 * self.nelx * self.nely + i1 * self.nely + j1
                        for k2 in range(
                            max(k1 - int(np.ceil(rmin)), 0),
                            min(k1 + int(np.ceil(rmin)) + 1, self.nelz),
                        ):
                            for i2 in range(
                                max(i1 - int(np.ceil(rmin)), 0),
                                min(i1 + int(np.ceil(rmin)) + 1, self.nelx),
                            ):
                                for j2 in range(
                                    max(j1 - int(np.ceil(rmin)), 0),
                                    min(j1 + int(np.ceil(rmin)) + 1, self.nely),
                                ):
                                    e2 = (
                                        k2 * self.nelx * self.nely
                                        + i2 * self.nely
                                        + j2
                                    )
                                    dist = np.sqrt(
                                        (i1 - i2) ** 2
                                        + (j1 - j2) ** 2
                                        + (k1 - k2) ** 2
                                    )
                                    if dist < rmin:
                                        iH[cc] = e1
                                        jH[cc] = e2
                                        sH[cc] = rmin - dist
                                        cc += 1

            H = csc_matrix((sH[:cc], (iH[:cc], jH[:cc])))
            Hs = np.array(H.sum(axis=1)).flatten()
        else:
            # 2D filter
            nfilter = int(self._num_elements * ((2 * int(np.ceil(rmin)) + 1) ** 2))
            iH = np.zeros(nfilter, dtype=int)
            jH = np.zeros(nfilter, dtype=int)
            sH = np.zeros(nfilter)
            cc = 0

            for i1 in range(self.nelx):
                for j1 in range(self.nely):
                    e1 = i1 * self.nely + j1
                    for i2 in range(
                        max(i1 - int(np.ceil(rmin)), 0),
                        min(i1 + int(np.ceil(rmin)) + 1, self.nelx),
                    ):
                        for j2 in range(
                            max(j1 - int(np.ceil(rmin)), 0),
                            min(j1 + int(np.ceil(rmin)) + 1, self.nely),
                        ):
                            e2 = i2 * self.nely + j2
                            dist = np.sqrt((i1 - i2) ** 2 + (j1 - j2) ** 2)
                            if dist < rmin:
                                iH[cc] = e1
                                jH[cc] = e2
                                sH[cc] = rmin - dist
                                cc += 1

            H = csc_matrix((sH[:cc], (iH[:cc], jH[:cc])))
            Hs = np.array(H.sum(axis=1)).flatten()

        return H, Hs

    def _element_stiffness_matrix(self) -> np.ndarray:
        """Compute element stiffness matrix."""
        E = 1.0
        nu = self.nu

        if self.is_3d:
            # 3D 8-node hexahedral element
            return self._hex8_stiffness(E, nu)
        else:
            # 2D 4-node quadrilateral element
            return self._quad4_stiffness(E, nu)

    def _quad4_stiffness(self, E: float, nu: float) -> np.ndarray:
        """4-node quadrilateral element stiffness matrix (plane stress)."""
        k = [
            1 / 2 - nu / 6,
            1 / 8 + nu / 8,
            -1 / 4 - nu / 12,
            -1 / 8 + 3 * nu / 8,
            -1 / 4 + nu / 12,
            -1 / 8 - nu / 8,
            nu / 6,
            1 / 8 - 3 * nu / 8,
        ]
        KE = (
            E
            / (1 - nu ** 2)
            * np.array(
                [
                    [k[0], k[1], k[2], k[3], k[4], k[5], k[6], k[7]],
                    [k[1], k[0], k[7], k[6], k[5], k[4], k[3], k[2]],
                    [k[2], k[7], k[0], k[5], k[6], k[3], k[4], k[1]],
                    [k[3], k[6], k[5], k[0], k[7], k[2], k[1], k[4]],
                    [k[4], k[5], k[6], k[7], k[0], k[1], k[2], k[3]],
                    [k[5], k[4], k[3], k[2], k[1], k[0], k[7], k[6]],
                    [k[6], k[3], k[4], k[1], k[2], k[7], k[0], k[5]],
                    [k[7], k[2], k[1], k[4], k[3], k[6], k[5], k[0]],
                ]
            )
        )
        return KE

    def _hex8_stiffness(self, E: float, nu: float) -> np.ndarray:
        """8-node hexahedral element stiffness matrix (simplified)."""
        # Using numerical integration with 2x2x2 Gauss points
        # This is a simplified version - full implementation would use shape functions
        a = E * (1 - nu) / ((1 + nu) * (1 - 2 * nu))
        b = E * nu / ((1 + nu) * (1 - 2 * nu))
        c = E / (2 * (1 + nu))

        # Constitutive matrix
        D = np.array(
            [
                [a, b, b, 0, 0, 0],
                [b, a, b, 0, 0, 0],
                [b, b, a, 0, 0, 0],
                [0, 0, 0, c, 0, 0],
                [0, 0, 0, 0, c, 0],
                [0, 0, 0, 0, 0, c],
            ]
        )

        # Simplified 24x24 stiffness matrix (using 2-point Gauss integration)
        KE = np.zeros((24, 24))
        gp = 1.0 / np.sqrt(3.0)
        gauss_points = [-gp, gp]
        weights = [1.0, 1.0]

        for i, xi in enumerate(gauss_points):
            for j, eta in enumerate(gauss_points):
                for k, zeta in enumerate(gauss_points):
                    B = self._strain_displacement_matrix(xi, eta, zeta)
                    w = weights[i] * weights[j] * weights[k]
                    KE += w * (B.T @ D @ B)

        return KE

    def _strain_displacement_matrix(
        self, xi: float, eta: float, zeta: float
    ) -> np.ndarray:
        """Compute strain-displacement matrix for hex8 element at natural coordinates."""
        # Shape function derivatives
        dN_dxi = np.array(
            [
                [
                    -(1 - eta) * (1 - zeta),
                    (1 - eta) * (1 - zeta),
                    (1 + eta) * (1 - zeta),
                    -(1 + eta) * (1 - zeta),
                    -(1 - eta) * (1 + zeta),
                    (1 - eta) * (1 + zeta),
                    (1 + eta) * (1 + zeta),
                    -(1 + eta) * (1 + zeta),
                ],
                [
                    -(1 - xi) * (1 - zeta),
                    -(1 + xi) * (1 - zeta),
                    (1 + xi) * (1 - zeta),
                    (1 - xi) * (1 - zeta),
                    -(1 - xi) * (1 + zeta),
                    -(1 + xi) * (1 + zeta),
                    (1 + xi) * (1 + zeta),
                    (1 - xi) * (1 + zeta),
                ],
                [
                    -(1 - xi) * (1 - eta),
                    -(1 + xi) * (1 - eta),
                    -(1 + xi) * (1 + eta),
                    -(1 - xi) * (1 + eta),
                    (1 - xi) * (1 - eta),
                    (1 + xi) * (1 - eta),
                    (1 + xi) * (1 + eta),
                    (1 - xi) * (1 + eta),
                ],
            ]
        ) / 8.0

        # Jacobian (assuming unit cube element)
        J = np.eye(3) * 0.5

        # Derivatives in physical coordinates
        dN_dx = np.linalg.inv(J) @ dN_dxi

        # Build B matrix
        B = np.zeros((6, 24))
        for node in range(8):
            B[0, 3 * node] = dN_dx[0, node]
            B[1, 3 * node + 1] = dN_dx[1, node]
            B[2, 3 * node + 2] = dN_dx[2, node]
            B[3, 3 * node] = dN_dx[1, node]
            B[3, 3 * node + 1] = dN_dx[0, node]
            B[4, 3 * node + 1] = dN_dx[2, node]
            B[4, 3 * node + 2] = dN_dx[1, node]
            B[5, 3 * node] = dN_dx[2, node]
            B[5, 3 * node + 2] = dN_dx[0, node]

        return B

    def _build_dof_connectivity(self) -> np.ndarray:
        """Build element DOF connectivity matrix."""
        if self.is_3d:
            return self._build_dof_connectivity_3d()
        return self._build_dof_connectivity_2d()

    def _build_dof_connectivity_2d(self) -> np.ndarray:
        """Build 2D element DOF connectivity."""
        edofMat = np.zeros((self._num_elements, 8), dtype=int)
        for elx in range(self.nelx):
            for ely in range(self.nely):
                el = elx * self.nely + ely
                n1 = (self.nely + 1) * elx + ely
                n2 = (self.nely + 1) * (elx + 1) + ely
                edofMat[el, :] = np.array(
                    [
                        2 * n1,
                        2 * n1 + 1,
                        2 * n2,
                        2 * n2 + 1,
                        2 * n2 + 2,
                        2 * n2 + 3,
                        2 * n1 + 2,
                        2 * n1 + 3,
                    ]
                )
        return edofMat

    def _build_dof_connectivity_3d(self) -> np.ndarray:
        """Build 3D element DOF connectivity."""
        edofMat = np.zeros((self._num_elements, 24), dtype=int)
        for elz in range(self.nelz):
            for elx in range(self.nelx):
                for ely in range(self.nely):
                    el = (
                        elz * self.nelx * self.nely + elx * self.nely + ely
                    )
                    # Node numbering for hex8 element
                    n1 = (
                        elz * (self.nelx + 1) * (self.nely + 1)
                        + elx * (self.nely + 1)
                        + ely
                    )
                    n2 = n1 + (self.nely + 1)
                    n3 = n2 + 1
                    n4 = n1 + 1
                    n5 = n1 + (self.nelx + 1) * (self.nely + 1)
                    n6 = n5 + (self.nely + 1)
                    n7 = n6 + 1
                    n8 = n5 + 1

                    nodes = [n1, n2, n3, n4, n5, n6, n7, n8]
                    dofs = []
                    for n in nodes:
                        dofs.extend([3 * n, 3 * n + 1, 3 * n + 2])
                    edofMat[el, :] = dofs

        return edofMat

    def _build_sparse_indices(self) -> Tuple[np.ndarray, np.ndarray]:
        """Build sparse matrix indices for assembly."""
        dofs_per_element = 24 if self.is_3d else 8
        iK = np.kron(self.edofMat, np.ones((dofs_per_element, 1))).flatten()
        jK = np.kron(self.edofMat, np.ones((1, dofs_per_element))).flatten()
        return iK.astype(int), jK.astype(int)

    def _assemble_stiffness(self, x: np.ndarray) -> csc_matrix:
        """Assemble global stiffness matrix."""
        sK = (
            (self.Emin + x ** self.penal * (self.E0 - self.Emin))
            .reshape(-1, 1, 1)
            * self.KE.reshape(1, *self.KE.shape)
        ).flatten()

        K = csc_matrix(
            (sK, (self.iK, self.jK)), shape=(self._num_dofs, self._num_dofs)
        )
        return K

    def optimize(
        self,
        force: np.ndarray,
        fixed_dofs: np.ndarray,
        callback: Optional[Callable[[int, float, np.ndarray], None]] = None,
    ) -> OptimizationResult:
        """Run SIMP topology optimization.

        Args:
            force: Force vector of size (num_dofs,)
            fixed_dofs: Array of fixed DOF indices
            callback: Optional callback function(iteration, compliance, densities)

        Returns:
            OptimizationResult with optimized density field
        """
        x = self.x.copy()
        xold = x.copy()
        xPhys = x.copy()
        convergence_history = []

        # Free DOFs
        all_dofs = np.arange(self._num_dofs)
        free_dofs = np.setdiff1d(all_dofs, fixed_dofs)

        loop = 0
        change = 1.0

        while change > self.config.convergence_tolerance and loop < self.config.max_iterations:
            loop += 1

            # Apply density filter
            xPhys = np.array(
                (self.H @ x.reshape(-1, 1)) / self.Hs.reshape(-1, 1)
            ).flatten()

            # Assemble stiffness matrix
            K = self._assemble_stiffness(xPhys)

            # Solve system
            u = np.zeros(self._num_dofs)
            K_ff = K[free_dofs, :][:, free_dofs]
            f_f = force[free_dofs]
            u[free_dofs] = spsolve(K_ff, f_f)

            # Compute compliance
            ce = np.zeros(self._num_elements)
            for el in range(self._num_elements):
                Ue = u[self.edofMat[el, :]]
                ce[el] = Ue @ self.KE @ Ue

            compliance = np.sum(
                (self.Emin + xPhys ** self.penal * (self.E0 - self.Emin)) * ce
            )
            convergence_history.append(compliance)

            # Compute sensitivities
            dc = (
                -self.penal
                * (self.E0 - self.Emin)
                * xPhys ** (self.penal - 1)
                * ce
            )
            dv = np.ones(self._num_elements)

            # Filter sensitivities
            dc = np.array(
                self.H @ (dc.reshape(-1, 1) / self.Hs.reshape(-1, 1))
            ).flatten()
            dv = np.array(
                self.H @ (dv.reshape(-1, 1) / self.Hs.reshape(-1, 1))
            ).flatten()

            # Optimality criteria update
            l1, l2 = 0, 1e9
            move = self.config.move_limit
            xnew = x.copy()

            while (l2 - l1) / (l1 + l2) > 1e-3:
                lmid = 0.5 * (l2 + l1)
                xnew = np.maximum(
                    self.config.min_density,
                    np.maximum(
                        x - move,
                        np.minimum(
                            1.0,
                            np.minimum(
                                x + move,
                                x * np.sqrt(-dc / dv / lmid),
                            ),
                        ),
                    ),
                )
                xPhys_new = np.array(
                    (self.H @ xnew.reshape(-1, 1)) / self.Hs.reshape(-1, 1)
                ).flatten()

                if xPhys_new.sum() > self.config.volume_fraction * self._num_elements:
                    l1 = lmid
                else:
                    l2 = lmid

            change = np.max(np.abs(xnew - x))
            x = xnew.copy()

            if callback:
                callback(loop, compliance, xPhys)

        # Final filtered densities
        xPhys = np.array(
            (self.H @ x.reshape(-1, 1)) / self.Hs.reshape(-1, 1)
        ).flatten()

        return OptimizationResult(
            densities=xPhys,
            compliance=convergence_history[-1] if convergence_history else 0,
            volume_fraction=xPhys.sum() / self._num_elements,
            iterations=loop,
            converged=change <= self.config.convergence_tolerance,
            convergence_history=convergence_history,
            constraint_violations={},
        )

    def get_density_field(self) -> np.ndarray:
        """Get current density field reshaped to grid."""
        if self.is_3d:
            return self.x.reshape(self.nelz, self.nelx, self.nely)
        return self.x.reshape(self.nelx, self.nely)


def create_cantilever_problem(
    nelx: int = 60, nely: int = 30, volume_fraction: float = 0.4
) -> Tuple[SIMPOptimizer, np.ndarray, np.ndarray]:
    """Create a standard cantilever beam optimization problem.

    Args:
        nelx: Number of elements in x
        nely: Number of elements in y
        volume_fraction: Target volume fraction

    Returns:
        Tuple of (optimizer, force_vector, fixed_dofs)
    """
    config = SIMPConfig(
        nelx=nelx,
        nely=nely,
        volume_fraction=volume_fraction,
    )
    optimizer = SIMPOptimizer(config)

    # Force at middle-right
    ndof = 2 * (nelx + 1) * (nely + 1)
    force = np.zeros(ndof)
    force[2 * (nelx + 1) * (nely + 1) - nely - 1] = -1.0

    # Fixed left edge
    fixed_dofs = np.array(
        [2 * i for i in range(nely + 1)] + [2 * i + 1 for i in range(nely + 1)]
    )

    return optimizer, force, fixed_dofs
