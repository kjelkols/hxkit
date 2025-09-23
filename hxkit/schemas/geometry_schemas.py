"""
Pydantic schemas for analyse input og output.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Tuple
from .thermodynamics_schemas import MoistAirInput, MoistAirOutput, PsychrometricConditions, FlowConditions
from .geometry_schemas import HeatExchangerCoreInput, GeometryConfig, OptimizationConstraints


class AnalysisInput(BaseModel):
    """Input schema for varmeveksleranalyse."""
    
    conditions: PsychrometricConditions = Field(..., description="Psykrometriske forhold")
    flow: FlowConditions = Field(..., description="Strømningsforhold")
    geometry: HeatExchangerCoreInput = Field(..., description="Varmevekslerkjerne")
    config: Optional[GeometryConfig] = Field(None, description="Geometrikonfigurasjon")
    
    class Config:
        """Pydantic konfigurasjon."""
        json_schema_extra = {
            "example": {
                "conditions": {
                    "hot_side": {
                        "temperature": 22.0,
                        "relative_humidity": 40.0
                    },
                    "cold_side": {
                        "temperature": -10.0,
                        "relative_humidity": 80.0
                    }
                },
                "flow": {
                    "hot_mass_flow": 0.1,
                    "cold_mass_flow": 0.1
                },
                "geometry": {
                    "n_plates": 21,
                    "plate_geometry": {
                        "length": 0.6,
                        "width": 0.2,
                        "thickness": 0.0005,
                        "channel_height": 0.004
                    },
                    "hot_channels": 10,
                    "cold_channels": 10
                }
            }
        }


class AnalysisOutput(BaseModel):
    """Output schema for varmeveksleranalyse."""
    
    # Hovedresultater
    heat_transfer_rate: float = Field(..., description="Varmeoverføringsrate [W]")
    effectiveness: float = Field(..., description="Effectiveness [-]")
    ntu: float = Field(..., description="Number of Transfer Units [-]")
    
    # Utløpstilstander
    hot_outlet: MoistAirOutput = Field(..., description="Varm utløpstilstand")
    cold_outlet: MoistAirOutput = Field(..., description="Kald utløpstilstand")
    
    # Trykkfall
    hot_pressure_drop: float = Field(..., description="Varm side trykkfall [Pa]")
    cold_pressure_drop: float = Field(..., description="Kald side trykkfall [Pa]")
    
    # Hastigheter
    hot_velocity: float = Field(..., description="Varm side hastighet [m/s]")
    cold_velocity: float = Field(..., description="Kald side hastighet [m/s]")
    
    # Varmeoverføringskoeffisienter
    u_overall: float = Field(..., description="Overall varmeoverføringskoeffisient [W/m²·K]")
    hot_htc: float = Field(..., description="Varm side varmeoverføringskoeffisient [W/m²·K]")
    cold_htc: float = Field(..., description="Kald side varmeoverføringskoeffisient [W/m²·K]")
    
    # Temperatureffektivitet
    temperature_effectiveness: Optional[float] = Field(None, description="Temperatureffektivitet [-]")
    
    class Config:
        """Pydantic konfigurasjon."""
        json_schema_extra = {
            "example": {
                "heat_transfer_rate": 3250.0,
                "effectiveness": 0.72,
                "ntu": 2.5,
                "hot_outlet": {
                    "temperature": 15.8,
                    "relative_humidity": 47.2,
                    "humidity_ratio": 0.0075,
                    "density": 1.21,
                    "enthalpy": 35.1
                },
                "cold_outlet": {
                    "temperature": 19.2,
                    "relative_humidity": 65.1,
                    "humidity_ratio": 0.0018,
                    "density": 1.25,
                    "enthalpy": 23.8
                },
                "hot_pressure_drop": 85.2,
                "cold_pressure_drop": 92.1,
                "hot_velocity": 1.25,
                "cold_velocity": 1.25,
                "u_overall": 45.2,
                "hot_htc": 125.3,
                "cold_htc": 118.7,
                "temperature_effectiveness": 0.72
            }
        }


class PerformancePoint(BaseModel):
    """Et punkt i performance map."""
    
    mass_flow: float = Field(..., description="Massestrøm [kg/s]")
    heat_transfer_rate: float = Field(..., description="Varmeoverføringsrate [W]")
    effectiveness: float = Field(..., description="Effectiveness [-]")
    hot_pressure_drop: float = Field(..., description="Varm side trykkfall [Pa]")
    cold_pressure_drop: float = Field(..., description="Kald side trykkfall [Pa]")


class PerformanceMapOutput(BaseModel):
    """Output schema for performance map."""
    
    conditions: PsychrometricConditions = Field(..., description="Testforhold")
    geometry: HeatExchangerCoreInput = Field(..., description="Geometri")
    mass_flow_range: Tuple[float, float] = Field(..., description="Massestrømområde [kg/s]")
    points: List[PerformancePoint] = Field(..., description="Performance punkter")
    
    # Sammendrag
    max_heat_transfer: float = Field(..., description="Maksimal varmeoverføring [W]")
    max_effectiveness: float = Field(..., description="Maksimal effectiveness [-]")
    optimal_mass_flow: float = Field(..., description="Optimal massestrøm [kg/s]")
    
    class Config:
        """Pydantic konfigurasjon."""
        json_schema_extra = {
            "example": {
                "mass_flow_range": [0.05, 0.2],
                "max_heat_transfer": 4850.0,
                "max_effectiveness": 0.85,
                "optimal_mass_flow": 0.15
            }
        }


class OptimizationInput(BaseModel):
    """Input schema for geometrioptimalisering."""
    
    conditions: PsychrometricConditions = Field(..., description="Driftsforhold")
    flow: FlowConditions = Field(..., description="Strømningsforhold")
    constraints: OptimizationConstraints = Field(..., description="Optimaliseringsbegrensninger")
    base_geometry: Optional[HeatExchangerCoreInput] = Field(None, description="Startgeometri")
    
    class Config:
        """Pydantic konfigurasjon."""
        json_schema_extra = {
            "example": {
                "conditions": {
                    "hot_side": {
                        "temperature": 22.0,
                        "relative_humidity": 40.0
                    },
                    "cold_side": {
                        "temperature": -10.0,
                        "relative_humidity": 80.0
                    }
                },
                "flow": {
                    "hot_mass_flow": 0.1,
                    "cold_mass_flow": 0.1
                },
                "constraints": {
                    "target_effectiveness": 0.8,
                    "max_pressure_drop": 500
                }
            }
        }


class OptimizationOutput(BaseModel):
    """Output schema for geometrioptimalisering."""
    
    optimized_geometry: HeatExchangerCoreInput = Field(..., description="Optimalisert geometri")
    performance: AnalysisOutput = Field(..., description="Ytelse med optimalisert geometri")
    optimization_summary: Dict[str, Any] = Field(..., description="Optimaliseringssammendrag")
    
    class Config:
        """Pydantic konfigurasjon."""
        json_schema_extra = {
            "example": {
                "optimization_summary": {
                    "iterations": 15,
                    "initial_effectiveness": 0.65,
                    "final_effectiveness": 0.80,
                    "plates_added": 8,
                    "improvement": "25% økning i effectiveness"
                }
            }
        }
"""
Pydantic schemas for konfigurasjon og innstillinger.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from enum import Enum


