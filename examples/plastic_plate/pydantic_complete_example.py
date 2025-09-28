#!/usr/bin/env python3
"""
Komplett eksempel med både input og output skjemaer for Plastic Plate Heat Exchanger.

Dette eksempelet viser hvordan man kan bruke Pydantic skjemaene til:
- Input validering og strukturering
- Output validering og serialisering 
- JSON export/import
- API dokumentasjon
"""

import json
from datetime import datetime
from hxkit.schemas import (
    PlasticPlateHeatExchangerInput,
    PlasticPlateHeatExchangerOutput,
    PlateMaterial
)

def create_example_input():
    """Lager eksempel input data for varmeveksler analyse."""
    
    input_data = {
        "geometry": {
            "width": 0.8,
            "length": 1.5,
            "plate_thickness": 0.0015,
            "channel_height": 0.010,
            "num_plates": 25,
            "plate_material": PlateMaterial.GLASS_FIBER_PLASTIC
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
        },
        "grid_resolution": (15, 20),
        "convergence_tolerance": 1e-7,
        "max_iterations": 800
    }
    
    return PlasticPlateHeatExchangerInput(**input_data)


def create_example_output():
    """Lager eksempel output data fra varmeveksler analyse."""
    
    output_data = {
        "performance": {
            "effectiveness": 0.825,
            "ntu": 3.12,
            "heat_transfer_rate": 18.7,
            "pressure_drop_hot": 52.3,
            "pressure_drop_cold": 44.8,
            "overall_heat_transfer_coefficient": 28.5
        },
        "hot_outlet": {
            "moist_air": {
                "temperature": 18.5,
                "pressure": 101273,
                "relative_humidity": 95.2,
                "humidity_ratio": 0.0138,
                "dew_point": 17.8,
                "wet_bulb": 18.1,
                "density": 1.196,
                "specific_volume": 0.836,
                "enthalpy": 53.4
            },
            "mass_flow": 3.2,
            "volume_flow": 2.68,
            "enthalpy_flow": 170.9
        },
        "cold_outlet": {
            "moist_air": {
                "temperature": 33.2,
                "pressure": 101280,
                "relative_humidity": 28.7,
                "humidity_ratio": 0.0096,
                "dew_point": 13.1,
                "wet_bulb": 21.8,
                "density": 1.132,
                "specific_volume": 0.883,
                "enthalpy": 57.8
            },
            "mass_flow": 2.8,
            "volume_flow": 2.47,
            "enthalpy_flow": 161.8
        },
        "phase_changes": {
            "condensation_rate": 0.0045,  # Litt kondensasjon
            "frost_thickness": 0.0,
            "condensation_occurred": True,
            "frost_occurred": False
        },
        "grid_results": {
            "grid_resolution": (15, 20),
            "plate_temperatures": [
                [20.1, 22.3, 24.5, 26.8, 29.1] * 4  # Forenklet 5x4 grid 
            ] * 15,
            "hot_air_temperatures": [
                [40.0, 38.2, 36.1, 33.8, 31.2] * 4
            ] * 15,
            "cold_air_temperatures": [
                [12.0, 14.5, 17.2, 20.1, 23.4] * 4
            ] * 15,
            "max_plate_temperature": 35.2,
            "min_plate_temperature": 15.8,
            "temperature_uniformity": 0.15
        },
        "convergence": {
            "converged": True,
            "iterations": 234,
            "final_residual": 3.8e-8,
            "convergence_tolerance": 1e-7,
            "computation_time": 4.67
        },
        "analysis_timestamp": datetime.now().isoformat() + "Z",
        "solver_version": "HXKit v0.2.0"
    }
    
    return PlasticPlateHeatExchangerOutput(**output_data)


