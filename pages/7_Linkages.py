import streamlit as st
import pandas as pd
from db import fetch_all, execute

st.set_page_config(page_title="Linkages", layout="wide")
st.title("Linkages")
st.caption("Manage the cross-layer relationships that form the lineage chain.")

DE_ROLES = ["numerator", "denominator", "filter", "dimension", "input"]

tab_mde, tab_des = st.tabs(["Metric ↔ Data Element", "Data Element ↔ System"])

# ═══════════════════════════════════════════════════════════════════
# Tab 1 — Metric ↔ Data Element
# ═══════════════════════════════════════════════════════════════════
with tab_mde:
    st.subheader("Metric ↔ Data Element")

    # ── Current links ──────────────────────────────────────────────
    links_mde = fetch_all("""
        SELECT
            mde.metric_id, m.name AS metric,
            mde.data_element_id, de.name AS data_element,
            mde.role
        FROM metric_data_element mde
        JOIN metric m       ON m.id  = mde.metric_id
        JOIN data_element de ON de.id = mde.data_element_id
        ORDER BY m.name, de.name
    """)

    if links_mde:
        st.dataframe(pd.DataFrame(links_mde), use_container_width=True, hide_index=True)
    else:
        st.info("No metric ↔ data element links yet.")

    # ── Add link ───────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("**Add Link**")

    metrics = fetch_all("""
        SELECT m.id, m.name, a.name AS action, os.name AS step, w.name AS workflow
        FROM metric m
        JOIN action a          ON a.id  = m.action_id
        JOIN operation_step os ON os.id = a.operation_step_id
        JOIN workflow w        ON w.id  = os.workflow_id
        ORDER BY w.name, os.step_order, m.name
    """)
    data_elements = fetch_all("SELECT id, name FROM data_element ORDER BY name")

    if metrics and data_elements:
        met_opts = {f"{m['workflow']} / {m['step']} / {m['name']}": m["id"] for m in metrics}
        de_opts = {d["name"]: d["id"] for d in data_elements}

        with st.form("add_mde", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            sel_met = c1.selectbox("Metric", list(met_opts.keys()))
            sel_de = c2.selectbox("Data Element", list(de_opts.keys()))
            sel_role = c3.selectbox("Role", DE_ROLES)
            if st.form_submit_button("Link"):
                try:
                    execute(
                        "INSERT INTO metric_data_element (metric_id, data_element_id, role) VALUES (%s,%s,%s)",
                        (met_opts[sel_met], de_opts[sel_de], sel_role),
                    )
                    st.success("Linked.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
    else:
        st.warning("Need at least one metric and one data element to create a link.")

    # ── Remove link ────────────────────────────────────────────────
    if links_mde:
        st.markdown("---")
        st.markdown("**Remove Link**")
        link_labels = {
            f"{l['metric']}  ←  {l['data_element']} [{l['role']}]": l
            for l in links_mde
        }
        sel_rm = st.selectbox("Select link to remove", list(link_labels.keys()), key="rm_mde")
        if st.button("Remove Link", key="btn_rm_mde"):
            lnk = link_labels[sel_rm]
            execute(
                "DELETE FROM metric_data_element WHERE metric_id=%s AND data_element_id=%s AND role=%s",
                (lnk["metric_id"], lnk["data_element_id"], lnk["role"]),
            )
            st.success("Removed.")
            st.rerun()


# ═══════════════════════════════════════════════════════════════════
# Tab 2 — Data Element ↔ System
# ═══════════════════════════════════════════════════════════════════
with tab_des:
    st.subheader("Data Element ↔ System")

    # ── Current links ──────────────────────────────────────────────
    links_des = fetch_all("""
        SELECT
            des.data_element_id, de.name AS data_element,
            des.system_id, s.name AS system,
            des.source_table, des.source_field
        FROM data_element_system des
        JOIN data_element de ON de.id = des.data_element_id
        JOIN system s        ON s.id  = des.system_id
        ORDER BY de.name, s.name
    """)

    if links_des:
        st.dataframe(pd.DataFrame(links_des), use_container_width=True, hide_index=True)
    else:
        st.info("No data element ↔ system links yet.")

    # ── Add link ───────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("**Add Link**")

    data_elements2 = fetch_all("SELECT id, name FROM data_element ORDER BY name")
    systems = fetch_all("SELECT id, name FROM system ORDER BY name")

    if data_elements2 and systems:
        de_opts2 = {d["name"]: d["id"] for d in data_elements2}
        sys_opts = {s["name"]: s["id"] for s in systems}

        with st.form("add_des", clear_on_submit=True):
            c1, c2, c3, c4 = st.columns(4)
            sel_de2 = c1.selectbox("Data Element", list(de_opts2.keys()))
            sel_sys = c2.selectbox("System", list(sys_opts.keys()))
            src_tbl = c3.text_input("Source Table")
            src_fld = c4.text_input("Source Field")
            if st.form_submit_button("Link"):
                try:
                    execute(
                        "INSERT INTO data_element_system (data_element_id, system_id, source_table, source_field) "
                        "VALUES (%s,%s,%s,%s)",
                        (de_opts2[sel_de2], sys_opts[sel_sys], src_tbl or None, src_fld or None),
                    )
                    st.success("Linked.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
    else:
        st.warning("Need at least one data element and one system to create a link.")

    # ── Remove link ────────────────────────────────────────────────
    if links_des:
        st.markdown("---")
        st.markdown("**Remove Link**")
        link_labels2 = {
            f"{l['data_element']}  →  {l['system']} ({l['source_table']}.{l['source_field']})": l
            for l in links_des
        }
        sel_rm2 = st.selectbox("Select link to remove", list(link_labels2.keys()), key="rm_des")
        if st.button("Remove Link", key="btn_rm_des"):
            lnk = link_labels2[sel_rm2]
            execute(
                "DELETE FROM data_element_system WHERE data_element_id=%s AND system_id=%s",
                (lnk["data_element_id"], lnk["system_id"]),
            )
            st.success("Removed.")
            st.rerun()
