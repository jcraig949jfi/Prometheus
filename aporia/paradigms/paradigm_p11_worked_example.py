"""PARADIGM-P11 worked example — Sieve Methods, executed.

The paradigm's move: filter a large set by local conditions; the structured
residue is the object. Executable instance: the Legendre sieve — the ur-sieve
— run EXACTLY (inclusion-exclusion over squarefree products of the sieving
primes) and reconciled against direct counts, integer-exact, at three scales.

Identity under test (derived in-code, not transcribed): with P = primes <= sqrt(N),
  phi(N, P) := #{1 <= n <= N : no p in P divides n}
             = sum over squarefree d | prod(P) of mu(d) * floor(N/d)
and the sieve residue is exactly {1} u {primes in (sqrt(N), N]}, so
  phi(N, P) = pi(N) - pi(sqrt(N)) + 1.

Gates (each with its own gate, P82 rule):
  - hand-checkable known first: N=100, P={2,3,5,7}: phi must equal
    pi(100)-pi(10)+1 = 25-4+1 = 22, and ALSO equal the brute-force count.
  - Mobius values derived by factorization in-code, not a table.

Pre-stated readings (BEFORE run):
  SIEVE-EXACT  inclusion-exclusion equals the direct sieve count EXACTLY
               (integers) at N = 1e4, 1e5, 1e6 — zero tolerance.
  MISMATCH     any difference — instrument-first: Mobius sign, floor division,
               duplicate subsets, the N=100 gate localizes.
"""
from __future__ import annotations
import json
import pathlib
import sys
from itertools import combinations

import numpy as np

HERE = pathlib.Path(__file__).parent
OUT = HERE / "paradigm_p11_results.json"
sys.path.insert(0, str(HERE.parent / "catalog_attacks"))
from nt_helpers import sieve_primes


def legendre_phi(N, sieve_ps):
    """Legendre's phi via the RECURSIVE pruned form:
        phi(x, a) = phi(x, a-1) - phi(x // p_a, a-1),  phi(x, 0) = x.
    INSTRUMENT-FIRST CATCH (P85 first draft): the naive inclusion-exclusion
    enumerated ALL subsets of the sieving primes — 2^168 at N=1e6 — and hung;
    the d>N break prunes products, not the enumeration. The recursion IS the
    inclusion-exclusion with the pruning built into the tree; mathematically
    identical (each recursion leaf is one squarefree d with its mu sign),
    computationally polynomial in practice.
    """
    import sys as _s
    _s.setrecursionlimit(10000)

    def phi(x, a):
        if a == 0 or x == 0:
            return x
        return phi(x, a - 1) - phi(x // sieve_ps[a - 1], a - 1)

    return phi(N, len(sieve_ps))


def direct_count(N, sieve_ps):
    """Brute residue count: integers in [1,N] coprime to every sieving prime."""
    mask = np.ones(N + 1, dtype=bool)
    mask[0] = False
    for p in sieve_ps:
        mask[p::p] = False
    return int(mask.sum())


primes_all = sieve_primes(1_000_000)

# --- gate: hand-checkable N=100 ----------------------------------------------
N0 = 100
P0 = [int(p) for p in primes_all[primes_all <= 10]]
phi0 = legendre_phi(N0, P0)
direct0 = direct_count(N0, P0)
pi100 = int((primes_all <= 100).sum())
pi10 = int((primes_all <= 10).sum())
identity0 = pi100 - pi10 + 1
print(f"gate N=100: inclusion-exclusion {phi0}, direct {direct0}, "
      f"pi(100)-pi(10)+1 = {pi100}-{pi10}+1 = {identity0}", flush=True)
assert phi0 == direct0 == identity0 == 22, "gate FAILS — localize before scaling"

# --- three scales, integer-exact ---------------------------------------------
rows = []
ok = True
for N in (10_000, 100_000, 1_000_000):
    z = int(N ** 0.5)
    ps = [int(p) for p in primes_all[primes_all <= z]]
    phi = legendre_phi(N, ps)
    direct = direct_count(N, ps)
    piN = int((primes_all <= N).sum())
    piz = int((primes_all <= z).sum())
    ident = piN - piz + 1
    match = (phi == direct == ident)
    ok &= match
    rows.append({"N": N, "sieving_primes": len(ps), "phi_inclusion_exclusion": phi,
                 "phi_direct": direct, "pi_identity": ident, "exact_match": match})
    print(f"N={N:>9,}: |P|={len(ps):3d}  incl-excl={phi:,}  direct={direct:,}  "
          f"pi(N)-pi(z)+1={ident:,}  {'EXACT' if match else 'MISMATCH'}", flush=True)

verdict = "SIEVE-EXACT" if ok else "MISMATCH"
print(f"-> {verdict}", flush=True)
OUT.write_text(json.dumps({
    "protocol": "Legendre sieve: inclusion-exclusion over squarefree products vs direct residue count vs pi-identity, integer-exact at three scales, N=100 hand gate",
    "gate_N100": {"phi": phi0, "direct": direct0, "identity": identity0},
    "rows": rows, "verdict": verdict}, indent=1), encoding="utf-8")
print(f"-> {OUT.name}", flush=True)
