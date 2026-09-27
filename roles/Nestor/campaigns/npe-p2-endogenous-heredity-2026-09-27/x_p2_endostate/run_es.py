"""X-P2-ENDOSTATE (EXPLORE, MEASUREMENT / endogenous transition; program P2 Blocks F, N). Declared before running.
Theory-aware by date. Existing data only (no world runs; light CPU, 2 processes).

Mechanism now in hand (P2 corpus delegate, delegates/corpus/CORPUS_ANALYSIS.md, on W1 genomes): most competent
donors are SELF-free offset-64 block copiers that take their own address from never-written ZERO registers or from
aligned immediates; stalled (NO_COPY) first donors depend on a fresh HL (14/20) and are all self-poisoning (their
own block copy advances HL/DE), established first donors mostly are not HL-dependent (2/22).
North-Star question (Block F "can evolution discover state robustness?"): inside lineages that established under
PERSISTENT registers (no aid), do later competent genomes copy from the state their own execution leaves (state-
robust) more often than the early donors did? That would be the lineage modifying its own reproductive machinery
to cross the establishment barrier.

Sample: the X-DD-DENSE-COPY DENSE_COPY runs (persistent registers, dense VM) that reached world causal depth >= 20
(23 runs). For each: the competent genomes recorded at (a) the first checkpoint with any, (b) the checkpoint at the
middle of the remaining span, (c) the last checkpoint with any; up to 6 genomes per checkpoint (fixed sampling seed).
Measurement per genome (X-DD-SELFSTATE's method, run_ss.job, 10 seeds x 2 sides): copy rate from fresh (k=0) and
after one own execution (k=1). STATE_ROBUST iff rate_1 >= 0.25 x rate_0 (i.e. not SELF_POISON), among genomes with
rate_0 > 0.
Per run: robust share at (a) and at (c).
Classification: SIGNAL (endogenous state robustness) if in >= 70% of runs with >= 3 measurable genomes at both (a) and
(c) the robust share at (c) exceeds (a) by >= 0.20; CLEAN_NULL if that holds in <= 30% of such runs AND the pooled
late robust share is within 0.10 of the pooled early share; WEAK_SIGNAL otherwise.
Caveat declared: selection inside a persistent-state runaway is expected to favour copiers that copy in-world, so a
rise is the anticipated direction; the measurement is whether it happens WITHIN the lineage (from a poisoned
founder class) rather than being present from the first donor.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
W1 = HERE.parent.parent / "npe-w1-donor-discovery-2026-09-26"
SS = W1 / "x_dd_selfstate"
for p in (SS, W1 / "x_dd_nocopy_context", W1 / "x_dd_dense_copy", W1 / "x_donor_discovery",
          HERE.parent.parent / "c9x-explore-2026-09-24" / "x_donor_swap",
          HERE.parent.parent / "z80atlas-verify-2026-09-22"):
    sys.path.insert(0, str(p))
PER = 6


def plan():
    out = []
    for p in sorted((W1 / "x_dd_dense_copy" / "results").glob("DENSE_COPY_*.json")):
        r = json.loads(p.read_text())
        if r["depth"] < 20:
            continue
        cps = [c for c in r["checkpoints"] if c.get("competent_genomes")]
        if not cps:
            continue
        picks = {"a": cps[0], "b": cps[len(cps) // 2], "c": cps[-1]}
        rng = random.Random(repr(("X-P2-ENDOSTATE", r["cell"], r["seed"])))
        for tag, c in picks.items():
            gs = sorted({g["hex"] for g in c["competent_genomes"]})
            for h in rng.sample(gs, min(PER, len(gs))):
                out.append((r["cell"], r["seed"], tag, c["epoch"], h))
    return out


def job(args):
    cell, seed, tag, epoch, h = args
    import run_ss
    run_ss.HERE = HERE / "scratch"
    rec = run_ss.job(("ANY", cell, seed, h))
    return {"cell": cell, "seed": seed, "tag": tag, "epoch": epoch, "hex": h,
            "rate0": rec["rates_by_k"][0], "rate1": rec["rates_by_k"][1],
            "robust": rec["rates_by_k"][0] > 0 and rec["rates_by_k"][1] >= 0.25 * rec["rates_by_k"][0]}


def main():
    (HERE / "scratch" / "results").mkdir(parents=True, exist_ok=True)
    todo = plan()
    with mp.Pool(2, maxtasksperchild=20) as pool:
        res = list(pool.imap(job, todo))
    (HERE / "RESULTS.json").write_text(json.dumps(res))
    runs = sorted({(r["cell"], r["seed"]) for r in res})
    per = []
    for key in runs:
        row = {"cell": key[0], "seed": key[1]}
        for t in ("a", "b", "c"):
            m = [r for r in res if (r["cell"], r["seed"]) == key and r["tag"] == t and r["rate0"] > 0]
            row[t] = {"n": len(m), "robust": sum(r["robust"] for r in m),
                      "epoch": next((r["epoch"] for r in res if (r["cell"], r["seed"]) == key and r["tag"] == t), None)}
        per.append(row)
    ok = [x for x in per if x["a"]["n"] >= 3 and x["c"]["n"] >= 3]
    rise = sum((x["c"]["robust"] / x["c"]["n"]) - (x["a"]["robust"] / x["a"]["n"]) >= 0.20 for x in ok)
    pe = sum(x["a"]["robust"] for x in ok) / max(1, sum(x["a"]["n"] for x in ok))
    pl = sum(x["c"]["robust"] for x in ok) / max(1, sum(x["c"]["n"] for x in ok))
    cls = ("INVALID" if not ok else "SIGNAL" if rise >= 0.7 * len(ok) else
           "CLEAN_NULL" if rise <= 0.3 * len(ok) and abs(pl - pe) <= 0.10 else "WEAK_SIGNAL")
    summ = {"classification": cls, "runs_measurable": len(ok), "runs_with_rise": rise,
            "pooled_robust_share_early": round(pe, 4), "pooled_robust_share_late": round(pl, 4), "per_run": per}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps({k: v for k, v in summ.items() if k != "per_run"}, indent=1))


if __name__ == "__main__":
    main()
