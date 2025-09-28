"""Pydantic schemas for Plastic Plate Heat Exchanger input og output."""

from pydantic import BaseModel, Field, model_validator
from typing import Optional
from enum import Enum

from ..definitions import Direction
from .thermodynamics_schemas import MoistAirInput


class PlateMaterial(str, Enum):
    """Platematerialer for plastic plate heat exchanger."""
    GLASS_FIBER_PLASTIC = "glass_fiber_plastic"
    POLYPROPYLENE = "polypropylene"
    POLYETHYLENE = "polyethylene"
    ABS_PLASTIC = "abs_plastic"


class PlateGeometryInput(BaseModel):
    """Input schema for plategeometri."""
    
    width: float = Field(
        ..., 
        description="Platebredde [m]",
        gt=0,
        le=5.0
    )
    
    length: float = Field(
        ..., 
        description="Platelengde [m]", 
        gt=0,
        le=10.0
    )
    
    plate_thickness: float = Field(
        ...,
        description="Platetykkelse [m]",
        gt=0,
        le=0.1
    )
    
    channel_height: float = Field(
        ...,
        description="Plateavstand (kanalhøyde) [m]",
        gt=0,
        le=0.5
    )
    
    num_plates: int = Field(
        ...,
        description="Antall plater",
        gt=0,
        le=1000
    )
    
    plate_material: PlateMaterial = Field(
        PlateMaterial.GLASS_FIBER_PLASTIC,
        description="Platemateriale"
    )


class FlowDirectionInput(BaseModel):
    """Input schema for strømningsretninger."""
    
    hot_direction: Direction = Field(
        ...,
        description="Strømningsretning for varm luft (N/S/E/W)"
    )
    
    cold_direction: Direction = Field(
        ...,
        description="Strømningsretning for kald luft (N/S/E/W)"
    )

    @model_validator(mode='after')
    def validate_directions(self):
        """Validerer at strømningsretningene er gyldige."""
        # Alle kombinasjoner er teknisk mulige, men gi en advarsel hvis samme retning
        if self.hot_direction == self.cold_direction:
            # Dette er teknisk mulig (parallel flow samme retning)
            pass
        
        return self


class StreamInput(BaseModel):
    """Input schema for luftstrøm inkludert termodynamisk tilstand og massestrøm."""
    
    moist_air: MoistAirInput = Field(
        ...,
        description="Termodynamisk tilstand for luftstrømmen"
    )
    
    mass_flow: float = Field(
        ...,
        description="Massestrøm av tørr luft [kg/s]",
        gt=0,
        le=1000.0
    )


class PlasticPlateHeatExchangerInput(BaseModel):
    """Komplett input schema for Plastic Plate Heat Exchanger analyse."""
    
    # Geometri
    geometry: PlateGeometryInput = Field(
        ...,
        description="Geometriske egenskaper for varmeveksleren"
    )
    
    # Strømningsretninger  
    flow_directions: FlowDirectionInput = Field(
        ...,
        description="Strømningsretninger for varm og kald luft"
    )
    
    # Innløpsstrømmer
    hot_stream: StreamInput = Field(
        ..., 
        description="Varm luftstrøm ved innløp"
    )
    
    cold_stream: StreamInput = Field(
        ...,
        description="Kald luftstrøm ved innløp"
    )
    
    # Valgfrie analyseparametere
    grid_resolution: Optional[tuple[int, int]] = Field(
        (10, 10),
        description="Grid oppløsning (bredde_celler, lengde_celler)"
    )
    
    convergence_tolerance: Optional[float] = Field(
        1e-6,
        description="Konvergensstoleranse for numerisk løsning",
        gt=0,
        le=1e-3
    )
    
    max_iterations: Optional[int] = Field(
        1000,
        description="Maksimalt antall iterasjoner",
        gt=0,
        le=10000
    )

    @model_validator(mode='after') 
    def validate_grid_resolution(self):
        """Validerer at grid oppløsningen er fornuftig."""
        if self.grid_resolution:
            width_cells, length_cells = self.grid_resolution
            if width_cells < 2 or length_cells < 2:
                raise ValueError("Grid oppløsning må være minimum (2, 2)")
            if width_cells > 100 or length_cells > 100:
                raise ValueError("Grid oppløsning bør ikke overstige (100, 100) for ytelse")
        
        return self

    @model_validator(mode='after')
    def validate_stream_temperatures(self):
        """Validerer at varm strøm er varmere enn kald strøm."""
        hot_temp = self.hot_stream.moist_air.temperature
        cold_temp = self.cold_stream.moist_air.temperature
        
        if hot_temp <= cold_temp:
            raise ValueError(f"Varm strøm temperatur ({hot_temp}°C) må være høyere enn kald strøm temperatur ({cold_temp}°C)")
        
        return self


