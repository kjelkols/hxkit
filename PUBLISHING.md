# Publisering til PyPI

Denne filen beskriver hvordan du publiserer HXKit til PyPI.

## Forberedelser

1. **Opprett kontoer på PyPI:**
   - Test-PyPI: https://test.pypi.org/account/register/
   - PyPI: https://pypi.org/account/register/

2. **Installer twine:**
```bash
pip install twine
```

3. **Konfigurer API-tokens (anbefalt):**
   - Gå til PyPI-kontoinstellinger
   - Opprett API-token
   - Lagre i ~/.pypirc (eller konfigurer direkte i terminal)

## Publiseringsprosess

### 1. Bygg pakken
```bash
# Sørg for at dist/ mappen er tom eller slett gamle versjoner
rm -rf dist/

# Bygg ny versjon
python -m build
```

### 2. Test på TestPyPI først
```bash
# Last opp til test-server
python -m twine upload --repository testpypi dist/*

# Test installasjon fra test-server
pip install -i https://test.pypi.org/simple/ hxkit==0.2.0
```

### 3. Publiser til ekte PyPI
```bash
# Når du er fornøyd med testen
python -m twine upload dist/*
```

### 4. Verifiser installasjon
```bash
# Test installasjon fra PyPI
pip install hxkit==0.2.0
python -c "import hxkit; print(hxkit.__version__)"
```

## Versjonshåndtering

Før hver publisering, oppdater versjonsnummeret i:
- `pyproject.toml`
- `setup.py` 
- `hxkit/__init__.py`

Bruk semantisk versjonering (SemVer):
- 0.1.0 → 0.1.1 (patch: bugfixes)
- 0.1.0 → 0.2.0 (minor: ny funksjonalitet)
- 0.2.0 → 1.0.0 (major: breaking changes)

## Automatisering

Du kan automatisere publisering med GitHub Actions:

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
```