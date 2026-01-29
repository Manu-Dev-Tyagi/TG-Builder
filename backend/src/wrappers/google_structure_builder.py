from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json
from src.llm import LLMClient
from src.models_campaign import GoogleAdGroup, GoogleKeywordGroup, GoogleAudienceSignals
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# Internal Models for JSON Parsing
class KeywordGroupOut(BaseModel):
    theme: str
    match_type: str  # Exact, Phrase, Broad
    keywords: List[str]

class AudienceSignalOut(BaseModel):
    in_market: List[str]
    affinity: List[str]
    custom_segments: List[str]

class AdGroupOut(BaseModel):
    name: str
    campaign_type: str  # Search, PMax, Demand Gen
    intent: str
    keywords: List[KeywordGroupOut]
    audience_signals: AudienceSignalOut

class GoogleStructureOut(BaseModel):
    adgroups: List[AdGroupOut]

GOOGLE_STRUCTURE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Google Ads Technical Architect (Top 1%).
Your goal is to design a granular Google Ads Structure for a single persona.

CAMPAIGN TYPES:
1. Search (Intent Capture): For high-intent triggers.
2. Performance Max (PMax): For blended intent/awareness (retail/ecom).
3. Demand Gen: For visual storytelling (YouTube/Discovery).

STRUCTURE RULES:
- Generate 2-3 Ad Groups per persona.
- For Search: MUST include specific Keyword Themes with Match Types.
  - "Exact": High intent, specific queries.
  - "Phrase": Moderate intent.
  - "Broad": Discovery.
- For PMax/Demand Gen: MUST define Audience Signals (In-Market, Affinity, Custom Segments).

EXAMPLE JSON:
{{
  "adgroups": [
    {{
      "name": "GOOGLE | Search | High Intent",
      "campaign_type": "Search",
      "intent": "Conversion",
      "keywords": [
        {{ "theme": "Buy Specific Model", "match_type": "Exact", "keywords": ["buy running shoes online", "best marathon shoes 2024"] }},
        {{ "theme": "Feature Discovery", "match_type": "Phrase", "keywords": ["cushioned sneakers", "shoes for knee pain"] }}
      ],
      "audience_signals": {{ "in_market": [], "affinity": [], "custom_segments": [] }}
    }},
    {{
      "name": "GOOGLE | PMax | Lifestyle Overlay",
      "campaign_type": "Performance Max",
      "intent": "Awareness",
      "keywords": [],
      "audience_signals": {{
        "in_market": ["Apparel & Accessories/Shoes"],
        "affinity": ["Health & Fitness Buffs"],
        "custom_segments": ["People researching marathon training"]
      }}
    }}
  ]
}}
"""),
    ("user", "Architect Google Structure. Product: {product}, Category: {category}, Persona: {persona_name}. Triggers: {triggers}")
])

class GoogleStructureBuilder:
    @staticmethod
    def build_structure(llm_client: LLMClient, persona: Dict[str, Any], brand_data: Dict[str, Any]) -> List[GoogleAdGroup]:
        try:
            chain = GOOGLE_STRUCTURE_PROMPT | llm_client.llm
            result = chain.invoke({
                "product": brand_data.get("brand_name"),
                "category": brand_data.get("product_category"),
                "persona_name": persona.get("name"),
                "triggers": str(persona.get("buying_behavior", {}).get("purchase_triggers", [])),
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
            
            final_adgroups = []
            if "adgroups" in data:
                for ag_raw in data["adgroups"]:
                    # Convert raw JSON to Models
                    kws = [GoogleKeywordGroup(**k) for k in ag_raw.get("keywords", [])]
                    sigs_raw = ag_raw.get("audience_signals", {})
                    sigs = GoogleAudienceSignals(
                        in_market=sigs_raw.get("in_market", []),
                        affinity=sigs_raw.get("affinity", []),
                        custom_segments=sigs_raw.get("custom_segments", [])
                    )
                    
                    ag = GoogleAdGroup(
                        name=ag_raw["name"],
                        campaign_type=ag_raw["campaign_type"],
                        intent=ag_raw["intent"],
                        keywords=kws,
                        audience_signals=sigs
                    )
                    final_adgroups.append(ag)
                    
            return final_adgroups

        except Exception as e:
            print(f"Google Structure Builder ERROR: {e}")
            return []
