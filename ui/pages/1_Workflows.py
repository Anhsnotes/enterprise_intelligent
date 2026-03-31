import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
import pandas as pd
from db import fetch_all, execute
from ui.workflow_ui import (
    WORKFLOW_CATEGORIES,
    group_workflows_for_display,
    label_workflow,
    sql_order_category,
    sort_workflows_by_category,
)

st.set_page_config(page_title="Workflows", layout="wide")
st.title("Workflows")
st.caption("Business cycles that define how the enterprise operates (e.g. Procure-to-Pay, Order-to-Cash).")

# -- Add new --------------------------------------------------------
with st.expander("Add New Workflow"):
    with st.form("add_wf", clear_on_submit=True):
        name = st.text_input("Name")
        desc = st.text_area("Description")
        cat = st.selectbox("Category", WORKFLOW_CATEGORIES, index=WORKFLOW_CATEGORIES.index("Other"))
        custom_cat = st.text_input("Custom category (if Other)", placeholder="e.g. Treasury & Risk")
        if st.form_submit_button("Add Workflow") and name:
            category = custom_cat.strip() if cat == "Other" and custom_cat.strip() else cat
            try:
                execute(
                    "INSERT INTO workflow (name, description, category) VALUES (%s, %s, %s)",
                    (name, desc, category or None),
                )
                st.success(f"Created workflow: {name}")
                st.rerun()
            except Exception as e:
                st.error(str(e))

# -- List (grouped by category) -------------------------------------
workflows = fetch_all(f"SELECT * FROM workflow {sql_order_category()}")
if not workflows:
    st.info("No workflows yet.")
    st.stop()

_col_order = ["id", "category", "name", "description", "created_at", "updated_at"]
for title, group in group_workflows_for_display(workflows):
    st.subheader(title)
    _df = pd.DataFrame(group)
    _cols = [c for c in _col_order if c in _df.columns]
    st.dataframe(_df[_cols], use_container_width=True, hide_index=True)

# -- Edit / Delete --------------------------------------------------
st.subheader("Edit / Delete")
wf_map = {f"{w['id']} — {label_workflow(w)}": w for w in sort_workflows_by_category(workflows)}
sel = st.selectbox("Select workflow", list(wf_map.keys()), key="wf_sel")
wf = wf_map[sel]

col_edit, col_del = st.columns(2)

with col_edit:
    with st.form("edit_wf"):
        new_name = st.text_input("Name", value=wf["name"])
        new_desc = st.text_area("Description", value=wf["description"] or "")
        cur_cat = wf.get("category") or ""
        cat_idx = (
            WORKFLOW_CATEGORIES.index(cur_cat)
            if cur_cat in WORKFLOW_CATEGORIES
            else WORKFLOW_CATEGORIES.index("Other")
        )
        new_cat = st.selectbox("Category", WORKFLOW_CATEGORIES, index=cat_idx, key="edit_wf_cat")
        new_custom = st.text_input(
            "Custom category (if Other)",
            value="" if cur_cat in WORKFLOW_CATEGORIES or not cur_cat else cur_cat,
            key="edit_wf_custom_cat",
        )
        if st.form_submit_button("Save Changes"):
            try:
                resolved_cat = (
                    new_custom.strip()
                    if new_cat == "Other" and new_custom.strip()
                    else (None if new_cat == "Other" and not new_custom.strip() else new_cat)
                )
                execute(
                    "UPDATE workflow SET name=%s, description=%s, category=%s WHERE id=%s",
                    (new_name, new_desc, resolved_cat, wf["id"]),
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
