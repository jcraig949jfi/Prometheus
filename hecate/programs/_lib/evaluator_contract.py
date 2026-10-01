"""Evaluator contract for Pass 3 v3 worlds (DRAFT -- not issued, not frozen).

A v3 world evaluator declares a spec and hands its rows to `evaluate()`, which
returns the OUTCOME dict in the row format the round-1..3 evaluators write
(`outcome`, `positive_control_detected`, `cheat_detected`,
`null_twin_meets_success`, `anomalies`, `notes`) plus per-clause values.

Each rule below answers a defect found in Wave 2:

- One shared row schema for every arm; every clause reads only schema
  fields, so the cheat, twin and SIMPLE_ALT are scored on the same fields
  as treatment (INV_F F6, F8).
- Preconditions: every required arm present with exactly the declared seeds,
  one row per seed, every schema field present and finite. Otherwise
  INSTRUMENT_FAIL with a reason. Nothing is ever `all()`-ed over an empty
  list, and a missing field is never a KeyError (INV_F F1, F4).
- Seed independence: two seeds of one arm with identical payloads mean
  pseudo-replication -> INSTRUMENT_FAIL (INV_F F5, M6).
- Exact comparisons: values are converted to Fraction (floats exactly); a
  clause states its tolerance explicitly ("0" for exact).
- One rule, `meets_success(arm)`, judges TREATMENT, NULL_TWIN, SIMPLE_ALT,
  POSITIVE_CONTROL and CHEAT alike (INV_F F3 ASYM; AUDIT_B X1).
- The positive control is run through every success clause, not only one
  (pass3_v3 L2).
- SIGNAL requires SIMPLE_ALT to fail at least one success clause (L1).

Class order: INSTRUMENT_FAIL / SPEC_UNATTAINABLE > CONFOUNDED > SIGNAL > NULL.

Stdlib only. Never raises from `evaluate()`: an internal error is returned
as INSTRUMENT_FAIL with the exception named in `outcome_reason`.

Spec shape (all keys required unless marked optional):

    {
      "stage": "evaluation" | "pilot",       # pilot: PC miss -> SPEC_UNATTAINABLE
      "seeds": [0, 1, 2, 3, 4],
      "seed_key": "seed",                      # optional, default "seed"
      "schema": {"score": "number", ...},      # payload fields every arm carries
      "required_arms": ["TREATMENT", "NULL_TWIN", "POSITIVE_CONTROL",
                        "CHEAT", "SIMPLE_ALT"],  # these five are mandatory
      "optional_arms": ["CONTROL"],            # optional; checked if present
      "success_clauses": [
        {"id": "S1", "field": "score", "agg": "mean",
         "comparison": ">=", "threshold": "3/4", "tolerance": "0"}
      ]
    }

Tolerance semantics (tol >= 0): ">=" holds iff v >= thr - tol; "<=" iff
v <= thr + tol; ">" iff v > thr + tol; "<" iff v < thr - tol. A tolerance
widens a non-strict comparison and narrows a strict one.
"""
from __future__ import annotations

import json
import math
from fractions import Fraction

TREATMENT, NULL_TWIN, CONTROL = "TREATMENT", "NULL_TWIN", "CONTROL"
POSITIVE_CONTROL, CHEAT, SIMPLE_ALT = "POSITIVE_CONTROL", "CHEAT", "SIMPLE_ALT"
MANDATORY_ARMS = (TREATMENT, NULL_TWIN, POSITIVE_CONTROL, CHEAT, SIMPLE_ALT)
META_ARMS = frozenset({"_META", "META", "RUNINFO", "CPU", "CALIBRATION"})
# Row fields that label a row rather than measure it; excluded from payloads.
LABEL_FIELDS = frozenset({"arm", "seed", "seed_index", "source", "triplicateId", "world", "role"})

SIGNAL, NULL, CONFOUNDED = "SIGNAL", "NULL", "CONFOUNDED"
INSTRUMENT_FAIL, SPEC_UNATTAINABLE = "INSTRUMENT_FAIL", "SPEC_UNATTAINABLE"
OUTCOMES = (SIGNAL, NULL, CONFOUNDED, INSTRUMENT_FAIL, SPEC_UNATTAINABLE)

AGGS = ("mean", "min", "max", "median")
COMPARISONS = (">=", ">", "<=", "<")


class ContractError(Exception):
    """A spec or row violates the contract. Caught inside evaluate()."""


