"""
Baja 1000 Trophy Truck Chassis Optimization Application
Main Flask application serving both backend API and frontend UI
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from datetime import datetime
from engine.optimizer import ChassisOptimizer
from engine.material_models import CarbonFiberMaterial
from engine.validation import ComplianceValidator
from engine.cad_generator import CADGenerator
from engine.reports import ReportGenerator

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Store optimization results temporarily
optimization_cache = {}


@app.route('/')
def index():
    """Main application page"""
    return render_template('index.html')


@app.route('/api/optimize', methods=['POST'])
def optimize_chassis():
    """
    Main optimization endpoint
    Expects JSON with race_rules, component_specs, and mission_profile
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not all(key in data for key in ['race_rules', 'component_specs', 'mission_profile']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Initialize optimizer
        optimizer = ChassisOptimizer(
            race_rules=data['race_rules'],
            component_specs=data['component_specs'],
            mission_profile=data['mission_profile']
        )
        
        # Run optimization
        optimization_result = optimizer.run_optimization()
        
        # Generate CAD geometry
        cad_generator = CADGenerator(optimization_result)
        cad_data = cad_generator.generate_geometry()
        
        # Generate layup schedules
        layup_schedule = cad_generator.generate_layup_schedule()
        
        # Generate fastener map
        fastener_map = cad_generator.generate_fastener_map()
        
        # Run validation
        validator = ComplianceValidator(
            optimization_result,
            data['race_rules']
        )
        validation_report = validator.validate()
        
        # Generate comprehensive report
        report_gen = ReportGenerator()
        report_data = report_gen.generate_report(
            optimization_result,
            cad_data,
            layup_schedule,
            fastener_map,
            validation_report
        )
        
        # Cache results with unique ID
        result_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        optimization_cache[result_id] = {
            'optimization': optimization_result,
            'cad': cad_data,
            'layup': layup_schedule,
            'fasteners': fastener_map,
            'validation': validation_report,
            'report': report_data
        }
        
        return jsonify({
            'success': True,
            'result_id': result_id,
            'summary': {
                'mass': optimization_result['mass'],
                'compliance': validation_report['compliant'],
                'drag_coefficient': optimization_result['aero_data']['drag_coefficient'],
                'safety_factor': optimization_result['structural_data']['min_safety_factor'],
                'stiffness': optimization_result['structural_data']['stiffness']
            },
            'validation': validation_report,
            'download_links': {
                'cad': f'/api/download/cad/{result_id}',
                'layup': f'/api/download/layup/{result_id}',
                'fasteners': f'/api/download/fasteners/{result_id}',
                'report': f'/api/download/report/{result_id}'
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/<file_type>/<result_id>')
def download_file(file_type, result_id):
    """Download generated files"""
    try:
        if result_id not in optimization_cache:
            return jsonify({'error': 'Result not found'}), 404
        
        result = optimization_cache[result_id]
        output_dir = 'outputs'
        os.makedirs(output_dir, exist_ok=True)
        
        if file_type == 'cad':
            filepath = os.path.join(output_dir, f'chassis_{result_id}.stl')
            with open(filepath, 'w') as f:
                f.write(result['cad']['stl_data'])
            return send_file(filepath, as_attachment=True, download_name=f'chassis_{result_id}.stl')
        
        elif file_type == 'layup':
            filepath = os.path.join(output_dir, f'layup_schedule_{result_id}.json')
            with open(filepath, 'w') as f:
                json.dump(result['layup'], f, indent=2)
            return send_file(filepath, as_attachment=True, download_name=f'layup_schedule_{result_id}.json')
        
        elif file_type == 'fasteners':
            filepath = os.path.join(output_dir, f'fastener_map_{result_id}.json')
            with open(filepath, 'w') as f:
                json.dump(result['fasteners'], f, indent=2)
            return send_file(filepath, as_attachment=True, download_name=f'fastener_map_{result_id}.json')
        
        elif file_type == 'report':
            filepath = os.path.join(output_dir, f'validation_report_{result_id}.html')
            with open(filepath, 'w') as f:
                f.write(result['report']['html'])
            return send_file(filepath, as_attachment=True, download_name=f'validation_report_{result_id}.html')
        
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/materials')
def get_materials():
    """Get available carbon fiber material properties"""
    materials = CarbonFiberMaterial.get_available_materials()
    return jsonify(materials)


if __name__ == '__main__':
    # Ensure outputs directory exists
    os.makedirs('outputs', exist_ok=True)
    
    # Run on single port for both frontend and backend
    # Note: Debug mode is enabled for development. 
    # For production deployment, set debug=False and use a production WSGI server like gunicorn
    print("Starting Baja 1000 Chassis Optimizer...")
    print("Access the application at: http://localhost:5000")
    print("")
    print("WARNING: Running in development mode. For production use, set debug=False")
    print("         and use a production WSGI server (e.g., gunicorn, waitress)")
    
    # Get debug mode from environment variable, default to False for security
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
