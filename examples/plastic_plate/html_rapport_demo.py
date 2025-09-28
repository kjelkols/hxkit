"""
Eksempel på bruk av HTML rapport generator for Plastic Plate Heat Exchanger.

Demonstrerer hvordan man genererer en frittstående HTML rapport med
interaktive 2D temperaturplott fra PlateHeatExchangerOutput data.
"""

import os
from datetime import datetime
from hxkit.schemas.plastic_plate_schemas import (
    PlasticPlateHeatExchangerOutput,
    PlasticPlateHeatExchangerInput,
    PlateGeometryInput,
    FlowDirectionInput,
    StreamInput,
    PlateMaterial,
    PerformanceMetrics,
    StreamOutput,
    PhaseChangeResults,
    GridResults,
    ConvergenceInfo
)
from hxkit.schemas.thermodynamics_schemas import MoistAirOutput, MoistAirInput
from hxkit.definitions import Direction
from hxkit.visualization.plastic_plate_html_report import save_html_report


def create_example_input_data() -> PlasticPlateHeatExchangerInput:
    """
    Lager eksempel input data for demonstrasjon.
    """
    input_data = PlasticPlateHeatExchangerInput(
        geometry=PlateGeometryInput(
            width=0.6,
            length=1.2,
            plate_thickness=0.001,
            channel_height=0.008,
            num_plates=20,
            plate_material=PlateMaterial.GLASS_FIBER_PLASTIC
        ),
        flow_directions=FlowDirectionInput(
            hot_direction=Direction.NORTH,
            cold_direction=Direction.SOUTH
        ),
        hot_stream=StreamInput(
            moist_air=MoistAirInput(
                temperature=35.0,
                pressure=101325,
                relative_humidity=60.0
            ),
            mass_flow=2.5
        ),
        cold_stream=StreamInput(
            moist_air=MoistAirInput(
                temperature=15.0,
                pressure=101325,
                relative_humidity=40.0
            ),
            mass_flow=2.0
        ),
        grid_resolution=(12, 15),
        convergence_tolerance=1e-6,
        max_iterations=500
    )
    return input_data


