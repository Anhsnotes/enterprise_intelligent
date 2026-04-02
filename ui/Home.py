import sys
from pathlib import Path

_p = Path(__file__).resolve().parent
sys.path.insert(0, str(_p.parent))

import streamlit as st
import pandas as pd
from collections import OrderedDict
from db import fetch_all
from ui.workflow_ui import (
    build_metric_hierarchy_mermaid,
    hierarchy_flowchart_legend_html,
    mermaid_escape_label,
    render_mermaid_html,
    sql_order_category,
    workflow_options_by_category,
)

st.set_page_config(page_title="Home", layout="wide")

st.title("Enterprise Intelligence")
st.caption(
    "Workflow **lineage** (cycle → source field) and **metric hierarchy** "
    "(control metrics rolling up to executive outcomes)."
)

tab_lineage, tab_hierarchy = st.tabs(["Workflow lineage", "Metric hierarchy"])

# -- Workflow lineage ---------------------------------------------------------
LINEAGE_SQL = """
SELECT
    os.id   AS step_id,   os.name AS step_name,   os.description AS step_desc,   os.step_order,
    a.id    AS action_id, a.name  AS action_name, a.description  AS action_desc, a.action_type,
    m.id    AS metric_id, m.name  AS metric_name, m.description  AS metric_desc, m.unit, m.direction,
    de.id   AS de_id,     de.name AS de_name,     de.data_type,  mde.role AS de_role,
    s.id    AS sys_id,    s.name  AS sys_name,    s.system_type, des.source_table, des.source_field
FROM operation_step os
LEFT JOIN action a              ON a.operation_step_id  = os.id
LEFT JOIN metric m              ON m.action_id          = a.id
LEFT JOIN metric_data_element mde ON mde.metric_id      = m.id
LEFT JOIN data_element de       ON de.id                = mde.data_element_id
LEFT JOIN data_element_system des ON des.data_element_id = de.id
LEFT JOIN system s              ON s.id                 = des.system_id
WHERE os.workflow_id = %s
ORDER BY os.step_order, a.id, m.id, de.name, s.name
"""


def build_tree(rows):
    steps = OrderedDict()
    for r in rows:
        sid = r["step_id"]
        if sid not in steps:
            steps[sid] = {
                "name": r["step_name"], "desc": r["step_desc"],
                "order": r["step_order"], "actions": OrderedDict(),
            }
        if not r["action_id"]:
            continue
        aid = r["action_id"]
        actions = steps[sid]["actions"]
        if aid not in actions:
            actions[aid] = {
                "name": r["action_name"], "desc": r["action_desc"],
                "type": r["action_type"], "metrics": OrderedDict(),
            }
        if not r["metric_id"]:
            continue
        mid = r["metric_id"]
        metrics = actions[aid]["metrics"]
        if mid not in metrics:
            metrics[mid] = {
                "name": r["metric_name"], "desc": r["metric_desc"],
                "unit": r["unit"], "direction": r["direction"],
                "data_elements": OrderedDict(),
            }
        if not r["de_id"]:
            continue
        de_key = (r["de_id"], r["de_role"])
        des = metrics[mid]["data_elements"]
        if de_key not in des:
            des[de_key] = {
                "name": r["de_name"], "type": r["data_type"],
                "role": r["de_role"], "systems": [],
            }
        if r["sys_id"]:
            already = {s["id"] for s in des[de_key]["systems"]}
            if r["sys_id"] not in already:
                des[de_key]["systems"].append({
                    "id": r["sys_id"], "name": r["sys_name"],
                    "stype": r["system_type"],
                    "table": r["source_table"], "field": r["source_field"],
                })
    return steps


DIRECTION_SYM = {"higher_is_better": "^ higher is better", "lower_is_better": "v lower is better", "target": "* target"}
LAYER_COLORS = {
    "step":   "#1976D2",
    "action": "#388E3C",
    "metric": "#E53935",
    "de":     "#7B1FA2",
    "system": "#546E7A",
}


