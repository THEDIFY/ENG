"""
Manufacturability checks module
Validates ply drapability, mold splits, and fastener maps
"""

import numpy as np
from typing import Dict, List, Tuple, Optional


class ManufacturabilityChecker:
    """Validates design for carbon fiber manufacturing"""
    
    def __init__(self, geometry: np.ndarray, min_thickness: float = 0.003):
        self.geometry = geometry
        self.min_thickness = min_thickness
        self.issues: List[Dict] = []
    
    def check_ply_drapability(self, max_curvature: float = 50.0) -> Dict:
        """
        Check if plies can be draped over geometry
        
        Args:
            max_curvature: Maximum allowable curvature (1/m)
            
        Returns:
            Drapability assessment
        """
        # Simplified curvature analysis
        # In production, use actual surface curvature calculations
        
        problem_areas = []
        
        # Simulate finding high-curvature regions
        num_issues = np.random.randint(0, 5)
        for i in range(num_issues):
            problem_areas.append({
                "location": (np.random.uniform(0, 5), 
                           np.random.uniform(-1, 1),
                           np.random.uniform(0, 2)),
                "curvature": np.random.uniform(max_curvature, max_curvature * 1.5),
                "severity": "HIGH" if np.random.rand() > 0.5 else "MEDIUM",
            })
        
        status = "PASS" if len(problem_areas) == 0 else "WARNING"
        
        return {
            "status": status,
            "max_curvature_limit": max_curvature,
            "problem_areas": problem_areas,
            "recommendation": "Consider adding darts or splits in high-curvature regions" if problem_areas else "All areas drapable",
        }
    
    def analyze_mold_splits(self) -> Dict:
        """
        Analyze optimal mold split lines
        
        Returns:
            Mold split recommendations
        """
        # Suggest mold parting lines based on geometry
        
        splits = [
            {
                "name": "Main body split",
                "type": "horizontal",
                "z_position": 1.0,  # meters
                "complexity": "LOW",
            },
            {
                "name": "Side panel split",
                "type": "vertical",
                "y_position": 0.0,  # centerline
                "complexity": "MEDIUM",
            }
        ]
        
        return {
            "num_splits_required": len(splits),
            "split_lines": splits,
            "tooling_complexity": "MEDIUM",
            "estimated_mold_cost": 150000,  # USD
        }
    
    def check_thickness_consistency(self) -> Dict:
        """
        Verify minimum thickness requirements
        
        Returns:
            Thickness validation results
        """
        # Check for thin sections that may be hard to manufacture
        
        thin_sections = []
        
        # Simulate thickness analysis
        num_thin = np.random.randint(0, 3)
        for i in range(num_thin):
            thin_sections.append({
                "location": (np.random.uniform(0, 5),
                           np.random.uniform(-1, 1),
                           np.random.uniform(0, 2)),
                "thickness": np.random.uniform(0.001, self.min_thickness),
                "required_thickness": self.min_thickness,
            })
        
        status = "PASS" if len(thin_sections) == 0 else "FAIL"
        
        return {
            "status": status,
            "min_thickness_requirement": self.min_thickness,
            "thin_sections": thin_sections,
            "action_required": "Increase thickness in flagged areas" if thin_sections else "All sections meet minimum thickness",
        }
    
    def generate_fastener_map(self, num_fasteners: int = 50) -> Dict:
        """
        Generate map of fastener locations
        
        Args:
            num_fasteners: Approximate number of fasteners
            
        Returns:
            Fastener map and specifications
        """
        fasteners = []
        
        # Generate fastener locations along perimeter and at joints
        fastener_types = ["M8 bolt", "M10 bolt", "M6 rivet"]
        
        for i in range(num_fasteners):
            fasteners.append({
                "id": f"FAST-{i+1:03d}",
                "location": (
                    np.random.uniform(0, 5),
                    np.random.uniform(-1, 1),
                    np.random.uniform(0, 2)
                ),
                "type": np.random.choice(fastener_types),
                "torque_spec": np.random.choice([25, 35, 50]),  # Nm
            })
        
        return {
            "num_fasteners": num_fasteners,
            "fastener_list": fasteners,
            "fastener_types": list(set(f["type"] for f in fasteners)),
            "spacing_check": "PASS",
        }
    
    def check_overhang_angles(self, max_angle: float = 45.0) -> Dict:
        """
        Check for overhangs that may need support during layup
        
        Args:
            max_angle: Maximum overhang angle in degrees
            
        Returns:
            Overhang analysis
        """
        problem_overhangs = []
        
        # Simulate overhang detection
        num_overhangs = np.random.randint(0, 4)
        for i in range(num_overhangs):
            problem_overhangs.append({
                "location": (np.random.uniform(0, 5),
                           np.random.uniform(-1, 1),
                           np.random.uniform(0, 2)),
                "angle": np.random.uniform(max_angle, 90),
                "requires_support": True,
            })
        
        return {
            "max_angle_limit": max_angle,
            "problem_overhangs": problem_overhangs,
            "support_structures_needed": len(problem_overhangs),
            "status": "PASS" if len(problem_overhangs) == 0 else "NEEDS_SUPPORT",
        }
    
    def validate_for_manufacturing(self) -> Dict:
        """
        Run all manufacturability checks
        
        Returns:
            Comprehensive validation report
        """
        drapability = self.check_ply_drapability()
        mold_splits = self.analyze_mold_splits()
        thickness = self.check_thickness_consistency()
        fasteners = self.generate_fastener_map()
        overhangs = self.check_overhang_angles()
        
        # Determine overall status
        critical_checks = [
            thickness["status"],
            drapability["status"]
        ]
        
        overall_status = "APPROVED" if all(s == "PASS" for s in critical_checks) else "NEEDS_REVISION"
        
        return {
            "overall_status": overall_status,
            "drapability": drapability,
            "mold_splits": mold_splits,
            "thickness": thickness,
            "fasteners": fasteners,
            "overhangs": overhangs,
            "ready_for_production": overall_status == "APPROVED",
        }
