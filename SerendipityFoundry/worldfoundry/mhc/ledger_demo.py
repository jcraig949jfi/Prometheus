"""Empirical demonstration of the admission-rights ledger guarantee -- and of
the exploit that PRECONDITION 1 exists to prevent.

Simulates null candidates as anytime-valid wealth processes built from fair
conditional ranks (the exact field statistic: P(top among m=3 refs) = 1/4
under H0, mixture betting as in stats.py).

  D1  GUARANTEE HOLDS under registration-before-evidence:
      register candidates at fixed K, then generate evidence; realized
      false admissions vs the ledger bound.
  D2  THE PEEKING EXPLOIT: observe all wealth trajectories FIRST, purchase
      only for observed crossers at K = observed peak; realized false
      admissions exceed ledger spend by ~K-fold. This is why the ledger
      REFUSES evidence for unregistered candidates.
  D3  MECHANICS: family over-reservation refused; post-registration K
      change impossible; selection/admission evidence overlap refused;
      entitlement exhaustion refused.

Run:  python -m mhc.ledger_demo
"""
from __future__ import annotations

from fractions import Fraction

from wforge.world import stream
from .ledger import AdmissionLedger, LedgerError
from .stats import LAM_GRID


def null_wealth_trajectory(seed: int, n_blocks: int):
    """Anytime wealth peak of a null candidate: fair rank betting, m=3 refs
    (top pays 4x), mixture over LAM_GRID -- identical arithmetic to the field
    statistic in stats.py."""
    r = stream("ledger-null", seed)
    wealths = [Fraction(1)] * len(LAM_GRID)
    peak = Fraction(1)
    for _ in range(n_blocks):
        top = r.below(4) == 0                      # P(top)=1/4 under H0
        for i, lam in enumerate(LAM_GRID):
            wealths[i] *= (1 - lam) + (lam * 4 if top else Fraction(0))
        mix = sum(wealths) / len(LAM_GRID)
        if mix > peak:
            peak = mix
    return peak


def main():
    print("=" * 72)
    print("ADMISSION-RIGHTS LEDGER -- GUARANTEE AND EXPLOIT DEMONSTRATION")
    print("=" * 72)
    N, L = 100_000, 64
    print(f"simulating {N} NULL candidates, {L} blocks each ...")
    peaks = [null_wealth_trajectory(s, L) for s in range(N)]

    # D1: honest use -----------------------------------------------------
    print("\nD1. REGISTRATION-BEFORE-EVIDENCE (the guarantee)")
    led = AdmissionLedger(Fraction(1, 10))
    led.open_family("famA", Fraction(1, 10), origin="preregistered",
                    co_signed=True)   # full-budget reservation needs co-signature
    K = 200
    n_reg = 20                                     # 20 x 1/200 = 0.1 exactly
    for i in range(n_reg):
        led.register_candidate(f"c{i}", "famA", K, frozenset({f"sel{i}"}),
                               block_budget=64)
    false_adm = 0
    for i in range(n_reg):
        c = led.candidates[f"c{i}"]
        c["wealth_peak"] = peaks[i]                # evidence generated AFTER
        if peaks[i] >= K:
            false_adm += 1
    s = led.spend_summary()
    print(f"    registered {n_reg} candidates at K={K} "
          f"(bound = {n_reg}/{K} = {float(s['false_admission_expectation_bound']):.3f})")
    print(f"    realized false admissions: {false_adm}   "
          f"(guarantee: expected <= {float(led.alpha_life):.2f})")

    # D2: the exploit ----------------------------------------------------
    print("\nD2. THE PEEKING EXPLOIT (what refusal prevents)")
    crossers = [(i, p) for i, p in enumerate(peaks) if p >= 100]
    exploit_spend = sum(Fraction(1, int(p)) for _, p in crossers)
    print(f"    null candidates observed : {N}")
    print(f"    peaks >= 100 (would-be 'admissions' bought post hoc at "
          f"K = observed peak): {len(crossers)}")
    print(f"    ledger spend if post-hoc purchase were allowed: "
          f"{float(exploit_spend):.4f}")
    print(f"    -> {len(crossers)} false admissions for ~{float(exploit_spend):.3f} "
          f"units: the expectation bound is violated ~{int(len(crossers)/max(float(exploit_spend),1e-9))}-fold.")
    print("    THE LEDGER REFUSES THIS: evidence for an unregistered candidate")
    print("    raises LedgerError; K is immutable after registration.")

    # D3: mechanics ------------------------------------------------------
    print("\nD3. MECHANICAL REFUSALS")
    led2 = AdmissionLedger(Fraction(1))
    led2.open_family("f1", Fraction(1, 5), origin="human")
    checks = []
    try:
        led2.open_family("f2", Fraction(1, 2), origin="llm-mining")
        checks.append(("family land-grab", "ACCEPTED (BUG)"))
    except LedgerError:
        checks.append(("family land-grab (>25% remaining, no co-sign) refused", "OK"))
    led2.register_candidate("x", "f1", 200, frozenset({"selblk"}), block_budget=64)
    try:
        led2.register_candidate("x", "f1", 500, frozenset(), block_budget=64)
        checks.append(("K mutation", "ACCEPTED (BUG)"))
    except LedgerError:
        checks.append(("post-registration K change refused", "OK"))
    try:
        led2.register_candidate("lowK", "f1", 10, frozenset(), block_budget=64)
        checks.append(("K below floor", "ACCEPTED (BUG)"))
    except LedgerError:
        checks.append(("K below preregistered floor (K_MIN=100) refused", "OK"))
    try:
        led2.register_candidate("unwin", "f1", 10**9, frozenset(), block_budget=8)
        checks.append(("unwinnable K", "ACCEPTED (BUG)"))
    except LedgerError:
        checks.append(("unreachable K within block budget refused", "OK"))
    try:
        led2.submit_evidence("x", "selblk", Fraction(3), beacon_round_seq=99)
        checks.append(("selection/admission overlap", "ACCEPTED (BUG)"))
    except LedgerError:
        checks.append(("selection/admission evidence overlap refused", "OK"))
    try:
        led2.submit_evidence("x", "blk1", Fraction(3), beacon_round_seq=0)
        checks.append(("pre-registration beacon", "ACCEPTED (BUG)"))
    except LedgerError:
        checks.append(("evidence without post-registration beacon refused", "OK"))
    try:
        led2.submit_evidence("ghost", "b1", Fraction(3), beacon_round_seq=99)
        checks.append(("unregistered evidence", "ACCEPTED (BUG)"))
    except LedgerError:
        checks.append(("evidence for unregistered candidate refused", "OK"))
    led2.submit_evidence("x", "blk1", Fraction(3), beacon_round_seq=99)
    led2.register_candidate("z", "f1", 200, frozenset(), block_budget=64)
    try:
        led2.submit_evidence("z", "blk1", Fraction(3), beacon_round_seq=99)
        checks.append(("cross-candidate block reuse", "ACCEPTED (BUG)"))
    except LedgerError:
        checks.append(("one-time-use block: cross-candidate reuse refused", "OK"))
    for msg, ok in checks:
        print(f"    [{ok}] {msg}")
    print("\n" + "=" * 72)
    print("LEDGER DEMONSTRATION COMPLETE")
    print("=" * 72)


if __name__ == "__main__":
    main()
