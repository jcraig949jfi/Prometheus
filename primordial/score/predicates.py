"""Predicate hypotheses (backlog F10): a hypothesis is a predicate checked by code against rows.

Schema (posted on the bus BEFORE the run, SWARM_R2 s4.5):

  metric      a row expression (below): what is measured
  cells       the rows it reads: {"source": "qd" | "rows", "path": rows file (source rows),
              "where": {dotted.field: value | [op, value], ...}}
  comparator  one of >= > <= < == !=
  threshold   a number, a verdict word (PASS), or a row expression on the same cells
  seeds       run seeds (recorded, not evaluated here)
  ttl_cpu_s   CPU-second budget (recorded; F13 enforces it)
  prior       probability that the predicate comes out true: a float, or {key: float}
              with one predicate per key
  gate        optional [[path, op, value], ...] that must hold on every selected row
              (oracle bars); a failed gate makes the predicate INDETERMINATE

Row expressions are JSON, never eval'd:

  {"field": "a.b"}                             value in the ONE selected row
  {"sum": [[coef, expr], ...], "const": c}     linear combination
  {"count": [path, op, value], "distinct": k}  selected rows passing the test (distinct by k)
  {"all": [predicate, ...]}                    conjunction; sub-predicates inherit cells
  {"qd_check": true}                           clause A verdict (qd_ledger.check) of the ONE
                                               selected QD row; oracle_clean = status != cheat
  {"rows_equal": {"a": cells, "b": cells, "key": [paths], "ignore": [fields]}}
                                               share of keyed rows identical on both sides

evaluate() -> {"outcome": True | False | None, "lhs", "rhs", "why"}. None is INDETERMINATE:
a row or field is missing, a selection is ambiguous, a gate fails, or clause A is
INELIGIBLE / NO_BASELINE. The outcome never depends on a prose field.
"""
from __future__ import annotations

import json
import operator
import re

REQUIRED = ("metric", "cells", "comparator", "threshold", "seeds", "ttl_cpu_s", "prior")
OPS = {">=": operator.ge, ">": operator.gt, "<=": operator.le, "<": operator.lt,
       "==": operator.eq, "!=": operator.ne}
EXPR_KEYS = ("field", "sum", "count", "all", "qd_check", "rows_equal")
UNDECIDED = ("INELIGIBLE", "NO_BASELINE")
_MISSING = object()


class Indeterminate(Exception):
    """The rows cannot decide the predicate."""


def get(row, path: str):
    cur = row
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return _MISSING
        cur = cur[part]
    return cur


def _cmp(op: str, a, b) -> bool:
    if a is _MISSING:
        return False
    try:
        return bool(OPS[op](a, b))
    except TypeError:
        return False


def _is_expr(x) -> bool:
    if isinstance(x, (bool, int, float)):
        return True
    if isinstance(x, str):
        return bool(re.fullmatch(r"[A-Z_]+", x))          # verdict words only; prose is not checkable
    return isinstance(x, dict) and sum(k in x for k in EXPR_KEYS) == 1


def validate_predicate(p: dict) -> list[str]:
    """-> problems (empty = a checkable predicate)."""
    problems = [f"missing {k}" for k in REQUIRED if k not in p]
    if "comparator" in p and p["comparator"] not in OPS:
        problems.append(f"comparator {p['comparator']!r} not in {sorted(OPS)}")
    c = p.get("cells")
    if "cells" in p and not (isinstance(c, dict) and c.get("source") in ("qd", "rows")):
        problems.append("cells must be {source: qd|rows, path?, where?}")
    elif isinstance(c, dict) and c.get("source") == "rows" and not c.get("path"):
        problems.append("cells with source rows need a path")
    if "prior" in p:
        pr = p["prior"]
        vals = list(pr.values()) if isinstance(pr, dict) else [pr]
        if not vals or not all(isinstance(v, (int, float)) and not isinstance(v, bool) and 0.0 <= v <= 1.0
                               for v in vals):
            problems.append("prior must be a probability or {key: probability}")
    for k in ("metric", "threshold"):
        if k in p and not _is_expr(p[k]):
            problems.append(f"{k} is not a row expression (prose is not checkable)")
    return problems


def _match(row, where) -> bool:
    for path, want in (where or {}).items():
        v = get(row, path)
        if isinstance(want, list):
            if not _cmp(want[0], v, want[1]):
                return False
        elif v is _MISSING or v != want:
            return False
    return True


def select(cells: dict, load) -> list[dict]:
    return [r for r in load(cells["source"], cells.get("path")) if _match(r, cells.get("where"))]


def _one(cells, load, what):
    rows = select(cells, load)
    if len(rows) != 1:
        raise Indeterminate(f"{what}: {len(rows)} rows selected, need 1")
    return rows[0]


