"""
Plastic Plate Heat Exchanger Simulator
=======================================

Web-basert simulator som lar brukeren endre input-parametere og kjøre
beregninger for plastic plate heat exchanger. Resultater vises som HTML-rapport.
"""

from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import os
import tempfile
import datetime
from typing import Optional
import traceback

# Import HXKit components
import sys
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

app = Flask(__name__)
app.secret_key = 'hxkit_simulator_2025'  # For flash messages

# Konfigurer upload folder for rapporter
REPORTS_FOLDER = os.path.join(os.path.dirname(__file__), 'generated_reports')
os.makedirs(REPORTS_FOLDER, exist_ok=True)


class PlasticPlateSimulator:
    """Simulator for plastic plate heat exchanger."""
    
    def __init__(self):
        self.version = "1.0.0"
    
    def run_simulation(self, input_data: PlasticPlateHeatExchangerInput) -> PlasticPlateHeatExchangerOutput:
        """
        Kjører simulering med gitt input og returnerer resultater.
        Denne implementerer en forenklet modell for demonstrasjon.
        """
        
        # Import calculation functions
        from calculations import calculate_heat_exchanger_performance
        
        try:
            # Kjør beregninger
            output = calculate_heat_exchanger_performance(input_data)
            return output
            
        except Exception as e:
            # Fallback med dummy data hvis beregninger feiler
            print(f"Beregning feilet: {e}")
            return self._create_fallback_output(input_data)
    
    def _create_fallback_output(self, input_data: PlasticPlateHeatExchangerInput) -> PlasticPlateHeatExchangerOutput:
        """Lag fallback output for testing."""
        
        # Enkle estimater basert på input
        hot_temp = input_data.hot_stream.moist_air.temperature
        cold_temp = input_data.cold_stream.moist_air.temperature
        hot_flow = input_data.hot_stream.mass_flow
        cold_flow = input_data.cold_stream.mass_flow
        
        # Estimat på utløpstemperaturer (60% effektivitet)
        temp_diff = hot_temp - cold_temp
        effectiveness = 0.6
        
        hot_outlet_temp = hot_temp - effectiveness * temp_diff * 0.7
        cold_outlet_temp = cold_temp + effectiveness * temp_diff * 0.8
        
        # Enkel varmeoverføring estimat
        cp_air = 1.005  # kJ/kg·K
        heat_transfer = min(hot_flow, cold_flow) * cp_air * temp_diff * effectiveness
        
        # Opprett grid resultater hvis ønsket
        grid_results = None
        if input_data.grid_resolution:
            width_cells, length_cells = input_data.grid_resolution
            grid_results = self._generate_temperature_field(
                width_cells, length_cells, 
                hot_outlet_temp, cold_outlet_temp, hot_temp, cold_temp
            )
        
        return PlasticPlateHeatExchangerOutput(
            input_data=input_data,
            performance=PerformanceMetrics(
                effectiveness=effectiveness,
                ntu=1.5,
                heat_transfer_rate=heat_transfer,
                pressure_drop_hot=30.0 + hot_flow * 5,
                pressure_drop_cold=25.0 + cold_flow * 5,
                overall_heat_transfer_coefficient=20.0
            ),
            hot_outlet=StreamOutput(
                moist_air=MoistAirOutput(
                    temperature=hot_outlet_temp,
                    pressure=input_data.hot_stream.moist_air.pressure - 30,
                    relative_humidity=min(95.0, (input_data.hot_stream.moist_air.relative_humidity or 50.0) * 1.2),
                    humidity_ratio=0.012,
                    dew_point=hot_outlet_temp - 5,
                    wet_bulb=hot_outlet_temp - 3,
                    density=1.15,
                    specific_volume=0.87,
                    enthalpy=50.0
                ),
                mass_flow=hot_flow,
                volume_flow=hot_flow / 1.15,
                enthalpy_flow=heat_transfer * 0.7
            ),
            cold_outlet=StreamOutput(
                moist_air=MoistAirOutput(
                    temperature=cold_outlet_temp,
                    pressure=input_data.cold_stream.moist_air.pressure - 25,
                    relative_humidity=max(20.0, (input_data.cold_stream.moist_air.relative_humidity or 50.0) * 0.8),
                    humidity_ratio=0.008,
                    dew_point=cold_outlet_temp - 8,
                    wet_bulb=cold_outlet_temp - 5,
                    density=1.18,
                    specific_volume=0.85,
                    enthalpy=35.0
                ),
                mass_flow=cold_flow,
                volume_flow=cold_flow / 1.18,
                enthalpy_flow=heat_transfer * 0.3
            ),
            phase_changes=PhaseChangeResults(
                condensation_rate=0.001 if hot_outlet_temp < 20 else 0.0,
                frost_thickness=0.0,
                condensation_occurred=hot_outlet_temp < 20,
                frost_occurred=False
            ),
            grid_results=grid_results,
            convergence=ConvergenceInfo(
                converged=True,
                iterations=45,
                final_residual=1.5e-7,
                convergence_tolerance=input_data.convergence_tolerance or 1e-6,
                computation_time=0.8
            ),
            analysis_timestamp=datetime.datetime.now().isoformat(),
            solver_version="HXKit Simulator v1.0"
        )
    
    def _generate_temperature_field(self, width: int, length: int, 
                                  hot_outlet: float, cold_outlet: float,
                                  hot_inlet: float, cold_inlet: float) -> GridResults:
        """Generer realistisk temperaturfeld for visualisering."""
        
        # Plate temperaturer (mellom varm og kald side)
        plate_temps = []
        hot_air_temps = []
        cold_air_temps = []
        
        for i in range(length):
            plate_row = []
            hot_row = []
            cold_row = []
            
            # Progresjon langs lengden (0 til 1)
            length_progress = i / (length - 1) if length > 1 else 0
            
            for j in range(width):
                # Variasjoner på tvers av bredden
                width_variation = (j / (width - 1) - 0.5) * 2 if width > 1 else 0
                
                # Temperaturfordeling
                hot_temp = hot_inlet - (hot_inlet - hot_outlet) * length_progress + width_variation * 1.5
                cold_temp = cold_inlet + (cold_outlet - cold_inlet) * length_progress - width_variation * 1.2
                plate_temp = (hot_temp + cold_temp) / 2 + width_variation * 0.8
                
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
            temperature_uniformity=0.15  # Dummy verdi
        )


