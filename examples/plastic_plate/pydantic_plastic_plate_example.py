#!/usr/bin/env python3
"""
Eksempel på bruk av Pydantic skjema for Plastic Plate Heat Exchanger.

Dette eksempelet viser hvordan man definerer input data med komplett validering
og bruker det til å konfigurere en varmeveksler-analyse.
"""

from hxkit.schemas import PlasticPlateHeatExchangerInput, PlateMaterial
from hxkit import Direction

def main():
    """Demonstrerer bruk av plastic plate heat exchanger input skjema."""
    
    print("=== Plastic Plate Heat Exchanger Schema Demo ===")
    
    # Eksempel 1: Counterflow konfiguration
    print("\n1. Counterflow konfigurasjon:")
    
    counterflow_data = {
        "geometry": {
            "width": 0.8,
            "length": 1.5, 
            "plate_thickness": 0.0015,
            "channel_height": 0.010,
            "num_plates": 25,
            "plate_material": "glass_fiber_plastic"
        },
        "flow_directions": {
            "hot_direction": "north",
            "cold_direction": "south"
        },
        "hot_stream": {
            "moist_air": {
                "temperature": 40.0,
                "pressure": 101325,
                "relative_humidity": 65.0
            },
            "mass_flow": 3.2
        },
        "cold_stream": {
            "moist_air": {
                "temperature": 12.0,
                "pressure": 101325,
                "relative_humidity": 45.0
            },
            "mass_flow": 2.8
        }
    }
    
    try:
        counterflow_config = PlasticPlateHeatExchangerInput(**counterflow_data)
        print("✅ Counterflow konfiguration validert!")
        print(f"   Geometri: {counterflow_config.geometry.width:.1f} × {counterflow_config.geometry.length:.1f} m")
        print(f"   Plater: {counterflow_config.geometry.num_plates} stk ({counterflow_config.geometry.plate_material.value})")
        print(f"   Strømning: {counterflow_config.flow_directions.hot_direction.value} → {counterflow_config.flow_directions.cold_direction.value}")
        print(f"   Temperaturer: {counterflow_config.hot_stream.moist_air.temperature}°C → {counterflow_config.cold_stream.moist_air.temperature}°C")
        print(f"   Massestrømmer: {counterflow_config.hot_stream.mass_flow} kg/s (varm), {counterflow_config.cold_stream.mass_flow} kg/s (kald)")
    except Exception as e:
        print(f"❌ Feil: {e}")
    
    # Eksempel 2: Crossflow konfiguration  
    print("\n2. Crossflow konfigurasjon:")
    
    crossflow_data = {
        "geometry": {
            "width": 0.6,
            "length": 1.2,
            "plate_thickness": 0.001,
            "channel_height": 0.008,
            "num_plates": 20,
            "plate_material": "polypropylene"
        },
        "flow_directions": {
            "hot_direction": "east",
            "cold_direction": "north"
        },
        "hot_stream": {
            "moist_air": {
                "temperature": 30.0,
                "pressure": 101325,
                "humidity_ratio": 0.012  # Bruker fuktighetsforhold isteden for RH
            },
            "mass_flow": 2.0
        },
        "cold_stream": {
            "moist_air": {
                "temperature": 18.0,
                "pressure": 101325,
                "wet_bulb": 14.0  # Bruker våtkuletemperatur
            },
            "mass_flow": 1.8
        },
        "grid_resolution": (8, 12),
        "convergence_tolerance": 5e-7
    }
    
    try:
        crossflow_config = PlasticPlateHeatExchangerInput(**crossflow_data)
        print("✅ Crossflow konfiguration validert!")
        print(f"   Material: {crossflow_config.geometry.plate_material.value}")
        print(f"   Strømning: {crossflow_config.flow_directions.hot_direction.value} × {crossflow_config.flow_directions.cold_direction.value} (crossflow)")
        if crossflow_config.grid_resolution:
            print(f"   Grid: {crossflow_config.grid_resolution[0]} × {crossflow_config.grid_resolution[1]} celler")
        print(f"   Konvergens: {crossflow_config.convergence_tolerance:.0e}")
    except Exception as e:
        print(f"❌ Feil: {e}")
    
    # Eksempel 3: Feilhåndtering
    print("\n3. Validerings-eksempler:")
    
    # Ugyldig temperatur-rekkefølge
    invalid_temp_data = counterflow_data.copy()
    invalid_temp_data["hot_stream"]["moist_air"]["temperature"] = 10.0
    invalid_temp_data["cold_stream"]["moist_air"]["temperature"] = 25.0
    
    try:
        PlasticPlateHeatExchangerInput(**invalid_temp_data)
    except Exception as e:
        print(f"✅ Temperatur validering fungerer: {str(e).split(',')[0]}")
    
    # Ugyldig grid oppløsning
    invalid_grid_data = counterflow_data.copy() 
    invalid_grid_data["grid_resolution"] = (1, 1)
    
    try:
        PlasticPlateHeatExchangerInput(**invalid_grid_data)
    except Exception as e:
        print(f"✅ Grid validering fungerer: {str(e).split(',')[0]}")
    
    # Negativ massestrøm
    invalid_mass_data = counterflow_data.copy()
    invalid_mass_data["hot_stream"]["mass_flow"] = -1.0
    
    try:
        PlasticPlateHeatExchangerInput(**invalid_mass_data)
    except Exception as e:
        print(f"✅ Massestrøm validering fungerer: negative verdier ikke tillatt")
    
    print("\n=== Demo fullført ===")
    print("\nSkjemaet kan nå brukes til:")
    print("- Input validering for API endpoints")
    print("- JSON serialisering/deserialisering") 
    print("- Automatisk dokumentasjon (OpenAPI/Swagger)")
    print("- Type checking med mypy")


if __name__ == "__main__":
    main()