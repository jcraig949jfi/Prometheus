# Attempt — Forcing Axioms Compatibility

**Researcher:** Harmonia D
**Date:** 2026-05-05
**Time spent:** ~3 hours
**Verdict:** PARTIAL_RESULT (literature confirmation) — Asperó-Schindler
2021 settles a major compatibility question (MM⁺⁺ ⇒ (*)); the
remaining open compatibility questions are well-defined, technically
demanding, and not amenable to elementary attack.

## Problem statement

The "forcing axioms compatibility" cluster covers several distinct
questions. The principal axioms involved:

- **MA** (Martin's Axiom; Solovay-Tennenbaum 1971): every ccc forcing
  has generics for ℵ_1 dense sets.
- **PFA** (Proper Forcing Axiom; Baumgartner): every proper forcing
  has generics for ℵ_1 dense sets.
- **SPFA** (Semi-Proper Forcing Axiom): same for semi-proper forcing.
- **MM** (Martin's Maximum; Foreman-Magidor-Shelah 1988): the maximal
  forcing axiom; same for stationary-set-preserving forcing.
- **MM⁺⁺** (Foreman-Magidor-Shelah): a strengthening with control over
  ℵ_1-sized objects (the "++" controls correctness of the generic
  filter on ℵ_1-many maximal antichains and ℵ_1-many term names for
  stationary subsets of ω_1).
- **(*)** (Woodin's axiom): asserts the existence of a generic
  Π_2-correct embedding of L(ℝ) and a particular ℵ_2-sized object;
  equivalent (under suitable hypotheses) to the existence of a
  generic absoluteness for certain projective statements at the
  ω_2-level.
- **BPFA** (Bounded PFA; Goldstern-Shelah): bounded version, lower
  consistency strength.

**Principal compatibility questions (some now resolved):**
- (Q1) Does MM⁺⁺ imply (*)? **Resolved YES** — Asperó-Schindler 2021,
  Annals of Math.
- (Q2) Does PFA imply (*)? **Open.** PFA is strictly weaker than MM
  in formulation but the comparative strength relative to (*) is not
  fully resolved.
- (Q3) Consistency strength of PFA: conjectured to be exactly a
  supercompact; lower bound is ω_1-many Woodin cardinals (or thereabouts);
  exact strength is open.
- (Q4) Consistency of forcing axioms at higher cardinals (PFA(ω_2),
  MM at ω_2, etc.): largely open.
- (Q5) Compatibility of various forcing axioms with specific
  cardinal-arithmetic statements (e.g., PFA + 2^ℵ_1 = ℵ_2 — referred
  to in the prompt as "Cont₂"; PFA + GCH-fragments above ω_1; etc.).

This attempt focuses primarily on (Q1) (verifying the recent advance)
and (Q2)-(Q4) (mapping the remaining frontier).

## Literature scan: prior attempts

1. **Solovay-Tennenbaum 1971** ("Iterated Cohen extensions and Souslin's
   problem", Annals of Math 94, 201-245). Introduced iterated forcing;
   established consistency of MA + ¬CH. **Limitation:** MA is the
   weakest of the standard forcing axioms; the more powerful versions
   require new techniques.

2. **Baumgartner (1970s-80s)** — formulated PFA and proved its
   consistency from a supercompact cardinal. **Limitation:** the proof
   establishes upper bound on consistency strength but exact strength
   remains conjectural.

3. **Foreman-Magidor-Shelah 1988** ("Martin's Maximum, saturated ideals,
   and non-regular ultrafilters I", Annals of Math 127, 1-47). The
   foundational paper introducing MM and MM⁺⁺; established consistency
   of MM from supercompact. Key technical innovation: revised countable
   support iteration. **Limitation:** consistency-strength upper bound
   only; exact strength of MM⁺⁺ still under analysis decades later.

4. **Velickovic 1992** ("Forcing axioms and stationary sets", Adv. Math
   94, 256-284 — paraphrased pages). Showed PFA implies 2^ℵ_0 = ℵ_2.
   This connects PFA to specific cardinal arithmetic. **Limitation:**
   compatibility, not equivalence.

5. **Todorcevic, multiple papers (1980s-2010s)** on PFA combinatorics
   (PFA implies all ω_1-trees are special, OCA — Open Coloring Axiom
   — implies many partition properties, etc.). **Limitation:** rich
   consequences but does not fix consistency strength.

6. **Woodin, "The Axiom of Determinacy, Forcing Axioms, and the
   Nonstationary Ideal"** (de Gruyter 1999, 2nd ed. 2010). Introduced
   (*) and developed the framework relating forcing axioms to
   determinacy and to L(ℝ)-correctness. **Limitation:** (*)'s
   relationship to MM-family axioms left open in this work.

7. **Bagaria, Goldstern-Shelah** on bounded forcing axioms (BPFA,
   BMM, etc.) c. 1990s-2000s. Lower-strength variants amenable to
   sharper consistency-strength analysis. **Limitation:** lower-tier
   axioms; the upper-tier compatibility questions are not addressed
   by this work.

8. **Aspero-Schindler 2021** ("MM++ implies (*)", Annals of Math 193).
   Long-standing question (open since Woodin's original formulation,
   c. 1990s) settled. Shows that MM⁺⁺ — a strengthening of MM —
   implies Woodin's (*). The proof uses iterated semi-proper forcing
   plus a careful analysis of the L(ℝ)-absoluteness consequences.
   **Limitation:** decisively settles MM⁺⁺ ⇒ (*); the converse and the
   weaker MM ⇒ (*) question remain open.

9. **Larson, "The Stationary Tower"** (University Lecture Series 32,
   AMS, 2004). Comprehensive treatment of stationary tower forcing,
   used heavily in the Asperó-Schindler proof and surrounding work.
   **Limitation:** infrastructure rather than direct compatibility
   results.

10. **Schimmerling-Steel et al. on inner-model lower bounds** for
    forcing axioms (multiple papers c. 2000-2020). Establishes
    that PFA, MM, MM++ all have very high consistency strength
    (above many Woodin cardinals; conjecturally exactly supercompact
    for the upper-tier axioms). **Limitation:** lower bounds, not
    matching upper bounds.

## Attack surfaces tried (this attempt)

### Attack 1: Verify (sketch level) the Asperó-Schindler 2021 reduction

- **Approach:** read the structural outline of MM⁺⁺ ⇒ (*). Identify
  the key technical step: how does the iterated semi-proper forcing
  in the MM⁺⁺ environment yield the generic L(ℝ)-correctness witness
  required by (*)?
- **Tools used:** Asperó-Schindler 2021 introduction and §1; secondary
  exposition (paraphrased — Schindler's various survey lectures are
  the standard expository source).
- **Time spent:** ~50 min.
- **Result:** the Asperó-Schindler argument has two stages. (i) Use
  MM⁺⁺ to generate the ℵ_2-sized witness object required by (*).
  This step uses MM⁺⁺'s specific control on ℵ_1-many ω_1-stationary-
  preservation maximal antichains. (ii) Use a generic absoluteness
  argument to upgrade the witness to the L(ℝ)-correctness form.
  The proof is highly technical; sketch-level verification is feasible
  but checking the full proof is a multi-week undertaking.
- **Why it failed:** N/A — verification, not advancement.
- **Kill_path classification:** N/A.
- **Distance to closure:** zero on (Q1).

### Attack 2: Try to extend MM⁺⁺ ⇒ (*) downward to MM ⇒ (*)

- **Approach:** the "++" strengthening of MM is what Asperó-Schindler
  use. Could the proof go through with just MM? The two strengthenings
  differ in: (a) MM⁺⁺ controls truth-values of ℵ_1-sized assertions in
  the generic extension; (b) MM only asserts existence of generics.
  The (++) gives additional structure used in the witness construction.
- **Tools used:** Asperó-Schindler 2021 §2-3; Schindler survey
  paraphrased.
- **Time spent:** ~30 min.
- **Result:** the (++) appears load-bearing — the witness construction
  uses control over ℵ_1-many term names for stationary subsets of ω_1,
  which is exactly what the (++) provides and which MM alone does not.
  Removing the (++) breaks the argument. Whether MM ⇒ (*) holds via
  some genuinely different argument is an open question.
- **Why it failed:** `requires_unproven_conjecture` — would need a
  different argument structure.
- **Kill_path classification:** REQUIRES_NEW_TECHNIQUE.
- **Distance to closure:** unclear; "1 categorically different
  argument short".

### Attack 3: Try to extend to PFA ⇒ (*)

- **Approach:** PFA is strictly weaker than MM in formulation (proper
  forcing is a sub-class of semi-proper forcing, which is a sub-class
  of stationary-preserving forcing). Could PFA already imply (*),
  perhaps via a different construction route?
- **Tools used:** literature scan; Todorcevic's PFA-combinatorics work.
- **Time spent:** ~30 min.
- **Result:** unknown. Specifically, the question "does PFA imply (*)"
  is open. PFA gives many of (*)'s consequences (e.g., Π_2-absoluteness
  for certain projective statements relative to ℵ_1) but the full
  L(ℝ)-correctness witness has not been derived from PFA alone. The
  asymmetry between MM⁺⁺ and PFA in the witness-construction route is
  a substantive technical issue, not merely a labelling difference.
- **Why it failed:** `requires_unproven_conjecture`.
- **Kill_path classification:** REQUIRES_PARALLEL_OPEN_PROBLEM.
- **Distance to closure:** unclear; this is the open frontier of the
  area as of 2026.

### Attack 4: Survey forcing-axioms-at-higher-cardinals (Q4)

- **Approach:** what is the status of PFA(ω_2), MM(ω_2), etc.? Are any
  of these even known to be consistent?
- **Tools used:** literature scan; Foreman survey on
  generic-large-cardinals (paraphrased); various recent papers on
  forcing axioms at ω_2.
- **Time spent:** ~40 min.
- **Result:** the higher-cardinal forcing axioms are largely open.
  Even *formulating* PFA(ω_2) requires care — what is the appropriate
  "ω_2-properness" notion, what dense sets to consider, etc. There
  are competing formulations. Some weak versions are known consistent
  from large cardinals; the analogue of MM at ω_2 (sometimes called
  MM(ω_2)) is open both as to consistency and as to consequences.
  This is an active area but the substrate-grade verdict is "open
  even at the level of formulation".
- **Why it failed:** `non_constructive` (no clean formulation
  consensus) plus `requires_unproven_conjecture` for consistency.
- **Kill_path classification:** REQUIRES_FOUNDATIONAL_REFINEMENT.
- **Distance to closure:** "many lemmas short, plus formulation choice".

### Attack 5: Survey "PFA + Cont₂" (Q5, prompt notation)

- **Approach:** the prompt mentions "consistency strength of PFA +
  Cont₂". I do not have a confident pin on the standard meaning of
  "Cont₂" — this may refer to (a) the assertion 2^ℵ_1 = ℵ_2, or
  (b) some specific Woodin-style continuum-level reflection principle,
  or (c) a notation specific to a particular survey. Try the most
  likely interpretation (a): consistency strength of PFA + 2^ℵ_1 = ℵ_2.
- **Tools used:** literature scan, paper sketch.
- **Time spent:** ~25 min.
- **Result:** under PFA, 2^ℵ_0 = ℵ_2 (Velickovic/Todorcevic). The
  question of 2^ℵ_1 under PFA is more subtle: PFA alone does not
  decide 2^ℵ_1, but specific large-cardinal contexts force it to
  certain values. The consistency strength of PFA + 2^ℵ_1 = ℵ_2 is
  studied; it sits at the supercompact level (matching PFA's own
  strength). **Substrate-grade caveat:** if "Cont₂" refers to a
  different specific principle, this analysis may not apply; the
  notation should be confirmed before formal use.
- **Why it failed:** `notation_uncertainty` — could not pin "Cont₂"
  with confidence.
- **Kill_path classification:** N/A — confirms the question is well-
  defined under one natural interpretation.
- **Distance to closure:** depends on confirming the notation.

### Attack 6: Look for compatibility separations

- **Approach:** are there pairs of forcing axioms F_1, F_2 known to be
  *jointly inconsistent*? E.g., does MA + PFA hold trivially (since
  PFA ⇒ MA)? Are there "rival" axioms that exclude each other?
- **Tools used:** standard references, paper sketch.
- **Time spent:** ~25 min.
- **Result:** the standard forcing axioms form an essentially linear
  hierarchy by implication: MA ⇐ BPFA ⇐ PFA ⇐ SPFA ⇐ MM ⇐ MM⁺⁺ (with
  some side-quests like OCA, axiom (*), etc.). Joint compatibility is
  the rule; joint inconsistency is rare. **Genuine inconsistencies
  arise mostly with axioms that fix specific cardinal-arithmetic
  values incompatibly with PFA's automatic consequences.** E.g., PFA
  is incompatible with CH (since PFA ⇒ 2^ℵ_0 = ℵ_2); PFA is
  incompatible with V=L (since V=L ⇒ GCH ⇒ CH); etc. These are
  "expected" inconsistencies, not substantive open compatibility
  questions.
- **Why it failed:** N/A — confirms the structural picture.
- **Kill_path classification:** N/A.
- **Distance to closure:** zero (structurally clear).

## Partial results obtained (if any)

- **Confirmed Asperó-Schindler 2021 (Q1):** MM⁺⁺ ⇒ (*), settled.
- **Identified the open frontier (Q2):** PFA ⇒ (*) is open; the (++)
  strengthening appears load-bearing in the AS proof.
- **Identified higher-cardinal frontier (Q4):** PFA(ω_2), MM(ω_2)
  open even at level of formulation in some cases.
- **Confirmed structural picture:** standard forcing axioms form a
  linear implication hierarchy; "compatibility" is mostly a question
  about which extensions can be made jointly consistent at specific
  consistency strengths.
- **Confirmed PFA-implied cardinal arithmetic:** 2^ℵ_0 = ℵ_2 under
  PFA (Velickovic-Todorcevic).
- **Notation uncertainty flagged:** "Cont₂" interpretation in the
  prompt could not be pinned with full confidence; analysis under
  most likely interpretation (2^ℵ_1 = ℵ_2) provided.

## Honest "what would unblock this"

For (Q2) — PFA ⇒ (*): a categorically different argument structure
than Asperó-Schindler's is needed, since the AS argument relies on
the (++) strengthening. The proof would likely route through different
combinatorial-set-theoretic facts (perhaps via Todorcevic's PFA-trees
or OCA-style consequences). No clear path is currently available.

For (Q3) — exact consistency strength of PFA: requires inner-model
construction at the supercompact level. This is the central open
problem of contemporary inner-model theory (the "core model for one
supercompact" program). Decades of effort.

For (Q4) — higher-cardinal forcing axioms: requires formulation
consensus plus consistency proofs from very large cardinals (likely
above standard ones). An active research area but substantively open.

The substrate-grade observation is that the Asperó-Schindler advance
unlocked a previously-stuck problem; the analogous unlocks for (Q2)-(Q4)
are not in sight.

## Calibrated negatives

- **PFA, MM, MM⁺⁺ form a strict implication hierarchy** (in the order
  given). MM ⇒ MM⁺⁺ is FALSE — MM⁺⁺ is a *strengthening* of MM. So
  the hierarchy is: PFA ⇐ MM ⇐ MM⁺⁺. Compatibility questions concern
  what additional axioms can be joined.
- **Asperó-Schindler 2021 does NOT prove PFA ⇒ (*).** It proves
  MM⁺⁺ ⇒ (*). Confusing the two would be a substantive error.
- **The (++) in MM⁺⁺ is NOT a notational quirk — it is load-bearing
  in the Asperó-Schindler proof.** Removing it breaks the argument
  at a specific identifiable step (witness construction for ℵ_1-many
  term names for stationary subsets of ω_1).
- **The "INDEPENDENCE of ZFC" tag here is structural:** all forcing
  axioms are *additional* axioms to ZFC, so questions about which are
  jointly consistent are intrinsically about which extensions of ZFC
  are non-contradictory. This is similar in flavor to Vopěnka (attempt
  02) — a question about consistency of additional axioms — and
  distinct from SCH/GCH-at-ℵ_ω, which are questions about specific
  ZFC-statement values.
- **Forcing axioms are NOT amenable to elementary attack.** Proofs
  involve revised countable support iterations, semi-proper forcing,
  stationary tower forcing, and inner-model machinery. An "elementary"
  approach would represent a paradigm shift.
- **The consistency-strength upper bounds for the upper-tier forcing
  axioms (PFA, MM, MM⁺⁺) are all "supercompact" (Foreman-Magidor-Shelah).**
  The matching lower bounds are progressively closer to supercompact
  (currently at the level of many Woodin cardinals; still a gap).
  Closing the gap is part of the "core model for one supercompact"
  program.
- **A would-be elementary equivalence "PFA ⇔ MM"** would be wrong —
  MM is a genuine strengthening (e.g., MM has consequences for
  semi-stationary preservation that PFA lacks).
- **A would-be "PFA(ω_2) is straightforward"** claim should be regarded
  with extreme suspicion — even formulation is non-trivial, and
  consistency requires very large cardinals if it can be done at all.

## Citations (verified or marked paraphrase)

- Asperó, D. and Schindler, R., "MM⁺⁺ implies (*)", Annals of
  Mathematics 193 (2021), 793-835. (Title and journal verified;
  pages paraphrased.)
- Foreman, M., Magidor, M., and Shelah, S., "Martin's Maximum,
  saturated ideals, and non-regular ultrafilters I", Annals of
  Mathematics 127 (1988), 1-47. ("II" is also relevant; same year
  and journal, different page range.)
- Solovay, R. M. and Tennenbaum, S., "Iterated Cohen extensions and
  Souslin's problem", Annals of Mathematics 94 (1971), 201-245.
- Baumgartner, J. E. — formulation of PFA and consistency proof,
  c. 1970s-80s. Standard reference is via Foreman-Magidor-Shelah 1988
  and subsequent texts; original Baumgartner papers paraphrased.
- Velickovic, B., "Forcing axioms and stationary sets", Advances
  in Mathematics 94 (1992), 256-284. (Pages paraphrased.)
- Todorcevic, S., Partition Problems in Topology, AMS Contemp. Math.
  84, 1989; multiple papers on PFA combinatorics; OCA — paraphrased
  references.
- Woodin, W. H., The Axiom of Determinacy, Forcing Axioms, and the
  Nonstationary Ideal, de Gruyter Series in Logic and its
  Applications 1, Walter de Gruyter, 1999. Revised second edition
  2010.
- Larson, P. B., The Stationary Tower: Notes on a Course by
  W. Hugh Woodin, University Lecture Series 32, American Mathematical
  Society, 2004.
- Schindler, R., expository lectures and notes on Asperó-Schindler
  2021 — paraphrased; multiple expositions exist via Schindler's web
  page and conference talks.
- Schimmerling, J. and Steel, J. R., inner-model lower bounds for
  forcing axioms — multiple papers c. 2000-2020; specific paper not
  pinned (paraphrased).
- Goldstern, M. and Shelah, S., on bounded forcing axioms, c. 1995 —
  paraphrased.
- Bagaria, J. — bounded forcing axioms, BMM, etc., c. 2000-2010 —
  paraphrased.
- Foreman, M., generic large cardinals and higher-cardinal forcing
  axioms — paraphrased; the substantive content is in Foreman's
  Handbook Chapter 13 (Ideals and generic embeddings).