# Eksempel på bruk
class StreamOutput(BaseModel):
    """Output schema for luftstrøm ved utløp."""
    
    moist_air: "MoistAirOutput" = Field(
        ...,
        description="Termodynamisk tilstand for luftstrømmen ved utløp"
    )
    
    mass_flow: float = Field(
        ...,
        description="Massestrøm av tørr luft [kg/s]",
        gt=0
    )
    
    volume_flow: float = Field(
        ...,
        description="Volumstrøm [m³/s]",
        gt=0
    )
    
    enthalpy_flow: float = Field(
        ..., 
        description="Entalpistrøm [kW]"
    )


class PerformanceMetrics(BaseModel):
    """Output schema for ytelsesmålinger."""
    
    effectiveness: float = Field(
        ...,
        description="Varmeveksler effektivitet [-]",
        ge=0,
        le=1
    )
    
    ntu: float = Field(
        ...,
        description="Number of Transfer Units [-]", 
        ge=0
    )
    
    heat_transfer_rate: float = Field(
        ...,
        description="Varmeoverføringsrate [kW]",
        ge=0
    )
    
    pressure_drop_hot: float = Field(
        ...,
        description="Trykkfall varm side [Pa]",
        ge=0
    )
    
    pressure_drop_cold: float = Field(
        ...,
        description="Trykkfall kald side [Pa]",
        ge=0
    )
    
    overall_heat_transfer_coefficient: Optional[float] = Field(
        None,
        description="Samlet varmeoverføringskoeffisient [W/m²·K]",
        gt=0
    )


class PhaseChangeResults(BaseModel):
    """Output schema for faseendringer."""
    
    condensation_rate: float = Field(
        0.0,
        description="Kondensasjonsrate [kg/s]",
        ge=0
    )
    
    frost_thickness: float = Field(
        0.0,
        description="Rimtykkelse [m]", 
        ge=0
    )
    
    condensation_occurred: bool = Field(
        ...,
        description="Om kondensasjon fant sted"
    )
    
    frost_occurred: bool = Field(
        ...,
        description="Om rimdannelse fant sted"
    )


class GridResults(BaseModel):
    """Output schema for grid-baserte resultater."""
    
    grid_resolution: tuple[int, int] = Field(
        ...,
        description="Faktisk grid oppløsning brukt (bredde, lengde)"
    )
    
    # Temperature fields som flate lister (JSON serializable)
    plate_temperatures: list[list[float]] = Field(
        ...,
        description="Platetemperaturer [°C] som 2D array (bredde × lengde)"
    )
    
    hot_air_temperatures: list[list[float]] = Field(
        ...,
        description="Varm luft temperaturer [°C] som 2D array"
    )
    
    cold_air_temperatures: list[list[float]] = Field(
        ...,
        description="Kald luft temperaturer [°C] som 2D array"
    )
    
    max_plate_temperature: float = Field(
        ...,
        description="Maksimal platetemperatur [°C]"
    )
    
    min_plate_temperature: float = Field(
        ...,
        description="Minimal platetemperatur [°C]"
    )
    
    temperature_uniformity: float = Field(
        ...,
        description="Temperaturuniformitet (std/mean) [-]",
        ge=0
    )


class ConvergenceInfo(BaseModel):
    """Output schema for konvergensinformasjon."""
    
    converged: bool = Field(
        ...,
        description="Om løsningen konvergerte"
    )
    
    iterations: int = Field(
        ...,
        description="Antall iterasjoner brukt",
        ge=0
    )
    
    final_residual: float = Field(
        ...,
        description="Endelig residual",
        ge=0
    )
    
    convergence_tolerance: float = Field(
        ...,
        description="Konvergenstoleranse brukt",
        gt=0
    )
    
    computation_time: float = Field(
        ...,
        description="Beregningstid [s]",
        ge=0
    )


