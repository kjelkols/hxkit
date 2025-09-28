"""
HTML rapport generator for Plastic Plate Heat Exchanger resultater.

Genererer frittstående HTML-rapporter med interaktive JavaScript visualiseringer
basert på PlasticPlateHeatExchangerOutput data.
"""

from datetime import datetime
from typing import Optional
import json
from ..schemas.plastic_plate_schemas import PlasticPlateHeatExchangerOutput


def generate_html_report(
    output_data: PlasticPlateHeatExchangerOutput,
    title: str = "Plastic Plate Heat Exchanger Analysis Report",
    description: Optional[str] = None
) -> str:
    """
    Genererer komplett HTML rapport fra PlasticPlateHeatExchangerOutput.
    
    Args:
        output_data: Validert output data fra varmeveksler analyse
        title: Tittel for rapporten
        description: Valgfri beskrivelse av analysen
        
    Returns:
        Komplett HTML string klar for lagring til fil
    """
    
    # Konverter Pydantic til dict for JSON serialisering
    data_dict = output_data.model_dump()
    
    # Generer timestamp
    report_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html_content = f"""<!DOCTYPE html>
<html lang="no">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        {_get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <header class="report-header">
            <h1>{title}</h1>
            {f'<p class="description">{description}</p>' if description else ''}
            <div class="report-meta">
                <span>Rapport generert: {report_timestamp}</span>
                <span>Analyse tidspunkt: {output_data.analysis_timestamp}</span>
                <span>Solver versjon: {output_data.solver_version}</span>
            </div>
        </header>

        <main>
            {_generate_input_configuration_section(output_data)}
            
            {_generate_summary_section(output_data)}
            
            {_generate_performance_section(output_data)}
            
            {_generate_streams_section(output_data)}
            
            {_generate_phase_changes_section(output_data)}
            
            {_generate_convergence_section(output_data)}
            
            {_generate_temperature_plots_section()}
        </main>
    </div>

    <script>
        // Data for JavaScript plotting
        const reportData = {json.dumps(data_dict, indent=2, default=str)};
        
        {_get_javascript_code()}
    </script>
</body>
</html>"""
    
    return html_content


