"""
Enkel Psykrometrisk Diagram Generator
====================================
Generer psykrometrisk diagram med matplotlib
Bruker lokal HXKit implementasjon for beregninger
"""

import numpy as np
import matplotlib.pyplot as plt

# Lokal implementasjon
try:
    from hxkit.thermodynamics import MoistAir
    LOCAL_AVAILABLE = True
except ImportError:
    LOCAL_AVAILABLE = False
    print("❌ HXKit ikke tilgjengelig. Installer med: pip install -e .")

def get_air_properties(temperature, relative_humidity=None, pressure=101325):
    """Hent luftegenskaper fra lokal implementasjon"""
    if not LOCAL_AVAILABLE:
        return None
    
    try:
        air = MoistAir(temperature=temperature, pressure=pressure, relative_humidity=relative_humidity)
        return {
            'temperature': air.temperature,
            'pressure': air.pressure,
            'relative_humidity': air.relative_humidity,
            'humidity_ratio': air.humidity_ratio,
            'dew_point': air.dew_point,
            'wet_bulb': air.wet_bulb,
            'density': air.density,
            'specific_volume': air.specific_volume,
            'enthalpy': air.enthalpy
        }
    except Exception as e:
        print(f"⚠️  Beregning feilet for T={temperature}°C, RH={relative_humidity}%: {e}")
        return None

def create_simple_psychrometric_chart():
    """Opprett enkelt psykrometrisk diagram"""
    
    print("📊 Genererer psykrometrisk diagram...")
    print("   Bruker lokal HXKit implementasjon for beregninger...")
    
    # Temperatur område (0-50°C)
    temp_range = np.linspace(0, 50, 26)
    
    # Opprett figur
    plt.figure(figsize=(12, 8))
    
    # Relativ fuktighet linjer
    rh_values = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    colors = ['lightblue', 'blue', 'green', 'orange', 'red', 'purple', 'brown', 'pink', 'gray', 'black']
    
    for i, rh in enumerate(rh_values):
        hr_values = []
        temps = []
        
        for temp in temp_range:
            result = get_air_properties(temperature=temp, relative_humidity=rh)
            if result:
                hr_values.append(result['humidity_ratio'] * 1000)  # Konverter til g/kg
                temps.append(temp)
        
        if hr_values:
            if rh == 100:
                plt.plot(temps, hr_values, color=colors[i], linewidth=3, 
                        label=f'{rh}% RH (Metning)', linestyle='-')
            else:
                plt.plot(temps, hr_values, color=colors[i], linewidth=2, 
                        label=f'{rh}% RH', linestyle='-')
    
    # Eksempel punkter
    example_points = [
        {"name": "Komfort (25°C, 50% RH)", "temp": 25, "rh": 50, "color": "red"},
        {"name": "Vinter (20°C, 40% RH)", "temp": 20, "rh": 40, "color": "blue"},
        {"name": "Sommer (30°C, 70% RH)", "temp": 30, "rh": 70, "color": "green"},
    ]
    
    for point in example_points:
        result = get_air_properties(temperature=point["temp"], relative_humidity=point["rh"])
        if result:
            hr = result['humidity_ratio'] * 1000
            plt.plot(point["temp"], hr, 'o', color=point["color"], markersize=10, 
                    markeredgecolor='black', markeredgewidth=2)
            plt.annotate(point["name"], (point["temp"], hr), 
                        xytext=(10, 10), textcoords='offset points',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.8),
                        fontsize=9, ha='left')
    
    # Formatering
    plt.xlabel('tørrkule Temperatur (°C)', fontsize=14, fontweight='bold')
    plt.ylabel('Fuktighetsforhold (g/kg tørr luft)', fontsize=14, fontweight='bold')
    plt.title('Psykrometrisk Diagram\n(Atmosfærisk trykk: 101325 Pa)', fontsize=16, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(loc='upper left', fontsize=10)
    
    # Aksegrenser
    plt.xlim(0, 50)
    plt.ylim(0, 25)
    
    # Tilleggsinformasjon
    plt.text(40, 1, 'Generert med HXKit (lokal)', fontsize=10, alpha=0.6, style='italic')
    
    plt.tight_layout()
    
    # Lagre diagram
    plt.savefig('psykrometrisk_diagram.png', dpi=300, bbox_inches='tight')
    print("💾 Diagram lagret som: psykrometrisk_diagram.png")
    
    # Vis diagram
    plt.show()
    print("📈 Diagram vises!")

def main():
    """Hovedfunksjon"""
    print("🌡️ HXKit - Enkel Psykrometrisk Diagram Generator")
    print("=" * 50)
    
    if not LOCAL_AVAILABLE:
        print("❌ HXKit ikke tilgjengelig!")
        print("   Installer med: pip install -e .")
        return
    
    print("✅ Bruker lokal HXKit implementasjon")
    create_simple_psychrometric_chart()
    print("\n✅ Psykrometrisk diagram generert!")

if __name__ == "__main__":
    main()