from typing import List, Dict
from src.models_budget import BudgetAllocation, FunnelSplit
from src.models_portfolio import FinalPersona

class FunnelBudgetService:
    @staticmethod
    def split_by_funnel(allocations: List[BudgetAllocation], personas: List[FinalPersona]) -> Dict[str, List[FunnelSplit]]:
        """
        Splits platform budgets into specific funnel containers (TOF/MOF/BOF).
        Returns a dictionary keyed by persona_id.
        """
        results = {}
        p_map = {p.persona_id: p for p in personas}
        
        for alloc in allocations:
            p = p_map.get(alloc.persona_id)
            splits = []
            
            # --- Meta Logic ---
            if alloc.meta_budget > 0:
                # Default Split
                tof_share = 0.2
                mof_share = 0.4
                bof_share = 0.4
                
                # Logic: Check Decision Speed for NO_TOF
                speed = p.buying_behavior.get("decision_speed", "Normal")
                if "Fast" in speed:
                     # Suppress TOF
                     tof_share = 0.0
                     mof_share = 0.5
                     bof_share = 0.5

                # Override: Experiment -> TOF Only
                if p.role_in_portfolio == "Experiment":
                    tof_share = 1.0; mof_share = 0; bof_share = 0
                # Override: Anchor -> Balanced
                
                if tof_share > 0:
                    splits.append(FunnelSplit(
                        structure_type="Meta Adset", name="Broad / TOF", 
                        funnel_stage="TOF", alloc_percentage=tof_share, 
                        daily_budget=round(alloc.meta_budget * tof_share, 2)
                    ))
                if mof_share > 0:
                    splits.append(FunnelSplit(
                        structure_type="Meta Adset", name="Interest Stack / MOF", 
                        funnel_stage="MOF", alloc_percentage=mof_share, 
                        daily_budget=round(alloc.meta_budget * mof_share, 2)
                    ))
                if bof_share > 0:
                     splits.append(FunnelSplit(
                        structure_type="Meta Adset", name="Remarketing / BOF", 
                        funnel_stage="BOF", alloc_percentage=bof_share, 
                        daily_budget=round(alloc.meta_budget * bof_share, 2)
                    ))

            # --- Google Logic ---
            if alloc.google_budget > 0:
                # Search is usually High Intent (MOF/BOF)
                # Assign to Keyword Exact/Phrase (Protected)
                splits.append(FunnelSplit(
                    structure_type="Google AdGroup", name="Search Intent", 
                    funnel_stage="BOF", alloc_percentage=1.0, 
                    daily_budget=alloc.google_budget
                ))
            
            results[alloc.persona_id] = splits
            
        return results
