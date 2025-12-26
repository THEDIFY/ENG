// JavaScript for Baja 1000 Chassis Optimizer UI

document.addEventListener('DOMContentLoaded', function() {
    const optimizeBtn = document.getElementById('optimizeBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultsSection = document.getElementById('resultsSection');
    
    optimizeBtn.addEventListener('click', runOptimization);
});

async function runOptimization() {
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultsSection = document.getElementById('resultsSection');
    const optimizeBtn = document.getElementById('optimizeBtn');
    
    // Show loading, hide results
    loadingIndicator.style.display = 'block';
    resultsSection.style.display = 'none';
    optimizeBtn.disabled = true;
    
    // Gather input data
    const raceRules = {
        max_weight: parseFloat(document.getElementById('max_weight').value),
        max_length: parseFloat(document.getElementById('max_length').value),
        max_width: parseFloat(document.getElementById('max_width').value),
        max_height: parseFloat(document.getElementById('max_height').value),
        min_safety_factor: parseFloat(document.getElementById('min_safety_factor').value),
        max_drag_coefficient: parseFloat(document.getElementById('max_drag_coefficient').value),
        symmetry: true
    };
    
    const componentSpecs = {
        estimated_mass: parseFloat(document.getElementById('vehicle_mass').value),
        engine_power: parseFloat(document.getElementById('engine_power').value),
        suspension_travel: parseFloat(document.getElementById('suspension_travel').value),
        wheel_diameter: parseFloat(document.getElementById('wheel_diameter').value)
    };
    
    const missionProfile = {
        max_speed: parseFloat(document.getElementById('max_speed').value),
        race_duration: parseFloat(document.getElementById('race_duration').value),
        terrain_roughness: document.getElementById('terrain_roughness').value,
        material_type: document.getElementById('material_type').value
    };
    
    try {
        const response = await fetch('/api/optimize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                race_rules: raceRules,
                component_specs: componentSpecs,
                mission_profile: missionProfile
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data);
        } else {
            displayError(data.error || 'Optimization failed');
        }
    } catch (error) {
        displayError('Network error: ' + error.message);
    } finally {
        loadingIndicator.style.display = 'none';
        optimizeBtn.disabled = false;
    }
}

function displayResults(data) {
    const resultsSection = document.getElementById('resultsSection');
    const statusMessage = document.getElementById('statusMessage');
    const metricsGrid = document.getElementById('metricsGrid');
    const validationResults = document.getElementById('validationResults');
    const downloadButtons = document.getElementById('downloadButtons');
    
    resultsSection.style.display = 'block';
    
    // Status message
    const compliant = data.validation.compliant;
    statusMessage.className = 'status-message ' + (compliant ? 'success' : 'warning');
    statusMessage.innerHTML = compliant 
        ? '✓ Design is COMPLIANT with all race rules and requirements!'
        : '⚠ Design has validation issues that need to be addressed.';
    
    // Metrics
    metricsGrid.innerHTML = `
        <div class="metric-card">
            <div class="metric-label">Total Mass</div>
            <div class="metric-value">${data.summary.mass.toFixed(2)} kg</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Safety Factor</div>
            <div class="metric-value">${data.summary.safety_factor.toFixed(2)}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Drag Coefficient</div>
            <div class="metric-value">${data.summary.drag_coefficient.toFixed(3)}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Stiffness</div>
            <div class="metric-value">${data.summary.stiffness.toFixed(0)} N⋅m/°</div>
        </div>
    `;
    
    // Validation results
    let validationHTML = '<h3>Validation Checks</h3>';
    data.validation.checks.forEach(check => {
        const passClass = check.passed ? 'pass' : 'fail';
        const icon = check.passed ? '✓' : '✗';
        validationHTML += `
            <div class="validation-check ${passClass}">
                <div class="check-name">${icon} ${check.name}</div>
                <div class="check-details">
                    Required: ${check.required} | 
                    Actual: ${check.actual}
                    ${check.margin ? ' | Margin: ' + check.margin : ''}
                </div>
            </div>
        `;
    });
    
    validationHTML += `
        <p style="margin-top: 20px; font-weight: bold;">
            Compliance: ${data.validation.summary.passed}/${data.validation.summary.total_checks} checks passed 
            (${data.validation.summary.compliance_percentage.toFixed(1)}%)
        </p>
    `;
    
    validationResults.innerHTML = validationHTML;
    
    // Download buttons
    downloadButtons.innerHTML = `
        <a href="${data.download_links.cad}" class="download-btn" download>
            📐 Download 3D CAD (STL)
        </a>
        <a href="${data.download_links.layup}" class="download-btn" download>
            📋 Download Layup Schedule
        </a>
        <a href="${data.download_links.fasteners}" class="download-btn" download>
            🔩 Download Fastener Map
        </a>
        <a href="${data.download_links.report}" class="download-btn" download>
            📄 Download Full Report
        </a>
    `;
}

function displayError(message) {
    const resultsSection = document.getElementById('resultsSection');
    const statusMessage = document.getElementById('statusMessage');
    const metricsGrid = document.getElementById('metricsGrid');
    const validationResults = document.getElementById('validationResults');
    const downloadButtons = document.getElementById('downloadButtons');
    
    resultsSection.style.display = 'block';
    
    statusMessage.className = 'status-message error';
    statusMessage.innerHTML = '✗ Error: ' + message;
    
    metricsGrid.innerHTML = '';
    validationResults.innerHTML = '';
    downloadButtons.innerHTML = '';
}
