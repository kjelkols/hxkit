"""
Komplett FastAPI implementasjon for HXKit Web-API

Dette viser hvordan du lager en produksjonsklar web-API.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import uvicorn
import json
from datetime import datetime

from hxkit.api import AnalysisAdapter, ThermodynamicsAdapter
from hxkit.schemas import AnalysisInput, AnalysisOutput, MoistAirInput, MoistAirOutput

# Opprett FastAPI app
app = FastAPI(
    title="HXKit API",
    description="Platevarmeveksler beregnings-API",
    version="1.0.0",
    docs_url="/docs",  # Interaktiv dokumentasjon på /docs
    redoc_url="/redoc"  # Alternativ dokumentasjon på /redoc
)

# Tillat CORS for web-frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # I produksjon: spesifiser domener
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enkel logging (i produksjon: bruk riktig logging)
api_log = []

def log_request(endpoint: str, success: bool, details: str = ""):
    """Logger API-kall"""
    api_log.append({
        "timestamp": datetime.now().isoformat(),
        "endpoint": endpoint,
        "success": success,
        "details": details
    })


# API Endepunkter
@app.get("/")
async def root():
    """Velkomstmelding og API informasjon"""
    return {
        "message": "Velkommen til HXKit API!",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "analyze": "POST /api/v1/analyze",
            "air_properties": "POST /api/v1/air-properties",
            "health": "GET /health",
            "stats": "GET /stats"
        }
    }


@app.post("/api/v1/analyze", response_model=AnalysisOutput)
async def analyze_heat_exchanger(
    analysis_input: AnalysisInput,
    background_tasks: BackgroundTasks
):
    """
    Analyser platevarmeveksler
    
    Tar imot komplett varmeveksler konfigurasjon og returnerer
    detaljerte analyseresultater inkludert varmeoverføring,
    effectiveness, trykkfall og utløpsforhold.
    """
    try:
        # Utfør analyse med adapter
        result = AnalysisAdapter.analyze_from_schema(analysis_input)
        
        # Log suksess i bakgrunnen
        background_tasks.add_task(
            log_request, 
            "analyze", 
            True, 
            f"HT: {result.heat_transfer_rate:.0f}W"
        )
        
        return result
        
    except Exception as e:
        # Log feil
        background_tasks.add_task(log_request, "analyze", False, str(e))
        raise HTTPException(status_code=400, detail=f"Analyse feil: {str(e)}")


@app.post("/api/v1/air-properties", response_model=MoistAirOutput)
async def get_air_properties(air_input: MoistAirInput):
    """
    Beregn luftegenskaper
    
    Beregner alle termodynamiske egenskaper for fuktig luft
    basert på temperatur og en fuktighetsparameter.
    """
    try:
        # Konverter til kjerne objekt og tilbake
        air_object = ThermodynamicsAdapter.from_schema(air_input)
        result = ThermodynamicsAdapter.to_schema(air_object)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Luftegenskap feil: {str(e)}")


@app.post("/api/v1/analyze-json")
async def analyze_from_json(json_data: dict):
    """
    JSON til JSON analyse
    
    Enkel endepunkt som tar imot ren JSON og returnerer JSON.
    Nyttig for systemer som ikke bruker OpenAPI schemas.
    """
    try:
        # Konverter dict til JSON string og prosesser
        json_string = json.dumps(json_data)
        result_json = AnalysisAdapter.analyze_from_json(json_string)
        return json.loads(result_json)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"JSON analyse feil: {str(e)}")


@app.get("/health")
async def health_check():
    """Helsesjekk for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.get("/stats")
async def get_stats():
    """API statistikk"""
    total_requests = len(api_log)
    successful_requests = sum(1 for log in api_log if log["success"])
    
    return {
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
        "recent_requests": api_log[-10:]  # Siste 10 requests
    }


# Batch prosessering endepunkt
class BatchAnalysisRequest(BaseModel):
    """Schema for batch analyse requests"""
    cases: List[AnalysisInput]
    case_names: List[str] = []

@app.post("/api/v1/batch-analyze")
async def batch_analyze(batch_request: BatchAnalysisRequest):
    """
    Batch analyse av flere cases
    
    Nyttig for å analysere mange konfigurasoner samtidig,
    for eksempel optimalisering eller parameterstudie.
    """
    try:
        results = []
        
        for i, case in enumerate(batch_request.cases):
            try:
                result = AnalysisAdapter.analyze_from_schema(case)
                case_name = (batch_request.case_names[i] 
                           if batch_request.case_names and i < len(batch_request.case_names)
                           else f"Case_{i+1}")
                
                results.append({
                    "case_name": case_name,
                    "success": True,
                    "result": result.model_dump()
                })
                
            except Exception as e:
                results.append({
                    "case_name": f"Case_{i+1}",
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "total_cases": len(batch_request.cases),
            "successful_cases": sum(1 for r in results if r["success"]),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Batch analyse feil: {str(e)}")


if __name__ == "__main__":
    print("🚀 Starter HXKit Web-API...")
    print("📚 Dokumentasjon: http://localhost:8000/docs")
    print("🔗 API: http://localhost:8000")
    print("📝 Trykk Ctrl+C for å stoppe serveren")
    print()
    
    # Start serveren
    try:
        uvicorn.run(
            app, 
            host="127.0.0.1",  # Lokal tilgang (localhost)
            port=8000,
            reload=False  # Deaktiver reload for å unngå import string warning
        )
    except KeyboardInterrupt:
        print("\n👋 Server stoppet")