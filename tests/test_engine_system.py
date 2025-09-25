"""
Tester for det forenklede engine-systemet.
"""

import pytest
import warnings
from hxkit import MoistAir


class TestEngineSupport:
    """Tester for engine-støtte i forenklede struktur."""
    
    def test_default_ashrae_engine(self):
        """Tester standard ASHRAE-oppførsel (ingen engine spesifisert)."""
        air = MoistAir(temperature=25.0, relative_humidity=50.0)
        
        # Standardoppførsel skal fungere som før
        assert abs(air.relative_humidity - 50.0) < 0.1
        assert abs(air.temperature - 25.0) < 0.1
        assert air.humidity_ratio > 0
        assert air.dew_point < air.temperature
        assert air.wet_bulb < air.temperature
    
    def test_explicit_ashrae_engine(self):
        """Tester eksplisitt ASHRAE engine."""
        air = MoistAir(temperature=25.0, relative_humidity=60.0, engine="ASHRAE")
        
        # Skal fungere likt som standard
        assert abs(air.relative_humidity - 60.0) < 0.1
        assert air.humidity_ratio > 0
        
    def test_coolprop_engine_without_library(self):
        """Tester CoolProp engine når biblioteket ikke er tilgjengelig."""
        
        # Skal gi advarsel og falle tilbake til ASHRAE
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            air = MoistAir(temperature=25.0, relative_humidity=50.0, engine="CoolProp")
            
            # Skal ha gitt advarsel om manglende CoolProp
            assert len(w) == 1
            assert "CoolProp ikke tilgjengelig" in str(w[0].message)
            
        # Men beregningen skal fortsatt fungere (fallback til ASHRAE)
        assert abs(air.relative_humidity - 50.0) < 0.1
        assert air.humidity_ratio > 0
    
    def test_unknown_engine(self):
        """Tester ukjent engine-navn."""
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            air = MoistAir(temperature=25.0, relative_humidity=50.0, engine="UnknownEngine")
            
            # Skal ha gitt advarsel om ukjent engine
            assert len(w) == 1
            assert "Ukjent engine" in str(w[0].message)
            
        # Men beregningen skal fortsatt fungere (fallback til ASHRAE)
        assert abs(air.relative_humidity - 50.0) < 0.1
        
    def test_engine_consistency(self):
        """Tester at forskjellige engine-spesifikasjoner gir konsistente resultater."""
        # Alle disse skal gi samme resultat (siden CoolProp ikke er installert)
        air1 = MoistAir(temperature=25.0, relative_humidity=50.0)  # Standard
        air2 = MoistAir(temperature=25.0, relative_humidity=50.0, engine="ASHRAE")
        air3 = MoistAir(temperature=25.0, relative_humidity=50.0, engine="CoolProp")  # Fallback
        
        # Skal være identiske (innenfor numerisk presisjon)
        assert abs(air1.humidity_ratio - air2.humidity_ratio) < 1e-6
        assert abs(air1.humidity_ratio - air3.humidity_ratio) < 1e-6
        assert abs(air1.dew_point - air2.dew_point) < 0.01
        assert abs(air1.dew_point - air3.dew_point) < 0.01
        
    def test_engine_with_different_inputs(self):
        """Tester engine-støtte med forskjellige input-typer."""
        
        # Test med humidity_ratio
        air1 = MoistAir(temperature=25.0, humidity_ratio=0.01, engine="ASHRAE")
        assert abs(air1.humidity_ratio - 0.01) < 1e-6
        
        # Test med dew_point
        air2 = MoistAir(temperature=25.0, dew_point=15.0, engine="ASHRAE")
        assert abs(air2.dew_point - 15.0) < 0.1
        
        # Test med wet_bulb
        air3 = MoistAir(temperature=25.0, wet_bulb=20.0, engine="ASHRAE")
        assert abs(air3.wet_bulb - 20.0) < 0.1
        
    def test_engine_parameter_types(self):
        """Tester at engine-parameteret håndterer forskjellige typer riktig."""
        
        # String
        air1 = MoistAir(temperature=25.0, relative_humidity=50.0, engine="ashrae")
        assert air1.relative_humidity > 0
        
        # None (standard)
        air2 = MoistAir(temperature=25.0, relative_humidity=50.0, engine=None)
        assert air2.relative_humidity > 0
        
        # Case-insensitive
        air3 = MoistAir(temperature=25.0, relative_humidity=50.0, engine="COOLPROP")
        assert air3.relative_humidity > 0  # Fallback til ASHRAE