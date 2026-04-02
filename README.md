# Enterprise Intelligence

A framework for standardizing decision-making across enterprises by redesigning Business Intelligence from the ground up.

## Streamlit UI

The app code is under `ui/`: entry point `ui/Home.py` (workflow **lineage** and **metric hierarchy** Mermaid views), multi-page routes in `ui/pages/`, and shared helpers in `ui/workflow_ui.py`. The database module stays at the repository root (`db.py`). From the repo root:

```bash
streamlit run ui/Home.py
```

## Motivation

Business Intelligence has long struggled to keep pace with the rate of change in business. Despite its promise of delivering actionable, data-driven insight, BI consistently falls short. The root cause is structural: every BI project carries technical debt from its inception, and that debt compounds over time. Each dashboard, report, and data pipeline is built to serve an isolated use case, with its own assumptions, definitions, and data lineage. The result is a landscape of fragmented artifacts that cannot be consolidated to tell a consistent, end-to-end story across departments.

This fragmentation is not a tooling problem - it is a design problem. Organizations do not lack data, nor do they lack technology. What they lack is a **coherent architectural foundation** that aligns intelligence with how the business actually operates.

Enterprise Intelligence addresses this by providing a layered framework that maps directly to the structure of business itself, rather than to the structure of individual analytics projects. The framework works top-down through six layers:

```
+---------------------------------------------+
|       Business Workflow & Cycles            |  How the business operates over time
+---------------------------------------------+
|       Business Operation Steps              |  The discrete steps within each workflow
+---------------------------------------------+
|       Control Actions                       |  The decisions and actions taken at each step
+---------------------------------------------+
|       Control Metrics                       |  The measures that govern each action
+---------------------------------------------+
|       Standard Data Points                  |  The canonical data the business produces
+---------------------------------------------+
|       System Layer (ERP / Source Systems)   |  Where data originates
+---------------------------------------------+
```

**Business Workflow & Cycles** - The top layer captures the standard workflows and cycles that define how an enterprise runs: plan-to-produce, procure-to-pay, order-to-cash, hire-to-retire, and so on. These are the rhythms of the business, not the rhythms of analytics projects.

**Business Operation Steps** - Each workflow decomposes into a sequence of standard operation steps. These steps define the structure of work - the phases and handoffs that move a workflow from initiation to completion.

**Control Actions** - Within each operation step, there are specific decisions and actions that determine outcomes. These are the levers the business pulls: approving a purchase order, releasing a production schedule, adjusting a forecast. Intelligence exists to inform and improve these actions.

**Control Metrics** - Every control action is governed by metrics that tell the business whether that action is producing the expected result. These are not vanity KPIs - they are the feedback signals that trigger corrective action when performance drifts.

**Standard Data Points** - Beneath metrics are the concrete, canonical data points the business generates. Standardizing these definitions eliminates the inconsistencies that plague fragmented BI.

**System Layer** - At the foundation sit the ERP and source systems that produce the data. The framework maps standard data points back to standard system structures, making the path from source to insight traceable and repeatable.

By starting from workflows rather than from tools or datasets, the framework ensures that intelligence is organized around what the business does - not around what was convenient to build. This makes it possible to consolidate BI artifacts into a unified, consistent layer that serves the entire enterprise.

The framework is designed to support businesses at any scale, from a small operation running a single ERP to a large enterprise with dozens of systems and thousands of users. The goal is to set a concrete foundation for Enterprise Intelligence from the very start - one that grows with the organization rather than accumulating debt against it.

## Reference workflows (by category)

Workflows are stored with a **category** so lists and the lineage viewer stay easy to scan. The seed data includes:

| Category | Workflows |
|----------|-----------|
| Finance & Control | Record-to-Report (R2R) |
| Sales & Revenue | Order-to-Cash; Lead-to-Order / Opportunity-to-Order |
| Procurement & Supply Chain | Procure-to-Pay; Source-to-Pay / Source-to-Contract |
| Operations & Manufacturing | Plan-to-Produce |
| Human Capital | Hire-to-Retire |

The seed includes full operation-step, action, metric, and lineage chains for all seven workflows. Existing databases created before `workflow.category` or before these chains were added should run `db/migration_workflow_category.sql` if needed, then reload or migrate seed data.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
