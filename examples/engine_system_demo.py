"""
Demo av termodynamiske beregninger i HXKit.

Viser hvordan man kan bruke forskjellige engines (ASHRAE/CoolProp)
for psykrometriske beregninger.
"""

from hxkit import MoistAir, Psychrometrics
import time

def demo_basic_usage():
    """Demonstrerer grunnleggende bruk av MoistAir."""
    print("=== GRUNNLEGGENDE BRUK ===")
    
    # Standard bruk med ASHRAE-implementasjon
    air1 = MoistAir(temperature=25.0, relative_humidity=50.0)
    print(f"MoistAir (ASHRAE):")
    print(f"  Temperatur: {air1.temperature:.1f}°C")
    print(f"  Relativ fuktighet: {air1.relative_humidity:.1f}%")
    print(f"  Fuktighetsforhold: {air1.humidity_ratio:.6f} kg/kg")
    print(f"  Duggpunkt: {air1.dew_point:.1f}°C")
    print(f"  Våtkule: {air1.wet_bulb:.1f}°C")
    print(f"  Entalpi: {air1.enthalpy:.1f} kJ/kg")
    print(f"  Tetthet: {air1.density:.3f} kg/m³")
    print()

def demo_different_input_methods():
    """Demonstrerer forskjellige måter å spesifisere fuktighet."""
    print("=== FORSKJELLIGE INPUT-METODER ===")
    
    temp = 20.0
    pressure = 101325.0
    
    # Relativ fuktighet
    air1 = MoistAir(temperature=temp, relative_humidity=60.0, pressure=pressure)
    print(f"Fra relativ fuktighet (60%):")
    print(f"  Fuktighetsforhold: {air1.humidity_ratio:.6f} kg/kg")
    print(f"  Duggpunkt: {air1.dew_point:.1f}°C")
    print(f"  Våtkule: {air1.wet_bulb:.1f}°C")
    print()
    
    # Fuktighetsforhold
    air2 = MoistAir(temperature=temp, humidity_ratio=0.008, pressure=pressure)
    print(f"Fra fuktighetsforhold (0.008 kg/kg):")
    print(f"  Relativ fuktighet: {air2.relative_humidity:.1f}%")
    print(f"  Duggpunkt: {air2.dew_point:.1f}°C")
    print(f"  Våtkule: {air2.wet_bulb:.1f}°C")
    print()
    
    # Duggpunkt
    air3 = MoistAir(temperature=temp, dew_point=10.0, pressure=pressure)
    print(f"Fra duggpunkt (10°C):")
    print(f"  Relativ fuktighet: {air3.relative_humidity:.1f}%")
    print(f"  Fuktighetsforhold: {air3.humidity_ratio:.6f} kg/kg")
    print(f"  Våtkule: {air3.wet_bulb:.1f}°C")
    print()
    
    # Våtkule
    air4 = MoistAir(temperature=temp, wet_bulb=15.0, pressure=pressure)
    print(f"Fra våtkule (15°C):")
    print(f"  Relativ fuktighet: {air4.relative_humidity:.1f}%")
    print(f"  Fuktighetsforhold: {air4.humidity_ratio:.6f} kg/kg")
    print(f"  Duggpunkt: {air4.dew_point:.1f}°C")
    print()

def demo_engine_selection():
    """Demonstrerer valg av termodynamisk engine."""
    print("=== ENGINE-VALG ===")
    
    temp, rh = 25.0, 50.0
    
    # ASHRAE engine (standard)
    air_ashrae = MoistAir(temperature=temp, relative_humidity=rh, engine="ASHRAE")
    print(f"ASHRAE Engine:")
    print(f"  Fuktighetsforhold: {air_ashrae.humidity_ratio:.6f} kg/kg")
    print(f"  Våtkule: {air_ashrae.wet_bulb:.2f}°C")
    print(f"  Entalpi: {air_ashrae.enthalpy:.1f} kJ/kg")
    print()
    
    # CoolProp engine (hvis tilgjengelig)
    try:
        air_coolprop = MoistAir(temperature=temp, relative_humidity=rh, engine="CoolProp")
        print(f"CoolProp Engine:")
        print(f"  Fuktighetsforhold: {air_coolprop.humidity_ratio:.6f} kg/kg")
        print(f"  Våtkule: {air_coolprop.wet_bulb:.2f}°C")
        print(f"  Entalpi: {air_coolprop.enthalpy:.1f} kJ/kg")
        
        # Sammenlign forskjellene
        diff_w = abs(air_ashrae.humidity_ratio - air_coolprop.humidity_ratio)
        diff_wb = abs(air_ashrae.wet_bulb - air_coolprop.wet_bulb)
        diff_h = abs(air_ashrae.enthalpy - air_coolprop.enthalpy)
        
        print(f"\nForskjeller (CoolProp - ASHRAE):")
        print(f"  Fuktighetsforhold: {diff_w:.2e} kg/kg")
        print(f"  Våtkule: {diff_wb:.3f}°C")
        print(f"  Entalpi: {diff_h:.2f} kJ/kg")
        
    except Exception as e:
        print(f"CoolProp Engine: Ikke tilgjengelig ({str(e)})")
        print("  Installer med: pip install CoolProp")
    print()

