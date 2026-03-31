/*
  Enterprise Intelligence - Seed Data

  Populates workflow definitions (with categories), full chains for key cycles,
  and demonstrates how the six layers link together.
*/

BEGIN;

-- ===============================================
-- Layer 6: Systems
-- ===============================================
INSERT INTO system (id, name, description, system_type, vendor) VALUES
(1, 'SAP S/4HANA',           'Core ERP system',                                'ERP', 'SAP'),
(2, 'Salesforce CRM',        'Customer relationship management',               'CRM', 'Salesforce'),
(3, 'SAP Extended Warehouse', 'Warehouse management system',                   'WMS', 'SAP'),
(4, 'SuccessFactors',        'Human capital management',                       'HCM', 'SAP');

-- ===============================================
-- Layer 5: Data Elements
-- ===============================================
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
(20, 'Days Sales Outstanding',        'Number of days to collect payment',                 'integer'),
-- Order-to-Cash (complete lineage for remaining metrics)
(21, 'Order Entry Error Count',       'Count of sales order lines flagged with errors',    'integer'),
(22, 'Sales Order Line Count',        'Total count of sales order lines entered',          'integer'),
(23, 'Sales Order Approval Date',     'Date the sales order was approved for fulfillment', 'date'),
(24, 'Payment Dispute Open Date',     'Date a payment dispute or collection case opened',  'date'),
(25, 'Payment Dispute Resolved Date', 'Date the payment dispute was closed',               'date'),
-- Plan-to-Produce
(26, 'Planned Production Quantity',   'Planned output quantity on production order',       'quantity'),
(27, 'Confirmed Yield Quantity',      'Confirmed good quantity from production',           'quantity'),
(28, 'Scheduled Start Date',          'Scheduled start date of the production order',      'date'),
(29, 'Confirmed Finish Date',         'Confirmed finish date of production',             'date'),
(30, 'Scrap Quantity',                'Scrapped quantity from production confirmations',   'quantity'),
(31, 'MRP Exception Count',         'Count of MRP exception messages or alerts',         'integer'),
(32, 'MRP Planned Item Count',        'Count of planned orders or MRP elements reviewed',  'integer'),
(33, 'Planning Cycle Start Date',     'Start date of the planning cycle run',            'date'),
(34, 'Planning Approval Date',        'Date the production plan was approved',             'date'),
(35, 'Demand Forecast Quantity',      'Forecast quantity for the planning horizon',      'quantity'),
(36, 'Actual Demand Quantity',        'Actual demand or consumption for comparison',       'quantity'),
(37, 'Inspection Accepted Quantity',  'Quantity accepted at quality inspection',          'quantity'),
(38, 'Inspection Total Quantity',     'Total quantity inspected',                         'quantity'),
(39, 'Finished Goods Receipt Quantity','Quantity posted as finished goods to inventory',   'quantity'),
(40, 'Standard Production Cost',      'Standard cost amount for production order',         'currency'),
(41, 'Actual Production Cost',        'Actual cost accumulated on production order',       'currency'),
-- Hire-to-Retire
(42, 'Job Requisition Open Date',     'Date the job requisition was published',           'date'),
(43, 'Offer Extended Date',           'Date offer was extended to candidate',             'date'),
(44, 'Employee Hire Date',            'Employee hire or start date',                       'date'),
(45, 'Onboarding Start Date',         'Date structured onboarding began',                  'date'),
(46, 'Onboarding Complete Date',      'Date onboarding milestones completed',             'date'),
(47, 'Payroll Payment Date',          'Date payroll payment posted',                      'date'),
(48, 'Termination Effective Date',    'Effective date of employment termination',          'date'),
(49, 'Active Employee Headcount',     'Count of active employees on a given date',         'integer'),
-- Hire-to-Retire (rate metrics: numerators / denominators)
(50, 'Employee Records With Validation Errors', 'Count of employee master records failing validation', 'integer'),
(51, 'Employees With Documented Goals Count',   'Count of employees with current goals on file',       'integer'),
(52, 'Performance Reviews Completed Count',   'Count of performance reviews completed in period',    'integer'),
(53, 'Performance Reviews Due Count',           'Count of performance reviews due in period',          'integer'),
(54, 'Benefits Enrolled Headcount',             'Count of employees enrolled in core benefits',        'integer'),
(55, 'Benefits Eligible Headcount',             'Count of employees eligible for core benefits',       'integer'),
(56, 'Payroll Runs Without Retro Correction',   'Count of payroll runs posted without retro correction', 'integer'),
(57, 'Payroll Runs In Period',                  'Total payroll runs in the measurement period',        'integer'),
(58, 'Voluntary Termination Count',            'Count of voluntary terminations in period',           'integer'),
(59, 'Offers Extended Count',                  'Count of job offers extended to candidates',          'integer'),
(60, 'Offers Accepted Count',                  'Count of offers accepted by candidates',              'integer'),
-- Procure-to-Pay (cost per payment)
(61, 'Accounts Payable Processing Cost',       'Total operational cost to process payments in period', 'currency'),
(62, 'Payment Run Transaction Count',          'Count of payment line items or runs in period',        'integer'),
-- Record-to-Report (R2R)
(63, 'GL Journal Posting Date',                 'Posting date of journal entries to the general ledger', 'date'),
(64, 'Journal Line Count',                      'Count of journal line items posted in period',          'integer'),
(65, 'Journal Posting Error Count',             'Count of journal postings rejected or with errors',     'integer'),
(66, 'Account Reconciliation Completed Date',   'Date account reconciliation was signed off',            'date'),
(67, 'Unreconciled Balance Amount',             'Absolute value of unreconciled balance by account',     'currency'),
(68, 'Financial Close Period Start Date',       'Date financial close activities began',                 'date'),
(69, 'Financial Close Completion Date',         'Date financial close was released for the period',      'date'),
(70, 'Consolidation Run Date',                  'Date group consolidation was executed',                 'date'),
(71, 'Consolidation Adjustment Amount',         'Amount of consolidation and elimination adjustments',   'currency'),
(72, 'Intercompany Out-of-Balance Amount',      'Remaining intercompany mismatch after matching',       'currency'),
(73, 'Management Report Publish Date',          'Date management reporting pack was published',          'date'),
(74, 'External Reporting Deadline',             'Due date for external or board reporting',              'date'),
(75, 'Statutory Filing Submission Date',         'Date statutory filing was submitted',                   'date'),
(76, 'Manual Journal Approval Date',            'Date manual journal was fully approved',                'date'),
(77, 'Close Task Completed Count',              'Count of close checklist tasks completed on time',      'integer'),
(78, 'Close Task Due Count',                    'Count of close checklist tasks due in the period',      'integer'),
-- Lead-to-Order / Opportunity-to-Order
(79, 'Lead Creation Date',                      'Date lead was created in CRM',                          'date'),
(80, 'Lead First Response Date',                'Date of first meaningful sales response to lead',       'date'),
(81, 'Opportunity Create Date',               'Date opportunity was created',                          'date'),
(82, 'Opportunity Close Date',                  'Date opportunity was closed won or lost',               'date'),
(83, 'Opportunity Amount',                      'Weighted or total opportunity value',                 'currency'),
(84, 'Quote Issue Date',                        'Date customer quote was issued',                        'date'),
(85, 'Quote Revision Count',                    'Number of quote revisions before acceptance',           'integer'),
(86, 'Contract Signature Date',                 'Date contract was fully executed',                      'date'),
(87, 'Lead Count',                              'Count of new leads in period',                          'integer'),
(88, 'Qualified Lead Count',                    'Count of leads qualified to opportunity',               'integer'),
(89, 'Open Opportunity Count',                  'Count of open opportunities in pipeline',             'integer'),
(90, 'Won Opportunity Count',                   'Count of opportunities closed won',                     'integer'),
(91, 'Quote Count',                             'Count of quotes issued in period',                      'integer'),
(92, 'Accepted Quote Count',                    'Count of quotes accepted by customer',                  'integer'),
-- Source-to-Pay / Source-to-Contract
(93, 'Category Addressable Spend Amount',       'Total addressable spend for the category',              'currency'),
(94, 'Category Managed Spend Amount',           'Spend under management (contracts or catalogs)',       'currency'),
(95, 'Sourcing Event Start Date',               'Date sourcing event or RFx was opened',                 'date'),
(96, 'Supplier Award Date',                     'Date supplier was awarded the business',                'date'),
(97, 'Strategic Contract Effective Date',       'Effective date of strategic supplier contract',         'date'),
(98, 'Strategic Contract Expiry Date',          'Expiry date of strategic supplier contract',            'date'),
(99, 'Catalog Active Item Count',               'Count of items active on negotiated catalogs',          'integer'),
(100, 'Off-Contract Purchase Amount',         'Purchase amount outside negotiated contracts',          'currency'),
(101, 'Sourcing Invitation Count',             'Count of supplier invitations to sourcing event',       'integer'),
(102, 'Sourcing Response Count',               'Count of complete supplier responses received',         'integer'),
(103, 'Supplier Corrective Action Count',      'Count of corrective actions open with supplier',        'integer'),
(104, 'Supplier Performance Review Due Count', 'Count of supplier reviews due in period',               'integer'),
(105, 'Supplier Performance Review Done Count','Count of supplier reviews completed on time',           'integer');

