"""
Definerer strømningsklasser for prosess-simulering.
"""

from .thermodynamics import MoistAir
from .definitions import Direction

class AirStream:
    """
    Kombinerer en MoistAir-tilstand med en massestrøm og retning.
    
    Denne klassen representerer en komplett luftstrøm inn i eller ut av 
    en komponent i en prosess-simulering.
    """
    
    def __init__(self, moist_air: MoistAir, mass_flow: float, direction: Direction):
        """
        Initialiserer luftstrømmen.
        
        Args:
            moist_air: Termodynamisk tilstand for luften (MoistAir objekt).
            mass_flow: Massestrøm av tørr luft [kg/s].
            direction: Strømningsretning på et grid (Direction enum).
        """
        self.moist_air = moist_air
        self.mass_flow = mass_flow
        self.direction = direction
        
    @property
    def volume_flow(self) -> float:
        """Beregner volumstrøm [m³/s]."""
        return self.mass_flow * self.moist_air.specific_volume
        
    @property
    def enthalpy_flow(self) -> float:
        """Beregner entalpistrøm [kW]."""
        return self.mass_flow * self.moist_air.enthalpy
