-- Add missing columns to final_personas table
ALTER TABLE final_personas
ADD COLUMN IF NOT EXISTS role_in_portfolio TEXT,
ADD COLUMN IF NOT EXISTS funnel_stage TEXT,
ADD COLUMN IF NOT EXISTS recommended_platforms JSONB,
ADD COLUMN IF NOT EXISTS notes TEXT;

-- Add comments
COMMENT ON COLUMN final_personas.role_in_portfolio IS 'Anchor, Expansion, or Experiment';
COMMENT ON COLUMN final_personas.funnel_stage IS 'Top, Middle, or Bottom of funnel';
COMMENT ON COLUMN final_personas.recommended_platforms IS 'Array of recommended ad platforms';
