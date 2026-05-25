"""
Icarus complexity tracking -- spec v0.2 #7 (ChatGPT review).

Not just raw LOC -- capability-per-LOC, concept-count, edit-locality, plus
DAG branching factor (Gemini review).

FIXED infrastructure -- Icarus does NOT modify this module.
"""
from __future__ import annotations

import ast
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


ICARUS_DIR = Path(r"D:\Prometheus\agents\icarus")
STATE_DIR = ICARUS_DIR / "state"
COMPLEXITY_HISTORY = STATE_DIR / "complexity_history.jsonl"

# Hard caps (spec v0.1 sect 7.2 + v0.2 unchanged)
HARD_LOC_CAP = 5000  # excludes tests
ALARM_RATIO = 1.5    # 1.5x 30-cycle moving average


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def compute_complexity_metrics(source_dir: Path) -> dict:
    """Walk source_dir; compute LOC, cyclomatic, import-graph, concept-count.
    Returns a dict suitable for both alarms and the wisdom module."""
    if not source_dir.exists():
        return _zero_metrics()

    loc_total = 0
    loc_non_test = 0
    loc_per_file: dict[str, int] = {}
    cyclomatic_total = 0
    cyclomatic_per_function: dict[str, int] = {}
    import_set: set = set()
    concept_count = 0  # named subsystems/classes

    for p in sorted(source_dir.rglob("*.py")):
        if "__pycache__" in str(p):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        lines = text.splitlines()
        # Exclude blank lines and pure comments from LOC
        nonblank = sum(1 for ln in lines if ln.strip() and not ln.strip().startswith("#"))
        loc_total += nonblank
        rel = str(p.relative_to(source_dir))
        loc_per_file[rel] = nonblank
        if "test" not in rel.lower() and "/tests/" not in rel.replace("\\", "/"):
            loc_non_test += nonblank
        # AST analysis
        try:
            tree = ast.parse(text)
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    for n in node.names:
                        import_set.add(n.name)
                elif isinstance(node, ast.ClassDef):
                    concept_count += 1
                elif isinstance(node, ast.FunctionDef):
                    # Approximate cyclomatic complexity: count decision points
                    cc = 1  # base
                    for sub in ast.walk(node):
                        if isinstance(sub, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With)):
                            cc += 1
                        elif isinstance(sub, ast.BoolOp):
                            cc += len(sub.values) - 1
                    cyclomatic_total += cc
                    cyclomatic_per_function[f"{rel}::{node.name}"] = cc
        except Exception:
            pass

    return {
        "loc_total": loc_total,
        "loc_non_test": loc_non_test,
        "loc_per_file": loc_per_file,
        "cyclomatic_total": cyclomatic_total,
        "cyclomatic_per_function": cyclomatic_per_function,
        "import_graph_nodes": len(import_set),
        "import_graph_edges": len(import_set),  # rough; could be improved
        "concept_count": concept_count,
        "edit_locality_score": _compute_edit_locality(source_dir),
        "computed_at": _now_iso(),
    }


def _compute_edit_locality(source_dir: Path) -> float:
    """Compare against the most-recent prior measurement; locality = fraction
    of files that did NOT change. Higher = more local edits = good."""
    # Phase 0 stub: returns 1.0 (perfectly local) until we have a baseline
    # to compare against. Phase 1+ will compare against prior cycle's
    # complexity_history.jsonl entry.
    return 1.0


def _zero_metrics() -> dict:
    return {
        "loc_total": 0, "loc_non_test": 0, "loc_per_file": {},
        "cyclomatic_total": 0, "cyclomatic_per_function": {},
        "import_graph_nodes": 0, "import_graph_edges": 0,
        "concept_count": 0, "edit_locality_score": 1.0,
        "computed_at": _now_iso(),
    }


def append_complexity_history(cycle_n: int, metrics: dict) -> None:
    """Append a snapshot to state/complexity_history.jsonl for moving-avg
    computation."""
    COMPLEXITY_HISTORY.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "cycle_n": cycle_n,
        "ts": _now_iso(),
        "loc_total": metrics.get("loc_total"),
        "loc_non_test": metrics.get("loc_non_test"),
        "cyclomatic_total": metrics.get("cyclomatic_total"),
        "import_graph_nodes": metrics.get("import_graph_nodes"),
        "concept_count": metrics.get("concept_count"),
    }
    try:
        with open(COMPLEXITY_HISTORY, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, default=str) + "\n")
    except Exception as e:
        print(f"[complexity] history append failed: {e}", file=sys.stderr)


def check_complexity_alarm(metrics_now: dict, window: int = 30) -> dict:
    """Compute 30-cycle moving averages from complexity_history.jsonl.
    Alarm if any tracked metric exceeds ALARM_RATIO."""
    if not COMPLEXITY_HISTORY.exists():
        return {"alarmed": False, "metric_violations": [], "moving_averages": {},
                "recommendation": "proceed", "note": "no_history_yet"}

    rows: list[dict] = []
    try:
        with open(COMPLEXITY_HISTORY, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except Exception:
                    continue
    except Exception:
        return {"alarmed": False, "metric_violations": [], "moving_averages": {},
                "recommendation": "proceed", "note": "history_unreadable"}

    if len(rows) < 3:
        return {"alarmed": False, "metric_violations": [], "moving_averages": {},
                "recommendation": "proceed", "note": "history_too_short"}

    recent = rows[-window:]
    averages = {}
    violations = []
    for metric in ("loc_total", "loc_non_test", "cyclomatic_total",
                   "import_graph_nodes", "concept_count"):
        vals = [r.get(metric) for r in recent if r.get(metric) is not None]
        if not vals:
            continue
        avg = sum(vals) / len(vals)
        averages[metric] = avg
        now_val = metrics_now.get(metric)
        if now_val is not None and avg > 0 and now_val > ALARM_RATIO * avg:
            violations.append(f"{metric}: {now_val} > {ALARM_RATIO}x avg {avg:.1f}")

    # Hard LOC cap (spec v0.1 sect 7.2)
    if (metrics_now.get("loc_non_test") or 0) > HARD_LOC_CAP:
        violations.append(f"loc_non_test: {metrics_now.get('loc_non_test')} > hard cap {HARD_LOC_CAP}")

    rec = "rollback" if violations else "proceed"
    return {
        "alarmed": bool(violations),
        "metric_violations": violations,
        "moving_averages": averages,
        "recommendation": rec,
    }


def compute_capability_per_loc(
    tier_pass_rate_before: float,
    tier_pass_rate_after: float,
    loc_delta: int,
) -> float:
    """Capability gain per LOC added. Higher = more efficient."""
    if loc_delta == 0:
        return 0.0
    return (tier_pass_rate_after - tier_pass_rate_before) / loc_delta


def compute_branching_factor(
    cycles_dir: Path,
    stable_cycle_id: str,
) -> int:
    """Count parked cycles whose parent equals stable_cycle_id.
    High value = thrashing (per Gemini's frontier review)."""
    if not cycles_dir.exists():
        return 0
    count = 0
    for cp in cycles_dir.iterdir():
        if not cp.is_dir() or not cp.name.startswith("cycle_"):
            continue
        parent_path = cp / "parent.json"
        outcome_path = cp / "outcome.json"
        if not parent_path.exists() or not outcome_path.exists():
            continue
        try:
            parent = json.loads(parent_path.read_text(encoding="utf-8"))
            outcome = json.loads(outcome_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if (str(parent.get("parent_cycle")) == stable_cycle_id
                and outcome.get("decision") == "park"):
            count += 1
    return count
