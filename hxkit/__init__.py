"""
HXKit - Et bibliotek for å bygge varmevekslere
==================================================

Dette biblioteket inneholder byggesteiner for termodynamikk og strømningsberegninger
for varmevekslere, med fokus på platevarmevekslere for fuktig luft.

Hovedmoduler:
- thermodynamics: Termodynamiske egenskaper og beregninger
- fluid_flow: Strømningsberegninger
- heat_transfer: Varmeoverføringsmodeller
- heatexchangers: Varmevekslermodeller (plate og plastic_plate)
- grid: Grid-system for numeriske beregninger
"""

__version__ = "0.2.0"
__author__ = "Kjell Kolsaker"

# Core modules
from .thermodynamics import MoistAir, Psychrometrics
from .fluid_flow import FlowCalculator
from .heat_transfer import HeatTransferCoefficients
from .streams import AirStream
from .definitions import Direction

# Heat exchangers - imported from new structure
from .heatexchangers.plate import PlateHeatExchanger, PlateGeometry, HeatExchangerCore
from .heatexchangers.plastic_plate import PlasticPlateHeatExchanger, PlasticPlateResults

# Visualization functions (optional dependencies)
try:
    from .visualization import visualize_heat_exchanger, create_interactive_visualization
    _VISUALIZATION_AVAILABLE = True
except ImportError:
    _VISUALIZATION_AVAILABLE = False

__all__ = [
    "MoistAir",
    "Psychrometrics", 
    "FlowCalculator",
    "HeatTransferCoefficients",
    "PlateHeatExchanger",
    "PlateGeometry", 
    "HeatExchangerCore",
    "PlasticPlateHeatExchanger",
    "AirStream",
    "Direction",
    "PlasticPlateResults",
]

# Add visualization functions if available
if _VISUALIZATION_AVAILABLE:
    __all__.extend(["visualize_heat_exchanger", "create_interactive_visualization"])
