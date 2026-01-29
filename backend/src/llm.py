import os
from typing import Literal, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser

from src.schemas.persona_schema import PersonaContractList
from src.prompts import PERSONA_GENERATION_PROMPT
from src.config import Config

load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI

class LLMClient:
    def __init__(self, provider: Literal["openai", "anthropic", "groq", "google"] = "groq", model_name: Optional[str] = None):
        self.provider = provider
        
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            self.llm = ChatOpenAI(
                model=model_name or "gpt-4-turbo",
                temperature=0.0,
                api_key=api_key
            )
        elif provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            self.llm = ChatAnthropic(
                model=model_name or "claude-3-opus-20240229",
                temperature=0.0,
                api_key=api_key
            )
        elif provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables")
            self.llm = ChatGroq(
                model=model_name or Config.DEFAULT_MODEL,
                temperature=0.0,
                api_key=api_key
            )
        elif provider == "google":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment variables")
            self.llm = ChatGoogleGenerativeAI(
                model=model_name or "gemini-2.0-flash",
                temperature=0.0,
                google_api_key=api_key
            )
        else:
            raise ValueError("Invalid provider. Choose 'openai', 'anthropic', 'groq', or 'google'")

    def generate_personas(
        self, 
        brand_name: str, 
        product_category: str, 
        price_positioning: str,
        primary_usp: str,
        primary_objective: str,
        known_audience_insights: str = "",
        count: int = 3,
        geography: str = "Global",
        campaign_context: str = "General"
    ) -> PersonaContractList:
        """
        Generates a list of personas based on brand inputs.
        """
        parser = PydanticOutputParser(pydantic_object=PersonaContractList)
        
        chain = PERSONA_GENERATION_PROMPT | self.llm
        
        response = chain.invoke({
            "count": count,
            "brand_name": brand_name,
            "product_category": product_category,
            "price_positioning": price_positioning,
            "primary_usp": primary_usp,
            "primary_objective": primary_objective,
            "known_audience_insights": known_audience_insights,
            "geography": geography,
            "campaign_context": campaign_context,
            "format_instructions": parser.get_format_instructions()
        })

        content = response.content.strip()
        # Clean up common LLM artifacts
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        # Robust JSON extraction: Find first '{' and last '}'
        start = content.find('{')
        end = content.rfind('}')
        if start != -1 and end != -1:
            content = content[start:end+1]
            
        # JSON REPAIR: Remove trailing commas before closing braces/brackets
        # Matches: , followed by whitespace and } or ]
        import re
        content = re.sub(r',\s*([\]}])', r'\1', content)
            
        return parser.parse(content)

if __name__ == "__main__":
    # Example usage (will fail without API keys)
    try:
        client = LLMClient(provider="openai") 
        # result = client.generate_personas("FitLife", "Fitness App", "Mid-range")
        # print(result)
        print("LLM Client initialized successfully.")
    except Exception as e:
        print(f"Initialization check: {e}")
