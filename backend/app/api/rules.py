"""Baja Rules API router for rules parsing and constraint management."""

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/rules", tags=["rules"])


class BajaRuleCategory(BaseModel):
    """Category of Baja 1000 rules."""

    name: str
    description: str
    rules: List[Dict[str, Any]]


class BajaRulesSet(BaseModel):
    """Complete Baja 1000 rules set."""

    version: str = "2024"
    categories: List[BajaRuleCategory]


# Baja 1000 Trophy Truck Rules (simplified version for demo)
BAJA_1000_RULES = BajaRulesSet(
    version="2024",
    categories=[
        BajaRuleCategory(
            name="Safety Equipment",
            description="Mandatory safety requirements for Trophy Trucks",
            rules=[
                {
                    "id": "SE-001",
                    "name": "Roll Cage",
                    "description": "Full roll cage with minimum 1.75\" x 0.120\" DOM tubing",
                    "type": "structural",
                    "requirements": {
                        "material": "DOM Steel or Chromoly",
                        "min_diameter_inches": 1.75,
                        "min_wall_thickness_inches": 0.120,
                        "construction": "Fully welded, no bolt-together joints in main hoop",
                    },
                },
                {
                    "id": "SE-002",
                    "name": "Fire Suppression",
                    "description": "Onboard fire suppression system required",
                    "type": "safety_system",
                    "requirements": {
                        "type": "AFFF or Halon replacement",
                        "min_capacity_lbs": 5,
                        "activation": "Driver accessible, quick-release",
                    },
                },
                {
                    "id": "SE-003",
                    "name": "Fuel Cell",
                    "description": "FIA-approved fuel cell required",
                    "type": "fuel_system",
                    "requirements": {
                        "certification": "FIA FT3 or FT3.5",
                        "max_capacity_gallons": 55,
                        "foam_filled": True,
                        "rollover_valve": True,
                    },
                },
                {
                    "id": "SE-004",
                    "name": "Harness",
                    "description": "5-point or 6-point racing harness",
                    "type": "restraint",
                    "requirements": {
                        "min_points": 5,
                        "certification": "SFI 16.1 or FIA 8853",
                        "max_age_years": 5,
                    },
                },
            ],
        ),
        BajaRuleCategory(
            name="Dimensional Limits",
            description="Maximum and minimum dimensions for Trophy Trucks",
            rules=[
                {
                    "id": "DL-001",
                    "name": "Maximum Width",
                    "description": "Overall width including tires",
                    "type": "dimension",
                    "value": 96,
                    "unit": "inches",
                    "limit_type": "max",
                },
                {
                    "id": "DL-002",
                    "name": "Maximum Length",
                    "description": "Overall length",
                    "type": "dimension",
                    "value": 220,
                    "unit": "inches",
                    "limit_type": "max",
                },
                {
                    "id": "DL-003",
                    "name": "Minimum Ground Clearance",
                    "description": "Ground clearance at static ride height",
                    "type": "dimension",
                    "value": 10,
                    "unit": "inches",
                    "limit_type": "min",
                },
                {
                    "id": "DL-004",
                    "name": "Wheelbase",
                    "description": "Distance from front to rear axle",
                    "type": "dimension",
                    "min_value": 100,
                    "max_value": 140,
                    "unit": "inches",
                    "limit_type": "range",
                },
                {
                    "id": "DL-005",
                    "name": "Front Track",
                    "description": "Distance between front wheel centers",
                    "type": "dimension",
                    "min_value": 60,
                    "max_value": 90,
                    "unit": "inches",
                    "limit_type": "range",
                },
                {
                    "id": "DL-006",
                    "name": "Rear Track",
                    "description": "Distance between rear wheel centers",
                    "type": "dimension",
                    "min_value": 60,
                    "max_value": 90,
                    "unit": "inches",
                    "limit_type": "range",
                },
            ],
        ),
        BajaRuleCategory(
            name="Suspension",
            description="Suspension system requirements",
            rules=[
                {
                    "id": "SU-001",
                    "name": "Wheel Travel",
                    "description": "Minimum suspension travel",
                    "type": "performance",
                    "requirements": {
                        "front_min_inches": 18,
                        "rear_min_inches": 22,
                    },
                },
                {
                    "id": "SU-002",
                    "name": "Shock Absorbers",
                    "description": "Bypass or coilover shocks required",
                    "type": "component",
                    "requirements": {
                        "min_quantity_front": 2,
                        "min_quantity_rear": 4,
                        "reservoir": "Remote recommended",
                    },
                },
            ],
        ),
        BajaRuleCategory(
            name="Engine and Drivetrain",
            description="Powertrain specifications",
            rules=[
                {
                    "id": "ED-001",
                    "name": "Engine Displacement",
                    "description": "Maximum engine displacement",
                    "type": "performance",
                    "value": 500,
                    "unit": "cubic_inches",
                    "limit_type": "max",
                },
                {
                    "id": "ED-002",
                    "name": "Drive Type",
                    "description": "Rear-wheel or four-wheel drive",
                    "type": "drivetrain",
                    "allowed_values": ["RWD", "4WD", "AWD"],
                },
                {
                    "id": "ED-003",
                    "name": "Transmission",
                    "description": "Manual or automatic transmission",
                    "type": "drivetrain",
                    "allowed_values": ["Manual", "Automatic", "Sequential"],
                },
            ],
        ),
        BajaRuleCategory(
            name="Weight",
            description="Minimum weight requirements",
            rules=[
                {
                    "id": "WT-001",
                    "name": "Minimum Race Weight",
                    "description": "Minimum weight with driver and co-driver",
                    "type": "weight",
                    "value": 5500,
                    "unit": "lbs",
                    "limit_type": "min",
                    "notes": "Includes fuel, driver, co-driver in race-ready condition",
                },
            ],
        ),
        BajaRuleCategory(
            name="Tires and Wheels",
            description="Tire and wheel specifications",
            rules=[
                {
                    "id": "TW-001",
                    "name": "Tire Size",
                    "description": "Maximum tire dimensions",
                    "type": "dimension",
                    "requirements": {
                        "max_diameter_inches": 40,
                        "max_width_inches": 15,
                    },
                },
                {
                    "id": "TW-002",
                    "name": "Wheel Size",
                    "description": "Wheel diameter range",
                    "type": "dimension",
                    "requirements": {
                        "diameter_inches": [17, 20],
                        "type": "Beadlock required for off-road",
                    },
                },
            ],
        ),
    ],
)


