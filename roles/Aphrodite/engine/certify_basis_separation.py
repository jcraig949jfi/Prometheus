"""BASIS-SEPARATION CERTIFICATE, formalised to the operator's ruling of
2026-09-21. RUN BEFORE ANY EVOLUTIONARY SEARCH.

  B1 BASIS INSUFFICIENCY   the unchanged primitive basis alone cannot solve
                           the variable-length family above the declared
                           threshold -- including when it is given access to
                           the query parameter `last`, which closes the side
                           channel explicitly.
  B2 M2 SUFFICIENCY        at least one valid witness exists inside the exact
                           fold grammar and escrow.
  B3 NEGATIVE DISCRIMINATION  a deliberately inexpressible family
                           (collatz_steps: no branch primitive, no integer
                           constants) is REJECTED by the reachability
                           analysis. A certificate that cannot fail a family
                           it should fail is not a certificate.
  B4 LENGTH EXTRAPOLATION  the witness, at fixed artifact size, continues to
                           work at sequence lengths well outside those seen
                           during search -- so the mechanism is genuinely
                           iterative rather than a bounded unrolling or an
                           accidental fit.

INVARIANT 1 is applied throughout: a witness is credited only if no simpler
causal surrogate reproduces its capability.

No witness found here is given to any improver.
"""
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import engine as E      # noqa: E402
import basis_v2 as B    # noqa: E402

CANDIDATES = ["list_sum", "list_prod_mod", "collatz_steps"]
DEV_N = 2
VALIDATION_N = 300
SOLVE_THRESHOLD = 0.99
FAIL_THRESHOLD = 0.10
COMPOSE_BUDGET = 5 * 10 ** 6
FOLD_BUDGET = 200000


def cert_seed(family, i=0):
    return int(hashlib.sha256(
        ("APHRODITE/ENGINE/BASISCERT/v2/%s/%d" % (family, i)).encode()).hexdigest()[:16], 16)


def _accuracy(source, instances):
    art = E.Artifact.from_modules(
        dict(E.base_image(), search=E.base_image()["search"] + source))
    r = E.Recipient.fresh(seed=11)
    r.load(art)
    return r.run_tasks(instances, E.Escrow(10 ** 7))["accuracy"], art


def _vectors(instances, with_last):
    """Terminals offered to the bounded composition. `with_last` deliberately
    hands it the query parameter, to prove that access alone does not solve
    the family."""
    vecs = []
    for t in instances:
        nums = [int(v) for v in re.findall(r"-?\d+", t["prompt"])]
        row = nums[:E.TERMINALS] + ([nums[-1]] if with_last else [])
        while len(row) < E.TERMINALS:
            row.append(0)
        vecs.append(row)
    return vecs, [t["gold"] for t in instances]


