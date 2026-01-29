from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.llm import LLMClient
from typing import Dict, Any

GOOGLE_CLASSIFIER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Google Ads Campaign Architect.
Classify the ideal Google Ads campaign structure for this persona.

INPUTS:
Persona: {persona_name}
Triggers: {triggers}
Purchase Intensity: {speed}

RULES:
1. Return EXACTLY one of:
   - Search (Intent Capture)
   - Performance Max (Cross-Channel)
   - Shopping (Product Sales)
   - Display (Awareness)
   - YouTube (Consideration)

2. If the persona has high 'search intent' in triggers, prioritize Search.
3. If they are 'Fast' decision makers and it's a physical product, prioritize Shopping or P-Max.
4. Output ONLY the string. No text before or after.
"""),
    ("user", "Classify Google campaign.")
])

ALLOWED_GOOGLE_STRUCTURES = [
    "Search (Intent Capture)", 
    "Performance Max (Cross-Channel)", 
    "Shopping (Product Sales)",
    "Display (Awareness)", 
    "YouTube (Consideration)",
    "Demand Gen (Visual Feed)"
]

class GoogleClassifierWrapper:
    @staticmethod
    def classify(llm_client: LLMClient, persona: Dict[str, Any]) -> str:
        """
        Judge-model for Google Campaign Structure.
        Splits Semantic Empty from Technical ERROR.
        """
        # Check if Google is even a platform affinity
        affinity = persona.get("platform_affinity", [])
        if "Google" not in affinity:
            return ""

        try:
            chain = GOOGLE_CLASSIFIER_PROMPT | llm_client.llm | StrOutputParser()
            
            result = chain.invoke({
                "persona_name": persona.get("name"),
                "triggers": str(persona.get("buying_behavior", {}).get("purchase_triggers", [])),
                "speed": persona.get("buying_behavior", {}).get("decision_speed", "Normal")
            })
            
            final_result = result.strip()
            
            # 1. Exact Match Validation
            if final_result in ALLOWED_GOOGLE_STRUCTURES:
                return final_result
            
            # 2. Fuzzy Match Validation (Locked to Enum)
            for opt in ALLOWED_GOOGLE_STRUCTURES:
                if opt.split(" (")[0].lower() in final_result.lower():
                    return opt
            
            # Semantic rejection
            return ""

        except Exception as e:
            print(f"Google Classification TECHNICAL ERROR: {e}")
            return "ERROR"
