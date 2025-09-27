"""
Plastic plate heat exchanger module.

Contains the plastic plate heat exchanger implementation with:
- Grid-based numerical simulation
- Phase change modeling (condensation/frost)
- Himmelretnings-system for flow configuration
"""

from .analyzer import PlasticPlateHeatExchanger, FlowConfiguration, PlasticPlateGeometry
from .solver import CrossflowSolver2D
from .results import PlasticPlateResults

__all__ = [
    'PlasticPlateHeatExchanger',
    'FlowConfiguration', 
    'PlasticPlateGeometry',
    'CrossflowSolver2D',
    'PlasticPlateResults'
]