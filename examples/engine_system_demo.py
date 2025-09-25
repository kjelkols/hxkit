"""
Demo av det nye modulære engine-systemet i HXKit.

Viser hvordan man kan bruke forskjellige termodynamiske engines
for psykrometriske beregninger.
"""

from hxkit import MoistAir
from hxkit.thermodynamics.registry import EngineRegistry
from hxkit.thermodynamics.engines import ASHRAEEngine

def demo_basic_usage():
    """Demonstrerer grunnleggende bruk av MoistAir med og uten engines."""
    print("=== GRUNNLEGGENDE BRUK ===")
    
    # Standard bruk (ingen engine spesifisert)
    air1 = MoistAir(temperature=25.0, relative_humidity=50.0)
    print(f"Standard MoistAir:")
    print(f"  Temperatur: {air1.temperature:.1f}°C")
    print(f"  Relativ fuktighet: {air1.relative_humidity:.1f}%")
    print(f"  Fuktighetsforhold: {air1.humidity_ratio:.6f} kg/kg")
    print(f"  Duggpunkt: {air1.dew_point:.1f}°C")
    print(f"  Våtkule: {air1.wet_bulb:.1f}°C")
    print(f"  Entalpi: {air1.enthalpy:.1f} kJ/kg")
    print(f"  Tetthet: {air1.density:.3f} kg/m³")
    print()

def demo_engine_registry():
    """Demonstrerer bruk av engine registry."""
    print("=== ENGINE REGISTRY ===")
    
    # Opprett registry
    registry = EngineRegistry()
    
    # List tilgjengelige engines
    available = registry.list_available()
    print("Tilgjengelige engines:")
    for name, description in available.items():
        status = "✓" if "ikke tilgjengelig" not in description.lower() else "✗"
        print(f"  {status} {name}: {description}")
    print()
    
    # Bruk ASHRAE engine via registry
    engine = registry.get_engine("ashrae")
    print(f"ASHRAE Engine:")
    print(f"  Navn: {engine.name}")
    print(f"  Beskrivelse: {engine.description}")
    print(f"  Temperaturområde: {engine.valid_temperature_range[0]:.0f} til {engine.valid_temperature_range[1]:.0f}°C")
    print(f"  Trykkområde: {engine.valid_pressure_range[0]/1000:.0f} til {engine.valid_pressure_range[1]/1000:.0f} kPa")
    print()

def demo_direct_engine_calculations():
    """Demonstrerer direkte bruk av engine for beregninger."""
    print("=== DIREKTE ENGINE BEREGNINGER ===")
    
    engine = ASHRAEEngine()
    
    # Beregn egenskaper med forskjellige input
    test_cases = [
        {"relative_humidity": 50.0},
        {"humidity_ratio": 0.010},
        {"dew_point": 15.0},
        {"wet_bulb": 20.0}
    ]
    
    for i, humidity_input in enumerate(test_cases, 1):
        print(f"Test {i} - Input: {humidity_input}")
        
        try:
            properties = engine.calculate_properties(25.0, 101325.0, humidity_input)
            print(f"  Fuktighetsforhold: {properties['humidity_ratio']:.6f} kg/kg")
            print(f"  Relativ fuktighet: {properties['relative_humidity']:.1f}%")
            print(f"  Duggpunkt: {properties['dew_point']:.1f}°C")
            print(f"  våtkule: {properties['wet_bulb']:.1f}°C")
            print(f"  Entalpi: {properties['enthalpy']:.1f} kJ/kg")
        except Exception as e:
            print(f"  Feil: {e}")
        print()

def demo_moistair_with_engines():
    """Demonstrerer MoistAir med forskjellige engines."""
    print("=== MOISTAIR MED ENGINES ===")
    
    # Sammenlign standard vs engine
    conditions = [
        (20.0, 60.0),
        (30.0, 40.0),
        (-5.0, 80.0),
        (50.0, 30.0)
    ]
    
    print("Sammenligning Standard vs ASHRAE Engine:")
    print(f"{'Temp':<6} {'RH':<4} {'Standard W':<12} {'Engine W':<12} {'Diff':<10}")
    print("-" * 60)
    
    for temp, rh in conditions:
        # Standard
        air_std = MoistAir(temperature=temp, relative_humidity=rh)
        
        # Med ASHRAE engine
        engine = ASHRAEEngine()
        air_eng = MoistAir(temperature=temp, relative_humidity=rh, engine=engine)
        
        diff = abs(air_std.humidity_ratio - air_eng.humidity_ratio)
        
        print(f"{temp:<6.1f} {rh:<4.0f} {air_std.humidity_ratio:<12.6f} {air_eng.humidity_ratio:<12.6f} {diff:<10.2e}")

def demo_engine_validation():
    """Demonstrerer engine validering og advarsler."""
    print("\n=== ENGINE VALIDERING ===")
    
    engine = ASHRAEEngine()
    
    # Test normale verdier
    warnings = engine.validate_inputs(25.0, 101325.0, {"relative_humidity": 50.0})
    print(f"Normale verdier - Advarsler: {len(warnings)}")
    
    # Test ekstreme verdier
    warnings = engine.validate_inputs(-40.0, 50000.0, {"relative_humidity": 95.0})
    print(f"Ekstreme verdier - Advarsler: {len(warnings)}")
    for warning in warnings:
        print(f"  - {warning}")
    
    # Test ugyldige verdier
    try:
        engine.validate_inputs(25.0, 101325.0, {"relative_humidity": -10.0})
    except ValueError as e:
        print(f"Ugyldig verdi - Feil: {e}")

def demo_performance_comparison():
    """Demonstrerer ytelsessammenligning."""
    print("\n=== YTELSESSAMMENLIGNING ===")
    
    import time
    
    # Test data
    test_conditions = [(20 + i, 40 + i) for i in range(20)]
    
    # Standard MoistAir
    start_time = time.time()
    for temp, rh in test_conditions:
        air = MoistAir(temperature=temp, relative_humidity=rh)
        _ = air.dew_point, air.wet_bulb, air.enthalpy
    std_time = time.time() - start_time
    
    # Med ASHRAE engine
    engine = ASHRAEEngine()
    start_time = time.time()
    for temp, rh in test_conditions:
        air = MoistAir(temperature=temp, relative_humidity=rh, engine=engine)
        _ = air.dew_point, air.wet_bulb, air.enthalpy
    eng_time = time.time() - start_time
    
    print(f"Standard implementasjon: {std_time*1000:.2f} ms")
    print(f"ASHRAE engine: {eng_time*1000:.2f} ms")
    print(f"Forhold: {eng_time/std_time:.2f}x")

if __name__ == "__main__":
    print("HXKit Modulær Engine System Demo")
    print("=" * 50)
    
    demo_basic_usage()
    demo_engine_registry()
    demo_direct_engine_calculations()
    demo_moistair_with_engines()
    demo_engine_validation()
    demo_performance_comparison()
    
    print("\nDemo fullført! 🎉")
    print("\nTilgjengelige engines kan utvides med:")
    print("- CoolProp engine: pip install CoolProp")
    print("- RefProp engine: Krever NIST RefProp lisens")
    print("- Egendefinerte engines: Implementer ThermodynamicEngine interface")