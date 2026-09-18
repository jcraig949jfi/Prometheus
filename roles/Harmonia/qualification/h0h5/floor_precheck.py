"""Structural-floor precheck any corpus must pass before issue.  FP-1.0.0  2026-09-18 (HARM-29).

Set in RULING_REPLICATE_C3_3_H1BETA_D3CUT_2026-09-10.md 3f (R-C3-1, R-C3-3):
before a corpus is issued, print its SUPPORT SIZE (distinct attained values of
the per-unit statistic), p_mode (the modal mass) and f (the non-degenerate
fraction), and refuse a corpus with p_mode > 0.50. A detector run over a
corpus that sits on a structural floor measures the floor, not the world:
C3-2's 120 acquired rules were 0.000 on every IC sample (f = 0.000,
p_mode = 1.000, support 1) and the D3-over-C3-acq result was STRUCTURALLY
VOID (RULING_C3_2_FINAL_2026-09-10.md).

    python floor_precheck.py                      reproduces C3-2's f = 0.000 from the
                                                  committed readout (positive control of
                                                  the refusal) and a clean synthetic PASS
    floor_precheck(values, lo, hi)                the library call

DEGENERATE means the unit's statistic sits AT the boundary of its attainable
range on every sample it has (all-zero or all-one accuracy); it is a structural
zero (or one), not a measurement. R-C3-1's hard floor at n = 8 is 0.688:
the smallest p_mode a corpus of eight can show while still being ruled on.
"""
from __future__ import annotations

import json
import math
import os
import sys
from collections import Counter

FP_VERSION = "FP-1.0.0"
P_MODE_MAX = 0.50
HARD_FLOOR_N8 = 0.688


class CorpusRefused(Exception):
    pass


def floor_precheck(values, lo=0.0, hi=1.0, per_sample=None, tol=1e-12) -> dict:
    """values: one statistic per unit (e.g. a rule's mean accuracy). per_sample:
    optional list of per-unit sample lists; a unit is DEGENERATE when every one
    of its samples sits at lo or at hi (falls back to `values` when absent).
    Raises CorpusRefused when p_mode > P_MODE_MAX. Never raises on f: f is
    reported and the consumer's rule (corpus size = ceil(120 / f)) reads it."""
    n = len(values)
    if n == 0:
        raise CorpusRefused("empty corpus: nothing could be checked")
    rounded = [round(float(v), 12) for v in values]
    support = sorted(set(rounded))
    mode_val, mode_n = Counter(rounded).most_common(1)[0]
    p_mode = mode_n / n
    if per_sample is None:
        per_sample = [[v] for v in values]

    def degenerate(samples):
        return all(abs(float(s) - lo) <= tol or abs(float(s) - hi) <= tol for s in samples)
    n_deg = sum(1 for s in per_sample if degenerate(s))
    f = (n - n_deg) / n
    out = {"version": FP_VERSION, "n_units": n, "support_size": len(support),
           "p_mode": p_mode, "mode_value": mode_val, "n_degenerate": n_deg,
           "non_degenerate_fraction_f": f, "attainable_range": [lo, hi],
           "corpus_size_for_120_nondegenerate": (math.ceil(120 / f) if f > 0 else None),
           "p_mode_max": P_MODE_MAX,
           "label": ("STRUCTURAL_FLOOR" if p_mode > P_MODE_MAX else "PASS")}
    if p_mode > P_MODE_MAX:
        raise CorpusRefused("p_mode %.3f > %.2f (mode value %s on %d of %d units; support %d; f %.3f): "
                            "the corpus sits on a structural floor and a detector over it measures the "
                            "floor" % (p_mode, P_MODE_MAX, mode_val, mode_n, n, len(support), f))
    return out


def c3_2_acq_rows(readout_path):
    with open(readout_path, encoding="utf-8") as fh:
        d = json.load(fh)
    rows = [r for r in d["table"] if r.get("arm") == "C3-acq"]
    return rows


def main(argv):
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(here, "..", "..", "..", ".."))
    readout = argv[1] if len(argv) > 1 else os.path.join(root, "archaeon", "docs", "h0h5", "C3_2_READOUT.json")
    rows = c3_2_acq_rows(readout)
    vals = [r["mean"] for r in rows]
    samples = [r["accuracy_by_sample"] for r in rows]
    print("C3-2 C3-acq: %d rules" % len(rows))
    try:
        floor_precheck(vals, 0.0, 1.0, samples)
        print("  UNEXPECTED PASS -- the positive control of the refusal FAILED")
        return 1
    except CorpusRefused as e:
        print("  REFUSED as expected: %s" % e)
    # the numbers, for the record (computed without the raise)
    n = len(vals)
    n_deg = sum(1 for s in samples if all(x in (0.0, 1.0) for x in s))
    print("  support_size %d  p_mode %.3f  f %.3f" % (len(set(vals)), Counter(vals).most_common(1)[0][1] / n, (n - n_deg) / n))
    # negative control: a clean synthetic corpus passes and reports f = 1
    import random
    rng = random.Random(29)
    clean = [rng.uniform(0.2, 0.8) for _ in range(120)]
    rec = floor_precheck(clean, 0.0, 1.0)
    print("  clean synthetic: %s support %d p_mode %.3f f %.3f corpus_for_120 %s"
          % (rec["label"], rec["support_size"], rec["p_mode"], rec["non_degenerate_fraction_f"],
             rec["corpus_size_for_120_nondegenerate"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
