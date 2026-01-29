from datetime import datetime
from src.db import get_db
from src.models_portfolio import FinalPersona

class PortfolioStorageService:
    @staticmethod
    def save_portfolio(portfolio: list[FinalPersona]):
        """
        Saves selected portfolio to 'final_personas' table.
        Includes all fields for frontend consumption.
        """
        db = get_db()
        records = []
        
        for p in portfolio:
            # Serialize platform_decisions if present
            platform_decisions_data = {}
            if hasattr(p, 'platform_decisions') and p.platform_decisions:
                for platform, decision in p.platform_decisions.items():
                    if hasattr(decision, 'model_dump'):
                        platform_decisions_data[platform] = decision.model_dump()
                    elif hasattr(decision, 'dict'):
                        platform_decisions_data[platform] = decision.dict()
                    else:
                        platform_decisions_data[platform] = {
                            "allowed": getattr(decision, 'allowed', True),
                            "reason": getattr(decision, 'reason', "")
                        }
            
            records.append({
                "persona_id": p.persona_id,
                "project_id": p.project_id,
                "rank": p.rank,
                "role_in_portfolio": p.role_in_portfolio,
                "funnel_stage": p.funnel_stage,
                "recommended_platforms": p.recommended_platforms,
                "campaign_type": p.campaign_type,
                "notes": p.notes,
                "platform_decisions": platform_decisions_data,
                # Demographics
                "location": p.location,
                "age_range": p.age_range,
                "gender": p.gender,
                "profession": p.profession,
                "household_income": p.household_income,
                # Behavior
                "psychographics": p.psychographics,
                "buying_behavior": p.buying_behavior,
                "pain_points": p.pain_points,
                "interests": p.interests,
                "hobbies": p.hobbies,
                "usp_alignment": p.usp_alignment,
                "created_at": datetime.now().isoformat()
            })
            
        if not records:
            return
            
        db.table("final_personas").insert(records).execute()

