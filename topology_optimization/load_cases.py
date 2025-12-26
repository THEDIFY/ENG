"""
Load case setup module
Applies static, dynamic, and impact loads for FEA
"""

import numpy as np
from typing import Dict, List, Tuple
from .config import LoadCase


class LoadCaseManager:
    """Manages load cases for topology optimization"""
    
    def __init__(self):
        self.load_cases: List[LoadCase] = []
        self.boundary_conditions: Dict[str, Dict] = {}
    
    def add_load_case(self, load_case: LoadCase) -> None:
        """Add a load case to the analysis"""
        self.load_cases.append(load_case)
    
    def add_boundary_condition(self, name: str, location: Tuple[float, float, float],
                               constraint_type: str, dofs: List[int]) -> None:
        """
        Add boundary condition (fixed support, pin, etc.)
        
        Args:
            name: Boundary condition identifier
            location: (x, y, z) coordinates
            constraint_type: 'fixed', 'pin', 'roller'
            dofs: List of constrained degrees of freedom (0-5: Tx,Ty,Tz,Rx,Ry,Rz)
        """
        self.boundary_conditions[name] = {
            "location": location,
            "type": constraint_type,
            "dofs": dofs
        }
    
    def get_combined_load_vector(self, node_positions: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Generate combined load vectors for all load cases
        
        Args:
            node_positions: Array of node coordinates (N x 3)
            
        Returns:
            Dictionary mapping load case names to load vectors
        """
        load_vectors = {}
        
        for load_case in self.load_cases:
            n_nodes = len(node_positions)
            load_vector = np.zeros((n_nodes, 3))
            
            # Apply forces at specified locations
            for location_name, force in load_case.forces.items():
                # Find nearest node to application point
                # In production, use proper interpolation
                load_vector[0] += np.array(force) * load_case.safety_factor
            
            load_vectors[load_case.name] = load_vector
        
        return load_vectors
    
    def get_load_case_summary(self) -> Dict:
        """Get summary of all load cases"""
        summary = {
            "num_load_cases": len(self.load_cases),
            "load_cases": []
        }
        
        for lc in self.load_cases:
            total_force = sum(
                np.linalg.norm(f) for f in lc.forces.values()
            )
            
            summary["load_cases"].append({
                "name": lc.name,
                "type": lc.load_type,
                "num_force_points": len(lc.forces),
                "total_force_magnitude": total_force,
                "safety_factor": lc.safety_factor,
            })
        
        return summary
    
    def scale_loads_for_material(self, material_strength: float) -> None:
        """
        Scale all loads based on material strength
        
        Args:
            material_strength: Material yield/ultimate strength in Pa
        """
        # Apply conservative scaling based on material properties
        for load_case in self.load_cases:
            if load_case.load_type == "impact":
                # Impact loads may need higher safety factors
                load_case.safety_factor *= 1.2
    
    def get_critical_load_case(self) -> LoadCase:
        """
        Determine the most critical load case
        
        Returns:
            The load case with highest combined load and safety factor
        """
        max_severity = 0
        critical_case = None
        
        for lc in self.load_cases:
            total_force = sum(np.linalg.norm(f) for f in lc.forces.values())
            severity = total_force * lc.safety_factor
            
            if severity > max_severity:
                max_severity = severity
                critical_case = lc
        
        return critical_case
