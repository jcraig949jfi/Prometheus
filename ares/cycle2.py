"""Ares cycle-2 driver: ATTACK THE MECHANISM (DESIGN_C2.md).
Resumable; one JSON per run; progress.log written from Python.

    python -m ares.cycle2 runs       # 180 GA runs, seeds 201-210
    python -m ares.cycle2 dissect    # edge/SCC-aware carrier ablation
    python -m ares.cycle2 battery    # Q1 causal battery (no GA)
    python -m ares.cycle2 graft      # Q3 transplant + carrier swap
    python -m ares.cycle2 gates      # the stopping-rule gates (s8)
    python -m ares.cycle2 all
"""
from __future__ import annotations

import json
import os
import sys
import time
from collections import Counter

import numpy as np

from . import carriers as C
from . import search as R
from . import substrate as S

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "runs", "sweep_c2")
SEEDS = list(range(201, 211))
P, G, EPS = 128, 120, 4

Q1_ARMS = {
    "c1_all": {},
    "c1_only_recur": dict(allow_keep=False, allow_plasticity=False),
    "c1_only_keep": dict(forbid_recurrence=True, allow_plasticity=False),
    "c1_only_plast": dict(allow_keep=False, forbid_recurrence=True),
    "c1_none": dict(allow_keep=False, allow_plasticity=False, forbid_recurrence=True),
}
Q2_ARMS = {
    "c2_no_selfloop": dict(forbid_self_loops=True),
    "c2_no_recur": dict(forbid_recurrence=True),
    "c2_tax_low": {},
    "c2_tax_high": {},
    "c2_keep_subsidy": dict(keep_mut_weight=8.0),
    "c2_recur_unstable": dict(recur_mut_noise=0.5),
}
TAX = {"c2_tax_low": 0.05, "c2_tax_high": 0.25}
HOSTILE = ["W14", "W15", "W16"]
CAP = {"W4": 40.0, "W14": 40.0, "W15": 40.0, "W16": 10.0}
THRESH = {w: 0.2 * c for w, c in CAP.items()}
FLOOR = 0.0
SEEDSETS = {}


def _log(msg):
    os.makedirs(OUT, exist_ok=True)
    line = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + " " + msg
    print(line, flush=True)
    with open(os.path.join(OUT, "progress.log"), "a") as f:
        f.write(line + "\n")


def _path(n):
    return os.path.join(OUT, n + ".json")


def _save(n, o):
    tmp = _path(n) + ".tmp"
    json.dump(o, open(tmp, "w"))
    os.replace(tmp, _path(n))


def _load(n):
    return json.load(open(_path(n)))


def seeds_for(w, mode):
    k = (w, mode)
    if k not in SEEDSETS:
        SEEDSETS[k] = R.balanced_seeds_for(R.make_world(w, mode), start=40_000)
    return SEEDSETS[k]


def _job(name, fn):
    if os.path.exists(_path(name)):
        return
    t0 = time.time()
    out = fn()
    _save(name, out)
    _log(f"{name}: heldout {out['final']['heldout']:.2f} in {time.time() - t0:.1f}s")


def arm_world(name):
    """(world, mode) an arm was run in."""
    if name.startswith("W1"):
        w, mode = name.split("_")[0], name.split("_")[1]
        return w, mode
    if name.startswith("c1_shuffled_ref"):
        return "W4", "shuffled"
    return "W4", "present"


# ----------------------------------------------------------------------
def phase_runs():
    for arm, kw in list(Q1_ARMS.items()) + list(Q2_ARMS.items()):
        cfg = S.Config(**kw)
        tax = TAX.get(arm, 0.0)
        for sd in SEEDS:
            _job(f"{arm}_s{sd}", lambda cfg=cfg, sd=sd, tax=tax: R.run(
                "W4", "present", cfg, P, G, EPS, sd, tag="c2",
                eval_seeds=seeds_for("W4", "present"), snapshots=True, recur_tax=tax))
    cfg = S.Config()
    for sd in SEEDS:
        _job(f"c1_shuffled_ref_s{sd}", lambda sd=sd: R.run(
            "W4", "shuffled", cfg, P, G, EPS, sd, tag="c2ref",
            eval_seeds=seeds_for("W4", "shuffled")))
    for w in HOSTILE:
        for mode in ("present", "shuffled"):
            for sd in SEEDS:
                _job(f"{w}_{mode}_s{sd}", lambda w=w, mode=mode, sd=sd: R.run(
                    w, mode, cfg, P, G, EPS, sd, tag="c2hostile",
                    eval_seeds=seeds_for(w, mode), snapshots=(mode == "present")))


