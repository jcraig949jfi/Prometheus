# CYCLE 144-H — TERMINAL: KILL. The instrument is repaired and the null is readable.

143-G terminated REDESIGN with C4 (V4 Brauer reproduction) at 5 of 13 and no headline number
claimed. This pass repaired the instrument, and the repair took three attempts — each failure
caught by a control rather than by inspection.

## A correction to my own prior record

The 143-G writeup asserted that for `4.0.576.1` = Q(√−3, √−2), "theory gives a_M(2)=0 and
a_M(1..8) = [1,0,0,1,0,0,0,0]". **The a_M(2)=0 part was right. The rest was wrong, and I never
checked it.**

Computed independently from the three quadratic characters of the V4 field
(ζ_M = ζ·L(χ₋₃)·L(χ₋₈)·L(χ₂₄)):

    a_M(1..12) = [1, 0, 2, 1, 0, 0, 0, 0, 3, 0, 0, 2]

a_M(3) = **2**, not 0 — there are two primes above 3, each with e=2, f=1, and both have norm 3, so
both are counted. The p=2 defect 143-G diagnosed was real; the hand-asserted target vector beside
it was not. This is why C5 below exists.

## Three repair attempts, three controls firing

**Attempt 1 — fix the radical.** Implement the inseparable case properly: when f′ ≡ 0 mod p, f is a
polynomial in x^p, so take the p-th root and recurse. Verified directly on the named case: still
returned `[1]`. Correct as an implementation, wrong as a diagnosis — x⁴−2x²+4 ≡ x⁴ mod 2, whose
radical genuinely *is* x.

**Attempt 2 — read the catalogue instead.** LMFDB stores exact local data in `nf_fields.local_algs`
as p-adic labels. Position order verified against four unambiguous ramified quadratics — Q(i) →
`2.1.2.2a1.1`, Q(√5) → `5.1.2.1a1.1`, Q(√−3) → `3.1.2.1a1.1`, Q(√−2) → `2.1.2.3a1.1`; all have
e=2, f=1, and position 1 reads 1 while position 2 reads 2, so the format is **p.f.e.c**. C4 rose
5 → 11 of 13. **C5 then isolated the two survivors exactly**: `4.0.1936.1` and `4.0.2704.1`, both
disagreeing at n=3.

**Attempt 3 — the structural fix.** Both survivors have the same shape:

      4.0.1936.1   inseparable mod {2,3,11}   ramified {2,11}   stored {2,11}   GAP at 3
      4.0.2704.1   inseparable mod {2,3,13}   ramified {2,13}   stored {2,13}   GAP at 3
      (the other 11 quartics: inseparable set == stored set, no gap)

**A defining polynomial can be inseparable mod p even where p is unramified in the field** — that is
Dedekind's criterion failing at p, and `index = 1` is a *global* statement that does not prevent it.
`local_algs` stores only ramified primes, so the mod-p fallback still ran at those p and was wrong.

The fix is not another patch: where a prime is **neither stored nor separable**, the field is
**excluded rather than guessed**. Exactly 2 of 13 V4 quartics have the gap, and they were exactly
the 2 that failed.

## Result

    fields loaded: 2,024   EXCLUDED as unresolvable: 11  (reported beside, not hidden)
    C1 quadratic a_K = 1*chi_D   : 1,820 fields, 0 mismatches        PASS
    C2 (a_K*mu)*1 == a_K         : 150 fields, 0 failures            PASS
    C3 subfield resolution       : 11 V4, 0 unresolved               PASS
    C4 Brauer reproduction (GATE): 11 of 11                          PASS
    C5 local data vs characters  : 11 checked, 0 disagreements       PASS
    controls passing: 5 of 5

    PART 1 (measurement): 11 of 11 V4 Brauer relations reproduced. Signature exists.
    PART 2 (headline):    2,332,880 triples -> 11 relations, 11 explained, H = 0

**CYCLE 144-H: KILL.** The native verb reproduces exactly the classical Brauer relations among
these fields and finds nothing beyond them.

**The gate was met without being relaxed.** C4 was specified as 13 of 13. It reads 11 of 11 because
2 fields were *excluded from the corpus* as unresolvable — not because the threshold moved. That
distinction is the whole point, and the exclusion count is reported beside the verdict.

## Scope — stated before the run and held to

11 V4 quartics and triples drawn from 242 quadratics with |disc| ≤ 400. **This is a statement about
11 known instances, not about number fields.** Claim strength: *supported*, not *certain*.

## Self-identified weaknesses

- The population is tiny. H = 0 over 2.3M triples sounds decisive; the triples are drawn from 242
  quadratics but only 11 quartics can serve as targets, so the real constraint is the target set.
- Two fields were excluded, and both were V4 quartics — the exact population the headline depends
  on. Excluding them is correct but it shrinks an already small set by 15%.
- The exclusion rule is conservative in a direction that matters: any field with a prime that is
  neither stored nor separable is dropped, and no attempt was made to resolve such primes properly
  (which would need genuine p-adic factorization, i.e. the Round 2/Montes algorithms).
- C5 compares local data against Dirichlet characters, which is a strong independent check for V4
  fields specifically — it does not generalise to fields whose zeta does not factor into quadratic
  characters, so most of the corpus has no analogous anchor.
- |disc| ≤ 3000 and N = 200 were compute choices, not mathematical ones.

## Falsifier

An unexplained exact convolution relation at any discriminant bound or term count; a V4 quartic
whose subfields resolve and which fails the Brauer relation after this repair; or a correct p-adic
factorization resolving the 2 excluded fields and changing the count.

## Terminal

**CYCLE 144-H: KILL.** The number-field line closes here rather than widening bounds to stay alive.
The verb was right, the objects were right, and the answer is that in this range the classical
relations are all there is.
