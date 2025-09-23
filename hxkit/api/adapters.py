"""
Adapters som kobler Pydantic schemas til kjernefunksjonaliteten.

Disse klassene håndterer konvertering mellom Pydantic modeller og 
de interne datastrukturene i hxkit.
"""

from typing import Dict, Any, List
from ..thermodynamics import MoistAir, Psychrometrics
from ..geometries import PlateGeometry, HeatExchangerCore, GeometryFactory
from ..plate_heat_exchanger import PlateHeatExchanger
from ..schemas.thermodynamics_schemas import (
    MoistAirInput, MoistAirOutput, PsychrometricConditions, MixingCalculation
)
from ..schemas.geometry_schemas import (
    PlateGeometryInput, HeatExchangerCoreInput, GeometryOutput
)
from ..schemas.analysis_schemas import (
    AnalysisInput, AnalysisOutput, PerformanceMapOutput
)


class ThermodynamicsAdapter:
    """Adapter for termodynamikk schemas."""
    
    @staticmethod
    def from_schema(schema: MoistAirInput) -> MoistAir:
        """Konverterer MoistAirInput schema til MoistAir objekt."""
        kwargs = {"temperature": schema.temperature, "pressure": schema.pressure}
        
        if schema.relative_humidity is not None:
            kwargs["relative_humidity"] = schema.relative_humidity
        elif schema.humidity_ratio is not None:
            kwargs["humidity_ratio"] = schema.humidity_ratio
        elif schema.dew_point is not None:
            # Konverter duggpunkt til fuktighetsforhold
            # Implementer konvertering
            raise NotImplementedError("Duggpunkt konvertering ikke implementert ennå")
        elif schema.wet_bulb is not None:
            # Konverter våtbulb til fuktighetsforhold
            raise NotImplementedError("Våtbulb konvertering ikke implementert ennå")
        
        return MoistAir(**kwargs)
    
    @staticmethod
    def to_schema(air: MoistAir) -> MoistAirOutput:
        """Konverterer MoistAir objekt til MoistAirOutput schema."""
        return MoistAirOutput(
            temperature=air.temperature,
            pressure=air.pressure,
            relative_humidity=air.relative_humidity,
            humidity_ratio=air.humidity_ratio,
            dew_point=0.0,  # TODO: Implementer duggpunkt beregning
            wet_bulb_temperature=air.wet_bulb_temperature,
            density=air.density,
            enthalpy=air.enthalpy
        )
    
    @staticmethod
    def mixing_from_schema(schema: MixingCalculation) -> MoistAir:
        """Utfører blandingsberegning fra schema."""
        air1 = ThermodynamicsAdapter.from_schema(schema.stream1)
        air2 = ThermodynamicsAdapter.from_schema(schema.stream2)
        
        return Psychrometrics.mixing_ratio(
            air1, schema.stream1_flow,
            air2, schema.stream2_flow
        )


class GeometryAdapter:
    """Adapter for geometri schemas."""
    
    @staticmethod
    def plate_geometry_from_schema(schema: PlateGeometryInput) -> PlateGeometry:
        """Konverterer PlateGeometryInput til PlateGeometry objekt."""
        return PlateGeometry(
            length=schema.length,
            width=schema.width,
            thickness=schema.thickness,
            channel_height=schema.channel_height,
            corrugation_angle=schema.corrugation_angle,
            area_enhancement=schema.area_enhancement
        )
    
    @staticmethod
    def plate_geometry_to_schema(geom: PlateGeometry) -> GeometryOutput:
        """Konverterer PlateGeometry til GeometryOutput schema."""
        return GeometryOutput(
            plate_area=geom.plate_area,
            effective_area=geom.effective_area,
            flow_area=geom.flow_area,
            hydraulic_diameter=geom.hydraulic_diameter,
            wetted_perimeter=geom.wetted_perimeter,
            total_heat_transfer_area=0.0,  # Trenger core for dette
            hot_side_flow_area=0.0,
            cold_side_flow_area=0.0,
            channel_configuration="N/A"
        )
    
    @staticmethod
    def core_from_schema(schema: HeatExchangerCoreInput) -> HeatExchangerCore:
        """Konverterer HeatExchangerCoreInput til HeatExchangerCore objekt."""
        plate_geom = GeometryAdapter.plate_geometry_from_schema(schema.plate_geometry)
        
        return HeatExchangerCore(
            n_plates=schema.n_plates,
            plate_geometry=plate_geom,
            hot_channels=schema.hot_channels,
            cold_channels=schema.cold_channels
        )
    
    @staticmethod
    def core_to_schema(core: HeatExchangerCore) -> GeometryOutput:
        """Konverterer HeatExchangerCore til GeometryOutput schema."""
        plate_output = GeometryAdapter.plate_geometry_to_schema(core.plate_geometry)
        
        # Oppdater med core-spesifikk informasjon
        plate_output.total_heat_transfer_area = core.total_heat_transfer_area
        plate_output.hot_side_flow_area = core.hot_side_flow_area
        plate_output.cold_side_flow_area = core.cold_side_flow_area
        plate_output.channel_configuration = core.channel_configuration()
        
        return plate_output


class AnalysisAdapter:
    """Adapter for analyse schemas."""
    
    @staticmethod
    def analyze_from_schema(schema: AnalysisInput) -> Dict[str, Any]:
        """Utfører varmeveksleranalyse fra schema."""
        # Konverter input schemas til objekter
        hot_inlet = ThermodynamicsAdapter.from_schema(schema.conditions.hot_side)
        cold_inlet = ThermodynamicsAdapter.from_schema(schema.conditions.cold_side)
        core = GeometryAdapter.core_from_schema(schema.geometry)
        
        # Opprett varmeveksler og utfør analyse
        hx = PlateHeatExchanger(core)
        results = hx.analyze(
            hot_inlet, cold_inlet,
            schema.flow.hot_mass_flow, schema.flow.cold_mass_flow
        )
        
        return results
    
    @staticmethod
    def results_to_schema(results: Dict[str, Any]) -> AnalysisOutput:
        """Konverterer analyse resultater til AnalysisOutput schema."""
        # Konverter MoistAir objekter til schemas
        hot_outlet = ThermodynamicsAdapter.to_schema(results["hot_outlet"])
        cold_outlet = ThermodynamicsAdapter.to_schema(results["cold_outlet"])
        
        # Beregn temperatureffektivitet
        temp_eff = (
            (cold_outlet.temperature - results["cold_inlet_temp"]) /
            (results["hot_inlet_temp"] - results["cold_inlet_temp"])
            if "hot_inlet_temp" in results and "cold_inlet_temp" in results
            else None
        )
        
        return AnalysisOutput(
            heat_transfer_rate=results["heat_transfer_rate"],
            effectiveness=results["effectiveness"],
            ntu=results["ntu"],
            hot_outlet=hot_outlet,
            cold_outlet=cold_outlet,
            hot_pressure_drop=results["hot_pressure_drop"],
            cold_pressure_drop=results["cold_pressure_drop"],
            hot_velocity=results["hot_velocity"],
            cold_velocity=results["cold_velocity"],
            u_overall=results["u_overall"],
            hot_htc=results["hot_htc"],
            cold_htc=results["cold_htc"],
            temperature_effectiveness=temp_eff
        )


class ConfigAdapter:
    """Adapter for konfigurasjon schemas."""
    
    @staticmethod
    def load_config(config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Laster konfigurasjon fra dictionary."""
        # Implementer konfigurasjonslasting
        return config_dict
    
    @staticmethod
    def save_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """Lagrer konfigurasjon til dictionary."""
        # Implementer konfigurasjonslagring
        return config
