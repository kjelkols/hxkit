"""
Forenklet eksempel på bruk av Pydantic schemas for input/output validering.

Dette eksemplet viser hvordan du kan bruke Pydantic modellene for:
1. Strukturert input validering
2. JSON serialisering/deserialisering
3. Datavalidering
"""

import json
from hxkit.schemas import (
    MoistAirInput, MoistAirOutput, PsychrometricConditions, FlowConditions,
    PlateGeometryInput, HeatExchangerCoreInput, 
    AnalysisInput, AnalysisOutput
)
from hxkit import MoistAir, PlateGeometry, HeatExchangerCore, PlateHeatExchanger


def main():
    print("HXKit Pydantic Schema Eksempel (Forenklet)")
    print("=" * 50)
    
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
    
    print(f"Input data keys: {list(input_data.keys())}")
    
    # 2. Valider input data med Pydantic schemas
    print("\n2. Validerer input data med Pydantic schemas...")
    
    try:
        # Parse og valider hver del
        conditions = PsychrometricConditions(**input_data["conditions"])
        flow = FlowConditions(**input_data["flow"])
        core = HeatExchangerCoreInput(**input_data["core"])
        
        # Opprett komplett analyse input
        analysis_input = AnalysisInput(
            conditions=conditions,
            flow=flow,
            core=core
        )
        
        print("✅ Input validering vellykket!")
        print(f"   Varm side: {analysis_input.conditions.hot_side.temperature}°C, "
              f"RH={analysis_input.conditions.hot_side.relative_humidity}%")
        print(f"   Kald side: {analysis_input.conditions.cold_side.temperature}°C, "
              f"RH={analysis_input.conditions.cold_side.relative_humidity}%")
        
    except Exception as e:
        print(f"❌ Valideringsfeil: {e}")
        return
    
    # 3. Konverter til kjerne objekter og utfør analyse
    print("\n3. Konverterer til kjerne objekter og utfører analyse...")
    
    try:
        # Manuell konvertering til kjerne objekter
        hot_air = MoistAir(
            temperature=conditions.hot_side.temperature,
            pressure=conditions.hot_side.pressure,
            relative_humidity=conditions.hot_side.relative_humidity
        )
        
        cold_air = MoistAir(
            temperature=conditions.cold_side.temperature,
            pressure=conditions.cold_side.pressure,
            relative_humidity=conditions.cold_side.relative_humidity
        )
        
        plate_geom = PlateGeometry(
            length=core.geometry.plate_width,
            width=core.geometry.plate_height,
            thickness=0.0005,  # Standard platetykkelse
            channel_height=core.geometry.plate_spacing,
            corrugation_angle=core.geometry.chevron_angle
        )
        
        hx_core = HeatExchangerCore(
            n_plates=core.num_plates,
            plate_geometry=plate_geom,
            hot_channels=(core.num_plates - 1) // 2,
            cold_channels=(core.num_plates - 1) // 2
        )
        
        # Utfør analyse
        hx = PlateHeatExchanger(hx_core)
        results = hx.analyze(
            hot_inlet=hot_air,
            cold_inlet=cold_air,
            hot_mass_flow=flow.hot_mass_flow,
            cold_mass_flow=flow.cold_mass_flow
        )
        
        print("✅ Analyse vellykket!")
        print(f"   Varmeoverføring: {results['heat_transfer_rate']:.2f} W")
        print(f"   Effectiveness: {results['effectiveness']:.3f}")
        
    except Exception as e:
        print(f"❌ Analysefeil: {e}")
        return
    
    # 4. Konverter resultater til output schema
    print("\n4. Konverterer resultater til output schema...")
    
    try:
        # Manuell konvertering til output schema
        # Note: hot_inlet og cold_inlet er ikke i results, så vi bruker de originale objektene
        hot_inlet_schema = MoistAirOutput(
            temperature=hot_air.temperature,
            pressure=hot_air.pressure,
            relative_humidity=hot_air.relative_humidity,
            humidity_ratio=hot_air.humidity_ratio,
            dew_point=hot_air.dew_point,
            wet_bulb=hot_air.wet_bulb,
            density=hot_air.density,
            enthalpy=hot_air.enthalpy
        )
        
        cold_inlet_schema = MoistAirOutput(
            temperature=cold_air.temperature,
            pressure=cold_air.pressure,
            relative_humidity=cold_air.relative_humidity,
            humidity_ratio=cold_air.humidity_ratio,
            dew_point=cold_air.dew_point,
            wet_bulb=cold_air.wet_bulb,
            density=cold_air.density,
            enthalpy=cold_air.enthalpy
        )
        
        hot_outlet_schema = MoistAirOutput(
            temperature=results["hot_outlet"].temperature,
            pressure=results["hot_outlet"].pressure,
            relative_humidity=results["hot_outlet"].relative_humidity,
            humidity_ratio=results["hot_outlet"].humidity_ratio,
            dew_point=results["hot_outlet"].dew_point,
            wet_bulb=results["hot_outlet"].wet_bulb,
            density=results["hot_outlet"].density,
            enthalpy=results["hot_outlet"].enthalpy
        )
        
        cold_outlet_schema = MoistAirOutput(
            temperature=results["cold_outlet"].temperature,
            pressure=results["cold_outlet"].pressure,
            relative_humidity=results["cold_outlet"].relative_humidity,
            humidity_ratio=results["cold_outlet"].humidity_ratio,
            dew_point=results["cold_outlet"].dew_point,
            wet_bulb=results["cold_outlet"].wet_bulb,
            density=results["cold_outlet"].density,
            enthalpy=results["cold_outlet"].enthalpy
        )
        
        # Opprett komplett output schema
        analysis_output = AnalysisOutput(
            hot_inlet=hot_inlet_schema,
            cold_inlet=cold_inlet_schema,
            hot_outlet=hot_outlet_schema,
            cold_outlet=cold_outlet_schema,
            heat_transfer_rate=results["heat_transfer_rate"],
            effectiveness=results["effectiveness"],
            hot_pressure_drop=results["hot_pressure_drop"],
            cold_pressure_drop=results["cold_pressure_drop"],
            overall_heat_transfer_coefficient=results["u_overall"],
            ntu=results["ntu"]
        )
        
        print("✅ Output schema opprettet!")
        
    except Exception as e:
        print(f"❌ Output schema feil: {e}")
        return
    
    # 5. JSON serialisering
    print("\n5. JSON serialisering/deserialisering...")
    
    try:
        # Eksporter til JSON
        output_json = analysis_output.model_dump_json(indent=2)
        print("✅ JSON eksport vellykket!")
        print(f"   JSON størrelse: {len(output_json)} bytes")
        
        # Import fra JSON
        recreated_output = AnalysisOutput.model_validate_json(output_json)
        print("✅ JSON import vellykket!")
        print(f"   Gjenskapt varmeoverføring: {recreated_output.heat_transfer_rate:.2f} W")
        
    except Exception as e:
        print(f"❌ JSON feil: {e}")
        return
    
    # 6. Demonstrer validering
    print("\n6. Demonstrerer input validering...")
    
    try:
        # Test ugyldig input
        invalid_input = {
            "temperature": 150,  # For høy temperatur
            "pressure": 101325,
            "relative_humidity": 40.0
        }
        
        try:
            MoistAirInput(**invalid_input)
            print("❌ Validering feilet - skulle ha kastet feil")
        except Exception as validation_error:
            print(f"✅ Validering fungerer: {validation_error}")
            
    except Exception as e:
        print(f"❌ Valideringtest feil: {e}")
    
    print("\n7. Eksempel fullført!")
    print("   Pydantic schemas gir strukturert og validert API for hxkit!")


if __name__ == "__main__":
    main()