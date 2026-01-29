from typing import List, Optional
from src.schemas.persona_schema import PersonaContract
import hashlib
import re

class ValidationService:
    @staticmethod
    def validate_schema(persona: PersonaContract) -> bool:
        """
        Hard schema validation. Checks required fields and non-empty values.
        """
        if not persona.name or not persona.name.strip():
            return False
            
        if not persona.age_range or not persona.location:
             return False
             
        if not persona.profession:
            return False
            
        # Check Buying Behavior
        if not persona.buying_behavior.purchase_triggers:
            return False
            
        # Check Lists
        if not persona.pain_points or not persona.digital_index.content_consumption:
            return False
            
        return True

    @staticmethod
    def normalize_fields(persona: PersonaContract) -> PersonaContract:
        """
        Normalizes Age and other fields.
        """
        persona.age_range = persona.age_range.replace(" to ", "-").strip()
        return persona

    @staticmethod
    def check_logical_consistency(persona: PersonaContract) -> bool:
        """
        Hard business rules. Returns False if invalid.
        """
        age_str = persona.age_range
        min_age = 0
        try:
             nums = re.findall(r'\d+', age_str)
             if nums:
                 min_age = int(nums[0])
        except:
            pass

        income = persona.household_income.lower()
        profession = persona.profession.lower()

        # Rule: Age < 18 AND Income = High
        if min_age > 0 and min_age < 18 and "high" in income:
            return False
            
        if "student" in profession and "high" in income:
            return False
            
        # Rule: Fast Decision vs High Friction Triggers (TC-04)
        decision_speed = persona.buying_behavior.decision_speed.lower()
        if "fast" in decision_speed:
            high_friction_keywords = ["extensive research", "doctor validation", "clinical trials", "peer review"]
            triggers = [t.lower() for t in persona.buying_behavior.purchase_triggers]
            
            for keyword in high_friction_keywords:
                if any(keyword in t for t in triggers):
                    return False
            
        return True

    @staticmethod
    def is_duplicate(persona: PersonaContract, existing_personas: List[PersonaContract]) -> bool:
        """
        Checks for duplicates using a content fingerprint.
        """
        def get_fingerprint(p: PersonaContract):
            components = [
                p.age_range.lower(),
                p.profession.lower(),
                "".join(sorted([pp.lower() for pp in p.pain_points]))
            ]
            content = "|".join(components)
            return hashlib.md5(content.encode()).hexdigest()

        current_fp = get_fingerprint(persona)
        
        for existing in existing_personas:
            if get_fingerprint(existing) == current_fp:
                return True
                
        return False
