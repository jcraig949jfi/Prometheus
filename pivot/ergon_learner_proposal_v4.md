# Ergon Learner — Proposal v4 (for external review)

### A closed-loop scientific learning system for empirical mathematical patterns. Hybrid neural-plus-evolutionary mutation with shared-prior-at-corpus-level honestly named, residual-primitive-integrated five-counts diagnostic, content-aware MAP-Elites descriptor, power-calculated pilot budgets, and a Techne meta-loop that makes "calibrated negative result" falsifiable.

**Date:** 2026-05-03 (evening — third revision of the day)
**Status:** Formalized for external review. Pasteable to frontier-model context windows as a standalone artifact. **Recommended as the genuine design-freeze version** — v3's freeze recommendation was premature; round-3 review caught internal contradictions and missed integrations that v3 had hidden behind language. v4 is corrective, not additive. After v4, MVP build begins.
**Supersedes:** [`pivot/ergon_learner_proposal_v3.md`](ergon_learner_proposal_v3.md) (commit 82790816, 2026-05-03 afternoon)
**Origin of v4 revisions:** Round 3 external review of v3 — the deepest of three rounds, identifying internal contradictions and missed substrate integrations that prior rounds missed. Verbatim capture: [`feedback_ergon_review_round3_2026-05-03.md`](feedback_ergon_review_round3_2026-05-03.md). Triage: [`meta_analysis_ergon_round3_2026-05-03.md`](meta_analysis_ergon_round3_2026-05-03.md).

---

## What v4 changes (delta from v3)

V3 was reviewed by a third external session that landed eight critiques, two of which were *internal contradictions or missed integrations* — qualitatively different from the round-1 / round-2 critiques which named missing mitigations.

V4's eight revisions:

1. **§5.1 Llemma rationale corrected.** v3 marketed Llemma as "closest to Silver's training distribution" — directly contradicting §3's asymmetry argument. v4 names the prior-overlap honestly: differentiation comes from action-space + value head + LoRA delta, not base-model prior. Llemma is retained as a starting point with strong math-reasoning prior; v0.5 ablation against Qwen-7B and Llama-7B added.

2. **Four-counts diagnostic → five-counts diagnostic.** v3's diagnostic ignored the residual primitive that shipped at commit `4872bb4a` on the same day. v4 adds a fifth count — `signal_class_residual_kill` — that gives the diagnostic statistical power even at low PROMOTE rates because residual events are denser than promotions by construction.

3. **Power calculation added (§7.5).** v3 projected pilots at 10K episodes per arm without estimating effect sizes. If PROMOTE rates are ≤10⁻⁴, even 10K episodes is informationally null. v4 names the rate floor and proposes the residual-count fifth column as the partial mitigation.

4. **Minimum proposal share for non-prior-shaped operators (§3.5.4).** v3's spawning policy under selection pressure squeezes out `uniform` exactly when it's most needed for exploration. v4 commits to `uniform` ≥5%, `anti_prior` ≥5%, `structured_null` ≥5%; total non-prior-shaped ≥15% of all proposals at all times.

5. **MAP-Elites descriptor — content-aware axis (§6.2).** v3's revised axes were partly content-aware but mostly construction-aware. v4 swaps DAG depth for output canonicalizer subclass (the discrete content classification of *what the output is mathematically*).

6. **Silver-ingestion operationalized (§13).** v3's "Silver's outputs become CLAIMs" was rhetorical. v4 specifies three substrate-ingestible fragments: empirical-pattern conjectures invoked in proofs (BSD-conditional, GRH-conditional, etc.), generalizations the proof makes from specific cases, near-miss CLAIMs from tactic-tree exploration.

7. **Mathlib added as comparison class (§3.7).** v3 framed against Silver alone. Mathlib is the closest existing analog to the Σ-kernel on the substrate side. The Σ-kernel's actual niche: the empirical-pattern manifold neither Mathlib nor Silver covers. Position survives any outcome of Silver's company.

