"""
Design space generation module
Establishes keep-in and keep-out zones for topology optimization
"""

import numpy as np
from typing import List, Tuple, Dict
from .config import ComponentBounds


class DesignSpaceGenerator:
    """Generates and manages the design space for topology optimization"""
    
    def __init__(self, dimensions: Tuple[float, float, float], resolution: int = 50):
        """
        Initialize design space generator
        
        Args:
            dimensions: (length, width, height) in meters
            resolution: Grid resolution per dimension
        """
        self.length, self.width, self.height = dimensions
        self.resolution = resolution
        self.design_space = None
        self.keep_in_zones: List[ComponentBounds] = []
        self.keep_out_zones: List[ComponentBounds] = []
    
    def add_keep_in_zone(self, zone: ComponentBounds) -> None:
        """Add zone where material must be present (e.g., load points)"""
        self.keep_in_zones.append(zone)
    
    def add_keep_out_zone(self, zone: ComponentBounds) -> None:
        """Add zone where material cannot be placed"""
        self.keep_out_zones.append(zone)
    
    def generate_space(self) -> np.ndarray:
        """
        Generate the design space with constraints
        
        Returns:
            3D array: -1 = keep-out, 0 = available, 1 = keep-in
        """
        x = np.linspace(0, self.length, self.resolution)
        y = np.linspace(-self.width/2, self.width/2, self.resolution)
        z = np.linspace(0, self.height, self.resolution)
        
        # Initialize with available space (0)
        space = np.zeros((self.resolution, self.resolution, self.resolution))
        
        # Mark keep-out zones (-1)
        for zone in self.keep_out_zones:
            for i, xi in enumerate(x):
                for j, yj in enumerate(y):
                    for k, zk in enumerate(z):
                        if (zone.x_min <= xi <= zone.x_max and
                            zone.y_min <= yj <= zone.y_max and
                            zone.z_min <= zk <= zone.z_max):
                            space[i, j, k] = -1
        
        # Mark keep-in zones (1)
        for zone in self.keep_in_zones:
            for i, xi in enumerate(x):
                for j, yj in enumerate(y):
                    for k, zk in enumerate(z):
                        if (zone.x_min <= xi <= zone.x_max and
                            zone.y_min <= yj <= zone.y_max and
                            zone.z_min <= zk <= zone.z_max):
                            space[i, j, k] = 1
        
        self.design_space = space
        return space
    
    def add_symmetry_constraint(self, plane: str = 'xy') -> None:
        """
        Add symmetry constraint to design space
        
        Args:
            plane: Symmetry plane ('xy', 'xz', or 'yz')
        """
        if self.design_space is None:
            self.generate_space()
        
        if plane == 'xy':
            # Mirror across XY plane (bilateral symmetry)
            mid = self.resolution // 2
            self.design_space[:, mid:, :] = self.design_space[:, :mid, :][:, ::-1, :]
        elif plane == 'xz':
            # Mirror across XZ plane
            mid = self.resolution // 2
            self.design_space[:, :, mid:] = self.design_space[:, :, :mid][:, :, ::-1]
    
    def get_volume_fraction(self) -> Dict[str, float]:
        """Calculate volume fractions of design space"""
        if self.design_space is None:
            self.generate_space()
        
        total = self.design_space.size
        keep_out = np.sum(self.design_space == -1)
        keep_in = np.sum(self.design_space == 1)
        available = np.sum(self.design_space == 0)
        
        return {
            "keep_out_fraction": keep_out / total,
            "keep_in_fraction": keep_in / total,
            "available_fraction": available / total,
            "total_elements": total,
        }
    
    def export_to_stl(self, filepath: str, threshold: float = 0.5) -> None:
        """
        Export design space boundaries to STL file
        
        Args:
            filepath: Output STL file path
            threshold: Density threshold for surface extraction
        """
        # Placeholder for STL export functionality
        # In production, use libraries like numpy-stl or trimesh
        pass
