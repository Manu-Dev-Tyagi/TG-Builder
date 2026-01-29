-- Migration: Flatten final_personas and update project schema
-- Aligns DB with Phase 4/5 Refactor (Deterministic Gating & Auditability)

-- 1. Update final_personas table
ALTER TABLE final_personas 
ADD COLUMN IF NOT EXISTS name TEXT,
ADD COLUMN IF NOT EXISTS role_in_portfolio TEXT,
ADD COLUMN IF NOT EXISTS funnel_stage TEXT,
ADD COLUMN IF NOT EXISTS campaign_type TEXT DEFAULT 'Unclassified',
ADD COLUMN IF NOT EXISTS recommended_platforms JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS platform_decisions JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS notes TEXT,
ADD COLUMN IF NOT EXISTS location TEXT,
ADD COLUMN IF NOT EXISTS age_range TEXT,
ADD COLUMN IF NOT EXISTS gender TEXT,
ADD COLUMN IF NOT EXISTS profession TEXT,
ADD COLUMN IF NOT EXISTS household_income TEXT,
ADD COLUMN IF NOT EXISTS psychographics JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS buying_behavior JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS pain_points JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS interests JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS hobbies JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS usp_alignment TEXT;

-- 2. Update projects table for Auditability
ALTER TABLE projects 
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS locked_strategy JSONB;

-- 3. Update targeting_blueprints (Engine B artifact tracking)
ALTER TABLE targeting_blueprints
ADD COLUMN IF NOT EXISTS persona_details JSONB DEFAULT '{}'::jsonb;