class SolverMethod(str, Enum):
    """Numeriske løsningsmetoder."""
    EFFECTIVENESS_NTU = "effectiveness_ntu"
    LMTD = "lmtd"
    FINITE_DIFFERENCE = "finite_difference"


class ConvergenceCriteria(BaseModel):
    """Konvergenskriterier for iterative løsninger."""
    
    max_iterations: int = Field(100, description="Maksimum iterasjoner", ge=1, le=1000)
    tolerance: float = Field(1e-6, description="Toleranse for konvergens", gt=0, le=1e-3)
    relaxation_factor: float = Field(0.5, description="Relaksasjonsfaktor", gt=0, le=1)
    
    class Config:
        """Pydantic konfigurasjon."""
        json_schema_extra = {
            "example": {
                "max_iterations": 100,
                "tolerance": 1e-6,
                "relaxation_factor": 0.5
            }
        }


class SolverSettings(BaseModel):
    """Innstillinger for numeriske løsere."""
    
    method: SolverMethod = SolverMethod.EFFECTIVENESS_NTU
    convergence: Optional[ConvergenceCriteria] = None
    enable_optimization: bool = True
    parallel_execution: bool = False
    
    class Config:
        """Pydantic konfigurasjon."""
        json_schema_extra = {
            "example": {
                "method": "effectiveness_ntu",
                "convergence": {
                    "max_iterations": 50,
                    "tolerance": 1e-5
                },
                "enable_optimization": True,
                "parallel_execution": False
            }
        }


