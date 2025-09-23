"""
Eksempel på bruk av Pydantic schemas for input/output validering.

Dette eksemplet viser hvordan du kan bruke Pydantic modellene for:
1. Strukturert input validering
2. API-kompatibel output
3. JSON serialisering/deserialisering
4. Konfigurasjonshåndtering
"""

import json
from hxkit.schemas import (
    MoistAirInput, PsychrometricConditions, FlowConditions,
    PlateGeometryInput, HeatExchangerCoreInput, 
    AnalysisInput, AnalysisOutput
)
from hxkit.api import ThermodynamicsAdapter, GeometryAdapter, AnalysisAdapter


def main():
    print("HXKit Pydantic Schema Eksempel")
    print("=" * 40)
    
    # 1. Definer input data som dictionaries (som fra JSON API)
    print("\n1. Definerer input data som JSON-kompatible dictionaries...")
    
    input_data = {
        "conditions": {
            "hot_side": {
                "temperature": 22.0,
                "pressure": 101325,
                "relative_humidity": 40.0
            },
            "cold_side": {
                "temperature": -10.0,
                "pressure": 101325,
                "relative_humidity": 80.0
            }
        },
        "flow": {
            "hot_mass_flow": 0.1,
            "cold_mass_flow": 0.1
        },
        "geometry": {
            "n_plates": 21,
            "plate_geometry": {
                "length": 0.6,
                "width": 0.2,
                "thickness": 0.0005,
                "channel_height": 0.004,
                "corrugation_angle": 60,
                "area_enhancement": 1.2
            },
            "hot_channels": 10,
            "cold_channels": 10
        }
    }
    
    # 2. Valider input med Pydantic
    print("\n2. Validerer input data med Pydantic schemas...")
    try:
        analysis_input = AnalysisInput(**input_data)
        print("   ✓ Input data validert OK")
        print(f"   Varm innløp: {analysis_input.conditions.hot_side.temperature}°C")
        print(f"   Kald innløp: {analysis_input.conditions.cold_side.temperature}°C")
        print(f"   Antall plater: {analysis_input.geometry.n_plates}")
    except Exception as e:
        print(f"   ✗ Valideringsfeil: {e}")
        return
    
    # 3. Konverter til kjerneobjekter og utfør analyse
    print("\n3. Utfører analyse med adaptere...")
    try:
        results = AnalysisAdapter.analyze_from_schema(analysis_input)
        print("   ✓ Analyse fullført")
        print(f"   Varmeoverføring: {results['heat_transfer_rate']/1000:.2f} kW")
        print(f"   Effectiveness: {results['effectiveness']:.3f}")
    except Exception as e:
        print(f"   ✗ Analysefeil: {e}")
        return
    
    # 4. Konverter resultater til Pydantic schema
    print("\n4. Konverterer resultater til strukturert output...")
    try:
        # Legg til manglende felter for adapter
        results["hot_inlet_temp"] = analysis_input.conditions.hot_side.temperature
        results["cold_inlet_temp"] = analysis_input.conditions.cold_side.temperature
        
        output_schema = AnalysisAdapter.results_to_schema(results)
        print("   ✓ Output schema opprettet")
        print(f"   Varm utløp: {output_schema.hot_outlet.temperature:.1f}°C")
        print(f"   Kald utløp: {output_schema.cold_outlet.temperature:.1f}°C")
    except Exception as e:
        print(f"   ✗ Output konverteringsfeil: {e}")
        return
    
    # 5. Serialiser til JSON
    print("\n5. Serialiserer til JSON...")
    try:
        # Input til JSON
        input_json = analysis_input.model_dump_json(indent=2)
        print("   ✓ Input serialisert til JSON")
        
        # Output til JSON  
        output_json = output_schema.model_dump_json(indent=2)
        print("   ✓ Output serialisert til JSON")
        
        # Vis en del av JSON
        print("\n   Input JSON (utdrag):")
        input_dict = json.loads(input_json)
        print(f"     Temperature hot: {input_dict['conditions']['hot_side']['temperature']}°C")
        print(f"     Plates: {input_dict['geometry']['n_plates']}")
        
        print("\n   Output JSON (utdrag):")
        output_dict = json.loads(output_json)
        print(f"     Heat transfer: {output_dict['heat_transfer_rate']:.0f} W")
        print(f"     Effectiveness: {output_dict['effectiveness']:.3f}")
        
    except Exception as e:
        print(f"   ✗ JSON serialiseringsfeil: {e}")
        return
    
    # 6. Test validering med feil data
    print("\n6. Tester validering med ugyldig data...")
    invalid_data = input_data.copy()
    invalid_data["conditions"]["hot_side"]["temperature"] = 150.0  # For høy temperatur
    
    try:
        AnalysisInput(**invalid_data)
        print("   ✗ Validering burde ha feilet")
    except Exception as e:
        print(f"   ✓ Validering fanget opp feil som forventet: {type(e).__name__}")
    
    # 7. Test forskjellige fuktighetsinput
    print("\n7. Tester forskjellige fuktighetsinput...")
    
    # Med fuktighetsforhold i stedet for relativ fuktighet
    humid_data = {
        "temperature": 25.0,
        "pressure": 101325,
        "humidity_ratio": 0.008
    }
    
    try:
        moist_air_schema = MoistAirInput(**humid_data)
        air_obj = ThermodynamicsAdapter.from_schema(moist_air_schema)
        air_output = ThermodynamicsAdapter.to_schema(air_obj)
        
        print(f"   ✓ Input: {moist_air_schema.humidity_ratio:.4f} kg/kg")
        print(f"   ✓ Output RH: {air_output.relative_humidity:.1f}%")
        
    except Exception as e:
        print(f"   ✗ Fuktighetskonvertering feil: {e}")
    
    print("\n8. Eksempel fullført!")
    print("\nFordeler med Pydantic schemas:")
    print("- Automatisk validering av input data")
    print("- Type hints og IDE støtte") 
    print("- JSON serialisering/deserialisering")
    print("- Dokumentasjon med examples")
    print("- API-kompatibel struktur")


if __name__ == "__main__":
    main()
