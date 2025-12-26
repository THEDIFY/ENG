"""Manufacturing validation and drapability analysis."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class ValidationSeverity(str, Enum):
    """Severity level for manufacturing violations."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ManufacturingViolation:
    """A manufacturing constraint violation."""

    rule_name: str
    severity: ValidationSeverity
    location: Optional[str]
    description: str
    suggested_fix: str
    affected_elements: Optional[List[int]] = None


@dataclass
class DrapabilityResult:
    """Result of drapability analysis."""

    is_drapeable: bool
    max_shear_angle: float  # degrees
    problem_regions: List[Dict[str, Any]]
    suggested_dart_locations: List[Tuple[float, float, float]]


@dataclass
class MoldSplitResult:
    """Result of mold split analysis."""

    is_manufacturable: bool
    suggested_split_planes: List[Dict[str, Any]]
    undercut_regions: List[Dict[str, Any]]
    draft_violations: List[Dict[str, Any]]


@dataclass
class ManufacturingReport:
    """Complete manufacturing validation report."""

    is_valid: bool
    violations: List[ManufacturingViolation]
    drapability: DrapabilityResult
    mold_splits: MoldSplitResult
    ply_validation: Dict[str, Any]
    insert_validation: Dict[str, Any]
    bond_validation: Dict[str, Any]


