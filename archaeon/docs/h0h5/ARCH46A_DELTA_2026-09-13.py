"""ARCH-46A deltas against S7, per state / per world, from the row files. For every state whose GATED_V2W cost changed
between S7 and ARCH-46A, the ROOT decision under the float form and the exact form is recomputed and the change is
ATTRIBUTED: 'float_tie_split' if the S7 float v2w split an exact tie at that root decision (or at the first differing
decision along any census trajectory), else 'UNATTRIBUTED' (to be investigated before the verdict is read).
Run from the repository root: python archaeon/docs/h0h5/ARCH46A_DELTA_2026-09-13.py"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from archaeon.producer import acquisition as AQ, fossil_inference as FI, s4_producers as P, s5_producers as O5, s6_endgame as S6, s7_gated as G7  # noqa: E402

HERE = Path(__file__).parent


def score(x, t):
    return sum(a == b for a, b in zip(x, t)) / len(t)


def v2w_float(L, S, q_int):
    D = O5._dist_matrix(L); row = D[q_int, S]; tot = 0.0; N = len(S)
    for e in np.unique(row):
        cell = S[row == e]; n = len(cell)
        if n == 1:
            continue
        M = D[:, cell]; counts = np.stack([(M == d).sum(1) for d in range(L + 1)], axis=1)
        tot += (n / N) * int((counts.astype(np.int64) ** 2).sum(1).min())
    return tot


def float_form_choice(E, si):
    """What the S7 (float) refinement would choose at E: G's exact-tie class re-ranked by float v2w, then lex."""
    st = AQ.feasible(E); L = st.length; S = S6.feasible_ints(E)
    st_, pool, vals = S6.g_pool_and_values(E, si); best = min(v.er_numerator for v in vals)
    adm = [v for v in vals if v.er_numerator == best]
    if len(adm) == 1:
        return adm[0].probe, False
    # S7 ranked by (ER numerator, -statistic, probe) with statistic = -v2w_float: i.e. SMALLER float v2w first, then lex
    scored = sorted(((v2w_float(L, S, O5._as_int(v.probe)), v.probe) for v in adm))
    exact = {}
    for v in adm:
        exact.setdefault(S6.v2w_num(L, S, O5._as_int(v.probe), {}), set()).add(v2w_float(L, S, O5._as_int(v.probe)))
    split = any(len(fs) > 1 for fs in exact.values())          # some exactly-equal group carried more than one float value
    return scored[0][1], split


def attribute(E0, targets, L, sid):
    """Walk every census trajectory under the EXACT candidate; at the first decision where the float form would have
    chosen differently, report whether that difference is a float tie split."""
    for t in targets:
        E = list(E0); k = 0
        while AQ.feasible(E).feasible_targets > 1 and k < 10:
            si = {"lane": "s6", "L": L, "world": sid, "arm": "G", "step": k + 1}
            p = G7.produce_gated_v2w(E, si)
            if p.extra["gate"]["active"]:
                fp, split = float_form_choice(E, si)
                if fp != p.probe:
                    return {"first_diff_snapshot": p.evidence_snapshot_id, "N": p.extra["gate"]["N"], "step": k + 1, "exact_choice": p.probe, "float_choice": fp, "attribution": "float_tie_split" if split else "UNATTRIBUTED"}
            E.append(FI.Fossil(p.probe, score(p.probe, t))); k += 1
    return {"attribution": "no_decision_differs_along_any_trajectory"}


