"""Shared workflow ordering and labels for Streamlit (group by category)."""

from __future__ import annotations

import base64
import re

import streamlit.components.v1 as components

WORKFLOW_CATEGORIES = [
    "Finance & Control",
    "Sales & Revenue",
    "Procurement & Supply Chain",
    "Operations & Manufacturing",
    "Human Capital",
    "Other",
]


def sql_order_category() -> str:
    """Safe to append after `FROM workflow` (includes leading space)."""
    return " ORDER BY category NULLS LAST, name"


def label_workflow(w: dict) -> str:
    """Dropdown label: category first when present."""
    cat = w.get("category")
    if cat:
        return f"{cat} — {w['name']}"
    return w["name"]


def sort_workflows_by_category(workflows: list[dict]) -> list[dict]:
    def cat_key(w: dict) -> tuple:
        cat = w.get("category")
        if not cat:
            return (99, "", w["name"])
        if cat in WORKFLOW_CATEGORIES:
            return (WORKFLOW_CATEGORIES.index(cat), cat, w["name"])
        return (50, cat, w["name"])

    return sorted(workflows, key=cat_key)


def workflow_options_by_category(workflows: list[dict]) -> tuple[list[str], dict[str, dict]]:
    """Labels sorted by category, then name; map label -> full workflow row."""
    ordered = sort_workflows_by_category(workflows)
    labels: list[str] = []
    label_to_w: dict[str, dict] = {}
    for w in ordered:
        lab = label_workflow(w)
        labels.append(lab)
        label_to_w[lab] = w
    return labels, label_to_w


def group_workflows_for_display(workflows: list[dict]) -> list[tuple[str, list[dict]]]:
    """
    Returns (section_title, workflows in that section).
    Order: WORKFLOW_CATEGORIES, then other category names A–Z, then uncategorised.
    """
    by_cat: dict[str | None, list[dict]] = {}
    for w in workflows:
        by_cat.setdefault(w.get("category"), []).append(w)
    for key in by_cat:
        by_cat[key].sort(key=lambda x: x["name"])

    sections: list[tuple[str, list[dict]]] = []
    for cat in WORKFLOW_CATEGORIES:
        if cat in by_cat:
            sections.append((cat, by_cat.pop(cat)))
    extras = sorted(
        [k for k in by_cat.keys() if k is not None],
        key=lambda x: str(x).lower(),
    )
    for cat in extras:
        sections.append((cat, by_cat.pop(cat)))
    if None in by_cat:
        sections.append(("Uncategorised", by_cat.pop(None)))
    return sections


# --- Mermaid.js (shared with Home lineage + Metric hierarchy) --------------------------------

def mermaid_escape_label(text, max_len: int = 72) -> str:
    if text is None:
        return ""
    s = str(text).replace("\n", " ").replace("\r", " ")
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) > max_len:
        s = s[: max_len - 1] + "..."
    s = s.replace('"', "'").replace("[", "(").replace("]", ")")
    return s


def render_mermaid_html(diagram_source: str, height: int = 920) -> None:
    """Render Mermaid via CDN inside a Streamlit HTML component (base64 payload avoids escaping issues)."""
    b64 = base64.standard_b64encode(diagram_source.encode("utf-8")).decode("ascii")
    html_page = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      display: flex;
      flex-direction: column;
      height: 100vh;
      background: transparent;
      font-family: system-ui, sans-serif;
      font-size: 13px;
    }}
    #toolbar {{
      flex: 0 0 auto;
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 6px 8px;
      border-bottom: 1px solid rgba(255,255,255,0.12);
      background: rgba(0,0,0,0.25);
    }}
    #toolbar button {{
      padding: 4px 10px;
      border-radius: 6px;
      border: 1px solid rgba(255,255,255,0.2);
      background: rgba(255,255,255,0.08);
      color: #e0e0e0;
      cursor: pointer;
    }}
    #toolbar button:hover {{ background: rgba(255,255,255,0.15); }}
    #zoomPct {{ min-width: 44px; color: #aaa; }}
    #viewport {{
      flex: 1 1 auto;
      min-height: 0;
      overflow: auto;
      padding: 8px;
    }}
    #zoom-inner {{
      transform-origin: top left;
      display: inline-block;
    }}
  </style>
