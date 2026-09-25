"""
AETH-00A -- tests 20 and 25: preregistered directional arbitration-bias
diagnostics. CPU-only, no Runpod spending.

PREREGISTRATION (fixed here, before any result below is interpreted):

- Measured event, per (arity, direction-combo, slot): among N
  independent contests of that arity where the slot's direction is one
  of the `arity` competing directions, the number of times that slot's
  proposal wins.
- Null model: each contest is drawn independently (fresh random seed
  and tick per contest, fixed target and fixed slot source positions);
  under the null of no directional bias, each of the `arity` competing
  proposals wins with probability exactly 1/arity, so win count per
  slot ~ Binomial(N, 1/arity).
- Strata: every combination of contest ARITY in {2,3,4} and the actual
  SET of competing directions (all C(4,2)=6 pairs, C(4,3)=4 triples,
  C(4,4)=1 quadruple -- 11 strata, 28 (stratum, slot) sites total).
  Never pooled across arity or direction-combo (that pooling is exactly
  what test 20 says is insufficient).
- Sample size: N = 300 contests per stratum (fixed here; not tuned
  after seeing results).
- Test: exact two-sided binomial test per site against p = 1/arity.
- Multiple-comparison handling: Bonferroni correction across all 28
  sites; family-wise alpha = 0.01, so per-site alpha = 0.01 / 28.
- Non-claim: failing to reject H0 for a site is NOT evidence that site
  is unbiased; it only means this sample did not detect deviation at
  this power. No "five-nines" or similar language is used here.
"""

import math
import random

from reference import oracle as ok

N_PER_STRATUM = 300
FAMILYWISE_ALPHA = 0.01
DIRECTIONS = (0, 1, 2, 3)  # 0=N, 1=E, 2=S, 3=W (AETHER_SPEC.md)
TARGET = (2, 2)
H = W = 5  # large enough that no direction-combo aliases (ordinary-run size)


def _direction_that_targets(src, target):
    for d in DIRECTIONS:
        if ok.neighbor(src[0], src[1], H, W, d) == target:
            return d
    raise AssertionError("no direction maps src to target")


def _slot_source(slot_direction):
    """The physical site at TARGET's `slot_direction` neighbor position."""
    return ok.neighbor(TARGET[0], TARGET[1], H, W, slot_direction)


def _run_one_contest(rng, combo):
    seed = rng.randrange(1 << 64)
    tick = rng.randrange((1 << 64) - 1)
    proposals = []
    for slot in combo:
        src = _slot_source(slot)
        proposals.append(ok.Proposal(src, TARGET, 0, slot))  # value=slot, for bookkeeping only
    contests = {(TARGET, 0): proposals}
    winner, _priority = ok.arbitrate(seed, tick, contests)[(TARGET, 0)]
    return winner.value  # the winning slot label


def _exact_two_sided_binomial_pvalue(k, n, p):
    observed = math.comb(n, k) * (p**k) * ((1 - p) ** (n - k))
    total = 0.0
    for i in range(n + 1):
        pi = math.comb(n, i) * (p**i) * ((1 - p) ** (n - i))
        if pi <= observed * (1 + 1e-9):
            total += pi
    return min(total, 1.0)


def run_diagnostic(rng_seed=20260920, n_per_stratum=N_PER_STRATUM):
    """Returns the full stratified report; never asserts fairness."""
    from itertools import combinations

    rng = random.Random(rng_seed)
    strata = []
    for arity in (2, 3, 4):
        for combo in combinations(DIRECTIONS, arity):
            strata.append(combo)
    num_cells = sum(len(combo) for combo in strata)
    per_cell_alpha = FAMILYWISE_ALPHA / num_cells

    report = {"n_per_stratum": n_per_stratum, "per_cell_alpha": per_cell_alpha, "strata": []}
    for combo in strata:
        arity = len(combo)
        counts = {slot: 0 for slot in combo}
        for _ in range(n_per_stratum):
            counts[_run_one_contest(rng, combo)] += 1
        p_null = 1.0 / arity
        sites = []
        for slot in combo:
            k = counts[slot]
            pval = _exact_two_sided_binomial_pvalue(k, n_per_stratum, p_null)
            sites.append(
                {
                    "slot": slot,
                    "wins": k,
                    "n": n_per_stratum,
                    "p_null": p_null,
                    "p_value": pval,
                    "flagged": pval < per_cell_alpha,
                }
            )
        report["strata"].append({"combo": combo, "sites": sites})
    return report


def test_diagnostic_protocol_runs_and_produces_full_stratified_report():
    # Smaller N here for CI speed; the frozen N=300 report is generated
    # once and its summary recorded in AETH-00A_RECEIPT.md, not re-run on
    # every test invocation with a different sample size.
    report = run_diagnostic(rng_seed=1, n_per_stratum=60)
    assert len(report["strata"]) == 11  # 6 pairs + 4 triples + 1 quadruple
    total_cells = sum(len(s["sites"]) for s in report["strata"])
    assert total_cells == 28
    for stratum in report["strata"]:
        n_total = sum(site["wins"] for site in stratum["sites"])
        assert n_total == 60  # every contest produced exactly one winner
        for site in stratum["sites"]:
            assert 0.0 <= site["p_value"] <= 1.0


if __name__ == "__main__":
    rpt = run_diagnostic()
    flagged = [
        (s["combo"], c["slot"], c["wins"], c["p_value"])
        for s in rpt["strata"]
        for c in s["sites"]
        if c["flagged"]
    ]
    print(f"n_per_stratum={rpt['n_per_stratum']} per_cell_alpha={rpt['per_cell_alpha']:.6f}")
    print(f"strata={len(rpt['strata'])} sites={sum(len(s['sites']) for s in rpt['strata'])}")
    print(f"flagged sites (p < per_cell_alpha): {len(flagged)}")
    for combo, slot, wins, p in flagged:
        print(f"  combo={combo} slot={slot} wins={wins} p={p:.6g}")
