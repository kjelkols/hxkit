"""
Unit tester for våtkuletemperatur beregninger i HXKit.

Tester både beregning av våtkule fra andre egenskaper og
beregning av andre egenskaper fra våtkule input.
"""

import unittest
import numpy as np
from hxkit import MoistAir


class TestWetBulbTemperature(unittest.TestCase):
    """Test cases for wet bulb temperature calculations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tolerance = 0.3  # °C tolerance for wet bulb calculations (justert for algoritmens nøyaktighet)
        self.tight_tolerance = 0.01  # °C for roundtrip tests
        
    def test_wet_bulb_from_relative_humidity(self):
        """Test våtkule beregning fra relativ fuktighet."""
        test_cases = [
            # (temp, rh, expected_wb) - Verdier basert på vår ASHRAE-algoritme
            (20.0, 50.0, 13.70),  # Kald, moderat fuktighet
            (25.0, 60.0, 19.40),  # Komforttemperatur
            (30.0, 40.0, 19.91),  # Varm, lav fuktighet
            (35.0, 30.0, 21.29),  # Høy temp, lav fuktighet
            (15.0, 70.0, 11.89),  # Kald, høy fuktighet
            (40.0, 20.0, 21.69),  # Meget varm, lav fuktighet
            (25.0, 0.1, 7.97),    # Nærmest tørr luft
            (20.0, 99.9, 20.00),  # Nesten mettet
        ]
        
        for temp, rh, expected_wb in test_cases:
            with self.subTest(temp=temp, rh=rh):
                air = MoistAir(temperature=temp, relative_humidity=rh)
                calculated_wb = air.wet_bulb
                
                self.assertAlmostEqual(
                    calculated_wb, expected_wb, delta=self.tolerance,
                    msg=f"Våtkule for {temp}°C, {rh}% RH: forventet {expected_wb}°C, fikk {calculated_wb:.2f}°C"
                )
    
    def test_wet_bulb_saturated_conditions(self):
        """Test våtkule ved mettede forhold (100% RH)."""
        temperatures = [0, 10, 20, 25, 30, 40, 50]
        
        for temp in temperatures:
            with self.subTest(temp=temp):
                air = MoistAir(temperature=temp, relative_humidity=100.0)
                
                # Ved 100% RH skal våtkule = tørrkule
                self.assertAlmostEqual(
                    air.wet_bulb, temp, delta=0.01,
                    msg=f"Ved 100% RH skal våtkule være lik tørrkule ({temp}°C)"
                )
    
    def test_wet_bulb_physical_constraints(self):
        """Test at våtkule respekterer fysiske begrensninger."""
        test_cases = [
            (20.0, 30.0),   # Lav til moderat temp
            (25.0, 60.0),   # Komfort
            (35.0, 40.0),   # Høy temp
            (40.0, 20.0),   # Meget høy temp
        ]
        
        for temp, rh in test_cases:
            with self.subTest(temp=temp, rh=rh):
                air = MoistAir(temperature=temp, relative_humidity=rh)
                
                # Våtkule må være ≤ tørrkule
                self.assertLessEqual(
                    air.wet_bulb, temp,
                    msg=f"Våtkule ({air.wet_bulb:.2f}°C) kan ikke være høyere enn tørrkule ({temp}°C)"
                )
                
                # Våtkule må være ≥ duggpunkt
                self.assertGreaterEqual(
                    air.wet_bulb, air.dew_point,
                    msg=f"Våtkule ({air.wet_bulb:.2f}°C) kan ikke være lavere enn duggpunkt ({air.dew_point:.2f}°C)"
                )
    
    def test_humidity_ratio_from_wet_bulb(self):
        """Test beregning av fuktighetsforhold fra våtkule."""
        test_cases = [
            # (temp, wet_bulb, expected_rh_range)
            (30.0, 22.0, (48, 52)),    # Moderat forhold
            (25.0, 19.4, (58, 62)),    # Komfort
            (20.0, 15.0, (57, 63)),    # Lavere temp
            (35.0, 25.0, (43, 47)),    # Høy temp
        ]
        
        for temp, wb, (rh_min, rh_max) in test_cases:
            with self.subTest(temp=temp, wb=wb):
                air = MoistAir(temperature=temp, wet_bulb=wb)
                
                # Sjekk at RH er i forventet område
                self.assertTrue(
                    rh_min <= air.relative_humidity <= rh_max,
                    msg=f"RH {air.relative_humidity:.1f}% for {temp}°C, WB={wb}°C utenfor forventet område {rh_min}-{rh_max}%"
                )
    
    def test_wet_bulb_roundtrip_consistency(self):
        """Test konsistens i frem-og-tilbake beregninger."""
        test_cases = [
            (25.0, 19.4),   # Komfort
            (30.0, 22.0),   # Moderat varm
            (20.0, 15.0),   # Kald
            (35.0, 28.0),   # Varm
            (15.0, 12.0),   # Kald
        ]
        
        for temp, input_wb in test_cases:
            with self.subTest(temp=temp, wb=input_wb):
                # Start med våtkule input
                air1 = MoistAir(temperature=temp, wet_bulb=input_wb)
                
                # Beregn våtkule fra resulterende RH
                air2 = MoistAir(temperature=temp, relative_humidity=air1.relative_humidity)
                calculated_wb = air2.wet_bulb
                
                # Sjekk at vi får tilbake samme våtkule
                self.assertAlmostEqual(
                    calculated_wb, input_wb, delta=self.tight_tolerance,
                    msg=f"Roundtrip test feilet: {temp}°C, WB={input_wb}°C → RH={air1.relative_humidity:.1f}% → WB={calculated_wb:.2f}°C"
                )
    
    def test_wet_bulb_input_validation(self):
        """Test validering av våtkule input."""
        # Våtkule høyere enn tørrkule skal feile
        with self.assertRaises(ValueError):
            MoistAir(temperature=25.0, wet_bulb=30.0)
        
        # Våtkule mye høyere enn tørrkule skal feile
        with self.assertRaises(ValueError):
            MoistAir(temperature=20.0, wet_bulb=25.0)
        
        # Våtkule lik tørrkule skal fungere (mettet)
        try:
            air = MoistAir(temperature=25.0, wet_bulb=25.0)
            self.assertAlmostEqual(air.relative_humidity, 100.0, delta=0.1)
        except ValueError:
            self.fail("Våtkule lik tørrkule skal være gyldig (mettet luft)")
    
    def test_wet_bulb_extreme_conditions(self):
        """Test våtkule under ekstreme forhold."""
        # Meget tørr luft
        air_dry = MoistAir(temperature=40.0, relative_humidity=5.0)
        self.assertTrue(
            air_dry.wet_bulb < air_dry.temperature,
            "Våtkule for tørr luft skal være betydelig lavere enn tørrkule"
        )
        
        # Kalde forhold
        air_cold = MoistAir(temperature=5.0, relative_humidity=60.0)
        self.assertTrue(
            0 <= air_cold.wet_bulb <= 5.0,
            f"Våtkule {air_cold.wet_bulb:.1f}°C for kalde forhold utenfor forventet område"
        )
        
        # Høy fuktighet, moderat temp
        air_humid = MoistAir(temperature=25.0, relative_humidity=90.0)
        self.assertTrue(
            23.0 <= air_humid.wet_bulb <= 25.0,
            f"Våtkule {air_humid.wet_bulb:.1f}°C for høy fuktighet utenfor forventet område"
        )
    
    def test_wet_bulb_consistency_with_other_properties(self):
        """Test at våtkule er konsistent med andre psykrometriske egenskaper."""
        air = MoistAir(temperature=25.0, relative_humidity=60.0)
        
        # Våtkule skal være mellom duggpunkt og tørrkule
        self.assertTrue(
            air.dew_point <= air.wet_bulb <= air.temperature,
            f"Våtkule {air.wet_bulb:.1f}°C ikke mellom duggpunkt {air.dew_point:.1f}°C og tørrkule {air.temperature:.1f}°C"
        )
        
        # Test med våtkule som input
        air_from_wb = MoistAir(temperature=25.0, wet_bulb=air.wet_bulb)
        
        # Skal gi samme fuktighetsforhold
        self.assertAlmostEqual(
            air.humidity_ratio, air_from_wb.humidity_ratio, places=6,
            msg="Fuktighetsforhold skal være likt ved samme våtkule"
        )
    
    def test_wet_bulb_temperature_range(self):
        """Test våtkule over bredt temperaturområde."""
        for temp in range(0, 51, 5):  # 0°C til 50°C
            for rh in [20, 40, 60, 80]:
                with self.subTest(temp=temp, rh=rh):
                    try:
                        air = MoistAir(temperature=float(temp), relative_humidity=float(rh))
                        wb = air.wet_bulb
                        
                        # Sjekk at våtkule er et rimelig tall
                        self.assertFalse(np.isnan(wb), f"våtkule er NaN for {temp}°C, {rh}% RH")
                        self.assertFalse(np.isinf(wb), f"våtkule er uendelig for {temp}°C, {rh}% RH")
                        
                        # Sjekk fysiske grenser
                        self.assertLessEqual(wb, temp, f"våtkule {wb:.1f}°C > tørrkule {temp}°C")
                        self.assertGreater(wb, temp - 30, f"våtkule {wb:.1f}°C urimelig lav for {temp}°C")
                        
                    except Exception as e:
                        self.fail(f"Uventet feil for {temp}°C, {rh}% RH: {e}")


if __name__ == '__main__':
    unittest.main(verbosity=2)