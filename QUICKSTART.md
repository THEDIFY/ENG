# Quick Start Guide - Topology Optimization System

## Installation

```bash
pip install -r requirements.txt
```

## Basic Usage

### Run Default Configuration
```python
from topology_optimization import TopologyOptimizationWorkflow

workflow = TopologyOptimizationWorkflow()
results = workflow.run(output_dir="output")
```

### Run Example Scripts
```bash
python examples.py basic      # Default configuration
python examples.py custom     # Custom chassis dimensions
python examples.py advanced   # Advanced material configuration
python examples.py all        # Run all examples
```

## Key Outputs

After running, check the `output/` directory for:
- `chassis.step` - CAD file (STEP format)
- `chassis.stl` - Mesh visualization
- `chassis.iges` - Alternative CAD format
- `compliance_report.txt` - Baja 1000 compliance
- `README.txt` - Manufacturing package overview

## Workflow Steps

The system executes 9 steps automatically:

1. **Rules Ingestion** - Load Baja 1000 regulations
2. **Component Placement** - Position engine, suspension, etc.
3. **Design Space Generation** - Create optimization domain
4. **Load Case Setup** - Define structural loads
5. **Material Assignment** - Configure carbon fiber layups
6. **Topology Optimization** - Run SIMP optimizer
7. **FEA & CFD Verification** - Structural and aero analysis
8. **Manufacturability Checks** - Validate for production
9. **CAD Output** - Generate manufacturing files

## Custom Configuration Example

```python
from topology_optimization import OptimizationConfig, TopologyOptimizationWorkflow
from topology_optimization.config import LoadCase

# Create custom config
config = OptimizationConfig(
    chassis_length=6.0,              # meters
    chassis_width=2.4,               # meters
    target_weight_reduction=0.35,    # 35%
    max_drag_coefficient=0.32,       # lower drag
)

# Add custom load case
config.load_cases.append(
    LoadCase(
        name="Extreme Jump",
        load_type="impact",
        forces={"front_left": (0, 0, -70000)},  # Newtons
        safety_factor=3.0
    )
)

# Run workflow
workflow = TopologyOptimizationWorkflow(config)
results = workflow.run(output_dir="output/custom")
```

## Key Results Explained

### Structural Performance
- **Safety Factor**: Ratio of material strength to max stress (>1.5 recommended)
- **Torsional Stiffness**: Chassis rigidity in Nm/degree (higher is stiffer)
- **Weight Reduction**: Percentage of mass removed vs. solid baseline

### Aerodynamic Performance
- **Drag Coefficient**: Lower is better (target: <0.35)
- **Drag Force**: Total aerodynamic drag in Newtons

### Compliance
- **Baja 1000 Compliant**: Pass/fail for race regulations
- **Manufacturing Ready**: Pass/fail for production feasibility

## Troubleshooting

### Import Errors
```bash
pip install -r requirements.txt
```

### Missing scipy
```bash
pip install scipy
```

### Missing numpy
```bash
pip install numpy
```

## File Structure

```
ENG/
├── topology_optimization/     # Main package
│   ├── workflow.py           # Orchestrates all steps
│   ├── config.py             # Configuration classes
│   ├── optimizer.py          # SIMP optimization engine
│   └── ...                   # Other modules
├── examples.py               # Example usage scripts
├── requirements.txt          # Dependencies
├── README.md                 # Full documentation
└── DOCUMENTATION.md          # Technical details
```

## Next Steps

1. Run basic example: `python examples.py basic`
2. Review output files in `output/basic_example/`
3. Customize configuration for your needs
4. Review compliance report
5. Use CAD files for manufacturing

## Support

For detailed documentation, see:
- `README.md` - Complete feature list and usage
- `DOCUMENTATION.md` - Technical methodology and math
- Problem statement - Original design requirements

For issues, open a GitHub issue with:
- Your configuration
- Error messages
- Expected vs. actual behavior
