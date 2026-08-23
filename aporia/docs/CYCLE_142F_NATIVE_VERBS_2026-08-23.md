# CYCLE 142-F — TERMINAL: KILL on binary verbs. And the vocabulary question is now SETTLED.

**The choice:** 141-E offered extending the vocabulary or changing the object class. Vocabulary was
taken, because finding (b) — that the operations native to L-functions were absent from the
operator set entirely — was the ambiguity blocking interpretation of *both* prior nulls. Another
object class would have produced a third null carrying the same ambiguity.

The pass was preregistered in two parts that must not be conflated.

## PART 1 — the diagnostic. This is the result that matters.

**One native verb finds 4,476 exact relations where seven generic operators found zero.**

    141-E:  7 unary operators, 294,909,843 reachable triples  ->  H = 0
    142-F:  1 native verb (quadratic twist), 900 curves        ->  4,476 exact relations

Same objects. Same representation. Same exactness bar of 20 consecutive terms. The difference is
entirely the verb.

**Finding (b) is resolved: the prior nulls were about the VOCABULARY, not about the objects.**
Elliptic curves are richly related to one another; `diff`, `partsum`, `binomial`, `moebius`,
`inverse_binomial`, `second_diff` and `stirling2` simply cannot see it. Generic sequence operators
are the wrong verbs for arithmetic objects.

This is a measurement confirming known mathematics — twisting is a theorem — and it was
preregistered as such. It is **not** a discovery and does not make the terminal an ADVANCE.

### The number that needed deflating, and does not survive

The run reported 3,896 of the 4,476 relations as "not recorded by LMFDB as a quadratic twist",
which reads like a discovery. It is not. Targets inside a single isogeny class have *identical*
a_p, and LMFDB records one representative per class — so each genuine relation is multiplied by
the target class size. Example from the run: `11.a1 --twist(-11)--> 121.d1` is recorded, and
`121.d2`, `121.d3` are the same class arriving as separate "unrecorded" rows.

Deduplicating the stored sample by (source, target **class**, disc): **12 distinct triples, 12 with
an LMFDB-recorded member — 100%.** There is no unrecorded relation here. The raw count is an
artifact and is reported as one.

## PART 2 — the headline. KILL.

Do binary native verbs map a *pair* of curves' trace sequences exactly onto a *third* curve's? No
theorem predicts this, so it is the genuine discovery statistic and the terminal rests on it alone.

    DEGENERACY: 892 of 900 pass nondeg (8 removed by the guard)
    target band: |a_p| <= 35 over the window
    PER-VERB REACHABILITY:
      hadamard          0 reachable source pairs   STRUCTURALLY INCAPABLE
      add         180,722 reachable source pairs
      sub         179,222 reachable source pairs
    ATTAINABILITY (reachable only): 323,229,712 triples, gate H>=1 inside range
    H = 0

`hadamard` is structurally incapable: the product of two Hasse-bounded traces escapes the band at
every one of ~400,000 source pairs. Its triples are excluded from the denominator rather than
inflating it. So the binary test is really **add and sub only**, and that is stated rather than
implied by the word "binary".

## Controls — all four, each with a stated failure mode

    C1 isogeny identity : 558 pairs, 0 mismatches            PASS
    C2 Hasse bound      : 0 violations                       PASS
    C3 independent algo : 240 brute-force checks, 0 disagree PASS
    C4 twist fidelity   : 298 recorded twist pairs,
                          0 |a_p| mismatches,
                          0 sign-pattern failures,
                          0 global-convention flips          PASS

C4 is the one guarding the new machinery, and it is the strongest control this line has produced:
298 pairs LMFDB independently records as quadratic twists, and the computed `kronecker(d,p)·a_p`
reproduces the partner's trace sequence exactly — right magnitudes *and* right signs at all 40
positions, with no convention flip. The twist verb is correct, so Part 1's 4,476 are real
relations rather than an implementation artifact.

## Prime window, chosen for a mathematical reason

The 40 primes from 101 to 313. Every fundamental discriminant used has |d| <= 100 < 101, so no
window prime divides any d, so `chi_d(p)` is never zero and the twist verb is exactly well-defined
at every position for every curve. Curves sharing a factor with the window were dropped (11,308 ->
10,278), giving all curves a common index — which is what makes binary verbs between *different*
curves well-defined at all.

## Verdict

**CYCLE 142-F: KILL** at pass 1 of a permitted 3 — on binary native verbs, which add nothing over
unary ones for this object.

Per the preregistered consequence, the next cycle changes the **object class**, and it does so with
the vocabulary question already settled rather than left open. That is what this pass bought.

## Self-identified weaknesses

- Full **Dirichlet convolution** was not attempted. It needs an n-indexed sequence and therefore
  bad-prime casework at every conductor. It was deliberately skipped rather than done badly, and
  it is the most natural verb still untested — so "native verbs" here means twist, Hadamard, add
  and sub, not the whole native family.
- 900 curves, bounded because the binary sweep is O(n²). The twist census would extend to the full
  10,278 cheaply; the binary sweep would not.
- Part 1 confirms a theorem. Its value is diagnostic — it tells us the earlier nulls were
  vocabulary artifacts — and none of it is new mathematics.
- `hadamard` contributed zero admissible triples, so one of the three binary verbs was never
  actually tested against data.
- The guard removed 8 of 900 sequences; small, and reported here beside the verdict.

## Falsifier

A binary-verb relation mapping two curves onto a third at any conductor bound or window; a
Dirichlet-convolution relation, which remains untested; or evidence that the twist census's 4,476
relations survive isogeny-class deduplication as unrecorded pairs, which would turn Part 1 from a
confirmation into a discovery.

## Terminal

**CYCLE 142-F: KILL.** Binary native verbs add nothing. But the vocabulary question that made the
last two nulls uninterpretable is answered: **the verbs must be native to the objects, and when
they are, the relations are there in abundance.**
