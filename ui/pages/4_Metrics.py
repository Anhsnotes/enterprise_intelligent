import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
import pandas as pd
from db import fetch_all, execute
from ui.workflow_ui import sql_order_category, workflow_options_by_category

st.set_page_config(page_title="Metrics", layout="wide")
st.title("Metrics")
st.caption(
    "Control metrics that govern each action. "
    "**metric_level** is `control` here; rolled-up metrics (workflow / cross-workflow / executive) "
    "are defined in the database and visualized under **Home → Metric hierarchy**."
)

DIRECTIONS = ["higher_is_better", "lower_is_better", "target"]

workflows = fetch_all(f"SELECT id, name, category FROM workflow {sql_order_category()}")
if not workflows:
    st.info("Create a workflow first.")
    st.stop()

_wf_labels, _wf_map = workflow_options_by_category(workflows)
sel_wf = st.selectbox("Workflow", _wf_labels)
wf_id = _wf_map[sel_wf]["id"]

actions = fetch_all("""
    SELECT a.id, a.name, os.name AS step_name, os.step_order
    FROM action a
    JOIN operation_step os ON os.id = a.operation_step_id
    WHERE os.workflow_id = %s
    ORDER BY os.step_order, a.id
""", (wf_id,))

if not actions:
    st.info("Add actions to this workflow first.")
    st.stop()

act_map = {f"Step {a['step_order']} / {a['name']}": a["id"] for a in actions}
sel_act = st.selectbox("Action", list(act_map.keys()))
action_id = act_map[sel_act]

# -- Add new metric -------------------------------------------------
with st.expander("Add New Metric"):
    with st.form("add_metric", clear_on_submit=True):
        name = st.text_input("Name")
        desc = st.text_area("Description")
        unit = st.text_input("Unit", placeholder="e.g. %, days, $, count")
        direction = st.selectbox("Direction", DIRECTIONS)
        if st.form_submit_button("Add Metric") and name:
            try:
                execute(
                    """
                    INSERT INTO metric (action_id, workflow_id, metric_level, name, description, unit, direction)
                    VALUES (%s, NULL, 'control', %s, %s, %s, %s)
                    """,
                    (action_id, name, desc, unit, direction),
                )
                st.success(f"Added metric: {name}")
                st.rerun()
            except Exception as e:
                st.error(str(e))

# -- List -----------------------------------------------------------
metrics = fetch_all(
    """
    SELECT id, action_id, workflow_id, metric_level, name, description, unit, direction,
           created_at, updated_at
    FROM metric
    WHERE action_id = %s
    ORDER BY id
    """,
    (action_id,),
)
if not metrics:
    st.info("No metrics for this action yet.")
    st.stop()

df_show = pd.DataFrame(metrics)
# Prominent hierarchy columns first
_prio = ["id", "metric_level", "workflow_id", "name", "unit", "direction", "description"]
df_show = df_show[[c for c in _prio if c in df_show.columns] + [c for c in df_show.columns if c not in _prio]]
st.dataframe(df_show, use_container_width=True, hide_index=True)

# -- Edit / Delete --------------------------------------------------
st.subheader("Edit / Delete")
met_map = {f"{m['id']} - {m['name']}": m for m in metrics}
sel = st.selectbox("Select metric", list(met_map.keys()), key="met_sel")
metric = met_map[sel]

col_edit, col_del = st.columns(2)

with col_edit:
    with st.form("edit_metric"):
        new_name = st.text_input("Name", value=metric["name"])
        new_desc = st.text_area("Description", value=metric["description"] or "")
        new_unit = st.text_input("Unit", value=metric["unit"] or "")
        new_dir = st.selectbox("Direction", DIRECTIONS, index=DIRECTIONS.index(metric["direction"]))
        if st.form_submit_button("Save Changes"):
            try:
                execute(
                    "UPDATE metric SET name=%s, description=%s, unit=%s, direction=%s WHERE id=%s",
                    (new_name, new_desc, new_unit, new_dir, metric["id"]),
                )
                st.success("Updated.")
                st.rerun()
            except Exception as e:
                st.error(str(e))

with col_del:
    st.warning("Deleting a metric also removes its data-element linkages.")
    if st.button("Delete This Metric", type="primary"):
        execute("DELETE FROM metric WHERE id=%s", (metric["id"],))
        st.success("Deleted.")
        st.rerun()

# -- Roll-up links (metric_rollup) ---------------------------------
st.subheader("Roll-up relationships")
try:
    parents = fetch_all(
        """
        SELECT mr.parent_metric_id, p.name AS parent_name, p.metric_level AS parent_level,
               mr.rollup_rule, mr.sort_order
        FROM metric_rollup mr
        JOIN metric p ON p.id = mr.parent_metric_id
        WHERE mr.child_metric_id = %s
        ORDER BY mr.sort_order, mr.parent_metric_id
        """,
        (metric["id"],),
    )
    children = fetch_all(
        """
        SELECT mr.child_metric_id, c.name AS child_name, c.metric_level AS child_level,
               mr.rollup_rule, mr.sort_order, mr.notes
        FROM metric_rollup mr
        JOIN metric c ON c.id = mr.child_metric_id
        WHERE mr.parent_metric_id = %s
        ORDER BY mr.sort_order, mr.child_metric_id
        """,
        (metric["id"],),
    )
    if parents:
        st.markdown("**Feeds into (this metric rolls up to):**")
        st.dataframe(pd.DataFrame(parents), use_container_width=True, hide_index=True)
    else:
        st.caption("*Not a child of any rolled-up metric in `metric_rollup`.*")

    if children:
        st.markdown("**Composed of (children in the hierarchy):**")
        st.dataframe(pd.DataFrame(children), use_container_width=True, hide_index=True)
    else:
        st.caption("*Not a parent in `metric_rollup` (typical for leaf control metrics).*")
except Exception:
    st.info(
        "Install the metric hierarchy (`db/migration_metric_hierarchy.sql`) to see roll-up links here."
    )
