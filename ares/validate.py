"""Ares cycle-1 driver: VALIDATE, COMPRESS, EXIT (DESIGN_C1.md).
Resumable; every run its own JSON; progress.log written from Python.

    python -m ares.validate runs        # 130 GA runs at 10 seeds
    python -m ares.validate dissect     # 3-way memory ablation, probes, signature
    python -m ares.validate ancestry    # emergence from snapshots
    python -m ares.validate transplant  # causal transplant vs random subgraph
    python -m ares.validate disposition # the hard disposition (DESIGN_C1 s5)
    python -m ares.validate all
"""
from __future__ import annotations

import json
import os
import sys
import time
from collections import Counter

import numpy as np

from . import search as R
from . import substrate as S
from .sweep import behaviour_probe

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "runs", "sweep_c1")
WORLDS = ["W4", "W5", "W12", "W13"]
SEEDS = list(range(1, 11))
P, G, EPS = 128, 120, 4
FLOOR = {"W4": 0.0, "W5": 0.0, "W12": 19.0, "W13": 0.0}
ATTAIN = {"W4": 40.0, "W5": 50.0, "W12": 30.28, "W13": 20.0}
THRESH = {w: FLOOR[w] + 0.2 * (ATTAIN[w] - FLOOR[w]) for w in WORLDS}
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
        SEEDSETS[k] = R.balanced_seeds_for(R.make_world(w, mode))
    return SEEDSETS[k]


def _job(name, fn):
    if os.path.exists(_path(name)):
        return
    t0 = time.time()
    out = fn()
    _save(name, out)
    _log(f"{name}: heldout {out['final']['heldout']:.2f} in {time.time() - t0:.1f}s")


# ----------------------------------------------------------------------
def phase_runs():
    cfg = S.Config()
    for w in WORLDS:
        for mode in ("present", "absent", "shuffled"):
            for sd in SEEDS:
                _job(f"{w}_{mode}_s{sd}", lambda w=w, mode=mode, sd=sd: R.run(
                    w, mode, cfg, P, G, EPS, sd, tag="c1", eval_seeds=seeds_for(w, mode), snapshots=(mode == "present")))
    nomem = S.Config(allow_keep=False, reset_each_step=True, allow_plasticity=False)
    for sd in SEEDS:
        _job(f"arm_nomem_W4_present_s{sd}", lambda sd=sd: R.run(
            "W4", "present", nomem, P, G, EPS, sd, tag="nomem", eval_seeds=seeds_for("W4", "present")))


# ----------------------------------------------------------------------
def _probe_w13(genome, mode):
    cfg = S.Config(**genome["cfg"])
    pop = S.Population.from_genomes([genome], cfg)
    world = R.make_world("W13", mode)
    _, tr = R.rollout(pop, world, seeds_for("W13", mode), record=True)
    A = np.stack(tr["actions"])[:, :, 0]
    r = np.array([ep[0]["regime"] for ep in tr["info"]])
    good = (A == (r[:, None] + 1))
    pay = slice(world.PAY_FROM, world.T)
    return dict(acc_late=float(good[:, pay].mean()), acc_late_r0=float(good[r == 0, pay].mean()),
                acc_late_r1=float(good[r == 1, pay].mean()), p_abstain=float((A[:, pay] == 0).mean()))


def memory_class(base, floor, abl, rng_=None):
    """A champion within 5% of its floor has no gain to attribute."""
    if rng_ is not None and (base - floor) < 0.05 * rng_:
        return "AT_FLOOR"
    gain = max(base - floor, 1e-9)
    def collapses(v):
        return (v - floor) <= 0.25 * gain
    a, p, m = collapses(abl["no_activation_mem"]), collapses(abl["no_plasticity"]), collapses(abl["no_memory"])
    if not m:
        return "NONE"
    if a and p:
        return "BOTH"
    if a and not p:
        return "ACT"
    if p and not a:
        return "PLAST"
    return "REDUNDANT"


