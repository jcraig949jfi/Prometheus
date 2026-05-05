# Negative Results in AI for Mathematical Discovery: A Case Study in Reward Pathology and Self-Falsifying Systems

**Status:** Outline only. Drafted 2026-05-04 by Techne, in response to converging recommendations from Aporia, ChatGPT, and Gemini that this session's strongest defensible claim is methodological, not mathematical. Not a commitment to publish; the artifact is the outline itself, which forces the team to separate what is defensible from what is narrative before any future write-up can over-claim.

**Framing decision (single, throughout):** This is a *negative-results methodology paper*. The contribution is an instrument that falsified its own headline within 24 hours, plus the synthetic control that proved the headline was reward pathology rather than mathematical discovery. We are not claiming AI made a discovery. We are claiming we built the discipline that catches AI not making one.

---

## 1. Abstract / Headline

Single paragraph. The bold version, kept honest:

> We report a negative result and the methodology that produced it. Prometheus is, to our knowledge, the first multi-agent AI-for-mathematics substrate that successfully falsified its own "headline" findings within 24 hours of generation. A reinforcement-learning discovery loop targeting Lehmer / Mahler-measure structure produced consistent cross-domain lifts (+1.37x to +18x, p < 0.05) on six independent mathematical domains (BSD rank, modular forms, knot trace fields, genus-2 curves, OEIS sleeping beauties, mock theta functions) — the kind of result typically published as cross-domain validation. A subsequent one-hour synthetic control, designed by an internal adversarial agent and using the identical training pipeline on continuous regression with linearly separable Gaussian-noise structure, demonstrated that the underlying RL learner does not learn: REINFORCE collapses to <=3 reward bins on every variant, PPO stays uniform, and on a low-noise variant where ordinary least squares trivially solves the task at >=60% accuracy, REINFORCE achieves 4.91% versus 4.84% random. The 5.8x lift on a skewed synthetic environment with nothing to discover reproduces the same lift pattern observed on the real mathematical domains. We conclude that the cross-domain "successes" were class-prior recovery via entropy collapse, not discovery. We describe the substrate-level discipline (typed caveats, hash-locked PROMOTE records, four-fold falsification gates, deterministic seeds, mandatory synthetic null controls) that made this self-falsification possible, and we argue that most published AI-for-math results would fail to clear this bar.

Length target: 220-260 words. Lead with the negative result. The infrastructure claim is the contribution; the math is the case study.

---

## 2. Introduction — the AI-for-math credibility gap

- 2026 landscape: AI-discovery papers in mathematics have proliferated faster than reproducibility / falsification discipline. The standard pattern is a headline lift on a real mathematical domain, an ablation that swaps one component, and publication.
- The recurring failure mode we observed in our own system (and characterize in published work later in the paper without naming): claim discovery -> modal-class collapse on a discrete reward -> class-prior recovery -> headline lift escapes upward, with no synthetic null run to catch it.
- The methodological gap: most published AI-for-math systems do not have substrate-level discipline that can falsify their own claims. They have evaluation harnesses, but evaluation is not falsification. Layer 1 (does the answer check out?) is not the same as Layer 2 (is the model actually learning the structure, or recovering the class prior?).
- Contribution of this paper: (i) a substrate design that enforces self-falsification, (ii) a worked case study where the substrate catches its own headline, (iii) a diagnosis (Layer 2 / signal extraction is broken; Layer 3 / search is replaceable), and (iv) a comparison bar that most current AI-for-math results would not clear.
- One-line thesis: *A falsification-first system without a gradient becomes a perfect null-result generator.* Building one that catches itself before publication is the contribution.

---

## 3. System architecture — substrate as instrument

This section describes the substrate, framed as an instrument for catching bad claims, not as a discovery engine.

