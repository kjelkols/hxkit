"""
Varmeoverføringsmodeller og korrelasjoner.

Dette modulet inneholder klasser og funksjoner for:
- Varmeoverføringskoeffisienter
- Nusselt-tall korrelasjoner
- Varmevekslereffektivitet
"""

import numpy as np
from typing import Union, Tuple, Optional
from .thermodynamics import MoistAir
from .fluid_flow import FlowCalculator


class HeatTransferCoefficients:
    """
    Klasse for beregning av varmeoverføringskoeffisienter.
    """
    
    def __init__(self, fluid: MoistAir):
        """
        Initialiserer varmeoverføringskalkulator.
        
        Args:
            fluid: Fluid tilstand (MoistAir objekt)
        """
        self.fluid = fluid
        self.flow_calc = FlowCalculator(fluid)
    
    @property
    def thermal_conductivity(self) -> float:
        """Termisk konduktivitet for luft [W/m·K]."""
        T = self.fluid.temperature + 273.15
        return 0.0241 * (T / 273.15)**0.9
    
    @property
    def prandtl_number(self) -> float:
        """Prandtl tall [-]."""
        cp = 1006  # Spesifikk varmekapasitet for luft [J/kg·K]
        return self.flow_calc.dynamic_viscosity * cp / self.thermal_conductivity
    
    def nusselt_number_plate(self, velocity: float, plate_geometry) -> float:
        """
        Beregner Nusselt tall for plate geometri.
        
        Args:
            velocity: Hastighet [m/s]
            plate_geometry: Plategeometri objekt
            
        Returns:
            Nusselt tall [-]
        """
        Re = self.flow_calc.reynolds_number(velocity, plate_geometry.hydraulic_diameter)
        Pr = self.prandtl_number
        
        if hasattr(plate_geometry, 'nusselt_correlation'):
            return plate_geometry.nusselt_correlation(Re, Pr)
        else:
            # Standard korrelasjon for plater
            if Re < 2000:
                # Laminær strømning
                return 0.332 * Re**0.5 * Pr**(1/3)
            else:
                # Turbulent strømning
                return 0.0296 * Re**0.8 * Pr**0.4
    
    def heat_transfer_coefficient(self, velocity: float, plate_geometry) -> float:
        """
        Beregner varmeoverføringskoeffisient.
        
        Args:
            velocity: Hastighet [m/s]
            plate_geometry: Plategeometri objekt
            
        Returns:
            Varmeoverføringskoeffisient [W/m²·K]
        """
        Nu = self.nusselt_number_plate(velocity, plate_geometry)
        return Nu * self.thermal_conductivity / plate_geometry.hydraulic_diameter


class EffectivenessNTU:
    """
    Klasse for effectiveness-NTU metoden for varmeveksleranalyse.
    """
    
    def __init__(self):
        """Initialiserer effectiveness-NTU kalkulator."""
        pass
    
    def ntu(self, ua_value: float, c_min: float) -> float:
        """
        Beregner Number of Transfer Units (NTU).
        
        Args:
            ua_value: UA verdi [W/K]
            c_min: Minimum varmekapasitetsrate [W/K]
            
        Returns:
            NTU [-]
        """
        return ua_value / c_min
    
    def capacity_rate_ratio(self, c_hot: float, c_cold: float) -> float:
        """
        Beregner varmekapasitetsrateforhold.
        
        Args:
            c_hot: Varm side varmekapasitetsrate [W/K]
            c_cold: Kald side varmekapasitetsrate [W/K]
            
        Returns:
            Kapasitetsrateforhold [-]
        """
        return min(c_hot, c_cold) / max(c_hot, c_cold)
    
    def effectiveness_counterflow(self, ntu: float, cr: float) -> float:
        """
        Beregner effectiveness for motstrømskonfigurasjon.
        
        Args:
            ntu: Number of Transfer Units [-]
            cr: Kapasitetsrateforhold [-]
            
        Returns:
            Effectiveness [-]
        """
        if abs(cr - 1.0) < 1e-6:
            return ntu / (1 + ntu)
        else:
            return (1 - np.exp(-ntu * (1 - cr))) / (1 - cr * np.exp(-ntu * (1 - cr)))
    
    def effectiveness_crossflow(self, ntu: float, cr: float, 
                              mixed_hot: bool = False, mixed_cold: bool = False) -> float:
        """
        Beregner effectiveness for kryssstrømskonfigurasjon.
        
        Args:
            ntu: Number of Transfer Units [-]
            cr: Kapasitetsrateforhold [-]
            mixed_hot: Om varm side er blandet
            mixed_cold: Om kald side er blandet
            
        Returns:
            Effectiveness [-]
        """
        if not mixed_hot and not mixed_cold:
            # Begge ublandede
            return 1 - np.exp((1/cr) * ntu**0.22 * (np.exp(-cr * ntu**0.78) - 1))
        elif mixed_hot and not mixed_cold:
            # Varm side blandet
            return (1/cr) * (1 - np.exp(-cr * (1 - np.exp(-ntu))))
        elif not mixed_hot and mixed_cold:
            # Kald side blandet
            return 1 - np.exp(-(1/cr) * (1 - np.exp(-cr * ntu)))
        else:
            # Begge blandede
            return ntu / (1 + ntu)


class ConvectiveCorrelations:
    """
    Samling av konvektive varmeoverføringskorrelasjoner.
    """
    
    @staticmethod
    def dittus_boelter(Re: float, Pr: float, heating: bool = True) -> float:
        """
        Dittus-Boelter korrelasjon for rør.
        
        Args:
            Re: Reynolds tall [-]
            Pr: Prandtl tall [-]
            heating: Om fluid blir varmet opp
            
        Returns:
            Nusselt tall [-]
        """
        n = 0.4 if heating else 0.3
        return 0.023 * Re**0.8 * Pr**n
    
    @staticmethod
    def gnielinski(Re: float, Pr: float, friction_factor: float) -> float:
        """
        Gnielinski korrelasjon for rør.
        
        Args:
            Re: Reynolds tall [-]
            Pr: Prandtl tall [-]
            friction_factor: Friksjonsfaktor [-]
            
        Returns:
            Nusselt tall [-]
        """
        numerator = (friction_factor / 8) * (Re - 1000) * Pr
        denominator = 1 + 12.7 * (friction_factor / 8)**0.5 * (Pr**(2/3) - 1)
        return numerator / denominator
