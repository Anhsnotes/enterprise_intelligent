"""Shared workflow ordering and labels for Streamlit (group by category)."""

from __future__ import annotations

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
