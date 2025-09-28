"""
Pydantic schemas for input/output validering og serialisering.
"""

from .thermodynamics_schemas import (
    HumidityInputType,
    MoistAirInput,
    MoistAirOutput,
    PsychrometricConditions,
    FlowConditions, 
    PlateGeometryInput,
    HeatExchangerCoreInput,
    AnalysisInput,
    AnalysisOutput,
)

from .plastic_plate_schemas import (
    # Input schemas
    PlateMaterial,
    PlateGeometryInput as PlasticPlateGeometryInput,
    FlowDirectionInput,
    StreamInput,
    PlasticPlateHeatExchangerInput,
    # Output schemas
    StreamOutput,
    PerformanceMetrics,
    PhaseChangeResults,
    GridResults,
    ConvergenceInfo,
    PlasticPlateHeatExchangerOutput,
)

__all__ = [
    # Thermodynamics schemas
    "HumidityInputType",
    "MoistAirInput", 
    "MoistAirOutput",
    "PsychrometricConditions",
    "FlowConditions", 
    "PlateGeometryInput",
    "HeatExchangerCoreInput",
    "AnalysisInput",
    "AnalysisOutput",
    
    # Plastic plate heat exchanger schemas - Input
    "PlateMaterial",
    "PlasticPlateGeometryInput", 
    "FlowDirectionInput",
    "StreamInput",
    "PlasticPlateHeatExchangerInput",
    
    # Plastic plate heat exchanger schemas - Output
    "StreamOutput",
    "PerformanceMetrics", 
    "PhaseChangeResults",
    "GridResults",
    "ConvergenceInfo",
    "PlasticPlateHeatExchangerOutput",
]