def _generate_input_configuration_section(output_data: PlasticPlateHeatExchangerOutput) -> str:
    """Genererer input konfigurasjon seksjon."""
    input_data = output_data.input_data
    
    return f"""
    <section class="section">
        <h2>Input Konfigurasjon</h2>
        
        <div class="grid">
            <!-- Geometri -->
            <div class="card">
                <h3>Geometri</h3>
                <div class="metric-grid">
                    <div class="metric">
                        <span class="label">Platebredde</span>
                        <span class="value">{input_data.geometry.width:.3f} m</span>
                    </div>
                    <div class="metric">
                        <span class="label">Platelengde</span>
                        <span class="value">{input_data.geometry.length:.3f} m</span>
                    </div>
                    <div class="metric">
                        <span class="label">Platetykkelse</span>
                        <span class="value">{input_data.geometry.plate_thickness:.4f} m</span>
                    </div>
                    <div class="metric">
                        <span class="label">Kanalhøyde</span>
                        <span class="value">{input_data.geometry.channel_height:.4f} m</span>
                    </div>
                    <div class="metric">
                        <span class="label">Antall plater</span>
                        <span class="value">{input_data.geometry.num_plates}</span>
                    </div>
                    <div class="metric">
                        <span class="label">Platemateriale</span>
                        <span class="value">{input_data.geometry.plate_material.value.replace('_', ' ').title()}</span>
                    </div>
                </div>
            </div>
            
            <!-- Strømningsretninger -->
            <div class="card">
                <h3>Strømningsretninger</h3>
                <div class="metric-grid">
                    <div class="metric">
                        <span class="label">Varm luft retning</span>
                        <span class="value">{input_data.flow_directions.hot_direction.value.upper()}</span>
                    </div>
                    <div class="metric">
                        <span class="label">Kald luft retning</span>
                        <span class="value">{input_data.flow_directions.cold_direction.value.upper()}</span>
                    </div>
                </div>
            </div>
            
            <!-- Varm strøm innløp -->
            <div class="card">
                <h3>Varm Strøm Innløp</h3>
                <div class="metric-grid">
                    <div class="metric">
                        <span class="label">Temperatur</span>
                        <span class="value">{input_data.hot_stream.moist_air.temperature:.1f}°C</span>
                    </div>
                    <div class="metric">
                        <span class="label">Trykk</span>
                        <span class="value">{input_data.hot_stream.moist_air.pressure:.0f} Pa</span>
                    </div>
                    <div class="metric">
                        <span class="label">Relativ fuktighet</span>
                        <span class="value">{input_data.hot_stream.moist_air.relative_humidity:.1f}%</span>
                    </div>
                    <div class="metric">
                        <span class="label">Massestrøm</span>
                        <span class="value">{input_data.hot_stream.mass_flow:.2f} kg/s</span>
                    </div>
                </div>
            </div>
            
            <!-- Kald strøm innløp -->
            <div class="card">
                <h3>Kald Strøm Innløp</h3>
                <div class="metric-grid">
                    <div class="metric">
                        <span class="label">Temperatur</span>
                        <span class="value">{input_data.cold_stream.moist_air.temperature:.1f}°C</span>
                    </div>
                    <div class="metric">
                        <span class="label">Trykk</span>
                        <span class="value">{input_data.cold_stream.moist_air.pressure:.0f} Pa</span>
                    </div>
                    <div class="metric">
                        <span class="label">Relativ fuktighet</span>
                        <span class="value">{input_data.cold_stream.moist_air.relative_humidity:.1f}%</span>
                    </div>
                    <div class="metric">
                        <span class="label">Massestrøm</span>
                        <span class="value">{input_data.cold_stream.mass_flow:.2f} kg/s</span>
                    </div>
                </div>
            </div>
            
            <!-- Numeriske parametere -->
            <div class="card">
                <h3>Numeriske Parametere</h3>
                <div class="metric-grid">
                    <div class="metric">
                        <span class="label">Grid oppløsning</span>
                        <span class="value">{input_data.grid_resolution[0] if input_data.grid_resolution else 'Standard'} × {input_data.grid_resolution[1] if input_data.grid_resolution else 'Standard'}</span>
                    </div>
                    <div class="metric">
                        <span class="label">Konvergenstoleranse</span>
                        <span class="value">{input_data.convergence_tolerance:.0e}</span>
                    </div>
                    <div class="metric">
                        <span class="label">Maks iterasjoner</span>
                        <span class="value">{input_data.max_iterations}</span>
                    </div>
                </div>
            </div>
        </div>
    </section>
    """


