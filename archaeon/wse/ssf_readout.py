"""Readout of an SSF cycle (DESIGN_v0.2 s5): landscape by (cell, regime, branch), learning
curves and their slopes, derived efficiency measures, the strategy DISTRIBUTION of the final
elites (not only the winner), and the boundary map beside them.

    python -m archaeon.wse.ssf_readout --campaign ssf-c1
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from archaeon.wse.readout import load_rows, results_digest, disasm      # noqa: E402

LEDGERS = Path(__file__).resolve().parent / "ledgers"


def landscape(rows: List[dict]) -> str:
    by = defaultdict(list)
    for r in rows:
        by[(r["world"]["name"], r["economics"]["name"], r["organism"]["branch"])].append(r)
    lines = ["%-12s %-3s %-11s floor  held per seed          vocab per seed        Kdx2 per seed        persist/tape per seed          ops/ep        slope/10k        class per seed" % ("cell", "reg", "branch"),
             "-" * 200]
    for key in sorted(by):
        rs = sorted(by[key], key=lambda z: z["world"]["seed"])
        f = lambda k: " ".join("%.3f" % z["result"][k] for z in rs)
        lines.append("%-12s %-3s %-11s %.3f  %-22s %-22s %-20s %-30s %-13s %-16s %s" % (
            key[0], key[1], key[2], rs[0]["interpretation"]["F"], f("competence_heldout"), f("competence_heldout_vocab"),
            " ".join("%.3f" % z["result"]["competence_changed"]["Kd_x2"] for z in rs),
            " ".join("%s/%d" % (z["result"]["persist"][:4], z["result"]["tape_words"]) for z in rs),
            " ".join("%.0f" % z["result"]["ops_per_episode"] for z in rs),
            " ".join("%s" % (("%.3f" % z["result"]["learning_slope_per_10k"]) if z["result"]["learning_slope_per_10k"] is not None else "-") for z in rs),
            "/".join(z["interpretation"]["class"][:8] for z in rs)))
    return "\n".join(lines)


def curves(rows: List[dict]) -> str:
    lines = ["LEARNING CURVES (competence on the curve family vs cumulative episodes evaluated by the lineage; m_g = cost multiplier)"]
    for r in sorted(rows, key=lambda z: (z["world"]["name"], z["economics"]["name"], z["organism"]["branch"], z["world"]["seed"])):
        lc = r["result"]["learning_curve"]
        if not lc:
            continue
        pts = " ".join("%dk:%.2f(m%.1f)" % (p["experience_episodes"] // 1000, p["competence"], p["m_g"]) for p in lc)
        lines.append("%-12s %-3s %-11s s%d  %s" % (r["world"]["name"], r["economics"]["name"], r["organism"]["branch"], r["world"]["seed"], pts))
    return "\n".join(lines)


def geometry(rows: List[dict], min_held: float = 0.3) -> str:
    names = ["ERASE_ALL", "ERASE_REGS", "ERASE_TAPE", "SCRAMBLE_LOC", "SCRAMBLE_VAL", "SWAP_TWO", "HALVE_CAP", "RESET_IP", "TRANSPLANT"]
    lines = ["INTERVENTION GEOMETRY + CURVES (elites with held-out >= %.1f)" % min_held,
             "%-12s %-3s %-11s s held  ceil persist tape regs pw   " % ("cell", "reg", "branch") + " ".join("%-9s" % n[:9] for n in names) + " Kd-curve(0,4,8,16,32) delay(4,16,64,128) K(1,2,4,8)"]
    for r in sorted(rows, key=lambda z: (z["world"]["name"], z["economics"]["name"], z["organism"]["branch"], z["world"]["seed"])):
        res = r["result"]
        if res["competence_heldout"] < min_held:
            continue
        d = res["intervention_drop"]
        cv = res.get("curves") or {}
        kd = " ".join("%.2f" % cv["Kd"][k]["reward"] for k in sorted(cv.get("Kd", {}), key=int)) if cv else "-"
        dl = " ".join("%.2f" % cv["delay"][k] for k in sorted(cv.get("delay", {}), key=int)) if cv else "-"
        kk = " ".join("%.2f" % cv["K"][k] for k in sorted(cv.get("K", {}), key=int)) if cv and cv.get("K") else "-"
        lines.append("%-12s %-3s %-11s %d %.3f %.2f %-7s %-4d %-4d %-4d " % (
            r["world"]["name"], r["economics"]["name"], r["organism"]["branch"], r["world"]["seed"], res["competence_heldout"],
            res["erase_ceiling"], res["persist"], res["tape_words"], res["n_regs"], res["persistent_words"])
            + " ".join("%-9.3f" % d[n] for n in names) + " | " + kd + " | " + dl + " | " + kk)
    return "\n".join(lines)


def strategy_distribution(rows: List[dict]) -> str:
    """Directive: inspect the distribution of strategies, not only the winner. The final
    generation's persist-policy shares (from the trace) and the top-4 elites' manifests."""
    lines = ["STRATEGY DISTRIBUTION (final generation persist shares; top-4 elite tape/regs/budget)"]
    for r in sorted(rows, key=lambda z: (z["world"]["name"], z["economics"]["name"], z["organism"]["branch"], z["world"]["seed"])):
        last = r["trace"][-1]
        tops = " ".join("%s/%d/%d/%d" % (m["persist"][:4], m["tape_words"], m["n_regs"], m["tick_budget"]) for m in r["final_elite_manifests"])
        lines.append("%-12s %-3s %-11s s%d  shares %s  mean_reward %.3f  top4 %s" % (
            r["world"]["name"], r["economics"]["name"], r["organism"]["branch"], r["world"]["seed"],
            json.dumps(last["persist_shares"]), last["mean_reward"], tops))
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign", default="ssf-c1")
    a = ap.parse_args(argv)
    rows = load_rows(a.campaign)
    out = LEDGERS / a.campaign
    txt = "rows: %d   results_digest (timing-free): %s\n\n" % (len(rows), results_digest(rows))
    txt += landscape(rows) + "\n\n" + geometry(rows) + "\n\n" + curves(rows) + "\n\n" + strategy_distribution(rows) + "\n"
    (out / "LANDSCAPE.txt").write_text(txt, encoding="utf-8", newline="\n")
    print(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