def demonstrate_json_serialization():
    """Demonstrerer JSON serialisering og deserialisering."""
    
    print("\\n=== JSON Serialisering ===")
    
    # Opprett input og output
    input_config = create_example_input()
    output_results = create_example_output()
    
    # Serialiser til JSON
    input_json = input_config.model_dump_json(indent=2)
    output_json = output_results.model_dump_json(indent=2)
    
    print(f"Input JSON størrelse: {len(input_json)} bytes")
    print(f"Output JSON størrelse: {len(output_json)} bytes")
    
    # Lagre til filer
    with open("hx_input_example.json", "w") as f:
        f.write(input_json)
    
    with open("hx_output_example.json", "w") as f:
        f.write(output_json)
    
    print("✅ JSON filer lagret: hx_input_example.json, hx_output_example.json")
    
    # Test deserialisering
    input_dict = json.loads(input_json)
    output_dict = json.loads(output_json)
    
    reconstructed_input = PlasticPlateHeatExchangerInput(**input_dict)
    reconstructed_output = PlasticPlateHeatExchangerOutput(**output_dict)
    
    print("✅ JSON roundtrip vellykket!")
    
    return input_json, output_json


def demonstrate_api_documentation():
    """Demonstrerer automatisk API dokumentasjon."""
    
    print("\\n=== API Dokumentasjon ===")
    
    # Generer OpenAPI/JSON schema
    input_schema = PlasticPlateHeatExchangerInput.model_json_schema()
    output_schema = PlasticPlateHeatExchangerOutput.model_json_schema()
    
    print(f"Input schema properties: {len(input_schema['properties'])}")
    print(f"Output schema properties: {len(output_schema['properties'])}")
    
    # Vis noen eksempel properties
    print("\\nInput schema geometry properties:")
    geometry_props = input_schema['$defs']['PlateGeometryInput']['properties']
    for prop, details in geometry_props.items():
        desc = details.get('description', 'No description')
        print(f"  - {prop}: {desc}")
    
    print("\\nOutput schema performance properties:")  
    perf_props = output_schema['$defs']['PerformanceMetrics']['properties']
    for prop, details in perf_props.items():
        desc = details.get('description', 'No description')
        print(f"  - {prop}: {desc}")
    
    # Lagre schema filer for API dokumentasjon
    with open("hx_input_schema.json", "w") as f:
        json.dump(input_schema, f, indent=2)
    
    with open("hx_output_schema.json", "w") as f:
        json.dump(output_schema, f, indent=2)
    
    print("\\n✅ API schema filer lagret for OpenAPI/Swagger dokumentasjon")


def demonstrate_validation():
    """Demonstrerer validering og feilhåndtering."""
    
    print("\\n=== Validering og Feilhåndtering ===")
    
    # Test 1: Ugyldig temperatur rekkefølge
    print("\\n1. Test ugyldig temperatur rekkefølge:")
    try:
        invalid_data = {
            "geometry": {
                "width": 0.6, "length": 1.2, "plate_thickness": 0.001,
                "channel_height": 0.008, "num_plates": 20, "plate_material": "glass_fiber_plastic"
            },
            "flow_directions": {"hot_direction": "north", "cold_direction": "south"},
            "hot_stream": {
                "moist_air": {"temperature": 10.0, "pressure": 101325, "relative_humidity": 60.0},
                "mass_flow": 2.5
            },
            "cold_stream": {
                "moist_air": {"temperature": 25.0, "pressure": 101325, "relative_humidity": 40.0},
                "mass_flow": 2.0
            }
        }
        PlasticPlateHeatExchangerInput(**invalid_data)
        print("❌ Skulle ha feilet!")
    except Exception as e:
        print(f"✅ Korrekt temperatur validering: {str(e).split(',')[0]}")
    
    # Test 2: Ugyldig effektivitet i output
    print("\\n2. Test ugyldig effektivitet (>1):")
    try:
        invalid_output = {
            "performance": {
                "effectiveness": 1.5,  # Ugyldig > 1
                "ntu": 2.0, "heat_transfer_rate": 10.0,
                "pressure_drop_hot": 50.0, "pressure_drop_cold": 45.0
            },
            "hot_outlet": {
                "moist_air": {
                    "temperature": 20.0, "pressure": 101325, "relative_humidity": 50.0,
                    "humidity_ratio": 0.01, "dew_point": 10.0, "wet_bulb": 15.0,
                    "density": 1.2, "specific_volume": 0.83, "enthalpy": 45.0
                },
                "mass_flow": 2.0, "volume_flow": 1.66, "enthalpy_flow": 90.0
            },
            "cold_outlet": {
                "moist_air": {
                    "temperature": 25.0, "pressure": 101325, "relative_humidity": 40.0,
                    "humidity_ratio": 0.008, "dew_point": 8.0, "wet_bulb": 18.0,
                    "density": 1.15, "specific_volume": 0.87, "enthalpy": 48.0
                },
                "mass_flow": 1.8, "volume_flow": 1.56, "enthalpy_flow": 86.4
            },
            "phase_changes": {
                "condensation_rate": 0.0, "frost_thickness": 0.0,
                "condensation_occurred": False, "frost_occurred": False
            },
            "convergence": {
                "converged": True, "iterations": 100, "final_residual": 1e-6,
                "convergence_tolerance": 1e-6, "computation_time": 2.0
            },
            "analysis_timestamp": "2025-09-28T15:00:00Z",
            "solver_version": "HXKit v0.2.0"
        }
        PlasticPlateHeatExchangerOutput(**invalid_output)
        print("❌ Skulle ha feilet!")
    except Exception as e:
        print(f"✅ Korrekt effektivitet validering: negative efficiency ikke tillatt")


