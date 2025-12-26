"""
CAD geometry generator for manufacturability
Converts optimization results to 3D CAD format (STL)
Generates layup schedules and fastener maps
"""

import numpy as np
from engine.material_models import CarbonFiberMaterial, optimize_layup_for_loading


class CADGenerator:
    """Generates manufacturable CAD geometry from optimization results"""
    
    def __init__(self, optimization_result):
        """
        Initialize CAD generator
        
        optimization_result: dict from ChassisOptimizer
        """
        self.result = optimization_result
        self.geometry = np.array(optimization_result['binary_geometry'])
        self.design_space = optimization_result['design_space']
        
    def generate_geometry(self):
        """
        Generate 3D CAD geometry in STL format
        Returns STL data and metadata
        """
        # Convert voxel data to mesh using marching cubes approach
        vertices, faces = self._voxels_to_mesh(self.geometry)
        
        # Smooth mesh for manufacturability
        vertices_smooth = self._smooth_mesh(vertices, faces)
        
        # Generate STL data
        stl_data = self._create_stl(vertices_smooth, faces)
        
        return {
            'stl_data': stl_data,
            'vertices': vertices_smooth.tolist(),
            'faces': faces.tolist(),
            'num_vertices': len(vertices_smooth),
            'num_faces': len(faces),
            'bounding_box': self._calculate_bounding_box(vertices_smooth)
        }
    
    def _voxels_to_mesh(self, voxels):
        """Convert voxel grid to triangle mesh (simplified marching cubes)"""
        vertices = []
        faces = []
        vertex_map = {}
        
        # Get voxel dimensions in physical space
        dims = self.design_space['dimensions']
        vox_dims = self.design_space['voxels']
        scale = [dims[i] / vox_dims[i] for i in range(3)]
        
        # Iterate through voxels to create surface mesh
        for i in range(voxels.shape[0] - 1):
            for j in range(voxels.shape[1] - 1):
                for k in range(voxels.shape[2] - 1):
                    if voxels[i, j, k] > 0.5:
                        # Create cube faces where adjacent voxels are empty
                        self._add_cube_faces(i, j, k, voxels, vertices, faces, 
                                           vertex_map, scale)
        
        return np.array(vertices), np.array(faces)
    
    def _add_cube_faces(self, i, j, k, voxels, vertices, faces, vertex_map, scale):
        """Add faces for a voxel cube where it borders empty space"""
        # Define cube vertices
        cube_verts = [
            (i, j, k), (i+1, j, k), (i+1, j+1, k), (i, j+1, k),  # Bottom
            (i, j, k+1), (i+1, j, k+1), (i+1, j+1, k+1), (i, j+1, k+1)  # Top
        ]
        
        # Define cube faces (each face = 2 triangles)
        cube_faces = [
            # Bottom (-Z)
            ([0, 1, 2], [0, 2, 3]) if k == 0 or voxels[i, j, k-1] < 0.5 else None,
            # Top (+Z)
            ([4, 6, 5], [4, 7, 6]) if k+1 >= voxels.shape[2] or voxels[i, j, k+1] < 0.5 else None,
            # Front (-Y)
            ([0, 4, 5], [0, 5, 1]) if j == 0 or voxels[i, j-1, k] < 0.5 else None,
            # Back (+Y)
            ([2, 6, 7], [2, 7, 3]) if j+1 >= voxels.shape[1] or voxels[i, j+1, k] < 0.5 else None,
            # Left (-X)
            ([0, 3, 7], [0, 7, 4]) if i == 0 or voxels[i-1, j, k] < 0.5 else None,
            # Right (+X)
            ([1, 5, 6], [1, 6, 2]) if i+1 >= voxels.shape[0] or voxels[i+1, j, k] < 0.5 else None,
        ]
        
        for face_pair in cube_faces:
            if face_pair is not None:
                for tri in face_pair:
                    face_indices = []
                    for vert_idx in tri:
                        v = cube_verts[vert_idx]
                        # Scale to physical dimensions
                        v_scaled = tuple(v[d] * scale[d] for d in range(3))
                        
                        if v_scaled not in vertex_map:
                            vertex_map[v_scaled] = len(vertices)
                            vertices.append(v_scaled)
                        
                        face_indices.append(vertex_map[v_scaled])
                    
                    faces.append(face_indices)
    
    def _smooth_mesh(self, vertices, faces, iterations=2):
        """
        Apply Laplacian smoothing to mesh
        
        NOTE: This implementation recalculates adjacency on each iteration.
        For better performance with large meshes, consider building adjacency
        structure once and reusing it.
        """
        vertices = np.array(vertices, dtype=float)
        
        # Build adjacency structure once (optimization)
        adjacency = [[] for _ in range(len(vertices))]
        for face in faces:
            for i in range(3):
                v1, v2 = face[i], face[(i+1)%3]
                adjacency[v1].append(v2)
                adjacency[v2].append(v1)
        
        # Remove duplicates in adjacency
        adjacency = [list(set(neighbors)) for neighbors in adjacency]
        
        for _ in range(iterations):
            # Smooth vertices based on pre-built adjacency
            new_vertices = vertices.copy()
            for i, neighbors in enumerate(adjacency):
                if len(neighbors) > 0:
                    new_vertices[i] = 0.5 * vertices[i] + 0.5 * np.mean(vertices[neighbors], axis=0)
            vertices = new_vertices
        
        return vertices
    
    def _create_stl(self, vertices, faces):
        """Create STL file content (ASCII format)"""
        stl_lines = ["solid chassis"]
        
        for face in faces:
            # Calculate normal
            v0, v1, v2 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
            edge1 = v1 - v0
            edge2 = v2 - v0
            normal = np.cross(edge1, edge2)
            norm_length = np.linalg.norm(normal)
            if norm_length > 0:
                normal = normal / norm_length
            else:
                normal = np.array([0, 0, 1])
            
            stl_lines.append(f"  facet normal {normal[0]:.6e} {normal[1]:.6e} {normal[2]:.6e}")
            stl_lines.append("    outer loop")
            for v_idx in face:
                v = vertices[v_idx]
                stl_lines.append(f"      vertex {v[0]:.6e} {v[1]:.6e} {v[2]:.6e}")
            stl_lines.append("    endloop")
            stl_lines.append("  endfacet")
        
        stl_lines.append("endsolid chassis")
        
        return "\n".join(stl_lines)
    
    def _calculate_bounding_box(self, vertices):
        """Calculate bounding box of mesh"""
        vertices = np.array(vertices)
        min_coords = np.min(vertices, axis=0)
        max_coords = np.max(vertices, axis=0)
        
        return {
            'min': min_coords.tolist(),
            'max': max_coords.tolist(),
            'size': (max_coords - min_coords).tolist()
        }
    
    def generate_layup_schedule(self):
        """
        Generate carbon fiber layup schedule for different chassis sections
        """
        # Analyze loading from optimization results
        loads = self.result['loads']
        
        # Define chassis sections
        sections = {
            'main_rails': {
                'loading_type': 'combined',
                'thickness_mm': 6.0,
                'area_m2': 2.5
            },
            'cross_members': {
                'loading_type': 'bending',
                'thickness_mm': 4.0,
                'area_m2': 1.2
            },
            'suspension_towers': {
                'loading_type': 'axial',
                'thickness_mm': 8.0,
                'area_m2': 0.8
            },
            'floor_pan': {
                'loading_type': 'bending',
                'thickness_mm': 3.0,
                'area_m2': 4.0
            },
            'bulkheads': {
                'loading_type': 'combined',
                'thickness_mm': 5.0,
                'area_m2': 1.5
            }
        }
        
        layup_schedule = {}
        material = CarbonFiberMaterial('T800_Epoxy')
        
        for section_name, section_info in sections.items():
            # Get recommended layup
            layup_rec = optimize_layup_for_loading(section_info['loading_type'])
            
            # Calculate number of plies needed
            ply_thickness = material.props['ply_thickness'] * 1000  # Convert to mm
            n_plies = int(section_info['thickness_mm'] / ply_thickness)
            
            # Scale layup sequence to match required plies
            layup_sequence = layup_rec['layup_sequence']
            while len(layup_sequence) < n_plies:
                layup_sequence = layup_sequence + layup_sequence
            layup_sequence = layup_sequence[:n_plies]
            
            # Calculate properties
            laminate_props = material.get_laminate_properties(layup_sequence)
            
            layup_schedule[section_name] = {
                'layup_sequence': layup_sequence,
                'total_plies': n_plies,
                'thickness_mm': section_info['thickness_mm'],
                'material': 'T800/Epoxy',
                'area_m2': section_info['area_m2'],
                'mass_kg': laminate_props['mass_per_area'] * section_info['area_m2'],
                'properties': {
                    'Ex_GPa': laminate_props['Ex'] / 1e9,
                    'Ey_GPa': laminate_props['Ey'] / 1e9,
                    'Gxy_GPa': laminate_props['Gxy'] / 1e9
                }
            }
        
        # Calculate total mass
        total_mass = sum(section['mass_kg'] for section in layup_schedule.values())
        
        return {
            'sections': layup_schedule,
            'total_mass_kg': total_mass,
            'material_type': 'T800/Epoxy',
            'manufacturing_notes': [
                'Use autoclave cure at 180°C',
                'Ensure proper fiber orientation alignment',
                'Apply vacuum bag pressure of -0.9 bar',
                'Cure time: 2 hours + 4 hour post-cure'
            ]
        }
    
    def generate_fastener_map(self):
        """
        Generate fastener locations and specifications for assembly
        """
        # Define connection points
        fastener_locations = []
        
        # Main rail connections (every 300mm)
        rail_length = self.design_space['dimensions'][0]
        n_fasteners_rail = int(rail_length / 0.3) + 1
        
        for i in range(n_fasteners_rail):
            x = i * 0.3
            # Left rail
            fastener_locations.append({
                'id': f'RAIL_L_{i+1:03d}',
                'location': [x, 0.2, 0.5],
                'type': 'M10_Grade_12.9',
                'torque_Nm': 55,
                'section': 'main_rails',
                'notes': 'Use threadlocker blue'
            })
            # Right rail
            fastener_locations.append({
                'id': f'RAIL_R_{i+1:03d}',
                'location': [x, 2.0, 0.5],
                'type': 'M10_Grade_12.9',
                'torque_Nm': 55,
                'section': 'main_rails',
                'notes': 'Use threadlocker blue'
            })
        
        # Suspension mount fasteners
        suspension_points = [
            ([0.5, 0.3, 0.2], 'FL'),  # Front left
            ([0.5, 1.9, 0.2], 'FR'),  # Front right
            ([4.0, 0.3, 0.2], 'RL'),  # Rear left
            ([4.0, 1.9, 0.2], 'RR'),  # Rear right
        ]
        
        for loc, pos_id in suspension_points:
            for j in range(4):  # 4 bolts per mount
                angle = j * 90
                offset_x = 0.05 * np.cos(np.radians(angle))
                offset_y = 0.05 * np.sin(np.radians(angle))
                
                fastener_locations.append({
                    'id': f'SUSP_{pos_id}_{j+1}',
                    'location': [loc[0] + offset_x, loc[1] + offset_y, loc[2]],
                    'type': 'M12_Grade_12.9',
                    'torque_Nm': 85,
                    'section': 'suspension_towers',
                    'notes': 'Critical connection - inspect regularly'
                })
        
        # Cross member fasteners
        n_cross_members = 6
        for i in range(n_cross_members):
            x = (i + 1) * rail_length / (n_cross_members + 1)
            for side in ['L', 'R']:
                y = 0.2 if side == 'L' else 2.0
                fastener_locations.append({
                    'id': f'CROSS_{i+1:02d}_{side}',
                    'location': [x, y, 0.6],
                    'type': 'M8_Grade_10.9',
                    'torque_Nm': 35,
                    'section': 'cross_members',
                    'notes': 'Alternate tightening pattern'
                })
        
        # Fastener summary
        fastener_types = {}
        for fastener in fastener_locations:
            ftype = fastener['type']
            if ftype not in fastener_types:
                fastener_types[ftype] = 0
            fastener_types[ftype] += 1
        
        return {
            'fasteners': fastener_locations,
            'total_count': len(fastener_locations),
            'types_summary': fastener_types,
            'specifications': {
                'M8_Grade_10.9': {
                    'size': 'M8',
                    'grade': '10.9',
                    'torque_Nm': 35,
                    'washer': 'Required'
                },
                'M10_Grade_12.9': {
                    'size': 'M10',
                    'grade': '12.9',
                    'torque_Nm': 55,
                    'washer': 'Required'
                },
                'M12_Grade_12.9': {
                    'size': 'M12',
                    'grade': '12.9',
                    'torque_Nm': 85,
                    'washer': 'Required + Lock washer'
                }
            },
            'assembly_notes': [
                'Clean all threads before assembly',
                'Apply anti-seize to all fasteners',
                'Use calibrated torque wrench',
                'Tighten in specified sequence',
                'Re-torque after first 100 miles'
            ]
        }
