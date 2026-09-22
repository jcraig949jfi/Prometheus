"""Read-only census of a JSONL ledger (LAYER: NECROPOLIS ADAPTER).

ORIGINAL SCIENTIFIC LOGIC: none.  This is a denominator instrument: it counts
rows, keys, value cardinality, dead fields and timestamp ranges so that a
verdict column can be read against the population it was drawn from.  The
dead-field check re-uses attacks.preflight.dead_field (techne-era helper)
when it imports; otherwise it reports its own absent/None count and says so.

NECROPOLIS VALIDATION: engine/necropolis/workshop/tests/run_controls.py::adapters_jsonl_census.*

Reads: one JSONL file.  Writes: nothing (returns a dict).  Malformed lines are
counted, never repaired, never dropped silently.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Optional

_TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def iter_rows(path: Path) -> Iterable[tuple]:
    """Yield (lineno, row_or_None, error_or_None) for every physical line, blanks skipped."""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh, 1):
            s = line.strip()
            if not s:
                continue
            try:
                obj = json.loads(s)
            except json.JSONDecodeError as e:  # noqa: PERF203
                yield i, None, f"{type(e).__name__}: {e}"
                continue
            if not isinstance(obj, dict):
                yield i, None, f"non-object row: {type(obj).__name__}"
                continue
            yield i, obj, None


def census(path, *, verdict_keys=("verdict", "status", "kill_pattern", "result"), max_values: int = 12) -> dict:
    path = Path(path)
    if not path.exists():
        return {"path": str(path), "exists": False, "rows": 0}
    n_ok = 0
    errors = []
    key_count: Counter = Counter()
    none_count: Counter = Counter()
    values: dict = defaultdict(Counter)
    ts_min: dict = {}
    ts_max: dict = {}
    for lineno, row, err in iter_rows(path):
        if err:
            errors.append({"line": lineno, "error": err})
            continue
        n_ok += 1
        for k, v in row.items():
            key_count[k] += 1
            if v is None:
                none_count[k] += 1
            if k in verdict_keys and isinstance(v, (str, int, bool)):
                values[k][str(v)] += 1
            if isinstance(v, str) and _TS_RE.match(v):
                ts_min[k] = min(ts_min.get(k, v), v)
                ts_max[k] = max(ts_max.get(k, v), v)
    dead = {k: {"present": c, "none": none_count[k], "absent": n_ok - c}
            for k, c in key_count.items() if (none_count[k] + (n_ok - c)) == n_ok}
    partial = {k: {"present": c, "absent": n_ok - c} for k, c in key_count.items() if 0 < n_ok - c}
    return {
        "path": str(path), "exists": True, "rows": n_ok, "malformed": len(errors), "malformed_lines": errors[:20],
        "keys": dict(key_count), "none_counts": {k: v for k, v in none_count.items() if v},
        "dead_fields": dead, "partial_fields": partial,
        "verdict_columns": {k: dict(c.most_common(max_values)) for k, c in values.items()},
        "timestamp_ranges": {k: {"min": ts_min[k], "max": ts_max[k]} for k in ts_min},
        "forbidden_inference": "row counts are denominators for THIS file only; a ledger that was rotated, "
                               "gitignored or rewritten is not represented here (see git_history_census).",
    }


def dead_field_via_preflight(path, fields) -> Optional[list]:
    """attacks.preflight.dead_field(rows, fields) if the helper imports; None otherwise.

    Returns the list of check names that FAILED (field absent from every row)."""
    try:
        from attacks.preflight import dead_field  # type: ignore
    except Exception:  # noqa: BLE001
        return None
    rows = [r for _, r, e in iter_rows(Path(path)) if e is None]
    return [f.check for f in dead_field(rows, list(fields)) if not f.ok]