class ManufacturingValidator:
    """Validator for composite manufacturing constraints."""

    def __init__(
        self,
        max_shear_angle: float = 45.0,
        min_radius: float = 10.0,
        draft_angle: float = 3.0,
        max_ply_drops_per_zone: int = 4,
        min_ply_thickness: float = 0.2,
    ):
        """Initialize manufacturing validator.

        Args:
            max_shear_angle: Maximum allowable fabric shear (degrees)
            min_radius: Minimum internal radius (mm)
            draft_angle: Minimum draft angle for mold release (degrees)
            max_ply_drops_per_zone: Maximum ply drops in one zone
            min_ply_thickness: Minimum ply thickness (mm)
        """
        self.max_shear_angle = max_shear_angle
        self.min_radius = min_radius
        self.draft_angle = draft_angle
        self.max_ply_drops_per_zone = max_ply_drops_per_zone
        self.min_ply_thickness = min_ply_thickness

    def validate_layup(
        self,
        layup_sequence: List[Dict[str, Any]],
    ) -> Tuple[bool, List[ManufacturingViolation]]:
        """Validate a laminate layup sequence.

        Args:
            layup_sequence: List of ply definitions

        Returns:
            Tuple of (is_valid, list of violations)
        """
        violations = []

        # Check for empty layup
        if not layup_sequence:
            violations.append(
                ManufacturingViolation(
                    rule_name="Empty Layup",
                    severity=ValidationSeverity.CRITICAL,
                    location=None,
                    description="Layup sequence is empty",
                    suggested_fix="Add at least one ply",
                )
            )
            return False, violations

        # Check symmetry
        n_plies = len(layup_sequence)
        is_symmetric = True
        for i in range(n_plies // 2):
            angle_i = layup_sequence[i].get("angle", 0)
            angle_mirror = layup_sequence[n_plies - 1 - i].get("angle", 0)
            if abs(angle_i - angle_mirror) > 0.1:
                is_symmetric = False
                break

        if not is_symmetric:
            violations.append(
                ManufacturingViolation(
                    rule_name="Symmetry",
                    severity=ValidationSeverity.WARNING,
                    location=None,
                    description="Laminate is not symmetric about mid-plane",
                    suggested_fix="Mirror ply sequence about mid-plane",
                )
            )

        # Check balance (+θ and -θ plies)
        angle_counts = {}
        for ply in layup_sequence:
            angle = ply.get("angle", 0) % 180
            if angle not in [0, 90]:
                angle_counts[angle] = angle_counts.get(angle, 0) + 1

        for angle in angle_counts:
            complement = 180 - angle
            if angle_counts.get(angle, 0) != angle_counts.get(complement, 0):
                violations.append(
                    ManufacturingViolation(
                        rule_name="Balance",
                        severity=ValidationSeverity.WARNING,
                        location=None,
                        description=f"Unbalanced: {angle}° has {angle_counts.get(angle, 0)} plies, "
                        f"{complement}° has {angle_counts.get(complement, 0)} plies",
                        suggested_fix="Add complementary angle plies",
                    )
                )
                break

        # Check maximum consecutive same-angle plies
        max_consecutive = 1
        current_consecutive = 1
        for i in range(1, len(layup_sequence)):
            if (
                abs(layup_sequence[i].get("angle", 0) - layup_sequence[i - 1].get("angle", 0))
                < 0.1
            ):
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 1

        if max_consecutive > 4:
            violations.append(
                ManufacturingViolation(
                    rule_name="Consecutive Plies",
                    severity=ValidationSeverity.ERROR,
                    location=None,
                    description=f"Too many consecutive same-angle plies: {max_consecutive} (max 4)",
                    suggested_fix="Interleave with different angle plies",
                )
            )

        # Check ply thickness
        for i, ply in enumerate(layup_sequence):
            thickness = ply.get("thickness", 0)
            if thickness < self.min_ply_thickness:
                violations.append(
                    ManufacturingViolation(
                        rule_name="Minimum Thickness",
                        severity=ValidationSeverity.ERROR,
                        location=f"Ply {i + 1}",
                        description=f"Ply thickness {thickness}mm < minimum {self.min_ply_thickness}mm",
                        suggested_fix="Use thicker ply or combine plies",
                    )
                )

        # Check 10% rule
        total_thickness = sum(p.get("thickness", 0.125) for p in layup_sequence)
        angle_fractions = {"0": 0, "45": 0, "90": 0}
        for ply in layup_sequence:
            angle = ply.get("angle", 0) % 180
            thickness = ply.get("thickness", 0.125)
            if angle < 10 or angle > 170:
                angle_fractions["0"] += thickness
            elif 80 < angle < 100:
                angle_fractions["90"] += thickness
            else:
                angle_fractions["45"] += thickness

        for direction, thickness in angle_fractions.items():
            fraction = thickness / total_thickness if total_thickness > 0 else 0
            if fraction < 0.10:
                violations.append(
                    ManufacturingViolation(
                        rule_name="10% Rule",
                        severity=ValidationSeverity.WARNING,
                        location=None,
                        description=f"{direction}° plies are {fraction * 100:.1f}% (< 10% required)",
                        suggested_fix=f"Add more {direction}° plies",
                    )
                )

        is_valid = not any(v.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL] for v in violations)
        return is_valid, violations

    def analyze_drapability(
        self,
        surface_mesh: Any,
        ply_direction: float = 0,
    ) -> DrapabilityResult:
        """Analyze fabric drapability over a surface.

        Args:
            surface_mesh: Surface mesh (nodes and elements)
            ply_direction: Primary fiber direction (degrees)

        Returns:
            DrapabilityResult with shear angles and problem regions
        """
        # Mock implementation
        # Real implementation would use kinematic draping simulation

        # Simulate some problem regions for complex geometry
        problem_regions = []
        max_shear = 0

        # Simulate shear angle distribution
        if hasattr(surface_mesh, "elements"):
            n_elements = len(surface_mesh.elements)
            shear_angles = np.random.exponential(10, n_elements)
            shear_angles = np.clip(shear_angles, 0, 60)
            max_shear = float(np.max(shear_angles))

            # Find elements exceeding limit
            high_shear_elements = np.where(shear_angles > self.max_shear_angle)[0]
            for elem_id in high_shear_elements[:5]:  # Limit to 5 regions
                problem_regions.append(
                    {
                        "element_id": int(elem_id),
                        "shear_angle": float(shear_angles[elem_id]),
                        "severity": "high" if shear_angles[elem_id] > 50 else "medium",
                    }
                )
        else:
            max_shear = 30.0  # Default assumption

        # Suggest dart locations for high-shear regions
        dart_locations = []
        if max_shear > self.max_shear_angle:
            # Suggest darts at regular intervals
            dart_locations = [
                (500.0, 200.0, 100.0),
                (1500.0, 200.0, 100.0),
                (2500.0, 200.0, 100.0),
            ]

        return DrapabilityResult(
            is_drapeable=max_shear <= self.max_shear_angle,
            max_shear_angle=max_shear,
            problem_regions=problem_regions,
            suggested_dart_locations=dart_locations,
        )

    def analyze_mold_splits(
        self,
        geometry: Any,
        pull_direction: Tuple[float, float, float] = (0, 0, 1),
    ) -> MoldSplitResult:
        """Analyze mold split requirements for manufacturing.

        Args:
            geometry: Geometry to analyze
            pull_direction: Primary mold pull direction

        Returns:
            MoldSplitResult with split planes and undercuts
        """
        # Mock implementation
        # Real implementation would analyze geometry for draft and undercuts

        # Suggest split planes for typical chassis geometry
        suggested_splits = [
            {
                "plane_type": "horizontal",
                "z_position": 750.0,  # mm
                "description": "Main horizontal split at chassis mid-height",
            },
            {
                "plane_type": "vertical",
                "y_position": 0.0,
                "description": "Centerline vertical split for symmetric halves",
            },
        ]

        # Check for undercuts (simplified)
        undercuts = []
        draft_violations = []

        return MoldSplitResult(
            is_manufacturable=len(undercuts) == 0,
            suggested_split_planes=suggested_splits,
            undercut_regions=undercuts,
            draft_violations=draft_violations,
        )

    def validate_inserts(
        self,
        insert_definitions: List[Dict[str, Any]],
    ) -> Tuple[bool, List[ManufacturingViolation]]:
        """Validate metallic insert placements.

        Args:
            insert_definitions: List of insert specifications

        Returns:
            Tuple of (is_valid, violations)
        """
        violations = []

        for i, insert in enumerate(insert_definitions):
            # Check edge distance
            edge_distance = insert.get("edge_distance", 0)
            min_edge = insert.get("diameter", 6) * 3  # 3D minimum
            if edge_distance < min_edge:
                violations.append(
                    ManufacturingViolation(
                        rule_name="Insert Edge Distance",
                        severity=ValidationSeverity.ERROR,
                        location=f"Insert {i + 1}",
                        description=f"Edge distance {edge_distance}mm < minimum {min_edge}mm",
                        suggested_fix="Move insert away from edge",
                    )
                )

            # Check insert spacing
            insert_spacing = insert.get("spacing_to_nearest", float("inf"))
            min_spacing = insert.get("diameter", 6) * 4  # 4D minimum
            if insert_spacing < min_spacing:
                violations.append(
                    ManufacturingViolation(
                        rule_name="Insert Spacing",
                        severity=ValidationSeverity.ERROR,
                        location=f"Insert {i + 1}",
                        description=f"Insert spacing {insert_spacing}mm < minimum {min_spacing}mm",
                        suggested_fix="Increase spacing between inserts",
                    )
                )

        is_valid = not any(v.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL] for v in violations)
        return is_valid, violations

    def validate_adhesive_bonds(
        self,
        bond_definitions: List[Dict[str, Any]],
    ) -> Tuple[bool, List[ManufacturingViolation]]:
        """Validate adhesive bond areas.

        Args:
            bond_definitions: List of bond area specifications

        Returns:
            Tuple of (is_valid, violations)
        """
        violations = []

        for i, bond in enumerate(bond_definitions):
            # Check bond width
            bond_width = bond.get("width", 0)
            min_width = 25.0  # mm minimum
            if bond_width < min_width:
                violations.append(
                    ManufacturingViolation(
                        rule_name="Bond Width",
                        severity=ValidationSeverity.WARNING,
                        location=f"Bond {i + 1}",
                        description=f"Bond width {bond_width}mm < recommended {min_width}mm",
                        suggested_fix="Increase bond width for structural integrity",
                    )
                )

            # Check surface preparation
            if not bond.get("surface_prep_specified", False):
                violations.append(
                    ManufacturingViolation(
                        rule_name="Surface Preparation",
                        severity=ValidationSeverity.INFO,
                        location=f"Bond {i + 1}",
                        description="Surface preparation method not specified",
                        suggested_fix="Specify surface preparation (e.g., peel ply, sanding, plasma)",
                    )
                )

        is_valid = not any(v.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL] for v in violations)
        return is_valid, violations

    def generate_full_report(
        self,
        layup_sequence: List[Dict[str, Any]],
        surface_mesh: Any,
        geometry: Any,
        inserts: List[Dict[str, Any]] = None,
        bonds: List[Dict[str, Any]] = None,
    ) -> ManufacturingReport:
        """Generate complete manufacturing validation report.

        Args:
            layup_sequence: Laminate layup sequence
            surface_mesh: Surface mesh for drapability
            geometry: Full geometry for mold analysis
            inserts: Optional insert definitions
            bonds: Optional bond area definitions

        Returns:
            Complete ManufacturingReport
        """
        all_violations = []

        # Validate layup
        layup_valid, layup_violations = self.validate_layup(layup_sequence)
        all_violations.extend(layup_violations)

        # Analyze drapability
        drapability = self.analyze_drapability(surface_mesh)
        if not drapability.is_drapeable:
            all_violations.append(
                ManufacturingViolation(
                    rule_name="Drapability",
                    severity=ValidationSeverity.ERROR,
                    location=None,
                    description=f"Max shear angle {drapability.max_shear_angle:.1f}° exceeds limit {self.max_shear_angle}°",
                    suggested_fix="Add darts or modify geometry",
                )
            )

        # Analyze mold splits
        mold_splits = self.analyze_mold_splits(geometry)

        # Validate inserts
        if inserts:
            insert_valid, insert_violations = self.validate_inserts(inserts)
            all_violations.extend(insert_violations)
        else:
            insert_valid = True
            insert_violations = []

        # Validate bonds
        if bonds:
            bond_valid, bond_violations = self.validate_adhesive_bonds(bonds)
            all_violations.extend(bond_violations)
        else:
            bond_valid = True
            bond_violations = []

        # Overall validity
        is_valid = not any(
            v.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]
            for v in all_violations
        )

        return ManufacturingReport(
            is_valid=is_valid,
            violations=all_violations,
            drapability=drapability,
            mold_splits=mold_splits,
            ply_validation={"valid": layup_valid, "violations": len(layup_violations)},
            insert_validation={"valid": insert_valid, "violations": len(insert_violations)},
            bond_validation={"valid": bond_valid, "violations": len(bond_violations)},
        )
