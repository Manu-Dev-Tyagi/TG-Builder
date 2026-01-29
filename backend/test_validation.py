from src.models import Persona, Demographics, Psychographics, PersonaList
from src.services_validation import ValidationService
import unittest

class TestValidationService(unittest.TestCase):
    
    def create_base_persona(self):
        return Persona(
            name="Test User",
            demographics=Demographics(
                age_range="25-34",
                gender="Female",
                location="Tier-1 Cities",
                profession="Software Engineer",
                income_level="High"
            ),
            psychographics=Psychographics(
                goals=["Career"],
                beliefs=["Work Hard"],
                lifestyle=["Urban"]
            ),
            motivations=["Growth"],
            pain_points=["Time"],
            content_consumption=["LinkedIn"],
            funnel_role="Primary Buyer"
        )

    def test_schema_valid(self):
        p = self.create_base_persona()
        self.assertTrue(ValidationService.validate_schema(p))

    def test_schema_invalid_empty_field(self):
        p = self.create_base_persona()
        p.motivations = [] # Empty list should fail
        self.assertFalse(ValidationService.validate_schema(p))

    def test_normalization_funnel_role(self):
        p = self.create_base_persona()
        p.funnel_role = "Active Researcher" # Should map to Researcher
        ValidationService.normalize_fields(p)
        self.assertEqual(p.funnel_role, "Researcher")

    def test_normalization_age(self):
        p = self.create_base_persona()
        p.demographics.age_range = "25 to 35"
        ValidationService.normalize_fields(p)
        self.assertEqual(p.demographics.age_range, "25-35")

    def test_logical_consistency_pass(self):
        p = self.create_base_persona()
        self.assertTrue(ValidationService.check_logical_consistency(p))

    def test_logical_consistency_fail_retired_young(self):
        p = self.create_base_persona()
        p.demographics.profession = "Retired"
        p.demographics.age_range = "25-30"
        self.assertFalse(ValidationService.check_logical_consistency(p))

    def test_logical_consistency_fail_tier1_rural(self):
        p = self.create_base_persona()
        p.demographics.location = "Tier-1 Cities"
        p.psychographics.lifestyle = ["Rural", "Simple"]
        self.assertFalse(ValidationService.check_logical_consistency(p))

    def test_duplicate_detection(self):
        p1 = self.create_base_persona()
        p2 = self.create_base_persona() # Identical
        
        existing = [p1]
        self.assertTrue(ValidationService.is_duplicate(p2, existing))
        
        p3 = self.create_base_persona()
        p3.demographics.profession = "Doctor" # Changed
        self.assertFalse(ValidationService.is_duplicate(p3, existing))

if __name__ == '__main__':
    unittest.main()
