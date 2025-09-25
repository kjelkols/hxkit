"""
HXKit - Et bibliotek for å bygge varmevekslere
==================================================

Dette biblioteket inneholder byggesteiner for termodynamikk og strømningsberegninger
for varmevekslere, med fokus på platevarmevekslere for fuktig luft.

Hovedmoduler:
- thermodynamics: Termodynamiske egenskaper og beregninger
- fluid_flow: Strømningsberegninger
- heat_transfer: Varmeoverføringsmodeller
- plate_heat_exchanger: Platevarmevekslermodeller
- geometries: Geometriske beskrivelser av varmevekslere
"""

__version__ = "0.2.0"
__author__ = "Kjell Kolsaker"

# Enkle, direkte imports
from .thermodynamics import MoistAir, Psychrometrics
from .fluid_flow import FlowCalculator
from .heat_transfer import HeatTransferCoefficients
from .plate_heat_exchanger import PlateHeatExchanger
from .geometries import PlateGeometry, HeatExchangerCore

__all__ = [
    "MoistAir",
    "Psychrometrics",
    "FlowCalculator", 
    "HeatTransferCoefficients",
    "PlateHeatExchanger",
    "PlateGeometry",
    "HeatExchangerCore",
]
