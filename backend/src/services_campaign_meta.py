from typing import List
from src.models_portfolio import FinalPersona
from src.schemas.persona_schema import PersonaContract
from src.models_campaign import MetaAdset
from src.wrappers.meta_cluster_builder import MetaClusterWrapper
from src.wrappers.meta_targeting_mapper import MetaTargetingWrapper
from src.llm import LLMClient

class MetaCampaignService:
    @staticmethod
    def generate_adsets(final_persona: FinalPersona, contract: PersonaContract, llm: LLMClient, brand_data: dict, funnel_depth: str = "FULL") -> List[MetaAdset]:
        """
        Generates Meta Adset Clusters based on Locked Strategy topology (Engine A).
        """
        adsets = []
        
        # 1. Fetch Targeting Map (Grounding - Engine B1)
        # Check if we should reuse a map if calculated at project level? For now, per-persona flow is fine, 
        # but actually map is product-level. We could cache it. 
        # However, for simplicity and robustness, we generate it once per call or it's cheap enough.
        product_desc = f"{brand_data.get('brand_name')} ({brand_data.get('product_category')})"
        targeting_map = MetaTargetingWrapper.map_interests(llm, product_desc)

        # 2. Fetch Clusters (Engine B2)
        clusters = MetaClusterWrapper.build_clusters(llm, contract.model_dump(), brand_data, targeting_map)
        
        # 2. Decision Logic: Skip TOF if Locked Strategy says NO_TOF
        for cluster in clusters:
            if funnel_depth == "NO_TOF" and cluster.funnel_stage == "TOF":
                print(f"Skipping TOF for {contract.name} due to Locked Strategy (NO_TOF).")
                continue

            # 3. Deterministic Placement Logic (Now AI-Driven)
            placement = cluster.placement # AI recommended: Advantage+ vs Manual
            targeting_type = "Remarketing" if cluster.funnel_stage == "BOF" else "Interest/Behavior Stack"

            name = f"META | {contract.name} | {cluster.funnel_stage} | {cluster.cluster_name}"
            
            # Map exclusions to unstructured model for DB storage (or structured if model updated)
            # In our MetaAdset model, exclusions is now MetaExclusions
            from src.models_campaign import MetaExclusions
            excl_data = MetaExclusions(
                interests=cluster.exclusions.interests,
                behaviors=cluster.exclusions.behaviors,
                custom_audiences=cluster.exclusions.custom_audiences 
            )

            adset = MetaAdset(
                name=name,
                funnel_stage=cluster.funnel_stage,
                targeting_type=targeting_type,
                age_range=contract.age_range,
                gender=contract.gender,
                locations=contract.location,
                interests=cluster.interests,
                behaviors=cluster.behaviors or [],
                exclusions=excl_data,
                placements=placement,
                primary_benefit=cluster.reasoning
            )
            adsets.append(adset)

        return adsets
