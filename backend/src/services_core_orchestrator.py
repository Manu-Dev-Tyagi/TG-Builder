from typing import List, Dict, Any
from src.llm import LLMClient
from src.config import Config
from src.services_read_input import InputReadService
from src.services_persona import PersonaService
from src.services_validation import ValidationService
from src.services_scoring import ScoringService
from src.services_storage import ScoringStorageService
from src.services_portfolio import PortfolioService
from src.services_storage_portfolio import PortfolioStorageService
from src.services_campaign_orchestrator import CampaignOrchestrator
from src.services_budget_orchestrator import BudgetOrchestrator
from src.schemas.persona_schema import PersonaContract
from src.models_scoring import ScoredPersona
from src.wrappers.intent_classifier import IntentClassifierWrapper
from src.services_cleanup import CleanupService

class CoreOrchestrator:
    @staticmethod
    def run_full_pipeline(project_id: str) -> Dict[str, Any]:
        """
        Executes Phases 2 through 7 with Contract-First Architecture and Pipeline Verdict.
        """
        from src.contracts.pipeline_result import PipelineRunResult, ArtifactResult
        from src.contracts.artifact_contract import REQUIRED_ARTIFACTS
        
        # Initialize Result Object
        run_result = PipelineRunResult(
            status="SUCCESS",
            project_id=project_id,
            personas_selected=0,
            artifacts=[],
            blocking_errors=[]
        )
        
        # Phase 0: Cleanup (Idempotency Fix)
        CleanupService.cleanup_project(project_id)
        run_result.logs.append("Project Storage Sanitized")

        
        def fail_artifact(name: str, error: str):
            run_result.artifacts.append(ArtifactResult(name=name, required=True, status="FAILED", error=error))
            run_result.blocking_errors.append(f"{name}: {error}")
            run_result.status = "FAILED"
            
        def success_artifact(name: str):
             run_result.artifacts.append(ArtifactResult(name=name, required=True, status="GENERATED"))

        # 1. Load Inputs
        try:
            brand_input = InputReadService.get_input(project_id)
            run_result.logs.append("Inputs Loaded")
        except Exception as e:
            run_result.blocking_errors.append(f"Input Load Failed: {e}")
            run_result.status = "FAILED"
            return run_result.model_dump()

        # --- ENGINE A: DETERMINISTIC CAMPAIGN CLASSIFIER ---
        # Classification depends ONLY on explicit intent, NOT personas.
        llm_light = LLMClient(provider=Config.DEFAULT_PROVIDER, model_name=Config.LIGHT_MODEL)
        
        # Initialize Audit Trail (Review Point 6)
        from src.models_audit import ProjectAuditTrail
        audit = ProjectAuditTrail(project_id=project_id)
        audit.add("ENGINE_A", "Input Received", f"Brand: {brand_input.brand_name}, Objective: {brand_input.primary_objective}")
        
        try:
            locked_strategy = IntentClassifierWrapper.classify(llm_light, brand_input.model_dump())
            
            if locked_strategy.campaign_type == "NA":
                audit.add("ENGINE_A", "Strategic Rejection", "No valid intent mapping")
                fail_artifact("LockedCampaignType", "Semantic Rejection - No valid intent mapping found")
                # Store Audit before returning
                run_result.logs.append(f"AUDIT: {[e.model_dump() for e in audit.entries]}")
                return run_result.model_dump()
            
            audit.add("ENGINE_A", f"Campaign Locked: {locked_strategy.campaign_type}", f"Funnel: {locked_strategy.funnel_depth}, Platforms: {locked_strategy.allowed_platforms}")
            success_artifact("LockedCampaignType")
            run_result.logs.append(f"Engine A: Classified as {locked_strategy.campaign_type}")
            
        except Exception as e:
            audit.add("ENGINE_A", "Technical Error", str(e))
            fail_artifact("LockedCampaignType", str(e))
            run_result.logs.append(f"AUDIT: {[e.model_dump() for e in audit.entries]}")
            return run_result.model_dump()

        # 2. Generate (Phase 2) - Upstream Wrapper
        llm = LLMClient(provider=Config.DEFAULT_PROVIDER, model_name=Config.HEAVY_MODEL)
        saved_personas_data = []
        try:
            # Using the new PersonaContractList schema
            raw_personas_list = llm.generate_personas(
                brand_name=brand_input.brand_name,
                product_category=brand_input.product_category,
                price_positioning=brand_input.price_positioning,
                primary_usp=brand_input.primary_usp,
                primary_objective=brand_input.primary_objective,
                known_audience_insights=brand_input.known_audience_insights or "",
                count=Config.DEFAULT_GENERATION_COUNT,
                geography=brand_input.geography,
                campaign_context=locked_strategy.campaign_type # Context Injection (Fix #2)
            )
            # Save Raw
            PersonaService.save_raw_personas(project_id, raw_personas_list, Config.HEAVY_MODEL)

            # Fetch back saved personas with their database-generated IDs
            saved_personas_data = PersonaService.fetch_personas_by_project(project_id)
            run_result.logs.append(f"Generated {len(raw_personas_list.personas)} Personas")
            success_artifact("PersonaSchema")
        except Exception as e:
            fail_artifact("PersonaSchema", str(e))
            return run_result.model_dump()

        # 3. Validate & Clean (Phase 3)
        valid_contracts: List[tuple[PersonaContract, str]] = [] # (Contract, DB_ID)
        try:
            for p_data in saved_personas_data:
                # Convert raw JSON from DB into PersonaContract
                try:
                    p = PersonaContract(**p_data['persona_data'])
                except Exception as e:
                    print(f"SCHEMA ERROR on persona {p_data.get('id')}: {e}")
                    print(f"RAW DATA: {p_data['persona_data']}")
                    raise e
                if ValidationService.validate_schema(p):
                     p = ValidationService.normalize_fields(p)
                     if ValidationService.check_logical_consistency(p):
                        if not ValidationService.is_duplicate(p, [vc[0] for vc in valid_contracts]):
                            valid_contracts.append((p, p_data['id']))
            
            run_result.logs.append(f"Validated: {len(valid_contracts)} remaining")
            if not valid_contracts:
                fail_artifact("PersonaSchema", "All personas failed validation")
                return run_result.model_dump()
        except Exception as e:
             # Validation logic failure shouldn't crash pipeline usually, but if contracts empty -> fail
             print(e)

        # 4. Score (Phase 4) - Deterministic Wrapper
        scored_pairs: List[tuple[ScoredPersona, PersonaContract]] = []
        scored_objects_only = []
        try:
            for p_contract, db_id in valid_contracts:
                sp = ScoringService.calculate_score(p_contract, brand_input, db_id, project_id)
                scored_pairs.append((sp, p_contract))
                scored_objects_only.append(sp)

            # Save Scores
            ScoringStorageService.save_scored_personas(scored_objects_only)
            run_result.logs.append("Scoring Complete")
            success_artifact("PersonaScore")
        except Exception as e:
            fail_artifact("PersonaScore", str(e))
            # Blocking if scoring fails
            return run_result.model_dump()

        # 5. Select Portfolio (Phase 5)
        portfolio = PortfolioService.build_portfolio(scored_pairs, top_n=5)
        # Save Final Selection
        PortfolioStorageService.save_portfolio(portfolio)
        run_result.logs.append(f"Selected {len(portfolio)} Final Personas")
        run_result.personas_selected = len(portfolio)

        # 6. Campaign Blueprints (Phase 6) - Platform & Campaign Classification Wrappers
        # Filter contract pairs to only those selected in portfolio
        portfolio_pairs = []
        for fp in portfolio:
            match = next((pair for pair in scored_pairs if pair[0].persona_id == fp.persona_id), None)
            if match:
                portfolio_pairs.append((fp, match[1]))
        
        try:
            CampaignOrchestrator.generate_blueprint(
                project_id=project_id, 
                final_portfolio=portfolio_pairs, 
                product_category=brand_input.product_category,
                locked_strategy=locked_strategy,
                strategy_depth=brand_input.strategy_depth,
                pipeline_result=run_result # Pass result object for Phase 5 Fallback tracking
            )
            run_result.logs.append(f"Campaign Blueprints Generated ({brand_input.strategy_depth} mode)")
            success_artifact("TargetingBlueprint") 
        except Exception as e:
            fail_artifact("TargetingBlueprint", str(e))
            # Don't return here, might have partial success or budget might work? 
            # But requirements say "Fail closed". Okay, return.
            return run_result.model_dump()

        # 7. Budget (Phase 7)
        try:
            budget_pairs = []
            for fp in portfolio:
                 match = next((pair for pair in scored_pairs if pair[0].persona_id == fp.persona_id), None)
                 if match:
                     budget_pairs.append((fp, match[0]))
                      
            total_budget = 1000.0
            BudgetOrchestrator.generate_budget_plan(budget_pairs, total_budget, project_id)
            audit.add("BUDGET", "Budget Plan Generated", f"Total: ${total_budget}")
            run_result.logs.append("Budget Plan Generated")
        except Exception as e:
             audit.add("BUDGET", "Budget Fail", str(e))
             run_result.blocking_errors.append(f"Budget Fail: {e}")

        # FINAL GATE: Check strict artifact completion
        missing_required = [
            req for req in REQUIRED_ARTIFACTS
            if not any(a.name == req and a.status == "GENERATED" for a in run_result.artifacts)
        ]

        if missing_required:
            run_result.status = "FAILED"
            error_msg = f"Missing Required Artifacts: {missing_required}"
            run_result.blocking_errors.append(error_msg)
            print(f"PIPELINE_VERDICT: FAILED. {error_msg}")
            for a in run_result.artifacts:
                print(f"  Artifact: {a.name} | Status: {a.status} | Error: {a.error}")

        # Append Full Audit Trail to Response (Review Point 6)
        audit.add("ORCHESTRATOR", "Pipeline Complete", f"Status: {run_result.status}")
        run_result.logs.append(f"AUDIT_TRAIL: {[e.model_dump() for e in audit.entries]}")
        
        return run_result.model_dump()
