from pydantic import BaseModel
from typing import List, Optional, Literal

class GoogleKeywordGroup(BaseModel):
    theme: str
    match_type: str # Relaxed from Literal["Exact", "Phrase", "Broad"]
    keywords: List[str]

class MetaExclusions(BaseModel):
    interests: List[str] = []
    behaviors: List[str] = []
    custom_audiences: List[str] = []

class MetaAdset(BaseModel):
    name: str # META | Persona | Funnel | Type
    funnel_stage: str # TOF, MOF, BOF
    targeting_type: str # Broad, Interest Stack, Remarketing, Lookalike
    age_range: str
    gender: str
    locations: str
    interests: List[str]
    behaviors: List[str]
    exclusions: MetaExclusions
    placements: str # Advantage+ or Manual (Specifics)
    primary_benefit: Optional[str] = None # For ad copy alignment

class GoogleAudienceSignals(BaseModel):
    in_market: List[str] = []
    affinity: List[str] = []
    custom_segments: List[str] = []
    demographics: Optional[str] = None

class GoogleAdGroup(BaseModel):
    name: str # GOOGLE | Persona | Intent | Theme
    campaign_type: str # Search, Demand Gen, P-Max
    intent: str # Awareness, Consideration, Conversion
    keywords: List[GoogleKeywordGroup] = []
    audience_signals: Optional[GoogleAudienceSignals] = None

class CampaignBlueprint(BaseModel):
    project_id: str
    meta_adsets: List[MetaAdset]
    google_adgroups: List[GoogleAdGroup]
    guardrails: List[str] = []
    platform_rationale: str = ""
