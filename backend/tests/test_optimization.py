"""Tests for optimization algorithms."""

import numpy as np
import pytest

from app.optimization.simp import SIMPConfig, SIMPOptimizer, create_cantilever_problem
from app.optimization.level_set import LevelSetConfig, LevelSetOptimizer
from app.optimization.laminate import (
    LaminateAnalyzer,
    Ply,
    create_quasi_isotropic_layup,
)


class TestSIMPOptimizer:
    """Tests for SIMP topology optimization."""

    def test_config_creation(self):
        """Test SIMP config creation."""
        config = SIMPConfig(
            nelx=30,
            nely=15,
            volume_fraction=0.4,
            penalty=3.0,
        )
        assert config.nelx == 30
        assert config.nely == 15
        assert config.volume_fraction == 0.4

    def test_optimizer_initialization(self):
        """Test optimizer initialization."""
        config = SIMPConfig(nelx=20, nely=10)
        optimizer = SIMPOptimizer(config)
        
        assert optimizer.nelx == 20
        assert optimizer.nely == 10
        assert len(optimizer.x) == 20 * 10

    def test_cantilever_problem(self):
        """Test cantilever problem creation."""
        optimizer, force, fixed_dofs = create_cantilever_problem(
            nelx=30, nely=15, volume_fraction=0.4
        )
        
        assert optimizer.nelx == 30
        assert optimizer.nely == 15
        assert len(force) == 2 * (30 + 1) * (15 + 1)
        assert len(fixed_dofs) == 2 * (15 + 1)

    def test_short_optimization(self):
        """Test a short optimization run."""
        config = SIMPConfig(
            nelx=20,
            nely=10,
            volume_fraction=0.4,
            max_iterations=5,  # Very short for testing
        )
        optimizer = SIMPOptimizer(config)
        
        # Create simple cantilever problem
        ndof = 2 * (20 + 1) * (10 + 1)
        force = np.zeros(ndof)
        force[2 * (20 + 1) * (10 + 1) - 10 - 1] = -1.0
        fixed_dofs = np.array(
            [2 * i for i in range(11)] + [2 * i + 1 for i in range(11)]
        )
        
        result = optimizer.optimize(force, fixed_dofs)
        
        assert result.iterations <= 5
        assert result.volume_fraction <= 0.5
        assert len(result.convergence_history) > 0


class TestLevelSetOptimizer:
    """Tests for level-set topology optimization."""

    def test_config_creation(self):
        """Test level-set config creation."""
        config = LevelSetConfig(
            nelx=30,
            nely=15,
            volume_fraction=0.4,
        )
        assert config.nelx == 30
        assert config.nely == 15

    def test_optimizer_initialization(self):
        """Test optimizer initialization."""
        config = LevelSetConfig(nelx=20, nely=10)
        optimizer = LevelSetOptimizer(config)
        
        assert optimizer.nelx == 20
        assert optimizer.nely == 10
        assert optimizer.phi.shape == (21, 11)  # Nodes, not elements


class TestLaminateAnalysis:
    """Tests for laminate analysis."""

    def test_ply_creation(self):
        """Test ply definition creation."""
        ply = Ply(
            material_name="T700",
            angle=45.0,
            thickness=0.125,
            e1=165.0,
            e2=10.5,
            g12=5.5,
            nu12=0.28,
        )
        assert ply.angle == 45.0
        assert ply.thickness == 0.125

    def test_quasi_isotropic_layup(self):
        """Test quasi-isotropic layup creation."""
        plies = create_quasi_isotropic_layup(
            material_name="T700",
            ply_thickness=0.125,
            n_sets=2,
        )
        
        assert len(plies) == 16  # [0/45/-45/90]2s = 8 * 2 = 16
        
        # Check symmetry
        n = len(plies)
        for i in range(n // 2):
            assert plies[i].angle == plies[n - 1 - i].angle

    def test_laminate_analyzer(self):
        """Test laminate analysis."""
        plies = create_quasi_isotropic_layup(
            material_name="T700",
            ply_thickness=0.125,
            n_sets=1,
        )
        
        analyzer = LaminateAnalyzer(plies)
        result = analyzer.compute_effective_properties()
        
        assert result.total_thickness > 0
        assert result.Ex > 0
        assert result.Ey > 0

    def test_abd_matrix(self):
        """Test ABD matrix computation."""
        plies = [
            Ply("T700", 0, 0.125, 165.0, 10.5, 5.5, 0.28),
            Ply("T700", 90, 0.125, 165.0, 10.5, 5.5, 0.28),
            Ply("T700", 90, 0.125, 165.0, 10.5, 5.5, 0.28),
            Ply("T700", 0, 0.125, 165.0, 10.5, 5.5, 0.28),
        ]
        
        analyzer = LaminateAnalyzer(plies)
        ABD = analyzer.compute_abd_matrix()
        
        assert ABD.shape == (6, 6)
        assert np.allclose(ABD, ABD.T)  # Should be symmetric

    def test_ply_rules_check(self):
        """Test ply rules validation."""
        plies = create_quasi_isotropic_layup(
            material_name="T700",
            ply_thickness=0.125,
            n_sets=2,
        )
        
        analyzer = LaminateAnalyzer(plies)
        checks = analyzer.check_ply_rules()
        
        assert len(checks) >= 3
        # Quasi-isotropic should pass symmetry and balance
        for name, passed, message in checks:
            if name in ["Symmetry", "Balance"]:
                assert passed, f"{name} check failed: {message}"


class TestStressAnalysis:
    """Tests for laminate stress analysis."""

    def test_stress_analysis(self):
        """Test stress analysis under load."""
        plies = create_quasi_isotropic_layup(
            material_name="T700",
            ply_thickness=0.125,
            n_sets=1,
        )
        
        analyzer = LaminateAnalyzer(plies)
        result = analyzer.analyze_stress(Nx=100.0)  # 100 N/mm in x
        
        assert result.ply_stresses is not None
        assert len(result.ply_stresses) == len(plies)
        assert result.failure_indices is not None
        assert all(fi >= 0 for fi in result.failure_indices)
