"""Materials API router."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.material import Material
from app.schemas.material import (
    MaterialCreate,
    MaterialListResponse,
    MaterialResponse,
    MaterialUpdate,
    PredefinedMaterials,
)

router = APIRouter(prefix="/materials", tags=["materials"])


@router.post("/", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
async def create_material(
    material: MaterialCreate,
    db: AsyncSession = Depends(get_db),
) -> Material:
    """Create a new material."""
    # Check if material with same name exists
    result = await db.execute(select(Material).where(Material.name == material.name))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Material with name '{material.name}' already exists",
        )

    db_material = Material(**material.model_dump())
    db.add(db_material)
    await db.commit()
    await db.refresh(db_material)
    return db_material


@router.get("/", response_model=List[MaterialListResponse])
async def list_materials(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> List[Material]:
    """List all materials."""
    result = await db.execute(
        select(Material).offset(skip).limit(limit).order_by(Material.name)
    )
    return list(result.scalars().all())


@router.get("/predefined", response_model=List[dict])
async def list_predefined_materials() -> List[dict]:
    """List predefined material templates."""
    return [
        PredefinedMaterials.T300_EPOXY,
        PredefinedMaterials.T700_EPOXY,
        PredefinedMaterials.M55J_EPOXY,
        PredefinedMaterials.WOVEN_CARBON,
    ]


@router.get("/{material_id}", response_model=MaterialResponse)
async def get_material(
    material_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Material:
    """Get a material by ID."""
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material {material_id} not found",
        )
    return material


@router.put("/{material_id}", response_model=MaterialResponse)
async def update_material(
    material_id: UUID,
    material_update: MaterialUpdate,
    db: AsyncSession = Depends(get_db),
) -> Material:
    """Update a material."""
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material {material_id} not found",
        )

    update_data = material_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(material, field, value)

    await db.commit()
    await db.refresh(material)
    return material


@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_material(
    material_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a material."""
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material {material_id} not found",
        )

    await db.delete(material)
    await db.commit()


@router.post("/seed-defaults", response_model=List[MaterialResponse])
async def seed_default_materials(
    db: AsyncSession = Depends(get_db),
) -> List[Material]:
    """Seed database with default carbon fiber materials."""
    predefined = [
        PredefinedMaterials.T300_EPOXY,
        PredefinedMaterials.T700_EPOXY,
        PredefinedMaterials.M55J_EPOXY,
        PredefinedMaterials.WOVEN_CARBON,
    ]

    created_materials = []
    for material_data in predefined:
        # Check if material exists
        result = await db.execute(
            select(Material).where(Material.name == material_data["name"])
        )
        if result.scalar_one_or_none():
            continue

        db_material = Material(**material_data)
        db.add(db_material)
        created_materials.append(db_material)

    await db.commit()
    for material in created_materials:
        await db.refresh(material)

    return created_materials