class RulesParseRequest(BaseModel):
    """Request to parse rules with optional custom constraints."""

    rule_set_version: str = "2024"
    custom_constraints: List[Dict[str, Any]] = Field(default_factory=list)
    override_rules: List[str] = Field(
        default_factory=list, description="List of rule IDs to override"
    )


class RulesParseResponse(BaseModel):
    """Response with parsed rules and constraints."""

    version: str
    total_rules: int
    categories: List[str]
    constraints: List[Dict[str, Any]]
    dimensional_constraints: Dict[str, Any]
    safety_requirements: List[Dict[str, Any]]


@router.get("/", response_model=BajaRulesSet)
async def get_rules() -> BajaRulesSet:
    """Get the complete Baja 1000 rules set."""
    return BAJA_1000_RULES


@router.get("/categories", response_model=List[str])
async def list_categories() -> List[str]:
    """List all rule categories."""
    return [cat.name for cat in BAJA_1000_RULES.categories]


@router.get("/categories/{category_name}", response_model=BajaRuleCategory)
async def get_category(category_name: str) -> BajaRuleCategory:
    """Get rules for a specific category."""
    for category in BAJA_1000_RULES.categories:
        if category.name.lower() == category_name.lower():
            return category
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Category '{category_name}' not found",
    )


@router.post("/parse", response_model=RulesParseResponse)
async def parse_rules(request: RulesParseRequest) -> RulesParseResponse:
    """Parse rules and generate optimization constraints."""
    # Collect all constraints from rules
    constraints = []
    dimensional_constraints = {}
    safety_requirements = []

    for category in BAJA_1000_RULES.categories:
        for rule in category.rules:
            # Skip overridden rules
            if rule["id"] in request.override_rules:
                continue

            constraint = {
                "rule_id": rule["id"],
                "name": rule["name"],
                "category": category.name,
                "type": rule.get("type"),
            }

            # Extract dimensional constraints
            if rule.get("type") == "dimension":
                dim_constraint = {
                    "name": rule["name"],
                    "unit": rule.get("unit", "mm"),
                }
                if "value" in rule:
                    dim_constraint["value"] = rule["value"]
                    dim_constraint["limit_type"] = rule.get("limit_type", "max")
                if "min_value" in rule:
                    dim_constraint["min"] = rule["min_value"]
                if "max_value" in rule:
                    dim_constraint["max"] = rule["max_value"]
                dimensional_constraints[rule["id"]] = dim_constraint
                constraint["dimensional"] = dim_constraint

            # Extract safety requirements
            if category.name == "Safety Equipment":
                safety_requirements.append(
                    {
                        "id": rule["id"],
                        "name": rule["name"],
                        "requirements": rule.get("requirements", {}),
                    }
                )

            if "requirements" in rule:
                constraint["requirements"] = rule["requirements"]
            if "value" in rule:
                constraint["value"] = rule["value"]
                constraint["unit"] = rule.get("unit")

            constraints.append(constraint)

    # Add custom constraints
    for custom in request.custom_constraints:
        constraints.append(
            {
                "rule_id": f"CUSTOM-{len(constraints)}",
                "name": custom.get("name", "Custom Constraint"),
                "category": "Custom",
                "type": custom.get("type", "custom"),
                **custom,
            }
        )

    return RulesParseResponse(
        version=BAJA_1000_RULES.version,
        total_rules=len(constraints),
        categories=[cat.name for cat in BAJA_1000_RULES.categories],
        constraints=constraints,
        dimensional_constraints=dimensional_constraints,
        safety_requirements=safety_requirements,
    )


@router.get("/dimensional-defaults")
async def get_dimensional_defaults() -> Dict[str, Any]:
    """Get default dimensional constraints in metric units (mm)."""
    return {
        "max_width_mm": 2438,  # 96 inches
        "max_length_mm": 5588,  # 220 inches
        "min_ground_clearance_mm": 254,  # 10 inches
        "wheelbase_min_mm": 2540,  # 100 inches
        "wheelbase_max_mm": 3556,  # 140 inches
        "front_track_min_mm": 1524,  # 60 inches
        "front_track_max_mm": 2286,  # 90 inches
        "rear_track_min_mm": 1524,  # 60 inches
        "rear_track_max_mm": 2286,  # 90 inches
    }
