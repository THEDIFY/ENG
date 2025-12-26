# Trophy Truck Topology Optimizer

A full-stack application for topology optimization of carbon fiber trophy truck chassis, optimized for the Baja 1000.

## Overview

This application performs multi-objective topology optimization for designing lightweight, high-performance carbon fiber chassis structures for trophy trucks. It integrates:

- **Rules Parsing**: Baja 1000 rules and constraints
- **Topology Optimization**: SIMP and level-set methods
- **FE Analysis**: Static, modal, and impact analysis
- **CFD Analysis**: External aerodynamics and cooling flow
- **Manufacturing Validation**: Composite layup rules, drapability, mold splits
- **Output Generation**: CAD exports, layup schedules, BOM, reports

## Features

### Frontend
- React + TypeScript SPA
- Three.js WebGL 3D viewer for design visualization
- Interactive rules and constraint editor
- Component placement interface
- Real-time optimization progress tracking
- Job dashboard

### Backend
- FastAPI REST API
- PostgreSQL database
- Redis + Celery job queue
- FE/CFD orchestration
- S3-compatible object storage

### Optimization Engine
- SIMP (Solid Isotropic Material with Penalization)
- Level-set method
- Orthotropic laminate models
- Multi-objective optimization (structural + aero + robustness)
- Manufacturing constraint integration

### Analysis
- FEniCS/CalculiX FE solver integration
- Gmsh mesh generation
- OpenFOAM CFD integration
- Modal analysis
- Impact scenarios
- Fatigue spectrum analysis

### Manufacturing
- Ply rules validation (angles, symmetry, balance)
- Drapability analysis
- Ply-drop limits
- Mold split detection
- Metallic insert placement
- Adhesive bond validation

### Outputs
- CAD: STEP, IGES, Parasolid, STL, glTF
- Data: CSV/JSON layup schedules, fastener maps
- Documentation: BOM, PDF technical reports, compliance checklists

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 20+ (for development)
- Python 3.11+ (for development)

### Running with Docker

```bash
# Clone the repository
git clone <repository-url>
cd ENG

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Flower (job monitoring): http://localhost:5555
```

### Development Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Start development server
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## API Documentation

The API documentation is available at `http://localhost:8000/docs` when running the backend.

### Key Endpoints

- `POST /api/v1/projects/` - Create a new project
- `GET /api/v1/projects/` - List all projects
- `PUT /api/v1/projects/{id}` - Update project configuration
- `POST /api/v1/projects/{id}/jobs` - Submit optimization job
- `GET /api/v1/rules/` - Get Baja 1000 rules
- `POST /api/v1/rules/parse` - Parse rules into constraints
- `GET /api/v1/materials/` - List materials
- `GET /api/v1/materials/predefined` - Get predefined carbon fiber materials

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── core/          # Configuration, database
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   ├── optimization/  # SIMP, level-set, laminate
│   │   ├── fe_solver/     # FE mesh and solver
│   │   ├── cfd/           # CFD solver interface
│   │   ├── manufacturing/ # Manufacturing validation
│   │   └── outputs/       # Geometry and report export
│   ├── tests/             # Backend tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/           # API client
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── stores/        # Zustand stores
│   │   ├── types/         # TypeScript types
│   │   └── hooks/         # Custom hooks
│   ├── Dockerfile
│   └── package.json
├── shared/                # Shared types and schemas
├── docs/                  # Documentation
├── examples/              # Example projects
├── docker-compose.yml
└── README.md
```

## Workflow

1. **Parse Rules**: Import Baja 1000 rules, confirm constraints in UI
2. **Place Components**: Define engine, transmission, fuel cell, etc. positions
3. **Generate Design Space**: Create design volume with keep-out zones
4. **Define Load Cases**: Derive from mission profile, add custom scenarios
5. **Assign Materials**: Select carbon fiber materials, set manufacturing constraints
6. **Run Optimization**: Execute SIMP/level-set with aero coupling
7. **Post-Process**: Convert density field to surfaces, apply layup rules
8. **Validate**: Run FE (static, modal, impact) and CFD verification
9. **Check Manufacturing**: Validate drapability, ply rules, mold splits
10. **Export**: Generate CAD, layup schedules, fastener maps, BOM, reports

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://postgres:postgres@localhost:5432/topology_opt` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `CELERY_BROKER_URL` | Celery broker URL | `redis://localhost:6379/1` |
| `STORAGE_PATH` | Local storage path | `./storage` |
| `FE_SOLVER` | FE solver to use | `internal` |
| `CFD_SOLVER` | CFD solver to use | `internal` |

## Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm test
```

## License

See LICENSE file.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request
