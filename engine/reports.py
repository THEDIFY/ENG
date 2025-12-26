"""
Report generator for validation and documentation
Creates comprehensive HTML reports
"""

from datetime import datetime


class ReportGenerator:
    """Generates validation and manufacturing reports"""
    
    def generate_report(self, optimization_result, cad_data, layup_schedule, 
                       fastener_map, validation_report):
        """
        Generate comprehensive HTML report
        
        Returns dict with HTML and summary data
        """
        html = self._create_html_report(
            optimization_result,
            cad_data,
            layup_schedule,
            fastener_map,
            validation_report
        )
        
        return {
            'html': html,
            'timestamp': datetime.now().isoformat(),
            'compliant': validation_report['compliant']
        }
    
    def _create_html_report(self, opt_result, cad_data, layup, fasteners, validation):
        """Create detailed HTML report"""
        
        # Header
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Baja 1000 Chassis Validation Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 4px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        .status {{
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
            font-weight: bold;
            font-size: 1.2em;
        }}
        .status.pass {{
            background: #d4edda;
            color: #155724;
            border: 2px solid #28a745;
        }}
        .status.fail {{
            background: #f8d7da;
            color: #721c24;
            border: 2px solid #dc3545;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #3498db;
            color: white;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .metric {{
            display: inline-block;
            margin: 10px 20px 10px 0;
            padding: 15px;
            background: #ecf0f1;
            border-radius: 5px;
            min-width: 200px;
        }}
        .metric-label {{
            font-size: 0.9em;
            color: #7f8c8d;
            text-transform: uppercase;
        }}
        .metric-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #2c3e50;
        }}
        .check-pass {{
            color: #28a745;
            font-weight: bold;
        }}
        .check-fail {{
            color: #dc3545;
            font-weight: bold;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #ecf0f1;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Baja 1000 Trophy Truck Chassis Optimization Report</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="status {'pass' if validation['compliant'] else 'fail'}">
            Overall Compliance: {'✓ PASSED' if validation['compliant'] else '✗ FAILED'}
        </div>
"""
        
        # Summary metrics
        html += """
        <h2>Design Summary</h2>
        <div>
            <div class="metric">
                <div class="metric-label">Total Mass</div>
                <div class="metric-value">{:.2f} kg</div>
            </div>
            <div class="metric">
                <div class="metric-label">Volume Fraction</div>
                <div class="metric-value">{:.1f}%</div>
            </div>
            <div class="metric">
                <div class="metric-label">Drag Coefficient</div>
                <div class="metric-value">{:.3f}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Safety Factor</div>
                <div class="metric-value">{:.2f}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Torsional Stiffness</div>
                <div class="metric-value">{:.0f} N⋅m/deg</div>
            </div>
        </div>
        """.format(
            opt_result['mass'],
            opt_result['volume_fraction'] * 100,
            opt_result['aero_data']['drag_coefficient'],
            opt_result['structural_data']['min_safety_factor'],
            opt_result['structural_data']['stiffness']
        )
        
        # Validation checks
        html += """
        <h2>Compliance Validation</h2>
        <table>
            <tr>
                <th>Check</th>
                <th>Status</th>
                <th>Required</th>
                <th>Actual</th>
                <th>Margin</th>
            </tr>
        """
        
        for check in validation['checks']:
            status_class = 'check-pass' if check['passed'] else 'check-fail'
            status_text = '✓ Pass' if check['passed'] else '✗ Fail'
            
            html += f"""
            <tr>
                <td>{check['name']}</td>
                <td class="{status_class}">{status_text}</td>
                <td>{check['required']}</td>
                <td>{check['actual']}</td>
                <td>{check.get('margin', 'N/A')}</td>
            </tr>
            """
        
        html += """
        </table>
        """
        
        # Layup schedule summary
        html += """
        <h2>Carbon Fiber Layup Schedule</h2>
        <table>
            <tr>
                <th>Section</th>
                <th>Plies</th>
                <th>Thickness (mm)</th>
                <th>Area (m²)</th>
                <th>Mass (kg)</th>
            </tr>
        """
        
        for section_name, section_data in layup['sections'].items():
            html += f"""
            <tr>
                <td>{section_name.replace('_', ' ').title()}</td>
                <td>{section_data['total_plies']}</td>
                <td>{section_data['thickness_mm']:.1f}</td>
                <td>{section_data['area_m2']:.2f}</td>
                <td>{section_data['mass_kg']:.2f}</td>
            </tr>
            """
        
        html += f"""
            <tr style="font-weight: bold; background: #ecf0f1;">
                <td>TOTAL</td>
                <td>-</td>
                <td>-</td>
                <td>-</td>
                <td>{layup['total_mass_kg']:.2f}</td>
            </tr>
        </table>
        """
        
        # Fastener summary
        html += f"""
        <h2>Fastener Map Summary</h2>
        <p><strong>Total Fasteners:</strong> {fasteners['total_count']}</p>
        <table>
            <tr>
                <th>Fastener Type</th>
                <th>Quantity</th>
                <th>Torque Spec</th>
            </tr>
        """
        
        for ftype, count in fasteners['types_summary'].items():
            spec = fasteners['specifications'].get(ftype, {})
            torque = spec.get('torque_Nm', 'N/A')
            html += f"""
            <tr>
                <td>{ftype}</td>
                <td>{count}</td>
                <td>{torque} N⋅m</td>
            </tr>
            """
        
        html += """
        </table>
        """
        
        # Manufacturing notes
        html += """
        <h2>Manufacturing Notes</h2>
        <ul>
        """
        for note in layup['manufacturing_notes']:
            html += f"<li>{note}</li>"
        html += """
        </ul>
        
        <h2>Assembly Notes</h2>
        <ul>
        """
        for note in fasteners['assembly_notes']:
            html += f"<li>{note}</li>"
        html += """
        </ul>
        """
        
        # CAD information
        html += f"""
        <h2>CAD Geometry Information</h2>
        <p><strong>Vertices:</strong> {cad_data['num_vertices']:,}</p>
        <p><strong>Faces:</strong> {cad_data['num_faces']:,}</p>
        <p><strong>Bounding Box:</strong> 
           {cad_data['bounding_box']['size'][0]:.2f} × 
           {cad_data['bounding_box']['size'][1]:.2f} × 
           {cad_data['bounding_box']['size'][2]:.2f} m
        </p>
        """
        
        # Footer
        html += """
        <div class="footer">
            <p>This report was automatically generated by the Baja 1000 Chassis Optimizer.</p>
            <p>All calculations are based on engineering principles and material specifications.</p>
            <p><strong>Note:</strong> This design should be reviewed by a qualified engineer before manufacturing.</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html
