"""
Enkel demonstrasjon av hvordan API Adapters brukes

Dette viser de grunnleggende bruksområdene for adapters.
"""

import json
from hxkit.api import ThermodynamicsAdapter, GeometryAdapter, AnalysisAdapter
from hxkit.schemas import MoistAirInput, AnalysisInput


def demo_basic_usage():
    """Grunnleggende bruk av adapters"""
    print("=== Grunnleggende API Adapter Bruk ===\n")
    
    # 1. Enkelt termodynamikk eksempel
    print("1. ThermodynamicsAdapter - Konvertering av lufttilstander:")
    
    # JSON data fra en API eller konfigurasjonsfil
    air_data = {
        "temperature": 25.0,
        "pressure": 101325,
        "relative_humidity": 60.0
    }
    
    # Konverter JSON til Pydantic schema (med validering)
    air_schema = MoistAirInput(**air_data)
    print(f"   📝 Input schema: {air_schema.temperature}°C, RH={air_schema.relative_humidity}%")
    
    # Bruk adapter til å lage kjerne objekt
    air_object = ThermodynamicsAdapter.from_schema(air_schema)
    print(f"   🔧 Kjerne objekt: {air_object.enthalpy:.1f} kJ/kg entalpi")
    
    # Konverter tilbake til strukturert output
    air_output = ThermodynamicsAdapter.to_schema(air_object)
    print(f"   📤 Output schema: {air_output.density:.2f} kg/m³ tetthet\n")


def demo_complete_analysis():
    """Komplett analyse med adapters"""
    print("2. AnalysisAdapter - Komplett varmeveksler analyse:")
    
    # Definer komplett analyse input som JSON-struktur
    analysis_data = {
        "conditions": {
            "hot_side": {
                "temperature": 30.0,
                "pressure": 101325,
                "relative_humidity": 45.0
            },
            "cold_side": {
                "temperature": 0.0,
                "pressure": 101325,
                "relative_humidity": 85.0
            }
        },
        "flow": {
            "hot_mass_flow": 0.12,
            "cold_mass_flow": 0.12
        },
        "core": {
            "geometry": {
                "plate_width": 0.7,
                "plate_height": 0.25,
                "plate_spacing": 0.004,
                "chevron_angle": 30.0
            },
            "num_plates": 25
        }
    }
    
    print(f"   📥 Input data: {analysis_data['conditions']['hot_side']['temperature']}°C → {analysis_data['conditions']['cold_side']['temperature']}°C")
    
    # Konverter til Pydantic schema (med automatisk validering)
    analysis_input = AnalysisInput(**analysis_data)
    
    # Utfør analyse med adapter - dette gjør ALT automatisk!
    analysis_output = AnalysisAdapter.analyze_from_schema(analysis_input)
    
    print(f"   🔥 Varmeoverføring: {analysis_output.heat_transfer_rate:.0f} W")
    print(f"   ⚡ Effectiveness: {analysis_output.effectiveness:.3f}")
    print(f"   🌡️  Utløpstemperaturer: {analysis_output.hot_outlet.temperature:.1f}°C / {analysis_output.cold_outlet.temperature:.1f}°C")
    print(f"   💨 Trykkfall: {analysis_output.hot_pressure_drop:.0f} Pa / {analysis_output.cold_pressure_drop:.0f} Pa\n")


def demo_json_workflow():
    """JSON til JSON arbeidsflyt"""
    print("3. JSON til JSON arbeidsflyt (perfekt for web-APIer):")
    
    # Simuler JSON fra en web-request
    json_input = '''
    {
        "conditions": {
            "hot_side": {
                "temperature": 22.0,
                "pressure": 101325,
                "relative_humidity": 40.0
            },
            "cold_side": {
                "temperature": -5.0,
                "pressure": 101325,
                "relative_humidity": 80.0
            }
        },
        "flow": {
            "hot_mass_flow": 0.1,
            "cold_mass_flow": 0.1
        },
        "core": {
            "geometry": {
                "plate_width": 0.6,
                "plate_height": 0.2,
                "plate_spacing": 0.004,
                "chevron_angle": 30.0
            },
            "num_plates": 21
        }
    }
    '''
    
    print(f"   📥 JSON input: {len(json_input)} bytes")
    
    # EN linje kode for å gjøre hele analysen!
    json_output = AnalysisAdapter.analyze_from_json(json_input)
    
    print(f"   📤 JSON output: {len(json_output)} bytes")
    
    # Parse output for å vise resultater
    result = json.loads(json_output)
    print(f"   ✅ Resultat: {result['heat_transfer_rate']:.0f} W varmeoverføring")


def main():
    """Hovedfunksjon"""
    print("HXKit API Adapters - Enkel Demonstrasjon")
    print("=" * 45)
    print()
    
    demo_basic_usage()
    demo_complete_analysis() 
    demo_json_workflow()
    
    print("=" * 45)
    print("🎯 Hovedpoeng med API Adapters:")
    print("   • Enkle funksjoner som gjør komplekse konverteringer")
    print("   • Automatisk datavalidering med Pydantic")
    print("   • Perfekt for web-APIer, konfigurasjonsfiler, og batch-kjøring")
    print("   • JSON inn → Analyse → JSON ut i én linje kode!")
    print()
    print("💡 Neste steg: Bruk AnalysisAdapter.analyze_from_json() i din web-API!")


if __name__ == "__main__":
    main()