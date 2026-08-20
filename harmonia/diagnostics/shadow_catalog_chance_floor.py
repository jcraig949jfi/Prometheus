"""Chance floor for the SHADOW_CATALOG survivor population.

The kill-resurrection audit found 0/92 resurrections and 84/84 SHADOW_CATALOG records
re-evaluating TRUE. So the survivors are genuinely true claims that were never promoted.
That raises the question the Metabolization Probe actually needs answered:

    are these claims true because they carry signal, or true by coincidence?

`relation`s like equal_mod_2 hold on ~half of all random integer pairs. A survivor
population sitting at its chance floor is not a mislabeled asset -- it is a correctly
labeled worthless one, and the zero-promotion streak is the gate behaving correctly.

Method: the random-pairing null. For each relation family, hold the left operands fixed
and permute the right operands across records (breaking any real pairing while preserving
both marginal distributions), then recompute the hold rate. Compare observed vs null.

This is the null `theseus/scoring/content_aware_promote.py` implements and that Harmonia A
reported is not wired into the gate (REVIEW_20260812_syntactic_router.md section 1). Here
it is run against the historical record rather than the live gate.

Usage:
  PYTHONPATH=. python harmonia/diagnostics/shadow_catalog_chance_floor.py

Harmonia C, 2026-08-19.
"""

from __future__ import annotations

import json
import os
import random
from collections import defaultdict

from harmonia.diagnostics.kill_resurrection_audit import evaluate

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SAMPLE = os.path.join(REPO, "pivot", "promoted_triage_sample.jsonl")
SEED = 20260819
N_PERM = 2000


def main():
    rows = [json.loads(l) for l in open(SAMPLE, encoding="utf-8") if l.strip()]

    # Only the two-operand kinds have a well-defined random-pairing null.
    pairs = defaultdict(list)
    for r in rows:
        rec = r["record"]
        if rec.get("claim_kind") not in ("invariant_equality", "mutation"):
            continue
        p = rec["claim_payload"]
        a, b, rel = p.get("value_a"), p.get("value_b"), p.get("relation")
        if a is None or b is None or evaluate(rel, a, b) is None:
            continue
        pairs[rel].append((float(a), float(b)))

    rng = random.Random(SEED)
    print("SHADOW_CATALOG chance floor -- random-pairing null")
    print(f"sample: {SAMPLE}   seed={SEED}  permutations={N_PERM}")
    print("=" * 78)
    print(f"{'relation':<18}{'n':>5}{'observed':>11}{'null (mean)':>13}"
          f"{'null 95% hi':>13}{'verdict':>12}")
    print("-" * 78)

    tot_obs = tot_null = tot_n = 0
    for rel, ps in sorted(pairs.items(), key=lambda kv: -len(kv[1])):
        n = len(ps)
        obs = sum(bool(evaluate(rel, a, b)) for a, b in ps) / n
        bs = [b for _, b in ps]
        null_rates = []
        for _ in range(N_PERM):
            sh = bs[:]
            rng.shuffle(sh)
            null_rates.append(
                sum(bool(evaluate(rel, a, b)) for (a, _), b in zip(ps, sh)) / n)
        null_rates.sort()
        mean_null = sum(null_rates) / len(null_rates)
        hi = null_rates[int(0.95 * len(null_rates)) - 1]
        verdict = "AT CHANCE" if obs <= hi else "above null"
        print(f"{rel:<18}{n:>5}{obs:>10.1%}{mean_null:>13.1%}{hi:>13.1%}{verdict:>12}")
        tot_obs += obs * n
        tot_null += mean_null * n
        tot_n += n

    print("-" * 78)
    print(f"{'POOLED':<18}{tot_n:>5}{tot_obs/tot_n:>10.1%}{tot_null/tot_n:>13.1%}")
    print()
    print("Reading: a relation whose observed hold rate sits inside the random-pairing")
    print("null's 95% band produces survivors that are true by coincidence. Promoting")
    print("them would be the error; NOT promoting them is the gate working.")
    print()
    print("Corroboration from the substrate's own census")
    print("(theseus/corpus_health_report.md, 394,623 records):")
    print("  equal_mod_2   67.2% categorical      abs_diff_le_*  67.0%")
    print("  divides       50.7%                  equal           2.4%")
    print("  -- `equal`, the only relation that is hard to satisfy by chance, is also")
    print("     the one that almost never holds. The substrate's yield is concentrated")
    print("     in exactly the relations a coin could pass.")


if __name__ == "__main__":
    main()
