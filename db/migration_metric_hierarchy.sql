/*
  Migration: metric hierarchy (control -> workflow -> cross_workflow -> executive)

  Run against an existing DB that already has the pre-hierarchy schema.
  Safe to run once; fails if columns already exist — adjust or skip steps as needed.
*/

BEGIN;

-- Rollup edges (create before altering metric FKs if metric table references itself only through this table)
CREATE TABLE IF NOT EXISTS metric_rollup (
    parent_metric_id INT NOT NULL REFERENCES metric(id) ON DELETE CASCADE,
    child_metric_id  INT NOT NULL REFERENCES metric(id) ON DELETE CASCADE,
    rollup_rule      VARCHAR(40) NOT NULL CHECK (rollup_rule IN (
                          'weighted_average', 'sum', 'min', 'max', 'structural', 'ratio'
                      )),
    sort_order       INT NOT NULL DEFAULT 0,
    notes            TEXT,
    PRIMARY KEY (parent_metric_id, child_metric_id),
    CHECK (parent_metric_id <> child_metric_id)
);

CREATE INDEX IF NOT EXISTS idx_metric_rollup_parent ON metric_rollup(parent_metric_id);
CREATE INDEX IF NOT EXISTS idx_metric_rollup_child ON metric_rollup(child_metric_id);

-- Add new columns to metric
ALTER TABLE metric ADD COLUMN IF NOT EXISTS workflow_id INT REFERENCES workflow(id) ON DELETE SET NULL;
ALTER TABLE metric ADD COLUMN IF NOT EXISTS metric_level VARCHAR(30) NOT NULL DEFAULT 'control';

-- Relax action_id for rolled-up metrics (existing rows keep non-null action_id)
ALTER TABLE metric DROP CONSTRAINT IF EXISTS metric_action_id_fkey;
ALTER TABLE metric ALTER COLUMN action_id DROP NOT NULL;
ALTER TABLE metric ADD CONSTRAINT metric_action_id_fkey
    FOREIGN KEY (action_id) REFERENCES action(id) ON DELETE CASCADE;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'metric_metric_level_check'
  ) THEN
    ALTER TABLE metric ADD CONSTRAINT metric_metric_level_check CHECK (metric_level IN (
      'control', 'workflow', 'cross_workflow', 'executive'
    ));
  END IF;
END $$;

UPDATE metric SET metric_level = 'control' WHERE metric_level IS NULL OR metric_level = '';

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'metric_level_scope_ck'
  ) THEN
    ALTER TABLE metric ADD CONSTRAINT metric_level_scope_ck CHECK (
      (metric_level = 'control' AND action_id IS NOT NULL AND workflow_id IS NULL)
      OR (metric_level = 'workflow' AND action_id IS NULL AND workflow_id IS NOT NULL)
      OR (metric_level IN ('cross_workflow', 'executive') AND action_id IS NULL AND workflow_id IS NULL)
    );
  END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_metric_workflow ON metric(workflow_id);
CREATE INDEX IF NOT EXISTS idx_metric_level ON metric(metric_level);

COMMIT;
