from src.models import Persona, Demographics, Psychographics
from src.models_portfolio import FinalPersona
from src.services_campaign_meta import MetaCampaignService
# from src.services_campaign_google import GoogleCampaignService # LLM involved, might mock
import unittest

class TestCampaignPhase(unittest.TestCase):
    
    def create_mock_pair(self, name, id, role="Anchor", habits=None):
        if habits is None: habits = ["Meta", "Instagram"]
        
        p = Persona(
            name=name,
            demographics=Demographics(
                age_range="25-30", location="US", 
                profession="Dev", income_level="Mid", gender="Any"
            ),
            psychographics=Psychographics(goals=[], beliefs=[], lifestyle=[]),
            motivations=["Growth", "Efficiency"], 
            pain_points=["Time"], 
            content_consumption=habits, 
            funnel_role="Primary Buyer"
        )
        
        fp = FinalPersona(
            persona_id=id, project_id="p", rank=1, 
            role_in_portfolio=role, funnel_stage="Bottom",
            recommended_platforms=habits
        )
        
        return (fp, p)

    def test_meta_structure(self):
        fp, p = self.create_mock_pair("TestUser", "1", role="Anchor")
        
        adsets = MetaCampaignService.generate_adsets(fp, p)
        
        # Expecting at least MOF (Interest) and TOF (Broad for Anchor)
        self.assertTrue(len(adsets) >= 2)
        
        types = [a.targeting_type for a in adsets]
        self.assertIn("Interest Stack", types)
        self.assertIn("Broad", types)
        
        # Check Interest Stack content
        mof = next(a for a in adsets if a.targeting_type == "Interest Stack")
        self.assertIn("Growth", mof.interests)

    def test_meta_skip_if_not_platform(self):
        # Only LinkedIn user
        fp, p = self.create_mock_pair("B2BUser", "2", habits=["LinkedIn"])
        
        adsets = MetaCampaignService.generate_adsets(fp, p)
        self.assertEqual(len(adsets), 0)

if __name__ == '__main__':
    unittest.main()