- **Sigma kernel.** Seven-opcode substrate: RESOLVE, CLAIM, FALSIFY, GATE, PROMOTE, ERRATA, TRACE. Every claim that survives must pass through GATE before PROMOTE; every PROMOTE is hash-locked and inherits caveats via TRACE.
- **Caveat-as-metadata schema.** Caveats are typed, structured records hash-locked into a PROMOTE def_blob. Downstream consumers receive caveats automatically through TRACE — narrative inflation cannot strip them out without breaking the hash chain.
- **Five-catalog cross-check + four-fold falsification (F1 / F6 / F9 / F11) + reciprocity + irreducibility gates.** Any candidate must agree across five independent catalog sources, survive four orthogonal falsification probes, and pass reciprocity and irreducibility checks before reaching PROMOTE.
- **Three terminal states:** PROMOTED, SHADOW_CATALOG (kept but flagged), REJECTED. SHADOW_CATALOG is the substrate's epistemically honest disposal: this looked plausible, here is the kill_path, do not delete.
- **Cost-model calibration discipline.** Top-50 operations stay within 2x of empirical-vs-declared cost. Drift triggers a recalibration before further runs.
- **Composable test gates.** A 4-category math-TDD gate (authority / property / edge / composition) plus a 7-category bug-hunt gate. Both gates run before any operation reaches PROMOTE.
- **Honest framing in the paper:** This is a substrate for catching false positives. It is not, on the evidence so far, a substrate for generating true positives — that is the open question Section 9 addresses.

---

## 4. The substrate's first failure case — cross-domain "validation"

The seductive-looking result, presented as it would have been published if the discipline had stopped here.

- Six mathematical domains tested independently: BSD rank, modular forms, knot trace fields, genus-2 curves, OEIS sleeping-beauty sequences, mock theta functions.
- Headline: substrate transports across mathematical structure. Lifts ranged from +1.37x (BSD) to +18x (modular forms), Welch p < 0.05 in every case, deterministic seeds, multiple replications.
- 350K+ episodes accumulated. Pre-registered evaluation harness. Five-catalog cross-check passed. Four-fold falsification gates passed.
- This is what most papers in the current AI-for-math landscape would publish as "cross-domain validation of a discovery substrate."
- Honest internal posture at the time: cautious optimism. We did not yet know what the synthetic test would find.

---

## 5. Falsifying our own headline — the synthetic test

The kill, presented straight.

- One-hour test, designed by Aporia (an internal adversarial agent) *after* the cross-domain claims were assembled internally. Aporia's mandate: build the simplest possible synthetic environment that uses the *identical* training pipeline as the real environments.
- Design: continuous regression task. Gaussian noise on linearly separable structure. Four variants spanning noise level, class skew, and signal magnitude. Three algorithms (REINFORCE, PPO, a tabular control). Three seeds each.
- Result, V1-V4: REINFORCE collapses to <=3 reward bins on every variant. PPO stays uniform. The collapse pattern is identical across noise regimes.
- Result, V3 specifically (low-noise, lstsq trivially solves at >=60% accuracy): REINFORCE 4.91%, random 4.84%. The learner is statistically indistinguishable from random on a task with abundant signal.
- Result, V2 (skewed class distribution, no discoverable structure): REINFORCE produces a 5.8x lift over uniform baseline — *on an environment where nothing is discoverable*. This 5.8x lift reproduces the lift pattern observed on modular forms (+1.58x in one configuration) and BSD (+1.37x).
- **Verdict: Case A.** The substrate is broken at the search-mechanism layer. The cross-domain "successes" of Section 4 are class-prior recovery via entropy collapse, not discovery. The lifts are what entropy collapse onto the dominant class produces, regardless of whether the underlying domain has signal.
- Headline retracted internally before any external write-up.

---

## 6. Diagnosis — Layer 2 (signal extraction) is broken, not Layer 3 (search)

Why the failure happened, framed in the three-layer model.