def phase_dissect():
    names = sorted(f[:-5] for f in os.listdir(OUT) if f.endswith(".json") and "_s" in f
                   and not f.endswith("_dissect.json") and not f.endswith("_ancestry.json") and not f.endswith("_transplant.json"))
    for name in names:
        if os.path.exists(_path(name + "_dissect")):
            continue
        res = _load(name)
        w, mode = res["world"], res["mode"]
        g = res["final"]["genome"]
        seeds = seeds_for(w, mode)
        d = R.dissect(g, w, mode, seeds=seeds)
        d["probe"] = _probe_w13(g, mode) if w == "W13" else behaviour_probe_seeded(g, w, mode, seeds)
        base, floor = d["base"], FLOOR[w]
        gain = max(base - floor, 1e-9)
        lb = [a for a in d["node_ablation"] if a["delta"] <= -0.25 * gain]
        d["load_bearing"] = lb
        d["signature"] = "+".join(sorted(a["op"] for a in lb)) if lb else "(none)"
        d["memory_class"] = memory_class(base, floor, d["substrate_ablation"], ATTAIN[w] - FLOOR[w])
        d["heldout"] = res["final"]["heldout"]
        _save(name + "_dissect", d)
        _log(f"dissect {name}: base {base:.2f} sig {d['signature']} class {d['memory_class']} "
             f"nomem {d['substrate_ablation']['no_memory']:.2f}")


def behaviour_probe_seeded(genome, w, mode, seeds):
    """sweep.behaviour_probe uses the cycle-0 global seed set; wrap it."""
    saved = R.EVAL_SEEDS
    try:
        R.EVAL_SEEDS = list(seeds)
        return behaviour_probe(genome, w, mode)
    finally:
        R.EVAL_SEEDS = saved


# ----------------------------------------------------------------------
def phase_ancestry():
    for w in ("W4", "W5", "W13"):
        for sd in SEEDS:
            name = f"{w}_present_s{sd}"
            if not os.path.exists(_path(name)) or os.path.exists(_path(name + "_ancestry")):
                continue
            res = _load(name)
            seeds = seeds_for(w, "present")
            floor = FLOOR[w]
            world = R.make_world(w, "present")
            curve = []
            for snap in res["snapshots"]:
                if snap["gen"] % 5 != 0 and snap["gen"] != G - 1:
                    continue
                g = snap["genome"]
                intact = float(R.rollout(S.Population.from_genomes([g]), world, seeds)[0])
                c2 = S.Config(**{**g["cfg"], "allow_keep": False, "reset_each_step": True, "allow_plasticity": False})
                nomem = float(R.rollout(S.Population.from_genomes([g], c2), world, seeds)[0])
                curve.append(dict(gen=snap["gen"], intact=intact, no_memory=nomem, gap=intact - nomem))
            final_gap = curve[-1]["gap"] if curve else 0.0
            rng_ = ATTAIN[w] - floor
            onset = next((c["gen"] for c in curve if c["intact"] > floor + 0.1 * rng_), None)
            emerg = next((c["gen"] for c in curve if final_gap > 0 and c["gap"] >= 0.5 * final_gap), None)
            out = dict(curve=curve, final_gap=final_gap, onset_gen=onset, emergence_gen=emerg,
                       accretion=(emerg - onset) if (onset is not None and emerg is not None) else None,
                       lineage_mutations=dict(Counter(m for step in res["ancestry"] for m in step["mut"])))
            _save(name + "_ancestry", out)
            _log(f"ancestry {name}: onset {onset} emergence {emerg} accretion {out['accretion']} final_gap {final_gap:.2f}")


