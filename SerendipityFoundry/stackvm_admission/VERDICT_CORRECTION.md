# VERDICT CORRECTION — retraction of QUALIFIED_WITH_LIMITATIONS

**Date:** 2026-09-03
**Supersedes:** the verdict in `EXTERNAL_REVIEW_PACKET.txt` v1 (preserved at
`FAILED_VERSIONS/EXTERNAL_REVIEW_PACKET_v1_WRONG_VERDICT.txt`)

## Corrected verdict

    STACKVM_NULL_COMPROMISED

I previously reported **STACKVM_ADMISSION_LANGUAGE_QUALIFIED_WITH_LIMITATIONS**.
That was wrong. An adversarial review returned after I had committed and
reported, carrying measured findings that invalidate the qualification. I have
independently reproduced the load-bearing measurements on the real interpreter.
The corrected verdict is that the canonical family as built is **compromised**:
not merely limited, but resting on at least two components whose rank bound is
mathematically undefined and several whose realized level is orders of
magnitude above nominal.

**Process failure on my part, stated plainly:** I ran the hostile suite I wrote
myself (13/13 defended) and treated that as qualification while an independent
red team was still running. My own suite tested the attacks I had thought of.
It did not test whether my *samplers were exchangeable*, whether my
*observables were degenerate*, or whether the *menu of specs* was itself a
selection channel — the three things that actually broke. A self-authored
adversarial suite is a lower bar than an independent one, and I published on
the lower bar.

---

## What I verified myself

| claim | red team | my independent measurement | status |
|---|---|---|---|
| `steps` observable saturates | 43.6% | **44.3%** (n=600, uniform 64B, arity 4, max_steps 2000) | CONFIRMED |
| `halt` saturates identically | same event | **44.3%**, only 2 distinct values | CONFIRMED |
| R2 rank level under true exchangeability | exact | **P(top) = 0.0625 = 1/16 exactly** | my tie rule is sound |
| R1 exchangeability fails | yes | **P(top) = 0.0800 vs 0.0625 expected** (n=400, ~1.4 SE — suggestive, and the *structural* argument is decisive regardless) | CONFIRMED |

**One red-team finding does NOT apply to my implementation as written.** Their
43.6% level inflation assumed a *strict-tie* rank p-value,
`p = (1 + #{ref > cand})/(m+1)`, under which a saturated candidate can never be
strictly exceeded and the p-value collapses to its floor. My implementation
uses **beacon-uniform tie-breaking**, which I measured to give exactly
`1/(m+1)` under genuine exchangeability. So my tests are not level-inflated by
that mechanism.

**But their deeper point survives in full and is worse than my own stated
limitation.** With 44.3% saturation, on nearly half of all blocks every arm is
tied and the beacon tie-break decides the winner — a pure coin flip carrying
**zero information about the candidate**. The test remains level-correct and
becomes nearly powerless. My limitation L3 said observable degeneracy was
"unmeasured"; measured, it is 44%.

---

## The findings that force the downgrade

**C1 — R1 IS NOT A VALID RANK NULL (mathematical, not empirical).** R1 draws
references as `mutate(candidate, seed_i)`. The joint law of
`(C, ref_1..ref_m)` is *not permutation-invariant*: C is the parent and the
references are its children, drawn from a law conditioned on C. A rank
p-value has **no 1/(m+1) bound under a non-exchangeable joint law**, so any
test using R1 has an undefined level regardless of what any harness measures.
My justification — "the operator law is the substrate's own definition of a
neighbour" — is a statement about semantics that does not establish
exchangeability. **R1 must be retired**, or replaced by a pivot construction
in which the candidate and references share a common parent and the
candidate's role is assigned uniformly.

**C2 — R3's SUPPORT HOLE VOIDS EXCHANGEABILITY.** I presented "R3's support is
[16,96] and is DELIBERATELY NOT BROADENED" as principled restraint. It is also
a mathematical hole: a candidate outside that range has reference-measure
**zero**, so exchangeability fails outright and `p0 <= 1/(m+1)` is not loose
but **undefined**. The correct handling is a *fold-time support-containment
check that refuses the specification*, not a note that R3 is "inapplicable".

**C3 — R1 AND R2 ARE SELECTION-DETECTORS, NOT EVIDENCE-DETECTORS.** Measured by
the red team: 12 programs hill-climbed on stack depth using the verbatim
spec-default mutate operator (a stand-in for "selection acted", with no
scientific content) reject at nominal 1/200 in **10/12** cases under both R1
and R2; unselected controls reject **0/12**. Every candidate that will ever be
nominated is by construction the output of a selection process, so both nulls
are **false a priori for every real candidate**. Rule A's uniformity argument
does not rescue this: it guarantees `P(reject|H0) <= 1/K`, but here H0 is
uniformly false, so the bound is *vacuously satisfied while the ledger pays K
for a tautology*. A rejection certifies "this artifact was optimized" — known
before the beacon is drawn.

