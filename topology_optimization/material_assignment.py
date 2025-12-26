"""
Material assignment module
Handles carbon fiber laminates with metallic inserts
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from .config import MaterialProperties


class MaterialAssignment:
    """Manages material properties and layup schedules"""
    
    def __init__(self, primary_material: MaterialProperties):
        self.primary_material = primary_material
        self.layup_regions: Dict[str, Dict] = {}
        self.metallic_inserts: List[Dict] = []
    
    def define_layup_region(self, region_name: str, 
                           ply_orientations: List[float],
                           num_plies: int) -> None:
        """
        Define a laminate layup region
        
        Args:
            region_name: Identifier for the region
            ply_orientations: List of ply angles in degrees [0, 45, -45, 90]
            num_plies: Number of plies in the laminate
        """
        self.layup_regions[region_name] = {
            "orientations": ply_orientations,
            "num_plies": num_plies,
            "thickness": num_plies * self.primary_material.ply_thickness,
            "stacking_sequence": self._generate_stacking_sequence(
                ply_orientations, num_plies
            )
        }
    
    def _generate_stacking_sequence(self, orientations: List[float], 
                                   num_plies: int) -> List[float]:
        """
        Generate symmetric stacking sequence
        
        Args:
            orientations: Available ply angles
            num_plies: Total number of plies
            
        Returns:
            Symmetric stacking sequence
        """
        # Create balanced, symmetric layup
        half_plies = num_plies // 2
        sequence = []
        
        for i in range(half_plies):
            sequence.append(orientations[i % len(orientations)])
        
        # Mirror for symmetry
        sequence = sequence + sequence[::-1]
        
        # Add middle ply if odd number
        if num_plies % 2 == 1:
            sequence.insert(half_plies, orientations[0])
        
        return sequence
    
    def add_metallic_insert(self, location: Tuple[float, float, float],
                           insert_type: str, diameter: float,
                           material: str = "steel") -> None:
        """
        Add metallic insert for bolted joints
        
        Args:
            location: (x, y, z) position
            insert_type: 'bolt', 'rivet', 'bushing'
            diameter: Insert diameter in meters
            material: 'steel', 'aluminum', 'titanium'
        """
        insert = {
            "location": location,
            "type": insert_type,
            "diameter": diameter,
            "material": material,
            "properties": self._get_metal_properties(material)
        }
        self.metallic_inserts.append(insert)
    
    def _get_metal_properties(self, material: str) -> Dict:
        """Get material properties for metallic inserts"""
        metal_props = {
            "steel": {
                "youngs_modulus": 200e9,
                "density": 7850,
                "yield_strength": 250e6,
            },
            "aluminum": {
                "youngs_modulus": 69e9,
                "density": 2700,
                "yield_strength": 276e6,
            },
            "titanium": {
                "youngs_modulus": 116e9,
                "density": 4500,
                "yield_strength": 880e6,
            }
        }
        return metal_props.get(material, metal_props["steel"])
    
    def calculate_laminate_properties(self, region_name: str) -> Dict:
        """
        Calculate effective laminate properties using Classical Laminate Theory
        
        Args:
            region_name: Name of the layup region
            
        Returns:
            Dictionary of effective properties
        """
        if region_name not in self.layup_regions:
            raise ValueError(f"Region {region_name} not defined")
        
        region = self.layup_regions[region_name]
        sequence = region["stacking_sequence"]
        
        # Simplified CLT - in production use full ABD matrix
        E_eff = self.primary_material.youngs_modulus
        rho_eff = self.primary_material.density
        
        # Account for ply orientations (simplified)
        num_0_deg = sum(1 for angle in sequence if angle == 0)
        num_90_deg = sum(1 for angle in sequence if angle == 90)
        num_45_deg = sum(1 for angle in sequence if abs(angle) == 45)
        
        total = len(sequence)
        
        return {
            "effective_E_x": E_eff * (num_0_deg / total),
            "effective_E_y": E_eff * (num_90_deg / total),
            "effective_G_xy": self.primary_material.shear_modulus * (num_45_deg / total),
            "effective_density": rho_eff,
            "thickness": region["thickness"],
            "num_plies": region["num_plies"],
        }
    
    def get_material_summary(self) -> Dict:
        """Get summary of material assignments"""
        total_insert_mass = sum(
            np.pi * (insert["diameter"]/2)**2 * 0.01 *  # Assume 10mm height
            insert["properties"]["density"]
            for insert in self.metallic_inserts
        )
        
        return {
            "primary_material": self.primary_material.name,
            "num_layup_regions": len(self.layup_regions),
            "num_metallic_inserts": len(self.metallic_inserts),
            "total_insert_mass": total_insert_mass,
            "layup_regions": list(self.layup_regions.keys()),
        }
    
    def export_layup_schedule(self, filepath: str) -> None:
        """Export layup schedule for manufacturing"""
        import json
        
        schedule = {
            "material": {
                "name": self.primary_material.name,
                "ply_thickness": self.primary_material.ply_thickness,
                "density": self.primary_material.density,
            },
            "regions": {}
        }
        
        for name, region in self.layup_regions.items():
            schedule["regions"][name] = {
                "stacking_sequence": region["stacking_sequence"],
                "total_thickness": region["thickness"],
                "num_plies": region["num_plies"],
            }
        
        schedule["metallic_inserts"] = self.metallic_inserts
        
        with open(filepath, 'w') as f:
            json.dump(schedule, f, indent=2)
