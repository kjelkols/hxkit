"""
Geometriske beskrivelser av varmevekslere.

Dette modulet inneholder klasser for:
- Plategeometrier
- Kanalgeometrier  
- Generiske geometriske parametere
"""

import numpy as np
from typing import Union, Tuple, Optional, Callable


class PlateGeometry:
    """
    Klasse for beskrivelse av platevarmevekslergeometri.
    """
    
    def __init__(self, length: float, width: float, thickness: float,
                 channel_height: float, corrugation_angle: float = 60,
                 area_enhancement: float = 1.2):
        """
        Initialiserer plategeometri.
        
        Args:
            length: Platelengde [m]
            width: Platebredde [m] 
            thickness: Platetykkelse [m]
            channel_height: Kanalhøyde [m]
            corrugation_angle: Korrugeringsvinkel [grader]
            area_enhancement: Arealforstørrelsesfaktor [-]
        """
        self.length = length
        self.width = width
        self.thickness = thickness
        self.channel_height = channel_height
        self.corrugation_angle = np.radians(corrugation_angle)
        self.area_enhancement = area_enhancement
    
    @property
    def plate_area(self) -> float:
        """Plate overflateareal [m²]."""
        return self.length * self.width
    
    @property
    def effective_area(self) -> float:
        """Effektivt varmeoverføringsareal [m²]."""
        return self.plate_area * self.area_enhancement
    
    @property
    def flow_area(self) -> float:
        """Strømningsareal per kanal [m²]."""
        return self.width * self.channel_height
    
    @property
    def hydraulic_diameter(self) -> float:
        """Hydraulisk diameter [m]."""
        return 2 * self.channel_height  # For parallelle plater
    
    @property
    def wetted_perimeter(self) -> float:
        """Fuktet perimeter [m]."""
        return 2 * (self.width + self.channel_height)
    
    def friction_factor_correlation(self, Re: float) -> float:
        """
        Friksjonsfaktor korrelasjon for plater.
        
        Args:
            Re: Reynolds tall [-]
            
        Returns:
            Friksjonsfaktor [-]
        """
        # Eksempel korrelasjon for herringbone plater
        if Re < 10:
            return 64 / Re
        elif Re < 1000:
            return 0.7 + 25 / Re + 0.024 * (Re / 100)**0.5
        else:
            return 0.0791 * Re**(-0.25)
    
    def nusselt_correlation(self, Re: float, Pr: float) -> float:
        """
        Nusselt tall korrelasjon for plater.
        
        Args:
            Re: Reynolds tall [-]
            Pr: Prandtl tall [-]
            
        Returns:
            Nusselt tall [-]
        """
        # Eksempel korrelasjon for plater
        if Re < 1000:
            return 0.665 * Re**0.5 * Pr**(1/3)
        else:
            return 0.135 * Re**0.68 * Pr**0.4


class ChannelGeometry:
    """
    Klasse for beskrivelse av kanalgeometri.
    """
    
    def __init__(self, height: float, width: float, length: float):
        """
        Initialiserer kanalgeometri.
        
        Args:
            height: Kanalhøyde [m]
            width: Kanalbredde [m]
            length: Kanallengde [m]
        """
        self.height = height
        self.width = width
        self.length = length
    
    @property
    def cross_sectional_area(self) -> float:
        """Tverrsnittsareal [m²]."""
        return self.height * self.width
    
    @property
    def hydraulic_diameter(self) -> float:
        """Hydraulisk diameter [m]."""
        return 4 * self.cross_sectional_area / self.wetted_perimeter
    
    @property
    def wetted_perimeter(self) -> float:
        """Fuktet perimeter [m]."""
        return 2 * (self.height + self.width)
    
    @property
    def aspect_ratio(self) -> float:
        """Sideforhold [-]."""
        return self.width / self.height


class HeatExchangerCore:
    """
    Klasse for beskrivelse av varmevekslerkjerne.
    """
    
    def __init__(self, n_plates: int, plate_geometry: PlateGeometry,
                 hot_channels: int, cold_channels: int):
        """
        Initialiserer varmevekslerkjerne.
        
        Args:
            n_plates: Antall plater
            plate_geometry: Plategeometri objekt
            hot_channels: Antall varme kanaler
            cold_channels: Antall kalde kanaler
        """
        self.n_plates = n_plates
        self.plate_geometry = plate_geometry
        self.hot_channels = hot_channels
        self.cold_channels = cold_channels
        
        if hot_channels + cold_channels != n_plates - 1:
            raise ValueError("Antall kanaler må være konsistent med antall plater")
    
    @property
    def total_heat_transfer_area(self) -> float:
        """Totalt varmeoverføringsareal [m²]."""
        return (self.n_plates - 1) * self.plate_geometry.effective_area
    
    @property
    def hot_side_flow_area(self) -> float:
        """Strømningsareal varm side [m²]."""
        return self.hot_channels * self.plate_geometry.flow_area
    
    @property
    def cold_side_flow_area(self) -> float:
        """Strømningsareal kald side [m²]."""
        return self.cold_channels * self.plate_geometry.flow_area
    
    def channel_configuration(self) -> str:
        """Returnerer kanalkonfigurasjon som streng."""
        return f"{self.hot_channels}H-{self.cold_channels}C"


class GeometryFactory:
    """
    Factory klasse for å lage standardgeometrier.
    """
    
    @staticmethod
    def standard_plate(size: str = "medium") -> PlateGeometry:
        """
        Lager standard plategeometri.
        
        Args:
            size: Størrelse ("small", "medium", "large")
            
        Returns:
            PlateGeometry objekt
        """
        sizes = {
            "small": (0.3, 0.1, 0.0005, 0.003),
            "medium": (0.6, 0.2, 0.0005, 0.004),
            "large": (1.2, 0.4, 0.0006, 0.005)
        }
        
        if size not in sizes:
            raise ValueError(f"Ukjent størrelse: {size}")
        
        length, width, thickness, channel_height = sizes[size]
        return PlateGeometry(length, width, thickness, channel_height)
    
    @staticmethod
    def custom_plate(dimensions: dict) -> PlateGeometry:
        """
        Lager tilpasset plategeometri fra dimensjoner.
        
        Args:
            dimensions: Dictionary med geometriske parametere
            
        Returns:
            PlateGeometry objekt
        """
        required_keys = ["length", "width", "thickness", "channel_height"]
        if not all(key in dimensions for key in required_keys):
            raise ValueError(f"Må inneholde: {required_keys}")
        
        return PlateGeometry(**dimensions)
