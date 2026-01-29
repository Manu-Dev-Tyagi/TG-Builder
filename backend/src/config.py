from pydantic import BaseModel

class ScoringWeights(BaseModel):
    objective_fit: float = 0.30
    price_fit: float = 0.20
    geography_fit: float = 0.15
    funnel_fit: float = 0.15
    ads_feasibility: float = 0.20

class Config:
    SCORING_WEIGHTS = ScoringWeights()
    
    # Thresholds
    MIN_SCORE_TO_SELECT = 40.0  # Lowered for MVP testing
    
    # Model defaults
    DEFAULT_PROVIDER = "google"
    HEAVY_MODEL = "gemini-2.0-flash" 
    LIGHT_MODEL = "gemini-2.0-flash" 
    DEFAULT_MODEL = HEAVY_MODEL
    DEFAULT_GENERATION_COUNT = 8
    
    # API Keys (Loaded from env usually, but can be referenced here)
    pass
