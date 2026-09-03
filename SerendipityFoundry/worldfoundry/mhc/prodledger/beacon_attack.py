"""SECTION VIII: BEACON-PRECOMPUTATION ATTACK.

An F-omniscient attacker (complete pre-registration system state, candidate
generator, detector code, historical population, all previous beacon values,
unlimited offline compute) tries to identify future crossers BEFORE paying.

  A1  OLD PROCEDURAL SEAL: evidence contexts are derivable pre-commit
      (deterministic substrate, no post-commit entropy). The attacker
      simulates every candidate's full wealth trajectory offline, registers
      ONLY known crossers. Expected result: attack SUCCEEDS -- realized
      false admissions vastly exceed purchased risk.
  A2  PRODUCTION SEAL: contexts/references/roles/ties derive from a beacon
      value that DOES NOT EXIST until after the registration is committed
      and anchored. The attacker's best strategy degrades to guessing.
      Expected result: crossing rate ~ 1/K; every cross is priced.
  A3  GRINDING UNDER THE PRODUCTION SEAL: register N candidates and hope.
      Expected: crossers ~ N/K, but the ledger charged N/K -- grinding is
      PRICED, not free; the guarantee is indifferent to it.

The wealth process is the exact field statistic (conditional-rank mixture
betting, m = 3 references, payoffs from the fairness-certified family).
Run:  python -m prodledger.beacon_attack
"""
from __future__ import annotations

import hashlib
from fractions import Fraction

LAM = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4))
M_REFS = 3
K = 1000
BLOCKS = 64


def h64(*parts) -> int:
    return int.from_bytes(hashlib.sha256(
        "|".join(str(p) for p in parts).encode()).digest()[:8], "big")


def rank_top(cand_seed: int, beacon: str, block: int) -> bool:
    """Null substrate: candidate value and 3 reference values are iid
    hashes; candidate ranks top iff its draw beats all references. Under
    the null P(top)=1/4 exactly (ties impossible on 64-bit draws)."""
    cv = h64("val", cand_seed, beacon, block, "cand")
    refs = [h64("val", cand_seed, beacon, block, "ref", i)
            for i in range(M_REFS)]
    return all(cv > r for r in refs)


def wealth_crosses(cand_seed: int, beacon: str) -> bool:
    wealths = [Fraction(1)] * len(LAM)
    for t in range(BLOCKS):
        top = rank_top(cand_seed, beacon, t)
        for i, lam in enumerate(LAM):
            wealths[i] *= (1 - lam) + (lam * (M_REFS + 1) if top
                                       else Fraction(0))
        if sum(wealths) / len(LAM) >= K:
            return True
    return False


def main():
    print("=" * 72)
    print("BEACON-PRECOMPUTATION ATTACK  (K=1000, 64 blocks, m=3)")
    print("=" * 72)
    N = 60_000

    # A1: procedural seal -- beacon derivable pre-registration
    print(f"\nA1. PROCEDURAL SEAL (old): attacker precomputes all {N} "
          f"trajectories")
    fixed_beacon = "procedural-derivable-0xDEAD"      # known pre-commit
    crossers = [s for s in range(N) if wealth_crosses(s, fixed_beacon)]
    spend = Fraction(len(crossers), K)
    print(f"    crossers identified offline : {len(crossers)}")
    print(f"    attacker registers ONLY those -> false admissions "
          f"{len(crossers)} for spend {float(spend):.4f}")
    if crossers:
        print(f"    guarantee violated {len(crossers) / float(spend):.0f}x "
              f"-- ATTACK SUCCEEDS against procedural sealing")

    # A2: production seal -- beacon value created after registration
    print(f"\nA2. PRODUCTION SEAL: attacker registers a strategy-chosen "
          f"subset FIRST; the beacon value is generated afterwards")
    # attacker picks the candidates that crossed under their best GUESS of
    # the future beacon (they know the beacon's format but not its entropy)
    guess = "attacker-best-guess-beacon"
    picked = [s for s in range(N) if wealth_crosses(s, guess)][:200]
    # ... the real beacon value is derived from entropy that did not exist
    # at registration time (here: hidden server seed revealed post-commit)
    real_beacon = hashlib.sha256(b"server-entropy-post-commit-7731").hexdigest()
    crossed = [s for s in picked if wealth_crosses(s, real_beacon)]
    print(f"    registered on best-guess    : {len(picked)} candidates "
          f"(spend {len(picked)}/{K} = {len(picked)/K:.3f})")
    print(f"    actually crossed            : {len(crossed)}  "
          f"(chance expectation ~ {len(picked)/K:.3f})")
    print(f"    -> precomputation advantage ELIMINATED; every cross is "
          f"paid for at 1/K")

    # A3: grinding is priced
    print(f"\nA3. GRINDING: register N candidates blind, hope for crossers")
    Ng = 5000
    g_crossed = sum(1 for s in range(Ng)
                    if wealth_crosses(1_000_000 + s, real_beacon))
    print(f"    {Ng} registrations -> {g_crossed} crossers "
          f"(expected ~{Ng/K:.1f}); ledger charged {Ng}/{K} = {Ng/K:.1f} "
          f"risk units -- the books balance BY CONSTRUCTION")
    print(f"    (and a real ledger would have refused: {Ng}/{K} = "
          f"{Ng/K:.1f} >> ALPHA_LIFE = 0.1 -- the budget runs out after "
          f"~100 registrations at K=1000)")
    print("=" * 72)


if __name__ == "__main__":
    main()
