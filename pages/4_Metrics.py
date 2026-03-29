import streamlit as st
import pandas as pd
from db import fetch_all, execute

st.set_page_config(page_title="Metrics", layout="wide")
st.title("Metrics")
st.caption("Control metrics that govern each action and signal when corrective action is needed.")

DIRECTIONS = ["higher_is_better", "lower_is_better", "target"]

workflows = fetch_all("SELECT id, name FROM workflow ORDER BY name")
if not workflows:
    st.info("Create a workflow first.")
    st.stop()

wf_map = {w["name"]: w["id"] for w in workflows}
sel_wf = st.selectbox("Workflow", list(wf_map.keys()))
wf_id = wf_map[sel_wf]

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

# ── Add new metric ─────────────────────────────────────────────────
with st.expander("Add New Metric"):
    with st.form("add_metric", clear_on_submit=True):
        name = st.text_input("Name")
        desc = st.text_area("Description")
        unit = st.text_input("Unit", placeholder="e.g. %, days, $, count")
        direction = st.selectbox("Direction", DIRECTIONS)
        if st.form_submit_button("Add Metric") and name:
            try:
                execute(
                    "INSERT INTO metric (action_id, name, description, unit, direction) VALUES (%s,%s,%s,%s,%s)",
                    (action_id, name, desc, unit, direction),
                )
                st.success(f"Added metric: {name}")
                st.rerun()
            except Exception as e:
                st.error(str(e))

# ── List ───────────────────────────────────────────────────────────
metrics = fetch_all("SELECT * FROM metric WHERE action_id=%s ORDER BY id", (action_id,))
if not metrics:
    st.info("No metrics for this action yet.")
    st.stop()

st.dataframe(pd.DataFrame(metrics), use_container_width=True, hide_index=True)

# ── Edit / Delete ──────────────────────────────────────────────────
st.subheader("Edit / Delete")
met_map = {f"{m['id']} — {m['name']}": m for m in metrics}
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
