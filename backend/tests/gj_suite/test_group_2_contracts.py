import pytest
from src.services_validation import ValidationService

# TC-03: Persona Without Buying Trigger
def test_tc03_persona_missing_trigger(mock_llm):
    """
    Context: Awareness-heavy industries (Daily Bloom IBS).
    Expected: Persona discarded at Contract Gate
    """
    # 1. Generate via Mock
    result = mock_llm.generate_personas(
        brand_name="Daily Bloom IBS", 
        product_category="Health", 
        price_positioning="Mid", 
        primary_usp="Relief", 
        primary_objective="Awareness"
    )
    persona = result.personas[0]
    
    # 2. Assert Generation happened as expected (Bad Mock)
    assert len(persona.buying_behavior.purchase_triggers) == 0
    
    # 3. Test Validation Service
    is_valid = ValidationService.validate_schema(persona)
    
    # 4. Expect Rejection
    print(f"\nTC-03 Validation Result: {is_valid}")
    assert is_valid is False, "Persona with empty buying triggers should fail schema validation"
    print("✅ TC-03 Passed: Empty Buying Triggers rejected.")


# TC-04: Conflicting Persona Signals
def test_tc04_conflicting_signals(mock_llm):
    """
    Context: Conflicting Personas (Fast Speed vs 'Extensive Research')
    Expected: Persona rejected by Logical Consistency Check
    """
    # 1. Generate via Mock
    result = mock_llm.generate_personas(
        brand_name="ConflictingBrand",
        product_category="Tech",
        price_positioning="High",
        primary_usp="Precision",
        primary_objective="Sales"
    )
    persona = result.personas[0]
    
    # 2. Assert Conflict exists in data
    assert persona.buying_behavior.decision_speed == "Fast"
    assert "Extensive research" in persona.buying_behavior.purchase_triggers
    
    # 3. Test Validation Logic
    is_logically_valid = ValidationService.check_logical_consistency(persona)
    
    # 4. Expect Rejection
    print(f"\nTC-04 Validation Result: {is_logically_valid}")
    assert is_logically_valid is False, "Persona with 'Fast' speed but 'Extensive Research' trigger should be rejected"
    print("✅ TC-04 Passed: Conflicting signals detected.")
