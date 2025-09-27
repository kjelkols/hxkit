"""
Felles definisjoner og enums som brukes på tvers av moduler i HXKit.
"""

from enum import Enum

class Direction(Enum):
    """Himmelretninger for å definere strømningsretning på et 2D-grid."""
    NORTH = "north"    # +Y retning (langs bredde)
    SOUTH = "south"    # -Y retning (langs bredde) 
    EAST = "east"      # +X retning (langs lengde)
    WEST = "west"      # -X retning (langs lengde)
