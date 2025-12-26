"""CAD geometry export utilities."""

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


@dataclass
class ExportResult:
    """Result of geometry export."""

    filepath: str
    format: str
    file_size: int
    metadata: Dict[str, Any]


class GeometryExporter:
    """Exporter for CAD geometry in various formats."""

    def __init__(self, output_dir: str = "./exports"):
        """Initialize geometry exporter.

        Args:
            output_dir: Directory for exported files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def export_stl(
        self,
        mesh_or_density: Any,
        filename: str,
        threshold: float = 0.5,
    ) -> ExportResult:
        """Export geometry as STL file.

        Args:
            mesh_or_density: Mesh object or density field
            filename: Output filename (without extension)
            threshold: Density threshold for isosurface

        Returns:
            ExportResult with file information
        """
        filepath = os.path.join(self.output_dir, f"{filename}.stl")

        # Mock STL generation
        # Real implementation would use marching cubes for density field
        # or direct mesh export

        if hasattr(mesh_or_density, "nodes") and hasattr(mesh_or_density, "elements"):
            # Export mesh as STL
            content = self._mesh_to_stl(mesh_or_density)
        else:
            # Export density field as STL using marching cubes
            content = self._density_to_stl(mesh_or_density, threshold)

        with open(filepath, "w") as f:
            f.write(content)

        file_size = os.path.getsize(filepath)

        return ExportResult(
            filepath=filepath,
            format="STL",
            file_size=file_size,
            metadata={"threshold": threshold, "units": "mm"},
        )

    def _mesh_to_stl(self, mesh: Any) -> str:
        """Convert mesh to ASCII STL format."""
        lines = ["solid mesh"]

        if hasattr(mesh, "elements") and hasattr(mesh, "nodes"):
            for elem in mesh.elements[:100]:  # Limit for demo
                # Triangulate each element face
                if len(elem) >= 4:
                    # Quad or hex face
                    nodes = [mesh.nodes[i] for i in elem[:4]]
                    # First triangle
                    normal = self._compute_normal(nodes[0], nodes[1], nodes[2])
                    lines.append(f"  facet normal {normal[0]:.6e} {normal[1]:.6e} {normal[2]:.6e}")
                    lines.append("    outer loop")
                    for n in nodes[:3]:
                        lines.append(f"      vertex {n[0]:.6e} {n[1]:.6e} {n[2]:.6e}")
                    lines.append("    endloop")
                    lines.append("  endfacet")
                    # Second triangle
                    lines.append(f"  facet normal {normal[0]:.6e} {normal[1]:.6e} {normal[2]:.6e}")
                    lines.append("    outer loop")
                    lines.append(f"      vertex {nodes[0][0]:.6e} {nodes[0][1]:.6e} {nodes[0][2]:.6e}")
                    lines.append(f"      vertex {nodes[2][0]:.6e} {nodes[2][1]:.6e} {nodes[2][2]:.6e}")
                    lines.append(f"      vertex {nodes[3][0]:.6e} {nodes[3][1]:.6e} {nodes[3][2]:.6e}")
                    lines.append("    endloop")
                    lines.append("  endfacet")

        lines.append("endsolid mesh")
        return "\n".join(lines)

    def _density_to_stl(self, density: np.ndarray, threshold: float) -> str:
        """Convert density field to STL using simplified marching cubes."""
        lines = ["solid density_field"]
        # Placeholder - real implementation would use marching cubes
        lines.append("  # Density field STL - placeholder")
        lines.append("endsolid density_field")
        return "\n".join(lines)

    def _compute_normal(
        self, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray
    ) -> np.ndarray:
        """Compute triangle normal."""
        v1 = np.array(p2) - np.array(p1)
        v2 = np.array(p3) - np.array(p1)
        normal = np.cross(v1, v2)
        norm = np.linalg.norm(normal)
        if norm > 0:
            normal = normal / norm
        return normal

    def export_gltf(
        self,
        mesh_or_density: Any,
        filename: str,
        threshold: float = 0.5,
    ) -> ExportResult:
        """Export geometry as glTF file for web visualization.

        Args:
            mesh_or_density: Mesh object or density field
            filename: Output filename (without extension)
            threshold: Density threshold

        Returns:
            ExportResult with file information
        """
        filepath = os.path.join(self.output_dir, f"{filename}.gltf")

        # Create minimal glTF structure
        gltf = {
            "asset": {"version": "2.0", "generator": "Trophy Truck Optimizer"},
            "scene": 0,
            "scenes": [{"nodes": [0]}],
            "nodes": [{"mesh": 0}],
            "meshes": [
                {
                    "primitives": [
                        {
                            "attributes": {"POSITION": 0},
                            "indices": 1,
                        }
                    ]
                }
            ],
            "accessors": [],
            "bufferViews": [],
            "buffers": [],
        }

        with open(filepath, "w") as f:
            json.dump(gltf, f, indent=2)

        file_size = os.path.getsize(filepath)

        return ExportResult(
            filepath=filepath,
            format="glTF",
            file_size=file_size,
            metadata={"threshold": threshold, "units": "mm"},
        )

    def export_step(
        self,
        geometry: Any,
        filename: str,
    ) -> ExportResult:
        """Export geometry as STEP file.

        Args:
            geometry: CAD geometry
            filename: Output filename

        Returns:
            ExportResult with file information
        """
        filepath = os.path.join(self.output_dir, f"{filename}.step")

        # STEP header
        step_content = """ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('Trophy Truck Chassis'),'2;1');
