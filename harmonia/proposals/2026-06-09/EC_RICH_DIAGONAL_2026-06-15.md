# EC Rich-Invariant Diagonal Mining — Results

**Author:** Harmonia_M2_D
**Date:** 2026-06-15
**Status:** COMPLETE — clean kill (0 novel within-object laws), instrument behaved as designed
**Target:** B_RESULTS §7 panel-ranked **#1 live target** — EC same-object diagonal, widened invariants
**Instrument:** `D:\Prometheus\harmonia\primitives\lattice_void_miner.py` (`evaluate_diagonal_lattice`, now with the T1b/D_THEOREM upgrade)
**Driver:** `D:\Prometheus\harmonia\experiments\ec_rich_diagonal_sweep.py`
**Artifact:** `D:\Prometheus\harmonia\experiments\ec_rich_diagonal_results.json`
**Validator:** `D:\Prometheus\harmonia\experiments\validate_ec_rich_diagonal.py`

---

## §0 Headline

The 2026-06-10 EC diagonal used 4 integer invariants and surfaced one law
(`torsion | tamagawa_product`). This pass widens to **9** (adds `sha_an`,
`num_bad_primes`, `cm`, `signD`, `conductor_radical`) with Mazur injected.

**Novel within-object laws found = 0.** The honest number. Every one of the 176
D_JOINT candidates is accounted for, and the survivor filter (perm-null 0 ∧ not
thin ∧ no known-math tag) returns **empty**.

The widening was not wasted: it produced one *new definitional rediscovery*
family and exercised the new D_THEOREM tier on real data.

---

## §1 The lattice and the partition

```
cells                              10,368   (9·8 ordered inv-pairs × 6f × 6g × 4rel)
exact voids                           777
  D_MARGINAL  (catalog-only marginal)  503
  D_THEOREM   (Mazur-protected marginal) 98   <- new T1b/D_THEOREM tier at work
  D_JOINT     (candidate joint law)     176
```

**D_JOINT partition (perm-null = P(survives column-shuffle); 0.0 = max signal):**

| Tag | n | What it is |
|---|---|---|
| DEFINITIONAL | 41 | `conductor` ↔ `conductor_radical`: `rad(N) \| N` and `N == rad(N) (mod 2)`, across all sign/parity-preserving operator variants. One fact (shared prime support) in many guises. |
| LITERATURE (Lorenzini 2011) | 9 | `torsion \| tamagawa_product`, sign-variants. The **same** law as the 4-invariant pass — re-found, not new. |
| DEGENERATE | 107 | any pair containing `cm` (= 0 for 995/1000 curves → absorbing-element facts). |
| LOW-INFO | 19 | `signD` ∈ {−1,1} or `sha_an` = 1 for 962/1000 — near-constant columns. |
| **untagged survivors** | **0** | — |

Live recount (independent of the sweep, `validate_ec_rich_diagonal.py`):
`rad(N)|N` **1000/1000**, `N≡rad(N) (mod 2)` **1000/1000**, `torsion|∏c_p`
**1000/1000**.

**The permutation null partitions the 176 cleanly:** exactly the **50**
DEFINITIONAL+LITERATURE cells have perm-null **0.0** (maximal joint signal —
column-shuffle always breaks them), and **all 126** perm-null > 0 cells are the
DEGENERATE/LOW-INFO `cm`/`signD`/`sha_an` columns. So the perm-null is not
redundant with the tagger: it independently isolates the two real law-families
from the near-constant noise. The triviality of the 50 is in the *explanation*
(they are definitional / known), not in the signal — which is exactly maximal.

---

## §2 Failure shapes (not verdict lines)

Per the failure-signature doctrine, what the void field's *shape* says:

1. **The only D_JOINT "signal" the rich fields added is the conductor/radical
   pair, and it is definitional.** `N` and `rad(N)` share their prime support by
   construction, so two laws fall out for free — `rad(N)|N` (divides) and
   `N≡rad(N) (mod 2)` (parity, since `2|N ⟺ 2|rad(N)`). These are not curve
   arithmetic; they are facts about the radical operation. A diagonal miner
   *will* surface them on any catalog carrying both a number and its radical.

2. **Sign/operator fan-out inflates the candidate count ~10×.** One underlying
   law generates a whole family because the operators `identity/abs/neg/
   sq_mod_100` preserve parity and `divides` is sign-invariant
   (`b % (−a) == 0 ⟺ a|b`). The conductor/radical fact alone produced **41**
   D_JOINT cells; `torsion|∏c_p` produced **9**. A naive "count untagged
   D_JOINT" reads 42 phantom discoveries where there are 2 laws + degeneracy.
   The tagger must recognise the *family*, not the identity-on-identity
   representative. **(FP nomination for Harmonia E's atlas: "sign-variant
   fan-out" — a single relation re-counted N× under operators that commute with
   it. Detector: canonicalise each candidate to (invariant-pair, relation,
   parity-class) before counting.)**

3. **Low-cardinality rich fields are void factories, not law sources.** `cm`
   (995/1000 zero), `signD` (2-valued), `sha_an` (962/1000 = 1) generated
   126/176 of the D_JOINT candidates and **none** survive the thin-column /
   absorbing-element guards. Adding fields raises coverage but not law-yield
   when the fields are near-constant — selection of *which* invariants to widen
   matters more than the count.

4. **The D_THEOREM tier earned its keep.** 98 marginal voids involving `torsion`
   are now tagged population-true-via-Mazur rather than over-read as catalog
   selection — the live payoff of the 2026-06-15 T1b upgrade, on a different
   lattice than the one it was built for.

---

## §3 What did NOT happen (kill paths exhausted)

- No invariant pair produced a maximal-signal joint void that resisted a
  definitional / literature / degeneracy explanation.
- `sha_an` (the BSD-square field, the most "interesting" addition) yielded only
  near-constant LOW-INFO voids — its perfect-square structure is a *single*-
  invariant fact, invisible to a 2-invariant diagonal. Mining it needs a
  unary-property miner, not the pair lattice. (Logged; not a void-miner job.)
- `num_bad_primes` ↔ `conductor_radical` (count vs product of the same prime
  set) produced only primorial size-facts, no tight relation.

---

## §4 Disposition

a3 cross-product: dead (product-measure theorem). EC diagonal, 4 invariants:
one law (`torsion|∏c_p`). EC diagonal, 9 invariants: that same law + one
definitional rediscovery family, **0 novel**. The diagonal direction is not
exhausted of *method* but the EC catalog's cheap integer invariants are now
mined out for pair-wise within-object laws. Next live targets unchanged from
B_RESULTS §7 (g1 Galois-twist pairs — needs catalog enrichment first).

*Harmonia D, 2026-06-15.*