class ValidationSettings(BaseModel):
    """Innstillinger for datavalidering."""
    
    strict_mode: bool = Field(True, description="Streng valideringsmodus")
    allow_extrapolation: bool = Field(False, description="Tillat ekstrapolering utenfor gyldighetsområde")
    warning_threshold: float = Field(0.9, description="Terskel for advarsler", ge=0, le=1)
    
    class Config:
        """Pydantic konfigurasjon."""
        json_schema_extra = {
            "example": {
                "strict_mode": True,
                "allow_extrapolation": False,
                "warning_threshold": 0.9
            }
        }


class OutputSettings(BaseModel):
    """Innstillinger for output formatering."""
    
    units: Dict[str, str] = Field(
        default_factory=lambda: {
            "temperature": "°C",
            "pressure": "Pa", 
            "mass_flow": "kg/s",
            "heat_transfer": "W",
            "area": "m²"
        },
        description="Enheter for output"
    )
    precision: int = Field(3, description="Antall desimaler", ge=1, le=10)
    scientific_notation: bool = Field(False, description="Bruk vitenskapelig notasjon")
    
    class Config:
        """Pydantic konfigurasjon."""
        json_schema_extra = {
            "example": {
                "units": {
                    "temperature": "°C",
                    "pressure": "Pa",
                    "mass_flow": "kg/s"
                },
                "precision": 3,
                "scientific_notation": False
            }
        }