8. **Deeper bear case + Techne meta-loop (§11.5).** v3's bear case was "neural ≈ evolutionary on PROMOTE rate." Round-3 reviewer's deeper case: PROMOTE rate may be zero across all arms because the battery is miscalibrated for novel structure. v4 operationalizes a meta-loop where Techne forges sharper checkers for high-residual kills and the substrate audits whether the original battery should have caught what the sharper checker promotes. This makes "calibrated negative result" falsifiable.

V4 also re-issues the design-freeze recommendation, but on substantively different grounds than v3's: v3 freeze was based on "fundamentals haven't changed" — round 3 falsified that. v4 freeze is based on "round 3 was the high-water mark for design-layer critique; further rounds will be additive surface, not corrective; MVP empirical signal is the next high-value increment."

---

## 1. The market context — David Silver's billion-dollar play

(Unchanged from v3 §1.)

On 2026-04-29, David Silver — formerly of Google DeepMind, lead architect of AlphaGo and AlphaZero — was reported raising **$1 billion** for *Ineffable Intelligence* (Sequoia-led, ~$4B pre-money, Nvidia/Google/Microsoft in talks; no product, no revenue, no public roadmap). His thesis: LLMs trained on human text cannot discover genuinely new knowledge; superintelligence requires AlphaGo-style self-play from first principles.

Two structural observations, load-bearing for this proposal:

**(1) "Discard human knowledge" is overclaim.** AlphaZero kept Go's rules; the *play* was discovered. For mathematics, the *game itself* is what's being invented. Self-play without a clean truth-condition produces reward-signal capture, not discovery. Silver's likely concrete artifact: a Lean / Mathlib / theorem-prover-acceptance learner.

**(2) Silver builds the proposer; nobody is building the substrate** *for empirical mathematical patterns.* (Lean Mathlib already exists as a substrate for the formal-proof manifold — see §3.7.) For the empirical-pattern manifold (BSD residuals, Mahler-measure scans, RMT statistics, structural anomalies in OEIS data) there is no content-addressed, append-only, mechanically-falsifiable substrate. Prometheus has been building exactly that for two years.

This proposal is the small learner Prometheus needs to push its substrate forward — calibrated against Silver's likely play, designed to complement it.

## 2. What Prometheus is, in 200 words

(Unchanged from v3 §2.)

Prometheus is a 20-year personal-bootstrap research program building a falsification substrate for mathematics. **Σ-kernel:** append-only, content-addressed, with seven typed primitives mechanically enforcing epistemic discipline; recently extended with BIND/EVAL and a Residual primitive. **Falsification battery:** F1+F6+F9+F11 (plus expansions) calibrated against ~180 known truths. **Multi-agent agora:** heterogeneous LLM agents proposing claims and running kill-tests on each other. Thesis (per [`bottled_serendipity.md`](../harmonia/memory/architecture/bottled_serendipity.md)): LLMs as mutation operators produce off-modal samples that occasionally land outside training distribution and inside truth; without filtration that fraction is invisible; with the kernel as filter it is the product. The substrate compounds because durable typed survivors accelerate future filtration.

## 3. The Ergon learner — corrected asymmetry argument

V3's asymmetry table claimed action-space asymmetry yielded different priors. Round-3 review correctly identified this as overclaim. **The honest framing:**

The prior is shared at the corpus level. Llemma-7B (Proof-Pile-2) and any Silver-class base model fine-tuned on Mathlib + ArXiv inherit the same statistical biases about what mathematical structures are "interesting." Action-space asymmetry alone does not protect against this.

**Differentiation in v4 comes from three sources, ordered by expected magnitude:**

1. **Value head asymmetry.** Silver's reward is Lean-kernel CLOSED on a goal. Ergon's reward is agreement-weighted (substrate-pass + cross-model + held-out-battery + signal-class-residual). These reward landscapes select for different mathematical content even when the proposer's prior is shared.

