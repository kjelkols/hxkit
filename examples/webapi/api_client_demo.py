"""
HXKit Web-API Klient Eksempel

Dette viser hvordan du bruker HXKit Web-APIet fra ulike klienter:
1. Python requests
2. JavaScript/Web browser
3. curl kommandolinje
4. Excel/VBA
"""

import requests
import json
from typing import Dict, Any


class HXKitAPIClient:
    """Python klient for HXKit Web-API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def analyze_heat_exchanger(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyser varmeveksler"""
        url = f"{self.base_url}/api/v1/analyze"
        
        response = self.session.post(url, json=analysis_data)
        response.raise_for_status()
        
        return response.json()
    
    def get_air_properties(self, temperature: float, pressure: float = 101325, 
                          relative_humidity: float = 50.0) -> Dict[str, Any]:
        """Hent luftegenskaper"""
        url = f"{self.base_url}/api/v1/air-properties"
        
        air_data = {
            "temperature": temperature,
            "pressure": pressure,
            "relative_humidity": relative_humidity,
            "humidity_ratio": None,
            "dew_point": None,
            "wet_bulb": None
        }
        
        response = self.session.post(url, json=air_data)
        response.raise_for_status()
        
        return response.json()
    
    from typing import Optional

    def batch_analyze(self, cases: list, case_names: Optional[list] = None) -> Dict[str, Any]:
        """Batch analyse av flere cases"""
        url = f"{self.base_url}/api/v1/batch-analyze"
        
        batch_data = {
            "cases": cases,
            "case_names": case_names if case_names is not None else []
        }
        
        response = self.session.post(url, json=batch_data)
        response.raise_for_status()
        
        return response.json()
    
    def health_check(self) -> Dict[str, Any]:
        """Sjekk API helse"""
        url = f"{self.base_url}/health"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()