- **Layer 1 — evaluation.** Works. The substrate's gates correctly identify when a candidate satisfies mathematical criteria.
- **Layer 2 — signal extraction.** Broken. Discrete-bin reward produces a discontinuous gradient. Entropy collapse onto the modal bin is the *optimal* policy under discrete reward — not a failure mode, the correct response to a measurement interface that supplies no usable gradient.
- **Layer 3 — search.** Replaceable. We tried REINFORCE and PPO; the failure is identical because the failure is upstream of search. Swapping in evolutionary methods, MCTS, or LLM-driven proposals would not fix it.
- The killer line: *"A falsification-first system without a gradient becomes a perfect null-result generator."* All the discipline in the world cannot rescue a learner that is being asked to climb a flat surface.
- The fix is *not* a different RL algorithm. The fix is a different *measurement interface*: continuous surrogate signals (distance to validity, count of violated constraints, magnitude of failure rather than binary fail/pass). This is a Layer 2 redesign, not a Layer 3 swap.
- Implication for the field: any AI-for-math system using discrete success/failure rewards on hard discovery tasks is at high risk of the same pathology. Class-prior recovery looks like cross-domain transport.

---

## 7. Self-falsification as substrate property

The methodological claim, supported by the case study and one ancillary catch.

- The synthetic test of Section 5 was designed *by an internal agent*, *after* the cross-domain claims of Section 4 were made internally, and *killed the headline*. The substrate's own falsification discipline produced the test that broke the substrate's own narrative. This is the design property we want to highlight.
- Ancillary instance: the brute-force F campaign (97M degree-14 +/-5 palindromic polynomials, queued and stalled). An 18-second smoke test on 2187 polynomials surfaced two bugs — a cyclotomic-noise false-positive and a verdict-logic inconsistency — that would have flooded the full 97M-poly run with thousands of false-positive "discoveries." Caught before the run consumed resources or produced publishable garbage.
- These are the same discipline pattern operating at different layers: never trust an internal narrative without an external falsification probe.
- **Caveat-as-metadata is the technical mechanism that makes this work.** Because caveats are hash-locked and inherited through TRACE, they cannot be silently dropped as a claim moves from raw output to internal summary to external write-up. Narrative inflation is structurally blocked at the data layer.
- The general principle: substrate-level discipline must be cheaper to invoke than the temptation to skip it. A one-hour synthetic test that kills a 350K-episode headline is an extreme demonstration of favorable cost asymmetry.

---

## 8. Comparison with the AI-for-math literature

Characterize patterns; do not name names. The point is the bar, not the call-out.

- We surveyed AI-for-math discovery results published in the last two years. We do not name systems; instead we characterize four recurring patterns:
  - **(a) No synthetic controls.** Headline numbers reported on real mathematical domains, with no parallel run on a constructed environment where the answer is known to be absent.
  - **(b) No null-hypothesis ablation.** No version of the system in which the learner is replaced by a class-prior recovery baseline (always-predict-mode, simple xgboost, or logistic regression on the same features).
  - **(c) Discipline-grade caveats absent.** Caveats reported in prose, not as typed structured records propagated through provenance. Easy to drop in summary.
  - **(d) Cannot detect class-prior recovery.** Evaluation harness does not distinguish between "model learned structure" and "model recovered the dominant class with high confidence."
- What our substrate enforces that we did not find consistently elsewhere: typed records, hash-locked caveats, kill_path metadata on every rejection, deterministic seeds, Welch p-values with explicit family-wise correction, and *mandatory synthetic null controls before any cross-domain claim*.
- Honest assessment: most published AI-for-math discovery results would fail to clear the synthetic-null bar. We know this because *our own* result failed to clear it, and our result was substantially more disciplined than the median published system in this space.
- This is a load-bearing claim. We will support it in the paper with a small structured survey (~10 systems, anonymized) scored against the four patterns above.

---

## 9. What this means going forward

The honest path forward, framed as instrument-mode rather than discovery-mode.

