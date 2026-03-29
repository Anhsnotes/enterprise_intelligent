import streamlit as st
import pandas as pd
from db import fetch_all, execute

st.set_page_config(page_title="Systems", layout="wide")
st.title("Systems")
st.caption("ERP and source systems where data originates.")

SYSTEM_TYPES = ["ERP", "CRM", "WMS", "MES", "PLM", "HCM", "SCM", "BI", "Other"]

# -- Add new --------------------------------------------------------
with st.expander("Add New System"):
    with st.form("add_sys", clear_on_submit=True):
        name = st.text_input("Name")
        desc = st.text_area("Description")
        stype = st.selectbox("System Type", SYSTEM_TYPES)
        vendor = st.text_input("Vendor", placeholder="e.g. SAP, Oracle, Microsoft")
        if st.form_submit_button("Add System") and name:
            try:
                execute(
                    "INSERT INTO system (name, description, system_type, vendor) VALUES (%s,%s,%s,%s)",
                    (name, desc, stype, vendor),
                )
                st.success(f"Added system: {name}")
                st.rerun()
            except Exception as e:
                st.error(str(e))

# -- List -----------------------------------------------------------
systems = fetch_all("SELECT * FROM system ORDER BY name")
if not systems:
    st.info("No systems yet.")
    st.stop()

st.dataframe(pd.DataFrame(systems), use_container_width=True, hide_index=True)

# -- Edit / Delete --------------------------------------------------
st.subheader("Edit / Delete")
sys_map = {f"{s['id']} - {s['name']}": s for s in systems}
sel = st.selectbox("Select system", list(sys_map.keys()), key="sys_sel")
system = sys_map[sel]

col_edit, col_del = st.columns(2)

with col_edit:
    with st.form("edit_sys"):
        new_name = st.text_input("Name", value=system["name"])
        new_desc = st.text_area("Description", value=system["description"] or "")
        new_type = st.selectbox("System Type", SYSTEM_TYPES, index=SYSTEM_TYPES.index(system["system_type"]))
        new_vendor = st.text_input("Vendor", value=system["vendor"] or "")
        if st.form_submit_button("Save Changes"):
            try:
                execute(
                    "UPDATE system SET name=%s, description=%s, system_type=%s, vendor=%s WHERE id=%s",
                    (new_name, new_desc, new_type, new_vendor, system["id"]),
                )
                st.success("Updated.")
                st.rerun()
            except Exception as e:
                st.error(str(e))

with col_del:
    st.warning("Deleting a system removes its data-element linkages.")
    if st.button("Delete This System", type="primary"):
        execute("DELETE FROM system WHERE id=%s", (system["id"],))
        st.success("Deleted.")
        st.rerun()
