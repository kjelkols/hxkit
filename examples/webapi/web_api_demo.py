"""
Eksempel på hvordan du kan lage en web-API med HXKit adapters

Dette viser hvordan adapters gjør det enkelt å bygge FastAPI/Flask endpoints.
"""

import json
from typing import Dict, Any
from hxkit.api import AnalysisAdapter
from hxkit.schemas import AnalysisInput, AnalysisOutput


class HXKitWebAPI:
    """
    Simulert web-API klasse som viser hvordan adapters brukes i praksis.
    
    I en ekte situasjon ville dette vært FastAPI eller Flask endepunkter.
    """
    
    def analyze_heat_exchanger(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulert POST /api/v1/analyze endpoint
        
        Args:
            request_data: JSON data fra HTTP request
            
        Returns:
            JSON response data
        """
        try:
            # 1. Parse og valider input (automatisk med Pydantic)
            analysis_input = AnalysisInput(**request_data)
            
            # 2. Utfør analyse (alt håndteres av adapter)
            analysis_output = AnalysisAdapter.analyze_from_schema(analysis_input)
            
            # 3. Returner som JSON-kompatibel dict
            return {
                "status": "success",
                "data": analysis_output.model_dump(),
                "metadata": {
                    "heat_transfer_rate": analysis_output.heat_transfer_rate,
                    "effectiveness": analysis_output.effectiveness,
                    "num_plates": request_data["core"]["num_plates"]
                }
            }
            
        except Exception as e:
            # Automatisk feilhåndtering
            return {
                "status": "error",
                "message": str(e),
                "error_type": type(e).__name__
            }
    
    def get_air_properties(self, temperature: float, pressure: float = 101325, 
                          relative_humidity: float = 50.0) -> Dict[str, Any]:
        """
        Simulert GET /api/v1/air-properties endpoint
        
        Args:
            temperature: Temperatur i °C
            pressure: Trykk i Pa
            relative_humidity: Relativ fuktighet i %
            
        Returns:
            Luftegenskaper som JSON
        """
        try:
            from hxkit.schemas import MoistAirInput
            from hxkit.api import ThermodynamicsAdapter
            
            # Lag input schema
            air_input = MoistAirInput(
                temperature=temperature,
                pressure=pressure,
                relative_humidity=relative_humidity,
                humidity_ratio=None,
                dew_point=None,
                wet_bulb=None
            )
            
            # Konverter til kjerne objekt og tilbake til schema
            air_object = ThermodynamicsAdapter.from_schema(air_input)
            air_output = ThermodynamicsAdapter.to_schema(air_object)
            
            return {
                "status": "success",
                "data": air_output.model_dump()
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "message": str(e)
            }


def demo_api_usage():
    """Demonstrerer bruk av den simulerte web-APIen"""
    print("=== Web-API Demonstrasjon ===\n")
    
    # Opprett API instans
    api = HXKitWebAPI()
    
    # Test 1: Komplett varmeveksler analyse
    print("1. POST /api/v1/analyze - Varmeveksler analyse:")
    
    request_data = {
        "conditions": {
            "hot_side": {
                "temperature": 28.0,
                "pressure": 101325,
                "relative_humidity": 45.0
            },
            "cold_side": {
                "temperature": -2.0,
                "pressure": 101325,
                "relative_humidity": 85.0
            }
        },
        "flow": {
            "hot_mass_flow": 0.15,
            "cold_mass_flow": 0.13
        },
        "core": {
            "geometry": {
                "plate_width": 0.8,
                "plate_height": 0.3,
                "plate_spacing": 0.005,
                "chevron_angle": 35.0
            },
            "num_plates": 30
        }
    }
    
    response = api.analyze_heat_exchanger(request_data)
    
    if response["status"] == "success":
        metadata = response["metadata"]
        print(f"   ✅ Status: {response['status']}")
        print(f"   🔥 Varmeoverføring: {metadata['heat_transfer_rate']:.0f} W")
        print(f"   ⚡ Effectiveness: {metadata['effectiveness']:.3f}")
        print(f"   📐 Antall plater: {metadata['num_plates']}")
    else:
        print(f"   ❌ Error: {response['message']}")
    
    print()
    
    # Test 2: Luftegenskaper
    print("2. GET /api/v1/air-properties - Luftegenskaper:")
    
    air_response = api.get_air_properties(temperature=20.0, relative_humidity=65.0)
    
    if air_response["status"] == "success":
        air_data = air_response["data"]
        print(f"   ✅ Status: {air_response['status']}")
        print(f"   🌡️  Temperatur: {air_data['temperature']}°C")
        print(f"   💧 Fuktighet: {air_data['relative_humidity']}% RH")
        print(f"   📊 Tetthet: {air_data['density']:.2f} kg/m³")
        print(f"   ⚡ Entalpi: {air_data['enthalpy']:.1f} kJ/kg")
    else:
        print(f"   ❌ Error: {air_response['message']}")
    
    print()
    
    # Test 3: Feilhåndtering
    print("3. Feilhåndtering - Ugyldig input:")
    
    invalid_request = {
        "conditions": {
            "hot_side": {
                "temperature": 150.0,  # Over grensen (100°C)
                "pressure": 101325,
                "relative_humidity": 45.0
            },
            "cold_side": {
                "temperature": -2.0,
                "pressure": 101325,
                "relative_humidity": 85.0
            }
        },
        "flow": {
            "hot_mass_flow": 0.15,
            "cold_mass_flow": 0.13
        },
        "core": {
            "geometry": {
                "plate_width": 0.8,
                "plate_height": 0.3,
                "plate_spacing": 0.005,
                "chevron_angle": 35.0
            },
            "num_plates": 30
        }
    }
    
    error_response = api.analyze_heat_exchanger(invalid_request)
    print(f"   ❌ Status: {error_response['status']}")
    print(f"   🚨 Error type: {error_response['error_type']}")
    print(f"   📝 Message: {error_response['message'][:80]}...")


def demo_fastapi_code():
    """Viser hvordan koden ville sett ut med FastAPI"""
    print("\n=== FastAPI Implementasjon (kodeeksempel) ===")
    
    fastapi_code = '''
from fastapi import FastAPI, HTTPException
from hxkit.api import AnalysisAdapter
from hxkit.schemas import AnalysisInput, AnalysisOutput

app = FastAPI(title="HXKit API", version="1.0.0")

@app.post("/api/v1/analyze", response_model=AnalysisOutput)
async def analyze_heat_exchanger(analysis_input: AnalysisInput):
    """Analyser platevarmeveksler"""
    try:
        # EN linje kode takket være adapters!
        return AnalysisAdapter.analyze_from_schema(analysis_input)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/analyze-json")
async def analyze_from_json(json_data: str):
    """JSON til JSON analyse"""
    try:
        # EN linje kode for JSON til JSON!
        return AnalysisAdapter.analyze_from_json(json_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    '''
    
    print("FastAPI implementasjon med adapters:")
    print(fastapi_code)
    print("🚀 Kjør med: uvicorn main:app --reload")


def main():
    """Hovedfunksjon"""
    print("HXKit API Adapters - Web-API Demonstrasjon")
    print("=" * 50)
    
    demo_api_usage()
    demo_fastapi_code()
    
    print("\n" + "=" * 50)
    print("🎯 Nøkkelfordeler med adapters for web-APIer:")
    print("   • Automatisk datavalidering med Pydantic")
    print("   • JSON serialisering/deserialisering innebygd")
    print("   • Enkle endepunkter - ofte bare én linje kode!")
    print("   • Konsistent feilhåndtering")
    print("   • OpenAPI dokumentasjon genereres automatisk")
    print()
    print("📚 For å lage en ekte web-API:")
    print("   pip install fastapi uvicorn")
    print("   # Bruk kodeeksempelet ovenfor")
    print("   uvicorn main:app --reload")


if __name__ == "__main__":
    main()