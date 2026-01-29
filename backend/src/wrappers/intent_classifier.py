from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from src.llm import LLMClient
from src.config import Config
from typing import Dict, Literal, List
from pydantic import BaseModel, Field

class LockedStrategy(BaseModel):
    campaign_type: Literal["Sales (Purchase Focus)", "Leads (Lead Capture)", "Leads (Website Conversion)", 
                           "Engagement (Post Interaction)", "Messages (Chat Intent)", "Search (Intent Capture)", 
                           "Shopping (Product Sales)", "Awareness & Reach", "Video Views", "App Promotion (Install Focus)", "NA"] = Field(description="The strict campaign objective")
    funnel_depth: Literal["FULL", "NO_TOF"] = Field(description="FULL for complex/expensive products, NO_TOF for impulse/fast products")
    allowed_platforms: List[Literal["Meta", "Google"]] = Field(description="Allowed platforms based on intent")

INTENT_CLASSIFIER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Stateless Intent Classifier (Engine A).
Your goal is to map Brand Inputs to a LOCKED STRATEGY TOPOLOGY.

INPUTS:
Brand: {brand_name}
Category: {category}
Price: {price}
Objective: {objective}
Platform Affinity: {affinity}

RULES:
1. CAMPAIGN TYPE:
   - Immediate purchase + Sales objective -> 'Sales (Purchase Focus)'
   - Lead gen / Consultation / Forms -> 'Leads (Lead Capture)' OR 'Leads (Website Conversion)'
   - App Installs / Mobile Growth / Downloads -> 'App Promotion (Install Focus)'
   - Awareness / Reach / Brand Recall -> 'Awareness & Reach'
   - Engagement / Video Content -> 'Video Views' OR 'Engagement (Post Interaction)'
   - Search-heavy intent -> 'Search (Intent Capture)'
   - eCommerce / Catalog -> 'Shopping (Product Sales)'
   - If completely ambiguous or invalid -> 'NA'

2. FUNNEL DEPTH:
   - Premium/High Price/Complex (Luxury, B2B, Specialized) -> 'FULL' (Requires Awareness/Consideration)
   - Low Price/Impulse/Simple (FMCG, Cheap gadgets) or App Installs -> 'NO_TOF' (Skip Awareness stage)
   - If Objective is Awareness -> Must be 'FULL'

3. PLATFORMS:
   - Search Intent (Users looking for solutions) -> include 'Google'
   - Visual Discovery / Impulse / Social -> include 'Meta'
   - AFFINITY RULES:
     - If 'Platform Affinity' is provided (not empty), ONLY output platforms from that list.
     - If 'Platform Affinity' is EMPTY, recommend the best platforms based on the intent (Meta/Google).

OUTPUT:
Return ONLY a JSON object matching the LockedStrategy schema.
{format_instructions}
"""),
    ("user", "Classify intent and topology now.")
])

class IntentClassifierWrapper:
    @staticmethod
    def classify(llm_client: LLMClient, brand_data: Dict[str, str]) -> LockedStrategy:
        """
        Engine A: Pure Deterministic Classifier.
        Outputs a LockedStrategy object containing Type, Topology, and Platforms.
        """
        parser = PydanticOutputParser(pydantic_object=LockedStrategy)
        
        chain = INTENT_CLASSIFIER_PROMPT | llm_client.llm
        
        try:
            result = chain.invoke({
                "brand_name": brand_data.get("brand_name"),
                "category": brand_data.get("product_category"),
                "price": brand_data.get("price_positioning"),
                "objective": brand_data.get("primary_objective"),
                "affinity": ", ".join(brand_data.get("platform_affinity", [])),
                "format_instructions": parser.get_format_instructions()
            })
            
            content = result.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # Robust extraction
            start = content.find('{')
            end = content.rfind('}')
            if start != -1 and end != -1:
                content = content[start:end+1]
                
            strategy = parser.parse(content)
            
            # Validate strict allowlist compatibility
            if strategy.campaign_type == "NA":
                 return strategy # Return as is, orchestrator handles it
                 
            return strategy
            
        except Exception as e:
            # Fallback for determinism
            print(f"Engine A Technical Fail: {e}")
            return LockedStrategy(campaign_type="NA", funnel_depth="FULL", allowed_platforms=[])
