import streamlit as st
import pandas as pd
from db import fetch_all, execute

st.set_page_config(page_title="Workflows", layout="wide")
st.title("Workflows")
st.caption("Business cycles that define how the enterprise operates (e.g. Procure-to-Pay, Order-to-Cash).")

# ── Add new ────────────────────────────────────────────────────────
with st.expander("Add New Workflow"):
    with st.form("add_wf", clear_on_submit=True):
        name = st.text_input("Name")
        desc = st.text_area("Description")
        if st.form_submit_button("Add Workflow") and name:
            try:
                execute("INSERT INTO workflow (name, description) VALUES (%s, %s)", (name, desc))
                st.success(f"Created workflow: {name}")
                st.rerun()
            except Exception as e:
                st.error(str(e))

# ── List ───────────────────────────────────────────────────────────
workflows = fetch_all("SELECT * FROM workflow ORDER BY name")
if not workflows:
    st.info("No workflows yet.")
    st.stop()

st.dataframe(pd.DataFrame(workflows), use_container_width=True, hide_index=True)

# ── Edit / Delete ──────────────────────────────────────────────────
st.subheader("Edit / Delete")
wf_map = {f"{w['id']} — {w['name']}": w for w in workflows}
sel = st.selectbox("Select workflow", list(wf_map.keys()), key="wf_sel")
wf = wf_map[sel]

col_edit, col_del = st.columns(2)

with col_edit:
    with st.form("edit_wf"):
        new_name = st.text_input("Name", value=wf["name"])
        new_desc = st.text_area("Description", value=wf["description"] or "")
        if st.form_submit_button("Save Changes"):
            try:
                execute(
                    "UPDATE workflow SET name=%s, description=%s WHERE id=%s",
                    (new_name, new_desc, wf["id"]),
                )
                st.success("Updated.")
                st.rerun()
            except Exception as e:
                st.error(str(e))

with col_del:
    st.warning("Deleting a workflow cascades to all its steps, actions, and metrics.")
    if st.button("Delete This Workflow", type="primary"):
        execute("DELETE FROM workflow WHERE id=%s", (wf["id"],))
        st.success("Deleted.")
        st.rerun()
