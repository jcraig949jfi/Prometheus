"""C-016-T030 subjects, competitors, Smuggler analogues, seed partition and the subject search (PREREGISTRATION.md s3, s6).

Read-only against ensorain/ (imported, never edited). Every genome is a native TAPE genome (ensorain/wtp5/tape.py:58).

    python -m rso.ensorain.subjects search <out.json>     # 8 searched subjects, arm L, C-R2-desert, NEW seeds
"""
import json
import sys

import numpy as np

from ensorain.wtp5.planted import switch_C
from ensorain.wtp5.tape import W, genome, node
from ensorain.wtp5.worlds import P0, P1, F2

# ------------------------------------------------------------------ seed partition (PREREGISTRATION.md s6)
DEV = (16_300_001, 16_300_999)              # development lives (never confirmatory)
SEARCH = [16_310_001 + i for i in range(8)]  # subject search, one run each
SEARCH_CERT = [16_401_000 + 1000 * i for i in range(8)]   # search.py log-time certify seeds (+ generation <= 999)
TIMING = (16_310_901, 16_311_999)           # the 2,000-eval timing run and its certify seeds (disclosed)
LADDER = 16_320_001                         # Ensorain null ladder, development only
CONFIRM0 = 16_330_001                       # confirmatory lives CONFIRM0 .. CONFIRM0 + N - 1 (never run in T030)
N_CONFIRM = 400                             # PREREGISTRATION.md s7
# WTP-05 registered seeds and the ranges they generate (search.py:82 cert = 7_000_000 + seed, + generation;
# ablate.py:62,102; admit.py:22; assays.py:36,54), plus T020's seeds. Upper ends are conservative.
REGISTERED = [(6_100_000, 6_100_999), (8_800_000, 8_800_999), (8_900_000, 8_900_999), (9_500_001, 9_500_999),
              (9_700_000, 9_700_999), (9_710_000, 9_710_999), (16_500_001, 16_510_999), (16_700_000, 16_720_999),
              (51_000_001, 51_000_008), (58_000_001, 58_020_999), (16_020_001, 16_020_999), (16_030_001, 16_030_001)]
SEARCH_BUDGET = 16_000                      # Ensorain SCREEN budget (ensorain/wtp5/plans/screen.json)


def our_ranges(n_confirm=10_000):
    rs = [DEV, TIMING, (LADDER, LADDER), (CONFIRM0, CONFIRM0 + n_confirm - 1)]
    rs += [(s, s) for s in SEARCH] + [(c, c + 999) for c in SEARCH_CERT]
    return rs


def seed_conflicts():
    """Every (ours, registered) pair of overlapping seed ranges, and overlaps among our own ranges."""
    ours, bad = our_ranges(), []
    for a in ours:
        bad += [(a, r) for r in REGISTERED if a[0] <= r[1] and r[0] <= a[1]]
    for i, a in enumerate(ours):
        bad += [(a, b) for b in ours[i + 1:] if a[0] <= b[1] and b[0] <= a[1]]
    return bad


# ------------------------------------------------------------------ constructed genomes
def _c(x):
    return np.full(W, float(x))


def reference():
    """The planted lawful reference (ensorain/wtp5/planted.py:113): act = theta * s on type-1, q on type-2."""
    return switch_C()


def memoryless(sign):
    """The reference with theta fixed at sign * 0.2 and no plasticity. sign=+1 is the pre-switch law (= the frozen
    reference); sign=-1 reads the POST-switch law from a non-plastic constant: the Smuggler analogue."""
    n = [node("OBS"), node("CH", 0, i=P0), node("CH", 0, i=P1), node("CH", 0, i=F2), node("CONST", v=_c(0.2 * sign))]
    n += [node("MUL", 1, 4), node("SEL", 3, 5, 2), node("ACT", 6)]
    return genome(n, S=1)


def constant(sign):
    """Acts sign at every gate (a memoryless policy that ignores the observation; chance on both laws)."""
    return genome([node("CONST", v=_c(sign)), node("ACT", 0)], S=1)


def smuggler():
    return memoryless(-1)


def smuggler_decorative():
    """Declares a plastic parameter and lifetime learning (eta, sigma as the reference), but its action reads the
    post-switch sign from a NON-plastic constant; the plastic node is live only through a zero-weight path."""
    n = [node("OBS"), node("CH", 0, i=P0), node("CH", 0, i=P1), node("CH", 0, i=F2), node("CONST", v=_c(-0.2)),
         node("CONST", v=_c(0.2), plastic=True), node("CONST", v=_c(0.0)), node("MUL", 5, 6), node("ADD", 4, 7)]
    n += [node("MUL", 1, 8), node("SEL", 3, 9, 2), node("ACT", 10)]
    return genome(n, S=1, eta=1.0, sigma=0.5)


# ------------------------------------------------------------------ genome <-> JSON (subjects are frozen by hash)
def to_json(g):
    def enc(x):
        if isinstance(x, np.ndarray):
            return {"__nd__": x.tolist(), "shape": list(x.shape)}
        if isinstance(x, (np.floating, np.integer)):
            return x.item()
        raise TypeError(type(x))
    return json.dumps(g, sort_keys=True, default=enc)


def from_json(s):
    def dec(d):
        return np.asarray(d["__nd__"], float).reshape(d["shape"]) if "__nd__" in d else d
    return json.loads(s, object_hook=dec)


# ------------------------------------------------------------------ subject search (search accessibility)
def search(out, scratch, part=None):
    """Arm L on C-R2-desert, SEARCH_BUDGET evaluations per seed, ensorain/wtp5/search.py unchanged. The subject of
    each run is its final elite pop[0] (fixed before the run; no other selection). Endpoints are not computed."""
    from ensorain.wtp5.search import Run
    res = []
    lo, hi = map(int, part.split("-")) if part else (0, len(SEARCH) - 1)
    for seed, cert in list(zip(SEARCH, SEARCH_CERT))[lo:hi + 1]:
        r = Run("C-R2-desert", "L", seed, SEARCH_BUDGET, scratch, log_every=2000, cert_seed=cert).run()
        res.append(dict(name="searched_%d" % seed, seed=seed, evals=r.evals, cpu_s=round(r.cpu, 1),
                        genome=to_json(r.pop[0]["g"])))
        print(seed, r.evals, round(r.cpu, 1), flush=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(dict(schema="prometheus.rso.ensorain.subjects.v1", world="C-R2-desert", arm="L",
                       budget=SEARCH_BUDGET, selection="final elite pop[0] of each run", runs=res), f, indent=1)


def load_searched(path):
    with open(path, encoding="utf-8") as f:
        return {r["name"]: from_json(r["genome"]) for r in json.load(f)["runs"]}


def merge(paths, out):
    """Join the per-part files of one search into SUBJECTS.json, in SEARCH order."""
    runs = []
    for p in paths:
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        runs += d["runs"]
    d["runs"] = sorted(runs, key=lambda r: r["seed"])
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, indent=1)


if __name__ == "__main__":
    if sys.argv[1] == "search":
        search(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else ".", sys.argv[4] if len(sys.argv) > 4 else None)
    elif sys.argv[1] == "merge":
        merge(sys.argv[3:], sys.argv[2])