2. **Action-space asymmetry.** Silver's actions are Lean tactics + lemma applications. Ergon's actions are typed compositions over the math arsenal. The composition spaces overlap only where formalizable; for empirical-pattern claims the action spaces are disjoint.

3. **LoRA-delta divergence.** When the same base model is fine-tuned against substrate verdicts (Ergon) vs. theorem-prover verdicts (Silver), the LoRA attractors diverge. Empirical magnitude of this divergence is unverified at v4 design time; v0.5 ablation will measure it.

**The corollary v3 missed:** if differentiation comes from action-space + value head + LoRA delta rather than from the base prior, then *Llemma is not a load-bearing choice.* A general-purpose 7B (Qwen-7B, Llama-7B) might produce more divergent fine-tuning attractors precisely because its prior is less fixed. v4 retains Llemma as the lead candidate but adds Qwen-7B and Llama-7B as v0.5 ablation candidates to measure which base model maximizes LoRA-delta divergence under substrate-verdict fine-tuning.

| Axis | Silver's likely learner | Ergon learner (v4) |
|---|---|---|
| Action space | Lean tactics + lemma applications | Typed compositions over the math arsenal |
| Reward | Lean-kernel CLOSED (single evaluator) | Agreement-weighted (multi-evaluator + signal-class-residual) |
| Policy | Transformer over proof states | Hybrid: LoRA-fine-tuned 7B + MAP-Elites archive |
| Pretraining | Mathlib + IMO + Lean stdlib | **Llemma-7B baseline; Qwen-7B and Llama-7B as v0.5 ablation candidates** (corrected from v3) |
| Operator classes | Single (policy network) | Seven lineage-tagged + minimum-share enforcement on non-prior classes |
| Discovery surface | Theorems with formal proofs | Empirical patterns, structural anomalies, conjectural-but-falsifiable claims |
| Compute economics | $1B / 18 months | ~$300–800/month / indefinite |

## 3.5 Defending against shared-prior contamination

(Unchanged from v3 §3.5: anti-prior operator class, coverage-pressure cell selection, periodic prior detox.)

### 3.5.4 Minimum proposal-share enforcement (NEW in v4)

Per round-3 critique #4: under selection pressure for cell-fill rate, `uniform` (and the other non-prior-shaped operators) gets squeezed out. v4 commits to operator-class minimums enforced at the scheduler level:

- `uniform` ≥ 5% of all proposals
- `anti_prior` ≥ 5% of all proposals
- `structured_null` ≥ 5% of all proposals
- Total non-prior-shaped operators ≥ 15% of all proposals at all times

This is a coordination constraint at the operator-class scheduler, not at the cell-selection level. Even when cell-fill-rate metrics favor LLM-derived operators, the scheduler reserves 15% of episodes for non-prior-shaped exploration.

## 3.6 Null-world baselines

(Unchanged from v3 §3.6: three null-world variants — uniform, structured_null, cross_domain_perturbation — running as first-class operator classes with statistical comparison via Welch t-test + Holm correction.)

## 3.7 Comparison class — Mathlib, AlphaProof, academic projects (NEW in v4)

Per round-3 review, the substrate's natural comparison class is broader than Silver alone:

- **Lean Mathlib.** A content-addressed, append-only, mechanically-verified substrate of mathematical truth. Structurally the closest existing analog to the Σ-kernel — but with `kill_test = Lean kernel accepts`. Mathlib's coverage: theorems with formal proofs. Mathlib's blind spot: empirical mathematical patterns that aren't yet stated as Lean theorems.
- **AlphaProof / DeepMind formal-math team.** Builds learners that operate inside Mathlib; competitor on the *learner* side, but downstream of Mathlib's substrate.
- **OpenAI's math-tuned models.** Frontier LLM with math benchmarks; competitor at the proposer layer; not building substrate.
- **Academic structured-conjecture projects** (PolyMath-class, Mossinghoff Mahler catalogs, OEIS curatorial work). Distributed truth-accumulation but with social-trust verification rather than mechanical kernel discipline.

