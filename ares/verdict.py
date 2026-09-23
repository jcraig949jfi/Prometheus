"""Apply the preregistered outcome rule (DESIGN_C0.md s4) to
runs/sweep_c0/summary.json. Deterministic; prints the per-world table
and writes runs/sweep_c0/verdict.json. The thresholds and directions
are copied from DESIGN_C0 s3/s4 verbatim; changing them here without a
dated addendum there is a protocol violation.

    python -m ares.verdict
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "runs", "sweep_c0")

THRESH = {  # (world, mode) -> threshold ; None = cannot exceed / at cap (INDETERMINATE for fitness)
    ("W1", "present"): 5.4, ("W1", "absent"): 5.4, ("W1", "shuffled"): 5.4,
    ("W2", "present"): 87.0, ("W2", "absent"): None, ("W2", "shuffled"): None,
    ("W3", "present"): 12.8, ("W3", "absent"): 14.2, ("W3", "shuffled"): None,
    ("W4", "present"): 8.0, ("W4", "absent"): 8.0, ("W4", "shuffled"): None,
    ("W5", "present"): 10.0, ("W5", "absent"): 10.0, ("W5", "shuffled"): None,
    ("W7", "present"): 57.6, ("W7", "absent"): 44.4, ("W7", "shuffled"): 49.7,
    ("W11", "present"): 10.0, ("W11", "absent"): 11.2, ("W11", "shuffled"): None,
    ("W12", "present"): 31.2, ("W12", "absent"): None, ("W12", "shuffled"): 20.2,
}
FLOOR = {"W1": 0.0, "W2": 60.0, "W3": 1.5, "W4": 0.0, "W5": 0.0, "W7": 49.5, "W11": 0.0, "W12": 19.0}


def _nan(x):
    return x is None or (isinstance(x, float) and x != x)


def cond_ii(world, pr, sh):
    """(ii): present probe differs from shuffled probe in the preregistered
    direction. Returns (present_ok, shuffled_not_ok, detail)."""
    if world == "W1":
        gp = pr["p_act_nodanger"] - pr["p_act_danger"]; gs = sh["p_act_nodanger"] - sh["p_act_danger"]
        return (not _nan(gp) and gp >= 0.2), (_nan(gs) or gs < 0.2), f"gap present {gp:.2f} shuffled {gs:.2f}"
    if world == "W2":
        gp = pr["p_risky_window"] - pr["p_risky_nowindow"]; gs = sh["p_risky_window"] - sh["p_risky_nowindow"]
        return (not _nan(gp) and gp >= 0.4), (_nan(gs) or gs < 0.4), f"gap present {gp:.2f} shuffled {gs:.2f}"
    if world == "W3":
        ok = (not _nan(pr["acc_post"]) and pr["acc_post"] >= 0.6 and pr["acc_pre"] >= 0.6)
        return ok, True, f"pre {pr['acc_pre']:.2f} post5 {pr['acc_post5']:.2f} post {pr['acc_post']:.2f}"
    if world == "W4":
        ok = pr["acc_late"] >= 0.65 and pr["acc_late_r0"] >= 0.55 and pr["acc_late_r1"] >= 0.55
        return ok, sh["acc_late"] < 0.65, f"late present {pr['acc_late']:.2f} (r0 {pr['acc_late_r0']:.2f} r1 {pr['acc_late_r1']:.2f}) shuffled {sh['acc_late']:.2f}"
    if world == "W5":
        ok = pr["dec_acc"] >= 0.7 and pr["dec_acc_pos"] >= 0.55 and pr["dec_acc_neg"] >= 0.55
        return ok, sh["dec_acc"] < 0.7, f"dec_acc present {pr['dec_acc']:.2f} (pos {pr['dec_acc_pos']:.2f} neg {pr['dec_acc_neg']:.2f}) shuffled {sh['dec_acc']:.2f}"
    if world == "W7":
        ok = pr["score_A"] >= 1.0 and pr["score_B"] >= 0.8
        return ok, True, f"A {pr['score_A']:.2f} B {pr['score_B']:.2f} (shuffled A {sh['score_A']:.2f} B {sh['score_B']:.2f})"
    if world == "W11":
        ok = pr["mean_commit_step"] >= 2 and pr["commit_acc"] >= 0.7
        return ok, sh["commit_acc"] < 0.7, f"commit step {pr['mean_commit_step']:.2f} acc {pr['commit_acc']:.2f} (shuffled step {sh['mean_commit_step']:.2f} acc {sh['commit_acc']:.2f})"
    if world == "W12":
        def slope(p):
            v = [x for x in p["p_risky_by_energy"] if not _nan(x)]
            return (v[0] - v[-1]) if len(v) >= 2 else float("nan")
        gp, gs = slope(pr), slope(sh)
        return (not _nan(gp) and gp >= 0.3), (_nan(gs) or gs < 0.15), f"low-high present {gp:.2f} shuffled {gs:.2f} bins {[round(x, 2) if not _nan(x) else None for x in pr['p_risky_by_energy']]}"
    return False, False, "n/a"


def main():
    s = json.load(open(os.path.join(OUT, "summary.json")))
    cells = s["cells"]
    verdict = {}
    lines = []
    for world in ["W1", "W2", "W3", "W4", "W5", "W7", "W11", "W12"]:
        rows = []
        i_ok = ii_ok = iii_ok = 0; absent_ok = 0; n = 0
        for sd in (1, 2, 3):
            pk, ak, sk = (f"main_{world}_{m}_s{sd}" for m in ("present", "absent", "shuffled"))
            if pk not in cells or sk not in cells:
                continue
            n += 1
            pc, sc = cells[pk], cells[sk]
            th = THRESH[(world, "present")]
            i = th is not None and pc["heldout"] >= th
            a_th = THRESH[(world, "absent")]
            a = ak in cells and a_th is not None and cells[ak]["heldout"] >= a_th
            ii_p, ii_s, detail = cond_ii(world, pc["probe"], sc["probe"])
            ii = ii_p and ii_s
            iii = pc.get("ablation", {}).get("n_load_bearing", 0) >= 1
            i_ok += i; ii_ok += ii; iii_ok += iii; absent_ok += a
            rows.append(dict(seed=sd, heldout=pc["heldout"], absent=cells.get(ak, {}).get("heldout"),
                             shuffled=sc["heldout"], i=bool(i), ii=bool(ii), iii=bool(iii), detail=detail,
                             load_bearing=pc.get("ablation", {}).get("n_load_bearing"), no_state=pc.get("ablation", {}).get("no_state"),
                             struct=pc["champ_struct"]))
        if n == 0:
            label = "NOT RUN"
        elif i_ok >= 2 and ii_ok >= 2 and iii_ok >= 2:
            label = "MATERIAL"
        elif i_ok < 2 and absent_ok >= 2:
            label = "DID NOTHING"
        elif i_ok < 2 and absent_ok < 2:
            label = "MERELY HARDER"
        elif i_ok >= 2 and ii_ok >= 2 and iii_ok < 2:
            label = "REFLEX (fitness+behaviour without a load-bearing node)"
        elif i_ok >= 2 and ii_ok < 2:
            label = "FITNESS WITHOUT THE BEHAVIOUR (ii fails)"
        else:
            label = "INDETERMINATE"
        verdict[world] = dict(label=label, i=i_ok, ii=ii_ok, iii=iii_ok, absent_above=absent_ok, eligible=n, rows=rows)
        lines.append(f"{world:4s} {label:52s} i {i_ok}/{n} ii {ii_ok}/{n} iii {iii_ok}/{n} absent>thr {absent_ok}/{n}")
        for r in rows:
            lines.append(f"     s{r['seed']} held {r['heldout']:8.2f} abs {r['absent'] if r['absent'] is None else round(r['absent'], 2)!s:>8} shuf {r['shuffled']:8.2f} "
                         f"i {int(r['i'])} ii {int(r['ii'])} iii {int(r['iii'])} lb {r['load_bearing']} nostate {r['no_state'] if r['no_state'] is None else round(r['no_state'], 2)} | {r['detail']}")
    txt = "\n".join(lines)
    print(txt)
    json.dump(verdict, open(os.path.join(OUT, "verdict.json"), "w"), indent=1)
    open(os.path.join(OUT, "verdict.txt"), "w").write(txt + "\n")


if __name__ == "__main__":
    main()
