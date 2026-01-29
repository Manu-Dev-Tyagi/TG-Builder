from typing import List
from src.models_portfolio import FinalPersona
from src.schemas.persona_schema import PersonaContract
from src.models_campaign import GoogleAdGroup
from src.wrappers.google_structure_builder import GoogleStructureBuilder
from src.llm import LLMClient

class GoogleCampaignService:
    @staticmethod
    def generate_adgroups(final_persona: FinalPersona, contract: PersonaContract, llm: LLMClient, brand_data: dict, funnel_depth: str = "FULL") -> List[GoogleAdGroup]:
        """
        Generates Google Ad Group Architecture (Engine B).
        Now uses GoogleStructureBuilder for deep structures (Search, PMax, Demand Gen).
        """
        
        # 1. Structural Decision & generation (AI Architect)
        adgroups = GoogleStructureBuilder.build_structure(llm, contract.model_dump(), brand_data)
        
        # 2. Filtering Logic (Funnel Depth)
        # If strategy is NO_TOF, we might filter out "Awareness" intent groups?
        # For now, we trust the Architect to follow the persona's needs, but we can enforce:
        filtered_adgroups = []
        for ag in adgroups:
            if funnel_depth == "NO_TOF" and ag.intent.lower() == "awareness":
                # Skip pure awareness plays if strictly performance locked
                continue
            filtered_adgroups.append(ag)
            
        return filtered_adgroups
