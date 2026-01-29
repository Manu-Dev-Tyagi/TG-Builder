from typing import List, Tuple
from src.models_portfolio import FinalPersona
from src.models_scoring import ScoredPersona
from src.models_budget import BudgetPlan
from src.services_budget_persona import PersonaBudgetService
from src.services_budget_platform import PlatformBudgetService
from src.services_budget_funnel import FunnelBudgetService
from src.services_budget_rules import BudgetRuleService
from datetime import datetime
from src.db import get_db
from src.llm import LLMClient
from src.config import Config
from src.wrappers.budget_reasoning_wrapper import BudgetReasoningWrapper

class BudgetOrchestrator:
    @staticmethod
    def generate_budget_plan(
        personas: List[tuple[FinalPersona, ScoredPersona]], 
        total_budget: float, 
        project_id: str
    ) -> BudgetPlan:
        """
        Orchestrates the entire budget planning process.
        """
        # 1. Persona Level
        persona_allocs = PersonaBudgetService.allocate_persona_budgets(personas, total_budget)
        
        # 2. Platform Level (Meta vs Google)
        # Need list of FinalPersonas for trait lookup
        final_p_list = [p[0] for p in personas]
        platform_allocs = PlatformBudgetService.split_by_platform(persona_allocs, final_p_list)
        
        # 3. Funnel Level (Adset/AdGroup splits)
        funnel_splits = FunnelBudgetService.split_by_funnel(platform_allocs, final_p_list)
        
        # 4. Rules
        rules = BudgetRuleService.generate_rules()
        
        # 5. Reasoning (Growth Jockey Logic)
        llm = LLMClient(provider=Config.DEFAULT_PROVIDER, model_name=Config.LIGHT_MODEL)
        brand_raw = get_db().table("brand_inputs").select("*").eq("project_id", project_id).single().execute()
        brand_data = brand_raw.data or {}
        
        # Summary for LLM
        summary = f"Total: {total_budget}, Meta: {sum(a.meta_budget for a in platform_allocs)}, Google: {sum(a.google_budget for a in platform_allocs)}"
        rationale = BudgetReasoningWrapper.explain(llm, brand_data, summary)

        plan = BudgetPlan(
            project_id=project_id,
            total_budget=total_budget,
            allocations=platform_allocs,
            funnel_splits=funnel_splits,
            rules=rules,
            rationale=rationale
        )
        
        # 6. Save
        BudgetOrchestrator.save_plan(plan)
        
        return plan

    @staticmethod
    def save_plan(plan: BudgetPlan):
        db = get_db()
        records = []
        
        for alloc in plan.allocations:
            splits = plan.funnel_splits.get(alloc.persona_id, [])
            records.append({
                "project_id": plan.project_id,
                # "persona_id": alloc.persona_id, # Optional if table supports it
                "platform": "Mixed",
                "daily_budget": alloc.total_daily_budget,
                "funnel": "Mixed",
                "rules": [r.model_dump() for r in plan.rules],
                # "allocation_data": alloc.model_dump(), # Store full detail
                # "split_data": [s.model_dump() for s in splits],
                "created_at": datetime.now().isoformat()
            })
            
        # Using 'campaign_blueprints' or 'targeting_blueprints' table might be wrong place
        # Ideally we need a 'budget_plans' table. 
        # For MVP, we will assume we append to 'targeting_blueprints' with platform='Budget' for storage
        # or just logging it.
        # Let's map to existing 'targeting_blueprints' table but abuse the 'targeting_data' jsonb column.
        
        to_insert = []
        for alloc in plan.allocations:
            splits = plan.funnel_splits.get(alloc.persona_id, [])
            to_insert.append({
                "project_id": plan.project_id,
                "persona_id": alloc.persona_id,
                "platform": "BudgetPlan",
                "funnel_stage": "All",
                "targeting_data": {
                    "total": alloc.total_daily_budget,
                    "meta": alloc.meta_budget,
                    "google": alloc.google_budget,
                    "splits": [s.model_dump() for s in splits],
                    "rules": [r.model_dump() for r in plan.rules],
                    "rationale": plan.rationale
                },
                "created_at": datetime.now().isoformat()
            })
            
        if to_insert:
            db.table("targeting_blueprints").insert(to_insert).execute()
