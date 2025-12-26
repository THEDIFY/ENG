"""Orthotropic laminate model for composite materials."""

from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np


@dataclass
class Ply:
    """Single ply definition."""

    material_name: str
    angle: float  # degrees
    thickness: float  # mm

    # Orthotropic elastic properties
    e1: float  # Longitudinal modulus (GPa)
    e2: float  # Transverse modulus (GPa)
    g12: float  # In-plane shear modulus (GPa)
    nu12: float  # In-plane Poisson's ratio

    # Strength properties (MPa)
    xt: float = 1500.0  # Longitudinal tensile strength
    xc: float = 1200.0  # Longitudinal compressive strength
    yt: float = 50.0  # Transverse tensile strength
    yc: float = 200.0  # Transverse compressive strength
    s12: float = 70.0  # In-plane shear strength


@dataclass
class LaminateResult:
    """Result of laminate analysis."""

    ABD: np.ndarray  # 6x6 ABD matrix
    abd_inv: np.ndarray  # Inverse ABD matrix
    Ex: float  # Effective longitudinal modulus
    Ey: float  # Effective transverse modulus
    Gxy: float  # Effective shear modulus
    nu_xy: float  # Effective Poisson's ratio
    total_thickness: float
    ply_stresses: Optional[List[np.ndarray]] = None
    ply_strains: Optional[List[np.ndarray]] = None
    failure_indices: Optional[List[float]] = None


