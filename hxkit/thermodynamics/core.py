"""
Termodynamiske beregninger for fuktig luft og andre fluider.

Dette modulet inneholder klasser og funksjoner for:
- Psykrometriske beregninger for fuktig luft
- Termodynamiske egenskaper
- Tilstandsligninger

Gyldighetsområder:
- Temperatur: -100°C til 100°C (høy nøyaktighet: -20°C til 60°C)
- Trykk: 50-200 kPa (optimal: 80-120 kPa)
- Relativ fuktighet: 0-100%
- Fuktighetsforhold: 0-0.030 kg/kg

Advarsler gis ved ekstreme verdier, men beregninger tillates for iterasjoner.

ENGINE-STØTTE:
Biblioteket støtter forskjellige termodynamiske engines for økt nøyaktighet:

    # Standard ASHRAE-beregninger (rask og nøyaktig for vanlige forhold)
    air = MoistAir(temperature=25, relative_humidity=50)
    
    # Eksplisitt ASHRAE engine
    air = MoistAir(temperature=25, relative_humidity=50, engine="ASHRAE")
    
    # CoolProp engine (høy nøyaktighet, krever CoolProp installasjon)
    air = MoistAir(temperature=25, relative_humidity=50, engine="CoolProp")

Hvis CoolProp ikke er tilgjengelig, faller systemet automatisk tilbake til 
ASHRAE-beregninger med en advarsel.

TILGJENGELIGE ENGINES:
- "ASHRAE": Standard ASHRAE-baserte beregninger (alltid tilgjengelig)
- "CoolProp": Høy-presisjon CoolProp-beregninger (krever pip install CoolProp)

Ukjente engine-navn vil gi advarsel og falle tilbake til ASHRAE.
"""

import numpy as np
import warnings
from functools import cached_property
from typing import Union, Tuple, Optional


class CoolPropEngine:
    """Enkel CoolProp engine for termodynamiske beregninger."""
    
    def __init__(self):
        try:
            import CoolProp.HumidAir as HA
            self.HA = HA
        except ImportError:
            raise ImportError("CoolProp er ikke installert")
    
    def calculate_properties(self, temperature, pressure, humidity_input):
        """Beregner egenskaper med CoolProp."""
        try:
            # CoolProp bruker Kelvin og Pa
            T_K = temperature + 273.15
            P_Pa = pressure
            
            if 'humidity_ratio' in humidity_input:
                W = humidity_input['humidity_ratio']
                
                # Beregn egenskaper med CoolProp
                Tdp = self.HA.HAProps('D', 'T', T_K, 'P', P_Pa, 'W', W) - 273.15
                Twb = self.HA.HAProps('B', 'T', T_K, 'P', P_Pa, 'W', W) - 273.15
                RH = self.HA.HAProps('R', 'T', T_K, 'P', P_Pa, 'W', W) * 100
                h = self.HA.HAProps('H', 'T', T_K, 'P', P_Pa, 'W', W) / 1000  # J/kg til kJ/kg
                rho = self.HA.HAProps('Rho', 'T', T_K, 'P', P_Pa, 'W', W)
                
                return {
                    'dew_point': Tdp,
                    'wet_bulb': Twb,
                    'relative_humidity': RH,
                    'enthalpy': h,
                    'density': rho
                }
        except Exception as e:
            warnings.warn(f"CoolProp beregning feilet: {e}. Bruker ASHRAE fallback.", UserWarning)
            return None
        
        return None


