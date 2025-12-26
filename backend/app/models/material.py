"""Material model for composite and metallic materials."""

import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import JSON, DateTime, Enum, Float, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MaterialType(str, PyEnum):
    """Material type enumeration."""

    CARBON_FIBER_UD = "carbon_fiber_ud"
    CARBON_FIBER_WOVEN = "carbon_fiber_woven"
    GLASS_FIBER = "glass_fiber"
    ARAMID = "aramid"
    ALUMINUM = "aluminum"
    STEEL = "steel"
    TITANIUM = "titanium"
    ADHESIVE = "adhesive"


class Material(Base):
    """Material model for composite and metallic materials."""

    __tablename__ = "materials"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    material_type: Mapped[MaterialType] = mapped_column(
        Enum(MaterialType), nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Orthotropic elastic properties
    e1: Mapped[float] = mapped_column(Float, nullable=False)  # Longitudinal modulus (GPa)
    e2: Mapped[float] = mapped_column(Float, nullable=False)  # Transverse modulus (GPa)
    e3: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Out-of-plane modulus (GPa)
    g12: Mapped[float] = mapped_column(Float, nullable=False)  # In-plane shear modulus (GPa)
    g13: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Out-of-plane shear modulus (GPa)
    g23: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Out-of-plane shear modulus (GPa)
    nu12: Mapped[float] = mapped_column(Float, nullable=False)  # In-plane Poisson's ratio
    nu13: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Out-of-plane Poisson's ratio
    nu23: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Out-of-plane Poisson's ratio

    # Strength properties
    xt: Mapped[float] = mapped_column(Float, nullable=False)  # Longitudinal tensile strength (MPa)
    xc: Mapped[float] = mapped_column(Float, nullable=False)  # Longitudinal compressive strength (MPa)
    yt: Mapped[float] = mapped_column(Float, nullable=False)  # Transverse tensile strength (MPa)
    yc: Mapped[float] = mapped_column(Float, nullable=False)  # Transverse compressive strength (MPa)
    s12: Mapped[float] = mapped_column(Float, nullable=False)  # In-plane shear strength (MPa)

    # Physical properties
    density: Mapped[float] = mapped_column(Float, nullable=False)  # kg/m³
    ply_thickness: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # mm

    # Thermal properties
    alpha1: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # CTE longitudinal (1/K)
    alpha2: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # CTE transverse (1/K)

    # Fatigue properties (S-N curve parameters)
    fatigue_params: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Drape/formability properties
    drapability_params: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Cost
    cost_per_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