**The Σ-kernel's niche, sharply:** the substrate for empirical mathematical patterns (BSD residuals, Mahler-measure scans, RMT statistics, structural anomalies) that don't yet exist as Lean theorems. Combined with the residual primitive, this niche is "structured kills near the falsification boundary" — exactly the class of evidence Mathlib's binary accept/reject doesn't represent.

This positioning *survives any outcome of Silver's company*. If Silver succeeds, his outputs become CLAIMs we ingest (per §13). If Silver fails, the empirical-pattern niche is still vacant; Mathlib still doesn't cover it; the substrate is still load-bearing for that niche.

## 4. Architecture — hybrid neural + evolutionary, single mutation framework

(Same shape as v3; seven operator classes with minimum-share enforcement.)

The architecture diagram from v3 §4 is unchanged. Key additions: minimum proposal-share enforcement (§3.5.4) at the scheduler level; five-counts diagnostic (§7.4) including signal-class-residual count.

## 5. The neural policy head — corrected base-model rationale

### 5.1 Base model — corrected from v3

V3's §5.1 marketed Llemma as "closest to Silver's training distribution." That language is removed. v4 framing:

**Lead candidate: Llemma-7B.** Strong math-reasoning prior from Proof-Pile-2; license clean (Apache 2.0); fits 2× 16GB at 4-bit quantized; fits a single H100 for full-precision LoRA fine-tuning. The strength is the math-reasoning prior, not "inheritance of Silver's likely distribution."

**Honest acknowledgment:** the Llemma prior overlaps Silver's likely training corpus at the *corpus level*. This is not a structural advantage for Ergon's discovery surface — the differentiation work is done by the action-space asymmetry, the agreement-weighted value head, and the LoRA delta produced by substrate-verdict fine-tuning.

**v0.5 ablation candidates:** Qwen-7B (general-purpose, Apache 2.0) and Llama-7B (general-purpose). Both lack math-pretraining; their LoRA deltas under substrate-verdict fine-tuning may produce more divergent attractors than Llemma's. The ablation runs all three under identical fine-tuning protocol (multi-task LoRA on Tasks A/B/C, agreement-weighted reward, 1K iterations). Metric: held-out-cell coverage divergence between the resulting policies. Acceptance criterion: pick the base model whose LoRA delta produces the most divergent operator-class lineage distribution from non-LLM operators.

### 5.2 Three task adapters with structural decoupling

(Unchanged from v3 §5.2 — disjoint training partitions, periodic Task B retraining from scratch, cross-validation on held-out cells, inference-time independence.)

### 5.3–5.6

(Unchanged from v3 §§5.3–5.6 — agreement-weighted reward, periodic prior detox, self-play loop with disjoint partitions, training data rings.)

## 6. The evolutionary engine — quality-diversity over typed compositions

### 6.1 Action space

(Unchanged from v3.)

### 6.2 MAP-Elites archive — content-aware descriptor (REVISED in v4)

Per round-3 critique #5, v3's revised axes were partly content-aware but mostly construction-aware. v4 swaps DAG depth (construction) for output canonicalizer subclass (content):

| Axis | Type | What it captures |
|---|---|---|
| 1. **Output canonicalizer subclass** ← NEW in v4 | Content (categorical, 4 classes) | Discrete classification of what the output IS mathematically: group_quotient / partition_refinement / ideal_reduction / variety_fingerprint |
| 2. Equivalence-class entropy of the DAG | Categorical | Shannon entropy over canonicalizer subclasses in DAG composition |
| 3. Output-type signature | Categorical | Discrete return type of root node (~10 categories) |
| 4. Output magnitude bucket | Output-space | Log-binned over numerical output magnitude (5 quantile buckets) |
| 5. Output canonical-form distance | Output-space | Distance to nearest catalog entry under canonical-form transformation (5 quantile buckets) |

