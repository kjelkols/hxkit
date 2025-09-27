"""
Metal plate heat exchanger module.

Contains the traditional metal plate heat exchanger implementation
with chevron patterns and ASHRAE-based calculations.
"""

from .analyzer import PlateHeatExchanger
from .geometry import PlateGeometry, HeatExchangerCore, ChannelGeometry, GeometryFactory

__all__ = [
    'PlateHeatExchanger',
    'PlateGeometry', 
    'HeatExchangerCore',
    'ChannelGeometry',
    'GeometryFactory'
]