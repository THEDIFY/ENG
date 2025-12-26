"""
Component placement module
Defines bounding boxes and keep-out zones for vehicle components
"""

from typing import List, Dict, Tuple
import numpy as np
from .config import ComponentBounds


class ComponentPlacer:
    """Manages component placement and packaging constraints"""
    
    def __init__(self, chassis_dims: Tuple[float, float, float]):
        """
        Initialize component placer
        
        Args:
            chassis_dims: (length, width, height) in meters
        """
        self.chassis_length, self.chassis_width, self.chassis_height = chassis_dims
        self.components: List[ComponentBounds] = []
        self.keep_out_zones: List[ComponentBounds] = []
    
    def add_component(self, component: ComponentBounds) -> None:
        """Add a component with its bounding box"""
        if not self._validate_bounds(component):
            raise ValueError(f"Component {component.name} exceeds chassis boundaries")
        self.components.append(component)
    
    def add_keep_out_zone(self, zone: ComponentBounds) -> None:
        """Add a keep-out zone where material cannot be placed"""
        self.keep_out_zones.append(zone)
    
    def _validate_bounds(self, component: ComponentBounds) -> bool:
        """Validate component fits within chassis"""
        return (
            0 <= component.x_min < component.x_max <= self.chassis_length and
            -self.chassis_width/2 <= component.y_min < component.y_max <= self.chassis_width/2 and
            0 <= component.z_min < component.z_max <= self.chassis_height
        )
    
    def check_interference(self) -> List[Tuple[str, str]]:
        """
        Check for interference between components
        
        Returns:
            List of component pairs with interference
        """
        interferences = []
        for i, comp1 in enumerate(self.components):
            for comp2 in self.components[i+1:]:
                if self._boxes_overlap(comp1, comp2):
                    interferences.append((comp1.name, comp2.name))
        return interferences
    
    def _boxes_overlap(self, box1: ComponentBounds, box2: ComponentBounds) -> bool:
        """Check if two bounding boxes overlap"""
        return (
            box1.x_min < box2.x_max and box1.x_max > box2.x_min and
            box1.y_min < box2.y_max and box1.y_max > box2.y_min and
            box1.z_min < box2.z_max and box1.z_max > box2.z_min
        )
    
    def get_design_space(self, resolution: int = 50) -> np.ndarray:
        """
        Generate design space as a 3D grid
        
        Args:
            resolution: Grid resolution per dimension
            
        Returns:
            3D numpy array where 1 = design space, 0 = keep-out
        """
        # Create mesh grid
        x = np.linspace(0, self.chassis_length, resolution)
        y = np.linspace(-self.chassis_width/2, self.chassis_width/2, resolution)
        z = np.linspace(0, self.chassis_height, resolution)
        
        # Initialize design space (all available)
        design_space = np.ones((resolution, resolution, resolution))
        
        # Mark keep-out zones
        for zone in self.keep_out_zones + self.components:
            for i, xi in enumerate(x):
                for j, yj in enumerate(y):
                    for k, zk in enumerate(z):
                        if (zone.x_min <= xi <= zone.x_max and
                            zone.y_min <= yj <= zone.y_max and
                            zone.z_min <= zk <= zone.z_max):
                            design_space[i, j, k] = 0
        
        return design_space
    
    def get_packaging_summary(self) -> Dict:
        """Get summary of component packaging"""
        total_volume = self.chassis_length * self.chassis_width * self.chassis_height
        occupied_volume = sum(comp.volume() for comp in self.components)
        
        return {
            "total_chassis_volume": total_volume,
            "occupied_volume": occupied_volume,
            "available_volume": total_volume - occupied_volume,
            "utilization_ratio": occupied_volume / total_volume,
            "num_components": len(self.components),
            "num_keep_out_zones": len(self.keep_out_zones),
            "component_list": [comp.name for comp in self.components],
        }
