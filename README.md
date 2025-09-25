# HXKit

Et Python-bibliotek for å bygge varmevekslermodeller, med fokus på platevarmevekslere for fuktig luft.

## Oversikt

HXKit inneholder byggesteiner for termodynamikk og strømningsberegninger som kan brukes til å sette opp beregningsmodeller for platevarmevekslere. Biblioteket er designet for å være modulært og utvidbart, slik at andre geometrier kan legges til senere.

## Hovedfunksjoner

- **Termodynamikk**: Psykrometriske beregninger for fuktig luft med modulær engine-støtte
- **Strømningsberegninger**: Trykkfall og massestrømfordelinger
- **Varmeoverføring**: Varmeoverføringskoeffisienter og effectiveness-NTU metoden
- **Plategeometrier**: Beskrivelse av platevarmevekslergeometri
- **Komplett analyse**: Integrert analyse av platevarmevekslere
- **Modulære engines**: Støtte for CoolProp, RefProp og andre termodynamiske biblioteker

## Installasjon

### Standard installasjon

```bash
pip install hxkit
```

### Fra kildekode (utviklingsmodus)

```bash
git clone https://github.com/kjelkols/hxkit.git
cd hxkit
pip install -e .
```

### Med ekstrafunksjoner

```bash
# For utvikling
pip install hxkit[dev]

# For plotting
pip install hxkit[plotting]

# For web-applikasjoner  
pip install hxkit[web]
```

## Rask start

```python
import hxkit
from hxkit import MoistAir, PlateHeatExchanger, HeatExchangerCore
from hxkit.geometries import GeometryFactory

# Lag plategeometri
plate_geom = GeometryFactory.standard_plate("medium")

# Lag varmevekslerkjerne (21 plater, 10+10 kanaler)
core = HeatExchangerCore(21, plate_geom, 10, 10)

# Definer lufttilstander
hot_inlet = MoistAir(temperature=22.0, relative_humidity=40.0)  # Innelluft
cold_inlet = MoistAir(temperature=-10.0, relative_humidity=80.0)  # Uteluft

# Utfør analyse
hx = PlateHeatExchanger(core)
results = hx.analyze(hot_inlet, cold_inlet, 
                    hot_mass_flow=0.1, cold_mass_flow=0.1)

print(f"Varmeoverføring: {results['heat_transfer_rate']/1000:.2f} kW")
print(f"Effectiveness: {results['effectiveness']:.3f}")
print(f"Utløpstemperaturer: {results['hot_outlet'].temperature:.1f}°C / {results['cold_outlet'].temperature:.1f}°C")
```

## Modulstruktur

### `hxkit.thermodynamics`
- `MoistAir`: Klasse for fuktig luft med psykrometriske egenskaper
- `Psychrometrics`: Statiske metoder for psykrometriske beregninger

### `hxkit.fluid_flow`
- `FlowCalculator`: Strømningsberegninger og trykkfall
- `MassFlowDistribution`: Massestrømfordelinger i parallelle kanaler

### `hxkit.heat_transfer`
- `HeatTransferCoefficients`: Varmeoverføringskoeffisienter og Nusselt-tall
- `EffectivenessNTU`: Effectiveness-NTU metoden for varmeveksleranalyse

### `hxkit.geometries`
- `PlateGeometry`: Beskrivelse av platevarmevekslergeometri
- `HeatExchangerCore`: Komplett kjernebeskrivelse
- `GeometryFactory`: Factory for standard geometrier

### `hxkit.plate_heat_exchanger`
- `PlateHeatExchanger`: Hovedklasse som kombinerer alle komponenter

## Termodynamiske Engines

HXKit støtter forskjellige termodynamiske engines for økt nøyaktighet:

### Standard bruk (ASHRAE-basert)
```python
# Standard ASHRAE-beregninger (rask og nøyaktig for vanlige forhold)
air = MoistAir(temperature=25.0, relative_humidity=50.0)

# Eksplisitt ASHRAE engine (identisk med standard)
air = MoistAir(temperature=25.0, relative_humidity=50.0, engine="ASHRAE")
```

### CoolProp engine for høy nøyaktighet
```python
# CoolProp engine (krever: pip install CoolProp)
air = MoistAir(temperature=25.0, relative_humidity=50.0, engine="CoolProp")

# Hvis CoolProp ikke er installert, faller systemet automatisk 
# tilbake til ASHRAE med en advarsel
```

### Tilgjengelige Engines
- **"ASHRAE"**: Standard ASHRAE-baserte beregninger (alltid tilgjengelig)
- **"CoolProp"**: Høy-presisjon CoolProp-beregninger (krever CoolProp installasjon)

Ukjente engine-navn vil gi advarsel og bruke ASHRAE som fallback.

## Eksempler

Se `examples/` mappen for detaljerte eksempler:

- `basic_example.py`: Grunnleggende bruk av biblioteket  
- `simple_psychrometric.py`: Enkle psykrometriske beregninger
- `performance_test.py`: Ytelsestesting av beregninger
- `fastapi_server.py`: Web API server med FastAPI
- `streamlit_app.py`: Interaktiv web-app med Streamlit

## Testing

Kjør tester med pytest:

```bash
pytest tests/
```

## Utvidelser

Biblioteket er designet for å være utvidbart:

### Nye geometrier
Legg til nye geometriklasser i `geometries.py` modulen:

```python
class TubeGeometry:
    def __init__(self, inner_diameter, outer_diameter, length):
        # Implementer tube geometri
        pass
```

### Nye korrelasjoner
Legg til nye varmeoverføringskorrelasjoner i `heat_transfer.py`:

```python
def new_correlation(Re, Pr):
    # Implementer ny korrelasjon
    return Nu
```

## Avhengigheter

- numpy >= 1.20.0
- scipy >= 1.7.0  
- pandas >= 1.3.0

### Valgfrie avhengigheter

For plotting og visualisering:
```bash
pip install hxkit[plotting]
```

For utvikling:
```bash
pip install hxkit[dev]
```

## Bidrag

1. Fork repositoriet
2. Lag en feature branch (`git checkout -b feature/ny-feature`)
3. Commit endringene (`git commit -am 'Legg til ny feature'`)
4. Push til branchen (`git push origin feature/ny-feature`)
5. Lag en Pull Request

## Lisens

MIT License - se LICENSE filen for detaljer.

## Forfattere

- Kjell Kolsaker - Initial work

## Anerkjennelser

- Basert på ASHRAE fundamentals for psykrometriske beregninger
- Varmeoverføringskorrelasjoner fra akademisk litteratur