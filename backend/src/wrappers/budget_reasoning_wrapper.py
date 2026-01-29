from langchain_core.prompts import ChatPromptTemplate
from src.llm import LLMClient
from typing import List, Dict, Any

REASONING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Performance Marketing Strategist. 
Your task is to justify a budget split between Meta (Demand Generation) and Google (Demand Capture) using specific mechanics.

STRATEGIC RULES:
1. DECISION SPEED: If 'Fast', justify high Meta TOF/MOF spend for impulse discovery. If 'Slow', justify high Google BOF and Retargeting spend for high-consideration research.
2. OBJECTIVE: If 'Sales', explain the budget as 'Demand Conversion'. If 'Leads', explain it as 'Pipeline Building'.
3. RISK PROFILE: Define 'Slow Speed + Sales Objective' as High Risk (requires more nurturing) and 'Fast Speed + Leads' as Low Risk (high efficiency).
4. DATA ANCHOR: Use words like 'Behavioral Targeting', 'Intent Capture', and 'Life Event Triggers' from our framework.

TASK:
Write exactly 3-4 professional sentences. Mention the specific Rs. allocation logic.
Return ONLY the plain text. No fluff.
"""),
    ("user", "Explain this budget: Brand: {brand_name}, Category: {category}, Objective: {objective}, Speed: {speed}, Allocations: {allocations}")
])

class BudgetReasoningWrapper:
    @staticmethod
    def explain(llm_client: LLMClient, brand_data: Dict[str, Any], plan_summary: str) -> str:
        # Replicating the trained behavior: mapping specific inputs to strategic outputs
        chain = REASONING_PROMPT | llm_client.llm
        try:
            result = chain.invoke({
                "brand_name": brand_data.get("brand_name", "the brand"),
                "category": brand_data.get("product_category", "the category"),
                "objective": brand_data.get("primary_objective", "Sales"),
                "speed": brand_data.get("decision_speed", "Normal"),
                "allocations": plan_summary
            })
            return result.content.strip()
        except Exception as e:
            # Fallback that still maintains the professional tone
            return f"Strategic Rs. allocation optimized for a {brand_data.get('decision_speed')} purchase cycle to achieve {brand_data.get('primary_objective')}."
