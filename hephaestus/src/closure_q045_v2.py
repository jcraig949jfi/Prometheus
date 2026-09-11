"""Specimen 3 instrument characterization v2 -- TRUE ring change on the shift column (Z7).

Operator ruling 1 (2026-09-11): reruns of Q045 are instrument-characterization experiments, never
replacements for the frozen result. This module changes ONE thing relative to closure_q045 (v1, the
run of record): the 300 shift points (entries 0..6, seed 20260901, identical to v1) are evaluated
under Z7 arithmetic -- both the target's certified program and every candidate -- instead of Z6.
v1's shift folded entry 6 onto 0 (mod 6), so it tested alphabet extension only; v2 tests whether a
witness relies on a Z6 identity (e.g. x^3 = x mod 6, 2x = -4x mod 6) that does not hold in a field.

Search and exhaustive columns are untouched (Z6); mechanism-bearing status therefore cannot change.
Only `robust` can. Preregistration: hephaestus/prereg/PREREG_Q045_v2_Z7_2026-09-11.md.
Output: hephaestus/closure_results/q045_lost_class_v2_Z7.json (v1's file is never written here).
"""
from __future__ import annotations

import contextlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "aporia" / "lot"))
import world3 as W  # noqa: E402
from hephaestus.src import closure_q045 as V1  # noqa: E402

SHIFT_MOD = 7


class SpecZ7(V1.Spec):
    @contextlib.contextmanager
    def shift_context(self):
        saved = W.MOD
        W.MOD = SHIFT_MOD
        try:
            yield
        finally:
            W.MOD = saved


def run(deep_size=8, deep_candidates=30_000_000):
    r = V1.run(deep_size, deep_candidates, spec_cls=SpecZ7, out_name="q045_lost_class_v2_Z7.json",
               prereg="hephaestus/prereg/PREREG_Q045_v2_Z7_2026-09-11.md")
    # v2 comparison against the frozen v1 rows (same targets by construction: same enumerator, same order)
    v1_path = ROOT / "hephaestus" / "closure_results" / "q045_lost_class.json"
    cmp = {"v1_file": str(v1_path.relative_to(ROOT)), "targets_identical": None, "mech_identical": None, "robust_changes": []}
    if v1_path.exists():
        v1 = json.loads(v1_path.read_text(encoding="utf-8"))
        same_t = [a["certified_full_program"] for a in v1["targets"]] == [b["certified_full_program"] for b in r["targets"]]
        cmp["targets_identical"] = same_t
        if same_t:
            mech_same = True
            for a, b in zip(v1["targets"], r["targets"]):
                for arm in ("A0", "A2", "B", "C"):
                    ma = [w.split(" (d")[0] for w in a["arms"][arm]["mech"]]; mb = [w.split(" (d")[0] for w in b["arms"][arm]["mech"]]
                    if ma != mb or a["arms"][arm]["n_alias"] != b["arms"][arm]["n_alias"]:
                        mech_same = False
                    if a["arms"][arm]["n_robust"] != b["arms"][arm]["n_robust"]:
                        cmp["robust_changes"].append({"target": a["certified_full_program"], "arm": arm,
                                                      "v1_robust": a["arms"][arm]["n_robust"], "v2_robust": b["arms"][arm]["n_robust"],
                                                      "v2_witnesses": b["arms"][arm]["mech"]})
            cmp["mech_identical"] = mech_same
    r["v1_comparison"] = cmp
    out = ROOT / "hephaestus" / "closure_results" / "q045_lost_class_v2_Z7.json"
    out.write_text(json.dumps(r, indent=2, default=str), encoding="utf-8")
    return r


if __name__ == "__main__":
    from hephaestus.workspace_guard import refuse_canonical  # D-23
    refuse_canonical("specimen 3 v2 (Z7 shift)")
    ds = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    dc = int(sys.argv[2]) if len(sys.argv) > 2 else 30_000_000
    r = run(ds, dc)
    print(json.dumps({k: r[k] for k in ("closure_sizes", "summary", "predictions", "v1_comparison")}, indent=1, default=str))
