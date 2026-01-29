#!/usr/bin/env python
# coding: utf-8

# # TG Builder Logic Playground

# In[ ]:


# %load_ext autoreload
# %autoreload 2

import sys
import os

# Add current directory to path so we can import src
sys.path.append(os.getcwd())


# In[ ]:


from src.llm import LLMClient
from src.services import ProjectService, InputService
from src.models import BrandInputCreate


# In[ ]:


# 1. Create a Project
try:
    project_id = ProjectService.create_project("Manual Test Run 1")
    print(f"Created Project ID: {project_id}")
except Exception as e:
    print(f"Project creation failed: {e}")


# In[ ]:


# 2. Define Brand Input (User data)
raw_input = BrandInputCreate(
    brand_name="  FitLife Pro  ",  # Space to test normalization
    product_category="Fitness App",
    price_positioning="Premium",
    geography="India Tier-1",
    primary_usp="AI-driven personalized workouts",
    primary_objective="App Install",
    age_ranges=["25-35"],
    known_audience_insights="Users usually like Yoga"
)

# 3. Normalize Input
clean_input = InputService.normalize_input(raw_input)
print(f"Normalized Brand Name: '{clean_input.brand_name}'")

# 4. Save to DB
try:
    input_id = InputService.save_brand_input(project_id, clean_input)
    print(f"Saved Input ID: {input_id}")
except Exception as e:
    print(f"Input save failed: {e}")


# In[ ]:


# 5. Generate Personas (Optional test)
# client = LLMClient(provider="groq")
# personas = client.generate_personas(
#     brand_name=clean_input.brand_name,
#     product_category=clean_input.product_category,
#     price_positioning=clean_input.price_positioning,
#     primary_usp=clean_input.primary_usp,
#     primary_objective=clean_input.primary_objective,
#     known_audience_insights=clean_input.known_audience_insights
# )
# print(f"Generated {len(personas.personas)} personas")

