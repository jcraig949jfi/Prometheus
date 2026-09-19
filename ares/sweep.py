"""Ares cycle-0 sweep driver. Resumable: every run writes its own JSON
and is skipped if that file exists. Progress goes to progress.log from
inside Python (never a shell redirect). Phases:

    python -m ares.sweep runs        # GA runs: main, W6, W9, W10, substrate-ablation arms
    python -m ares.sweep dissect     # champion dissection + behaviour probes
    python -m ares.sweep transfer    # present champions on every other world
    python -m ares.sweep transplant  # W8 protocol
    python -m ares.sweep summary     # summary.json + ASCII tables
    python -m ares.sweep all
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

from . import search as R
from . import substrate as S
from .develop import run_dev

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "runs", "sweep_c0")
MAIN_WORLDS = ["W1", "W2", "W3", "W4", "W5", "W7", "W11", "W12"]
SEEDS = [1, 2, 3]
P, G, EPS = 128, 120, 4


def _log(msg):
    os.makedirs(OUT, exist_ok=True)
    line = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + " " + msg
    print(line, flush=True)
    with open(os.path.join(OUT, "progress.log"), "a") as f:
        f.write(line + "\n"); f.flush()


def _path(name):
    return os.path.join(OUT, name + ".json")


def _save(name, obj):
    with open(_path(name), "w") as f:
        json.dump(obj, f)


def _load(name):
    with open(_path(name)) as f:
        return json.load(f)


def _job(name, fn):
    if os.path.exists(_path(name)):
        return
    t0 = time.time()
    out = fn()
    _save(name, out)
    ho = out.get("final", {}).get("heldout", float("nan"))
    _log(f"{name}: heldout {ho:.2f} in {time.time() - t0:.1f}s")


# ----------------------------------------------------------------------
def phase_runs():
    cfg = S.Config()
    for w in MAIN_WORLDS:
        for mode in ("present", "absent", "shuffled"):
            for sd in SEEDS:
                _job(f"main_{w}_{mode}_s{sd}", lambda w=w, mode=mode, sd=sd: R.run(w, mode, cfg, P, G, EPS, sd, tag="main"))
    for label, c in (("W6scarce", S.Config(n_hidden=2, ticks=1)), ("W6abundant", S.Config(n_hidden=12, ticks=4))):
        for sd in SEEDS:
            _job(f"{label}_present_s{sd}", lambda c=c, sd=sd, label=label: R.run("W3", "present", c, P, G, EPS, sd, tag=label))
    for mode in ("present", "absent", "shuffled"):
        for sd in SEEDS:
            _job(f"W9_{mode}_s{sd}", lambda mode=mode, sd=sd: R.run_coevo(mode, cfg, P, G, EPS, sd, tag="W9"))
    for w in ("W4", "W3"):
        for sd in SEEDS:
            _job(f"W10dev_{w}_present_s{sd}", lambda w=w, sd=sd: run_dev(w, "present", cfg, P, G, EPS, sd, tag="W10"))
    arms = (("nostate", S.Config(allow_keep=False, reset_each_step=True)), ("notopo", S.Config(allow_topology=False)),
            ("noplast", S.Config(allow_plasticity=False)))
    for label, c in arms:
        for w in ("W3", "W4", "W12", "W2"):
            for sd in SEEDS:
                _job(f"arm_{label}_{w}_present_s{sd}", lambda c=c, w=w, sd=sd, label=label: R.run(w, "present", c, P, G, EPS, sd, tag=label))


# ----------------------------------------------------------------------
def behaviour_probe(genome, world_name, mode):
    """World-specific conditional behaviour statistics over the held-out
    episodes. Every statistic is a plain frequency; nothing is named."""
    cfg = S.Config(**genome["cfg"])
    pop = S.Population.from_genomes([genome], cfg)
    world = R.make_world(world_name, mode)
    _, tr = R.rollout(pop, world, R.EVAL_SEEDS, record=True)
    A = np.stack(tr["actions"])[:, :, 0]          # (S, T)
    Rw = np.stack(tr["rewards"])[:, :, 0]
    info = tr["info"]
    S_, T = A.shape
    out = {}

    def grid(key):
        return np.array([[ep[t][key] for t in range(T)] for ep in info])

    if world_name in ("W1",):
        d = grid("danger")
        out = dict(p_act_danger=float((A[d == 1] == 1).mean()) if (d == 1).any() else float("nan"),
                   p_act_nodanger=float((A[d == 0] == 1).mean()), n_danger_steps=int((d == 1).sum()))
    elif world_name == "W2":
        w = grid("window")
        out = dict(p_risky_window=float((A[w == 1] == 1).mean()) if (w == 1).any() else float("nan"),
                   p_risky_nowindow=float((A[w == 0] == 1).mean()), n_window_steps=int((w == 1).sum()))
    elif world_name in ("W3", "W6"):
        c = grid("correct"); fl = np.array([ep[0]["flip"] for ep in info])
        t = np.arange(T)[None, :]
        pre = (t < fl[:, None]) if mode == "present" else np.ones_like(A, bool)
        post5 = (t >= fl[:, None]) & (t < fl[:, None] + 5)
        post = (t >= fl[:, None] + 5)
        acc = (A == c)
        out = dict(acc_pre=float(acc[pre].mean()), acc_post5=float(acc[post5].mean()) if post5.any() else float("nan"),
                   acc_post=float(acc[post].mean()) if post.any() else float("nan"), p_abstain=float((A == 0).mean()))
    elif world_name == "W4":
        r = np.array([ep[0]["regime"] for ep in info])
        good = (A == (r[:, None] + 1))
        out = dict(acc_early=float(good[:, :3].mean()), acc_late=float(good[:, 10:].mean()),
                   acc_late_r0=float(good[r == 0, 10:].mean()), acc_late_r1=float(good[r == 1, 10:].mean()),
                   p_abstain=float((A == 0).mean()))
    elif world_name == "W5":
        pay = np.array([ep[0]["pay"] for ep in info]); dec = T - 2
        good = np.where(pay > 0, 1, 2)
        out = dict(dec_acc=float((A[:, dec] == good).mean()), dec_abstain=float((A[:, dec] == 0).mean()),
                   dec_acc_pos=float((A[pay > 0, dec] == 1).mean()), dec_acc_neg=float((A[pay < 0, dec] == 2).mean()))
    elif world_name == "W7":
        rg = grid("regime")
        out = dict(score_A=float(Rw[rg == 0].mean()), score_B=float(Rw[rg == 1].mean()) if (rg == 1).any() else float("nan"),
                   p_opt0_A=float((A[rg == 0] == 0).mean()), p_opt0_B=float((A[rg == 1] == 0).mean()) if (rg == 1).any() else float("nan"),
                   switch_rate_A=float((A[:, 1:] != A[:, :-1])[rg[:, 1:] == 0].mean()),
                   switch_rate_B=float((A[:, 1:] != A[:, :-1])[rg[:, 1:] == 1].mean()) if (rg == 1).any() else float("nan"))
    elif world_name == "W11":
        truth = np.array([ep[0]["truth"] for ep in info]); good = np.where(truth > 0, 1, 2)
        if mode == "absent":
            out = dict(p_good=float((A == good[:, None]).mean()), p_probe=float((A == 0).mean()))
        else:
            first = np.array([int(np.argmax(a != 0)) if (a != 0).any() else T for a in A])
            choice = np.array([a[f] if f < T else 0 for a, f in zip(A, first)])
            out = dict(mean_commit_step=float(first.mean()), commit_acc=float((choice == good).mean()),
                       p_never=float((first >= T).mean()), commit_step_hist=np.bincount(np.minimum(first, T), minlength=T + 1).tolist())
    elif world_name == "W12":
        E = np.asarray(grid("energy"), dtype=float); E = E[..., 0] if E.ndim == 3 else E; risky = (A == 1)
        alive = np.ones_like(A, bool)
        alive[:, 1:] = np.cumprod(Rw[:, :-1] > 0, axis=1).astype(bool)
        bins = [(-1, 2), (2, 4), (4, 6), (6, 8), (8, 99)]
        out = dict(p_risky_by_energy=[float(risky[(E > lo) & (E <= hi) & alive].mean()) if ((E > lo) & (E <= hi) & alive).any() else float("nan") for lo, hi in bins],
                   n_by_energy=[int(((E > lo) & (E <= hi) & alive).sum()) for lo, hi in bins],
                   mean_lifetime=float(alive.sum(1).mean()))
    return out


def phase_dissect():
    names = [f[:-5] for f in os.listdir(OUT) if f.endswith(".json") and not f.endswith("_dissect.json")
             and (f.startswith("main_") or f.startswith("W6") or f.startswith("arm_") or f.startswith("W10dev_"))]
    for name in sorted(names):
        if os.path.exists(_path(name + "_dissect")):
            continue
        res = _load(name)
        w = res["world"]; mode = res["mode"]
        wn = "W3" if w == "W6" else w
        g = res["final"]["genome"]
        d = R.dissect(g, wn, mode)
        d["probe"] = behaviour_probe(g, wn if not name.startswith("W6") else "W3", mode)
        d["heldout"] = res["final"]["heldout"]
        _save(name + "_dissect", d)
        _log(f"dissect {name}: base {d['base']:.2f} nodes {len(d['node_ablation'])} "
             f"maxdelta {min([a['delta'] for a in d['node_ablation']] or [0]):.2f} no_state {d['substrate_ablation']['no_state']:.2f}")


def phase_transfer():
    if os.path.exists(_path("transfer")):
        return
    rows = []
    for w in MAIN_WORLDS:
        for sd in SEEDS:
            name = f"main_{w}_present_s{sd}"
            if not os.path.exists(_path(name)):
                continue
            g = _load(name)["final"]["genome"]
            rows.append(dict(source=w, seed=sd, scores=R.transfer(g, MAIN_WORLDS)))
    _save("transfer", rows)
    _log("transfer matrix written")


def phase_transplant():
    """W8: subgraphs from the most ablation-sensitive nodes of a source
    champion, spliced every 10 generations into 25% of a target world's
    population; evolved vs random-subgraph control; retention and fitness."""
    sources = ["W2", "W4", "W7"]; targets = ["W1", "W3", "W12"]
    cfg = S.Config()
    for src in sources:
        name = f"main_{src}_present_s1"
        if not os.path.exists(_path(name + "_dissect")):
            continue
        g = _load(name)["final"]["genome"]; d = _load(name + "_dissect")
        abl = sorted(d["node_ablation"], key=lambda a: a["delta"])[:3]
        nodes = [a["node"] for a in abl]
        if not nodes:
            _log(f"transplant: source {src} has no hidden nodes; skipped"); continue
        for tgt in targets:
            for arm, rc in (("evolved", False), ("random", True)):
                for sd in (1, 2):
                    _job(f"W8_{src}_to_{tgt}_{arm}_s{sd}",
                         lambda tgt=tgt, rc=rc, sd=sd, g=g, nodes=nodes: R.run(
                             tgt, "present", cfg, P, 60, EPS, sd, tag=f"W8_{arm}",
                             transplant=dict(source=g, nodes=nodes, every=10, frac=0.25, random_control=rc)))
            for sd in (1, 2):
                _job(f"W8_none_to_{tgt}_s{sd}", lambda tgt=tgt, sd=sd: R.run(tgt, "present", cfg, P, 60, EPS, sd, tag="W8_none"))


# ----------------------------------------------------------------------
def phase_summary():
    base = json.load(open(os.path.join(HERE, "runs", "baselines.json")))["rows"]
    floor = {(r["world"], r["mode"]): r["best_fixed"] for r in base if "best_fixed" in r}
    summary = dict(floors={f"{k[0]}/{k[1]}": v for k, v in floor.items()}, cells={})
    files = sorted(f[:-5] for f in os.listdir(OUT) if f.endswith(".json") and not f.endswith("_dissect.json"))
    for name in files:
        if name in ("transfer",):
            continue
        res = _load(name)
        cell = dict(world=res["world"], mode=res["mode"], seed=res["seed"], tag=res.get("tag"),
                    heldout=res["final"]["heldout"], best_ever=res.get("best_ever", {}).get("heldout"),
                    elapsed_s=res["elapsed_s"])
        lg = res["log"]
        cell["gen_curve"] = [(r["gen"], round(r["champ_heldout"], 2)) for r in lg]
        last = lg[-1]
        cell["champ_struct"] = {k: v for k, v in last["champ"].items() if k != "op_hist"}
        cell["champ_ophist"] = last["champ"].get("op_hist")
        cell["pop_mean"] = last.get("pop_mean")
        cell["struct_div"] = last.get("struct_div"); cell["behav_div"] = last.get("behav_div")
        ms = [r["mutation_survival"] for r in lg if r.get("mutation_survival") is not None and r.get("mutation_survival") == r.get("mutation_survival")]
        cell["mutation_survival_mean"] = float(np.mean(ms)) if ms else None
        if "choice_autocorr" in res:
            cell["choice_autocorr"] = res["choice_autocorr"]
        if res.get("transplant_log"):
            cell["transplant_log"] = res["transplant_log"]
        dp = _path(name + "_dissect")
        if os.path.exists(dp):
            d = _load(name + "_dissect")
            deltas = [a["delta"] for a in d["node_ablation"]]
            cell["ablation"] = dict(base=d["base"], n_nodes=len(deltas), min_delta=min(deltas) if deltas else 0.0,
                                    max_delta=max(deltas) if deltas else 0.0,
                                    n_load_bearing=int(sum(1 for x in deltas if x < -0.25 * max(1e-9, d["base"] - floor.get((res["world"] if res["world"] != "W6" else "W3", res["mode"]), 0)))),
                                    no_state=d["substrate_ablation"]["no_state"], no_plasticity=d["substrate_ablation"]["no_plasticity"])
            cell["probe"] = d["probe"]
        summary["cells"][name] = cell
    if os.path.exists(_path("transfer")):
        summary["transfer"] = _load("transfer")
    _save("summary", summary)
    _print_tables(summary)


def _print_tables(summary):
    cells = summary["cells"]
    print(f"\n{'cell':34s} {'held':>8s} {'floor':>7s} {'hid':>4s} {'edg':>4s} {'keep':>4s} {'cyc':>4s} {'gate':>4s} {'plas':>4s} {'lb':>3s} {'nostate':>8s}")
    for name, c in cells.items():
        st = c["champ_struct"]; ab = c.get("ablation", {})
        fl = summary["floors"].get(f"{c['world'] if c['world'] != 'W6' else 'W3'}/{c['mode']}", float("nan"))
        print(f"{name:34s} {c['heldout']:8.2f} {fl:7.2f} {st.get('n_hidden', 0):4d} {st.get('n_edges', 0):4d} {st.get('n_keep', 0):4d} "
              f"{st.get('n_cyclic', 0):4d} {st.get('n_gate_like', 0):4d} {st.get('n_plastic', 0):4d} {ab.get('n_load_bearing', 0):3d} {ab.get('no_state', float('nan')):8.2f}")


def main():
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    os.makedirs(OUT, exist_ok=True)
    _log(f"phase {phase} start; code {R.code_commit()[:9]}")
    if phase in ("runs", "all"):
        phase_runs()
    if phase in ("dissect", "all"):
        phase_dissect()
    if phase in ("transfer", "all"):
        phase_transfer()
    if phase in ("transplant", "all"):
        phase_transplant()
    if phase in ("summary", "all"):
        phase_summary()
    _log(f"phase {phase} done")


if __name__ == "__main__":
    main()
