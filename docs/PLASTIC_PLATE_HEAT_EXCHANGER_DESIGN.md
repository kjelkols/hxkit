# PlasticPlateHeatExchanger - Designdokumentasjon

## Oversikt

Dette dokumentet oppsummerer designet og arkitekturen for den nye `PlasticPlateHeatExchanger`-klassen som skal simulere varmegjenvinnere laget av glassfiber-forsterket plast med kondenserings- og frostkapasiteter.

## Bakgrunn

Den eksisterende `PlateHeatExchanger`-klassen i HXKit er designet for metallplater med chevron-mønstre. For plast-varmevekslere trenger vi:

- **Separate implementasjon**: Helt uavhengig av eksisterende PlateHeatExchanger
- **Grid-basert beregning**: 2D-grid for kryssstrøm, 1D-grid for motstrøm
- **Faseendringer**: Kondensering og frost/rim-dannelse
- **Materialegenskaper**: Spesifikke egenskaper for glassfiber-forsterket plast

## Arkitektur

### Himmelretnings-system

For intuitiv konfigurasjon av strømningsretninger:

```python
class Direction(Enum):
    NORTH = "north"    # +Y retning (bredde)
    SOUTH = "south"    # -Y retning (bredde) 
    EAST = "east"      # +X retning (lengde)
    WEST = "west"      # -X retning (lengde)
```

**Geometriske sammenhenger:**
- **North/South**: Strømning langs bredden (Y-akse)
- **East/West**: Strømning langs lengden (X-akse)
- **Counterflow**: Motsatte retninger (North↔South eller East↔West)
- **Crossflow**: Vinkelrette retninger (North/South + East/West)

### Grid-strukturer

#### 1D Grid (Counterflow/Parallelflow)
```python
class Grid1D:
    def __init__(self, length: float, segments: int):
        self.length = length
        self.segments = segments
        self.dx = length / segments
```

**Anvendelse:**
- Motstrøm (counterflow): North↔South eller East↔West
- Medstrøm (parallelflow): North→North eller East→East

#### 2D Grid (Crossflow)
```python
class Grid2D:
    def __init__(self, width: float, length: float, 
                 width_segments: int, length_segments: int):
        self.width = width          # Y-retning
        self.length = length        # X-retning
        self.width_segments = width_segments
        self.length_segments = length_segments
        self.dy = width / width_segments
        self.dx = length / length_segments
```

**Anvendelse:**
- Kryssstrøm: North/South kombinert med East/West

### Stream-konsept

```python
class AirStream:
    """Kombinerer MoistAir med massestrøm for strømningsberegninger."""
    
    def __init__(self, moist_air: MoistAir, mass_flow: float, direction: Direction):
        self.moist_air = moist_air
        self.mass_flow = mass_flow      # kg/s
        self.direction = direction
        
    @property
    def volume_flow(self) -> float:
        """Volumstrøm [m³/s]"""
        return self.mass_flow * self.moist_air.specific_volume
        
    @property
    def enthalpy_flow(self) -> float:
        """Entalpistøm [kW]"""
        return self.mass_flow * self.moist_air.enthalpy
```

### Hovedklasse

```python
class PlasticPlateHeatExchanger:
    """
    Simulator for plast-varmevekslere med grid-basert beregning.
    
    Støtter:
    - Counterflow, crossflow, parallelflow
    - Kondensering og frost/rim-dannelse
    - Glassfiber-forsterket plast materialegenskaper
    - Grid-basert numerisk løsning
    """
    
    def __init__(self, 
                 width: float,           # Y-dimensjon [m]
                 length: float,          # X-dimensjon [m] 
                 plate_thickness: float, # Platetykkelse [m]
                 channel_height: float,  # Kanalhøyde [m]
                 num_plates: int,        # Antall plater
                 thermal_conductivity: float = 0.3,  # W/m·K for plast
                 grid_resolution: Tuple[int, int] = (10, 10)):
        
        self.geometry = PlasticPlateGeometry(...)
        self.material = PlasticMaterial(thermal_conductivity)
        self.grid = self._create_grid(grid_resolution)
        
    def analyze(self, 
                hot_stream: AirStream,
                cold_stream: AirStream) -> PlasticPlateResults:
        """Hovedanalyse med grid-basert løsning."""
        
        # 1. Bestem strømningskonfigurasjon
        flow_config = self._determine_flow_configuration(
            hot_stream.direction, cold_stream.direction)
        
        # 2. Velg grid-type basert på konfigurasjon
        if flow_config.is_counterflow or flow_config.is_parallelflow:
            solver = CounterflowSolver1D(self.grid)
        else:  # crossflow
            solver = CrossflowSolver2D(self.grid)
            
        # 3. Løs med faseendringer
        results = solver.solve_with_phase_changes(
            hot_stream, cold_stream, self.material)
            
        return results
```

## Strømningskonfigurasjoner

### FlowConfiguration-klasse

