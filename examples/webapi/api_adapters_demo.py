"""
Praktisk eksempel på hvordan du bruker API Adapters

Dette eksemplet viser forskjellige bruksscenarier for adapters:
1. Web API simulering
2. Konfigurasjonsfil håndtering  
3. Batch prosessering
4. Feilhåndtering og validering
"""

import json
from hxkit.api import ThermodynamicsAdapter, GeometryAdapter, AnalysisAdapter
from hxkit.schemas import AnalysisInput


def demo_web_api_simulation():
    """Simulerer hvordan en web-API ville brukt adapters"""
    print("=== Web API Simulering ===")
    
    # Simuler JSON data fra en web-request
    api_request = {
        "conditions": {
            "hot_side": {
                "temperature": 25.0,
                "pressure": 101325,
                "relative_humidity": 50.0
            },
            "cold_side": {
                "temperature": 5.0,
                "pressure": 101325,
                "relative_humidity": 90.0
            }
        },
        "flow": {
            "hot_mass_flow": 0.15,
            "cold_mass_flow": 0.12
        },
        "core": {
            "geometry": {
                "plate_width": 0.8,
                "plate_height": 0.3,
                "plate_spacing": 0.005,
                "chevron_angle": 35.0
            },
            "num_plates": 25
        }
    }
    
    print(f"📥 API Request received: {len(json.dumps(api_request))} bytes")
    
    # Konverter til JSON string (som en ekte web-request)
    json_request = json.dumps(api_request)
    
    # Bruk adapter til å prosessere hele requesten
    try:
        json_response = AnalysisAdapter.analyze_from_json(json_request)
        print(f"📤 API Response generated: {len(json_response)} bytes")
        
        # Parse response for å vise resultater
        response_data = json.loads(json_response)
        print(f"✅ Heat Transfer: {response_data['heat_transfer_rate']:.1f} W")
        print(f"✅ Effectiveness: {response_data['effectiveness']:.3f}")
        
    except Exception as e:
        print(f"❌ API Error: {e}")


def demo_configuration_file():
    """Viser hvordan adapters kan brukes med konfigurasjonsfiler"""
    print("\n=== Konfigurasjonsfil Håndtering ===")
    
    # Simuler en konfigurasjonsfil (JSON/YAML format)
    config_file_content = {
        "default_conditions": {
            "hot_side": {
                "temperature": 22.0,
                "relative_humidity": 40.0
            },
            "cold_side": {
                "temperature": -5.0,
                "relative_humidity": 85.0
            }
        },
        "standard_geometry": {
            "plate_width": 0.6,
            "plate_height": 0.2,
            "plate_spacing": 0.004,
            "chevron_angle": 30.0,
            "num_plates": 21
        }
    }
    
    print("📁 Laster konfigurasjon...")
    
    # Bruk individuell adapters for fleksibilitet
    try:
        from hxkit.schemas import MoistAirInput, PlateGeometryInput
        
        # Last hot side konfigurasjon
        hot_schema = MoistAirInput(
            temperature=config_file_content["default_conditions"]["hot_side"]["temperature"],
            pressure=101325,  # Default verdi
            relative_humidity=config_file_content["default_conditions"]["hot_side"]["relative_humidity"]
        )
        
        hot_air = ThermodynamicsAdapter.from_schema(hot_schema)
        print(f"🔥 Hot air loaded: {hot_air.temperature}°C, {hot_air.enthalpy:.1f} kJ/kg")
        
        # Last geometri konfigurasjon
        geom_config = config_file_content["standard_geometry"]
        geom_schema = PlateGeometryInput(**geom_config)
        plate_geom = GeometryAdapter.plate_from_schema(geom_schema)
        
        print(f"📐 Geometry loaded: {plate_geom.length}x{plate_geom.width}m plates")
        
    except Exception as e:
        print(f"❌ Config Error: {e}")


