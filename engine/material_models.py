"""
Material models for carbon fiber composites
Used in chassis optimization
"""

import numpy as np


class CarbonFiberMaterial:
    """Carbon fiber composite material properties and models"""
    
    # Standard carbon fiber materials database
    MATERIALS = {
        'T300_Epoxy': {
            'name': 'T300/Epoxy Standard Modulus',
            'E11': 135e9,  # Longitudinal modulus (Pa)
            'E22': 10e9,   # Transverse modulus (Pa)
            'G12': 5e9,    # Shear modulus (Pa)
            'nu12': 0.3,   # Poisson's ratio
            'rho': 1600,   # Density (kg/m³)
            'Xt': 1500e6,  # Tensile strength longitudinal (Pa)
            'Xc': 1200e6,  # Compressive strength longitudinal (Pa)
            'Yt': 50e6,    # Tensile strength transverse (Pa)
            'Yc': 200e6,   # Compressive strength transverse (Pa)
            'S': 70e6,     # Shear strength (Pa)
            'ply_thickness': 0.125e-3  # Ply thickness (m)
        },
        'T800_Epoxy': {
            'name': 'T800/Epoxy Intermediate Modulus',
            'E11': 165e9,
            'E22': 11e9,
            'G12': 5.5e9,
            'nu12': 0.32,
            'rho': 1580,
            'Xt': 2200e6,
            'Xc': 1650e6,
            'Yt': 60e6,
            'Yc': 230e6,
            'S': 90e6,
            'ply_thickness': 0.125e-3
        },
        'M40J_Epoxy': {
            'name': 'M40J/Epoxy High Modulus',
            'E11': 240e9,
            'E22': 12e9,
            'G12': 6e9,
            'nu12': 0.33,
            'rho': 1550,
            'Xt': 1800e6,
            'Xc': 1400e6,
            'Yt': 55e6,
            'Yc': 220e6,
            'S': 85e6,
            'ply_thickness': 0.125e-3
        }
    }
    
    def __init__(self, material_type='T800_Epoxy'):
        """Initialize material model"""
        if material_type not in self.MATERIALS:
            raise ValueError(f"Material {material_type} not found")
        
        self.material_type = material_type
        self.props = self.MATERIALS[material_type]
    
    def get_stiffness_matrix(self, theta=0):
        """
        Calculate the stiffness matrix for a ply at angle theta
        theta: fiber orientation angle in degrees
        Returns: Q matrix (3x3) in material coordinates
        """
        E11 = self.props['E11']
        E22 = self.props['E22']
        G12 = self.props['G12']
        nu12 = self.props['nu12']
        nu21 = nu12 * E22 / E11
        
        # Reduced stiffness matrix in material coordinates
        Q11 = E11 / (1 - nu12 * nu21)
        Q12 = nu12 * E22 / (1 - nu12 * nu21)
        Q22 = E22 / (1 - nu12 * nu21)
        Q66 = G12
        
        Q = np.array([
            [Q11, Q12, 0],
            [Q12, Q22, 0],
            [0, 0, Q66]
        ])
        
        # Transform to global coordinates if needed
        if theta != 0:
            theta_rad = np.radians(theta)
            c = np.cos(theta_rad)
            s = np.sin(theta_rad)
            
            # Stress transformation matrix (Reuter matrix)
            T_sigma = np.array([
                [c**2, s**2, 2*s*c],
                [s**2, c**2, -2*s*c],
                [-s*c, s*c, c**2 - s**2]
            ])
            
            # Transform stiffness matrix: Q_global = T_sigma^-T @ Q @ T_sigma^-1
            T_inv = np.linalg.inv(T_sigma)
            Q = T_inv.T @ Q @ T_inv
        
        return Q
    
    def get_laminate_properties(self, layup_sequence):
        """
        Calculate effective laminate properties
        layup_sequence: list of ply angles, e.g., [0, 45, -45, 90]
        Returns: dict with effective properties
        """
        n_plies = len(layup_sequence)
        t_ply = self.props['ply_thickness']
        total_thickness = n_plies * t_ply
        
        # Calculate ABD matrix (Classical Laminate Theory)
        A = np.zeros((3, 3))
        B = np.zeros((3, 3))
        D = np.zeros((3, 3))
        
        z = np.linspace(-total_thickness/2, total_thickness/2, n_plies + 1)
        
        for i, theta in enumerate(layup_sequence):
            Q = self.get_stiffness_matrix(theta)
            z_k = z[i]
            z_k1 = z[i + 1]
            
            A += Q * (z_k1 - z_k)
            B += Q * (z_k1**2 - z_k**2) / 2
            D += Q * (z_k1**3 - z_k**3) / 3
        
        # Calculate effective moduli
        a = np.linalg.inv(A)
        Ex = 1 / (a[0, 0] * total_thickness)
        Ey = 1 / (a[1, 1] * total_thickness)
        Gxy = 1 / (a[2, 2] * total_thickness)
        nuxy = -a[0, 1] / a[0, 0]
        
        return {
            'Ex': Ex,
            'Ey': Ey,
            'Gxy': Gxy,
            'nuxy': nuxy,
            'thickness': total_thickness,
            'mass_per_area': self.props['rho'] * total_thickness,
            'A_matrix': A.tolist(),
            'B_matrix': B.tolist(),
            'D_matrix': D.tolist()
        }
    
    def check_failure(self, stress, layup_angle=0):
        """
        Check failure using Tsai-Wu failure criterion
        stress: [sigma_x, sigma_y, tau_xy] in global coordinates
        Returns: failure index (< 1 is safe)
        """
        # Transform stress to material coordinates
        theta_rad = np.radians(layup_angle)
        c = np.cos(theta_rad)
        s = np.sin(theta_rad)
        
        T = np.array([
            [c**2, s**2, 2*s*c],
            [s**2, c**2, -2*s*c],
            [-s*c, s*c, c**2 - s**2]
        ])
        
        stress_material = T @ stress
        
        sig1 = stress_material[0]
        sig2 = stress_material[1]
        tau12 = stress_material[2]
        
        Xt = self.props['Xt']
        Xc = self.props['Xc']
        Yt = self.props['Yt']
        Yc = self.props['Yc']
        S = self.props['S']
        
        # Tsai-Wu coefficients
        F1 = 1/Xt - 1/Xc
        F2 = 1/Yt - 1/Yc
        F11 = 1/(Xt*Xc)
        F22 = 1/(Yt*Yc)
        F66 = 1/(S*S)
        F12 = -0.5 * np.sqrt(F11 * F22)
        
        # Failure index
        FI = F1*sig1 + F2*sig2 + F11*sig1**2 + F22*sig2**2 + F66*tau12**2 + 2*F12*sig1*sig2
        
        return FI
    
    @staticmethod
    def get_available_materials():
        """Return list of available materials with properties"""
        return {
            name: {
                'name': props['name'],
                'density': props['rho'],
                'E11': props['E11'],
                'E22': props['E22'],
                'tensile_strength': props['Xt']
            }
            for name, props in CarbonFiberMaterial.MATERIALS.items()
        }


def optimize_layup_for_loading(loading_type, material_type='T800_Epoxy'):
    """
    Suggest optimal layup sequence based on loading type
    loading_type: 'axial', 'bending', 'torsion', 'combined'
    """
    recommendations = {
        'axial': [0, 0, 0, 0],  # Unidirectional for axial loading
        'bending': [0, 45, -45, 90, 90, -45, 45, 0],  # Symmetric for bending
        'torsion': [45, -45, -45, 45],  # ±45° for torsion
        'combined': [0, 45, 90, -45, -45, 90, 45, 0]  # Quasi-isotropic
    }
    
    if loading_type not in recommendations:
        loading_type = 'combined'
    
    return {
        'layup_sequence': recommendations[loading_type],
        'loading_type': loading_type,
        'material': material_type
    }