-- ===============================================
-- Layer 1: Workflows
-- ===============================================
INSERT INTO workflow (id, name, description, category) VALUES
-- Existing full chains (ids 1–4 referenced by operation_step)
(1, 'Procure-to-Pay', 'End-to-end procurement cycle from requisition through payment to vendor', 'Procurement & Supply Chain'),
(2, 'Order-to-Cash', 'End-to-end sales cycle from sales order through cash collection', 'Sales & Revenue'),
(3, 'Plan-to-Produce', 'Production planning through manufacturing execution and output', 'Operations & Manufacturing'),
(4, 'Hire-to-Retire', 'Employee lifecycle from recruitment through retirement', 'Human Capital'),
-- Additional standard workflows (full seed chains below)
(5, 'Record-to-Report (R2R)', 'Financial close, general ledger, reconciliations, consolidation, and management or statutory reporting. Almost every company with a real finance function; often the most standardised after core ERP go-live (close calendars, reconciliations, reporting).', 'Finance & Control'),
(6, 'Lead-to-Order / Opportunity-to-Order', 'Pipeline and opportunity management through qualified order or hand-off to fulfilment. Extremely common wherever there is a formal sales pipeline (CRM + ERP); often branded under Salesforce, Microsoft, or SAP sales clouds rather than a single ERP term.', 'Sales & Revenue'),
(7, 'Source-to-Pay / Source-to-Contract', 'Strategic sourcing, contracts, and supplier engagement through operational buying; often distinguished from day-to-day P2P until spend-under-management matures. Very common in mid-size and large organisations with procurement maturity; sometimes rolled into P2P until spend under management becomes a priority.', 'Procurement & Supply Chain');

