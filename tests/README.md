# Unit Tests for HXKit

Dette mappen inneholder unit tester for HXKit biblioteket.

## Test Files

### `test_wet_bulb.py`
Omfattende tester for våtkule-temperatur beregninger:

- **`test_wet_bulb_from_relative_humidity`**: Tester beregning av våtkule fra temperatur og relativ fuktighet
- **`test_wet_bulb_saturated_conditions`**: Validerer at våtkule = tørrkule ved 100% RH
- **`test_wet_bulb_physical_constraints`**: Sikrer at fysiske grenser respekteres
- **`test_humidity_ratio_from_wet_bulb`**: Tester beregning av fuktighetsforhold fra våtkule input
- **`test_wet_bulb_roundtrip_consistency`**: Validerer konsistens i frem-og-tilbake beregninger
- **`test_wet_bulb_input_validation`**: Tester feilhåndtering for ugyldige input-verdier
- **`test_wet_bulb_extreme_conditions`**: Tester under ekstreme forhold (meget tørr/fuktig luft)
- **`test_wet_bulb_consistency_with_other_properties`**: Sjekker konsistens med andre psykrometriske egenskaper
- **`test_wet_bulb_temperature_range`**: Validerer våtkule over bredt temperatur- og fuktighetsområde

### `test_thermodynamics.py`
Grunnleggende psykrometriske beregninger:

- Termodynamiske egenskaper for fuktig luft
- Psykrometriske funksjoner som blanding og sensibel kjøling

### `test_geometries.py`
Geometriske beregninger for platevarmevekslere:

- Plategeometri og flow-områder
- Friksjonsfaktorer og trykkfall

## Kjøre Tester

```bash
# Kjør alle tester
python -m pytest tests/ -v

# Kjør kun våtkule tester
python -m pytest tests/test_wet_bulb.py -v

# Kjør med detaljer om feilende tester
python -m pytest tests/ -v --tb=long
```

## Testresultater

Alle våtkule-tester validerer at algoritmen:

1. ✅ Gir nøyaktige resultater innenfor ±0.3°C
2. ✅ Respekterer fysiske grenser (våtkule ≤ tørrkule ≥ duggpunkt)  
3. ✅ Håndterer ekstreme forhold (0.1% - 99.9% RH)
4. ✅ Er konsistent i roundtrip-beregninger (0.01°C nøyaktighet)
5. ✅ Validerer input og gir passende feilmeldinger
6. ✅ Fungerer over bredt temperaturområde (0-50°C)

Algoritmen er basert på ASHRAE psykrometriske fundamentalligninger og er produksjonsklar.