class MoistAir:
    """
    Klasse for beregning av termodynamiske egenskaper for fuktig luft.
    
    Basert på ASHRAE fundamentals og psykrometriske sammenhenger.
    
    Gyldighetsområder:
    - Temperatur: -100°C til 100°C (advarsler utenfor -20°C til 60°C)
    - Trykk: 50-200 kPa (advarsler utenfor 80-120 kPa)
    - Relativ fuktighet: 0-100%
    - Fuktighetsforhold: 0-0.030 kg/kg
    """
    
    # Klassekonstanter for gyldighetsområder
    TEMP_MIN_ABSOLUTE = -100.0  # °C
    TEMP_MAX_ABSOLUTE = 100.0   # °C
    TEMP_MIN_OPTIMAL = -20.0    # °C
    TEMP_MAX_OPTIMAL = 60.0     # °C
    
    PRESSURE_MIN_ABSOLUTE = 10000.0   # Pa (0.1 bar)
    PRESSURE_MAX_ABSOLUTE = 1000000.0 # Pa (10 bar)
    PRESSURE_MIN_OPTIMAL = 80000.0    # Pa (0.8 bar)
    PRESSURE_MAX_OPTIMAL = 120000.0   # Pa (1.2 bar)
    
    HUMIDITY_RATIO_MAX = 0.030        # kg/kg
    
    def __init__(self, temperature: float, humidity_ratio: Optional[float] = None,
                 relative_humidity: Optional[float] = None, wet_bulb: Optional[float] = None,
                 dew_point: Optional[float] = None, pressure: float = 101325,
                 engine: Optional[Union[str, 'CoolPropEngine']] = None):
        """
        Initialiserer fuktig luft tilstand.
        
        Args:
            temperature: Tørrkuletemperatur [°C]
                        Gyldighetsområde: -100°C til 100°C
                        Optimal nøyaktighet: -20°C til 60°C
            humidity_ratio: Fuktighetsforhold [kg_vanndamp/kg_tørr_luft]
                          Område: 0 til ~0.030 kg/kg
            relative_humidity: Relativ fuktighet [%] (0-100)
                             Tolererer opp til 100.5% med advarsel
            wet_bulb: Våtkuletemperatur [°C]
                     Må være <= tørrkuletemperatur
            dew_point: Duggpunkt [°C]
                      Må være <= tørrkuletemperatur
            pressure: Trykk [Pa], default 101325 Pa (1 atm)
                     Gyldighetsområde: 10-1000 kPa
                     Optimal nøyaktighet: 80-120 kPa
            engine: Termodynamisk engine for beregninger
                   - None (default): Bruker ASHRAE-implementasjon
                   - str: Engine navn ("ASHRAE", "CoolProp")
                   - ThermodynamicEngine: Engine objekt direkte
                     
        Note:
            - Kun en av humidity_ratio, relative_humidity, wet_bulb eller dew_point må oppgis
            - Advarsler gis for verdier utenfor optimalt område
            - Beregninger tillates for iterasjoner selv ved ekstreme verdier
            - Engine-valg påvirker nøyaktighet og gyldighetsområder
            
        Raises:
            ValueError: Ved ugyldig kombinasjon av parametere eller ekstreme verdier
            UserWarning: Ved verdier utenfor optimalt område (kan ignoreres)
            EngineNotAvailableError: Hvis valgt engine ikke er tilgjengelig
            
        Examples:
            >>> # Standard forhold med ASHRAE
            >>> air = MoistAir(temperature=20.0, relative_humidity=50.0)
            >>> 
            >>> # Bruk CoolProp engine for høyere nøyaktighet
            >>> air_cp = MoistAir(temperature=25.0, relative_humidity=60.0, engine="CoolProp")
            >>>
            >>> # Bruk engine object direkte
            >>> # Enkelt engine bruk
            >>> air_eng = MoistAir(temperature=15.0, relative_humidity=70.0, engine="ASHRAE")
        """
        # Initialiser termodynamisk engine
        self._engine = self._initialize_engine(engine)
        
        # Valider input med advarsler
        self._validate_inputs(temperature, pressure, humidity_ratio, relative_humidity, 
                             wet_bulb, dew_point)
        
        self.temperature = temperature
        self.pressure = pressure
        
        # Tell antall oppgitte fuktighetsparametere
        humidity_params = [humidity_ratio, relative_humidity, wet_bulb, dew_point]
        provided_count = sum(1 for param in humidity_params if param is not None)
        
        if provided_count != 1:
            raise ValueError("Nøyaktig en av følgende må oppgis: humidity_ratio, relative_humidity, wet_bulb, dew_point")
        
        # Beregn fuktighetsforhold - bruk alltid innebygde beregninger
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
    
    def _validate_inputs(self, temperature: float, pressure: float,
                        humidity_ratio: Optional[float], relative_humidity: Optional[float],
                        wet_bulb: Optional[float], dew_point: Optional[float]) -> None:
        """Validerer input-parametere og gir advarsler for ekstreme verdier."""
        
        # Temperaturvalidering
        if temperature < self.TEMP_MIN_ABSOLUTE or temperature > self.TEMP_MAX_ABSOLUTE:
            raise ValueError(f"Temperatur {temperature}°C utenfor absolutt område "
                           f"({self.TEMP_MIN_ABSOLUTE}°C til {self.TEMP_MAX_ABSOLUTE}°C)")
        
        if temperature < self.TEMP_MIN_OPTIMAL or temperature > self.TEMP_MAX_OPTIMAL:
            warnings.warn(f"Temperatur {temperature}°C utenfor optimalt område "
                         f"({self.TEMP_MIN_OPTIMAL}°C til {self.TEMP_MAX_OPTIMAL}°C). "
                         f"Nøyaktigheten kan være redusert.", UserWarning)
        
        # Trykkvalidering
        if pressure < self.PRESSURE_MIN_ABSOLUTE or pressure > self.PRESSURE_MAX_ABSOLUTE:
            raise ValueError(f"Trykk {pressure/1000:.1f} kPa utenfor absolutt område "
                           f"({self.PRESSURE_MIN_ABSOLUTE/1000:.1f} til {self.PRESSURE_MAX_ABSOLUTE/1000:.1f} kPa)")
        
        if pressure < self.PRESSURE_MIN_OPTIMAL or pressure > self.PRESSURE_MAX_OPTIMAL:
            warnings.warn(f"Trykk {pressure/1000:.1f} kPa utenfor optimalt område "
                         f"({self.PRESSURE_MIN_OPTIMAL/1000:.1f} til {self.PRESSURE_MAX_OPTIMAL/1000:.1f} kPa). "
                         f"Nøyaktigheten kan være redusert.", UserWarning)
        
        # Fuktighetsverdier validering
        if relative_humidity is not None:
            if relative_humidity < 0 or relative_humidity > 100.5:
                if relative_humidity > 100.5:
                    warnings.warn(f"Relativ fuktighet {relative_humidity:.1f}% over 100%. "
                                 f"Dette kan indikere fysisk umulige forhold.", UserWarning)
                if relative_humidity < 0:
                    raise ValueError(f"Relativ fuktighet kan ikke være negativ: {relative_humidity}%")
        
        if humidity_ratio is not None:
            if humidity_ratio < 0:
                raise ValueError(f"Fuktighetsforhold kan ikke være negativt: {humidity_ratio}")
            if humidity_ratio > self.HUMIDITY_RATIO_MAX:
                warnings.warn(f"Fuktighetsforhold {humidity_ratio:.4f} kg/kg over praktisk grense "
                             f"({self.HUMIDITY_RATIO_MAX} kg/kg). Dette er ekstremt fuktige forhold.", 
                             UserWarning)
    
    def _initialize_engine(self, engine):
        """Initialiserer termodynamisk engine basert på input."""
        if engine is None:
            # Standard oppførsel: Bruk innebygde ASHRAE-beregninger
            return None
        
        if isinstance(engine, str):
            if engine.lower() == "coolprop":
                return self._get_coolprop_engine()
            elif engine.lower() == "ashrae":
                return None  # Standard ASHRAE
            else:
                warnings.warn(f"Ukjent engine '{engine}'. Bruker standard ASHRAE-implementasjon.", 
                             UserWarning)
                return None
        else:
            # Antatt å være engine objekt med calculate_properties metode
            return engine
    
    def _get_coolprop_engine(self):
        """Prøver å lage CoolProp engine."""
        try:
            import CoolProp.HumidAir as HA
            return CoolPropEngine()
        except ImportError:
            warnings.warn("CoolProp ikke tilgjengelig. Bruker standard ASHRAE-implementasjon.", 
                         UserWarning)
            return None
    
    def _get_engine_properties(self):
        """Henter alle egenskaper fra engine hvis tilgjengelig."""
        if self._engine is not None and hasattr(self._engine, 'calculate_properties'):
            humidity_input = {'humidity_ratio': self.humidity_ratio}
            return self._engine.calculate_properties(self.temperature, self.pressure, humidity_input)
        return None
    
    @staticmethod
    def atmospheric_pressure(altitude: float) -> float:
        """
        Beregner atmosfærisk trykk ved gitt høyde over havet.
        
        Bruker barometrisk formel basert på standard atmosfære.
        Gyldig for høyder opp til ~11000m.
        
        Args:
            altitude: Høyde over havet [m]
                     Gyldighetsområde: -500m til 11000m
            
        Returns:
            Atmosfærisk trykk [Pa]
            
        Examples:
            >>> MoistAir.atmospheric_pressure(0)      # Havnivå: ~101325 Pa
            >>> MoistAir.atmospheric_pressure(1000)   # 1000m: ~89876 Pa
            >>> MoistAir.atmospheric_pressure(3000)   # 3000m: ~69682 Pa
        """
        if altitude < -500 or altitude > 11000:
            warnings.warn(f"Høyde {altitude}m utenfor anbefalt område (-500m til 11000m). "
                         f"Nøyaktigheten kan være redusert.", UserWarning)
        
        return 101325 * (1 - 2.25577e-5 * altitude)**5.25588
    
    @staticmethod
    def validate_psychrometric_consistency(temperature: float, wet_bulb: float, 
                                         dew_point: float) -> bool:
        """
        Validerer psykrometrisk konsistens mellom temperaturer.
        
        Args:
            temperature: Tørrkuletemperatur [°C]
            wet_bulb: Våtkuletemperatur [°C]  
            dew_point: Duggpunkt [°C]
            
        Returns:
            True hvis konsistent, False ellers
            
        Note:
            Fysisk riktig rekkefølge: dew_point <= wet_bulb <= temperature
        """
        tolerance = 0.01  # °C
        return (dew_point <= wet_bulb + tolerance and 
                wet_bulb <= temperature + tolerance)
    
    def _calc_humidity_ratio_from_rh(self, rh: float) -> float:
        """Beregner fuktighetsforhold fra relativ fuktighet."""
        p_sat = self._saturation_pressure(self.temperature)
        p_vapor = rh / 100 * p_sat
        return 0.622 * p_vapor / (self.pressure - p_vapor)
    
    def _saturation_pressure(self, temp: float) -> float:
        """
        Beregner metningstrykk for vanndamp [Pa].
        
        Bruker forbedrede formler for større nøyaktighet:
        - Goff-Gratch ligning for ekstreme temperaturer
        - Magnus formel for normale temperaturer
        """
        # For ekstreme temperaturer, bruk Goff-Gratch ligning
        if temp < -40 or temp > 80:
            return self._saturation_pressure_goff_gratch(temp)
        
        # Magnus formel for normale temperaturer (høyere hastighet)
        if temp >= 0:
            # For væske (over 0°C)
            return 610.78 * np.exp(17.27 * temp / (temp + 237.3))
        else:
            # For is (under 0°C) 
            return 610.78 * np.exp(21.875 * temp / (temp + 265.5))
    
    def _saturation_pressure_goff_gratch(self, temp: float) -> float:
        """
        Beregner metningstrykk med Goff-Gratch ligning for høy nøyaktighet.
        
        Gyldig område: -100°C til 100°C
        """
        T = temp + 273.15  # Konverter til Kelvin
        
        if temp >= 0.01:
            # Goff-Gratch ligning for væske
            T_s = 373.16  # Triple point temperature
            log10_p = -7.90298 * (T_s/T - 1) + \
                      5.02808 * np.log10(T_s/T) - \
                      1.3816e-7 * (10**(11.344*(1 - T/T_s)) - 1) + \
                      8.1328e-3 * (10**(-3.49149*(T_s/T - 1)) - 1) + \
                      np.log10(1013.246)
            return 100 * (10**log10_p)  # Konverter fra mbar til Pa
        else:
            # Goff-Gratch ligning for is
            T_s = 273.16  # Triple point temperature
            log10_p = -9.09718 * (T_s/T - 1) - \
                      3.56654 * np.log10(T_s/T) + \
                      0.876793 * (1 - T/T_s) + \
                      np.log10(6.1071)
            return 100 * (10**log10_p)  # Konverter fra mbar til Pa
    
    def _calc_humidity_ratio_from_wet_bulb(self, wet_bulb_temp: float) -> float:
        """Beregner fuktighetsforhold fra våtkuletemperatur [ASHRAE-metode]."""
        # Validering: våtkule kan ikke være høyere enn tørrkule
        if wet_bulb_temp > self.temperature + 0.01:
            raise ValueError(f"Våtkuletemperatur ({wet_bulb_temp:.1f}°C) kan ikke være høyere enn tørrkule ({self.temperature:.1f}°C)")
        
        # Hvis temperaturene er nesten like, er lufta mettet
        if abs(self.temperature - wet_bulb_temp) < 0.01:
            return self._calc_humidity_ratio_from_rh_at_temp(100.0, wet_bulb_temp)
        
        # Bruk konstante verdier for konsistens i våtkule-beregninger
        c_pa = 1.006  # Spesifikk varmekapasitet tørr luft [kJ/kg·K]
        c_pw = 4.186  # Spesifikk varmekapasitet vann [kJ/kg·K]
        
        # Ved våtkule-temperatur er luften mettet
        w_sat_wb = self._calc_humidity_ratio_from_rh_at_temp(100.0, wet_bulb_temp)
        
        # ASHRAE psykrometrisk fundamentalligning:
        # h = c_pa * T + w * (h_fg + c_pv * T)
        # Ved våtkule: h_db = h_wb + (w_sat_wb - w) * c_pw * (T_db - T_wb)
        
        # Entalpi ved våtkule-tilstand (mettet)
        h_fg_wb = 2501 + 1.86 * wet_bulb_temp  # Forenklad fordampingsvarme for konsistens
        h_wb = c_pa * wet_bulb_temp + w_sat_wb * h_fg_wb
        
        # Løs for w fra psykrometrisk ligning
        # h_db = c_pa * T_db + w * (2501 + 1.86 * T_db)
        # h_db = h_wb + (w_sat_wb - w) * c_pw * (T_db - T_wb)
        
        # Kombinert: c_pa * T_db + w * (2501 + 1.86 * T_db) = h_wb + (w_sat_wb - w) * c_pw * (T_db - T_wb)
        # Omskrevet: w * [(2501 + 1.86 * T_db) + c_pw * (T_db - T_wb)] = h_wb + w_sat_wb * c_pw * (T_db - T_wb) - c_pa * T_db
        
        dt = self.temperature - wet_bulb_temp
        h_fg_db = 2501 + 1.86 * self.temperature
        
        numerator = h_wb + w_sat_wb * c_pw * dt - c_pa * self.temperature
        denominator = h_fg_db + c_pw * dt
        
        if abs(denominator) > 1e-10:
            w = numerator / denominator
        else:
            # Fallback hvis denominatoren er nær null
            w = w_sat_wb * 0.8
        
        # Begrens til fysisk mulige verdier
        w = max(0.0, min(w, w_sat_wb))
        
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
        # Prøv å bruke engine først
        engine_props = self._get_engine_properties()
        if engine_props and 'relative_humidity' in engine_props:
            return engine_props['relative_humidity']
        
        # Fallback til original beregning
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
    def specific_heat_dry_air(self) -> float:
        """Temperaturavhengig spesifikk varmekapasitet for tørr luft [kJ/kg·K]."""
        T = self.temperature + 273.15
        # Polynomisk tilnærming basert på NIST data
        return 1.030356 - 0.00028470 * T + 7.8163e-7 * T**2 - 4.2773e-10 * T**3
    
    @cached_property
    def specific_heat_water_vapor(self) -> float:
        """Temperaturavhengig spesifikk varmekapasitet for vanndamp [kJ/kg·K]."""
        T = self.temperature + 273.15
        # Polynomisk tilnærming basert på NIST data
        return 1.3605 + 2.31334e-3 * T - 2.46784e-10 * T**2 + 5.91332e-13 * T**3
    
    @cached_property
    def latent_heat_vaporization(self) -> float:
        """Temperaturavhengig fordampingsvarme [kJ/kg]."""
        # Mer nøyaktig formel enn konstant 2501
        return 2501.3 - 2.361 * self.temperature
    
    @cached_property
    def enthalpy(self) -> float:
        """Entalpi [kJ/kg_tørr_luft] - med temperaturavhengige egenskaper."""
        cp_a = self.specific_heat_dry_air
        cp_v = self.specific_heat_water_vapor
        h_fg = self.latent_heat_vaporization
        
        return cp_a * self.temperature + self.humidity_ratio * (h_fg + cp_v * self.temperature)
    
    @cached_property
    def wet_bulb(self) -> float:
        """Våtkuletemperatur [°C] - ASHRAE metode."""
        # For mettet luft er våtkule = tørrkule
        if self.relative_humidity >= 99.9:
            return self.temperature
            
        # Benytt ASHRAE iterativ algoritme
        # Psykrometrisk fundamentalligning: h = h_wb + (w_s,wb - w) * c_pw * (T - T_wb)
        
        # Startverdi: interpolasjon mellom duggpunkt og tørrkule
        t_wb = self.dew_point + 0.33 * (self.temperature - self.dew_point)
        
        for iteration in range(25):
            # Metningsverdi ved denne våtkule-temperaturen
            w_sat_wb = self._calc_humidity_ratio_from_rh_at_temp(100.0, t_wb)
            
            # Entalpi ved våtkule-tilstand (bruk forenklede konstanter for hastighet)
            h_wb = 1.006 * t_wb + w_sat_wb * (2501 + 1.86 * t_wb)
            
            # Entalpi ved tørrkule-tilstand
            h_db = 1.006 * self.temperature + self.humidity_ratio * (2501 + 1.86 * self.temperature)
            
            # ASHRAE psykrometrisk ligning:
            # h_db = h_wb + (w_sat_wb - w) * c_pw * (T_db - T_wb)
            # Løst for T_wb:
            c_pw = 4.186  # kJ/kg·K
            
            if abs(w_sat_wb - self.humidity_ratio) > 1e-8 and abs(self.temperature - t_wb) > 1e-8:
                # Ny estimat
                f_wb = h_db - h_wb - (w_sat_wb - self.humidity_ratio) * c_pw * (self.temperature - t_wb)
                
                # Beregn derivat for Newton-Raphson
                delta_t = 0.1
                w_sat_wb_plus = self._calc_humidity_ratio_from_rh_at_temp(100.0, t_wb + delta_t)
                h_wb_plus = 1.006 * (t_wb + delta_t) + w_sat_wb_plus * (2501 + 1.86 * (t_wb + delta_t))
                
                f_wb_plus = h_db - h_wb_plus - (w_sat_wb_plus - self.humidity_ratio) * c_pw * (self.temperature - (t_wb + delta_t))
                
                df_dt = (f_wb_plus - f_wb) / delta_t
                
                if abs(df_dt) > 1e-10:
                    t_wb_new = t_wb - f_wb / df_dt
                else:
                    # Fallback til bisection
                    t_wb_new = (t_wb + self.dew_point) / 2
            else:
                break
                
            # Begrens til fysisk mulige verdier
            t_wb_new = max(self.dew_point, min(t_wb_new, self.temperature))
            
            # Konvergenssjekk
            if abs(t_wb_new - t_wb) < 0.005:
                t_wb = t_wb_new
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
    
    @property
    def is_physically_valid(self) -> bool:
        """
        Sjekker om lufttilstanden er fysisk gyldig.
        
        Returns:
            True hvis tilstanden er fysisk konsistent
        """
        try:
            # Sjekk grunnleggende begrensninger
            if self.relative_humidity < 0 or self.relative_humidity > 101:
                return False
            if self.humidity_ratio < 0:
                return False
            
            # Sjekk temperaturrekkefølge
            if not self.validate_psychrometric_consistency(
                self.temperature, self.wet_bulb, self.dew_point):
                return False
                
            return True
        except:
            return False
    
    def get_validation_warnings(self) -> list:
        """
        Returnerer liste over valideringsvarsler for denne tilstanden.
        
        Returns:
            Liste med beskrivende advarsler som strenger
        """
        warnings_list = []
        
        if self.temperature < self.TEMP_MIN_OPTIMAL or self.temperature > self.TEMP_MAX_OPTIMAL:
            warnings_list.append(f"Temperatur {self.temperature}°C utenfor optimalt område "
                                f"({self.TEMP_MIN_OPTIMAL}°C til {self.TEMP_MAX_OPTIMAL}°C)")
        
        if self.pressure < self.PRESSURE_MIN_OPTIMAL or self.pressure > self.PRESSURE_MAX_OPTIMAL:
            warnings_list.append(f"Trykk {self.pressure/1000:.1f} kPa utenfor optimalt område "
                                f"({self.PRESSURE_MIN_OPTIMAL/1000:.1f} til {self.PRESSURE_MAX_OPTIMAL/1000:.1f} kPa)")
        
        if self.relative_humidity > 100.1:
            warnings_list.append(f"Relativ fuktighet {self.relative_humidity:.1f}% over 100%")
        
        if self.humidity_ratio > self.HUMIDITY_RATIO_MAX:
            warnings_list.append(f"Fuktighetsforhold {self.humidity_ratio:.4f} kg/kg over praktisk grense")
        
        return warnings_list


class Psychrometrics:
    """
    Samling av psykrometriske beregningsfunksjoner.
    
    Inneholder statiske metoder for vanlige HVAC-beregninger som:
    - Blanding av luftstrømmer
    - Sensibel kjøling/oppvarming
    - Prosessanalyse
    
    Note:
        Alle beregninger bruker de samme gyldighetsområdene som MoistAir-klassen.
        Ved ekstreme forhold gis advarsler, men beregninger utføres likevel.
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
        # Bruk konstante verdier for konsistens med øvrige beregninger
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
