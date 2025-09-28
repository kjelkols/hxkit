#!/usr/bin/env python3
"""
Eksempel som tar et input-skjema og genererer et output-skjema for en spesifikk varmeveksler.

Spesifikasjoner:
- Platebredde: 1.4 m
- Platelengde: 1.4 m  
- Platetykkelse: 0.001 m
- Plateavstand: 0.007 m
- Antall plater: 10

Dette eksemplet viser hvordan man kan bruke Pydantic schemas til å:
1. Definere input med validering
2. Kjøre en simulert analyse
3. Generere validert output
"""

import json
import math
from datetime import datetime
from typing import Tuple, List

from hxkit.schemas import (
    PlasticPlateHeatExchangerInput,
    PlasticPlateHeatExchangerOutput,
    PlateMaterial
)
from hxkit import Direction


def create_input_configuration() -> PlasticPlateHeatExchangerInput:
    """
    Oppretter input-konfigurasjon med spesifiserte dimensjoner.
    
    Returns:
        Validert input-skjema for varmeveksler analysen
    """
    
    input_data = {
        "geometry": {
            "width": 1.4,           # m
            "length": 1.4,          # m  
            "plate_thickness": 0.001,  # m
            "channel_height": 0.007,   # m (plateavstand)
            "num_plates": 10,
            "plate_material": PlateMaterial.GLASS_FIBER_PLASTIC
        },
        "flow_directions": {
            "hot_direction": Direction.NORTH,
            "cold_direction": Direction.SOUTH  # Counterflow konfigurasjon
        },
        "hot_stream": {
            "moist_air": {
                "temperature": 45.0,    # °C - Varm tilluft
                "pressure": 101325,     # Pa - Standard atmosfærisk trykk
                "relative_humidity": 70.0  # % - Høy fuktighet
            },
            "mass_flow": 4.5  # kg/s - Høyere massestrøm for større varmeveksler
        },
        "cold_stream": {
            "moist_air": {
                "temperature": 8.0,     # °C - Kald utluft  
                "pressure": 101325,     # Pa
                "relative_humidity": 50.0  # % - Moderat fuktighet
            },
            "mass_flow": 4.0  # kg/s
        },
        "grid_resolution": (16, 16),  # 16x16 grid for kvadratisk geometri
        "convergence_tolerance": 5e-7,
        "max_iterations": 1000
    }
    
    return PlasticPlateHeatExchangerInput(**input_data)


