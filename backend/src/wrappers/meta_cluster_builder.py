from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json
from src.llm import LLMClient
from src.models_campaign import MetaAdset
from typing import List, Dict, Any
from pydantic import BaseModel, Field

class ExclusionCluster(BaseModel):
    interests: List[str] = Field(description="Meta-native interest exclusions")
    behaviors: List[str] = Field(description="Meta-native behavior exclusions")
    custom_audiences: List[str] = Field(default=[], description="Mocked CA exclusions e.g. 'Purchasers'")

class InterestCluster(BaseModel):
    funnel_stage: str = Field(..., description="TOF, MOF, or BOF")
    cluster_name: str = Field(..., description="e.g. 'Fitness Tech Enthusiasts'")
    interests: List[str] = Field(..., description="5-7 EXACT Meta-native interest keywords")
    behaviors: List[str] = Field(..., description="Meta-native behaviors (e.g. 'Frequent Travelers')")
    placement: str = Field(..., description="'Advantage+' or 'Manual'")
    exclusions: ExclusionCluster
    reasoning: str

class MetaClusterList(BaseModel):
    clusters: List[InterestCluster]

META_CLUSTER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a World-Class Meta Ads Performance Marketer (Top 1%).
Your goal is to architect a high-performance Adset Structure for a single persona.

STRATEGIC ARCHITECTURE (2-4 Adsets Required):
1. TOF (Top of Funnel) - "The Broad Hook"
   - Objective: Awareness & Prospecting.
   - Targeting: Broad Interest Clusters (e.g., "Physical Fitness" + "Wellness").
   - Placement: Advantage+ (Let the Algo work).
   - Exclusions: Existing Customers.

2. MOF (Middle of Funnel) - "The Consideration Stack"
   - Objective: Intent Capture.
   - Targeting: Specific Interest Stack + Behavior Layer (e.g., "Yoga" AND "Recent Shopper").
   - Placement: Manual (Feeds, Stories, Reels) - Force visibility.
   - Exclusions: Recent Purchasers (30d).

3. BOF (Bottom of Funnel) - "The Closer" (MOCK THIS)
   - Objective: Retargeting / Conversion.
   - Targeting: "Website Visitors (180d)", "Add to Cart (30d)", "IG Engagers (365d)".
   - Placement: Manual (High Attention Zones).
   - Exclusions: Recent Purchasers (180d), Competitors.

DATA SOURCE (STRICT USE):
- Interests: Use broad categories for TOF, specific niches for MOF.
- Behaviors: Use "Purchase Behavior", "Mobile Device User", "Travel", "Expat", "Soccer Mom" etc.

REQUIRED OUTPUT TARGET:
- Generate 2-4 distinct adsets.
- Ensure "Exclusions" are logical (e.g. dont show TOF ads to recent buyers).

JSON FORMAT:
{{
  "clusters": [
    {{
      "funnel_stage": "TOF",
      "cluster_name": "Broad Lifestyle & Wellness",
      "interests": ["Physical fitness", "Meditation", "Healthy diet"], 
      "behaviors": ["Engaged Shoppers"],
      "placement": "Advantage+",
      "exclusions": {{ "interests": [], "behaviors": [], "custom_audiences": ["Purchasers (180d)"] }},
      "reasoning": "Broad net to catch high-affinity users."
    }},
    {{
      "funnel_stage": "MOF",
      "cluster_name": "Niche Yoga Enthusiasts",
      "interests": ["Lululemon", "Manduka", "Bikram Yoga"],
      "behaviors": ["Frequent Travelers"],
      "placement": "Manual (Feeds/Stories)",
      "exclusions": {{ "interests": ["Zumba"], "behaviors": [], "custom_audiences": ["Purchasers (30d)"] }},
      "reasoning": "Targeting specific brand affinity for higher conversion."
    }}
  ]
}}
"""),
    ("user", "Architect Meta Adsets. Product: {product}, Category: {category}, Persona: {persona_name}. Mapped Data: {targeting_map}")
])

class MetaClusterWrapper:
    @staticmethod
    def build_clusters(llm_client: LLMClient, persona: Dict[str, Any], brand_data: Dict[str, Any], targeting_map: Dict[str, Any] = None) -> List[InterestCluster]:
        try:
            chain = META_CLUSTER_PROMPT | llm_client.llm
            result = chain.invoke({
                "product": brand_data.get("brand_name"),
                "category": brand_data.get("product_category"),
                "price_position": brand_data.get("price_positioning"),
                "persona_name": persona.get("name"),
                "profession": persona.get("profession"),
                "pain_points": ", ".join(persona.get("pain_points", [])),
                "usp": brand_data.get("primary_usp", "Generic Quality"),
                "targeting_map": json.dumps(targeting_map) if targeting_map else "No specific map provided."
            })
            
            content = result.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            start = content.find('{')
            end = content.rfind('}')
            if start != -1 and end != -1:
                content = content[start:end+1]
            
            data = json.loads(content)
            
            if "clusters" in data:
                clusters = [InterestCluster(**c) for c in data["clusters"]]
                if not (2 <= len(clusters) <= 4):
                     print(f"Warning: Meta Cluster count {len(clusters)} is outside 2-4 range.")
                
                return clusters
            return []
        except Exception as e:
            print(f"Meta Cluster Wrap Error: {e}")
            return []
