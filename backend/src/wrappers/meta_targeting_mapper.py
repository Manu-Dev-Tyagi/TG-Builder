from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.llm import LLMClient
from typing import Dict, Any, List

META_TARGETING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Meta Ads Targeting Specialist. 
Your goal is to map a product to the EXACT categories found in the Alchemy Marketing source.

STRICT FORMAT RULES:
1. Return ONLY raw JSON.
2. The JSON must have keys: "demographics", "interests", "behaviors".
3. Values must be arrays of STRINGS.
4. Use the exact sub-heading names from the repository (e.g., 'Home Ownership', 'Life Events').
5. If a value does not exist in the source link, do NOT include it.

DATA REPOSITORY REFERENCE:
- Demographics: Home Ownership, Home Type, Life Events, Parents, Moms, Financial (Income), Relationship Status, Work.
- Interests: Business and Industry, Entertainment, Family and Relationships, Fitness and Wellness, Food and Drink, Hobbies and Activities (includes Home and Garden), Shopping and Fashion, Technology.
- Behaviors: Purchase Behavior, Residential Profiles, Consumer Classification, Digital Device User, Travel.

REQUIRED OUTPUT FORMAT:
{{
  "demographics": ["Value 1", "Value 2"],
  "interests": ["Value 3", "Value 4"],
  "behaviors": ["Value 5"]
}}
"""),
    ("user", "Industry/Product: {product}\n\nMap all relevant data points from the link properly. Return only JSON.")
])

class MetaTargetingWrapper:
    @staticmethod
    def map_interests(llm_client: LLMClient, product: str) -> Dict[str, List[str]]:
        try:
            chain = META_TARGETING_PROMPT | llm_client.llm
            result = chain.invoke({"product": product})
            
            content = result.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            import json
            start = content.find('{')
            end = content.rfind('}')
            if start != -1 and end != -1:
                content = content[start:end+1]
            
            data = json.loads(content)
            return {
                "demographics": data.get("demographics", []),
                "interests": data.get("interests", []),
                "behaviors": data.get("behaviors", [])
            }
        except Exception as e:
            print(f"Meta Targeting Map Error: {e}")
            return {"demographics": [], "interests": [], "behaviors": []}
