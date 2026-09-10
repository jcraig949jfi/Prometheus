"""C3 exact-symmetry null check. Executable, for Archaeon's 18 null rows.

Takes two `ca_density_v0` wrapper results -- an UNTRANSFORMED twin and its
TRANSFORMED partner -- and returns IDENTICAL, NOT_IDENTICAL or INDETERMINATE.

WHAT THE SYMMETRY PREDICTS. Reflection and complement are exact
semantics-preserving moves, so the two runs must misclassify THE SAME initial
conditions. That is the claim, and the correctness mask is the field that
carries it.

THE FIELDS, IN THE ORDER THEY MATTER

    mask digest         orientation-free by construction, because it is a
                        per-IC boolean vector rather than a lattice. This is
                        the field that carries the claim.
    witness ICs         which initial conditions failed. Same content as the
                        mask, in a form a human can act on. Compared when both
                        rows carry it and neither was truncated.
    incorrect counts    necessary but weak: two different masks can share a
                        count, and a permutation of failures is exactly what a
                        broken reflection produces.
    per-sample accuracy weakest, and it can agree for the WRONG REASON under
                        complement, because the target flips and a target-flip
                        bug can land on the same accuracy with a different set
                        of ICs wrong. Never sufficient alone.

COMPLEMENT HANDLING. The majority target flips with the complemented initial
condition; it is not a correction applied afterwards. A row that complemented
the run but computed its target from the ORIGINAL IC will report a symmetry
failure that did not happen. That is the specific false-negative route, and
`explain` names it whenever a complement row fails on mask but agrees on
accuracy.

NEVER COMPARE RAW TRAJECTORIES. Two identical dynamics under a mirror produce
different bytes, so a digest of those bytes reports a break that has not
happened. This module refuses to compare any field whose name suggests a
trajectory or a lattice, and says so rather than silently ignoring it.

INDETERMINATE IS NOT FAILURE. A row that cannot evidence that the INITIAL
CONDITION was transformed has not run the test: "same seed" alone is not the
symmetry. So is a row with a truncated witness, or a missing mask digest.
Those are scope facts, not results.

    python -m herakles.evca.c3_null_check --self-test
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Dict, List, Optional, Tuple

IDENTICAL = "IDENTICAL"
NOT_IDENTICAL = "NOT_IDENTICAL"
INDETERMINATE = "INDETERMINATE"

TRANSFORMS = ("none", "reflect", "complement", "reflect_complement")

#: Fields that must never be compared across a transform.
FORBIDDEN_FIELDS = ("trajectory", "frames", "lattice", "raster", "state",
                    "trajectory_digest", "space_time")

#: The comparison, strongest first. (field, required, weight)
COMPARED = ("mask_digest", "witness", "incorrect_counts", "accuracy_per_sample")


def _get(row: Dict, *names, default=None):
    for n in names:
        if n in row and row[n] is not None:
            return row[n]
    return default


def _transform_of(row: Dict) -> Optional[str]:
    t = _get(row, "transform", "symmetry", "arm_transform")
    if t is None:
        return None
    t = str(t).strip().lower()
    return t if t in TRANSFORMS else None


def check_pair(base_row: Dict, transformed_row: Dict) -> Dict[str, object]:
    """Compare an untransformed twin with its transformed partner."""
    reasons: List[str] = []
    compared: List[str] = []
    disagreed: List[str] = []

    forbidden = sorted({f for f in FORBIDDEN_FIELDS
                        if f in base_row or f in transformed_row})

    transform = _transform_of(transformed_row)
    if transform is None:
        return _out(INDETERMINATE, transform, compared, disagreed, forbidden,
                    ["the transformed row does not declare which transform it "
                     "applied; without that the comparison has no claim to "
                     "test"])
    if transform == "none":
        return _out(INDETERMINATE, transform, compared, disagreed, forbidden,
                    ["the 'transformed' row declares transform=none, so this "
                     "is a twin pair and not a symmetry test"])

    # The IC must have been transformed too. "Same seed" alone is not it.
    ic_flag = _get(transformed_row, "ic_transformed", "initial_condition_"
                   "transformed", "ic_transform_applied")
    if ic_flag is None:
        return _out(INDETERMINATE, transform, compared, disagreed, forbidden,
                    ["the row does not record whether the INITIAL CONDITION "
                     "was transformed. Transforming the rule alone is not the "
                     "symmetry, so this row has not run the test"])
    if not bool(ic_flag):
        return _out(INDETERMINATE, transform, compared, disagreed, forbidden,
                    ["the row records that the initial condition was NOT "
                     "transformed. Rule-only is not the symmetry; this is a "
                     "scope fact, not a failed null"])

    # Complement must flip the majority target. Absence is indeterminate.
    if "complement" in transform:
        flip = _get(transformed_row, "majority_target_flipped",
                    "target_flipped")
        if flip is None:
            reasons.append(
                "complement row does not record whether the majority target "
                "flipped; if it was computed from the ORIGINAL IC this "
                "comparison will report a break that did not happen")
        elif not bool(flip):
            return _out(INDETERMINATE, transform, compared, disagreed,
                        forbidden,
                        ["complement row records the majority target as NOT "
                         "flipped. Under complement it must flip. The row is "
                         "mis-specified rather than falsifying the symmetry"])

    # ---- strongest field first
    bm = _get(base_row, "mask_digest", "correct_mask_digest")
    tm = _get(transformed_row, "mask_digest", "correct_mask_digest")
    if bm is None or tm is None:
        reasons.append("no mask digest on one or both rows; the field that "
                       "carries the claim is absent")
    else:
        compared.append("mask_digest")
        if bm != tm:
            disagreed.append("mask_digest")

    bw, tw = _get(base_row, "witness"), _get(transformed_row, "witness")
    b_tr = bool(_get(base_row, "witness_truncated", default=False))
    t_tr = bool(_get(transformed_row, "witness_truncated", default=False))
    if bw is not None and tw is not None:
        if b_tr or t_tr:
            reasons.append("witness truncated on at least one row; not "
                           "compared, because a truncated witness cannot "
                           "evidence equality")
        else:
            compared.append("witness")
            if sorted(bw) != sorted(tw):
                disagreed.append("witness")

    bc = _get(base_row, "incorrect_counts", "n_incorrect")
    tc = _get(transformed_row, "incorrect_counts", "n_incorrect")
    if bc is not None and tc is not None:
        compared.append("incorrect_counts")
        if bc != tc:
            disagreed.append("incorrect_counts")

    ba = _get(base_row, "accuracy_per_sample", "accuracy")
    ta = _get(transformed_row, "accuracy_per_sample", "accuracy")
    if ba is not None and ta is not None:
        compared.append("accuracy_per_sample")
        if ba != ta:
            disagreed.append("accuracy_per_sample")

    if "mask_digest" not in compared and "witness" not in compared:
        reasons.append("neither the mask digest nor an untruncated witness "
                       "was available, so nothing decisive was compared; "
                       "accuracy and counts alone cannot establish the "
                       "symmetry")
        return _out(INDETERMINATE, transform, compared, disagreed, forbidden,
                    reasons)

    if disagreed:
        if ("complement" in transform
                and "mask_digest" in disagreed
                and "accuracy_per_sample" in compared
                and "accuracy_per_sample" not in disagreed):
            reasons.append(
                "SUSPECT A TARGET-FLIP BUG: the mask differs while the "
                "accuracy agrees. Under complement that is the signature of a "
                "target computed from the ORIGINAL initial condition")
        return _out(NOT_IDENTICAL, transform, compared, disagreed, forbidden,
                    reasons)
    return _out(IDENTICAL, transform, compared, disagreed, forbidden, reasons)


def _out(verdict, transform, compared, disagreed, forbidden, reasons):
    if forbidden:
        reasons = list(reasons) + [
            "rows carry field(s) %s which are NOT compared: two identical "
            "dynamics under a mirror produce different bytes, so comparing a "
            "trajectory across a transform reports a break that has not "
            "happened" % (", ".join(forbidden),)]
    return {"verdict": verdict, "transform": transform,
            "fields_compared": compared, "fields_disagreed": disagreed,
            "fields_refused": forbidden, "reasons": reasons}


def check_rows(rows: List[Dict]) -> List[Dict]:
    """Pair every transformed row with the untransformed twin sharing its id."""
    base = {}
    for r in rows:
        if _transform_of(r) in (None, "none"):
            key = _get(r, "twin_id", "pair_id", "rule_hex")
            if key is not None:
                base[key] = r
    out = []
    for r in rows:
        t = _transform_of(r)
        if t in (None, "none"):
            continue
        key = _get(r, "twin_id", "pair_id", "rule_hex")
        b = base.get(key)
        if b is None:
            out.append({"row": key, "verdict": INDETERMINATE,
                        "transform": t, "fields_compared": [],
                        "fields_disagreed": [], "fields_refused": [],
                        "reasons": ["no untransformed twin found for %r" % key]})
            continue
        res = check_pair(b, r)
        res["row"] = key
        out.append(res)
    return out


# ---------------------------------------------------------------------------
# Self-test against the committed transform fixture
# ---------------------------------------------------------------------------

def self_test() -> int:
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "c3_transform_fixture.json"),
              encoding="utf-8") as fh:
        fx = json.load(fh)
    failures = 0
    for rule, rec in sorted(fx["rules"].items()):
        base = {"twin_id": rule, "transform": "none",
                "mask_digest": rec["base_digest"],
                "n_incorrect": 1, "accuracy": rec["accuracy"]}
        for arm, key, flip in (("reflect", "reflect_digest", None),
                               ("complement", "complement_digest", True)):
            row = {"twin_id": rule, "transform": arm,
                   "ic_transformed": True,
                   "mask_digest": rec[key],
                   "n_incorrect": 1, "accuracy": rec["accuracy"]}
            if flip is not None:
                row["majority_target_flipped"] = flip
            got = check_pair(base, row)
            want = IDENTICAL
            ok = got["verdict"] == want
            failures += 0 if ok else 1
            print("%-10s %-12s %-14s %s" % (rule, arm, got["verdict"],
                                            "ok" if ok else "EXPECTED " + want))
    # negative: a target-flip bug, mask differs while accuracy agrees
    bug = check_pair({"twin_id": "x", "transform": "none",
                      "mask_digest": "sha256:aaa", "accuracy": 0.8},
                     {"twin_id": "x", "transform": "complement",
                      "ic_transformed": True, "majority_target_flipped": True,
                      "mask_digest": "sha256:bbb", "accuracy": 0.8})
    ok = (bug["verdict"] == NOT_IDENTICAL
          and any("TARGET-FLIP" in r for r in bug["reasons"]))
    failures += 0 if ok else 1
    print("%-10s %-12s %-14s %s" % ("negative", "complement", bug["verdict"],
                                    "ok, named the bug" if ok else "MISSED"))
    # indeterminate: rule transformed but IC not
    ind = check_pair({"twin_id": "y", "transform": "none",
                      "mask_digest": "sha256:aaa"},
                     {"twin_id": "y", "transform": "reflect",
                      "ic_transformed": False, "mask_digest": "sha256:aaa"})
    ok2 = ind["verdict"] == INDETERMINATE
    failures += 0 if ok2 else 1
    print("%-10s %-12s %-14s %s" % ("ic-only", "reflect", ind["verdict"],
                                    "ok" if ok2 else "EXPECTED INDETERMINATE"))
    print()
    print("self-test failures: %d" % failures)
    return 0 if failures == 0 else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--rows", help="JSON file: a list of wrapper result rows")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.rows:
        ap.error("give --rows or --self-test")
    with open(args.rows, encoding="utf-8") as fh:
        rows = json.load(fh)
    out = check_rows(rows if isinstance(rows, list) else rows.get("rows", []))
    print(json.dumps(out, indent=1))
    return 0 if all(r["verdict"] == IDENTICAL for r in out) else 1


if __name__ == "__main__":
    sys.exit(main())
