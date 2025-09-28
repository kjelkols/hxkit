# Thermodynamics Module

This module provides thermodynamic calculations for moist air using both ASHRAE and CoolProp engines.

## 📁 Structure

- **`core.py`** - Main thermodynamics implementation
  - `MoistAir` class for moist air state calculations
  - `Psychrometrics` class for psychrometric calculations
  - Support for both ASHRAE and CoolProp engines

- **`__init__.py`** - Module exports

## 🏗️ Classes

### `MoistAir`
Represents a moist air state with thermodynamic properties.

```python
from hxkit.thermodynamics import MoistAir

# Create from temperature and relative humidity
air = MoistAir(temperature=25.0, pressure=101325, relative_humidity=60.0)

# Access properties
print(f"Density: {air.density} kg/m³")
print(f"Enthalpy: {air.enthalpy} kJ/kg")
print(f"Humidity ratio: {air.humidity_ratio} kg/kg")
```

### `Psychrometrics`
Static methods for psychrometric calculations.

```python
from hxkit.thermodynamics import Psychrometrics

# Calculate saturation pressure
p_sat = Psychrometrics.saturation_pressure(25.0)

# Calculate humidity ratio from relative humidity
w = Psychrometrics.humidity_ratio_from_relative_humidity(
    temperature=25.0, 
    relative_humidity=60.0, 
    pressure=101325
)
```

## 🔧 Engines

### ASHRAE Engine (Default)
- Built-in implementation based on ASHRAE formulations
- No external dependencies
- Good accuracy for typical HVAC conditions

### CoolProp Engine (Optional)
- High-accuracy thermodynamic library
- Requires `pip install CoolProp`
- Wider range of validity

```python
# Use specific engine
air = MoistAir(temperature=25.0, pressure=101325, 
               relative_humidity=60.0, engine="CoolProp")
```

## 📊 Properties Calculated

- Temperature (dry bulb, wet bulb, dew point)
- Humidity (relative humidity, humidity ratio)
- Density and specific volume  
- Enthalpy and entropy
- Saturation pressure

## 🔬 Validation

Properties are validated for physical consistency:
- Temperature limits: -50°C to 100°C
- Pressure limits: 10 kPa to 200 kPa  
- Humidity limits: 0% to 100% RH
- Warnings for extreme conditions

## 🧪 Testing

Comprehensive test suite covers:
- Engine consistency between ASHRAE and CoolProp
- Roundtrip calculations (e.g., RH → humidity ratio → RH)
- Extreme condition handling
- Input validation

## 📚 References

- ASHRAE Handbook - Fundamentals
- CoolProp thermodynamic library documentation
- Psychrometric chart calculations