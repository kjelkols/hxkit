"""
Test av specific_volume tillegg og web kalkulator fiks.
"""

from hxkit.thermodynamics import MoistAir
from hxkit.api.adapters import ThermodynamicsAdapter
from hxkit.schemas.thermodynamics_schemas import MoistAirInput

# Test at specific_volume fungerer
air = MoistAir(temperature=25.0, pressure=101325.0, relative_humidity=60.0)

print("Testing MoistAir specific_volume property:")
print(f"Density: {air.density:.4f} kg/m³")
print(f"Specific volume: {air.specific_volume:.4f} m³/kg")
print(f"Check (1/density): {1/air.density:.4f} m³/kg")

# Test API adapter
print("\nTesting API adapter with all properties:")
schema_input = MoistAirInput(
    temperature=25.0,
    pressure=101325.0,
    relative_humidity=60.0,
    humidity_ratio=None,
    dew_point=None,
    wet_bulb=None
)

air_from_schema = ThermodynamicsAdapter.from_schema(schema_input)
schema_output = ThermodynamicsAdapter.to_schema(air_from_schema)

print(f"Temperature: {schema_output.temperature} °C")
print(f"Relative humidity: {schema_output.relative_humidity:.1f} %")
print(f"Dew point: {schema_output.dew_point:.1f} °C")
print(f"Wet bulb: {schema_output.wet_bulb:.1f} °C")
print(f"Density: {schema_output.density:.4f} kg/m³")
print(f"Specific volume: {schema_output.specific_volume:.4f} m³/kg")
print(f"Enthalpy: {schema_output.enthalpy:.0f} kJ/kg")

print("\n✅ All properties are available - web calculator should work now!")