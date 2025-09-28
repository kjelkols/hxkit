# Plastic Plate Heat Exchanger Simulator

Interaktiv web-basert simulator for analyse av plastic plate varmeveksler med realtids beregninger og HTML-rapportgenerering.

## Funksjonalitet

### 🌐 Webgrensesnitt
- **Intuitivt form** for input av alle parametere
- **Preset-konfigurasjoner** for vanlige scenarioer
- **Sanntidsvalidering** av input-verdier
- **Responsive design** som fungerer på alle enheter

### 🔬 Simuleringsparametere

#### Geometri
- Platebredde og -lengde
- Platetykkelse og kanalhøyde
- Antall plater og materialevalg

#### Luftstrømmer
- Temperatur, trykk og fuktighet for begge strømmer
- Massestrøm for varm og kald luft
- Strømningsretninger (N/S/E/W)

#### Numeriske parametere
- Grid-oppløsning for 2D-beregninger
- Konvergenstoleranse og iterasjoner

### 📊 Resultater
- **HTML-rapport** med alle resultater
- **2D temperaturplott** (interaktive heatmaps)
- **Ytelsesmålinger** (effektivitet, NTU, varmeoverføring)
- **Detaljerte utløpsstrømmer**
- **Faseendringer** (kondensasjon/rim)

## Installasjon

### 1. Installer avhengigheter
```bash
cd examples/plastic_plate/simulator
pip install -r requirements.txt
```

### 2. Start simulatoren
```bash
python app.py
```

### 3. Åpne nettleser
Gå til: `http://localhost:5000`

## Bruk av simulatoren

### Steg 1: Fyll ut parametere
1. **Geometri**: Definer platestørrelse og konfiguration
2. **Strømmer**: Sett temperatur, trykk og massestrøm
3. **Numerisk**: Velg grid-oppløsning og konvergens

### Steg 2: Bruk presets (valgfritt)
- **Standard**: Typisk kommersiell konfigurasjon
- **Høy temperatur**: For høytemperatur applikasjoner  
- **Lav temperatur**: For kjøle-/kondensasjonsapplikasjoner

### Steg 3: Kjør simulering
- Klikk "Kjør Simulering"
- HTML-rapport lastes ned automatisk
- Se "Tidligere rapporter" for historikk

## Teknisk implementering

### Backend (Flask)
- **Form-håndtering**: Parsing og validering av input
- **Simuleringsmotor**: Beregninger av varmeoverføring
- **Rapportgenerering**: HTML-eksport med visualiseringer

### Frontend (HTML/CSS/JS)
- **Responsivt design**: Fungerer på mobil og desktop
- **Preset-konfigurasjon**: Hurtig lasting av typiske scenarioer
- **Input-validering**: Sanntidssjekk av parametere

### Beregningsmodul
- **Varmeoverføringsberegninger**: NTU-metode og effektivitet
- **Trykkfallestimering**: Basert på geometri og strømning  
- **2D temperaturfordeling**: Grid-basert numerisk løsning
- **Faseendringer**: Kondensasjon og rimdannelse

## Eksempel på bruk

### Scenario 1: Standard ventilasjonssystem
```
Geometri: 0.6m × 1.2m, 20 plater
Varm luft: 35°C, 60% RH, 2.5 kg/s
Kald luft: 15°C, 40% RH, 2.0 kg/s
```

### Scenario 2: Høytemperatur prosess  
```
Geometri: 0.8m × 1.5m, 25 plater
Varm luft: 60°C, 80% RH, 3.0 kg/s
Kald luft: 5°C, 30% RH, 2.5 kg/s
```

## Utvidelsesmuligheter

### Avanserte beregninger
- Implementer detaljerte CFD-beregninger
- Legg til frostmodellering
- Inkluder materialegenskaper

### Flere visualiseringer
- 3D temperaturplott
- Animert strømningsvisualisering  
- Sammenlignende analyser

### API-integrasjon
- RESTful API for automatisering
- Batch-kjøring av simuleringer
- Database-lagring av resultater

## Feilsøking

### Vanlige problemer
- **Import-feil**: Sjekk at HXKit er riktig installert
- **Port opptatt**: Endre port i `app.py` hvis 5000 er opptatt
- **Rapport ikke generert**: Sjekk skrivetilgang til `generated_reports/`

### Debug-modus
Start med debug for detaljert feilmelding:
```bash
export FLASK_DEBUG=1
python app.py
```

## Arkitektur

```
simulator/
├── app.py                 # Flask hovedapplikasjon
├── calculations.py        # Beregningsmodul
├── requirements.txt       # Python-avhengigheter
├── templates/            
│   ├── index.html        # Hovedform for simulator
│   └── reports.html      # Rapportliste
├── static/               # CSS/JS filer (valgfritt)
└── generated_reports/    # Genererte HTML-rapporter
```

## Lisensiering

Denne simulatoren er en del av HXKit og følger samme lisens som hovedprosjektet.