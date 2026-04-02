/*
  Enterprise Intelligence - Core Schema

  Maps the six-layer framework to a relational model:

    Workflow  ->  Operation Step  ->  Action  ->  Metric  ->  Data Element  ->  System

  Vertical 1:N relationships flow top-down through FKs.
  Metric<->Data Element and Data Element<->System are M:N via junction tables.
*/

BEGIN;

-- ---------------------------------------------
-- Layer 1: Business Workflow & Cycles
-- ---------------------------------------------
CREATE TABLE workflow (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(200) NOT NULL UNIQUE,
    description   TEXT,
    category      VARCHAR(120),
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- ---------------------------------------------
-- Layer 2: Business Operation Steps
-- ---------------------------------------------
CREATE TABLE operation_step (
    id            SERIAL PRIMARY KEY,
    workflow_id   INT          NOT NULL REFERENCES workflow(id) ON DELETE CASCADE,
    name          VARCHAR(200) NOT NULL,
    description   TEXT,
    step_order    INT          NOT NULL,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    UNIQUE (workflow_id, step_order)
);

-- ---------------------------------------------
-- Layer 3: Control Actions
-- ---------------------------------------------
CREATE TABLE action (
    id                  SERIAL PRIMARY KEY,
    operation_step_id   INT          NOT NULL REFERENCES operation_step(id) ON DELETE CASCADE,
    name                VARCHAR(200) NOT NULL,
    description         TEXT,
    action_type         VARCHAR(50)  NOT NULL CHECK (action_type IN (
                            'decision', 'approval', 'execution', 'review', 'adjustment'
                        )),
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- ---------------------------------------------
-- Layer 4: Metrics (control + rolled-up workflow / cross-workflow / executive)
-- Control metrics (metric_level = control) attach to an action.
-- Higher levels roll up from child metrics via metric_rollup (no L0 data elements required).
-- ---------------------------------------------
CREATE TABLE metric (
    id            SERIAL PRIMARY KEY,
    action_id     INT          REFERENCES action(id) ON DELETE CASCADE,
    workflow_id   INT          REFERENCES workflow(id) ON DELETE SET NULL,
    metric_level  VARCHAR(30)  NOT NULL DEFAULT 'control' CHECK (metric_level IN (
                      'control', 'workflow', 'cross_workflow', 'executive'
                  )),
    name          VARCHAR(200) NOT NULL,
    description   TEXT,
    unit          VARCHAR(50),
    direction     VARCHAR(20)  NOT NULL CHECK (direction IN (
                      'higher_is_better', 'lower_is_better', 'target'
                  )),
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    CONSTRAINT metric_level_scope_ck CHECK (
        (metric_level = 'control' AND action_id IS NOT NULL AND workflow_id IS NULL)
        OR (metric_level = 'workflow' AND action_id IS NULL AND workflow_id IS NOT NULL)
        OR (metric_level IN ('cross_workflow', 'executive') AND action_id IS NULL AND workflow_id IS NULL)
    )
);

-- Parent metric composed of child metrics (L1 control -> L2 -> L3 -> L4).
CREATE TABLE metric_rollup (
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

-- ---------------------------------------------
-- Layer 5: Standard Data Points (Data Elements)
-- ---------------------------------------------
CREATE TABLE data_element (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(200) NOT NULL UNIQUE,
    description   TEXT,
    data_type     VARCHAR(50)  NOT NULL CHECK (data_type IN (
                      'date', 'timestamp', 'currency', 'quantity', 'percentage',
                      'text', 'boolean', 'integer', 'decimal'
                  )),
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- ---------------------------------------------
-- Layer 6: System Layer (ERP / Source Systems)
-- ---------------------------------------------
CREATE TABLE system (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(200) NOT NULL UNIQUE,
    description   TEXT,
    system_type   VARCHAR(50)  NOT NULL CHECK (system_type IN (
                      'ERP', 'CRM', 'WMS', 'MES', 'PLM', 'HCM', 'SCM', 'BI', 'Other'
                  )),
    vendor        VARCHAR(200),
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- ---------------------------------------------
-- Junction: Metric <-> Data Element (M:N)
-- A metric is composed of one or more data elements,
-- each playing a specific role (numerator, filter, etc.)
-- ---------------------------------------------
CREATE TABLE metric_data_element (
    metric_id       INT         NOT NULL REFERENCES metric(id) ON DELETE CASCADE,
    data_element_id INT         NOT NULL REFERENCES data_element(id) ON DELETE CASCADE,
    role            VARCHAR(50) NOT NULL CHECK (role IN (
                        'numerator', 'denominator', 'filter', 'dimension', 'input'
                    )),
    PRIMARY KEY (metric_id, data_element_id, role)
);

-- ---------------------------------------------
-- Junction: Data Element <-> System (M:N)
-- Traces each data element back to its source
-- system, table, and field for full lineage.
-- ---------------------------------------------
CREATE TABLE data_element_system (
    data_element_id INT          NOT NULL REFERENCES data_element(id) ON DELETE CASCADE,
    system_id       INT          NOT NULL REFERENCES system(id) ON DELETE CASCADE,
    source_table    VARCHAR(200),
    source_field    VARCHAR(200),
    PRIMARY KEY (data_element_id, system_id)
);

-- ---------------------------------------------
-- Indexes for common query patterns
-- ---------------------------------------------
CREATE INDEX idx_workflow_category        ON workflow(category);
CREATE INDEX idx_operation_step_workflow  ON operation_step(workflow_id);
CREATE INDEX idx_action_operation_step    ON action(operation_step_id);
CREATE INDEX idx_metric_action            ON metric(action_id);
CREATE INDEX idx_metric_workflow          ON metric(workflow_id);
CREATE INDEX idx_metric_level             ON metric(metric_level);
CREATE INDEX idx_metric_rollup_parent     ON metric_rollup(parent_metric_id);
CREATE INDEX idx_metric_rollup_child      ON metric_rollup(child_metric_id);
CREATE INDEX idx_mde_data_element         ON metric_data_element(data_element_id);
CREATE INDEX idx_des_system               ON data_element_system(system_id);

-- ---------------------------------------------
-- Trigger: auto-update updated_at on row change
-- ---------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_workflow_updated       BEFORE UPDATE ON workflow         FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_operation_step_updated BEFORE UPDATE ON operation_step   FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_action_updated         BEFORE UPDATE ON action           FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_metric_updated         BEFORE UPDATE ON metric           FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_data_element_updated   BEFORE UPDATE ON data_element     FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_system_updated         BEFORE UPDATE ON system           FOR EACH ROW EXECUTE FUNCTION update_updated_at();

COMMIT;
