from typing import Optional, List, Literal
from pydantic import BaseModel, Field, UUID4, validator
from datetime import datetime

class BrandInputBase(BaseModel):
    brand_name: str
    product_category: str
    price_positioning: str
    geography: str
    primary_usp: str
    primary_objective: str
    price_sensitivity: Literal["High", "Medium", "Low"]
    decision_speed: Literal["Fast", "Normal", "Slow"] # Added for Input Layer
    platform_affinity: List[str] = Field(default_factory=list) # Added for Input Layer
    budget_range: Optional[str] = None # Added for Input Layer ("$1k-$5k")
    
    @validator("primary_objective")
    def validate_objective(cls, v):
        # Frontend Requirement 1.2: Hard Gated Enum
        allowed = ["Purchases", "Leads", "App Installs"]
        if v.title() not in allowed:
            raise ValueError(f"Invalid objective. Must be one of {allowed}")
        return v.title()

    @validator("price_positioning")
    def validate_price(cls, v):
        if not v or v.lower() == "null" or v.lower() == "none":
            raise ValueError("Price positioning cannot be empty")
        return v

    # Optional fields with defaults
    age_ranges: List[str] = Field(default_factory=list)
    cities: List[str] = Field(default_factory=list)
    professions: List[str] = Field(default_factory=list)
    known_audience_insights: Optional[str] = None
    strategy_depth: Literal["classification_only", "full_funnel"] = "full_funnel"

class BrandInputCreate(BrandInputBase):
    pass

class BrandInputInDB(BrandInputBase):
    id: str  # UUID as string for compatibility
    project_id: str
    created_at: str

    class Config:
        from_attributes = True

# Response Models
class ProjectCreate(BaseModel):
    project_name: str

class ProjectInDB(ProjectCreate):
    id: str
    created_at: str
    updated_at: str

# Existing models below (kept for reference, can merge if needed)
class Demographics(BaseModel):
    age_range: str = Field(..., description="e.g. '25-34'")
    gender: str = Field(..., description="e.g. 'Female', 'Male', 'All'")
    location: str = Field(..., description="Geographic focus, e.g. 'Tier-1 Cities'")
    profession: str = Field(..., description="Job title or industry")
    income_level: str = Field(..., description="e.g. 'High', 'Mid-High'")

class Psychographics(BaseModel):
    goals: List[str] = Field(..., description="Key aspirations of this persona")
    beliefs: List[str] = Field(..., description="Core values or beliefs")
    lifestyle: List[str] = Field(..., description="Lifestyle descriptors, e.g. 'Urban', 'Busy'")

class Persona(BaseModel):
    name: str = Field(..., description="A creative name for this persona")
    demographics: Demographics
    psychographics: Psychographics
    motivations: List[str] = Field(..., description="Why they would buy the product")
    pain_points: List[str] = Field(..., description="What stops them from buying")
    content_consumption: List[str] = Field(..., description="Where they spend time online")
    funnel_role: str = Field(..., description="e.g. 'Primary Buyer', 'Influencer'")

class PersonaList(BaseModel):
    personas: List[Persona]
