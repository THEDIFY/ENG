"""
Configuration management for topology optimization workflow
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class MaterialProperties:
    """Carbon fiber material properties"""
    name: str = "Carbon Fiber Laminate"
    youngs_modulus: float = 150e9  # Pa
    poisson_ratio: float = 0.3
    density: float = 1600  # kg/m³
    tensile_strength: float = 600e6  # Pa
    compressive_strength: float = 570e6  # Pa
    shear_modulus: float = 5e9  # Pa
    ply_thickness: float = 0.125e-3  # m (125 microns)


@dataclass
class ComponentBounds:
    """Bounding box for chassis components"""
    name: str
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_min: float
    z_max: float
    
    def volume(self) -> float:
        """Calculate volume of bounding box"""
        return ((self.x_max - self.x_min) * 
                (self.y_max - self.y_min) * 
                (self.z_max - self.z_min))


@dataclass
class LoadCase:
    """Load case definition"""
    name: str
    load_type: str  # 'static', 'dynamic', 'impact'
    forces: Dict[str, Tuple[float, float, float]]  # location -> (Fx, Fy, Fz)
    moments: Dict[str, Tuple[float, float, float]] = field(default_factory=dict)
    safety_factor: float = 1.5


@dataclass
class OptimizationConfig:
    """Main configuration for topology optimization"""
    
    # Chassis dimensions (meters)
    chassis_length: float = 5.5
    chassis_width: float = 2.3
    chassis_height: float = 2.0
    
    # Material properties
    material: MaterialProperties = field(default_factory=MaterialProperties)
    
    # Optimization objectives
    target_weight_reduction: float = 0.3  # 30% weight reduction
    min_stiffness_ratio: float = 0.9  # Maintain 90% of original stiffness
    max_drag_coefficient: float = 0.35
    
    # Baja 1000 regulation constraints
    min_ground_clearance: float = 0.35  # meters
    max_vehicle_width: float = 2.5  # meters
    safety_cell_volume: float = 1.5  # cubic meters
    roll_cage_tube_diameter: float = 0.05  # meters
    
    # Component placements
    components: List[ComponentBounds] = field(default_factory=list)
    
    # Load cases
    load_cases: List[LoadCase] = field(default_factory=list)
    
    # Manufacturing constraints
    min_member_thickness: float = 0.003  # 3mm minimum wall thickness
    max_overhang_angle: float = 45.0  # degrees
    min_hole_diameter: float = 0.006  # 6mm minimum hole size
    
    # CFD settings
    target_velocity: float = 45.0  # m/s (100 mph)
    air_density: float = 1.225  # kg/m³
    
    def __post_init__(self):
        """Initialize default components and load cases if not provided"""
        if not self.components:
            self._setup_default_components()
        if not self.load_cases:
            self._setup_default_load_cases()
    
    def _setup_default_components(self):
        """Setup default component bounding boxes"""
        self.components = [
            ComponentBounds("Engine", 1.0, 1.8, -0.4, 0.4, 0.3, 0.9),
            ComponentBounds("Transmission", 1.8, 2.3, -0.3, 0.3, 0.2, 0.7),
            ComponentBounds("Front Suspension", 0.2, 0.8, -1.0, 1.0, 0.0, 0.6),
            ComponentBounds("Rear Suspension", 4.5, 5.2, -1.0, 1.0, 0.0, 0.6),
            ComponentBounds("Safety Cell", 1.5, 3.0, -0.6, 0.6, 0.5, 1.8),
            ComponentBounds("Fuel Tank", 3.5, 4.2, -0.5, 0.5, 0.2, 0.8),
        ]
    
    def _setup_default_load_cases(self):
        """Setup default load cases for Baja 1000 racing"""
        # Static cornering load
        cornering = LoadCase(
            name="Cornering",
            load_type="static",
            forces={
                "front_left": (-5000, -15000, -8000),
                "front_right": (-5000, 15000, -8000),
                "rear_left": (-5000, -10000, -8000),
                "rear_right": (-5000, 10000, -8000),
            },
            safety_factor=2.0
        )
        
        # Jump landing impact
        landing = LoadCase(
            name="Landing Impact",
            load_type="impact",
            forces={
                "front_left": (0, 0, -40000),
                "front_right": (0, 0, -40000),
                "rear_left": (0, 0, -50000),
                "rear_right": (0, 0, -50000),
            },
            safety_factor=2.5
        )
        
        # Torsional rigidity
        torsion = LoadCase(
            name="Torsion",
            load_type="static",
            forces={
                "front_left": (0, 0, -10000),
                "rear_right": (0, 0, -10000),
                "front_right": (0, 0, 10000),
                "rear_left": (0, 0, 10000),
            },
            safety_factor=1.5
        )
        
        # Frontal impact
        frontal_impact = LoadCase(
            name="Frontal Impact",
            load_type="impact",
            forces={
                "front_bumper": (-100000, 0, 0),
            },
            safety_factor=3.0
        )
        
        self.load_cases = [cornering, landing, torsion, frontal_impact]
