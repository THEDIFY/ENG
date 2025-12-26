/**
 * Shared types for the Trophy Truck Topology Optimizer
 */

export interface Project {
  id: string
  name: string
  description?: string
  status: ProjectStatus
  rules_config?: BajaRulesConfig
  components_config?: ComponentsConfig
  design_space_config?: DesignSpaceConfig
  load_cases?: LoadCasesConfig
  materials_config?: Record<string, any>
  manufacturing_config?: ManufacturingConfig
  optimization_params?: OptimizationParams
  optimization_results?: OptimizationResults
  validation_results?: ValidationResults
  created_at: string
  updated_at: string
}

export type ProjectStatus =
  | 'draft'
  | 'rules_parsed'
  | 'components_placed'
  | 'design_space_generated'
  | 'loads_defined'
  | 'optimizing'
  | 'post_processing'
  | 'validating'
  | 'completed'
  | 'failed'

export interface BajaRulesConfig {
  rule_set_version: string
  constraints: Constraint[]
  max_width: number
  max_length: number
  min_ground_clearance: number
  wheelbase_min: number
  wheelbase_max: number
}

export interface Constraint {
  name: string
  category: string
  value: any
  unit?: string
  min_value?: number
  max_value?: number
  description?: string
}

export interface ComponentPlacement {
  component_id: string
  name: string
  component_type: string
  position: [number, number, number]
  orientation: [number, number, number]
  bounding_box?: [number, number, number]
  mass?: number
  cg_offset?: [number, number, number]
  mounting_points?: MountingPoint[]
  clearance_required: number
}

export interface MountingPoint {
  id: string
  position: [number, number, number]
  type: 'bolt' | 'weld' | 'adhesive'
}

export interface ComponentsConfig {
  components: ComponentPlacement[]
  engine?: ComponentPlacement
  transmission?: ComponentPlacement
  fuel_cell?: ComponentPlacement
  radiator?: ComponentPlacement
  driver_seat?: ComponentPlacement
  co_driver_seat?: ComponentPlacement
}

export interface DesignSpaceConfig {
  design_volume: any
  keep_out_zones: KeepOutZone[]
  symmetry_plane?: string
  minimum_member_size: number
  maximum_member_size: number
}

export interface KeepOutZone {
  name: string
  zone_type: 'box' | 'cylinder' | 'mesh'
  geometry: any
  reason: string
}

export interface LoadCase {
  name: string
  load_type: 'static' | 'dynamic' | 'impact' | 'fatigue'
  description?: string
  forces?: Force[]
  moments?: Moment[]
  pressures?: Pressure[]
  accelerations?: [number, number, number]
  safety_factor: number
  load_factor: number
  frequency?: number
}

export interface Force {
  location: string
  magnitude: number
  direction: [number, number, number]
}

export interface Moment {
  location: string
  magnitude: number
  axis: [number, number, number]
}

export interface Pressure {
  surface: string
  magnitude: number
  direction: [number, number, number]
}

export interface LoadCasesConfig {
  mission_profile: string
  load_cases: LoadCase[]
  max_vertical_g: number
  max_lateral_g: number
  max_braking_g: number
  impact_velocity: number
  roll_over_scenario: boolean
}

export interface ManufacturingConfig {
  allowed_ply_angles: number[]
  min_ply_thickness: number
  max_ply_drops_per_zone: number
  max_consecutive_same_angle: number
  enforce_symmetry: boolean
  enforce_balance: boolean
  max_shear_angle: number
  min_radius: number
  mold_split_planes?: any[]
  draft_angle: number
  metallic_inserts?: any[]
  adhesive_bond_areas?: any[]
}

export interface OptimizationParams {
  method: 'simp' | 'level_set' | 'hybrid'
  volume_fraction: number
  penalty_factor: number
  filter_radius: number
  max_iterations: number
  convergence_tolerance: number
  move_limit: number
  compliance_weight: number
  mass_weight: number
  aero_weight: number
  displacement_limit?: number
  stress_limit?: number
  modal_constraints?: ModalConstraint[]
  aero_coupling: boolean
  aero_update_interval: number
}

export interface ModalConstraint {
  mode_number: number
  min_frequency: number
}

export interface OptimizationResults {
  density_field: number[]
  final_compliance: number
  final_volume_fraction: number
  iterations: number
  converged: boolean
  convergence_history: number[]
}

export interface ValidationResults {
  structural: StructuralValidation
  modal: ModalValidation
  aero: AeroValidation
  manufacturing: ManufacturingValidation
  compliance: Record<string, boolean>
  overall_pass: boolean
}

export interface StructuralValidation {
  max_displacement: number
  max_stress: number
  safety_factor: number
  compliance: number
}

export interface ModalValidation {
  frequencies: number[]
  mode_shapes?: any[]
}

export interface AeroValidation {
  cd: number
  cl: number
  drag_force: number
  cooling_flow: number
}

export interface ManufacturingValidation {
  drapeable: boolean
  max_shear: number
  ply_rules_valid: boolean
  mold_valid: boolean
  violations: string[]
}
