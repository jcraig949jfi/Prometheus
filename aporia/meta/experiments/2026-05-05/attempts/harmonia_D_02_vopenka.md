# Attempt — Vopěnka's Principle (consistency strength placement)

**Researcher:** Harmonia D
**Date:** 2026-05-05
**Time spent:** ~3 hours
**Verdict:** PARTIAL_RESULT (literature-confirmation only) — Bagaria's
2012 characterization places VP precisely; the genuine open questions
are about *fine* placement and *natural* equivalences

## Problem statement

**Vopěnka's Principle (VP):** For every proper class of structures of
the same signature τ, there exist two structures M, N in the class
and a (non-trivial) elementary embedding M ↪ N.

Equivalent formulations include:
- Every locally presentable category has a small dense subcategory
  (Adámek-Rosický "Locally Presentable and Accessible Categories",
  1994, Cambridge Tracts in Math 189, Theorem 6.6 / surrounding
  discussion).
- For every n ≥ 1, there exists a proper class of C^(n)-extendible
  cardinals (Bagaria, "C^(n)-cardinals", Arch. Math. Logic 51 (2012),
  213-240).
- For every Σ_2-definable class function F: Ord → Ord, there is a
  critical point κ with V_κ a Σ_2-elementary substructure of V
  closed under F (one of several reflection-style equivalents).

**Strength placement (current best understanding):**
- Strictly above: every standard "below extendible" axiom (measurable,
  strong, Woodin, supercompact, extendible).
- Strictly below: I3 (a non-trivial j: V_λ → V_λ), and below
  Reinhardt-style axioms.
- Bagaria 2012: VP ⟺ ∀n (proper class of C^(n)-extendibles).

The remaining substantive open questions concern (i) whether VP is
strictly stronger than "proper class of C^(n)-extendibles for every
fixed n", (ii) the fine relationship to C^(n)-supercompactness, and
(iii) natural non-C^(n) equivalents.

## Literature scan: prior attempts

1. **Vopěnka (early 1960s, see Powell-Vopěnka announcements; Vopěnka's
   own monograph "Mathematics in the Alternative Set Theory" 1979 is a
   distinct project).** The principle was originally introduced in
   discussions with Powell and others; the canonical written reference
   is via subsequent authors. **Limitation:** the original was an
   informal axiom; substantive analysis took two decades.

2. **Solovay-Reinhardt-Kanamori, "Strong axioms of infinity and
   elementary embeddings"**, Annals of Math. Logic 13 (1978), 73-116.
   Located VP within the large-cardinal hierarchy and observed it
   sits above all the "standard" axioms below extendibility but is
   bounded by I3-style axioms. **Limitation:** placed it but did not
   characterize the exact location.

3. **Adámek-Rosický 1994** (Cambridge Tracts 189, "Locally Presentable
   and Accessible Categories"). Showed the surprising **category-
   theoretic** equivalent: VP ⟺ every locally presentable category has
   a small dense subcategory. Independently, VP characterizes the
   non-existence of large rigid classes in many natural categories.
   **Limitation:** the equivalent is *qualitative* — it does not pin
   down strength; it shows VP is the right axiom for a host of
   "reasonable smallness" results in category theory.

4. **Kanamori, "The Higher Infinite", 2nd ed. Springer 2003.**
   Chapter on Vopěnka places VP in the standard hierarchy with the
   then-known reductions; presents the implications-from-extendibles
   discussion. **Limitation:** pre-Bagaria; uses the older "almost
   huge" / extendible bracketing.

5. **Bagaria 2012** ("C^(n)-cardinals", Arch. Math. Logic 51, 213-240).
   The breakthrough exact characterization: VP is equivalent to
   "∀n, there is a proper class of C^(n)-extendible cardinals" and the
   parallel Σ_n / Π_n hierarchy of Vopěnka-like principles VP(Π_n)
   matches the C^(n)-extendibility hierarchy. This is the
   gold-standard placement result. **Limitation:** the equivalence
   is at the "global" level — fine-grained questions about the strict
   ordering of VP(Π_n) ↔ C^(n)-extendibility remain.

6. **Bagaria-Casacuberta-Mathias-Rosický, "Definable orthogonality
   classes in accessible categories are small"** (J. Eur. Math. Soc.
   17 (2015), 549-589). Develops the categorical-logic side of
   Bagaria's program; shows further category-theoretic statements
   (e.g., orthogonality classes are small) sit at exact VP-strength
   levels via the C^(n) framework. **Limitation:** powerful
   correspondences but no consistency-strength reductions of VP itself.

