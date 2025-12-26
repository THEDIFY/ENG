# Baja 1000 Trophy Truck Chassis Optimizer

A comprehensive local application for optimizing trophy truck chassis designs for the Baja 1000 race. This system uses topology optimization with aerodynamic and structural stability targets to generate manufacturable carbon fiber chassis designs.

## Features

- **Topology Optimization**: SIMP (Solid Isotropic Material with Penalization) method for optimal material distribution
- **Carbon Fiber Material Models**: Multiple material options (T300, T800, M40J) with laminate theory calculations
- **Load Analysis**: Comprehensive load case generation from mission profiles
- **Aerodynamics**: Drag coefficient calculation and optimization
- **Structural Analysis**: Stiffness, strength, and safety factor calculations
- **Compliance Validation**: Automatic checking against race rules and safety requirements
- **CAD Generation**: Manufacturable 3D geometry output in STL format
- **Layup Schedules**: Detailed carbon fiber layup specifications for each chassis section
- **Fastener Maps**: Complete fastener specifications with locations and torque requirements
- **Validation Reports**: Comprehensive HTML reports with all design details

## Installation

1. Clone the repository:
```bash
git clone https://github.com/THEDIFY/ENG.git
cd ENG
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Start the server (runs both backend and frontend on the same port):

```bash
python app.py
```

The application will be available at: **http://localhost:5000**

## Usage

1. Open your web browser and navigate to `http://localhost:5000`
2. Enter race rules and constraints (max weight, dimensions, safety factors)
3. Specify component specifications (vehicle mass, engine power, suspension)
4. Define mission profile (speed, terrain, duration, material)
5. Click "Run Optimization" to start the analysis
6. Review results and download generated files (CAD, layup schedules, fastener maps, reports)

## Architecture

### Backend (Python/Flask)
- **app.py**: Main Flask application serving both API and frontend
- **engine/optimizer.py**: Topology optimization engine
- **engine/material_models.py**: Carbon fiber composite material properties
- **engine/validation.py**: Compliance checking against race rules
- **engine/cad_generator.py**: 3D CAD geometry and manufacturing data generation
- **engine/reports.py**: HTML report generation

### Frontend (HTML/CSS/JavaScript)
- **templates/index.html**: Main UI template
- **static/css/style.css**: Responsive styling
- **static/js/app.js**: Client-side logic and API interaction

## Technical Details

### Optimization Method
- SIMP (Solid Isotropic Material with Penalization)
- Density-based topology optimization
- Voxel-based design space representation
- Optimality criteria update method

### Material Modeling
- Classical Laminate Theory (CLT)
- Tsai-Wu failure criterion
- Orthotropic material properties

## Requirements

- Python 3.8+
- Flask 3.0.0
- NumPy 1.24.3
- SciPy 1.11.4

## Safety Notice

⚠️ **Important**: This tool provides design suggestions based on engineering principles. All designs should be reviewed by a qualified structural engineer before manufacturing.

## License

See LICENSE file for details.

## Version

1.0.0 - Initial Release
