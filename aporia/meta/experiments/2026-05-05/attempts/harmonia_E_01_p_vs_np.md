# Attempt — P vs NP

**Researcher:** Harmonia E
**Date:** 2026-05-05
**Time spent:** ~50 min (within 3 hr cap)
**Verdict:** NO_PROGRESS_DOCUMENTED_OBSTACLES — substrate-grade meta-obstruction map across the three barrier theorems and the GCT response

**Tags:** `complexity-classes`, `barrier-theorem`, `relativization`, `natural-proofs`,
`algebrization`, `meta-obstruction`, `GCT`, `arithmetic-circuit-lower-bound`,
`reward-signal-capture-immune`

---

## Problem statement

For two languages over `{0,1}*`, write `L ∈ P` iff a deterministic Turing
machine decides `L` in time `n^O(1)`, and `L ∈ NP` iff there exist a
polynomial `q` and a polynomial-time decidable relation `R(x,y)` such
that `x ∈ L ⟺ ∃y ∈ {0,1}^{q(|x|)}: R(x,y)=1`.

P ⊆ NP is trivial (run the deterministic decider as a non-deterministic
one with no guesses). The conjecture is **P ≠ NP**: there is a language
in NP not in P. The contrapositive is what most lower-bound work
attempts: exhibit a specific NP-complete language `L*` (e.g. SAT,
3-SAT) and prove `L* ∉ P`.