class LoggingSettings(BaseModel):
    """Innstillinger for logging."""
    
    level: str = Field("INFO", description="Log nivå")
    log_to_file: bool = Field(False, description="Logg til fil")
    log_file_path: Optional[str] = Field(None, description="Sti til loggfil")
    include_timestamps: bool = Field(True, description="Inkluder tidsstempler")
    
    @validator('level')
    def validate_log_level(cls, v):
        """Validerer log nivå."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Log nivå må være en av: {valid_levels}")
        return v.upper()
    
    class Config:
        """Pydantic konfigurasjon."""
        json_schema_extra = {
            "example": {
                "level": "INFO",
                "log_to_file": False,
                "include_timestamps": True
            }
        }


class HXKitConfig(BaseModel):
    """Hovedkonfigurasjon for HXKit."""
    
    solver: Optional[SolverSettings] = None
    validation: Optional[ValidationSettings] = None
    output: Optional[OutputSettings] = None
    logging: Optional[LoggingSettings] = None
    
    # Globale innstillinger
    cache_results: bool = Field(True, description="Cache beregningsresultater")
    auto_save: bool = Field(False, description="Automatisk lagring av resultater")
    default_working_directory: Optional[str] = Field(None, description="Standard arbeidsmappe")
    
    class Config:
        """Pydantic konfigurasjon."""
        json_schema_extra = {
            "example": {
                "solver": {
                    "method": "effectiveness_ntu",
                    "enable_optimization": True
                },
                "validation": {
                    "strict_mode": True
                },
                "output": {
                    "precision": 3
                },
                "logging": {
                    "level": "INFO"
                },
                "cache_results": True,
                "auto_save": False
            }
        }


class CorrelationSettings(BaseModel):
    """Innstillinger for korrelasjoner."""
    
    friction_factor_correlation: str = Field("default", description="Friksjonsfaktor korrelasjon")
    heat_transfer_correlation: str = Field("default", description="Varmeoverføring korrelasjon")
    custom_correlations: Dict[str, Any] = Field(default_factory=dict, description="Tilpassede korrelasjoner")
    
    class Config:
        """Pydantic konfigurasjon."""
        json_schema_extra = {
            "example": {
                "friction_factor_correlation": "default",
                "heat_transfer_correlation": "default",
                "custom_correlations": {}
            }
        }


class MaterialProperties(BaseModel):
    """Materialegenskaper for plater."""
    
    name: str = Field(..., description="Materialnavn")
    thermal_conductivity: float = Field(..., description="Termisk konduktivitet [W/m·K]", gt=0)
    density: float = Field(..., description="Tetthet [kg/m³]", gt=0)
    specific_heat: float = Field(..., description="Spesifikk varmekapasitet [J/kg·K]", gt=0)
    surface_roughness: float = Field(1e-6, description="Overflateruhet [m]", ge=0)
    
    class Config:
        """Pydantic konfigurasjon."""
        json_schema_extra = {
            "example": {
                "name": "stainless_steel_316",
                "thermal_conductivity": 16.0,
                "density": 8000,
                "specific_heat": 500,
                "surface_roughness": 1e-6
            }
        }
"""
Pydantic schemas for geometriske beskrivelser.
"""

from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Dict, Any
from enum import Enum


class PlateSize(str, Enum):
    """Standard platestørrelser."""
    SMALL = "small"
    MEDIUM = "medium" 
    LARGE = "large"
    CUSTOM = "custom"


class PlateGeometryInput(BaseModel):
    """Input schema for plategeometri."""
    
    length: float = Field(..., description="Platelengde [m]", gt=0, le=5.0)
    width: float = Field(..., description="Platebredde [m]", gt=0, le=2.0)
    thickness: float = Field(..., description="Platetykkelse [m]", gt=0, le=0.01)
    channel_height: float = Field(..., description="Kanalhøyde [m]", gt=0, le=0.02)
    corrugation_angle: float = Field(60, description="Korrugeringsvinkel [grader]", ge=0, le=90)
    area_enhancement: float = Field(1.2, description="Arealforstørrelsesfaktor [-]", ge=1.0, le=3.0)
    
    class Config:
        """Pydantic konfigurasjon."""
        json_schema_extra = {
            "example": {
                "length": 0.6,
                "width": 0.2,
                "thickness": 0.0005,
                "channel_height": 0.004,
                "corrugation_angle": 60,
                "area_enhancement": 1.2
            }
        }


class StandardPlateInput(BaseModel):
    """Input schema for standard plategeometri."""
    
    size: PlateSize = Field(..., description="Standard platestørrelse")
    
    class Config:
        """Pydantic konfigurasjon."""
        json_schema_extra = {
            "example": {
                "size": "medium"
            }
        }


class HeatExchangerCoreInput(BaseModel):
    """Input schema for varmevekslerkjerne."""
    
    n_plates: int = Field(..., description="Antall plater", ge=3, le=200)
    plate_geometry: PlateGeometryInput = Field(..., description="Plategeometri")
    hot_channels: int = Field(..., description="Antall varme kanaler", ge=1)
    cold_channels: int = Field(..., description="Antall kalde kanaler", ge=1)
    
    @validator('hot_channels', 'cold_channels')
    def validate_channel_count(cls, v, values):
        """Validerer at kanaltall er konsistent med antall plater."""
        if 'n_plates' in values and 'hot_channels' in values:
            n_plates = values['n_plates']
            hot_channels = values.get('hot_channels', 0)
            
            if v + hot_channels != n_plates - 1:
                raise ValueError(f"hot_channels + cold_channels må være {n_plates - 1}")
        
        return v
    
    class Config:
        """Pydantic konfigurasjon."""
        json_schema_extra = {
            "example": {
                "n_plates": 21,
                "plate_geometry": {
                    "length": 0.6,
                    "width": 0.2,
                    "thickness": 0.0005,
                    "channel_height": 0.004
                },
                "hot_channels": 10,
                "cold_channels": 10
            }
        }


class GeometryConfig(BaseModel):
    """Konfigurasjon for geometriske parametere."""
    
    wall_thickness: float = Field(0.0005, description="Platetykkelse [m]", gt=0)
    wall_conductivity: float = Field(16.0, description="Termisk konduktivitet [W/m·K]", gt=0)
    material: str = Field("stainless_steel", description="Platemateriale")
    surface_roughness: float = Field(1e-6, description="Overflateruhet [m]", ge=0)
    
    class Config:
        """Pydantic konfigurasjon."""
        json_schema_extra = {
            "example": {
                "wall_thickness": 0.0005,
                "wall_conductivity": 16.0,
                "material": "stainless_steel",
                "surface_roughness": 1e-6
            }
        }


class GeometryOutput(BaseModel):
    """Output schema for geometriske egenskaper."""
    
    plate_area: float = Field(..., description="Plate overflateareal [m²]")
    effective_area: float = Field(..., description="Effektivt varmeoverføringsareal [m²]")
    flow_area: float = Field(..., description="Strømningsareal per kanal [m²]")
    hydraulic_diameter: float = Field(..., description="Hydraulisk diameter [m]")
    wetted_perimeter: float = Field(..., description="Fuktet perimeter [m]")
    total_heat_transfer_area: float = Field(..., description="Totalt varmeoverføringsareal [m²]")
    hot_side_flow_area: float = Field(..., description="Varm side strømningsareal [m²]")
    cold_side_flow_area: float = Field(..., description="Kald side strømningsareal [m²]")
    channel_configuration: str = Field(..., description="Kanalkonfigurasjon")
    
    class Config:
        """Pydantic konfigurasjon."""
        json_schema_extra = {
            "example": {
                "plate_area": 0.12,
                "effective_area": 0.144,
                "flow_area": 0.0008,
                "hydraulic_diameter": 0.008,
                "wetted_perimeter": 0.408,
                "total_heat_transfer_area": 2.88,
                "hot_side_flow_area": 0.008,
                "cold_side_flow_area": 0.008,
                "channel_configuration": "10H-10C"
            }
        }


class OptimizationConstraints(BaseModel):
    """Begrensninger for geometrioptimalisering."""
    
    min_plates: int = Field(5, description="Minimum antall plater", ge=3)
    max_plates: int = Field(50, description="Maksimum antall plater", le=200)
    max_pressure_drop: float = Field(500, description="Maks trykkfall [Pa]", gt=0)
    min_effectiveness: float = Field(0.6, description="Minimum effectiveness [-]", ge=0, le=1)
    target_effectiveness: float = Field(0.8, description="Ønsket effectiveness [-]", ge=0, le=1)
    
    @validator('target_effectiveness')
    def validate_target_effectiveness(cls, v, values):
        """Validerer at ønsket effectiveness er over minimum."""
        if 'min_effectiveness' in values and v < values['min_effectiveness']:
            raise ValueError("target_effectiveness må være >= min_effectiveness")
        return v
    
    class Config:
        """Pydantic konfigurasjon."""
        json_schema_extra = {
            "example": {
                "min_plates": 5,
                "max_plates": 50,
                "max_pressure_drop": 500,
                "min_effectiveness": 0.6,
                "target_effectiveness": 0.8
            }
        }
"""
Pydantic schemas for termodynamiske tilstander og beregninger.
"""

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
    wet_bulb: Optional[float] = Field(None, description="Våtbulbtemperatur [°C]")
    
    @model_validator(mode='after')
    def validate_humidity_inputs(self):
        """Validerer at kun en type fuktighetsinput er oppgitt."""
        humidity_fields = [self.relative_humidity, self.humidity_ratio, self.dew_point, self.wet_bulb]
        provided_count = sum(1 for field in humidity_fields if field is not None)
        
        if provided_count != 1:
            raise ValueError("Nøyaktig en av følgende må oppgis: relative_humidity, humidity_ratio, dew_point, wet_bulb")
        
        return self
    
    class Config:
        """Pydantic konfigurasjon."""
        json_json_schema_extra = {
            "example": {
                "temperature": 22.0,
                "pressure": 101325,
                "relative_humidity": 45.0
            }
        }


class MoistAirOutput(BaseModel):
    """Output schema for fuktig luft tilstand."""
    
    temperature: float = Field(..., description="Tørrbulbtemperatur [°C]")
    pressure: float = Field(..., description="Trykk [Pa]")
    relative_humidity: float = Field(..., description="Relativ fuktighet [%]")
    humidity_ratio: float = Field(..., description="Fuktighetsforhold [kg/kg]")
    dew_point: float = Field(..., description="Duggpunkt [°C]")
    wet_bulb_temperature: float = Field(..., description="Våtbulbtemperatur [°C]")
    density: float = Field(..., description="Tetthet [kg/m³]")
    enthalpy: float = Field(..., description="Entalpi [kJ/kg]")
    
    class Config:
        """Pydantic konfigurasjon."""
        json_json_schema_extra = {
            "example": {
                "temperature": 22.0,
                "pressure": 101325,
                "relative_humidity": 45.0,
                "humidity_ratio": 0.0075,
                "dew_point": 9.8,
                "wet_bulb_temperature": 15.2,
                "density": 1.19,
                "enthalpy": 41.2
            }
        }


class PsychrometricConditions(BaseModel):
    """Schema for psykrometriske forhold."""
    
    hot_side: MoistAirInput = Field(..., description="Varm side innløp")
    cold_side: MoistAirInput = Field(..., description="Kald side innløp")
    
    class Config:
        """Pydantic konfigurasjon."""
        json_schema_extra = {
            "example": {
                "hot_side": {
                    "temperature": 22.0,
                    "relative_humidity": 40.0
                },
                "cold_side": {
                    "temperature": -10.0,
                    "relative_humidity": 80.0
                }
            }
        }


class FlowConditions(BaseModel):
    """Schema for strømningsforhold."""
    
    hot_mass_flow: float = Field(..., description="Varm side massestrøm [kg/s]", gt=0)
    cold_mass_flow: float = Field(..., description="Kald side massestrøm [kg/s]", gt=0)
    
    class Config:
        """Pydantic konfigurasjon."""
        json_schema_extra = {
            "example": {
                "hot_mass_flow": 0.1,
                "cold_mass_flow": 0.1
            }
        }


class MixingCalculation(BaseModel):
    """Schema for blandingsberegning."""
    
    stream1: MoistAirInput = Field(..., description="Første luftstrøm")
    stream1_flow: float = Field(..., description="Massestrøm første strøm [kg/s]", gt=0)
    stream2: MoistAirInput = Field(..., description="Andre luftstrøm")  
    stream2_flow: float = Field(..., description="Massestrøm andre strøm [kg/s]", gt=0)
    
    class Config:
        """Pydantic konfigurasjon."""
        json_schema_extra = {
            "example": {
                "stream1": {
                    "temperature": 25.0,
                    "relative_humidity": 30.0
                },
                "stream1_flow": 0.05,
                "stream2": {
                    "temperature": 15.0,
                    "relative_humidity": 80.0
                },
                "stream2_flow": 0.05
            }
        }
"""
Pydantic schemas for input/output validering og serialisering.

