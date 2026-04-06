"""
Suggestions Ledger — Accumulates improvement proposals from all review stages.
================================================================================
Three sources feed suggestions:
  1. Tensor review (dataset quality — computational, free)
  2. Council review (pipeline improvement — LLM, periodic)
  3. Manual (human or Claude Code observations)

Each suggestion has:
  - source: tensor_review | council_review | manual | branch_exhaustion
  - category: data_enrichment | search_improvement | battery_improvement |
              pipeline_change | new_dataset | schema_change
  - priority: high | medium | low
  - status: pending | approved | rejected | implemented
  - description: what to do
  - evidence: why (metric, kill pattern, or council quote)

Storage: convergence/data/suggestions_ledger.jsonl (append-only)
Active view: convergence/data/pending_suggestions.json

HITL gate: nothing moves from 'pending' to 'approved' without human sign-off.
"""

import json
from datetime import datetime
from pathlib import Path

CONVERGENCE = Path(__file__).resolve().parents[2] / "convergence"
LEDGER = CONVERGENCE / "data" / "suggestions_ledger.jsonl"
PENDING = CONVERGENCE / "data" / "pending_suggestions.json"

VALID_CATEGORIES = {"data_enrichment", "search_improvement", "battery_improvement",
                    "pipeline_change", "new_dataset", "schema_change"}
VALID_PRIORITIES = {"high", "medium", "low"}
VALID_STATUSES = {"pending", "approved", "rejected", "implemented"}


def _ensure():
    LEDGER.parent.mkdir(parents=True, exist_ok=True)


def add(source: str, category: str, description: str,
        evidence: str = "", priority: str = "medium",
        cycle_id: str = "") -> str:
    """Add a suggestion to the ledger. Returns suggestion ID."""
    _ensure()
    sid = f"S-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{hash(description) % 1000:03d}"
    entry = {
        "id": sid,
        "source": source,
        "category": category,
        "priority": priority,
        "status": "pending",
        "description": description,
        "evidence": evidence,
        "cycle_id": cycle_id,
        "created_at": datetime.now().isoformat(),
        "reviewed_at": None,
        "reviewed_by": None,
    }
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    _refresh_pending()
    return sid


def add_from_tensor_review(review_results: dict, cycle_id: str = ""):
    """Ingest suggestions from a tensor review result dict."""
    for dataset, result in review_results.items():
        for sug in result.get("suggestions", []):
            # Deduplicate: skip if an identical pending suggestion exists
            if _is_duplicate(sug):
                continue
            cat = _classify_suggestion(sug)
            add(source="tensor_review", category=cat, description=sug,
                evidence=f"Dataset: {dataset}, objects: {result.get('n_objects', '?')}",
                priority=_priority_from_suggestion(sug),
                cycle_id=cycle_id)


def add_from_council_review(review_text: str, provider: str, cycle_id: str = ""):
    """Extract actionable suggestions from a council review response.

    Looks for numbered recommendations or lines starting with '- **'.
    """
    lines = review_text.split("\n")
    for line in lines:
        line = line.strip()
        # Match patterns like "1. **Add..." or "- **Fix..."
        if (line.startswith(("1.", "2.", "3.", "4.", "5.")) or
            line.startswith("- **")) and len(line) > 20:
            # Clean markdown
            desc = line.lstrip("0123456789.-* ")
            if len(desc) > 30:
                if _is_duplicate(desc[:60]):
                    continue
                cat = _classify_suggestion(desc)
                add(source=f"council_review:{provider}", category=cat,
                    description=desc[:300],
                    priority="medium", cycle_id=cycle_id)


def review_suggestion(sid: str, status: str, reviewed_by: str = "HITL"):
    """Approve, reject, or mark a suggestion as implemented. HITL gate."""
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}")
    entries = _load_all()
    updated = False
    for e in entries:
        if e["id"] == sid:
            e["status"] = status
            e["reviewed_at"] = datetime.now().isoformat()
            e["reviewed_by"] = reviewed_by
            updated = True
            break
    if updated:
        _save_all(entries)
        _refresh_pending()
    return updated


def list_pending() -> list[dict]:
    """Return all pending suggestions."""
    if PENDING.exists():
        return json.loads(PENDING.read_text(encoding="utf-8"))
    return [e for e in _load_all() if e["status"] == "pending"]


def summary() -> dict:
    """Summary counts by status and category."""
    entries = _load_all()
    by_status = {}
    by_category = {}
    for e in entries:
        by_status[e["status"]] = by_status.get(e["status"], 0) + 1
        by_category[e["category"]] = by_category.get(e["category"], 0) + 1
    return {"total": len(entries), "by_status": by_status, "by_category": by_category}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_all() -> list[dict]:
    if not LEDGER.exists():
        return []
    entries = []
    with open(LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries


def _save_all(entries: list[dict]):
    _ensure()
    with open(LEDGER, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, default=str) + "\n")


def _refresh_pending():
    pending = [e for e in _load_all() if e["status"] == "pending"]
    _ensure()
    PENDING.write_text(json.dumps(pending, indent=2, default=str), encoding="utf-8")


def _is_duplicate(description: str) -> bool:
    """Check if a similar suggestion already exists in pending."""
    pending = list_pending()
    desc_lower = description.lower()[:60]
    for p in pending:
        if desc_lower in p.get("description", "").lower()[:60]:
            return True
    return False


def _classify_suggestion(text: str) -> str:
    """Heuristic category from suggestion text."""
    t = text.lower()
    if any(w in t for w in ["ingest", "download", "expand", "api", "add data", "150k"]):
        return "data_enrichment"
    if any(w in t for w in ["search", "query", "keyword", "index"]):
        return "search_improvement"
    if any(w in t for w in ["battery", "test", "validation", "false positive"]):
        return "battery_improvement"
    if any(w in t for w in ["schema", "table", "column", "field"]):
        return "schema_change"
    if any(w in t for w in ["new dataset", "new source", "corpus"]):
        return "new_dataset"
    return "pipeline_change"


def _priority_from_suggestion(text: str) -> str:
    """Heuristic priority from suggestion text."""
    t = text.lower()
    if any(w in t for w in ["corrupted", "disabled", "0%", "missing", "blocked"]):
        return "high"
    if any(w in t for w in ["only", "incomplete", "limited"]):
        return "medium"
    return "low"


if __name__ == "__main__":
    print("=== Suggestions Ledger ===")
    s = summary()
    print(f"Total: {s['total']}")
    print(f"By status: {s['by_status']}")
    print(f"By category: {s['by_category']}")
    print()
    pending = list_pending()
    if pending:
        print(f"Pending ({len(pending)}):")
        for p in pending:
            print(f"  [{p['priority']:6s}] [{p['category']:20s}] {p['description'][:80]}")
    else:
        print("No pending suggestions.")