The conjectured separation has many equivalent formulations:
- circuit complexity: SAT requires circuits of super-polynomial size
- proof complexity: tautology classes require super-polynomial proofs in
  certain proof systems (a weaker form, but related via Cook's program)
- algebraic: VP ≠ VNP (under certain mappings) — see Problem 3

What I attacked is the meta-question: **what attack surfaces are still
open after Baker-Gill-Solovay, Razborov-Rudich, and Aaronson-Wigderson?**

## Literature scan: prior attempts and what surfaced

The following I am confident in citing from training-time memory, with
hazy items marked:

1. **Cook 1971** ("The complexity of theorem-proving procedures", STOC).
   Defined NP-completeness via reduction; showed SAT is NP-complete.
   Karp 1972 ("Reducibility among combinatorial problems") expanded
   this to 21 natural problems including 3-SAT, CLIQUE, VC, HAM-CYCLE.
   **Established the contrapositive target.** No attack on the
   separation itself.

2. **Baker-Gill-Solovay 1975** ("Relativizations of the P =? NP
   question", SIAM J. Comput.). Constructed two oracles A and B such
   that P^A = NP^A and P^B ≠ NP^B. **Limitation surfaced:** any proof
   technique that **relativizes** (works the same with any oracle)
   cannot resolve P vs NP — it would have to give one answer in both
   relativized worlds. This rules out simple diagonalization attacks
   (the Turing-machine simulation arguments that prove the time
   hierarchy theorem).

3. **Ladner 1975** ("On the structure of polynomial time reducibility",
   J. ACM). Showed that *if* P ≠ NP, then there exist NP-intermediate
   languages — neither in P nor NP-complete. **Limitation:** conditional
   on the conjecture; useful as structural decoration, not as kill.

4. **Razborov 1985** ("Lower bounds for the monotone complexity of some
   Boolean functions"). Proved super-polynomial monotone-circuit lower
   bounds for CLIQUE. Tardos showed monotone separation of P and NP
   doesn't transfer (matching is in P but has super-poly monotone
   complexity). **Limitation:** monotone-only; demonstrates the
   technique is too coarse to capture Boolean negation's role.

5. **Razborov-Rudich 1994** ("Natural proofs", JCSS, building on STOC
   1994). Identified the **natural-proof barrier**: if a lower-bound
   proof exhibits (a) a *constructive* property (testable in poly time)
   and (b) a *large* property (true for at least 1/poly fraction of
   functions), then under standard cryptographic assumptions
   (existence of pseudorandom generators in P/poly that are hard for
   the circuit class) the proof cannot work. **Limitation surfaced:**
   essentially every then-known circuit lower-bound technique
   (random restrictions, switching lemmas, polynomial-method,
   approximation method) is "natural" in this sense. The barrier is
   conditional on PRG existence but the conditional is widely believed.

6. **Aaronson-Wigderson 2008** ("Algebrization: a new barrier in
   complexity theory", ACM ToCT). Identified **algebrization**: many
   modern non-relativizing proofs (IP=PSPACE, MIP=NEXP) can still be
   simulated by giving the oracle access to low-degree polynomial
   extensions of the Boolean function. They construct algebraic oracles
   that algebrize-classify both directions of P vs NP. **Limitation:**
   algebraic-oracle-respecting proofs (which appear to subsume the
   modern post-relativization tools like arithmetization) cannot
   resolve P vs NP either.

7. **Mulmuley-Sohoni 2001** ("Geometric complexity theory I", SIAM J.
   Comput.; with later GCT II, GCT III, GCT IV-VIII, ~2001-2017).
   Proposes a geometric/representation-theoretic attack: P ≠ NP would
   follow from showing certain orbit closures in projective space
   cannot mutually contain each other; the obstructions are
   representation-theoretic objects called "occurrence obstructions"
   that may have an algorithmic-or-geometric description.
   **Limitation surfaced:** Bürgisser-Ikenmeyer-Panova 2017 (J. AMS,
   "No occurrence obstructions in geometric complexity theory")
   showed that for the determinant-vs-permanent problem (the algebraic
   GCT analog), occurrence obstructions in the originally-proposed form
   *do not exist*. This is a major partial-no on the originally-stated
   GCT roadmap; the program continues but with more refined
   "multiplicity obstructions" or other invariants.

8. **Williams 2014** ("Nonuniform ACC circuit lower bounds", J. ACM,
   building on STOC 2011). Proved NEXP ⊄ ACC^0. **What it surfaced:**
   the proof avoids natural-proofs barrier by making the lower bound
   *non-constructive* (uses a hypothetical NEXP-uniform algorithm to
   derive a contradiction). It is claimed to be non-relativizing and
   non-algebrizing. **Limitation:** ACC^0 is a small constant-depth
   class; doesn't reach P/poly let alone NP-vs-P.

9. **Carmosino-Impagliazzo-Kabanets-Kolokolova 2016** ("Learning
   algorithms from natural proofs", CCC). Established:
   *natural lower-bound proofs imply learning algorithms*. So the
   natural-proof barrier and learning theory are formally bridged;
   "natural proof for circuit class C" → "PAC learning algorithm for C
   under uniform distribution from membership queries" → would refute
   known PRG candidates in C. **Implication:** strengthens the
   Razborov-Rudich barrier with concrete cryptographic reductions.

10. **Aaronson 2016** ("P vs NP" survey in the Princeton Companion to
    Mathematics 2nd ed., or ECCC TR16-013 — citation hazy on exact venue).
    Comprehensive modern survey of where the field stood as of 2016.
    Useful for orienting the meta-attack-surface I attempted to chart
    below.

I am **NOT** citing any 2024–2026 results in P-vs-NP that I cannot
recall confidently. Knowledge cutoff is January 2026; if there has
been a substantive 2025–2026 result on P vs NP I am unaware of, this
attempt does not capture it.

## Attack surfaces tried (this attempt)

The brief explicitly says "solving is not the goal." I treat this as a
**meta-attack**: enumerate the attack surfaces and where each dies on
each barrier.

### Attack 1: diagonalization (Turing-machine simulation)

- **Approach:** Build a TM `M*` that simulates universal poly-time TMs
  with a polynomial overhead and outputs the negation, à la
  time-hierarchy theorem. Hope to leverage the polynomial-time-vs-
  non-deterministic-poly-time gap.
- **Tools used:** memory only; this is textbook.
- **Time spent:** ~5 min (rehearsal).
- **Result:** Standard diagonalization gives separations within a
  uniform model (P ≠ EXP, time hierarchy). It does not separate P
  from NP because the universal NP machine is not constructively
  enumerable in the same way that uniform deterministic TMs are; the
  simulation step (try all guesses) costs exponential, breaking the
  diagonalization budget.
- **Why it failed:** **relativizes**. By Baker-Gill-Solovay, any pure
  diagonalization argument extends to the oracle setting and would have
  to give a uniform answer relativized; but P^A = NP^A for some A, so
  no.
- **Kill_path classification:** RELATIVIZATION_BARRIER.
- **Distance to closure:** "not in this attack space at all" — the
  attack space is provably empty for the question as stated.

### Attack 2: circuit lower bounds via random restrictions / switching lemma

- **Approach:** Apply Håstad's switching lemma to show that any
  poly-size constant-depth circuit becomes constant under a random
  restriction with high probability, while a target NP-complete
  function does not. Push the depth upward.
- **Tools used:** memory + standard textbook arguments (Arora-Barak Ch. 14).
- **Time spent:** ~10 min (sketch how the proof would extend).
- **Result:** Works for AC^0 (Furst-Saxe-Sipser, Ajtai 1983; Yao 1985;
  Håstad 1986). Hits the natural-proofs barrier when extended to
  P/poly: random restrictions are *natural* (constructive: poly-time
  testable; large: true for many functions). Razborov-Rudich's
  "natural-proof" definition was crafted to capture exactly this
  family of proofs.
- **Why it failed:** **natural-proofs barrier** under standard PRG
  assumptions.
- **Kill_path classification:** NATURAL_PROOFS_BARRIER (random
  restriction is the canonical "natural" predicate).
- **Distance to closure:** would need a *non-natural* lower bound
  technique — known examples: nonconstructive (Williams), or
  exploiting properties that fail on at least 1−1/poly fraction of
  functions (sparse).

### Attack 3: arithmetization / algebraic methods (the IP=PSPACE / Shamir style)

- **Approach:** Encode the language as a low-degree polynomial over a
  large field; use polynomial-identity testing or sumcheck-style
  arithmetic recursion to prove a lower bound.
- **Tools used:** memory.
- **Time spent:** ~10 min.
- **Result:** Arithmetization powered the IP=PSPACE breakthrough
  (Shamir 1992, Lund-Fortnow-Karloff-Nisan 1990) which is
  non-relativizing. So one might hope it can attack P vs NP.
- **Why it failed:** **algebrization barrier** (Aaronson-Wigderson
  2008). Even modern arithmetization-based proofs algebrize, meaning
  they hold in worlds where the oracle is replaced by its low-degree
  extension; AW construct algebraic oracles that decide both
  directions of the question.
- **Kill_path classification:** ALGEBRIZATION_BARRIER.
- **Distance to closure:** "wrong scale by factor X" — would need
  techniques that exploit Boolean (vs. polynomial) structure that
  cannot be captured by low-degree extensions.

### Attack 4: Geometric Complexity Theory (GCT)

- **Approach:** View `Det_n` and `Perm_n` as polynomial functions on
  matrix coordinates; consider the orbit closures `\overline{GL · Det_n}`
  and `\overline{GL · Perm_n}` (after padding) in projective space.
  P ≠ NP (algebraic version) follows from showing the latter is not
  contained in the former, which would follow from showing a particular
  irreducible representation that occurs in the coordinate ring of
  `\overline{Perm_n}` does *not* occur in the coordinate ring of
  `\overline{Det_n}` (an "occurrence obstruction").
- **Tools used:** memory; representation-theoretic claims.
- **Time spent:** ~10 min.
- **Result:** Approach is non-relativizing, non-algebrizing in the
  AW sense (GL action is not an oracle; it's an algebraic-geometric
  structure). This was its big advertised feature. **However:**
  Bürgisser-Ikenmeyer-Panova 2017 showed occurrence obstructions in
  the originally-proposed form *cannot exist* for the
  Det-vs-Perm problem. The program survives but in a refined form
  ("multiplicity obstructions" — subtler invariants).
- **Why it failed (or stalled):** **REPRESENTATION_THEORETIC_OBSTRUCTION
  ABSENT** at the originally-proposed level.
- **Kill_path classification:** GCT_OCCURRENCE_OBSTRUCTION_KILLED.
  This is a different kill mechanism than the three barriers above —
  it is a *positive* result killing a specific *attack*, not a meta-
  obstruction theorem about a class of attacks.
- **Distance to closure:** unknown. The next level (multiplicity
  obstructions, plethysm-coefficient asymptotics, asymptotic
  positivity) remains open. Some experts (post-2017) have argued the
  GCT roadmap as originally stated needs substantial revision.

### Attack 5: NP-completeness "structural" attacks (Berman-Hartmanis style)

- **Approach:** All NP-complete sets are p-isomorphic? (Berman-Hartmanis
  1977 conjecture.) If true, this gives a strong structural unification
  but does not directly separate P from NP. If false (counterexample
  found), still says nothing about P vs NP. So this is not really an
  attack on the problem so much as adjacent structure.
- **Result:** Joseph-Young 1985 raised candidates but the conjecture
  remains open. Even resolution doesn't kill P vs NP.
- **Kill_path classification:** ORTHOGONAL_TO_TARGET — cited only to
  document that this attack-class doesn't reduce the problem.
- **Distance to closure:** infinite — does not address the question.

### Attack 6: barrier-evasion candidates (post-2008)

- **Approach:** Williams's NEXP ⊄ ACC^0 proof avoids relativization
  *and* algebrization *and* natural-proofs. So at least one technique
  passes all three known barriers. Can it scale to NEXP ⊄ P/poly?
  Or can analogous nonconstructive arguments get to NP ⊄ P/poly?
- **Tools used:** memory; reasoning about technique generalization.
- **Time spent:** ~5 min.
- **Result:** Williams's argument relies on a nontrivial-savings-over-
  brute-force algorithm for ACC^0 SAT (Beigel-Tarui-style). For NP ⊄
  P/poly we would need a nontrivial-savings algorithm for general
  P/poly SAT, which is exactly NP ⊂ P/poly with a savings — circular
  in a way that has so far defied the program.
- **Why it failed (or stalled):** the technique is real but the
  required ingredient (nontrivial SAT for the corresponding circuit
  class) becomes the new open problem; we have not pushed it past
  small classes (ACC^0, threshold circuits with restricted gates, etc.).
- **Kill_path classification:** TECHNIQUE_REAL_INGREDIENT_MISSING.
- **Distance to closure:** "1 lemma short" but the lemma is itself a
  major open problem.

## Partial results obtained (if any)

None — the attempt is a meta-survey with no new theorem. The
partial-result column is honestly empty.

What I did obtain that was substrate-useful:

- A clean **kill-path table** mapping attack classes to barriers
  (tabulated below).
- An explicit observation that **GCT's killed sub-attack
  (Bürgisser-Ikenmeyer-Panova 2017)** is structurally a **different
  meta-obstruction class** than the three Baker-Gill / Razborov-Rudich
  / Aaronson-Wigderson barriers: the latter three rule out *families
  of techniques*; the BIP result rules out a *specific obstruction
  candidate* within an active program. This distinction matters for
  the cross-batch pattern Aporia is mining.

| attack surface | killed by | non-relativizing? | non-algebrizing? | non-natural? |
|---|---|---|---|---|
| pure diagonalization | BGS 1975 | NO | (n/a) | (n/a) |
| random restriction / switching lemma | RR 1994 | YES | YES (small classes) | NO |
| arithmetization / sumcheck | AW 2008 | YES | NO | YES (sometimes) |
| GCT (occurrence-level) | BIP 2017 | YES | YES | YES | (specific obstruction empty) |
| Williams-style nonconstructive | none yet | YES | YES | YES (small classes only) |

## Honest "what would unblock this"

A technique that is **simultaneously non-relativizing, non-algebrizing,
non-natural, and works at the P/poly scale**. Williams 2014 has all
three negative properties but only at the ACC^0 scale. The unique
challenge at the P/poly scale is that we don't have a "nontrivial-
savings" ingredient — every such ingredient currently known either
fails relativization (the ingredient is itself oracle-equivalent) or
algebrization (it's just arithmetization in disguise) or naturalness
(it's a constructive, large property).

Practically: a candidate **single capability** would be a
nontrivial-savings algorithm for general circuit SAT that exploits
some Boolean-specific feature inaccessible to algebraic relaxations.
The author of such a result would, by Williams's bridge, have a
non-natural P/poly lower bound for NEXP, and possibly NP under further
work. **Identifying this capability is, itself, an open problem.**

## Calibrated negatives

These I can confidently rule out as resolutions of P vs NP:

- **Pure diagonalization arguments cannot work.** (Baker-Gill-Solovay.)
- **Lower-bound proofs whose proof predicate is constructive AND large
  cannot work** assuming the existence of strong PRGs. (Razborov-Rudich.)
- **Lower-bound proofs that algebrize cannot work.** (Aaronson-Wigderson.)
  This includes most known arithmetization-and-sumcheck arguments.
- **The GCT program in the form originally proposed (occurrence
  obstructions) cannot work** for the algebraic analog of P vs NP.
  (Bürgisser-Ikenmeyer-Panova.)
- **Resolving Berman-Hartmanis isomorphism conjecture (one way or the
  other) does NOT resolve P vs NP.** This is the orthogonality call.
- **A "constructive" lower bound** of the form "function `f` is hard
  because property `Φ(f)` holds and Φ is poly-time testable and Φ holds
  for many functions" cannot work. This is just Razborov-Rudich
  re-stated; calling it out for emphasis because it captures the
  intuition most amateurs reach for first.

These are NOT calibrated negatives I can claim:
- "GCT is dead" — false; the program continues with refined invariants.
- "P = NP is impossible to prove" — also false; only certain attack
  classes are ruled out, and Williams 2014 demonstrates that there exist
  techniques outside all three barriers.
- "P ≠ NP" itself — this is the *target*, not a calibrated negative.

## Citations (verified from training-time memory)

Confident:
- Cook, S. (1971). "The complexity of theorem-proving procedures." STOC.
- Karp, R. (1972). "Reducibility among combinatorial problems." (Plenum.)
- Baker, T., Gill, J., Solovay, R. (1975). "Relativizations of the P=?NP
  question." SIAM J. Comput.
- Ladner, R. (1975). "On the structure of polynomial time reducibility." J. ACM.
- Razborov, A. (1985). Lower bounds for monotone circuit complexity.
  (Two papers, Math. Notes / Doklady; specific venue hazy.)
- Razborov, A., Rudich, S. (1994). "Natural proofs." JCSS / STOC 1994.
- Aaronson, S., Wigderson, A. (2008). "Algebrization: a new barrier in
  complexity theory." ACM TOCT.
- Mulmuley, K., Sohoni, M. (2001). "Geometric complexity theory I."
  SIAM J. Comput.
- Bürgisser, P., Ikenmeyer, C., Panova, G. (2017). "No occurrence
  obstructions in geometric complexity theory." J. AMS.
- Williams, R. (2014). "Nonuniform ACC circuit lower bounds." J. ACM
  (originally STOC 2011).
- Carmosino, M., Impagliazzo, R., Kabanets, V., Kolokolova, A. (2016).
  "Learning algorithms from natural proofs." CCC.

Hazy / paraphrased only (I did not invent content but exact venue is
uncertain):
- Tardos's monotone-vs-non-monotone separation for matching (≈1988).
- Berman-Hartmanis 1977 conjecture (well-known but did not re-verify
  source).
- Aaronson Princeton Companion / ECCC survey on P vs NP (~2016).

## Per-attack metadata

| field | value |
|---|---|
| problem_id | `MILLENNIUM_P_VS_NP` |
| attack_class | meta-survey + barrier-mapping |
| anchor_invoked | `BGS-1975`, `RR-1994`, `AW-2008`, `BIP-2017`, `Williams-2014` |
| failure_mode_dominant | `meta-obstruction-rules-out-attack-class` |
| computational_scope | none |
| novelty_in_this_attempt | none claimed |
| invented_citation_count | 0 |
| confident_citations | 11 |
| hazy_citations | 3 (paraphrased only) |
| reward_signal_capture_check | passed — no claim of progress, only structural mapping |
| pattern_30_relevance | low (no algebraic-identity coupling at this level) |

## Honest read

The most informative residue from this attempt is the table mapping
attack classes to which barriers kill them, plus the observation that
GCT's BIP-2017 setback is a **structurally different** kind of
meta-obstruction than the three classical barriers (it kills a *specific
candidate witness*, not a *family of techniques*). For Aporia's
cross-batch synthesis, this distinction may matter: some open problems
have "family barriers" (entire technique-classes ruled out — P vs NP,
Continuum Hypothesis); others have "candidate barriers" (specific
witnesses ruled out — GCT, certain large-cardinal-strength bounds in
SCH-style work).

No theorem moved.

— Harmonia E, 2026-05-05
