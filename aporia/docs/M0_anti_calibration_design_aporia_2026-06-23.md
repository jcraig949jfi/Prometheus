# M0 Anti-Calibration Design — Aporia's Perspective (a second, differentiated read)

**Author:** Aporia (Claude Opus 4.8, Anthropic) · **Date:** 2026-06-23
**Status:** PROPOSAL — pre-registered design. NOT a ratification of Harmonia A's M0.
**SUPERSEDING FRAME (added 2026-06-23, post-Techne-dissent):** James agrees with
`pivot/REASSESSMENT_2026-06-23_techne_dissent.md`. This M0 design is now **subordinate
to M1-as-metabolization** — see §10 (Reconciliation). Read §10 first; it demotes M0
from "the experiment that decides the bet" to "a navigability diagnostic inside the
metabolization loop."
**Relationship to prior docs:** This is a *peer* perspective to
`pivot/REASSESSMENT_2026-06-22_v2_enforcement.md` §2 (M0) and `..._v3_the_reframing.md`,
deliberately built from Aporia's role-doctrine and Aporia's *own* prior reassessment
(`aporia/docs/STATUS_2026-06-15_reset.md`, `aporia/docs/program_audit_2026-06-10.md`),
which the 06-22 audit cites as authoritative but does not actually carry through into M0.

> **Read this as the falsification-of-the-audit that `feedback_agent_differentiation`
> asks for: differentiate at layer-of-operation, cross-compare as falsification.** James
> has flagged Harmonia A's audit as non-canonical. This document does not assume it is.

---

## 0. The conflict-of-interest disclosure (read first)

Harmonia A is **Claude Opus 4.8, Anthropic. So is the author of this document.** By our
own `feedback_llm_convergence_is_gravity_amplifier`, agreement between us is *gravity*,
not corroboration. v2 "mitigated" single-family risk with a ChatGPT cross-check that
**endorsed** v1's core — but by the same doctrine, two frontier LLMs converging on
"the battery can't see novelty" is exactly what you would expect if that framing sits in
the shared training corpus. **It is a warning, not a validation.** Consequently this
design treats the *experiment itself* as a place gravity can hide, and §5 makes Set C
generation LLM-free on purpose.

---

## 1. The divergence, in one paragraph

Harmonia A's M0 (v2 §2) feeds the battery a curated benchmark of **true/false math
*claims*** — re-encodings (Set A), adjacent-domain truths (Set B), synthetic truths
(Set C) — and asks whether the battery accepts the true ones outside its calibration
manifold. **That is an experiment in CLAIM space.** Aporia's own deepest committed
finding (STATUS_2026-06-15 §2) is that *claim space is exhaust*: every claim-level signal
hunt — A3 lattice mining, cold-start metadata routing, non-conservativity on math
objects, the 90-batch zero-promotion streak — returned NULL, while *every* signal that
ever emerged was **capability-attached failure** (Hephaestus near-miss → +11/+32pp;
co-solve → +0.075 AUC; compute-traces → +0.16 transfer). The restated doctrine:
**the failure of a reasoner attempting something is residue; the failure of a random
claim is exhaust.** Harmonia A's M0 measures the battery on exhaust. **The M0 that
decides the 20-year bet must be run in capability space, on capability-attached novel
results — not on a list of free-floating novel-true claims.**

This is the load-bearing divergence. The other four (§3) follow from it or guard it.

---

## 2. Where Aporia agrees with Harmonia A (so the disagreement is legible)

- **The question is real and gating.** Whether the selector can recognize structure
  outside its calibration set is the keystone, and v3 is right that the D-thesis
  (progress meter) *raises* its stakes rather than escaping them. No dispute.
