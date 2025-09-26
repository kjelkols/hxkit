# Feilretting: Runtime-feil i basic_example.py

## Problemet
Runtime-feil på linje 61 i `basic_example.py` når `PlateHeatExchanger.analyze()` ble kalt:

```
NameError: name 'Psychrometrics' is not defined
```

## Årsaken
I `plate_heat_exchanger.py` var `Psychrometrics` kun importert inne i en `TYPE_CHECKING`-blokk for type hints, men klassen ble brukt i runtime-kode på linje 89:

```python
# Import var kun for type checking
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .thermodynamics import MoistAir, Psychrometrics

# Men brukt i runtime
hot_outlet = Psychrometrics.sensible_cooling(hot_inlet, hot_outlet_temp)
```

## Løsningen
Endret importen til normal runtime-import:

```python
# Før
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .thermodynamics import MoistAir, Psychrometrics

# Etter
from .thermodynamics import MoistAir, Psychrometrics
```

## Verifisering
- ✅ `basic_example.py` kjører uten feil
- ✅ Alle 30 tester passerer
- ✅ Pakken bygget og reinstallert vellykket
- ✅ Eksempel viser korrekte resultater:
  - Varmeoverføring: 2.09 kW
  - Effectiveness: 0.650
  - Utløpstemperaturer: 1.2°C / 10.8°C

## Endrede filer
- `hxkit/plate_heat_exchanger.py`: Fikset import-problem
- Pakken rebuildt til versjon 0.2.0

Feilen er nå løst og alle eksempler fungerer som forventet.