def demo_psychrometric_calculations():
    """Demonstrerer bruk av Psychrometrics-klassen."""
    print("=== PSYKROMETRISKE BEREGNINGER ===")
    
    # Mixing av to luftstrømmer
    air1 = MoistAir(temperature=25.0, relative_humidity=30.0)  # Tørr luft
    air2 = MoistAir(temperature=20.0, relative_humidity=80.0)  # Fuktig luft
    
    print(f"Luftstrøm 1: {air1.temperature:.1f}°C, {air1.relative_humidity:.1f}% RH")
    print(f"Luftstrøm 2: {air2.temperature:.1f}°C, {air2.relative_humidity:.1f}% RH")
    
    # Blanding (50/50)
    mixed = Psychrometrics.mixing_ratio(air1, 1.0, air2, 1.0)
    print(f"Blandet luft: {mixed.temperature:.1f}°C, {mixed.relative_humidity:.1f}% RH")
    print(f"  Fuktighetsforhold: {mixed.humidity_ratio:.6f} kg/kg")
    print()
    
    # Sensibel kjøling
    original = MoistAir(temperature=30.0, relative_humidity=40.0)
    cooled = Psychrometrics.sensible_cooling(original, 25.0)
    
    print(f"Sensibel kjøling:")
    print(f"  Før: {original.temperature:.1f}°C, {original.relative_humidity:.1f}% RH")
    print(f"  Etter: {cooled.temperature:.1f}°C, {cooled.relative_humidity:.1f}% RH")
    print(f"  Fuktighetsforhold uendret: {abs(original.humidity_ratio - cooled.humidity_ratio) < 1e-6}")
    print()

def demo_extreme_conditions():
    """Demonstrerer beregninger under ekstreme forhold."""
    print("=== EKSTREME FORHOLD ===")
    
    test_cases = [
        ("Kaldt og tørt", -20.0, 30.0),
        ("Varmt og fuktig", 45.0, 90.0),
        ("Standard kontor", 22.0, 45.0),
        ("Tropisk klima", 35.0, 80.0),
        ("Ørken", 50.0, 10.0)
    ]
    
    print(f"{'Tilstand':<15} {'Temp':<6} {'RH':<4} {'Våtkule':<8} {'Entalpi':<8} {'Tetthet':<8}")
    print("-" * 65)
    
    for name, temp, rh in test_cases:
        try:
            air = MoistAir(temperature=temp, relative_humidity=rh)
            print(f"{name:<15} {temp:<6.1f} {rh:<4.0f} {air.wet_bulb:<8.1f} {air.enthalpy:<8.1f} {air.density:<8.3f}")
        except Exception as e:
            print(f"{name:<15} {temp:<6.1f} {rh:<4.0f} {'ERROR':<24}")
    print()

def demo_performance_comparison():
    """Demonstrerer ytelsessammenligning av forskjellige beregninger."""
    print("=== YTELSESTEST ===")
    
    # Test data
    n_iterations = 1000
    test_conditions = [(20 + i*0.1, 40 + i*0.2) for i in range(100)]
    
    # Test forskjellige beregningstyper
    print(f"Tester {n_iterations} iterasjoner med {len(test_conditions)} forskjellige tilstander...")
    
    # MoistAir opprettelse
    start_time = time.time()
    for _ in range(n_iterations//100):
        for temp, rh in test_conditions:
            air = MoistAir(temperature=temp, relative_humidity=rh)
    creation_time = time.time() - start_time
    
    # Egenskapsberegninger
    air = MoistAir(temperature=25.0, relative_humidity=50.0)
    start_time = time.time()
    for _ in range(n_iterations):
        _ = air.wet_bulb, air.dew_point, air.enthalpy, air.density
    properties_time = time.time() - start_time
    
    print(f"Opprettelse av MoistAir: {creation_time*1000:.2f} ms")
    print(f"Egenskapsberegninger: {properties_time*1000:.2f} ms")
    print(f"Gjennomsnitt per operasjon: {(creation_time + properties_time)/n_iterations*1000000:.2f} μs")
    print()

if __name__ == "__main__":
    print("HXKit Termodynamiske Beregninger Demo")
    print("=" * 50)
    
    demo_basic_usage()
    demo_different_input_methods()
    demo_engine_selection()
    demo_psychrometric_calculations()
    demo_extreme_conditions()
    demo_performance_comparison()
    
    print("\nDemo fullført! 🎉")
    print("\nTilgjengelige engines:")
    print("- ASHRAE: Standard implementasjon (alltid tilgjengelig)")
    print("- CoolProp: Høy presisjon (pip install CoolProp)")
    print("\nFor mer informasjon, se dokumentasjonen eller andre eksempler.")