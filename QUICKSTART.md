# Quick Start Guide

## Baja 1000 Trophy Truck Chassis Optimizer

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/THEDIFY/ENG.git
cd ENG
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

### Running the Application

**Start the server (runs both backend and frontend on port 5000):**
```bash
python app.py
```

You should see:
```
Starting Baja 1000 Chassis Optimizer...
Access the application at: http://localhost:5000
 * Running on http://127.0.0.1:5000
```

### Testing the System

**Run the test suite:**
```bash
python test_system.py
```

This verifies:
- Material models
- Optimization engine
- Validation system
- CAD generation
- Report generation

### Using the Application

1. **Open your browser** and navigate to `http://localhost:5000`

2. **Enter Race Rules:**
   - Max Weight (kg): Chassis weight limit
   - Max Dimensions (m): Length, width, height constraints
   - Min Safety Factor: Structural safety requirement
   - Max Drag Coefficient: Aerodynamic target

3. **Specify Component Specs:**
   - Vehicle Mass (kg): Total estimated vehicle weight
   - Engine Power (HP): Engine horsepower
   - Suspension Travel (mm): Suspension stroke
   - Wheel Diameter (inches): Tire size

4. **Define Mission Profile:**
   - Max Speed (km/h): Target maximum speed
   - Race Duration (hours): Expected race length
   - Terrain Roughness: smooth/medium/rough/extreme
   - Primary Material: Carbon fiber type (T300/T800/M40J)

5. **Run Optimization:**
   - Click "Run Optimization"
   - Wait 1-2 minutes for analysis
   - Review results

6. **Download Files:**
   - 3D CAD Geometry (STL) - For CAD/CAM systems
   - Layup Schedule (JSON) - For manufacturing
   - Fastener Map (JSON) - For assembly
   - Validation Report (HTML) - Complete documentation

### Example Input Values

**Race Rules:**
- Max Weight: 1000 kg
- Max Length: 5.0 m
- Max Width: 2.2 m
- Max Height: 1.8 m
- Min Safety Factor: 2.0
- Max Drag Coefficient: 0.6

**Component Specs:**
- Vehicle Mass: 1500 kg
- Engine Power: 850 HP
- Suspension Travel: 450 mm
- Wheel Diameter: 37 inches

**Mission Profile:**
- Max Speed: 160 km/h
- Race Duration: 24 hours
- Terrain: medium
- Material: T800/Epoxy

### Output Files

**1. 3D CAD Geometry (STL)**
- Optimized chassis geometry
- Ready for CAD software import
- Can be used for CNC programming

**2. Layup Schedule (JSON)**
```json
{
  "sections": {
    "main_rails": {
      "layup_sequence": [0, 45, 90, -45, ...],
      "total_plies": 48,
      "thickness_mm": 6.0,
      "material": "T800/Epoxy"
    }
  }
}
```

**3. Fastener Map (JSON)**
```json
{
  "fasteners": [
    {
      "id": "RAIL_L_001",
      "location": [0.0, 0.2, 0.5],
      "type": "M10_Grade_12.9",
      "torque_Nm": 55
    }
  ]
}
```

**4. Validation Report (HTML)**
- Complete design summary
- Compliance verification
- Manufacturing notes
- Assembly instructions

### Troubleshooting

**Port 5000 already in use:**
```bash
# Edit app.py and change the port:
app.run(host='0.0.0.0', port=8080, debug=True)
```

**Module import errors:**
```bash
# Reinstall dependencies:
pip install -r requirements.txt --force-reinstall
```

**Optimization takes too long:**
The optimization uses 100 iterations by default. For faster results during testing, you can modify `engine/optimizer.py` and reduce `max_iterations` to 50.

### Technical Support

For issues or questions:
- Check the README.md for detailed documentation
- Review test_system.py for example usage
- Open an issue on GitHub

### Safety Notice

⚠️ **Important:** This is a design tool. All outputs must be reviewed by a qualified structural engineer before manufacturing. Physical testing and validation are required before use in competition.
