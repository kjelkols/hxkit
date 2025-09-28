# Thermodynamics Examples

Denne mappen inneholder eksempler spesifikt for thermodynamiske beregninger av fuktig luft.

## 📁 Filer

### Core Psychrometric Examples

- **`simple_psychrometric.py`** - Enkel psykrometrisk diagram generator
  - Genererer komplett psykrometrisk diagram med matplotlib
  - Bruker lokal HXKit implementasjon (ingen API avhengigheter)
  - Viser relativ fuktighet linjer og eksempel-punkter
  - Lagrer diagram som PNG-fil

- **`psychrometric_chart.py`** - Avansert psykrometrisk diagram
  - Genererer detaljerte psykrometriske diagrammer
  - Visualisering av lufttilstander og prosesslinjer
  - Plotting av komplekse prosesslinjer

### Interactive Examples

- **`moist_air_gui.py`** - GUI kalkulator for fuktig luft
  - Interaktiv calculator med grafisk grensesnitt
  - Real-time beregninger
  - Visuell feedback på egenskaper

### Engine System Examples

- **`engine_system_demo.py`** - Sammenligning av termodynamiske engines
  - Demonstrerer ASHRAE vs CoolProp engines
  - Ytelse og nøyaktighetssammenligning
  - Engine-switcher eksempel

## 🚀 Kom i gang

### Psykrometrisk diagram (enkel)
```bash
python simple_psychrometric.py
# Genererer psykrometrisk_diagram.png
# Krever matplotlib: pip install matplotlib
```

### Avansert psykrometrisk diagram
```bash
python psychrometric_chart.py
# Krever matplotlib: pip install matplotlib
```

### Interaktiv GUI
```bash  
python moist_air_gui.py
# Krever tkinter (vanligvis inkludert i Python)
```

### Engine sammenligning
```bash
python engine_system_demo.py
# Test både ASHRAE og CoolProp (hvis installert)
```

## 📊 Hva eksemplene viser

- ✅ **Fuktig luft egenskaper**: Temperatur, fuktighet, entalpi, tetthet
- ✅ **Psykrometriske beregninger**: Duggpunkt, våtkuletemperatur
- ✅ **Engine sammenligning**: ASHRAE vs CoolProp nøyaktighet
- ✅ **Visualisering**: Psykrometriske diagrammer og grafer
- ✅ **Interaktivitet**: GUI og real-time beregninger

## 🔬 Termodynamiske engines

### ASHRAE Engine (Standard)
- Innebygd implementasjon
- Ingen eksterne avhengigheter
- God nøyaktighet for HVAC-forhold

### CoolProp Engine (Valgfri)
```bash
pip install CoolProp
```
- Høy nøyaktighet termodynamisk bibliotek
- Bredere gyldighetsområde
- Støtter flere fluider

## 📈 Bruksområder

- **HVAC design**: Luftbehandlingsberegninger
- **Prosessoptimalisering**: Energi og fuktighetsbalanse
- **Validering**: Sammenligning med andre verktøy
- **Utdanning**: Læring av psykrometriske prinsipper

## 🔗 Relaterte moduler

- `hxkit.thermodynamics` - Core thermodynamics implementasjon
- `hxkit.schemas.thermodynamics_schemas` - Pydantic schemas
- `hxkit.visualization` - Plotting og visualisering

## 📝 Noter

Alle eksempler bruker realistiske lufttilstander og HVAC-betingelser. Resultatene er validert mot standard psykrometriske tabeller og diagrammer.