Total cells: 4 × 5 × 10 × 5 × 5 = **5,000** (was 6,250 in v3; tradeoff is fewer cells with better content/construction balance).

**Removed from v3:** DAG depth (replaced by output canonicalizer subclass).

The descriptor now has one strict-content axis (canonicalizer subclass), one categorical-entropy axis (equivalence-class entropy of DAG, a hybrid), one coarse-content axis (output-type signature), and two output-space axes. The archive forces diversity in *what the output is mathematically*, not just how the genome was constructed.

### 6.3 Seven mutation operator classes

(Unchanged from v3 §6.3 — `structural` / `symbolic` / `neural` / `external_llm` / `anti_prior` / `uniform` / `structured_null`. v4 adds the minimum-share enforcement of §3.5.4.)

### 6.4 Feature representation — staged transition

(Unchanged from v3.)

## 7. Discovery preservation in the fitness predictor (Task B)

(§§7.1–7.3 unchanged from v3 — asymmetric prune threshold P>0.95, asymmetric 3:1 loss, no-pruning sweeps, predictor_recall meta-metric.)

### 7.4 Five-counts diagnostic (REVISED from v3's four-counts)

Per round-3 critique #2 — the residual primitive (commit `4872bb4a`) shipped on the same day as v3 and the diagnostic didn't use it. v4 corrects:

For each operator class, run N episodes against `DiscoveryEnv` + `DiscoveryPipeline` + Residual primitive. Report **five counts** (was four):

1. **Catalog-hit rate** — episode produced a polynomial in Mossinghoff (rediscovery)
2. **Claim-into-kernel rate** — episode minted a CLAIM on a sub-Lehmer-band catalog miss
3. **PROMOTE rate** — the CLAIM survived the kill-path battery and was promoted (substrate-only and agreement-weighted variants)
4. **Battery-kill rate** — the CLAIM was rejected with typed kill-pattern captured
5. **Signal-class-residual rate** ← NEW in v4 — battery-killed CLAIMs whose residual classifier confidence ≥ 0.7 for signal-class

Statistical comparison runs Welch t-test with Holm correction across operator classes on **both** PROMOTE rate (count 3) and signal-class-residual rate (count 5). The five-counts diagnostic has statistical power even when PROMOTE rates are too low to differentiate operator classes — see §7.5.

### 7.5 Power calculation (NEW in v4)

Per round-3 critique #3 — projecting 10K-episode pilots without estimating effect sizes leaves the diagnostic possibly informationally null at every budget contemplated.

Welch t-test for two proportions, α=0.01 (Holm-corrected for multiple arms), β=0.2, lift d=0.5 (50% improvement of one arm over another). Approximate sample size:

```
n ≈ 4 * (z_α + z_β)² * p * (1-p) / d²
n ≈ 4 * (2.58 + 0.84)² * p * (1-p) / 0.25
n ≈ 187 * p * (1-p) / 0.25
n ≈ 750 * p * (1-p)
```

Resulting required episodes-per-arm at various PROMOTE rate floors:

| PROMOTE rate (p) | Episodes-per-arm needed | Compute envelope at $0.0001/episode |
|---|---|---|
| 10⁻¹ | ~70 | $0.01 |
| 10⁻² | ~750 | $0.08 |
| 10⁻³ | ~7.5K | $0.75 |
| 10⁻⁴ | ~75K | $7.50 |
| 10⁻⁵ | ~750K | $75 |

V3's projected 10K-episode pilots resolve operator-class differences only when PROMOTE rates are ≥10⁻³. The 1000×3 pilot at commit `1666c4a4` produced 0 PROMOTEs in 3000 episodes, suggesting the rate is ≤10⁻³ in the Lehmer-Mahler domain at MVP descriptor resolution.

