"""
Example usage of the Topology Optimization Workflow
For Baja 1000 Carbon Fiber Trophy Truck Chassis
"""

from topology_optimization import TopologyOptimizationWorkflow, OptimizationConfig
from topology_optimization.config import MaterialProperties, ComponentBounds, LoadCase


def run_basic_example():
    """Run workflow with default configuration"""
    print("Running basic topology optimization example...")
    
    # Use default configuration
    workflow = TopologyOptimizationWorkflow()
    
    # Run complete workflow
    results = workflow.run(output_dir="output/basic_example")
    
    print("\n" + "=" * 80)
    print("BASIC EXAMPLE COMPLETE")
    print("=" * 80)
    print(f"Check output files in: output/basic_example/")
    
    return results


def run_custom_example():
    """Run workflow with custom configuration"""
    print("Running custom topology optimization example...")
    
    # Create custom configuration
    config = OptimizationConfig(
        chassis_length=6.0,  # Longer chassis
        chassis_width=2.4,
        chassis_height=2.1,
        target_weight_reduction=0.35,  # Target 35% weight reduction
        max_drag_coefficient=0.32,  # Lower drag target
    )
    
    # Add custom load case
    extreme_landing = LoadCase(
        name="Extreme Landing",
        load_type="impact",
        forces={
            "front_left": (0, 0, -60000),
            "front_right": (0, 0, -60000),
            "rear_left": (0, 0, -70000),
            "rear_right": (0, 0, -70000),
        },
        safety_factor=3.0
    )
    config.load_cases.append(extreme_landing)
    
    # Create and run workflow
    workflow = TopologyOptimizationWorkflow(config)
    results = workflow.run(output_dir="output/custom_example")
    
    print("\n" + "=" * 80)
    print("CUSTOM EXAMPLE COMPLETE")
    print("=" * 80)
    print(f"Check output files in: output/custom_example/")
    
    return results


def run_advanced_example():
    """Run workflow with advanced customization"""
    print("Running advanced topology optimization example...")
    
    # Create advanced configuration
    config = OptimizationConfig()
    
    # Custom material properties for high-modulus carbon fiber
    config.material = MaterialProperties(
        name="High-Modulus Carbon Fiber",
        youngs_modulus=200e9,  # Higher modulus
        density=1550,  # Slightly lower density
        tensile_strength=700e6,  # Higher strength
    )
    
    # Add additional components
    config.components.append(
        ComponentBounds("Shock Tower Front", 0.5, 0.9, -0.8, 0.8, 0.8, 1.4)
    )
    config.components.append(
        ComponentBounds("Shock Tower Rear", 4.8, 5.1, -0.8, 0.8, 0.8, 1.4)
    )
    
    # Create workflow and run
    workflow = TopologyOptimizationWorkflow(config)
    results = workflow.run(output_dir="output/advanced_example")
    
    print("\n" + "=" * 80)
    print("ADVANCED EXAMPLE COMPLETE")
    print("=" * 80)
    print(f"Check output files in: output/advanced_example/")
    
    # Print detailed results
    print("\nDetailed Results:")
    print(f"  FEA Max Stress: {results['fea_static']['max_von_mises_stress']/1e6:.2f} MPa")
    print(f"  FEA Safety Factor: {results['fea_static']['safety_factor']:.2f}")
    print(f"  Torsional Stiffness: {results['fea_stiffness']['torsional_stiffness']:.1f} Nm/deg")
    print(f"  First Natural Frequency: {results['fea_modal']['first_natural_frequency']:.1f} Hz")
    print(f"  Drag Coefficient: {results['cfd_aero']['drag_coefficient']:.3f}")
    print(f"  Drag Force at 100mph: {results['cfd_aero']['drag_force']:.1f} N")
    
    return results


if __name__ == "__main__":
    import sys
    
    print("=" * 80)
    print("TOPOLOGY OPTIMIZATION FOR BAJA 1000 CARBON FIBER CHASSIS")
    print("Example Demonstrations")
    print("=" * 80)
    print()
    
    # Determine which example to run
    if len(sys.argv) > 1:
        example_type = sys.argv[1].lower()
    else:
        example_type = "basic"
    
    if example_type == "basic":
        run_basic_example()
    elif example_type == "custom":
        run_custom_example()
    elif example_type == "advanced":
        run_advanced_example()
    elif example_type == "all":
        print("Running all examples...\n")
        run_basic_example()
        print("\n\n")
        run_custom_example()
        print("\n\n")
        run_advanced_example()
    else:
        print(f"Unknown example type: {example_type}")
        print("Usage: python examples.py [basic|custom|advanced|all]")
        print("  basic    - Run with default configuration")
        print("  custom   - Run with custom configuration")
        print("  advanced - Run with advanced material and component customization")
        print("  all      - Run all examples")
        sys.exit(1)
    
    print("\n✓ All examples completed successfully!")
