# CYCLE 143-G — TERMINAL: REDESIGN. A control finally caught something.

**Object class:** number fields (LMFDB `nf_fields`), degrees 2–4, index = 1. Chosen over
`mf_newforms` deliberately — weight-2 rational newforms *are* elliptic curves by modularity, so a
newform sweep would have re-entered the banned object class through the back door.

**Representation:** the Dedekind zeta coefficient sequence `a_K(n) = #{ideals of norm n}`. Canonical,
multiplicative, and — unlike a Frobenius trace — **unbounded**, which matters because 141-E found
three generic operators structurally unreachable precisely because traces are Hasse-bounded.

**Native verb:** Dirichlet convolution. Number theorists multiply and divide zeta functions; on
coefficient sequences that operation *is* convolution. It is also the verb 142-F could not test,
because it needs an n-indexed sequence and therefore exact behaviour at ramified primes. Restricting
to `index = 1` makes Dedekind's theorem apply at *every* prime, which is what unlocked it.

## Pass 1's verdict is WITHDRAWN, and why

Pass 1 returned KILL. It should not have, on two counts found afterwards:

1. **The only convolution-shaped control never ran.** D2 (the V4 Brauer relation) reported
   `0 of 0 checked`. Cause: `nf_fields.subfields` is TEXT holding **polynomial coefficients**
   (`{1.-1.1, 1.0.1, -3.0.1}` = x²−x+1, x²+1, x²−3), not LMFDB labels, so label matching could never
   match. D1 verified the ideal counting, but D1 is a *factorization*-shaped identity. Nothing had
   shown the pipeline could detect a relation of the shape the headline tested.
2. **The headline shape had no known instances.** Pass 1 tested `1*a_M = a_K1*a_K2` with
   deg M = deg K1 + deg K2 − 1. For two quadratics that demands a *cubic* M with
   ζ_M = ζ·L(χ1)L(χ2) — but a cubic field's zeta factors as ζ·L(2-dim Artin) or ζ·L(χ)L(χ̄) for χ of
   order 3, never as two quadratic characters. The shape is not instantiable.

Reading a null from an instrument never shown able to detect the signature is the failure doctrine
forbids. Hence withdrawn rather than re-scoped.

## Pass 2 repaired the control — and the control caught a real defect

Subfields matched by coefficient tuple (exact: LMFDB stores 2.2.12.1 with coeffs `{-3,0,1}`, and the
subfield entry `-3.0.1` is that polynomial). Headline retargeted to the shape that *does* have known
instances, the V4 Brauer relation `a_K1 * a_K2 * a_K3 = 1 * 1 * a_M`, which holds classically exactly
when K1,K2,K3 are M's three quadratic subfields (from ζ_K1ζ_K2ζ_K3 = ζ²ζ_M).

    C1 quadratic a_K = 1*chi_D : 1,820 fields, 0 mismatches            PASS
    C2 (a_K*mu)*1 == a_K       : 150 fields, 0 failures                PASS
    C3 subfield resolution     : 13 V4 quartics, 0 unresolved          PASS
    C4 Brauer reproduction     : 5 of 13 reproduce the relation        **FAIL**

**C4 is the finding.** After three consecutive passes shipping controls that could not fail, this one
failed — and it failed on real mathematics rather than on bookkeeping.

## The defect, diagnosed exactly

For M = 4.0.576.1 = Q(√−3, √−2), defining polynomial x⁴ − 2x² + 4:

    p=2: residue_degrees -> [1]          theory: ONE prime, e=2, f=2  -> should be [2]
    computed a_M(1..8): [1, 1, 2, 1, 0, 2, 0, 1]
    theory   a_M(1..8): [1, 0, 0, 1, 0, 0, 0, 0]

**Mechanism:** the code takes the radical of f mod p as `f / gcd(f, f')`. At p = 2 this polynomial is
even, so f′ ≡ 0 mod 2, the gcd branch is skipped, and the fallback uses the **full polynomial with
multiplicity** instead of its radical. Distinct-degree factorization then counts repeated factors as
separate primes, so the Euler factor is wrong at every prime where f′ ≡ 0 mod p. That is why 8 of 13
V4 quartics failed while the other 5 — whose defining polynomials have non-vanishing derivative at
every ramified prime — passed.

## Verdict

Reading: **VACUOUS.** Campaign terminal: **REDESIGN** at pass 2 of a permitted 3.

The headline reported H = 0 unexplained relations over 2,332,880 admissible triples, and **that number
is not reportable as a null** — 8 of 13 known-true instances were computed wrongly, so the sweep was
partly searching against corrupted targets. It is recorded, not claimed.

## The repair, specified

Replace the radical computation with a correct squarefree decomposition over F_p that handles the
inseparable case: when f′ ≡ 0 mod p, f is a p-th power of a polynomial in x^p, so take
f = g(x^p) = g₁(x)^p and recurse on g₁. Then re-run pass 2 unchanged; C4 must reach 13 of 13 before
any headline null is readable.

## Self-identified weaknesses

- Two of the three pass-1 design errors (label-vs-polynomial, uninstantiable shape) were found only by
  looking at *why* a control reported zero. Neither was caught by the branch structure.
- The V4 population in range is **13 quartics** — very small. Even repaired, C4 would rest on 13
  instances, and the headline's discriminant bound (|disc| ≤ 3000, quadratics ≤ 400 for the sweep) was
  set for compute rather than mathematics.
- Arithmetic equivalence — non-isomorphic fields with identical zeta — cannot appear below degree 7,
  so the dedup census (2,529 labels → 2,529 distinct sequences, 0 equivalent groups) was a foregone
  result in this range and is reported as such.
- The `index = 1` restriction is what makes the whole approach exact, and it also biases the corpus
  toward fields with small index; that selection was not characterised.

## Falsifier

A correct squarefree-decomposition implementation giving C4 = 13 of 13, after which a genuine null or
a genuine unexplained relation becomes readable; or a V4 quartic whose subfields are correctly
resolved and which still fails the Brauer relation after the repair, which would indicate the defect
is not the inseparability fallback.

## Terminal

**CYCLE 143-G: REDESIGN.** The question is well-posed and the verb is right; the instrument is wrong
at primes where the defining polynomial is inseparable mod p. Repair is specified and cheap. No null
is claimed from this pass.