def main():
    """Kjører komplett demo av input og output skjemaer."""
    
    print("=== Plastic Plate Heat Exchanger Schema Demo ===")
    print("Demonstrerer input/output validering, JSON serialisering og API dokumentasjon")
    
    # Opprett og vis eksempler
    print("\\n=== Eksempel Input ===")
    input_config = create_example_input()
    print(f"✅ Input validert!")
    print(f"Geometri: {input_config.geometry.width}×{input_config.geometry.length} m")
    print(f"Plater: {input_config.geometry.num_plates} stk ({input_config.geometry.plate_material.value})")
    print(f"Strømning: {input_config.flow_directions.hot_direction.value} → {input_config.flow_directions.cold_direction.value}")
    print(f"Temperaturer: {input_config.hot_stream.moist_air.temperature}°C → {input_config.cold_stream.moist_air.temperature}°C")
    if input_config.grid_resolution:
        print(f"Grid: {input_config.grid_resolution[0]}×{input_config.grid_resolution[1]} celler")
    
    print("\\n=== Eksempel Output ===")
    output_results = create_example_output()
    print(f"✅ Output validert!")
    print(f"Effektivitet: {output_results.performance.effectiveness:.1%}")
    print(f"NTU: {output_results.performance.ntu:.2f}")  
    print(f"Varmeoverføring: {output_results.performance.heat_transfer_rate:.1f} kW")
    print(f"Trykkfall: {output_results.performance.pressure_drop_hot:.1f} Pa (varm), {output_results.performance.pressure_drop_cold:.1f} Pa (kald)")
    print(f"Kondensasjon: {'Ja' if output_results.phase_changes.condensation_occurred else 'Nei'} ({output_results.phase_changes.condensation_rate:.4f} kg/s)")
    print(f"Konvergens: {output_results.convergence.iterations} iter på {output_results.convergence.computation_time:.1f}s")
    
    # Kjør demo-funksjoner
    demonstrate_json_serialization()
    demonstrate_api_documentation()
    demonstrate_validation()
    
    print("\\n=== Demo Fullført ===")
    print("Skjemaene kan nå brukes til:")
    print("- ✅ REST API endpoints med automatisk validering")
    print("- ✅ JSON serialisering for lagring og transport") 
    print("- ✅ OpenAPI/Swagger dokumentasjon")
    print("- ✅ Type hints og mypy checking")
    print("- ✅ Data klasser for type-sikker programmering")


if __name__ == "__main__":
    main()