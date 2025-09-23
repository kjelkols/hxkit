"""
Termodynamiske beregninger for fuktig luft og andre fluider.

Dette modulet inneholder klasser og funksjoner for:
- Psykrometriske beregninger for fuktig luft
- Termodynamiske egenskaper
- Tilstandsligninger
"""

import numpy as np
from typing import Union, Tuple, Optional


class MoistAir:
    """
    Klasse for beregning av termodynamiske egenskaper for fuktig luft.
    
    Basert på ASHRAE fundamentals og psykrometriske sammenhenger.
    """
    
    def __init__(self, temperature: float, humidity_ratio: Optional[float] = None,
                 relative_humidity: Optional[float] = None, pressure: float = 101325):
        """
        Initialiserer fuktig luft tilstand.
        
        Args:
            temperature: Tørrbulbtemperatur [°C]
            humidity_ratio: Fuktighetsforhold [kg_vanndamp/kg_tørr_luft]
            relative_humidity: Relativ fuktighet [%] (0-100)
            pressure: Trykk [Pa]
        """
        self.temperature = temperature
        self.pressure = pressure
        
        if humidity_ratio is not None:
            self.humidity_ratio = humidity_ratio
        elif relative_humidity is not None:
            self.humidity_ratio = self._calc_humidity_ratio_from_rh(relative_humidity)
        else:
            raise ValueError("Enten humidity_ratio eller relative_humidity må oppgis")
    
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
    
    @property
    def relative_humidity(self) -> float:
        """Relativ fuktighet [%]."""
        p_sat = self._saturation_pressure(self.temperature)
        p_vapor = self.humidity_ratio * self.pressure / (0.622 + self.humidity_ratio)
        return 100 * p_vapor / p_sat
    
    @property
    def density(self) -> float:
        """Tetthet av fuktig luft [kg/m³]."""
        return self.pressure / (287.055 * (self.temperature + 273.15) * (1 + 1.608 * self.humidity_ratio))
    
    @property
    def enthalpy(self) -> float:
        """Entalpi [kJ/kg_tørr_luft]."""
        return 1.006 * self.temperature + self.humidity_ratio * (2501 + 1.86 * self.temperature)
    
    @property
    def wet_bulb_temperature(self) -> float:
        """Våtbulbtemperatur [°C]."""
        # Iterativ løsning for våtbulbtemperatur
        t_wb = self.temperature
        for _ in range(10):
            w_sat = self._calc_humidity_ratio_from_rh(100)  # Ved våtbulbtemperatur
            t_wb_new = (2501 * self.humidity_ratio + 1.006 * self.temperature - w_sat * 2501) / (1.006 + 1.86 * w_sat)
            if abs(t_wb_new - t_wb) < 0.01:
                break
            t_wb = t_wb_new
        return t_wb


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
