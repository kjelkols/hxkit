# 3D Visualisering av Varmevekslere

HXKit tilbyr to måter å visualisere varmevekslere i 3D:

## 📊 **Matplotlib (Statisk 3D)**

**Fordeler:**
- ✅ Høy kvalitet bilder
- ✅ Perfekt for rapporter og dokumentasjon
- ✅ Eksport til PNG, PDF, SVG
- ✅ God kontroll over styling

**Installasjon:**
```bash
pip install matplotlib
```

**Eksempel:**
```python
from hxkit import Direction
from hxkit.heatexchangers.plastic_plate import PlasticPlateGeometry
from hxkit.visualization import visualize_heat_exchanger

# Opprett geometri
geometry = PlasticPlateGeometry(
    width=0.6, length=1.2, plate_thickness=0.001, 
    channel_height=0.008, num_plates=20
)

# Visualiser crossflow konfigurasjon
fig = visualize_heat_exchanger(
    geometry=geometry,
    hot_direction=Direction.NORTH,
    cold_direction=Direction.EAST,
    show_grid=True,
    grid_resolution=(6, 8),
    save_path="my_heat_exchanger.png"
)

fig.show()
```

## 🌐 **Plotly (Interaktiv 3D)**

**Fordeler:**
- ✅ Interaktiv zoom, rotate, pan
- ✅ Hover-informasjon på komponenter
- ✅ Web-basert visning
- ✅ Eksport til HTML for deling
- ✅ Profesjonell finish

**Installasjon:**
```bash
pip install plotly
```

**Eksempel:**
```python
from hxkit import Direction
from hxkit.heatexchangers.plastic_plate import PlasticPlateGeometry
from hxkit.visualization import create_interactive_visualization

# Opprett geometri
geometry = PlasticPlateGeometry(
    width=0.6, length=1.2, plate_thickness=0.001,
    channel_height=0.008, num_plates=20
)

# Visualiser counterflow konfigurasjon
fig = create_interactive_visualization(
    geometry=geometry,
    hot_direction=Direction.NORTH,
    cold_direction=Direction.SOUTH,
    save_html="interactive_hx.html"
)

fig.show()  # Åpner i nettleser
```

## 🎯 **Hva visualiseres**

### Plater
- **Røde plater**: Kanaler for varm luft
- **Turkise plater**: Kanaler for kald luft
- **Realistisk tykkelse**: Faktisk platetykkelse og kanalhøyde

### Strømningsretninger
- **Orange piler**: Varm luftstrøm med retning
- **Cyan piler**: Kald luftstrøm med retning
- **Himmelretninger**: North, South, East, West

### Grid (valgfritt)
- **Sorte linjer**: Viser numerisk diskretisering
- **Konfigurerbar**: Justerbar oppløsning

## 🔧 **Konfigurerbare parametere**

### Geometri
```python
PlasticPlateGeometry(
    width=0.6,           # Bredde [m] (Y-akse)
    length=1.2,          # Lengde [m] (X-akse)  
    plate_thickness=0.001,  # Platetykkelse [m]
    channel_height=0.008,   # Kanalhøyde [m]
    num_plates=20        # Antall plater
)
```

### Strømningskonfigurasjoner
```python
# Counterflow (motstrøm)
Direction.NORTH ↔ Direction.SOUTH
Direction.EAST ↔ Direction.WEST

# Parallelflow (medstrøm)  
Direction.NORTH → Direction.NORTH
Direction.EAST → Direction.EAST

# Crossflow (kryssstrøm)
Direction.NORTH × Direction.EAST
Direction.SOUTH × Direction.WEST
# ... alle kombinasjoner av vinkelrette retninger
```

### Grid-visualisering
```python
show_grid=True              # Vis/skjul grid
grid_resolution=(6, 8)      # Oppløsning (bredde × lengde)
```

## 📁 **Eksport-alternativer**

### Matplotlib
```python
# Lagre som høyoppløselig bilde
fig.savefig("hx.png", dpi=300, bbox_inches='tight')
fig.savefig("hx.pdf", bbox_inches='tight')  # For LaTeX/rapporter
fig.savefig("hx.svg", bbox_inches='tight')  # Vektorgrafikk
```

### Plotly
```python
# Lagre som interaktiv HTML
fig.write_html("hx.html")

# Lagre som statisk bilde (krever kaleido: pip install kaleido)
fig.write_image("hx.png", width=1200, height=800)
fig.write_image("hx.pdf", width=1200, height=800)
```

## 🎨 **Tilpasning av utseende**

### Matplotlib farger
```python
visualizer = HeatExchangerVisualizer()
visualizer.colors['hot_plate'] = '#FF0000'    # Rød
visualizer.colors['cold_plate'] = '#0000FF'   # Blå
visualizer.colors['hot_flow'] = '#FFA500'     # Orange
# ... osv
```

### Plotly styling
```python
visualizer = InteractiveHeatExchangerVisualizer()
visualizer.colors['hot_plate'] = '#FF6B6B'
# Tilpass kamera-vinkel, lighting, osv.
```

## 🚀 **Komplett eksempel**

```python
#!/usr/bin/env python3
"""Komplett visualiserings-eksempel."""

from hxkit import Direction
from hxkit.heatexchangers.plastic_plate import PlasticPlateGeometry

# Test både statisk og interaktiv visualisering
def main():
    # Definer geometri
    geometry = PlasticPlateGeometry(0.8, 1.5, 0.0015, 0.010, 25)
    
    # Matplotlib (statisk)
    try:
        from hxkit.visualization import visualize_heat_exchanger
        fig = visualize_heat_exchanger(
            geometry, Direction.NORTH, Direction.EAST,
            save_path="static_hx.png"
        )
        print("✅ Statisk visualisering lagret som static_hx.png")
    except ImportError:
        print("⚠️  Installer matplotlib: pip install matplotlib")
    
    # Plotly (interaktiv)  
    try:
        from hxkit.visualization import create_interactive_visualization
        fig = create_interactive_visualization(
            geometry, Direction.NORTH, Direction.SOUTH,
            save_html="interactive_hx.html"
        )
        print("✅ Interaktiv visualisering lagret som interactive_hx.html")
        fig.show()
    except ImportError:
        print("⚠️  Installer plotly: pip install plotly")

if __name__ == "__main__":
    main()
```

## 🔍 **Brukstilfeller**

### Dokumentasjon og rapporter
- **Matplotlib**: Høykvalitets figurer for teknisk dokumentasjon
- **Grid-vis**: Vis numerisk diskretisering
- **Eksport**: PDF/SVG for LaTeX-dokumenter

### Interaktiv utforsking  
- **Plotly**: Utforsk geometri fra alle vinkler
- **Hover**: Detaljert informasjon om komponenter
- **Web-deling**: Send HTML-fil til kolleger

### Presentasjoner
- **Begge**: Avhengig av om du trenger interaktivitet
- **Animasjon**: Plotly støtter animerte overganger
- **Zoom**: Fokuser på spesifikke områder

---

*For mer informasjon, se eksemplene i `examples/` mappen.*