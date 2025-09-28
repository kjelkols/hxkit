"""
HXKit Fuktig Luft Kalkulator - Streamlit Web App
===============================================
Moderne web-basert GUI for beregning av fuktig luft egenskaper
Bruker HXKit Web-API for beregninger
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional, Dict, Any
import numpy as np


# Konfigurer siden
st.set_page_config(
    page_title="HXKit - Fuktig Luft Kalkulator",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API konfigurasjon
API_BASE_URL = "http://localhost:8000"


def check_api_connection() -> bool:
    """Sjekk om APIet er tilgjengelig"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def calculate_air_properties(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Beregn luftegenskaper via API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/air-properties",
            json=data,
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API feil: {response.json().get('detail', 'Ukjent feil')}")
            return None
    except requests.RequestException:
        st.error("Kan ikke koble til API. Sjekk at serveren kjører.")
        return None
    except Exception as e:
        st.error(f"Uventet feil: {str(e)}")
        return None


def create_psychrometric_chart(data_points: list) -> go.Figure:
    """Opprett psykrometrisk diagram"""
    if not data_points:
        return go.Figure()
    
    # Ekstraher data
    temps = [p['temperature'] for p in data_points]
    rh_values = [p['relative_humidity'] for p in data_points]
    hr_values = [p['humidity_ratio'] * 1000 for p in data_points]  # g/kg
    
    # Opprett figur
    fig = go.Figure()
    
    # Legg til datapunkter
    fig.add_trace(go.Scatter(
        x=temps,
        y=hr_values,
        mode='markers+text',
        marker=dict(size=12, color='red'),
        text=[f'RH: {rh:.1f}%' for rh in rh_values],
        textposition='top center',
        name='Beregnet punkt'
    ))
    
    # Konstant RH linjer (10%, 20%, ..., 100%)
    temp_range = np.linspace(0, 50, 100)
    colors = px.colors.qualitative.Set3
    
    for i, rh in enumerate([10, 20, 30, 40, 50, 60, 70, 80, 90, 100]):
        hr_line = []
        for temp in temp_range:
            try:
                data = {
                    "temperature": temp,
                    "pressure": 101325,
                    "relative_humidity": rh,
                    "humidity_ratio": None,
                    "dew_point": None,
                    "wet_bulb": None
                }
                result = calculate_air_properties(data)
                if result:
                    hr_line.append(result['humidity_ratio'] * 1000)
                else:
                    hr_line.append(None)
            except:
                hr_line.append(None)
        
        fig.add_trace(go.Scatter(
            x=temp_range,
            y=hr_line,
            mode='lines',
            line=dict(width=1, color=colors[i % len(colors)], dash='dot'),
            name=f'{rh}% RH',
            showlegend=True if rh in [20, 40, 60, 80, 100] else False
        ))
    
    # Layout
    fig.update_layout(
        title="Psykrometrisk Diagram",
        xaxis_title="Temperatur (°C)",
        yaxis_title="Fuktighetsforhold (g/kg)",
        height=600,
        showlegend=True,
        hovermode='closest'
    )
    
    return fig


