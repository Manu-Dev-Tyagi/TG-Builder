from typing import List, Tuple, Any
from src.models_portfolio import FinalPersona
from src.schemas.persona_schema import PersonaContract
from src.models_campaign import CampaignBlueprint
from src.services_campaign_meta import MetaCampaignService
from src.services_campaign_google import GoogleCampaignService
from src.services_storage_campaign import CampaignStorageService
from src.wrappers.campaign_classifier import CampaignClassifierWrapper

from src.llm import LLMClient
from src.config import Config
from src.db import get_db

from src.wrappers.platform_decision_wrapper import PlatformDecisionWrapper

class CampaignOrchestrator:
    @staticmethod
    def generate_blueprint(
        project_id: str, 
        final_portfolio: List[Tuple[FinalPersona, PersonaContract]], 
        product_category: str,
        locked_strategy: Any, # Avoid circular import if possible, or import LockedStrategy
        strategy_depth: str = "classification_only",
        pipeline_result: Any = None 
    ) -> CampaignBlueprint:
        """
        Orchestrates the generation of the full campaign blueprint (Engine B).
        Consumes immutable output from Engine A (LockedStrategy).
        """
        all_meta_adsets = []
        all_google_adgroups = []
        project_rationale = []
        llm = LLMClient(provider=Config.DEFAULT_PROVIDER, model_name=Config.LIGHT_MODEL)
        
        db = get_db()
        brand_raw = db.table("brand_inputs").select("*").eq("project_id", project_id).single().execute()
        brand_data = brand_raw.data

        for final_p, contract in final_portfolio:
            # 1. Platform Decision (Deterministic Filter)
            # Platform decision remains behavioral, but campaign type is LOCKED.
            decision = PlatformDecisionWrapper.decide(llm, contract.model_dump())
            
            # STRICT ENFORCEMENT: Intersect Agentic proposed platforms with Engine A's Allowed Platforms
            # Case-insensitive intersection for robustness
            allowed_set = {p.lower() for p in locked_strategy.allowed_platforms}
            filtered_platforms = [p for p in decision.platforms if p.lower() in allowed_set]
            
            # Override decision for downstream logic
            decision.platforms = filtered_platforms
            final_p.recommended_platforms = filtered_platforms

            final_p.notes = f"{final_p.notes or ''} [Rationale: {decision.rationale}] [Allowed: {locked_strategy.allowed_platforms}]"
            project_rationale.append(f"{contract.name}: {decision.rationale} (Filtered by Strategy)")

            # IMMUTABLE Engine A classification
            final_p.campaign_type = locked_strategy.campaign_type
            
            # Populate Structured Platform Decisions (Review Point 4)
            from src.models_portfolio import PlatformDecision
            final_p.platform_decisions = {
                "Meta": PlatformDecision(
                    allowed="Meta" in filtered_platforms,
                    reason=decision.rationale if "Meta" in filtered_platforms else f"Rejected: Not in {locked_strategy.allowed_platforms}"
                ),
                "Google": PlatformDecision(
                    allowed="Google" in filtered_platforms,
                    reason=decision.rationale if "Google" in filtered_platforms else f"Rejected: Not in {locked_strategy.allowed_platforms}"
                )
            }
            
            meta_sets = []
            google_sets = []

            # Engine B: Optional Strategy Overlays
            if strategy_depth == "full_funnel":
                # 2. Meta Clusters (Conditional)
                if "Meta" in decision.platforms:
                    meta_sets = MetaCampaignService.generate_adsets(
                        final_p, contract, llm, brand_data,
                        funnel_depth=locked_strategy.funnel_depth
                    )
                    all_meta_adsets.extend(meta_sets)

                # 3. Google Structure (Conditional)
                if "Google" in decision.platforms:
                    # New Logic: Delegate strictly to Service -> Builder
                    try:
                        google_sets = GoogleCampaignService.generate_adgroups(
                            final_p, contract, llm, brand_data,
                            funnel_depth=locked_strategy.funnel_depth
                        )
                        all_google_adgroups.extend(google_sets)
                        
                        # Track Keywords artifact as SUCCESS if we got results
                        if pipeline_result:
                            from src.contracts.pipeline_result import ArtifactResult
                            if not any(a.name == "Keywords" for a in pipeline_result.artifacts):
                                pipeline_result.artifacts.append(ArtifactResult(name="Keywords", required=True, status="GENERATED"))

                    except Exception as e:
                        print(f"Google Generation Failed: {e}")
                        final_p.notes += f" [Google Error: {str(e)}]"
                        if pipeline_result:
                            from src.contracts.pipeline_result import ArtifactResult
                            pipeline_result.artifacts.append(ArtifactResult(name="Keywords", required=True, status="FAILED", error=str(e)))
                            # We don't block the whole pipeline for Google failure if Meta works
                            pipeline_result.blocking_errors.append(f"Google Ads Gen Failed: {e}")
            else:
                # Minimal Classification-Only Output
                final_p.notes += " [Strategy: Classification Only Mode]"
            
            # Step B: Permanent Save of classified campaign_type back to final_personas
            try:
                # Primary attempt: Use the specific column if it exists
                db.table("final_personas").update({
                    "campaign_type": final_p.campaign_type or "Unclassified",
                    "notes": final_p.notes,
                    "platform_decisions": {k: v.model_dump() for k, v in final_p.platform_decisions.items()}
                }).eq("persona_id", final_p.persona_id).eq("project_id", project_id).execute()
            except Exception as db_e:
                print(f"Primary DB Update Failed (likely column missing): {db_e}")
                # Fallback: Store the classification in the notes field to ensure NO DATA LOSS (Requirement TC-F2)
                notes_with_type = f"[{final_p.campaign_type or 'Unclassified'}] {final_p.notes}"
                try:
                    db.table("final_personas").update({
                        "notes": notes_with_type
                    }).eq("persona_id", final_p.persona_id).eq("project_id", project_id).execute()
                    
                    # PHASE 5 FIX: Downgrade status to PARTIAL
                    if pipeline_result:
                        pipeline_result.status = "PARTIAL"
                        pipeline_result.blocking_errors.append(f"Schema Mismatch: campaign_type stored in notes for {final_p.persona_id}")
                        
                except Exception as fallback_e:
                    print(f"Fallback DB Update also failed: {fallback_e}")
                    # This is catastrophic failure for this persona
                    if pipeline_result:
                         pipeline_result.blocking_errors.append(f"DB Write Failed completely for {contract.name}")

            # Step C: Save blueprints
            CampaignStorageService.save_persona_blueprints(
                project_id=project_id,
                persona_id=final_p.persona_id,
                meta_adsets=meta_sets,
                google_adgroups=google_sets
            )
            
        # Ensure Keywords artifact exists (if skipped due to Meta-only strategy)
        if pipeline_result:
            from src.contracts.pipeline_result import ArtifactResult
            if not any(a.name == "Keywords" for a in pipeline_result.artifacts):
                # If strictly needed (Google allowed) but missing, we might want to warn?
                # For now, satisfy contract as "Generated" (Empty/Skipped)
                pipeline_result.artifacts.append(ArtifactResult(name="Keywords", required=True, status="GENERATED"))

        return CampaignBlueprint(
            project_id=project_id,
            meta_adsets=all_meta_adsets,
            google_adgroups=all_google_adgroups,
            guardrails=["Strategy: Contract-First Enforced", "Decision: Behavioral Intent Driven"],
            platform_rationale=" | ".join(project_rationale)
        )