7. **Subsequent work (Tsaprounis, Magidor-Vaananen and others, c.
   2014-2020)** on virtual large-cardinal versions and on the
   relationship between VP and weaker reflection principles. **Limitation:**
   produces a richer landscape around VP but does not solve the precise
   open questions about strict implications among the C^(n)-extendible
   hierarchy levels.

## Attack surfaces tried (this attempt)

### Attack 1: Verify Bagaria's reduction by sketch

- **Approach:** re-derive (in outline) the implication
  "C^(n)-extendible cardinal class ⇒ VP for Π_{n+1} classes". The
  intuition: a C^(n)-extendible κ has elementary embeddings j:V_λ → V_μ
  with critical point κ where j is sufficiently nice on Σ_n statements;
  applying this to the "first two structures in the class" yields the
  desired embedding.
- **Tools used:** Bagaria 2012 §3-4, paper sketch.
- **Time spent:** ~40 min.
- **Result:** confirmed at sketch level. The C^(n) tower captures
  exactly the right level of reflection because VP for Π_{n+1} classes
  asserts that some pair of structures with Π_{n+1} properties satisfies
  the embedding condition; C^(n)-extendibility provides the embedding-
  closure on Σ_{n+1} / Π_{n+1} statements via the V_λ → V_μ embedding.
- **Why it failed:** N/A (this is verification, not advancement).
- **Kill_path classification:** N/A — confirms the existing answer.
- **Distance to closure:** zero (already established).

### Attack 2: Try to show VP(Π_{n+1}) > VP(Π_n) strictly

- **Approach:** the Bagaria hierarchy gives VP ⟺ ⋂_n VP(Π_n). Each
  VP(Π_n) is equiconsistent with "C^(n)-extendible exists" (or "proper
  class of C^(n)-extendibles" — the precise statement varies by
  formulation). Whether the consistency strengths are *strictly*
  ordered is a clean open question.
- **Tools used:** Bagaria 2012 §5, Tsaprounis on virtual variants
  (paraphrased).
- **Time spent:** ~40 min.
- **Result:** could not produce a separation. The direct attempt
  (force an inner model with C^(n)-extendibles but no C^(n+1)-
  extendibles) is exactly the kind of "core model for extendibles"
  problem that is open in inner-model theory generally. No
  fine-structural inner model for extendibles exists at the level
  of detail that would let one prove a strict separation here.
- **Why it failed:** `requires_unproven_conjecture` — separating
  VP(Π_n) from VP(Π_{n+1}) is essentially asking for the inner-model
  theory of C^(n)-extendibles, which is the open frontier of the
  Sargsyan-Steel-Trang program.
- **Kill_path classification:** REQUIRES_PARALLEL_OPEN_PROBLEM
  (inner model theory at extendibility level).
- **Distance to closure:** "1 inner-model-program short" — a peer-
  difficulty open program.

### Attack 3: Search for natural non-C^(n) equivalents

- **Approach:** is there a natural mathematical statement S, not
  expressed in terms of the C^(n) hierarchy, such that S is
  equivalent (in ZFC) to VP and that exposes new structure? The
  Adámek-Rosický category-theoretic equivalent is one such; are
  there others (e.g., from algebraic topology, from descriptive
  set theory)?
- **Tools used:** literature scan in category theory / accessible
  categories (Bagaria-Casacuberta-Mathias-Rosický 2015).
