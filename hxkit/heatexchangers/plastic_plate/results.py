"""
Resultat-klasser for varmeveksler-analyser.
"""

import numpy as np
from ...thermodynamics import MoistAir

class PlasticPlateResults:
    """
    Holder resultatene fra en analyse av PlasticPlateHeatExchanger.
    
    Inneholder både overordnede ytelsesindikatorer og detaljerte
    grid-baserte data.
    """
    
    def __init__(self):
        self.effectiveness: float = 0.0
        self.ntu: float = 0.0
        self.heat_transfer_rate: float = 0.0     # kW
        self.pressure_drop_hot: float = 0.0      # Pa
        self.pressure_drop_cold: float = 0.0     # Pa
        
        # Faseendringer
        self.condensation_rate: float = 0.0      # kg/s
        self.frost_thickness: float = 0.0        # m
        
        # Grid-resultater
        self.plate_temperature_field: np.ndarray = None
        self.hot_air_temperature_field: np.ndarray = None
        self.cold_air_temperature_field: np.ndarray = None
        
        # Utløpstilstander
        self.hot_outlet_state: MoistAir = None
        self.cold_outlet_state: MoistAir = None
