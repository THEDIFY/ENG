"""FE Solver interface for structural analysis."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from app.fe_solver.mesh import Mesh


class AnalysisType(str, Enum):
    """Type of FE analysis."""

    STATIC = "static"
    MODAL = "modal"
    TRANSIENT = "transient"
    BUCKLING = "buckling"


@dataclass
class MaterialProperties:
    """Material properties for FE analysis."""

    name: str
    youngs_modulus: float  # MPa
    poissons_ratio: float
    density: float  # kg/m³
    
    # For orthotropic materials
    is_orthotropic: bool = False
    e1: Optional[float] = None
    e2: Optional[float] = None
    e3: Optional[float] = None
    g12: Optional[float] = None
    g13: Optional[float] = None
    g23: Optional[float] = None
    nu12: Optional[float] = None
    nu13: Optional[float] = None
    nu23: Optional[float] = None


@dataclass
class LoadCase:
    """Load case definition."""

    name: str
    forces: List[Dict[str, Any]]  # List of force definitions
    pressures: List[Dict[str, Any]] = None
    accelerations: List[float] = None  # Body accelerations [ax, ay, az]
    thermal_load: Optional[float] = None  # Temperature change


@dataclass
class Constraint:
    """Boundary constraint definition."""

    name: str
    node_set: str  # Name of node set
    dofs: List[int]  # Constrained DOFs (1-6)
    values: Optional[List[float]] = None  # Prescribed values (None = fixed at 0)


@dataclass
class FEResult:
    """Result of FE analysis."""

    analysis_type: AnalysisType
    displacements: Optional[np.ndarray] = None
    stresses: Optional[np.ndarray] = None
    strains: Optional[np.ndarray] = None
    reaction_forces: Optional[np.ndarray] = None
    eigenvalues: Optional[np.ndarray] = None
    eigenvectors: Optional[np.ndarray] = None
    max_displacement: float = 0
    max_stress: float = 0
    max_strain: float = 0
    safety_factor: float = 0
    modal_frequencies: Optional[List[float]] = None
    compliance: float = 0


class FESolver:
    """FE solver interface (mock implementation for demo).
    
    In production, this would interface with FEniCS or CalculiX.
    """

    def __init__(self, solver_type: str = "internal"):
        """Initialize FE solver.

        Args:
            solver_type: 'internal', 'fenics', or 'calculix'
        """
        self.solver_type = solver_type
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the solver."""
        if self.solver_type == "fenics":
            self._init_fenics()
        elif self.solver_type == "calculix":
            self._init_calculix()
        self._initialized = True

    def _init_fenics(self) -> None:
        """Initialize FEniCS solver."""
        try:
            import dolfinx
            self._fenics_available = True
        except ImportError:
            self._fenics_available = False

    def _init_calculix(self) -> None:
        """Initialize CalculiX solver."""
        # Check if ccx is available in PATH
        import shutil
        self._calculix_available = shutil.which("ccx") is not None

    def solve_static(
        self,
        mesh: Mesh,
        material: MaterialProperties,
        load_cases: List[LoadCase],
        constraints: List[Constraint],
    ) -> FEResult:
        """Solve static structural analysis.

        Args:
            mesh: FE mesh
            material: Material properties
            load_cases: List of load cases
            constraints: Boundary constraints

        Returns:
            FEResult with displacements, stresses, etc.
        """
        n_nodes = len(mesh.nodes)
        n_elements = len(mesh.elements)

        # Mock implementation - in production would use actual FE solver
        # Simulate results based on simple beam theory approximations

        # Estimate compliance (simplified)
        E = material.youngs_modulus
        
        # Approximate max displacement (very simplified)
        # Assuming a loaded beam-like structure
        total_force = 0
        for lc in load_cases:
            for force in lc.forces:
                total_force += abs(force.get("magnitude", 0))

        # Rough estimate using beam formula
        L = np.max(mesh.nodes[:, 0]) - np.min(mesh.nodes[:, 0])
        I = (np.max(mesh.nodes[:, 1]) - np.min(mesh.nodes[:, 1])) ** 4 / 12
        
        if E > 0 and I > 0:
            max_disp = (total_force * L ** 3) / (48 * E * I) if total_force > 0 else 0
        else:
            max_disp = 0

        # Simulate displacement field
        displacements = np.random.randn(n_nodes, 3) * max_disp * 0.1
        displacements = np.clip(displacements, -max_disp, max_disp)

        # Stress estimation (von Mises)
        max_stress = (total_force * L) / (2 * I) if I > 0 else 0
        stresses = np.random.rand(n_elements) * max_stress

        # Strain
        strains = stresses / E if E > 0 else np.zeros_like(stresses)

        # Safety factor (assuming yield strength ~ 0.6 * E * 0.001 for demo)
        yield_strength = 500  # MPa typical for carbon fiber
        safety_factor = yield_strength / max_stress if max_stress > 0 else 10

        # Compliance
        compliance = np.sum(displacements ** 2) * total_force if total_force > 0 else 0

        return FEResult(
            analysis_type=AnalysisType.STATIC,
            displacements=displacements,
            stresses=stresses,
            strains=strains,
            max_displacement=float(np.max(np.abs(displacements))),
            max_stress=float(np.max(stresses)),
            max_strain=float(np.max(strains)),
            safety_factor=safety_factor,
            compliance=compliance,
        )

    def solve_modal(
        self,
        mesh: Mesh,
        material: MaterialProperties,
        constraints: List[Constraint],
        n_modes: int = 10,
    ) -> FEResult:
        """Solve modal analysis for natural frequencies.

        Args:
            mesh: FE mesh
            material: Material properties
            constraints: Boundary constraints
            n_modes: Number of modes to compute

        Returns:
            FEResult with eigenvalues and eigenvectors
        """
        n_nodes = len(mesh.nodes)

        # Mock implementation
        # Estimate natural frequencies using simplified beam theory
        E = material.youngs_modulus * 1e6  # Convert to Pa
        rho = material.density
        
        L = np.max(mesh.nodes[:, 0]) - np.min(mesh.nodes[:, 0])
        W = np.max(mesh.nodes[:, 1]) - np.min(mesh.nodes[:, 1])
        H = np.max(mesh.nodes[:, 2]) - np.min(mesh.nodes[:, 2])

        I = W * H ** 3 / 12
        A = W * H

        # First bending mode frequency estimate
        if E > 0 and rho > 0 and I > 0 and A > 0 and L > 0:
            f1 = (np.pi / (2 * L ** 2)) * np.sqrt(E * I / (rho * A))
        else:
            f1 = 100  # Default Hz

        # Generate mode frequencies (approximately spaced)
        frequencies = [f1 * (n + 1) ** 2 / 4 for n in range(n_modes)]
        eigenvalues = [(2 * np.pi * f) ** 2 for f in frequencies]

        # Simulate mode shapes
        eigenvectors = np.random.randn(n_modes, n_nodes, 3)
        for i in range(n_modes):
            eigenvectors[i] /= np.linalg.norm(eigenvectors[i])

        return FEResult(
            analysis_type=AnalysisType.MODAL,
            eigenvalues=np.array(eigenvalues),
            eigenvectors=eigenvectors,
            modal_frequencies=frequencies,
        )

    def solve_impact(
        self,
        mesh: Mesh,
        material: MaterialProperties,
        constraints: List[Constraint],
        impact_velocity: float = 15.0,  # m/s
        impact_direction: List[float] = None,
    ) -> FEResult:
        """Solve impact analysis.

        Args:
            mesh: FE mesh
            material: Material properties
            constraints: Boundary constraints
            impact_velocity: Impact velocity (m/s)
            impact_direction: Impact direction unit vector

        Returns:
            FEResult with impact stresses and deformations
        """
        if impact_direction is None:
            impact_direction = [1, 0, 0]

        # Convert to numpy array
        direction = np.array(impact_direction)
        direction = direction / np.linalg.norm(direction)

        # Estimate impact energy
        L = np.max(mesh.nodes[:, 0]) - np.min(mesh.nodes[:, 0])
        W = np.max(mesh.nodes[:, 1]) - np.min(mesh.nodes[:, 1])
        H = np.max(mesh.nodes[:, 2]) - np.min(mesh.nodes[:, 2])
        volume = L * W * H * 1e-9  # mm³ to m³
        mass = material.density * volume

        kinetic_energy = 0.5 * mass * impact_velocity ** 2

        # Estimate peak force using energy equivalence
        E = material.youngs_modulus * 1e6  # Pa
        A = W * H * 1e-6  # m²
        
        if E > 0 and A > 0:
            # Simplified: F * delta = KE, delta = F*L/(E*A)
            # F² * L / (E * A) = KE => F = sqrt(KE * E * A / L)
            peak_force = np.sqrt(kinetic_energy * E * A / (L * 1e-3)) if L > 0 else 0
        else:
            peak_force = 0

        # Peak stress
        max_stress = peak_force / (A * 1e6) if A > 0 else 0  # MPa

        n_elements = len(mesh.elements)
        stresses = np.random.rand(n_elements) * max_stress

        return FEResult(
            analysis_type=AnalysisType.TRANSIENT,
            stresses=stresses,
            max_stress=float(max_stress),
            safety_factor=500 / max_stress if max_stress > 0 else 10,
        )


def create_baja_load_cases() -> List[LoadCase]:
    """Create standard load cases for Baja 1000 trophy truck.

    Returns:
        List of standard load cases
    """
    return [
        LoadCase(
            name="Maximum Vertical (5g Landing)",
            forces=[],
            accelerations=[0, 0, -5 * 9.81],  # 5g vertical
        ),
        LoadCase(
            name="Maximum Lateral (2g Cornering)",
            forces=[],
            accelerations=[0, 2 * 9.81, -1 * 9.81],  # 2g lateral + 1g vertical
        ),
        LoadCase(
            name="Maximum Braking (1.5g)",
            forces=[],
            accelerations=[-1.5 * 9.81, 0, -1 * 9.81],  # 1.5g braking + 1g vertical
        ),
        LoadCase(
            name="Combined Jump Landing",
            forces=[],
            accelerations=[-0.5 * 9.81, 0.5 * 9.81, -4 * 9.81],  # Combined
        ),
        LoadCase(
            name="Rollover",
            forces=[{"location": "roll_cage_top", "magnitude": 50000, "direction": [0, 0, -1]}],
            accelerations=[0, 0, -1 * 9.81],
        ),
    ]
