"""KNOWN MECHANISMS: executable competitors for mechanistic reproduction.

Twelve parametric families of textbook machinery, written in the SAME
substrate as every candidate, so "reproduced" means an actual genome of a
known family produces the candidate's intervention-response signature, not
that an LLM named an analogy. The families are human-designed on purpose:
they are the archive of known machinery the charter asks candidates to be
tested against. They are never collision parents (origin "known").

Reproduction attempt for a candidate fingerprint f:
  1. nearest members of a precomputed family library (LIB_PER_FAMILY random
     parameterisations per family, fingerprinted once per run);
  2. local refinement: REFINE_STEPS coordinate perturbations around the two
     best library members, each fully fingerprinted;
  3. classify by the best euclid_z distance d*:
       d* <= tau_rep        REPRODUCED_BY_KNOWN  (as close as a replicate)
       d* <= 2 tau_rep      PARTIALLY_REPRODUCED
       otherwise            NOT_REPRODUCED_YET   (never proof of novelty)
  The budget (library size, refine steps) is recorded with every verdict; a
  bigger budget can move a candidate out of NOT_REPRODUCED_YET.
"""

from __future__ import annotations

import numpy as np

from . import battery as bt
from . import rulers as ru

LIB_PER_FAMILY = 40
REFINE_STEPS = 16

TOPO_CHOICES = [("ring", "periodic"), ("line", "reflect"), ("line", "absorb"), ("rrg", "periodic"), ("mean", "periodic")]
INIT_CHOICES = ["spike", "random", "gradient", "blocks", "alternate"]


def _g(C, rules, topo_i, init_i, amp=1.0):
    t, bc = TOPO_CHOICES[int(topo_i) % len(TOPO_CHOICES)]
    return {"C": C, "topo": {"kind": t, "seed": 5}, "bc": bc,
            "init": {"kind": INIT_CHOICES[int(init_i) % len(INIT_CHOICES)], "amp": amp},
            "rules": [dict(r, prov="known") for r in rules]}


def R(op, src, dst, p):
    return {"op": op, "src": src, "dst": dst, "p": list(p)}


# family: (param bounds [(lo, hi)], builder(theta) -> genome). The last two
# params of every family are (topology index, init index).
FAMILIES = {
    "K01_diffusion": ([(0.01, 0.5), (0, 4.99), (0, 4.99)],
                      lambda t: _g(1, [R("diffuse", [0], 0, [t[0]])], t[1], t[2])),
    "K02_forced_dissipative": ([(0.01, 0.5), (0.005, 0.3), (-1, 1), (2, 32), (0, 4.99), (0, 4.99)],
                               lambda t: _g(1, [R("diffuse", [0], 0, [t[0]]), R("decay", [], 0, [t[1]]),
                                                R("drive", [], 0, [t[2], int(t[3]), 0.5])], t[4], t[5])),
    "K03_fisher_kpp": ([(0.01, 0.5), (0.05, 1.0), (0.2, 5.0), (0, 4.99), (0, 4.99)],
                       lambda t: _g(1, [R("diffuse", [0], 0, [t[0]]), R("react", [0], 0, [t[1], 0.5, -1.0]),
                                        R("saturate", [], 0, [t[2]])], t[3], t[4])),
    "K04_phase_lattice": ([(0.01, 0.5), (-3, 3), (0.05, 0.9), (0.5, 4.0), (0, 4.99), (0, 4.99)],
                          lambda t: _g(1, [R("diffuse", [0], 0, [t[0]]), R("advect", [0], 0, [int(t[1]), t[2]]),
                                           R("wrap", [], 0, [t[3]])], t[4], t[5])),
    "K05_threshold_majority": ([(0.05, 0.5), (-1, 1), (0.1, 1.0), (0.2, 3.0), (0, 4.99), (0, 4.99)],
                               lambda t: _g(1, [R("diffuse", [0], 0, [t[0]]), R("threshold", [0], 0, [t[1], t[2]]),
                                                R("saturate", [], 0, [t[3]])], t[4], t[5])),
    "K06_replicator_selection": ([(0.02, 0.9), (0.1, 0.9), (0.02, 0.6), (0.05, 1.0), (0, 4.99), (0, 4.99)],
                                 lambda t: _g(1, [R("replicate", [0], 0, [t[0]]), R("select", [], 0, [t[1], t[2]]),
                                                  R("conserve", [], 0, [t[3]])], t[4], t[5])),
    "K07_activator_inhibitor": ([(0.01, 0.1), (0.2, 0.5), (0.1, 1.0), (0.1, 1.0), (0.01, 0.2), (0, 4.99), (0, 4.99)],
                                lambda t: _g(2, [R("diffuse", [0], 0, [t[0]]), R("diffuse", [1], 1, [t[1]]),
                                                 R("react", [0, 1], 0, [t[2], 0.3, 1.5, -1.5]),
                                                 R("react", [0], 1, [t[3], 0.0, 1.0]),
                                                 R("decay", [], 0, [t[4]]), R("decay", [], 1, [t[4]]),
                                                 R("saturate", [], 0, [3.0])], t[5], t[6])),
    "K08_travelling_wave": ([(-3, 3), (0.05, 0.9), (0.2, 5.0), (0.0, 0.2), (0, 4.99), (0, 4.99)],
                            lambda t: _g(1, [R("advect", [0], 0, [int(t[0]) or 1, t[1]]), R("saturate", [], 0, [t[2]]),
                                             R("decay", [], 0, [max(t[3], 0.005)])], t[4], t[5])),
    "K09_predator_prey": ([(0.1, 1.0), (0.1, 1.0), (0.01, 0.3), (0.01, 0.3), (0, 4.99), (0, 4.99)],
                          lambda t: _g(2, [R("react", [0, 1], 0, [-t[0], 0.5, 1.0, 1.0]),
                                           R("react", [0, 1], 1, [t[1], 0.5, 1.0, 1.0]),
                                           R("decay", [], 1, [t[2]]), R("diffuse", [0], 0, [t[3]]),
                                           R("diffuse", [1], 1, [t[3]]), R("saturate", [], 0, [2.0]),
                                           R("saturate", [], 1, [2.0])], t[4], t[5])),
    "K10_coupled_map_lattice": ([(0.3, 1.0), (-2, 2), (0.01, 0.5), (0.2, 3.0), (0, 4.99), (0, 4.99)],
                                lambda t: _g(1, [R("react", [0], 0, [t[0], 0.0, t[1]]), R("diffuse", [0], 0, [t[2]]),
                                                 R("wrap", [], 0, [t[3]])], t[4], t[5])),
    "K11_echo_memory": ([(0.02, 0.9), (-1, 1), (0.005, 0.3), (0.01, 0.5), (0, 4.99), (0, 4.99)],
                        lambda t: _g(1, [R("remember", [0], 0, [t[0]]), R("recall", [], 0, [t[1]]),
                                         R("decay", [], 0, [t[2]]), R("diffuse", [0], 0, [t[3]])], t[4], t[5])),
    "K12_coarse_relaxation": ([(1, 3), (0.02, 0.9), (0.01, 0.5), (0.005, 0.3), (0, 4.99), (0, 4.99)],
                              lambda t: _g(1, [R("coarse", [0], 0, [int(t[0]), t[1]]), R("diffuse", [0], 0, [t[2]]),
                                               R("decay", [], 0, [t[3]])], t[4], t[5])),
}
FAMILY_NAMES = sorted(FAMILIES)


