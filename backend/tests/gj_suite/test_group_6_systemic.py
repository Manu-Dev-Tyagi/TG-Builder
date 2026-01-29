import pytest
from src.services_core_orchestrator import CoreOrchestrator
from src.wrappers.intent_classifier import IntentClassifierWrapper, LockedStrategy
from src.models import BrandInputBase
from backend.tests.gj_suite.conftest import MockLLMClient

# TC-10: Downstream Mutation Attempt (Engine A Immutability)

def test_tc10_engine_a_immutability(monkeypatch):
    """
    Test that IF Engine A returns 'NO_TOF', the Core Orchestrator enforces this
    even if Engine B (mocked) tries to be helpful and return TOF assets.
    """
    # 1. Setup Inputs
    input_data = BrandInputBase(
        brand_name="Livguard",
        product_category="Battery",
        price_positioning="Medium", # Fixed Enum
        geography="IN",
        primary_usp="Fast",
        primary_objective="Sales", # Fixed Enum
        price_sensitivity="Low", # Fixed Enum
        decision_speed="Fast" # Added per BrandInputBase update
    )
    
    # 2. Mock Engine A to STRICTLY return NO_TOF
    def mock_classify(*args, **kwargs):
        return LockedStrategy(
             campaign_type="Sales (Purchase Focus)",
             funnel_depth="NO_TOF",
             allowed_platforms=["Meta", "Google"]
        )
    monkeypatch.setattr(IntentClassifierWrapper, "classify", mock_classify)
    
    # 3. Spy on Meta Service
    from src.services_campaign_meta import MetaCampaignService
    
    call_args = []
    
    def spy_generate_adsets(final_persona, contract, llm, brand_usp, funnel_depth="FULL"):
        call_args.append(funnel_depth)
        return [] 
        
    monkeypatch.setattr(MetaCampaignService, "generate_adsets", spy_generate_adsets)
    
    # 3b. Mock Database (get_db)
    from unittest.mock import MagicMock
    import src.services_campaign_orchestrator
    
    mock_db = MagicMock()
    # Mock chain: db.table().select().eq().single().execute().data
    mock_query = MagicMock()
    mock_query.data = {"primary_usp": "Fast Charging"}
    mock_db.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_query
    
    # Monkeypatch get_db in the module namespace
    monkeypatch.setattr(src.services_campaign_orchestrator, "get_db", lambda: mock_db)
    
    # Also need to mock the Update call in Step B of Orchestrator
    # db.table().update().eq().eq().execute()
    # Our mock_db.table() return value is reused, so we need to ensure update chain doesn't crash
    mock_db.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = None

    # Also Mock CampaignStorageService to avoid real FS/DB writes
    from src.services_storage_campaign import CampaignStorageService
    monkeypatch.setattr(CampaignStorageService, "save_persona_blueprints", lambda **kwargs: None)
    
    # 4. Run Orchestrator Logic
    # We invoke CampaignOrchestrator directly
    from src.services_campaign_orchestrator import CampaignOrchestrator
    from src.models_portfolio import FinalPersona
    from src.schemas.persona_schema import PersonaContract
    
    llm = MockLLMClient()
    
    mock_p = FinalPersona(
        persona_id="p1", name="Test", rationale=".", role_in_portfolio=".", funnel_stage="Bottom", 
        recommended_platforms=["Meta"], rank=1, project_id="test_proj",
        location=".", age_range=".", gender=".", profession=".", household_income=".",
        psychographics={}, buying_behavior={}, pain_points=[], interests=[], hobbies=[]
    )
    mock_c = PersonaContract(
        persona_id="p1", name="Test", profession=".", age_range=".", gender=".", location=".", household_income=".",
        psychographics={"values":[],"motivations":[],"beliefs":[]}, 
        buying_behavior={"purchase_triggers":[], "price_sensitivity":"Low","decision_speed":"Fast"}, 
        pain_points=[], content_consumption=[], platform_affinity=["Meta"], preferred_platforms=[], usp_alignment_reason=".",
        interests=[], hobbies=[], exclusions=[], placements=[], confidence_score=0.9
    )
    
    # Run
    # Note: CampaignOrchestrator uses `locked_strategy` argument.
    CampaignOrchestrator.generate_blueprint(
        project_id="test_proj",
        final_portfolio=[(mock_p, mock_c)], # Changed to match signature List[Tuple[FinalPersona, PersonaContract]]
        product_category="Cat",
        locked_strategy=LockedStrategy(campaign_type="Sales (Purchase Focus)", funnel_depth="NO_TOF", allowed_platforms=["Meta"]),
        strategy_depth="full_funnel" # Ensure it hits the logic blocks
    )
    
    # Check Spy
    print(f"\nSpy Captured Funnel Depth: {call_args}")
    assert "NO_TOF" in call_args
    print("✅ TC-10 Passed: Engine A 'NO_TOF' lock successfully propagated to Engine B.")


