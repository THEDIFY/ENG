"""
Topology Optimization System for Carbon Fiber Trophy Truck Chassis
Designed for Baja 1000 Racing Applications
"""

__version__ = "1.0.0"
__author__ = "ENG Team"

from .workflow import TopologyOptimizationWorkflow
from .config import OptimizationConfig

__all__ = [
    "TopologyOptimizationWorkflow",
    "OptimizationConfig",
]
