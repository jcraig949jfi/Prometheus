"""Cycle-4 reconciler notes, part E: P-F05 (protocol x geometry), P-F06 (replication), P-F04 (price 0)."""
from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import looprun as L            # noqa: E402
import recordsafety as RS      # noqa: E402

EXP = HERE.parent / "experiments"


def main():
    L.append_evidence("T-E06", "P-F05", "RECONCILER: the exclusion window is REAL BUT NOT FIXED. From scratch (f0 .1, 120 gens, new ids) rare TREE fails only at .55 (1/3 gains); pre-adapted TAPE residents exclude invading TREE at .65 (0/3) and .70 (1/3); P-E06 (other ids, 160 gens) put it at .6-.7. The two protocols disagree on the direction at 3/7 rates; TAPE invades a pre-adapted TREE resident in 0-2/3 cells at every rate and mutual invasibility appears in 2/21 cells (.55, .80). GEOMETRY x RATE: with graph targets (phi 0) TREE dominates from .1 at every rate; at phi .5 and phi 1 (legacy tree-native items) the sign flips to TAPE in 2-3 of 6 rates with no monotone pattern. Reading: geometry (T-X04) is a portable coordinate of direction; the recombination rate acts through a window whose position moves with attempt id, protocol and run length - a local, not a portable, structure.", True,
                      state="ACTIVE", state_reason="continuation: window position vs attempt id (6 ids at .05 steps) to read whether it is target-dependent; geometry x rate x price")
    L.append_evidence("T-X14", "P-F05", "RECONCILER: 'the rate sets direction' is BROKEN as a portable claim; the rate window exists in every protocol but its location is not reproducible across ids (.55 / .6-.7 / .65-.7).", True)
    L.append_evidence("T-X04", "P-F05", "RECONCILER: target geometry flips the direction map (phi 0: TREE everywhere; phi .5 / 1: TAPE at 2-3 of 6 rates) - the geometry axis survives crossing with rate; CROSS_WORLD within e06.", True)
    p6 = EXP / "cw01-arch4" / "P-F06" / "RESULT.json"
    if p6.exists():
        r = json.loads(p6.read_text(encoding="utf-8"))
        dose = r["generation_dose"]
        L.append_evidence("T-ARCH4/M1", "P-F06", "RECONCILER (6 seeds, competent neutral-band drift control; final reward select %s vs ndrift %s): %s - seeds holding the promotion rule at G60: %s; generation dose (loss select / ndrift, seeds select<anc, seeds ndrift<anc): %s; ndrift moves loss vs ancestors in %d seeds; ancestor loss %s; ancestors surviving %s. The selection effect on damage loss is %s."
                          % ({k: round(v, 2) for k, v in r["final_reward_mean"].items() if k.startswith("select")}, {k: round(v, 2) for k, v in r["final_reward_mean"].items() if k.startswith("ndrift")}, r["reading"], r["seeds_holding"],
                             {g: (round(v["loss_select"], 3) if v["loss_select"] is not None else None, round(v["loss_ndrift"], 3) if v["loss_ndrift"] is not None else None, v["seeds_select_below_anc"], v["seeds_ndrift_below_anc"]) for g, v in dose.items()},
                             r["ndrift_moves_vs_ancestor_seeds"], round(r["anc_loss_mean"], 3) if r["anc_loss_mean"] is not None else None, r["ancestors_surviving"],
                             "REPLICATED against a competent control" if r["reading"] == "SELECTED_REPLICATED" else "NOT PROMOTED (the paired ancestor contrast and the control contrast do not both hold in >= 4/6 seeds)"), bool(r["material"]),
                          state="ACTIVE", state_reason="promotion decided by the preregistered 4/6 rule; see reading")
    p4 = EXP / "cw01-loop4" / "P-F04" / "RESULT.json"
    if p4.exists():
        r = json.loads(p4.read_text(encoding="utf-8"))
        s = r["pruning_signature"]
        L.append_evidence("T-X16", "P-F04", "RECONCILER (none == sham %s): decision %s. Pruning signature (final240 TREE: tree-damaged minus tape-damaged, paired over 3 ids x 5 rates x 3 fractions) at price .01: %+.3f (above p95 %s); at price 0: %+.3f (above p95 %s, below p05 %s). Damage-minus-none by price and fraction: %s. Rate-window signs (undamaged) at price .01 %s vs price 0 %s. Coexistence at 240 by regime: %s."
                          % (r["harness_none_equals_sham"], r["decision"], s["0.010"]["mean"], s["0.010"]["above_p95"], s["0.000"]["mean"], s["0.000"]["above_p95"], s["0.000"]["below_p05"],
                             {p: {k: (round(v["mean"], 3), v["above_p95"], v["below_p05"]) for k, v in e.items()} for p, e in r["damage_minus_none"].items()},
                             {k: v for k, v in r["window_signs_none"]["0.010"].items() if k != "finals"}, {k: v for k, v in r["window_signs_none"]["0.000"].items() if k != "finals"}, r["coexist240"]), bool(r["material"]),
                          state="ACTIVE", state_reason="the sign of damage under price 0 is now on record: %s" % r["decision"])
        L.append_evidence("T-E07", "P-F04", "cross: 'damage robustness' in e06 reads %s under price 0 (signature %+.3f) vs %+.3f under the price." % (r["decision"], s["0.000"]["mean"], s["0.010"]["mean"]), bool(r["material"]))
    for f in (HERE / "EVIDENCE.jsonl", HERE / "STATE.jsonl"):
        RS.require_ascii_safe(f)
    print("notes E appended")


if __name__ == "__main__":
    main()
