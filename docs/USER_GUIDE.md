# User Guide

## Trophy Truck Topology Optimizer

### Introduction

This application helps you design optimized carbon fiber trophy truck chassis for the Baja 1000 using topology optimization techniques. The workflow guides you through:

1. Setting up Baja 1000 rules and constraints
2. Placing components (engine, transmission, fuel cell, etc.)
3. Defining the design space and load cases
4. Running multi-objective topology optimization
5. Validating the design against structural, aero, and manufacturing requirements
6. Exporting manufacturable outputs

### Getting Started

#### Dashboard

The dashboard provides an overview of your projects and quick access to common actions:

- **Create New Project**: Start a new topology optimization project
- **Configure Baja Rules**: Set up Baja 1000 rules and constraints
- **Material Library**: Manage carbon fiber material properties

#### Creating a Project

1. Navigate to **Projects** in the sidebar
2. Click **New Project**
3. Enter a project name and description
4. Click **Create Project**

### Workflow Steps

#### Step 1: Parse Baja 1000 Rules

Navigate to **Rules** to configure the Baja 1000 constraints:

- **Safety Equipment**: Roll cage, fire suppression, fuel cell requirements
- **Dimensional Limits**: Width, length, ground clearance, wheelbase
- **Suspension**: Wheel travel, shock absorber requirements
- **Engine/Drivetrain**: Displacement limits, drive type options
- **Weight**: Minimum race weight with driver and co-driver

Review each category and confirm the constraints apply to your design. You can add custom constraints or override specific rules.

#### Step 2: Place Components

Define the position and envelope of major components:

- **Engine**: Location, size, mounting points
- **Transmission**: Position relative to engine
- **Fuel Cell**: Required clearances and access
- **Radiator**: Cooling airflow path requirements
- **Driver/Co-driver Seats**: Safety cell requirements
- **Suspension Pickups**: A-arm and shock mounting locations

Each component creates a keep-out zone in the design space.

#### Step 3: Generate Design Space

The design space is automatically generated based on:

- Vehicle dimensional constraints
- Component envelopes and clearances
- Access corridors for maintenance
- Symmetry requirements

You can manually adjust:

- **Minimum Member Size**: Controls feature resolution
- **Maximum Member Size**: Prevents overly coarse structure
- **Keep-out Zones**: Add custom exclusion regions

#### Step 4: Define Load Cases

Standard Baja load cases are pre-configured:

| Load Case | Description |
|-----------|-------------|
| Maximum Vertical | 5g landing from jump |
| Maximum Lateral | 2g cornering |
| Maximum Braking | 1.5g hard braking |
| Combined Jump Landing | Multi-axis impact |
| Rollover | FIA crush load on roll cage |

Add custom load cases for specific scenarios (e.g., rock impacts, side hits).

#### Step 5: Assign Materials

Select carbon fiber materials from the library:

- **T300/Epoxy**: Standard modulus, balanced properties
- **T700S/Epoxy**: Intermediate modulus, higher strength
- **M55J/Epoxy**: High modulus, stiffer but more brittle
- **Woven Carbon/Epoxy**: Good for complex geometry, lower strength

Configure manufacturing constraints:

- **Allowed Ply Angles**: Typically [0°, 45°, -45°, 90°]
- **Symmetry**: Enforce symmetric layup about midplane
- **Balance**: Equal +θ and -θ plies
- **Maximum Consecutive**: Limit same-angle ply stacking

#### Step 6: Run Optimization

Configure optimization parameters:

| Parameter | Description | Typical Value |
|-----------|-------------|---------------|
| Method | SIMP or Level-Set | SIMP |
| Volume Fraction | Target material usage | 0.3 (30%) |
| Penalty Factor | SIMP penalization | 3.0 |
| Filter Radius | Feature size control | 2.0 elements |
| Max Iterations | Convergence limit | 200 |
| Convergence Tolerance | Stopping criterion | 0.01 |

Enable **Aero Coupling** to include drag/lift optimization.

Click **Start Optimization** to begin. Monitor progress in real-time:

- Iteration count
- Compliance (lower is stiffer)
- Volume fraction
- Convergence metric

#### Step 7: Validate Design

After optimization, the design is validated against:

**Structural Checks:**
- Maximum displacement under each load case
- Maximum stress vs. allowable
- Buckling safety factor
- Modal frequencies (minimum first mode)

**Aerodynamic Checks:**
- Drag coefficient
- Lift/downforce balance
- Side-wind stability
- Cooling flow adequacy

**Manufacturing Checks:**
- Drapability (max shear angle)
- Ply rule compliance
- Mold split feasibility
- Insert edge distances

Review any violations and modify the design as needed.

#### Step 8: Export Outputs

Generate final deliverables:

**CAD Geometry:**
- STEP (native CAD exchange)
- IGES (legacy compatibility)
- STL (3D printing, CFD meshing)
- glTF (web visualization)

**Manufacturing Data:**
- Layup schedules (CSV/JSON)
- Fastener maps
- Insert locations
- Bond line definitions

**Documentation:**
- Bill of Materials (BOM)
- Technical validation report (PDF)
- Baja 1000 compliance checklist

### Tips and Best Practices

1. **Start with higher volume fraction** (40-50%) to ensure connectivity, then reduce

2. **Use SIMP for initial exploration**, level-set for final refinement

3. **Check drapability early** - complex surfaces may need design changes

4. **Review ply drops** - excessive drops create stress concentrations

5. **Validate cooling flow** - ensure radiator inlet has adequate pressure

6. **Consider access** - leave room for wiring, fluid lines, maintenance

### Troubleshooting

**Optimization not converging:**
- Increase filter radius
- Reduce move limit
- Check for disconnected regions

**Low safety factor:**
- Increase volume fraction
- Use higher-strength material
- Add local reinforcement

**Drapability violations:**
- Add relief darts
- Modify surface curvature
- Consider preform segmentation

**Modal frequency too low:**
- Add stiffness in weak directions
- Increase laminate thickness
- Check for flexible joints

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+S` | Save project |
| `Ctrl+R` | Run optimization |
| `Ctrl+E` | Export outputs |
| `Space` | Pause/resume optimization |
| `Esc` | Cancel current operation |

### 3D Viewer Controls

- **Left-click + drag**: Rotate view
- **Right-click + drag**: Pan view
- **Scroll wheel**: Zoom in/out
- **Double-click**: Reset view
