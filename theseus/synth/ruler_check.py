"""THESEUS-23a: can the rulers tell designed structure from random wiring?

Prereg: roles/Theseus/prereg/2026-10-08_ruler_check/PREREG.md.

PLANTED: six families of designed motif programs (gated delay loop, memory
relay ring, rank-threshold sorter, driven cross-scale feedback, replicate-
select-mirror, phase-wrapped coupled advection). None is a known-library
family. Each member draws its parameters uniformly inside the op bounds.
RANDOM: substrate programs complexity-matched one-to-one to a planted member
(same n_rules, C, max sources).

Rulers (each reported separately, AUC planted-vs-random with a bootstrap CI;
higher score = "more planted-like" in the stated direction):
  R1 viable                        (bool)
  R2 sparseness_vs_g0              euclid_z k-NN distance to the frozen G0 set (v0_1)
  R3 known_dist                    distance to the nearest known-library member (v0_1 library)
  R4 jitter_smoothness             - mean fp distance under 4 small parameter jitters (scored as
                                   negative distance: smoother = higher)
  R5 resp_midband                  share of intervention responses in (0.05, 0.9): graded causal
                                   structure rather than inert or all-or-nothing
  R6 rep_stability                 - replicate distance between IC seeds (scored negative)
Calibration, library and G0 set are read from the committed v0_1 run (frozen).
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import time
from multiprocessing import Pool

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

from . import battery as bt  # noqa: E402
from . import collide as co  # noqa: E402
from . import rulers as ru  # noqa: E402
from . import substrate as sb  # noqa: E402

REF = "v0_1_2026-09-30"
N_JITTER = 4
JITTER = 0.10


def U(rng, lo, hi):
    return float(rng.uniform(lo, hi))


def _g(C, rules, rng, topo=None, init=None):
    return {"C": C, "topo": {"kind": topo or str(rng.choice(["ring", "line", "rrg"])), "seed": int(rng.integers(1 << 16))},
            "bc": "periodic", "init": {"kind": init or str(rng.choice(["spike", "random", "gradient", "blocks"])), "amp": 1.0},
            "rules": [dict(r, prov="planted") for r in rules]}


def R(op, src, dst, p):
    return {"op": op, "src": src, "dst": dst, "p": list(p)}


def fam_gated_delay(rng):
    return _g(2, [R("delay", [0], 1, [int(rng.integers(2, 8)), U(rng, 0.3, 0.9)]),
                  R("gate", [1, 0], 0, [U(rng, -0.3, 0.3), U(rng, 0.2, 0.8)]),
                  R("diffuse", [0], 0, [U(rng, 0.05, 0.3)]),
                  R("saturate", [], 0, [U(rng, 0.5, 2.0)]),
                  R("saturate", [], 1, [U(rng, 0.5, 2.0)])], rng)


def fam_memory_relay(rng):
    return _g(2, [R("remember", [0], 0, [U(rng, 0.1, 0.5)]),
                  R("recall", [], 1, [U(rng, 0.2, 0.8)]),
                  R("advect", [1], 1, [int(rng.choice([-2, -1, 1, 2])), U(rng, 0.2, 0.8)]),
                  R("remember", [1], 1, [U(rng, 0.1, 0.5)]),
                  R("recall", [], 0, [U(rng, -0.8, -0.2)]),
                  R("saturate", [], 0, [U(rng, 0.5, 2.0)])], rng)


def fam_rank_sorter(rng):
    return _g(2, [R("rank", [], 0, [U(rng, 0.2, 0.8)]),
                  R("threshold", [0], 1, [U(rng, -0.3, 0.3), U(rng, 0.2, 0.8)]),
                  R("diffuse", [1], 1, [U(rng, 0.05, 0.4)]),
                  R("conserve", [], 1, [U(rng, 0.3, 1.0)]),
                  R("saturate", [], 1, [U(rng, 0.5, 2.0)])], rng)


def fam_driven_crossscale(rng):
    return _g(2, [R("drive", [], 0, [U(rng, 0.3, 1.0), int(rng.integers(6, 24)), U(rng, 0.0, 0.99)]),
                  R("coarse", [0], 1, [int(rng.integers(1, 4)), U(rng, 0.2, 0.7)]),
                  R("react", [1, 0], 0, [U(rng, -0.8, -0.2), U(rng, 0.2, 0.6), U(rng, 0.5, 1.5), U(rng, 0.5, 1.5)]),
                  R("diffuse", [0], 0, [U(rng, 0.05, 0.3)]),
                  R("saturate", [], 0, [U(rng, 0.5, 2.0)])], rng, init="spike")


def fam_replicate_select(rng):
    return _g(1, [R("replicate", [0], 0, [U(rng, 0.1, 0.6)]),
                  R("select", [], 0, [U(rng, 0.2, 0.6), U(rng, 0.1, 0.4)]),
                  R("mirror", [], 0, [U(rng, 0.05, 0.4)]),
                  R("decay", [], 0, [U(rng, 0.01, 0.1)])], rng, init="random")


def fam_phase_coupled(rng):
    return _g(2, [R("advect", [0], 0, [int(rng.choice([-1, 1])), U(rng, 0.2, 0.7)]),
                  R("advect", [1], 1, [int(rng.choice([-2, 2])), U(rng, 0.2, 0.7)]),
                  R("react", [0, 1], 0, [U(rng, 0.2, 0.8), 0.0, U(rng, 0.5, 1.5), U(rng, 0.5, 1.5)]),
                  R("wrap", [], 0, [U(rng, 1.0, 3.0)]),
                  R("wrap", [], 1, [U(rng, 1.0, 3.0)])], rng, init="random")


FAMILIES = {"gated_delay": fam_gated_delay, "memory_relay": fam_memory_relay, "rank_sorter": fam_rank_sorter,
            "driven_crossscale": fam_driven_crossscale, "replicate_select": fam_replicate_select,
            "phase_coupled": fam_phase_coupled}


def jitter(g, rng):
    h = copy.deepcopy(g)
    for r in h["rules"]:
        for j, v in enumerate(r["p"]):
            if isinstance(v, float):
                r["p"][j] = sb.clamp_param(r["op"], j, v * float(rng.uniform(1 - JITTER, 1 + JITTER)))
    return h


_CAL = None


def _init(cald):
    global _CAL
    _CAL = ru.Cal(cald)


def _job(args):
    g, seed = args
    cal = _CAL
    t0 = time.process_time()
    ev = bt.evaluate(g, cal.desc_scales, cal.tau_rep, cal.sd)
    rng = np.random.default_rng(seed)
    fps = [bt.fingerprint(jitter(g, rng), cal.desc_scales, seed=0)["fp"] for _ in range(N_JITTER)]
    base = np.asarray(ev["fp_seed0"])
    jd = float(np.mean([ru.dist_matrix(base[None], f[None], "euclid_z", cal)[0, 0] for f in fps]))
    resp = np.asarray(ev["fp"])[bt.N_DESC:]
    return {"viable": ev["viable"], "fp": ev["fp"], "rep_dist": ev["viability"]["rep_dist"], "jitter_dist": jd,
            "resp_midband": float(((resp > 0.05) & (resp < 0.9)).mean()), "viability": ev["viability"],
            "cpu_s": time.process_time() - t0}


def auc(pos, neg):
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    if not len(pos) or not len(neg):
        return None
    allv = np.concatenate([pos, neg])
    ranks = np.argsort(np.argsort(allv)) + 1.0
    # average ranks for ties
    for v in np.unique(allv):
        m = allv == v
        ranks[m] = ranks[m].mean()
    return float((ranks[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def auc_ci(pos, neg, rng, n=1000):
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    a = [auc(pos[rng.integers(len(pos), size=len(pos))], neg[rng.integers(len(neg), size=len(neg))]) for _ in range(n)]
    return [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--per_family", type=int, default=40)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)
    out_dir = f"theseus/runs/{a.tag}"
    os.makedirs(out_dir, exist_ok=True)
    cal = ru.Cal(json.load(open(f"theseus/runs/{REF}/CAL.json", encoding="utf-8")))
    lib = json.load(open(f"theseus/archive/known_library_{REF}.json", encoding="utf-8"))
    libF = np.asarray(lib["fp"])
    g0F = np.array([json.loads(l)["fp"] for l in open(f"theseus/fingerprints/{REF}.jsonl", encoding="utf-8")
                    if json.loads(l)["id"].startswith("G0-")])
    rng = np.random.default_rng(20261008)
    rows = []
    for fam, fn in FAMILIES.items():
        for i in range(a.per_family):
            g = fn(rng)
            assert not sb.validate(g), sb.validate(g)
            cx = sb.complexity(g)
            rg = co.random_genome(rng, cx["n_rules"], cx["C"], max(1, cx["max_src"]))
            rows.append({"id": f"PL-{fam}-{i:03d}", "class": "planted", "family": fam, "genome": g})
            rows.append({"id": f"RM-{fam}-{i:03d}", "class": "random", "family": fam, "genome": rg})
    t0 = time.time()
    with Pool(a.workers, initializer=_init, initargs=(cal.to_json(),)) as pool:
        res = pool.map(_job, [(r["genome"], 1000 + j) for j, r in enumerate(rows)])
    for r, x in zip(rows, res):
        r.update(x)
        fp = np.asarray(x["fp"])[None]
        r["sparseness_vs_g0"] = float(ru.sparseness(fp, g0F, "euclid_z", cal)[0])
        r["known_dist"] = float(ru.dist_matrix(fp, libF, "euclid_z", cal).min())
    wall = time.time() - t0
    brng = np.random.default_rng(7)
    rulers = {"R2_sparseness_vs_g0": ("sparseness_vs_g0", 1), "R3_known_dist": ("known_dist", 1),
              "R4_jitter_smoothness": ("jitter_dist", -1), "R5_resp_midband": ("resp_midband", 1),
              "R6_rep_stability": ("rep_dist", -1)}
    summary = {"n_per_class": len(rows) // 2, "wall_s": round(wall, 1),
               "cpu_s": round(sum(x["cpu_s"] for x in res), 1), "tau_rep": cal.tau_rep}
    P = [r for r in rows if r["class"] == "planted"]
    Q = [r for r in rows if r["class"] == "random"]
    summary["R1_viable"] = {"planted": sum(r["viable"] for r in P), "random": sum(r["viable"] for r in Q), "n": len(P)}
    for scope in ("all", "viable_only"):
        pp = P if scope == "all" else [r for r in P if r["viable"]]
        qq = Q if scope == "all" else [r for r in Q if r["viable"]]
        s = {"n_planted": len(pp), "n_random": len(qq)}
        for name, (key, sign) in rulers.items():
            a_ = auc([sign * r[key] for r in pp], [sign * r[key] for r in qq])
            s[name] = {"auc": a_, "ci95": auc_ci([sign * r[key] for r in pp], [sign * r[key] for r in qq], brng) if a_ is not None else None,
                       "median_planted": float(np.median([r[key] for r in pp])) if pp else None,
                       "median_random": float(np.median([r[key] for r in qq])) if qq else None}
        summary[scope] = s
    fam_s = {}
    for fam in FAMILIES:
        pp = [r for r in P if r["family"] == fam]
        fam_s[fam] = {"viable": sum(r["viable"] for r in pp), "n": len(pp),
                      "median_jitter_dist": float(np.median([r["jitter_dist"] for r in pp])),
                      "median_known_dist": float(np.median([r["known_dist"] for r in pp]))}
    summary["by_family"] = fam_s
    with open(f"{out_dir}/ROWS.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps({k: v for k, v in r.items() if k != "fp"} | {"fp": r["fp"]}, separators=(",", ":")) + "\n")
    with open(f"{out_dir}/SUMMARY.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