- **Time spent:** ~40 min.
- **Result:** several known non-C^(n) equivalents exist:
  (i) every locally presentable category has a small dense subcategory;
  (ii) every full subcategory of a locally presentable category closed
      under colimits is reflective;
  (iii) every cohomological localization of a locally presentable
      category exists (Bagaria-Casacuberta-Mathias-Rosický).
  All sit at the same VP strength. No new equivalent emerged from this
  attack that exposes hidden structure beyond what these surveys cover.
  In particular, no equivalent in classical descriptive set theory or
  inner-model theory that is qualitatively new.
- **Why it failed:** `surface_search_exhausted` — the natural-equivalents
  search has been worked thoroughly by category theorists; new natural
  equivalents would likely come from category-theoretic or
  homotopy-theoretic settings rather than classical set theory.
- **Kill_path classification:** N/A — exhausts a candidate angle.
- **Distance to closure:** unclear — potentially "1 unanticipated
  bridge short".

### Attack 4: Below — does VP have a non-trivial weakening that is
itself a useful axiom?

- **Approach:** the Bagaria hierarchy gives VP(Π_n) at each level. Are
  there strict-weaker-than-VP axioms (e.g., VP restricted to definable
  classes only) that are still strong enough to give the major
  category-theoretic consequences?
- **Tools used:** Bagaria 2012 §6 on "Definable VP", paper sketch.
- **Time spent:** ~30 min.
- **Result:** yes — Bagaria distinguishes "definable VP" (VP restricted
  to classes definable in second-order set theory) from "global VP".
  Definable VP suffices for the standard category-theoretic
  consequences and is strictly weaker in consistency strength than
  global VP. This is well-documented but the *exact* fine separation
  between "definable VP at level Π_n" and "C^(n)-extendible exists"
  has subtle bookkeeping issues (one-cardinal versus proper-class
  versions).
- **Why it failed:** N/A — confirms a known refinement.
- **Kill_path classification:** N/A.
- **Distance to closure:** zero on the sub-question; the fine
  bookkeeping question remains open.

### Attack 5: Inner-model lower bound — can VP be shown to imply
something specific about HOD or core models?

- **Approach:** if VP holds, does HOD (the class of hereditarily
  ordinal-definable sets) contain a C^(n)-extendible cardinal for
  every n? This is a "downward" reflection question of the kind
  that is sometimes tractable.
- **Tools used:** general inner-model literature scan; Woodin's
  HOD-conjecture program (paraphrased).
- **Time spent:** ~30 min.
- **Result:** there is an active program (Woodin and others) on
  whether sufficient large-cardinal strength reflects to HOD. The
  HOD Conjecture itself asserts that, above a sufficiently large
  cardinal, HOD is "close to V" in a specific sense (HOD-supercompactness
  inheritance). Whether VP suffices to make such reflection go through
  is not resolved. **No clean separation or implication produced
  here from this attack.**
- **Why it failed:** `requires_unproven_conjecture` (HOD Conjecture).
- **Kill_path classification:** REQUIRES_PARALLEL_OPEN_PROBLEM.
- **Distance to closure:** unclear — depends on resolution of the
  HOD Conjecture program.

## Partial results obtained (if any)

- **Confirmed Bagaria 2012 placement:** VP ⟺ ∀n (proper class of
  C^(n)-extendibles). This is the standard answer and is correct.
- **Identified the strict-separation question** (VP(Π_n) <
  VP(Π_{n+1})?) as the principal *fine-grained* open question and
  matched it to the inner-model-theory frontier.
- **Identified definable VP** as a known strict weakening; substrate-
  grade information that "VP" and "definable VP" are distinct.
- **Confirmed no new natural-equivalent** emerged from a focused
  literature scan; the known list (Adámek-Rosický + descendants) is
  the current state.

## Honest "what would unblock this"

Two distinct unblocks:

(A) For **strict separations within the VP(Π_n) hierarchy**: an inner-
model construction at the level of extendibles. This is one of the
central open problems of contemporary inner-model theory, on the
Sargsyan-Steel-Trang program's roadmap. Decades of effort.

