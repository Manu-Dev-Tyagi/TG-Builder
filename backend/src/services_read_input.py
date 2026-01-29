from datetime import datetime
from src.db import get_db
from src.models import BrandInputCreate, BrandInputInDB

class InputReadService:
    @staticmethod
    def get_input(project_id: str) -> BrandInputCreate:
        """
        Fetches the most recent brand input for a project.
        """
        db = get_db()
        response = db.table("brand_inputs")\
            .select("*")\
            .eq("project_id", project_id)\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()
            
        if not response.data:
            raise ValueError(f"No inputs found for project {project_id}")
            
        # Convert DB record back to Pydantic
        # Note: DB might return snake_case or whatever formatting, Pydantic handles passing by keyword args
        # Ensure json/list fields are parsed correctly (PostgREST usually provides JSON objects locally)
        record = response.data[0]
        
        # Helper to safely handle potential key mismatches if DB schema diverged
        # For now direct mapping
        
        # EXTRACT HACK (Preserved for optional override)
        insights = record.get("known_audience_insights") or ""
        # Default to full_funnel unless explicitly overridden
        strategy_depth = record.get("strategy_depth") or "full_funnel"
        
        if "[STRATEGY_DEPTH:" in insights:
            try:
                import re
                match = re.search(r'\[STRATEGY_DEPTH:(.*?)\]', insights)
                if match:
                    strategy_depth = match.group(1)
                    # output clean insights without the tag
                    record["known_audience_insights"] = insights.replace(match.group(0), "").strip()
            except:
                pass
        
        record["strategy_depth"] = strategy_depth
        return BrandInputCreate(**record)