# ----------------------------------------------------------------------
def phase_transplant():
    cfg = S.Config()
    for w in ("W4", "W5", "W13", "W12"):
        for sd in SEEDS:
            name = f"{w}_present_s{sd}"
            if not os.path.exists(_path(name + "_dissect")) or os.path.exists(_path(name + "_transplant")):
                continue
            d = _load(name + "_dissect")
            g = _load(name)["final"]["genome"]
            nodes = [a["node"] for a in d["load_bearing"]]
            if not nodes:
                _save(name + "_transplant", dict(skipped="no load-bearing nodes"))
                _log(f"transplant {name}: skipped (no load-bearing nodes)")
                continue
            rng = np.random.default_rng(1000 + sd)
            world = R.make_world(w, "present")
            seeds = seeds_for(w, "present")
            src = S.Population.from_genomes([g])
            hosts_e = S.random_population(cfg, 64, rng)
            hosts_r = S.random_population(cfg, 64, rng)
            ok_e = ok_r = 0
            for i in range(64):
                if S.splice_subgraph(hosts_e, i, src, 0, nodes, rng) is not None:
                    ok_e += 1
                rs, rn = R._random_subgraph_like(src, nodes, rng)
                if S.splice_subgraph(hosts_r, i, rs, 0, rn, rng) is not None:
                    ok_r += 1
            fe = R.rollout(hosts_e, world, seeds)
            fr = R.rollout(hosts_r, world, seeds)
            base = d["base"]; floor = FLOOR[w]
            portable = bool((fe.mean() - fr.mean()) >= 0.25 * (base - floor))
            out = dict(nodes=nodes, signature=d["signature"], n_spliced_evolved=ok_e, n_spliced_random=ok_r,
                       evolved_mean=float(fe.mean()), evolved_max=float(fe.max()), random_mean=float(fr.mean()),
                       random_max=float(fr.max()), champion=base, portable=portable)
            _save(name + "_transplant", out)
            _log(f"transplant {name}: evolved {fe.mean():.2f} random {fr.mean():.2f} champion {base:.2f} portable {portable}")


# ----------------------------------------------------------------------
def _crit_ii(w, pr, sh):
    if w in ("W4", "W13"):
        return (pr["acc_late"] >= 0.65 and pr["acc_late_r0"] >= 0.55 and pr["acc_late_r1"] >= 0.55), (sh["acc_late"] < 0.65)
    if w == "W5":
        return (pr["dec_acc"] >= 0.7 and pr["dec_acc_pos"] >= 0.55 and pr["dec_acc_neg"] >= 0.55), (sh["dec_acc"] < 0.7)
    if w == "W12":
        def slope(p):
            v = [x for x in p["p_risky_by_energy"] if x == x and x is not None]
            return (v[0] - v[-1]) if len(v) >= 2 else 0.0
        return slope(pr) >= 0.3, slope(sh) < 0.15
    return False, False


