# Web API Examples

Denne mappen inneholder eksempler for web-baserte APIer og web-applikasjoner med HXKit.

## 📁 Filer

### FastAPI Server

- **`fastapi_server.py`** - Fullstendig FastAPI server
  - RESTful API med automatisk dokumentasjon (Swagger/OpenAPI)
  - Endpoints for luftegenskaper og varmeveksler-analyse
  - Pydantic schema validering
  - CORS-støtte for web-applikasjoner

### API Demonstrasjoner

- **`web_api_demo.py`** - Web API eksempel
  - Simulert web-API klasse
  - Viser hvordan adapters brukes i praksis
  - Demonstrerer JSON request/response håndtering

- **`api_client_demo.py`** - API client eksempel
  - Viser hvordan man konsumerer HXKit API
  - HTTP request/response håndtering
  - Feilhåndtering og timeout-konfiguration

### API Adapters

- **`api_adapters_demo.py`** - Detaljert adapter demo
  - Komplett demonstrasjon av alle adapter-typer
  - ThermodynamicsAdapter, GeometryAdapter, AnalysisAdapter
  - Schema-til-objekt konvertering

- **`api_adapters_simple.py`** - Enkel adapter demo
  - Grunnleggende bruk av adapters
  - Enkel schema-validering
  - Rask intro til adapter-konseptet

### Web Applications

- **`streamlit_app.py`** - Streamlit web-app
  - Interaktiv web-applikasjon
  - Real-time beregninger i nettleser
  - Grafiske brukergrensesnitt for HXKit

- **`web_calculator.html`** - HTML kalkulator
  - Statisk HTML/JavaScript kalkulator
  - Frontend for HXKit API
  - Enkel web-basert beregning

## 🚀 Kom i gang

### Start FastAPI server
```bash
# Fra root-katalogen
python examples/webapi/fastapi_server.py

# Server kjører på http://localhost:8000
# API dokumentasjon: http://localhost:8000/docs
```

### Test API endpoints
```bash
# Test API client
python examples/webapi/api_client_demo.py

# Web API demo (simulert)
python examples/webapi/web_api_demo.py
```

### Kjør web-app
```bash
# Streamlit app
streamlit run examples/webapi/streamlit_app.py

# Åpner i nettleser på http://localhost:8501
```

### Adapter eksempler
```bash
# Detaljert demo
python examples/webapi/api_adapters_demo.py

# Enkel demo
python examples/webapi/api_adapters_simple.py
```

## 🌐 API Endpoints

Når FastAPI serveren kjører, er disse endpoints tilgjengelige:

### Thermodynamics
- `POST /api/v1/air-properties` - Beregn luftegenskaper
- `GET /health` - Server health check

### Heat Exchangers
- `POST /api/v1/analyze` - Varmeveksler analyse
- `GET /api/v1/geometries` - Tilgjengelige geometrier

### Documentation
- `GET /docs` - Swagger/OpenAPI dokumentasjon
- `GET /redoc` - Alternative API dokumentasjon

## 📊 Hva eksemplene viser

- ✅ **FastAPI integration**: Moderne Python web framework
- ✅ **Pydantic schemas**: Automatisk validering og dokumentasjon
- ✅ **Adapter pattern**: Clean separation mellom API og core logic
- ✅ **CORS configuration**: Support for web-applikasjoner
- ✅ **Error handling**: Robust feilhåndtering og statuskoder
- ✅ **Interactive UIs**: Streamlit og HTML/JavaScript grensesnitt

## 🔧 Avhengigheter

```bash
# For FastAPI
pip install fastapi uvicorn

# For Streamlit
pip install streamlit

# For HTTP requests
pip install requests

# Alle avhengigheter
pip install fastapi uvicorn streamlit requests
```

## 🌍 Bruksområder

- **Microservices**: HXKit som mikroservice i større systemer
- **Web dashboard**: Real-time monitoring og beregninger
- **Integration**: Integrere HXKit med eksisterende web-systemer
- **Prototyping**: Rask utvikling av web-baserte verktøy
- **API-first**: Bygg frontend-agnostiske løsninger

## 🔗 Relaterte moduler

- `hxkit.api` - API adapter implementasjoner
- `hxkit.schemas` - Pydantic schema definisjoner
- `hxkit.thermodynamics` - Core thermodynamic beregninger
- `hxkit.heatexchangers` - Varmeveksler implementasjoner

## 📝 Noter

- FastAPI serveren kjører på port 8000 som standard
- Streamlit app kjører på port 8501 som standard
- CORS er konfigurert for utvikling (tillater alle origins)
- Alle APIer bruker JSON for data-utveksling
- Automatisk API dokumentasjon genereres av FastAPI