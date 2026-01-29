from typing import List
from src.db import get_db
from src.schemas.persona_schema import PersonaContractList

class PersonaService:
    @staticmethod
    def save_raw_personas(project_id: str, personas: PersonaContractList, llm_model: str) -> int:
        """
        Saves a list of personas to the raw_personas table.
        Returns the count of saved personas.
        """
        db = get_db()
        records_to_insert = []
        
        for persona in personas.personas:
            records_to_insert.append({
                "project_id": project_id,
                "persona_name": persona.name,
                "persona_data": persona.model_dump(),  # Automatically serializes nested Pydantic models
                "llm_model": llm_model,
                "prompt_version": "v1.0"
            })
            
        if not records_to_insert:
            return 0
            
        response = db.table("raw_personas").insert(records_to_insert).execute()
        
        # In Supabase/PostgREST, successful insert returns the data.
        # We assume if no exception raised, it succeeded.
        return len(response.data) if response.data else 0

    @staticmethod
    def fetch_personas_by_project(project_id: str):
        """Helper to fetch personas for a project."""
        db = get_db()
        response = db.table("raw_personas").select("*").eq("project_id", project_id).execute()
        return response.data
