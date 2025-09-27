"""
2D løser for kryss-strøm varmevekslere.
"""

import numpy as np
from ...grid.grids import Grid2D
from ...streams import AirStream
from ...materials import PlasticMaterial
from ...definitions import Direction
from ...thermodynamics import MoistAir
from .results import PlasticPlateResults

class CrossflowSolver2D:
    """
    2D løser for kryss-strøm med faseendringer (planlagt).
    
    Denne klassen håndterer den numeriske iterasjonen over et 2D-grid
    for å løse varme- og masseoverføring i en kryss-strømskonfigurasjon.
    """
    
    def __init__(self, grid: Grid2D, geometry, material: PlasticMaterial):
        """
        Initialiserer løseren.
        
        Args:
            grid: Grid2D-objektet som definerer beregningsgridet.
            geometry: Geometri-objektet for varmeveksleren.
            material: Material-objektet for platene.
        """
        self.grid = grid
        self.geometry = geometry
        self.material = material
        
        # Initialiser grid-variabler
        self.plate_temp = np.zeros((grid.width_segments, grid.length_segments))
        self.hot_air_temp = np.zeros_like(self.plate_temp)
        self.cold_air_temp = np.zeros_like(self.plate_temp)
        
    def solve(self, hot_stream: AirStream, cold_stream: AirStream):
        """
        Hovedmetode for å kjøre den iterative løseren.
        
        Args:
            hot_stream: Innkommende varm luftstrøm.
            cold_stream: Innkommende kald luftstrøm.
            
        Returns:
            Et PlasticPlateResults objekt med simuleringsresultatene.
        """
        
        # 1. Initialiser temperaturfelter
        self._initialize_fields(hot_stream, cold_stream)
        
        # 2. Iterer til konvergens
        max_iterations = 100
        tolerance = 0.01
        
        for i in range(max_iterations):
            old_plate_temp = self.plate_temp.copy()
            
            # Oppdater luft- og platetemperaturer
            self._update_fields(hot_stream, cold_stream)
            
            # Sjekk konvergens
            max_change = np.max(np.abs(self.plate_temp - old_plate_temp))
            if max_change < tolerance:
                print(f"Konvergens oppnådd etter {i+1} iterasjoner.")
                break
        else:
            print("Advarsel: Maksimalt antall iterasjoner nådd uten konvergens.")
            
        # 3. Beregn og returner resultater
        return self._calculate_results(hot_stream, cold_stream)

    def _initialize_fields(self, hot_stream: AirStream, cold_stream: AirStream):
        """Initialiserer temperaturfeltene før første iterasjon."""
        # Enkel lineær interpolasjon som start-estimat
        avg_temp = (hot_stream.moist_air.temperature + cold_stream.moist_air.temperature) / 2
        self.plate_temp.fill(avg_temp)
        self.hot_air_temp.fill(hot_stream.moist_air.temperature)
        self.cold_air_temp.fill(cold_stream.moist_air.temperature)
        print("Temperaturfelter initialisert.")

    def _update_fields(self, hot_stream: AirStream, cold_stream: AirStream):
        """
        Utfører en komplett sekvensiell oppdatering av alle felter for en iterasjon.
        1. Beregn varm side basert på T_plate_old.
        2. Beregn kald side basert på T_plate_old.
        3. Beregn T_plate_new basert på varmeoverføring fra begge sider.
        """
        w_seg = self.grid.width_segments
        l_seg = self.grid.length_segments

        # Midlertidige lagringsarrays for denne iterasjonen
        self.hot_air_grid = np.full((w_seg, l_seg), None, dtype=object)
        self.cold_air_grid = np.full((w_seg, l_seg), None, dtype=object)
        q_hot_grid = np.zeros_like(self.plate_temp)
        q_cold_grid = np.zeros_like(self.plate_temp)

        # --- 1. Beregn varm side ---
        self._calculate_air_side(hot_stream, self.plate_temp, self.hot_air_grid, q_hot_grid)

        # --- 2. Beregn kald side ---
        self._calculate_air_side(cold_stream, self.plate_temp, self.cold_air_grid, q_cold_grid)

        # --- 3. Oppdater platetemperatur ---
        # Plassholder-verdier for varmeovergangskoeffisienter
        h_hot = 50.0  # W/m²K
        h_cold = 55.0 # W/m²K
        cell_area = self.grid.dx * self.grid.dy

        for i in range(w_seg):
            for j in range(l_seg):
                t_hot_avg = (self.hot_air_grid[i,j].temperature) # Forenkling
                t_cold_avg = (self.cold_air_grid[i,j].temperature) # Forenkling
                
                # Enklere oppdatering for feilsøking
                self.plate_temp[i, j] = (t_hot_avg + t_cold_avg) / 2
        
        # Oppdater temperaturfelter for logging/resultater
        for i in range(w_seg):
            for j in range(l_seg):
                self.hot_air_temp[i, j] = self.hot_air_grid[i, j].temperature
                self.cold_air_temp[i, j] = self.cold_air_grid[i, j].temperature


    def _calculate_air_side(self, stream: AirStream, plate_temp_grid: np.ndarray, 
                            air_grid: np.ndarray, q_grid: np.ndarray):
        """Beregner tilstanden for en luftstrøm gjennom hele gridet."""
        
        w_seg = self.grid.width_segments
        l_seg = self.grid.length_segments

        if stream.direction == Direction.NORTH:
            mass_flow_per_strip = stream.mass_flow / l_seg
            for j in range(l_seg):
                for i in range(w_seg):
                    inlet_air = stream.moist_air if i == 0 else air_grid[i - 1, j]
                    outlet_air, q = self._process_cell_sensible(inlet_air, plate_temp_grid[i, j], mass_flow_per_strip)
                    air_grid[i, j] = outlet_air
                    q_grid[i, j] = q
        elif stream.direction == Direction.SOUTH:
            mass_flow_per_strip = stream.mass_flow / l_seg
            for j in range(l_seg):
                for i in range(w_seg - 1, -1, -1):
                    inlet_air = stream.moist_air if i == w_seg - 1 else air_grid[i + 1, j]
                    outlet_air, q = self._process_cell_sensible(inlet_air, plate_temp_grid[i, j], mass_flow_per_strip)
                    air_grid[i, j] = outlet_air
                    q_grid[i, j] = q
        elif stream.direction == Direction.EAST:
            mass_flow_per_strip = stream.mass_flow / w_seg
            for i in range(w_seg):
                for j in range(l_seg):
                    inlet_air = stream.moist_air if j == 0 else air_grid[i, j - 1]
                    outlet_air, q = self._process_cell_sensible(inlet_air, plate_temp_grid[i, j], mass_flow_per_strip)
                    air_grid[i, j] = outlet_air
                    q_grid[i, j] = q
        elif stream.direction == Direction.WEST:
            mass_flow_per_strip = stream.mass_flow / w_seg
            for i in range(w_seg):
                for j in range(l_seg - 1, -1, -1):
                    inlet_air = stream.moist_air if j == l_seg - 1 else air_grid[i, j + 1]
                    outlet_air, q = self._process_cell_sensible(inlet_air, plate_temp_grid[i, j], mass_flow_per_strip)
                    air_grid[i, j] = outlet_air
                    q_grid[i, j] = q

    def _process_cell_sensible(self, inlet_air: MoistAir, plate_temp: float, mass_flow: float):
        """
        Behandler en enkelt celle kun med sensibel varmeoverføring.
        Returnerer (outlet_air, heat_transfer_rate).
        """
        # Plassholder-verdier
        h = 50.0  # W/m²K
        cp = 1006 # J/kgK
        cell_area = self.grid.dx * self.grid.dy
        
        # NTU-epsilon metode for en enkelt celle
        ua = h * cell_area
        c_min = mass_flow * cp
        
        if c_min < 1e-9: # Unngå divisjon med null hvis massestrøm er null
            return inlet_air, 0.0

        ntu = ua / c_min
        effectiveness = 1 - np.exp(-ntu)
        
        q_max = c_min * (inlet_air.temperature - plate_temp)
        q = effectiveness * q_max
        
        # Beregn utløpstemperatur
        outlet_temp = inlet_air.temperature - q / c_min
        
        outlet_air = MoistAir(temperature=outlet_temp, humidity_ratio=inlet_air.humidity_ratio)
        
        return outlet_air, q

    def _calculate_results(self, hot_stream_in: AirStream, cold_stream_in: AirStream) -> PlasticPlateResults:
        """Beregner og returnerer det endelige resultatobjektet."""
        results = PlasticPlateResults()

        # 1. Finn gjennomsnittlig utløpstilstand
        hot_outlet_air = self._get_outlet_state(self.hot_air_grid, hot_stream_in.direction)
        cold_outlet_air = self._get_outlet_state(self.cold_air_grid, cold_stream_in.direction)
        
        results.hot_outlet_state = hot_outlet_air
        results.cold_outlet_state = cold_outlet_air

        # 2. Beregn virkningsgrad og varmeoverføring basert på temperatur
        cp_hot = hot_stream_in.moist_air.specific_heat_dry_air * 1000 # J/kgK
        c_hot = hot_stream_in.mass_flow * cp_hot

        q_actual = c_hot * (hot_stream_in.moist_air.temperature - hot_outlet_air.temperature)
        
        results.heat_transfer_rate = q_actual / 1000 # Konverter til kW

        # 3. Beregn maksimal mulig varmeoverføring
        cp_cold = cold_stream_in.moist_air.specific_heat_dry_air * 1000 # J/kgK
        c_cold = cold_stream_in.mass_flow * cp_cold
        c_min = min(c_hot, c_cold)
        
        temp_diff_max = hot_stream_in.moist_air.temperature - cold_stream_in.moist_air.temperature
        q_max = c_min * temp_diff_max
        
        if abs(q_max) > 1e-9:
            results.effectiveness = q_actual / q_max
        
        # 4. Lagre felt-data
        results.plate_temperature_field = self.plate_temp
        results.hot_air_temperature_field = self.hot_air_temp
        results.cold_air_temperature_field = self.cold_air_temp

        return results

    def _get_outlet_state(self, air_grid: np.ndarray, direction: Direction) -> MoistAir:
        """Beregner gjennomsnittlig utløpstilstand fra et grid."""
        w_seg, l_seg = air_grid.shape
        
        if direction == Direction.NORTH:
            outlet_cells = air_grid[w_seg - 1, :]
        elif direction == Direction.SOUTH:
            outlet_cells = air_grid[0, :]
        elif direction == Direction.EAST:
            outlet_cells = air_grid[:, l_seg - 1]
        else: # WEST
            outlet_cells = air_grid[:, 0]
            
        # Gjennomsnitt av entalpi og fuktighet
        avg_enthalpy = np.mean([cell.enthalpy for cell in outlet_cells])
        avg_hr = np.mean([cell.humidity_ratio for cell in outlet_cells])
        
        # Beregn temperatur fra gjennomsnittlig entalpi/fuktighet
        # (h - w*h_fg) / cp
        avg_temp = (avg_enthalpy - avg_hr * 2501) / (1.006 + 1.86 * avg_hr)
        
        return MoistAir(temperature=avg_temp, humidity_ratio=avg_hr)