def demo_python_client():
    """Demonstrerer Python klient"""
    print("=== Python Klient Demonstrasjon ===\n")
    
    # Opprett klient
    client = HXKitAPIClient()
    
    # Test 1: Helsesjekk
    print("1. Helsesjekk:")
    try:
        health = client.health_check()
        print(f"   ✅ API Status: {health['status']}")
        print(f"   🕐 Timestamp: {health['timestamp']}")
    except Exception as e:
        print(f"   ❌ API ikke tilgjengelig: {e}")
        return
    
    # Test 2: Luftegenskaper
    print("\n2. Luftegenskaper:")
    try:
        air_props = client.get_air_properties(temperature=25.0, relative_humidity=60.0)
        print(f"   🌡️  25°C, 60% RH:")
        print(f"   📊 Tetthet: {air_props['density']:.2f} kg/m³")
        print(f"   ⚡ Entalpi: {air_props['enthalpy']:.1f} kJ/kg")
    except Exception as e:
        print(f"   ❌ Feil: {e}")
    
    # Test 3: Varmeveksler analyse
    print("\n3. Varmeveksler analyse:")
    
    analysis_data = {
        "conditions": {
            "hot_side": {
                "temperature": 30.0,
                "pressure": 101325,
                "relative_humidity": 45.0,
                "humidity_ratio": None,
                "dew_point": None,
                "wet_bulb": None
            },
            "cold_side": {
                "temperature": 5.0,
                "pressure": 101325,
                "relative_humidity": 85.0,
                "humidity_ratio": None,
                "dew_point": None,
                "wet_bulb": None
            }
        },
        "flow": {
            "hot_mass_flow": 0.15,
            "cold_mass_flow": 0.15
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
    
    try:
        result = client.analyze_heat_exchanger(analysis_data)
        print(f"   🔥 Varmeoverføring: {result['heat_transfer_rate']:.0f} W")
        print(f"   ⚡ Effectiveness: {result['effectiveness']:.3f}")
        print(f"   🌡️  Utløp: {result['hot_outlet']['temperature']:.1f}°C / {result['cold_outlet']['temperature']:.1f}°C")
    except Exception as e:
        print(f"   ❌ Feil: {e}")


def demo_javascript_example():
    """Viser JavaScript kode for web-bruk"""
    print("\n=== JavaScript/Web Browser Eksempel ===")
    
    js_code = '''
// JavaScript kode for å bruke HXKit APIet fra en nettside

async function analyzeHeatExchanger() {
    const analysisData = {
        conditions: {
            hot_side: {
                temperature: 25.0,
                pressure: 101325,
                relative_humidity: 50.0,
                humidity_ratio: null,
                dew_point: null,
                wet_bulb: null
            },
            cold_side: {
                temperature: 10.0,
                pressure: 101325,
                relative_humidity: 80.0,
                humidity_ratio: null,
                dew_point: null,
                wet_bulb: null
            }
        },
        flow: {
            hot_mass_flow: 0.1,
            cold_mass_flow: 0.1
        },
        core: {
            geometry: {
                plate_width: 0.6,
                plate_height: 0.2,
                plate_spacing: 0.004,
                chevron_angle: 30.0
            },
            num_plates: 21
        }
    };

    try {
        const response = await fetch('http://localhost:8000/api/v1/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(analysisData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        console.log('Varmeoverføring:', result.heat_transfer_rate, 'W');
        console.log('Effectiveness:', result.effectiveness);
        
        // Oppdater HTML elementer
        document.getElementById('heat-transfer').textContent = 
            result.heat_transfer_rate.toFixed(0) + ' W';
        document.getElementById('effectiveness').textContent = 
            result.effectiveness.toFixed(3);
            
    } catch (error) {
        console.error('API feil:', error);
        alert('Feil ved analyse: ' + error.message);
    }
}

// Bruk i HTML:
// <button onclick="analyzeHeatExchanger()">Analyser</button>
// <p>Varmeoverføring: <span id="heat-transfer">-</span></p>
// <p>Effectiveness: <span id="effectiveness">-</span></p>
'''
    
    print("JavaScript implementasjon:")
    print(js_code)


def demo_curl_examples():
    """Viser curl kommandoer"""
    print("\n=== Curl Kommandolinje Eksempler ===")
    
    curl_examples = '''
# 1. Helsesjekk
curl http://localhost:8000/health

# 2. Luftegenskaper
curl -X POST http://localhost:8000/api/v1/air-properties \\
  -H "Content-Type: application/json" \\
  -d '{
    "temperature": 25.0,
    "pressure": 101325,
    "relative_humidity": 60.0,
    "humidity_ratio": null,
    "dew_point": null,
    "wet_bulb": null
  }'

# 3. Varmeveksler analyse
curl -X POST http://localhost:8000/api/v1/analyze \\
  -H "Content-Type: application/json" \\
  -d '{
    "conditions": {
      "hot_side": {
        "temperature": 30.0,
        "pressure": 101325,
        "relative_humidity": 45.0,
        "humidity_ratio": null,
        "dew_point": null,
        "wet_bulb": null
      },
      "cold_side": {
        "temperature": 5.0,
        "pressure": 101325,
        "relative_humidity": 85.0,
        "humidity_ratio": null,
        "dew_point": null,
        "wet_bulb": null
      }
    },
    "flow": {
      "hot_mass_flow": 0.15,
      "cold_mass_flow": 0.15
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
  }'

# 4. API dokumentasjon (åpne i browser)
# http://localhost:8000/docs
'''
    
    print("Curl kommandoer:")
    print(curl_examples)


def demo_excel_vba():
    """Viser VBA kode for Excel"""
    print("\n=== Excel VBA Eksempel ===")
    
    vba_code = '''
' VBA kode for å bruke HXKit APIet fra Excel

Sub AnalyzeHeatExchanger()
    Dim http As Object
    Dim jsonText As String
    Dim response As String
    
    ' Opprett HTTP objekt
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    ' Bygg JSON data (kan leses fra Excel celler)
    jsonText = "{" & _
        """conditions"": {" & _
            """hot_side"": {" & _
                """temperature"": " & Range("B2").Value & "," & _
                """pressure"": 101325," & _
                """relative_humidity"": " & Range("B3").Value & "," & _
                """humidity_ratio"": null," & _
                """dew_point"": null," & _
                """wet_bulb"": null" & _
            "}," & _
            """cold_side"": {" & _
                """temperature"": " & Range("B4").Value & "," & _
                """pressure"": 101325," & _
                """relative_humidity"": " & Range("B5").Value & "," & _
                """humidity_ratio"": null," & _
                """dew_point"": null," & _
                """wet_bulb"": null" & _
            "}" & _
        "}," & _
        """flow"": {" & _
            """hot_mass_flow"": " & Range("B6").Value & "," & _
            """cold_mass_flow"": " & Range("B7").Value & _
        "}," & _
        """core"": {" & _
            """geometry"": {" & _
                """plate_width"": " & Range("B8").Value & "," & _
                """plate_height"": " & Range("B9").Value & "," & _
                """plate_spacing"": " & Range("B10").Value & "," & _
                """chevron_angle"": " & Range("B11").Value & _
            "}," & _
            """num_plates"": " & Range("B12").Value & _
        "}" & _
    "}"
    
    ' Send HTTP forespørsel
    http.Open "POST", "http://localhost:8000/api/v1/analyze", False
    http.setRequestHeader "Content-Type", "application/json"
    http.send jsonText
    
    ' Hent respons
    response = http.responseText
    
    ' Parse JSON respons (enkel parsing for demo)
    ' I praksis: bruk JSON parser bibliotek
    
    ' Skriv resultat til Excel
    Range("D2").Value = "Varmeoverføring: " & ExtractValue(response, "heat_transfer_rate") & " W"
    Range("D3").Value = "Effectiveness: " & ExtractValue(response, "effectiveness")
    
End Sub

Function ExtractValue(jsonText As String, key As String) As String
    ' Enkel JSON parsing (ikke robust - bruk riktig JSON parser)
    Dim startPos As Integer
    Dim endPos As Integer
    
    startPos = InStr(jsonText, """" & key & """:") + Len(key) + 3
    endPos = InStr(startPos, jsonText, ",")
    If endPos = 0 Then endPos = InStr(startPos, jsonText, "}")
    
    ExtractValue = Mid(jsonText, startPos, endPos - startPos)
End Function
'''
    
    print("Excel VBA implementasjon:")
    print(vba_code)


def main():
    """Hovedfunksjon"""
    print("HXKit Web-API Klient Demonstrasjon")
    print("=" * 40)
    
    print("🚀 For å teste disse eksemplene:")
    print("   1. Start serveren: python examples/fastapi_server.py")
    print("   2. Gå til http://localhost:8000/docs for interaktiv dokumentasjon")
    print("   3. Kjør denne filen for Python klient demo")
    print()
    
    demo_python_client()
    demo_javascript_example()
    demo_curl_examples()
    demo_excel_vba()
    
    print("\n" + "=" * 40)
    print("🎯 Web-API Fordeler i Praksis:")
    print("   • Tilgjengelig fra alle programmeringsspråk")
    print("   • Ingen Python-installasjon nødvendig for brukere")
    print("   • Automatisk dokumentasjon på /docs")
    print("   • Sentralisert versjonskontroll")
    print("   • Enkel å integrere i eksisterende systemer")


if __name__ == "__main__":
    main()