-- ===============================================
-- Layer 2: Operation Steps
-- ===============================================
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

-- Plan-to-Produce steps
INSERT INTO operation_step (id, workflow_id, name, description, step_order) VALUES
(10, 3, 'Demand & Production Planning', 'Align demand forecast with production and capacity plan', 1),
(11, 3, 'Material Requirements Planning', 'Explode BOM, run MRP, and release planned orders',      2),
(12, 3, 'Manufacturing Execution', 'Release and execute production orders on the shop floor', 3),
(13, 3, 'Quality & Yield',       'Inspect output, record scrap, and release batches',               4),
(14, 3, 'Finished Goods & Variance', 'Post finished goods, absorb variances, close orders',   5);

-- Hire-to-Retire steps
INSERT INTO operation_step (id, workflow_id, name, description, step_order) VALUES
(15, 4, 'Recruit & Select',      'Attract, assess, and hire candidates',                              1),
(16, 4, 'Onboard',               'Complete contracts, provisioning, and role readiness',              2),
(17, 4, 'Develop & Perform',     'Goals, feedback, and performance management',                     3),
(18, 4, 'Compensation & Benefits', 'Payroll, rewards, and benefits administration',                 4),
(19, 4, 'Separate & Offboard',   'Exit process, knowledge transfer, and alumni transition',         5);

-- Record-to-Report (workflow 5)
INSERT INTO operation_step (id, workflow_id, name, description, step_order) VALUES
(20, 5, 'Subledger & journals',     'Capture transactions, post journals, and maintain subledgers', 1),
(21, 5, 'Reconciliation',         'Reconcile GL accounts, bank, and subledger to GL',            2),
(22, 5, 'Period close',           'Execute close checklist, accruals, and period lock',           3),
(23, 5, 'Consolidation',          'Group consolidation, eliminations, and currency translation', 4),
(24, 5, 'Reporting & filing',     'Management reporting, statutory filings, and disclosures',     5);

-- Lead-to-Order (workflow 6)
INSERT INTO operation_step (id, workflow_id, name, description, step_order) VALUES
(25, 6, 'Lead capture',           'Ingest, score, and qualify inbound and marketing leads',       1),
(26, 6, 'Opportunity management', 'Develop pipeline, forecast, and advance opportunities',       2),
(27, 6, 'Quotation',              'Configure, price, and issue proposals or quotes',               3),
(28, 6, 'Contract',               'Negotiate and execute commercial terms before order',         4),
(29, 6, 'Order handoff',          'Convert to sales order and validate CRM–ERP alignment',        5);

-- Source-to-Pay / Source-to-Contract (workflow 7)
INSERT INTO operation_step (id, workflow_id, name, description, step_order) VALUES
(30, 7, 'Category strategy',      'Define category plans, policies, and spend under management', 1),
(31, 7, 'Sourcing & award',       'Run RFx, evaluate bids, and award suppliers',                  2),
(32, 7, 'Strategic contract',     'Draft, negotiate, and sign framework agreements',              3),
(33, 7, 'Catalog enablement',     'Publish catalogs, pricing, and purchasing channels',          4),
(34, 7, 'Supplier performance',   'Scorecard, risk, and corrective action management',            5);

-- ===============================================
-- Layer 3: Actions
-- ===============================================
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

