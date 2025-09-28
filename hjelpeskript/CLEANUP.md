# 🧹 Cleanup Scripts for Generated Files

Dette prosjektet inneholder to scripts for å slette maskingenererte filer som automatisk kan gjenopprettes:

## 📝 Scripts

### `clean_generated_files.py` (Python)
- **Cross-platform**: Fungerer på Windows, macOS og Linux
- **Detaljert output**: Viser nøyaktig hvor mye plass som frigjøres
- **Robust**: Håndterer store datamengder effektivt

### `clean_files.ps1` (PowerShell)
- **Windows-optimalisert**: Bruker native PowerShell kommandoer
- **Rask**: Optimalisert for Windows filsystem
- **Färgkodad output**: Lettlest output med farger

## 🚀 Bruk

### Python versjon
```bash
# Vis hva som ville blitt slettet (anbefalt første gang)
python clean_generated_files.py --dry-run

# Slett filene med detaljert output
python clean_generated_files.py --verbose

# Slett filene (stille modus)
python clean_generated_files.py
```

### PowerShell versjon
```powershell
# Vis hva som ville blitt slettet (anbefalt første gang)
.\clean_files.ps1 -DryRun

# Slett filene med detaljert output
.\clean_files.ps1 -ShowDetails

# Slett filene (stille modus)
.\clean_files.ps1
```

## 🗂️ Hva slettes

### ✅ Trygt å slette (gjenopprettes automatisk):

| Kategori | Filer/Kataloger | Gjenopprettes ved |
|----------|-----------------|-------------------|
| **Python bytecode** | `__pycache__/`, `*.pyc`, `*.pyo`, `*.pyd` | Kjør Python-kode |
| **Build artifakter** | `dist/`, `build/`, `*.egg-info/` | `python -m build`, `pip install -e .` |
| **Test cache** | `.pytest_cache/`, `.coverage`, `htmlcov/` | `pytest`, `coverage run` |
| **IDE filer** | `.vscode/settings.json`, `*.swp`, `*.swo` | IDE-konfigurering |
| **Temp filer** | `*.tmp`, `*.temp`, `*.log` | Automatisk ved behov |
| **Demo filer** | `*_hx_demo.png`, `*_hx_demo.html` | Kjør visualiserings-demoer |

### ❌ Slettes IKKE (viktige filer):
- Kildekode (`.py` filer)
- Konfigurasjonfiler (`pyproject.toml`, `.gitignore`)
- Dokumentasjon (`.md` filer)
- Tests og eksempler
- Git historie (`.git/`)

## 📊 Forventet resultat

Typisk frigjør scriptet:
- **Python bytecode**: 200-300 KB (kan være mer etter mye testing)
- **Build artifakter**: 50-100 KB
- **Test cache**: 1-10 KB
- **Demo filer**: 1-2 MB (hvis visualiseringsdemoer er kjørt)

**Total**: Vanligvis 1-5 MB, kan være mer hvis `.venv/` kataloger finnes.

## ⚡ Når bør du kjøre cleanup?

### 🔄 Regelmessig (ukentlig/månedlig):
- Før pushing til git (mindre repository størrelse)
- Etter å ha kjørt mange tester (cache kan bli stor)
- Når du ser at disk space blir lavt

### 🧪 Testing og utvikling:
- Etter store kodeendringer (nytt bytecode)
- Før å lage nye builds/releases
- Når du migrerer kodebasen til ny maskin

### 🎯 Spesielle tilfeller:
- Før å arkivere prosjektet
- Når du deler kodebasen (zip/tar)
- Hvis du mistenker korrupte cache-filer

## 🔧 Tilpasning

Du kan enkelt legge til flere filer/mønstre ved å redigere `items_to_clean` strukturen i scriptene:

```python
# Eksempel: Legg til node_modules (hvis du bruker JavaScript også)
"Node modules": [
    "node_modules",
    "**\\node_modules"
]
```

## ⚠️ Sikkerhet

- **Dry-run først**: Alltid kjør `--dry-run` først for å se hva som slettes
- **Backup viktige filer**: Hvis du er usikker, ta backup før sletting
- **Ingen system-filer**: Scriptene berører bare prosjekt-lokale filer
- **Ingen permanente tap**: Alt som slettes kan gjenopprettes automatisk