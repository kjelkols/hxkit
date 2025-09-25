# Installasjonsinstruksjoner for HXKit

## Installering med pip

### Fra lokal kildekode

For å installere HXKit direkte fra kildekoden i denne mappen:

```bash
# Installer pakken i utviklingsmodus (anbefalt under utvikling)
pip install -e .

# Eller installer fra bygget pakke
pip install dist/hxkit-0.2.0-py3-none-any.whl

# Eller bygg og installer direkte
pip install .
```

### Med ekstrafunksjoner

Du kan installere pakken med tilleggsfunksjoner:

```bash
# For utvikling
pip install -e .[dev]

# For plotting-funksjoner
pip install -e .[plotting]

# For web-applikasjoner
pip install -e .[web]

# Alle ekstrafunksjoner
pip install -e .[dev,plotting,web]
```

## Verifisering av installasjon

Test at installasjonen fungerer:

```python
import hxkit
print(f"HXKit versjon {hxkit.__version__}")

# Test grunnleggende funksjonalitet
from hxkit import MoistAir
air = MoistAir(temperature=25, relative_humidity=50)
print(f"Våtkule: {air.wet_bulb:.1f}°C")
```

## Bygging av distribusjonsfilene

Hvis du vil bygge pakken selv:

```bash
# Installer byggeverktyø
pip install build

# Bygg pakken
python -m build

# Dette vil lage filer i dist/ mappen:
# - hxkit-0.2.0.tar.gz (kildekode)
# - hxkit-0.2.0-py3-none-any.whl (binær pakke)
```

## Publisering til PyPI

Når pakken er klar for publisering:

```bash
# Installer twine
pip install twine

# Last opp til PyPI test-server først
python -m twine upload --repository testpypi dist/*

# Test installasjon fra test-server
pip install -i https://test.pypi.org/simple/ hxkit

# Last opp til ekte PyPI når du er fornøyd
python -m twine upload dist/*
```

## Krav

- Python 3.8 eller nyere
- numpy >= 1.20.0
- scipy >= 1.7.0  
- pandas >= 1.3.0
- pydantic >= 2.0.0
- requests >= 2.25.0

## Avhengigheter

Pakken installerer automatisk alle nødvendige avhengigheter.