"""G-R5-1 (round 5 P-BUILD, builder G): the explicit seed/run schema (operator 19 s2).

Round 4 wrote sampling as "32 x 4", which reads as 128 runs. Every new row, summary, receipt and worlds cell stamp
carries the three fields instead, top-level:

  runs_total        int   runs pooled
  rng_family_count  int   distinct RNG families
  runs_per_family   int   runs in every family; None when families are unequal

plus families (sorted family ids) and n_per_family ({"4200": 8, ...}) beside them -- ONE list and ONE map, the names
BASELINE_N and F12 already read (conductor 1789467299042-0: no rng_families key anywhere new). Invariants
(check_invariant): runs_total == sum(n_per_family); rng_family_count == len(families) == len(n_per_family);
runs_per_family == runs_total / rng_family_count whenever it is not None.

The same three-field minimum is enforced for baselines (BASELINE_N) and Clause A candidates (CANDIDATE_N, O4):
runs_total >= 32, rng_family_count >= 4, runs_per_family >= 8 (every family, when unequal).

lint_text flags an "N x M" written for a run count ("32 x 4 families", "8x4 runs", "32 runs x 4"); budgets such as
"800 x 128 genomes" are not run counts and are not flagged.
"""
from __future__ import annotations

import re

FIELDS = ("runs_total", "rng_family_count", "runs_per_family")
NEED = {"runs_total": 32, "rng_family_count": 4, "runs_per_family": 8}
PILOT_B2 = {"runs_total": 16, "rng_family_count": 2, "runs_per_family": 8}


def from_counts(n_per_family: dict) -> dict:
    """{family: n} -> the explicit stamp."""
    per = {str(int(k)): int(v) for k, v in n_per_family.items() if int(v) > 0}
    fams = sorted(int(k) for k in per)
    total = sum(per.values())
    counts = set(per.values())
    s = {"runs_total": total, "rng_family_count": len(fams),
         "runs_per_family": counts.pop() if len(counts) == 1 else None,
         "families": fams, "n_per_family": per}
    check_invariant(s)
    return s


def stamp(runs) -> dict:
    """Run rows (rng_family, run_seed) -> the explicit stamp. Refuses a duplicate (family, run seed)."""
    seen, per = set(), {}
    for x in runs:
        key = (int(x["rng_family"]), int(x["run_seed"]))
        if key in seen:
            raise ValueError(f"duplicate run {key}")
        seen.add(key)
        per[key[0]] = per.get(key[0], 0) + 1
    return from_counts(per)


def check_invariant(s: dict) -> None:
    if "rng_families" in s:
        raise ValueError("rng_families is not a schema field: use families (conductor 1789467299042-0)")
    fams = s.get("families")
    if fams is not None and s["rng_family_count"] != len(set(fams)):
        raise ValueError(f"rng_family_count {s['rng_family_count']} != len(families) {len(set(fams))}")
    per = s.get("n_per_family")
    if fams is not None and per is not None and sorted(int(f) for f in fams) != sorted(int(k) for k in per):
        raise ValueError(f"families {sorted(fams)} != n_per_family keys {sorted(per)}")
    if per is not None:
        if s["runs_total"] != sum(int(v) for v in per.values()):
            raise ValueError(f"runs_total {s['runs_total']} != sum(n_per_family) {sum(int(v) for v in per.values())}")
        if s["rng_family_count"] != len(per):
            raise ValueError(f"rng_family_count {s['rng_family_count']} != len(n_per_family) {len(per)}")
    rpf = s.get("runs_per_family")
    if rpf is not None and s["runs_total"] != s["rng_family_count"] * rpf:
        raise ValueError(f"runs_total {s['runs_total']} != rng_family_count {s['rng_family_count']} * runs_per_family {rpf}")


def meets(s: dict | None, need: dict = NEED) -> bool:
    """The three-field minimum. Unequal families (runs_per_family None) pass only if every family has >= need."""
    if not s:
        return False
    try:
        total, count = int(s.get("runs_total") or 0), int(s.get("rng_family_count") or 0)
    except (TypeError, ValueError):
        return False
    rpf = s.get("runs_per_family")
    per = s.get("n_per_family")
    if rpf is None:
        if not per:
            return False
        rpf_ok = min(int(v) for v in per.values()) >= need["runs_per_family"]
    else:
        rpf_ok = int(rpf) >= need["runs_per_family"] and (not per or min(int(v) for v in per.values()) >= need["runs_per_family"])
    return total >= need["runs_total"] and count >= need["rng_family_count"] and rpf_ok


def refusal(s: dict | None, prefix: str, need: dict = NEED) -> dict:
    """Machine-readable payload of a sample-rule refusal (prefix 'candidate' or 'baseline')."""
    s = s or {}
    out = {f"{prefix}_{k}": s.get(k) for k in FIELDS}
    out[f"{prefix}_n_per_family"] = s.get("n_per_family")
    out.update({f"need_{k}": v for k, v in need.items()})
    return out


_RUNWORD = r"(?:rng\s*)?(?:famil(?:y|ies)|runs?|run\s*seeds?|seeds?)"
LINT = [re.compile(r"\b\d+\s*[x×X]\s*\d+\s*" + _RUNWORD, re.I),                    # 32 x 4 families, 8x4 runs
        re.compile(r"\b\d+\s*(?:runs?|run\s*seeds?|seeds?)\s*[x×X]\s*\d+", re.I)]  # 32 runs x 4, 8 seeds x 4


def lint_text(text: str) -> list[str]:
    """Every "N x M" run-count phrase in `text` (operator 19 s2: new receipts and tables use the three fields)."""
    hits = []
    for pat in LINT:
        hits += [m.group(0) for m in pat.finditer(text)]
    return hits
