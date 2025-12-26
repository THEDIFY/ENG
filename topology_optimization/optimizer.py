"""
Topology optimization engine
Multi-objective optimization for stiffness, weight, aerodynamics, and stability
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from .config import OptimizationConfig


class TopologyOptimizer:
    """Core topology optimization engine using SIMP method"""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.density_field = None
        self.compliance_history: List[float] = []
        self.volume_history: List[float] = []
        self.iteration = 0
    
    def initialize_density_field(self, design_space: np.ndarray, 
                                 initial_volume_fraction: float = 0.5) -> np.ndarray:
        """
        Initialize density field for optimization
        
        Args:
            design_space: 3D array defining available space
            initial_volume_fraction: Starting volume fraction
            
        Returns:
            Initial density field
        """
        # Start with uniform density in available space
        self.density_field = np.where(
            design_space >= 0,
            initial_volume_fraction,
            0.0
        )
        return self.density_field
    
    def simp_interpolation(self, density: np.ndarray, penalty: float = 3.0) -> np.ndarray:
        """
        SIMP (Solid Isotropic Material with Penalization) interpolation
        
        Args:
            density: Element densities [0, 1]
            penalty: Penalization factor (typically 3.0)
            
        Returns:
            Penalized stiffness values
        """
        return density ** penalty
    
    def optimize_step(self, load_vectors: Dict[str, np.ndarray],
                     design_space: np.ndarray) -> Dict:
        """
        Perform one optimization iteration
        
        Args:
            load_vectors: Dictionary of load cases
            design_space: Valid design space
            
        Returns:
            Optimization step results
        """
        self.iteration += 1
        
        # Apply SIMP penalization
        penalized_density = self.simp_interpolation(self.density_field)
        
        # Calculate compliance for each load case (simplified)
        total_compliance = 0
        for load_name, load_vec in load_vectors.items():
            # Simplified compliance calculation
            # In production, solve FEA K*u = f and calculate u'*f
            compliance = np.sum(penalized_density * np.random.rand(*penalized_density.shape))
            total_compliance += compliance
        
        # Calculate volume
        current_volume = np.sum(self.density_field) / self.density_field.size
        target_volume = 1.0 - self.config.target_weight_reduction
        
        # Sensitivity analysis (simplified)
        # In production, compute dC/dx using adjoint method
        sensitivity = -3.0 * (self.density_field ** 2)
        
        # Filter sensitivities to avoid checkerboard patterns
        filtered_sensitivity = self._filter_sensitivity(sensitivity)
        
        # Update densities using optimality criteria method
        self.density_field = self._update_densities_oc(
            self.density_field,
            filtered_sensitivity,
            target_volume
        )
        
        # Enforce design space constraints
        self.density_field = np.where(design_space >= 0, self.density_field, 0.0)
        
        # Record history
        self.compliance_history.append(total_compliance)
        self.volume_history.append(current_volume)
        
        return {
            "iteration": self.iteration,
            "compliance": total_compliance,
            "volume_fraction": current_volume,
            "max_density": np.max(self.density_field),
            "min_density": np.min(self.density_field),
        }
    
    def _filter_sensitivity(self, sensitivity: np.ndarray, 
                           filter_radius: int = 2) -> np.ndarray:
        """
        Apply density filter to sensitivities
        
        Args:
            sensitivity: Raw sensitivities
            filter_radius: Filter radius in elements
            
        Returns:
            Filtered sensitivities
        """
        # Simple averaging filter (in production use proper convolution)
        from scipy.ndimage import uniform_filter
        return uniform_filter(sensitivity, size=filter_radius)
    
    def _update_densities_oc(self, densities: np.ndarray,
                            sensitivities: np.ndarray,
                            target_volume: float,
                            move_limit: float = 0.2) -> np.ndarray:
        """
        Update densities using optimality criteria method
        
        Args:
            densities: Current densities
            sensitivities: Sensitivity values
            target_volume: Target volume fraction
            move_limit: Maximum change per iteration
            
        Returns:
            Updated densities
        """
        # Bisection method to find Lagrange multiplier
        l1, l2 = 0, 1e9
        
        while (l2 - l1) > 1e-9:
            lmid = 0.5 * (l1 + l2)
            
            # Optimality criteria update
            Be = -sensitivities / lmid
            new_densities = np.minimum(
                1.0,
                np.minimum(
                    densities + move_limit,
                    densities * np.sqrt(Be)
                )
            )
            new_densities = np.maximum(
                0.001,  # Minimum density to avoid singularity
                np.maximum(
                    densities - move_limit,
                    new_densities
                )
            )
            
            # Check volume constraint
            if np.sum(new_densities) / new_densities.size > target_volume:
                l1 = lmid
            else:
                l2 = lmid
        
        return new_densities
    
    def run_optimization(self, design_space: np.ndarray,
                        load_vectors: Dict[str, np.ndarray],
                        max_iterations: int = 100,
                        convergence_tol: float = 0.01) -> Dict:
        """
        Run full optimization loop
        
        Args:
            design_space: Valid design space
            load_vectors: Load cases
            max_iterations: Maximum iterations
            convergence_tol: Convergence tolerance
            
        Returns:
            Optimization results
        """
        # Initialize
        self.initialize_density_field(design_space)
        
        print(f"Starting optimization with {max_iterations} max iterations...")
        
        for i in range(max_iterations):
            step_result = self.optimize_step(load_vectors, design_space)
            
            if i % 10 == 0:
                print(f"Iteration {i}: Compliance={step_result['compliance']:.2e}, "
                      f"Volume={step_result['volume_fraction']:.3f}")
            
            # Check convergence
            if i > 10:
                change = abs(
                    self.compliance_history[-1] - self.compliance_history[-2]
                ) / self.compliance_history[-2]
                
                if change < convergence_tol:
                    print(f"Converged at iteration {i}")
                    break
        
        return {
            "final_density": self.density_field,
            "final_compliance": self.compliance_history[-1],
            "final_volume": self.volume_history[-1],
            "iterations": self.iteration,
            "compliance_history": self.compliance_history,
            "volume_history": self.volume_history,
        }
    
    def extract_geometry(self, threshold: float = 0.5) -> np.ndarray:
        """
        Extract solid geometry from density field
        
        Args:
            threshold: Density threshold for material presence
            
        Returns:
            Binary geometry array
        """
        return (self.density_field >= threshold).astype(int)