# ----------------------------------------------------------------------
def probe(genome, w, mode):
    """Late-life accuracy by regime on the paying steps. W16 pays only in
    the last 10 steps; the W4 family pays every step."""
    pop = S.Population.from_genomes([genome])
    world = R.make_world(w, mode)
    _, tr = R.rollout(pop, world, seeds_for(w, mode), record=True)
    A = np.stack(tr["actions"])[:, :, 0]
    r = np.array([ep[0]["regime"] for ep in tr["info"]])
    good = (A == (r[:, None] + 1))
    pay = slice(world.T - 10, world.T) if w == "W16" else slice(10, world.T)
    return dict(acc_late=float(good[:, pay].mean()),
                acc_late_r0=float(good[r == 0, pay].mean()), acc_late_r1=float(good[r == 1, pay].mean()),
                p_abstain=float((A[:, pay] == 0).mean()))


def phase_dissect():
    names = sorted(f[:-5] for f in os.listdir(OUT) if f.endswith(".json") and "_s" in f
                   and not any(f.endswith(x) for x in ("_dissect.json", "_graft.json")))
    for name in names:
        if os.path.exists(_path(name + "_dissect")):
            continue
        res = _load(name)
        arm = name.rsplit("_s", 1)[0]
        w, mode = arm_world(arm)
        g = res["final"]["genome"]
        s = seeds_for(w, mode)
        d = C.carrier_ablation(g, w, mode, s, floor=FLOOR)
        d["probe"] = probe(g, w, mode)
        d["heldout"] = res["final"]["heldout"]
        d["arm"] = arm
        d["world"] = w
        d["mode"] = mode
        thr = THRESH[w]
        d["above_threshold"] = bool(res["final"]["heldout"] >= thr)
        d["time_to_threshold"] = next((row["gen"] for row in res["log"] if row["champ_heldout"] >= thr), None)
        _save(name + "_dissect", d)
        _log(f"dissect {name}: held {d['heldout']:.2f} class {d['carrier_class']} "
             f"self {d['inventory']['self_loops']} rec {d['inventory']['recurrent_edges']} "
             f"keep {d['inventory']['keep_nodes']} plast {d['inventory']['plastic_edges']} ttt {d['time_to_threshold']}")


# ----------------------------------------------------------------------
def phase_battery():
    if not os.path.exists(_path("battery")):
        out = {}
        out["opportunity_default"] = C.opportunity(S.Config(), n_trials=6000, seed=11)
        out["opportunity_keep_subsidy"] = C.opportunity(S.Config(keep_mut_weight=8.0), n_trials=6000, seed=12)
        out["opportunity_no_recur"] = C.opportunity(S.Config(forbid_recurrence=True), n_trials=3000, seed=13)
        grads = []
        s = seeds_for("W4", "present")
        for sd in SEEDS[:5]:
            p = _path(f"c1_all_s{sd}")
            if os.path.exists(p):
                g = _load(f"c1_all_s{sd}")["final"]["genome"]
                grads.append(dict(seed=sd, **C.single_mutation_gradient(g, "W4", "present", s, floor=FLOOR, n=300, seed=sd)))
        out["gradient"] = grads
        # robustness + cost of each arm's champions
        rob = []
        for arm in list(Q1_ARMS) + list(Q2_ARMS):
            for sd in SEEDS:
                p = _path(f"{arm}_s{sd}_dissect")
                if not os.path.exists(p):
                    continue
                d = _load(f"{arm}_s{sd}_dissect")
                g = _load(f"{arm}_s{sd}")["final"]["genome"]
                pop = S.Population.from_genomes([g])
                row = dict(arm=arm, seed=sd, heldout=d["heldout"], carrier_class=d["carrier_class"],
                           ttt=d["time_to_threshold"], n_edges=d["inventory"]["n_edges"],
                           n_hidden=d["inventory"]["n_hidden"], rec_edges=d["inventory"]["recurrent_edges"])
                for w in ("W14", "W15"):
                    row["on_" + w] = float(R.rollout(pop, R.make_world(w, "present"), seeds_for(w, "present"))[0])
                rob.append(row)
        out["robustness_cost"] = rob
        _save("battery", out)
        _log("battery written")