class PlasticPlateHeatExchangerOutput(BaseModel):
    """Komplett output schema for Plastic Plate Heat Exchanger analyse."""
    
    # Input-konfigurasjon (for komplett dokumentasjon)
    input_data: PlasticPlateHeatExchangerInput = Field(
        ...,
        description="Opprinnelig input-konfigurasjon som ble brukt i analysen"
    )
    
    # Hovedresultater
    performance: PerformanceMetrics = Field(
        ...,
        description="Ytelsesmålinger for varmeveksleren"
    )
    
    # Utløpsstrømmer 
    hot_outlet: StreamOutput = Field(
        ...,
        description="Varm luftstrøm ved utløp"
    )
    
    cold_outlet: StreamOutput = Field(
        ...,
        description="Kald luftstrøm ved utløp"
    )
    
    # Faseendringer
    phase_changes: PhaseChangeResults = Field(
        ...,
        description="Resultater for kondensasjon og rimdannelse"
    )
    
    # Detaljerte grid-resultater (valgfritt)
    grid_results: Optional[GridResults] = Field(
        None,
        description="Detaljerte grid-baserte temperaturfelter"
    )
    
    # Konvergensinformasjon
    convergence: ConvergenceInfo = Field(
        ...,
        description="Informasjon om numerisk konvergens"
    )
    
    # Metadata
    analysis_timestamp: str = Field(
        ...,
        description="Tidspunkt for analyse (ISO format)"
    )
    
    solver_version: str = Field(
        ...,
        description="Versjon av solver brukt"
    )
    
    @model_validator(mode='after')
    def validate_energy_balance(self):
        """Validerer energibalanse (optional check)."""
        hot_energy_change = (
            self.hot_outlet.enthalpy_flow - 
            # Vi mangler inlet enthalpy, så dette er kun et eksempel
            0  # inlet_hot_enthalpy_flow
        )
        cold_energy_change = (
            self.cold_outlet.enthalpy_flow - 
            0  # inlet_cold_enthalpy_flow  
        )
        
        # Denne valideringen kan implementeres når inlet data er tilgjengelig
        # energy_balance_error = abs(hot_energy_change + cold_energy_change)
        # if energy_balance_error > 0.01 * abs(hot_energy_change):
        #     raise ValueError(f"Energibalanse feil: {energy_balance_error:.3f} kW")
        
        return self


# Forward reference for MoistAirOutput
from .thermodynamics_schemas import MoistAirOutput
StreamOutput.model_rebuild()


if __name__ == "__main__":
    """Eksempel på hvordan man bruker input og output skjemaene."""
    
    # Eksempel input data
    example_input = {
        "geometry": {
            "width": 0.6,
            "length": 1.2, 
            "plate_thickness": 0.001,
            "channel_height": 0.008,
            "num_plates": 20,
            "plate_material": "glass_fiber_plastic"
        },
        "flow_directions": {
            "hot_direction": "north",
            "cold_direction": "south"  
        },
        "hot_stream": {
            "moist_air": {
                "temperature": 35.0,
                "pressure": 101325,
                "relative_humidity": 60.0
            },
            "mass_flow": 2.5
        },
        "cold_stream": {
            "moist_air": {
                "temperature": 15.0,
                "pressure": 101325, 
                "relative_humidity": 40.0
            },
            "mass_flow": 2.0
        },
        "grid_resolution": (12, 15),
        "convergence_tolerance": 1e-6,
        "max_iterations": 500
    }
    
    # Eksempel output data
    example_output = {
        "input_data": example_input,  # Inkluder input-dataene for komplett dokumentasjon
        "performance": {
            "effectiveness": 0.78,
            "ntu": 2.45,
            "heat_transfer_rate": 12.5,
            "pressure_drop_hot": 45.2,
            "pressure_drop_cold": 38.7,
            "overall_heat_transfer_coefficient": 25.3
        },
        "hot_outlet": {
            "moist_air": {
                "temperature": 22.3,
                "pressure": 101280,
                "relative_humidity": 85.2,
                "humidity_ratio": 0.0142,
                "dew_point": 19.8,
                "wet_bulb": 20.7,
                "density": 1.184
            },
            "mass_flow": 2.5,
            "volume_flow": 2.11,
            "enthalpy_flow": 78.2
        },
        "cold_outlet": {
            "moist_air": {
                "temperature": 27.8,
                "pressure": 101287,
                "relative_humidity": 32.1,
                "humidity_ratio": 0.0089,
                "dew_point": 11.2,
                "wet_bulb": 18.4,
                "density": 1.148
            },
            "mass_flow": 2.0,
            "volume_flow": 1.74,
            "enthalpy_flow": 59.8
        },
        "phase_changes": {
            "condensation_rate": 0.0,
            "frost_thickness": 0.0,
            "condensation_occurred": False,
            "frost_occurred": False
        },
        "convergence": {
            "converged": True,
            "iterations": 127,
            "final_residual": 4.2e-7,
            "convergence_tolerance": 1e-6,
            "computation_time": 2.34
        },
        "analysis_timestamp": "2025-09-28T14:30:45.123Z",
        "solver_version": "HXKit v0.2.0"
    }
    
    # Valider skjemaene
    try:
        validated_input = PlasticPlateHeatExchangerInput(**example_input)
        print("✅ Input skjema validert!")
        
        validated_output = PlasticPlateHeatExchangerOutput(**example_output)
        print("✅ Output skjema validert!")
        
        print(f"Effektivitet: {validated_output.performance.effectiveness:.1%}")
        print(f"Varmeoverføring: {validated_output.performance.heat_transfer_rate:.1f} kW")
        print(f"Konvergert på {validated_output.convergence.iterations} iterasjoner")
        
    except Exception as e:
        print(f"❌ Validering feilet: {e}")