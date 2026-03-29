import streamlit as st
import pandas as pd
from db import fetch_all, execute

st.set_page_config(page_title="Actions", layout="wide")
st.title("Actions")
st.caption("Control decisions and actions taken at each operation step.")

ACTION_TYPES = ["decision", "approval", "execution", "review", "adjustment"]

workflows = fetch_all("SELECT id, name FROM workflow ORDER BY name")
if not workflows:
    st.info("Create a workflow first.")
    st.stop()

wf_map = {w["name"]: w["id"] for w in workflows}
sel_wf = st.selectbox("Workflow", list(wf_map.keys()))
wf_id = wf_map[sel_wf]

steps = fetch_all(
    "SELECT id, name, step_order FROM operation_step WHERE workflow_id=%s ORDER BY step_order",
    (wf_id,),
)
if not steps:
    st.info("Add operation steps to this workflow first.")
    st.stop()

step_map = {f"Step {s['step_order']}: {s['name']}": s["id"] for s in steps}
sel_step = st.selectbox("Operation Step", list(step_map.keys()))
step_id = step_map[sel_step]

# ── Add new action ─────────────────────────────────────────────────
with st.expander("Add New Action"):
    with st.form("add_action", clear_on_submit=True):
        name = st.text_input("Name")
        desc = st.text_area("Description")
        atype = st.selectbox("Action Type", ACTION_TYPES)
        if st.form_submit_button("Add Action") and name:
            try:
                execute(
                    "INSERT INTO action (operation_step_id, name, description, action_type) VALUES (%s,%s,%s,%s)",
                    (step_id, name, desc, atype),
                )
                st.success(f"Added action: {name}")
                st.rerun()
            except Exception as e:
                st.error(str(e))

# ── List ───────────────────────────────────────────────────────────
actions = fetch_all(
    "SELECT * FROM action WHERE operation_step_id=%s ORDER BY id", (step_id,)
)
if not actions:
    st.info("No actions for this step yet.")
    st.stop()

st.dataframe(pd.DataFrame(actions), use_container_width=True, hide_index=True)

# ── Edit / Delete ──────────────────────────────────────────────────
st.subheader("Edit / Delete")
act_map = {f"{a['id']} — {a['name']}": a for a in actions}
sel = st.selectbox("Select action", list(act_map.keys()), key="act_sel")
action = act_map[sel]

col_edit, col_del = st.columns(2)

with col_edit:
    with st.form("edit_action"):
        new_name = st.text_input("Name", value=action["name"])
        new_desc = st.text_area("Description", value=action["description"] or "")
        new_type = st.selectbox("Action Type", ACTION_TYPES, index=ACTION_TYPES.index(action["action_type"]))
        if st.form_submit_button("Save Changes"):
            try:
                execute(
                    "UPDATE action SET name=%s, description=%s, action_type=%s WHERE id=%s",
                    (new_name, new_desc, new_type, action["id"]),
                )
                st.success("Updated.")
                st.rerun()
            except Exception as e:
                st.error(str(e))

with col_del:
    st.warning("Deleting an action cascades to its metrics.")
    if st.button("Delete This Action", type="primary"):
        execute("DELETE FROM action WHERE id=%s", (action["id"],))
        st.success("Deleted.")
        st.rerun()
