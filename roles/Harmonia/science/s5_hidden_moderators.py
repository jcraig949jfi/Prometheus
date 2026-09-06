"""S5 -- HIDDEN MODERATORS: which "arbitrary" parameters decide the sign?

Harmonia science loop 6, 2026-09-05.

SE-1b established, with every guard in place, that hill-climbing beats random
sampling at a 20-encounter budget (d=0.60, p=0.0005). The attack on that
conclusion found a crossover at encounter 15: at a 12-encounter budget the same
experiment reports the OPPOSITE winner.

That raises the question this loop exists to answer:

    A PARAMETER HELD FIXED IS AN UNTESTED CLAIM THAT IT DOES NOT MATTER.

SE-1b fixed three parameters without argument -- budget 20, landscape 64 bits,
landscape smooth. Each was an implementation detail. This loop promotes all
three to experimental factors and asks how many cells of the resulting grid
would have produced a DIFFERENT SIGN, and therefore a different published
mechanism, from an equally rigorous campaign.

  budget        5, 10, 15, 20, 40, 80 encounters
  landscape     32, 64, 128 bits
  structure     SMOOTH (per-bit credit -- single mutations always visible)
                BLOCKED (credit only for fully-matched 8-bit blocks, so most
                single-bit mutations are invisible and the climber sits on
                plateaus)

36 cells. Within each cell the unit is the WORLD and n=64, exactly as SE-1b.
Across cells the question is descriptive -- how many signs flip -- not a
36-way inferential sweep, which is precisely the searcher's curse packet 1
measured. The Bonferroni threshold for the full grid is reported so the cost of
treating it inferentially is visible.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import statistics
import sys
import urllib.error
import urllib.request

NW = 64
BUDGETS = [5, 10, 15, 20, 40, 80]
SIZES = [32, 64, 128]
STRUCTURES = ["smooth", "blocked"]
BLOCK = 8


def target_for(seed, bits):
    r = random.Random("t|%s|%s" % (seed, bits))
    return [r.randint(0, 1) for _ in range(bits)]


def score(b, t, structure):
    bits = len(t)
    if structure == "smooth":
        return sum(1 for i in range(bits) if b[i] == t[i]) / bits
    # BLOCKED: credit only for entirely-correct blocks. Most single-bit
    # mutations change nothing, so the landscape is a set of plateaus.
    nb = bits // BLOCK
    good = 0
    for k in range(nb):
        seg = range(k * BLOCK, (k + 1) * BLOCK)
        if all(b[i] == t[i] for i in seg):
            good += 1
    return good / nb


def play_hill(t, seed, enc, structure):
    bits = len(t)
    r = random.Random("hill|%s" % seed)
    cur = [r.randint(0, 1) for _ in range(bits)]
    best = score(cur, t, structure)
    for _ in range(enc - 1):
        cand = list(cur)
        cand[r.randrange(bits)] ^= 1
        s = score(cand, t, structure)
        if s >= best:
            cur, best = cand, s
    return best


def play_sample(t, seed, enc, structure):
    bits = len(t)
    r = random.Random("sample|%s" % seed)
    best = score([r.randint(0, 1) for _ in range(bits)], t, structure)
    for _ in range(enc - 1):
        best = max(best, score([r.randint(0, 1) for _ in range(bits)],
                               t, structure))
    return best


def perm_p(a, b, iters=2000, rng=None):
    rng = rng or random.Random(0)
    obs = abs(statistics.fmean(a) - statistics.fmean(b))
    pool = list(a) + list(b)
    n = len(a)
    hits = 0
    for _ in range(iters):
        rng.shuffle(pool)
        if abs(statistics.fmean(pool[:n]) - statistics.fmean(pool[n:])) >= obs:
            hits += 1
    return (hits + 1) / (iters + 1)


def cohen_d(a, b):
    va, vb = statistics.variance(a), statistics.variance(b)
    sp = (((len(a) - 1) * va + (len(b) - 1) * vb) / (len(a) + len(b) - 2)) ** 0.5
    return (statistics.fmean(a) - statistics.fmean(b)) / sp if sp else 0.0


class C:
    def __init__(self, base):
        self.base, self.token, self.key = base.rstrip("/"), None, None

    def call(self, m, p, body=None):
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = "Bearer " + self.token
        if self.key:
            h["X-SFE-Session"] = self.key
        d = json.dumps(body).encode() if body is not None else None
        r = urllib.request.Request(self.base + p, data=d, headers=h, method=m)
        try:
            with urllib.request.urlopen(r, timeout=60) as z:
                return z.status, json.loads(z.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            try:
                return e.code, json.loads(e.read().decode() or "{}")
            except Exception:                                      # noqa: BLE001
                return e.code, {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8893/v2")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    c = C(a.base)
    live = c.call("GET", "/version")[0] == 200
    if live:
        c.token = c.call("POST", "/clients", {"name": "s5"})[1]["token"]
        s = c.call("POST", "/sessions", {"name": "s5"})[1]
        c.key = s["session_key"]
        sid = s["session_id"]

    n_cells = len(BUDGETS) * len(SIZES) * len(STRUCTURES)
    bonf = 0.05 / n_cells
    print("=" * 74)
    print("S5  HIDDEN MODERATOR SWEEP -- %d cells, n=%d worlds per arm per cell"
          % (n_cells, NW))
    print("=" * 74)
    print("  SE-1b's fixed choices were: budget 20, 64 bits, smooth.")
    print("  Bonferroni for the full grid if treated inferentially: p < %.5f\n"
          % bonf)

    cells = []
    for structure in STRUCTURES:
        print("  --- structure = %s ---" % structure)
        print("  bits  budget      hill   sample    d       p       winner")
        for bits in SIZES:
            for enc in BUDGETS:
                hs, ss = [], []
                for w in range(NW):
                    t = target_for(5000 + w, bits)
                    hs.append(play_hill(t, 5000 + w, enc, structure))
                    ss.append(play_sample(t, 5000 + w, enc, structure))
                d = cohen_d(hs, ss)
                p = perm_p(hs, ss, 2000, random.Random(w))
                win = "HILL" if d > 0 else ("sample" if d < 0 else "tie")
                sig = "*" if p < bonf else " "
                cells.append({"structure": structure, "bits": bits,
                              "budget": enc, "hill": statistics.fmean(hs),
                              "sample": statistics.fmean(ss),
                              "d": d, "p": p, "winner": win,
                              "sig_bonferroni": p < bonf})
                print("  %4d  %6d   %7.4f %7.4f  %+6.2f  %.4f%s  %s"
                      % (bits, enc, statistics.fmean(hs), statistics.fmean(ss),
                         d, p, sig, win))
        print()

    # ---- how many signs flip? -------------------------------------------
    hill_wins = [x for x in cells if x["winner"] == "HILL"]
    samp_wins = [x for x in cells if x["winner"] == "sample"]
    sig_cells = [x for x in cells if x["sig_bonferroni"]]
    sig_hill = [x for x in sig_cells if x["winner"] == "HILL"]
    sig_samp = [x for x in sig_cells if x["winner"] == "sample"]

    print("=" * 74)
    print("RESULT")
    print("=" * 74)
    print("  cells where HILL wins   : %d of %d" % (len(hill_wins), n_cells))
    print("  cells where SAMPLE wins : %d of %d" % (len(samp_wins), n_cells))
    print("  cells significant at the grid-corrected threshold: %d"
          % len(sig_cells))
    print("      of which HILL wins   : %d" % len(sig_hill))
    print("      of which SAMPLE wins : %d" % len(sig_samp))
    print()
    print("  SE-1b's cell (smooth, 64 bits, budget 20): d=%+.2f -> %s"
          % ([x for x in cells if x["structure"] == "smooth"
              and x["bits"] == 64 and x["budget"] == 20][0]["d"],
             [x for x in cells if x["structure"] == "smooth"
              and x["bits"] == 64 and x["budget"] == 20][0]["winner"]))

    both_signs_significant = bool(sig_hill) and bool(sig_samp)
    print("\n  BOTH SIGNS ARE SIGNIFICANT SOMEWHERE IN THE GRID: %s"
          % both_signs_significant)
    if both_signs_significant:
        h = max(sig_hill, key=lambda x: abs(x["d"]))
        s_ = max(sig_samp, key=lambda x: abs(x["d"]))
        print("    strongest HILL   cell: %s %d bits, budget %d, d=%+.2f, p=%.4f"
              % (h["structure"], h["bits"], h["budget"], h["d"], h["p"]))
        print("    strongest SAMPLE cell: %s %d bits, budget %d, d=%+.2f, p=%.4f"
              % (s_["structure"], s_["bits"], s_["budget"], s_["d"], s_["p"]))
        print("\n    Two campaigns, each rigorous, each pre-registered, each")
        print("    passing every guard built in loops 1-5, would publish")
        print("    OPPOSITE MECHANISMS from this one system.")

    out = {"n_cells": n_cells, "n_per_arm": NW, "bonferroni": bonf,
           "cells": cells,
           "hill_wins": len(hill_wins), "sample_wins": len(samp_wins),
           "significant_cells": len(sig_cells),
           "significant_hill": len(sig_hill),
           "significant_sample": len(sig_samp),
           "both_signs_significant": both_signs_significant}

    if live:
        import base64
        blob = json.dumps(out, sort_keys=True).encode()
        wid = c.call("POST", "/worlds", {"session_id": sid, "name": "S5-sweep",
                                         "seed_root": 5,
                                         "sharing_policy": "ISOLATED"})[1]["world_id"]
        c.call("POST", "/worlds/%s/start" % wid, {})
        st, art = c.call("POST", "/worlds/%s/artifacts" % wid,
                         {"kind": "observation_payload",
                          "data_b64": base64.b64encode(blob).decode(),
                          "expected_blob_hash": "sha256:" +
                          hashlib.sha256(blob).hexdigest(),
                          "meta": {"role": "MODERATOR_SWEEP"}})
        print("\n  sweep fossilised: %s %s" % (st, art.get("blob_hash", "")[:26]))
        out["fossil"] = art.get("blob_hash")

    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print("  rows: %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