-- Plan-to-Produce actions
INSERT INTO action (id, operation_step_id, name, description, action_type) VALUES
(15, 10, 'Approve Production Plan',       'Review and sign off the master production plan',           'approval'),
(16, 10, 'Publish Demand Plan',         'Publish demand and supply plan to operations',             'execution'),
(17, 11, 'Run MRP',                     'Execute material requirements planning run',               'execution'),
(18, 11, 'Resolve Material Exception',  'Clear MRP exceptions, shortages, and reschedules',         'decision'),
(19, 12, 'Release Production Order',    'Release order to shop floor and issue components',         'execution'),
(20, 12, 'Confirm Production Output',   'Confirm yields, activities, and order progress',           'review'),
(21, 13, 'Record Scrap and Rework',     'Post scrap, rework, and non-conformance',                  'execution'),
(22, 13, 'Inspect and Release Batch',   'Quality inspection and batch release',                     'review'),
(23, 14, 'Post Finished Goods Receipt', 'Receive finished goods into inventory',                    'execution'),
(24, 14, 'Analyze Production Variance', 'Compare plan vs actual cost and quantity',                 'review');

-- Hire-to-Retire actions
INSERT INTO action (id, operation_step_id, name, description, action_type) VALUES
(25, 15, 'Post Job Requisition',        'Publish role and open requisition',                        'execution'),
(26, 15, 'Select Candidate',            'Interview, assess, and select hire',                       'decision'),
(27, 16, 'Complete Onboarding Tasks',   'Provisioning, training, and policy acknowledgements',      'execution'),
(28, 16, 'Verify Employee Data',        'Validate master data and org assignment',                  'review'),
(29, 17, 'Set Goals and Review',        'Cascade goals and cadence for performance cycle',          'execution'),
(30, 17, 'Conduct Performance Review', 'Formal review and rating in performance cycle',            'review'),
(31, 18, 'Process Payroll Run',         'Calculate and post payroll payments',                      'execution'),
(32, 18, 'Administer Benefits',         'Enroll and maintain benefits elections',                   'execution'),
(33, 19, 'Process Termination',         'Initiate separation workflow and final pay',               'execution'),
(34, 19, 'Conduct Exit Interview',      'Capture feedback and complete offboarding checklist',      'review');

-- Record-to-Report actions
INSERT INTO action (id, operation_step_id, name, description, action_type) VALUES
(35, 20, 'Post and validate journals',        'Review postings and validation messages before close',    'review'),
(36, 20, 'Approve manual journals',           'Approve high-value or non-standard journal entries',      'approval'),
(37, 21, 'Complete account reconciliation',   'Sign off reconciliations for owned accounts',             'execution'),
(38, 21, 'Resolve reconciliation exceptions', 'Clear breaks and escalate material variances',            'decision'),
(39, 22, 'Execute close checklist',           'Run close tasks, accruals, and dependencies',             'execution'),
(40, 22, 'Approve financial close',         'Approve release of financial results for the period',     'approval'),
(41, 23, 'Run group consolidation',           'Execute consolidation and elimination runs',              'execution'),
(42, 23, 'Review consolidation adjustments','Validate IC matching and consolidation entries',          'review'),
(43, 24, 'Publish management reports',      'Issue management reporting pack and commentary',          'execution'),
(44, 24, 'Submit statutory filings',        'File statutory and regulatory submissions on time',       'execution');

-- Lead-to-Order actions
INSERT INTO action (id, operation_step_id, name, description, action_type) VALUES
(45, 25, 'Qualify lead',                      'Apply qualification criteria and next-best action',       'decision'),
(46, 25, 'Convert lead to opportunity',       'Create opportunity and assign ownership',                 'execution'),
(47, 26, 'Advance opportunity',             'Update stage, stakeholders, and close plan',            'execution'),
(48, 26, 'Refresh pipeline forecast',       'Update forecast and commit for revenue planning',         'review'),
(49, 27, 'Issue customer quote',            'Configure, price, and send formal quote',                   'execution'),
(50, 27, 'Approve pricing and discount',    'Approve non-standard price or discount',                  'approval'),
(51, 28, 'Negotiate contract',              'Negotiate legal and commercial terms',                    'execution'),
(52, 28, 'Execute contract',                'Obtain signatures and activate agreement',                  'approval'),
(53, 29, 'Create sales order handoff',      'Generate sales order and trigger fulfilment',             'execution'),
(54, 29, 'Validate CRM–ERP alignment',      'Reconcile opportunity, quote, and order data',            'review');

-- Source-to-Pay actions
INSERT INTO action (id, operation_step_id, name, description, action_type) VALUES
(55, 30, 'Define category strategy',        'Set policies, segmentation, and sourcing approach',       'execution'),
(56, 30, 'Approve category plan',           'Approve category strategy and savings targets',           'approval'),
(57, 31, 'Run sourcing event',              'Issue RFx and manage Q&A and submissions',                'execution'),
(58, 31, 'Award supplier',                  'Select winning bid and debrief participants',             'decision'),
(59, 32, 'Author strategic contract',       'Draft framework agreement from approved award',         'execution'),
(60, 32, 'Negotiate contract terms',        'Redline legal and commercial clauses to signature',     'execution'),
(61, 33, 'Publish catalog and pricing',     'Activate items, pricing, and punch-out channels',         'execution'),
(62, 33, 'Validate purchasing channel',     'Verify catalog and contract data in purchasing',          'review'),
(63, 34, 'Review supplier scorecard',       'Review KPIs and performance vs contract',                 'review'),
(64, 34, 'Initiate corrective action',      'Open improvement plan for underperforming supplier',      'decision');