def demo_batch_processing():
    """Viser hvordan adapters kan brukes for batch prosessering"""
    print("\n=== Batch Prosessering ===")
    
    # Simuler flere analyse cases
    batch_cases = [
        {
            "name": "Summer Operation",
            "hot_temp": 35.0,
            "cold_temp": 15.0,
            "flow_ratio": 1.0
        },
        {
            "name": "Winter Operation", 
            "hot_temp": 20.0,
            "cold_temp": -15.0,
            "flow_ratio": 0.8
        },
        {
            "name": "Part Load",
            "hot_temp": 25.0,
            "cold_temp": 5.0,
            "flow_ratio": 0.5
        }
    ]
    
    print(f"🔄 Prosesserer {len(batch_cases)} cases...")
    
    base_geometry = {
        "plate_width": 0.6,
        "plate_height": 0.2, 
        "plate_spacing": 0.004,
        "chevron_angle": 30.0
    }
    
    results = []
    
    for case in batch_cases:
        try:
            # Bygg analyse input for denne casen
            analysis_input = AnalysisInput(
                conditions={
                    "hot_side": {
                        "temperature": case["hot_temp"],
                        "pressure": 101325,
                        "relative_humidity": 40.0
                    },
                    "cold_side": {
                        "temperature": case["cold_temp"], 
                        "pressure": 101325,
                        "relative_humidity": 80.0
                    }
                },
                flow={
                    "hot_mass_flow": 0.1 * case["flow_ratio"],
                    "cold_mass_flow": 0.1 * case["flow_ratio"]
                },
                core={
                    "geometry": base_geometry,
                    "num_plates": 21
                }
            )
            
            # Utfør analyse med adapter
            output = AnalysisAdapter.analyze_from_schema(analysis_input)
            
            results.append({
                "case": case["name"],
                "heat_transfer": output.heat_transfer_rate,
                "effectiveness": output.effectiveness
            })
            
            print(f"✅ {case['name']}: {output.heat_transfer_rate:.0f}W, ε={output.effectiveness:.3f}")
            
        except Exception as e:
            print(f"❌ {case['name']}: {e}")
    
    # Sammendrag
    if results:
        avg_effectiveness = sum(r["effectiveness"] for r in results) / len(results)
        print(f"📊 Gjennomsnittlig effectiveness: {avg_effectiveness:.3f}")


def demo_error_handling():
    """Viser hvordan adapters håndterer valideringsfeil"""
    print("\n=== Feilhåndtering og Validering ===")
    
    # Test cases med feil
    error_cases = [
        {
            "name": "Invalid Temperature",
            "data": {"temperature": 150, "relative_humidity": 50},  # Over 100°C
            "expected": "Temperature validation error"
        },
        {
            "name": "Invalid Humidity", 
            "data": {"temperature": 25, "relative_humidity": 150},  # Over 100%
            "expected": "Humidity validation error"
        },
        {
            "name": "Missing Data",
            "data": {"temperature": 25},  # Mangler fuktighetsinput
            "expected": "Missing humidity validation error"
        }
    ]
    
    for case in error_cases:
        print(f"\n🧪 Testing: {case['name']}")
        try:
            from hxkit.schemas import MoistAirInput
            
            # Prøv å lage schema med ugyldig data
            schema = MoistAirInput(pressure=101325, **case["data"])
            air = ThermodynamicsAdapter.from_schema(schema)
            
            print(f"❌ Should have failed: {case['name']}")
            
        except Exception as e:
            print(f"✅ Caught expected error: {str(e)[:60]}...")


def main():
    """Hovedfunksjon som kjører alle demonstrasjonene"""
    print("HXKit API Adapters - Praktisk Demonstrasjon")
    print("=" * 50)
    
    demo_web_api_simulation()
    demo_configuration_file()
    demo_batch_processing()
    demo_error_handling()
    
    print("\n" + "=" * 50)
    print("🎯 Hovedfordelene med API Adapters:")
    print("   • Automatisk datavalidering med Pydantic")
    print("   • JSON serialisering/deserialisering")
    print("   • Separasjon av API-logikk og kjerneberegninger")
    print("   • Enkelt å bygge web-APIer og konfigurasjonsverktøy")
    print("   • Type-sikkerhet og bedre feilhåndtering")


if __name__ == "__main__":
    main()