# --------------------------------------------------------------------------- numbers
def to_fraction(x, what="value"):
    """Exact conversion. Accepts int, Fraction, finite float (exact binary
    value), bool (0/1) and rational strings such as "3/4" or "0.1" (decimal,
    exact). Rejects NaN, inf, None, containers."""
    if isinstance(x, Fraction):
        return x
    if isinstance(x, bool):
        return Fraction(int(x))
    if isinstance(x, int):
        return Fraction(x)
    if isinstance(x, float):
        if not math.isfinite(x):
            raise ContractError(f"{what} is not finite: {x!r}")
        return Fraction(x)
    if isinstance(x, str):
        try:
            return Fraction(x.strip())
        except (ValueError, ZeroDivisionError):
            raise ContractError(f"{what} is not a rational string: {x!r}") from None
    raise ContractError(f"{what} has non-numeric type {type(x).__name__}: {x!r}")


def aggregate(values, agg):
    if not values:   # never aggregate (or all()) over an empty list
        raise ContractError(f"aggregate {agg} over zero values")
    if agg == "mean":
        return sum(values, Fraction(0)) / len(values)
    if agg == "min":
        return min(values)
    if agg == "max":
        return max(values)
    if agg == "median":
        v = sorted(values)
        n = len(v)
        return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2
    raise ContractError(f"unknown aggregate {agg!r}")


def compare(value, comparison, threshold, tolerance):
    if tolerance < 0:
        raise ContractError("tolerance must be >= 0")
    if comparison == ">=":
        return value >= threshold - tolerance
    if comparison == "<=":
        return value <= threshold + tolerance
    if comparison == ">":
        return value > threshold + tolerance
    if comparison == "<":
        return value < threshold - tolerance
    raise ContractError(f"unknown comparison {comparison!r}")


def _fmt(fr):
    return {"exact": f"{fr.numerator}/{fr.denominator}", "float": float(fr)}


# --------------------------------------------------------------------------- spec
def validate_spec(spec):
    """Return a normalised spec; raise ContractError on any defect."""
    if not isinstance(spec, dict):
        raise ContractError("spec is not a dict")
    stage = spec.get("stage")
    if stage not in ("evaluation", "pilot"):
        raise ContractError(f"spec.stage must be 'evaluation' or 'pilot', got {stage!r}")
    seeds = spec.get("seeds")
    if not isinstance(seeds, list) or not seeds:
        raise ContractError("spec.seeds must be a non-empty list")
    if len(set(map(repr, seeds))) != len(seeds):
        raise ContractError("spec.seeds has duplicates")
    schema = spec.get("schema")
    if not isinstance(schema, dict) or not schema:
        raise ContractError("spec.schema must be a non-empty {field: 'number'} dict")
    for f, t in schema.items():
        if t != "number":
            raise ContractError(f"schema field {f!r}: only 'number' is supported, got {t!r}")
        if f in LABEL_FIELDS:
            raise ContractError(f"schema field {f!r} is a label field")
    required = spec.get("required_arms")
    if not isinstance(required, list):
        raise ContractError("spec.required_arms must be a list")
    missing = [a for a in MANDATORY_ARMS if a not in required]
    if missing:
        raise ContractError(f"spec.required_arms lacks mandatory arms {missing}")
    optional = spec.get("optional_arms", [])
    if not isinstance(optional, list) or set(optional) & set(required):
        raise ContractError("spec.optional_arms must be a list disjoint from required_arms")
    clauses = spec.get("success_clauses")
    if not isinstance(clauses, list) or not clauses:
        raise ContractError("spec.success_clauses must be a non-empty list")
    norm, ids = [], set()
    for c in clauses:
        for k in ("id", "field", "agg", "comparison", "threshold", "tolerance"):
            if k not in c:
                raise ContractError(f"clause {c.get('id', '?')!r} lacks {k!r} (tolerance must be stated, '0' = exact)")
        if c["id"] in ids:
            raise ContractError(f"duplicate clause id {c['id']!r}")
        ids.add(c["id"])
        if c["field"] not in schema:
            raise ContractError(f"clause {c['id']} reads {c['field']!r}, which is not in the shared schema")
        if c["agg"] not in AGGS:
            raise ContractError(f"clause {c['id']}: agg must be one of {AGGS}")
        if c["comparison"] not in COMPARISONS:
            raise ContractError(f"clause {c['id']}: comparison must be one of {COMPARISONS}")
        tol = to_fraction(c["tolerance"], f"clause {c['id']} tolerance")
        if tol < 0:
            raise ContractError(f"clause {c['id']}: tolerance must be >= 0")
        norm.append(dict(c, threshold=to_fraction(c["threshold"], f"clause {c['id']} threshold"),
                         tolerance=tol))
    return {"stage": stage, "seeds": list(seeds), "seed_key": spec.get("seed_key", "seed"),
            "schema": dict(schema), "required_arms": list(required),
            "optional_arms": list(optional), "success_clauses": norm}


