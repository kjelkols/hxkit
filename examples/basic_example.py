"""
Eksempel på bruk av HXKit for platevarmeveksleranalyse.

Dette eksemplet viser hvordan du kan bruke biblioteket til å:
1. Definere geometri
2. Sette opp lufttilstander  
3. Utføre varmeveksleranalyse
4. Generere performance map
"""

import hxkit
from hxkit import MoistAir, PlateGeometry, PlateHeatExchanger, HeatExchangerCore
from hxkit.geometries import GeometryFactory
import numpy as np


def main():
    print("HXKit Platevarmeveksler Eksempel")
    print("=" * 40)
    
    # 1. Lag plategeometri
    print("\n1. Definerer plategeometri...")
    plate_geom = GeometryFactory.standard_plate("medium")
    print(f"   Platedimensjoner: {plate_geom.length:.2f} x {plate_geom.width:.2f} m")
    print(f"   Kanalhøyde: {plate_geom.channel_height*1000:.1f} mm")
    print(f"   Hydraulisk diameter: {plate_geom.hydraulic_diameter*1000:.2f} mm")
    
    # 2. Lag varmevekslerkjerne
    n_plates = 21  # 20 kanaler (10 varme, 10 kalde)
    hot_channels = 10
    cold_channels = 10
    
    core = HeatExchangerCore(n_plates, plate_geom, hot_channels, cold_channels)
    print(f"\n2. Varmevekslerkjerne:")
    print(f"   Antall plater: {core.n_plates}")
    print(f"   Kanalkonfigurasjon: {core.channel_configuration()}")
    print(f"   Totalt varmeoverføringsareal: {core.total_heat_transfer_area:.2f} m²")
    
    # 3. Definer lufttilstander
    print(f"\n3. Definerer lufttilstander...")
    
    # Varm innløpsluft (fra hus)
    hot_inlet = MoistAir(temperature=22.0, relative_humidity=40.0)
    print(f"   Varm innløp: {hot_inlet.temperature:.1f}°C, RH={hot_inlet.relative_humidity:.1f}%")
    print(f"   Entalpi: {hot_inlet.enthalpy:.1f} kJ/kg")
    
    # Kald innløpsluft (uteluft)
    cold_inlet = MoistAir(temperature=-10.0, relative_humidity=80.0)
    print(f"   Kald innløp: {cold_inlet.temperature:.1f}°C, RH={cold_inlet.relative_humidity:.1f}%")
    print(f"   Entalpi: {cold_inlet.enthalpy:.1f} kJ/kg")
    
    # 4. Definer massestrømmer
    hot_mass_flow = 0.1  # kg/s
    cold_mass_flow = 0.1  # kg/s
    print(f"\n4. Massestrømmer:")
    print(f"   Varm side: {hot_mass_flow:.2f} kg/s")
    print(f"   Kald side: {cold_mass_flow:.2f} kg/s")
    
    # 5. Utfør varmeveksleranalyse
    print(f"\n5. Utfører varmeveksleranalyse...")
    hx = PlateHeatExchanger(core)
    results = hx.analyze(hot_inlet, cold_inlet, hot_mass_flow, cold_mass_flow)
    
    # 6. Vis resultater
    print(f"\n6. Resultater:")
    print(f"   Varmeoverføringsrate: {results['heat_transfer_rate']/1000:.2f} kW")
    print(f"   Effectiveness: {results['effectiveness']:.3f}")
    print(f"   NTU: {results['ntu']:.2f}")
    print(f"   Overall U-verdi: {results['u_overall']:.1f} W/m²K")
    
    print(f"\n   Utløpstemperaturer:")
    print(f"   Varm utløp: {results['hot_outlet'].temperature:.1f}°C")
    print(f"   Kald utløp: {results['cold_outlet'].temperature:.1f}°C")
    
    print(f"\n   Trykkfall:")
    print(f"   Varm side: {results['hot_pressure_drop']:.0f} Pa")
    print(f"   Kald side: {results['cold_pressure_drop']:.0f} Pa")
    
    print(f"\n   Hastigheter:")
    print(f"   Varm side: {results['hot_velocity']:.2f} m/s")
    print(f"   Kald side: {results['cold_velocity']:.2f} m/s")
    
    # 7. Temperatureffektivitet
    temp_effectiveness = (results['cold_outlet'].temperature - cold_inlet.temperature) / \
                        (hot_inlet.temperature - cold_inlet.temperature)
    print(f"\n   Temperatureffektivitet: {temp_effectiveness:.3f}")
    
    # 8. Performance map
    print(f"\n7. Genererer performance map...")
    perf_map = hx.performance_map(hot_inlet, cold_inlet, (0.05, 0.2), n_points=10)
    
    print(f"   Performance map generert for massestrømmer {perf_map['mass_flows'][0]:.3f} - {perf_map['mass_flows'][-1]:.3f} kg/s")
    print(f"   Maksimal varmeoverføring: {np.max(perf_map['heat_transfer_rates'])/1000:.2f} kW")
    print(f"   Maksimal effectiveness: {np.max(perf_map['effectiveness']):.3f}")
    
    # 9. Optimalisering
    print(f"\n8. Optimaliserer for 80% effectiveness...")
    try:
        optimal_core = hx.optimize_geometry(hot_inlet, cold_inlet, 
                                          hot_mass_flow, cold_mass_flow, 
                                          target_effectiveness=0.8)
        print(f"   Optimalt antall plater: {optimal_core.n_plates}")
        print(f"   Optimal konfigurasjon: {optimal_core.channel_configuration()}")
    except Exception as e:
        print(f"   Optimalisering ikke mulig med nåværende parametere")
    
    print(f"\n9. Eksempel fullført!")


if __name__ == "__main__":
    main()
