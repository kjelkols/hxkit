#!/usr/bin/env python3
"""
Demo av PlasticPlateHeatExchanger med automatisk grid-optimalisering.

Viser hvordan 2D-grid automatisk optimaliseres til 1D for counterflow/parallelflow,
mens det forblir 2D for crossflow.
"""

from hxkit import PlasticPlateHeatExchanger, MoistAir, AirStream, Direction

def main():
    print("=== PlasticPlateHeatExchanger Grid-Optimalisering Demo ===\n")
    
    # Opprett varmeveksler
    hx = PlasticPlateHeatExchanger(
        width=0.5,           # 0.5 m bredde
        length=1.0,          # 1.0 m lengde  
        plate_thickness=0.001,  # 1 mm tykkelse
        channel_height=0.005,   # 5 mm kanalhøyde
        num_plates=50,       # 50 plater
        grid_resolution=(10, 10)  # 10x10 grid som default
    )
    
    print(f"Varmeveksler: {hx.geometry.width}×{hx.geometry.length} m, {hx.geometry.num_plates} plater")
    print(f"Default grid-oppløsning: {hx.grid_resolution}\n")
    
    # Definer lufttilstander
    hot_air = MoistAir(temperature=25.0, relative_humidity=60.0)
    cold_air = MoistAir(temperature=-5.0, relative_humidity=80.0)
    
    print("Lufttilstander:")
    print(f"  Varm luft: {hot_air.temperature}°C, {hot_air.relative_humidity:.1f}% RH")
    print(f"  Kald luft: {cold_air.temperature}°C, {cold_air.relative_humidity:.1f}% RH\n")
    
    # Test forskjellige strømningskonfigurasjoner
    configurations = [
        ("Counterflow (North↔South)", Direction.NORTH, Direction.SOUTH),
        ("Counterflow (East↔West)", Direction.EAST, Direction.WEST),
        ("Parallelflow (North→North)", Direction.NORTH, Direction.NORTH), 
        ("Crossflow (North×East)", Direction.NORTH, Direction.EAST),
    ]
    
    for config_name, hot_dir, cold_dir in configurations:
        print(f"--- {config_name} ---")
        
        # Opprett strømmer
        hot_stream = AirStream(hot_air, mass_flow=1.2, direction=hot_dir)
        cold_stream = AirStream(cold_air, mass_flow=1.0, direction=cold_dir)
        
        print(f"Strømningsretninger: Varm({hot_dir.value}) vs Kald({cold_dir.value})")
        
        # Analyser (dette trigger grid-optimalisering)
        results = hx.analyze(hot_stream, cold_stream)
        
        # Vis grid-informasjon
        grid = hx.grid
        grid_type = "1D" if (grid.width_segments == 1 or grid.length_segments == 1) else "2D"
        print(f"Optimalisert grid: {grid_type} ({grid.width_segments}×{grid.length_segments})")
        
        # Vis resultater
        print(f"Resultater:")
        print(f"  Virkningsgrad: {results.effectiveness:.1%}")
        print(f"  Varmeoverføring: {results.heat_transfer_rate:.1f} kW")
        print(f"  Utløpstemperaturer: {results.hot_outlet_state.temperature:.1f}°C / {results.cold_outlet_state.temperature:.1f}°C")
        print(f"  Temperaturfeld form: {results.plate_temperature_field.shape}")
        print()

if __name__ == "__main__":
    main()