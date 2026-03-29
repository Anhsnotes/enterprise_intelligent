import streamlit as st
import pandas as pd
from db import fetch_all, execute

st.set_page_config(page_title="Data Elements", layout="wide")
st.title("Data Elements")
st.caption("Canonical, standardised data points the business produces.")

DATA_TYPES = [
    "date", "timestamp", "currency", "quantity", "percentage",
    "text", "boolean", "integer", "decimal",
]

# ── Add new ────────────────────────────────────────────────────────
with st.expander("Add New Data Element"):
    with st.form("add_de", clear_on_submit=True):
        name = st.text_input("Name")
        desc = st.text_area("Description")
        dtype = st.selectbox("Data Type", DATA_TYPES)
        if st.form_submit_button("Add Data Element") and name:
            try:
                execute(
                    "INSERT INTO data_element (name, description, data_type) VALUES (%s,%s,%s)",
                    (name, desc, dtype),
                )
                st.success(f"Added data element: {name}")
                st.rerun()
            except Exception as e:
                st.error(str(e))

# ── List ───────────────────────────────────────────────────────────
elements = fetch_all("SELECT * FROM data_element ORDER BY name")
if not elements:
    st.info("No data elements yet.")
    st.stop()

st.dataframe(pd.DataFrame(elements), use_container_width=True, hide_index=True)

# ── Edit / Delete ──────────────────────────────────────────────────
st.subheader("Edit / Delete")
de_map = {f"{d['id']} — {d['name']}": d for d in elements}
sel = st.selectbox("Select data element", list(de_map.keys()), key="de_sel")
de = de_map[sel]

col_edit, col_del = st.columns(2)

with col_edit:
    with st.form("edit_de"):
        new_name = st.text_input("Name", value=de["name"])
        new_desc = st.text_area("Description", value=de["description"] or "")
        new_dtype = st.selectbox("Data Type", DATA_TYPES, index=DATA_TYPES.index(de["data_type"]))
        if st.form_submit_button("Save Changes"):
            try:
                execute(
                    "UPDATE data_element SET name=%s, description=%s, data_type=%s WHERE id=%s",
                    (new_name, new_desc, new_dtype, de["id"]),
                )
                st.success("Updated.")
                st.rerun()
            except Exception as e:
                st.error(str(e))

with col_del:
    st.warning("Deleting a data element removes its metric and system linkages.")
    if st.button("Delete This Data Element", type="primary"):
        execute("DELETE FROM data_element WHERE id=%s", (de["id"],))
        st.success("Deleted.")
        st.rerun()
