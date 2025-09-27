"""
Interaktiv 3D visualisering med Plotly.

Dette modulet tilbyr interaktiv 3D visualisering av varmevekslere 
med zoom, rotate og hover-funksjonalitet.
"""

try:
    import plotly.graph_objects as go
    import plotly.express as px
    import numpy as np
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from ..definitions import Direction
from typing import Tuple, List, Optional


class InteractiveHeatExchangerVisualizer:
    """
    Interaktiv 3D visualisering med Plotly.
    
    Tilbyr zoom, rotate, hover og eksport til HTML.
    """
    
    def __init__(self):
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly er ikke installert. Installer med: pip install plotly")
            
        self.colors = {
            'hot_plate': '#FF6B6B',
            'cold_plate': '#4ECDC4', 
            'hot_flow': '#FF9F43',
            'cold_flow': '#00D2D3',
        }
    
    def create_interactive_view(self, geometry, hot_direction: Direction,
                               cold_direction: Direction, 
                               show_grid: bool = True) -> go.Figure:
        """
        Opprett interaktiv 3D visualisering.
        
        Args:
            geometry: PlasticPlateGeometry objekt
            hot_direction: Retning for varm luftstrøm
            cold_direction: Retning for kald luftstrøm
            show_grid: Om grid skal vises
            
        Returns:
            Plotly Figure objekt
        """
        
        fig = go.Figure()
        
        # Tegn plater
        self._add_plates_to_figure(fig, geometry)
        
        # Tegn strømningsretninger
        self._add_flow_arrows(fig, geometry, hot_direction, cold_direction)
        
        # Sett opp layout
        self._setup_plotly_layout(fig, geometry, hot_direction, cold_direction)
        
        return fig
    
    def _add_plates_to_figure(self, fig: go.Figure, geometry):
        """Legger til plater som 3D mesh objekter."""
        
        width = geometry.width
        length = geometry.length
        plate_thickness = geometry.plate_thickness
        channel_height = geometry.channel_height
        num_plates = geometry.num_plates
        
        for i in range(num_plates):
            z_pos = i * (plate_thickness + channel_height)
            
            # Velg farge
            if i % 2 == 0:
                color = self.colors['hot_plate']
                name = f'Varm plate {i+1}'
            else:
                color = self.colors['cold_plate']
                name = f'Kald plate {i+1}'
            
            # Opprett plate som mesh
            self._add_plate_mesh(fig, width, length, plate_thickness, 
                               z_pos, color, name)
    
    def _add_plate_mesh(self, fig: go.Figure, width: float, length: float,
                       thickness: float, z_pos: float, color: str, name: str):
        """Legger til en plate som 3D mesh."""
        
        # Definér vertices for en boks
        x = [0, length, length, 0, 0, length, length, 0]
        y = [0, 0, width, width, 0, 0, width, width]
        z = [z_pos, z_pos, z_pos, z_pos, 
             z_pos + thickness, z_pos + thickness, 
             z_pos + thickness, z_pos + thickness]
        
        # Definér triangulær mesh for alle sider av boksen
        i = [0, 0, 0, 0, 4, 4, 2, 2, 1, 1, 3, 3]  # Vertex indices for triangles
        j = [1, 2, 3, 4, 5, 6, 6, 3, 5, 2, 7, 0]
        k = [2, 3, 0, 5, 6, 7, 7, 7, 1, 6, 4, 4]
        
        fig.add_trace(go.Mesh3d(
            x=x, y=y, z=z,
            i=i, j=j, k=k,
            color=color,
            opacity=0.7,
            name=name,
            showlegend=True,
            hovertemplate=f"<b>{name}</b><br>" +
                         f"Posisjon: Z = {z_pos:.3f} m<br>" +
                         f"Tykkelse: {thickness*1000:.1f} mm<extra></extra>"
        ))
    
    def _add_flow_arrows(self, fig: go.Figure, geometry, 
                        hot_direction: Direction, cold_direction: Direction):
        """Legger til strømningspiler."""
        
        width = geometry.width  
        length = geometry.length
        total_height = geometry.num_plates * (geometry.plate_thickness + geometry.channel_height)
        
        arrow_length = min(width, length) * 0.4
        
        # Hot flow arrow
        hot_start, hot_end = self._get_arrow_coordinates(
            hot_direction, width, length, arrow_length)
        
        fig.add_trace(go.Scatter3d(
            x=[hot_start[0], hot_end[0]],
            y=[hot_start[1], hot_end[1]], 
            z=[total_height + 0.05, total_height + 0.05],
            mode='lines+markers',
            line=dict(color=self.colors['hot_flow'], width=8),
            marker=dict(size=[2, 8], symbol=['circle', 'diamond']),
            name=f'Varm luft ({hot_direction.value})',
            hovertemplate=f"<b>Varm luftstrøm</b><br>Retning: {hot_direction.value}<extra></extra>"
        ))
        
        # Cold flow arrow  
        cold_start, cold_end = self._get_arrow_coordinates(
            cold_direction, width, length, arrow_length)
        
        fig.add_trace(go.Scatter3d(
            x=[cold_start[0], cold_end[0]],
            y=[cold_start[1], cold_end[1]],
            z=[-0.05, -0.05],
            mode='lines+markers', 
            line=dict(color=self.colors['cold_flow'], width=8),
            marker=dict(size=[2, 8], symbol=['circle', 'diamond']),
            name=f'Kald luft ({cold_direction.value})',
            hovertemplate=f"<b>Kald luftstrøm</b><br>Retning: {cold_direction.value}<extra></extra>"
        ))
    
    def _get_arrow_coordinates(self, direction: Direction, width: float,
                              length: float, arrow_length: float):
        """Beregner pil-koordinater basert på retning."""
        
        center_x, center_y = length / 2, width / 2
        
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
    
    def _setup_plotly_layout(self, fig: go.Figure, geometry,
                            hot_direction: Direction, cold_direction: Direction):
        """Setter opp plotly layout og styling."""
        
        width = geometry.width
        length = geometry.length  
        total_height = geometry.num_plates * (geometry.plate_thickness + geometry.channel_height)
        
        flow_type = self._determine_flow_type(hot_direction, cold_direction)
        
        fig.update_layout(
            title={
                'text': f'PlasticPlateHeatExchanger - {flow_type}<br>' +
                       f'<sub>Dimensjoner: {length:.2f} × {width:.2f} × {total_height:.3f} m</sub>',
                'x': 0.5,
                'xanchor': 'center'
            },
            scene=dict(
                xaxis_title='Lengde (X) [m]',
                yaxis_title='Bredde (Y) [m]', 
                zaxis_title='Høyde (Z) [m]',
                aspectmode='data',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.0)
                )
            ),
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left", 
                x=0.01
            )
        )
    
    def _determine_flow_type(self, hot_direction: Direction, 
                           cold_direction: Direction) -> str:
        """Bestemmer strømningstype."""
        
        counterflow_pairs = [
            (Direction.NORTH, Direction.SOUTH),
            (Direction.SOUTH, Direction.NORTH),
            (Direction.EAST, Direction.WEST),
            (Direction.WEST, Direction.EAST)
        ]
        
        if (hot_direction, cold_direction) in counterflow_pairs:
            return "Counterflow"
        elif hot_direction == cold_direction:
            return "Parallelflow"
        else:
            return "Crossflow"


