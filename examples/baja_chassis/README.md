# Example Baja 1000 Trophy Truck Chassis Project

This directory contains an example project configuration for topology optimization of a carbon fiber trophy truck chassis.

## Files

- `project.json` - Complete project configuration with all settings
- `layup_schedule.csv` - Example layup schedule output (generated after optimization)

## Configuration Overview

### Vehicle Specifications
- Wheelbase: 3000mm
- Width: 2000mm
- Ground clearance: 254mm minimum

### Components
- LS3 V8 Engine (180 kg)
- 4L80E Transmission (75 kg)
- 55 Gallon FIA Fuel Cell (45 kg empty)
- Dual Pass Radiator
- Driver and Co-Driver Seats

### Load Cases
1. Maximum Vertical: 5g landing from jump
2. Maximum Lateral: 2g cornering
3. Maximum Braking: 1.5g deceleration
4. Front Impact: 15 m/s collision
5. Rollover Crush: FIA-style roof load

### Material
- Primary: T700S/Epoxy UD carbon fiber
- Properties:
  - E1 = 165 GPa (fiber direction)
  - E2 = 10.5 GPa (transverse)
  - Xt = 2550 MPa (tensile strength)
  - Density = 1570 kg/m³
  - Ply thickness = 0.14mm

### Manufacturing Constraints
- Allowed ply angles: [0°, ±45°, 90°]
- Symmetric and balanced layup required
- Maximum 4 consecutive same-angle plies
- Maximum shear angle for drapability: 45°
- Minimum internal radius: 10mm

### Optimization Settings
- Method: SIMP
- Target volume fraction: 30%
- Penalty factor: 3.0
- Filter radius: 2.0 elements
- Max iterations: 200
- Aero coupling enabled

## Running the Example

1. Start the application:
   ```bash
   docker-compose up -d
   ```

2. Open the web interface at http://localhost:3000

3. Create a new project and import `project.json`

4. Click "Run Optimization" to start

5. Monitor progress in real-time

6. After completion, review:
   - Structural validation results
   - Aerodynamic performance
   - Manufacturing feasibility
   - Export CAD and documentation

## Expected Results

After optimization, you should see:
- Optimized topology with ~30% material volume
- Primary load paths through chassis
- Compliance with all Baja 1000 rules
- Manufacturable composite layup schedule
- Technical report with validation results
