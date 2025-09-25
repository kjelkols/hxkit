# HXKit Termodynamikk Dokumentasjon

Denne dokumentasjonen beskriver termodynamikk-modulen i HXKit biblioteket, som inneholder klasser og funksjoner for psykrometriske beregninger og termodynamiske egenskaper for fuktig luft.

## Innholdsfortegnelse

- [Oversikt](#oversikt)
- [MoistAir Klassen](#moistair-klassen)
- [Psykrometriske Egenskaper](#psykrometriske-egenskaper)
- [Constructors](#constructors)
- [Psychrometrics Klassen](#psychrometrics-klassen)
- [Algoritmer og Referanser](#algoritmer-og-referanser)
- [Eksempler](#eksempler)
- [API Referanse](#api-referanse)

## Oversikt

Termodynamikk-modulen implementerer nøyaktige psykrometriske beregninger basert på ASHRAE Fundamentals. Modulen støtter:

- ✅ Beregning av alle psykrometriske egenskaper fra minimal input
- ✅ Støtte for fire ulike input-parametre (RH, fuktighetsforhold, våtkule, duggpunkt)
- ✅ Nøyaktige våtkule-beregninger med ASHRAE-algoritmer
- ✅ Ytelsesoptimalisert med cached properties
- ✅ Fysisk validerte beregninger med feilhåndtering

## MoistAir Klassen

`MoistAir` er hovedklassen for psykrometriske beregninger. Den tar minimal input og beregner alle termodynamiske egenskaper.

### Constructor

```python
MoistAir(temperature: float, 
         humidity_ratio: Optional[float] = None,
         relative_humidity: Optional[float] = None, 
         wet_bulb: Optional[float] = None,
         dew_point: Optional[float] = None, 
         pressure: float = 101325)
```

**Parametre:**
- `temperature` (float): Tørrkuletemperatur [°C]
- `pressure` (float): Trykk [Pa] (standard: 101325 Pa = 1 atm)
- **Nøyaktig én** av følgende fuktighetsparametre må oppgis:
  - `relative_humidity` (float): Relativ fuktighet [%] (0-100)
  - `humidity_ratio` (float): Fuktighetsforhold [kg_vanndamp/kg_tørr_luft]
  - `wet_bulb` (float): Våtkuletemperatur [°C]
  - `dew_point` (float): Duggpunkt [°C]

**Eksempler:**
```python
from hxkit.thermodynamics import MoistAir

# Fra relativ fuktighet
air1 = MoistAir(temperature=25.0, relative_humidity=60.0)

# Fra fuktighetsforhold
air2 = MoistAir(temperature=25.0, humidity_ratio=0.012)

# Fra våtkuletemperatur
air3 = MoistAir(temperature=30.0, wet_bulb=22.0)

# Fra duggpunkt
air4 = MoistAir(temperature=25.0, dew_point=16.7)
```

## Psykrometriske Egenskaper

Alle egenskaper er implementert som `cached_property` for optimal ytelse - de beregnes kun én gang ved første tilgang.

### Grunnleggende Egenskaper

#### `temperature` (float)
Tørrkuletemperatur [°C] - oppgitt ved konstruksjon.

#### `pressure` (float) 
Trykk [Pa] - oppgitt ved konstruksjon (standard: 101325 Pa).

#### `humidity_ratio` (float)
Fuktighetsforhold [kg_vanndamp/kg_tørr_luft] - beregnet eller oppgitt.

### Beregnede Egenskaper

#### `relative_humidity` (float)
Relativ fuktighet [%] (0-100).

**Formel:**
```
RH = 100 × (p_vapor / p_sat)
hvor p_vapor = w × p / (0.622 + w)
```

**Eksempel:**
```python
air = MoistAir(temperature=25.0, humidity_ratio=0.012)
print(f"Relativ fuktighet: {air.relative_humidity:.1f}%")  # → 60.1%
```

#### `dew_point` (float)
Duggpunkt temperatur [°C] - temperaturen hvor luften blir mettet.

**Algoritme:** Inverse Magnus-formel
- For T ≥ 0°C: `T_dp = 237.3 × ln(p/610.78) / (17.27 - ln(p/610.78))`
- For T < 0°C: `T_dp = 265.5 × ln(p/610.78) / (21.875 - ln(p/610.78))`

**Eksempel:**
```python
air = MoistAir(temperature=25.0, relative_humidity=60.0)
print(f"Duggpunkt: {air.dew_point:.1f}°C")  # → 16.7°C
```

#### `wet_bulb` (float)
Våtkuletemperatur [°C] - temperaturen et vått termometer ville vise.

**Algoritme:** ASHRAE iterativ metode basert på entalpi-balanse:
```
h_db = h_wb + (w_sat_wb - w) × c_pw × (T_db - T_wb)
```

Våtkule-temperaturen konvergeres ved Newton-Raphson iterasjon.

**Fysiske begrensninger:**
- `dew_point ≤ wet_bulb ≤ temperature`
- Ved 100% RH: `wet_bulb = temperature`

**Eksempel:**
```python
air = MoistAir(temperature=25.0, relative_humidity=60.0)
print(f"Våtkule: {air.wet_bulb:.1f}°C")  # → 19.4°C
```

#### `density` (float)
Tetthet av fuktig luft [kg/m³].

**Formel:**
```
ρ = p / (R_da × T × (1 + 1.608 × w))
hvor R_da = 287.055 J/kg·K (gaskonstant for tørr luft)
```

**Eksempel:**
```python
air = MoistAir(temperature=25.0, relative_humidity=60.0)
print(f"Tetthet: {air.density:.4f} kg/m³")  # → 1.1617 kg/m³
```

#### `specific_volume` (float)
Spesifikt volum av fuktig luft [m³/kg].

**Formel:**
```
v = 1 / ρ
```

**Eksempel:**
```python
air = MoistAir(temperature=25.0, relative_humidity=60.0)
print(f"Spesifikt volum: {air.specific_volume:.4f} m³/kg")  # → 0.8608 m³/kg
```

#### `enthalpy` (float)
Entalpi [kJ/kg_tørr_luft] - totalt varmeinnhold.

**Formel:**
```
h = c_pa × T + w × (h_fg + c_pv × T)
h = 1.006 × T + w × (2501 + 1.86 × T)
```

hvor:
- `c_pa = 1.006 kJ/kg·K` (spesifikk varmekapasitet tørr luft)
- `h_fg = 2501 kJ/kg` (fordampingsvarme ved 0°C)
- `c_pv = 1.86 kJ/kg·K` (spesifikk varmekapasitet vanndamp)

**Eksempel:**
```python
air = MoistAir(temperature=25.0, relative_humidity=60.0)
print(f"Entalpi: {air.enthalpy:.1f} kJ/kg")  # → 55.4 kJ/kg
```

## Constructors

### Fra Relativ Fuktighet
```python
air = MoistAir(temperature=25.0, relative_humidity=60.0)
```
**Bruk:** Mest vanlige input for komfortberegninger.

### Fra Fuktighetsforhold
```python
air = MoistAir(temperature=25.0, humidity_ratio=0.012)
```
**Bruk:** Direkte termodynamiske beregninger, blanding av luftstrømmer.

### Fra Våtkuletemperatur
```python
air = MoistAir(temperature=30.0, wet_bulb=22.0)
```
**Bruk:** Fra målinger med våtkule-termometer, kjøleanlegg.

**Validering:** `wet_bulb ≤ temperature` (kaster `ValueError` hvis ikke oppfylt)

### Fra Duggpunkt
```python
air = MoistAir(temperature=25.0, dew_point=16.7)
```
**Bruk:** Fra dugpunkt-målinger, kondensasjonsproblematikk.

## Psychrometrics Klassen

Statisk klasse med hjelpefunksjoner for psykrometriske beregninger.

### `mixing_ratio()`
Beregner blandingstilstand for to luftstrømmer.

```python
@staticmethod
def mixing_ratio(state1: MoistAir, mass_flow1: float, 
                state2: MoistAir, mass_flow2: float) -> MoistAir
```

**Algoritme:** Konservering av masse og entalpi:
```
h_mixed = (h₁ × ṁ₁ + h₂ × ṁ₂) / (ṁ₁ + ṁ₂)
w_mixed = (w₁ × ṁ₁ + w₂ × ṁ₂) / (ṁ₁ + ṁ₂)
```

**Eksempel:**
```python
from hxkit.thermodynamics import MoistAir, Psychrometrics

# To luftstrømmer
air1 = MoistAir(temperature=30.0, relative_humidity=40.0)  # Varm, tørr
air2 = MoistAir(temperature=20.0, relative_humidity=80.0)  # Kald, fuktig

# Blanding
mixed = Psychrometrics.mixing_ratio(air1, 0.5, air2, 0.3)
print(f"Blandingstemperatur: {mixed.temperature:.1f}°C")
print(f"Blandings-RH: {mixed.relative_humidity:.1f}%")
```

### `sensible_cooling()`
Beregner utløpstilstand ved sensibel kjøling (konstant fuktighetsforhold).

```python
@staticmethod
def sensible_cooling(inlet: MoistAir, outlet_temp: float) -> MoistAir
```

**Eksempel:**
```python
inlet = MoistAir(temperature=30.0, relative_humidity=50.0)
outlet = Psychrometrics.sensible_cooling(inlet, 20.0)

print(f"Innløp: {inlet.temperature}°C, {inlet.relative_humidity:.1f}% RH")
print(f"Utløp: {outlet.temperature}°C, {outlet.relative_humidity:.1f}% RH")
# Fuktighetsforholdet forblir konstant
```

## Algoritmer og Referanser

### Magnus Formel (Metningstrykk)
Brukt for å beregne metningstrykk for vanndamp:

**For væske (T ≥ 0°C):**
```
p_sat = 610.78 × exp(17.27 × T / (T + 237.3))
```

**For is (T < 0°C):**
```
p_sat = 610.78 × exp(21.875 × T / (T + 265.5))
```

### ASHRAE Våtkule-algoritme
Implementerer ASHRAE Fundamentals psykrometrisk ligning:

```
h_db = h_wb + (w_sat_wb - w) × c_pw × (T_db - T_wb)
```

Løses iterativt med Newton-Raphson metode for optimal konvergens.

### Ytelsesoptimalisering
- **`@cached_property`**: Dyre beregninger utføres kun én gang
- **Iterative algoritmer**: Optimalisert konvergenskriterier
- **Fysisk validering**: Forhindrer ugyldige tilstander

## Eksempler

### Grunnleggende Bruk
```python
from hxkit.thermodynamics import MoistAir

# Opprett lufttilstand
air = MoistAir(temperature=25.0, relative_humidity=60.0)

# Tilgang til alle egenskaper
print(f"Temperatur: {air.temperature}°C")
print(f"Relativ fuktighet: {air.relative_humidity:.1f}%")
print(f"Duggpunkt: {air.dew_point:.1f}°C")
print(f"Våtkule: {air.wet_bulb:.1f}°C")
print(f"Fuktighetsforhold: {air.humidity_ratio:.6f} kg/kg")
print(f"Tetthet: {air.density:.4f} kg/m³")
print(f"Entalpi: {air.enthalpy:.1f} kJ/kg")
```

### Varmeveksler Analyse
```python
# Innløpsforhold
hot_inlet = MoistAir(temperature=40.0, relative_humidity=30.0)
cold_inlet = MoistAir(temperature=20.0, relative_humidity=70.0)

print("=== VARMEVEKSLER ANALYSE ===")
print(f"Varm side inn: {hot_inlet.temperature}°C, {hot_inlet.relative_humidity:.1f}% RH")
print(f"Kald side inn: {cold_inlet.temperature}°C, {cold_inlet.relative_humidity:.1f}% RH")

# Entalpi-differanse
delta_h = hot_inlet.enthalpy - cold_inlet.enthalpy
print(f"Entalpi-differanse: {delta_h:.1f} kJ/kg")
```

### Luftbehandling
```python
from hxkit.thermodynamics import MoistAir, Psychrometrics

# Uteluft og resirkulert luft
outdoor = MoistAir(temperature=35.0, relative_humidity=60.0)
recirculated = MoistAir(temperature=24.0, relative_humidity=50.0)

# Blanding (70% resirk, 30% uteluft)
mixed = Psychrometrics.mixing_ratio(recirculated, 0.7, outdoor, 0.3)

print("=== LUFTBEHANDLING ===")
print(f"Uteluft: {outdoor.temperature}°C, {outdoor.relative_humidity:.1f}% RH")
print(f"Resirkulert: {recirculated.temperature}°C, {recirculated.relative_humidity:.1f}% RH")
print(f"Blandet luft: {mixed.temperature:.1f}°C, {mixed.relative_humidity:.1f}% RH")

# Kjøling til 18°C
cooled = Psychrometrics.sensible_cooling(mixed, 18.0)
print(f"Etter kjøling: {cooled.temperature}°C, {cooled.relative_humidity:.1f}% RH")
```

### Kondensasjon og Fuktproblemer
```python
# Innendørs forhold
indoor = MoistAir(temperature=22.0, relative_humidity=45.0)

# Sjekk kondensasjon på kalde overflater
wall_temp = 10.0
if wall_temp < indoor.dew_point:
    print(f"⚠️  KONDENSASJON på vegg ved {wall_temp}°C!")
    print(f"Duggpunkt: {indoor.dew_point:.1f}°C")
else:
    print(f"✅ Ingen kondensasjon på vegg ved {wall_temp}°C")
    print(f"Duggpunkt: {indoor.dew_point:.1f}°C")
```

## API Referanse

### MoistAir Klasse

```python
class MoistAir:
    def __init__(self, temperature: float, 
                 humidity_ratio: Optional[float] = None,
                 relative_humidity: Optional[float] = None, 
                 wet_bulb: Optional[float] = None,
                 dew_point: Optional[float] = None, 
                 pressure: float = 101325) -> None
    
    # Grunnleggende egenskaper
    temperature: float              # [°C]
    pressure: float                 # [Pa]
    humidity_ratio: float           # [kg/kg]
    
    # Beregnede egenskaper (cached_property)
    relative_humidity: float        # [%]
    dew_point: float               # [°C]  
    wet_bulb: float                # [°C]
    density: float                 # [kg/m³]
    specific_volume: float         # [m³/kg]
    enthalpy: float               # [kJ/kg]
```

### Psychrometrics Klasse

```python
class Psychrometrics:
    @staticmethod
    def mixing_ratio(state1: MoistAir, mass_flow1: float,
                    state2: MoistAir, mass_flow2: float) -> MoistAir
    
    @staticmethod  
    def sensible_cooling(inlet: MoistAir, outlet_temp: float) -> MoistAir
```

### Feilhåndtering

**ValueError** kastes ved:
- Manglende eller flere fuktighetsparametre
- Våtkuletemperatur høyere enn tørrkuletemperatur
- Fysisk umulige verdier

**Eksempel:**
```python
try:
    # Dette vil feile - våtkuletemperatur høyere enn tørrkuletemperatur
    air = MoistAir(temperature=20.0, wet_bulb=25.0)
except ValueError as e:
    print(f"Feil: {e}")
```

---

## Referanser

1. **ASHRAE Fundamentals Handbook** - Psykrometriske beregninger
2. **Magnus Formula** - Metningstrykk for vanndamp  
3. **NIST Webbook** - Termodynamiske data for vanndamp
4. **ISO 12571** - Hygrotermiske egenskaper for bygningsmaterialer

---

*Dokumentasjon generert for HXKit versjon 1.0*  
*Sist oppdatert: September 2025*