def main():
    """Hovedapplikasjon"""
    
    # Header
    st.title("🌡️ HXKit - Fuktig Luft Kalkulator")
    st.markdown("Beregn egenskaper for fuktig luft med forskjellige input parametere")
    
    # Sjekk API tilkobling
    if not check_api_connection():
        st.error(
            "⚠️ HXKit API er ikke tilgjengelig!\n\n"
            "Start serveren med: `python examples/fastapi_server.py`"
        )
        st.stop()
    else:
        st.success("✅ API tilkobling OK")
    
    # Sidebar for input
    st.sidebar.header("Input Parametere")
    
    # Grunnleggende parametere
    temperature = st.sidebar.number_input(
        "Temperatur (°C)", 
        min_value=-50.0, 
        max_value=100.0, 
        value=25.0, 
        step=0.1
    )
    
    pressure = st.sidebar.number_input(
        "Trykk (Pa)", 
        min_value=50000, 
        max_value=200000, 
        value=101325, 
        step=100
    )
    
    # Fuktighet metode
    humidity_method = st.sidebar.selectbox(
        "Fuktighet Parameter",
        ["Relativ fuktighet (%)", "Fuktighetsforhold (kg/kg)", "Doggpunkt (°C)", "Våtkuletemperatur (°C)"]
    )
    
    # Fuktighet input basert på metode
    humidity_value = None
    if humidity_method == "Relativ fuktighet (%)":
        humidity_value = st.sidebar.slider(
            "Relativ fuktighet (%)", 
            min_value=0.0, 
            max_value=100.0, 
            value=60.0, 
            step=0.1
        )
        humidity_key = "relative_humidity"
    elif humidity_method == "Fuktighetsforhold (kg/kg)":
        humidity_value = st.sidebar.number_input(
            "Fuktighetsforhold (kg/kg)", 
            min_value=0.0, 
            max_value=0.1, 
            value=0.010, 
            step=0.001,
            format="%.6f"
        )
        humidity_key = "humidity_ratio"
    elif humidity_method == "Doggpunkt (°C)":
        humidity_value = st.sidebar.number_input(
            "Doggpunkt (°C)", 
            min_value=-50.0, 
            max_value=50.0, 
            value=15.0, 
            step=0.1
        )
        humidity_key = "dew_point"
    else:  # Våtkuletemperatur
        humidity_value = st.sidebar.number_input(
            "Våtkuletemperatur (°C)", 
            min_value=-50.0, 
            max_value=50.0, 
            value=20.0, 
            step=0.1
        )
        humidity_key = "wet_bulb"
    
    # Beregn knapp
    if st.sidebar.button("🧮 Beregn Egenskaper", type="primary"):
        
        # Bygg API request
        data = {
            "temperature": temperature,
            "pressure": pressure,
            "relative_humidity": None,
            "humidity_ratio": None,
            "dew_point": None,
            "wet_bulb": None
        }
        data[humidity_key] = humidity_value
        
        # Beregn egenskaper
        result = calculate_air_properties(data)
        
        if result:
            # Lagre i session state for plotting
            if 'calculations' not in st.session_state:
                st.session_state.calculations = []
            st.session_state.calculations.append(result)
            
            # Vis resultater
            st.header("📊 Beregnede Egenskaper")
            
            # Hovedresultater i kolonner
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Temperatur", f"{result['temperature']:.1f} °C")
                st.metric("Relativ fuktighet", f"{result['relative_humidity']:.1f} %")
                st.metric("Fuktighetsforhold", f"{result['humidity_ratio']:.6f} kg/kg")
            
            with col2:
                st.metric("Doggpunkt", f"{result['dew_point']:.1f} °C")
                st.metric("Våtkuletemperatur", f"{result['wet_bulb']:.1f} °C")
                st.metric("Entalpi", f"{result['enthalpy']:.0f} J/kg")
            
            with col3:
                st.metric("Tetthet", f"{result['density']:.3f} kg/m³")
                st.metric("Spesifikt volum", f"{1/result['density']:.3f} m³/kg")
                st.metric("Trykk", f"{result['pressure']:.0f} Pa")
            
            # Detaljert tabell
            st.subheader("📋 Detaljerte Resultater")
            result_df = pd.DataFrame([{
                "Parameter": "Temperatur",
                "Verdi": f"{result['temperature']:.2f}",
                "Enhet": "°C"
            }, {
                "Parameter": "Trykk",
                "Verdi": f"{result['pressure']:.0f}",
                "Enhet": "Pa"
            }, {
                "Parameter": "Relativ fuktighet",
                "Verdi": f"{result['relative_humidity']:.2f}",
                "Enhet": "%"
            }, {
                "Parameter": "Fuktighetsforhold",
                "Verdi": f"{result['humidity_ratio']:.6f}",
                "Enhet": "kg/kg"
            }, {
                "Parameter": "Doggpunkt",
                "Verdi": f"{result['dew_point']:.2f}",
                "Enhet": "°C"
            }, {
                "Parameter": "Våtkuletemperatur",
                "Verdi": f"{result['wet_bulb']:.2f}",
                "Enhet": "°C"
            }, {
                "Parameter": "Entalpi",
                "Verdi": f"{result['enthalpy']:.0f}",
                "Enhet": "J/kg"
            }, {
                "Parameter": "Tetthet",
                "Verdi": f"{result['density']:.4f}",
                "Enhet": "kg/m³"
            }, {
                "Parameter": "Spesifikt volum",
                "Verdi": f"{1/result['density']:.4f}",
                "Enhet": "m³/kg"
            }])
            
            st.dataframe(result_df, use_container_width=True, hide_index=True)
    
    # Historikk og plotting
    if 'calculations' in st.session_state and st.session_state.calculations:
        st.header("📈 Beregnings Historikk")
        
        # Vis historikk tabell
        history_data = []
        for i, calc in enumerate(st.session_state.calculations):
            history_data.append({
                "#": i + 1,
                "T (°C)": f"{calc['temperature']:.1f}",
                "RH (%)": f"{calc['relative_humidity']:.1f}",
                "HR (kg/kg)": f"{calc['humidity_ratio']:.6f}",
                "Doggpunkt (°C)": f"{calc['dew_point']:.1f}",
                "Entalpi (J/kg)": f"{calc['enthalpy']:.0f}"
            })
        
        history_df = pd.DataFrame(history_data)
        st.dataframe(history_df, use_container_width=True, hide_index=True)
        
        # Psykrometrisk diagram
        st.subheader("🌡️ Psykrometrisk Diagram")
        chart = create_psychrometric_chart(st.session_state.calculations)
        st.plotly_chart(chart, use_container_width=True)
        
        # Knapp for å tømme historikk
        if st.button("🗑️ Tøm Historikk"):
            st.session_state.calculations = []
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**HXKit Fuktig Luft Kalkulator** | "
        "Powered by [HXKit Web-API](http://localhost:8000/docs) | "
        "Made with [Streamlit](https://streamlit.io)"
    )
    
    # Eksempel data knapp
    with st.sidebar:
        st.markdown("---")
        if st.button("📝 Last Eksempel Data"):
            st.sidebar.success("Eksempel data lastet!")
            # Sett eksempel verdier (dette vil trigge re-run)


if __name__ == "__main__":
    main()