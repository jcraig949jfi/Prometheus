"""Slice 3 organ-reuse experiment. Frozen by AMENDMENT_7 + ADDENDUM 1.

Arms (16 paired recipients each, identical escrow, independent development
entropy per recipient index, shared across arms so the comparison is paired):

  CLOSED     list_prod_mod's complete fold, transplanted UNCHANGED, no search
  ORGAN      extracted organ, skeleton FROZEN, searches only the declared holes
  SCRATCH_A  as AMENDMENT 7 declared it: composition + the FULL fold space
  SCRATCH_B  the pre-slice-2C grammar: composition + scalar while-helper, no fold
  SHAM       SCRATCH_B's grammar while carrying the decorative h//h fossil
  POSITIVE   hand-written correct solver, to show the family is solvable

The tribunal is constructed only after each artifact is frozen and hashed.
Search never sees it.
"""
import json
import re
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import basis_v2 as B    # noqa: E402
import basis_v3 as V    # noqa: E402
import engine as E      # noqa: E402
import slice2c as S     # noqa: E402

FAMILY = json.loads((HERE / "THIRD_FAMILY_CERTIFICATE_2026-09-22.json").read_text()
                    )["selected_family"]
N = 16
BUDGET = 400000
DEV_PER_FAMILY = 2


def dev_for(i):
    return V.tasks(FAMILY, DEV_PER_FAMILY, E.dev_entropy("S3-%03d" % i, 0))


def _artifact(source):
    return E.Artifact.from_modules(
        dict(E.base_image(), search=E.base_image()["search"] + source),
        generation=E.FROZEN_GENERATION)


def _closed_source():
    """list_prod_mod's fold, unchanged. Chosen mechanically: list_prod_mod is
    the lexicographically first slice-2C family."""
    lin = S.Lineage2C(lineage_id="L2C-001", base=E.base_image())
    lin.evolve(generations=E.FROZEN_GENERATION, escrow=E.Escrow(10 ** 7))
    m = S.parse_folds(lin.extract(E.FROZEN_GENERATION))["list_prod_mod"]
    # transplanted verbatim, only the dispatch name changes so it is reachable
    # for the third family: no INIT, E, F, control flow or constant is touched
    return B.fold_source(FAMILY, m["init"], m["body"], m["final"])


def arm_closed(i, esc):
    return _closed_source(), 0


def arm_organ(i, esc):
    got = V.search_organ_holes(FAMILY, dev_for(i), esc, BUDGET)
    return (got[0]["source"], got[1]) if got else (None, esc.spent)


def arm_scratch_a(i, esc):
    dev = dev_for(i)
    got = B.search_fold(FAMILY, dev, esc, BUDGET)
    if got:
        return got["source"], esc.spent
    return None, esc.spent


def _composition_then_helper(i, esc, carry=""):
    """The pre-slice-2C grammar: bounded composition, then the scalar
    while-helper search. Neither can express variable-length accumulation."""
    dev = dev_for(i)
    vecs, golds = [], []
    for t in dev:
        nums = [int(v) for v in re.findall(r"-?\d+", t["prompt"])]
        while len(nums) < E.TERMINALS:
            nums.append(0)
        vecs.append(nums[:E.TERMINALS])
        golds.append(t["gold"])
    got = E._compose_v2(vecs, golds, esc, BUDGET)
    if got:
        return carry + E._discovered_solver_source(FAMILY, got[0]), esc.spent
    st = E._structural_search(dev, esc, BUDGET, __import__("random").Random(i))
    if st:
        return carry + E.helper_solver_source(FAMILY, st[0], st[1], st[2]), esc.spent
    return (carry or None), esc.spent


def arm_scratch_b(i, esc):
    return _composition_then_helper(i, esc)


def arm_sham(i, esc):
    """Equal-size structural scaffold that FAILED slice-2C load-bearing."""
    fossil = E.helper_solver_source(
        "sham_scaffold", e1="(x + y)", e2="(x // x)",
        answer="((h(nums[0], nums[1]) // h(nums[0], nums[1])) + (nums[0] * nums[1]))")
    return _composition_then_helper(i, esc, carry=fossil)


