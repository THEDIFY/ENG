# System Architecture

## Baja 1000 Chassis Optimizer - Technical Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User Interface Layer                         │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  templates/index.html + static/css/style.css + static/js/app.js  │
│  │  • Race rules input form                                    │     │
│  │  • Component specifications                                 │     │
│  │  • Mission profile configuration                            │     │
│  │  • Results visualization                                    │     │
│  │  • Download management                                      │     │
│  └────────────────────────────────────────────────────────────┘     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTP (Port 5000)
┌──────────────────────────────┴──────────────────────────────────────┐
│                      Flask Application Layer (app.py)                │
│  ┌────────────────────┐  ┌────────────────────┐  ┌──────────────┐  │
│  │   Route: /         │  │ Route: /api/optimize│  │ Route: /api/ │  │
│  │   (Serve UI)       │  │ (Main optimization) │  │ download/*   │  │
│  └────────────────────┘  └────────────────────┘  └──────────────┘  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────┴──────────────────────────────────────┐
│                        Engine Layer (engine/)                        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  optimizer.py - ChassisOptimizer                              │  │
│  │  • Define design space (voxel grid)                          │  │
│  │  • Calculate load cases from mission profile                 │  │
│  │  • Run SIMP topology optimization (100 iterations)           │  │
│  │  • Calculate aerodynamics and structural properties          │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  material_models.py - CarbonFiberMaterial                     │  │
│  │  • Material database (T300, T800, M40J)                      │  │
│  │  • Classical Laminate Theory (CLT)                           │  │
│  │  • Tsai-Wu failure criterion                                 │  │
│  │  • Layup optimization recommendations                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  validation.py - ComplianceValidator                          │  │
│  │  • Weight compliance check                                   │  │
│  │  • Dimension validation                                      │  │
│  │  • Strength and stiffness verification                       │  │
│  │  • Safety factor calculation                                 │  │
│  │  • Aerodynamic efficiency check                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  cad_generator.py - CADGenerator                              │  │
│  │  • Voxel-to-mesh conversion (marching cubes)                 │  │
│  │  • STL file generation                                       │  │
│  │  • Layup schedule generation (5 sections)                    │  │
│  │  • Fastener map creation (62 fasteners)                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  reports.py - ReportGenerator                                 │  │
│  │  • Generate comprehensive HTML reports                       │  │
│  │  • Include all validation results                            │  │
│  │  • Manufacturing and assembly instructions                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                           Output Files                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐│
│  │ chassis_*.stl│  │layup_*.json  │  │fastener_*.json│  │report_*  ││
│  │ 3D CAD       │  │Carbon fiber  │  │Assembly specs │  │.html     ││
│  │ ~21k vertices│  │5 sections    │  │62 fasteners   │  │Complete  ││
│  │ ~42k faces   │  │Ply angles    │  │Torque specs   │  │validation││
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────┘│
└──────────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
User Input → Flask API → ChassisOptimizer
                              ↓
                    ┌─────────┴─────────┐
                    ↓                   ↓
            Material Models      Load Calculation
                    ↓                   ↓
            ┌───────┴───────────────────┴───────┐
            │   SIMP Topology Optimization      │
            │   • Initialize density field      │
            │   • Calculate compliance          │
            │   • Update densities (100 iter)   │
            │   • Apply filters                 │
            └───────────────┬───────────────────┘
                           ↓
                ┌──────────┴──────────┐
                ↓                     ↓
        Aero Analysis        Structural Analysis
                ↓                     ↓
                └──────────┬──────────┘
                           ↓
                   Optimization Result
                           ↓
        ┌──────────────────┼──────────────────┐
        ↓                  ↓                  ↓
  CADGenerator      Validator         ReportGenerator
        ↓                  ↓                  ↓
   STL + Layup      Compliance          HTML Report
    + Fasteners       Checks
        ↓                  ↓                  ↓
        └──────────────────┴──────────────────┘
                           ↓
                    User Downloads
```

## Key Technologies

**Backend:**
- Python 3.8+
- Flask 3.0.0 (Web framework)
- NumPy 2.4.0 (Array operations, optimization)
- SciPy 1.16.3 (Gaussian filtering, algorithms)
- Trimesh 4.10.1 (3D mesh operations)

**Frontend:**
- HTML5 (Structure)
- CSS3 (Styling, gradients, responsive grid)
- JavaScript (ES6+) (Async API calls, DOM manipulation)

**Algorithms:**
1. **SIMP (Solid Isotropic Material with Penalization)**
   - Density-based topology optimization
   - Penalty factor: 3.0
   - Optimality criteria update

2. **Classical Laminate Theory**
   - ABD matrix calculation
   - Effective moduli computation
   - Ply-by-ply analysis

3. **Tsai-Wu Failure Criterion**
   - Composite failure prediction
   - Stress transformation
   - Safety factor calculation

4. **Marching Cubes (Simplified)**
   - Voxel-to-mesh conversion
   - Surface extraction
   - Mesh smoothing

## Performance Characteristics

**Time Complexity:**
- Optimization: O(n × iterations) where n = voxel count
- CAD Generation: O(m) where m = surface voxels
- Validation: O(1) constant time checks

**Space Complexity:**
- Design space: O(nx × ny × nz) = O(250 × 110 × 90) ≈ 2.5M voxels
- Mesh storage: O(vertices + faces) ≈ 60k elements

**Typical Performance:**
- Optimization: 60-90 seconds
- CAD generation: 5-10 seconds
- Report generation: < 1 second
- Total workflow: ~2 minutes

## Deployment

**Single Port Architecture:**
```
Port 5000
    ├── Static files (CSS, JS)
    ├── Templates (HTML)
    ├── API endpoints (/api/*)
    └── File downloads (/api/download/*)
```

**No External Dependencies:**
- No database required
- No external API calls
- No cloud services
- Runs completely offline

## Security Considerations

- Input validation on all user inputs
- File size limits (16 MB)
- Output sanitization
- No code execution from user input
- Temporary file cleanup
- Session-based result caching

## Extensibility Points

1. **New Materials:** Add to CarbonFiberMaterial.MATERIALS
2. **New Load Cases:** Extend _calculate_loads()
3. **New Validation Checks:** Add methods to ComplianceValidator
4. **Output Formats:** Extend CADGenerator for STEP, IGES, etc.
5. **Optimization Algorithms:** Replace SIMP with BESO, level-set, etc.

## Testing

**test_system.py covers:**
- Material model calculations
- Optimization convergence
- Validation logic
- CAD generation
- Report creation

**Run tests:**
```bash
python test_system.py
```

**Expected output:**
- ✓ Material models working
- ✓ Optimization working
- ✓ Validation working
- ✓ CAD generation working
- ✓ Report generation working
