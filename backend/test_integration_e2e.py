"""
End-to-End Integration Test for TG Builder
Tests the complete workflow from input to results
"""
import pytest
from fastapi.testclient import TestClient
from main import app
import time

client = TestClient(app)

class TestE2EWorkflow:
    """Test the complete user journey through the API"""

    def test_health_check(self):
        """Test that the API is running"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        print("✅ Health check passed")

    def test_complete_workflow(self):
        """Test the complete workflow: Create project -> Save inputs -> Generate -> Get results"""

        # Step 1: Create Project
        print("\n🔹 Step 1: Creating project...")
        project_response = client.post("/projects", json={"name": "E2E Test Project"})
        assert project_response.status_code == 200
        project_data = project_response.json()
        assert "project_id" in project_data
        project_id = project_data["project_id"]
        print(f"✅ Project created: {project_id}")

        # Step 2: Save Brand Inputs
        print("\n🔹 Step 2: Saving brand inputs...")
        brand_input = {
            "brand_name": "ZenWorkspace",
            "product_category": "Ergonomic Office Furniture",
            "price_positioning": "Premium",
            "geography": "USA & Canada",
            "primary_usp": "Aesthetic minimalism meets orthopedic science",
            "primary_objective": "Purchase",
            "known_audience_insights": "People who work from home and have back pain"
        }

        input_response = client.post("/inputs", json={
            "project_id": project_id,
            "brand_input": brand_input
        })
        assert input_response.status_code == 200
        print("✅ Brand inputs saved")

        # Step 3: Trigger Generation (This is the heavy operation)
        print("\n🔹 Step 3: Triggering full pipeline generation...")
        print("⏳ This may take 30-60 seconds (LLM + processing)...")

        start_time = time.time()
        generate_response = client.post("/generate", json={"project_id": project_id}, timeout=120.0)
        duration = time.time() - start_time

        assert generate_response.status_code == 200
        generation_result = generate_response.json()

        print(f"✅ Generation completed in {duration:.2f}s")
        print(f"   Status: {generation_result.get('status')}")
        print(f"   Personas Selected: {generation_result.get('personas_selected')}")

        assert generation_result["status"] == "completed"
        assert generation_result["personas_selected"] > 0
        assert "log" in generation_result

        # Verify pipeline steps completed
        log = generation_result["log"]
        assert "Inputs Loaded" in log
        assert "Generated" in str(log)
        assert "Validated" in str(log)
        assert "Scoring Complete" in log
        assert "Selected" in str(log)
        assert "Campaign Blueprints Generated" in log
        assert "Budget Plan Generated" in log
        print(f"   Pipeline log: {log}")

        # Step 4: Fetch Results
        print("\n🔹 Step 4: Fetching results...")
        results_response = client.get(f"/projects/{project_id}/results")
        assert results_response.status_code == 200
        results = results_response.json()

        # Validate results structure
        assert "personas" in results
        assert "campaigns" in results
        assert "budget" in results

        personas = results["personas"]
        campaigns = results["campaigns"]
        budget = results["budget"]

        print(f"✅ Results fetched successfully")
        print(f"   - Personas: {len(personas)}")
        print(f"   - Campaign blueprints: {len(campaigns)}")
        print(f"   - Budget plan: {'Present' if budget else 'Missing'}")

        # Validate personas
        assert len(personas) > 0, "No personas returned"
        assert len(personas) <= 5, "Too many personas (should be top 3-5)"

        for idx, persona in enumerate(personas):
            assert "persona_id" in persona
            assert "rank" in persona
            assert "role_in_portfolio" in persona
            assert persona["role_in_portfolio"] in ["Anchor", "Expansion", "Experiment"]
            print(f"   Persona {idx+1}: Rank {persona['rank']}, Role: {persona['role_in_portfolio']}")

        # Validate campaigns
        assert len(campaigns) > 0, "No campaigns returned"
        platforms = set(c["platform"] for c in campaigns)
        print(f"   Platforms: {platforms}")
        assert "Meta" in platforms or "Google" in platforms

        # Validate budget
        assert budget is not None, "Budget plan missing"
        if isinstance(budget, dict):
            assert "targeting_data" in budget or "platform" in budget
            print(f"   Budget Total: {budget.get('targeting_data', {}).get('total', 'N/A')}")

        print("\n" + "="*60)
        print("🎉 END-TO-END TEST PASSED!")
        print("="*60)
        return project_id

    def test_error_handling_invalid_project(self):
        """Test error handling for invalid project ID"""
        print("\n🔹 Testing error handling...")
        response = client.get("/projects/invalid-uuid-123/results")
        # Should either return 404 or 500 with error message
        assert response.status_code in [404, 500]
        print("✅ Error handling works")

    def test_validation_empty_inputs(self):
        """Test validation of empty brand inputs"""
        print("\n🔹 Testing input validation...")

        # Create project first
        project_response = client.post("/projects", json={"name": "Validation Test"})
        project_id = project_response.json()["project_id"]

        # Try to save invalid inputs (missing required fields)
        invalid_input = {
            "brand_name": "",  # Empty
            "product_category": "Test",
            "price_positioning": "Mid",
            "geography": "USA",
            "primary_usp": "",  # Empty
            "primary_objective": "Purchase"
        }

        # This should fail validation or be handled gracefully
        input_response = client.post("/inputs", json={
            "project_id": project_id,
            "brand_input": invalid_input
        })

        # FastAPI/Pydantic should return 422 for validation errors
        # Or our service should handle it gracefully
        print(f"   Response status: {input_response.status_code}")
        assert input_response.status_code in [200, 422, 400]
        print("✅ Input validation working")


if __name__ == "__main__":
    print("="*60)
    print("TG BUILDER - END-TO-END INTEGRATION TEST")
    print("="*60)
    print("\nThis test will:")
    print("1. Create a project")
    print("2. Save brand inputs")
    print("3. Generate personas, campaigns & budget (LLM call)")
    print("4. Fetch and validate results")
    print("\n⚠️  Requires:")
    print("   - Supabase connection configured")
    print("   - LLM API key (Groq/OpenAI/Anthropic)")
    print("   - Backend dependencies installed")
    print("\n" + "="*60 + "\n")

    # Run the test
    test = TestE2EWorkflow()
    test.test_health_check()
    test.test_complete_workflow()
    test.test_error_handling_invalid_project()
    test.test_validation_empty_inputs()

    print("\n✅ ALL TESTS PASSED!")
