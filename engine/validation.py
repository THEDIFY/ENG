"""
Validation module for compliance checking
Ensures design meets race rules and safety requirements
"""

import numpy as np


class ComplianceValidator:
    """Validates chassis design against race rules and safety standards"""
    
    def __init__(self, optimization_result, race_rules):
        """
        Initialize validator
        
        optimization_result: dict from optimizer
        race_rules: dict with race requirements
        """
        self.result = optimization_result
        self.rules = race_rules
        
    def validate(self):
        """
        Run all validation checks
        Returns validation report with compliance status
        """
        checks = []
        
        # Weight check
        checks.append(self._check_weight())
        
        # Dimension check
        checks.append(self._check_dimensions())
        
        # Strength check
        checks.append(self._check_strength())
        
        # Stiffness check
        checks.append(self._check_stiffness())
        
        # Safety factor check
        checks.append(self._check_safety_factor())
        
        # Aerodynamic efficiency check
        checks.append(self._check_aero_efficiency())
        
        # Durability check
        checks.append(self._check_durability())
        
        # Overall compliance
        all_passed = all(check['passed'] for check in checks)
        
        return {
            'compliant': all_passed,
            'checks': checks,
            'summary': self._generate_summary(checks)
        }
    
    def _check_weight(self):
        """Check if chassis mass is within limits"""
        max_weight = self.rules.get('max_weight', 1000)  # kg
        actual_weight = self.result['mass']
        
        passed = actual_weight <= max_weight
        
        return {
            'name': 'Weight Compliance',
            'passed': passed,
            'required': f"≤ {max_weight} kg",
            'actual': f"{actual_weight:.2f} kg",
            'margin': f"{max_weight - actual_weight:.2f} kg",
            'severity': 'critical' if not passed else 'pass'
        }
    
    def _check_dimensions(self):
        """Check if dimensions are within limits"""
        max_length = self.rules.get('max_length', 5.0)  # m
        max_width = self.rules.get('max_width', 2.2)    # m
        max_height = self.rules.get('max_height', 1.8)  # m
        
        dims = self.result['design_space']['dimensions']
        
        passed = (dims[0] <= max_length and 
                 dims[1] <= max_width and 
                 dims[2] <= max_height)
        
        return {
            'name': 'Dimension Compliance',
            'passed': passed,
            'required': f"L≤{max_length}m, W≤{max_width}m, H≤{max_height}m",
            'actual': f"L={dims[0]:.2f}m, W={dims[1]:.2f}m, H={dims[2]:.2f}m",
            'severity': 'critical' if not passed else 'pass'
        }
    
    def _check_strength(self):
        """Check if strength requirements are met"""
        max_allowed_stress = self.rules.get('max_stress', 400e6)  # Pa
        actual_stress = self.result['structural_data']['max_stress']
        
        passed = actual_stress <= max_allowed_stress
        
        return {
            'name': 'Strength Requirements',
            'passed': passed,
            'required': f"Max stress ≤ {max_allowed_stress/1e6:.0f} MPa",
            'actual': f"{actual_stress/1e6:.0f} MPa",
            'margin': f"{(max_allowed_stress - actual_stress)/1e6:.0f} MPa",
            'severity': 'critical' if not passed else 'pass'
        }
    
    def _check_stiffness(self):
        """Check if stiffness requirements are met"""
        min_stiffness = self.rules.get('min_torsional_stiffness', 15000)  # N⋅m/deg
        actual_stiffness = self.result['structural_data']['stiffness']
        
        passed = actual_stiffness >= min_stiffness
        
        return {
            'name': 'Torsional Stiffness',
            'passed': passed,
            'required': f"≥ {min_stiffness} N⋅m/deg",
            'actual': f"{actual_stiffness:.0f} N⋅m/deg",
            'margin': f"{actual_stiffness - min_stiffness:.0f} N⋅m/deg",
            'severity': 'high' if not passed else 'pass'
        }
    
    def _check_safety_factor(self):
        """Check if safety factor is adequate"""
        min_safety_factor = self.rules.get('min_safety_factor', 2.0)
        actual_sf = self.result['structural_data']['min_safety_factor']
        
        passed = actual_sf >= min_safety_factor
        
        return {
            'name': 'Safety Factor',
            'passed': passed,
            'required': f"≥ {min_safety_factor}",
            'actual': f"{actual_sf:.2f}",
            'margin': f"{actual_sf - min_safety_factor:.2f}",
            'severity': 'critical' if not passed else 'pass'
        }
    
    def _check_aero_efficiency(self):
        """Check aerodynamic efficiency"""
        max_drag_coeff = self.rules.get('max_drag_coefficient', 0.6)
        actual_cd = self.result['aero_data']['drag_coefficient']
        
        passed = actual_cd <= max_drag_coeff
        
        return {
            'name': 'Drag Efficiency',
            'passed': passed,
            'required': f"Cd ≤ {max_drag_coeff}",
            'actual': f"Cd = {actual_cd:.3f}",
            'margin': f"{max_drag_coeff - actual_cd:.3f}",
            'severity': 'medium' if not passed else 'pass'
        }
    
    def _check_durability(self):
        """Check durability requirements"""
        max_deflection = self.rules.get('max_deflection', 0.020)  # m
        actual_deflection = self.result['structural_data']['max_deflection']
        
        passed = actual_deflection <= max_deflection
        
        return {
            'name': 'Deflection/Durability',
            'passed': passed,
            'required': f"Max deflection ≤ {max_deflection*1000:.0f} mm",
            'actual': f"{actual_deflection*1000:.1f} mm",
            'margin': f"{(max_deflection - actual_deflection)*1000:.1f} mm",
            'severity': 'medium' if not passed else 'pass'
        }
    
    def _generate_summary(self, checks):
        """Generate summary of validation results"""
        total_checks = len(checks)
        passed_checks = sum(1 for c in checks if c['passed'])
        failed_checks = total_checks - passed_checks
        
        critical_failures = [c for c in checks if not c['passed'] and c['severity'] == 'critical']
        
        return {
            'total_checks': total_checks,
            'passed': passed_checks,
            'failed': failed_checks,
            'critical_failures': len(critical_failures),
            'compliance_percentage': (passed_checks / total_checks) * 100
        }