**The five-counts diagnostic's signal-class-residual rate (count 5) should be denser than PROMOTE rate by at least one order of magnitude** because residual events fire on every signal-class kill, which is a strict subset of all events but a strict superset of all promotions. Empirically: if signal-class-residual rate is 10⁻¹ to 10⁻², the diagnostic resolves operator-class differences at 10K episodes; if PROMOTE rate is the only signal, it resolves only at 75K+ episodes.

**This is why v4's diagnostic upgrade is load-bearing, not cosmetic.** Without count 5, the substrate's empirical anchor is statistically dependent on a rate that may be unresolvable at any plausible compute envelope.

## 8. Compute and storage

(Unchanged from v3 except: add `residual_event_archive` table to track per-CLAIM residual classifier outputs for the five-counts diagnostic. ~5–10 GB at year-1 scale.)

## 9. The progression — MVP to v2.0

(Unchanged from v3 except: v0.5 includes the Qwen-7B / Llama-7B base-model ablation per §5.1.)

## 10. Empirical maturity caveats

V3's caveats retained, plus four v4-specific:

- **Llemma vs Qwen vs Llama LoRA-delta divergence.** *Pilot data: TBD.* v0.5 ablation will measure which base model produces the most divergent fine-tuning attractor under substrate-verdict fine-tuning.
- **Signal-class-residual rate floor.** *Pilot data: TBD.* The five-counts diagnostic's statistical power depends on count 5 being denser than count 3; first measurement is the v0.5 multi-arm pilot.
- **Output canonicalizer subclass distribution.** *Pilot data: TBD.* Whether the four canonicalizer subclasses populate non-trivially across MAP-Elites cells is an empirical question; if 90% of outputs land in one subclass, the axis is degenerate and v4.5 needs different content axes.
- **Calibration-bias rate.** *Pilot data: TBD.* The §11.5 meta-loop's substrate-grade metric (sharper-checker-promoted-but-original-battery-killed rate); first measurement when the Techne meta-loop ships.

## 11. What this proposal does NOT claim

V3's framing retained, plus:

- **Does not claim Llemma is structurally better than alternatives.** Only that it has a strong math-reasoning prior at acceptable size. v0.5 ablation may demonstrate Qwen or Llama produces more divergent LoRA deltas; if so, v0.5 swaps base models.
- **Does not claim PROMOTE rate is detectable at MVP scale.** §7.5 power calculation suggests it may not be. The five-counts diagnostic is the v4 mitigation; signal-class-residual rate is expected to be denser by an order of magnitude.

### 11.5 The deeper bear case + Techne meta-loop (NEW in v4)

Round-3 reviewer's deepest critique: the v3 bear case ("neural ≈ evolutionary on PROMOTE rate") assumes PROMOTE rate is non-zero. If the battery is miscalibrated for novel structure, PROMOTE rate is zero across all arms and the diagnostic is never informative; "engine bad" vs "battery bad" is undistinguishable.

V4's mitigation is a meta-loop integrating Techne's tool-forging capability with the residual primitive's classification:

**The meta-loop in operation:**

1. **High-residual kill detection.** Battery-killed CLAIMs whose residual classifier confidence is ≥ 0.9 for signal-class are flagged as `META_AUDIT_CANDIDATE`. These are kills the residual classifier "expected" to be signals — high confidence of structured residual but the kill happened anyway.

2. **Sharper-checker forging.** When `META_AUDIT_CANDIDATE` rate exceeds threshold (default: 5% of all kills in a 1K-episode window), Techne is triggered to forge a sharper checker for the dominant residual class. The sharper checker is a more refined falsification gate that addresses specific kinds of structured residuals the original battery may be over-rejecting.

3. **Historical audit.** The sharper checker is run on a curated set of historical battery-kills with similar residual signature. If the sharper checker promotes any of them, the original battery is flagged: `PATTERN_BATTERY_OVERREJECT_AT_RESIDUAL_CLASS_X`.

