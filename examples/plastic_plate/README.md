# Plastic Plate Heat Exchanger Examples

Denne mappen inneholder eksempler spesifikt for plastic plate heat exchangers.

## 📁 Filer

### Core Examples

- **`plastic_plate_demo.py`** - Grunnleggende demo av plastic plate heat exchanger
  - Viser hvordan man oppretter og konfigurerer en plastic plate varmeveksler
  - Demonstrerer forskjellige strømningskonfigurasjoner
  - Enkelt eksempel for å komme i gang

- **`input_to_output_example.py`** - Komplett input-til-output eksempel
  - Tar spesifiserte dimensjoner (1.4×1.4 m, 10 plater)
  - Simulerer fullstendig analyse med realistiske resultater
  - Genererer både input og output JSON-filer
  - Viser detaljerte ytelsesresultater

### Pydantic Schema Examples

- **`pydantic_plastic_plate_example.py`** - Input schema demo
  - Demonstrerer bruk av Pydantic input-skjemaer
  - Viser validering og feilhåndtering
  - Eksempler på forskjellige konfigurasjoner

- **`pydantic_complete_example.py`** - Fullstendig schema demo
  - Kombinerer både input og output schemas
  - JSON serialisering og deserialisering
  - API dokumentasjon generering
  - Komplett eksempel på schema-bruk

## 🚀 Kom i gang

### Enkel demo
```bash
python plastic_plate_demo.py
```

### Komplett analyse
```bash
python input_to_output_example.py
```

### Schema eksempler
```bash
python pydantic_plastic_plate_example.py
python pydantic_complete_example.py
```

## 📊 Hva eksemplene viser

- ✅ **Geometri-konfigurasjon**: Platebredde, -lengde, -tykkelse, antall plater
- ✅ **Strømningsretninger**: Counterflow, crossflow, parallelflow
- ✅ **Termodynamikk**: Fuktig luft, temperatur, fuktighet
- ✅ **Validering**: Pydantic schemas for type-sikkerhet
- ✅ **JSON I/O**: Serialisering for API og lagring
- ✅ **Ytelsesberegning**: Effektivitet, varmeoverføring, trykkfall

## 🔗 Relaterte moduler

- `hxkit.heatexchangers.plastic_plate` - Core implementasjon
- `hxkit.schemas.plastic_plate_schemas` - Pydantic schemas
- `hxkit.visualization` - 3D visualisering

## 📝 Noter

Alle eksempler bruker realistiske dimensjoner og operasjonsbetingelser for plastic plate heat exchangers. Resultatene er basert på forenklede modeller for demonstrasjonsformål.