Dette modulet inneholder alle Pydantic-modeller som brukes for:
- API input/output
- Konfigurasjonsfiler
- Data validering
- Serialisering til JSON/YAML
"""

from .thermodynamics_schemas import (
    MoistAirInput, 
    MoistAirOutput, 
    PsychrometricConditions,
    FlowConditions,
    MixingCalculation
)
from .geometry_schemas import (
    PlateGeometryInput,
    HeatExchangerCoreInput,
    GeometryConfig,
    GeometryOutput,
    OptimizationConstraints
)
from .analysis_schemas import (
    AnalysisInput,
    AnalysisOutput,
    PerformanceMapOutput,
    OptimizationInput,
    OptimizationOutput
)
from .config_schemas import (
    HXKitConfig,
    SolverSettings,
    ValidationSettings,
    OutputSettings,
    LoggingSettings,
    MaterialProperties
)

__all__ = [
    # Thermodynamics
    "MoistAirInput",
    "MoistAirOutput", 
    "PsychrometricConditions",
    "FlowConditions",
    "MixingCalculation",
    
    # Geometry
    "PlateGeometryInput",
    "HeatExchangerCoreInput",
    "GeometryConfig",
    "GeometryOutput",
    "OptimizationConstraints",
    
    # Analysis
    "AnalysisInput",
    "AnalysisOutput",
    "PerformanceMapOutput",
    "OptimizationInput",
    "OptimizationOutput",
    
    # Configuration
    "HXKitConfig",
    "SolverSettings",
    "ValidationSettings", 
    "OutputSettings",
    "LoggingSettings",
    "MaterialProperties",
]
