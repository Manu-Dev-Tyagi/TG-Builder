from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from src.llm import LLMClient
from typing import Dict, Any, List
from pydantic import BaseModel, Field

class PlatformDecision(BaseModel):
    platforms: List[str] = Field(..., description="List containing 'Meta', 'Google', or both")
    rationale: str = Field(..., description="Explain why these platforms were chosen based on buying behavior")

PLATFORM_DECISION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Media Channel Strategist.
Your goal is to decide the best advertising platforms (Meta, Google, or Both) for a specific persona.

INPUTS:
Persona Profession: {profession}
Buying Habits: {habits}
Purchase Triggers: {triggers}
Decision Speed: {speed}

DECISION RULES:
1. If 'High Search Intent' or 'Specific Need Discovery' is a trigger -> Must include Google.
2. If 'Impulse', 'Social Proof', or 'Aspiration' driven -> Must include Meta.
3. If decision speed is 'Fast' and search intent is low -> Prioritize Meta.
4. If it's a 'Considered Purchase' (Slow/Normal) -> Usually 'Both' to capture intent and nurture.

OUTPUT FORMAT (JSON):
{{
  "platforms": ["Meta", "Google"],
  "rationale": "Detailed explanation..."
}}
"""),
    ("user", "Decide the platform strategy. Return ONLY raw JSON.")
])

ALLOWED_PLATFORMS = ["Meta", "Google"]

class PlatformDecisionWrapper:
    @staticmethod
    def decide(llm_client: LLMClient, persona: Dict[str, Any]) -> PlatformDecision:
        """
        Deterministic Platform Gatekeeper.
        Splits TECHNICAL ERROR from SEMANTIC NA.
        """
        try:
            chain = PLATFORM_DECISION_PROMPT | llm_client.llm
            bh = persona.get("buying_behavior", {})
            
            # 1. LLM Semantic Classification
            result = chain.invoke({
                "profession": persona.get("profession"),
                "habits": ", ".join(bh.get("habits", []) if hasattr(bh, 'get') else []), 
                "triggers": ", ".join(bh.get("purchase_triggers", []) if hasattr(bh, 'get') else []),
                "speed": bh.get("decision_speed", "Normal") if hasattr(bh, 'get') else "Normal"
            })
            
            import json
            content = result.content.strip()
            # Robust extraction logic repeated for stability
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            start = content.find('{')
            end = content.rfind('}')
            if start != -1 and end != -1:
                content = content[start:end+1]
            
            data = json.loads(content)
            decision = PlatformDecision(**data)
            
            # 2. Enum Validation (Constraint 3)
            # Filter platforms to only allowed values
            decision.platforms = [p for p in decision.platforms if p in ALLOWED_PLATFORMS]
            if not decision.platforms:
                return PlatformDecision(platforms=["NA"], rationale="Semantic rejection: No strong platform alignment found.")
                
            return decision

        except json.JSONDecodeError:
            return PlatformDecision(platforms=["NA"], rationale="Semantic rejection: Model output was non-deterministic.")
        except Exception as e:
            print(f"Platform Decision TECHNICAL ERROR: {e}")
            # Technical failure returns a state that can be flagged separately from a 'Reasoned NA'
            return PlatformDecision(platforms=["ERROR"], rationale=f"Technical Failure: {str(e)}")