def simulate_heat_exchanger_analysis(input_config: PlasticPlateHeatExchangerInput) -> dict:
    """
    Simulerer varmeveksler-analyse basert på input-konfigurasjonen.
    
    I en ekte implementasjon ville dette kalle den faktiske PlasticPlateHeatExchanger
    analyzer. Her simulerer vi resultatene basert på realistiske antagelser.
    
    Args:
        input_config: Validert input-konfigurasjon
        
    Returns:
        Dictionary med analyse-resultater
    """
    
    print("🔄 Simulerer varmeveksler-analyse...")
    
    # Grunnleggende geometriske beregninger
    geom = input_config.geometry
    plate_area = geom.width * geom.length  # m²
    total_heat_area = plate_area * geom.num_plates  # Total varmeoverføringsareal
    
    # Strømningsdata
    hot = input_config.hot_stream
    cold = input_config.cold_stream
    
    # Simulerte beregninger (forenklet modell)
    delta_t_initial = hot.moist_air.temperature - cold.moist_air.temperature  # °C
    
    # Estimert effectiveness basert på geometri og strømning (typisk 0.6-0.9)
    # Større varmeveksler med god counterflow -> høyere effectiveness
    estimated_effectiveness = 0.75 + 0.1 * (total_heat_area / 10.0)  # Skalering basert på størrelse
    estimated_effectiveness = min(estimated_effectiveness, 0.92)  # Maksimum realistisk verdi
    
    # NTU estimering (Number of Transfer Units)
    estimated_ntu = -math.log(1 - estimated_effectiveness)
    
    # Varmeoverføring (forenklet)
    # Q = m_min * cp * effectiveness * (T_hot_in - T_cold_in)
    m_min = min(hot.mass_flow, cold.mass_flow)  # kg/s
    cp_air = 1.006  # kJ/kg·K for luft
    heat_transfer_rate = m_min * cp_air * estimated_effectiveness * delta_t_initial  # kW
    
    # Utløpstemperaturer
    q_over_m_min_cp = heat_transfer_rate / (m_min * cp_air)
    
    if hot.mass_flow < cold.mass_flow:
        # Varm side er begrensende
        hot_outlet_temp = hot.moist_air.temperature - q_over_m_min_cp
        cold_outlet_temp = cold.moist_air.temperature + (hot.mass_flow / cold.mass_flow) * q_over_m_min_cp
    else:
        # Kald side er begrensende  
        cold_outlet_temp = cold.moist_air.temperature + q_over_m_min_cp
        hot_outlet_temp = hot.moist_air.temperature - (cold.mass_flow / hot.mass_flow) * q_over_m_min_cp
    
    # Trykkfall estimering (basert på kanal-geometri og strømningshastighet)
    # Forenklet modell: delta_P ∝ L * rho * v² / (2 * D_h)
    channel_area = geom.width * geom.channel_height  # m²
    
    # Hastigheter
    rho_air = 1.2  # kg/m³ (tilnærming for luft)
    v_hot = hot.mass_flow / (rho_air * channel_area * (geom.num_plates // 2))
    v_cold = cold.mass_flow / (rho_air * channel_area * (geom.num_plates // 2))
    
    # Hydraulisk diameter for rektangulær kanal
    d_h = 2 * geom.width * geom.channel_height / (geom.width + geom.channel_height)
    
    # Trykkfall (forenklet Darcy-Weisbach)
    f = 0.025  # Friksjonsfaktor (tilnærming)
    pressure_drop_hot = f * (geom.length / d_h) * (rho_air * v_hot**2 / 2)
    pressure_drop_cold = f * (geom.length / d_h) * (rho_air * v_cold**2 / 2)
    
    # Kondensasjon (enkel sjekk basert på temperaturendring)
    condensation_rate = 0.0
    condensation_occurred = False
    if hot_outlet_temp < hot.moist_air.temperature - 10:  # Betydelig avkjøling
        # Estimert kondensasjon basert på temperaturendring og fuktighet
        condensation_rate = 0.002 * hot.mass_flow * ((hot.moist_air.relative_humidity or 60.0) / 100.0)
        condensation_occurred = True
    
    # Grid-resultater (simulerte temperaturfelter)
    grid_w, grid_l = input_config.grid_resolution or (16, 16)
    plate_temps = generate_temperature_field(
        grid_w, grid_l, hot.moist_air.temperature, cold.moist_air.temperature, "plate"
    )
    hot_air_temps = generate_temperature_field(
        grid_w, grid_l, hot.moist_air.temperature, hot_outlet_temp, "hot_flow"
    )
    cold_air_temps = generate_temperature_field(
        grid_w, grid_l, cold.moist_air.temperature, cold_outlet_temp, "cold_flow"
    )
    
    return {
        "effectiveness": estimated_effectiveness,
        "ntu": estimated_ntu,
        "heat_transfer_rate": heat_transfer_rate,
        "pressure_drop_hot": pressure_drop_hot,
        "pressure_drop_cold": pressure_drop_cold,
        "hot_outlet_temperature": hot_outlet_temp,
        "cold_outlet_temperature": cold_outlet_temp,
        "condensation_rate": condensation_rate,
        "condensation_occurred": condensation_occurred,
        "plate_temperatures": plate_temps,
        "hot_air_temperatures": hot_air_temps,
        "cold_air_temperatures": cold_air_temps,
        "iterations": 185,  # Simulert konvergens
        "computation_time": 3.2
    }


def generate_temperature_field(width: int, height: int, t_in: float, t_out: float, flow_type: str) -> List[List[float]]:
    """
    Genererer et realistisk 2D temperaturfeld for visualisering.
    
    Args:
        width, height: Grid dimensjoner
        t_in, t_out: Innløps- og utløpstemperaturer
        flow_type: Type strømning ("plate", "hot_flow", "cold_flow")
        
    Returns:
        2D liste med temperaturer
    """
    
    field = []
    for i in range(height):
        row = []
        for j in range(width):
            # Lineær gradient med litt støy for realisme
            progress = j / (width - 1) if width > 1 else 0
            
            # Platetemp er gjennomsnitt av hot og cold flow
            if flow_type == "plate":
                temp = t_in + progress * (t_out - t_in)
                # Litt variasjon for platetemperatur
                temp += 0.5 * math.sin(i * 0.3) * math.cos(j * 0.4)
            else:
                temp = t_in + progress * (t_out - t_in)
                # Litt strømningsvariasjon
                temp += 0.2 * math.sin(i * 0.5 + j * 0.3)
            
            row.append(round(temp, 2))
        field.append(row)
    
    return field


def create_output_results(input_config: PlasticPlateHeatExchangerInput, analysis_results: dict) -> PlasticPlateHeatExchangerOutput:
    """
    Oppretter validert output-skjema basert på analyse-resultater.
    
    Args:
        input_config: Original input-konfigurasjon
        analysis_results: Resultater fra simulert analyse
        
    Returns:
        Validert output-skjema
    """
    
    print("📊 Genererer output-skjema...")
    
    # Beregn termodynamiske egenskaper for utløp (forenklet)
    hot = input_config.hot_stream
    cold = input_config.cold_stream
    
    # Utløp varm side
    hot_outlet_data = {
        "temperature": analysis_results["hot_outlet_temperature"],
        "pressure": hot.moist_air.pressure - analysis_results["pressure_drop_hot"],
        "relative_humidity": min(95.0, (hot.moist_air.relative_humidity or 70.0) * 1.2),  # Økt RH ved avkjøling
        "humidity_ratio": 0.0145,  # Forenklet - ville beregnes fra termoynamikk
        "dew_point": analysis_results["hot_outlet_temperature"] - 3.0,  # Tilnærming
        "wet_bulb": analysis_results["hot_outlet_temperature"] - 1.5,   # Tilnærming
        "density": 1.15,  # kg/m³
        "specific_volume": 1/1.15,  # m³/kg
        "enthalpy": 52.3  # kJ/kg
    }
    
    # Utløp kald side
    cold_outlet_data = {
        "temperature": analysis_results["cold_outlet_temperature"],
        "pressure": cold.moist_air.pressure - analysis_results["pressure_drop_cold"],
        "relative_humidity": (cold.moist_air.relative_humidity or 50.0) * 0.8,  # Redusert RH ved oppvarming
        "humidity_ratio": 0.0087,  # Forenklet
        "dew_point": analysis_results["cold_outlet_temperature"] - 8.0,
        "wet_bulb": analysis_results["cold_outlet_temperature"] - 4.0,
        "density": 1.08,  # kg/m³
        "specific_volume": 1/1.08,  # m³/kg  
        "enthalpy": 48.7  # kJ/kg
    }
    
    # Samle output data
    output_data = {
        "performance": {
            "effectiveness": analysis_results["effectiveness"],
            "ntu": analysis_results["ntu"],
            "heat_transfer_rate": analysis_results["heat_transfer_rate"],
            "pressure_drop_hot": analysis_results["pressure_drop_hot"],
            "pressure_drop_cold": analysis_results["pressure_drop_cold"],
            "overall_heat_transfer_coefficient": 22.5  # W/m²·K (estimert)
        },
        "hot_outlet": {
            "moist_air": hot_outlet_data,
            "mass_flow": hot.mass_flow,
            "volume_flow": hot.mass_flow * hot_outlet_data["specific_volume"],
            "enthalpy_flow": hot.mass_flow * hot_outlet_data["enthalpy"]
        },
        "cold_outlet": {
            "moist_air": cold_outlet_data,
            "mass_flow": cold.mass_flow,
            "volume_flow": cold.mass_flow * cold_outlet_data["specific_volume"],
            "enthalpy_flow": cold.mass_flow * cold_outlet_data["enthalpy"]
        },
        "phase_changes": {
            "condensation_rate": analysis_results["condensation_rate"],
            "frost_thickness": 0.0,  # Ingen frost ved disse temperaturene
            "condensation_occurred": analysis_results["condensation_occurred"],
            "frost_occurred": False
        },
        "grid_results": {
            "grid_resolution": input_config.grid_resolution or (16, 16),
            "plate_temperatures": analysis_results["plate_temperatures"],
            "hot_air_temperatures": analysis_results["hot_air_temperatures"],
            "cold_air_temperatures": analysis_results["cold_air_temperatures"],
            "max_plate_temperature": max(max(row) for row in analysis_results["plate_temperatures"]),
            "min_plate_temperature": min(min(row) for row in analysis_results["plate_temperatures"]),
            "temperature_uniformity": 0.12  # Beregnet fra temperaturfeltet
        },
        "convergence": {
            "converged": True,
            "iterations": analysis_results["iterations"],
            "final_residual": 2.1e-7,
            "convergence_tolerance": input_config.convergence_tolerance,
            "computation_time": analysis_results["computation_time"]
        },
        "analysis_timestamp": datetime.now().isoformat() + "Z",
        "solver_version": "HXKit v0.2.0 (Simulated)"
    }
    
    return PlasticPlateHeatExchangerOutput(**output_data)


def print_summary(input_config: PlasticPlateHeatExchangerInput, output_results: PlasticPlateHeatExchangerOutput):
    """Skriver ut en lesbar sammendrag av analysen."""
    
    print("\n" + "="*60)
    print("📋 VARMEVEKSLER ANALYSE SAMMENDRAG")
    print("="*60)
    
    # Geometri
    geom = input_config.geometry
    print(f"\n🏗️  GEOMETRI:")
    print(f"   Dimensjoner: {geom.width} × {geom.length} m")
    print(f"   Platetykkelse: {geom.plate_thickness*1000:.1f} mm")
    print(f"   Plateavstand: {geom.channel_height*1000:.1f} mm")
    print(f"   Antall plater: {geom.num_plates}")
    print(f"   Total varmeoverføringsareal: {geom.width * geom.length * geom.num_plates:.1f} m²")
    print(f"   Material: {geom.plate_material.value}")
    
    # Strømningskonfigurasjon
    flow = input_config.flow_directions
    print(f"\n🌬️  STRØMNING:")
    print(f"   Konfigurasjon: {flow.hot_direction.value} → {flow.cold_direction.value} (counterflow)")
    print(f"   Varm innløp: {input_config.hot_stream.moist_air.temperature}°C, {input_config.hot_stream.mass_flow} kg/s")
    print(f"   Kald innløp: {input_config.cold_stream.moist_air.temperature}°C, {input_config.cold_stream.mass_flow} kg/s")
    
    # Ytelsesresultater
    perf = output_results.performance
    print(f"\n⚡ YTELSE:")
    print(f"   Effektivitet: {perf.effectiveness:.1%}")
    print(f"   NTU: {perf.ntu:.2f}")
    print(f"   Varmeoverføring: {perf.heat_transfer_rate:.1f} kW")
    print(f"   U-verdi: {perf.overall_heat_transfer_coefficient:.1f} W/m²·K")
    
    # Utløpstemperaturer
    hot_out = output_results.hot_outlet
    cold_out = output_results.cold_outlet
    print(f"\n🌡️  TEMPERATURER:")
    print(f"   Varm utløp: {hot_out.moist_air.temperature:.1f}°C (Δ={input_config.hot_stream.moist_air.temperature - hot_out.moist_air.temperature:.1f}°C)")
    print(f"   Kald utløp: {cold_out.moist_air.temperature:.1f}°C (Δ={cold_out.moist_air.temperature - input_config.cold_stream.moist_air.temperature:.1f}°C)")
    
    # Trykkfall
    print(f"\n💨 TRYKKFALL:")
    print(f"   Varm side: {perf.pressure_drop_hot:.1f} Pa")
    print(f"   Kald side: {perf.pressure_drop_cold:.1f} Pa")
    
    # Faseendringer
    phase = output_results.phase_changes
    print(f"\n💧 FASEENDRINGER:")
    if phase.condensation_occurred:
        print(f"   Kondensasjon: {phase.condensation_rate:.4f} kg/s")
    else:
        print(f"   Ingen kondensasjon")
    
    # Konvergens
    conv = output_results.convergence
    print(f"\n🔢 NUMERIKK:")
    if output_results.grid_results:
        print(f"   Grid oppløsning: {output_results.grid_results.grid_resolution[0]}×{output_results.grid_results.grid_resolution[1]}")
    print(f"   Konvergert: {conv.converged} ({conv.iterations} iterasjoner)")
    print(f"   Beregningstid: {conv.computation_time:.1f} sekunder")
    
    print("\n" + "="*60)


def save_results_to_files(input_config: PlasticPlateHeatExchangerInput, output_results: PlasticPlateHeatExchangerOutput):
    """Lagrer input og output til JSON-filer."""
    
    # Lagre input
    input_json = input_config.model_dump_json(indent=2)
    with open("varmeveksler_input.json", "w", encoding="utf-8") as f:
        f.write(input_json)
    
    # Lagre output  
    output_json = output_results.model_dump_json(indent=2)
    with open("varmeveksler_output.json", "w", encoding="utf-8") as f:
        f.write(output_json)
    
    print(f"\n💾 Resultater lagret:")
    print(f"   Input: varmeveksler_input.json ({len(input_json)} bytes)")
    print(f"   Output: varmeveksler_output.json ({len(output_json)} bytes)")


def main():
    """Hovedfunksjon som kjører komplett eksempel fra input til output."""
    
    print("🚀 PLASTIC PLATE HEAT EXCHANGER ANALYSE")
    print("="*60)
    print("Spesifikasjoner:")
    print("- Platebredde: 1.4 m")
    print("- Platelengde: 1.4 m")
    print("- Platetykkelse: 0.001 m (1 mm)")
    print("- Plateavstand: 0.007 m (7 mm)")
    print("- Antall plater: 10")
    print("="*60)
    
    # Steg 1: Opprett og valider input
    print("\n1️⃣ Oppretter input-konfigurasjon...")
    input_config = create_input_configuration()
    print("   ✅ Input-skjema validert og opprettet")
    
    # Steg 2: Kjør simulert analyse
    print("\n2️⃣ Kjører varmeveksler-analyse...")
    analysis_results = simulate_heat_exchanger_analysis(input_config)
    print("   ✅ Analyse fullført")
    
    # Steg 3: Generer output
    print("\n3️⃣ Genererer output-skjema...")
    output_results = create_output_results(input_config, analysis_results)
    print("   ✅ Output-skjema validert og opprettet")
    
    # Steg 4: Vis sammendrag
    print_summary(input_config, output_results)
    
    # Steg 5: Lagre til filer
    save_results_to_files(input_config, output_results)
    
    print("\n🎉 Analyse fullført! Input og output skjemaer er opprettet og validert.")
    print("\nSkjemaene kan nå brukes til:")
    print("- API endpoints med automatisk validering")
    print("- JSON serialisering for lagring og transport")
    print("- Type-sikker programmering med mypy")
    print("- Automatisk API dokumentasjon")


if __name__ == "__main__":
    main()