# Plate Heat Exchanger Examples

Denne katalogen inneholder eksempler som bruker den generiske `PlateHeatExchanger` klassen med `PlateGeometry` og `HeatExchangerCore`.

## Eksempler

### basic_example.py
Grunnleggende eksempel som viser hvordan man oppretter og bruker en `PlateHeatExchanger`:
- Definerer geometri med `PlateGeometry`
- Oppretter `HeatExchangerCore` med plater og kanaler
- Kjører beregninger og viser resultater

### pydantic_example.py
Omfattende eksempel som viser Pydantic-integrasjon for validering og serialisering:
- Bruker Pydantic-skjemaer for input-validering
- Demonstrerer JSON serialisering/deserialisering
- Fullstendig input-til-output arbeidsflyt

### pydantic_example_simple.py
Forenklet versjon av Pydantic-eksemplet:
- Grunnleggende Pydantic-skjema bruk
- Enklere input-data struktur
- Rask introduksjon til skjema-validering

## Kjøring

Alle eksemplene kan kjøres direkte fra `examples/plate/` katalogen:

```bash
cd examples/plate
python basic_example.py
python pydantic_example.py
python pydantic_example_simple.py
```

## Relaterte eksempler

- `../plastic_plate/` - Eksempler for `PlasticPlateHeatExchanger`
- `../thermodynamics/` - Eksempler for termodynamiske beregninger
- `../webapi/` - Eksempler for web API integrasjon