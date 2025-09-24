"""
Termodynamiske beregninger for fuktig luft og andre fluider.

Dette modulet inneholder klasser og funksjoner for:
- Psykrometriske beregninger for fuktig luft
- Termodynamiske egenskaper
- Tilstandsligninger
"""

import numpy as np
from functools import cached_property
from typing import Union, Tuple, Optional


class MoistAir:
    """
    Klasse for beregning av termodynamiske egenskaper for fuktig luft.
    
    Basert på ASHRAE fundamentals og psykrometriske sammenhenger.
    """
    
    def __init__(self, temperature: float, humidity_ratio: Optional[float] = None,
                 relative_humidity: Optional[float] = None, wet_bulb: Optional[float] = None,
                 dew_point: Optional[float] = None, pressure: float = 101325):
        """
        Initialiserer fuktig luft tilstand.
        
        Args:
            temperature: Tørrbulbtemperatur [°C]
            humidity_ratio: Fuktighetsforhold [kg_vanndamp/kg_tørr_luft]
            relative_humidity: Relativ fuktighet [%] (0-100)
            wet_bulb: Våtbulbtemperatur [°C]
            dew_point: Duggpunkt [°C]
            pressure: Trykk [Pa]
            
        Note:
            Kun en av humidity_ratio, relative_humidity, wet_bulb eller dew_point 
            må oppgis.
        """
        self.temperature = temperature
        self.pressure = pressure
        
        # Tell antall oppgitte fuktighetsparametere
        humidity_params = [humidity_ratio, relative_humidity, wet_bulb, dew_point]
        provided_count = sum(1 for param in humidity_params if param is not None)
        
        if provided_count != 1:
            raise ValueError("Nøyaktig en av følgende må oppgis: humidity_ratio, relative_humidity, wet_bulb, dew_point")
        
        if humidity_ratio is not None:
            self.humidity_ratio = humidity_ratio
        elif relative_humidity is not None:
            self.humidity_ratio = self._calc_humidity_ratio_from_rh(relative_humidity)
        elif wet_bulb is not None:
            self.humidity_ratio = self._calc_humidity_ratio_from_wet_bulb(wet_bulb)
        elif dew_point is not None:
            self.humidity_ratio = self._calc_humidity_ratio_from_dew_point(dew_point)
        else:
            raise ValueError("En fuktighetsparameter må oppgis")
    
    def _calc_humidity_ratio_from_rh(self, rh: float) -> float:
        """Beregner fuktighetsforhold fra relativ fuktighet."""
        p_sat = self._saturation_pressure(self.temperature)
        p_vapor = rh / 100 * p_sat
        return 0.622 * p_vapor / (self.pressure - p_vapor)
    
    def _saturation_pressure(self, temp: float) -> float:
        """Beregner metningstrykk for vanndamp [Pa]."""
        # Magnus formel for metningstrykk (mer nøyaktig for psykrometriske beregninger)
        if temp >= 0:
            # For væske (over 0°C)
            return 610.78 * np.exp(17.27 * temp / (temp + 237.3))
        else:
            # For is (under 0°C) 
            return 610.78 * np.exp(21.875 * temp / (temp + 265.5))
    
    def _calc_humidity_ratio_from_wet_bulb(self, wet_bulb_temp: float) -> float:
        """Beregner fuktighetsforhold fra våtbulbtemperatur [iterativ løsning]."""
        # Iterativ løsning for å finne fuktighetsforhold fra våtbulb
        w = 0.01  # Start gjetting
        for _ in range(20):
            # Beregn entalpi ved våtbulb-tilstand (mettet)
            w_sat_wb = self._calc_humidity_ratio_from_rh_at_temp(100.0, wet_bulb_temp)
            h_wb = 1.006 * wet_bulb_temp + w_sat_wb * (2501 + 1.86 * wet_bulb_temp)
            
            # Beregn entalpi ved tørrbulb-tilstand med gjetting
            h_db = 1.006 * self.temperature + w * (2501 + 1.86 * self.temperature)
            
            # Våtbulb-sammenhengen: h_db = h_wb + (w_sat_wb - w) * 4.186 * (T_db - T_wb)
            w_new = w_sat_wb + (h_db - h_wb) / (2501 + 1.86 * wet_bulb_temp - 4.186 * (self.temperature - wet_bulb_temp))
            
            if abs(w_new - w) < 1e-6:
                break
            w = w_new
        return w
    
    def _calc_humidity_ratio_from_dew_point(self, dew_point_temp: float) -> float:
        """Beregner fuktighetsforhold fra duggpunkt."""
        # Ved duggpunkt er luften mettet ved duggpunkt-temperaturen
        p_sat_dp = self._saturation_pressure(dew_point_temp)
        return 0.622 * p_sat_dp / (self.pressure - p_sat_dp)
    
    def _calc_humidity_ratio_from_rh_at_temp(self, rh: float, temp: float) -> float:
        """Hjelpemetode: Beregner fuktighetsforhold fra RH ved gitt temperatur."""
        p_sat = self._saturation_pressure(temp)
        p_vapor = rh / 100 * p_sat
        return 0.622 * p_vapor / (self.pressure - p_vapor)
    
    @cached_property
    def relative_humidity(self) -> float:
        """Relativ fuktighet [%]."""
        p_sat = self._saturation_pressure(self.temperature)
        p_vapor = self.humidity_ratio * self.pressure / (0.622 + self.humidity_ratio)
        return 100 * p_vapor / p_sat
    
    @cached_property
    def density(self) -> float:
        """Tetthet av fuktig luft [kg/m³]."""
        return self.pressure / (287.055 * (self.temperature + 273.15) * (1 + 1.608 * self.humidity_ratio))
    
    @cached_property
    def specific_volume(self) -> float:
        """Spesifikt volum av fuktig luft [m³/kg]."""
        return 1.0 / self.density
    
    @cached_property
    def enthalpy(self) -> float:
        """Entalpi [kJ/kg_tørr_luft]."""
        return 1.006 * self.temperature + self.humidity_ratio * (2501 + 1.86 * self.temperature)
    
    @cached_property
    def wet_bulb(self) -> float:
        """Våtbulbtemperatur [°C]."""
        # Iterativ løsning for våtbulbtemperatur
        t_wb = self.temperature
        for _ in range(10):
            w_sat = self._calc_humidity_ratio_from_rh_at_temp(100.0, t_wb)  # Ved våtbulbtemperatur
            t_wb_new = (2501 * self.humidity_ratio + 1.006 * self.temperature - w_sat * 2501) / (1.006 + 1.86 * w_sat)
            if abs(t_wb_new - t_wb) < 0.01:
                break
            t_wb = t_wb_new
        return t_wb
    
    @cached_property
    def dew_point(self) -> float:
        """Duggpunkt temperatur [°C]."""
        # Beregner duggpunkt ved å finne temperaturen hvor relativ fuktighet = 100%
        # ved konstant fuktighetsforhold
        
        # Partielltrykk av vanndamp
        p_vapor = self.humidity_ratio * self.pressure / (0.622 + self.humidity_ratio)
        
        # Inverse Magnus formel for å finne temperatur ved gitt damptrykk
        if p_vapor <= 611.21:  # Under trippelpunkt
            # Magnus formel for is (under 0°C)
            # p_sat = 610.78 * exp(21.875 * T / (T + 265.5))
            # Løs for T: T = 265.5 * ln(p/610.78) / (21.875 - ln(p/610.78))
            ln_ratio = np.log(p_vapor / 610.78)
            t_dp = 265.5 * ln_ratio / (21.875 - ln_ratio)
        else:
            # Magnus formel for væske (over 0°C)  
            # p_sat = 610.78 * exp(17.27 * T / (T + 237.3))
            # Løs for T: T = 237.3 * ln(p/610.78) / (17.27 - ln(p/610.78))
            ln_ratio = np.log(p_vapor / 610.78)
            t_dp = 237.3 * ln_ratio / (17.27 - ln_ratio)
        
        return t_dp