- **My own last-turn operational fixes still hold and are folded in below:** matched
  true/false twins (against `PATTERN_BASE_RATE_NEGLECT`), three-way accept/reject/**unknown**,
  ablation for structural-vs-surface verdicts, pre-registered measurement-level thresholds
  (`feedback_take_a_stand`, `pattern_prediction_level_mismatch`), stratified sampling
  (`feedback_sampling_strategy_is_analysis`), seeds/volume (`feedback_replicate_seeds`).
- **Set C (synthetic, externally checkable) is the clean arm.** Agreed — and promoted to
  primary, with a stronger generation constraint (§5).

The disagreement is not about rigor. It is about **which space M0 is run in**, and about
**what counts as a pass.**

---

## 3. The five divergences

### D1 — M0 must be run in CAPABILITY space, not CLAIM space (the load-bearing one)
Per §1. A novel-true *claim* handed to the battery cold is exhaust by Aporia's own
finding; the battery has never produced signal on it and there is no prior reason M0
will. The discovery the program actually wants is a **reasoner-attached result**: an
agent attempted a problem, produced a candidate that is true-but-novel, and the kill
geometry came attached. **M0-capability:** take held-out solved problems whose solution
is *not* in any calibration corpus, run them through the reasoner→battery pipeline, and
ask whether the battery's verdict + kill-vector tracks the externally-known truth. This
is testable today against the **already-frozen** transfer eval battery (STATUS-06-15 §4C:
entity-disjoint + domain-transfer + computation-required slices). **Corollary that
matters:** in capability space, "can it recognize out-of-manifold truth" *substantially
overlaps the R3 "THE WALL" gate already pre-registered* (cross-op transfer > 0, p<.05).
Harmonia A may have re-derived, in claim space, a question Aporia already operationalized
in capability space. M0 should be designed to expose that overlap, not hide it.

### D2 — The void is INTERPOLATIVE, not extrapolative (re-targets the manifold metric)
Harmonia A's framing — and my own last-turn "distance from manifold" proposal — implies
novelty = *far from* the calibration set. **Aporia's role-doctrine says otherwise.** The
canonical voids (Mendeleev's gallium, Dirac's antimatter, the Higgs) were holes
**bracketed by known structure, inside the hull** — not distant outliers. The dangerous
failure mode of a calibration-recognizer is therefore *not* "rejects the far-away truth";
it is **"accepts the interpolative void as already-known"** because it is surrounded by
things it recognizes. M0 must split its synthetic set into **interpolative voids** (gaps
enclosed by calibration truths) and **extrapolative outliers** (genuinely beyond), and
score them separately. Aporia's pre-registered stand: the battery will look *better* on
extrapolative outliers (it can at least abstain) and *worse — silently — on interpolative
voids* (it will confidently mis-locate them as known). If so, "distance from manifold" is
the wrong instrument and **void-enclosure** is the right one.

### D3 — The battery SHOULD be conservative; acceptance is Goodhart bait (flips the pass condition)
v2's pass condition is "certifies enough out-of-manifold truths." **Aporia objects on
doctrine.** A falsification battery is an immune system; asking it to *accept* novel
truth is asking the immune system to bless a mutation — which it is built not to do, and
which is the exact `PROMOTE`-trusts-the-caller Goodhart hole the whole audit indicts.
Reframe the pass condition to the `feedback_residue_must_be_navigable_not_logged`
eligibility gate: **when the battery fails to accept a novel truth, does it ABSTAIN and
LOCALIZE THE BOUNDARY (residue — names the missing feature) or REJECT on a surface
feature (exhaust)?** A battery that says "unknown — feature X is absent" on a novel truth
is *succeeding as a void detector*: the abstention names the void. Only confident
false-kill-on-surface-feature demotes the thesis. **This reframe is more aligned with v3
than Harmonia A's own inherited M0:** under the D-thesis the battery's job is to point
direction (Q3 "what next"), not to certify discovery — and abstain-and-localize is
exactly that directional signal.

### D4 — Operators over objects: M0's unit is the KILL-VECTOR, not the verdict (verbs over nouns)
`feedback_verbs_over_nouns` + `feedback_failure_signal_vector_field`. Harmonia A's M0
scores verdicts (accept/reject). Aporia scores the **operator that fired**: which
falsifier, on which feature, pointing which direction. A *correct* reject for a *surface*
reason is a failure; an *abstention* whose kill-vector localizes the missing structure is
a success (D3). So M0's per-claim record centers `which_falsifier_killed_it` +
`feature_engaged` + `is_boundary_localizing`, and the headline metric is **kill-vector
validity off-manifold**, not discrimination accuracy. Discrimination accuracy (my §2
matched-twin gap) is retained as a *control*, not the verdict.

### D5 — The experiment design is itself gravity-exposed; Set C must be LLM-free (guards §0)
Because author and auditor share a family (§0), an LLM proposing "novel-looking math
claims" for Set C will draw Set C from the **same gravity well** the battery was
calibrated in — manufacturing a false pass or a false fail. Set C must be generated by a
**mechanical enumerator over a decidable/semi-decidable theory with an external oracle,
zero LLM in the generation loop** (§5). This is the only arm with neither calibration
leakage *nor* shared-prior contamination, which is why it is primary.

---

## 4. The redesigned M0 (two tracks, capability-space primary)

**Track 1 — M0-capability (PRIMARY, decides the bet).**
Held-out solved problems with externally-known truth, *absent from all calibration
corpora*, run reasoner→battery. Per item record: external truth; battery verdict
(accept/reject/**unknown**); kill-vector (`falsifier`, `feature_engaged`,
`is_boundary_localizing`); whether verdict survives surface-feature ablation (D4).
Stratify by interpolative-void vs extrapolative-outlier (D2). **Overlap check:** report
how much of M0-capability is the existing R3 WALL gate by construction.

**Track 2 — M0-claim (CONTROL, replicates Harmonia A's framing).**
Harmonia A's claim-space M0, run *as the contrast arm*. If the battery shows the same
verdict behavior in claim space as in capability space, Aporia's D1 divergence is
falsified and Harmonia A's framing is vindicated — **good, that's the adjudication M0
exists to make (§8).** If claim space is NULL/exhaust while capability space carries
signal, Aporia's doctrine holds and the audit's M0 was testing the wrong space.

Both tracks use matched true/false twins (same surface/domain/enclosure, opposite truth)
so the null perturbs *truth-value only* — the axis recognition varies on
(`feedback_null_must_perturb_the_statistics_axis`); a permissive battery and a
discriminating one no longer score alike.

---

## 5. Set C generator spec (LLM-free, the clean core)

Goal: matched true/false pairs of mechanically-checkable claims, generated with no LLM,
stratified by enclosure (interpolative vs extrapolative) relative to the calibration set.

- **Source theory:** a decidable or externally-oracled formal system already wired in the
  repo — candidates: (a) Presburger/linear-arithmetic statements via z3 (Icarus already
  ships a z3 executing lens); (b) finite-field / modular-arithmetic identities checkable
  by `prometheus_math` verified code; (c) property-test-generated computation claims
  (STATUS-06-15 §4B: "property-based tests give unlimited fresh instances; gold computed
  by verified code"). All three give ground truth with **no LLM in the loop.**
- **Truth/false twins:** for each true statement, generate a minimally-perturbed false
  twin (flip a coefficient, weaken a bound by 1, swap a quantifier) that is *surface- and
  domain-matched* and verified false by the same oracle.
- **Enclosure stratification (D2):** embed calibration claims + candidates in the
  battery's own feature space; label a candidate **interpolative** if it lies inside the
  convex hull / k-NN neighborhood of calibration truths but is unoccupied, **extrapolative**
  if outside. Draw balanced counts per stratum (stratified, not alphabetical).
- **Volume:** enough matched pairs per (stratum × truth-value) cell for a CI on the
  type-II rate, not 5–10 anecdotes. Cheap because mechanical.
- **Leakage audit on A/B:** Sets A (re-encodings) and B (adjacent domains) are retained as
  *supplements only*, each gated by a check that they are genuinely far in feature space
  (A) and genuinely absent from the calibration corpus (B). Un-verified, they measure
  disguised in-manifold recall — discard.

---

## 6. Pre-registered pass / fail (measurement-level, set BEFORE running)

Stated now, per `pattern_prediction_level_mismatch` (predictions at the measurement
level — verdict gap, sign test — never at an estimator coefficient):

- **Aporia thesis (capability-space, D1) ALIVE** iff M0-capability shows a matched-twin
  discrimination gap > 0 *and* boundary-localizing abstention rate exceeds
  surface-reject rate on the interpolative stratum, both beating the truth-shuffle null.
- **Harmonia A framing (claim-space) VINDICATED** iff M0-claim shows the same gap as
  M0-capability (D1 falsified).
- **Discovery thesis DEMOTED to A/C** iff *both* tracks show the matched-twin gap
  collapsing to base-rate off-manifold AND interpolative voids are confidently
  mis-accepted as known (D2 confirmed in its dangerous direction).
- **Battery is a recognizer-not-detector (the deep crux) CONFIRMED** iff verdicts flip
  when surface features are ablated but content retained (D4) — independent of truth.

Pre-registering both the Aporia-alive and the Harmonia-A-vindicated conditions is the
point: M0 is built to be able to falsify *Aporia's own* divergence, not just the audit's.

---

## 7. The adjudication M0 performs (why two tracks, not one)

This design does not assert Aporia is right and Harmonia A is wrong. It builds the one
experiment that can **decide between them**, with both outcomes pre-committed:

- claim-space ≈ capability-space → Harmonia A's M0 was sufficient; Aporia's D1 over-thought it.
- claim-space NULL, capability-space signal → the audit's M0 tested exhaust; capability-space M0 (≈ the existing R3 gate) is the real keystone, and the program should not have spent days building a claim-space benchmark.

Either way the program learns which space its progress meter lives in — which is exactly
the kind of typed, falsifiable verdict the substrate exists to produce.

---

## 8. What would make THIS document wrong (self-falsification, per Standing Order 2)

- If M0-claim and M0-capability agree, D1 is dead and I over-differentiated (the
  `feedback_agent_differentiation` risk run in reverse — manufacturing a distinction).
- If interpolative and extrapolative strata behave identically, D2's enclosure instrument
  adds nothing and "distance from manifold" was fine.
- If a clean, LLM-free Set C proves impractical to generate at volume, D5's purity demand
  is aspirational and the experiment falls back to leakage-graded A/B (weaker, but real).
- The capability-space framing inherits the LoRA-capacity confound (STATUS-06-15 §5D:
  "do not interpret capacity bounds as data failures") — M0-capability must control for
  model capacity or it will mistake a 3B ceiling for a battery blindness.

---

## 9. Consumer declaration (Aporia Stand A2 — named before build)

- **Consumer:** the CC-0 / v3 vision arbitration. M0's verdict decides whether the
  D-thesis progress meter is sighted (capability-space) or blind, and whether the program
  falls back to success-state A.
- **Expected decision-delta:** a *space* verdict (claim vs capability) + a *pass/fail* on
  the discovery thesis, each pre-registered in §6. If M0 cannot change the arbitration,
  it should not be built — it would be another /dev/null artifact.
- **Owner:** Aporia (set design + enclosure instrument + generator); reasoner→battery
  pipeline and the frozen eval slices are Ergon/Learner + Icarus territory.

---

---

## 10. Reconciliation with Techne's dissent (added 2026-06-23, James concurs)

`pivot/REASSESSMENT_2026-06-23_techne_dissent.md` rejects v3's organism/instrument
dichotomy: the metabolization loop *is* both at once, and the decisive experiment is not
"can the selector recognize novelty" but **"can a model metabolize the kill-geometry the
substrate produces and change its behavior because of it?"** — framed as kill-geometry
navigability over Charon's `signature_index` proto-tensor (3,311 signature-classes over
413M records). James concurs. This reconciliation stands; where this doc conflicts with
it, the dissent wins.

**What survives, sharpened — not contradicted.** Techne and this doc converge, from
different roles, on the same target via the same gate:

- Techne §3.4 calls navigability — *changes routing / localizes a boundary / falsifies a
  prior signature / adds tensor rank* — "a sharper M0 than recognize-novelty." That is
  verbatim the `feedback_residue_must_be_navigable_not_logged` 4-criteria gate this doc's
  **D3/D4** used to reframe M0's pass condition (kill-vector validity + abstain-and-localize,
  not verdict accuracy).
- Techne §3.3/§3.4 move the decider to **capability-space metabolization**; this doc's
  **D1** moved M0 to capability space on Aporia's own 06-15 doctrine. Same move.
- The convergence is **doctrine-grounded, not single-family gravity** (the §0 risk):
  both readings derive from `feedback_tensor_first`, `feedback_failure_metabolization_doctrine`,
  the residue gate, and STATUS-06-15 — all of which predate the Harmonia chain. James's
  agreement is the non-LLM cross-check the gravity warning requires.

**What changes here.** M0 is demoted and re-scoped:

1. **M0 is not the decider; M1-metabolization is.** Drop the framing of M0-as-the-bet.
   Gate-hardening / recognition-M0 is cheap background hygiene (dissent §5.2). The single
   decisive experiment is the dissent's §5.3: point the forge at the Learner's failure
   clusters, show consuming the kill-geometry changes behavior, and the change survives an
   ablation — an ablation-positive M1 card.
2. **M0-capability (Track 1) folds into M1 as its navigability probe.** It is no longer a
   standalone benchmark; it is the *measurement* that the metabolization loop is moving
   through kill-geometry toward unkilled regions. "Closer than yesterday" is a byproduct,
   not a separate apparatus (dissent §4).
3. **M0-claim (Track 2) remains, but only as the cheap control** that confirms claim-space
   is exhaust — one run, then stop. Not days of benchmark-building.

**Aporia's specific addition to the metabolization frame (the void-detector's job).**
Techne frames navigability as "move toward *unkilled* regions." Aporia sharpens the
*target*: the discovery-relevant cells of the `signature_index` proto-tensor are not the
distant unkilled frontier but the **unoccupied cells enclosed by killed-and-confirmed
structure** — the interpolative voids of **D2**, Mendeleev gaps in signature space.
`feedback_failure_signal_vector_field`: *voids in the lattice ARE the mathematics.* So the
navigability metric M1 should report is not only "did behavior move toward unkilled space"
but **"did it move toward an enclosed-but-empty signature cell, and was that cell a real
target"** — the proto-tensor occupancy distribution (Techne's "invariant_equality = 33%")
read as a void map. That is the one thing Aporia adds that neither the audit nor the
dissent states: *navigability is necessary; navigability-toward-enclosed-voids is the
discovery signal.* It is falsifiable — if enclosed-empty cells are unreachable or not real
targets, the void-map adds nothing over plain unkilled-frontier navigation, and Aporia's
addition dies.

**Net standing.** Keep v3's meta-falsification guard (genuinely good). Refuse v3's
demotion of the organism. Run M1-metabolization as the decider. M0 (this doc) is its
navigability instrument, with void-enclosure as Aporia's contribution to what
"navigable" should mean.

---

*This is the second perspective James asked for. Its single claim against the audit:
Harmonia A's M0 tests CLAIM space, which Aporia's own 06-15 doctrine already found to be
exhaust; the M0 that decides the bet runs in CAPABILITY space and substantially overlaps
the R3 WALL gate already pre-registered. Everything else (interpolative voids, conservative
battery, kill-vector unit, LLM-free Set C) follows from Aporia's role and guards against
the fact that author and auditor share a model family. The design is built to falsify
itself, not just the audit. — Aporia, 2026-06-23.*
