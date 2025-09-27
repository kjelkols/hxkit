"""
Definerer materialegenskaper for bruk i varmevekslerberegninger.
"""

class PlasticMaterial:
    """
    Materialegenskaper for glassfiber-forsterket plast.
    
    Inneholder typiske verdier for termisk konduktivitet, tetthet, etc.
    """
    
    def __init__(self, thermal_conductivity: float = 0.3):
        """
        Initialiserer materialet.
        
        Args:
            thermal_conductivity: Termisk konduktivitet [W/m·K].
                                  Default er 0.3 W/m·K.
        """
        self.thermal_conductivity = thermal_conductivity
        self.density = 1800.0                            # kg/m³
        self.specific_heat = 1200.0                      # J/kg·K
        self.surface_roughness = 2e-6                    # m (2 μm)
        
    @property
    def thermal_diffusivity(self) -> float:
        """Beregner temperaturledningsevne [m²/s]."""
        return self.thermal_conductivity / (self.density * self.specific_heat)
