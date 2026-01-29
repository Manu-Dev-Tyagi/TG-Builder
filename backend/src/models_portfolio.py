from pydantic import BaseModel
from typing import List, Optional, Dict

class PlatformDecision(BaseModel):
    """Structured Platform Gate Decision (Review Point 4)"""
    allowed: bool
    reason: str

class FinalPersona(BaseModel):
    persona_id: str
    rank: int
    role_in_portfolio: str
    recommended_platforms: List[str]
    campaign_type: str = "NA"
    funnel_stage: str
    notes: Optional[str] = None
    project_id: str

    # Structured Platform Decisions (addresses Review Point 4)
    platform_decisions: Dict[str, PlatformDecision] = {}
    # e.g. {"Meta": {"allowed": False, "reason": "Impulse absent"}, "Google": {"allowed": True, "reason": "High intent"}}

    # Complete Snapshot Fields (Requirement 4)
    location: str
    age_range: str
    gender: str
    profession: str
    household_income: str
    psychographics: Dict  # Nested values, motivations, beliefs
    buying_behavior: Dict # Nested triggers, sensitivity, speed
    pain_points: List[str]
    interests: List[str]
    hobbies: List[str]
    usp_alignment: Optional[str] = None