def sample_theta(fam, rng):
    return [float(rng.uniform(lo, hi)) for lo, hi in FAMILIES[fam][0]]


def build(fam, theta):
    return FAMILIES[fam][1](theta)


def perturb_theta(fam, theta, rng, scale=0.15):
    b = FAMILIES[fam][0]
    t = list(theta)
    j = int(rng.integers(len(t)))
    lo, hi = b[j]
    t[j] = float(np.clip(t[j] + rng.normal(0, scale * (hi - lo)), lo, hi))
    return t


def fp_of(g, cal):
    return bt.fingerprint(g, cal.desc_scales, seed=0)["fp"]


def build_library(cal, seed=0, per_family=LIB_PER_FAMILY, mapper=map):
    rng = np.random.default_rng(seed)
    jobs = []
    for fam in FAMILY_NAMES:
        for _ in range(per_family):
            jobs.append((fam, sample_theta(fam, rng)))
    fps = list(mapper(_lib_job, [(fam, th, cal.to_json()) for fam, th in jobs]))
    return {"fam": [j[0] for j in jobs], "theta": [j[1] for j in jobs], "fp": np.array(fps)}


def _lib_job(args):
    fam, th, cald = args
    cal = ru.Cal(cald)
    return fp_of(build(fam, th), cal)


def reproduce(fp, lib, cal, seed=0, refine=REFINE_STEPS):
    """Attempt to reproduce fingerprint fp with known families."""
    rng = np.random.default_rng(seed)
    fp = np.asarray(fp)
    D = ru.dist_matrix(fp[None], lib["fp"], "euclid_z", cal)[0]
    order = np.argsort(D)
    best = {"dist": float(D[order[0]]), "fam": lib["fam"][order[0]], "theta": lib["theta"][order[0]]}
    evals = 0
    for idx in order[:2]:
        fam, th, d = lib["fam"][idx], lib["theta"][idx], float(D[idx])
        for _ in range(refine // 2):
            t2 = perturb_theta(fam, th, rng)
            f2 = fp_of(build(fam, t2), cal)
            evals += 1
            d2 = float(ru.dist_matrix(fp[None], f2[None], "euclid_z", cal)[0, 0])
            if d2 < d:
                th, d = t2, d2
        if d < best["dist"]:
            best = {"dist": d, "fam": fam, "theta": th}
    tau = cal.tau_rep
    if best["dist"] <= tau:
        verdict = "REPRODUCED_BY_KNOWN"
    elif best["dist"] <= 2 * tau:
        verdict = "PARTIALLY_REPRODUCED"
    else:
        verdict = "NOT_REPRODUCED_YET"
    return {"verdict": verdict, "best_dist": best["dist"], "best_family": best["fam"],
            "best_theta": best["theta"], "tau_rep": tau,
            "budget": {"library": int(len(lib["fam"])), "refine_evals": evals}}
