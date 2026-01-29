import pytest
from src.wrappers.meta_cluster_builder import MetaClusterWrapper, InterestCluster, MetaClusterList, ExclusionCluster
from unittest.mock import MagicMock
from src.llm import LLMClient
from langchain_core.runnables import RunnableLambda

def test_tc09_overlap_logic_run(capsys):
    """
    Context: LLM outputs TOF interests that bleed into MOF (e.g., 'Yoga' in both).
    Expected: Wrapper detects overlap, prints CRITICAL warning, and Prunes the MOF duplicate.
    """
    
    # Construct a runnable that returns our JSON
    overlap_json = """
    {
        "clusters": [
            { "funnel_stage": "TOF", "cluster_name": "A", "interests": ["Yoga", "Run"], "exclusions": {"interests":[], "behaviors":[]}, "reasoning": "R" },
            { "funnel_stage": "MOF", "cluster_name": "B", "interests": ["Yoga", "Gym"], "exclusions": {"interests":[], "behaviors":[]}, "reasoning": "R" },
            { "funnel_stage": "BOF", "cluster_name": "C", "interests": ["Buy"], "exclusions": {"interests":[], "behaviors":[]}, "reasoning": "R" }
        ]
    }
    """
    
    def fake_invoke(input):
        return MagicMock(content=overlap_json)
        
    fake_chain = RunnableLambda(fake_invoke)
    
    # Apply Patch to the PROMPT itself to intercept the '|' operator
    class MockPrompt:
         def __or__(self, other):
             return fake_chain
             
    import src.wrappers.meta_cluster_builder
    # Store original to restore after test (good practice)
    original_prompt = src.wrappers.meta_cluster_builder.META_CLUSTER_PROMPT
    src.wrappers.meta_cluster_builder.META_CLUSTER_PROMPT = MockPrompt()
    
    try:
        # Run
        llm = MagicMock() # irrelevant now
        clusters = MetaClusterWrapper.build_clusters(llm, {}, "")
        
        # Assert
        # Expect TOF to keep Yoga, MOF to lose Yoga
        tof = clusters[0]
        mof = clusters[1]
        
        print(f"\nTOF Interests: {tof.interests}")
        print(f"MOF Interests: {mof.interests}")
        
        assert "Yoga" in tof.interests, "TOF should keep strict interest"
        assert "Yoga" not in mof.interests, "MOF should be pruned of overlapping interest"
        assert "Gym" in mof.interests, "MOF should keep unique interest"
        print("✅ TC-09 Passed: Overlap Pruned (Yoga removed from MOF).")
        
    finally:
        # Restore
        src.wrappers.meta_cluster_builder.META_CLUSTER_PROMPT = original_prompt
