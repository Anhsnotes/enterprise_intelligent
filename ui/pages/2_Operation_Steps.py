import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
import pandas as pd
from db import fetch_all, execute
from ui.workflow_ui import sql_order_category, workflow_options_by_category

st.set_page_config(page_title="Operation Steps", layout="wide")
st.title("Operation Steps")
st.caption("Discrete phases within each workflow, ordered sequentially.")

workflows = fetch_all(f"SELECT id, name, category FROM workflow {sql_order_category()}")
if not workflows:
    st.info("Create a workflow first.")
    st.stop()

_wf_labels, _wf_map = workflow_options_by_category(workflows)

# -- Filter by workflow ---------------------------------------------
sel_wf = st.selectbox("Workflow", _wf_labels)
wf_id = _wf_map[sel_wf]["id"]

# -- Add new step ---------------------------------------------------
with st.expander("Add New Step"):
    with st.form("add_step", clear_on_submit=True):
        name = st.text_input("Name")
        desc = st.text_area("Description")
        order = st.number_input("Step Order", min_value=1, step=1)
        if st.form_submit_button("Add Step") and name:
            try:
                execute(
                    "INSERT INTO operation_step (workflow_id, name, description, step_order) VALUES (%s,%s,%s,%s)",
                    (wf_id, name, desc, order),
                )
                st.success(f"Added step: {name}")
                st.rerun()
            except Exception as e:
                st.error(str(e))

# -- List steps -----------------------------------------------------
steps = fetch_all(
    "SELECT * FROM operation_step WHERE workflow_id=%s ORDER BY step_order", (wf_id,)
)
if not steps:
    st.info("No steps for this workflow yet.")
    st.stop()

st.dataframe(pd.DataFrame(steps), use_container_width=True, hide_index=True)

# -- Edit / Delete --------------------------------------------------
st.subheader("Edit / Delete")
step_map = {f"Step {s['step_order']}: {s['name']}": s for s in steps}
sel = st.selectbox("Select step", list(step_map.keys()), key="step_sel")
step = step_map[sel]

col_edit, col_del = st.columns(2)

with col_edit:
    with st.form("edit_step"):
        new_name = st.text_input("Name", value=step["name"])
        new_desc = st.text_area("Description", value=step["description"] or "")
        new_order = st.number_input("Step Order", value=step["step_order"], min_value=1, step=1)
        if st.form_submit_button("Save Changes"):
            try:
                execute(
                    "UPDATE operation_step SET name=%s, description=%s, step_order=%s WHERE id=%s",
                    (new_name, new_desc, new_order, step["id"]),
                )
                st.success("Updated.")
                st.rerun()
            except Exception as e:
                st.error(str(e))

with col_del:
    st.warning("Deleting a step cascades to its actions and metrics.")
    if st.button("Delete This Step", type="primary"):
        execute("DELETE FROM operation_step WHERE id=%s", (step["id"],))
        st.success("Deleted.")
        st.rerun()