def flowchart_legend_html() -> str:
    """Swatches aligned with Mermaid classDef (wf, st, ac, mt, de, sy) in build_mermaid_flowchart."""
    items = (
        ("#1565c0", "#0d47a1", "Workflow"),
        ("#1976d2", "#0d47a1", "Operation step"),
        ("#2e7d32", "#1b5e20", "Action"),
        ("#c62828", "#b71c1c", "Metric"),
        ("#6a1b9a", "#4a148c", "Data element"),
        ("#455a64", "#263238", "System (source field)"),
    )
    chips = []
    for fill, stroke, label in items:
        chips.append(
            f'<span style="display:inline-flex;align-items:center;gap:6px;font-size:0.9em">'
            f'<span style="display:inline-block;width:14px;height:14px;border-radius:3px;'
            f"background:{fill};border:2px solid {stroke};flex-shrink:0\"></span>"
            f"{label}</span>"
        )
    inner = " ".join(chips)
    return (
        '<div style="display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;'
        "margin:0 0 12px 0;padding:10px 14px;border:1px solid rgba(127,127,127,0.28);"
        'border-radius:8px;background:rgba(128,128,128,0.06);">'
        '<strong style="margin-right:4px;font-size:0.95em">Legend</strong>'
        f"{inner}</div>"
    )


def render_tree_html(tree):
    parts = []
    for step in tree.values():
        parts.append(
            f'<div style="border-left:4px solid {LAYER_COLORS["step"]};padding:10px 0 10px 18px;margin:10px 0">'
            f'<div style="font-weight:700;font-size:1.08em;color:{LAYER_COLORS["step"]}">'
            f'Step {step["order"]}: {step["name"]}</div>'
        )
        if step["desc"]:
            parts.append(f'<div style="color:#888;font-size:0.88em;margin-bottom:4px">{step["desc"]}</div>')

        if not step["actions"]:
            parts.append('<div style="color:#aaa;padding-left:18px;font-style:italic">No actions defined</div>')

        for action in step["actions"].values():
            parts.append(
                f'<div style="border-left:4px solid {LAYER_COLORS["action"]};padding:6px 0 6px 18px;margin:6px 0">'
                f'<span style="font-weight:600">{action["name"]}</span>'
                f' <span style="background:#e8f5e9;color:#2e7d32;padding:1px 8px;border-radius:4px;'
                f'font-size:0.78em;font-weight:500">{action["type"]}</span>'
            )

            if not action["metrics"]:
                parts.append('<div style="color:#aaa;padding-left:18px;font-style:italic">No metrics defined</div>')

            for metric in action["metrics"].values():
                dir_label = DIRECTION_SYM.get(metric["direction"], "")
                parts.append(
                    f'<div style="border-left:4px solid {LAYER_COLORS["metric"]};padding:5px 0 5px 18px;margin:5px 0">'
                    f'<span style="font-weight:500;color:{LAYER_COLORS["metric"]}">{metric["name"]}</span>'
                    f' <span style="color:#999;font-size:0.85em">({metric["unit"]}, {dir_label})</span>'
                )

                if not metric["data_elements"]:
                    parts.append('<div style="color:#aaa;padding-left:18px;font-style:italic">No data elements linked</div>')

                for de in metric["data_elements"].values():
                    sys_parts = []
                    for s in de["systems"]:
                        sys_parts.append(
                            f'<span style="background:#eceff1;color:#37474f;padding:1px 6px;border-radius:3px;'
                            f'font-size:0.82em">{s["name"]}</span>'
                            f' <span style="color:#90a4ae;font-size:0.82em">{s["table"]}.{s["field"]}</span>'
                        )
                    sys_str = " | ".join(sys_parts) if sys_parts else '<span style="color:#ccc">unmapped</span>'

                    parts.append(
                        f'<div style="border-left:4px solid {LAYER_COLORS["de"]};padding:3px 0 3px 18px;margin:3px 0">'
                        f'<span>{de["name"]}</span>'
                        f' <span style="background:#f3e5f5;color:#6a1b9a;padding:1px 6px;border-radius:4px;'
                        f'font-size:0.76em">{de["role"]}</span>'
                        f' <- {sys_str}'
                        f'</div>'
                    )

                parts.append('</div>')
            parts.append('</div>')
        parts.append('</div>')
    return "".join(parts)


