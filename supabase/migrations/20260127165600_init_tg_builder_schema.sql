-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Projects Table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Brand Inputs Table
CREATE TABLE IF NOT EXISTS brand_inputs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE NOT NULL,
    brand_name TEXT NOT NULL,
    product_category TEXT NOT NULL,
    price_positioning TEXT NOT NULL, -- 'low', 'mid', 'premium'
    geography TEXT NOT NULL,         -- 'India', 'US', 'Tier-1', etc.
    primary_usp TEXT NOT NULL,
    primary_objective TEXT NOT NULL, -- 'leads', 'purchase', 'app_install'
    age_ranges JSONB,                -- Array of strings or objects
    cities JSONB,                    -- Array of strings
    professions JSONB,               -- Array of strings
    known_audience_insights TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Raw Personas Table (LLM Output)
CREATE TABLE IF NOT EXISTS raw_personas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE NOT NULL,
    persona_name TEXT NOT NULL,
    persona_data JSONB NOT NULL,     -- Full persona object
    llm_model TEXT,
    prompt_version TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Persona Scores Table (Deterministic Logic Output)
CREATE TABLE IF NOT EXISTS persona_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    persona_id UUID REFERENCES raw_personas(id) ON DELETE CASCADE NOT NULL,
    objective_fit_score NUMERIC CHECK (objective_fit_score >= 0 AND objective_fit_score <= 100),
    price_fit_score NUMERIC CHECK (price_fit_score >= 0 AND price_fit_score <= 100),
    geography_fit_score NUMERIC CHECK (geography_fit_score >= 0 AND geography_fit_score <= 100),
    funnel_fit_score NUMERIC CHECK (funnel_fit_score >= 0 AND funnel_fit_score <= 100),
    ads_feasibility_score NUMERIC CHECK (ads_feasibility_score >= 0 AND ads_feasibility_score <= 100),
    total_score NUMERIC CHECK (total_score >= 0 AND total_score <= 100),
    score_breakdown JSONB,           -- Detailed scoring log
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Final Personas Table (Selected Top 3-5)
CREATE TABLE IF NOT EXISTS final_personas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    persona_id UUID REFERENCES raw_personas(id) ON DELETE CASCADE NOT NULL,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE NOT NULL,
    rank INTEGER CHECK (rank > 0),
    reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Targeting Blueprints Table (Platform Ready Output)
CREATE TABLE IF NOT EXISTS targeting_blueprints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE NOT NULL,
    persona_id UUID REFERENCES raw_personas(id) ON DELETE CASCADE NOT NULL,
    platform TEXT NOT NULL,          -- 'meta', 'google', etc.
    funnel_stage TEXT NOT NULL,      -- 'top', 'mid', 'bottom'
    targeting_data JSONB NOT NULL,   -- Platform specific targeting JSON
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_brand_inputs_project_id ON brand_inputs(project_id);
CREATE INDEX IF NOT EXISTS idx_raw_personas_project_id ON raw_personas(project_id);
CREATE INDEX IF NOT EXISTS idx_persona_scores_persona_id ON persona_scores(persona_id);
CREATE INDEX IF NOT EXISTS idx_final_personas_project_id ON final_personas(project_id);
CREATE INDEX IF NOT EXISTS idx_final_personas_persona_id ON final_personas(persona_id);
CREATE INDEX IF NOT EXISTS idx_targeting_blueprints_project_id ON targeting_blueprints(project_id);
CREATE INDEX IF NOT EXISTS idx_targeting_blueprints_persona_id ON targeting_blueprints(persona_id);

-- Add comments for documentation
COMMENT ON TABLE projects IS 'Stores one row per TG Builder run/project';
COMMENT ON TABLE brand_inputs IS 'Stores exact user inputs for replayability';
COMMENT ON TABLE raw_personas IS 'Stores raw LLM-generated personas before scoring';
COMMENT ON TABLE persona_scores IS 'Stores deterministic scoring results for personas';
COMMENT ON TABLE final_personas IS 'Stores the selected top personas for the UI';
COMMENT ON TABLE targeting_blueprints IS 'Stores platform-ready targeting instructions';
