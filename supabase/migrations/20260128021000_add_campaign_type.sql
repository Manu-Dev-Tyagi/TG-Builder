-- Add campaign_type column to final_personas
ALTER TABLE final_personas ADD COLUMN IF NOT EXISTS campaign_type TEXT DEFAULT 'NA';
