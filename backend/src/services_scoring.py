from typing import List, Dict
from src.schemas.persona_schema import PersonaContract
from src.models import BrandInputCreate
from src.models_scoring import ScoredPersona, ScoreBreakdown
from src.config import Config

class ScoringService:
    @staticmethod
    def calculate_score(persona: PersonaContract, brand_input: BrandInputCreate, persona_id: str, project_id: str) -> ScoredPersona:
        """
        Deterministic scoring engine based on PersonaContract.
        Scores are calculated from 0-5 and then weighted.
        """
        
        # 1. Objective Fit
        obj_score = ScoringService._score_objective_fit(persona, brand_input.primary_objective)
        
        # 2. Price Fit
        price_score = ScoringService._score_price_fit(persona, brand_input.price_positioning)
        
        # 3. Geo Fit
        geo_score = ScoringService._score_geo_fit(persona, brand_input.geography)
        
        # 4. Funnel Fit (Logic based on Decision Speed)
        funnel_score = ScoringService._score_funnel_fit(persona)
        
        # 5. Ads Feasibility (Platform Affinity)
        ads_score = ScoringService._score_ads_feasibility(persona)

        # Weighted Sum
        w = Config.SCORING_WEIGHTS
        
        total = (
            (obj_score * w.objective_fit) +
            (price_score * w.price_fit) +
            (geo_score * w.geography_fit) +
            (funnel_score * w.funnel_fit) +
            (ads_score * w.ads_feasibility)
        ) * 20 # Scale 0.0 - 5.0 to 0 - 100

        return ScoredPersona(
            persona_id=persona_id,
            project_id=project_id,
            total_score=round(total, 2),
            score_breakdown=ScoreBreakdown(
                objective_fit=obj_score,
                price_fit=price_score,
                geography_fit=geo_score,
                funnel_fit=funnel_score,
                ads_feasibility=ads_score
            )
        )

    @staticmethod
    def _score_objective_fit(persona: PersonaContract, objective: str) -> float:
        score = 1.0
        obj = objective.lower()
        
        # Logical mapping from persona triggers/usp alignment
        if "purchase" in obj:
            if persona.buying_behavior.decision_speed == "Fast": score += 2.0
            if "purchase" in " ".join(persona.buying_behavior.purchase_triggers).lower(): score += 2.0
        elif "lead" in obj:
            if "research" in " ".join(persona.buying_behavior.purchase_triggers).lower(): score += 2.0
            if "Normal" in persona.buying_behavior.decision_speed: score += 1.0
        
        return min(score, 5.0)

    @staticmethod
    def _score_price_fit(persona: PersonaContract, price_pos: str) -> float:
        score = 2.0
        p_price = persona.buying_behavior.price_sensitivity
        
        if price_pos.lower() == "premium":
            if p_price == "Low": score += 3.0
            elif p_price == "Medium": score += 1.0
            else: score -= 1.0
        elif price_pos.lower() == "mid":
            if p_price == "Medium": score += 3.0
            else: score += 1.0
        else: # Low/Budget
            if p_price == "High": score += 3.0
            else: score += 2.0
            
        return max(0.0, min(score, 5.0))

    @staticmethod
    def _score_geo_fit(persona: PersonaContract, target_geo: str) -> float:
        score = 2.0
        if target_geo.lower() in persona.location.lower():
            score += 3.0
        return min(score, 5.0)

    @staticmethod
    def _score_funnel_fit(persona: PersonaContract) -> float:
        # Map decision speed to funnel proximity
        if persona.buying_behavior.decision_speed == "Fast": return 5.0
        if persona.buying_behavior.decision_speed == "Normal": return 3.5
        return 2.0

    @staticmethod
    def _score_ads_feasibility(persona: PersonaContract) -> float:
        score = 1.0
        if "Meta" in persona.platform_affinity: score += 2.0
        if "Google" in persona.platform_affinity: score += 2.0
        return min(score, 5.0)

    @staticmethod
    def rank_personas(scored_list: List[ScoredPersona]) -> List[ScoredPersona]:
        scored_list.sort(key=lambda x: x.total_score, reverse=True)
        for i, p in enumerate(scored_list):
            p.rank = i + 1
        return scored_list
