"""Level-set topology optimization method."""

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
from scipy import ndimage
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import spsolve


@dataclass
class LevelSetConfig:
    """Configuration for level-set optimization."""

    nelx: int  # Number of elements in x direction
    nely: int  # Number of elements in y direction
    volume_fraction: float = 0.3
    dt: float = 0.5  # Time step for Hamilton-Jacobi evolution
    reinit_interval: int = 5  # Reinitialization interval
    max_iterations: int = 200
    convergence_tolerance: float = 0.01
    youngs_modulus: float = 1.0
    poissons_ratio: float = 0.3
    ersatz_stiffness: float = 1e-3  # Stiffness of void regions


@dataclass
class LevelSetResult:
    """Result of level-set optimization."""

    phi: np.ndarray  # Level-set function
    densities: np.ndarray  # Element densities (derived from phi)
    compliance: float
    volume_fraction: float
    iterations: int
    converged: bool
    convergence_history: List[float]


class LevelSetOptimizer:
    """Level-set topology optimization solver."""

    def __init__(self, config: LevelSetConfig):
        """Initialize level-set optimizer.

        Args:
            config: Level-set configuration parameters
        """
        self.config = config
        self.nelx = config.nelx
        self.nely = config.nely

        # Material properties
        self.E0 = config.youngs_modulus
        self.Emin = config.ersatz_stiffness * self.E0
        self.nu = config.poissons_ratio

        # Initialize level-set function (signed distance to initial shape)
        self.phi = self._initialize_phi()

        # Build element stiffness matrix
        self.KE = self._element_stiffness_matrix()

        # Build DOF connectivity
        self.edofMat = self._build_dof_connectivity()

        # Build sparse stiffness matrix indices
        self.iK, self.jK = self._build_sparse_indices()

    def _initialize_phi(self) -> np.ndarray:
        """Initialize level-set function with circular holes pattern."""
        x = np.linspace(0, self.nelx, self.nelx + 1)
        y = np.linspace(0, self.nely, self.nely + 1)
        X, Y = np.meshgrid(x, y, indexing='ij')

        # Initialize with a pattern of circular holes
        phi = np.ones_like(X)
        
        # Create holes pattern based on volume fraction
        hole_radius = 0.25 * min(self.nelx, self.nely) / 3
        nx_holes = max(1, self.nelx // 20)
        ny_holes = max(1, self.nely // 10)
        
        spacing_x = self.nelx / (nx_holes + 1)
        spacing_y = self.nely / (ny_holes + 1)
        
        for i in range(1, nx_holes + 1):
            for j in range(1, ny_holes + 1):
                cx = i * spacing_x
                cy = j * spacing_y
                dist = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
                phi = np.minimum(phi, dist - hole_radius)

        return phi

    def _heaviside(self, phi: np.ndarray, eps: float = 1.0) -> np.ndarray:
        """Smooth Heaviside function for projection."""
        H = np.zeros_like(phi)
        H[phi > eps] = 1.0
        H[phi < -eps] = 0.0
        mask = np.abs(phi) <= eps
        H[mask] = 0.5 + phi[mask] / (2 * eps) + np.sin(np.pi * phi[mask] / eps) / (2 * np.pi)
        return H

    def _delta(self, phi: np.ndarray, eps: float = 1.0) -> np.ndarray:
        """Smooth delta function (derivative of Heaviside)."""
        delta = np.zeros_like(phi)
        mask = np.abs(phi) <= eps
        delta[mask] = 1 / (2 * eps) + np.cos(np.pi * phi[mask] / eps) / (2 * eps)
        return delta

    def _phi_to_density(self, phi: np.ndarray) -> np.ndarray:
        """Convert level-set function to element densities."""
        # Average nodal values to get element values
        phi_elem = np.zeros((self.nelx, self.nely))
        for i in range(self.nelx):
            for j in range(self.nely):
                phi_elem[i, j] = 0.25 * (
                    phi[i, j] + phi[i + 1, j] + phi[i, j + 1] + phi[i + 1, j + 1]
                )
        
        # Apply Heaviside to get density
        H = self._heaviside(phi_elem)
        return H.flatten()

    def _element_stiffness_matrix(self) -> np.ndarray:
        """Compute element stiffness matrix (plane stress)."""
        E = 1.0
        nu = self.nu
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

    def _build_dof_connectivity(self) -> np.ndarray:
        """Build element DOF connectivity matrix."""
        n_elements = self.nelx * self.nely
        edofMat = np.zeros((n_elements, 8), dtype=int)
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

    def _build_sparse_indices(self) -> Tuple[np.ndarray, np.ndarray]:
        """Build sparse matrix indices for assembly."""
        iK = np.kron(self.edofMat, np.ones((8, 1))).flatten()
        jK = np.kron(self.edofMat, np.ones((1, 8))).flatten()
        return iK.astype(int), jK.astype(int)

    def _assemble_stiffness(self, x: np.ndarray) -> csc_matrix:
        """Assemble global stiffness matrix."""
        ndof = 2 * (self.nelx + 1) * (self.nely + 1)
        sK = (
            (self.Emin + x * (self.E0 - self.Emin)).reshape(-1, 1, 1)
            * self.KE.reshape(1, *self.KE.shape)
        ).flatten()

        K = csc_matrix((sK, (self.iK, self.jK)), shape=(ndof, ndof))
        return K

    def _compute_velocity_field(
        self, phi: np.ndarray, x: np.ndarray, u: np.ndarray, ce: np.ndarray, lagrange: float
    ) -> np.ndarray:
        """Compute velocity field for level-set evolution.

        The velocity is derived from shape sensitivities of the Lagrangian.
        """
        # Shape sensitivity on the interface
        # V_n = -(compliance sensitivity) + lagrange * (volume sensitivity)
        
        # Map element sensitivities to nodes
        velocity = np.zeros((self.nelx + 1, self.nely + 1))
        count = np.zeros((self.nelx + 1, self.nely + 1))
        
        for i in range(self.nelx):
            for j in range(self.nely):
                el = i * self.nely + j
                # Compliance sensitivity
                dc = -(self.E0 - self.Emin) * ce[el]
                # Combined velocity
                v = dc + lagrange
                
                # Distribute to corner nodes
                velocity[i, j] += v
                velocity[i + 1, j] += v
                velocity[i, j + 1] += v
                velocity[i + 1, j + 1] += v
                count[i, j] += 1
                count[i + 1, j] += 1
                count[i, j + 1] += 1
                count[i + 1, j + 1] += 1
        
        velocity = velocity / np.maximum(count, 1)
        
        # Normalize velocity
        max_vel = np.max(np.abs(velocity))
        if max_vel > 1e-10:
            velocity = velocity / max_vel
        
        return velocity

    def _upwind_gradient(self, phi: np.ndarray, velocity: np.ndarray) -> np.ndarray:
        """Compute upwind gradient for Hamilton-Jacobi equation."""
        # Finite difference gradients
        dphi_dx_p = np.zeros_like(phi)
        dphi_dx_m = np.zeros_like(phi)
        dphi_dy_p = np.zeros_like(phi)
        dphi_dy_m = np.zeros_like(phi)
        
        dphi_dx_p[:-1, :] = phi[1:, :] - phi[:-1, :]
        dphi_dx_m[1:, :] = phi[1:, :] - phi[:-1, :]
        dphi_dy_p[:, :-1] = phi[:, 1:] - phi[:, :-1]
        dphi_dy_m[:, 1:] = phi[:, 1:] - phi[:, :-1]
        
        # Upwind scheme - use Godunov approach
        # For positive velocity: use backward differences (dphi_m)
        # For negative velocity: use forward differences (dphi_p)
        grad_sq = np.zeros_like(phi)
        
        # X direction
        grad_sq += np.where(
            velocity >= 0,
            np.maximum(dphi_dx_m, 0) ** 2 + np.minimum(dphi_dx_p, 0) ** 2,
            np.maximum(-dphi_dx_p, 0) ** 2 + np.minimum(-dphi_dx_m, 0) ** 2
        )
        
        # Y direction
        grad_sq += np.where(
            velocity >= 0,
            np.maximum(dphi_dy_m, 0) ** 2 + np.minimum(dphi_dy_p, 0) ** 2,
            np.maximum(-dphi_dy_p, 0) ** 2 + np.minimum(-dphi_dy_m, 0) ** 2
        )
        
        return np.sqrt(grad_sq)

    def _reinitialize(self, phi: np.ndarray, n_iter: int = 5) -> np.ndarray:
        """Reinitialize level-set function to signed distance function."""
        phi0 = phi.copy()
        dt = 0.5
        
        for _ in range(n_iter):
            # Sign function
            sign_phi = phi0 / np.sqrt(phi0 ** 2 + 1e-6)
            
            # Gradients
            dphi_dx = np.zeros_like(phi)
            dphi_dy = np.zeros_like(phi)
            dphi_dx[1:-1, :] = (phi[2:, :] - phi[:-2, :]) / 2
            dphi_dy[:, 1:-1] = (phi[:, 2:] - phi[:, :-2]) / 2
            
            grad_mag = np.sqrt(dphi_dx ** 2 + dphi_dy ** 2 + 1e-10)
            
            # Update
            phi = phi - dt * sign_phi * (grad_mag - 1)
        
        return phi

    def optimize(
        self,
        force: np.ndarray,
        fixed_dofs: np.ndarray,
        callback: Optional[Callable[[int, float, np.ndarray], None]] = None,
    ) -> LevelSetResult:
        """Run level-set topology optimization.

        Args:
            force: Force vector of size (num_dofs,)
            fixed_dofs: Array of fixed DOF indices
            callback: Optional callback function(iteration, compliance, phi)

        Returns:
            LevelSetResult with optimized level-set field
        """
        phi = self.phi.copy()
        ndof = 2 * (self.nelx + 1) * (self.nely + 1)
        n_elements = self.nelx * self.nely
        
        # Free DOFs
        all_dofs = np.arange(ndof)
        free_dofs = np.setdiff1d(all_dofs, fixed_dofs)
        
        convergence_history = []
        loop = 0
        change = 1.0
        
        while change > self.config.convergence_tolerance and loop < self.config.max_iterations:
            loop += 1
            
            # Get densities from level-set
            x = self._phi_to_density(phi)
            
            # Assemble and solve
            K = self._assemble_stiffness(x)
            u = np.zeros(ndof)
            K_ff = K[free_dofs, :][:, free_dofs]
            f_f = force[free_dofs]
            u[free_dofs] = spsolve(K_ff, f_f)
            
            # Compute compliance
            ce = np.zeros(n_elements)
            for el in range(n_elements):
                Ue = u[self.edofMat[el, :]]
                ce[el] = Ue @ self.KE @ Ue
            
            compliance = np.sum((self.Emin + x * (self.E0 - self.Emin)) * ce)
            convergence_history.append(compliance)
            
            # Compute Lagrange multiplier for volume constraint
            current_volume = x.sum() / n_elements
            volume_target = self.config.volume_fraction
            lagrange = 0.0
            
            # Simple bisection to find lagrange multiplier
            if current_volume > volume_target:
                lagrange = 1.0  # Push to remove material
            elif current_volume < volume_target:
                lagrange = -1.0  # Push to add material
            
            # Compute velocity field
            velocity = self._compute_velocity_field(phi, x, u, ce, lagrange)
            
            # Evolve level-set with Hamilton-Jacobi
            grad = self._upwind_gradient(phi, velocity)
            phi_old = phi.copy()
            phi = phi - self.config.dt * velocity * grad
            
            # Reinitialize periodically
            if loop % self.config.reinit_interval == 0:
                phi = self._reinitialize(phi)
            
            # Compute change
            change = np.max(np.abs(phi - phi_old)) / np.max(np.abs(phi) + 1e-10)
            
            if callback:
                callback(loop, compliance, phi)
        
        # Final densities
        x = self._phi_to_density(phi)
        
        return LevelSetResult(
            phi=phi,
            densities=x,
            compliance=convergence_history[-1] if convergence_history else 0,
            volume_fraction=x.sum() / n_elements,
            iterations=loop,
            converged=change <= self.config.convergence_tolerance,
            convergence_history=convergence_history,
        )

    def get_boundary(self, phi: Optional[np.ndarray] = None) -> np.ndarray:
        """Extract zero level-set contour points."""
        if phi is None:
            phi = self.phi
        
        # Find zero crossings
        boundary_points = []
        for i in range(self.nelx):
            for j in range(self.nely):
                # Check each edge for sign change
                corners = [
                    (phi[i, j], i, j),
                    (phi[i + 1, j], i + 1, j),
                    (phi[i + 1, j + 1], i + 1, j + 1),
                    (phi[i, j + 1], i, j + 1),
                ]
                
                for k in range(4):
                    p1 = corners[k]
                    p2 = corners[(k + 1) % 4]
                    
                    if p1[0] * p2[0] < 0:  # Sign change
                        # Linear interpolation
                        t = -p1[0] / (p2[0] - p1[0])
                        x = p1[1] + t * (p2[1] - p1[1])
                        y = p1[2] + t * (p2[2] - p1[2])
                        boundary_points.append([x, y])
        
        return np.array(boundary_points) if boundary_points else np.array([])