</head>
<body>
  <div id="toolbar">
    <span style="color:#888;margin-right:4px">Zoom</span>
    <button type="button" id="zoomOut" title="Zoom out">-</button>
    <button type="button" id="zoomReset" title="Reset to default (400%)">Reset</button>
    <button type="button" id="zoomIn" title="Zoom in">+</button>
    <span id="zoomPct">400%</span>
    <span style="color:#666;font-size:11px;margin-left:8px">or hold Ctrl/Cmd and scroll wheel</span>
  </div>
  <div id="viewport">
    <div id="zoom-inner">
      <div id="mmd-out" class="mermaid"></div>
    </div>
  </div>
  <script>
    (async function () {{
      const diagram = atob("{b64}");
      const el = document.getElementById("mmd-out");
      const zoomInner = document.getElementById("zoom-inner");
      const viewport = document.getElementById("viewport");
      const zoomPct = document.getElementById("zoomPct");
      const DEFAULT_ZOOM = 4;
      let scale = DEFAULT_ZOOM;
      const MIN = 0.25, MAX = 10;

      function applyScale() {{
        scale = Math.min(MAX, Math.max(MIN, scale));
        zoomInner.style.transform = "scale(" + scale + ")";
        zoomPct.textContent = Math.round(scale * 100) + "%";
      }}

      el.textContent = diagram;
      mermaid.initialize({{
        startOnLoad: false,
        theme: "dark",
        securityLevel: "loose",
        flowchart: {{ useMaxWidth: true, htmlLabels: true, curve: "basis" }}
      }});
      await mermaid.run({{ querySelector: "#mmd-out" }});
      applyScale();

      document.getElementById("zoomIn").onclick = function () {{
        scale *= 1.15;
        applyScale();
      }};
      document.getElementById("zoomOut").onclick = function () {{
        scale /= 1.15;
        applyScale();
      }};
      document.getElementById("zoomReset").onclick = function () {{
        scale = DEFAULT_ZOOM;
        applyScale();
        viewport.scrollTop = 0;
        viewport.scrollLeft = 0;
      }};

      viewport.addEventListener("wheel", function (e) {{
        if (e.ctrlKey || e.metaKey) {{
          e.preventDefault();
          const delta = e.deltaY > 0 ? -0.08 : 0.08;
          scale += delta;
          applyScale();
        }}
      }}, {{ passive: false }});
    }})();
  </script>
</body>
</html>"""
    components.html(html_page, height=height, scrolling=True)


def build_metric_hierarchy_mermaid(
    m_by_id: dict,
    rollup: list[dict],
    direction: str = "TB",
) -> str:
    """
    Roll-up DAG: parent metric --> child metric (same orientation as the tree tab:
    executive at the anchor, drilling down into contributing metrics).
    """
    direction = (direction or "TB").upper()
    if direction not in ("TB", "LR"):
        direction = "TB"
    lines = [
        f"flowchart {direction}",
        "  %% Metric hierarchy roll-up (auto-generated)",
    ]
    class_lines = [
        "  classDef mh fill:#1565c0,stroke:#0d47a1,stroke-width:2px,color:#fff",
        "  classDef ex fill:#4527a0,stroke:#311b92,color:#fff",
        "  classDef cw fill:#6a1b9a,stroke:#4a148c,color:#fff",
        "  classDef wm fill:#1976d2,stroke:#0d47a1,color:#fff",
        "  classDef cm fill:#c62828,stroke:#b71c1c,color:#fff",
    ]
    if not rollup:
        lines.extend(class_lines)
        return "\n".join(lines)

    child_ids = {r["child_metric_id"] for r in rollup}
    parent_ids = {r["parent_metric_id"] for r in rollup}
    all_ids = sorted(parent_ids | child_ids)

    level_class = {
        "executive": "ex",
        "cross_workflow": "cw",
        "workflow": "wm",
        "control": "cm",
    }

    for mid in all_ids:
        m = m_by_id.get(mid)
        if not m:
            continue
        unit = m.get("unit") or "—"
        d = (m.get("direction") or "").replace("_", " ")
        lbl = mermaid_escape_label(f"{m['name']} [{unit}, {d}]")
        cls = level_class.get(m.get("metric_level"), "cm")
        lines.append(f'  HM{mid}["{lbl}"]:::{cls}')

    lines.append('  MH["Metric hierarchy (roll-up)"]:::mh')
    roots = sorted(parent_ids - child_ids)
    for rid in roots:
        lines.append(f"  MH --> HM{rid}")

    for r in sorted(
        rollup,
        key=lambda x: (x["parent_metric_id"], x["sort_order"], x["child_metric_id"]),
    ):
        pid, cid = r["parent_metric_id"], r["child_metric_id"]
        rule = mermaid_escape_label((r.get("rollup_rule") or "").replace("_", " "), 28)
        lines.append(f'  HM{pid} -->|"{rule}"| HM{cid}')

    lines.extend(class_lines)
    return "\n".join(lines)


def hierarchy_flowchart_legend_html() -> str:
    """Legend aligned with Mermaid classDef (mh, ex, cw, wm, cm)."""
    items = (
        ("#1565c0", "#0d47a1", "Anchor"),
        ("#4527a0", "#311b92", "L4 Executive"),
        ("#6a1b9a", "#4a148c", "L3 Cross-workflow"),
        ("#1976d2", "#0d47a1", "L2 Workflow"),
        ("#c62828", "#b71c1c", "L1 Control"),
    )
    chips = []
    for fill, stroke, label in items:
        chips.append(
            f'<span style="display:inline-flex;align-items:center;gap:6px;font-size:0.9em">'
            f'<span style="display:inline-block;width:14px;height:14px;border-radius:3px;'
            f"background:{fill};border:2px solid {stroke};flex-shrink:0\"></span>"
            f"{label}</span>"
        )
    inner = " ".join(chips)
    return (
        '<div style="display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;'
        "margin:0 0 12px 0;padding:10px 14px;border:1px solid rgba(127,127,127,0.28);"
        'border-radius:8px;background:rgba(128,128,128,0.06);">'
        '<strong style="margin-right:4px;font-size:0.95em">Legend</strong>'
        f"{inner}</div>"
    )
