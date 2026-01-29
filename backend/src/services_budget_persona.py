from typing import List, Dict
from src.models_portfolio import FinalPersona
from src.models_scoring import ScoredPersona
from src.models_budget import BudgetAllocation

class PersonaBudgetService:
    ROLE_MULTIPLIERS = {
        "Anchor": 1.3,
        "Expansion": 1.1,
        "Influencer": 0.9,
        "Retention": 1.0, # Default for safety
        "Experiment": 0.5
    }

    @staticmethod
    def allocate_persona_budgets(personas: List[tuple[FinalPersona, ScoredPersona]], total_budget: float) -> List[BudgetAllocation]:
        """
        Splits global budget across personas based on score and portfolio role.
        """
        combined_scores = 0.0
        details = []

        # 1. Calculate Weighted Scores
        for final_p, scored_p in personas:
            multiplier = PersonaBudgetService.ROLE_MULTIPLIERS.get(final_p.role_in_portfolio, 1.0)
            # Use score * multiplier as the "weight"
            weight = scored_p.total_score * multiplier
            combined_scores += weight
            details.append({
                "final_p": final_p,
                "weight": weight
            })
            
        allocations = []
        
        # 2. Assign Budget
        for item in details:
            final_p = item["final_p"]
            weight = item["weight"]
            
            # Basic share
            share = weight / combined_scores if combined_scores > 0 else 0
            allocated_amount = share * total_budget
            
            # Guardrail: Experiment Cap (Global rule check usually happens before or requires 2 passes. 
            # Simplified: If Experiment and share > 15%, cap it. (Logic omitted for brevity in MVP)
            
            allocations.append(BudgetAllocation(
                persona_id=final_p.persona_id,
                project_id=final_p.project_id,
                total_daily_budget=round(allocated_amount, 2),
                meta_budget=0, # Filled in next step
                google_budget=0 # Filled in next step
            ))
            
        return allocations