def build_mermaid_flowchart(wf, tree, direction: str = "TB"):
    """Build Mermaid flowchart from workflow + nested tree. direction: TB (vertical) or LR (sideways / left-to-right)."""
    direction = (direction or "TB").upper()
    if direction not in ("TB", "LR"):
        direction = "TB"
    lines = [
        f"flowchart {direction}",
        "  %% Enterprise Intelligence lineage (auto-generated)",
    ]
    class_lines = [
        "  classDef wf fill:#1565c0,stroke:#0d47a1,stroke-width:2px,color:#fff",
        "  classDef st fill:#1976d2,stroke:#0d47a1,color:#fff",
        "  classDef ac fill:#2e7d32,stroke:#1b5e20,color:#fff",
        "  classDef mt fill:#c62828,stroke:#b71c1c,color:#fff",
        "  classDef de fill:#6a1b9a,stroke:#4a148c,color:#fff",
        "  classDef sy fill:#455a64,stroke:#263238,color:#fff",
    ]

    wf_id = wf["id"]
    wf_node = f"WF{wf_id}"
    wf_lbl = mermaid_escape_label(f"Workflow: {wf['name']}")
    lines.append(f'  {wf_node}["{wf_lbl}"]:::wf')

    if not tree:
        lines.extend(class_lines)
        return "\n".join(lines)

    for sid, step in tree.items():
        st_node = f"S{sid}"
        st_lbl = mermaid_escape_label(f"Step {step['order']}: {step['name']}")
        lines.append(f'  {st_node}["{st_lbl}"]:::st')
        lines.append(f"  {wf_node} --> {st_node}")

        if not step["actions"]:
            continue

        for aid, action in step["actions"].items():
            ac_node = f"A{aid}"
            ac_lbl = mermaid_escape_label(f"{action['name']} ({action['type']})")
            lines.append(f'  {ac_node}["{ac_lbl}"]:::ac')
            lines.append(f"  {st_node} --> {ac_node}")

            if not action["metrics"]:
                continue

            for mid, metric in action["metrics"].items():
                mt_node = f"M{mid}"
                unit = metric.get("unit") or " - "
                direction = (metric.get("direction") or "").replace("_", " ")
                mt_lbl = mermaid_escape_label(f"{metric['name']} [{unit}, {direction}]")
                lines.append(f'  {mt_node}["{mt_lbl}"]:::mt')
                lines.append(f"  {ac_node} --> {mt_node}")

                if not metric["data_elements"]:
                    continue

                for (de_id, role), de in metric["data_elements"].items():
                    role_s = (role or "link").replace(" ", "_")
                    de_node = f"DE{de_id}_{role_s}"
                    de_lbl = mermaid_escape_label(f"{de['name']}, role: {role}")
                    lines.append(f'  {de_node}["{de_lbl}"]:::de')
                    lines.append(f"  {mt_node} --> {de_node}")

                    if not de["systems"]:
                        continue

                    for idx, sysrow in enumerate(de["systems"]):
                        tbl = sysrow.get("table") or "?"
                        fld = sysrow.get("field") or "?"
                        sy_node = f"SY{sysrow['id']}_DE{de_id}_{idx}"
                        sy_lbl = mermaid_escape_label(
                            f"{sysrow['name']}: {tbl}.{fld}"
                        )
                        lines.append(f'  {sy_node}["{sy_lbl}"]:::sy')
                        lines.append(f"  {de_node} --> {sy_node}")

    lines.extend(class_lines)
    return "\n".join(lines)


