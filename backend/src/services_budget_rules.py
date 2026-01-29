from typing import List
from src.models_budget import ScalingRule

class BudgetRuleService:
    @staticmethod
    def generate_rules() -> List[ScalingRule]:
        """
        Returns standard production rules for scaling and killing.
        In future, this could be dynamic based on user risk profile.
        """
        return [
            ScalingRule(
                name="Scale Up Winner",
                condition="CPA < Target AND Spend > 3x Daily Budget",
                action="Increase Budget 20%",
                trigger_type="Scale Up"
            ),
             ScalingRule(
                name="Kill Loser",
                condition="Spend > 5x Target CPA AND Conversions = 0",
                action="Pause Adset",
                trigger_type="Kill"
            ),
            ScalingRule(
                name="Hold Steady",
                condition="CPA within 10% of Target",
                action="No Action",
                trigger_type="Hold"
            )
        ]