def certify(family):
    dev = B.tasks(family, DEV_N, cert_seed(family, 0))
    val = B.tasks(family, VALIDATION_N, cert_seed(family, 1))
    long_val = B.tasks(family, VALIDATION_N, cert_seed(family, 2),
                       length_range=B.EXTRAPOLATION_LENGTHS)
    stress = B.tasks(family, 100, cert_seed(family, 3),
                     length_range=(B.STRESS_LENGTH, B.STRESS_LENGTH))
    rec = {"family": family,
           "required_property": B.REQUIRED_PROPERTY[family],
           "query_parameter_outside_sequence": B.uses_query_param(family),
           "search_lengths": list(B.SEARCH_LENGTHS),
           "extrapolation_lengths": list(B.EXTRAPOLATION_LENGTHS),
           "stress_length": B.STRESS_LENGTH,
           "development_instances": DEV_N}

    # ---- B1 basis insufficiency, with and without the query parameter
    b1 = {}
    for label, with_last in (("without_last", False), ("with_last", True)):
        vecs, golds = _vectors(dev, with_last)
        esc = E.Escrow(COMPOSE_BUDGET)
        got = E._compose_v2(vecs, golds, esc, COMPOSE_BUDGET)
        acc = None
        if got:
            acc, _ = _accuracy(E._discovered_solver_source(family, got[0]), val)
        b1[label] = {"found_on_dev": bool(got), "expression": got[0] if got else None,
                     "validated_accuracy": acc, "charges": esc.spent,
                     "solves": bool(acc is not None and acc >= SOLVE_THRESHOLD)}
    rec["B1_basis_insufficiency"] = dict(
        b1, **{"pass": not (b1["without_last"]["solves"] or b1["with_last"]["solves"])})

    # ---- B2 M2 sufficiency
    esc2 = E.Escrow(FOLD_BUDGET)
    mech = B.search_fold(family, dev, esc2, FOLD_BUDGET)
    mech_acc, art = (None, None)
    if mech:
        mech_acc, art = _accuracy(mech["source"], val)
    rec["B2_m2_sufficiency"] = {
        "mechanism": ({"init": mech["init"], "body": mech["body"],
                       "final": mech["final"]} if mech else None),
        "validated_accuracy": mech_acc,
        "charges": esc2.spent,
        "pass": bool(mech and mech_acc is not None and mech_acc >= SOLVE_THRESHOLD),
    }

    # ---- INVARIANT 1: no simpler surrogate reproduces it
    rec["surrogate_battery"] = {"survivors": [], "load_bearing": None}
    if rec["B2_m2_sufficiency"]["pass"]:
        survivors = []
        for name, src in B.fold_surrogates(family, mech):
            try:
                a, _ = _accuracy(src, val)
            except Exception:      # noqa: BLE001
                continue
            if a >= mech_acc - 1e-9:
                survivors.append({"surrogate": name, "accuracy": a})
        rec["surrogate_battery"] = {"survivors": survivors,
                                    "load_bearing": len(survivors) == 0}

    # ---- B4 length extrapolation at FIXED artifact size
    rec["B4_length_extrapolation"] = {"pass": None}
    if rec["B2_m2_sufficiency"]["pass"]:
        long_acc, _ = _accuracy(mech["source"], long_val)
        stress_acc, _ = _accuracy(mech["source"], stress)
        single = dict(B.fold_surrogates(family, mech))["single_iteration"]
        single_long, _ = _accuracy(single, long_val)
        rec["B4_length_extrapolation"] = {
            "artifact_sha256": art.sha256,
            "artifact_bytes": len(art.bytes),
            "accuracy_at_search_lengths": mech_acc,
            "accuracy_at_extrapolation_lengths": long_acc,
            "accuracy_at_stress_length_%d" % B.STRESS_LENGTH: stress_acc,
            "single_iteration_at_extrapolation": single_long,
            "pass": bool(long_acc >= SOLVE_THRESHOLD and stress_acc >= SOLVE_THRESHOLD
                         and single_long < FAIL_THRESHOLD),
        }

    rec["ELIGIBLE_TO_FREEZE"] = bool(
        rec["B1_basis_insufficiency"]["pass"]
        and rec["B2_m2_sufficiency"]["pass"]
        and rec["surrogate_battery"]["load_bearing"]
        and rec["B4_length_extrapolation"].get("pass"))
    return rec


def main():
    rows = [certify(f) for f in CANDIDATES]
    by = {r["family"]: r for r in rows}
    negative = by.get("collatz_steps", {})
    out = {
        "written_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "engine_sha256": E.source_hash(),
        "grammar_version": E.GRAMMAR_VERSION,
        "grammar_hash": E.grammar_hash(),
        "basis_primitives": B.BASIS_PRIMITIVES,
        "mechanism_grammar": ("M2 fold: acc = INIT; for v in vals: acc = E(acc, v); "
                              "return F(acc[, last])  -- `last` exposed ONLY for "
                              "query-parameter families"),
        "thresholds": {"solves": SOLVE_THRESHOLD, "fails": FAIL_THRESHOLD},
        "candidates": rows,
        "B3_negative_discrimination": {
            "family": "collatz_steps",
            "rejected_as_expected": not negative.get("B2_m2_sufficiency", {}).get("pass", True),
            "note": ("the basis has no branch primitive and no integer constants, "
                     "so the 3n+1 transition is inexpressible; if this family had "
                     "passed, the certificate would be suspect"),
        },
        "eligible_families": [r["family"] for r in rows if r["ELIGIBLE_TO_FREEZE"]],
        "status": "CERTIFICATE ONLY -- no evolutionary search was run",
    }
    (HERE / "BASIS_SEPARATION_CERTIFICATE_2026-09-21.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