with tab_lineage:
    st.markdown(
        "Trace a **business workflow** from cycle through steps, actions, metrics, "
        "data elements, and source system fields."
    )
    workflows = fetch_all(
        f"SELECT id, name, description, category FROM workflow {sql_order_category()}"
    )
    if not workflows:
        st.info("No workflows found. Use the **Workflows** page to add one.")
    else:
        _wf_labels, wf_options = workflow_options_by_category(workflows)
        _DEFAULT_WF = "Procure-to-Pay"
        _wf_idx = next(
            (i for i, lab in enumerate(_wf_labels) if wf_options[lab]["name"] == _DEFAULT_WF),
            0,
        )
        selected_label = st.selectbox("Workflow", _wf_labels, index=_wf_idx)
        wf = wf_options[selected_label]

        if wf["description"]:
            st.caption(wf["description"])

        rows = fetch_all(LINEAGE_SQL, (wf["id"],))
        tree = build_tree(rows)

        n_steps = len(tree)
        n_actions = sum(len(s["actions"]) for s in tree.values())
        n_metrics = sum(
            len(m)
            for s in tree.values()
            for m in [a["metrics"] for a in s["actions"].values()]
        )
        n_des = len({
            de_key
            for s in tree.values()
            for a in s["actions"].values()
            for m in a["metrics"].values()
            for de_key in m["data_elements"]
        })

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Steps", n_steps)
        c2.metric("Actions", n_actions)
        c3.metric("Metrics", n_metrics)
        c4.metric("Data Elements", n_des)

        st.divider()

        tab_mermaid, tab_tree, tab_table = st.tabs(
            ["Lineage Flowchart", "Lineage Tree", "Lineage Table"]
        )

        with tab_mermaid:
            st.caption(
                "Interactive flowchart powered by [Mermaid.js](https://mermaid.js.org/) "
                "(workflow -> step -> action -> metric -> data element -> system field). "
                "**Zoom:** use the **- / + / Reset** bar above the chart inside the frame, or **Ctrl+scroll** "
                "(**Cmd+scroll** on Mac) while the pointer is over the chart area."
            )
            if not tree:
                st.info("This workflow has no operation steps yet.")
            else:
                col_layout, _ = st.columns([1, 4])
                with col_layout:
                    mermaid_dir = st.radio(
                        "Diagram layout",
                        ("LR", "TB"),
                        horizontal=True,
                        index=0,
                        format_func=lambda d: "Left -> right"
                        if d == "LR"
                        else "Top -> bottom",
                        help="`flowchart LR` runs left-to-right; `flowchart TB` runs top-down.",
                    )
                st.markdown(flowchart_legend_html(), unsafe_allow_html=True)
                mermaid_src = build_mermaid_flowchart(wf, tree, direction=mermaid_dir)
                with st.expander("View / copy Mermaid source"):
                    st.code(mermaid_src, language="mermaid")
                render_mermaid_html(mermaid_src, height=950)

        with tab_tree:
            if not tree:
                st.info("This workflow has no operation steps yet.")
            else:
                st.markdown(render_tree_html(tree), unsafe_allow_html=True)

        with tab_table:
            if not rows:
                st.info("This workflow has no lineage data yet.")
            else:
                df = pd.DataFrame(rows)
                display_cols = [
                    "step_order", "step_name", "action_name", "action_type",
                    "metric_name", "unit", "direction",
                    "de_name", "de_role", "data_type",
                    "sys_name", "system_type", "source_table", "source_field",
                ]
                df = df[[c for c in display_cols if c in df.columns]].rename(columns={
                    "step_order": "Step #", "step_name": "Step", "action_name": "Action",
                    "action_type": "Type", "metric_name": "Metric", "unit": "Unit",
                    "direction": "Direction", "de_name": "Data Element",
                    "de_role": "Role", "data_type": "Data Type",
                    "sys_name": "System", "system_type": "Sys Type",
                    "source_table": "Table", "source_field": "Field",
                })
                st.dataframe(df, use_container_width=True, hide_index=True)


# -- Metric hierarchy --------------------------------------------------------
LEVEL_LABEL = {
    "control": "L1 Control",
    "workflow": "L2 Workflow",
    "cross_workflow": "L3 Cross-workflow",
    "executive": "L4 Executive",
}


def _hierarchy_tables_exist():
    try:
        col = fetch_all(
            """
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'metric' AND column_name = 'metric_level'
            """
        )
        tab = fetch_all(
            """
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'metric_rollup'
            """
        )
        return bool(col) and bool(tab)
    except Exception:
        return False


