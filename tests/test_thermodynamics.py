"""
Tester for termodynamikk modulen.
"""

import pytest
import numpy as np
from hxkit.thermodynamics import MoistAir, Psychrometrics


class TestMoistAir:
    """Test klasse for MoistAir."""
    
    def test_create_from_relative_humidity(self):
        """Test opprettelse av MoistAir fra relativ fuktighet."""
        air = MoistAir(temperature=20.0, relative_humidity=50.0)
        assert abs(air.temperature - 20.0) < 1e-6
        assert abs(air.relative_humidity - 50.0) < 1e-1
    
    def test_create_from_humidity_ratio(self):
        """Test opprettelse av MoistAir fra fuktighetsforhold."""
        air = MoistAir(temperature=20.0, humidity_ratio=0.01)
        assert abs(air.temperature - 20.0) < 1e-6
        assert abs(air.humidity_ratio - 0.01) < 1e-6
    
    def test_saturation_pressure(self):
        """Test metningstrykk beregning."""
        air = MoistAir(temperature=0.0, relative_humidity=100.0)
        p_sat = air._saturation_pressure(0.0)
        # Ved 0°C skal metningstrykk være ca 611 Pa
        assert abs(p_sat - 611) < 50
    
    def test_density_calculation(self):
        """Test tetthet beregning."""
        air = MoistAir(temperature=20.0, relative_humidity=50.0)
        density = air.density
        # Tetthet av luft ved 20°C skal være ca 1.2 kg/m³
        assert 1.1 < density < 1.3
    
    def test_enthalpy_calculation(self):
        """Test entalpi beregning."""
        air = MoistAir(temperature=20.0, relative_humidity=50.0)
        enthalpy = air.enthalpy
        # Entalpi skal være positiv og rimelig verdi
        assert enthalpy > 0
        assert enthalpy < 100  # kJ/kg


class TestPsychrometrics:
    """Test klasse for Psychrometrics."""
    
    def test_mixing_ratio(self):
        """Test blanding av to luftstrømmer."""
        air1 = MoistAir(temperature=25.0, relative_humidity=30.0)
        air2 = MoistAir(temperature=15.0, relative_humidity=80.0)
        
        mixed = Psychrometrics.mixing_ratio(air1, 1.0, air2, 1.0)
        
        # Blandingstemperatur skal være mellom de to
        assert 15.0 < mixed.temperature < 25.0
    
    def test_sensible_cooling(self):
        """Test sensibel kjøling."""
        inlet = MoistAir(temperature=25.0, relative_humidity=50.0)
        outlet = Psychrometrics.sensible_cooling(inlet, 20.0)
        
        assert abs(outlet.temperature - 20.0) < 1e-6
        assert abs(outlet.humidity_ratio - inlet.humidity_ratio) < 1e-6
