"""
Standalone Psykrometrisk Diagram Generator
=========================================
Genererer og viser psykrometrisk diagram med HXKit API
"""

import requests
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Any
import json

# API konfigurasjon
API_BASE_URL = "http://localhost:8000"

def check_api_connection():
    """Sjekk om APIet er tilgjengelig"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def get_air_properties(temperature: float, pressure: float = 101325, relative_humidity: float = None, 
                      humidity_ratio: float = None, dew_point: float = None, wet_bulb: float = None):
    """Hent luftegenskaper fra API"""
    data = {
        "temperature": temperature,
        "pressure": pressure,
        "relative_humidity": relative_humidity,
        "humidity_ratio": humidity_ratio,
        "dew_point": dew_point,
        "wet_bulb": wet_bulb
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/v1/air-properties", json=data, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API feil: {response.json().get('detail', 'Ukjent feil')}")
            return None
    except Exception as e:
        print(f"Feil ved API-kall: {e}")
        return None

def generate_constant_rh_lines(temp_range: np.ndarray, rh_values: List[float], pressure: float = 101325):
    """Generer konstant relativ fuktighet linjer"""
    rh_lines = {}
    
    for rh in rh_values:
        hr_values = []
        temps = []
        
        for temp in temp_range:
            result = get_air_properties(temperature=temp, pressure=pressure, relative_humidity=rh)
            if result:
                hr_values.append(result['humidity_ratio'] * 1000)  # Konverter til g/kg
                temps.append(temp)
        
        if hr_values:
            rh_lines[rh] = {'temperatures': temps, 'humidity_ratios': hr_values}
    
    return rh_lines

def generate_constant_wb_lines(temp_range: np.ndarray, wb_values: List[float], pressure: float = 101325):
    """Generer konstant våtkulb temperatur linjer"""
    wb_lines = {}
    
    for wb in wb_values:
        hr_values = []
        temps = []
        
        for temp in temp_range:
            if temp > wb:  # Våtkulb kan ikke være høyere enn tørrkulb
                result = get_air_properties(temperature=temp, pressure=pressure, wet_bulb=wb)
                if result:
                    hr_values.append(result['humidity_ratio'] * 1000)
                    temps.append(temp)
        
        if hr_values:
            wb_lines[wb] = {'temperatures': temps, 'humidity_ratios': hr_values}
    
    return wb_lines

def create_psychrometric_chart(save_filename: str = None, show_plot: bool = True):
    """Opprett komplett psykrometrisk diagram"""
    
    # Sjekk API tilkobling
    if not check_api_connection():
        print("❌ API ikke tilgjengelig. Start serveren med: python examples/fastapi_server.py")
        return
    
    print("📊 Genererer psykrometrisk diagram...")
    
    # Temperatur område
    temp_range = np.linspace(0, 50, 51)  # 0-50°C
    
    # Opprett figur
    plt.figure(figsize=(14, 10))
    plt.style.use('seaborn-v0_8')
    
    # Generer konstant RH linjer
    print("🔄 Genererer konstant RH linjer...")
    rh_values = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    rh_lines = generate_constant_rh_lines(temp_range, rh_values)
    
    colors = plt.cm.Blues(np.linspace(0.3, 0.9, len(rh_values)))
    
    for i, (rh, data) in enumerate(rh_lines.items()):
        plt.plot(data['temperatures'], data['humidity_ratios'], 
                color=colors[i], linewidth=2, label=f'{rh}% RH')
    
    # Generer konstant våtkulb linjer
    print("🔄 Genererer konstant våtkulb linjer...")
    wb_values = [5, 10, 15, 20, 25, 30, 35, 40]
    wb_lines = generate_constant_wb_lines(temp_range, wb_values)
    
    wb_colors = plt.cm.Reds(np.linspace(0.3, 0.9, len(wb_values)))
    
    for i, (wb, data) in enumerate(wb_lines.items()):
        if data['temperatures']:  # Sjekk at vi har data
            plt.plot(data['temperatures'], data['humidity_ratios'], 
                    color=wb_colors[i], linewidth=1, linestyle='--', alpha=0.7,
                    label=f'{wb}°C WB')
    
    # Metningslinje (100% RH)
    if 100 in rh_lines:
        plt.plot(rh_lines[100]['temperatures'], rh_lines[100]['humidity_ratios'], 
                'k-', linewidth=3, label='Metningslinje (100% RH)')
    
    # Formatering
    plt.xlabel('Tørrbulb Temperatur (°C)', fontsize=12, fontweight='bold')
    plt.ylabel('Fuktighetsforhold (g/kg tørr luft)', fontsize=12, fontweight='bold')
    plt.title('Psykrometrisk Diagram\n(Trykk: 101325 Pa)', fontsize=16, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    
    # Aksegrenser
    plt.xlim(0, 50)
    plt.ylim(0, 25)
    
    # Tekst annotering
    plt.text(45, 23, 'HXKit Psykrometrisk Diagram', 
             fontsize=10, alpha=0.6, style='italic')
    
    plt.tight_layout()
    
    # Lagre hvis spesifisert
    if save_filename:
        plt.savefig(save_filename, dpi=300, bbox_inches='tight')
        print(f"💾 Diagram lagret som: {save_filename}")
    
    # Vis diagram
    if show_plot:
        plt.show()
        print("📈 Diagram vises...")
    
    return plt.gcf()

def plot_example_points():
    """Plot eksempel punkter på psykrometrisk diagram"""
    
    # Eksempel punkter
    example_points = [
        {"name": "Komfort sommer", "temp": 25, "rh": 50},
        {"name": "Komfort vinter", "temp": 22, "rh": 45},
        {"name": "Varmt og fuktig", "temp": 35, "rh": 80},
        {"name": "Kaldt og tørt", "temp": 5, "rh": 30},
    ]
    
    print("📍 Legger til eksempel punkter...")
    
    for point in example_points:
        result = get_air_properties(
            temperature=point["temp"], 
            relative_humidity=point["rh"]
        )
        
        if result:
            hr = result['humidity_ratio'] * 1000  # g/kg
            plt.plot(point["temp"], hr, 'ro', markersize=8, markeredgecolor='black')
            plt.annotate(point["name"], 
                        (point["temp"], hr), 
                        xytext=(5, 5), 
                        textcoords='offset points',
                        fontsize=9,
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))

def main():
    """Hovedfunksjon"""
    print("🌡️ HXKit Psykrometrisk Diagram Generator")
    print("=" * 45)
    
    # Opprett diagram
    fig = create_psychrometric_chart(
        save_filename="psykrometrisk_diagram.png",
        show_plot=False
    )
    
    if fig:
        # Legg til eksempel punkter
        plot_example_points()
        
        # Vis endelig diagram
        plt.show()
        
        print("\n✅ Psykrometrisk diagram generert!")
        print("📁 Lagret som: psykrometrisk_diagram.png")
    else:
        print("❌ Kunne ikke generere diagram")

if __name__ == "__main__":
    main()