def create_example_output_data() -> PlasticPlateHeatExchangerOutput:
    """
    Lager eksempel output data med realistiske verdier inkludert grid resultater.
    """
    
    # Lag 2D temperaturfelter for demonstrasjon
    width_cells, length_cells = 12, 15
    
    # Plate temperaturer (gradient fra varm til kald side)
    plate_temps = []
    for i in range(length_cells):
        row = []
        for j in range(width_cells):
            # Gradient fra 30°C til 20°C
            temp = 30.0 - (i / (length_cells - 1)) * 10.0 + (j / width_cells - 0.5) * 2.0
            row.append(temp)
        plate_temps.append(row)
    
    # Varm luft temperaturer (starter høyere, kjøles ned)
    hot_air_temps = []
    for i in range(length_cells):
        row = []
        for j in range(width_cells):
            temp = 35.0 - (i / (length_cells - 1)) * 12.0 + (j / width_cells - 0.5) * 1.5
            row.append(temp)
        hot_air_temps.append(row)
    
    # Kald luft temperaturer (starter lavere, varmes opp)
    cold_air_temps = []
    for i in range(length_cells):
        row = []
        for j in range(width_cells):
            temp = 15.0 + (i / (length_cells - 1)) * 8.0 + (j / width_cells - 0.5) * 1.0
            row.append(temp)
        cold_air_temps.append(row)
    
    # Beregn statistikk
    all_plate_temps = [temp for row in plate_temps for temp in row]
    max_plate_temp = max(all_plate_temps)
    min_plate_temp = min(all_plate_temps)
    mean_plate_temp = sum(all_plate_temps) / len(all_plate_temps)
    std_plate_temp = (sum((t - mean_plate_temp)**2 for t in all_plate_temps) / len(all_plate_temps))**0.5
    temp_uniformity = std_plate_temp / mean_plate_temp if mean_plate_temp > 0 else 0
    
    # Opprett eksempel input data
    input_data = create_example_input_data()
    
    # Opprett komplette output data
    output_data = PlasticPlateHeatExchangerOutput(
        input_data=input_data,
        performance=PerformanceMetrics(
            effectiveness=0.78,
            ntu=2.45,
            heat_transfer_rate=12.5,
            pressure_drop_hot=45.2,
            pressure_drop_cold=38.7,
            overall_heat_transfer_coefficient=25.3
        ),
        hot_outlet=StreamOutput(
            moist_air=MoistAirOutput(
                temperature=22.3,
                pressure=101280,
                relative_humidity=85.2,
                humidity_ratio=0.0142,
                dew_point=19.8,
                wet_bulb=20.7,
                density=1.184,
                specific_volume=0.844,
                enthalpy=58.5
            ),
            mass_flow=2.5,
            volume_flow=2.11,
            enthalpy_flow=78.2
        ),
        cold_outlet=StreamOutput(
            moist_air=MoistAirOutput(
                temperature=27.8,
                pressure=101287,
                relative_humidity=32.1,
                humidity_ratio=0.0089,
                dew_point=11.2,
                wet_bulb=18.4,
                density=1.148,
                specific_volume=0.871,
                enthalpy=49.8
            ),
            mass_flow=2.0,
            volume_flow=1.74,
            enthalpy_flow=59.8
        ),
        phase_changes=PhaseChangeResults(
            condensation_rate=0.0,
            frost_thickness=0.0,
            condensation_occurred=False,
            frost_occurred=False
        ),
        grid_results=GridResults(
            grid_resolution=(width_cells, length_cells),
            plate_temperatures=plate_temps,
            hot_air_temperatures=hot_air_temps,
            cold_air_temperatures=cold_air_temps,
            max_plate_temperature=max_plate_temp,
            min_plate_temperature=min_plate_temp,
            temperature_uniformity=temp_uniformity
        ),
        convergence=ConvergenceInfo(
            converged=True,
            iterations=127,
            final_residual=4.2e-7,
            convergence_tolerance=1e-6,
            computation_time=2.34
        ),
        analysis_timestamp=datetime.now().isoformat(),
        solver_version="HXKit v0.2.0"
    )
    
    return output_data


def main():
    """Hovedfunksjon som demonstrerer HTML rapport generering."""
    
    print("HTML Rapport Generator - Plastic Plate Heat Exchanger")
    print("=" * 60)
    
    # 1. Opprett eksempel output data
    print("\\n1. Oppretter eksempel output data...")
    output_data = create_example_output_data()
    print(f"   ✓ Output data opprettet med {output_data.grid_results.grid_resolution if output_data.grid_results else 'ingen'} grid")
    print(f"   ✓ Effektivitet: {output_data.performance.effectiveness:.1%}")
    print(f"   ✓ Varmeoverføring: {output_data.performance.heat_transfer_rate:.1f} kW")
    
    # 2. Generer HTML rapport
    print("\\n2. Genererer HTML rapport...")
    
    # Opprett output mappe hvis den ikke eksisterer
    output_dir = "rapport_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"   ✓ Opprettet output katalog: {output_dir}")
    
    # Generer filnavn med timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_filepath = os.path.join(output_dir, f"varmeveksler_rapport_{timestamp}.html")
    
    # Lagre rapport
    save_html_report(
        output_data=output_data,
        filepath=html_filepath,
        title="Plastic Plate Heat Exchanger - Analyse Rapport",
        description="Detaljert analyse av plastic plate varmeveksler med 2D temperaturfordeling og ytelsesmålinger."
    )
    
    print(f"   ✓ HTML rapport generert: {html_filepath}")
    
    # 3. Vis rapport informasjon
    print("\\n3. Rapport innhold:")
    print("   • Sammendrag med nøkkeltall")
    print("   • Detaljerte ytelsesparametre") 
    print("   • Luftstrømmer ved utløp")
    print("   • Faseendringer (kondensasjon/rim)")
    print("   • Numerisk konvergens informasjon")
    print("   • Interaktive 2D temperaturplott")
    
    # 4. Instruksjoner for bruk
    print("\\n4. Bruk av rapport:")
    print(f"   • Åpne filen i en nettleser: {html_filepath}")
    print("   • Rapporten er frittstående og krever ingen internett-tilkobling")
    print("   • Hover over temperaturplottene for detaljerte verdier")
    print("   • Rapporten kan deles via epost eller lagres i rapportsystemer")
    
    # 5. Vis filstørrelse og statistikk
    if os.path.exists(html_filepath):
        file_size = os.path.getsize(html_filepath)
        print(f"\\n5. Rapport statistikk:")
        print(f"   • Filstørrelse: {file_size / 1024:.1f} KB")
        if output_data.grid_results:
            print(f"   • Grid oppløsning: {output_data.grid_results.grid_resolution[0]} × {output_data.grid_results.grid_resolution[1]} celler")
            print(f"   • Temperaturområde: {output_data.grid_results.min_plate_temperature:.1f}°C - {output_data.grid_results.max_plate_temperature:.1f}°C")
            print(f"   • Temperaturuniformitet: {output_data.grid_results.temperature_uniformity:.3f}")
        else:
            print("   • Grid data: Ikke tilgjengelig")
    
    print("\\n✅ Eksempel fullført!")
    print("\\nRapporten kan nå åpnes i en nettleser for å se interaktive visualiseringer.")