-- ===============================================
-- Layer 4: Metrics
-- ===============================================
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

-- Plan-to-Produce metrics
INSERT INTO metric (id, action_id, name, description, unit, direction) VALUES
(15, 15, 'Planning Cycle Time',                'Days from planning cycle start to plan approval',          'days',    'lower_is_better'),
(16, 16, 'Forecast Bias',                     'Average deviation of forecast from actual demand',           '%',       'target'),
(17, 17, 'MRP Exception Rate',                'Percentage of MRP items with exception messages',          '%',       'lower_is_better'),
(18, 18, 'Material Exception Resolution Time','Average days to clear MRP or shortage exceptions',        'days',    'lower_is_better'),
(19, 19, 'Schedule Adherence',                'Percentage of orders started on scheduled start date',      '%',       'higher_is_better'),
(20, 20, 'Production Order Lead Time',        'Days from order release to final confirmation',            'days',    'lower_is_better'),
(21, 21, 'First Pass Yield',                  'Percentage of output passing inspection without rework',    '%',       'higher_is_better'),
(22, 22, 'Scrap Rate',                        'Scrap quantity as percentage of confirmed output',         '%',       'lower_is_better'),
(23, 23, 'Plan vs Actual Quantity Variance',   'Variance between planned and finished goods quantity',      '%',       'target'),
(24, 24, 'Manufacturing Cost Variance',        'Variance between standard and actual production cost',     '%',       'target');

-- Hire-to-Retire metrics
INSERT INTO metric (id, action_id, name, description, unit, direction) VALUES
(25, 25, 'Time to Fill',                      'Days from requisition open to accepted offer',             'days',    'lower_is_better'),
(26, 26, 'Offer Acceptance Rate',             'Percentage of offers accepted by candidates',              '%',       'higher_is_better'),
(27, 27, 'Onboarding Cycle Time',             'Days from hire date to onboarding completion',             'days',    'lower_is_better'),
(28, 28, 'Employee Data Error Rate',          'Percentage of employee records with validation errors',    '%',       'lower_is_better'),
(29, 29, 'Goal Setting Completion Rate',      'Percentage of employees with current goals on file',       '%',       'higher_is_better'),
(30, 30, 'Performance Review Timeliness',     'Percentage of reviews completed by due date',              '%',       'higher_is_better'),
(31, 31, 'Payroll Accuracy Rate',             'Percentage of payroll runs without retroactive correction', '%',      'higher_is_better'),
(32, 32, 'Benefits Enrollment Rate',          'Percentage of eligible employees enrolled in core benefits', '%',     'higher_is_better'),
(33, 33, 'Voluntary Turnover Rate',            'Voluntary terminations as percentage of average headcount', '%',     'lower_is_better'),
(34, 34, 'Offboarding Cycle Time',            'Days from termination notice to effective exit date',      'days',    'lower_is_better');

-- Record-to-Report metrics
INSERT INTO metric (id, action_id, name, description, unit, direction) VALUES
(35, 35, 'Journal Posting Error Rate',        'Percentage of journal lines posted with errors or rejects', '%',       'lower_is_better'),
(36, 36, 'Manual Journal Approval Cycle Time','Days from journal entry to full approval',                 'days',    'lower_is_better'),
(37, 37, 'Reconciliation Timeliness',       'Days from period end to reconciliation sign-off',        'days',    'lower_is_better'),
(38, 38, 'Unreconciled Balance Exposure',     'Aggregate unreconciled balance as percentage of assets',   '%',       'lower_is_better'),
(39, 39, 'Financial Close Duration',          'Days from close start to close completion',                'days',    'lower_is_better'),
(40, 40, 'Close Task On-Time Completion Rate','Percentage of close tasks completed by due date',          '%',       'higher_is_better'),
(41, 41, 'Consolidation Adjustment Rate',     'Consolidation adjustments as percentage of group revenue', '%',       'target'),
(42, 42, 'Intercompany Match Rate',           'Percentage of IC accounts matched without residual',       '%',       'higher_is_better'),
(43, 43, 'Management Reporting Timeliness',   'Days from period end to management pack publication',      'days',    'lower_is_better'),
(44, 44, 'Statutory Filing On-Time Rate',     'Percentage of filings submitted by legal deadline',        '%',       'higher_is_better');

