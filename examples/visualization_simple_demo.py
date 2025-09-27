#!/usr/bin/env python3
"""
Enkel demo av varmeveksler-visualisering.

Viser hvordan man kan visualisere en PlasticPlateHeatExchanger 
med både matplotlib (statisk) og plotly (interaktiv).
"""

from hxkit import Direction
from hxkit.heatexchangers.plastic_plate import PlasticPlateGeometry

def demo_visualization():
    print("=== Varmeveksler 3D Visualisering Demo ===\n")
    
    # Opprett en eksempel-geometri
    geometry = PlasticPlateGeometry(
        width=0.8,           # 80 cm bredde
        length=1.5,          # 150 cm lengde
        plate_thickness=0.0015,  # 1.5 mm tykkelse
        channel_height=0.010,    # 10 mm kanalhøyde
        num_plates=25        # 25 plater
    )
    
    print(f"Geometri:")
    print(f"  Dimensjoner: {geometry.length:.1f} × {geometry.width:.1f} m")  
    print(f"  Plater: {geometry.num_plates} stk")
    print(f"  Platetykkelse: {geometry.plate_thickness*1000:.1f} mm")
    print(f"  Kanalhøyde: {geometry.channel_height*1000:.1f} mm")
    
    total_height = geometry.num_plates * (geometry.plate_thickness + geometry.channel_height)
    print(f"  Total høyde: {total_height*1000:.1f} mm\n")
    
    # Test matplotlib visualisering (hvis tilgjengelig)
    print("--- Matplotlib Visualisering ---")
    try:
        from hxkit.visualization import visualize_heat_exchanger
        
        print("Oppretter crossflow visualisering med matplotlib...")
        fig = visualize_heat_exchanger(
            geometry=geometry,
            hot_direction=Direction.NORTH,
            cold_direction=Direction.EAST, 
            show_grid=True,
            grid_resolution=(4, 6),
            save_path="crossflow_hx_demo.png"
        )
        
        print("✅ Matplotlib visualisering opprettet og lagret!")
        
        # Vis figuren hvis mulig
        try:
            import matplotlib.pyplot as plt
            plt.show(block=False)
            print("Figur vist i matplotlib vindu.")
            input("Trykk Enter for å fortsette...")
            plt.close(fig)
        except:
            print("Kunne ikke vise figur, men den er lagret som PNG.")
            
    except ImportError as e:
        print(f"⚠️  Matplotlib ikke tilgjengelig: {e}")
        print("   Installer med: pip install matplotlib")
    except Exception as e:
        print(f"❌ Feil ved matplotlib visualisering: {e}")
    
    print()
    
    # Test Plotly visualisering (hvis tilgjengelig)
    print("--- Plotly Interaktiv Visualisering ---")
    try:
        from hxkit.visualization import create_interactive_visualization
        
        print("Oppretter interaktiv counterflow visualisering med plotly...")
        fig = create_interactive_visualization(
            geometry=geometry,
            hot_direction=Direction.NORTH,
            cold_direction=Direction.SOUTH,
            save_html="counterflow_hx_demo.html"
        )
        
        print("✅ Plotly visualisering opprettet og lagret!")
        
        # Vis figuren hvis mulig
        try:
            fig.show()
            print("Interaktiv figur åpnet i nettleser.")
        except:
            print("Kunne ikke åpne nettleser automatisk, men HTML-fil er lagret.")
            
    except ImportError as e:
        print(f"⚠️  Plotly ikke tilgjengelig: {e}")
        print("   Installer med: pip install plotly")
    except Exception as e:
        print(f"❌ Feil ved plotly visualisering: {e}")
    
    print("\n--- Installasjonsinstruksjoner ---")
    print("For å bruke visualiseringsfunksjonene:")
    print("  pip install matplotlib        # For statiske 3D-bilder")
    print("  pip install plotly           # For interaktive 3D-modeller")
    print("  pip install matplotlib plotly # For begge")
    
    print("\n--- Brukseksempler ---")
    print("Etter installasjon kan du bruke:")
    print("""
# Matplotlib (statisk)
from hxkit.visualization import visualize_heat_exchanger
fig = visualize_heat_exchanger(geometry, Direction.NORTH, Direction.EAST)
fig.savefig("my_hx.png", dpi=300)

# Plotly (interaktiv) 
from hxkit.visualization import create_interactive_visualization
fig = create_interactive_visualization(geometry, Direction.NORTH, Direction.SOUTH)
fig.write_html("my_hx.html")
fig.show()
""")
    
    print("=== Demo fullført ===")


if __name__ == "__main__":
    demo_visualization()