"""
API adapters som kobler Pydantic schemas til kjernefunksjonaliteten.
"""

from .adapters import *

__all__ = [
    "ThermodynamicsAdapter",
    "GeometryAdapter", 
    "AnalysisAdapter",
    "ConfigAdapter",
]