FILE_NAME('{filename}','2024-01-01T00:00:00',('Author'),('Organization'),'Python','Trophy Truck Optimizer','');
FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));
ENDSEC;
DATA;
/* Placeholder STEP data - real implementation would use OpenCASCADE */
#1 = SHAPE_REPRESENTATION('Chassis',(),#10);
#10 = ( GEOMETRIC_REPRESENTATION_CONTEXT(3) 
GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#11)) 
GLOBAL_UNIT_ASSIGNED_CONTEXT((#12,#13,#14)) 
REPRESENTATION_CONTEXT('Context','3D') );
#11 = UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-07),#12,'distance_accuracy_value','');
#12 = ( LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.) );
#13 = ( NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.) );
#14 = ( NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT() );
ENDSEC;
END-ISO-10303-21;
""".format(filename=filename)

        with open(filepath, "w") as f:
            f.write(step_content)

        file_size = os.path.getsize(filepath)

        return ExportResult(
            filepath=filepath,
            format="STEP",
            file_size=file_size,
            metadata={"standard": "AP214", "units": "mm"},
        )


class LayupExporter:
    """Exporter for laminate layup schedules."""

    def __init__(self, output_dir: str = "./exports"):
        """Initialize layup exporter."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def export_csv(
        self,
        layup_data: List[Dict[str, Any]],
        filename: str,
        zones: Optional[List[str]] = None,
    ) -> ExportResult:
        """Export layup schedule as CSV.

        Args:
            layup_data: List of ply definitions
            filename: Output filename
            zones: Optional zone names

        Returns:
            ExportResult
        """
        filepath = os.path.join(self.output_dir, f"{filename}.csv")

        lines = ["Ply Number,Material,Angle (deg),Thickness (mm),Zone,Coverage"]

        for i, ply in enumerate(layup_data):
            line = f"{i + 1},{ply.get('material', 'Carbon/Epoxy')},"
            line += f"{ply.get('angle', 0)},{ply.get('thickness', 0.125)},"
            line += f"{ply.get('zone', 'Full')},{ply.get('coverage', '100%')}"
            lines.append(line)

        content = "\n".join(lines)
        with open(filepath, "w") as f:
            f.write(content)

        return ExportResult(
            filepath=filepath,
            format="CSV",
            file_size=os.path.getsize(filepath),
            metadata={"ply_count": len(layup_data)},
        )

    def export_json(
        self,
        layup_data: List[Dict[str, Any]],
        filename: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ExportResult:
        """Export layup schedule as JSON.

        Args:
            layup_data: List of ply definitions
            filename: Output filename
            metadata: Optional additional metadata

        Returns:
            ExportResult
        """
        filepath = os.path.join(self.output_dir, f"{filename}.json")

        export_data = {
            "version": "1.0",
            "project": "Trophy Truck Chassis",
            "metadata": metadata or {},
            "total_plies": len(layup_data),
            "total_thickness": sum(p.get("thickness", 0.125) for p in layup_data),
            "plies": layup_data,
        }

        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2)

        return ExportResult(
            filepath=filepath,
            format="JSON",
            file_size=os.path.getsize(filepath),
            metadata={"ply_count": len(layup_data)},
        )


