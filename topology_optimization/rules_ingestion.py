"""
Rules ingestion module for Baja 1000 regulations
Parses and validates race regulations for dimensional and safety constraints
"""

from typing import Dict, List, Optional
import json
from dataclasses import asdict


class Baja1000Rules:
    """Parser and validator for Baja 1000 race regulations"""
    
    def __init__(self):
        self.rules = self._load_default_rules()
    
    def _load_default_rules(self) -> Dict:
        """Load default Baja 1000 regulations"""
        return {
            "dimensional_constraints": {
                "max_overall_length": 6.1,  # meters
                "max_overall_width": 2.5,  # meters
                "max_overall_height": 2.5,  # meters
                "min_ground_clearance": 0.35,  # meters
                "max_wheelbase": 4.0,  # meters
                "min_wheelbase": 2.4,  # meters
            },
            "safety_requirements": {
                "roll_cage_mandatory": True,
                "min_roll_cage_tube_diameter": 0.0381,  # 1.5 inches in meters
                "min_roll_cage_wall_thickness": 0.00254,  # 0.1 inches in meters
                "safety_harness_points": 5,  # minimum 5-point harness
                "fire_suppression_required": True,
                "safety_cell_required": True,
                "min_safety_cell_volume": 1.5,  # cubic meters
            },
            "suspension_requirements": {
                "min_suspension_travel": 0.254,  # 10 inches in meters
                "max_suspension_travel": 0.762,  # 30 inches in meters
                "shock_absorbers_required": True,
            },
            "weight_constraints": {
                "min_weight": 1360,  # kg (3000 lbs)
                "max_weight": None,  # No maximum
                "weight_distribution_front": (0.40, 0.60),  # 40-60% front
            },
            "structural_requirements": {
                "chassis_material_approved": ["steel", "chromoly", "carbon_fiber", "aluminum"],
                "min_structural_thickness": 0.003,  # 3mm
                "weld_certification_required": True,
            },
            "aerodynamic_constraints": {
                "max_frontal_area": 4.0,  # square meters
                "wing_restrictions": True,
                "underbody_aero_allowed": True,
            }
        }
    
    def load_from_file(self, filepath: str) -> None:
        """Load rules from JSON file"""
        with open(filepath, 'r') as f:
            self.rules = json.load(f)
    
    def validate_design(self, design_params: Dict) -> Dict[str, List[str]]:
        """
        Validate design parameters against Baja 1000 rules
        
        Args:
            design_params: Dictionary of design parameters to validate
            
        Returns:
            Dictionary with 'passed' and 'violations' lists
        """
        violations = []
        passed = []
        
        # Check dimensional constraints
        dim_rules = self.rules["dimensional_constraints"]
        if "length" in design_params:
            if design_params["length"] > dim_rules["max_overall_length"]:
                violations.append(
                    f"Length {design_params['length']}m exceeds maximum "
                    f"{dim_rules['max_overall_length']}m"
                )
            else:
                passed.append("Length within regulations")
        
        if "width" in design_params:
            if design_params["width"] > dim_rules["max_overall_width"]:
                violations.append(
                    f"Width {design_params['width']}m exceeds maximum "
                    f"{dim_rules['max_overall_width']}m"
                )
            else:
                passed.append("Width within regulations")
        
        if "ground_clearance" in design_params:
            if design_params["ground_clearance"] < dim_rules["min_ground_clearance"]:
                violations.append(
                    f"Ground clearance {design_params['ground_clearance']}m "
                    f"below minimum {dim_rules['min_ground_clearance']}m"
                )
            else:
                passed.append("Ground clearance meets requirements")
        
        # Check safety requirements
        safety_rules = self.rules["safety_requirements"]
        if "safety_cell_volume" in design_params:
            if design_params["safety_cell_volume"] < safety_rules["min_safety_cell_volume"]:
                violations.append(
                    f"Safety cell volume {design_params['safety_cell_volume']}m³ "
                    f"below minimum {safety_rules['min_safety_cell_volume']}m³"
                )
            else:
                passed.append("Safety cell volume adequate")
        
        # Check material constraints
        struct_rules = self.rules["structural_requirements"]
        if "chassis_material" in design_params:
            if design_params["chassis_material"] not in struct_rules["chassis_material_approved"]:
                violations.append(
                    f"Chassis material '{design_params['chassis_material']}' not approved. "
                    f"Approved materials: {struct_rules['chassis_material_approved']}"
                )
            else:
                passed.append("Chassis material approved")
        
        if "min_thickness" in design_params:
            if design_params["min_thickness"] < struct_rules["min_structural_thickness"]:
                violations.append(
                    f"Minimum thickness {design_params['min_thickness']}m "
                    f"below required {struct_rules['min_structural_thickness']}m"
                )
            else:
                passed.append("Structural thickness meets requirements")
        
        return {
            "passed": passed,
            "violations": violations,
            "compliant": len(violations) == 0
        }
    
    def get_constraints(self) -> Dict:
        """Get all constraints for optimization"""
        return self.rules
    
    def export_compliance_report(self, validation_results: Dict, filepath: str) -> None:
        """Export compliance report to file"""
        with open(filepath, 'w') as f:
            json.dump(validation_results, f, indent=2)