# --------------------------------------------------------------------------- rows
def load_rows(path):
    """Read a JSONL rows file. Returns (rows, error_or_None); never raises."""
    try:
        with open(path, encoding="utf-8") as fh:
            rows = []
            for i, line in enumerate(fh, 1):
                if line.strip():
                    r = json.loads(line)
                    if not isinstance(r, dict):
                        return None, f"line {i} is not a JSON object"
                    rows.append(r)
        return rows, None
    except (OSError, ValueError) as e:
        return None, f"cannot read rows: {type(e).__name__}: {e}"


def payload(row, schema_only=None):
    keys = schema_only if schema_only is not None else [k for k in row if k not in LABEL_FIELDS]
    return json.dumps({k: row.get(k) for k in sorted(keys)}, sort_keys=True, default=str)


def load_arms(spec, rows):
    """Group rows into {arm: {seed: row}} and check preconditions.

    Returns (arms, values, problems, notes). `values[arm][seed][field]` is a
    Fraction. `problems` non-empty means INSTRUMENT_FAIL."""
    sk, seeds, schema = spec["seed_key"], spec["seeds"], spec["schema"]
    known = set(spec["required_arms"]) | set(spec["optional_arms"])
    problems, notes = [], []
    grouped = {}
    for i, r in enumerate(rows):
        if not isinstance(r, dict):
            problems.append(f"row {i} is not an object")
            continue
        arm = r.get("arm")
        if arm is None or arm in META_ARMS:
            continue
        if arm not in known:
            notes.append(f"row {i}: undeclared arm {arm!r} ignored")
            continue
        grouped.setdefault(arm, []).append(r)

    present = [a for a in spec["required_arms"]] + [a for a in spec["optional_arms"] if a in grouped]
    arms, values = {}, {}
    for arm in present:
        rs = grouped.get(arm, [])
        if not rs:
            problems.append(f"required arm {arm} has no rows")
            continue
        by = {}
        for r in rs:
            if sk not in r:
                problems.append(f"{arm}: row without seed key {sk!r}")
                continue
            by.setdefault(repr(r[sk]), []).append(r)
        want = {repr(s) for s in seeds}
        dup = sorted(s for s, v in by.items() if len(v) > 1)
        extra = sorted(set(by) - want)
        miss = sorted(want - set(by))
        if dup:
            problems.append(f"{arm}: more than one row for seeds {dup}")
        if extra:
            problems.append(f"{arm}: undeclared seeds {extra}")
        if miss:
            problems.append(f"{arm}: missing seeds {miss}")
        if dup or extra or miss:
            continue
        arms[arm] = {s: by[repr(s)][0] for s in seeds}
        values[arm] = {}
        for s in seeds:
            row, vs = arms[arm][s], {}
            for f in schema:
                if f not in row:
                    problems.append(f"{arm} seed {s!r}: schema field {f!r} absent")
                    continue
                try:
                    vs[f] = to_fraction(row[f], f"{arm} seed {s!r} field {f!r}")
                except ContractError as e:
                    problems.append(str(e))
            values[arm][s] = vs
        arm_only = sorted({k for r in rs for k in r} - set(schema) - LABEL_FIELDS)
        if arm_only:
            notes.append(f"{arm}: non-schema fields present and never read: {arm_only}")
    return arms, values, problems, notes


def seed_independence(spec, arms):
    """Return problems for any arm in which two seeds carry identical payloads.

    The payload is every non-label field of the row (schema and diagnostics),
    so a world should record at least one seed-dependent raw measurement."""
    out = []
    if len(spec["seeds"]) < 2:
        return out
    for arm, by in arms.items():
        seen = {}
        for s, row in by.items():
            seen.setdefault(payload(row), []).append(s)
        for group in seen.values():
            if len(group) > 1:
                out.append(f"pseudo-replication: {arm} seeds {group} carry identical payloads "
                           f"(duplicated rows, not independent replicates)")
    return out


# --------------------------------------------------------------------------- clauses
def clause_values(spec, values, arm):
    """Evaluate every success clause on one arm. Same code for every arm."""
    res = {}
    for c in spec["success_clauses"]:
        xs = [values[arm][s][c["field"]] for s in spec["seeds"]]
        v = aggregate(xs, c["agg"])
        res[c["id"]] = dict(_fmt(v), holds=bool(compare(v, c["comparison"], c["threshold"], c["tolerance"])),
                            _value=v)
    return res


def meets_success(per_clause):
    if not per_clause:   # no clause evaluated is not a success
        return False
    return all(c["holds"] for c in per_clause.values())


def _clean(per_arm):
    return {a: {cid: {k: v for k, v in c.items() if not k.startswith("_")} for cid, c in cl.items()}
            for a, cl in per_arm.items()}


def criterion_text(spec):
    parts = [f"{c['id']}: {c['agg']}({c['field']}) {c['comparison']} {c['threshold']} (tol {c['tolerance']})"
             for c in spec["success_clauses"]]
    return ("SUCCESS(arm) iff every clause holds on that arm, over seeds "
            f"{spec['seeds']}; " + "; ".join(parts) +
            ". The same rule judges TREATMENT, NULL_TWIN, SIMPLE_ALT, POSITIVE_CONTROL and CHEAT.")


