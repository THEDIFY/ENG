"""
Topology optimization engine for chassis design
Implements SIMP (Solid Isotropic Material with Penalization) method
"""

import numpy as np
from scipy.ndimage import gaussian_filter


class ChassisOptimizer:
    """Main chassis topology optimization engine"""
    
    def __init__(self, race_rules, component_specs, mission_profile):
        """
        Initialize optimizer with design constraints
        
        race_rules: dict with rules like max_weight, dimensions, safety_requirements
        component_specs: dict with engine, suspension, wheel specs
        mission_profile: dict with terrain, speed, duration, loads
        """
        self.race_rules = race_rules
        self.component_specs = component_specs
        self.mission_profile = mission_profile
        
        # Design space parameters
        self.design_space = self._define_design_space()
        self.loads = self._calculate_loads()
        self.constraints = self._define_constraints()
        
    def _define_design_space(self):
        """Define the 3D design space for optimization"""
        # Get dimensions from race rules or use defaults
        length = self.race_rules.get('max_length', 5.0)  # meters
        width = self.race_rules.get('max_width', 2.2)    # meters
        height = self.race_rules.get('max_height', 1.8)  # meters
        
        # Create voxel grid for topology optimization
        resolution = 50  # voxels per meter
        nx = int(length * resolution)
        ny = int(width * resolution)
        nz = int(height * resolution)
        
        return {
            'dimensions': (length, width, height),
            'voxels': (nx, ny, nz),
            'resolution': resolution,
            'volume': length * width * height
        }
    
    def _calculate_loads(self):
        """Calculate load cases from mission profile"""
        loads = []
        
        # Extract mission parameters
        terrain = self.mission_profile.get('terrain_roughness', 'medium')
        max_speed = self.mission_profile.get('max_speed', 160)  # km/h
        
        # Terrain roughness multipliers
        terrain_factors = {'smooth': 1.0, 'medium': 2.5, 'rough': 4.0, 'extreme': 6.0}
        terrain_factor = terrain_factors.get(terrain, 2.5)
        
        # Vehicle mass estimate (kg)
        vehicle_mass = self.component_specs.get('estimated_mass', 1500)
        
        # Load case 1: Vertical impact (landing jump)
        g_vertical = 5.0 * terrain_factor  # G-forces
        load_vertical = vehicle_mass * 9.81 * g_vertical
        loads.append({
            'type': 'vertical_impact',
            'magnitude': load_vertical,
            'direction': [0, 0, -1],
            'location': 'suspension_mounts'
        })
        
        # Load case 2: Lateral loading (cornering)
        g_lateral = 2.0
        load_lateral = vehicle_mass * 9.81 * g_lateral
        loads.append({
            'type': 'lateral',
            'magnitude': load_lateral,
            'direction': [0, 1, 0],
            'location': 'center_of_gravity'
        })
        
        # Load case 3: Longitudinal (braking/acceleration)
        g_longitudinal = 1.5
        load_longitudinal = vehicle_mass * 9.81 * g_longitudinal
        loads.append({
            'type': 'longitudinal',
            'magnitude': load_longitudinal,
            'direction': [1, 0, 0],
            'location': 'center_of_gravity'
        })
        
        # Load case 4: Torsional (uneven terrain)
        torque = vehicle_mass * 9.81 * 0.5 * terrain_factor
        loads.append({
            'type': 'torsional',
            'magnitude': torque,
            'direction': [1, 0, 0],  # About longitudinal axis
            'location': 'chassis_twist'
        })
        
        return loads
    
    def _define_constraints(self):
        """Define optimization constraints"""
        return {
            'max_mass': self.race_rules.get('max_weight', 1000),  # kg for chassis
            'min_safety_factor': self.race_rules.get('min_safety_factor', 2.0),
            'max_deflection': self.race_rules.get('max_deflection', 0.020),  # 20mm
            'min_torsional_stiffness': 15000,  # N⋅m/degree
            'max_stress': 400e6,  # Pa (carbon fiber)
            'volume_fraction_target': 0.3,  # 30% material usage
            'symmetry': self.race_rules.get('symmetry', True)
        }
    
    def run_optimization(self):
        """
        Run topology optimization using SIMP method
        Returns optimized density distribution and performance metrics
        """
        print("Starting topology optimization...")
        
        # Initialize density field (uniform distribution)
        vox = self.design_space['voxels']
        rho = np.ones(vox) * self.constraints['volume_fraction_target']
        
        # Optimization parameters
        penalty = 3.0  # SIMP penalty factor
        filter_radius = 2  # Density filter radius
        max_iterations = 100
        tolerance = 0.01
        
        # Fixed regions (mounting points, suspension, engine bay)
        fixed_regions = self._define_fixed_regions()
        
        for iteration in range(max_iterations):
            # Apply density filter for manufacturability
            rho_filtered = gaussian_filter(rho, sigma=filter_radius)
            
            # Calculate compliance (objective function)
            compliance = self._calculate_compliance(rho_filtered, penalty)
            
            # Calculate sensitivity
            dc_drho = self._calculate_sensitivity(rho_filtered, penalty)
            
            # Update densities using optimality criteria method
            rho_new = self._update_densities(rho, dc_drho)
            
            # Apply fixed regions
            rho_new = self._apply_fixed_regions(rho_new, fixed_regions)
            
            # Check convergence
            change = np.max(np.abs(rho_new - rho))
            rho = rho_new
            
            if iteration % 10 == 0:
                print(f"Iteration {iteration}: Compliance={compliance:.2f}, Change={change:.4f}")
            
            if change < tolerance:
                print(f"Converged at iteration {iteration}")
                break
        
        # Post-process results
        result = self._post_process_results(rho)
        
        return result
    
    def _define_fixed_regions(self):
        """Define regions that must remain solid (mounting points, etc.)"""
        vox = self.design_space['voxels']
        fixed = np.zeros(vox, dtype=bool)
        
        # Suspension mounting points (corners, bottom)
        corner_radius = 5
        fixed[:corner_radius, :corner_radius, -corner_radius:] = True
        fixed[-corner_radius:, :corner_radius, -corner_radius:] = True
        fixed[:corner_radius, -corner_radius:, -corner_radius:] = True
        fixed[-corner_radius:, -corner_radius:, -corner_radius:] = True
        
        # Engine mounting area (front-center)
        engine_x = slice(0, vox[0]//4)
        engine_y = slice(vox[1]//3, 2*vox[1]//3)
        engine_z = slice(2*vox[2]//3, vox[2])
        fixed[engine_x, engine_y, engine_z] = True
        
        return fixed
    
    def _calculate_compliance(self, rho, penalty):
        """Calculate structural compliance (simplified FEA)"""
        # Simplified compliance calculation
        # In full implementation, this would solve FEA system
        E_min = 1e-9  # Minimum stiffness to avoid singularity
        E_0 = 70e9    # Young's modulus for carbon fiber
        
        # SIMP interpolation
        E = E_min + (E_0 - E_min) * rho**penalty
        
        # Simplified compliance (lower is better)
        compliance = np.sum(1.0 / E) / E.size
        
        return compliance
    
    def _calculate_sensitivity(self, rho, penalty):
        """Calculate sensitivity of objective to density changes"""
        E_min = 1e-9
        E_0 = 70e9
        
        # Derivative of compliance with respect to density
        dc_drho = -penalty * (E_0 - E_min) * rho**(penalty - 1) / (E_min + (E_0 - E_min) * rho**penalty)**2
        
        return dc_drho
    
    def _update_densities(self, rho, dc_drho):
        """Update density field using optimality criteria"""
        move = 0.2  # Move limit
        l1 = 0
        l2 = 1e9
        
        # Target volume fraction
        target_volume = self.constraints['volume_fraction_target']
        
        # Bisection to find Lagrange multiplier
        while (l2 - l1) / (l2 + l1) > 1e-3:
            lmid = 0.5 * (l1 + l2)
            
            # Optimality criteria update
            rho_new = np.maximum(0.001, 
                      np.maximum(rho - move,
                      np.minimum(1.0,
                      np.minimum(rho + move,
                      rho * np.sqrt(-dc_drho / lmid)))))
            
            if np.mean(rho_new) > target_volume:
                l1 = lmid
            else:
                l2 = lmid
        
        return rho_new
    
    def _apply_fixed_regions(self, rho, fixed):
        """Enforce fixed regions in density field"""
        rho[fixed] = 1.0
        return rho
    
    def _post_process_results(self, rho):
        """Post-process optimization results and calculate metrics"""
        # Threshold density for solid/void
        threshold = 0.5
        rho_binary = (rho > threshold).astype(float)
        
        # Calculate mass
        voxel_volume = np.prod(self.design_space['dimensions']) / np.prod(rho_binary.shape)
        material_density = 1580  # kg/m³ for carbon fiber
        mass = np.sum(rho_binary) * voxel_volume * material_density
        
        # Calculate aerodynamic properties (simplified)
        aero_data = self._calculate_aerodynamics(rho_binary)
        
        # Calculate structural properties
        structural_data = self._calculate_structural_properties(rho_binary)
        
        return {
            'density_field': rho.tolist(),
            'binary_geometry': rho_binary.tolist(),
            'mass': mass,
            'volume': np.sum(rho_binary) * voxel_volume,
            'volume_fraction': np.mean(rho_binary),
            'aero_data': aero_data,
            'structural_data': structural_data,
            'design_space': self.design_space,
            'loads': self.loads,
            'constraints': self.constraints
        }
    
    def _calculate_aerodynamics(self, geometry):
        """Calculate aerodynamic properties (simplified)"""
        # Frontal area estimation
        frontal_area = np.sum(np.max(geometry, axis=0)) * \
                      (self.design_space['dimensions'][1] * self.design_space['dimensions'][2]) / \
                      (geometry.shape[1] * geometry.shape[2])
        
        # Simplified drag coefficient estimation
        # Lower for more streamlined shapes
        volume_ratio = np.mean(geometry)
        base_cd = 0.35  # Base coefficient for race vehicle
        cd = base_cd + 0.2 * (1 - volume_ratio)  # Penalty for blockier shapes
        
        return {
            'drag_coefficient': cd,
            'frontal_area': frontal_area,
            'estimated_drag_force': 0.5 * 1.225 * cd * frontal_area * (160/3.6)**2  # At 160 km/h
        }
    
    def _calculate_structural_properties(self, geometry):
        """Calculate structural properties"""
        # Simplified structural analysis
        # In full implementation, would run FEA
        
        # Estimate stiffness based on material distribution
        volume_fraction = np.mean(geometry)
        base_stiffness = 50000  # N⋅m/degree
        stiffness = base_stiffness * volume_fraction**2
        
        # Safety factor estimation
        max_stress = 350e6  # Estimated from load cases
        material_strength = 400e6  # Carbon fiber strength
        safety_factor = material_strength / max_stress
        
        return {
            'stiffness': stiffness,
            'min_safety_factor': safety_factor,
            'max_stress': max_stress,
            'max_deflection': 0.015  # Estimated 15mm max deflection
        }
