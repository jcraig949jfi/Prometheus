"""H-R7-1 (round 7, SWARM_R7 O1; operator 23 ruling, D13): EVIDENCE_N_v1, the ONE evidentiary sample rule.

Operator 23: "the word verdict means the observation survived minimum stochastic diversity". Any job whose
experiment_class can emit a verdict must declare exactly

    runs_total 32, rng_family_count 4, runs_per_family 8, families = 4 distinct ids, n_per_family = 8 each

(family balance is structural: 16/1/16, 32/4/(16,8,4,4) and 32/4/(29,1,1,1) do not qualify). The rule is checked
LEFT of the run: at admission (fabric/envelope.admit, zero simulation), at the predicate (predicate_ref.post_predicate)
and at the receipt (receipt_guard). All three import this module; there is no other copy.

An envelope may instead declare `evidence_class: OBSERVATION`: it is admitted at any sample size, and no receipt it
files can carry PASS/FAIL (OBSERVATION_CARRIES_VERDICT). Versioned: a different regime is a new rule id, prospectively.
Existing round 6 receipts are not re-judged. Leave-one-family-out is NOT part of admission (operator 23).
"""
from __future__ import annotations

RULE = "EVIDENCE_N_v1"
VERDICT_CLASSES = frozenset({"CLAUSE_A", "CLAUSE_B", "ANTI_PRIOR", "DISTANT_QD", "ROBUSTNESS_LOO", "REPLICATION",
                             "B2_SCREEN", "R16_SCREEN_CELL"})
NEED = {"runs_total": 32, "rng_family_count": 4, "runs_per_family": 8}
EVIDENCE_CLASSES = ("VERDICT", "OBSERVATION")
VERDICT_WORDS = ("PASS", "FAIL")
REASON = "SAMPLE_RULE_MISMATCH"
OBSERVATION_REASON = "OBSERVATION_CARRIES_VERDICT"


def _int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def failures(sample) -> list[str]:
    """Every way `sample` misses EVIDENCE_N_v1 (empty = conforms)."""
    if not isinstance(sample, dict):
        return ["no sample block declared"]
    out = []
    for k, need in NEED.items():
        v = sample.get(k)
        if not _int(v):
            out.append(f"{k} missing or not an int ({v!r})")
        elif v != need:
            out.append(f"{k} {v} != {need}")
    fams, per = sample.get("families"), sample.get("n_per_family")
    if not isinstance(fams, list) or not all(_int(f) for f in fams) or len(set(fams)) != len(fams):
        out.append(f"families must be a list of distinct int ids ({fams!r})")
    elif len(fams) != NEED["rng_family_count"]:
        out.append(f"families declares {len(fams)} ids != {NEED['rng_family_count']}")
    if not isinstance(per, dict):
        out.append(f"n_per_family missing ({per!r})")
    else:
        try:
            counts = {int(k): v for k, v in per.items()}
        except (TypeError, ValueError):
            counts = None
            out.append(f"n_per_family keys are not family ids ({sorted(per)})")
        if counts is not None:
            if isinstance(fams, list) and sorted(counts) != sorted(f for f in fams if _int(f)):
                out.append(f"n_per_family keys {sorted(counts)} != families {sorted(fams)}")
            unbalanced = {k: v for k, v in counts.items() if v != NEED["runs_per_family"]}
            if unbalanced:
                out.append(f"n_per_family not balanced at {NEED['runs_per_family']}: {unbalanced}")
            if all(_int(v) for v in counts.values()) and _int(sample.get("runs_total")) \
                    and sum(counts.values()) != sample["runs_total"]:
                out.append(f"runs_total {sample['runs_total']} != sum(n_per_family) {sum(counts.values())}")
    return out


def mismatch(sample) -> dict | None:
    f = failures(sample)
    return None if not f else {"reason": REASON, "rule": RULE, "failures": f, "sample": sample, "need": NEED}


def evidence_class_of(obj: dict | None) -> str | None:
    obj = obj or {}
    return obj.get("evidence_class") or (obj.get("envelope") or {}).get("evidence_class")


def _bad_class(ec) -> dict | None:
    if ec is not None and ec not in EVIDENCE_CLASSES:
        return {"reason": REASON, "rule": RULE, "failures": [f"evidence_class {ec!r} not in {EVIDENCE_CLASSES}"]}
    return None


def requirement(experiment_class, sample, evidence_class=None) -> dict | None:
    """None when the declared job/predicate may proceed; else the SAMPLE_RULE_MISMATCH refusal."""
    bad = _bad_class(evidence_class)
    if bad:
        return bad
    if evidence_class == "OBSERVATION" or experiment_class not in VERDICT_CLASSES:
        return None
    return mismatch(sample)


def admission(env: dict | None) -> dict | None:
    """envelope.admit's check, before any ceiling, clock or simulation. The sample fields sit at the envelope's top
    level (F 1789504304514-0: runs_total, rng_family_count, runs_per_family, families, n_per_family); a `sample` block
    is read too."""
    env = env or {}
    return requirement(env.get("experiment_class"), sample_of(env), env.get("evidence_class"))


def admission_reasons(env: dict | None) -> list[str]:
    """The hook F's envelope.admit calls: [] or ["SAMPLE_RULE_MISMATCH"] (stub False on that reason, D16)."""
    return [] if admission(env) is None else [REASON]


def sample_of(rec: dict) -> dict:
    """A receipt's sample block: rec['sample'], else the top-level (or science) schema fields."""
    if isinstance(rec.get("sample"), dict):
        return rec["sample"]
    sci = rec.get("science") or {}
    return {k: rec.get(k, sci.get(k)) for k in ("runs_total", "rng_family_count", "runs_per_family", "families",
                                                "n_per_family")}


def receipt(rec: dict, verdict_words=VERDICT_WORDS) -> list[dict]:
    """Receipt-time refusals: an OBSERVATION carrying PASS/FAIL, or a verdict whose sample misses the rule."""
    ec = evidence_class_of(rec)
    bad = _bad_class(ec)
    if bad:
        return [bad]
    sci = rec.get("science") or {}
    words = {str(rec.get("status") or ""), str(sci.get("verdict") or "")}
    if ec == "OBSERVATION":
        carried = sorted(w for w in words if w in verdict_words)
        return [{"reason": OBSERVATION_REASON, "rule": RULE, "failures": [f"OBSERVATION carries {carried}"]}] \
            if carried else []
    return []