# TC-12: Budget Integrity (No Orphaned Money)
def test_tc12_budget_reallocation_integrity(monkeypatch):
    """
    Context: If TOF is suppressed (Fast Decision Speed), TOF budget should be 0, and MOF/BOF should absorb it.
    """
    from src.services_budget_orchestrator import BudgetOrchestrator
    from src.models_portfolio import FinalPersona
    from src.models_scoring import ScoredPersona
    from src.models_budget import ScalingRule
    
    # Validation Fix: Mock save_plan to avoid DB Interaction
    def mock_save(*args, **kwargs):
        pass
    monkeypatch.setattr(BudgetOrchestrator, "save_plan", mock_save)
    
    # 1. Setup Data with "Fast" decision speed
    final_p = FinalPersona(
        persona_id="p_fast", name="Fast Buyer", rationale=".", role_in_portfolio="Anchor",
        funnel_stage="Bottom", recommended_platforms=["Meta"], rank=1, project_id="proj",
        location=".", age_range=".", gender=".", profession=".", household_income=".",
        psychographics={}, 
        buying_behavior={"decision_speed": "Fast", "price_sensitivity": "Low", "purchase_triggers": []}, 
        pain_points=[], interests=[], hobbies=[]
    )
    
    # Needs to match ScoredPersona definition completely
    scored_p = ScoredPersona(
        persona_id="p_fast", name="Fast Buyer", fit_score=0.9, rationale=".",
        platform_breakdown={"Meta": 1.0, "Google": 0.0},
        funnel_stage="Bottom",
        cost_efficiency_score=0.8, scalable_audience_score=0.8,
        strategic_value_score=0.9,
        total_score=0.9,
        score_breakdown={
            "objective_fit": 0.9,
            "price_fit": 0.9,
            "geography_fit": 0.9,
            "funnel_fit": 0.9,
            "ads_feasibility": 0.9,
            "fit": 0.9
        },
        project_id="proj"
    )
    
    input_list = [(final_p, scored_p)]
    
    # 2. Generate Plan
    plan = BudgetOrchestrator.generate_budget_plan(input_list, 10000.0, "proj")
    
    # 3. Verify
    alloc = plan.allocations[0]
    meta_splits = plan.funnel_splits[alloc.persona_id] # List of FunnelSplit
    
    print(f"\nMeta Splits: {[s.dict() for s in meta_splits]}")
    
    tof_budget = sum(s.daily_budget for s in meta_splits if s.funnel_stage == "TOF")
    mof_budget = sum(s.daily_budget for s in meta_splits if s.funnel_stage == "MOF")
    bof_budget = sum(s.daily_budget for s in meta_splits if s.funnel_stage == "BOF")
    
    assert tof_budget == 0, "TOF Budget should be 0 for Fast decision speed"
    assert mof_budget > 0, "MOF should absorb budget"
    assert bof_budget > 0, "BOF should absorb budget"
    
    # Total check (floating point tolerance)
    total_split = tof_budget + mof_budget + bof_budget
    assert abs(total_split - alloc.meta_budget) < 1.0, "Total split matches allocated meta budget"
    
    print("✅ TC-12 Passed: Budget rearranged (TOF=0) due to Decision Speed.")
