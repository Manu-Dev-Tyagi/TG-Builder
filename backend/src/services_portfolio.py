from typing import List, Optional, Tuple
from src.models_scoring import ScoredPersona
from src.schemas.persona_schema import PersonaContract
from src.models_portfolio import FinalPersona
from src.config import Config

class PortfolioService:
    MIN_SCORE = Config.MIN_SCORE_TO_SELECT

    @staticmethod
    def build_portfolio(scored_items: List[Tuple[ScoredPersona, PersonaContract]], top_n: int = 5) -> List[FinalPersona]:
        """
        Selects top personas respecting diversity and score thresholds using the PersonaContract.
        """
        # 1. Filter by Threshold
        eligible = [
            (sp, p) for (sp, p) in scored_items 
            if sp.total_score >= PortfolioService.MIN_SCORE
        ]
        
        # Sort by score descending
        eligible.sort(key=lambda x: x[0].total_score, reverse=True)
        
        portfolio: List[FinalPersona] = []
        selected_professions = set()

        # 2. Select with Diversity
        for sp, p in eligible:
            if len(portfolio) >= top_n:
                break
                
            # Diversity check by profession
            if p.profession in selected_professions:
                continue
            
            # 3. Assign Attributes
            role = PortfolioService._assign_role(sp, p, len(portfolio))
            funnel = PortfolioService._map_funnel(p)
            platforms = p.platform_affinity
            
            final_p = FinalPersona(
                persona_id=sp.persona_id,
                project_id=sp.project_id,
                rank=len(portfolio) + 1,
                role_in_portfolio=role,
                funnel_stage=funnel,
                recommended_platforms=platforms,
                location=p.location,
                age_range=p.age_range,
                gender=p.gender,
                profession=p.profession,
                household_income=p.household_income,
                psychographics=p.psychographics.model_dump(),
                buying_behavior=p.buying_behavior.model_dump(),
                pain_points=p.pain_points,
                interests=p.interests,
                hobbies=p.hobbies,
                usp_alignment=p.usp_alignment_reason,
                notes=f"Selected as {role}. Score: {sp.total_score}."
            )
            
            portfolio.append(final_p)
            selected_professions.add(p.profession)
            
        return portfolio

    @staticmethod
    def _assign_role(scored: ScoredPersona, p: PersonaContract, current_count: int) -> str:
        # First best is Anchor
        if current_count == 0:
            return "Anchor"
            
        # Decision speed informs role
        if p.buying_behavior.decision_speed == "Fast":
            return "Conversion Driver"
        
        if scored.total_score > 80:
            return "Expansion"
            
        return "Experiment"

    @staticmethod
    def _map_funnel(p: PersonaContract) -> str:
        # Map Decision Speed to Funnel Stage
        if p.buying_behavior.decision_speed == "Fast": return "Bottom"
        if p.buying_behavior.decision_speed == "Normal": return "Mid"
        return "Top"