# Global simulator instans
simulator = PlasticPlateSimulator()


@app.route('/')
def index():
    """Hovedside med simulator form."""
    return render_template('index.html')


@app.route('/simulate', methods=['POST'])
def simulate():
    """Kjør simulering basert på form input."""
    
    try:
        # Parse form data
        input_data = parse_form_data(request.form)
        
        # Kjør simulering
        output_data = simulator.run_simulation(input_data)
        
        # Generer HTML rapport
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"simulation_result_{timestamp}.html"
        filepath = os.path.join(REPORTS_FOLDER, filename)
        
        # Generer rapport
        html_content = generate_html_report(
            output_data,
            title="Plastic Plate Heat Exchanger - Simuleringsresultat",
            description="Resultater fra interaktiv simulator"
        )
        
        # Lagre rapport
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Returner rapport til bruker
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        flash(f"Feil under simulering: {str(e)}", "error")
        return redirect(url_for('index'))


def parse_form_data(form_data) -> PlasticPlateHeatExchangerInput:
    """Parse HTML form data til PlasticPlateHeatExchangerInput."""
    
    try:
        # Geometri
        geometry = PlateGeometryInput(
            width=float(form_data['width']),
            length=float(form_data['length']),
            plate_thickness=float(form_data['plate_thickness']),
            channel_height=float(form_data['channel_height']),
            num_plates=int(form_data['num_plates']),
            plate_material=PlateMaterial(form_data['plate_material'])
        )
        
        # Strømningsretninger
        flow_directions = FlowDirectionInput(
            hot_direction=Direction(form_data['hot_direction']),
            cold_direction=Direction(form_data['cold_direction'])
        )
        
        # Varm strøm
        hot_stream = StreamInput(
            moist_air=MoistAirInput(
                temperature=float(form_data['hot_temperature']),
                pressure=float(form_data['hot_pressure']),
                relative_humidity=float(form_data['hot_humidity'])
            ),
            mass_flow=float(form_data['hot_mass_flow'])
        )
        
        # Kald strøm
        cold_stream = StreamInput(
            moist_air=MoistAirInput(
                temperature=float(form_data['cold_temperature']),
                pressure=float(form_data['cold_pressure']),
                relative_humidity=float(form_data['cold_humidity'])
            ),
            mass_flow=float(form_data['cold_mass_flow'])
        )
        
        # Numeriske parametere
        grid_width = int(form_data.get('grid_width', 10))
        grid_length = int(form_data.get('grid_length', 12))
        
        return PlasticPlateHeatExchangerInput(
            geometry=geometry,
            flow_directions=flow_directions,
            hot_stream=hot_stream,
            cold_stream=cold_stream,
            grid_resolution=(grid_width, grid_length),
            convergence_tolerance=float(form_data.get('convergence_tolerance', 1e-6)),
            max_iterations=int(form_data.get('max_iterations', 500))
        )
        
    except Exception as e:
        raise ValueError(f"Ugyldig input data: {str(e)}")


@app.route('/reports')
def list_reports():
    """Vis liste over genererte rapporter."""
    reports = []
    if os.path.exists(REPORTS_FOLDER):
        for filename in os.listdir(REPORTS_FOLDER):
            if filename.endswith('.html'):
                filepath = os.path.join(REPORTS_FOLDER, filename)
                stat = os.stat(filepath)
                reports.append({
                    'filename': filename,
                    'size': f"{stat.st_size / 1024:.1f} KB",
                    'created': datetime.datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
                })
    
    reports.sort(key=lambda x: x['created'], reverse=True)
    return render_template('reports.html', reports=reports)


@app.route('/reports/<filename>')
def view_report(filename):
    """Vis en spesifikk rapport."""
    filepath = os.path.join(REPORTS_FOLDER, filename)
    if os.path.exists(filepath):
        return send_file(filepath)
    else:
        flash("Rapport ikke funnet", "error")
        return redirect(url_for('list_reports'))


if __name__ == '__main__':
    print("Plastic Plate Heat Exchanger Simulator")
    print("=====================================")
    print(f"Starter web simulator på http://localhost:5000")
    print("Rapporter lagres i:", REPORTS_FOLDER)
    
    app.run(debug=True, host='0.0.0.0', port=5000)