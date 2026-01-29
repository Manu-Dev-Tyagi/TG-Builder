from src.models import Persona, Demographics, Psychographics, BrandInputCreate
from src.services_scoring import ScoringService
from src.services_storage import ScoringStorageService
from src.models_scoring import ScoredPersona
from src.services_persona import PersonaService
from src.services import ProjectService, InputService
from src.config import Config
import unittest
from unittest.mock import MagicMock

class TestScoringEngine(unittest.TestCase):
    
    def setUp(self):
        # Mock Brand Input
        self.brand_input = BrandInputCreate(
            brand_name="LuxCar",
            product_category="Luxury Cars",
            price_positioning="Premium",
            geography="USA",
            primary_usp="Status",
            primary_objective="Purchase"
        )
        
    def create_persona(self, income="High", role="Primary Buyer", loc="USA", motivation="Status"):
        return Persona(
            name="Test",
            demographics=Demographics(
                age_range="30-40",
                gender="Any",
                location=loc,
                profession="CEO",
                income_level=income
            ),
            psychographics=Psychographics(goals=[], beliefs=[], lifestyle=[]),
            motivations=[motivation],
            pain_points=[],
            content_consumption=["Google", "Meta"],
            funnel_role=role
        )

    def test_high_score_match(self):
        # Perfect match
        p = self.create_persona(income="High", role="Primary Buyer", loc="USA")
        scored = ScoringService.calculate_score(p, self.brand_input, "123", "proj_1")
        
        # Expect high score (> 80)
        self.assertGreater(scored.total_score, 80)
        
    def test_low_score_mismatch(self):
        # Mismatch: Low income for Premium product
        p = self.create_persona(income="Low", role="Researcher", loc="India")
        scored = ScoringService.calculate_score(p, self.brand_input, "124", "proj_1")
        
        # Expect lower score (Penalty for price and geo)
        self.assertLess(scored.total_score, 70)

    def test_ranking(self):
        # Correctly instantiating objects for the test to avoid Model validation errors
        from src.models_scoring import ScoreBreakdown
        
        dummy_bd = ScoreBreakdown(objective_fit=0, price_fit=0, geography_fit=0, funnel_fit=0, ads_feasibility=0)

        p1 = ScoredPersona(persona_id="1", total_score=90, score_breakdown=dummy_bd, project_id="p")
        p2 = ScoredPersona(persona_id="2", total_score=95, score_breakdown=dummy_bd, project_id="p")
        
        ranked = ScoringService.rank_personas([p1, p2])
        self.assertEqual(ranked[0].persona_id, "2")
        self.assertEqual(ranked[0].rank, 1)

if __name__ == '__main__':
    unittest.main()
