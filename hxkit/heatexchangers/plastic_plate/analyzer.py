"""
Simulator for platevarmevekslere i plast med grid-basert beregning.

Denne modulen inneholder hovedklassen `PlasticPlateHeatExchanger` og relaterte
klasser for å definere strømningskonfigurasjoner.
"""

from ...definitions import Direction
from ...grid.grids import Grid2D
from ...materials import PlasticMaterial
from ...streams import AirStream
from .solver import CrossflowSolver2D
from typing import Tuple


class FlowConfiguration:
    """
    Bestemmer strømningskonfigurasjonen (motstrøm, medstrøm, kryss-strøm)
    basert på retningene til den varme og kalde luftstrømmen.
    """
    def __init__(self, hot_direction: Direction, cold_direction: Direction):
        self.hot_direction = hot_direction
        self.cold_direction = cold_direction
        
    @property
    def is_counterflow(self) -> bool:
        """Sjekker om strømmene går i motsatte retninger."""
        return ((self.hot_direction == Direction.NORTH and self.cold_direction == Direction.SOUTH) or
                (self.hot_direction == Direction.SOUTH and self.cold_direction == Direction.NORTH) or
                (self.hot_direction == Direction.EAST and self.cold_direction == Direction.WEST) or
                (self.hot_direction == Direction.WEST and self.cold_direction == Direction.EAST))
    
    @property
    def is_crossflow(self) -> bool:
        """Sjekker om strømmene krysser hverandre (går langs forskjellige akser)."""
        hot_axis = "Y" if self.hot_direction in [Direction.NORTH, Direction.SOUTH] else "X"
        cold_axis = "Y" if self.cold_direction in [Direction.NORTH, Direction.SOUTH] else "X"
        return hot_axis != cold_axis
        
    @property
    def is_parallelflow(self) -> bool:
        """Sjekker om strømmene går i samme retning."""
        return self.hot_direction == self.cold_direction


class PlasticPlateGeometry:
    """
    Geometrisk beskrivelse for en enkel plast-platevarmeveksler.
    """
    def __init__(self, width: float, length: float, plate_thickness: float,
                 channel_height: float, num_plates: int):
        self.width = width
        self.length = length
        self.plate_thickness = plate_thickness
        self.channel_height = channel_height
        self.num_plates = num_plates

    @property
    def plate_area(self) -> float:
        """Arealet til en enkelt plate [m²]."""
        return self.width * self.length


class PlasticPlateHeatExchanger:
    """
    Simulator for plast-varmevekslere med grid-basert beregning.
    
    Støtter:
    - Counterflow, crossflow, parallelflow
    - Kondensering og frost/rim-dannelse (planlagt)
    - Glassfiber-forsterket plast materialegenskaper
    - Grid-basert numerisk løsning
    """
    
    def __init__(self, 
                 width: float,
                 length: float,
                 plate_thickness: float,
                 channel_height: float,
                 num_plates: int,
                 thermal_conductivity: float = 0.3,
                 grid_resolution: Tuple[int, int] = (10, 10)):
        
        self.geometry = PlasticPlateGeometry(
            width=width,
            length=length,
            plate_thickness=plate_thickness,
            channel_height=channel_height,
            num_plates=num_plates
        )
        self.material = PlasticMaterial(thermal_conductivity)
        self.grid_resolution = grid_resolution
        
        # Grid opprettes i analyze() basert på strømningskonfigurasjon
        self.grid = None
        self.solver = None
        
    def analyze(self, 
                hot_stream: AirStream,
                cold_stream: AirStream):
        """Hovedanalyse med grid-basert løsning."""
        
        # 1. Beregn antall kanaler og massestrøm per kanal
        # Antar jevn fordeling for enkelhets skyld
        num_channels = (self.geometry.num_plates - 1) / 2.0
        
        hot_mass_flow_per_channel = hot_stream.mass_flow / num_channels
        cold_mass_flow_per_channel = cold_stream.mass_flow / num_channels

        hot_stream_channel = AirStream(
            moist_air=hot_stream.moist_air,
            mass_flow=hot_mass_flow_per_channel,
            direction=hot_stream.direction
        )
        cold_stream_channel = AirStream(
            moist_air=cold_stream.moist_air,
            mass_flow=cold_mass_flow_per_channel,
            direction=cold_stream.direction
        )

        # 2. Bestem strømningskonfigurasjon og opprett optimalt grid
        flow_config = self._determine_flow_configuration(
            hot_stream.direction, cold_stream.direction)
        
        self.grid = self._create_optimal_grid(flow_config)
        self.solver = CrossflowSolver2D(self.grid, self.geometry, self.material)
            
        # 3. Løs systemet for en enkelt kanal
        results_channel = self.solver.solve(hot_stream_channel, cold_stream_channel)
            
        # 4. Skaler resultater til hele varmeveksleren
        results_channel.heat_transfer_rate *= num_channels
        
        return results_channel

    def _determine_flow_configuration(self, hot_direction: Direction, cold_direction: Direction) -> FlowConfiguration:
        """Hjelpemetode for å opprette FlowConfiguration."""
        return FlowConfiguration(hot_direction, cold_direction)
    
    def _create_optimal_grid(self, flow_config: FlowConfiguration) -> 'Grid2D':
        """
        Oppretter optimalt grid basert på strømningskonfigurasjon.
        
        For counterflow: Bruker 1D (en dimensjon har 1 segment)
        For crossflow: Bruker full 2D
        """
        width_seg, length_seg = self.grid_resolution
        
        if flow_config.is_counterflow or flow_config.is_parallelflow:
            # 1D-optimalisering: Velg retning basert på strømningsretning
            if flow_config.hot_direction in [Direction.NORTH, Direction.SOUTH]:
                # Strømning langs Y-aksen (bredde), 1D i Y-retning
                print(f"Optimaliserer for 1D strømning langs bredde: {max(width_seg, length_seg)} segmenter")
                return Grid2D(
                    width=self.geometry.width, 
                    length=self.geometry.length,
                    width_segments=max(width_seg, length_seg), 
                    length_segments=1
                )
            else:
                # Strømning langs X-aksen (lengde), 1D i X-retning  
                print(f"Optimaliserer for 1D strømning langs lengde: {max(width_seg, length_seg)} segmenter")
                return Grid2D(
                    width=self.geometry.width, 
                    length=self.geometry.length,
                    width_segments=1, 
                    length_segments=max(width_seg, length_seg)
                )
        else:
            # Full 2D for crossflow
            print(f"Bruker full 2D grid for crossflow: {width_seg}×{length_seg} segmenter")
            return Grid2D(
                width=self.geometry.width,
                length=self.geometry.length, 
                width_segments=width_seg,
                length_segments=length_seg
            )
