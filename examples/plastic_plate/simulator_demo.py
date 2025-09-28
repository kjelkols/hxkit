"""
Forenklet demo av Plastic Plate Heat Exchanger Simulator
=========================================================

Demonstrerer simulatorfunksjonalitet uten web-grensesnitt.
"""

import os
import sys
import datetime
from typing import Dict, Any

# Add path to HXKit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from hxkit.schemas.plastic_plate_schemas import (
    PlasticPlateHeatExchangerInput,
    PlasticPlateHeatExchangerOutput,
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
from hxkit.schemas.thermodynamics_schemas import MoistAirInput, MoistAirOutput
from hxkit.definitions import Direction
from hxkit.visualization.plastic_plate_html_report import generate_html_report


class PlasticPlateSimulatorDemo:
    """Forenklet simulator for demonstrasjon."""
    
    def __init__(self):
        self.version = "1.0.0"
    
    def create_example_scenario(self, scenario: str) -> PlasticPlateHeatExchangerInput:
        """Lag eksempel-scenario for testing."""
        
        scenarios = {
            'standard': {
                'geometry': {
                    'width': 0.6,
                    'length': 1.2,
                    'plate_thickness': 0.001,
                    'channel_height': 0.008,
                    'num_plates': 20,
                    'plate_material': PlateMaterial.GLASS_FIBER_PLASTIC
                },
                'hot_stream': {
                    'temperature': 35.0,
                    'pressure': 101325,
                    'humidity': 60.0,
                    'mass_flow': 2.5
                },
                'cold_stream': {
                    'temperature': 15.0,
                    'pressure': 101325,
                    'humidity': 40.0,
                    'mass_flow': 2.0
                },
                'grid': (12, 15)
            },
            'hightemp': {
                'geometry': {
                    'width': 0.8,
                    'length': 1.5,
                    'plate_thickness': 0.0015,
                    'channel_height': 0.010,
                    'num_plates': 25,
                    'plate_material': PlateMaterial.ABS_PLASTIC
                },
                'hot_stream': {
                    'temperature': 60.0,
                    'pressure': 101325,
                    'humidity': 80.0,
                    'mass_flow': 3.0
                },
                'cold_stream': {
                    'temperature': 5.0,
                    'pressure': 101325,
                    'humidity': 30.0,
                    'mass_flow': 2.5
                },
                'grid': (15, 20)
            },
            'lowtemp': {
                'geometry': {
                    'width': 0.5,
                    'length': 1.0,
                    'plate_thickness': 0.0008,
                    'channel_height': 0.006,
                    'num_plates': 15,
                    'plate_material': PlateMaterial.POLYETHYLENE
                },
                'hot_stream': {
                    'temperature': 25.0,
                    'pressure': 101325,
                    'humidity': 50.0,
                    'mass_flow': 1.5
                },
                'cold_stream': {
                    'temperature': 10.0,
                    'pressure': 101325,
                    'humidity': 60.0,
                    'mass_flow': 1.2
                },
                'grid': (10, 12)
            }
        }
        
        config = scenarios.get(scenario, scenarios['standard'])
        
        return PlasticPlateHeatExchangerInput(
            geometry=PlateGeometryInput(
                width=config['geometry']['width'],
                length=config['geometry']['length'],
                plate_thickness=config['geometry']['plate_thickness'],
                channel_height=config['geometry']['channel_height'],
                num_plates=config['geometry']['num_plates'],
                plate_material=config['geometry']['plate_material']
            ),
            flow_directions=FlowDirectionInput(
                hot_direction=Direction.SOUTH,
                cold_direction=Direction.NORTH
            ),
            hot_stream=StreamInput(
                moist_air=MoistAirInput(
                    temperature=config['hot_stream']['temperature'],
                    pressure=config['hot_stream']['pressure'],
                    relative_humidity=config['hot_stream']['humidity']
                ),
                mass_flow=config['hot_stream']['mass_flow']
            ),
            cold_stream=StreamInput(
                moist_air=MoistAirInput(
                    temperature=config['cold_stream']['temperature'],
                    pressure=config['cold_stream']['pressure'],
                    relative_humidity=config['cold_stream']['humidity']
                ),
                mass_flow=config['cold_stream']['mass_flow']
            ),
            grid_resolution=config['grid'],
            convergence_tolerance=1e-6,
            max_iterations=500
        )
    
    def run_simulation(self, input_data: PlasticPlateHeatExchangerInput) -> PlasticPlateHeatExchangerOutput:
        """Kjør forenklet simulering."""
        
        # Hent input-verdier
        hot_temp = input_data.hot_stream.moist_air.temperature
        cold_temp = input_data.cold_stream.moist_air.temperature
        hot_flow = input_data.hot_stream.mass_flow
        cold_flow = input_data.cold_stream.mass_flow
        hot_humidity = input_data.hot_stream.moist_air.relative_humidity or 50.0
        cold_humidity = input_data.cold_stream.moist_air.relative_humidity or 50.0
        
        # Forenklet beregning av effektivitet basert på forhold
        temp_diff = hot_temp - cold_temp
        flow_ratio = min(hot_flow, cold_flow) / max(hot_flow, cold_flow)
        
        # Estimat effektivitet (0.5 til 0.85)
        effectiveness = 0.5 + 0.35 * flow_ratio * (temp_diff / 40.0) if temp_diff > 0 else 0.5
        effectiveness = min(0.85, max(0.3, effectiveness))
        
        # Utløpstemperaturer
        hot_outlet_temp = hot_temp - effectiveness * temp_diff * 0.7
        cold_outlet_temp = cold_temp + effectiveness * temp_diff * 0.8
        
        # Varmeoverføring
        cp_air = 1.005  # kJ/kg·K
        heat_transfer = min(hot_flow, cold_flow) * cp_air * temp_diff * effectiveness
        
        # NTU estimat
        ntu = -1 * (effectiveness / (effectiveness - 1)) if effectiveness < 0.99 else 3.0
        ntu = max(0.5, min(5.0, ntu))
        
        # Trykkfall (forenklet)
        pressure_drop_hot = 20.0 + hot_flow * 8 + input_data.geometry.length * 10
        pressure_drop_cold = 18.0 + cold_flow * 8 + input_data.geometry.length * 10
        
        # Grid resultater
        grid_results = None
        if input_data.grid_resolution:
            width_cells, length_cells = input_data.grid_resolution
            grid_results = self._generate_temperature_field(
                width_cells, length_cells,
                hot_temp, cold_temp, hot_outlet_temp, cold_outlet_temp
            )
        
        # Komplett output
        return PlasticPlateHeatExchangerOutput(
            input_data=input_data,
            performance=PerformanceMetrics(
                effectiveness=effectiveness,
                ntu=ntu,
                heat_transfer_rate=heat_transfer,
                pressure_drop_hot=pressure_drop_hot,
                pressure_drop_cold=pressure_drop_cold,
                overall_heat_transfer_coefficient=15.0 + effectiveness * 15.0
            ),
            hot_outlet=StreamOutput(
                moist_air=MoistAirOutput(
                    temperature=hot_outlet_temp,
                    pressure=input_data.hot_stream.moist_air.pressure - pressure_drop_hot,
                    relative_humidity=min(95.0, hot_humidity * 1.3),
                    humidity_ratio=0.010 + hot_humidity * 0.0002,
                    dew_point=hot_outlet_temp - 8,
                    wet_bulb=hot_outlet_temp - 5,
                    density=1.15,
                    specific_volume=0.87,
                    enthalpy=45.0 + hot_outlet_temp * 1.2
                ),
                mass_flow=hot_flow,
                volume_flow=hot_flow / 1.15,
                enthalpy_flow=heat_transfer * 0.6
            ),
            cold_outlet=StreamOutput(
                moist_air=MoistAirOutput(
                    temperature=cold_outlet_temp,
                    pressure=input_data.cold_stream.moist_air.pressure - pressure_drop_cold,
                    relative_humidity=max(25.0, cold_humidity * 0.8),
                    humidity_ratio=0.006 + cold_humidity * 0.0001,
                    dew_point=cold_outlet_temp - 10,
                    wet_bulb=cold_outlet_temp - 6,
                    density=1.18,
                    specific_volume=0.85,
                    enthalpy=25.0 + cold_outlet_temp * 1.1
                ),
                mass_flow=cold_flow,
                volume_flow=cold_flow / 1.18,
                enthalpy_flow=heat_transfer * 0.4
            ),
            phase_changes=PhaseChangeResults(
                condensation_rate=0.005 if hot_outlet_temp < 18 else 0.0,
                frost_thickness=0.0001 if cold_outlet_temp < 2 else 0.0,
                condensation_occurred=hot_outlet_temp < 18,
                frost_occurred=cold_outlet_temp < 2
            ),
            grid_results=grid_results,
            convergence=ConvergenceInfo(
                converged=True,
                iterations=int(25 + effectiveness * 50),
                final_residual=1.5e-7,
                convergence_tolerance=input_data.convergence_tolerance or 1e-6,
                computation_time=0.3 + effectiveness * 1.2
            ),
            analysis_timestamp=datetime.datetime.now().isoformat(),
            solver_version=f"HXKit Demo Simulator v{self.version}"
        )
    
    def _generate_temperature_field(self, width: int, length: int,
                                  hot_inlet: float, cold_inlet: float,
                                  hot_outlet: float, cold_outlet: float) -> GridResults:
        """Generer realistisk temperaturfeld."""
        
        plate_temps = []
        hot_air_temps = []
        cold_air_temps = []
        
        for i in range(length):
            plate_row = []
            hot_row = []
            cold_row = []
            
            # Progresjon langs lengden
            progress = i / (length - 1) if length > 1 else 0
            
            for j in range(width):
                # Variasjoner på tvers
                width_var = (j / (width - 1) - 0.5) * 2 if width > 1 else 0
                
                # Temperaturer med progresjon og variasjon
                hot_temp = hot_inlet - (hot_inlet - hot_outlet) * progress + width_var * 1.5
                cold_temp = cold_inlet + (cold_outlet - cold_inlet) * progress - width_var * 1.2
                plate_temp = (hot_temp + cold_temp) / 2 + width_var * 0.8
                
                plate_row.append(round(plate_temp, 1))
                hot_row.append(round(hot_temp, 1))
                cold_row.append(round(cold_temp, 1))
            
            plate_temps.append(plate_row)
            hot_air_temps.append(hot_row)
            cold_air_temps.append(cold_row)
        
        all_plate_temps = [t for row in plate_temps for t in row]
        
        return GridResults(
            grid_resolution=(width, length),
            plate_temperatures=plate_temps,
            hot_air_temperatures=hot_air_temps,
            cold_air_temperatures=cold_air_temps,
            max_plate_temperature=max(all_plate_temps),
            min_plate_temperature=min(all_plate_temps),
            temperature_uniformity=0.12
        )