def create_interactive_visualization(geometry, hot_direction: Direction,
                                   cold_direction: Direction,
                                   save_html: Optional[str] = None):
    """
    Konveniensfunksjon for interaktiv visualisering.
    
    Args:
        geometry: PlasticPlateGeometry objekt
        hot_direction: Retning for varm luftstrøm
        cold_direction: Retning for kald luftstrøm
        save_html: Filnavn for lagring som HTML (valgfritt)
        
    Returns:
        Plotly Figure objekt
        
    Examples:
        >>> from hxkit.heatexchangers.plastic_plate import PlasticPlateGeometry
        >>> from hxkit.definitions import Direction 
        >>> from hxkit.visualization_plotly import create_interactive_visualization
        >>>
        >>> geometry = PlasticPlateGeometry(0.5, 1.0, 0.001, 0.005, 20)
        >>> fig = create_interactive_visualization(
        ...     geometry, Direction.NORTH, Direction.EAST,
        ...     save_html="interactive_hx.html"
        ... )
        >>> fig.show()
    """
    
    if not PLOTLY_AVAILABLE:
        raise ImportError("Plotly er ikke installert. Installer med: pip install plotly")
    
    visualizer = InteractiveHeatExchangerVisualizer()
    fig = visualizer.create_interactive_view(geometry, hot_direction, cold_direction)
    
    if save_html:
        fig.write_html(save_html)
        print(f"Interaktiv visualisering lagret som: {save_html}")
    
    return fig


__all__ = ['InteractiveHeatExchangerVisualizer', 'create_interactive_visualization']