```python
class FlowConfiguration:
    def __init__(self, hot_direction: Direction, cold_direction: Direction):
        self.hot_direction = hot_direction
        self.cold_direction = cold_direction
        
    @property
    def is_counterflow(self) -> bool:
        """Sjekker om strømmene går i motsatte retninger."""
        return ((self.hot_direction == Direction.NORTH and self.cold_direction == Direction.SOUTH) or
                (self.hot_direction == Direction.SOUTH and self.cold_direction == Direction.NORTH) or
                (self.hot_direction == Direction.EAST and self.cold_direction == Direction.WEST) or
                (self.hot_direction == Direction.WEST and self.cold_direction == Direction.EAST))
    
    @property
    def is_crossflow(self) -> bool:
        """Sjekker om strømmene krysser hverandre."""
        hot_axis = "Y" if self.hot_direction in [Direction.NORTH, Direction.SOUTH] else "X"
        cold_axis = "Y" if self.cold_direction in [Direction.NORTH, Direction.SOUTH] else "X"
        return hot_axis != cold_axis
        
    @property
    def is_parallelflow(self) -> bool:
        """Sjekker om strømmene går i samme retning."""
        return self.hot_direction == self.cold_direction
```

## Grid-baserte løsere

### CounterflowSolver1D

```python
class CounterflowSolver1D:
    """1D løser for mot-/medstrøm med faseendringer."""
    
    def solve_with_phase_changes(self, hot_stream: AirStream, 
                                cold_stream: AirStream,
                                material: PlasticMaterial) -> Results:
        
        # Diskretiser langs strømningsretning
        for i in range(self.grid.segments):
            # Beregn lokale tilstander
            hot_local = self._get_hot_state(i)
            cold_local = self._get_cold_state(i)
            
            # Sjekk for kondensering
            if self._check_condensation(hot_local, cold_local):
                # Beregn kondensering og varmeoverføring
                condensation_rate = self._calculate_condensation(...)
                heat_transfer = self._calculate_heat_with_condensation(...)
            else:
                # Sensibel varmeoverføring
                heat_transfer = self._calculate_sensible_heat(...)
                
            # Oppdater tilstander
            self._update_states(i, heat_transfer)
```

### CrossflowSolver2D

```python
class CrossflowSolver2D:
    """2D løser for kryssstrøm med faseendringer."""
    
    def solve_with_phase_changes(self, hot_stream: AirStream,
                                cold_stream: AirStream,
                                material: PlasticMaterial) -> Results:
        
        # 2D grid iterasjon
        for i in range(self.grid.length_segments):
            for j in range(self.grid.width_segments):
                # Beregn lokale tilstander ved (i,j)
                hot_local = self._get_hot_state(i, j)
                cold_local = self._get_cold_state(i, j)
                
                # Faseendringer og varmeoverføring
                self._process_cell(i, j, hot_local, cold_local, material)
```

## Faseendringer

### Kondensering

```python
def _check_condensation(self, hot_air: MoistAir, plate_temp: float) -> bool:
    """Sjekker om kondensering oppstår."""
    return hot_air.dew_point > plate_temp

def _calculate_condensation_rate(self, hot_air: MoistAir, 
                                plate_temp: float,
                                heat_transfer_coeff: float) -> float:
    """Beregner kondensasjonsrate [kg/s·m²]."""
    
    # Lewis-relasjon for masse-varme analogi
    mass_transfer_coeff = heat_transfer_coeff / (hot_air.density * 1.006)
    
    # Fuktighetsforhold ved platetemperatur
    w_sat_plate = MoistAir(temperature=plate_temp, 
                          relative_humidity=100.0).humidity_ratio
    
    # Kondensasjonsrate
    return mass_transfer_coeff * hot_air.density * (hot_air.humidity_ratio - w_sat_plate)
```

### Frost/Rim

```python
def _check_frost_formation(self, cold_air: MoistAir, plate_temp: float) -> bool:
    """Sjekker om frost/rim dannes."""
    return (plate_temp < 0.0 and cold_air.dew_point > plate_temp)

def _calculate_frost_growth(self, cold_air: MoistAir,
                           plate_temp: float,
                           time_step: float) -> float:
    """Beregner frosttilvekst [m]."""
    
    # Forenklet frostmodell basert på sublimering
    if plate_temp < -5.0:
        # Kraftig frostdannelse
        frost_rate = 1e-6  # m/s base rate
    else:
        # Moderat rimdannelse
        frost_rate = 1e-7  # m/s base rate
        
    return frost_rate * time_step
```

## Materialegenskaper

### PlasticMaterial-klasse

```python
class PlasticMaterial:
    """Materialegenskaper for glassfiber-forsterket plast."""
    
    def __init__(self, thermal_conductivity: float = 0.3):
        self.thermal_conductivity = thermal_conductivity  # W/m·K
        self.density = 1800.0                            # kg/m³
        self.specific_heat = 1200.0                      # J/kg·K
        self.surface_roughness = 2e-6                    # m (2 μm)
        
    @property
    def thermal_diffusivity(self) -> float:
        """Temperaturledningsevne [m²/s]."""
        return self.thermal_conductivity / (self.density * self.specific_heat)
```