# --------------------------------------------------------------------------- outcome
def _result(outcome, reason, **kw):
    out = {"outcome": outcome, "outcome_reason": reason,
           "positive_control_detected": None, "cheat_detected": None,
           "null_twin_meets_success": None, "simple_alt_meets_success": None,
           "treatment_meets_success": None, "clauses": {}, "preconditions": {"ok": False, "problems": []},
           "anomalies": [], "notes": []}
    out.update(kw)
    return out


def evaluate(spec, rows):
    """Apply the contract. Always returns a dict; never raises."""
    try:
        return _evaluate(spec, rows)
    except Exception as e:  # noqa: BLE001 -- the contract is "never crash"
        return _result(INSTRUMENT_FAIL, f"evaluator error {type(e).__name__}: {e}",
                       anomalies=[f"internal error {type(e).__name__}: {e}"])


def _evaluate(spec, rows):
    try:
        sp = validate_spec(spec)
    except ContractError as e:
        return _result(INSTRUMENT_FAIL, f"spec invalid: {e}",
                       preconditions={"ok": False, "problems": [f"spec: {e}"]})
    if not isinstance(rows, list):
        return _result(INSTRUMENT_FAIL, "rows is not a list",
                       preconditions={"ok": False, "problems": ["rows is not a list"]})

    arms, values, problems, notes = load_arms(sp, rows)
    if problems:
        return _result(INSTRUMENT_FAIL, "preconditions failed: " + "; ".join(problems[:5]),
                       preconditions={"ok": False, "problems": problems}, notes=notes,
                       criterion_as_applied=criterion_text(sp))
    dup = seed_independence(sp, arms)
    if dup:
        return _result(INSTRUMENT_FAIL, "seed independence failed: " + "; ".join(dup[:3]),
                       preconditions={"ok": False, "problems": dup}, anomalies=dup, notes=notes,
                       criterion_as_applied=criterion_text(sp))

    per_arm = {a: clause_values(sp, values, a) for a in arms}
    succ = {a: meets_success(per_arm[a]) for a in arms}
    pc, ch = succ[POSITIVE_CONTROL], succ[CHEAT]
    nt, sa, tr = succ[NULL_TWIN], succ[SIMPLE_ALT], succ[TREATMENT]
    anomalies = []
    pc_missed = [cid for cid, c in per_arm[POSITIVE_CONTROL].items() if not c["holds"]]
    sa_failed = [cid for cid, c in per_arm[SIMPLE_ALT].items() if not c["holds"]]

    if not pc:
        if sp["stage"] == "pilot":
            outcome, reason = SPEC_UNATTAINABLE, f"positive control misses clauses {pc_missed} at pilot"
        else:
            outcome, reason = INSTRUMENT_FAIL, f"positive control not detected (misses {pc_missed})"
    elif not ch:
        outcome, reason = INSTRUMENT_FAIL, "cheat control does not meet the success rule (instrument cannot fire on it)"
    elif nt:
        outcome, reason = CONFOUNDED, "null twin meets the success rule"
    elif tr and sa:
        outcome, reason = CONFOUNDED, "SIMPLE_ALT meets every success clause (L1): treatment not distinguished from the simpler alternative"
    elif tr:
        outcome, reason = SIGNAL, f"treatment meets every clause; twin does not; SIMPLE_ALT fails {sa_failed}"
    else:
        tr_failed = [cid for cid, c in per_arm[TREATMENT].items() if not c["holds"]]
        outcome, reason = NULL, f"treatment fails clauses {tr_failed}"
        if sa:
            anomalies.append("SIMPLE_ALT meets every success clause while treatment does not: clause set does not need the mechanism")

    return _result(outcome, reason,
                   positive_control_detected=pc, cheat_detected=ch, null_twin_meets_success=nt,
                   simple_alt_meets_success=sa, treatment_meets_success=tr,
                   clauses=_clean(per_arm), preconditions={"ok": True, "problems": []},
                   anomalies=anomalies, notes=notes, criterion_as_applied=criterion_text(sp))


def evaluate_file(spec, rows_path):
    rows, err = load_rows(rows_path)
    if err:
        return _result(INSTRUMENT_FAIL, err, preconditions={"ok": False, "problems": [err]})
    return evaluate(spec, rows)


def check_output_name(output_path, input_paths):
    """L10: the output file must not share a case-folded basename with any input."""
    import os
    o = os.path.basename(output_path).casefold()
    clash = [p for p in input_paths if os.path.basename(p).casefold() == o]
    if clash:
        raise ContractError(f"output {output_path!r} collides with input(s) {clash}")