# ----------------------------------------------------------------------
def phase_graft():
    """Q3: edge-aware transplant of each champion's carrier into naive
    hosts, and carrier SWAP between independently evolved lineages."""
    cfg = S.Config()
    s = seeds_for("W4", "present")
    champs = []
    for sd in SEEDS:
        p = _path(f"c1_all_s{sd}_dissect")
        if not os.path.exists(p):
            continue
        d = _load(f"c1_all_s{sd}_dissect")
        g = _load(f"c1_all_s{sd}")["final"]["genome"]
        nodes = sorted({x for comp in d["inventory"]["scc_nodes"] for x in comp})
        champs.append(dict(seed=sd, genome=g, nodes=nodes, dissect=d))
    for ch in champs:
        name = f"c1_all_s{ch['seed']}_graft"
        if os.path.exists(_path(name)) or not ch["nodes"]:
            continue
        t = C.transplant(ch["genome"], ch["nodes"], "W4", "present", s, cfg, floor=FLOOR, seed=ch["seed"])
        _save(name, t)
        _log(f"transplant s{ch['seed']}: evolved {t['evolved_mean']:.2f} random {t['random_mean']:.2f} "
             f"top10 {t['evolved_top10']:.2f}/{t['random_top10']:.2f} portable {t['portable']}")
    if not os.path.exists(_path("swaps")):
        rows = []
        for a in champs:
            for b in champs:
                if a["seed"] == b["seed"] or not (a["nodes"] and b["nodes"]):
                    continue
                r = C.swap(a["genome"], b["genome"], a["nodes"], b["nodes"], "W4", "present", s, floor=FLOOR, seed=a["seed"])
                rows.append(dict(host=a["seed"], donor=b["seed"], **r))
        _save("swaps", rows)
        rec = [r["recovery_fraction"] for r in rows if r["recovery_fraction"] is not None]
        _log(f"swaps: {len(rows)} pairs, median recovery {np.median(rec) if rec else float('nan'):.2f}")


# ----------------------------------------------------------------------
def _arm_rows(arm):
    rows = []
    for sd in SEEDS:
        p = _path(f"{arm}_s{sd}_dissect")
        if os.path.exists(p):
            rows.append(_load(f"{arm}_s{sd}_dissect"))
    return rows


