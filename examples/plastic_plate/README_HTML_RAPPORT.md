# HTML Rapport Generator

HTML rapport generatoren for Plastic Plate Heat Exchanger lager frittstående, profesjonelle rapporter med interaktive visualiseringer.

## Funksjoner

### `generate_html_report()`
Genererer komplett HTML rapport fra `PlasticPlateHeatExchangerOutput` data.

```python
from hxkit.visualization import generate_html_report

html_content = generate_html_report(
    output_data=analysis_results,
    title="Min Varmeveksler Analyse",
    description="Detaljert analyse av plastic plate varmeveksler"
)
```

### `save_html_report()`
Genererer og lagrer HTML rapport direkte til fil.

```python
from hxkit.visualization import save_html_report

save_html_report(
    output_data=analysis_results,
    filepath="rapport.html",
    title="Varmeveksler Rapport",
    description="Analyse utført 28. september 2025"
)
```

## Rapport innhold

Rapporten inneholder følgende seksjoner:

### 1. Sammendrag
- Effektivitet (%)
- Varmeoverføringsrate (kW)
- NTU (Number of Transfer Units)
- Utløpstemperatur varm side

### 2. Ytelsesparametre
- Detaljerte ytelsesmålinger
- Trykkfall for begge sider
- Varmeoverføringskoeffisient (hvis tilgjengelig)

### 3. Luftstrømmer ved utløp
- Termodynamiske egenskaper for varm og kald luftstrøm
- Massestrøm, volumstrøm og entalpistrøm
- Side-ved-side sammenligning

### 4. Faseendringer
- Kondensasjonsstatus og -rate
- Rimdannelse og tykkelse
- Visuelle statusindikatorer

### 5. Numerisk konvergens
- Konvergensstatus
- Antall iterasjoner
- Beregningstid og residualer

### 6. Temperaturfordeling (hvis grid data tilgjengelig)
- **Interaktive 2D heatmaps** for:
  - Plate temperaturer
  - Varm luft temperaturer  
  - Kald luft temperaturer
- **Temperaturprofil sammenligning** (linjediagram)

## 2D Temperatur Visualiseringer

Hvis `grid_results` er tilgjengelig i output dataene, genereres interaktive plott:

### Heatmaps
- **Fargekodede temperaturfelter** med viridis-inspirert fargepalett
- **Hover-effekter** som viser nøyaktige temperaturer
- **Automatisk skalering** basert på min/maks temperaturer
- **Responsive design** som fungerer på mobile enheter

### Temperaturprofil
- **Gjennomsnittlige temperaturer** langs lengdeaksen
- **Sammenligning** mellom plate, varm luft og kald luft
- **Interaktive linjer** med hover-informasjon

## Tekniske detaljer

### JavaScript biblioteker
- **Chart.js 4.4.0** - For alle plott og visualiseringer
- **Ingen eksterne avhengigheter** utover Chart.js CDN

### CSS styling
- **Responsive design** - Fungerer på desktop og mobil
- **Profesjonelt utseende** med moderne CSS
- **Print-vennlig** styling
- **Mørk/lys tilpasset** basert på brukerpreferanser

### Filstørrelse
- **Typisk størrelse**: 30-50 KB
- **Med store grid**: Kan nå 100+ KB
- **Komprimert JSON** data for effektivitet

## Eksempler

### Grunnleggende bruk
```python
from hxkit.schemas.plastic_plate_schemas import PlasticPlateHeatExchangerOutput
from hxkit.visualization import save_html_report

# ... lag eller hent analysis output_data ...

save_html_report(
    output_data=output_data,
    filepath="varmeveksler_rapport.html"
)

print("Åpne varmeveksler_rapport.html i nettleser")
```

### Med egendefinert tittel og beskrivelse
```python
save_html_report(
    output_data=output_data,
    filepath="detaljert_analyse.html",
    title="Plastic Plate Heat Exchanger - Prosjekt Alpha",
    description="Analyse av 1.4m × 1.4m varmeveksler for HVAC-system. Utført som del av energioptimalisering av kontorbygg."
)
```

### Batch generering av rapporter
```python
import os
from datetime import datetime

# Liste av analyseresultater
analyses = [result1, result2, result3]

# Opprett output mappe
os.makedirs("rapporter", exist_ok=True)

for i, result in enumerate(analyses):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"rapporter/analyse_{i+1}_{timestamp}.html"
    
    save_html_report(
        output_data=result,
        filepath=filepath,
        title=f"Analyse #{i+1}",
        description=f"Automatisk generert rapport {timestamp}"
    )
    
    print(f"Rapport {i+1} lagret: {filepath}")
```

### Kombinert med eksisterende analyse
```python
from hxkit import PlasticPlateHeatExchanger
from hxkit.schemas import PlasticPlateHeatExchangerInput
from hxkit.visualization import save_html_report

# 1. Kjør analyse
input_config = PlasticPlateHeatExchangerInput(...)
heat_exchanger = PlasticPlateHeatExchanger(...)
results = heat_exchanger.analyze(...)

# 2. Konverter til output schema (implementeres senere)
output_data = create_output_schema(input_config, results)

# 3. Generer rapport
save_html_report(
    output_data=output_data,
    filepath="analyse_rapport.html",
    title="Varmeveksler Analyse Rapport",
    description="Komplett analyse med 2D temperaturfordeling"
)
```

## Feilsøking

### Grid data ikke tilgjengelig
Hvis `grid_results` er `None` eller mangler, viser rapporten:
- Meldinger om manglende temperaturdata i plott-seksjonene
- Alle andre seksjoner fungerer normalt

### Chart.js ikke lastet
Hvis internett-tilkobling mangler:
- Temperaturseksjonene viser bare placeholders
- Resten av rapporten fungerer normalt
- Vurder å laste ned Chart.js lokalt for offline bruk

### Store filer
For meget store grid (>100×100 celler):
- Filstørrelsen kan bli >1 MB
- Vurder å redusere grid oppløsning
- Eller bruk dataakomprimering

## Utvidelses muligheter

### Egendefinerte fargepaletter
Endre `getTemperatureColor()` funksjonen for andre fargevalg.

### Flere plott-typer
Legg til:
- Hastighetsfelter
- Fuktighetsfordelinger
- Trykkfall visualiseringer

### Export funksjoner
Legg til knopper for:
- PNG export av plott
- PDF rapport generering
- Excel data export

## Se også

- `examples/plastic_plate/html_rapport_demo.py` - Komplett eksempel
- `hxkit.schemas.plastic_plate_schemas` - Schema definisjonier
- `hxkit.visualization` - Andre visualiseringsmetoder