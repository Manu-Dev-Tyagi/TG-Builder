from src.llm import LLMClient
from src.services import ProjectService, InputService
from src.services_persona import PersonaService
from src.models import BrandInputCreate
from src.config import Config
import time

def run_phase_2(project_id: str = None, input_id: str = None):
    print("🚀 Starting Phase 2 Test: Persona Generation")
    
    # 0. Setup Context (Same as Phase 1 if passed, or create new)
    if not project_id:
        print("Creating new project for context...")
        project_id = ProjectService.create_project("Phase 2 Test Run")
        
        raw_input = BrandInputCreate(
            brand_name="ZenWorkspace",
            product_category="Ergonomic Office Furniture",
            price_positioning="Premium",
            geography="USA & Canada",
            primary_usp="Aesthetic minimalism meets orthopedic science",
            primary_objective="Purchase",
            known_audience_insights="People who work from home and have back pain"
        )
        input_data = InputService.normalize_input(raw_input)
        InputService.save_brand_input(project_id, input_data)
        print(f"Created Project: {project_id}")
    else:
        # Fetch input data (mocking fetch for now since we have the object in memory in a real app flow)
        # For this test script, we'll re-declare the input if not passed, but let's stick to creating new for isolation.
        pass

    # Re-declare input for LLM call convenience in this script
    input_data = BrandInputCreate(
        brand_name="ZenWorkspace",
        product_category="Ergonomic Office Furniture",
        price_positioning="Premium",
        geography="USA & Canada",
        primary_usp="Aesthetic minimalism meets orthopedic science",
        primary_objective="Purchase",
        known_audience_insights="People who work from home and have back pain"
    )

    # 1. Initialize LLM
    client = LLMClient(provider="groq")
    print(f"🤖 LLM Client Ready. Model: {Config.DEFAULT_MODEL}")
    print(f"Generating {Config.DEFAULT_GENERATION_COUNT} personas...")
    
    start_time = time.time()
    
    # 2. Call LLM
    try:
        personas_result = client.generate_personas(
            brand_name=input_data.brand_name,
            product_category=input_data.product_category,
            price_positioning=input_data.price_positioning,
            primary_usp=input_data.primary_usp,
            primary_objective=input_data.primary_objective,
            known_audience_insights=input_data.known_audience_insights,
            count=Config.DEFAULT_GENERATION_COUNT
        )
    except Exception as e:
        print(f"❌ LLM Generation Failed: {e}")
        return

    duration = time.time() - start_time
    print(f"✅ Generation Complete in {duration:.2f}s")
    print(f"Generated {len(personas_result.personas)} personas.")

    # 3. Save to DB
    try:
        saved_count = PersonaService.save_raw_personas(
            project_id=project_id,
            personas=personas_result,
            llm_model=Config.DEFAULT_MODEL
        )
        print(f"💾 Saved {saved_count} personas to DB (table: raw_personas)")
    except Exception as e:
        print(f"❌ DB Save Failed: {e}")
        return

    # 4. Verify & Inspect
    print("\n--- Sample Persona 1 ---")
    p1 = personas_result.personas[0]
    print(f"Name: {p1.name}")
    print(f"Role: {p1.funnel_role}")
    print(f"Motivations: {p1.motivations}")
    print("------------------------")

if __name__ == "__main__":
    run_phase_2()
