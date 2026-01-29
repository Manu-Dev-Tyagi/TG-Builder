-- Migration: Ensure project_id is unique in brand_inputs
-- This enables idempotent upserts and prevents Engine B from failing on multiple rows

ALTER TABLE brand_inputs 
ADD CONSTRAINT brand_inputs_project_id_key UNIQUE (project_id);
