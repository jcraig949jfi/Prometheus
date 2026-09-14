"""Descriptive readout of S5 result files (rows -> tables). The verdict itself is computed only by S5_RUNNER::evaluate
under the frozen rule; everything printed here is descriptive and labelled as such.
Usage: python S5_ANALYSIS_2026-09-13.py S5_RESULTS_RUN2_L8_2026-09-13.json [S5_RESULTS_RUN2_L9_2026-09-13.json ...]"""
import json, sys
from collections import defaultdict
from pathlib import Path


def load(paths):
    worlds = []; rows = []; meta = []
    for p in paths:
        r = json.loads(Path(p).read_text(encoding="utf-8")); worlds += r["worlds"]; rows += r["decision_states"]
        meta.append({"file": p, "verdict": r["verdict"], "failures": r["instrument_failures"], "elapsed_s": r.get("elapsed_s"), "versions": r["producer_versions"]})
    return worlds, rows, meta


def main(paths):
    worlds, rows, meta = load(paths)
    for m in meta:
        print("FILE", m["file"], "| frozen-rule verdict:", m["verdict"], "| failures:", m["failures"], "| elapsed %.0f s" % (m["elapsed_s"] or 0), "| versions", m["versions"])
    arms = list(worlds[0]["summary"].keys()); n = len(worlds); tot_targets = sum(w["N"] for w in worlds)
    print("states", n, "targets", tot_targets, "arms", arms)
    print("\n== world level: mean E[probes] (census-weighted and state-mean), relative advantage over G, states separated at the bar (>= 2 % and more target wins), states worse than G at the bar")
    for a in arms:
        Ew = sum(w["summary"][a]["E_probes"] * w["N"] for w in worlds) / tot_targets; Es = sum(w["summary"][a]["E_probes"] for w in worlds) / n
        if a == "G":
            print("  %-3s E_target-weighted %.4f  E_state-mean %.4f" % (a, Ew, Es)); continue
        rel = [w["pairs_vs_G"][a]["rel_advantage_over_G"] for w in worlds]; sep = sum(w["pairs_vs_G"][a]["separated_at_bar"] for w in worlds); worse = sum(1 for x in rel if x <= -0.02)
        wins = sum(w["pairs_vs_G"][a]["arm_wins"] for w in worlds); losses = sum(w["pairs_vs_G"][a]["G_wins"] for w in worlds)
        print("  %-3s E_target-weighted %.4f  E_state-mean %.4f  mean rel vs G %+.4f  separated %3d/%d  worse-at-bar %3d  target wins/losses vs G %d/%d  compute %.1f s  O-calls %d/%d  exhausted %d scope %d" % (
            a, Ew, Es, sum(rel) / n, sep, n, worse, wins, losses, sum(w["summary"][a]["compute_s"] for w in worlds), sum(w["summary"][a]["o_calls"] for w in worlds), sum(w["summary"][a]["proposals"] for w in worlds),
            sum(w["summary"][a]["budget_exhausted"] for w in worlds), sum(w["summary"][a]["scope_exceeded"] for w in worlds)))
    print("\n== O vs G by state size and family (where does the exact optimum beat the real G?)")
    by = defaultdict(list)
    for w in worlds:
        key = (w["family"], "N<=8" if w["N"] <= 8 else ("N<=16" if w["N"] <= 16 else "N>16")); by[key].append(w["pairs_vs_G"]["O"])
    for k in sorted(by):
        v = by[k]; print("  %-6s %-6s states %3d  separated %3d  mean rel %+.4f  max rel %+.4f" % (k[0], k[1], len(v), sum(x["separated_at_bar"] for x in v), sum(x["rel_advantage_over_G"] for x in v) / len(v), max(x["rel_advantage_over_G"] for x in v)))
    print("\n== root coordinates vs O-beats-G (state level; descriptive)")
    for c in ("two_block_proxy", "entropy_disagreement"):
        for val in (True, False):
            ws = [w for w in worlds if bool(w["root_coordinates"].get(c)) == val]
            if ws: print("  %-20s=%-5s states %3d  O separated %3d (%.2f)  mean rel %+.4f" % (c, val, len(ws), sum(w["pairs_vs_G"]["O"]["separated_at_bar"] for w in ws), sum(w["pairs_vs_G"]["O"]["separated_at_bar"] for w in ws) / len(ws), sum(w["pairs_vs_G"]["O"]["rel_advantage_over_G"] for w in ws) / len(ws)))
    for c, thr in (("entropy_deficit_bits", 1e-9), ("two_step_gap", 1e-9)):
        ws = [w for w in worlds if w["root_coordinates"].get(c, 0) > thr]; wn = [w for w in worlds if not w["root_coordinates"].get(c, 0) > thr]
        for lab, s in (("> 0", ws), ("= 0", wn)):
            if s: print("  %-20s%-5s states %3d  O separated %3d (%.2f)  mean rel %+.4f" % (c, lab, len(s), sum(w["pairs_vs_G"]["O"]["separated_at_bar"] for w in s), sum(w["pairs_vs_G"]["O"]["separated_at_bar"] for w in s) / len(s), sum(w["pairs_vs_G"]["O"]["rel_advantage_over_G"] for w in s) / len(s)))
    print("\n== decision-state audit (G's own choices; exact delta = Q*(s, g) - V*(s))")
    g = [r for r in rows if r["arm"] == "G"]; base = sum(r["myopic_exact"] for r in g) / len(g)
    print("  decision states %d  myopic %.3f  mean delta %.4f" % (len(g), base, sum(r["delta"] for r in g) / len(g)))
    for k in ("kappa_H", "kappa_tie", "kappa_proxy", "pool_suboptimal"):
        pos = [r for r in g if r[k]]; neg = [r for r in g if not r[k]]; tp = sum(r["myopic_exact"] for r in pos); fn = sum(r["myopic_exact"] for r in neg)
        print("  %-16s fires %4d (%.3f)  precision %.3f  recall %.3f  lift x%.2f  mean delta on/off %.4f/%.4f" % (k, len(pos), len(pos) / len(g), tp / len(pos) if pos else float("nan"), tp / (tp + fn) if tp + fn else float("nan"), (tp / len(pos)) / base if pos and base else float("nan"), sum(r["delta"] for r in pos) / len(pos) if pos else float("nan"), sum(r["delta"] for r in neg) / len(neg) if neg else float("nan")))
    byd = defaultdict(list)
    for r in g: byd[r["step"]].append(r["myopic_exact"])
    print("  myopia by depth:", {d: "%d/%d" % (sum(v), len(v)) for d, v in sorted(byd.items())})
    byN = defaultdict(list)
    for r in g: byN["N<=4" if r["N"] <= 4 else ("N<=8" if r["N"] <= 8 else ("N<=16" if r["N"] <= 16 else "N>16"))].append(r["myopic_exact"])
    print("  myopia by |T| at the decision:", {d: "%d/%d=%.2f" % (sum(v), len(v), sum(v) / len(v)) for d, v in sorted(byN.items())})
    print("\n== compute accounting (seconds summed over proposals; O work units are fresh DP evaluations)")
    for a in arms:
        print("  %-3s compute %8.1f s  proposals %6d  work_units %d" % (a, sum(w["summary"][a]["compute_s"] for w in worlds), sum(w["summary"][a]["proposals"] for w in worlds), sum(w["summary"][a]["work_units"] for w in worlds)))
    print("\n== POST-HOC (not the preregistered verdict): the same rows under the remaining clauses if the failing clause is set aside")
    o_sep = sum(w["pairs_vs_G"]["O"]["separated_at_bar"] for w in worlds) / n; o_mean = sum(w["pairs_vs_G"]["O"]["rel_advantage_over_G"] for w in worlds) / n
    posH = [r for r in g if r["kappa_H"]]; tp = sum(r["myopic_exact"] for r in posH); fn = sum(r["myopic_exact"] for r in g if not r["kappa_H"])
    prec = tp / len(posH) if posH else 0; rec = tp / (tp + fn) if tp + fn else 0
    rh_sep = sum(w["pairs_vs_G"]["RH"]["separated_at_bar"] for w in worlds) / n; rh_frac = sum(w["summary"]["RH"]["o_calls"] for w in worlds) / max(1, sum(w["summary"]["RH"]["proposals"] for w in worlds))
    print("  O separates: frac %.3f (>= 1/3?) mean rel %.4f (>= 0.02?) -> %s" % (o_sep, o_mean, o_sep >= 1 / 3 or o_mean >= 0.02))
    print("  kappa_H routes: precision %.3f (>= 0.5?) recall %.3f (>= 0.5?) RH separated frac %.3f (>= 1/3?) O-call frac %.3f (<= 0.5?) -> %s" % (prec, rec, rh_sep, rh_frac, prec >= 0.5 and rec >= 0.5 and rh_sep >= 1 / 3 and rh_frac <= 0.5))


if __name__ == "__main__":
    main(sys.argv[1:])