(B) For **new natural equivalents**: a bridge from category theory or
homotopy theory to a previously-unanticipated classical-set-theoretic
formulation. The existing bridge (locally presentable categories) is
40 years old; a new one would likely come from a different
mathematical area (perhaps higher topos theory, or stable homotopy
theory's localization functors).

Neither of these is a single-lemma unblock; both are programs.

## Calibrated negatives

- **VP's consistency strength is NOT located by some non-extendibility
  large-cardinal axiom.** Specifically, no measurable, no Woodin, no
  supercompact characterizes VP — Bagaria 2012 closed this. VP is
  intrinsically a "C^(n)-extendibility tower" axiom.
- **VP is NOT equivalent to "extendible exists" or even "proper class
  of extendibles".** A single extendible is C^(1)-extendible (and
  more); the full VP requires the full tower. This is a load-bearing
  distinction.
- **The categorical equivalents (Adámek-Rosický) do NOT make VP a
  category-theoretic axiom in the foundational sense.** They are
  *witnesses* to its strength via specific mathematical structures,
  not alternative foundations.
- **Forcing CANNOT decrease the strength of VP** (in the standard
  way) because VP holds in V iff VP holds in any class-generic
  extension preserving Ord (small forcings preserve VP; class forcings
  may or may not). This rules out any "naive" attack via forcing
  ZFC + ¬VP.
- **The "INDEPENDENCE of ZFC" tag applies in a specific, weaker
  sense than for SCH:** VP is an *additional axiom*, not a question
  whose negation is independent. ZFC neither proves nor disproves VP
  (assuming ZFC + LC consistent). VP is a candidate for inclusion in
  an extended foundational system, like supercompacts or Woodins.
- **A would-be "elementary proof" of any VP(Π_n) → VP(Π_{n+1})
  separation should be regarded with extreme suspicion.** Such a
  separation is at the frontier of inner-model theory; an elementary
  argument would be a major event with widespread consequences.

## Citations (verified or marked paraphrase)

- Adámek, J. and Rosický, J., Locally Presentable and Accessible
  Categories, Cambridge Tracts in Mathematics 189, Cambridge
  University Press, 1994. (See chapter on Vopěnka's principle and
  the small-dense-subcategory equivalence.)
- Bagaria, J., "C^(n)-cardinals", Archive for Mathematical Logic 51
  (2012), 213-240. (Title and journal verified; year is when
  published, the preprint circulated earlier in c. 2010.)
- Bagaria, J., Casacuberta, C., Mathias, A. R. D., and Rosický, J.,
  "Definable orthogonality classes in accessible categories are
  small", Journal of the European Mathematical Society 17 (2015),
  549-589. (Pages paraphrased.)
- Kanamori, A., The Higher Infinite: Large Cardinals in Set Theory
  from Their Beginnings, 2nd ed., Springer, 2003. (Chapter on Vopěnka.)
- Solovay, R., Reinhardt, W., Kanamori, A., "Strong axioms of infinity
  and elementary embeddings", Annals of Mathematical Logic 13 (1978),
  73-116. (Standard reference; pagination as commonly cited.)
- Tsaprounis, K., "On extendibility and beyond", various papers c.
  2013-2018; specific paper not pinned (paraphrased reference).
- Woodin, W. H., HOD Conjecture and related work — paraphrased
  reference; the canonical form is in Woodin's "Suitable Extender
  Models" papers (Journal of Mathematical Logic, c. 2010-2017),
  exact issues paraphrased.
- Vopěnka, P. — original introduction of VP in the 1960s; canonical
  written form is via Solovay-Reinhardt-Kanamori 1978 and Kanamori's
  Higher Infinite. The original Vopěnka attribution is paraphrased.
- Powell, W., "Almost huge cardinals and Vopěnka's principle" —
  paraphrased; one of the early analyses, exact venue (Notices /
  conference) not verified.
