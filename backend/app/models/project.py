"""Project model for topology optimization projects."""

import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProjectStatus(str, PyEnum):
    """Project status enumeration."""

    DRAFT = "draft"
    RULES_PARSED = "rules_parsed"
    COMPONENTS_PLACED = "components_placed"
    DESIGN_SPACE_GENERATED = "design_space_generated"
    LOADS_DEFINED = "loads_defined"
    OPTIMIZING = "optimizing"
    POST_PROCESSING = "post_processing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"


class Project(Base):
    """Project model for topology optimization projects."""

    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus), default=ProjectStatus.DRAFT
    )

    # Baja rules configuration
    rules_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Component specifications
    components_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Design space configuration
    design_space_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Load cases
    load_cases: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Material configuration
    materials_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Manufacturing constraints
    manufacturing_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Optimization parameters
    optimization_params: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Results
    optimization_results: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    validation_results: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    jobs: Mapped[List["OptimizationJob"]] = relationship(
        "OptimizationJob", back_populates="project", cascade="all, delete-orphan"
    )
    outputs: Mapped[List["ProjectOutput"]] = relationship(
        "ProjectOutput", back_populates="project", cascade="all, delete-orphan"
    )


class JobType(str, PyEnum):
    """Job type enumeration."""

    TOPOLOGY_OPTIMIZATION = "topology_optimization"
    FE_ANALYSIS = "fe_analysis"
    CFD_ANALYSIS = "cfd_analysis"
    MANUFACTURABILITY_CHECK = "manufacturability_check"
    GEOMETRY_EXPORT = "geometry_export"
    REPORT_GENERATION = "report_generation"


class JobStatus(str, PyEnum):
    """Job status enumeration."""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OptimizationJob(Base):
    """Model for optimization and analysis jobs."""

    __tablename__ = "optimization_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    job_type: Mapped[JobType] = mapped_column(Enum(JobType), nullable=False)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus), default=JobStatus.PENDING
    )
    
    # Job configuration
    config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Progress tracking
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    current_iteration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_iterations: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Results
    results: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Celery task ID
    celery_task_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="jobs")


class OutputType(str, PyEnum):
    """Output type enumeration."""

    STEP = "step"
    IGES = "iges"
    PARASOLID = "parasolid"
    STL = "stl"
    GLTF = "gltf"
    LAYUP_CSV = "layup_csv"
    LAYUP_JSON = "layup_json"
    FASTENER_MAP = "fastener_map"
    BOM = "bom"
    VALIDATION_REPORT = "validation_report"
    TECHNICAL_REPORT = "technical_report"


class ProjectOutput(Base):
    """Model for project outputs (CAD files, reports, etc.)."""

    __tablename__ = "project_outputs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    output_type: Mapped[OutputType] = mapped_column(Enum(OutputType), nullable=False)
    
    # File information
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="outputs")
