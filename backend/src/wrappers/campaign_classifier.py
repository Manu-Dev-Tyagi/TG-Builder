from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.llm import LLMClient
from typing import Dict, Any

CAMPAIGN_CLASSIFIER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Strict Strategy Gatekeeper.
Your goal is to map a persona/goal to a specific campaign type ONLY if the evidence is overwhelming.

INPUTS:
Platform: {platform}
Brand Goal: {goal}
Marketing Flow: {flow}
Persona: {persona_name} (Archetype: {profession})
Buying Behavior: {behavior}

STRICT MAPPING RULES:
1. If brand goal is 'Purchase' AND buying behavior triggers involve 'immediate need' -> Sales (Purchase Focus)
2. If brand goal is 'Leads' AND flow is 'Form' -> Leads (Lead Capture)
3. If brand goal is 'Leads' AND flow is 'Website' -> Leads (Website Conversion)
4. IF THE INPUTS ARE AMBIGUOUS, MISSING INTENT, OR CONTRADICTORY -> RETURN 'NA'

RULES OF CONDUCT:
- DO NOT GUESS.
- DO NOT INFER MISSING DATA.
- IF IN DOUBT, RETURN 'NA'.
- Output ONLY the string.
"""),
    ("user", "Classify this campaign. If not 100% sure, return 'NA'.")
])

ALLOWED_CAMPAIGNS = ["Sales (Purchase Focus)", "Leads (Lead Capture)", "Leads (Website Conversion)"]

class CampaignClassifierWrapper:
    @staticmethod
    def classify(llm_client: LLMClient, platform: str, goal: str, flow: str, persona: Dict[str, Any]) -> str:
        """
        Judge-model for Campaign Type. 
        Splits Semantic 'NA' from Technical 'ERROR'.
        """
        try:
            chain = CAMPAIGN_CLASSIFIER_PROMPT | llm_client.llm | StrOutputParser()
            
            result = chain.invoke({
                "platform": platform,
                "goal": goal,
                "flow": flow,
                "persona_name": persona.get("name"),
                "profession": persona.get("profession"),
                "behavior": str(persona.get("buying_behavior"))
            })
            
            classified = result.strip()
            
            # Enum Validation
            if classified in ALLOWED_CAMPAIGNS:
                return classified
            
            # Semantic NA
            return "NA"

        except Exception as e:
            print(f"Campaign Classification TECHNICAL ERROR: {e}")
            return "ERROR"