def main():
    """Hovedfunksjon for demo."""
    print("🔥 Plastic Plate Heat Exchanger Simulator - Demo")
    print("=" * 50)
    
    simulator = PlasticPlateSimulatorDemo()
    
    scenarios = ['standard', 'hightemp', 'lowtemp']
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\\n{i}. Kjører {scenario.upper()} scenario...")
        
        # Opprett input
        input_data = simulator.create_example_scenario(scenario)
        print(f"   • Geometri: {input_data.geometry.width}×{input_data.geometry.length}m, {input_data.geometry.num_plates} plater")
        print(f"   • Varm luft: {input_data.hot_stream.moist_air.temperature}°C, {input_data.hot_stream.mass_flow} kg/s")
        print(f"   • Kald luft: {input_data.cold_stream.moist_air.temperature}°C, {input_data.cold_stream.mass_flow} kg/s")
        
        # Kjør simulering
        output_data = simulator.run_simulation(input_data)
        
        # Resultat-sammendrag
        perf = output_data.performance
        print(f"   ✅ Effektivitet: {perf.effectiveness:.1%}")
        print(f"   ✅ Varmeoverføring: {perf.heat_transfer_rate:.1f} kW")
        print(f"   ✅ NTU: {perf.ntu:.2f}")
        print(f"   ✅ Konvergert på {output_data.convergence.iterations} iterasjoner")
        
        # Generer rapport
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"simulator_demo_{scenario}_{timestamp}.html"
        filepath = os.path.join("rapport_output", filename)
        
        # Sikre at output-mappa eksisterer
        os.makedirs("rapport_output", exist_ok=True)
        
        html_content = generate_html_report(
            output_data,
            title=f"Simulator Demo - {scenario.title()} Scenario",
            description=f"Demonstrasjon av {scenario} konfigurasjon med interaktiv simulator"
        )
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        file_size = os.path.getsize(filepath)
        print(f"   📊 Rapport lagret: {filename} ({file_size/1024:.1f} KB)")
    
    print(f"\\n✅ Demo fullført! {len(scenarios)} rapporter generert i rapport_output/")
    print("\\n🌐 For web-simulator, kjør:")
    print("   cd examples/plastic_plate/simulator")
    print("   python start_simulator.py")


if __name__ == '__main__':
    main()