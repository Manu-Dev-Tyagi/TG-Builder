import pytest
from pydantic import ValidationError
from src.models import BrandInputCreate
from src.services import InputService
from backend.tests.gj_suite.fixtures import AMPERE_BAD_INPUT, LIVGUARD_URGENT_INPUT

# TC-01: Invalid Objective Rejection
def test_tc01_invalid_objective_rejection(mock_llm):
    """
    Context: Junior marketer enters vague goal (very common in agencies).
    Expected: Hard reject at InputService / Pydantic Model.
    LLM is never called.
    """
    print(f"\nTesting Input: {AMPERE_BAD_INPUT}")
    
    with pytest.raises(ValidationError) as excinfo:
        # Action: Try to instantiate the model with bad input
        BrandInputCreate(**AMPERE_BAD_INPUT)

    # Assertion: Check error message
    error_msg = str(excinfo.value)
    print(f"Caught Expected Error: {error_msg}")
    
    # Check specifically for the enum error
    assert "Invalid objective" in error_msg
    assert "Sales" in error_msg and "Leads" in error_msg
    
    # Assertion: LLM never called (Mock Verification)
    assert len(mock_llm.call_history) == 0
    print("✅ TC-01 Passed: Enum Gates Logic verified.")

# TC-02: Silent Inference Prevention
def test_tc02_silent_inference_prevention():
    """
    Context: Missing mandatory field (price_sensitivity in this case).
    Expected: Reject with Missing Field error.
    """
    # Create input missing price_sensitivity
    BAD_INPUT = LIVGUARD_URGENT_INPUT.copy()
    del BAD_INPUT["price_sensitivity"]
    
    print(f"\nTesting Missing Field Input: {BAD_INPUT}")

    with pytest.raises(ValidationError) as excinfo:
        BrandInputCreate(**BAD_INPUT)
        
    error_msg = str(excinfo.value)
    print(f"Caught Expected Error: {error_msg}")
    
    assert "Field required" in error_msg or "price_sensitivity" in error_msg
    print("✅ TC-02 Passed: Mandatory Field check verified.")