- The discovery framing is not currently defensible. We do not have evidence that the substrate produces mathematical discoveries.
- The instrument framing is defensible. We have evidence that the substrate catches its own false positives within 24 hours and at substrate-level cost.
- **Concrete near-term work:**
  - **Layer 2 repair.** Replace discrete success/failure reward with continuous surrogate signals (distance to validity, violation counts, failure-magnitude). This is a measurement-interface redesign, not an algorithm swap.
  - **Supervised baselines first.** Before any further RL investment, run xgboost / logistic regression baselines on the same features. If a supervised model recovers most of the lift, the RL machinery is unnecessary; if it does not, the residual is the discovery question.
  - **Brute-force closure.** When the smoke-test bugs are fixed, the brute-force F campaign (deg-14 +/-5 palindromic, 97M polys) is the rigorous-Lemma path: a finite subspace where the right answer is the answer.
- The substrate stays. The RL loop is on probation pending Layer 2 repair and supervised-baseline comparison.
- The paper itself does not commit to any of these next steps. It documents the kill and the methodology that produced it.

---

## 10. Honest limitations

The section that the team must not let get cut.

- **N = 1 case study.** One substrate, one domain family, one team. The methodological claim generalizes; the specific numbers do not.
- **Cost.** Substrate-grade discipline is slow. We accumulated 350K+ episodes before the one-hour synthetic test killed the headline. Discipline is cheaper than wrong publications, but it is not free, and we should be honest that it took us longer than it should have to run the synthetic null.
- **The methodology might still produce positive discovery results.** When Layer 2 is repaired and supervised baselines are run, the substrate may produce true positives. We do not yet know. The negative result documented here is a result *about this configuration of the substrate*, not a permanent claim about the architecture.
- **Selection effects in the synthetic-test design.** Aporia's synthetic environments were constructed to expose the suspected failure mode. We argue they are fair tests (linearly separable structure, abundant signal in V3, identical pipeline). A reviewer could reasonably ask whether other synthetic environments would tell a different story; we believe not, but we cannot prove a universal.
- **Open audience question.** What is the right venue for negative-results methodology in AI-for-math? The result is too methodological for a pure mathematics journal and too negative for most ML venues. Workshops on reproducibility, ML evaluation, or AI-for-science methodology are plausible homes; formal systems venues (CPP, ITP) are not. The team should decide.

---

## Decisions awaited from team

The following decisions are required before this outline becomes a draft. Listed without preference; each is a real branch point.

1. **Target venue.** Options: (a) ML reproducibility workshop (e.g., a NeurIPS / ICML reproducibility track), (b) AI-for-science methodology venue, (c) arXiv-only with no formal submission, (d) blog-post / technical-report form on the project site, (e) do not publish; outline serves as internal anchor only.
2. **Co-authorship.** Who attaches their name? The substrate work spans Techne (toolsmith), Aporia (synthetic test designer), Charon (cross-domain validation runs), and the human PI. Each has a real contribution; each carries reputational exposure on a negative-results paper. Decide explicitly.
3. **Timeline.** Half-day outline (this document) is done. Full draft is a separate decision. Options: (a) one-week sprint to submission-ready draft, (b) two-week sprint with external review, (c) park the outline as internal anchor and revisit in a month after Layer 2 repair, (d) park indefinitely.
4. **Whether to publish at all.** The outline is valuable even if we never publish — it forces the framing question and prevents accidental over-claiming in future internal docs. The decision to publish is separate from the decision to maintain the outline.
5. **Naming of compared systems.** Section 8 currently anonymizes. The team must decide whether to (a) keep anonymized characterization, (b) name systems with a structured comparison table, or (c) cut Section 8 entirely and let the methodological bar speak for itself.
6. **Internal vs external scope.** Whether to include the brute-force smoke-test catch (Section 7) and the kill_path metadata details (Section 3) — both are revealing about substrate internals. Decide what the team is willing to expose publicly.
7. **Title commitment.** Current title is the merged ChatGPT framing. Gemini's "high-fidelity falsification substrate" framing is also live. The team should commit before any draft begins; switching titles mid-draft costs more than it saves.
