"""FastAPI main application for Trophy Truck Topology Optimizer."""

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.materials import router as materials_router
from app.api.projects import router as projects_router
from app.api.rules import router as rules_router
from app.core.config import get_settings
from app.core.database import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    Trophy Truck Chassis Topology Optimization API
    
    This API provides endpoints for:
    - Managing topology optimization projects
    - Parsing Baja 1000 rules and constraints
    - Running SIMP and level-set optimization
    - FE analysis (static, modal, impact)
    - CFD aerodynamic analysis
    - Manufacturing validation
    - Generating CAD exports and reports
    """,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects_router, prefix=settings.api_prefix)
app.include_router(materials_router, prefix=settings.api_prefix)
app.include_router(rules_router, prefix=settings.api_prefix)

# Serve static files (frontend)
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists() and (static_dir / "index.html").exists():
    # Mount static assets
    if (static_dir / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")
    
    # Serve other static files (like favicon, manifest, etc.)
    for item in static_dir.iterdir():
        if item.is_file() and item.name != "index.html":
            @app.get(f"/{item.name}")
            async def serve_static_file(filename=item.name):
                return FileResponse(str(static_dir / filename))


@app.get("/")
async def root():
    """Serve the frontend application."""
    static_index = static_dir / "index.html"
    if static_index.exists():
        return FileResponse(str(static_index))
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "message": "Frontend not built. Run 'npm run build' in frontend directory."
    }


# Catch-all route for SPA - must be last
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve SPA for all non-API routes."""
    # Don't intercept API routes
    if full_path.startswith("api/"):
        return {"error": "Not found"}
    
    # Serve index.html for all other routes (SPA routing)
    static_index = static_dir / "index.html"
    if static_index.exists():
        return FileResponse(str(static_index))
    
    return {"error": "Frontend not available"}


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.get(f"{settings.api_prefix}/info")
async def api_info() -> Dict[str, Any]:
    """API information endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "features": {
            "optimization": ["simp", "level_set"],
            "fe_solvers": ["internal", "fenics", "calculix"],
            "cfd_solvers": ["internal", "openfoam"],
            "export_formats": ["step", "iges", "stl", "gltf"],
            "report_formats": ["pdf", "json"],
        },
        "endpoints": {
            "projects": f"{settings.api_prefix}/projects",
            "materials": f"{settings.api_prefix}/materials",
            "rules": f"{settings.api_prefix}/rules",
        },
    }
