"""Pydantic schemas for termodynamiske tilstander og beregninger."""
from pydantic import BaseModel, Field, model_validator
from typing import Optional, Union, List
from enum import Enum

class HumidityInputType(str, Enum):
    """Type av fuktighetsinput."""
    RELATIVE_HUMIDITY = "relative_humidity"
    HUMIDITY_RATIO = "humidity_ratio"
    DEW_POINT = "dew_point"
    WET_BULB = "wet_bulb"


class MoistAirInput(BaseModel):
    """Input schema for fuktig luft tilstand."""
    
    temperature: float = Field(..., description="Tørrbulbtemperatur [°C]", ge=-50, le=100)
    pressure: float = Field(101325, description="Trykk [Pa]", gt=0)
    
    # En av disse må være oppgitt
    relative_humidity: Optional[float] = Field(None, description="Relativ fuktighet [%]", ge=0, le=100)
    humidity_ratio: Optional[float] = Field(None, description="Fuktighetsforhold [kg/kg]", ge=0)
    dew_point: Optional[float] = Field(None, description="Duggpunkt [°C]")
    wet_bulb: Optional[float] = Field(None, description="Våtkuletemperatur [°C]")

    @model_validator(mode='after')
    def validate_humidity_inputs(self):
        """Validerer at kun en type fuktighetsinput er oppgitt."""
        humidity_fields = [self.relative_humidity, self.humidity_ratio, self.dew_point, self.wet_bulb]
        provided_count = sum(1 for field in humidity_fields if field is not None)
        
        if provided_count != 1:
            raise ValueError("Nøyaktig en av følgende må oppgis: relative_humidity, humidity_ratio, dew_point, wet_bulb")
        
        return self


class MoistAirOutput(BaseModel):
    """Output schema for fuktig luft tilstand."""
    
    temperature: float = Field(..., description="Tørrbulbtemperatur [°C]")
    pressure: float = Field(..., description="Trykk [Pa]")
    relative_humidity: float = Field(..., description="Relativ fuktighet [%]")
    humidity_ratio: float = Field(..., description="Fuktighetsforhold [kg/kg]")
    dew_point: float = Field(..., description="Duggpunkt [°C]")
    wet_bulb: float = Field(..., description="Våtkuletemperatur [°C]")
    density: float = Field(..., description="Tetthet [kg/m³]")
    specific_volume: float = Field(..., description="Spesifikt volum [m³/kg]")
    enthalpy: float = Field(..., description="Entalpi [kJ/kg]")


class PsychrometricConditions(BaseModel):
    """Schema for psykrometriske forhold."""

    hot_side: MoistAirInput = Field(..., description="Varm side innløp")
    cold_side: MoistAirInput = Field(..., description="Kald side innløp")


class FlowConditions(BaseModel):
    """Schema for strømningsforhold."""
    
    hot_mass_flow: float = Field(..., description="Varm side massestrøm [kg/s]", gt=0)
    cold_mass_flow: float = Field(..., description="Kald side massestrøm [kg/s]", gt=0)


class PlateGeometryInput(BaseModel):
    """Input schema for plategeometri."""
    
    plate_width: float = Field(..., description="Platelengde [m]", gt=0)
    plate_height: float = Field(..., description="Platebredde [m]", gt=0)
    plate_spacing: float = Field(..., description="Plateavstand [m]", gt=0)
    chevron_angle: float = Field(30, description="Chevron vinkel [grader]", ge=0, le=90)


class HeatExchangerCoreInput(BaseModel):
    """Input schema for varmevekslerkjerne."""
    
    geometry: PlateGeometryInput = Field(..., description="Plategeometri")
    num_plates: int = Field(..., description="Antall plater", gt=0)


class AnalysisInput(BaseModel):
    """Input schema for varmeveksleranalyse."""
    
    core: HeatExchangerCoreInput = Field(..., description="Varmevekslerkjerne")
    conditions: PsychrometricConditions = Field(..., description="Psykrometriske forhold")
    flow: FlowConditions = Field(..., description="Strømningsforhold")


class AnalysisOutput(BaseModel):
    """Output schema for varmeveksleranalyse."""
    
    # Innløpsforhold
    hot_inlet: MoistAirOutput = Field(..., description="Varm side innløp")
    cold_inlet: MoistAirOutput = Field(..., description="Kald side innløp")
    
    # Utløpsforhold  
    hot_outlet: MoistAirOutput = Field(..., description="Varm side utløp")
    cold_outlet: MoistAirOutput = Field(..., description="Kald side utløp")
    
    # Ytelse
    heat_transfer_rate: float = Field(..., description="Varmeoverføring [W]")
    effectiveness: float = Field(..., description="Virkningsgrad [-]", ge=0, le=1)
    
    # Strømning
    hot_pressure_drop: float = Field(..., description="Trykkfall varm side [Pa]")
    cold_pressure_drop: float = Field(..., description="Trykkfall kald side [Pa]")
    
    # Koeffisienter
    overall_heat_transfer_coefficient: float = Field(..., description="Samlet varmeoverføringskoeff. [W/m²K]")
    ntu: float = Field(..., description="Number of Transfer Units [-]")


# Eksporterte skjemaer
__all__ = [
    "HumidityInputType",
    "MoistAirInput",
    "MoistAirOutput",
    "PsychrometricConditions",
    "FlowConditions", 
    "PlateGeometryInput",
    "HeatExchangerCoreInput",
    "AnalysisInput",
    "AnalysisOutput",
]