def phase_gates():
    lines, summary = [], {}
    all_arms = list(Q1_ARMS) + list(Q2_ARMS) + [f"{w}_present" for w in HOSTILE] + [f"{w}_shuffled" for w in HOSTILE] + ["c1_shuffled_ref"]
    for arm in all_arms:
        rows = _arm_rows(arm)
        if not rows:
            continue
        w, mode = arm_world(arm)
        above = [r for r in rows if r["above_threshold"]]
        cls = Counter(r["carrier_class"] for r in above)
        maj = cls.most_common(1)[0] if cls else ("(none)", 0)
        ttt = [r["time_to_threshold"] for r in above if r["time_to_threshold"] is not None]
        summary[arm] = dict(world=w, mode=mode, n=len(rows), above=len(above), threshold=THRESH[w],
                            heldout=[round(r["heldout"], 2) for r in rows],
                            median_heldout=float(np.median([r["heldout"] for r in rows])),
                            classes=dict(cls), majority=list(maj),
                            median_ttt=float(np.median(ttt)) if ttt else None,
                            median_rec_edges=float(np.median([r["inventory"]["recurrent_edges"] for r in rows])),
                            median_keep_nodes=float(np.median([r["inventory"]["keep_nodes"] for r in rows])),
                            median_plastic=float(np.median([r["inventory"]["plastic_edges"] for r in rows])),
                            acc_late=[round(r["probe"]["acc_late"], 2) for r in rows])
        lines.append(f"{arm:20s} {w}/{mode:8s} above {len(above):2d}/{len(rows):2d} med {summary[arm]['median_heldout']:6.2f} "
                     f"ttt {summary[arm]['median_ttt']} classes {dict(cls)} rec {summary[arm]['median_rec_edges']:.1f} "
                     f"keep {summary[arm]['median_keep_nodes']:.1f} plast {summary[arm]['median_plastic']:.1f}")

    bat = _load("battery") if os.path.exists(_path("battery")) else {}
    # ---- GATE A: substitution / new carrier
    gate_a, a_detail = False, []
    for arm in list(Q2_ARMS) + [f"{w}_present" for w in HOSTILE]:
        s_ = summary.get(arm)
        if not s_:
            continue
        maj_cls, maj_n = s_["majority"]
        if s_["above"] >= 5 and maj_n >= 5 and maj_cls != "RECUR":
            gate_a = True
            a_detail.append(f"{arm}: {maj_n}/10 above-threshold champions are {maj_cls}")
    new_carrier = [arm for arm in summary if summary[arm]["classes"].get("NONE", 0) >= 5 and summary[arm]["above"] >= 5]
    # ---- GATE B: causal explanation
    ok = summary.get("c1_only_keep", {}).get("above", 0)
    p_rec = bat.get("opportunity_default", {}).get("p_create", {}).get("recurrent")
    p_keep = bat.get("opportunity_default", {}).get("p_create", {}).get("keep")
    grads = bat.get("gradient", [])
    def gmean(k):
        v = [g[k]["mean"] for g in grads if g.get(k, {}).get("mean") is not None]
        return float(np.mean(v)) if v else None
    g_rec, g_keep = gmean("recur"), gmean("keep")
    rec_ok = summary.get("c1_only_recur", {}).get("above", 0)
    if rec_ok < 7:
        # the apparatus itself failed: no conclusion about either carrier
        verdict_b = "UNDECIDED (only_recur arm did not reach threshold)"
        gate_b = False
    elif ok < 5:
        verdict_b = "SUPERIORITY"
        gate_b = True
    elif ok >= 7 and ((p_rec is not None and p_keep is not None and p_rec > p_keep)
                      or (g_rec is not None and g_keep is not None and g_rec - g_keep >= 2.0)):
        verdict_b = "ACCESSIBILITY"
        gate_b = True
    else:
        verdict_b = "MIXED/UNDECIDED"
        gate_b = False
    # ---- GATE C: transplantable
    ports = [_load(f"c1_all_s{sd}_graft")["portable"] for sd in SEEDS if os.path.exists(_path(f"c1_all_s{sd}_graft"))]
    swaps = _load("swaps") if os.path.exists(_path("swaps")) else []
    host_best = {}
    for r in swaps:
        if r["recovery_fraction"] is not None:
            host_best[r["host"]] = max(host_best.get(r["host"], -9), r["recovery_fraction"])
    gate_c = (sum(ports) >= 5) or (sum(1 for v in host_best.values() if v >= 0.5) >= 5)

    gates = dict(A=dict(open=gate_a, detail=a_detail, new_carrier_arms=new_carrier),
                 B=dict(open=gate_b, verdict=verdict_b, only_keep_above=ok,
                        p_create_recurrent=p_rec, p_create_keep=p_keep,
                        gradient_recur=g_rec, gradient_keep=g_keep),
                 C=dict(open=gate_c, portable=sum(ports), n_transplants=len(ports),
                        hosts_recovered=sum(1 for v in host_best.values() if v >= 0.5),
                        median_recovery=float(np.median(list(host_best.values()))) if host_best else None))
    disposition = "CONTINUE_RECOMMENDED" if (gate_a or gate_b or gate_c) else "CLOSE_AND_EXPORT"
    lines.append("")
    lines.append(f"GATE A substitution : {'OPEN' if gate_a else 'shut'}  {a_detail} new_carrier={new_carrier}")
    lines.append(f"GATE B causal       : {'OPEN' if gate_b else 'shut'}  verdict={verdict_b} only_keep_above={ok}/10 "
                 f"p_create rec={p_rec} keep={p_keep} gradient rec={g_rec} keep={g_keep}")
    lines.append(f"GATE C transplant   : {'OPEN' if gate_c else 'shut'}  portable={sum(ports)}/{len(ports)} "
                 f"hosts_recovered={gates['C']['hosts_recovered']} median_recovery={gates['C']['median_recovery']}")
    lines.append(f"DISPOSITION         : {disposition}  (gates opening is a RECOMMENDATION to the operator)")
    txt = "\n".join(lines)
    print(txt)
    _save("gates", dict(summary=summary, gates=gates, disposition=disposition))
    open(os.path.join(OUT, "gates.txt"), "w").write(txt + "\n")


def main():
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    os.makedirs(OUT, exist_ok=True)
    _log(f"phase {phase} start; code {R.code_commit()[:9]}; thresholds {THRESH}")
    if phase in ("runs", "all"):
        phase_runs()
    if phase in ("dissect", "all"):
        phase_dissect()
    if phase in ("battery", "all"):
        phase_battery()
    if phase in ("graft", "all"):
        phase_graft()
    if phase in ("gates", "all"):
        phase_gates()
    _log(f"phase {phase} done")


if __name__ == "__main__":
    main()
