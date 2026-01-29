from uuid import uuid4
from src.db import get_db
from src.models import BrandInputCreate, BrandInputInDB, ProjectCreate, ProjectInDB

class ProjectService:
    @staticmethod
    def create_project(name: str) -> str:
        """Creates a new project and returns its ID."""
        db = get_db()
        response = db.table("projects").insert({"project_name": name}).execute()
        if response.data:
            return response.data[0]["id"]
        raise Exception("Failed to create project")

class InputService:
    @staticmethod
    def save_brand_input(project_id: str, input_data: BrandInputCreate) -> str:
        """
        Validates and saves brand input to the database.
        Returns the ID of the created input record.
        """
        db = get_db()
        
        # Prepare data for insertion
        data = input_data.model_dump()
        data["project_id"] = project_id
        
        # HACK: Persist strategy_depth in known_audience_insights to avoid DB migration
        strategy_depth = data.pop("strategy_depth", "classification_only")
        existing_insights = data.get("known_audience_insights") or ""
        data["known_audience_insights"] = f"{existing_insights} [STRATEGY_DEPTH:{strategy_depth}]".strip()
        
        # Upsert into DB (Idempotency Fix)
        response = db.table("brand_inputs").upsert(data, on_conflict="project_id").execute()
        
        if response.data:
            return response.data[0].get("id", "OK")
        raise Exception("Failed to save/update brand inputs")

    @staticmethod
    def normalize_input(input_data: BrandInputCreate) -> BrandInputCreate:
        """
        Simulated normalization logic.
        In a real app, this might use an LLM to standardize vague terms.
        For now, it cleans strings and ensures defaults.
        """
        # Basic cleaning
        input_data.brand_name = input_data.brand_name.strip()
        input_data.price_positioning = input_data.price_positioning.lower()
        input_data.primary_objective = input_data.primary_objective.lower()
        
        # Example: Enforce defaults if empty lists are passed (already handled by pydantic default_factory, 
        # but here we could apply business logic like "If no city, default to 'All India'")
        
        return input_data