class Psychrometrics:
    """
    Samling av psykrometriske beregningsfunksjoner.
    """
    
    @staticmethod
    def mixing_ratio(state1: MoistAir, mass_flow1: float, 
                    state2: MoistAir, mass_flow2: float) -> MoistAir:
        """
        Beregner blandingstilstand for to luftstrømmer.
        
        Args:
            state1: Første lufttilstand
            mass_flow1: Massestrøm første luft [kg/s]
            state2: Andre lufttilstand  
            mass_flow2: Massestrøm andre luft [kg/s]
            
        Returns:
            Blandingstilstand som MoistAir objekt
        """
        total_flow = mass_flow1 + mass_flow2
        
        # Konserver entalpi og fuktighetsforhold
        mixed_enthalpy = (state1.enthalpy * mass_flow1 + state2.enthalpy * mass_flow2) / total_flow
        mixed_humidity = (state1.humidity_ratio * mass_flow1 + state2.humidity_ratio * mass_flow2) / total_flow
        
        # Løs for temperatur ved gitt entalpi og fuktighetsforhold
        mixed_temp = (mixed_enthalpy - mixed_humidity * 2501) / (1.006 + 1.86 * mixed_humidity)
        
        return MoistAir(temperature=mixed_temp, humidity_ratio=mixed_humidity)
    
    @staticmethod
    def sensible_cooling(inlet: MoistAir, outlet_temp: float) -> MoistAir:
        """
        Beregner utløpstilstand ved sensibel kjøling (konstant fuktighetsforhold).
        
        Args:
            inlet: Innløpstilstand
            outlet_temp: Ønsket utløpstemperatur [°C]
            
        Returns:
            Utløpstilstand som MoistAir objekt
        """
        return MoistAir(temperature=outlet_temp, humidity_ratio=inlet.humidity_ratio, 
                       pressure=inlet.pressure)
