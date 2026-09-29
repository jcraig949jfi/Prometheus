"""PKG-S1 three-loci decomposition (answer-keyed; ARC3 "storage vs hypothesis vs readout").

For every learner the analytic resource profile at T symbols is:
  stored_bits      raw symbols kept verbatim (STAT: the last k; VERB_*: B; NEAREST: B; HMM_EM: the window or T)
  hypothesis_bits  persistent learned/summary state (STAT: 2^k x 2 counters x log2(T+1); HMM: 2 S^2 + S floats x 32)
  transient_bits   state built at query time and discarded (VERB_SUM: 2^k x 2 x log2(B+1) counts over the window)
  readout_ops      per query
Joined with the measured EXCESS log-loss vs the exact Bayes predictor (results/ladder.json, results/hmm_pilot.json), it
answers per world: for the best learner of each locus, how many bits sit where?
Writes results/loci.json and prints a table."""
import json
import math
import os
import re

HERE = os.path.dirname(__file__)


def profile(name, T):
    m = re.match(r"STAT_k(\d+)", name)
    if m:
        k = int(m.group(1))
        return dict(locus="storage-statistic", stored=k, hypothesis=2 ** k * 2 * math.log2(T + 1), transient=0, ops=k)
    m = re.match(r"VERB_SUM_B(\d+)_k(\d+)", name)
    if m:
        B, k = map(int, m.groups())
        return dict(locus="verbatim+readout-summary", stored=B, hypothesis=0, transient=2 ** k * 2 * math.log2(B + 1),
                    ops=B * k)
    m = re.match(r"VERB_RESTRICT_B(\d+)", name)
    if m:
        B = int(m.group(1))
        return dict(locus="verbatim+restricted-readout", stored=B, hypothesis=0, transient=4 * math.log2(B + 1), ops=B)
    m = re.match(r"NEAREST_B(\d+)_L(\d+)", name)
    if m:
        B, L = map(int, m.groups())
        return dict(locus="verbatim+nonparametric-readout", stored=B, hypothesis=0, transient=0, ops=B * L)
    m = re.match(r"HMM(\d+)_EM_(full|W(\d+))", name)
    if m:
        S = int(m.group(1))
        stored = T if m.group(2) == "full" else int(m.group(3))
        return dict(locus="learned-hypothesis(+history for refits)", stored=stored, hypothesis=(2 * S * S + S) * 32,
                    transient=0, ops=S * S)
    return None


def main(T=4000):
    lad = json.load(open(os.path.join(HERE, "results", "ladder.json")))["results"]
    hmm = json.load(open(os.path.join(HERE, "results", "hmm_pilot.json")))
    rows = {}
    for w, v in lad.items():
        if w.startswith("W5"):
            continue
        for name, r in v.items():
            p = profile(name, T)
            if p:
                rows.setdefault(w, []).append(dict(name=name, excess=r["excess"]["mean"], **p))
    for w, v in hmm.items():
        for name, r in v.items():
            p = profile(name, T)
            if p and name.startswith("HMM"):
                rows.setdefault(w, []).append(dict(name=name, excess=r["excess_all"], excess_2nd=r["excess_2nd_half"], **p))
    best = {}
    for w, rs in rows.items():
        by = {}
        for r in rs:
            if r["locus"] not in by or r["excess"] < by[r["locus"]]["excess"]:
                by[r["locus"]] = r
        best[w] = by
    json.dump(dict(T=T, best_per_locus=best), open(os.path.join(HERE, "results", "loci.json"), "w"), indent=1)
    for w, by in best.items():
        print(w)
        for loc, r in sorted(by.items(), key=lambda kv: kv[1]["excess"]):
            print(f"   {loc:40s} {r['name']:22s} excess {r['excess']:.3f}  stored {r['stored']:>6.0f}b  "
                  f"hyp {r['hypothesis']:>7.0f}b  transient {r['transient']:>5.0f}b  ops {r['ops']:>6.0f}")
    return best


if __name__ == "__main__":
    main()
