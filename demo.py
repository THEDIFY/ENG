#!/usr/bin/env python3
"""
Quick demonstration of the Topology Optimization System
Shows the complete workflow in action
"""

from topology_optimization import TopologyOptimizationWorkflow, OptimizationConfig
from topology_optimization.config import LoadCase

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║         TOPOLOGY OPTIMIZATION FOR CARBON FIBER TROPHY TRUCK CHASSIS          ║
║                        Baja 1000 Racing Application                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

This demo showcases the complete 9-step workflow for optimizing a carbon fiber
chassis design for extreme off-road racing conditions.
""")

# Create custom configuration for demonstration
print("Configuring optimization parameters...")
config = OptimizationConfig(
    chassis_length=5.8,
    chassis_width=2.35,
    chassis_height=2.1,
    target_weight_reduction=0.32,  # 32% weight reduction target
    max_drag_coefficient=0.33,
)

print(f"  ✓ Chassis dimensions: {config.chassis_length}m × {config.chassis_width}m × {config.chassis_height}m")
print(f"  ✓ Target weight reduction: {config.target_weight_reduction*100:.0f}%")
print(f"  ✓ Max drag coefficient: {config.max_drag_coefficient}")

# Add an extreme load case for desert racing
print("\nAdding custom extreme load case for desert terrain...")
desert_jump = LoadCase(
    name="Desert Jump Landing",
    load_type="impact",
    forces={
        "front_left": (0, 0, -55000),   # 55 kN vertical
        "front_right": (0, 0, -55000),
        "rear_left": (0, 0, -65000),    # 65 kN vertical (rear heavy)
        "rear_right": (0, 0, -65000),
    },
    safety_factor=2.8
)
config.load_cases.append(desert_jump)
print(f"  ✓ Added '{desert_jump.name}' with safety factor {desert_jump.safety_factor}")

# Create and run workflow
print("\nInitializing topology optimization workflow...\n")
workflow = TopologyOptimizationWorkflow(config)

# Run the complete optimization
results = workflow.run(output_dir="output/demo")

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           DEMONSTRATION COMPLETE                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

The optimized chassis design has been generated and validated!

Key Deliverables:
  📁 output/demo/chassis.step       - CAD model for manufacturing
  📁 output/demo/chassis.stl         - Mesh for visualization
  📁 output/demo/compliance_report.txt - Baja 1000 compliance
  📁 output/demo/README.txt          - Manufacturing instructions

Next Steps:
  1. Review the compliance report
  2. Load CAD files into your CAD/CAM system
  3. Review layup schedules for carbon fiber manufacturing
  4. Begin production with approved design

Thank you for using the Topology Optimization System!
""")
