from src.models_portfolio import FinalPersona
from src.models_scoring import ScoredPersona
from src.services_budget_orchestrator import BudgetOrchestrator
import unittest

class TestBudgetEngine(unittest.TestCase):
    
    def setUp(self):
        # Mock save to avoid DB errors with fake IDs
        self.original_save = BudgetOrchestrator.save_plan
        BudgetOrchestrator.save_plan = lambda x: None
        
    def tearDown(self):
        BudgetOrchestrator.save_plan = self.original_save
    
    def create_mock_pair(self, id, score, role, platforms):
        fp = FinalPersona(
            persona_id=id, project_id="p", rank=1, 
            role_in_portfolio=role, funnel_stage="Bottom",
            recommended_platforms=platforms
        )
        # Mock scored persona
        # Need breakdown for strict typing? 
        from src.models_scoring import ScoreBreakdown
        bd = ScoreBreakdown(objective_fit=0, price_fit=0, geography_fit=0, funnel_fit=0, ads_feasibility=0)
        sp = ScoredPersona(
            persona_id=id, project_id="p", total_score=score, 
            score_breakdown=bd 
        )
        return (fp, sp)

    def test_persona_allocation_logic(self):
        # Anchor (1.3x) vs Experiment (0.5x)
        # Score 90 vs 90 -> Anchor should get way more
        p1 = self.create_mock_pair("1", 90, "Anchor", ["Meta"])
        p2 = self.create_mock_pair("2", 90, "Experiment", ["Meta"])
        
        plan = BudgetOrchestrator.generate_budget_plan([p1, p2], 1000.0, "p")
        
        alloc1 = next(a for a in plan.allocations if a.persona_id == "1")
        alloc2 = next(a for a in plan.allocations if a.persona_id == "2")
        
        self.assertGreater(alloc1.total_daily_budget, alloc2.total_daily_budget * 2)

    def test_platform_split(self):
        # User on Meta and Google -> Should split ~60/40 or similar
        p1 = self.create_mock_pair("1", 90, "Anchor", ["Meta", "Google Search"])
        
        plan = BudgetOrchestrator.generate_budget_plan([p1], 1000.0, "p")
        alloc = plan.allocations[0]
        
        self.assertGreater(alloc.meta_budget, 0)
        self.assertGreater(alloc.google_budget, 0)
        # Sum should be total
        self.assertAlmostEqual(alloc.meta_budget + alloc.google_budget, alloc.total_daily_budget, delta=0.1)

    def test_funnel_split(self):
        # Anchor on Meta -> Should have TOF, MOF, BOF
        p1 = self.create_mock_pair("1", 90, "Anchor", ["Meta"])
        
        plan = BudgetOrchestrator.generate_budget_plan([p1], 1000.0, "p")
        splits = plan.funnel_splits["1"]
        
        stages = [s.funnel_stage for s in splits]
        self.assertIn("TOF", stages)
        self.assertIn("MOF", stages)
        self.assertIn("BOF", stages)

if __name__ == '__main__':
    unittest.main()