def arm_positive(i, esc):
    return V.organ_source(FAMILY, "0", "math.gcd(abs(acc), abs(v))", "acc"), 0


ARMS = {"CLOSED": arm_closed, "ORGAN": arm_organ, "SCRATCH_A": arm_scratch_a,
        "SCRATCH_B": arm_scratch_b, "SHAM": arm_sham, "POSITIVE": arm_positive}


def main():
    t0 = time.perf_counter()
    results = {}
    for arm, fn in ARMS.items():
        rows = []
        for i in range(N):
            esc = E.Escrow(BUDGET)
            started = time.perf_counter()
            try:
                src, charges = fn(i, esc)
            except E.EscrowExhausted:
                src, charges = None, esc.spent
            row = {"recipient": i, "charges_to_solution": charges if src else None,
                   "escrow_spent": esc.spent,
                   "seconds": round(time.perf_counter() - started, 2)}
            if src is None:
                row.update({"qualified": False, "artifact_sha256": None,
                            "disposition": "no solution found within escrow"})
            else:
                art = _artifact(src)          # FROZEN and hashed...
                trib = V.Tribunal3.after_freeze(art, FAMILY)   # ...before this exists
                sc = trib.score(art)
                row.update({
                    "artifact_sha256": art.sha256,
                    "artifact_bytes": len(art.bytes),
                    "tribunal": sc,
                    "qualified": bool(sc["held_out_extrapolation"] >= 0.99
                                      and sc["stress_length_200"] >= 0.99
                                      and sc["counterexample_accuracy"] >= 0.99
                                      and sc["metamorphic_pass"]),
                })
                row["disposition"] = "QUALIFIED" if row["qualified"] else (
                    "solution found but tribunal-rejected: extrap=%.3f ce=%.3f meta=%s"
                    % (sc["held_out_extrapolation"], sc["counterexample_accuracy"],
                       sc["metamorphic_pass"]))
            rows.append(row)
            if arm in ("CLOSED", "POSITIVE"):
                rows = rows * 1               # deterministic, one run suffices
                break
        qual = [r for r in rows if r["qualified"]]
        charges = [r["charges_to_solution"] for r in qual if r["charges_to_solution"]]
        results[arm] = {
            "recipients": len(rows),
            "M2_qualified_fraction": "%d/%d" % (len(qual), len(rows)),
            "M1_median_charges_to_qualified": (statistics.median(charges) if charges else None),
            "M1_charges_all": charges,
            "M3_median_tribunal_extrapolation": (
                statistics.median([r["tribunal"]["held_out_extrapolation"]
                                   for r in rows if r.get("tribunal")]) if rows else None),
            "M4_median_stress_200": (
                statistics.median([r["tribunal"]["stress_length_200"]
                                   for r in rows if r.get("tribunal")]) if rows else None),
            "M5_median_artifact_bytes": (
                statistics.median([r["artifact_bytes"] for r in rows
                                   if r.get("artifact_bytes")]) if rows else None),
            "rows": rows,
        }

    organ, scr_a, scr_b = results["ORGAN"], results["SCRATCH_A"], results["SCRATCH_B"]
    out = {
        "written_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "family": FAMILY,
        "organ_sha256": json.loads((HERE / "ORGAN_2026-09-22.json").read_text())["organ_sha256"],
        "escrow_per_recipient": BUDGET,
        "DIRECT_COMPETENCE_REUSE": "YES" if results["CLOSED"]["rows"][0]["qualified"] else "NO",
        "arms": {k: {m: v[m] for m in v if m != "rows"} for k, v in results.items()},
        "detail": results,
        "total_seconds": round(time.perf_counter() - t0, 1),
    }
    (HERE / "SLICE3_RESULTS_2026-09-22.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "detail"}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