with tab_hierarchy:
    st.markdown(
        "**Roll-up chain** from control metrics (L1) through workflow (L2), "
        "cross-workflow (L3), to executive (L4). "
        "See `metric_rollup` and `metric.metric_level` in the database."
    )
    if not _hierarchy_tables_exist():
        st.warning(
            "Metric hierarchy is not installed. Apply `db/migration_metric_hierarchy.sql` "
            "and load `db/seed_metric_hierarchy.sql` (or the hierarchy section of `db/seed.sql`), then refresh."
        )
    else:
        metrics = fetch_all(
            """
            SELECT id, action_id, workflow_id, metric_level, name, description, unit, direction
            FROM metric
            ORDER BY metric_level, id
            """
        )
        rollup = fetch_all(
            """
            SELECT
                mr.parent_metric_id,
                mr.child_metric_id,
                mr.rollup_rule,
                mr.sort_order,
                mr.notes,
                p.name  AS parent_name,
                p.metric_level AS parent_level,
                c.name  AS child_name,
                c.metric_level AS child_level
            FROM metric_rollup mr
            JOIN metric p ON p.id = mr.parent_metric_id
            JOIN metric c ON c.id = mr.child_metric_id
            ORDER BY mr.parent_metric_id, mr.sort_order, mr.child_metric_id
            """
        )

        if not metrics:
            st.info("No metrics in the database.")
        else:
            m_by_id = {m["id"]: m for m in metrics}
            children_map = {}
            for r in rollup:
                children_map.setdefault(r["parent_metric_id"], []).append(r)

            for pid in children_map:
                children_map[pid].sort(key=lambda x: (x["sort_order"], x["child_metric_id"]))

            child_ids = {r["child_metric_id"] for r in rollup}
            root_ids = [
                m["id"]
                for m in metrics
                if m["id"] in children_map and m["id"] not in child_ids
            ]

            h_mermaid, h_tree, h_edges, h_levels = st.tabs(
                ["Roll-up flowchart", "Roll-up tree", "Roll-up edges", "Metrics by level"]
            )

            with h_mermaid:
                st.caption(
                    "Interactive flowchart powered by [Mermaid.js](https://mermaid.js.org/) "
                    "(anchor → executive / rolled-up metrics → … → control metrics). "
                    "Edge labels show the roll-up rule. "
                    "**Zoom:** use the **- / + / Reset** bar above the chart inside the frame, or **Ctrl+scroll** "
                    "(**Cmd+scroll** on Mac) while the pointer is over the chart area."
                )
                if not rollup:
                    st.info("No rows in `metric_rollup` yet. Load hierarchy seed data.")
                else:
                    col_layout, _ = st.columns([1, 4])
                    with col_layout:
                        h_dir = st.radio(
                            "Diagram layout",
                            ("LR", "TB"),
                            horizontal=True,
                            index=0,
                            format_func=lambda d: "Left -> right"
                            if d == "LR"
                            else "Top -> bottom",
                            help="`flowchart LR` runs left-to-right; `flowchart TB` runs top-down.",
                            key="hier_mermaid_dir",
                        )
                    st.markdown(hierarchy_flowchart_legend_html(), unsafe_allow_html=True)
                    h_src = build_metric_hierarchy_mermaid(
                        m_by_id, rollup, direction=h_dir
                    )
                    with st.expander("View / copy Mermaid source"):
                        st.code(h_src, language="mermaid")
                    render_mermaid_html(h_src, height=950)

            with h_tree:
                st.subheader("From executive roots downward")
                if not rollup:
                    st.info("No rows in `metric_rollup` yet. Load seed data for the hierarchy section.")
                elif not root_ids:
                    st.info("No root metrics found (every parent is also a child). Check data integrity.")
                else:

                    def render_node(mid: int, depth: int = 0):
                        m = m_by_id.get(mid)
                        if not m:
                            return
                        indent = "    " * depth
                        lvl = LEVEL_LABEL.get(m["metric_level"], m["metric_level"])
                        unit = m.get("unit") or "—"
                        st.write(
                            f"{indent}**{m['name']}** · {lvl} · {unit} · "
                            f"{m['direction'].replace('_', ' ')}"
                        )
                        if m.get("description"):
                            st.caption(f"{indent}{m['description']}")
                        for edge in children_map.get(mid, []):
                            rule = edge["rollup_rule"].replace("_", " ")
                            note = f" — {edge['notes']}" if edge.get("notes") else ""
                            st.write(
                                f"{indent}  ↳ {rule}{note} → **{edge['child_name']}** "
                                f"({LEVEL_LABEL.get(edge['child_level'], edge['child_level'])})"
                            )
                            render_node(edge["child_metric_id"], depth + 1)

                    for rid in sorted(root_ids):
                        with st.container():
                            render_node(rid, 0)
                            st.divider()

            with h_edges:
                if rollup:
                    df = pd.DataFrame(rollup)
                    show = df[
                        [
                            "parent_name",
                            "parent_level",
                            "rollup_rule",
                            "sort_order",
                            "child_name",
                            "child_level",
                            "notes",
                        ]
                    ].rename(
                        columns={
                            "parent_name": "Parent metric",
                            "parent_level": "Parent level",
                            "rollup_rule": "Roll-up rule",
                            "sort_order": "Order",
                            "child_name": "Child metric",
                            "child_level": "Child level",
                            "notes": "Notes",
                        }
                    )
                    st.dataframe(show, use_container_width=True, hide_index=True)
                else:
                    st.info("No roll-up edges defined.")

            with h_levels:
                dfm = pd.DataFrame(metrics)
                dfm["level"] = dfm["metric_level"].map(LEVEL_LABEL).fillna(dfm["metric_level"])
                st.dataframe(
                    dfm[
                        ["id", "level", "name", "unit", "direction", "workflow_id", "action_id"]
                    ].rename(columns={"workflow_id": "workflow_id (L2 anchor)"}),
                    use_container_width=True,
                    hide_index=True,
                )

                unlinked = [
                    m
                    for m in metrics
                    if m["metric_level"] == "control" and m["id"] not in child_ids
                ]
                st.markdown(
                    "**Control metrics not referenced as children in any roll-up** "
                    "(expected for many leaves)."
                )
                st.caption(
                    f"Count: {len(unlinked)} — e.g. baseline operational metrics awaiting hierarchy linkage."
                )
