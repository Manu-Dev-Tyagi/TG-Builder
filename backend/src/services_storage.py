from datetime import datetime
from src.db import get_db
from src.models_scoring import ScoredPersona

class ScoringStorageService:
    @staticmethod
    def save_scored_personas(scored_list: list[ScoredPersona]):
        """
        Saves scores to the 'persona_scores' table.
        """
        db = get_db()
        records = []
        
        for sp in scored_list:
            records.append({
                "persona_id": sp.persona_id,
                "objective_fit_score": sp.score_breakdown.objective_fit * 20, # Store as normalized 0-100
                "price_fit_score": sp.score_breakdown.price_fit * 20,
                "geography_fit_score": sp.score_breakdown.geography_fit * 20,
                "funnel_fit_score": sp.score_breakdown.funnel_fit * 20,
                "ads_feasibility_score": sp.score_breakdown.ads_feasibility * 20,
                "total_score": sp.total_score,
                "score_breakdown": sp.score_breakdown.model_dump(),
                "created_at": datetime.now().isoformat()
            })
            
        if not records:
            return 
            
        db.table("persona_scores").insert(records).execute()

    @staticmethod
    def save_final_selection(scored_list: list[ScoredPersona], top_n=5):
        """
        Saves top N personas to 'final_personas' table.
        """
        db = get_db()
        top_picks = scored_list[:top_n]
        records = []
        
        for p in top_picks:
            records.append({
                "persona_id": p.persona_id,
                "project_id": p.project_id,
                "rank": p.rank,
                "reason": f"Scored {p.total_score} pts. Strong match for objective." # Logic can be enhanced later
            })
            
        if not records:
            return
            
        db.table("final_personas").insert(records).execute()
