import pytest
from src.services_campaign_meta import MetaCampaignService
from src.wrappers.meta_cluster_builder import MetaClusterWrapper
from src.models_portfolio import FinalPersona
from src.schemas.persona_schema import PersonaContract
from backend.tests.gj_suite.conftest import mock_build_clusters, MockLLMClient

# TC-07: Fast Decision Only (Livguard)
def test_tc07_fast_decision_suppression(monkeypatch):
    """
    Context: Livguard needs 'Fast' replacement.
    Expected: Engine A locks 'NO_TOF'. Engine B (MetaCampaignService) MUST NOT generate TOF adsets.
    """
    
    # 1. Setup Mock
    llm = MockLLMClient()
    mock_persona = PersonaContract(
        persona_id="p1", name="Fast Buyer", profession="Driver",
        age_range="25-34", gender="All", location="Metro", household_income="Low",
        psychographics={"values":[], "motivations":[], "beliefs":[]},
        buying_behavior={"purchase_triggers":[], "price_sensitivity":"Low", "decision_speed":"Fast"},
        pain_points=[], content_consumption=[], platform_affinity=["Meta"],
        preferred_platforms=["Facebook"], usp_alignment_reason=".",
        interests=["Speed"], hobbies=["Driving"], exclusions=["Slow"], placements=["Feed"], confidence_score=0.9
    )
    final_p = FinalPersona(
        persona_id="p1", name="Fast Buyer", rationale=".", role_in_portfolio="Anchor",
        funnel_stage="Bottom", recommended_platforms=["Meta"], rank=1, project_id="mock_proj",
        location="Metro", age_range="25-34", gender="All", profession="Driver", household_income="Low",
        psychographics={}, buying_behavior={}, pain_points=[], interests=[], hobbies=[]
    )
    
    # 2. Monkeypatch the Cluster Builder to return TOF/MOF/BOF
    monkeypatch.setattr(MetaClusterWrapper, "build_clusters", mock_build_clusters)
    
    # 3. Execution: Call Service with funnel_depth="NO_TOF"
    # This simulates the Orchestrator passing down the LockedStrategy from TC-05/06 logic
    adsets = MetaCampaignService.generate_adsets(
        final_persona=final_p, 
        contract=mock_persona, 
        llm=llm, 
        brand_usp="Fast Power", 
        funnel_depth="NO_TOF"  # <--- CRITICAL INPUT
    )
    
    # 4. Assertions
    stages = [a.funnel_stage for a in adsets]
    print(f"\nGenerated Stages: {stages}")
    
    assert "TOF" not in stages, "TOF Adset should have been suppressed for Fast Decision speed"
    assert "MOF" in stages
    assert "BOF" in stages
    print("✅ TC-07 Passed: TOF Suppressed.")

# TC-08: Slow Decision (Dulux)
def test_tc08_slow_decision_full_funnel(monkeypatch):
    """
    Context: Dulux (Slow Consideration).
    Expected: Engine A locks 'FULL'. Engine B generates ALL stages.
    """
    llm = MockLLMClient()
    mock_persona = PersonaContract(
        persona_id="p2", name="Slow Buyer", profession="Painter",
        age_range="25-34", gender="All", location="Metro", household_income="Low",
        psychographics={"values":[], "motivations":[], "beliefs":[]},
        buying_behavior={"purchase_triggers":[], "price_sensitivity":"Low", "decision_speed":"Slow"},
        pain_points=[], content_consumption=[], platform_affinity=["Meta"],
        preferred_platforms=["Facebook"], usp_alignment_reason=".",
        interests=["Paint"], hobbies=["Art"], exclusions=["Cheap"], placements=["Feed"], confidence_score=0.9
    )
    final_p = FinalPersona(
        persona_id="p2", name="Slow Buyer", rationale=".", role_in_portfolio="Anchor",
        funnel_stage="Bottom", recommended_platforms=["Meta"], rank=1, project_id="mock_proj",
        location="Metro", age_range="25-34", gender="All", profession="Painter", household_income="Low",
        psychographics={}, buying_behavior={}, pain_points=[], interests=[], hobbies=[]
    )
    
    monkeypatch.setattr(MetaClusterWrapper, "build_clusters", mock_build_clusters)
    
    adsets = MetaCampaignService.generate_adsets(
        final_persona=final_p, 
        contract=mock_persona, 
        llm=llm, 
        brand_usp="Premium Paint", 
        funnel_depth="FULL" # <--- NORMAL INPUT
    )
    
    stages = [a.funnel_stage for a in adsets]
    print(f"\nGenerated Stages: {stages}")
    
    assert len(adsets) == 3
    assert "TOF" in stages
    assert "MOF" in stages
    assert "BOF" in stages
    print("✅ TC-08 Passed: Full Funnel Generated.")
