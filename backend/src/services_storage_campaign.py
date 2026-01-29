from datetime import datetime
from src.db import get_db
from src.models_campaign import CampaignBlueprint

class CampaignStorageService:
    @staticmethod
    def save_blueprint(blueprint: CampaignBlueprint):
        """
        Saves the generated campaign blueprint.
        Currently saves as a huge JSON blob for the 'targeting_blueprints' table idea,
        although our schema had 'targeting_blueprints' linked primarily to a single persona.
        
        We will adapt: Save individually per persona-platform pair if possible, 
        or save the whole project blueprint in a new structure/metadata.
        
        Using the existing 'targeting_blueprints' table:
        id | project_id | persona_id | platform | funnel_stage | targeting_data
        """
        db = get_db()
        records = []
        
        # 1. Save Meta Adsets
        # Map back adsets to personas? The blueprint object might lose the direct link if not careful.
        # Ideally, we should generate and save PER persona in the loop. 
        # But assuming we have the context.
        
        # NOTE: For this service to be clean, it should probably take the RAW lists generated in the orchestrator
        # and match them to the persona IDs. 
        # Alternatively, we iterate through the generated objects.
        # But 'MetaAdset' model didn't store persona_id. 
        # IMPROVEMENT: Let's assume the Name string contains the key or we pass metadata.
        
        # For MVP, we will rely on the orchestrator calling a 'save_persona_blueprint' method 
        # instead of saving the monolithic object.
        pass

    @staticmethod
    def save_persona_blueprints(project_id: str, persona_id: str, meta_adsets: list, google_adgroups: list):
        db = get_db()
        records = []
        
        if meta_adsets:
            records.append({
                "project_id": project_id,
                "persona_id": persona_id,
                "platform": "Meta",
                "funnel_stage": "Mixed", # Contains TOF/MOF etc
                "targeting_data": [m.model_dump() for m in meta_adsets],
                "created_at": datetime.now().isoformat()
            })
            
        if google_adgroups:
            records.append({
                "project_id": project_id,
                "persona_id": persona_id,
                "platform": "Google",
                "funnel_stage": "Mixed",
                "targeting_data": [g.model_dump() for g in google_adgroups],
                "created_at": datetime.now().isoformat()
            })

        if records:
            db.table("targeting_blueprints").insert(records).execute()
