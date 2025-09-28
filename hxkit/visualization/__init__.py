"""
Visualization modules for HXKit.

This package contains different visualization implementations:
- matplotlib_viz: Static 3D visualization with matplotlib
- plotly_viz: Interactive 3D visualization with plotly
"""

# Try to import matplotlib visualization
try:
    from .matplotlib_viz import visualize_heat_exchanger, HeatExchangerVisualizer
    _MATPLOTLIB_AVAILABLE = True
except ImportError:
    _MATPLOTLIB_AVAILABLE = False

# Try to import plotly visualization  
try:
    from .plotly_viz import create_interactive_visualization, InteractiveHeatExchangerVisualizer
    _PLOTLY_AVAILABLE = True
except ImportError:
    _PLOTLY_AVAILABLE = False

# Plastic Plate HTML report generator (always available)
try:
    from .plastic_plate_html_report import generate_html_report, save_html_report
    _HTML_REPORT_AVAILABLE = True
except ImportError:
    _HTML_REPORT_AVAILABLE = False

__all__ = []

# Add matplotlib functions if available
if _MATPLOTLIB_AVAILABLE:
    __all__.extend(['visualize_heat_exchanger', 'HeatExchangerVisualizer'])

# Add plotly functions if available
if _PLOTLY_AVAILABLE:
    __all__.extend(['create_interactive_visualization', 'InteractiveHeatExchangerVisualizer'])

# Add HTML report functions if available
if _HTML_REPORT_AVAILABLE:
    __all__.extend(['generate_html_report', 'save_html_report'])

# Convenience function to check availability
def get_available_backends():
    """
    Returns a dictionary of available visualization backends.
    
    Returns:
        dict: Available backends with boolean values
        
    Example:
        >>> from hxkit.visualization import get_available_backends
        >>> backends = get_available_backends()
        >>> print(f"Matplotlib: {backends['matplotlib']}")
        >>> print(f"Plotly: {backends['plotly']}")
    """
    return {
        'matplotlib': _MATPLOTLIB_AVAILABLE,
        'plotly': _PLOTLY_AVAILABLE,
        'html_report': _HTML_REPORT_AVAILABLE
    }

# Add convenience function to __all__
__all__.append('get_available_backends')