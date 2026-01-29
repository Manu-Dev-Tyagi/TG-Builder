from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json
from src.llm import LLMClient
from src.models_campaign import GoogleAudienceSignals
from typing import Dict, Any

GOOGLE_SIGNAL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Google Ads Audience Architect.
Generate audience signals optimized for a {campaign_type} campaign.

ADAPTATION RULES:
- If Search: 'custom_segments' must be high-intent search terms (e.g., 'buy [product]', '[product] reviews').
- If Demand Gen/YouTube/Display: 'custom_segments' must be interests, URLs of competitors, or app names.
- If P-Max: Blend broad intent with specific high-value behaviors.

STRICT FORMAT RULES:
1. MANDATORY FIELDS: 'in_market', 'affinity', 'custom_segments', and 'demographics'.
2. EMPTY STATE: return [] if no relevant segments found.
3. Return ONLY raw JSON.

REQUIRED OUTPUT FORMAT (JSON):
{
  "in_market": ["segment1", "segment2"],
  "affinity": ["segment1", "segment2"],
  "custom_segments": ["term/interest 1", "term/interest 2"],
  "demographics": "Detailed demographic description (Age, Gender, Household Income)"
}

INPUTS:
Campaign Type: {campaign_type}
Profession: {profession}
Interests: {interests}
Pain Points: {pain_points}
"""),
    ("user", "Generate the signals strictly for {campaign_type}. Return ONLY raw JSON.")
])

class GoogleAudienceSignalWrapper:
    @staticmethod
    def generate_signals(llm_client: LLMClient, persona: Dict[str, Any], campaign_type: str) -> GoogleAudienceSignals:
        try:
            chain = GOOGLE_SIGNAL_PROMPT | llm_client.llm
            result = chain.invoke({
                "campaign_type": campaign_type,
                "persona_name": persona.get("name"),
                "profession": persona.get("profession"),
                "interests": ", ".join(persona.get("interests", [])),
                "pain_points": ", ".join(persona.get("pain_points", []))
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
            return GoogleAudienceSignals(**data)
        except Exception as e:
            print(f"Google Signal Wrap Error: {e}")
            return GoogleAudienceSignals()
