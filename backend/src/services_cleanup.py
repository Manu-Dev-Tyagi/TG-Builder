from src.db import get_db

class CleanupService:
    @staticmethod
    def cleanup_project(project_id: str):
        """
        Deletes all artifacts related to a project for re-generation.
        Ensures idempotency and prevents duplicates.
        """
        db = get_db()
        
        # 1. Delete Targeting Blueprints
        db.table("targeting_blueprints").delete().eq("project_id", project_id).execute()
        
        # 2. Delete Final Personas
        db.table("final_personas").delete().eq("project_id", project_id).execute()
        
        # 3. Delete Persona Scores
        # Subquery to find persona_ids
        raw_personas = db.table("raw_personas").select("id").eq("project_id", project_id).execute()
        p_ids = [r["id"] for r in raw_personas.data]
        if p_ids:
            db.table("persona_scores").delete().in_("persona_id", p_ids).execute()
        
        # 4. Delete Raw Personas
        db.table("raw_personas").delete().eq("project_id", project_id).execute()
        
        # 5. Delete Projects Table Entries? NO.
        # But we might want to clear specific project metadata like audit_trail?
        # db.table("projects").update({"audit_trail": [], "locked_strategy": None}).eq("id", project_id).execute()
        
        return True
