-- Run once against an existing database that was created before workflow.category existed.
-- New installs get this column from schema.sql.

ALTER TABLE workflow ADD COLUMN IF NOT EXISTS category VARCHAR(120);
CREATE INDEX IF NOT EXISTS idx_workflow_category ON workflow(category);
