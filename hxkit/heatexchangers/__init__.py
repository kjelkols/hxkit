"""
Heat exchanger modules for HXKit.

This package contains different types of heat exchanger implementations:
- plate: Metal plate heat exchangers with chevron patterns
- plastic_plate: Plastic plate heat exchangers with grid-based simulation
"""

# Import main heat exchanger classes for convenient access
from .plate.analyzer import PlateHeatExchanger
from .plastic_plate.analyzer import PlasticPlateHeatExchanger

__all__ = [
    'PlateHeatExchanger',
    'PlasticPlateHeatExchanger',
]