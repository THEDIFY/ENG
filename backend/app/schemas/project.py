"""Pydantic schemas for Project API."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.project import JobStatus, JobType, OutputType, ProjectStatus


# Base schemas
class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    class Config:
        from_attributes = True


# Baja Rules schemas
class BajaRulesConstraint(BaseModel):
    """Individual constraint from Baja rules."""

    name: str
    category: str  # safety, dimensions, materials, etc.
    value: Any
    unit: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    description: Optional[str] = None


class BajaRulesConfig(BaseModel):
    """Baja 1000 rules configuration."""

    rule_set_version: str = "2024"
    constraints: List[BajaRulesConstraint] = Field(default_factory=list)
    
    # Safety requirements
    roll_cage_requirements: Optional[Dict[str, Any]] = None
    fire_suppression: Optional[Dict[str, Any]] = None
    fuel_cell_requirements: Optional[Dict[str, Any]] = None
    
    # Dimensional constraints
    max_width: float = 2438  # mm (96 inches)
    max_length: float = 5486  # mm (18 feet)
    min_ground_clearance: float = 254  # mm (10 inches)
    wheelbase_min: float = 2540  # mm (100 inches)
    wheelbase_max: float = 3556  # mm (140 inches)


# Component schemas
class ComponentPlacement(BaseModel):
    """Component placement specification."""

    component_id: str
    name: str
    component_type: str  # engine, transmission, suspension, etc.
    position: List[float] = Field(..., min_length=3, max_length=3)  # x, y, z
    orientation: List[float] = Field(default=[0, 0, 0], min_length=3, max_length=3)  # roll, pitch, yaw
    bounding_box: Optional[List[float]] = None  # length, width, height
    mass: Optional[float] = None  # kg
    cg_offset: Optional[List[float]] = None  # local CG offset
    mounting_points: Optional[List[Dict[str, Any]]] = None
    clearance_required: float = 25.0  # mm
    access_corridor: Optional[Dict[str, Any]] = None


class ComponentsConfig(BaseModel):
    """Configuration for all components."""

    components: List[ComponentPlacement] = Field(default_factory=list)
    
    # Standard Baja components
    engine: Optional[ComponentPlacement] = None
    transmission: Optional[ComponentPlacement] = None
    fuel_cell: Optional[ComponentPlacement] = None
    radiator: Optional[ComponentPlacement] = None
    driver_seat: Optional[ComponentPlacement] = None
    co_driver_seat: Optional[ComponentPlacement] = None
    front_suspension: Optional[Dict[str, Any]] = None
    rear_suspension: Optional[Dict[str, Any]] = None


# Design Space schemas
class KeepOutZone(BaseModel):
    """Keep-out zone definition."""

    name: str
    zone_type: str  # box, cylinder, mesh
    geometry: Dict[str, Any]
    reason: str


class DesignSpaceConfig(BaseModel):
    """Design space configuration."""

    design_volume: Dict[str, Any]  # Bounding geometry for design space
    keep_out_zones: List[KeepOutZone] = Field(default_factory=list)
    symmetry_plane: Optional[str] = "xz"  # Symmetry plane
    minimum_member_size: float = 5.0  # mm
    maximum_member_size: float = 100.0  # mm
    boundary_conditions: Optional[Dict[str, Any]] = None


# Load Case schemas
class LoadCase(BaseModel):
    """Individual load case definition."""

    name: str
    load_type: str  # static, dynamic, impact, fatigue
    description: Optional[str] = None
    
    # Load specifications
    forces: Optional[List[Dict[str, Any]]] = None  # Point forces
    moments: Optional[List[Dict[str, Any]]] = None  # Moments
    pressures: Optional[List[Dict[str, Any]]] = None  # Distributed loads
    accelerations: Optional[List[float]] = None  # Body accelerations (g's)
    
    # Importance and factors
    safety_factor: float = 1.5
    load_factor: float = 1.0
    frequency: Optional[int] = None  # For fatigue (cycles)


class LoadCasesConfig(BaseModel):
    """Configuration for all load cases."""

    mission_profile: str = "baja_1000"
    load_cases: List[LoadCase] = Field(default_factory=list)
    
    # Standard Baja load cases
    max_vertical_g: float = 5.0
    max_lateral_g: float = 2.0
    max_braking_g: float = 1.5
    impact_velocity: float = 15.0  # m/s
    roll_over_scenario: bool = True


# Manufacturing schemas
class PlyDefinition(BaseModel):
    """Single ply definition."""

    ply_id: int
    material_id: str
    angle: float  # degrees
    thickness: float  # mm
    coverage_region: Optional[str] = None  # Region name or full


class LayupSequence(BaseModel):
    """Laminate layup sequence."""

    name: str
    plies: List[PlyDefinition]
    total_thickness: Optional[float] = None
    symmetry: bool = True
    balanced: bool = True


class ManufacturingConfig(BaseModel):
    """Manufacturing constraints configuration."""

    # Ply rules
    allowed_ply_angles: List[float] = Field(default=[0, 45, -45, 90])
    min_ply_thickness: float = 0.2  # mm
    max_ply_drops_per_zone: int = 4
    max_consecutive_same_angle: int = 4
    
    # Symmetry and balance
    enforce_symmetry: bool = True
    enforce_balance: bool = True
    
    # Drapability
    max_shear_angle: float = 45.0  # degrees
    min_radius: float = 10.0  # mm
    
    # Mold constraints
    mold_split_planes: Optional[List[Dict[str, Any]]] = None
    draft_angle: float = 3.0  # degrees
    
    # Inserts and fasteners
    metallic_inserts: Optional[List[Dict[str, Any]]] = None
    adhesive_bond_areas: Optional[List[Dict[str, Any]]] = None


# Optimization schemas
class OptimizationParams(BaseModel):
    """Optimization parameters."""

    method: str = "simp"  # simp, level_set, hybrid
    volume_fraction: float = 0.3
    penalty_factor: float = 3.0
    filter_radius: float = 2.0  # mesh elements
    
    # Convergence
    max_iterations: int = 500
    convergence_tolerance: float = 1e-4
    move_limit: float = 0.2
    
    # Multi-objective weights
    compliance_weight: float = 1.0
    mass_weight: float = 0.5
    aero_weight: float = 0.3
    
    # Constraints
    displacement_limit: Optional[float] = None  # mm
    stress_limit: Optional[float] = None  # MPa
    modal_constraints: Optional[List[Dict[str, Any]]] = None
    
    # Aero coupling
    aero_coupling: bool = True
    aero_update_interval: int = 50  # iterations


# Project schemas
class ProjectCreate(BaseSchema):
    """Schema for creating a new project."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectUpdate(BaseSchema):
    """Schema for updating a project."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    rules_config: Optional[BajaRulesConfig] = None
    components_config: Optional[ComponentsConfig] = None
    design_space_config: Optional[DesignSpaceConfig] = None
    load_cases: Optional[LoadCasesConfig] = None
    materials_config: Optional[Dict[str, Any]] = None
    manufacturing_config: Optional[ManufacturingConfig] = None
    optimization_params: Optional[OptimizationParams] = None


class ProjectResponse(BaseSchema):
    """Schema for project response."""

    id: UUID
    name: str
    description: Optional[str]
    status: ProjectStatus
    rules_config: Optional[Dict[str, Any]]
    components_config: Optional[Dict[str, Any]]
    design_space_config: Optional[Dict[str, Any]]
    load_cases: Optional[Dict[str, Any]]
    materials_config: Optional[Dict[str, Any]]
    manufacturing_config: Optional[Dict[str, Any]]
    optimization_params: Optional[Dict[str, Any]]
    optimization_results: Optional[Dict[str, Any]]
    validation_results: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(BaseSchema):
    """Schema for project list response."""

    id: UUID
    name: str
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime


# Job schemas
class JobCreate(BaseSchema):
    """Schema for creating a job."""

    job_type: JobType
    config: Optional[Dict[str, Any]] = None


class JobResponse(BaseSchema):
    """Schema for job response."""

    id: UUID
    project_id: UUID
    job_type: JobType
    status: JobStatus
    progress: float
    current_iteration: Optional[int]
    total_iterations: Optional[int]
    results: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


class JobProgressUpdate(BaseSchema):
    """Schema for job progress updates."""

    iteration: int
    objective_value: float
    constraint_violations: Optional[Dict[str, float]] = None
    volume_fraction: float
    convergence_metric: float


# Output schemas
class OutputResponse(BaseSchema):
    """Schema for output response."""

    id: UUID
    project_id: UUID
    output_type: OutputType
    filename: str
    file_size: Optional[int]
    mime_type: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime


# Validation schemas
class ValidationResult(BaseModel):
    """Validation result for a single check."""

    check_name: str
    category: str
    passed: bool
    actual_value: Optional[Any] = None
    required_value: Optional[Any] = None
    message: str


class ValidationReport(BaseModel):
    """Complete validation report."""

    project_id: UUID
    timestamp: datetime
    overall_passed: bool
    structural_checks: List[ValidationResult]
    aero_checks: List[ValidationResult]
    manufacturing_checks: List[ValidationResult]
    rules_compliance: List[ValidationResult]
