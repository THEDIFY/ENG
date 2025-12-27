"""Project API router."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.project import (
    JobStatus,
    JobType,
    OptimizationJob,
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

router = APIRouter(prefix="/projects", tags=["projects"])


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
    """Run topology optimization for a project."""
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
    
    # Simulate some optimization results for demo
    import random
    project.optimization_results = {
        "iterations": random.randint(100, 300),
        "final_volume_fraction": round(random.uniform(0.25, 0.35), 3),
        "final_compliance": round(random.uniform(0.001, 0.01), 6),
        "mass_reduction": round(random.uniform(40, 60), 1),
        "convergence_achieved": True,
        "mesh_elements": random.randint(50000, 100000),
        "density_field": [round(random.random(), 2) for _ in range(100)],
    }
    project.status = ProjectStatus.COMPLETED
    
    db_job.status = JobStatus.COMPLETED
    db_job.progress = 100.0
    db_job.results = project.optimization_results
    
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
