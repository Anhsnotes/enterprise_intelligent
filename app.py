import base64
import re
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from collections import OrderedDict
from db import fetch_all

st.set_page_config(page_title="Enterprise Intelligence", layout="wide")

st.title("Enterprise Intelligence")
st.markdown("**Lineage Viewer** — trace every workflow from business cycle down to source system field.")

# ── Workflow selector ──────────────────────────────────────────────
workflows = fetch_all("SELECT id, name, description FROM workflow ORDER BY name")

if not workflows:
    st.info("No workflows found. Use the **Workflows** page to add one.")
    st.stop()

wf_options = {w["name"]: w for w in workflows}
selected_name = st.selectbox("Workflow", list(wf_options.keys()))
wf = wf_options[selected_name]

if wf["description"]:
    st.caption(wf["description"])


# ── Fetch full lineage in one query ────────────────────────────────
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

rows = fetch_all(LINEAGE_SQL, (wf["id"],))


# ── Build nested tree from flat rows ──────────────────────────────
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


tree = build_tree(rows)

# ── Summary metrics ────────────────────────────────────────────────
n_steps = len(tree)
n_actions = sum(len(s["actions"]) for s in tree.values())
n_metrics = sum(len(m) for s in tree.values() for m in [a["metrics"] for a in s["actions"].values()])
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

# ── Tabs: Tree vs Mermaid flowchart vs Table ───────────────────────
tab_tree, tab_mermaid, tab_table = st.tabs(
    ["Lineage Tree", "Lineage Flowchart (Mermaid)", "Lineage Table"]
)

DIRECTION_SYM = {"higher_is_better": "▲ higher is better", "lower_is_better": "▼ lower is better", "target": "◆ target"}
LAYER_COLORS = {
    "step":   "#1976D2",
    "action": "#388E3C",
    "metric": "#E53935",
    "de":     "#7B1FA2",
    "system": "#546E7A",
}


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
                        f' &larr; {sys_str}'
                        f'</div>'
                    )

                parts.append('</div>')
            parts.append('</div>')
        parts.append('</div>')
    return "".join(parts)


def _mermaid_escape_label(text, max_len=72):
    if text is None:
        return ""
    s = str(text).replace("\n", " ").replace("\r", " ")
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) > max_len:
        s = s[: max_len - 1] + "…"
    # Avoid breaking Mermaid ["..."] node syntax
    s = s.replace('"', "'").replace("[", "(").replace("]", ")")
    return s


def build_mermaid_flowchart(wf, tree):
    """Build Mermaid flowchart TB from workflow + nested tree (same structure as HTML tree)."""
    lines = [
        "flowchart TB",
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
    wf_lbl = _mermaid_escape_label(f"Workflow · {wf['name']}")
    lines.append(f'  {wf_node}["{wf_lbl}"]:::wf')

    if not tree:
        lines.extend(class_lines)
        return "\n".join(lines)

    for sid, step in tree.items():
        st_node = f"S{sid}"
        st_lbl = _mermaid_escape_label(f"Step {step['order']}: {step['name']}")
        lines.append(f'  {st_node}["{st_lbl}"]:::st')
        lines.append(f"  {wf_node} --> {st_node}")

        if not step["actions"]:
            continue

        for aid, action in step["actions"].items():
            ac_node = f"A{aid}"
            ac_lbl = _mermaid_escape_label(f"{action['name']} ({action['type']})")
            lines.append(f'  {ac_node}["{ac_lbl}"]:::ac')
            lines.append(f"  {st_node} --> {ac_node}")

            if not action["metrics"]:
                continue

            for mid, metric in action["metrics"].items():
                mt_node = f"M{mid}"
                unit = metric.get("unit") or "—"
                direction = (metric.get("direction") or "").replace("_", " ")
                mt_lbl = _mermaid_escape_label(f"{metric['name']} [{unit}, {direction}]")
                lines.append(f'  {mt_node}["{mt_lbl}"]:::mt')
                lines.append(f"  {ac_node} --> {mt_node}")

                if not metric["data_elements"]:
                    continue

                for (de_id, role), de in metric["data_elements"].items():
                    role_s = (role or "link").replace(" ", "_")
                    de_node = f"DE{de_id}_{role_s}"
                    de_lbl = _mermaid_escape_label(f"{de['name']} · role: {role}")
                    lines.append(f'  {de_node}["{de_lbl}"]:::de')
                    lines.append(f"  {mt_node} --> {de_node}")

                    if not de["systems"]:
                        continue

                    for idx, sysrow in enumerate(de["systems"]):
                        tbl = sysrow.get("table") or "?"
                        fld = sysrow.get("field") or "?"
                        sy_node = f"SY{sysrow['id']}_DE{de_id}_{idx}"
                        sy_lbl = _mermaid_escape_label(
                            f"{sysrow['name']} · {tbl}.{fld}"
                        )
                        lines.append(f'  {sy_node}["{sy_lbl}"]:::sy')
                        lines.append(f"  {de_node} --> {sy_node}")

    lines.extend(class_lines)
    return "\n".join(lines)


def render_mermaid_html(diagram_source: str, height: int = 920):
    """Render Mermaid via CDN inside a Streamlit HTML component (base64 payload avoids escaping issues)."""
    b64 = base64.standard_b64encode(diagram_source.encode("utf-8")).decode("ascii")
    html_page = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
</head>
<body style="margin:0;padding:8px;background:transparent;">
  <div id="mmd-out" class="mermaid"></div>
  <script>
    (async function () {{
      const diagram = atob("{b64}");
      const el = document.getElementById("mmd-out");
      el.textContent = diagram;
      mermaid.initialize({{
        startOnLoad: false,
        theme: "dark",
        securityLevel: "loose",
        flowchart: {{ useMaxWidth: true, htmlLabels: true, curve: "basis" }}
      }});
      await mermaid.run({{ querySelector: "#mmd-out" }});
    }})();
  </script>
</body>
</html>"""
    components.html(html_page, height=height, scrolling=True)


with tab_tree:
    if not tree:
        st.info("This workflow has no operation steps yet.")
    else:
        st.markdown(render_tree_html(tree), unsafe_allow_html=True)

with tab_mermaid:
    st.caption(
        "Interactive flowchart powered by [Mermaid.js](https://mermaid.js.org/) "
        "(workflow → step → action → metric → data element → system field)."
    )
    if not tree:
        st.info("This workflow has no operation steps yet.")
    else:
        mermaid_src = build_mermaid_flowchart(wf, tree)
        with st.expander("View / copy Mermaid source"):
            st.code(mermaid_src, language="mermaid")
        # Tall iframe: large lineages scroll inside the component
        render_mermaid_html(mermaid_src, height=950)

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
