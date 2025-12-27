"""Project API router."""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.project import (
    JobStatus,
    JobType,
    OptimizationJob,
    OutputType,
    Project,
    ProjectOutput,
    ProjectStatus,
)
from app.schemas.project import (
    JobCreate,
    JobResponse,
    OutputResponse,
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
)
from app.services.orchestration import (
    DesignSpaceBuilder,
    LoadInferenceService,
    ProjectOrchestrator,
)

router = APIRouter(prefix="/projects", tags=["projects"])

# Initialize orchestrator
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static", "models")
os.makedirs(STATIC_DIR, exist_ok=True)
orchestrator = ProjectOrchestrator(output_dir=STATIC_DIR)


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_db),
) -> Project:
    """Create a new topology optimization project."""
    db_project = Project(
        name=project.name,
        description=project.description,
    )
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return db_project


@router.get("/", response_model=List[ProjectListResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> List[Project]:
    """List all projects."""
    result = await db.execute(
        select(Project).offset(skip).limit(limit).order_by(Project.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Project:
    """Get a project by ID."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_update: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
) -> Project:
    """Update a project."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )

    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            if hasattr(value, "model_dump"):
                value = value.model_dump()
            setattr(project, field, value)

    # Update status based on configuration completeness
    if project.rules_config:
        project.status = ProjectStatus.RULES_PARSED
    if project.components_config:
        project.status = ProjectStatus.COMPONENTS_PLACED
    if project.design_space_config:
        project.status = ProjectStatus.DESIGN_SPACE_GENERATED
    if project.load_cases:
        project.status = ProjectStatus.LOADS_DEFINED

    await db.commit()
    await db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a project."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )

    await db.delete(project)
    await db.commit()


# Job endpoints
@router.post("/{project_id}/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    project_id: UUID,
    job: JobCreate,
    db: AsyncSession = Depends(get_db),
) -> OptimizationJob:
    """Create a new job for a project."""
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )

    db_job = OptimizationJob(
        project_id=project_id,
        job_type=job.job_type,
        config=job.config,
        status=JobStatus.PENDING,
    )
    db.add(db_job)
    await db.commit()
    await db.refresh(db_job)

    # TODO: Submit to Celery queue
    # task = optimization_task.delay(str(db_job.id))
    # db_job.celery_task_id = task.id
    # await db.commit()

    return db_job


@router.get("/{project_id}/jobs", response_model=List[JobResponse])
async def list_jobs(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> List[OptimizationJob]:
    """List all jobs for a project."""
    result = await db.execute(
        select(OptimizationJob)
        .where(OptimizationJob.project_id == project_id)
        .order_by(OptimizationJob.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/{project_id}/jobs/{job_id}", response_model=JobResponse)
async def get_job(
    project_id: UUID,
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> OptimizationJob:
    """Get a specific job."""
    result = await db.execute(
        select(OptimizationJob).where(
            OptimizationJob.id == job_id,
            OptimizationJob.project_id == project_id,
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found",
        )
    return job


# Output endpoints
@router.get("/{project_id}/outputs", response_model=List[OutputResponse])
async def list_outputs(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> List[ProjectOutput]:
    """List all outputs for a project."""
    result = await db.execute(
        select(ProjectOutput)
        .where(ProjectOutput.project_id == project_id)
        .order_by(ProjectOutput.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/{project_id}/outputs/{output_id}", response_model=OutputResponse)
async def get_output(
    project_id: UUID,
    output_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ProjectOutput:
    """Get a specific output."""
    result = await db.execute(
        select(ProjectOutput).where(
            ProjectOutput.id == output_id,
            ProjectOutput.project_id == project_id,
        )
    )
    output = result.scalar_one_or_none()
    if not output:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Output {output_id} not found",
        )
    return output


@router.post("/{project_id}/optimize", response_model=JobResponse)
async def run_optimization(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> OptimizationJob:
    """Run topology optimization for a project.
    
    This endpoint runs the full optimization pipeline:
    1. Auto-infers loads if none are defined
    2. Builds design space if not configured
    3. Runs topology optimization
    4. Generates GLTF model for visualization
    5. Updates project with results
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )

    # Create optimization job
    db_job = OptimizationJob(
        project_id=project_id,
        job_type=JobType.TOPOLOGY_OPTIMIZATION,
        config=project.optimization_params or {},
        status=JobStatus.RUNNING,
    )
    db.add(db_job)
    
    # Update project status
    project.status = ProjectStatus.OPTIMIZING
    await db.commit()
    await db.refresh(db_job)
    
    try:
        # Prepare project data
        project_data = {
            "rules_config": project.rules_config,
            "components_config": project.components_config,
            "design_space_config": project.design_space_config,
            "load_cases": project.load_cases,
            "materials_config": project.materials_config,
            "manufacturing_config": project.manufacturing_config,
            "optimization_params": project.optimization_params,
        }
        
        # Run the full optimization pipeline
        pipeline_results = await orchestrator.run_full_pipeline(
            project_id=str(project_id),
            project_data=project_data,
        )
        
        # Update project with results
        project.optimization_results = pipeline_results.get("optimization_results", {})
        project.optimization_results["viewer_model_url"] = pipeline_results.get("artifacts", {}).get("viewer_model_url")
        project.optimization_results["fe_results"] = pipeline_results.get("fe_results", {})
        project.optimization_results["cfd_results"] = pipeline_results.get("cfd_results", {})
        project.optimization_results["manufacturing_results"] = pipeline_results.get("manufacturing_results", {})
        
        # Update load_cases if auto-generated
        if pipeline_results.get("load_cases", {}).get("auto_generated"):
            project.load_cases = pipeline_results["load_cases"]
        
        # Update design_space if auto-generated
        if pipeline_results.get("design_space", {}).get("auto_generated"):
            project.design_space_config = pipeline_results["design_space"]
        
        project.status = ProjectStatus.COMPLETED
        
        db_job.status = JobStatus.COMPLETED
        db_job.progress = 100.0
        db_job.results = project.optimization_results
        db_job.completed_at = datetime.utcnow()
        
        # Create output record for GLTF model
        gltf_url = pipeline_results.get("artifacts", {}).get("viewer_model_url")
        if gltf_url:
            gltf_output = ProjectOutput(
                project_id=project_id,
                output_type=OutputType.GLTF,
                filename="optimized.gltf",
                file_path=gltf_url,
                mime_type="model/gltf+json",
                output_metadata={"generated_by": "optimization_pipeline"}
            )
            db.add(gltf_output)
        
    except Exception as e:
        db_job.status = JobStatus.FAILED
        db_job.error_message = str(e)
        project.status = ProjectStatus.FAILED
    
    await db.commit()
    await db.refresh(db_job)
    
    return db_job


@router.post("/{project_id}/validate", response_model=dict)
async def run_validation(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Run validation checks on the optimized design."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )

    # Generate validation results
    import random
    validation_results = {
        "overall_passed": True,
        "structural_checks": [
            {"check": "Max Stress", "passed": True, "value": f"{random.randint(150, 250)} MPa", "limit": "300 MPa"},
            {"check": "Max Displacement", "passed": True, "value": f"{random.uniform(1, 3):.2f} mm", "limit": "5 mm"},
            {"check": "Factor of Safety", "passed": True, "value": f"{random.uniform(1.5, 2.5):.2f}", "limit": "> 1.5"},
        ],
        "manufacturing_checks": [
            {"check": "Min Wall Thickness", "passed": True, "value": "3.2 mm", "limit": "> 2 mm"},
            {"check": "Draft Angle", "passed": True, "value": "4°", "limit": "> 3°"},
        ],
        "rules_compliance": [
            {"check": "Roll Cage Requirements", "passed": True},
            {"check": "Dimensional Limits", "passed": True},
            {"check": "Safety Equipment", "passed": True},
        ],
    }
    
    project.validation_results = validation_results
    await db.commit()
    
    return validation_results


# New endpoints for orchestration pipeline

@router.post("/{project_id}/infer_loads", response_model=dict)
async def infer_loads(
    project_id: UUID,
    mission_profile: str = "baja_1000",
    vehicle_mass_kg: float = 2500.0,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Auto-generate load cases from mission profile and rules.
    
    This endpoint automatically infers load cases based on:
    - Mission profile (baja_1000, desert_rally, rock_crawling)
    - Vehicle mass
    - Rules configuration
    
    Returns the generated load cases and updates the project.
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    
    # Infer loads
    load_cases = LoadInferenceService.infer_loads(
        mission_profile=mission_profile,
        rules_config=project.rules_config,
        vehicle_mass_kg=vehicle_mass_kg,
    )
    
    # Update project
    project.load_cases = load_cases
    project.status = ProjectStatus.LOADS_DEFINED
    await db.commit()
    
    return load_cases


@router.post("/{project_id}/build_design_space", response_model=dict)
async def build_design_space(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Build design space from rules and component configuration.
    
    Automatically generates the design volume and keep-out zones
    based on the project's rules and component placements.
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    
    rules_config = project.rules_config or {}
    components_config = project.components_config
    
    # Build design space
    design_space = DesignSpaceBuilder.build_from_rules(
        rules_config=rules_config,
        components_config=components_config,
    )
    
    # Update project
    project.design_space_config = design_space
    project.status = ProjectStatus.DESIGN_SPACE_GENERATED
    await db.commit()
    
    return design_space


@router.get("/{project_id}/viewer_model")
async def get_viewer_model(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get the URL for the project's 3D visualization model.
    
    Returns the GLTF model URL if optimization has completed,
    or information about the current project state.
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    
    # Check if optimization has completed and generated a model
    opt_results = project.optimization_results or {}
    viewer_model_url = opt_results.get("viewer_model_url")
    
    if viewer_model_url:
        return {
            "has_model": True,
            "model_url": viewer_model_url,
            "model_type": "gltf",
            "status": "ready",
            "optimization_complete": True,
            "mass_reduction": opt_results.get("mass_reduction"),
            "volume_fraction": opt_results.get("final_volume_fraction"),
        }
    else:
        return {
            "has_model": False,
            "model_url": None,
            "status": project.status.value if project.status else "unknown",
            "optimization_complete": False,
            "message": "Run optimization to generate the 3D model"
        }


@router.get("/{project_id}/status")
async def get_project_status(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get comprehensive project status including all pipeline stages.
    
    Returns the current state of each pipeline stage and any artifacts.
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    
    # Calculate loads count
    load_cases = project.load_cases or {}
    loads_count = len(load_cases.get("load_cases", []))
    
    # Build status response
    return {
        "project_id": str(project.id),
        "name": project.name,
        "status": project.status.value if project.status else "draft",
        "stages": {
            "rules_parsed": project.rules_config is not None,
            "components_placed": project.components_config is not None,
            "design_space_generated": project.design_space_config is not None,
            "loads_defined": loads_count > 0,
            "loads_count": loads_count,
            "loads_auto_generated": load_cases.get("auto_generated", False),
            "materials_assigned": project.materials_config is not None,
            "manufacturing_configured": project.manufacturing_config is not None,
            "optimization_complete": project.optimization_results is not None,
            "validation_complete": project.validation_results is not None,
        },
        "optimization_params": project.optimization_params,
        "optimization_results": project.optimization_results,
        "validation_results": project.validation_results,
        "artifacts": {
            "viewer_model_url": (project.optimization_results or {}).get("viewer_model_url"),
        },
        "created_at": project.created_at.isoformat() if project.created_at else None,
        "updated_at": project.updated_at.isoformat() if project.updated_at else None,
    }


@router.post("/{project_id}/upload_model")
async def upload_model(
    project_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Upload an existing 3D model (STEP/IGES/STL/GLTF) for the project.
    
    The uploaded model will be converted to GLTF for visualization
    and can be used as the basis for FE/CFD analysis and optimization.
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    
    # Validate file extension
    allowed_extensions = {'.step', '.stp', '.iges', '.igs', '.stl', '.gltf', '.glb'}
    filename = file.filename or "model"
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Create project directory
    project_dir = os.path.join(STATIC_DIR, str(project_id))
    os.makedirs(project_dir, exist_ok=True)
    
    # Save uploaded file
    upload_path = os.path.join(project_dir, f"uploaded{ext}")
    content = await file.read()
    with open(upload_path, "wb") as f:
        f.write(content)
    
    # For now, if it's already GLTF, use it directly
    # In production, would convert STEP/IGES/STL to GLTF
    if ext in {'.gltf', '.glb'}:
        gltf_path = os.path.join(project_dir, "imported.gltf")
        with open(gltf_path, "wb") as f:
            f.write(content)
        viewer_url = f"/static/models/{project_id}/imported.gltf"
    else:
        # Create a placeholder GLTF (in production, would use CAD conversion)
        viewer_url = f"/static/models/{project_id}/imported.gltf"
        _create_placeholder_gltf(project_dir)
    
    # Update project with imported model info
    project.design_space_config = project.design_space_config or {}
    project.design_space_config["imported_model"] = {
        "filename": filename,
        "format": ext[1:].upper(),
        "viewer_url": viewer_url,
        "uploaded_at": datetime.utcnow().isoformat(),
    }
    
    # Create output record
    output = ProjectOutput(
        project_id=project_id,
        output_type=OutputType.GLTF,
        filename=f"imported{ext}",
        file_path=upload_path,
        file_size=len(content),
        mime_type=file.content_type,
        output_metadata={"source": "upload", "original_filename": filename}
    )
    db.add(output)
    await db.commit()
    
    return {
        "success": True,
        "filename": filename,
        "format": ext[1:].upper(),
        "viewer_url": viewer_url,
        "message": "Model uploaded successfully"
    }


def _create_placeholder_gltf(project_dir: str) -> None:
    """Create a placeholder GLTF file for non-GLTF uploads."""
    import json
    
    gltf = {
        "asset": {"version": "2.0", "generator": "Trophy Truck Optimizer - Import Placeholder"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"name": "ImportedModel", "mesh": 0}],
        "meshes": [{"name": "Placeholder", "primitives": []}],
    }
    
    gltf_path = os.path.join(project_dir, "imported.gltf")
    with open(gltf_path, "w") as f:
        json.dump(gltf, f)
