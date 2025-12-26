"""Application configuration settings."""

from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Trophy Truck Topology Optimizer"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"

    # API
    api_prefix: str = "/api/v1"
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/topology_opt"
    database_echo: bool = False

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Object Storage
    storage_backend: str = "local"  # local, s3, minio
    storage_path: str = "./storage"
    s3_bucket: Optional[str] = None
    s3_access_key: Optional[str] = None
    s3_secret_key: Optional[str] = None
    s3_endpoint: Optional[str] = None

    # Optimization
    max_optimization_iterations: int = 500
    convergence_tolerance: float = 1e-4
    default_volume_fraction: float = 0.3
    simp_penalty: float = 3.0

    # FE Solver
    fe_solver: str = "fenics"  # fenics, calculix
    mesh_refinement_level: int = 2
    element_order: int = 2

    # CFD
    cfd_solver: str = "openfoam"
    turbulence_model: str = "kOmegaSST"
    max_cfd_iterations: int = 1000

    # Manufacturing
    min_ply_angle_step: float = 45.0  # degrees
    min_ply_thickness: float = 0.2  # mm
    max_ply_drops_per_zone: int = 4
    symmetry_tolerance: float = 1e-6

    # Security
    secret_key: str = "development-secret-key-change-in-production"
    access_token_expire_minutes: int = 30

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