## Resultater

### PlasticPlateResults-klasse

```python
class PlasticPlateResults:
    """Resultater fra plast-varmeveksler analyse."""
    
    def __init__(self):
        self.effectiveness: float = 0.0
        self.ntu: float = 0.0
        self.heat_transfer_rate: float = 0.0     # kW
        self.pressure_drop_hot: float = 0.0      # Pa
        self.pressure_drop_cold: float = 0.0     # Pa
        
        # Faseendringer
        self.condensation_rate: float = 0.0      # kg/s
        self.frost_thickness: float = 0.0        # m
        
        # Grid-resultater
        self.temperature_field: np.ndarray = None
        self.humidity_field: np.ndarray = None
        self.condensation_field: np.ndarray = None
        
        # Utløpstilstander
        self.hot_outlet: MoistAir = None
        self.cold_outlet: MoistAir = None
```

## Implementeringsplan

### Fase 1: Grunnleggende struktur
1. ✅ **Definer Direction enum og FlowConfiguration**
2. ✅ **Implementer AirStream-klasse i thermodynamics.py**
3. ✅ **Lag PlasticMaterial-klasse**
4. ✅ **Opprett PlasticPlateGeometry**

### Fase 2: Grid-system
1. **Implementer Grid1D og Grid2D klasser**
2. **Lag CounterflowSolver1D**
3. **Lag CrossflowSolver2D**
4. **Test grid-oppløsning og konvergens**

### Fase 3: Faseendringer
1. **Implementer kondensasjonsberegninger**
2. **Legg til frost/rim-modeller**
3. **Integrer faseendringer i løsere**
4. **Valider mot eksperimentelle data**

### Fase 4: Hovedklasse og testing
1. **Implementer PlasticPlateHeatExchanger hovedklasse**
2. **Lag omfattende testsuite**
3. **Opprett eksempler og dokumentasjon**
4. **Performance-optimering**

## Eksempelbruk

```python
# Opprett varmeveksler
exchanger = PlasticPlateHeatExchanger(
    width=0.5,           # m
    length=1.0,          # m
    plate_thickness=0.001,  # 1 mm
    channel_height=0.005,   # 5 mm
    num_plates=50,
    grid_resolution=(20, 20)
)

# Definer luftstrømmer
hot_air = MoistAir(temperature=25.0, relative_humidity=60.0)
cold_air = MoistAir(temperature=-10.0, relative_humidity=80.0)

hot_stream = AirStream(hot_air, mass_flow=1.0, direction=Direction.NORTH)
cold_stream = AirStream(cold_air, mass_flow=0.8, direction=Direction.EAST)

# Analyser
results = exchanger.analyze(hot_stream, cold_stream)

print(f"Virkningsgrad: {results.effectiveness:.1%}")
print(f"Varmeoverføring: {results.heat_transfer_rate:.1f} kW")
print(f"Kondensering: {results.condensation_rate:.3f} kg/s")
print(f"Frosttykkelse: {results.frost_thickness*1000:.1f} mm")
```

## Designprinsipper

### 1. Separasjon
- **Helt uavhengig** av eksisterende PlateHeatExchanger
- **Egen modul** for plast-spesifikke beregninger
- **Ingen arv** fra eksisterende klasser

### 2. Intuitivitet  
- **Himmelretnings-system** for enkel konfigurasjon
- **Fysisk intuitive** parametre og resultater
- **Tydelige** feilmeldinger og advarsler

### 3. Fleksibilitet
- **Grid-oppløsning** kan tilpasses nøyaktighets-/hastighetsbehov
- **Modulære løsere** for ulike strømningskonfigurasjoner
- **Utvidbar** for nye materialtyper og faseendringer

### 4. Nøyaktighet
- **Ingen cross-mixing** antakelse i første versjon
- **Temperaturavhengige** materialegenskaper
- **Validering** mot kjente analytiske løsninger

## Tekniske forutsetninger

### Gyldighetsområder
- **Temperatur**: -30°C til 60°C (tipisk for ventilasjon)
- **Relative fuktighet**: 10% til 95%
- **Massestrømmer**: 0.1 til 10 kg/s per kanal
- **Platetykkelse**: 0.5 til 3.0 mm

### Modellavgrensninger
- **Ingen cross-mixing** mellom kanaler (første versjon)
- **Stabil drift** (ingen transiente effekter)
- **Ren luft** (ingen forurensninger)
- **Uniform** plategeometri

### Validering
- **Analytiske løsninger** for enkle tilfeller
- **CFD-sammenligning** for komplekse geometrier  
- **Eksperimentelle data** fra produsent
- **Energibalanse** og massekonsistens

---

*Dette dokumentet vil bli oppdatert etter hvert som implementeringen skrider frem.*