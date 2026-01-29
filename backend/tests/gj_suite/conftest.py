import pytest
from unittest.mock import MagicMock
from src.llm import LLMClient
from src.schemas.persona_schema import PersonaContractList, PersonaContract
from src.wrappers.meta_cluster_builder import InterestCluster, MetaClusterList, ExclusionCluster

# Mock Data for Clusters
def mock_build_clusters(llm_client, persona, brand_usp):
     # 3 Clusters (TOF, MOF, BOF)
     return [
         InterestCluster(
             funnel_stage="TOF",
             cluster_name="Broad",
             interests=["Interest 1", "Interest 2"],
             exclusions=ExclusionCluster(interests=[], behaviors=[]),
             reasoning="Awareness"
         ),
         InterestCluster(
             funnel_stage="MOF",
             cluster_name="Consideration",
             interests=["Interest 3", "Interest 4"],
             exclusions=ExclusionCluster(interests=[], behaviors=[]),
             reasoning="Nurture"
         ),
         InterestCluster(
             funnel_stage="BOF",
             cluster_name="Conversion",
             interests=["Interest 5"],
             exclusions=ExclusionCluster(interests=[], behaviors=[]),
             reasoning="Close"
         )
     ]

# --- MOCK LLM CLIENT ---
class MockLLMClient:
    def __init__(self, provider="groq", model_name=None):
        self.provider = provider
        self.call_history = [] # To verify if called

    def generate_personas(
        self, 
        brand_name: str, 
        product_category: str, 
        price_positioning: str, 
        primary_usp: str, 
        primary_objective: str, 
        known_audience_insights: str = "", 
        count: int = 3, 
        geography: str = "Global", 
        campaign_context: str = "General"
    ) -> PersonaContractList:
        
        self.call_history.append("generate_personas")
        
        # MOCK BEHAVIOR: Return specific personas based on brand_name for specific TCs
        
        # TC-03: IBS Persona (Missing Trigger)
        if brand_name == "Daily Bloom IBS":
            return PersonaContractList(personas=[
                PersonaContract(
                    persona_id="mock_ni",
                    name="Invalid IBS Sufferer",
                    profession="Teacher",
                    age_range="35-44",
                    gender="Female",
                    location="Metro",
                    household_income="Medium",
                    psychographics={"values": ["Relief"], "motivations": ["Pain free"], "beliefs": ["Natural"]},
                    buying_behavior={
                         "purchase_triggers": [], # EMPTY LIST -> VIOLATION
                         "price_sensitivity": "Medium", 
                         "decision_speed": "Slow"
                    },
                    pain_points=["Bloating"],
                    content_consumption=["Blogs"],
                    platform_affinity=["Google"],
                    preferred_platforms=["Google Search"],
                    usp_alignment_reason="Matches",
                    confidence_score=0.8,
                    interests=["Health"],
                    hobbies=["Yoga"],
                    exclusions=["Chemicals"],
                    placements=["Search"]
                )
            ])

        # TC-04: Conflicting Persona Signals
        if brand_name == "ConflictingBrand":
            return PersonaContractList(personas=[
                PersonaContract(
                    persona_id="mock_conflict",
                    name="Confused Buyer",
                    profession="Analyst",
                    age_range="25-34",
                    gender="Male",
                    location="Metro",
                    household_income="High",
                    psychographics={"values": ["Data"], "motivations": ["Accuracy"], "beliefs": ["Verify"]},
                    buying_behavior={
                         "purchase_triggers": ["Extensive research", "Doctor validation", "Peer review"], 
                         "price_sensitivity": "High", 
                         "decision_speed": "Fast" # CONFLICT: Extensive research != Fast
                    },
                    pain_points=["Inaccuracy"],
                    content_consumption=["Whitepapers"],
                    platform_affinity=["Google"], # Fixed Enum
                    preferred_platforms=["LinkedIn"], # This field is free text list usually
                    usp_alignment_reason="Matches",
                    confidence_score=0.85,
                    interests=["Analysis"],
                    hobbies=["Chess"],
                    exclusions=["Hype"],
                    placements=["Feed"]
                )
            ])

        # Default Mock Response (Happy Path)
        return PersonaContractList(personas=[
            PersonaContract(
                persona_id="mock_1",
                name="Mock Persona 1",
                profession="Tester",
                age_range="25-34",
                gender="All",
                location="Global",
                household_income="Medium",
                psychographics={
                    "values": ["Efficiency"], 
                    "motivations": ["Testing"], 
                    "beliefs": ["Code is Law"]
                },
                buying_behavior={
                     "purchase_triggers": ["Need to test"], 
                     "price_sensitivity": "Low", 
                     "decision_speed": "Fast"
                },
                pain_points=["Bugs"],
                content_consumption=["Docs"],
                platform_affinity=["Google"],
                preferred_platforms=["Google Search"],
                usp_alignment_reason="Fits perfectly",
                confidence_score=0.9,
                interests=["Testing"],
                hobbies=["Coding"],
                exclusions=["Fluff"],
                placements=["Search"]
            )
        ])

    # ENGINE A MOCK: Intent Classification
    def classify_intent(self, brand_data: dict):
        self.call_history.append("classify_intent")
        
        brand = brand_data.get("brand_name")
        
        # TC-05: Strategic NA (Nerivio)
        if brand == "Nerivio":
            from src.wrappers.intent_classifier import LockedStrategy
            # Meta Intent Weak -> Google Only
            return LockedStrategy(
                campaign_type="Search (Intent Capture)",
                funnel_depth="FULL",
                allowed_platforms=["Google"] # Meta rejected
            )
            
        # TC-05b: Strategic Rejection (Unknown Brand)
        if brand == "MysteryBox":
             from src.wrappers.intent_classifier import LockedStrategy
             return LockedStrategy(
                 campaign_type="NA",
                 funnel_depth="FULL",
                 allowed_platforms=[]
             )

        # TC-07: Livguard (Fast Decision -> NO_TOF)
        if brand == "Livguard":
            from src.wrappers.intent_classifier import LockedStrategy
            return LockedStrategy(
                campaign_type="Sales (Purchase Focus)",
                funnel_depth="NO_TOF", # Explicitly suppressing Awareness
                allowed_platforms=["Google", "Meta"] # Meta allowed for retargeting, but TOF blocked
            )
            
        # TC-08: Dulux (Slow Decision -> FULL)
        if brand == "Dulux":
            from src.wrappers.intent_classifier import LockedStrategy
            return LockedStrategy(
                campaign_type="Engagement (Post Interaction)", # Or Awareness
                funnel_depth="FULL",
                allowed_platforms=["Meta", "Google"]
            )

        # Default Happy Mock
        from src.wrappers.intent_classifier import LockedStrategy
        return LockedStrategy(
            campaign_type="Sales (Purchase Focus)",
            funnel_depth="FULL",
            allowed_platforms=["Meta", "Google"]
        )

@pytest.fixture
def mock_llm():
    return MockLLMClient()

# --- VALIDATION SERVICE FIXTURE ---
# If tests need the real ValidationService, import it.
# Ideally unit tests shouldn't need a DB, but if Service classes import DB, we might need to mock get_db
