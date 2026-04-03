import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
import pandas as pd
from db import fetch_all, execute
from ui.workflow_ui import label_workflow

st.set_page_config(page_title="Linkages", layout="wide")
st.title("Linkages")
st.caption("Manage the cross-layer relationships that form the lineage chain.")

DE_ROLES = ["numerator", "denominator", "filter", "dimension", "input"]
ROLLUP_RULES = [
    "weighted_average",
    "sum",
    "min",
    "max",
    "structural",
    "ratio",
]


def _metric_rollup_installed() -> bool:
    try:
        r = fetch_all(
            """
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'metric_rollup'
            """
        )
        return bool(r)
    except Exception:
        return False


tab_mde, tab_des, tab_roll = st.tabs(
    ["Metric <-> Data Element", "Data Element <-> System", "Metric roll-up"]
)

# ===================================================================
# Tab 1 - Metric <-> Data Element
# ===================================================================
with tab_mde:
    st.subheader("Metric <-> Data Element")

    # -- Current links ----------------------------------------------
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
        st.info("No metric <-> data element links yet.")

    # -- Add link ---------------------------------------------------
    st.markdown("---")
    st.markdown("**Add Link**")

    metrics = fetch_all("""
        SELECT m.id, m.name, a.name AS action, os.name AS step,
               w.name AS workflow, w.category AS workflow_cat
        FROM metric m
        JOIN action a          ON a.id  = m.action_id
        JOIN operation_step os ON os.id = a.operation_step_id
        JOIN workflow w        ON w.id  = os.workflow_id
        ORDER BY w.category NULLS LAST, w.name, os.step_order, m.name
    """)
    data_elements = fetch_all("SELECT id, name FROM data_element ORDER BY name")

    if metrics and data_elements:
        def _met_label(row: dict) -> str:
            wf_part = label_workflow(
                {"name": row["workflow"], "category": row.get("workflow_cat")}
            )
            return f"{wf_part} / {row['step']} / {row['name']}"

        met_opts = {_met_label(m): m["id"] for m in metrics}
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

    # -- Remove link ------------------------------------------------
    if links_mde:
        st.markdown("---")
        st.markdown("**Remove Link**")
        link_labels = {
            f"{l['metric']} <- {l['data_element']} [{l['role']}]": l
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


# ===================================================================
# Tab 2 - Data Element <-> System
# ===================================================================
with tab_des:
    st.subheader("Data Element <-> System")

    # -- Current links ----------------------------------------------
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
        st.info("No data element <-> system links yet.")

    # -- Add link ---------------------------------------------------
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

    # -- Remove link ------------------------------------------------
    if links_des:
        st.markdown("---")
        st.markdown("**Remove Link**")
        link_labels2 = {
            f"{l['data_element']} -> {l['system']} ({l['source_table']}.{l['source_field']})": l
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


# ===================================================================
# Tab 3 - Metric roll-up (parent composes child)
# ===================================================================
with tab_roll:
    st.subheader("Metric roll-up (parent → child)")
    st.caption(
        "Each row is an edge in `metric_rollup`: the **parent** metric aggregates **child** metrics "
        "using **rollup_rule**. To change parent/child, remove the edge and add a new one."
    )

    if not _metric_rollup_installed():
        st.warning(
            "Table `metric_rollup` is not installed. Run `db/migration_metric_hierarchy.sql`, then refresh."
        )
    else:
        all_metrics = fetch_all(
            """
            SELECT id, name, metric_level, workflow_id
            FROM metric
            ORDER BY metric_level, id
            """
        )
        links_ru = fetch_all(
            """
            SELECT
                mr.parent_metric_id,
                p.name AS parent_name,
                p.metric_level AS parent_level,
                mr.child_metric_id,
                c.name AS child_name,
                c.metric_level AS child_level,
                mr.rollup_rule,
                mr.sort_order,
                mr.notes
            FROM metric_rollup mr
            JOIN metric p ON p.id = mr.parent_metric_id
            JOIN metric c ON c.id = mr.child_metric_id
            ORDER BY mr.parent_metric_id, mr.sort_order, mr.child_metric_id
            """
        )

        if links_ru:
            st.dataframe(pd.DataFrame(links_ru), use_container_width=True, hide_index=True)
        else:
            st.info("No roll-up rows yet.")

        st.markdown("---")
        st.markdown("**Add roll-up edge**")

        if not all_metrics:
            st.warning("Add metrics first (control metrics via **Metrics**, rolled-up metrics via SQL/seed).")
        else:

            def _m_label(m: dict) -> str:
                lvl = m.get("metric_level") or "control"
                wf = m.get("workflow_id")
                extra = f", wf_id={wf}" if wf else ""
                return f"{m['id']} — {m['name']} ({lvl}{extra})"

            id_by_label = {_m_label(m): m["id"] for m in all_metrics}
            labels = list(id_by_label.keys())

            with st.form("add_roll", clear_on_submit=True):
                c1, c2 = st.columns(2)
                parent_lab = c1.selectbox(
                    "Parent metric (composite / higher level)",
                    labels,
                    key="ru_parent",
                )
                child_lab = c2.selectbox(
                    "Child metric (contributing / lower level)",
                    labels,
                    key="ru_child",
                )
                c3, c4, c5 = st.columns(3)
                rule = c3.selectbox("Roll-up rule", ROLLUP_RULES)
                sort_order = c4.number_input("Sort order", min_value=0, value=0, step=1)
                notes = c5.text_input("Notes (optional)", "")
                if st.form_submit_button("Add edge"):
                    pid, cid = id_by_label[parent_lab], id_by_label[child_lab]
                    if pid == cid:
                        st.error("Parent and child must be different metrics.")
                    else:
                        try:
                            execute(
                                """
                                INSERT INTO metric_rollup
                                    (parent_metric_id, child_metric_id, rollup_rule, sort_order, notes)
                                VALUES (%s, %s, %s, %s, %s)
                                """,
                                (
                                    pid,
                                    cid,
                                    rule,
                                    int(sort_order),
                                    notes or None,
                                ),
                            )
                            st.success("Roll-up edge added.")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

        st.markdown("---")
        st.markdown("**Remove roll-up edge**")
        if links_ru:
            rm_labels = {
                f"{r['parent_name']} (id {r['parent_metric_id']}) → "
                f"{r['child_name']} (id {r['child_metric_id']}) [{r['rollup_rule']}]": r
                for r in links_ru
            }
            sel_ru = st.selectbox("Select edge to remove", list(rm_labels.keys()), key="rm_ru")
            if st.button("Remove edge", key="btn_rm_ru"):
                r = rm_labels[sel_ru]
                execute(
                    """
                    DELETE FROM metric_rollup
                    WHERE parent_metric_id = %s AND child_metric_id = %s
                    """,
                    (r["parent_metric_id"], r["child_metric_id"]),
                )
                st.success("Removed.")
                st.rerun()
        elif all_metrics:
            st.caption("No edges to remove.")
