"""Pydantic schemas for Material API."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.material import MaterialType


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    class Config:
        from_attributes = True


class MaterialCreate(BaseSchema):
    """Schema for creating a new material."""

    name: str = Field(..., min_length=1, max_length=255)
    material_type: MaterialType
    description: Optional[str] = None

    # Elastic properties (GPa for moduli)
    e1: float = Field(..., gt=0, description="Longitudinal modulus (GPa)")
    e2: float = Field(..., gt=0, description="Transverse modulus (GPa)")
    e3: Optional[float] = Field(None, gt=0, description="Out-of-plane modulus (GPa)")
    g12: float = Field(..., gt=0, description="In-plane shear modulus (GPa)")
    g13: Optional[float] = Field(None, gt=0)
    g23: Optional[float] = Field(None, gt=0)
    nu12: float = Field(..., ge=0, le=0.5, description="In-plane Poisson's ratio")
    nu13: Optional[float] = Field(None, ge=0, le=0.5)
    nu23: Optional[float] = Field(None, ge=0, le=0.5)

    # Strength properties (MPa)
    xt: float = Field(..., gt=0, description="Longitudinal tensile strength (MPa)")
    xc: float = Field(..., gt=0, description="Longitudinal compressive strength (MPa)")
    yt: float = Field(..., gt=0, description="Transverse tensile strength (MPa)")
    yc: float = Field(..., gt=0, description="Transverse compressive strength (MPa)")
    s12: float = Field(..., gt=0, description="In-plane shear strength (MPa)")

    # Physical properties
    density: float = Field(..., gt=0, description="Density (kg/m³)")
    ply_thickness: Optional[float] = Field(None, gt=0, description="Ply thickness (mm)")

    # Thermal properties
    alpha1: Optional[float] = Field(None, description="CTE longitudinal (1/K)")
    alpha2: Optional[float] = Field(None, description="CTE transverse (1/K)")

    # Additional properties
    fatigue_params: Optional[Dict[str, Any]] = None
    drapability_params: Optional[Dict[str, Any]] = None
    cost_per_kg: Optional[float] = Field(None, ge=0)


class MaterialUpdate(BaseSchema):
    """Schema for updating a material."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    e1: Optional[float] = Field(None, gt=0)
    e2: Optional[float] = Field(None, gt=0)
    e3: Optional[float] = Field(None, gt=0)
    g12: Optional[float] = Field(None, gt=0)
    g13: Optional[float] = Field(None, gt=0)
    g23: Optional[float] = Field(None, gt=0)
    nu12: Optional[float] = Field(None, ge=0, le=0.5)
    nu13: Optional[float] = Field(None, ge=0, le=0.5)
    nu23: Optional[float] = Field(None, ge=0, le=0.5)
    xt: Optional[float] = Field(None, gt=0)
    xc: Optional[float] = Field(None, gt=0)
    yt: Optional[float] = Field(None, gt=0)
    yc: Optional[float] = Field(None, gt=0)
    s12: Optional[float] = Field(None, gt=0)
    density: Optional[float] = Field(None, gt=0)
    ply_thickness: Optional[float] = Field(None, gt=0)
    alpha1: Optional[float] = None
    alpha2: Optional[float] = None
    fatigue_params: Optional[Dict[str, Any]] = None
    drapability_params: Optional[Dict[str, Any]] = None
    cost_per_kg: Optional[float] = Field(None, ge=0)


class MaterialResponse(BaseSchema):
    """Schema for material response."""

    id: UUID
    name: str
    material_type: MaterialType
    description: Optional[str]
    e1: float
    e2: float
    e3: Optional[float]
    g12: float
    g13: Optional[float]
    g23: Optional[float]
    nu12: float
    nu13: Optional[float]
    nu23: Optional[float]
    xt: float
    xc: float
    yt: float
    yc: float
    s12: float
    density: float
    ply_thickness: Optional[float]
    alpha1: Optional[float]
    alpha2: Optional[float]
    fatigue_params: Optional[Dict[str, Any]]
    drapability_params: Optional[Dict[str, Any]]
    cost_per_kg: Optional[float]
    created_at: datetime
    updated_at: datetime


class MaterialListResponse(BaseSchema):
    """Schema for material list response."""

    id: UUID
    name: str
    material_type: MaterialType
    density: float
    ply_thickness: Optional[float]


# Predefined material library
class PredefinedMaterials:
    """Standard carbon fiber materials for reference."""

    T300_EPOXY = {
        "name": "T300/Epoxy",
        "material_type": MaterialType.CARBON_FIBER_UD,
        "description": "Standard modulus carbon fiber with epoxy matrix",
        "e1": 135.0,
        "e2": 10.0,
        "e3": 10.0,
        "g12": 5.0,
        "g13": 5.0,
        "g23": 3.5,
        "nu12": 0.27,
        "nu13": 0.27,
        "nu23": 0.40,
        "xt": 1500.0,
        "xc": 1200.0,
        "yt": 50.0,
        "yc": 200.0,
        "s12": 70.0,
        "density": 1600.0,
        "ply_thickness": 0.125,
        "alpha1": -0.3e-6,
        "alpha2": 28.0e-6,
    }

    T700_EPOXY = {
        "name": "T700S/Epoxy",
        "material_type": MaterialType.CARBON_FIBER_UD,
        "description": "Intermediate modulus carbon fiber with epoxy matrix",
        "e1": 165.0,
        "e2": 10.5,
        "e3": 10.5,
        "g12": 5.5,
        "g13": 5.5,
        "g23": 3.8,
        "nu12": 0.28,
        "nu13": 0.28,
        "nu23": 0.38,
        "xt": 2550.0,
        "xc": 1600.0,
        "yt": 55.0,
        "yc": 220.0,
        "s12": 85.0,
        "density": 1570.0,
        "ply_thickness": 0.14,
        "alpha1": -0.5e-6,
        "alpha2": 26.0e-6,
    }

    M55J_EPOXY = {
        "name": "M55J/Epoxy",
        "material_type": MaterialType.CARBON_FIBER_UD,
        "description": "High modulus carbon fiber with epoxy matrix",
        "e1": 295.0,
        "e2": 8.5,
        "e3": 8.5,
        "g12": 5.0,
        "g13": 5.0,
        "g23": 3.0,
        "nu12": 0.29,
        "nu13": 0.29,
        "nu23": 0.42,
        "xt": 1900.0,
        "xc": 850.0,
        "yt": 35.0,
        "yc": 150.0,
        "s12": 55.0,
        "density": 1650.0,
        "ply_thickness": 0.10,
        "alpha1": -1.0e-6,
        "alpha2": 30.0e-6,
    }

    WOVEN_CARBON = {
        "name": "Woven Carbon/Epoxy",
        "material_type": MaterialType.CARBON_FIBER_WOVEN,
        "description": "Plain weave carbon fiber with epoxy matrix",
        "e1": 70.0,
        "e2": 70.0,
        "e3": 10.0,
        "g12": 5.0,
        "g13": 5.0,
        "g23": 5.0,
        "nu12": 0.04,
        "nu13": 0.30,
        "nu23": 0.30,
        "xt": 600.0,
        "xc": 500.0,
        "yt": 600.0,
        "yc": 500.0,
        "s12": 90.0,
        "density": 1550.0,
        "ply_thickness": 0.25,
        "alpha1": 2.0e-6,
        "alpha2": 2.0e-6,
    }
