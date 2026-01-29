-- Migration: Add missing columns to brand_inputs table
-- These columns were added to the backend models for deterministic gating

-- Add price_sensitivity column (required for scoring)
ALTER TABLE brand_inputs 
ADD COLUMN IF NOT EXISTS price_sensitivity TEXT DEFAULT 'Medium';

-- Add decision_speed column (required for strategy locking)
ALTER TABLE brand_inputs 
ADD COLUMN IF NOT EXISTS decision_speed TEXT DEFAULT 'Normal';

-- Add platform_affinity column (JSONB array of preferred platforms)
ALTER TABLE brand_inputs 
ADD COLUMN IF NOT EXISTS platform_affinity JSONB DEFAULT '[]'::jsonb;

-- Add budget_range column (optional, for budget-aware recommendations)
ALTER TABLE brand_inputs 
ADD COLUMN IF NOT EXISTS budget_range TEXT;

-- Add strategy_depth column (controls full_funnel vs classification_only)
ALTER TABLE brand_inputs 
ADD COLUMN IF NOT EXISTS strategy_depth TEXT DEFAULT 'classification_only';

-- Add comments for documentation
COMMENT ON COLUMN brand_inputs.price_sensitivity IS 'High/Medium/Low - affects pricing recommendations';
COMMENT ON COLUMN brand_inputs.decision_speed IS 'Fast/Normal/Slow - affects campaign type selection';
COMMENT ON COLUMN brand_inputs.platform_affinity IS 'Array of preferred ad platforms (e.g. ["Meta", "Google"])';
COMMENT ON COLUMN brand_inputs.budget_range IS 'Optional budget range string (e.g. "$1k-$5k")';
COMMENT ON COLUMN brand_inputs.strategy_depth IS 'classification_only or full_funnel - controls output depth';