def phase_disposition():
    report = {}
    lines = []
    for w in WORLDS:
        per = []
        for sd in SEEDS:
            pn, sn = f"{w}_present_s{sd}_dissect", f"{w}_shuffled_s{sd}_dissect"
            if not (os.path.exists(_path(pn)) and os.path.exists(_path(sn))):
                continue
            pd_, sd_ = _load(pn), _load(sn)
            i = pd_["heldout"] >= THRESH[w]
            ii_p, ii_s = _crit_ii(w, pd_["probe"], sd_["probe"])
            iii = len(pd_["load_bearing"]) >= 1
            gain = max(pd_["base"] - FLOOR[w], 1e-9)
            iv = (pd_["substrate_ablation"]["no_memory"] - FLOOR[w]) <= 0.25 * gain
            anc = _load(f"{w}_present_s{sd}_ancestry") if os.path.exists(_path(f"{w}_present_s{sd}_ancestry")) else {}
            tp = _load(f"{w}_present_s{sd}_transplant") if os.path.exists(_path(f"{w}_present_s{sd}_transplant")) else {}
            per.append(dict(seed=sd, heldout=pd_["heldout"], shuffled_heldout=sd_["heldout"], i=bool(i), ii=bool(ii_p and ii_s),
                            ii_present=bool(ii_p), shuffled_shows_behaviour=bool(not ii_s), iii=bool(iii), iv=bool(iv),
                            memory_class=pd_["memory_class"], signature=pd_["signature"],
                            ablation=pd_["substrate_ablation"], probe=pd_["probe"],
                            accretion=anc.get("accretion"), emergence_gen=anc.get("emergence_gen"),
                            portable=tp.get("portable"), transplant=tp))
        n = len(per)
        c = lambda k: sum(1 for r in per if r[k])
        sig = Counter(r["signature"] for r in per)
        top_sig, top_n = (sig.most_common(1)[0] if sig else ("(none)", 0))
        cls = Counter(r["memory_class"] for r in per)
        shuf_behav = sum(1 for r in per if r["shuffled_shows_behaviour"])
        hold = lambda k: c(k) >= 7
        if w == "W13":
            above = [r for r in per if r["i"]]
            if len(above) < 5:
                disp = "FAIL"
            else:
                mc = Counter(r["memory_class"] for r in above).most_common(1)[0][0]
                disp = {"ACT": "PRESERVE", "BOTH": "RECRUIT", "PLAST": "RECRUIT", "REDUNDANT": "DIFFERENT", "NONE": "NEW_CARRIER"}[mc]
                if mc == "NONE" and sum(1 for r in above if r["memory_class"] == "NONE") < 5:
                    disp = "DIFFERENT"
        else:
            need_iv = w != "W12"
            if not (hold("i") and hold("ii")):
                disp = "NO_REPLICATION"
            elif shuf_behav >= 4 or (need_iv and not hold("iv")):
                disp = "CONTROL_ARTIFACT"
            elif hold("iii") and top_n >= 5:
                disp = "VALIDATED_FOSSIL"
            else:
                disp = "MECHANISM_DIVERSE"
        acc = [r["accretion"] for r in per if r["accretion"] is not None]
        port = sum(1 for r in per if r["portable"])
        report[w] = dict(disposition=disp, n=n, i=c("i"), ii=c("ii"), iii=c("iii"), iv=c("iv"),
                         shuffled_shows_behaviour=shuf_behav, signatures=dict(sig), top_signature=[top_sig, top_n],
                         memory_classes=dict(cls), accretion=acc, portable=port, threshold=THRESH[w], rows=per)
        lines.append(f"{w:4s} {disp:18s} n {n} i {c('i')} ii {c('ii')} iii {c('iii')} iv {c('iv')} shufbehav {shuf_behav} "
                     f"top_sig {top_sig}x{top_n} classes {dict(cls)} accretion {acc} portable {port}/{n}")
        for r in per:
            lines.append(f"     s{r['seed']:<2d} held {r['heldout']:6.2f} shuf {r['shuffled_heldout']:6.2f} i{int(r['i'])} ii{int(r['ii'])} "
                         f"iii{int(r['iii'])} iv{int(r['iv'])} {r['memory_class']:9s} {r['signature']:22s} "
                         f"noact {r['ablation']['no_activation_mem']:6.2f} noplast {r['ablation']['no_plasticity']:6.2f} "
                         f"nomem {r['ablation']['no_memory']:6.2f} accr {r['accretion']} port {r['portable']}")
    # nomem arm
    arm = [_load(f"arm_nomem_W4_present_s{sd}")["final"]["heldout"] for sd in SEEDS if os.path.exists(_path(f"arm_nomem_W4_present_s{sd}"))]
    report["arm_nomem_W4"] = dict(heldout=arm, at_floor=sum(1 for x in arm if x <= 4.0), n=len(arm))
    lines.append(f"arm_nomem_W4: held {[round(x, 2) for x in arm]} at_floor(<=4) {report['arm_nomem_W4']['at_floor']}/{len(arm)}")
    txt = "\n".join(lines)
    print(txt)
    _save("disposition", report)
    open(os.path.join(OUT, "disposition.txt"), "w").write(txt + "\n")


def main():
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    os.makedirs(OUT, exist_ok=True)
    _log(f"phase {phase} start; code {R.code_commit()[:9]}; thresholds {THRESH}")
    if phase in ("runs", "all"):
        phase_runs()
    if phase in ("dissect", "all"):
        phase_dissect()
    if phase in ("ancestry", "all"):
        phase_ancestry()
    if phase in ("transplant", "all"):
        phase_transplant()
    if phase in ("disposition", "all"):
        phase_disposition()
    _log(f"phase {phase} done")


if __name__ == "__main__":
    main()