4. **META_CLAIM minting.** A META_CLAIM is minted against the original battery's calibration. Promoted META_CLAIMs add new kill tests to the battery's hierarchical lattice (per the v2-thesis Battery Limitations subsection's hierarchical falsification commitment).

5. **Calibration-bias rate metric.** `calibration_bias_rate = (sharper_checker_promoted) / (original_battery_killed_with_high_residual_confidence)`. Tracked as a substrate-grade metric.

**This makes "calibrated negative result" falsifiable.** If calibration-bias rate is high (>10%), the battery is the bottleneck; engine improvements won't help and battery refinement is the priority. If calibration-bias rate is low (<1%) and PROMOTE rate is still zero across all operator classes, the engine is the bottleneck; the bottled-serendipity thesis is unsupported and substrate gains a calibrated negative result.

The meta-loop is plug-compatible with all shipped substrate components: it consumes residual classifier outputs (existing); it triggers Techne tool-forging (existing capability per `pivot/techne.md`); it mints META_CLAIMs (existing kernel primitive); it adds new kill tests via the hierarchical-lattice mechanism (committed in v2-thesis but not yet shipped).

**v0.5 deliverable:** the meta-loop ships alongside the five-counts diagnostic. Without it, low PROMOTE rates are interpretively ambiguous.

## 12. Open questions for review

(V1's six retained; v2's three retained; v3's three retained; v4's two new added.)

13. (v4) Is the `output canonicalizer subclass` axis genuinely content-aware, or does its mapping back to DAG topology re-introduce construction bias? The canonicalizer is structural (it categorizes by algebraic invariant class); whether the mapping `output → canonicalizer subclass` is independent of DAG composition is unverified.

14. (v4) Is the calibration-bias rate metric actionable at the MVP scale, or does it require so much battery-history accumulation (multiple thousand kills with structured residuals) that it's only meaningful at v1.0+ scale? If the latter, the deeper bear case has no MVP-stage falsification path.

## 13. The 20-year position with operationalized Silver-ingestion

V3's §13 was rhetorical. V4 specifies what the substrate actually ingests from Silver-class output and what verdict it can render that the Lean kernel can't:

**The substrate ingests three fragments of Silver's likely output:**

1. **Empirical-pattern conjectures invoked in proofs.** Lean proofs sometimes invoke conjectures (BSD-conditional, GRH-conditional, Selmer-rank-conditional, Riemann-conditional) that the Lean kernel treats as axioms but which the substrate could falsify empirically through F1+F6+F9+F11 against held-out data. The substrate's verdict: "this conjectural axiom passes / fails empirical falsification." Lean's verdict: "this conjectural axiom is stated correctly." Different verdicts; both useful.

2. **Generalizations the proof makes from specific cases.** Lean tactic chains that prove "for all x: P(x)" via finite case-analysis or strong-induction can be ablated: substrate runs P(x) on out-of-distribution x and checks empirical survival. The substrate's verdict: "the proof's generalization survives empirical battery on OOD x" or "the generalization fails on x'." Lean's verdict: "the proof type-checks." Different surfaces; complementary.

3. **Near-miss CLAIMs from tactic-tree exploration.** Silver's learner explores tactic chains; intermediate goals and near-misses from the exploration are substrate-ingestible CLAIMs even when the parent proof closes via different tactics. Each near-miss CLAIM mints a separate substrate entry; the residual primitive classifies whether the near-miss is structured or noise.

**What the substrate does NOT ingest:** Lean-closed proofs themselves. There is no useful substrate falsification of "this Lean proof type-checks" — the Lean kernel did that. The substrate's role is the *empirical-pattern* layer adjacent to the formal-proof layer, not the formal-proof layer itself.

**The joint position:** Silver's learner ships formal-proof outputs to Mathlib (where they belong); empirical-pattern conjectures and generalizations and near-misses ship to the Σ-substrate (where they belong). The two substrates are content-addressed siblings rather than competitors.

## 14. The 20-year position

Identical to v3 §14. By the time Silver ships, the substrate has ~10⁶ promoted symbols and a public CLAIM API; the empirical-pattern fragment of Silver's output becomes CLAIMs in our pipeline; the joint becomes an ecosystem.

## 15. The first principle

(Unchanged from v3.)

> **Truth stays harder to satisfy than generation is to produce.**

V4's revisions are in service of preserving this asymmetry under sharper attack: the meta-loop prevents the substrate from compounding around a miscalibrated battery; the five-counts diagnostic prevents the substrate from being statistically blind at low PROMOTE rates; the minimum proposal-share enforcement prevents exploration from being squeezed out under selection pressure.

## 16. Genuine design freeze

V3's design-freeze recommendation was premature. Round-3 review caught internal contradictions and missed integrations that v3 had hidden behind language. V4 corrects them.

After v4:
- The §5.1 Llemma rationale is honest about prior overlap
- The diagnostic integrates the residual primitive (count 5)
- The power calculation is on the record
- The meta-loop makes "calibrated negative result" falsifiable
- The Mathlib comparison clarifies the substrate's actual niche
- The Silver-ingestion story is operationalized

V4 design freeze is justified on substantively different grounds than v3's: not "fundamentals haven't changed" (round 3 falsified that), but "round 3 was the high-water mark for design-layer critique; further rounds will be additive surface, not corrective; MVP empirical signal is the next high-value increment."

If a round-4 review surfaces critiques as deep as round 3's (internal contradictions or missed integrations), v5 is warranted. My prior: round 3 was the deepest the design-layer review will reach. Round 4 will be additive mitigation surface or shallow rephrasing. MVP empirical signal — observed signal-class-residual rate, observed cell-fill distribution, observed Task A/B accuracy divergence — is what the design needs next, not more text-layer critique.

## 17. One sentence

The Ergon learner v4 is a closed-loop scientific learning system for empirical mathematical patterns — a hybrid neural-plus-evolutionary mutation engine where the neural policy (LoRA on Llemma-7B with Qwen and Llama as v0.5 ablation candidates, prior overlap with Silver's likely corpus honestly named, differentiation from action-space + value head + LoRA delta rather than base prior) and six other mutation classes (with minimum proposal-share enforcement on `uniform` / `anti_prior` / `structured_null`) all contribute to a single MAP-Elites archive whose five-axis content-aware behavior descriptor (output canonicalizer subclass, equivalence-class entropy, output-type signature, output magnitude bucket, output canonical-form distance) forces diversity in what the output IS mathematically rather than how the genome was constructed, every CLAIM lineage-tagged and rewarded by an agreement-weighted combination of substrate-pass + cross-model agreement + held-out-battery-pass + signal-class-residual to mitigate specification gaming AND give the diagnostic statistical power at low PROMOTE rates, the fitness predictor calibrated for discovery preservation via asymmetric loss + no-pruning sweeps + recall-tracking, structurally decoupled from the mutation policy via disjoint training partitions, and audited against battery miscalibration via a Techne meta-loop that forges sharper checkers for high-residual kills and tracks calibration-bias rate as a substrate-grade metric — built MVP-first on local hardware ($0/mo, 2 weeks) and progressing to v2.0 (~$700–900/mo, +32 weeks), positioned alongside Lean Mathlib (the substrate-side comparison; covers theorems with formal proofs) rather than Silver alone (the learner-side comparison), covering the empirical-pattern manifold that neither Mathlib nor Silver reaches today, in service of the design principle that truth must stay harder to satisfy than generation is to produce — and now genuinely recommended for design freeze, with MVP empirical signal as the next high-value increment.

— Ergon, on behalf of the Prometheus agent ensemble