class FastenerMapExporter:
    """Exporter for fastener and insert maps."""

    def __init__(self, output_dir: str = "./exports"):
        """Initialize fastener exporter."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def export_fastener_map(
        self,
        fasteners: List[Dict[str, Any]],
        filename: str,
    ) -> ExportResult:
        """Export fastener map as JSON.

        Args:
            fasteners: List of fastener definitions
            filename: Output filename

        Returns:
            ExportResult
        """
        filepath = os.path.join(self.output_dir, f"{filename}.json")

        export_data = {
            "version": "1.0",
            "project": "Trophy Truck Chassis",
            "total_fasteners": len(fasteners),
            "fasteners": fasteners,
            "summary": {
                "by_type": self._summarize_by_type(fasteners),
                "by_size": self._summarize_by_size(fasteners),
            },
        }

        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2)

        return ExportResult(
            filepath=filepath,
            format="JSON",
            file_size=os.path.getsize(filepath),
            metadata={"fastener_count": len(fasteners)},
        )

    def _summarize_by_type(self, fasteners: List[Dict[str, Any]]) -> Dict[str, int]:
        """Summarize fasteners by type."""
        summary = {}
        for f in fasteners:
            ftype = f.get("type", "unknown")
            summary[ftype] = summary.get(ftype, 0) + 1
        return summary

    def _summarize_by_size(self, fasteners: List[Dict[str, Any]]) -> Dict[str, int]:
        """Summarize fasteners by size."""
        summary = {}
        for f in fasteners:
            size = f.get("size", "unknown")
            summary[size] = summary.get(size, 0) + 1
        return summary


class BOMExporter:
    """Exporter for Bill of Materials."""

    def __init__(self, output_dir: str = "./exports"):
        """Initialize BOM exporter."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_bom(
        self,
        layup_data: List[Dict[str, Any]],
        fasteners: List[Dict[str, Any]],
        inserts: List[Dict[str, Any]],
        adhesives: List[Dict[str, Any]],
        filename: str,
    ) -> ExportResult:
        """Generate complete Bill of Materials.

        Args:
            layup_data: Layup schedule
            fasteners: Fastener list
            inserts: Insert list
            adhesives: Adhesive specifications
            filename: Output filename

        Returns:
            ExportResult
        """
        filepath = os.path.join(self.output_dir, f"{filename}.json")

        # Calculate material quantities
        materials = {}
        for ply in layup_data:
            mat_name = ply.get("material", "Carbon/Epoxy")
            thickness = ply.get("thickness", 0.125)
            area = ply.get("area", 10000)  # cm² default

            if mat_name not in materials:
                materials[mat_name] = {"total_area_m2": 0, "total_mass_kg": 0}

            area_m2 = area / 10000  # cm² to m²
            materials[mat_name]["total_area_m2"] += area_m2
            # Assume 1.55 kg/m² for carbon fiber prepreg at 0.125mm
            materials[mat_name]["total_mass_kg"] += area_m2 * thickness / 0.125 * 0.2

        bom = {
            "version": "1.0",
            "project": "Trophy Truck Chassis",
            "composite_materials": materials,
            "fasteners": self._aggregate_items(fasteners, "type", "size"),
            "inserts": self._aggregate_items(inserts, "type", "size"),
            "adhesives": adhesives,
            "total_composite_mass_kg": sum(m["total_mass_kg"] for m in materials.values()),
            "total_fastener_count": len(fasteners),
            "total_insert_count": len(inserts),
        }

        with open(filepath, "w") as f:
            json.dump(bom, f, indent=2)

        return ExportResult(
            filepath=filepath,
            format="JSON",
            file_size=os.path.getsize(filepath),
            metadata={"item_count": len(materials) + len(fasteners) + len(inserts)},
        )

    def _aggregate_items(
        self,
        items: List[Dict[str, Any]],
        key1: str,
        key2: str,
    ) -> List[Dict[str, Any]]:
        """Aggregate items by type and size."""
        aggregated = {}
        for item in items:
            key = (item.get(key1, "unknown"), item.get(key2, "unknown"))
            if key not in aggregated:
                aggregated[key] = {"type": key[0], "size": key[1], "quantity": 0}
            aggregated[key]["quantity"] += 1
        return list(aggregated.values())
