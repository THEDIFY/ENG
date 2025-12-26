"""
Main workflow orchestrator for topology optimization
Integrates all modules following the workflow diagram
"""

import numpy as np
from typing import Dict, Optional
import os
from datetime import datetime

from .config import OptimizationConfig
from .rules_ingestion import Baja1000Rules
from .component_placement import ComponentPlacer
from .design_space import DesignSpaceGenerator
from .load_cases import LoadCaseManager
from .material_assignment import MaterialAssignment
from .optimizer import TopologyOptimizer
from .verification import FEAVerification, CFDVerification
from .manufacturability import ManufacturabilityChecker
from .cad_output import CADOutputGenerator


class TopologyOptimizationWorkflow:
    """
    Complete workflow for topology optimization of carbon fiber chassis
    Follows the Baja 1000 Trophy Truck design process
    """
    
    def __init__(self, config: Optional[OptimizationConfig] = None):
        """
        Initialize workflow
        
        Args:
            config: Optimization configuration (uses defaults if None)
        """
        self.config = config or OptimizationConfig()
        self.results = {}
        
        print("=" * 80)
        print("TOPOLOGY OPTIMIZATION WORKFLOW FOR CARBON FIBER TROPHY TRUCK CHASSIS")
        print("Baja 1000 Racing Application")
        print("=" * 80)
    
    def run(self, output_dir: str = "output") -> Dict:
        """
        Execute complete topology optimization workflow
        
        Args:
            output_dir: Directory for output files
            
        Returns:
            Complete results dictionary
        """
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\nStarting workflow at {datetime.now().isoformat()}")
        print(f"Output directory: {output_dir}\n")
        
        # Step 1: Rules Ingestion
        print("Step 1: Rules Ingestion - Baja 1000 Regulations")
        print("-" * 80)
        rules = self._step1_rules_ingestion()
        print(f"✓ Loaded {len(rules.rules)} regulation categories")
        
        # Step 2: Component Placement
        print("\nStep 2: Component Placement")
        print("-" * 80)
        component_placer = self._step2_component_placement()
        packaging = component_placer.get_packaging_summary()
        print(f"✓ Placed {packaging['num_components']} components")
        print(f"  Chassis utilization: {packaging['utilization_ratio']:.1%}")
        
        # Step 3: Design Space Generation
        print("\nStep 3: Design Space Generation")
        print("-" * 80)
        design_space_gen = self._step3_design_space(component_placer)
        design_space = design_space_gen.generate_space()
        volume_fracs = design_space_gen.get_volume_fraction()
        print(f"✓ Generated design space with {volume_fracs['total_elements']} elements")
        print(f"  Available space: {volume_fracs['available_fraction']:.1%}")
        
        # Step 4: Load Case Setup
        print("\nStep 4: Load Case Setup")
        print("-" * 80)
        load_manager = self._step4_load_cases()
        load_summary = load_manager.get_load_case_summary()
        print(f"✓ Configured {load_summary['num_load_cases']} load cases")
        for lc in load_summary['load_cases']:
            print(f"  - {lc['name']}: {lc['type']} (SF={lc['safety_factor']})")
        
        # Step 5: Material Assignment
        print("\nStep 5: Material Assignment")
        print("-" * 80)
        material_mgr = self._step5_material_assignment()
        material_summary = material_mgr.get_material_summary()
        print(f"✓ Material: {material_summary['primary_material']}")
        print(f"  Layup regions: {material_summary['num_layup_regions']}")
        print(f"  Metallic inserts: {material_summary['num_metallic_inserts']}")
        
        # Step 6: Topology Optimization
        print("\nStep 6: Topology Optimization Engine")
        print("-" * 80)
        optimizer = self._step6_optimization(design_space, load_manager)
        opt_results = optimizer.run_optimization(
            design_space,
            load_manager.get_combined_load_vector(np.zeros((100, 3))),
            max_iterations=50,
        )
        print(f"✓ Optimization completed in {opt_results['iterations']} iterations")
        print(f"  Final volume fraction: {opt_results['final_volume']:.3f}")
        print(f"  Weight reduction: {(1 - opt_results['final_volume']):.1%}")
        
        # Step 7: FEA & CFD Verification
        print("\nStep 7: FEA & CFD Verification")
        print("-" * 80)
        fea, cfd = self._step7_verification(optimizer.extract_geometry())
        print(f"✓ FEA Analysis:")
        print(f"  - Max stress: {self.results['fea_static']['max_von_mises_stress']/1e6:.1f} MPa")
        print(f"  - Safety factor: {self.results['fea_static']['safety_factor']:.2f}")
        print(f"  - Status: {self.results['fea_static']['status']}")
        print(f"✓ CFD Analysis:")
        print(f"  - Drag coefficient: {self.results['cfd_aero']['drag_coefficient']:.3f}")
        print(f"  - Drag force: {self.results['cfd_aero']['drag_force']:.1f} N")
        
        # Step 8: Manufacturability Checks
        print("\nStep 8: Manufacturability Checks")
        print("-" * 80)
        manuf_check = self._step8_manufacturability(optimizer.extract_geometry())
        validation = manuf_check.validate_for_manufacturing()
        print(f"✓ Manufacturing validation: {validation['overall_status']}")
        print(f"  - Drapability: {validation['drapability']['status']}")
        print(f"  - Thickness: {validation['thickness']['status']}")
        print(f"  - Overhangs: {validation['overhangs']['status']}")
        print(f"  - Fasteners: {validation['fasteners']['num_fasteners']} locations")
        
        # Step 9: CAD & Documentation Output
        print("\nStep 9: CAD & Documentation Output")
        print("-" * 80)
        cad_output = self._step9_output(optimizer.extract_geometry(), output_dir)
        print(f"✓ CAD files generated:")
        for cad_file in self.results['manufacturing_package']['cad_files']:
            print(f"  - {os.path.basename(cad_file)}")
        
        # Rules compliance check
        print("\nFinal Compliance Validation")
        print("-" * 80)
        design_params = {
            "length": self.config.chassis_length,
            "width": self.config.chassis_width,
            "ground_clearance": self.config.min_ground_clearance,
            "safety_cell_volume": self.config.safety_cell_volume,
            "chassis_material": "carbon_fiber",
            "min_thickness": self.config.min_member_thickness,
        }
        compliance = rules.validate_design(design_params)
        
        # Export compliance report
        compliance_file = os.path.join(output_dir, "compliance_report.json")
        cad_output.generate_compliance_report(compliance, compliance_file)
        
        print(f"✓ Compliance: {'PASS' if compliance['compliant'] else 'FAIL'}")
        print(f"  - Passed checks: {len(compliance['passed'])}")
        print(f"  - Violations: {len(compliance['violations'])}")
        
        if compliance['violations']:
            print("\n  Violations:")
            for violation in compliance['violations']:
                print(f"    ! {violation}")
        
        # Summary
        print("\n" + "=" * 80)
        print("WORKFLOW COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print(f"Output location: {output_dir}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("\nKey Results:")
        print(f"  - Weight reduction achieved: {(1 - opt_results['final_volume']):.1%}")
        print(f"  - Structural safety factor: {self.results['fea_static']['safety_factor']:.2f}")
        print(f"  - Drag coefficient: {self.results['cfd_aero']['drag_coefficient']:.3f}")
        print(f"  - Manufacturing ready: {validation['ready_for_production']}")
        print(f"  - Baja 1000 compliant: {compliance['compliant']}")
        
        self.results['workflow_complete'] = True
        self.results['compliance'] = compliance
        
        return self.results
    
    def _step1_rules_ingestion(self) -> Baja1000Rules:
        """Step 1: Parse Baja 1000 regulations"""
        rules = Baja1000Rules()
        self.results['rules'] = rules.get_constraints()
        return rules
    
    def _step2_component_placement(self) -> ComponentPlacer:
        """Step 2: Place components and define packaging"""
        placer = ComponentPlacer(
            (self.config.chassis_length, 
             self.config.chassis_width, 
             self.config.chassis_height)
        )
        
        for component in self.config.components:
            placer.add_component(component)
        
        self.results['component_placement'] = placer.get_packaging_summary()
        return placer
    
    def _step3_design_space(self, component_placer: ComponentPlacer) -> DesignSpaceGenerator:
        """Step 3: Generate design space with constraints"""
        ds_gen = DesignSpaceGenerator(
            (self.config.chassis_length,
             self.config.chassis_width,
             self.config.chassis_height),
            resolution=30  # Reduced for faster computation
        )
        
        # Add keep-out zones for components
        for component in component_placer.components:
            ds_gen.add_keep_out_zone(component)
        
        # Add symmetry constraint (bilateral)
        ds_gen.add_symmetry_constraint('xy')
        
        return ds_gen
    
    def _step4_load_cases(self) -> LoadCaseManager:
        """Step 4: Setup load cases"""
        manager = LoadCaseManager()
        
        for load_case in self.config.load_cases:
            manager.add_load_case(load_case)
        
        # Scale loads based on material
        manager.scale_loads_for_material(
            self.config.material.tensile_strength
        )
        
        return manager
    
    def _step5_material_assignment(self) -> MaterialAssignment:
        """Step 5: Assign materials and layup schedules"""
        material_mgr = MaterialAssignment(self.config.material)
        
        # Define layup regions
        material_mgr.define_layup_region(
            "main_structure",
            ply_orientations=[0, 45, -45, 90],
            num_plies=16
        )
        
        material_mgr.define_layup_region(
            "high_stress",
            ply_orientations=[0, 45, -45, 90],
            num_plies=24
        )
        
        # Add metallic inserts for mounting points
        for i in range(8):
            material_mgr.add_metallic_insert(
                location=(i * 0.7, 0, 0.5),
                insert_type="bolt",
                diameter=0.012,  # M12
                material="steel"
            )
        
        return material_mgr
    
    def _step6_optimization(self, design_space: np.ndarray,
                           load_manager: LoadCaseManager) -> TopologyOptimizer:
        """Step 6: Run topology optimization"""
        optimizer = TopologyOptimizer(self.config)
        self.results['optimizer'] = optimizer
        return optimizer
    
    def _step7_verification(self, geometry: np.ndarray) -> tuple:
        """Step 7: FEA and CFD verification"""
        # FEA
        fea = FEAVerification(
            geometry,
            {
                "tensile_strength": self.config.material.tensile_strength,
                "youngs_modulus": self.config.material.youngs_modulus,
            }
        )
        
        self.results['fea_static'] = fea.run_static_analysis({})
        self.results['fea_modal'] = fea.run_modal_analysis()
        self.results['fea_stiffness'] = fea.calculate_stiffness()
        
        # CFD
        cfd = CFDVerification(
            geometry,
            self.config.target_velocity,
            self.config.air_density
        )
        
        self.results['cfd_aero'] = cfd.run_aerodynamic_analysis()
        self.results['cfd_stability'] = cfd.calculate_stability_derivatives()
        
        return fea, cfd
    
    def _step8_manufacturability(self, geometry: np.ndarray) -> ManufacturabilityChecker:
        """Step 8: Check manufacturability"""
        checker = ManufacturabilityChecker(
            geometry,
            self.config.min_member_thickness
        )
        
        self.results['manufacturability'] = checker.validate_for_manufacturing()
        return checker
    
    def _step9_output(self, geometry: np.ndarray, output_dir: str) -> CADOutputGenerator:
        """Step 9: Generate CAD and documentation"""
        cad_gen = CADOutputGenerator(geometry, self.config.__dict__)
        
        # Generate complete manufacturing package
        package = cad_gen.generate_manufacturing_package(output_dir)
        self.results['manufacturing_package'] = package
        
        return cad_gen
