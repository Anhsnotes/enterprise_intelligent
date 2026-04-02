-- Idempotent load of metric hierarchy (L2–L4). Safe after db/migration_metric_hierarchy.sql.
-- Use when the main seed already ran without this block, or to re-apply after partial failure.

BEGIN;

INSERT INTO metric (id, action_id, workflow_id, metric_level, name, description, unit, direction) VALUES
(65, NULL, 2, 'workflow', 'O2C Fulfillment Quality Index',
 'Weighted roll-up of on-time delivery, shipment accuracy, and billing accuracy within Order-to-Cash.',
 'index', 'higher_is_better'),
(66, NULL, 2, 'workflow', 'O2C Collection & Dispute Performance',
 'Structural combination of DSO and dispute resolution time; higher index = healthier cash collection (normalize in analytics).',
 'index', 'higher_is_better'),
(67, NULL, 1, 'workflow', 'P2P Match & Payment Efficiency',
 'Weighted roll-up of invoice match rate and payment on-time rate in Procure-to-Pay.',
 'index', 'higher_is_better'),
(68, NULL, 5, 'workflow', 'R2R Close & Reporting Reliability',
 'Weighted roll-up of close duration, task timeliness, and statutory filing performance for Record-to-Report.',
 'index', 'higher_is_better'),
(69, NULL, 6, 'workflow', 'Lead-to-Order Pipeline Effectiveness',
 'Weighted roll-up of lead conversion, opportunity win rate, and lead-to-order cycle time.',
 'index', 'higher_is_better'),
(70, NULL, NULL, 'cross_workflow', 'Order-to-Cash Chain Performance',
 'Cross-functional view of O2C fulfillment quality and collection/dispute performance.',
 'index', 'higher_is_better'),
(71, NULL, NULL, 'cross_workflow', 'Procurement & Finance Control Posture',
 'Aligns Procure-to-Pay efficiency with financial close and reporting reliability.',
 'index', 'higher_is_better'),
(72, NULL, NULL, 'cross_workflow', 'Lead-to-Cash Commercial Velocity',
 'Links pipeline effectiveness to O2C fulfillment quality (sales through delivery).',
 'index', 'higher_is_better'),
(73, NULL, NULL, 'executive', 'Customer & Order-to-Cash Outcomes',
 'Executive view of customer delivery, cash collection, and commercial velocity.',
 'index', 'higher_is_better'),
(74, NULL, NULL, 'executive', 'Financial & Supply Control Discipline',
 'Executive view of procurement payment performance and financial close integrity.',
 'index', 'higher_is_better'),
(75, NULL, NULL, 'executive', 'Enterprise Operating Summary (Illustrative)',
 'Top-level roll-up of customer/commercial outcomes and financial discipline for board-style reporting.',
 'index', 'higher_is_better')
ON CONFLICT (id) DO NOTHING;

INSERT INTO metric_rollup (parent_metric_id, child_metric_id, rollup_rule, sort_order, notes) VALUES
(65, 10, 'weighted_average', 1, 'On-Time Delivery Rate'),
(65, 11, 'weighted_average', 2, 'Shipment Accuracy Rate'),
(65, 12, 'weighted_average', 3, 'Billing Accuracy Rate'),
(66, 13, 'structural', 1, 'Days Sales Outstanding'),
(66, 14, 'structural', 2, 'Dispute Resolution Time'),
(67,  5, 'weighted_average', 1, 'Invoice Match Rate'),
(67,  6, 'weighted_average', 2, 'Payment On-Time Rate'),
(68, 39, 'weighted_average', 1, 'Financial Close Duration'),
(68, 40, 'weighted_average', 2, 'Close Task On-Time Completion Rate'),
(68, 44, 'weighted_average', 3, 'Statutory Filing On-Time Rate'),
(69, 45, 'weighted_average', 1, 'Lead-to-Opportunity Conversion Rate'),
(69, 47, 'weighted_average', 2, 'Opportunity Win Rate'),
(69, 54, 'weighted_average', 3, 'Lead-to-Order Cycle Time'),
(70, 65, 'structural', 1, NULL),
(70, 66, 'structural', 2, NULL),
(71, 67, 'structural', 1, NULL),
(71, 68, 'structural', 2, NULL),
(72, 69, 'structural', 1, NULL),
(72, 65, 'structural', 2, NULL),
(73, 70, 'structural', 1, NULL),
(73, 72, 'structural', 2, NULL),
(74, 71, 'structural', 1, NULL),
(75, 73, 'structural', 1, NULL),
(75, 74, 'structural', 2, NULL)
ON CONFLICT (parent_metric_id, child_metric_id) DO NOTHING;

SELECT setval('metric_id_seq', (SELECT COALESCE(MAX(id), 1) FROM metric));

COMMIT;
