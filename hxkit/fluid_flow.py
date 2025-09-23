"""
Strømningsberegninger for varmevekslere.

Dette modulet inneholder klasser og funksjoner for:
- Trykkfall i kanaler og over plater
- Reynolds tall og strømningskarakteristikker
- Massestrømfordelinger
"""

import numpy as np
from typing import Union, Tuple, Optional
from .thermodynamics import MoistAir


class FlowCalculator:
    """
    Klasse for strømningsberegninger i varmevekslere.
    """
    
    def __init__(self, fluid: MoistAir):
        """
        Initialiserer strømningskalkulator for et gitt fluid.
        
        Args:
            fluid: Fluid tilstand (MoistAir objekt)
        """
        self.fluid = fluid
    
    @property
    def dynamic_viscosity(self) -> float:
        """Dynamisk viskositet [Pa·s]."""
        # For luft, temperaturavhengig viskositet
        T = self.fluid.temperature + 273.15
        return 1.716e-5 * (T / 273.15)**1.5 * (273.15 + 110.4) / (T + 110.4)
    
    @property
    def kinematic_viscosity(self) -> float:
        """Kinematisk viskositet [m²/s]."""
        return self.dynamic_viscosity / self.fluid.density
    
    def reynolds_number(self, velocity: float, characteristic_length: float) -> float:
        """
        Beregner Reynolds tall.
        
        Args:
            velocity: Hastighet [m/s]
            characteristic_length: Karakteristisk lengde [m]
            
        Returns:
            Reynolds tall [-]
        """
        return velocity * characteristic_length / self.kinematic_viscosity
    
    def pressure_drop_channel(self, velocity: float, length: float, 
                            hydraulic_diameter: float, roughness: float = 0) -> float:
        """
        Beregner trykkfall i en kanal.
        
        Args:
            velocity: Hastighet [m/s]
            length: Kanallengde [m]
            hydraulic_diameter: Hydraulisk diameter [m]
            roughness: Overflateruhet [m]
            
        Returns:
            Trykkfall [Pa]
        """
        Re = self.reynolds_number(velocity, hydraulic_diameter)
        
        # Friksjonsfaktor
        if Re < 2300:
            # Laminær strømning
            f = 64 / Re
        else:
            # Turbulent strømning - Colebrook-White
            relative_roughness = roughness / hydraulic_diameter
            f = self._colebrook_white(Re, relative_roughness)
        
        return f * (length / hydraulic_diameter) * 0.5 * self.fluid.density * velocity**2
    
    def _colebrook_white(self, Re: float, relative_roughness: float) -> float:
        """Beregner friksjonsfaktor med Colebrook-White ligning."""
        # Iterativ løsning
        f = 0.02  # Startverdi
        for _ in range(10):
            f_new = (-2 * np.log10(relative_roughness/3.7 + 2.51/(Re * np.sqrt(f))))**(-2)
            if abs(f_new - f) < 1e-6:
                break
            f = f_new
        return f
    
    def pressure_drop_plate(self, velocity: float, plate_geometry) -> float:
        """
        Beregner trykkfall over en varmevekslerplate.
        
        Args:
            velocity: Hastighet [m/s]
            plate_geometry: Plategeometri objekt
            
        Returns:
            Trykkfall [Pa]
        """
        Re = self.reynolds_number(velocity, plate_geometry.hydraulic_diameter)
        
        # Trykkfallskorrelasjon for plater (eksempel)
        if hasattr(plate_geometry, 'friction_factor_correlation'):
            f = plate_geometry.friction_factor_correlation(Re)
        else:
            # Standard korrelasjon for herringbone plater
            f = 0.724 + 22.6 / Re + 1.5 * (np.log10(Re / 10))**2.5
        
        return f * 0.5 * self.fluid.density * velocity**2


class MassFlowDistribution:
    """
    Klasse for beregning av massestrømfordelinger i parallelle kanaler.
    """
    
    def __init__(self, n_channels: int):
        """
        Initialiserer massestrømfordeling.
        
        Args:
            n_channels: Antall parallelle kanaler
        """
        self.n_channels = n_channels
    
    def uniform_distribution(self, total_mass_flow: float) -> np.ndarray:
        """
        Beregner uniform massestrømfordeling.
        
        Args:
            total_mass_flow: Total massestrøm [kg/s]
            
        Returns:
            Array med massestrøm per kanal [kg/s]
        """
        return np.full(self.n_channels, total_mass_flow / self.n_channels)
    
    def calculate_distribution(self, total_mass_flow: float, 
                             channel_resistances: np.ndarray) -> np.ndarray:
        """
        Beregner massestrømfordeling basert på kanalmotstander.
        
        Args:
            total_mass_flow: Total massestrøm [kg/s]
            channel_resistances: Array med hydraulisk motstand per kanal
            
        Returns:
            Array med massestrøm per kanal [kg/s]
        """
        # Inverst proporsjonal med motstand
        conductances = 1 / channel_resistances
        normalized_conductances = conductances / np.sum(conductances)
        return total_mass_flow * normalized_conductances
