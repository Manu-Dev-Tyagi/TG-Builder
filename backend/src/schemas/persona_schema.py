from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field

class Psychographics(BaseModel):
    values: List[str]
    motivations: List[str]
    beliefs: List[str]

class BuyingBehavior(BaseModel):
    purchase_triggers: List[str]
    price_sensitivity: str # Relaxed from Literal
    decision_speed: str # Relaxed from Literal

    model_config = {"extra": "ignore"}

class DigitalIndex(BaseModel):
    research_orientation: int 
    digital_comfort: int
    category_maturity: int
    shopping_intent: int
    device_usage: List[str]
    content_consumption: List[str] = [] # Optional default
    model_config = {"extra": "ignore"}

class PersonaContract(BaseModel):
    persona_id: Optional[str] = None
    name: str

    # Demographics
    funnel_role: Literal["Primary Buyer", "Influencer", "Repeat Purchaser", "Decision Maker", "End User"]
    location: str
    age_range: str
    gender: str
    profession: str
    household_income: str

    # Psychographics
    archetype: str # e.g. "Gutsy Solopreneur"
    psychographics: Psychographics
    needs: List[str] # Deep underlying needs
    frustrations: List[str] # Distinct from pain points (emotional)
    value_drivers: List[str]
    delights: List[str]
    
    # Digital Index
    digital_index: DigitalIndex
    
    # Marketing Layer
    pain_points: List[str]
    usp_alignment_reason: str
    platform_affinity: List[str]
    preferred_platforms: List[str]
    
    # Buying Behavior
    buying_behavior: BuyingBehavior

    # Targeting
    interests: List[str]
    hobbies: List[str]
    exclusions: List[str]
    placements: List[str]

    # Meta info
    confidence_score: float
    model_config = {"extra": "ignore"}

class PersonaContractList(BaseModel):
    personas: List[PersonaContract]
