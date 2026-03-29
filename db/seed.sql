/*
  Enterprise Intelligence — Seed Data

  Populates two complete workflow chains (Procure-to-Pay and Order-to-Cash)
  to demonstrate how the six layers link together.
*/

BEGIN;

-- ═══════════════════════════════════════════════
-- Layer 6: Systems
-- ═══════════════════════════════════════════════
INSERT INTO system (id, name, description, system_type, vendor) VALUES
(1, 'SAP S/4HANA',           'Core ERP system',                                'ERP', 'SAP'),
(2, 'Salesforce CRM',        'Customer relationship management',               'CRM', 'Salesforce'),
(3, 'SAP Extended Warehouse', 'Warehouse management system',                   'WMS', 'SAP'),
(4, 'SuccessFactors',        'Human capital management',                       'HCM', 'SAP');

-- ═══════════════════════════════════════════════
-- Layer 5: Data Elements
-- ═══════════════════════════════════════════════
INSERT INTO data_element (id, name, description, data_type) VALUES
-- Procurement-related
(1,  'Purchase Requisition Date',     'Date a purchase requisition was created',          'date'),
(2,  'Purchase Order Amount',         'Total monetary value of a purchase order',         'currency'),
(3,  'Purchase Order Date',           'Date a purchase order was issued',                 'date'),
(4,  'Goods Receipt Date',            'Date goods were received at warehouse',            'date'),
(5,  'Goods Receipt Quantity',        'Quantity of goods received',                       'quantity'),
(6,  'Invoice Amount',                'Amount on the vendor invoice',                     'currency'),
(7,  'Invoice Date',                  'Date the vendor invoice was received',             'date'),
(8,  'Payment Date',                  'Date payment was made to vendor',                  'date'),
(9,  'Payment Amount',                'Amount paid to vendor',                            'currency'),
(10, 'Vendor ID',                     'Unique identifier of the vendor',                  'text'),
-- Sales-related
(11, 'Sales Order Date',              'Date a sales order was created',                   'date'),
(12, 'Sales Order Amount',            'Total monetary value of a sales order',            'currency'),
(13, 'Requested Delivery Date',       'Customer-requested delivery date',                 'date'),
(14, 'Actual Delivery Date',          'Date goods were actually delivered',                'date'),
(15, 'Shipped Quantity',              'Quantity shipped to customer',                      'quantity'),
(16, 'Billing Amount',                'Amount billed to customer',                         'currency'),
(17, 'Customer Payment Date',         'Date customer payment was received',                'date'),
(18, 'Customer Payment Amount',       'Amount received from customer',                     'currency'),
(19, 'Customer ID',                   'Unique identifier of the customer',                 'text'),
(20, 'Days Sales Outstanding',        'Number of days to collect payment',                 'integer');

-- ═══════════════════════════════════════════════
-- Layer 1: Workflows
-- ═══════════════════════════════════════════════
INSERT INTO workflow (id, name, description) VALUES
(1, 'Procure-to-Pay',    'End-to-end procurement cycle from requisition through payment to vendor'),
(2, 'Order-to-Cash',     'End-to-end sales cycle from sales order through cash collection'),
(3, 'Plan-to-Produce',   'Production planning through manufacturing execution and output'),
(4, 'Hire-to-Retire',    'Employee lifecycle from recruitment through retirement');

-- ═══════════════════════════════════════════════
-- Layer 2: Operation Steps
-- ═══════════════════════════════════════════════
-- Procure-to-Pay steps
INSERT INTO operation_step (id, workflow_id, name, description, step_order) VALUES
(1, 1, 'Requisition',           'Identify and request goods or services needed',                     1),
(2, 1, 'Sourcing & PO Creation','Select vendor and issue purchase order',                            2),
(3, 1, 'Goods Receipt',         'Receive and verify delivered goods',                                3),
(4, 1, 'Invoice Verification',  'Match invoice against PO and goods receipt (3-way match)',          4),
(5, 1, 'Payment Execution',     'Release and execute payment to vendor',                             5);

