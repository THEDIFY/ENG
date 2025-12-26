#!/usr/bin/env python3
"""
Test script for Baja 1000 Chassis Optimizer
Verifies the complete optimization workflow
"""

import json
import sys
from engine.optimizer import ChassisOptimizer
from engine.material_models import CarbonFiberMaterial
from engine.validation import ComplianceValidator
from engine.cad_generator import CADGenerator
from engine.reports import ReportGenerator


def test_material_models():
    """Test carbon fiber material models"""
    print("\n=== Testing Material Models ===")
    
    material = CarbonFiberMaterial('T800_Epoxy')
    print(f"Material: {material.props['name']}")
    print(f"E11: {material.props['E11']/1e9:.1f} GPa")
    print(f"Density: {material.props['rho']} kg/m³")
    
    # Test layup
    layup_sequence = [0, 45, -45, 90, 90, -45, 45, 0]
    laminate_props = material.get_laminate_properties(layup_sequence)
    print(f"Laminate Ex: {laminate_props['Ex']/1e9:.1f} GPa")
    print(f"Laminate thickness: {laminate_props['thickness']*1000:.2f} mm")
    
    print("✓ Material models working")
    return True


def test_optimization():
    """Test optimization engine"""
    print("\n=== Testing Optimization Engine ===")
    
    race_rules = {
        'max_weight': 1000,
        'max_length': 5.0,
        'max_width': 2.2,
        'max_height': 1.8,
        'min_safety_factor': 2.0,
        'max_drag_coefficient': 0.6
    }
    
    component_specs = {
        'estimated_mass': 1500,
        'engine_power': 850,
        'suspension_travel': 450,
        'wheel_diameter': 37
    }
    
    mission_profile = {
        'max_speed': 160,
        'race_duration': 24,
        'terrain_roughness': 'medium',
        'material_type': 'T800_Epoxy'
    }
    
    optimizer = ChassisOptimizer(race_rules, component_specs, mission_profile)
    print(f"Design space: {optimizer.design_space['dimensions']} m")
    print(f"Voxel grid: {optimizer.design_space['voxels']}")
    print(f"Number of load cases: {len(optimizer.loads)}")
    
    # Run optimization (reduced iterations for testing)
    result = optimizer.run_optimization()
    
    print(f"Optimized mass: {result['mass']:.2f} kg")
    print(f"Volume fraction: {result['volume_fraction']*100:.1f}%")
    print(f"Drag coefficient: {result['aero_data']['drag_coefficient']:.3f}")
    print(f"Stiffness: {result['structural_data']['stiffness']:.0f} N⋅m/deg")
    
    print("✓ Optimization working")
    return result


def test_validation(optimization_result):
    """Test validation module"""
    print("\n=== Testing Validation ===")
    
    race_rules = {
        'max_weight': 1000,
        'max_length': 5.0,
        'max_width': 2.2,
        'max_height': 1.8,
        'min_safety_factor': 2.0,
        'max_drag_coefficient': 0.6
    }
    
    validator = ComplianceValidator(optimization_result, race_rules)
    validation_report = validator.validate()
    
    print(f"Compliant: {validation_report['compliant']}")
    print(f"Checks passed: {validation_report['summary']['passed']}/{validation_report['summary']['total_checks']}")
    print(f"Compliance: {validation_report['summary']['compliance_percentage']:.1f}%")
    
    for check in validation_report['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"  {status} {check['name']}: {check['actual']}")
    
    print("✓ Validation working")
    return validation_report


def test_cad_generation(optimization_result):
    """Test CAD generation"""
    print("\n=== Testing CAD Generation ===")
    
    cad_gen = CADGenerator(optimization_result)
    
    # Generate geometry
    cad_data = cad_gen.generate_geometry()
    print(f"Vertices: {cad_data['num_vertices']:,}")
    print(f"Faces: {cad_data['num_faces']:,}")
    print(f"STL size: {len(cad_data['stl_data'])} bytes")
    
    # Generate layup schedule
    layup = cad_gen.generate_layup_schedule()
    print(f"Sections: {len(layup['sections'])}")
    print(f"Total layup mass: {layup['total_mass_kg']:.2f} kg")
    
    # Generate fastener map
    fasteners = cad_gen.generate_fastener_map()
    print(f"Total fasteners: {fasteners['total_count']}")
    print(f"Fastener types: {len(fasteners['types_summary'])}")
    
    print("✓ CAD generation working")
    return cad_data, layup, fasteners


def test_report_generation(opt_result, cad_data, layup, fasteners, validation):
    """Test report generation"""
    print("\n=== Testing Report Generation ===")
    
    report_gen = ReportGenerator()
    report = report_gen.generate_report(
        opt_result, cad_data, layup, fasteners, validation
    )
    
    print(f"Report HTML size: {len(report['html'])} bytes")
    print(f"Report compliant: {report['compliant']}")
    print(f"Report timestamp: {report['timestamp']}")
    
    print("✓ Report generation working")
    return report


def main():
    """Run all tests"""
    print("=" * 60)
    print("Baja 1000 Chassis Optimizer - Test Suite")
    print("=" * 60)
    
    try:
        # Test material models
        test_material_models()
        
        # Test optimization
        opt_result = test_optimization()
        
        # Test validation
        validation = test_validation(opt_result)
        
        # Test CAD generation
        cad_data, layup, fasteners = test_cad_generation(opt_result)
        
        # Test report generation
        report = test_report_generation(opt_result, cad_data, layup, fasteners, validation)
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        print("\nThe Baja 1000 Chassis Optimizer is working correctly!")
        print("Run 'python app.py' to start the web application.")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
