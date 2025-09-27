"""
3D visualisering av varmeveksler-geometrier.

Dette modulet inneholder funksjoner for å visualisere varmevekslere
i tre dimensjoner, inkludert plater, kanaler og strømningsretninger.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.patches as patches
from typing import Tuple, List, Optional
from ..definitions import Direction


class HeatExchangerVisualizer:
    """
    Visualiserer varmevekslere i 3D med matplotlib.
    
    Kan vise både PlateHeatExchanger og PlasticPlateHeatExchanger
    med plater, kanaler og strømningsretninger.
    """
    
    def __init__(self, figsize: Tuple[float, float] = (12, 8)):
        """
        Initialiserer visualizer.
        
        Args:
            figsize: Størrelse på matplotlib figur (width, height).
        """
        self.figsize = figsize
        self.colors = {
            'hot_plate': '#FF6B6B',      # Rød for varme plater
            'cold_plate': '#4ECDC4',     # Turkis for kalde plater
            'plate_edge': '#2C3E50',     # Mørk grå for platekanter
            'hot_flow': '#FF9F43',       # Orange for varm strømning
            'cold_flow': '#00D2D3',      # Cyan for kald strømning
            'structure': '#95A5A6',      # Grå for struktur
        }
    
    def visualize_plastic_plate_hx(self, 
                                  geometry, 
                                  hot_direction: Direction,
                                  cold_direction: Direction,
                                  show_grid: bool = True,
                                  grid_resolution: Tuple[int, int] = (5, 5)) -> plt.Figure:
        """
        Visualiserer PlasticPlateHeatExchanger i 3D.
        
        Args:
            geometry: PlasticPlateGeometry objekt
            hot_direction: Retning for varm luftstrøm  
            cold_direction: Retning for kald luftstrøm
            show_grid: Om grid skal vises
            grid_resolution: Grid-oppløsning for visualisering
            
        Returns:
            matplotlib Figure objekt
        """
        fig = plt.figure(figsize=self.figsize)
        ax = fig.add_subplot(111, projection='3d')
        
        # Beregn dimensjoner
        width = geometry.width
        length = geometry.length
        plate_thickness = geometry.plate_thickness
        channel_height = geometry.channel_height
        num_plates = geometry.num_plates
        
        # Total høyde
        total_height = (num_plates * plate_thickness + 
                       (num_plates - 1) * channel_height)
        
        # Tegn plater
        self._draw_plates(ax, width, length, plate_thickness, 
                         channel_height, num_plates)
        
        # Tegn strømningsretninger
        self._draw_flow_directions(ax, width, length, total_height,
                                 hot_direction, cold_direction)
        
        # Tegn grid hvis ønsket
        if show_grid:
            self._draw_grid_on_plates(ax, width, length, plate_thickness,
                                    channel_height, num_plates, grid_resolution)
        
        # Sett opp akser og labels
        self._setup_axes(ax, width, length, total_height,
                        hot_direction, cold_direction)
        
        return fig
    
    def _draw_plates(self, ax, width: float, length: float, 
                    plate_thickness: float, channel_height: float, 
                    num_plates: int):
        """Tegner platene i varmeveksleren."""
        
        for i in range(num_plates):
            # Z-posisjon for denne platen
            z_pos = i * (plate_thickness + channel_height)
            
            # Bestem farge basert på om det er varm eller kald kanal
            if i % 2 == 0:
                color = self.colors['hot_plate']
                alpha = 0.7
            else:
                color = self.colors['cold_plate']  
                alpha = 0.7
            
            # Opprett plate som en boks
            self._draw_plate_box(ax, width, length, plate_thickness, z_pos, 
                                color, alpha)
    
    def _draw_plate_box(self, ax, width: float, length: float, 
                       thickness: float, z_pos: float, 
                       color: str, alpha: float):
        """Tegner en enkelt plate som en 3D boks."""
        
        # Definér hjørner for boksen
        x = [0, width, width, 0, 0, width, width, 0]
        y = [0, 0, length, length, 0, 0, length, length]  
        z = [z_pos, z_pos, z_pos, z_pos, 
             z_pos + thickness, z_pos + thickness, 
             z_pos + thickness, z_pos + thickness]
        
        # Definér flatene av boksen
        faces = [
            # Bunn
            [[x[0], y[0], z[0]], [x[1], y[1], z[1]], 
             [x[2], y[2], z[2]], [x[3], y[3], z[3]]],
            # Topp  
            [[x[4], y[4], z[4]], [x[5], y[5], z[5]], 
             [x[6], y[6], z[6]], [x[7], y[7], z[7]]],
            # Sider
            [[x[0], y[0], z[0]], [x[1], y[1], z[1]], 
             [x[5], y[5], z[5]], [x[4], y[4], z[4]]],
            [[x[1], y[1], z[1]], [x[2], y[2], z[2]], 
             [x[6], y[6], z[6]], [x[5], y[5], z[5]]],
            [[x[2], y[2], z[2]], [x[3], y[3], z[3]], 
             [x[7], y[7], z[7]], [x[6], y[6], z[6]]],
            [[x[3], y[3], z[3]], [x[0], y[0], z[0]], 
             [x[4], y[4], z[4]], [x[7], y[7], z[7]]],
        ]
        
        # Legg til flatene
        poly3d = Poly3DCollection(faces, alpha=alpha, facecolor=color, 
                                 edgecolor=self.colors['plate_edge'], 
                                 linewidth=0.5)
        ax.add_collection3d(poly3d)
    
    def _draw_flow_directions(self, ax, width: float, length: float, 
                             total_height: float, hot_direction: Direction, 
                             cold_direction: Direction):
        """Tegner piler som viser strømningsretningene."""
        
        # Definér pil-parametere
        arrow_length = min(width, length) * 0.3
        arrow_width = 0.02
        
        # Hot flow arrow (øverst)
        hot_z = total_height + 0.1
        hot_start, hot_end = self._get_flow_arrow_coords(
            hot_direction, width, length, arrow_length)
        
        ax.quiver(hot_start[0], hot_start[1], hot_z,
                 hot_end[0] - hot_start[0], 
                 hot_end[1] - hot_start[1], 0,
                 color=self.colors['hot_flow'], 
                 arrow_length_ratio=0.2, linewidth=3,
                 label=f'Varm luft ({hot_direction.value})')
        
        # Cold flow arrow (nederst)
        cold_z = -0.1
        cold_start, cold_end = self._get_flow_arrow_coords(
            cold_direction, width, length, arrow_length)
        
        ax.quiver(cold_start[0], cold_start[1], cold_z,
                 cold_end[0] - cold_start[0],
                 cold_end[1] - cold_start[1], 0,
                 color=self.colors['cold_flow'],
                 arrow_length_ratio=0.2, linewidth=3,
                 label=f'Kald luft ({cold_direction.value})')
    
    def _get_flow_arrow_coords(self, direction: Direction, width: float, 
                              length: float, arrow_length: float) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Beregner start- og slutt-koordinater for strømningspiler."""
        
        center_x, center_y = width / 2, length / 2
        
        if direction == Direction.NORTH:
            start = (center_x, center_y - arrow_length / 2)
            end = (center_x, center_y + arrow_length / 2)
        elif direction == Direction.SOUTH:
            start = (center_x, center_y + arrow_length / 2)
            end = (center_x, center_y - arrow_length / 2)
        elif direction == Direction.EAST:
            start = (center_x - arrow_length / 2, center_y)
            end = (center_x + arrow_length / 2, center_y)
        else:  # WEST
            start = (center_x + arrow_length / 2, center_y)
            end = (center_x - arrow_length / 2, center_y)
            
        return start, end
    
    def _draw_grid_on_plates(self, ax, width: float, length: float,
                           plate_thickness: float, channel_height: float,
                           num_plates: int, grid_resolution: Tuple[int, int]):
        """Tegner grid-linjer på platene for å vise diskretisering."""
        
        width_segments, length_segments = grid_resolution
        
        # Bare vis grid på noen plater for å unngå rot
        plates_to_show = [0, num_plates // 2, num_plates - 1]
        
        for plate_idx in plates_to_show:
            if plate_idx >= num_plates:
                continue
                
            z_pos = plate_idx * (plate_thickness + channel_height) + plate_thickness
            
            # Grid linjer i width-retning
            for i in range(width_segments + 1):
                y_pos = i * width / width_segments
                ax.plot([0, length], [y_pos, y_pos], [z_pos, z_pos], 
                       color='black', alpha=0.3, linewidth=0.5)
            
            # Grid linjer i length-retning
            for j in range(length_segments + 1):
                x_pos = j * length / length_segments
                ax.plot([x_pos, x_pos], [0, width], [z_pos, z_pos], 
                       color='black', alpha=0.3, linewidth=0.5)
    
    def _setup_axes(self, ax, width: float, length: float, height: float,
                   hot_direction: Direction, cold_direction: Direction):
        """Setter opp akser, labels og visning."""
        
        # Sett akser-grenser med litt margin
        margin = 0.1
        ax.set_xlim(-margin * length, length + margin * length)
        ax.set_ylim(-margin * width, width + margin * width)
        ax.set_zlim(-margin * height, height + margin * height)
        
        # Labels
        ax.set_xlabel('Lengde (X) [m]', fontsize=10)
        ax.set_ylabel('Bredde (Y) [m]', fontsize=10)
        ax.set_zlabel('Høyde (Z) [m]', fontsize=10)
        
        # Tittel
        flow_config = self._determine_flow_type(hot_direction, cold_direction)
        ax.set_title(f'PlasticPlateHeatExchanger - {flow_config}\n'
                    f'Dimensjoner: {length:.2f} × {width:.2f} × {height:.3f} m', 
                    fontsize=12, pad=20)
        
        # Legg til legend
        ax.legend(loc='upper left', bbox_to_anchor=(0.02, 0.98))
        
        # Forbedre visningen
        ax.grid(True, alpha=0.3)
        
    def _determine_flow_type(self, hot_direction: Direction, 
                           cold_direction: Direction) -> str:
        """Bestemmer strømningstype for tittel."""
        
        # Sjekk counterflow
        counterflow_pairs = [
            (Direction.NORTH, Direction.SOUTH),
            (Direction.SOUTH, Direction.NORTH),
            (Direction.EAST, Direction.WEST),
            (Direction.WEST, Direction.EAST)
        ]
        
        if (hot_direction, cold_direction) in counterflow_pairs:
            return "Counterflow (Motstrøm)"
        
        # Sjekk parallelflow  
        if hot_direction == cold_direction:
            return "Parallelflow (Medstrøm)"
        
        # Ellers crossflow
        return "Crossflow (Kryssstrøm)"


def visualize_heat_exchanger(geometry, hot_direction: Direction, 
                           cold_direction: Direction, 
                           show_grid: bool = True,
                           grid_resolution: Tuple[int, int] = (5, 5),
                           save_path: Optional[str] = None) -> plt.Figure:
    """
    Konveniensfunksjon for å visualisere en varmeveksler.
    
    Args:
        geometry: PlasticPlateGeometry objekt
        hot_direction: Retning for varm luftstrøm
        cold_direction: Retning for kald luftstrøm  
        show_grid: Om grid skal vises
        grid_resolution: Grid-oppløsning
        save_path: Sti for å lagre bildet (valgfritt)
        
    Returns:
        matplotlib Figure objekt
        
    Examples:
        >>> from hxkit.heatexchangers.plastic_plate import PlasticPlateGeometry
        >>> from hxkit.definitions import Direction
        >>> from hxkit.visualization import visualize_heat_exchanger
        >>> 
        >>> geometry = PlasticPlateGeometry(0.5, 1.0, 0.001, 0.005, 20)
        >>> fig = visualize_heat_exchanger(
        ...     geometry, 
        ...     Direction.NORTH, 
        ...     Direction.EAST,
        ...     save_path="my_heat_exchanger.png"
        ... )
        >>> fig.show()
    """
    
    visualizer = HeatExchangerVisualizer()
    fig = visualizer.visualize_plastic_plate_hx(
        geometry, hot_direction, cold_direction, show_grid, grid_resolution)
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Visualisering lagret som: {save_path}")
    
    return fig


# Convenience import for easy access
__all__ = ['HeatExchangerVisualizer', 'visualize_heat_exchanger']