def create_simple_report_example():
    """Lag et enkelt eksempel uten grid data."""
    
    print("\\nLager også en enkel rapport uten grid data...")
    
    # Opprett enkel input konfigurasjon
    simple_input = create_example_input_data()
    
    # Enkel output uten grid resultater
    simple_output = PlasticPlateHeatExchangerOutput(
        input_data=simple_input,
        performance=PerformanceMetrics(
            effectiveness=0.65,
            ntu=1.85,
            heat_transfer_rate=8.3,
            pressure_drop_hot=28.5,
            pressure_drop_cold=32.1,
            overall_heat_transfer_coefficient=None
        ),
        hot_outlet=StreamOutput(
            moist_air=MoistAirOutput(
                temperature=18.5,
                pressure=101290,
                relative_humidity=75.0,
                humidity_ratio=0.0098,
                dew_point=14.2,
                wet_bulb=16.8,
                density=1.198,
                specific_volume=0.835,
                enthalpy=43.2
            ),
            mass_flow=1.8,
            volume_flow=1.50,
            enthalpy_flow=45.8
        ),
        cold_outlet=StreamOutput(
            moist_air=MoistAirOutput(
                temperature=22.1,
                pressure=101285,
                relative_humidity=45.0,
                humidity_ratio=0.0076,
                dew_point=9.8,
                wet_bulb=15.9,
                density=1.175,
                specific_volume=0.851,
                enthalpy=41.5
            ),
            mass_flow=1.5,
            volume_flow=1.28,
            enthalpy_flow=38.2
        ),
        phase_changes=PhaseChangeResults(
            condensation_rate=0.0,
            frost_thickness=0.0,
            condensation_occurred=False,
            frost_occurred=False
        ),
        grid_results=None,
        convergence=ConvergenceInfo(
            converged=True,
            iterations=89,
            final_residual=2.1e-7,
            convergence_tolerance=1e-6,
            computation_time=1.12
        ),
        analysis_timestamp=datetime.now().isoformat(),
        solver_version="HXKit v0.2.0"
    )
    
    # Lagre enkel rapport
    output_dir = "rapport_output"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    simple_filepath = os.path.join(output_dir, f"enkel_rapport_{timestamp}.html")
    
    save_html_report(
        output_data=simple_output,
        filepath=simple_filepath,
        title="Enkel Varmeveksler Rapport",
        description="Grunnleggende analyse uten detaljerte temperaturfelter."
    )
    
    print(f"   ✓ Enkel rapport lagret: {simple_filepath}")
    print("   (Denne rapporten viser meldinger om manglende grid data i plott-seksjonene)")


if __name__ == "__main__":
    main()
    create_simple_report_example()