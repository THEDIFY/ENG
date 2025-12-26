# API Documentation

## Overview

The Trophy Truck Topology Optimizer API provides RESTful endpoints for managing topology optimization projects for carbon fiber trophy truck chassis design.

Base URL: `http://localhost:8000/api/v1`

## Authentication

Currently, the API does not require authentication for development purposes. Production deployments should implement JWT-based authentication.

## Endpoints

### Projects

#### Create Project
```http
POST /projects/
Content-Type: application/json

{
  "name": "Baja 1000 Trophy Truck Chassis",
  "description": "Carbon fiber monocoque chassis optimized for desert racing"
}
```

Response:
```json
{
  "id": "uuid",
  "name": "Baja 1000 Trophy Truck Chassis",
  "description": "Carbon fiber monocoque chassis optimized for desert racing",
  "status": "draft",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### List Projects
```http
GET /projects/
```

#### Get Project
```http
GET /projects/{project_id}
```

#### Update Project
```http
PUT /projects/{project_id}
Content-Type: application/json

{
  "rules_config": {...},
  "components_config": {...},
  "optimization_params": {...}
}
```

#### Delete Project
```http
DELETE /projects/{project_id}
```

### Jobs

#### Create Job
```http
POST /projects/{project_id}/jobs
Content-Type: application/json

{
  "job_type": "topology_optimization",
  "config": {
    "method": "simp",
    "volume_fraction": 0.3,
    "max_iterations": 200
  }
}
```

Job Types:
- `topology_optimization`
- `fe_analysis`
- `cfd_analysis`
- `manufacturability_check`
- `geometry_export`
- `report_generation`

#### List Jobs
```http
GET /projects/{project_id}/jobs
```

#### Get Job
```http
GET /projects/{project_id}/jobs/{job_id}
```

### Rules

#### Get All Rules
```http
GET /rules/
```

Response includes complete Baja 1000 rules set with categories:
- Safety Equipment
- Dimensional Limits
- Suspension
- Engine and Drivetrain
- Weight
- Tires and Wheels

#### Parse Rules
```http
POST /rules/parse
Content-Type: application/json

{
  "rule_set_version": "2024",
  "custom_constraints": [],
  "override_rules": []
}
```

Response:
```json
{
  "version": "2024",
  "total_rules": 25,
  "categories": ["Safety Equipment", "Dimensional Limits", ...],
  "constraints": [...],
  "dimensional_constraints": {...},
  "safety_requirements": [...]
}
```

#### Get Dimensional Defaults
```http
GET /rules/dimensional-defaults
```

Response:
```json
{
  "max_width_mm": 2438,
  "max_length_mm": 5588,
  "min_ground_clearance_mm": 254,
  "wheelbase_min_mm": 2540,
  "wheelbase_max_mm": 3556
}
```

### Materials

#### List Materials
```http
GET /materials/
```

#### Get Predefined Materials
```http
GET /materials/predefined
```

Returns standard carbon fiber material templates:
- T300/Epoxy
- T700S/Epoxy
- M55J/Epoxy
- Woven Carbon/Epoxy

#### Create Material
```http
POST /materials/
Content-Type: application/json

{
  "name": "Custom Carbon",
  "material_type": "carbon_fiber_ud",
  "e1": 165.0,
  "e2": 10.5,
  "g12": 5.5,
  "nu12": 0.28,
  "xt": 2550.0,
  "xc": 1600.0,
  "yt": 55.0,
  "yc": 220.0,
  "s12": 85.0,
  "density": 1570.0,
  "ply_thickness": 0.14
}
```

#### Seed Default Materials
```http
POST /materials/seed-defaults
```

Populates database with predefined carbon fiber materials.

## Data Schemas

### Project Configuration

```typescript
interface ProjectConfiguration {
  rules_config?: {
    rule_set_version: string;
    constraints: Constraint[];
    max_width: number;
    max_length: number;
    min_ground_clearance: number;
    wheelbase_min: number;
    wheelbase_max: number;
  };
  
  components_config?: {
    components: ComponentPlacement[];
    engine?: ComponentPlacement;
    transmission?: ComponentPlacement;
    fuel_cell?: ComponentPlacement;
  };
  
  design_space_config?: {
    design_volume: Geometry;
    keep_out_zones: KeepOutZone[];
    symmetry_plane?: string;
    minimum_member_size: number;
    maximum_member_size: number;
  };
  
  load_cases?: {
    mission_profile: string;
    load_cases: LoadCase[];
    max_vertical_g: number;
    max_lateral_g: number;
    max_braking_g: number;
  };
  
  manufacturing_config?: {
    allowed_ply_angles: number[];
    min_ply_thickness: number;
    max_ply_drops_per_zone: number;
    enforce_symmetry: boolean;
    enforce_balance: boolean;
    max_shear_angle: number;
  };
  
  optimization_params?: {
    method: 'simp' | 'level_set' | 'hybrid';
    volume_fraction: number;
    penalty_factor: number;
    filter_radius: number;
    max_iterations: number;
    convergence_tolerance: number;
    aero_coupling: boolean;
  };
}
```

## Error Responses

The API returns standard HTTP status codes:

- `200 OK` - Success
- `201 Created` - Resource created
- `204 No Content` - Resource deleted
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

Error response format:
```json
{
  "detail": "Error message describing the issue"
}
```

## WebSocket Events

For real-time optimization progress updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/jobs/{job_id}');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Progress:', data.progress);
  console.log('Iteration:', data.iteration);
  console.log('Compliance:', data.objective_value);
};
```
