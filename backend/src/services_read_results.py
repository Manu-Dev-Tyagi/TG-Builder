from typing import List, Optional
from src.db import get_db
from src.models_portfolio import FinalPersona
from src.models_campaign import CampaignBlueprint
# from src.models_budget import BudgetPlan # Need schema matching DB storage

class ResultsReadService:
    @staticmethod
    def get_final_personas(project_id: str) -> List[dict]:
        db = get_db()
        # Join with raw_personas to get name and other data
        response = db.table("final_personas").select("*, raw_personas(persona_name, persona_data)").eq("project_id", project_id).execute()
        
        # Flatten the response for frontend convenience
        flattened = []
        for item in response.data:
            raw = item.get("raw_personas", {})
            persona_data = raw.get("persona_data", {})
            
            # Build complete persona object for frontend
            result = {
                # Core fields from final_personas table
                "id": item.get("id"),
                "persona_id": item.get("persona_id"),
                "project_id": item.get("project_id"),
                "rank": item.get("rank"),
                "role_in_portfolio": item.get("role_in_portfolio"),
                "funnel_stage": item.get("funnel_stage"),
                "recommended_platforms": item.get("recommended_platforms", []),
                "campaign_type": item.get("campaign_type"),
                "notes": item.get("notes"),
                "created_at": item.get("created_at"),
                
                # Platform decisions (from FinalPersona model)
                "platform_decisions": item.get("platform_decisions", {}),
                
                # Name from raw_personas
                "name": raw.get("persona_name", "Unnamed Persona"),
                
                # Demographics from stored data
                "location": item.get("location") or persona_data.get("location", ""),
                "age_range": item.get("age_range") or persona_data.get("age_range", ""),
                "gender": item.get("gender") or persona_data.get("gender", ""),
                "profession": item.get("profession") or persona_data.get("profession", ""),
                "household_income": item.get("household_income") or persona_data.get("household_income", ""),
                
                # Behavior data
                "psychographics": item.get("psychographics") or persona_data.get("psychographics", {}),
                "buying_behavior": item.get("buying_behavior") or persona_data.get("buying_behavior", {}),
                "pain_points": item.get("pain_points") or persona_data.get("pain_points", []),
                "interests": item.get("interests") or persona_data.get("interests", []),
                "hobbies": item.get("hobbies") or persona_data.get("hobbies", []),
                
                # Rich Fields extracted from Raw Data (No DB Migration needed)
                "archetype": item.get("archetype") or persona_data.get("archetype", "Persona Archetype"),
                "needs": item.get("needs") or persona_data.get("needs", []),
                "frustrations": item.get("frustrations") or persona_data.get("frustrations", []),
                "value_drivers": item.get("value_drivers") or persona_data.get("value_drivers", []),
                "delights": item.get("delights") or persona_data.get("delights", []),
                "value_drivers": item.get("value_drivers") or persona_data.get("value_drivers", []),
                "delights": item.get("delights") or persona_data.get("delights", []),
                "digital_index": item.get("digital_index") or persona_data.get("digital_index", {}),
                "preferred_platforms": item.get("preferred_platforms") or persona_data.get("preferred_platforms", []),
                "platform_affinity": item.get("platform_affinity") or persona_data.get("platform_affinity", []),

                # Keep full_data for backward compat
                "full_data": persona_data,
            }
            flattened.append(result)
            
        return flattened

    @staticmethod
    def get_campaign_blueprints(project_id: str) -> List[dict]:
        db = get_db()
        response = db.table("targeting_blueprints").select("*").eq("project_id", project_id).execute()
        
        # Filter out budget plans if mixed in same table
        campaigns = [r for r in response.data if r.get("platform") != "BudgetPlan"]
        
        # Schema Adaptation for Frontend (Google expects google_adgroups)
        for c in campaigns:
            if c.get("platform") == "Google":
                c["google_adgroups"] = c.get("targeting_data", [])
                
        return campaigns

    @staticmethod
    def get_budget_plan(project_id: str) -> List[dict]:
        db = get_db()
        response = db.table("targeting_blueprints").select("*").eq("project_id", project_id).eq("platform", "BudgetPlan").execute()
        return response.data or []

    @staticmethod
    def get_locked_strategy(project_id: str) -> dict:
        """
        Reconstructs the immutable 'Engine A' strategy for the Frontend Intent Lock Card.
        """
        db = get_db()
        
        # 1. Get Brand Inputs (for Decision Speed)
        brand_res = db.table("brand_inputs").select("decision_speed, primary_objective").eq("project_id", project_id).single().execute()
        brand_data = brand_res.data or {}
        
        # 2. Get One Final Persona (for Campaign Type & Funnel Depth inference)
        # We assume strategy is uniform across project (Hardware Lock)
        persona_res = db.table("final_personas").select("campaign_type, notes").eq("project_id", project_id).limit(1).execute()
        
        strategy = {
            "campaign_type": "Pending...",
            "decision_speed": brand_data.get("decision_speed", "Normal"),
            "funnel_policy": "FULL_FUNNEL", # Default - Authoritative Backend State
            "status": "LOCKED",
            "notes": ""
        }
        
        if persona_res.data:
            p = persona_res.data[0]
            strategy["campaign_type"] = p.get("campaign_type", "NA")
            strategy["notes"] = p.get("notes", "")
            
            # Deterministic Policy Construction
            # If Fast Decision Speed -> Suppress TOF, UNLESS Objective is Awareness
            obj = brand_data.get("primary_objective", "").lower()
            if "fast" in strategy["decision_speed"].lower() and "awareness" not in obj:
                strategy["funnel_policy"] = "NO_TOF"
            else:
                strategy["funnel_policy"] = "FULL_FUNNEL"
            
            # Check for NA / Rejection
            if strategy["campaign_type"] == "NA":
                strategy["status"] = "NA_REJECTION"
        
        return strategy
