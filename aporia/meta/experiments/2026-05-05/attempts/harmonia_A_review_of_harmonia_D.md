# Cross-Batch Review — Harmonia A on Harmonia D

**Reviewer:** Harmonia A (Harmonia_M2_sessionA)
**Date:** 2026-05-05
**Batch reviewed:** Harmonia D — Logic / Foundations (P1 SCH, P2 Vopěnka,
P3 Whitehead, P4 GCH at singulars, P5 Forcing Axioms compatibility)
**Files reviewed:**
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_D_01_singular_cardinals_hypothesis.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_D_02_vopenka.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_D_03_whitehead.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_D_04_gch_singular.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_D_05_forcing_axioms.md`
- batch prompt at `D:\Prometheus\aporia\meta\experiments\2026-05-05\batch_harmonia_D.md`

**Note on review redundancy:** D has already been reviewed by Harmonia B
(at `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_B_review_of_harmonia_D.md`)
and Harmonia E
(at `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_E_review_of_harmonia_D.md`).
This review is a third perspective from the combinatorics-trained outsider
position. I have not read those reviews (intentional — keeps my read
independent). My review may overlap or contradict; both signals are
substrate-grade.

---

## 0. Top-line verdict

**D's batch is the most literature-dense and the least computational of the
batches I have reviewed.** That is structurally honest: foundations problems
about cardinal arithmetic, large-cardinal placement, and forcing-axiom
compatibility don't admit small-scale numerical experiments the way
combinatorics, dynamics, or analysis do. D correctly recognized this —
none of the 5 attempts pretends a numerical experiment moved the open
question, and the *attack templates* are visibly adapted to the domain
(literature scan / structural verification / sketch-level argument /
calibrated negative).

**The strongest single output of D's batch is the kill_path classification
taxonomy** (TECHNIQUE_DOMAIN_LIMIT, SHELAH_INDEPENDENCE,
REQUIRES_PARALLEL_OPEN_PROBLEM, REQUIRES_NEW_TECHNIQUE, etc.). This is
substrate-grade: it formalizes the *diversity* of "ways an attack can
fail" beyond the standard verdict tags, and several of the named classes
generalize to other batches (e.g., Class A "missing rigidity functional"
in Harmonia B's batch maps cleanly onto REQUIRES_PARALLEL_OPEN_PROBLEM).

**The structural weakness of the batch is what's NOT done:** zero
machine-verified proof checks (no Lean / Isabelle / Coq / mathlib query),
zero citation verification (the load-bearing references like
Asperó-Schindler 2021 *Annals* 193 are real and verifiable in seconds —
D leaves them paraphrase-flagged), and zero engagement with the
*formalization frontier* of set theory (which is itself moving fast and
is a genuine round-2 axis for any foundations batch).

**Falsification-first read on D's own claims.**
- "No finite computational handle" (P1 Attack 4) is half-right. There's
  no finite analogue of `2^ℵ_ω`. But there ARE finite computational
  handles for specific structural lemmas in PCF (the "no-hole" theorem,
  the localization theorem) at small ordinals; for tree-property /
  square-principle violations at small successor cardinals; for Bagaria's
  C^(n)-extendibility tower at small `n` in mathlib-style formalization;
  and for verifying that specific forcing constructions preserve specific
  properties via finite-state-machine analysis. D categorically rules
  out a route that is partially open.
- "Whitehead's general problem is settled" (P3 verdict) is correct in the
  classical sense, but the *formalization* status is a separate axis.
  Last I checked, the Shelah 1974 independence proof is *not* formalized
  in mathlib or Isabelle's HOL. That is a substrate-grade open task — a
  formalization gap that is open in a different sense than the
  mathematical question.
- "Vopěnka's natural-equivalents search has been worked thoroughly"
  (P2 Attack 3) is true if "thoroughly" means "by category theorists for
  40 years." But the *homotopy-type-theoretic* and ∞-categorical
  equivalents are a younger frontier. D briefly mentions "perhaps higher
  topos theory, or stable homotopy theory's localization functors" then
  doesn't push.
- The "REQUIRES_PARALLEL_OPEN_PROBLEM" tag is applied 4+ times. That's
  fine bookkeeping but the tag becomes near-vacuous if applied to *any*
  open question that depends on another open question. A sharper
  taxonomy would distinguish "depends on a peer-difficulty open
  problem" from "depends on a strictly weaker open problem" from
  "depends on a strictly stronger open problem."

This review is friendly. The batch is solid; the round-2 question is
genuinely harder for foundations than for the other batches.

---

## 1. Per-problem critique and round-2 proposals

### P1 — Singular Cardinals Hypothesis (SCH)

**Critique of round 1.**
- Six attacks across the structural map: Silver-bound re-derivation
  (Attack 1, confirmed cf-restricted), Shelah PCF bookkeeping
  (Attack 2, identified the +3 in ℵ_{ω₄}), Gitik-Mitchell tightness
  (Attack 3, confirmed closed at o(κ)=κ⁺⁺), finite-model probe
  (Attack 4, ruled out), pp-function reformulation (Attack 5,
  REQUIRES_PARALLEL_OPEN_PROBLEM = SH), independence-of-independence
  (Attack 6, ruled out). Solid coverage.
- The cleanest substrate-grade observation in the attempt is the
  **structural decomposition of Shelah's bound: the "+3" in ℵ_{ω₄}
  comes from three chained inequalities** (localization → no-hole →
  ω₃-step → closure ordinal ω₄). Improving any one drops the overall
  bound. This is *concrete, modular, attackable* substrate
  information. D mentions it but doesn't extract it as a methodology
  candidate.
- Attack 4 (finite model probe) is dismissed as
  `non_constructive` / `comp_ceiling`. The dismissal is correct
  *for cardinal-arithmetic value at ℵ_ω*. But D could have used a
  countable transitive model construction to verify that the *Silver
  argument* runs correctly internally — i.e., calibrate the proof,
  not the bound. Mizar / Lean / Isabelle have machinery for this and
  D didn't probe.

**Round-2 proposal.**

1. **Mathlib / Lean / Isabelle formalization status check.** What
   parts of the Silver argument, the PCF machinery, and the
   Gitik-Mitchell equiconsistency are currently formalized? Where are
   the gaps? This is a 30-minute query plus a write-up; produces a
   concrete map of "what's machine-verified vs paper-only" for SCH.
   Substrate-grade because it surfaces the formalization frontier as a
   parallel kill-data axis.
2. **Symbolic verification of the three structural inequalities in
   Shelah's bound.** The localization theorem, no-hole theorem, and
   closure-ordinal step each have explicit statements that can be
   checked by hand (or by a proof assistant) on small explicit
   cofinality structures. Build a small Python program that, given a
   finite-structure encoding of an ordinal interval, verifies the
   PCF relations numerically. This isn't a proof but is a sanity-check
   tool for any future PCF probe.
3. **Cross-cutting check vs the Sargsyan-Trang 2024-2026 program.**
   Sargsyan and collaborators have been actively pushing the
   inner-model frontier in the period D's literature scan covers. A
   focused arXiv search for "hod mouse SCH" with date filter
   ≥ 2023 may surface refinements D hasn't tracked. ~30 minutes.
4. **Read the original proofs at non-sketch level.** D's Attack 1 is
   "verify Silver's argument from first principles to confirm the
   structural step that fails at countable cofinality." This is
   marked confirmed at sketch level; a careful read of the actual
   stationary-set Fodor argument at the proof level (vs the textbook
   summary level) may surface a candidate non-stationarity-based
   proof attempt. Substrate-relevant: the gap between "I know the
   sketch" and "I've verified the proof step-by-step" is exactly
   where new ideas come from.

**Round-2 verdict candidate:** PARTIAL_RESULT (formalization-frontier
map; symbolic PCF verifier; tightened literature scan).

**Effort estimate:** ~3-4 hours.

---

### P2 — Vopěnka's Principle

**Critique of round 1.**
- Bagaria 2012 placement is correctly anchored: VP ⟺ ∀n proper class
  of C^(n)-extendibles. D verifies at sketch level. Solid.
- Attack 2 (try to show VP(Π_{n+1}) > VP(Π_n) strictly) is correctly
  identified as the inner-model frontier. The
  REQUIRES_PARALLEL_OPEN_PROBLEM tag is right.
- Attack 3 (search for natural non-C^(n) equivalents) is the
  highest-leverage missed opportunity. D writes "no new equivalent
  emerged from this attack" but the search was confined to a
  literature scan in classical category theory. The relevant frontier
  for *new* equivalents is:
    - Higher topos theory (Lurie's HTT, ∞-categorical accessible
      categories)
    - Univalent foundations (HoTT-Book Chapter 11 onwards on size
      issues; the Lurie-Lawvere-Tierney smallness-of-localizations
      story)
    - Homotopy-type-theoretic versions of locally presentable
      structures
  D mentions "perhaps higher topos theory" as a placeholder; doesn't
  probe. **A 1-hour focused arXiv search for "Vopěnka ∞-categorical"
  or "Vopěnka HoTT" likely surfaces papers D hasn't tracked.**
- Attack 5 (HOD inner-model lower bound) correctly identifies the
  Woodin HOD-Conjecture as the relevant open problem. Solid.

**Round-2 proposal.**

1. **arXiv search: Vopěnka in ∞-categorical / HoTT contexts.** Date
   filter ≥ 2018. Look for Lurie-circle papers, HoTT papers, and
   topos-theoretic papers using VP-equivalent statements. This is the
   single highest-leverage round-2 action for P2. ~1 hour.
2. **Mathlib / Coq / Agda formalization status of VP and the C^(n)
   tower.** Not all proof assistants have ordinals up to extendible
   strength, but mathlib has ordinals; whether the C^(n) hierarchy is
   even *expressible* in current mathlib is itself substrate-grade
   information. ~30 minutes.
3. **Bagaria-Casacuberta-Mathias-Rosický 2015 deep read.** D scanned
   it for natural equivalents and found "orthogonality classes are
   small" + "cohomological localization exists." A more careful read
   for the *categorical-logic infrastructure* (definability,
   accessibility, locally presentable category structure as a
   formalization target) might surface additional equivalents at
   strict-VP-strength. ~1.5 hours.
4. **Tsaprounis virtual large-cardinal angle.** D mentions Tsaprounis
   on virtual variants but doesn't probe. Virtual VP / virtual
   C^(n)-extendibility is a recent (post-2015) line that lowers
   consistency strength while preserving structural consequences. An
   arXiv check + brief survey could surface a new "natural variant"
   axis. ~1 hour.

**Round-2 verdict candidate:** PARTIAL_RESULT (∞-categorical
equivalents survey; formalization status; virtual-VP map).

**Effort estimate:** ~3-4 hours.

---

### P3 — Whitehead Problem

**Critique of round 1.**
- This is the cleanest "settled" case in the batch — Shelah 1974 is
  the canonical "substrate is the obstruction" example. D correctly
  identifies that the substantive open instances inherit
  Shelah-independence in transparent ways.
- Six attacks, all of which converge on SHELAH_INDEPENDENCE.
  Methodologically clean; substantively unilluminating because the
  question really IS settled.
- **The genuinely interesting axis D doesn't probe is the
  formalization status.** Shelah 1974 is, to the best of my
  recollection, NOT formalized in any major proof assistant. The
  positive direction (V=L → every Whitehead group free) requires
  ◇_{ω₁}-style construction; the negative direction (MA + ¬CH → non-free
  Whitehead groups exist) requires forcing machinery. **Whether
  either has been mechanized is a load-bearing substrate question.**
- D's "honest what would unblock this" answer — "find a
  Whitehead-equivalent property that does not depend on the global
  combinatorics of Ord" — is a real conceptual move. But the prior on
  this succeeding is essentially zero (D acknowledges); the
  practical round-2 angle is the formalization one.
- **Trlifaj-style cotorsion-theoretic generalizations** (Attack 4) get
  one paragraph. The tilting-theory / silting-theory / cotorsion-pair
  literature has expanded substantially in the 2010s-2020s; whether
  there are *new* slender-ring instances where Whitehead-class
  questions are ZFC-decidable is plausibly open. D doesn't probe.

**Round-2 proposal.**

1. **Formalization status of Shelah 1974 in mathlib / Isabelle / Coq.**
   The expected answer is "neither direction formalized." Confirming
   this, mapping the gap, and identifying the *blocking* primitives
   (forcing, ◇, MA) is substrate-grade. ~1 hour.
2. **Survey 2015-2025 cotorsion / silting / tilting literature for
   ZFC-decidable Whitehead-class results over exotic rings.** Trlifaj
   and collaborators have continued; recent papers may have produced
   new ZFC-decidable instances. ~2 hours.
3. **Sheaf / topos-theoretic Whitehead variants.** The original
   Whitehead problem is about Ext¹(A, ℤ); sheaf cohomology versions
   over various sites give related questions. Whether these inherit
   Shelah-independence cleanly or admit ZFC-decidable instances is a
   real open axis. Survey + sketch. ~1 hour.
4. **Computational verification at *small* uncountable cardinals via
   countable transitive models.** Build a CTM of ZFC + V=L, identify
   what its Whitehead question looks like at ℵ_1^M, verify the
   ◇_{ω₁}^M construction internally. This is mechanizable in
   principle (much harder in practice). At minimum the *outline* of
   such a construction would be substrate-relevant.

**Round-2 verdict candidate:** NO_PROGRESS_DOCUMENTED_OBSTACLES
remains correct. The round-2 *output* is a formalization gap map and
a refreshed cotorsion-frontier survey, not a closer move on the
mathematical question.

**Effort estimate:** ~3-4 hours.

---

### P4 — GCH at singulars (specifically 2^ℵ_ω)

**Critique of round 1.**
- This attempt and P1 SCH overlap heavily — both are about Shelah PCF
  bounds at ℵ_ω. D acknowledges the overlap implicitly (P4 references
  the same Cardinal Arithmetic 1994 + Gitik machinery). **The
  five-problem framing of D's batch has a structural redundancy:
  P1 and P4 are essentially the same problem viewed from different
  angles, and the batch would arguably have been better with P1 OR
  P4 plus a different fifth problem.** I'd flag this for batch-design
  review, not as D's failure.
- Attack 6 (computational PCF in specific models) is the most
  promising direction in the attempt and is sketched, not run. "What
  is pp(ℵ_ω) explicitly in V=L vs in Magidor's 1977 model vs in
  Gitik's various models" is a *bookkeeping* question that admits
  partial mechanization: build a small Python program that
  manipulates the PCF combinatorics symbolically and produces the
  characteristic values for each model.
- D's "substrate-grade observation" — the Easton-vs-PCF asymmetry —
  is the strongest single insight. *Regulars wild, singulars
  constrained.* This is genuinely substrate-grade and worth promoting
  to a methodology toolkit entry.

**Round-2 proposal.**

1. **Build a PCF symbolic calculator.** `harmonia/runners/pcf_calculator.py`.
   Given an interval `a` of regular cardinals, compute (symbolically) the
   bounds from localization + no-hole + closure-ordinal. Verify
   pp(ℵ_ω) = ℵ_{ω+1} in V=L and pp(ℵ_ω) = ℵ_{ω+2} in Magidor's
   model by direct symbolic computation. Solid substrate primitive
   for any future PCF-flavored work. ~3 hours.
2. **Formalization status of Shelah PCF in mathlib / Isabelle.**
   Same query as for SCH; the answer is presumably "not yet." Map
   the gap. ~30 minutes.
3. **Gitik 2020-2026 extender-based forcing literature scan.** The
   consistency frontier moves with each new Gitik paper; D's literature
   scan is recall-only. arXiv search ≥ 2020 for "extender-based forcing
   Prikry" + "singular cardinal hypothesis" likely surfaces results
   D hasn't tracked. ~1 hour.
4. **Promote Easton-vs-PCF asymmetry to methodology toolkit.** Anchor:
   the 2^κ-at-regular vs 2^κ-at-singular structural difference. Write
   the entry in `harmonia/memory/methodology_toolkit.md`. Pattern:
   "structural asymmetries within a problem class are themselves
   substrate-grade observations and hint at where the right
   instruments live." ~30 minutes.

**Round-2 verdict candidate:** PARTIAL_RESULT (PCF calculator built;
Easton-PCF asymmetry promoted; updated literature frontier).

**Effort estimate:** ~5 hours, mostly the PCF calculator.

---

### P5 — Forcing Axioms Compatibility

**Critique of round 1.**
- Asperó-Schindler 2021 boundary correctly anchored: MM⁺⁺ ⇒ (*) closed,
  PFA ⇒ (*) open. D verifies the AS proof structure at sketch level.
  Solid.
- Attack 5 (Cont₂ notation uncertainty) is honest — D explicitly
  flags `notation_uncertainty` and provides analysis under the most
  likely interpretation. This is exactly the falsification-first
  discipline. Good.
- The single highest-leverage missing action: **the AS 2021 paper has
  been heavily expounded by Schindler in lecture notes and surveys;
  some of these are publicly available and should have been pulled
  before sketch-verification.** D pulls Schindler "various survey
  lectures" as paraphrased and doesn't fetch.
- Attack 4 (forcing axioms at higher cardinals, PFA(ω_2) etc.) is the
  active frontier. D acknowledges "open even at level of formulation"
  but doesn't engage with the *specific* recent formulations
  (Neeman's PFA(ω_2), Yorioka, Aspero-Veličković on side conditions).
  This is the post-2015 active frontier and D's recall is hazier here.

**Round-2 proposal.**

1. **Verify the Asperó-Schindler 2021 citation** (Annals 193, 793-835)
   directly via arXiv. ~2 minutes. Removes `[paraphrase]` flag.
2. **Schindler's expository materials.** Pull at least one of: arXiv
   talk slides, conference video transcript, or published expository
   paper on AS 2021. Replaces sketch-verification with informed
   summary. ~1.5 hours.
3. **Higher-cardinal forcing axioms post-2015 literature scan.**
   Neeman's PFA(ω_2), Aspero-Veličković side-condition methods, recent
   Yorioka work. arXiv search ≥ 2015 for "forcing axiom" + "ω_2".
   ~1.5 hours.
4. **Map the (*)-implication graph.** Build a small Python /
   Graphviz diagram: nodes are forcing axioms (MA, BPFA, PFA, MM,
   MM⁺⁺, (*)); edges are proven implications + implications open
   under standard hypotheses. The PFA → (*) status as "open" should
   appear visually. Substrate-grade because the graph form is
   reusable for other axiom-hierarchy questions. ~1 hour.
5. **Sargsyan-Steel-Trang core-model-for-supercompact program update.**
   PFA's exact consistency strength gates on this program. arXiv
   search ≥ 2022. ~30 minutes.

**Round-2 verdict candidate:** PARTIAL_RESULT (citation verified,
post-2015 frontier mapped, implication graph shipped, expository
materials integrated).

**Effort estimate:** ~5 hours.

---

## 2. Cross-cutting infrastructure proposals

These are *shared* primitives for foundations work. They are
qualitatively different from the infrastructure proposals I made for
B's and C's batches because foundations doesn't sit at a numerical
level.

### Tool 1 — arXiv API verifier
`harmonia/runners/citation_verify.py`. Same as I proposed for B's
batch. The Asperó-Schindler 2021 *Annals* 193 example shows the same
pattern as B's Fleischer 2024 incident: a load-bearing reference is
flagged `[paraphrase]` when 30 seconds of arXiv search resolves it.
**This tool generalizes across every batch, not just dynamics or
foundations.** ~2 hours to build.

### Tool 2 — Mathlib / Lean / Isabelle formalization-status query
`harmonia/runners/formalization_status.py`. Given a mathematical
statement (e.g., "Silver's theorem on SCH at uncountable cofinality"),
query mathlib's online status pages, Isabelle AFP entries, Coq
mathematical components, and report what is formalized vs missing.
Substrate-grade because it makes the formalization frontier a
*queryable axis* parallel to the open-problem frontier. ~3-4 hours
to build a v0.1.

### Tool 3 — PCF symbolic calculator
`harmonia/runners/pcf_calculator.py`. Sketched in P4 round-2
above. Computes pp-function bounds for explicit cardinal interval
inputs; verifies localization + no-hole + closure-ordinal lemmas;
produces the characteristic values for V=L, Magidor 1977, and other
named models. ~3 hours.

### Tool 4 — Forcing-axiom implication graph
`harmonia/runners/forcing_axiom_graph.py`. Codifies the implication
hierarchy among MA, PFA, MM, MM⁺⁺, BPFA, (*), etc., with edges
labeled "proven", "open", "false". Outputs Graphviz / Mermaid. As
new results land, edges get updated. Substrate-grade because the
graph is the *current state* of P5's open frontier. ~1 hour.

### Tool 5 — Kill-path classification taxonomy as substrate primitive
This is D's own contribution. D used named tags
(TECHNIQUE_DOMAIN_LIMIT, SHELAH_INDEPENDENCE, REQUIRES_PARALLEL_OPEN_PROBLEM,
REQUIRES_NEW_TECHNIQUE, REQUIRES_FOUNDATIONAL_REFINEMENT, etc.).
**Promote to `harmonia/memory/methodology_toolkit.md` as a
classification taxonomy for attempt-failure modes.** Apply
retroactively to A, B, C batches' attempts to verify the taxonomy
covers all observed failure modes. If gaps appear, refine the
taxonomy. ~2 hours.

### Dataset 1 — Independence-status registry
For each open foundations problem in D's batch (and beyond), a
canonical record:
- Open or settled?
- If settled, by which independence proof?
- If open, what is the consistency-strength range?
- What is the formalization status?
- What recent (≥ 2020) advances have been made?

Stored at `harmonia/memory/foundations_independence_registry.md`.
Substrate-grade because it externalizes information that currently
lives in D's training-data recall (and hence is haziness-flagged).
~3 hours to seed with the 5 batch problems plus 5-10 obvious adjacents
(Suslin, square, tree property, V=HOD, etc.).

### Dataset 2 — PCF / large-cardinal hierarchy diagram
A canonical reference diagram of the large-cardinal hierarchy with
known and conjectured strict implications. Updated as new
equiconsistencies / strict-implications land. Currently scattered
across Kanamori, Jech, Cummings; consolidated form would be
substrate-grade. ~2 hours.

---

## 3. Additional solution angles

For foundations problems the "additional angles" are necessarily
speculative and meta-level. None is a path to closure; each is a
candidate axis worth probing in a "novelty budget" fraction of round 2.

### P1 / P4 — SCH / GCH-at-singulars
- **Constructive set theory angle.** In intuitionistic set theory
  (IZF), or in CZF, what does the cardinal arithmetic look like? Is
  there a constructive analogue of PCF? Speculative; some work
  exists (Aczel, Rathjen) but the bridge to classical PCF bounds is
  unclear.
- **Ultrafinitism / strict-finitist analogues.** In a foundation
  that rejects actual infinities, the questions reduce to
  combinatorial properties of *very large but finite* models. PCF
  has finite analogues that don't transfer cleanly (D notes this in
  P4 Attack 5) but might transfer differently in a strict-finitist
  framework. Highly speculative.

### P2 — Vopěnka
- **HoTT / univalent foundations.** As mentioned above, the
  size-issues chapter of the HoTT book and subsequent work
  (Awodey-Voevodsky-Lumsdaine) treat smallness via universe levels.
  Whether VP corresponds to a univalent universe condition is open
  and would be a genuinely new equivalent if found.
- **∞-categorical accessibility.** Lurie's HTT formalizes
  presentability for ∞-categories. The VP-equivalent
  "every locally presentable category has a small dense subcategory"
  has an ∞-categorical analogue. Whether the analogue is equivalent
  to VP in classical set theory, or strictly weaker / stronger, is
  open as far as I know.

### P3 — Whitehead
- **Derived-categorical / spectrum-of-modules angle.** Modern
  homological algebra views Ext via derived categories; whether
  triangulated-category structure on D(Ab) gives ZFC-decidable
  Whitehead-analogues is plausibly studied (Trlifaj circle) but D
  doesn't engage with the recent literature here.
- **Univalent foundations Whitehead.** In HoTT, what does
  Whitehead's question look like? Speculative; the higher inductive
  type machinery may give a different answer than ZFC-Whitehead.

### P5 — Forcing axioms
- **Generic-multiverse perspective.** Hamkins's set-theoretic
  multiverse views forcing extensions as parallel "worlds." The
  compatibility questions translate to "which multiverse positions
  satisfy which axiom combinations." This reframes the questions
  but doesn't immediately solve them. Speculative.
- **Reverse-mathematics-style strength comparison.** Map forcing
  axioms onto the second-order arithmetic hierarchy (where they
  project) and ask which of RCA_0 / WKL_0 / ACA_0 / ATR_0 / Π¹_1-CA_0
  prove specific consequences. Already partially done; D doesn't
  engage with reverse-math angle.

---

## 4. Recommended round-2 sequencing

Foundations round 2 is qualitatively different from numerical-batch
round 2. The high-leverage actions are mostly *queries* (arXiv,
mathlib, recent literature) and *infrastructure* (PCF calculator,
implication graph, classification taxonomy promotion), not
experiments.

If round 2 is greenlit at ~15h budget:

1. **Build Tool 1 (arXiv verifier) first.** ~2 hours. Same
   recommendation as for B's batch. Citation verification is
   load-bearing across all foundations work.
2. **Build Tool 2 (formalization status query) v0.1.** ~3 hours.
   Surfaces the formalization frontier as a parallel kill-data axis.
3. **Promote D's kill_path classification taxonomy to substrate
   primitive.** ~2 hours. Apply retroactively to A, B, C; verify
   coverage; refine if gaps appear.
4. **P4 round 2** (~5 hours): build PCF symbolic calculator;
   formalization status check; Gitik 2020-2026 scan; promote
   Easton-PCF asymmetry to methodology toolkit. Highest concrete
   output in the batch.
5. **P5 round 2** (~5 hours): verify AS 2021 citation; pull Schindler
   expository materials; map post-2015 higher-cardinal forcing
   frontier; build implication graph.
6. **P1 / P3 round 2** (~3 hours each): formalization status; targeted
   literature refresh.
7. **P2 round 2** (~3 hours): ∞-categorical / HoTT equivalents
   search; virtual-VP map; mathlib status.

Total ~28 hours, well past the 15h budget.

If 15h is hard, the lean version is: **Tools 1, 2, 5 + P4 round 2 +
P5 round 2** = ~17 hours. That captures the highest-value
substrate-grade output (citation verifier, formalization frontier,
classification taxonomy promoted, PCF calculator, post-2015 forcing
axiom map).

**Compounding return.** Tools 1, 2, 5 amortize across *every* batch
in the substrate. They are particularly load-bearing for foundations
because foundations work has higher citation-density and higher
[paraphrase]-flag density than the other batches.

---

## 5. Methodology-toolkit candidates: discipline check

D's batch produces several candidates. Anchor-count discipline says
hold each until a second anchor surfaces.

**Candidate A — Kill-path classification taxonomy.** Anchor: D's
own batch (5 problems × 6 attacks each = 30 attempts, classified).
Strong single-batch anchor. **Recommend: promote to
`harmonia/memory/methodology_toolkit.md` immediately and apply
retroactively to A, B, C batches. The retroactive application is
itself the second anchor.**

**Candidate B — Independence-vs-open distinction as a kill-path
class.** D's batch prompt explicitly frames this; D operationalizes
it consistently. **Recommend: this is essentially a sub-class of
Candidate A; promote together.**

**Candidate C — Easton-vs-PCF structural asymmetry as a substrate-
grade observation pattern.** Anchor: P4. **Recommend: hold as
candidate. Second anchor would be a similar structural-asymmetry
observation in a *different* substrate (e.g., the
"hyperbolic-vs-non-hyperbolic" asymmetry in B's Palis attempt is a
candidate parallel; the
"surviving-the-coordinate-change-vs-not" asymmetry across all
batches is potentially a third).**

**Candidate D — "Sketch-level verification is not the same as
proof-level verification."** D consistently flags Attack 1 of P1, P2,
P5 as "sketch-level confirmed." This is honest discipline but is
also a gap — the substrate's confidence is calibrated to sketch level,
not proof level. **Recommend: this is operating-discipline guidance,
not a promotable pattern; add to operating-disposition notes.**

**Candidate E — "Two-class problem taxonomy: settled-by-independence vs
constrained-with-open-fine-structure"** (cross-distinction across the
batch). The cleanest example: P3 Whitehead is settled-by-independence;
P1 SCH is settled-as-consistency-strength but constrained-with-open-
fine-structure (the value of 2^ℵ_ω). **Recommend: hold as candidate;
this taxonomy generalizes across foundations more than across the
other batches.**

---

## 6. What I might be wrong about

- **The "no computational handle" critique might be unfair.** D
  correctly recognized that foundations problems don't admit small-N
  numerical experiments. My critique is that *formalization-frontier*
  and *symbolic PCF* are computational handles D didn't probe. But
  they are computational handles of a qualitatively different kind
  (machine-verified proof; symbolic combinatorial bookkeeping); the
  batch prompt arguably didn't ask for these and D's
  literature-scan-heavy approach was budget-appropriate.
- **My "Asperó-Schindler citation costs 30 seconds to verify" claim**
  assumes arXiv access is available. D may have been working without
  network access; in that case the [paraphrase] flag is appropriate
  and my critique misfires. If round 2 is run in an environment with
  arXiv access, the verifier becomes high-leverage; if not, it
  remains only a paper recommendation.
- **The "five-problem framing has structural redundancy" critique**
  (P1 vs P4 overlap) is real but not D's responsibility — that's a
  batch-design issue, owned by Aporia. I should flag it to Aporia
  separately rather than counting it against D.
- **The HoTT / ∞-categorical Vopěnka angle** is real but my recall
  of the post-2015 literature here is hazy. I am near-certain such
  work exists but I haven't pinned specific papers. My round-2
  proposal asks D to do the search I haven't done; that's appropriate
  delegation but I should be honest that I don't know whether the
  search will surface novelty.
- **The kill_path classification taxonomy promotion** I'm
  recommending may be premature. D used the tags consistently across
  one batch; whether they generalize cleanly is exactly what
  retroactive application would test, and the test might fail (my
  combinatorics batch's failure modes might not fit cleanly into D's
  taxonomy). The recommendation is "promote and test"; the test is
  the second anchor.

---

## 7. Closing read

Harmonia D's batch is the most literature-dense of the four batches
I have reviewed (A, B, C, D). Its strongest substrate-grade output is
the kill_path classification taxonomy — a primitive that generalizes
across batches and is worth promoting today, with retroactive
application to A/B/C as the second-anchor test. Its weakness is the
absence of formalization-frontier engagement: mathlib / Lean /
Isabelle have ongoing set-theory formalization that is itself a
parallel "kill data" axis D didn't probe.

Across all four batches, the same structural pattern recurs:
~50% budget used, ~2/3 of the listed attacks marked
"sketched, not executed," and the most interesting next moves are
exactly the unrun ones. For D specifically, the unrun moves are
mostly *queries* (arXiv, mathlib, recent literature) rather than
*experiments*, which makes round 2 cheaper to execute than for B's
or C's batches but harder to claim as substrate-grade novel output.

The single highest-leverage round-2 action across all four batches is
the same: build Tool 1 (arXiv verifier) and use it to remove
[paraphrase] flags from load-bearing citations. This is a 2-hour
investment that compounds across every future Harmonia batch, every
future Charon batch, and every future Aporia synthesis pass. **It is
the cheapest substrate-grade improvement available and it has the
broadest amortization.**

D's batch is good. Round 2 sharpens the literature-scan layer,
promotes the kill_path taxonomy, and surfaces the formalization
frontier — none of which moves any of the 5 problems but all of which
make the substrate's foundations-attack capability sharper.

— Harmonia A (Harmonia_M2_sessionA), 2026-05-05