class LaminateAnalyzer:
    """Classical Laminate Theory (CLT) analyzer for orthotropic composites."""

    def __init__(self, plies: List[Ply]):
        """Initialize laminate analyzer.

        Args:
            plies: List of plies from bottom to top
        """
        self.plies = plies
        self.total_thickness = sum(p.thickness for p in plies)
        self.z_coords = self._compute_z_coordinates()

    def _compute_z_coordinates(self) -> List[float]:
        """Compute z-coordinates of ply interfaces from midplane."""
        z = [-self.total_thickness / 2]
        for ply in self.plies:
            z.append(z[-1] + ply.thickness)
        return z

    def _rotation_matrix(self, angle_deg: float) -> np.ndarray:
        """Compute stress transformation matrix for rotation."""
        theta = np.radians(angle_deg)
        c = np.cos(theta)
        s = np.sin(theta)

        T = np.array(
            [
                [c ** 2, s ** 2, 2 * c * s],
                [s ** 2, c ** 2, -2 * c * s],
                [-c * s, c * s, c ** 2 - s ** 2],
            ]
        )
        return T

    def _rotation_matrix_strain(self, angle_deg: float) -> np.ndarray:
        """Compute strain transformation matrix for rotation."""
        theta = np.radians(angle_deg)
        c = np.cos(theta)
        s = np.sin(theta)

        T = np.array(
            [
                [c ** 2, s ** 2, c * s],
                [s ** 2, c ** 2, -c * s],
                [-2 * c * s, 2 * c * s, c ** 2 - s ** 2],
            ]
        )
        return T

    def _ply_stiffness_local(self, ply: Ply) -> np.ndarray:
        """Compute ply stiffness matrix in local coordinates (Q)."""
        E1 = ply.e1 * 1e3  # Convert GPa to MPa
        E2 = ply.e2 * 1e3
        G12 = ply.g12 * 1e3
        nu12 = ply.nu12
        nu21 = nu12 * E2 / E1

        denom = 1 - nu12 * nu21

        Q = np.array(
            [
                [E1 / denom, nu12 * E2 / denom, 0],
                [nu12 * E2 / denom, E2 / denom, 0],
                [0, 0, G12],
            ]
        )
        return Q

    def _ply_stiffness_global(self, ply: Ply) -> np.ndarray:
        """Compute ply stiffness matrix in global coordinates (Q_bar)."""
        Q = self._ply_stiffness_local(ply)
        T = self._rotation_matrix(ply.angle)
        T_inv = np.linalg.inv(T)
        
        # Reuter matrix for engineering strain conversion
        R = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 2]])
        R_inv = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 0.5]])

        Q_bar = T_inv @ Q @ R_inv @ T @ R
        return Q_bar

    def compute_abd_matrix(self) -> np.ndarray:
        """Compute the ABD stiffness matrix."""
        A = np.zeros((3, 3))
        B = np.zeros((3, 3))
        D = np.zeros((3, 3))

        for i, ply in enumerate(self.plies):
            Q_bar = self._ply_stiffness_global(ply)
            z_k = self.z_coords[i + 1]
            z_k_1 = self.z_coords[i]

            A += Q_bar * (z_k - z_k_1)
            B += Q_bar * (z_k ** 2 - z_k_1 ** 2) / 2
            D += Q_bar * (z_k ** 3 - z_k_1 ** 3) / 3

        # Assemble ABD matrix
        ABD = np.zeros((6, 6))
        ABD[:3, :3] = A
        ABD[:3, 3:] = B
        ABD[3:, :3] = B
        ABD[3:, 3:] = D

        return ABD

    def compute_effective_properties(self) -> LaminateResult:
        """Compute effective engineering properties of the laminate."""
        ABD = self.compute_abd_matrix()
        
        try:
            abd_inv = np.linalg.inv(ABD)
        except np.linalg.LinAlgError:
            # Singular matrix - return defaults
            return LaminateResult(
                ABD=ABD,
                abd_inv=np.zeros_like(ABD),
                Ex=0,
                Ey=0,
                Gxy=0,
                nu_xy=0,
                total_thickness=self.total_thickness,
            )

        h = self.total_thickness

        # Extensional stiffness inverse
        a = abd_inv[:3, :3]

        # Effective moduli
        Ex = 1 / (h * a[0, 0]) if a[0, 0] != 0 else 0
        Ey = 1 / (h * a[1, 1]) if a[1, 1] != 0 else 0
        Gxy = 1 / (h * a[2, 2]) if a[2, 2] != 0 else 0
        nu_xy = -a[0, 1] / a[0, 0] if a[0, 0] != 0 else 0

        return LaminateResult(
            ABD=ABD,
            abd_inv=abd_inv,
            Ex=Ex / 1e3,  # Convert back to GPa
            Ey=Ey / 1e3,
            Gxy=Gxy / 1e3,
            nu_xy=nu_xy,
            total_thickness=h,
        )

    def analyze_stress(
        self, 
        Nx: float = 0, Ny: float = 0, Nxy: float = 0,
        Mx: float = 0, My: float = 0, Mxy: float = 0
    ) -> LaminateResult:
        """Analyze laminate under given loads.

        Args:
            Nx, Ny, Nxy: In-plane force resultants (N/mm)
            Mx, My, Mxy: Moment resultants (N)

        Returns:
            LaminateResult with ply stresses and failure indices
        """
        result = self.compute_effective_properties()
        
        # Load vector
        N = np.array([Nx, Ny, Nxy, Mx, My, Mxy])
        
        # Mid-plane strains and curvatures
        eps_kappa = result.abd_inv @ N
        eps0 = eps_kappa[:3]  # Mid-plane strains
        kappa = eps_kappa[3:]  # Curvatures

        ply_stresses = []
        ply_strains = []
        failure_indices = []

        for i, ply in enumerate(self.plies):
            # Z-coordinate at ply mid-plane
            z_mid = (self.z_coords[i] + self.z_coords[i + 1]) / 2

            # Strain at ply mid-plane (global coordinates)
            eps_global = eps0 + z_mid * kappa

            # Transform to local coordinates
            T_strain = self._rotation_matrix_strain(ply.angle)
            eps_local = T_strain @ eps_global

            # Stress in local coordinates
            Q_local = self._ply_stiffness_local(ply)
            sigma_local = Q_local @ eps_local

            ply_strains.append(eps_local)
            ply_stresses.append(sigma_local)

            # Failure index using Tsai-Hill criterion
            sigma_1, sigma_2, tau_12 = sigma_local

            # Select appropriate strength based on sign
            X = ply.xt if sigma_1 >= 0 else ply.xc
            Y = ply.yt if sigma_2 >= 0 else ply.yc
            S = ply.s12

            # Tsai-Hill failure index
            FI = (
                (sigma_1 / X) ** 2
                - (sigma_1 * sigma_2) / (X ** 2)
                + (sigma_2 / Y) ** 2
                + (tau_12 / S) ** 2
            )
            failure_indices.append(np.sqrt(FI))

        result.ply_stresses = ply_stresses
        result.ply_strains = ply_strains
        result.failure_indices = failure_indices

        return result

    def check_ply_rules(self) -> List[Tuple[str, bool, str]]:
        """Check laminate against standard manufacturing rules.

        Returns:
            List of (rule_name, passed, message) tuples
        """
        checks = []

        # Check 1: Symmetry
        n = len(self.plies)
        is_symmetric = True
        for i in range(n // 2):
            if abs(self.plies[i].angle - self.plies[n - 1 - i].angle) > 0.1:
                is_symmetric = False
                break
        checks.append(
            ("Symmetry", is_symmetric, 
             "Laminate is symmetric" if is_symmetric else "Laminate is NOT symmetric")
        )

        # Check 2: Balance (equal +θ and -θ plies)
        angle_counts = {}
        for ply in self.plies:
            angle = ply.angle % 180
            if angle not in [0, 90]:
                angle_counts[angle] = angle_counts.get(angle, 0) + 1
                angle_counts[180 - angle] = angle_counts.get(180 - angle, 0) + 1

        is_balanced = all(
            angle_counts.get(a, 0) == angle_counts.get(180 - a, 0)
            for a in angle_counts.keys()
            if a < 90
        )
        checks.append(
            ("Balance", is_balanced,
             "Laminate is balanced" if is_balanced else "Laminate is NOT balanced")
        )

        # Check 3: Maximum consecutive same-angle plies
        max_consecutive = 1
        current_consecutive = 1
        for i in range(1, len(self.plies)):
            if abs(self.plies[i].angle - self.plies[i - 1].angle) < 0.1:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 1

        max_allowed = 4
        consecutive_ok = max_consecutive <= max_allowed
        checks.append(
            ("Max Consecutive Plies", consecutive_ok,
             f"Max consecutive same-angle plies: {max_consecutive} (limit: {max_allowed})")
        )

        # Check 4: 10% rule (at least 10% in each direction)
        angle_fractions = {}
        total_thickness = self.total_thickness
        for ply in self.plies:
            angle = ply.angle % 180
            # Group angles: 0, 90, +45/-45
            if angle < 10 or angle > 170:
                key = "0"
            elif 80 < angle < 100:
                key = "90"
            else:
                key = "45"
            angle_fractions[key] = angle_fractions.get(key, 0) + ply.thickness

        min_fraction = 0.10
        ten_percent_ok = all(
            angle_fractions.get(d, 0) / total_thickness >= min_fraction
            for d in ["0", "90", "45"]
        )
        fractions_str = ", ".join(
            f"{d}°: {angle_fractions.get(d, 0) / total_thickness * 100:.1f}%"
            for d in ["0", "90", "45"]
        )
        checks.append(
            ("10% Rule", ten_percent_ok,
             f"Angle fractions - {fractions_str}")
        )

        return checks


def create_quasi_isotropic_layup(
    material_name: str,
    ply_thickness: float,
    n_sets: int = 2,
    e1: float = 135.0,
    e2: float = 10.0,
    g12: float = 5.0,
    nu12: float = 0.27,
) -> List[Ply]:
    """Create a quasi-isotropic layup [0/45/-45/90]ns.

    Args:
        material_name: Name of material
        ply_thickness: Individual ply thickness (mm)
        n_sets: Number of [0/45/-45/90] sets (will be symmetric)
        e1, e2, g12, nu12: Material properties

    Returns:
        List of plies for a symmetric, balanced quasi-isotropic laminate
    """
    angles = [0, 45, -45, 90]
    plies = []

    # Build first half
    for _ in range(n_sets):
        for angle in angles:
            plies.append(
                Ply(
                    material_name=material_name,
                    angle=angle,
                    thickness=ply_thickness,
                    e1=e1,
                    e2=e2,
                    g12=g12,
                    nu12=nu12,
                )
            )

    # Add symmetric half
    for ply in reversed(plies):
        plies.append(
            Ply(
                material_name=ply.material_name,
                angle=ply.angle,
                thickness=ply.thickness,
                e1=ply.e1,
                e2=ply.e2,
                g12=ply.g12,
                nu12=ply.nu12,
            )
        )

    return plies
