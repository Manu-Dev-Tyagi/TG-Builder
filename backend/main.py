from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import logging

# Import existing Services and Models
from src.services import ProjectService, InputService
from src.services_persona import PersonaService
from src.services_validation import ValidationService
from src.services_scoring import ScoringService
from src.services_storage import ScoringStorageService
from src.services_portfolio import PortfolioService
from src.services_storage_portfolio import PortfolioStorageService
from src.services_campaign_orchestrator import CampaignOrchestrator
from src.services_storage_campaign import CampaignStorageService
from src.services_budget_orchestrator import BudgetOrchestrator
from src.models import BrandInputCreate, Persona, PersonaList
from src.models_portfolio import FinalPersona
from src.models_campaign import CampaignBlueprint
from src.models_budget import BudgetPlan
from src.llm import LLMClient
from src.config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TG Builder API", version="1.0")

# CORS Configuration for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default + common React ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models for API Request/Response ---

class ProjectResponse(BaseModel):
    project_id: str

class InputRequest(BaseModel):
    project_id: str
    brand_input: BrandInputCreate

class GenerationResponse(BaseModel):
    status: str
    count: int
    project_id: str

# --- Endpoints ---

@app.post("/projects", response_model=ProjectResponse)
def create_project(name: str = Body(..., embed=True)):
    """Create a new project container."""
    try:
        pid = ProjectService.create_project(name)
        return {"project_id": pid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/inputs", response_model=ProjectResponse)
def save_input(request: InputRequest):
    """Normalize and save brand inputs."""
    try:
        normalized = InputService.normalize_input(request.brand_input)
        InputService.save_brand_input(request.project_id, normalized)
        return {"project_id": request.project_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from src.services_core_orchestrator import CoreOrchestrator
from src.services_read_results import ResultsReadService

# ... (Previous imports kept) ...

# --- Endpoints ---

# ... (Previous POST projects/inputs kept) ...

@app.post("/generate", response_model=Dict[str, Any])
def generate_personas(project_id: str = Body(..., embed=True)):
    """
    Trigger Full Pipeline (Phases 2-7).
    Returns Pipeline Verdict.
    """
    try:
        result = CoreOrchestrator.run_full_pipeline(project_id)
        
        # Enforce Pipeline Verdict (Phase 1)
        if result.get("status") == "FAILED":
            # Log the full failure detail for debugging
            logger.error(f"Generation Failed: {result}")
            # Return 422 for strict fail-closed contract
            raise HTTPException(status_code=422, detail=result)
            
        return result
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/{project_id}/results")
def get_project_results(project_id: str): 
    """
    Read-only endpoint to fetch all generated assets.
    """
    try:
        personas = ResultsReadService.get_final_personas(project_id)
        campaigns = ResultsReadService.get_campaign_blueprints(project_id)
        budget = ResultsReadService.get_budget_plan(project_id)
        strategy = ResultsReadService.get_locked_strategy(project_id)
        
        return {
            "strategy": strategy, # Added for Frontend Section 2
            "personas": personas,
            "blueprints": campaigns, # Renamed to match frontend domain model
            "budget": budget
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from src.services_playbook import PlaybookAssemblerService
from fastapi.responses import FileResponse

@app.get("/projects/{project_id}/playbook")
def download_playbook(project_id: str):
    """
    Export the full strategy playbook as a professional PDF.
    """
    try:
        pdf_path = PlaybookAssemblerService.generate_pdf(project_id)
        return FileResponse(
            path=pdf_path,
            filename=f"Auditable_Strategy_{project_id}.pdf",
            media_type="application/pdf"
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/")
def health_check():
    return {"status": "ok", "version": "1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