-- Order-to-Cash steps
INSERT INTO operation_step (id, workflow_id, name, description, step_order) VALUES
(6, 2, 'Order Entry',           'Capture and validate customer sales order',                         1),
(7, 2, 'Fulfillment',           'Pick, pack, and ship goods to customer',                            2),
(8, 2, 'Billing',               'Generate and send invoice to customer',                             3),
(9, 2, 'Cash Collection',       'Receive and apply customer payment',                                4);

-- ═══════════════════════════════════════════════
-- Layer 3: Actions
-- ═══════════════════════════════════════════════
-- Procure-to-Pay actions
INSERT INTO action (id, operation_step_id, name, description, action_type) VALUES
(1,  1, 'Approve Purchase Requisition',  'Review and authorize the purchase request',                 'approval'),
(2,  2, 'Select Vendor',                 'Evaluate and choose supplier based on criteria',            'decision'),
(3,  2, 'Release Purchase Order',        'Finalize and send purchase order to vendor',                'execution'),
(4,  3, 'Confirm Goods Receipt',         'Verify received quantity and quality match PO',             'review'),
(5,  4, 'Perform 3-Way Match',           'Match invoice to PO and goods receipt',                     'review'),
(6,  5, 'Authorize Payment',             'Approve payment for release',                               'approval'),
(7,  5, 'Execute Payment Run',           'Process payment through banking channel',                   'execution');

-- Order-to-Cash actions
INSERT INTO action (id, operation_step_id, name, description, action_type) VALUES
(8,  6, 'Validate Sales Order',          'Check pricing, credit, and availability',                   'review'),
(9,  6, 'Approve Sales Order',           'Authorize order for fulfillment',                           'approval'),
(10, 7, 'Release Delivery',              'Schedule and release shipment to customer',                 'execution'),
(11, 7, 'Confirm Shipment',              'Verify goods shipped and update tracking',                  'review'),
(12, 8, 'Generate Invoice',              'Create billing document from delivery',                     'execution'),
(13, 9, 'Apply Customer Payment',        'Match incoming payment to open invoice',                    'execution'),
(14, 9, 'Adjust Outstanding Balance',    'Correct discrepancies in customer account',                 'adjustment');

-- ═══════════════════════════════════════════════
-- Layer 4: Metrics
-- ═══════════════════════════════════════════════
-- Procure-to-Pay metrics
INSERT INTO metric (id, action_id, name, description, unit, direction) VALUES
(1,  1, 'Requisition Approval Cycle Time',     'Days from requisition creation to approval',             'days',    'lower_is_better'),
(2,  2, 'Vendor Lead Time',                    'Average days from PO to delivery by vendor',             'days',    'lower_is_better'),
(3,  3, 'PO Accuracy Rate',                    'Percentage of POs requiring no amendment',               '%',       'higher_is_better'),
(4,  4, 'Goods Receipt Discrepancy Rate',      'Percentage of receipts with quantity/quality issues',     '%',       'lower_is_better'),
(5,  5, 'Invoice Match Rate',                  'Percentage of invoices passing 3-way match on first try', '%',       'higher_is_better'),
(6,  6, 'Payment On-Time Rate',                'Percentage of payments made by due date',                 '%',       'higher_is_better'),
(7,  7, 'Cost Per Payment Transaction',        'Average cost to process a single payment',                '$',       'lower_is_better');

-- Order-to-Cash metrics
INSERT INTO metric (id, action_id, name, description, unit, direction) VALUES
(8,  8, 'Order Error Rate',                    'Percentage of orders with data entry errors',             '%',       'lower_is_better'),
(9,  9, 'Order Approval Cycle Time',           'Days from order entry to approval',                       'days',    'lower_is_better'),
(10, 10, 'On-Time Delivery Rate',              'Percentage of orders delivered by requested date',         '%',       'higher_is_better'),
(11, 11, 'Shipment Accuracy Rate',             'Percentage of shipments matching order exactly',           '%',       'higher_is_better'),
(12, 12, 'Billing Accuracy Rate',              'Percentage of invoices requiring no credit/debit memo',   '%',       'higher_is_better'),
(13, 13, 'Days Sales Outstanding',             'Average days to collect payment after invoicing',          'days',    'lower_is_better'),
(14, 14, 'Dispute Resolution Time',            'Average days to resolve payment discrepancies',            'days',    'lower_is_better');