def main():
    report = {"eligible": {}, "universe": {}, "L10": {}}
    for L in (8, 9):
        a = json.loads((HERE / f"S7_RESULTS_ELIGIBLE_L{L}_2026-09-13.json").read_text(encoding="utf-8")); b = json.loads((HERE / f"S7_RESULTS_ELIGIBLE_L{L}_ARCH46A_2026-09-13.json").read_text(encoding="utf-8"))
        ra = {r["eid"]: r for r in a["rows"]}; rb = {r["eid"]: r for r in b["rows"]}; uni = {s["eid"]: s for s in json.loads((HERE / f"S6_ENDGAME_UNIVERSE_L{L}_2026-09-13.json").read_text(encoding="utf-8"))}
        changed = []
        for eid in ra:
            ca, cb = ra[eid]["arms"]["GATED_V2W"]["cost"], rb[eid]["arms"]["GATED_V2W"]["cost"]; g = ra[eid]["arms"]["G"]["cost"]
            assert abs(g - rb[eid]["arms"]["G"]["cost"]) < 1e-9
            if abs(ca - cb) > 1e-9:
                fs = [FI.Fossil(x, y) for x, y in uni[eid]["fossils"]]; S = S6.feasible_ints(fs); targets = [O5._as_bits(int(x), L) for x in S]
                changed.append({"eid": eid, "N": ra[eid]["N"], "G": g, "S7": ca, "ARCH46A": cb, "V_star": ra[eid]["V_star"], "status_S7": ("worse" if ca > g + 1e-9 else ("better" if ca < g - 1e-9 else "same")), "status_46A": ("worse" if cb > g + 1e-9 else ("better" if cb < g - 1e-9 else "same")), **attribute(fs, targets, L, eid)})
        sa, sb = a["summary"], b["summary"]
        report["eligible"][str(L)] = {"states": sa["states"], "changed_states": changed, "S7": {k: sa[k] for k in ("improved", "unchanged", "worsened", "worsened_ids", "recovery", "aggregate_probe_reduction_rel", "C_median_units", "median_ratio", "C_max_units", "fired_fraction", "total_incremental_units")},
                                     "ARCH46A": {k: sb[k] for k in ("improved", "unchanged", "worsened", "worsened_ids", "recovery", "aggregate_probe_reduction_rel", "C_median_units", "median_ratio", "C_max_units", "fired_fraction", "total_incremental_units")},
                                     "S7_improvements_surviving": sum(1 for eid in ra if ra[eid]["arms"]["GATED_V2W"]["cost"] < ra[eid]["arms"]["G"]["cost"] - 1e-9 and rb[eid]["arms"]["GATED_V2W"]["cost"] < rb[eid]["arms"]["G"]["cost"] - 1e-9),
                                     "S7_improvements": sum(1 for eid in ra if ra[eid]["arms"]["GATED_V2W"]["cost"] < ra[eid]["arms"]["G"]["cost"] - 1e-9),
                                     "new_regressions": [eid for eid in rb if rb[eid]["arms"]["GATED_V2W"]["cost"] > rb[eid]["arms"]["G"]["cost"] + 1e-9 and not ra[eid]["arms"]["GATED_V2W"]["cost"] > ra[eid]["arms"]["G"]["cost"] + 1e-9],
                                     "identity_audit_46A": {k: (v if k != "violations" else len(v)) for k, v in b["identity_audit"].items()}}
    for name, fa, fb in (("universe", "S7_RESULTS_UNIVERSE_2026-09-13.json", "S7_RESULTS_UNIVERSE_ARCH46A_2026-09-13.json"), ("L10", "S7_RESULTS_L10_2026-09-13.json", "S7_RESULTS_L10_ARCH46A_2026-09-13.json")):
        a = json.loads((HERE / fa).read_text(encoding="utf-8")); b = json.loads((HERE / fb).read_text(encoding="utf-8"))
        ra = {r["root"]: r for r in a["rows"]}; rb = {r["root"]: r for r in b["rows"]}; changed = []
        for root in ra:
            ca, cb = ra[root]["arms"]["GATED_V2W"]["cost"], rb[root]["arms"]["GATED_V2W"]["cost"]; g = ra[root]["arms"]["G"]["cost"]
            if abs(ca - cb) > 1e-9:
                L = ra[root]["L"]
                if name == "universe":
                    w = {x["state_id"]: x for x in json.loads((HERE / f"S5_RESULTS_RUN2_L{L}_SLIM_2026-09-13.json").read_text(encoding="utf-8"))["worlds"]}[root]; fs = [FI.Fossil(x, y) for x, y in w["fossils"]]
                    S = S6.feasible_ints(fs); att = attribute(fs, [O5._as_bits(int(x), L) for x in S], L, root)
                else:
                    att = {"attribution": "L10 (lane s7): see rerun rows"}
                changed.append({"root": root, "N": ra[root]["N"], "G": g, "S7": ca, "ARCH46A": cb, "status_S7": ("worse" if ca > g + 1e-9 else ("better" if ca < g - 1e-9 else "same")), "status_46A": ("worse" if cb > g + 1e-9 else ("better" if cb < g - 1e-9 else "same")), **att})
        keys = [k for k in ("worsened_any", "worsened_ge_2pct", "worst_regression_rel", "improved_any", "improved_ge_2pct", "aggregate_cost_rel_to_G", "probes_saved_census", "fired_fraction", "C_median_units", "C_max_units", "total_incremental_units", "recovery_where_available", "gap_worlds", "canaries_all_pass") if k in a["summary"]]
        report[name] = {"changed": changed, "S7": {k: a["summary"][k] for k in keys}, "ARCH46A": {k: b["summary"][k] for k in keys}, "identity_audit_46A": {k: (v if k != "violations" else len(v)) for k, v in b["identity_audit"].items()}}
        if name == "universe":
            report[name]["canaries_46A"] = [{k: c[k] for k in ("root", "G_cost", "GATED_cost", "root_decision_equals_G", "S6_refinement_differed_at_root", "passes")} for c in b["summary"]["canaries"]]
            report[name]["root_decisions_changed_vs_S7"] = [root for root in ra if ra[root]["root_decision"]["GATED_V2W"] != rb[root]["root_decision"]["GATED_V2W"]]
    (HERE / "ARCH46A_DELTA_2026-09-13.json").write_text(json.dumps(report, indent=1, default=str), encoding="utf-8")
    print(json.dumps(report, indent=1, default=str))


if __name__ == "__main__":
    main()