-- Lead-to-Order metrics
INSERT INTO metric (id, action_id, name, description, unit, direction) VALUES
(45, 45, 'Lead-to-Opportunity Conversion Rate','Percentage of leads qualified to opportunity',            '%',       'higher_is_better'),
(46, 46, 'Lead Response Time',                'Hours from lead creation to first meaningful response',    'hours',   'lower_is_better'),
(47, 47, 'Opportunity Win Rate',              'Percentage of closed opportunities won',                   '%',       'higher_is_better'),
(48, 48, 'Pipeline Forecast Accuracy',        'Variance of weighted pipeline to actual bookings',         '%',       'target'),
(49, 49, 'Quote Win Rate',                    'Percentage of quotes accepted vs issued',                  '%',       'higher_is_better'),
(50, 50, 'Average Quote Revisions',           'Average revisions per quote before decision',              'count',   'lower_is_better'),
(51, 51, 'Contract Cycle Time',               'Days from verbal agreement to executed contract',          'days',    'lower_is_better'),
(52, 52, 'Non-Standard Contract Rate',        'Percentage of contracts requiring legal exception',        '%',       'lower_is_better'),
(53, 53, 'Order Handoff Error Rate',          'Percentage of orders requiring fix after CRM–ERP handoff', '%',       'lower_is_better'),
(54, 54, 'Lead-to-Order Cycle Time',          'Days from lead creation to sales order creation',          'days',    'lower_is_better');

-- Source-to-Pay metrics
INSERT INTO metric (id, action_id, name, description, unit, direction) VALUES
(55, 55, 'Spend Under Management Rate',       'Managed spend as percentage of addressable category spend','%',       'higher_is_better'),
(56, 56, 'Category Strategy Cycle Time',      'Days to refresh and approve category strategy',             'days',    'lower_is_better'),
(57, 57, 'Sourcing Event Response Rate',      'Percentage of invited suppliers submitting complete bids', '%',       'higher_is_better'),
(58, 58, 'Sourcing Savings Yield',            'Negotiated savings vs baseline spend',                     '%',       'higher_is_better'),
(59, 59, 'Strategic Contract Cycle Time',     'Days from award to executed framework contract',           'days',    'lower_is_better'),
(60, 60, 'Contract Renewal On-Time Rate',     'Percentage of contracts renewed before expiry',            '%',       'higher_is_better'),
(61, 61, 'Catalog Coverage Rate',             'Percentage of spend through catalogued items',             '%',       'higher_is_better'),
(62, 62, 'Maverick Spend Rate',               'Off-contract spend as percentage of managed category spend','%',      'lower_is_better'),
(63, 63, 'Supplier Scorecard Timeliness',     'Percentage of supplier reviews completed by due date',       '%',       'higher_is_better'),
(64, 64, 'Supplier Corrective Action Rate',   'Corrective actions as percentage of active strategic suppliers','%',   'lower_is_better');

-- ===============================================
-- Junction: Metric <-> Data Element
-- ===============================================
INSERT INTO metric_data_element (metric_id, data_element_id, role) VALUES
-- Requisition Approval Cycle Time = PO Date - Requisition Date
(1, 1, 'input'),
(1, 3, 'input'),
-- Vendor Lead Time = Goods Receipt Date - PO Date
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
-- Cost Per Payment Transaction
(7, 61, 'numerator'),
(7, 62, 'denominator'),
-- On-Time Delivery Rate = Actual <= Requested
(10, 13, 'input'),
(10, 14, 'input'),
(10, 19, 'dimension'),
-- Shipment Accuracy Rate
(11, 15, 'numerator'),
-- Billing Accuracy Rate
(12, 16, 'numerator'),
-- Days Sales Outstanding = Customer Payment Date - Invoice Date (via Billing Date proxy)
(13, 17, 'input'),
(13, 20, 'numerator'),
(13, 19, 'dimension'),
-- Order-to-Cash (complete metric 8, 9, 14)
(8,  21, 'numerator'),
(8,  22, 'denominator'),
(9,  11, 'input'),
(9,  23, 'input'),
(14, 24, 'input'),
(14, 25, 'input'),
(14, 19, 'dimension'),
-- Plan-to-Produce
(15, 33, 'input'),
(15, 34, 'input'),
(16, 35, 'input'),
(16, 36, 'input'),
(16, 19, 'dimension'),
(17, 31, 'numerator'),
(17, 32, 'denominator'),
(18, 28, 'input'),
(18, 29, 'input'),
(19, 28, 'input'),
(19, 29, 'input'),
(20, 28, 'input'),
(20, 29, 'input'),
(21, 37, 'numerator'),
(21, 38, 'denominator'),
(22, 30, 'numerator'),
(22, 27, 'denominator'),
(23, 26, 'input'),
(23, 39, 'input'),
(24, 40, 'input'),
(24, 41, 'input'),
(24, 27, 'denominator'),
-- Hire-to-Retire
(25, 42, 'input'),
(25, 43, 'input'),
(26, 60, 'numerator'),
(26, 59, 'denominator'),
(27, 44, 'input'),
(27, 46, 'input'),
(28, 50, 'numerator'),
(28, 49, 'denominator'),
(29, 51, 'numerator'),
(29, 49, 'denominator'),
(30, 52, 'numerator'),
(30, 53, 'denominator'),
(31, 56, 'numerator'),
(31, 57, 'denominator'),
(32, 54, 'numerator'),
(32, 55, 'denominator'),
(33, 58, 'numerator'),
(33, 49, 'denominator'),
(34, 45, 'input'),
(34, 46, 'input'),
-- Record-to-Report
(35, 65, 'numerator'),
(35, 64, 'denominator'),
(36, 63, 'input'),
(36, 76, 'input'),
(37, 68, 'input'),
(37, 66, 'input'),
(38, 67, 'numerator'),
(39, 68, 'input'),
(39, 69, 'input'),
(40, 77, 'numerator'),
(40, 78, 'denominator'),
(41, 71, 'numerator'),
(41, 12, 'denominator'),
(42, 72, 'numerator'),
(42, 71, 'denominator'),
(43, 69, 'input'),
(43, 73, 'input'),
(44, 75, 'input'),
(44, 74, 'input'),
-- Lead-to-Order
(45, 88, 'numerator'),
(45, 87, 'denominator'),
(46, 79, 'input'),
(46, 80, 'input'),
(47, 90, 'numerator'),
(47, 87, 'denominator'),
(48, 83, 'input'),
(48, 12, 'input'),
(49, 92, 'numerator'),
(49, 91, 'denominator'),
(50, 85, 'numerator'),
(51, 84, 'input'),
(51, 86, 'input'),
(52, 85, 'numerator'),
(52, 92, 'denominator'),
(53, 21, 'numerator'),
(53, 22, 'denominator'),
(54, 79, 'input'),
(54, 11, 'input'),
-- Source-to-Pay
(55, 94, 'numerator'),
(55, 93, 'denominator'),
(56, 95, 'input'),
(56, 97, 'input'),
(57, 102, 'numerator'),
(57, 101, 'denominator'),
(58, 94, 'numerator'),
(58, 93, 'denominator'),
(59, 95, 'input'),
(59, 97, 'input'),
(60, 97, 'input'),
(60, 98, 'input'),
(61, 94, 'numerator'),
(61, 93, 'denominator'),
(62, 100, 'numerator'),
(62, 94, 'denominator'),
(63, 105, 'numerator'),
(63, 104, 'denominator'),
(64, 103, 'numerator'),
(64, 104, 'denominator');