-- ═══════════════════════════════════════════════
-- Junction: Metric ↔ Data Element
-- ═══════════════════════════════════════════════
INSERT INTO metric_data_element (metric_id, data_element_id, role) VALUES
-- Requisition Approval Cycle Time = PO Date − Requisition Date
(1, 1, 'input'),
(1, 3, 'input'),
-- Vendor Lead Time = Goods Receipt Date − PO Date
(2, 3, 'input'),
(2, 4, 'input'),
(2, 10, 'dimension'),
-- PO Accuracy Rate
(3, 2, 'numerator'),
-- Goods Receipt Discrepancy Rate
(4, 5, 'numerator'),
-- Invoice Match Rate
(5, 6, 'numerator'),
(5, 2, 'denominator'),
(5, 5, 'filter'),
-- Payment On-Time Rate
(6, 8, 'input'),
(6, 9, 'numerator'),
-- On-Time Delivery Rate = Actual ≤ Requested
(10, 13, 'input'),
(10, 14, 'input'),
(10, 19, 'dimension'),
-- Shipment Accuracy Rate
(11, 15, 'numerator'),
-- Billing Accuracy Rate
(12, 16, 'numerator'),
-- Days Sales Outstanding = Customer Payment Date − Invoice Date (via Billing Date proxy)
(13, 17, 'input'),
(13, 20, 'numerator'),
(13, 19, 'dimension');

-- ═══════════════════════════════════════════════
-- Junction: Data Element ↔ System
-- ═══════════════════════════════════════════════
INSERT INTO data_element_system (data_element_id, system_id, source_table, source_field) VALUES
-- SAP S/4HANA procurement tables
(1,  1, 'EBAN',  'BADAT'),
(2,  1, 'EKPO',  'NETWR'),
(3,  1, 'EKKO',  'BEDAT'),
(4,  1, 'EKBE',  'BUDAT'),
(5,  1, 'EKBE',  'MENGE'),
(6,  1, 'RBKP',  'RMWWR'),
(7,  1, 'RBKP',  'BLDAT'),
(8,  1, 'BSEG',  'BUDAT'),
(9,  1, 'BSEG',  'DMBTR'),
(10, 1, 'LFA1',  'LIFNR'),
-- SAP S/4HANA sales tables
(11, 1, 'VBAK',  'ERDAT'),
(12, 1, 'VBAP',  'NETWR'),
(13, 1, 'VBEP',  'EDATU'),
(14, 1, 'LIKP',  'WADAT_IST'),
(15, 1, 'LIPS',  'LFIMG'),
(16, 1, 'VBRP',  'NETWR'),
(17, 1, 'BSAD',  'BUDAT'),
(18, 1, 'BSAD',  'DMBTR'),
(19, 1, 'KNA1',  'KUNNR'),
-- Salesforce CRM
(19, 2, 'Account', 'AccountId'),
-- Warehouse system
(4,  3, 'WMTRANSFER', 'RECEIPT_DATE'),
(5,  3, 'WMTRANSFER', 'QTY_RECEIVED'),
(15, 3, 'WMTRANSFER', 'QTY_SHIPPED');

-- Reset sequences to avoid PK conflicts on future inserts
SELECT setval('workflow_id_seq',       (SELECT MAX(id) FROM workflow));
SELECT setval('operation_step_id_seq', (SELECT MAX(id) FROM operation_step));
SELECT setval('action_id_seq',         (SELECT MAX(id) FROM action));
SELECT setval('metric_id_seq',         (SELECT MAX(id) FROM metric));
SELECT setval('data_element_id_seq',   (SELECT MAX(id) FROM data_element));
SELECT setval('system_id_seq',         (SELECT MAX(id) FROM system));

COMMIT;
