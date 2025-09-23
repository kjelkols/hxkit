"""
Tester for plategeometri modulen.
"""

import pytest
import numpy as np
from hxkit.geometries import PlateGeometry, HeatExchangerCore, GeometryFactory


class TestPlateGeometry:
    """Test klasse for PlateGeometry."""
    
    def test_basic_properties(self):
        """Test grunnleggende geometriske egenskaper."""
        geom = PlateGeometry(length=0.6, width=0.2, thickness=0.0005, channel_height=0.004)
        
        assert abs(geom.plate_area - 0.12) < 1e-6
        assert abs(geom.flow_area - 0.0008) < 1e-6
        assert abs(geom.hydraulic_diameter - 0.008) < 1e-6
    
    def test_friction_factor_correlation(self):
        """Test friksjonsfaktor korrelasjon."""
        geom = PlateGeometry(length=0.6, width=0.2, thickness=0.0005, channel_height=0.004)
        
        # Test forskjellige Reynolds tall
        f_low = geom.friction_factor_correlation(5.0)
        f_high = geom.friction_factor_correlation(5000.0)
        
        assert f_low > f_high  # Friksjonsfaktor skal avta med Reynolds tall


class TestHeatExchangerCore:
    """Test klasse for HeatExchangerCore."""
    
    def test_channel_consistency(self):
        """Test at kanalkonfigurasjon er konsistent."""
        geom = PlateGeometry(length=0.6, width=0.2, thickness=0.0005, channel_height=0.004)
        
        # Dette skal fungere
        core = HeatExchangerCore(n_plates=11, plate_geometry=geom, 
                               hot_channels=5, cold_channels=5)
        assert core.n_plates == 11
        
        # Dette skal gi feil
        with pytest.raises(ValueError):
            HeatExchangerCore(n_plates=11, plate_geometry=geom, 
                            hot_channels=3, cold_channels=3)  # 3+3 != 11-1
    
    def test_flow_areas(self):
        """Test strømningsarealer."""
        geom = PlateGeometry(length=0.6, width=0.2, thickness=0.0005, channel_height=0.004)
        core = HeatExchangerCore(n_plates=11, plate_geometry=geom, 
                               hot_channels=5, cold_channels=5)
        
        assert abs(core.hot_side_flow_area - 5 * geom.flow_area) < 1e-9
        assert abs(core.cold_side_flow_area - 5 * geom.flow_area) < 1e-9


class TestGeometryFactory:
    """Test klasse for GeometryFactory."""
    
    def test_standard_geometries(self):
        """Test standard geometrier."""
        small = GeometryFactory.standard_plate("small")
        medium = GeometryFactory.standard_plate("medium")
        large = GeometryFactory.standard_plate("large")
        
        # Størrelse skal øke
        assert small.plate_area < medium.plate_area < large.plate_area
    
    def test_invalid_size(self):
        """Test ugyldig størrelse."""
        with pytest.raises(ValueError):
            GeometryFactory.standard_plate("invalid")
    
    def test_custom_plate(self):
        """Test tilpasset plate."""
        dimensions = {
            "length": 1.0,
            "width": 0.3,
            "thickness": 0.0006,
            "channel_height": 0.005
        }
        geom = GeometryFactory.custom_plate(dimensions)
        assert abs(geom.length - 1.0) < 1e-6
        assert abs(geom.width - 0.3) < 1e-6