-- ===============================================
-- Junction: Data Element <-> System
-- ===============================================
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
(15, 3, 'WMTRANSFER', 'QTY_SHIPPED'),
-- Order-to-Cash (lineage completion) — illustrative SAP S/4HANA fields
(21, 1, 'VBAP',  'ABGRU'),
(22, 1, 'VBAP',  'POSNR'),
(23, 1, 'VBUK',  'CMGST'),
(24, 1, 'FQM_C_CASE', 'CREATION_DATE'),
(25, 1, 'FQM_C_CASE', 'CLOSE_DATE'),
-- Plan-to-Produce — SAP S/4HANA PP / QM / costing
(26, 1, 'AFKO',  'GAMNG'),
(27, 1, 'AFRU',  'LMNGA'),
(28, 1, 'AFKO',  'GSTRP'),
(29, 1, 'AFRU',  'ISDD'),
(30, 1, 'AFRU',  'XMNGA'),
(31, 1, 'MDKP',  'AUSKT'),
(32, 1, 'PLAF',  'PLNUM'),
(33, 1, 'PBIM',  'BEDAT'),
(34, 1, 'PBPT',  'DATUB'),
(35, 1, 'MPOP',  'PLNMG'),
(36, 1, 'VBAP',  'KWMENG'),
(37, 1, 'QALS',  'LMENGE01'),
(38, 1, 'QALS',  'LMENGEIST'),
(39, 1, 'MSEG',  'ERFMG'),
(40, 1, 'AFKO',  'PLSCN'),
(41, 1, 'COEP',  'WRTTP'),
-- Hire-to-Retire — SAP HCM (illustrative) + SuccessFactors
(42, 1, 'HRP1001', 'OBJID'),
(43, 1, 'HRP1001', 'BEGDA'),
(44, 1, 'PA0001',  'BEGDA'),
(45, 1, 'PA0001',  'BEGDA'),
(46, 1, 'PA0001',  'BEGDA'),
(47, 1, 'PC_PAYRESULT', 'PAYDATE'),
(48, 1, 'PA0000',  'BEGDA'),
(49, 1, 'PA0001',  'PERNR'),
(50, 1, 'PA0002',  'PERNR'),
(51, 1, 'HRP1001', 'OBJID'),
(52, 1, 'HRPAP00', 'SUBTY'),
(53, 1, 'HRPAP00', 'BEGDA'),
(54, 1, 'PA0378',  'BAREA'),
(55, 1, 'PA0378',  'PLTYP'),
(56, 1, 'PC_PAYRESULT', 'RUNIND'),
(57, 1, 'PC_PAYRESULT', 'SEQNR'),
(58, 1, 'PA0000',  'MASSN'),
(59, 1, 'PBAY',    'OFFER_ID'),
(60, 1, 'PBAY',    'ACCEPT_FLG'),
(42, 4, 'JobRequisition', 'createdDateTime'),
(43, 4, 'JobOffer',       'createdDateTime'),
(44, 4, 'PerPersonal',    'startDate'),
(45, 4, 'OnboardingInfo', 'startDate'),
(46, 4, 'OnboardingInfo', 'completionDate'),
(47, 4, 'PayrollResults', 'paymentDate'),
(48, 4, 'EmploymentTerm', 'endDate'),
(49, 4, 'EmpJob',         'fte'),
(50, 4, 'PerPersonal',    'validationStatus'),
(51, 4, 'Goal',           'employeeId'),
(52, 4, 'PerformanceReview', 'completionDate'),
(53, 4, 'PerformanceReview', 'dueDate'),
(54, 4, 'BenefitsEnrollment', 'enrolledCount'),
(55, 4, 'BenefitsEnrollment', 'eligibleCount'),
(56, 4, 'PayrollRun',     'runsWithoutRetro'),
(57, 4, 'PayrollRun',     'runCount'),
(58, 4, 'Termination',    'voluntaryCount'),
(59, 4, 'JobOffer',       'extendedCount'),
(60, 4, 'JobOffer',       'acceptedCount'),
(61, 1, 'FIBKPF', 'WRBTR'),
(62, 1, 'REGUH',  'LAUFD'),
-- Record-to-Report — SAP S/4HANA Finance (illustrative)
(63, 1, 'ACDOCA', 'BUDAT'),
(64, 1, 'ACDOCA', 'DOCLN'),
(65, 1, 'ACDOCA', 'XREVERSING'),
(66, 1, 'FAGLFLEXA', 'DATUM'),
(67, 1, 'ACDOCA', 'TSL'),
(68, 1, 'FIN_CLOSING', 'STARTDATE'),
(69, 1, 'FIN_CLOSING', 'ENDDATE'),
(70, 1, 'ECCS', 'RUN_DATE'),
(71, 1, 'ECCS', 'ADJ_AMOUNT'),
(72, 1, 'ECCS', 'IC_BALANCE'),
(73, 1, 'FIN_REP', 'PUBLISH_DATE'),
(74, 1, 'FIN_REP', 'DEADLINE'),
(75, 1, 'FIN_REP', 'FILING_DATE'),
(76, 1, 'BKPF', 'CPUDT'),
(77, 1, 'CLOSING_TASK', 'DONE_CNT'),
(78, 1, 'CLOSING_TASK', 'DUE_CNT'),
-- Lead-to-Order — Salesforce CRM + SAP order handoff
(79, 2, 'Lead', 'CreatedDate'),
(80, 2, 'Lead', 'FirstRespondedDate'),
(81, 2, 'Opportunity', 'CreatedDate'),
(82, 2, 'Opportunity', 'CloseDate'),
(83, 2, 'Opportunity', 'Amount'),
(84, 2, 'Quote', 'CreatedDate'),
(85, 2, 'Quote', 'VersionNumber'),
(86, 2, 'Contract', 'ActivatedDate'),
(86, 1, 'VBAK', 'ERDAT'),
(87, 2, 'Lead', 'Id'),
(88, 2, 'Lead', 'IsConverted'),
(89, 2, 'Opportunity', 'IsClosed'),
(90, 2, 'Opportunity', 'IsWon'),
(91, 2, 'Quote', 'Id'),
(92, 2, 'Quote', 'Status'),
-- Source-to-Pay — SAP S/4HANA MM / sourcing (illustrative)
(93, 1, 'FAGL_SPLINFO', 'ADDR_SPEND'),
(94, 1, 'FAGL_SPLINFO', 'MNGD_SPEND'),
(95, 1, 'BBP_PD', 'PUBLISH_DATE'),
(96, 1, 'BBP_PD', 'AWARD_DATE'),
(97, 1, 'A016', 'VDATU'),
(98, 1, 'A016', 'VDATU_END'),
(99, 1, 'WLK1', 'MATNR'),
(100, 1, 'EKPO', 'NETWR'),
(101, 1, 'BBP_PD', 'INVITE_CNT'),
(102, 1, 'BBP_PD', 'RESP_CNT'),
(103, 1, 'LFA1', 'QSSYS'),
(104, 1, 'SRM_SCORE', 'DUE_CNT'),
(105, 1, 'SRM_SCORE', 'DONE_CNT');

-- Reset sequences to avoid PK conflicts on future inserts
SELECT setval('workflow_id_seq',       (SELECT MAX(id) FROM workflow));
SELECT setval('operation_step_id_seq', (SELECT MAX(id) FROM operation_step));
SELECT setval('action_id_seq',         (SELECT MAX(id) FROM action));
SELECT setval('metric_id_seq',         (SELECT MAX(id) FROM metric));
SELECT setval('data_element_id_seq',   (SELECT MAX(id) FROM data_element));
SELECT setval('system_id_seq',         (SELECT MAX(id) FROM system));

COMMIT;