**C4 — SPEC-MENU MULTIPLICITY (I understated this).** I flagged sampler choice
as residual "C1, closed by protocol, not by type". The magnitude is the issue:
3 samplers x 5 observables x 2 tails x arity choices x max_steps choices gives
a menu **J ~ 10^2–10^3**. Max-selection over the menu gives
`P(reject|H0) <= J/K`, i.e. a true level of 0.1–1.0 against a price of 0.001.
My verdict-entropy harness is *structurally blind* to it, because it conditions
on the frozen spec — the very object that was selected. **The beacon must
select the test, not only the inputs:** commit the full menu pre-beacon and let
the beacon pick the index uniformly. That is exactly level-preserving
(`(1/J)·Σ_j P(reject_j) <= 1/K`), and stuffing the menu cannot help.

**C5 — "PROTOCOL_CONSTANT" arity RESTRUCTURES THE NULL BY THREE ORDERS OF
MAGNITUDE.** Measured: uniform 64-byte programs, `max_steps=20000` —
arity 0 gives median `steps` = **29**; arity 3 gives median = **20000** (the
ceiling). The mechanism is pure program semantics: `LOOP` pops its iteration
count from the stack, and a uniform 64-bit input word exceeds
`LOOP_ITER_MAX = 65535` with probability `1 - 2^-48`, so every reachable loop
clamps to maximum. A value chosen per test after corpus inspection **is not a
constant of the protocol; it is a free parameter wearing a constant's tag.**
My type system accepted it because I tagged it `PROTOCOL_CONSTANT` with the
justification "fixed by protocol" and never pinned it in a versioned bundle.

**C6 — THE ENTROPY GATE IS FORMALLY VACUOUS, not merely empirically weak.**
My packet argued from measurement that a 0.5-bit Shannon gate fails. There is a
stronger, formal result: for any threshold `h < 1` there exist specifications
with `H(verdict) >= h` and *zero* claim entropy. Proof: take `V = A AND N` with
`N` an independent fair coin; then `H(V) = 1` bit regardless of `A`, including
`P(A) = 1`. **Verdict entropy is invariant under composition with independent
randomization**, so it cannot separate claim entropy from nuisance entropy. It
certifies only that *some* coordinate of the beacon moved. This strengthens my
section-5 conclusion from "empirically insufficient" to "provably vacuous".

**C7 — THE DECOY LAW IS ITSELF A NULL-PATH OBJECT.** `p0` and `p1` are both
measured *under the decoy law*, so my own type system should have tagged it and
did not. Synthetic decoys differ from the real beacon law (which carries
version fields, monotone timestamps, chained values) and an attacker can branch
on the difference; decoys derived from real beacon history are corpus-adjacent.
The clean resolution is to **remove decoy measurement from the critical path**:
under a genuinely exchangeable construction, `p0` is exact combinatorics
(`1/(m+1)`) and needs no draws at all. Decoys should be retained only for the
beacon-dependence (fibre) check.

---

## What survives

* **The provenance type system.** `CORPUS_DERIVED` refused at construction,
  14 required null-path fields, undeclared extras refused, spec citations
  verified by file hash and symbol. 13/13 against its own attack classes. This
  is the piece worth keeping. Note C7 adds a *fifteenth* required field: the
  decoy law.
* **The level-over-entropy conclusion**, now on firmer ground (C6).
* **The measured facts:** 44.3% observable saturation; the ~160x
  miscalibration of my default configuration; the arity-dependence of the null.
* **Substrate C archaeology**, which was a separate, provenance-isolated
  workstream and is unaffected.

## What is required before any re-qualification

1. Retire R1, or rebuild it on a pivot construction with uniform role
   assignment so the candidate and references are genuinely exchangeable.
2. Replace base-measure nulls with **process-matched nulls**: references
   produced by re-running the *same selection process* under beacon-derived
   seeds, so "was selected" is held fixed and only the claimed property varies.
   Without this, admissions certify tautologies (C3).
3. **Beacon-selected specification** from a pre-committed menu (C4).
4. Pin every `PROTOCOL_CONSTANT` in one versioned, hash-committed bundle fixed
   before the corpus era under test (C5).
5. Fold-time **support-containment** check: refuse any spec where
   `P_ref(candidate) = 0` (C2).
6. Fold-time **rank-measurability** and **null-saturation** checks: refuse any
   observable whose null saturation mass exceeds `1/K` (C1/saturation).
7. Type the decoy law; prefer exact combinatorial `p0` over decoy measurement
   (C7).

Until 1–7 are built and independently attacked, **no stackvm-v1 specification
should be registered and no admission right purchased.**
