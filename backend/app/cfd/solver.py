"""CFD solver interface for aerodynamic analysis."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np


class TurbulenceModel(str, Enum):
    """Turbulence model options."""

    KOMEGA_SST = "kOmegaSST"
    SPALART_ALLMARAS = "SpalartAllmaras"
    REALIZABLE_KEPSILON = "realizableKE"


@dataclass
class CFDConfig:
    """Configuration for CFD analysis."""

    velocity: float = 44.7  # m/s (100 mph typical Baja speed)
    air_density: float = 1.225  # kg/m³
    kinematic_viscosity: float = 1.5e-5  # m²/s
    turbulence_model: TurbulenceModel = TurbulenceModel.KOMEGA_SST
    max_iterations: int = 1000
    convergence_tolerance: float = 1e-4
    
    # Mesh settings
    boundary_layer_first_cell: float = 1e-5  # m
    boundary_layer_growth_rate: float = 1.2
    boundary_layer_layers: int = 15


@dataclass
class CFDResult:
    """Result of CFD analysis."""

    drag_force: float  # N
    lift_force: float  # N
    side_force: float  # N
    drag_coefficient: float
    lift_coefficient: float
    side_coefficient: float
    frontal_area: float  # m²
    reference_velocity: float  # m/s
    pressure_distribution: Optional[np.ndarray] = None
    wall_shear: Optional[np.ndarray] = None
    convergence_history: Optional[List[float]] = None
    is_converged: bool = True


@dataclass
class CoolingFlowResult:
    """Result of cooling flow analysis."""

    mass_flow_rate: float  # kg/s
    pressure_drop: float  # Pa
    inlet_velocity: float  # m/s
    exit_temperature_rise: float  # K
    heat_rejection_capacity: float  # W


class CFDSolver:
    """CFD solver interface for aerodynamic analysis.
    
    Mock implementation - in production would interface with OpenFOAM.
    """

    def __init__(self, config: CFDConfig):
        """Initialize CFD solver.

        Args:
            config: CFD configuration
        """
        self.config = config
        self._openfoam_available = False
        self._check_openfoam()

    def _check_openfoam(self) -> None:
        """Check if OpenFOAM is available."""
        import shutil
        self._openfoam_available = shutil.which("simpleFoam") is not None

    def analyze_external_aero(
        self,
        geometry_file: str,
        yaw_angle: float = 0,
        pitch_angle: float = 0,
    ) -> CFDResult:
        """Analyze external aerodynamics.

        Args:
            geometry_file: Path to geometry file (STL)
            yaw_angle: Vehicle yaw angle (degrees)
            pitch_angle: Vehicle pitch angle (degrees)

        Returns:
            CFDResult with drag, lift, and side forces
        """
        velocity = self.config.velocity
        rho = self.config.air_density

        # Mock implementation - estimate based on typical trophy truck values
        # Real implementation would run OpenFOAM simulation

        # Estimate frontal area for trophy truck
        frontal_area = 3.5  # m² typical

        # Base drag coefficient for boxy off-road vehicle
        cd_base = 0.55

        # Adjust for yaw angle (increased drag in crosswind)
        cd = cd_base * (1 + 0.3 * np.sin(np.radians(abs(yaw_angle))) ** 2)

        # Lift coefficient (slight lift for typical truck shape)
        cl = 0.15 + 0.1 * np.sin(np.radians(pitch_angle))

        # Side force coefficient
        cs = 0.8 * np.sin(np.radians(yaw_angle))

        # Dynamic pressure
        q = 0.5 * rho * velocity ** 2

        # Forces
        drag_force = cd * q * frontal_area
        lift_force = cl * q * frontal_area
        side_force = cs * q * frontal_area

        # Simulate convergence history
        convergence_history = [1.0]
        for i in range(100):
            convergence_history.append(convergence_history[-1] * 0.95)

        return CFDResult(
            drag_force=drag_force,
            lift_force=lift_force,
            side_force=side_force,
            drag_coefficient=cd,
            lift_coefficient=cl,
            side_coefficient=cs,
            frontal_area=frontal_area,
            reference_velocity=velocity,
            convergence_history=convergence_history,
            is_converged=True,
        )

    def analyze_side_wind_stability(
        self,
        geometry_file: str,
        vehicle_speed: float = 44.7,  # m/s
        wind_speeds: List[float] = None,
    ) -> Dict[str, CFDResult]:
        """Analyze vehicle stability under side wind conditions.

        Args:
            geometry_file: Path to geometry file
            vehicle_speed: Vehicle forward speed (m/s)
            wind_speeds: List of crosswind speeds to analyze

        Returns:
            Dictionary of yaw_angle -> CFDResult
        """
        if wind_speeds is None:
            wind_speeds = [5, 10, 15, 20]  # m/s

        results = {}

        for wind_speed in wind_speeds:
            # Calculate effective yaw angle
            yaw_angle = np.degrees(np.arctan(wind_speed / vehicle_speed))
            
            # Analyze at this yaw
            result = self.analyze_external_aero(geometry_file, yaw_angle=yaw_angle)
            results[f"wind_{wind_speed}ms"] = result

        return results

    def analyze_cooling_flow(
        self,
        radiator_geometry: Dict[str, Any],
        vehicle_speed: float = 44.7,
        inlet_area: float = 0.15,  # m²
    ) -> CoolingFlowResult:
        """Analyze cooling airflow through radiator.

        Args:
            radiator_geometry: Radiator dimensions and core properties
            vehicle_speed: Vehicle speed (m/s)
            inlet_area: Inlet opening area (m²)

        Returns:
            CoolingFlowResult with mass flow and heat rejection
        """
        rho = self.config.air_density

        # Estimate inlet velocity (reduced from freestream due to resistance)
        inlet_velocity = vehicle_speed * 0.4  # Typical reduction factor

        # Mass flow rate
        mass_flow = rho * inlet_velocity * inlet_area

        # Pressure drop across radiator (simplified)
        # Typical radiator has 500-2000 Pa drop at full flow
        pressure_drop = 800 * (inlet_velocity / 20) ** 2

        # Heat rejection capacity
        # Typical: 20-40 kW/kg air flow at 50K temperature difference
        cp_air = 1005  # J/(kg·K)
        delta_t = 30  # K typical air temperature rise
        heat_rejection = mass_flow * cp_air * delta_t

        return CoolingFlowResult(
            mass_flow_rate=mass_flow,
            pressure_drop=pressure_drop,
            inlet_velocity=inlet_velocity,
            exit_temperature_rise=delta_t,
            heat_rejection_capacity=heat_rejection,
        )


def create_aero_targets() -> Dict[str, Any]:
    """Create aerodynamic targets for Baja trophy truck.

    Returns:
        Dictionary of aero targets and constraints
    """
    return {
        "max_drag_coefficient": 0.65,
        "max_lift_coefficient": 0.3,
        "max_side_force_coefficient_at_20ms_crosswind": 1.2,
        "min_cooling_flow_rate_kg_s": 0.8,
        "max_pressure_drop_radiator_pa": 1500,
        "min_heat_rejection_kw": 40,
        "target_downforce_at_100mph_n": 500,  # Slight downforce desired
        "max_front_rear_lift_imbalance": 0.2,  # For stability
    }
