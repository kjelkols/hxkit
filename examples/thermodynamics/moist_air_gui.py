"""
HXKit Fuktig Luft Kalkulator - GUI
==================================
Desktop GUI for beregning av fuktig luft egenskaper
Bruker HXKit Web-API for beregninger
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from typing import Optional


class MoistAirCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("HXKit - Fuktig Luft Kalkulator")
        self.root.geometry("800x600")
        
        # API konfigurasjon
        self.api_base_url = "http://localhost:8000"
        
        # Sjekk API tilkobling ved oppstart
        self.check_api_connection()
        
        # Opprett GUI
        self.create_widgets()
        
    def check_api_connection(self):
        """Sjekk om APIet er tilgjengelig"""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=2)
            if response.status_code != 200:
                self.show_api_error()
        except:
            self.show_api_error()
    
    def show_api_error(self):
        """Vis feilmelding hvis API ikke er tilgjengelig"""
        messagebox.showerror(
            "API Ikke Tilgjengelig",
            "HXKit API er ikke tilgjengelig.\n\n"
            "Start serveren med:\n"
            "python examples/fastapi_server.py\n\n"
            "Applikasjonen vil fortsette, men beregninger vil feile."
        )
    
    def create_widgets(self):
        """Opprett GUI elementer"""
        
        # Hovedframe
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Tittel
        title_label = ttk.Label(
            main_frame, 
            text="Fuktig Luft Kalkulator",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # Input seksjoner
        self.create_input_section(main_frame)
        self.create_results_section(main_frame)
        self.create_buttons(main_frame)
        
        # Konfigurer grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(3, weight=1)
    
    def create_input_section(self, parent):
        """Opprett input seksjonen"""
        
        # Input frame
        input_frame = ttk.LabelFrame(parent, text="Lufttilstand", padding="10")
        input_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Input felter
        self.input_vars = {}
        
        # Temperatur
        ttk.Label(input_frame, text="Temperatur (°C):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.input_vars['temperature'] = tk.StringVar(value="25.0")
        ttk.Entry(input_frame, textvariable=self.input_vars['temperature'], width=15).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 20), pady=2
        )
        
        # Trykk
        ttk.Label(input_frame, text="Trykk (Pa):").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.input_vars['pressure'] = tk.StringVar(value="101325")
        ttk.Entry(input_frame, textvariable=self.input_vars['pressure'], width=15).grid(
            row=0, column=3, sticky=(tk.W, tk.E), padx=(10, 0), pady=2
        )
        
        # Velg input metode
        ttk.Label(input_frame, text="Fuktighet:").grid(row=1, column=0, sticky=tk.W, pady=(10, 2))
        
        self.humidity_method = tk.StringVar(value="relative_humidity")
        methods_frame = ttk.Frame(input_frame)
        methods_frame.grid(row=1, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 2))
        
        ttk.Radiobutton(
            methods_frame, text="Relativ fuktighet (%)", 
            variable=self.humidity_method, value="relative_humidity",
            command=self.on_method_change
        ).grid(row=0, column=0, sticky=tk.W)
        
        ttk.Radiobutton(
            methods_frame, text="Fuktighetsforhold (kg/kg)", 
            variable=self.humidity_method, value="humidity_ratio",
            command=self.on_method_change
        ).grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        ttk.Radiobutton(
            methods_frame, text="Doggpunkt (°C)", 
            variable=self.humidity_method, value="dew_point",
            command=self.on_method_change
        ).grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        
        # Fuktighet input
        self.humidity_label = ttk.Label(input_frame, text="Relativ fuktighet (%):")
        self.humidity_label.grid(row=2, column=0, sticky=tk.W, pady=2)
        
        self.input_vars['humidity_value'] = tk.StringVar(value="60.0")
        self.humidity_entry = ttk.Entry(input_frame, textvariable=self.input_vars['humidity_value'], width=15)
        self.humidity_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 20), pady=2)
        
        # Konfigurer grid weights
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)
    
    def create_results_section(self, parent):
        """Opprett resultat seksjonen"""
        
        # Resultat frame
        results_frame = ttk.LabelFrame(parent, text="Beregnet Luftegenskaper", padding="10")
        results_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Resultat labels
        self.result_vars = {}
        properties = [
            ("Temperatur", "°C", "temperature"),
            ("Trykk", "Pa", "pressure"),
            ("Relativ fuktighet", "%", "relative_humidity"),
            ("Fuktighetsforhold", "kg/kg", "humidity_ratio"),
            ("Doggpunkt", "°C", "dew_point"),
            ("Våtkuletemperatur", "°C", "wet_bulb"),
            ("Entalpi", "J/kg", "enthalpy"),
            ("Tetthet", "kg/m³", "density"),
            ("Spesifikt volum", "m³/kg", "specific_volume")
        ]
        
        for i, (name, unit, key) in enumerate(properties):
            row = i // 3
            col = (i % 3) * 2
            
            ttk.Label(results_frame, text=f"{name}:").grid(
                row=row, column=col, sticky=tk.W, pady=2, padx=(0, 10)
            )
            
            self.result_vars[key] = tk.StringVar(value="−")
            result_label = ttk.Label(
                results_frame, 
                textvariable=self.result_vars[key],
                font=("Courier", 9)
            )
            result_label.grid(row=row, column=col+1, sticky=tk.W, pady=2, padx=(0, 30))
            
            # Legg til enhet
            ttk.Label(results_frame, text=unit, foreground="gray").grid(
                row=row, column=col+1, sticky=tk.E, pady=2, padx=(0, 30)
            )
        
        # Konfigurer grid weights
        for i in range(6):
            results_frame.columnconfigure(i, weight=1)
        
        parent.rowconfigure(2, weight=1)
    
    def create_buttons(self, parent):
        """Opprett knapper"""
        
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=3, column=0, columnspan=4, pady=(10, 0))
        
        ttk.Button(
            button_frame, text="Beregn Egenskaper", 
            command=self.calculate_properties,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            button_frame, text="Nullstill", 
            command=self.reset_form
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            button_frame, text="Eksempel Data", 
            command=self.load_example
        ).pack(side=tk.LEFT)
    
    def on_method_change(self):
        """Oppdater GUI når fuktighet metode endres"""
        method = self.humidity_method.get()
        
        if method == "relative_humidity":
            self.humidity_label.config(text="Relativ fuktighet (%):")
            self.input_vars['humidity_value'].set("60.0")
        elif method == "humidity_ratio":
            self.humidity_label.config(text="Fuktighetsforhold (kg/kg):")
            self.input_vars['humidity_value'].set("0.010")
        elif method == "dew_point":
            self.humidity_label.config(text="Doggpunkt (°C):")
            self.input_vars['humidity_value'].set("15.0")
    
    def calculate_properties(self):
        """Beregn luftegenskaper via API"""
        try:
            # Hent input verdier
            temperature = float(self.input_vars['temperature'].get())
            pressure = float(self.input_vars['pressure'].get())
            humidity_value = float(self.input_vars['humidity_value'].get())
            method = self.humidity_method.get()
            
            # Bygg API request
            data = {
                "temperature": temperature,
                "pressure": pressure,
                "relative_humidity": None,
                "humidity_ratio": None,
                "dew_point": None,
                "wet_bulb": None
            }
            
            # Sett riktig fuktighet parameter
            data[method] = humidity_value
            
            # Send API request
            response = requests.post(
                f"{self.api_base_url}/api/v1/air-properties",
                json=data,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                self.display_results(result)
            else:
                error_msg = response.json().get('detail', 'Ukjent feil')
                messagebox.showerror("API Feil", f"Feil fra API: {error_msg}")
                
        except ValueError as e:
            messagebox.showerror("Input Feil", "Sjekk at alle verdier er gyldige tall")
        except requests.RequestException as e:
            messagebox.showerror(
                "Tilkobling Feil", 
                "Kan ikke koble til API. Sjekk at serveren kjører:\n"
                "python examples/fastapi_server.py"
            )
        except Exception as e:
            messagebox.showerror("Feil", f"Uventet feil: {str(e)}")
    
    def display_results(self, result):
        """Vis beregnet resultater"""
        
        # Formatering funksjoner
        def format_number(value, decimals=3):
            if value is None:
                return "−"
            if isinstance(value, (int, float)):
                return f"{value:.{decimals}f}"
            return str(value)
        
        # Oppdater alle resultat felter
        self.result_vars['temperature'].set(format_number(result.get('temperature'), 1))
        self.result_vars['pressure'].set(format_number(result.get('pressure'), 0))
        self.result_vars['relative_humidity'].set(format_number(result.get('relative_humidity'), 1))
        self.result_vars['humidity_ratio'].set(format_number(result.get('humidity_ratio'), 6))
        self.result_vars['dew_point'].set(format_number(result.get('dew_point'), 1))
        self.result_vars['wet_bulb'].set(format_number(result.get('wet_bulb'), 1))
        self.result_vars['enthalpy'].set(format_number(result.get('enthalpy'), 0))
        self.result_vars['density'].set(format_number(result.get('density'), 3))
        self.result_vars['specific_volume'].set(format_number(result.get('specific_volume'), 3))
    
    def reset_form(self):
        """Nullstill alle felter"""
        self.input_vars['temperature'].set("25.0")
        self.input_vars['pressure'].set("101325")
        self.input_vars['humidity_value'].set("60.0")
        self.humidity_method.set("relative_humidity")
        self.on_method_change()
        
        # Nullstill resultater
        for var in self.result_vars.values():
            var.set("−")
    
    def load_example(self):
        """Last inn eksempel data"""
        self.input_vars['temperature'].set("30.0")
        self.input_vars['pressure'].set("101325")
        self.input_vars['humidity_value'].set("75.0")
        self.humidity_method.set("relative_humidity")
        self.on_method_change()


def main():
    """Hovedfunksjon"""
    # Opprett hovedvindu
    root = tk.Tk()
    
    # Sett opp styling
    style = ttk.Style()
    style.theme_use('clam')  # Moderne tema
    
    # Opprett applikasjon
    app = MoistAirCalculator(root)
    
    # Start GUI loop
    root.mainloop()


if __name__ == "__main__":
    main()