def value(expr, cells: dict, load):
    if expr is None or isinstance(expr, (bool, int, float, str)):
        return expr
    op = next(k for k in EXPR_KEYS if k in expr)
    if op == "field":
        v = get(_one(cells, load, f"field {expr['field']}"), expr["field"])
        if v is _MISSING or v is None:
            raise Indeterminate(f"field {expr['field']} absent")
        return v
    if op == "sum":
        return sum(float(c) * float(value(e, cells, load)) for c, e in expr["sum"]) + float(expr.get("const", 0.0))
    if op == "count":
        path, cop, want = expr["count"]
        rows = select(cells, load)
        if not rows:
            raise Indeterminate(f"count {path}: 0 rows selected")
        if any(get(r, path) is _MISSING for r in rows):
            raise Indeterminate(f"count {path}: absent in a selected row")
        hit = [r for r in rows if _cmp(cop, get(r, path), want)]
        if expr.get("distinct"):
            return len({json.dumps(get(r, expr["distinct"]), sort_keys=True, default=str) for r in hit})
        return len(hit)
    if op == "all":
        outs = [evaluate(dict(sub, cells=sub.get("cells", cells)), load)["outcome"] for sub in expr["all"]]
        if False in outs:
            return False
        if None in outs:
            raise Indeterminate("a conjunct is indeterminate")
        return True
    if op == "qd_check":
        from primordial.ops import qd_ledger as Q
        r = _one(cells, load, "qd_check")
        f = r.get("fitness") or {}
        if f.get("held64_median") is None:
            raise Indeterminate("qd_check: row has no held64_median")
        verdict = Q.check(load("qd", None), r["cell"]["world"], r["cell"]["pressure"], f["held64_median"],
                          f.get("iqr") or 0.0, int(r["footprint"]["genome_bytes"]), int(f.get("n_runs") or 0),
                          oracle_clean=r.get("status") != "cheat")["verdict"]
        if verdict in UNDECIDED:
            raise Indeterminate(f"qd_ledger check {verdict}")
        return verdict
    spec = expr["rows_equal"]
    ignore = set(spec.get("ignore", ()))

    def index(side):
        out = {}
        for r in select(side, load):
            k = tuple(json.dumps(get(r, p), sort_keys=True, default=str) for p in spec["key"])
            if k in out:
                raise Indeterminate(f"rows_equal: duplicate key {k}")
            out[k] = {a: b for a, b in r.items() if a not in ignore}
        return out

    a, b = index(spec["a"]), index(spec["b"])
    if not a or not b:
        raise Indeterminate("rows_equal: a side selects 0 rows")
    return sum(1 for k in a.keys() & b.keys() if a[k] == b[k]) / max(len(a), len(b))


def evaluate(p: dict, load) -> dict:
    """load(source, path) -> list of rows; it may raise Indeterminate for an absent file."""
    cells = p["cells"]
    try:
        if p.get("gate"):
            rows = select(cells, load)
            if not rows:
                raise Indeterminate("gate: 0 rows selected")
            for path, op, want in p["gate"]:
                bad = sum(not _cmp(op, get(r, path), want) for r in rows)
                if bad:
                    raise Indeterminate(f"gate {path} {op} {want!r} fails in {bad}/{len(rows)} rows")
        lhs = value(p["metric"], cells, load)
        rhs = value(p["threshold"], cells, load)
        return {"outcome": bool(OPS[p["comparator"]](lhs, rhs)), "lhs": lhs, "rhs": rhs, "why": ""}
    except Indeterminate as e:
        return {"outcome": None, "lhs": None, "rhs": None, "why": str(e)}


def calibration(resolutions: list[dict], by: tuple = ("cohort",)) -> list[dict]:
    """Prior vs reality per group. Only decided predicates (outcome True/False) are scored."""
    groups: dict[tuple, list] = {}
    for r in resolutions:
        groups.setdefault(tuple(r.get(k) for k in by), []).append(r)
    out = []
    for g, rs in sorted(groups.items(), key=lambda kv: [str(x) for x in kv[0]]):
        dec = [r for r in rs if r["outcome"] is not None]
        row = {**dict(zip(by, g)), "n": len(rs), "n_decided": len(dec), "n_indeterminate": len(rs) - len(dec)}
        if dec:
            p = [float(r["prior"]) for r in dec]
            y = [1.0 if r["outcome"] else 0.0 for r in dec]
            row.update(mean_prior=round(sum(p) / len(p), 4), hit_rate=round(sum(y) / len(y), 4),
                       brier=round(sum((a - b) ** 2 for a, b in zip(p, y)) / len(p), 4))
            row["over_confidence"] = round(row["mean_prior"] - row["hit_rate"], 4)
        out.append(row)
    return out
