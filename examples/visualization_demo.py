#!/usr/bin/env python3
"""
Demo av 3D visualisering for PlasticPlateHeatExchanger.

Viser varmeveksleren i 3D med plater, kanaler, strømningsretninger og grid.
"""

from hxkit import PlasticPlateHeatExchanger, Direction
from hxkit.heatexchangers.plastic_plate import PlasticPlateGeometry

try:
    from hxkit.visualization import visualize_heat_exchanger
    matplotlib_available = True
except ImportError:
    print("Matplotlib ikke tilgjengelig. Installer med: pip install matplotlib")
    matplotlib_available = False

def main():
    if not matplotlib_available:
        return
        
    print("=== 3D Visualisering av PlasticPlateHeatExchanger ===\n")
    
    # Opprett geometri
    geometry = PlasticPlateGeometry(
        width=0.6,           # 0.6 m bredde
        length=1.2,          # 1.2 m lengde
        plate_thickness=0.001,  # 1 mm tykkelse
        channel_height=0.008,   # 8 mm kanalhøyde
        num_plates=15        # 15 plater
    )
    
    print(f"Geometri: {geometry.width}×{geometry.length} m")
    print(f"Plater: {geometry.num_plates} stk, {geometry.plate_thickness*1000:.1f} mm tykkelse")
    print(f"Kanaler: {geometry.channel_height*1000:.1f} mm høyde\n")
    
    # Test forskjellige konfigurasjoner
    configurations = [
        ("Counterflow North↔South", Direction.NORTH, Direction.SOUTH),
        ("Crossflow North×East", Direction.NORTH, Direction.EAST),
        ("Parallelflow East→East", Direction.EAST, Direction.EAST),
    ]
    
    for config_name, hot_dir, cold_dir in configurations:
        print(f"Visualiserer: {config_name}")
        
        try:
            # Opprett visualisering
            fig = visualize_heat_exchanger(
                geometry=geometry,
                hot_direction=hot_dir,
                cold_direction=cold_dir,
                show_grid=True,
                grid_resolution=(6, 8),  # 6×8 grid for demonstrasjon
                save_path=f"hx_{config_name.lower().replace(' ', '_').replace('↔', '_').replace('×', '_').replace('→', '_')}.png"
            )
            
            # Vis figuren
            import matplotlib.pyplot as plt
            plt.show(block=False)  # Non-blocking vis
            
            input(f"Trykk Enter for å fortsette til neste konfigurasjon...")
            plt.close(fig)
            
        except Exception as e:
            print(f"Feil ved visualisering: {e}")
    
    print("\n=== Demonstrasjon fullført ===")
    print("Bildene er lagret som PNG-filer i arbeidsmappe.")

if __name__ == "__main__":
    main()