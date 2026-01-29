from src.models import Persona, Demographics, Psychographics
from src.models_scoring import ScoredPersona
from src.services_portfolio import PortfolioService
import unittest

class TestPortfolioService(unittest.TestCase):
    
    def create_mock_pair(self, id, score, profession, role="Primary Buyer", habits=None):
        if habits is None: habits = ["Meta"]
        
        p = Persona(
            name=f"P{id}",
            demographics=Demographics(
                age_range="25-30", location="US", 
                profession=profession, income_level="Mid", gender="Any"
            ),
            psychographics=Psychographics(goals=[], beliefs=[], lifestyle=[]),
            motivations=[], pain_points=[], content_consumption=habits, 
            funnel_role=role
        )
        
        # Mock breakdown to pass validation
        from src.models_scoring import ScoreBreakdown
        dummy_bd = ScoreBreakdown(objective_fit=0, price_fit=0, geography_fit=0, funnel_fit=0, ads_feasibility=0)

        sp = ScoredPersona(
            persona_id=id, project_id="proj", total_score=score, 
            score_breakdown=dummy_bd 
        )
        
        return (sp, p)

    def test_diversity_enforcement(self):
        # 3 personas, same profession. only 2 should be selected.
        candidates = [
            self.create_mock_pair("1", 90, "Dev"),
            self.create_mock_pair("2", 85, "Dev"),
            self.create_mock_pair("3", 80, "Dev")
        ]
        
        portfolio = PortfolioService.build_portfolio(candidates, top_n=5)
        self.assertEqual(len(portfolio), 2)
        self.assertEqual(portfolio[0].persona_id, "1")
        self.assertEqual(portfolio[1].persona_id, "2")

    def test_role_assignment(self):
        # 1. Best score -> Anchor
        # 2. Influencer role -> Influencer
        c1 = self.create_mock_pair("1", 95, "CEO")
        c2 = self.create_mock_pair("2", 80, "Blogger", role="Influencer")
        
        portfolio = PortfolioService.build_portfolio([c1, c2])
        
        self.assertEqual(portfolio[0].role_in_portfolio, "Anchor")
        self.assertEqual(portfolio[1].role_in_portfolio, "Influencer")

    def test_platform_mapping(self):
        c1 = self.create_mock_pair("1", 90, "User", habits=["Search", "Reviews"])
        portfolio = PortfolioService.build_portfolio([c1])
        
        self.assertIn("Google Search", portfolio[0].recommended_platforms)
        self.assertNotIn("Meta", portfolio[0].recommended_platforms)

if __name__ == '__main__':
    unittest.main()