def _get_css_styles() -> str:
    """Returnerer CSS styling for rapporten."""
    return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .report-header {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }

        .report-header h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .description {
            font-size: 1.2em;
            color: #666;
            margin-bottom: 20px;
        }

        .report-meta {
            display: flex;
            gap: 30px;
            font-size: 0.9em;
            color: #888;
            flex-wrap: wrap;
        }

        .section {
            background: white;
            margin-bottom: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .section-header {
            background: #34495e;
            color: white;
            padding: 20px 30px;
            font-size: 1.4em;
            font-weight: 600;
        }

        .section-content {
            padding: 30px;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .metric-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #3498db;
        }

        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }

        .metric-label {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .stream-comparison {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-top: 20px;
        }

        .stream-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
        }

        .stream-card.hot {
            border-left: 4px solid #e74c3c;
        }

        .stream-card.cold {
            border-left: 4px solid #3498db;
        }

        .stream-header {
            font-size: 1.2em;
            font-weight: 600;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .temp-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }

        .temp-indicator.hot { background: #e74c3c; }
        .temp-indicator.cold { background: #3498db; }

        .property-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }

        .property {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }

        .property-label {
            color: #666;
        }

        .property-value {
            font-weight: 600;
        }

        .plot-container {
            margin: 20px 0;
            position: relative;
            height: 350px;
            width: 100%;
        }
        
        .plot-container canvas {
            width: 100%;
            height: 100%;
            cursor: crosshair;
        }

        .plot-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-top: 20px;
        }

        .plot-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
        }

        .plot-title {
            font-size: 1.1em;
            font-weight: 600;
            margin-bottom: 15px;
            text-align: center;
        }

        .status-indicator {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
        }

        .status-success {
            background: #d4edda;
            color: #155724;
        }

        .status-warning {
            background: #fff3cd;
            color: #856404;
        }

        .convergence-details {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            margin-top: 15px;
        }

        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .stream-comparison {
                grid-template-columns: 1fr;
            }
            
            .plot-grid {
                grid-template-columns: 1fr;
            }
            
            .report-meta {
                flex-direction: column;
                gap: 10px;
            }
        }
    """


def _generate_summary_section(output_data: PlasticPlateHeatExchangerOutput) -> str:
    """Genererer sammendrag seksjon."""
    perf = output_data.performance
    
    return f"""
    <section class="section">
        <div class="section-header">
            Sammendrag
        </div>
        <div class="section-content">
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{perf.effectiveness:.1%}</div>
                    <div class="metric-label">Effektivitet</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{perf.heat_transfer_rate:.1f} kW</div>
                    <div class="metric-label">Varmeoverføring</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{perf.ntu:.2f}</div>
                    <div class="metric-label">NTU</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{output_data.hot_outlet.moist_air.temperature:.1f}°C</div>
                    <div class="metric-label">Varm utløp</div>
                </div>
            </div>
        </div>
    </section>
    """


def _generate_performance_section(output_data: PlasticPlateHeatExchangerOutput) -> str:
    """Genererer ytelse seksjon."""
    perf = output_data.performance
    
    return f"""
    <section class="section">
        <div class="section-header">
            Ytelsesparametre
        </div>
        <div class="section-content">
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{perf.heat_transfer_rate:.2f} kW</div>
                    <div class="metric-label">Varmeoverføringsrate</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{perf.effectiveness:.3f}</div>
                    <div class="metric-label">Effektivitet</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{perf.ntu:.2f}</div>
                    <div class="metric-label">NTU (Number of Transfer Units)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{perf.pressure_drop_hot:.1f} Pa</div>
                    <div class="metric-label">Trykkfall varm side</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{perf.pressure_drop_cold:.1f} Pa</div>
                    <div class="metric-label">Trykkfall kald side</div>
                </div>
                {f'''<div class="metric-card">
                    <div class="metric-value">{perf.overall_heat_transfer_coefficient:.1f} W/m²·K</div>
                    <div class="metric-label">Samlet varmeoverføringskoeffisient</div>
                </div>''' if perf.overall_heat_transfer_coefficient else ''}
            </div>
        </div>
    </section>
    """


def _generate_streams_section(output_data: PlasticPlateHeatExchangerOutput) -> str:
    """Genererer luftstrømmer seksjon."""
    hot = output_data.hot_outlet
    cold = output_data.cold_outlet
    
    return f"""
    <section class="section">
        <div class="section-header">
            Luftstrømmer ved utløp
        </div>
        <div class="section-content">
            <div class="stream-comparison">
                <div class="stream-card hot">
                    <div class="stream-header">
                        <span class="temp-indicator hot"></span>
                        Varm luftstrøm
                    </div>
                    <div class="property-grid">
                        <div class="property">
                            <span class="property-label">Temperatur:</span>
                            <span class="property-value">{hot.moist_air.temperature:.1f}°C</span>
                        </div>
                        <div class="property">
                            <span class="property-label">Relativ fuktighet:</span>
                            <span class="property-value">{hot.moist_air.relative_humidity:.1f}%</span>
                        </div>
                        <div class="property">
                            <span class="property-label">Massestrøm:</span>
                            <span class="property-value">{hot.mass_flow:.2f} kg/s</span>
                        </div>
                        <div class="property">
                            <span class="property-label">Volumstrøm:</span>
                            <span class="property-value">{hot.volume_flow:.2f} m³/s</span>
                        </div>
                        <div class="property">
                            <span class="property-label">Entalpistrøm:</span>
                            <span class="property-value">{hot.enthalpy_flow:.1f} kW</span>
                        </div>
                    </div>
                </div>
                
                <div class="stream-card cold">
                    <div class="stream-header">
                        <span class="temp-indicator cold"></span>
                        Kald luftstrøm
                    </div>
                    <div class="property-grid">
                        <div class="property">
                            <span class="property-label">Temperatur:</span>
                            <span class="property-value">{cold.moist_air.temperature:.1f}°C</span>
                        </div>
                        <div class="property">
                            <span class="property-label">Relativ fuktighet:</span>
                            <span class="property-value">{cold.moist_air.relative_humidity:.1f}%</span>
                        </div>
                        <div class="property">
                            <span class="property-label">Massestrøm:</span>
                            <span class="property-value">{cold.mass_flow:.2f} kg/s</span>
                        </div>
                        <div class="property">
                            <span class="property-label">Volumstrøm:</span>
                            <span class="property-value">{cold.volume_flow:.2f} m³/s</span>
                        </div>
                        <div class="property">
                            <span class="property-label">Entalpistrøm:</span>
                            <span class="property-value">{cold.enthalpy_flow:.1f} kW</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
    """


def _generate_phase_changes_section(output_data: PlasticPlateHeatExchangerOutput) -> str:
    """Genererer faseendringer seksjon."""
    pc = output_data.phase_changes
    
    condensation_status = "Ingen kondensasjon" if not pc.condensation_occurred else f"Kondensasjonsrate: {pc.condensation_rate:.4f} kg/s"
    frost_status = "Ingen rimdannelse" if not pc.frost_occurred else f"Rimtykkelse: {pc.frost_thickness:.4f} m"
    
    return f"""
    <section class="section">
        <div class="section-header">
            Faseendringer
        </div>
        <div class="section-content">
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="status-indicator {'status-success' if not pc.condensation_occurred else 'status-warning'}">
                        {'✓' if not pc.condensation_occurred else '⚠'} {condensation_status}
                    </div>
                </div>
                <div class="metric-card">
                    <div class="status-indicator {'status-success' if not pc.frost_occurred else 'status-warning'}">
                        {'✓' if not pc.frost_occurred else '⚠'} {frost_status}
                    </div>
                </div>
            </div>
        </div>
    </section>
    """


def _generate_convergence_section(output_data: PlasticPlateHeatExchangerOutput) -> str:
    """Genererer konvergens seksjon."""
    conv = output_data.convergence
    
    return f"""
    <section class="section">
        <div class="section-header">
            Numerisk konvergens
        </div>
        <div class="section-content">
            <div class="status-indicator {'status-success' if conv.converged else 'status-warning'}">
                {'✓ Konvergert' if conv.converged else '⚠ Ikke konvergert'}
            </div>
            
            <div class="convergence-details">
                <div class="property-grid">
                    <div class="property">
                        <span class="property-label">Iterasjoner:</span>
                        <span class="property-value">{conv.iterations}</span>
                    </div>
                    <div class="property">
                        <span class="property-label">Endelig residual:</span>
                        <span class="property-value">{conv.final_residual:.2e}</span>
                    </div>
                    <div class="property">
                        <span class="property-label">Toleranse:</span>
                        <span class="property-value">{conv.convergence_tolerance:.2e}</span>
                    </div>
                    <div class="property">
                        <span class="property-label">Beregningstid:</span>
                        <span class="property-value">{conv.computation_time:.2f} s</span>
                    </div>
                </div>
            </div>
        </div>
    </section>
    """


def _generate_temperature_plots_section() -> str:
    """Genererer temperaturplott seksjon."""
    return """
    <section class="section">
        <div class="section-header">
            Temperaturfordeling
        </div>
        <div class="section-content">
            <div class="plot-grid">
                <div class="plot-card">
                    <div class="plot-title">Plate temperaturer</div>
                    <div class="plot-container">
                        <canvas id="plateTemperatureChart"></canvas>
                    </div>
                </div>
                
                <div class="plot-card">
                    <div class="plot-title">Varm luft temperaturer</div>
                    <div class="plot-container">
                        <canvas id="hotAirTemperatureChart"></canvas>
                    </div>
                </div>
            </div>
            
            <div class="plot-grid">
                <div class="plot-card">
                    <div class="plot-title">Kald luft temperaturer</div>
                    <div class="plot-container">
                        <canvas id="coldAirTemperatureChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
    </section>
    """


def _get_javascript_code() -> str:
    """Returnerer JavaScript kode for interaktive plott."""
    return """
        // Heatmap farger (viridis-inspirert)
        function getTemperatureColor(temp, minTemp, maxTemp) {
            const normalized = (temp - minTemp) / (maxTemp - minTemp);
            const colors = [
                [68, 1, 84],    // Mørk lilla
                [59, 82, 139],  // Blå
                [33, 145, 140], // Cyan
                [94, 201, 98],  // Grønn
                [253, 231, 37]  // Gul
            ];
            
            const scaledIndex = normalized * (colors.length - 1);
            const lowerIndex = Math.floor(scaledIndex);
            const upperIndex = Math.ceil(scaledIndex);
            const fraction = scaledIndex - lowerIndex;
            
            if (lowerIndex === upperIndex) {
                const [r, g, b] = colors[lowerIndex];
                return `rgb(${r}, ${g}, ${b})`;
            }
            
            const [r1, g1, b1] = colors[lowerIndex];
            const [r2, g2, b2] = colors[upperIndex];
            
            const r = Math.round(r1 + (r2 - r1) * fraction);
            const g = Math.round(g1 + (g2 - g1) * fraction);
            const b = Math.round(b1 + (b2 - b1) * fraction);
            
            return `rgb(${r}, ${g}, ${b})`;
        }

        // Konverter 2D temperaturdata til heatmap dataset
        function createHeatmapData(temperatureArray, label) {
            if (!temperatureArray || !temperatureArray.length) {
                return { datasets: [] };
            }
            
            const allTemps = temperatureArray.flat();
            const minTemp = Math.min(...allTemps);
            const maxTemp = Math.max(...allTemps);
            
            const data = [];
            for (let y = 0; y < temperatureArray.length; y++) {
                for (let x = 0; x < temperatureArray[y].length; x++) {
                    const temp = temperatureArray[y][x];
                    data.push({
                        x: x,
                        y: y,
                        v: temp,
                        backgroundColor: getTemperatureColor(temp, minTemp, maxTemp)
                    });
                }
            }
            
            return {
                datasets: [{
                    label: label,
                    data: data,
                    backgroundColor: function(context) {
                        return context.parsed.raw.backgroundColor;
                    },
                    borderWidth: 1,
                    borderColor: 'rgba(255, 255, 255, 0.3)'
                }]
            };
        }

        // Opprett heatmap med Canvas 2D API
        function createHeatmapChart(canvasId, temperatureData, title) {
            const canvas = document.getElementById(canvasId);
            if (!canvas || !temperatureData || !temperatureData.length) {
                console.warn(`Ingen data tilgjengelig for ${canvasId}`);
                return;
            }
            
            const ctx = canvas.getContext('2d');
            const containerWidth = canvas.parentElement.clientWidth;
            const containerHeight = 350;
            
            canvas.width = containerWidth;
            canvas.height = containerHeight;
            canvas.style.width = containerWidth + 'px';
            canvas.style.height = containerHeight + 'px';
            
            const width = temperatureData[0].length;
            const height = temperatureData.length;
            
            // Beregn temperaturområde
            const allTemps = temperatureData.flat();
            const minTemp = Math.min(...allTemps);
            const maxTemp = Math.max(...allTemps);
            
            // Beregn celle størrelser
            const cellWidth = (containerWidth - 100) / width;  // Legg til plass for akser
            const cellHeight = (containerHeight - 100) / height;
            
            const offsetX = 60;
            const offsetY = 20;
            
            // Tegn tittel
            ctx.fillStyle = '#333';
            ctx.font = 'bold 16px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(title, containerWidth / 2, 20);
            
            // Tegn heatmap celler
            for (let y = 0; y < height; y++) {
                for (let x = 0; x < width; x++) {
                    const temp = temperatureData[y][x];
                    const color = getTemperatureColor(temp, minTemp, maxTemp);
                    
                    ctx.fillStyle = color;
                    ctx.fillRect(
                        offsetX + x * cellWidth,
                        offsetY + 30 + y * cellHeight,
                        cellWidth,
                        cellHeight
                    );
                    
                    // Tegn temperaturverdi hvis cellene er store nok
                    if (cellWidth > 30 && cellHeight > 20) {
                        ctx.fillStyle = temp > (minTemp + maxTemp) / 2 ? 'white' : 'black';
                        ctx.font = '10px Arial';
                        ctx.textAlign = 'center';
                        ctx.fillText(
                            temp.toFixed(1),
                            offsetX + x * cellWidth + cellWidth / 2,
                            offsetY + 30 + y * cellHeight + cellHeight / 2 + 3
                        );
                    }
                }
            }
            
            // Tegn fargeskala
            drawColorScale(ctx, containerWidth - 50, offsetY + 30, 20, height * cellHeight, minTemp, maxTemp);
            
            // Tegn akser
            ctx.fillStyle = '#666';
            ctx.font = '12px Arial';
            
            // X-akse
            for (let x = 0; x <= width; x += Math.max(1, Math.floor(width / 10))) {
                ctx.textAlign = 'center';
                ctx.fillText(
                    x.toString(),
                    offsetX + x * cellWidth,
                    offsetY + 30 + height * cellHeight + 20
                );
            }
            
            // Y-akse
            for (let y = 0; y <= height; y += Math.max(1, Math.floor(height / 10))) {
                ctx.textAlign = 'right';
                ctx.fillText(
                    y.toString(),
                    offsetX - 10,
                    offsetY + 30 + y * cellHeight + 4
                );
            }
            
            // Akselabels
            ctx.fillStyle = '#333';
            ctx.font = 'bold 12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('Bredde posisjon', containerWidth / 2, containerHeight - 5);
            
            ctx.save();
            ctx.translate(15, containerHeight / 2);
            ctx.rotate(-Math.PI / 2);
            ctx.fillText('Lengde posisjon', 0, 0);
            ctx.restore();
        }
        
        // Tegn fargeskala
        function drawColorScale(ctx, x, y, width, height, minTemp, maxTemp) {
            const steps = 100;
            const stepHeight = height / steps;
            
            for (let i = 0; i < steps; i++) {
                const temp = minTemp + (maxTemp - minTemp) * (1 - i / steps);
                const color = getTemperatureColor(temp, minTemp, maxTemp);
                
                ctx.fillStyle = color;
                ctx.fillRect(x, y + i * stepHeight, width, stepHeight);
            }
            
            // Fargeskala ramme
            ctx.strokeStyle = '#ccc';
            ctx.lineWidth = 1;
            ctx.strokeRect(x, y, width, height);
            
            // Fargeskala labels
            ctx.fillStyle = '#333';
            ctx.font = '10px Arial';
            ctx.textAlign = 'left';
            
            const labelSteps = 5;
            for (let i = 0; i <= labelSteps; i++) {
                const temp = minTemp + (maxTemp - minTemp) * (1 - i / labelSteps);
                const labelY = y + (i / labelSteps) * height;
                
                ctx.fillText(
                    temp.toFixed(1) + '°C',
                    x + width + 5,
                    labelY + 3
                );
            }
        }



        // Legg til tooltip interaktivitet for heatmaps
        function addHeatmapTooltip(canvasId, temperatureData) {
            const canvas = document.getElementById(canvasId);
            if (!canvas || !temperatureData || !temperatureData.length) return;
            
            const tooltip = document.createElement('div');
            tooltip.style.cssText = `
                position: absolute;
                background: rgba(0,0,0,0.8);
                color: white;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
                pointer-events: none;
                z-index: 1000;
                display: none;
            `;
            document.body.appendChild(tooltip);
            
            const width = temperatureData[0].length;
            const height = temperatureData.length;
            const containerWidth = canvas.clientWidth;
            const containerHeight = 350;
            
            const cellWidth = (containerWidth - 100) / width;
            const cellHeight = (containerHeight - 100) / height;
            const offsetX = 60;
            const offsetY = 50;
            
            canvas.addEventListener('mousemove', function(event) {
                const rect = canvas.getBoundingClientRect();
                const mouseX = event.clientX - rect.left;
                const mouseY = event.clientY - rect.top;
                
                const gridX = Math.floor((mouseX - offsetX) / cellWidth);
                const gridY = Math.floor((mouseY - offsetY) / cellHeight);
                
                if (gridX >= 0 && gridX < width && gridY >= 0 && gridY < height) {
                    const temp = temperatureData[gridY][gridX];
                    tooltip.innerHTML = `Posisjon (${gridX}, ${gridY})<br>Temperatur: ${temp.toFixed(1)}°C`;
                    tooltip.style.left = event.clientX + 10 + 'px';
                    tooltip.style.top = event.clientY - 30 + 'px';
                    tooltip.style.display = 'block';
                } else {
                    tooltip.style.display = 'none';
                }
            });
            
            canvas.addEventListener('mouseleave', function() {
                tooltip.style.display = 'none';
            });
        }

        // Initialiser alle plott når siden er lastet
        document.addEventListener('DOMContentLoaded', function() {
            if (reportData.grid_results) {
                const gridResults = reportData.grid_results;
                
                createHeatmapChart(
                    'plateTemperatureChart',
                    gridResults.plate_temperatures,
                    'Plate temperaturer (°C)'
                );
                addHeatmapTooltip('plateTemperatureChart', gridResults.plate_temperatures);
                
                createHeatmapChart(
                    'hotAirTemperatureChart',
                    gridResults.hot_air_temperatures,
                    'Varm luft temperaturer (°C)'
                );
                addHeatmapTooltip('hotAirTemperatureChart', gridResults.hot_air_temperatures);
                
                createHeatmapChart(
                    'coldAirTemperatureChart',
                    gridResults.cold_air_temperatures,
                    'Kald luft temperaturer (°C)'
                );
                addHeatmapTooltip('coldAirTemperatureChart', gridResults.cold_air_temperatures);
                

            } else {
                // Vis meldinger hvis grid data ikke er tilgjengelig
                const charts = ['plateTemperatureChart', 'hotAirTemperatureChart', 'coldAirTemperatureChart'];
                charts.forEach(chartId => {
                    const canvas = document.getElementById(chartId);
                    if (canvas) {
                        const ctx = canvas.getContext('2d');
                        ctx.font = '16px Arial';
                        ctx.fillStyle = '#666';
                        ctx.textAlign = 'center';
                        canvas.width = canvas.parentElement.clientWidth;
                        canvas.height = 300;
                        ctx.fillText('Grid resultater ikke tilgjengelig i denne analysen', canvas.width/2, canvas.height/2);
                    }
                });
            }
        });
    """


def save_html_report(
    output_data: PlasticPlateHeatExchangerOutput,
    filepath: str,
    title: str = "Plastic Plate Heat Exchanger Analysis Report",
    description: Optional[str] = None
) -> None:
    """
    Genererer og lagrer HTML rapport til fil.
    
    Args:
        output_data: Validert output data fra varmeveksler analyse
        filepath: Sti til HTML fil som skal opprettes
        title: Tittel for rapporten
        description: Valgfri beskrivelse av analysen
    """
    html_content = generate_html_report(output_data, title, description)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML rapport lagret til: {filepath}")


if __name__ == "__main__":
    # Eksempel på bruk
    from ..schemas.plastic_plate_schemas import PlasticPlateHeatExchangerOutput
    
    print("HTML rapport generator for Plastic Plate Heat Exchanger")
    print("Bruk save_html_report() funksjonen for å generere rapporter.")