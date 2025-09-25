"""
API Adapters for hxkit - Kobler Pydantic schemas til kjernefunksjonalitet

Adapters fungerer som et "oversettelsslag" mellom:
- JSON/API data (Pydantic modeller) 
- Interne Python objekter (MoistAir, PlateGeometry, etc.)

Dette gjør det enkelt å bygge web-APIer, konfigurasjonsverktøy, og andre 
grensesnitt oppå hxkit kjernefunksjonaliteten.

Med den forenklede arkitekturen kan adapters nå bruke normale Python imports
uten komplekse lazy loading mekanismer.
"""

from typing import Dict, Any, TYPE_CHECKING
from ..geometries import PlateGeometry, HeatExchangerCore

# Enkle direkte imports
from ..thermodynamics import MoistAir
from ..plate_heat_exchanger import PlateHeatExchanger
from ..schemas.thermodynamics_schemas import (
    MoistAirInput, MoistAirOutput, PsychrometricConditions, FlowConditions,
    PlateGeometryInput, HeatExchangerCoreInput, AnalysisInput, AnalysisOutput
)


class ThermodynamicsAdapter:
    """
    Adapter for termodynamiske beregninger.
    
    Konverterer mellom Pydantic schemas og MoistAir objekter.
    """
    
    @staticmethod
    def from_schema(schema: MoistAirInput):
        """
        Konverterer MoistAirInput schema til MoistAir objekt.
        
        Args:
            schema: Validert Pydantic input schema
            
        Returns:
            MoistAir objekt for interne beregninger
        """
        kwargs = {
            "temperature": schema.temperature, 
            "pressure": schema.pressure
        }
        
        # Legg til engine hvis spesifisert
        if schema.engine is not None:
            kwargs["engine"] = schema.engine
        
        # Bestem hvilken fuktighetsparameter som er oppgitt
        if schema.relative_humidity is not None:
            kwargs["relative_humidity"] = schema.relative_humidity
        elif schema.humidity_ratio is not None:
            kwargs["humidity_ratio"] = schema.humidity_ratio
        elif schema.dew_point is not None:
            kwargs["dew_point"] = schema.dew_point
        elif schema.wet_bulb is not None:
            kwargs["wet_bulb"] = schema.wet_bulb
            
        return MoistAir(**kwargs)
    
    @staticmethod
    def to_schema(air) -> MoistAirOutput:
        """
        Konverterer MoistAir objekt til MoistAirOutput schema.
        
        Args:
            air: MoistAir objekt fra beregninger
            
        Returns:
            Strukturert output schema for API/JSON
        """
        return MoistAirOutput(
            temperature=air.temperature,
            pressure=air.pressure,
            relative_humidity=air.relative_humidity,
            humidity_ratio=air.humidity_ratio,
            dew_point=air.dew_point,
            wet_bulb=air.wet_bulb,
            density=air.density,
            specific_volume=air.specific_volume,
            enthalpy=air.enthalpy
        )


class GeometryAdapter:
    """
    Adapter for geometri konverteringer.
    
    Konverterer mellom Pydantic schemas og geometri objekter.
    """
    
    @staticmethod  
    def plate_from_schema(schema: PlateGeometryInput) -> PlateGeometry:
        """
        Konverterer PlateGeometryInput til PlateGeometry.
        
        Args:
            schema: Validert plate geometri input
            
        Returns:
            PlateGeometry objekt for beregninger
        """
        return PlateGeometry(
            length=schema.plate_width,
            width=schema.plate_height,
            thickness=0.0005,  # Standard verdi - kunne vært parameter
            channel_height=schema.plate_spacing,
            corrugation_angle=schema.chevron_angle
        )
    
    @staticmethod
    def core_from_schema(schema: HeatExchangerCoreInput) -> HeatExchangerCore:
        """
        Konverterer HeatExchangerCoreInput til HeatExchangerCore.
        
        Args:
            schema: Validert varmeveksler kjerne input
            
        Returns:
            HeatExchangerCore objekt for analyse
        """
        plate_geom = GeometryAdapter.plate_from_schema(schema.geometry)
        
        # Beregn kanaler basert på antall plater
        total_channels = schema.num_plates - 1
        hot_channels = total_channels // 2
        cold_channels = total_channels - hot_channels
        
        return HeatExchangerCore(
            n_plates=schema.num_plates,
            plate_geometry=plate_geom,
            hot_channels=hot_channels,
            cold_channels=cold_channels
        )


class AnalysisAdapter:
    """
    Adapter for varmeveksler analyse.
    
    Orkestrerer hele analysen fra Pydantic input til strukturert output.
    """
    
    @staticmethod
    def analyze_from_schema(schema: AnalysisInput) -> AnalysisOutput:
        """
        Utfører komplett varmeveksler analyse fra strukturert input.
        
        Dette er "hovedfunksjonen" som en web-API ville kalle.
        
        Args:
            schema: Komplett validert analyse input
            
        Returns:
            Strukturert analyse output klar for JSON serialisering
        """
        
        # 1. Konverter input schemas til kjerne objekter
        hot_air = ThermodynamicsAdapter.from_schema(schema.conditions.hot_side)
        cold_air = ThermodynamicsAdapter.from_schema(schema.conditions.cold_side)
        core = GeometryAdapter.core_from_schema(schema.core)
        
        # 2. Opprett varmeveksler og utfør analyse
        hx = PlateHeatExchanger(core)
        results = hx.analyze(
            hot_inlet=hot_air,
            cold_inlet=cold_air, 
            hot_mass_flow=schema.flow.hot_mass_flow,
            cold_mass_flow=schema.flow.cold_mass_flow
        )
        
        # 3. Konverter resultater til strukturert output
        return AnalysisOutput(
            hot_inlet=ThermodynamicsAdapter.to_schema(hot_air),
            cold_inlet=ThermodynamicsAdapter.to_schema(cold_air),
            hot_outlet=ThermodynamicsAdapter.to_schema(results["hot_outlet"]),
            cold_outlet=ThermodynamicsAdapter.to_schema(results["cold_outlet"]),
            heat_transfer_rate=results["heat_transfer_rate"],
            effectiveness=results["effectiveness"],
            hot_pressure_drop=results["hot_pressure_drop"],
            cold_pressure_drop=results["cold_pressure_drop"],
            overall_heat_transfer_coefficient=results["u_overall"],
            ntu=results["ntu"]
        )
    
    @staticmethod
    def analyze_from_json(json_data: str) -> str:
        """
        Convenience metode for JSON til JSON analyse.
        
        Args:
            json_data: JSON string med analyse input
            
        Returns:
            JSON string med analyse output
        """
        # Parse JSON til Pydantic schema (med automatisk validering)
        input_schema = AnalysisInput.model_validate_json(json_data)
        
        # Utfør analyse
        output_schema = AnalysisAdapter.analyze_from_schema(input_schema)
        
        # Konverter tilbake til JSON
        return output_schema.model_dump_json(indent=2)
