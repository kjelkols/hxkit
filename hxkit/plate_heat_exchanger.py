"""
Platevarmevekslermodeller og beregninger.

Dette modulet inneholder hovedklassen for platevarmeveksleranalyse
som kombinerer termodynamikk, strømning og varmeoverføring.
"""

import numpy as np
from typing import Union, Tuple, Optional, Dict
# Import MoistAir og Psychrometrics dynamisk for å unngå sirkulær import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .thermodynamics import MoistAir, Psychrometrics
from .fluid_flow import FlowCalculator, MassFlowDistribution
from .heat_transfer import HeatTransferCoefficients, EffectivenessNTU
from .geometries import PlateGeometry, HeatExchangerCore


class PlateHeatExchanger:
    """
    Hovedklasse for platevarmeveksleranalyse.
    
    Denne klassen kombinerer alle byggesteinene for å utføre komplette
    beregninger av platevarmevekslere.
    """
    
    def __init__(self, core: HeatExchangerCore, wall_thickness: float = 0.0005,
                 wall_conductivity: float = 16.0):
        """
        Initialiserer platevarmeveksler.
        
        Args:
            core: HeatExchangerCore objekt med geometri
            wall_thickness: Platetykkelse [m]
            wall_conductivity: Termisk konduktivitet for platemateriale [W/m·K]
        """
        self.core = core
        self.wall_thickness = wall_thickness
        self.wall_conductivity = wall_conductivity
        self.effectiveness_ntu = EffectivenessNTU()
    
    def analyze(self, hot_inlet, cold_inlet,
                hot_mass_flow: float, cold_mass_flow: float) -> Dict:
        """
        Utfører fullstendig analyse av varmeveksleren.
        
        Args:
            hot_inlet: Varm innløpstilstand
            cold_inlet: Kald innløpstilstand  
            hot_mass_flow: Varm massestrøm [kg/s]
            cold_mass_flow: Kald massestrøm [kg/s]
            
        Returns:
            Dictionary med resultater
        """
        # Beregn hastigheter
        hot_velocity = self._calculate_velocity(hot_mass_flow, hot_inlet, "hot")
        cold_velocity = self._calculate_velocity(cold_mass_flow, cold_inlet, "cold")
        
        # Beregn varmeoverføringskoeffisienter
        hot_htc = self._heat_transfer_coefficient(hot_inlet, hot_velocity)
        cold_htc = self._heat_transfer_coefficient(cold_inlet, cold_velocity)
        
        # Beregn overall varmeoverføringskoeffisient
        u_overall = self._overall_heat_transfer_coefficient(hot_htc, cold_htc)
        
        # Beregn varmekapasitetsrater
        cp_hot = 1006 + 1.86 * hot_inlet.humidity_ratio  # [J/kg·K]
        cp_cold = 1006 + 1.86 * cold_inlet.humidity_ratio
        c_hot = hot_mass_flow * cp_hot
        c_cold = cold_mass_flow * cp_cold
        c_min = min(c_hot, c_cold)
        
        # Effectiveness-NTU analyse
        ua_value = u_overall * self.core.total_heat_transfer_area
        ntu = self.effectiveness_ntu.ntu(ua_value, c_min)
        cr = self.effectiveness_ntu.capacity_rate_ratio(c_hot, c_cold)
        effectiveness = self.effectiveness_ntu.effectiveness_counterflow(ntu, cr)
        
        # Beregn varmeoverføring
        q_max = c_min * (hot_inlet.temperature - cold_inlet.temperature)
        q_actual = effectiveness * q_max
        
        # Beregn utløpstemperaturer
        hot_outlet_temp = hot_inlet.temperature - q_actual / c_hot
        cold_outlet_temp = cold_inlet.temperature + q_actual / c_cold
        
        # Lag utløpstilstander (antatt sensibel varmeoverføring)
        hot_outlet = Psychrometrics.sensible_cooling(hot_inlet, hot_outlet_temp)
        # Lazy import av MoistAir
        import importlib
        hxkit = importlib.import_module('hxkit')
        MoistAir = hxkit.MoistAir
        
        cold_outlet = MoistAir(temperature=cold_outlet_temp, 
                              humidity_ratio=cold_inlet.humidity_ratio,
                              pressure=cold_inlet.pressure)
        
        # Beregn trykkfall
        hot_pressure_drop = self._pressure_drop(hot_inlet, hot_velocity, "hot")
        cold_pressure_drop = self._pressure_drop(cold_inlet, cold_velocity, "cold")
        
        return {
            "heat_transfer_rate": q_actual,  # [W]
            "effectiveness": effectiveness,
            "ntu": ntu,
            "hot_outlet": hot_outlet,
            "cold_outlet": cold_outlet,
            "hot_pressure_drop": hot_pressure_drop,  # [Pa]
            "cold_pressure_drop": cold_pressure_drop,
            "hot_velocity": hot_velocity,  # [m/s]
            "cold_velocity": cold_velocity,
            "u_overall": u_overall,  # [W/m²·K]
            "hot_htc": hot_htc,
            "cold_htc": cold_htc,
        }
    
    def _calculate_velocity(self, mass_flow: float, fluid, side: str) -> float:
        """Beregner hastighet basert på massestrøm og geometri."""
        if side == "hot":
            flow_area = self.core.hot_side_flow_area
        else:
            flow_area = self.core.cold_side_flow_area
        
        return mass_flow / (fluid.density * flow_area)
    
    def _heat_transfer_coefficient(self, fluid, velocity: float) -> float:
        """Beregner varmeoverføringskoeffisient."""
        htc_calc = HeatTransferCoefficients(fluid)
        return htc_calc.heat_transfer_coefficient(velocity, self.core.plate_geometry)
    
    def _overall_heat_transfer_coefficient(self, h_hot: float, h_cold: float) -> float:
        """Beregner overall varmeoverføringskoeffisient."""
        wall_resistance = self.wall_thickness / self.wall_conductivity
        return 1 / (1/h_hot + wall_resistance + 1/h_cold)
    
    def _pressure_drop(self, fluid, velocity: float, side: str) -> float:
        """Beregner trykkfall."""
        flow_calc = FlowCalculator(fluid)
        return flow_calc.pressure_drop_plate(velocity, self.core.plate_geometry)
    
    def performance_map(self, hot_inlet, cold_inlet,
                       mass_flow_range: Tuple[float, float], 
                       n_points: int = 20) -> Dict:
        """
        Lager performance map for varmeveksleren.
        
        Args:
            hot_inlet: Varm innløpstilstand
            cold_inlet: Kald innløpstilstand
            mass_flow_range: (min, max) massestrøm [kg/s]
            n_points: Antall beregningspunkter
            
        Returns:
            Dictionary med arrays av resultater
        """
        mass_flows = np.linspace(mass_flow_range[0], mass_flow_range[1], n_points)
        
        results = {
            "mass_flows": mass_flows,
            "heat_transfer_rates": [],
            "effectiveness": [],
            "hot_pressure_drops": [],
            "cold_pressure_drops": []
        }
        
        for m_dot in mass_flows:
            analysis = self.analyze(hot_inlet, cold_inlet, m_dot, m_dot)
            results["heat_transfer_rates"].append(analysis["heat_transfer_rate"])
            results["effectiveness"].append(analysis["effectiveness"])
            results["hot_pressure_drops"].append(analysis["hot_pressure_drop"])
            results["cold_pressure_drops"].append(analysis["cold_pressure_drop"])
        
        # Konverter til numpy arrays
        for key in ["heat_transfer_rates", "effectiveness", "hot_pressure_drops", "cold_pressure_drops"]:
            results[key] = np.array(results[key])
        
        return results
    
    def optimize_geometry(self, hot_inlet, cold_inlet,
                         hot_mass_flow: float, cold_mass_flow: float,
                         target_effectiveness: float = 0.8) -> HeatExchangerCore:
        """
        Optimaliserer varmevekslerkjerne for ønsket effectiveness.
        
        Args:
            hot_inlet: Varm innløpstilstand
            cold_inlet: Kald innløpstilstand
            hot_mass_flow: Varm massestrøm [kg/s]
            cold_mass_flow: Kald massestrøm [kg/s]
            target_effectiveness: Ønsket effectiveness [-]
            
        Returns:
            Optimalisert HeatExchangerCore objekt
        """
        # Enkel optimalisering - varierer antall plater
        current_geometry = self.core.plate_geometry
        best_n_plates = self.core.n_plates
        
        for n_plates in range(5, 50, 2):
            # Lag ny kjerne med forskjellig antall plater
            hot_channels = (n_plates - 1) // 2
            cold_channels = n_plates - 1 - hot_channels
            
            test_core = HeatExchangerCore(n_plates, current_geometry, 
                                        hot_channels, cold_channels)
            test_hx = PlateHeatExchanger(test_core)
            
            analysis = test_hx.analyze(hot_inlet, cold_inlet, 
                                     hot_mass_flow, cold_mass_flow)
            
            if abs(analysis["effectiveness"] - target_effectiveness) < 0.01:
                best_n_plates = n_plates
                break
        
        # Returner optimalisert kjerne
        return HeatExchangerCore(best_n_plates, current_geometry,
                               (best_n_plates - 1) // 2,
                               best_n_plates - 1 - (best_n_plates - 1) // 2)
