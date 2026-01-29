from typing import List
from src.models_portfolio import FinalPersona
from src.models_budget import BudgetAllocation

class PlatformBudgetService:
    @staticmethod
    def split_by_platform(allocations: List[BudgetAllocation], personas: List[FinalPersona]) -> List[BudgetAllocation]:
        """
        Splits persona budget into Meta vs Google based on traits.
        """
        # Map persona_id to FinalPersona object for easy lookup
        p_map = {p.persona_id: p for p in personas}
        
        for alloc in allocations:
            p = p_map.get(alloc.persona_id)
            if not p:
                continue
                
            platforms = p.recommended_platforms
            has_meta_types = any(x in platforms for x in ["Meta", "Instagram", "YouTube"])
            has_search_types = any(x in platforms for x in ["Google Search", "LinkedIn"])
            
            # Simple Heuristic
            # If both: 60/40 split favoring behavior
            # If only one: 100%
            
            meta_share = 0.0
            google_share = 0.0
            
            if has_meta_types and has_search_types:
                # Check for "Search Intent" bias (if mapped in future, using simple check now)
                if "Google Search" in platforms:
                    google_share = 0.60
                    meta_share = 0.40
                else:
                    meta_share = 0.60
                    google_share = 0.40
            elif has_meta_types:
                meta_share = 1.0
            elif has_search_types:
                google_share = 1.0
                
            alloc.meta_budget = round(alloc.total_daily_budget * meta_share, 2)
            alloc.google_budget = round(alloc.total_daily_budget * google_share, 2)
            
        return allocations
