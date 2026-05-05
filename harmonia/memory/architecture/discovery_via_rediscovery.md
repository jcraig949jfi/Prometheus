# Discovery via Rediscovery
## Rediscovery is the calibration test for discovery. The same loop, different oracle states.

**Status:** Foundational architectural recognition. Companion to [`bottled_serendipity.md`](bottled_serendipity.md), [`residual_signal.md`](residual_signal.md), [`sigma_kernel.md`](sigma_kernel.md).
**Date:** 2026-05-03
**Origin:** James Craig (HITL), articulated as an epiphany 2026-05-03 in response to Techne's `prometheus_math/DISCOVERY_RESULTS.md` of 2026-05-02 demonstrating the discovery_env reaching M=1.458 in the Salem cluster band. Charon (Claude Opus 4.7) is the writing instrument; the recognition is James's.
**Companions:**
- [`/prometheus_math/discovery_env.py`](../../../prometheus_math/discovery_env.py) — the generative env that demonstrates the loop closes
- [`/prometheus_math/DISCOVERY_RESULTS.md`](../../../prometheus_math/DISCOVERY_RESULTS.md) — Techne's results doc (rediscovery of Salem cluster band)
- [`/sigma_kernel/bind_eval.py`](../../../sigma_kernel/bind_eval.py) — the executable-symbols kernel extension that makes the loop possible
- [`residual_primitive_spec.md`](residual_primitive_spec.md) — the residual classification machinery that makes discovery distinguishable from artifact

---

## TL;DR

If the architecture can rediscover existing mathematics (it can — Techne's discovery_env reached M=1.458 in the Salem cluster band on 2026-05-02), then by the same architecture's structural logic — applying mutation operators against the same falsification battery — it should be able to discover *adjacent* undiscovered mathematics. **Rediscovery and discovery are the same loop with different oracle states.**

But — per ChatGPT's adversarial review of this doc on 2026-05-03 — **rediscovery competence is necessary but not sufficient for discovery competence.** A system can be excellent at closed-world search (rediscovering known structure) and fail completely at open-world search (producing meaningful novelty). The honest framing is a three-stage validation ladder:

1. **Rediscovery (closed world).** Can the system recover known results? Calibration / sanity check.
2. **Withheld rediscovery (blind test).** Can the system rediscover results intentionally hidden from it? This is the much stronger test.
3. **Open discovery + null baseline.** Can the system produce candidates that (a) are not in catalogs, (b) survive the falsification battery, AND (c) outperform null-generator baselines under adversarial verification?

The third condition is the one most ML "discovery" papers skip. Without a null comparator, "we found a polynomial in band that's not in the catalog" might be exactly what uniform random sampling produces; the system's contribution is then zero. Discovery means *better-than-random* survival under the same battery.

Architecturally, the difference between rediscovery and discovery is one additional gate (catalog-miss → CLAIM → battery → classify) plus one comparator (run the null in parallel and compare survivor rates). Every component exists or is being built; the pipeline becomes operational pending three pieces: (i) promote `DISCOVERY_CANDIDATE` from a log line to a substrate CLAIM, (ii) Techne's residual primitive 5-day MVP, (iii) a withheld-catalog benchmark + null-generator scaffolding.

## 1. The unification

The field treats two things as separate:

- **Rediscovery** = "can the system find what we already know?" (a capability test)
- **Discovery** = "can the system find what we don't know?" (the research goal)

In the Prometheus architecture, they are the **same loop with different oracle states.** A discovery candidate is a rediscovery target whose catalog entry doesn't exist yet. Mossinghoff's 178-entry snapshot is a proxy for the universe of small-Mahler-measure polynomials; any polynomial the agent finds in band that's not in the snapshot is either:

- (a) a numerical artifact (floating-point drift, near-cyclotomic case)
- (b) a known polynomial in non-canonical form (different ordering, different normalization)
- (c) genuinely new

The pipeline distinguishes (a)/(b)/(c) using machinery that already exists or is being built. The catalog membership becomes a discriminator, not a reward signal.

This recognition collapses what looked like two engineering programs (rediscovery validation + discovery research) into one (calibrate the loop on rediscovery; run it forward for discovery). Same code, same kernel, same battery, same agents. Only the absence-from-catalog interpretation changes.

## 2. The pipeline

Rediscovery loop (already running):
```
agent → generative_action → BIND/EVAL → reward (matches catalog) → policy gradient
```

Discovery loop (one extra gate):
```
agent → generative_action → BIND/EVAL → catalog_check
   if HIT:  reward fires (rediscovery — calibration evidence)
   if MISS: CLAIM into kernel
            → falsification battery (F1+F6+F9+F11)
            → residual classification (signal/noise/instrument_drift)
            → cross-modality verification (PARI/GP + SAT + symbolic)
            → if signal-class survives: PROMOTE as discovery_candidate@v1
            → if noise/drift: archive with typed reason
```

Component status:

| Component | Status | Source |
|---|---|---|
| Generative env (action space, sparse reward) | shipped | `prometheus_math/discovery_env.py` |
| BIND/EVAL primitives | shipped 2026-05-02 | `sigma_kernel/bind_eval.py` (+ v2 in `sigma_kernel/bind_eval_v2.py`) |
| Catalog cross-check | shipped (Mossinghoff only) | `prometheus_math/discovery_env.py` |
| CLAIM into kernel | shipped (v0.1) | `sigma_kernel/sigma_kernel.py` |
| Falsification battery (F1–F20) | shipped | `cartography/shared/scripts/falsification_battery.py` |
| Residual classification | **shipped 2026-05-03** | `sigma_kernel/residuals.py` (~748 LOC, commit `4872bb4a`) |
| ObstructionEnv (cross-domain validation) | **shipped 2026-05-03** | `prometheus_math/obstruction_env.py` (commit `d339dc45`) |
| OEIS-data rediscovery validation | **shipped 2026-05-03** | `prometheus_math/_obstruction_corpus_live.py` + `OBSTRUCTION_LIVE_RESULTS.md` (commit `b0355b1d`) |
| Cross-modality verification | proposed in residual spec | spec stage |
| PROMOTE with provenance | shipped (v0.1) | `sigma_kernel/sigma_kernel.py` |
| `DISCOVERY_CANDIDATE` → substrate CLAIM | partial integration | Ergon's `DISCOVERY_RESULTS.md` update (commit `aae30bf3`) |
| Withheld-rediscovery benchmark (stage 2) | not yet built | per §6.2.5 |
| Null-baseline comparator (stage 3) | not yet built | per §6.2 |

**Status update note (2026-05-03 evening):** the table immediately above reflects shipping events that happened in the 24 hours after this doc's first version was written. Five of the first eleven rows transitioned from "spec stage" / "proposed" / "not yet attempted" to "shipped." This is itself an empirical observation about the architecture's compounding rate — the substrate produces convergent multi-agent action when foundational docs are sharp. Treated as data, not as celebration: convergence does not equal correctness, and the validation ladder (§3.5) still applies to the architecture's claims about itself.

The pipeline is operational pending two pieces:

1. **Engineering step:** in `discovery_env.py`, promote the `DISCOVERY_CANDIDATE` log line from a side-note to a substrate CLAIM that triggers the full pipeline (battery → residual classification → cross-modality → PROMOTE-or-archive). Techne's lane; small change; recommended as next move.

2. **Architectural completion:** Techne's residual primitive MVP (5 days per the stoa proposal). The classification machinery is what tells artifact from real discovery.

## 3. Why this is a genuine architectural unification, not just rhetoric

Three reasons.

**First — it makes the bottled-serendipity thesis empirically falsifiable in a sharper form.** The thesis says LLMs-as-mutation-operators produce off-modal samples that occasionally land outside the training distribution and inside truth. The "outside training, inside truth" claim is exactly "outside the catalog, surviving the battery, classifying as signal-class." Rediscovery proves the second clause works (the architecture can find truth-class samples); discovery via the same loop tests whether off-modal samples ever land outside the catalog. If they don't, the bottled-serendipity prior is too tight and the thesis is partially wrong. If they do, the thesis has a positive case.

**Second — it operationalizes the mad-scientist principle at the architecture level.** Rediscovery IS the chase; discovery candidates ARE the byproducts. The mad-scientist principle says capture all six (chase + five byproducts); the discovery pipeline mechanically captures both. Catalog hits drive policy-gradient learning; catalog misses become CLAIMs. Neither is wasted. Both feed the substrate.

**Third — it inverts the conventional research-validation relationship.** Conventional ML benchmarks rediscovery to *validate the system*; the architecture goes further and uses rediscovery to *calibrate the discovery loop*. Same compute pays for two outputs: capability evidence (the agent rediscovers known structure) and discovery harvest (the agent occasionally produces structure that's not in the catalog and survives the battery). Most labs run only the first half because they don't have the substrate to capture the second half.

## 3.5 The validation ladder (added 2026-05-03 from ChatGPT review)

A system that passes only stage 1 has demonstrated nothing about discovery — it has demonstrated competent search in known territory. Three stages, in order of difficulty:

### Stage 1 — Rediscovery (closed world)

Run the agent against a fully-visible catalog. Reward fires on catalog match. Capability claim demonstrated: search-competence + representation-adequacy + verification-alignment. This is what Techne's discovery_env did on 2026-05-02 (M=1.458 in Salem cluster band, catalog-grade rediscovery).

**Purpose:** unit-test the loop. Prove the architecture can find SOMETHING.
**Sufficient for:** validating the framework isn't broken.
**NOT sufficient for:** any claim about discovery.

### Stage 2 — Withheld rediscovery (blind test)

Curate a held-out subset of the catalog (e.g., remove 20% of Mossinghoff entries before evaluation). Treat removed entries as "unknown" to the system. Run the agent. Measure: how many removed-but-real entries does the system rediscover?

**Purpose:** test generalization beyond known regions under controlled conditions.
**Sufficient for:** validating that catalog-miss-survival isn't just memorization.
**NOT sufficient for:** open discovery (the held-out entries are still in *some* catalog the system might have seen during training; LLM-prior contamination is a real concern).

### Stage 3 — Open discovery with null baseline

Run agent for N episodes. Run a null generator (uniform random over the action space, OR random reciprocal polynomials in the search domain) for the same N episodes. Both stream through the same pipeline (BIND/EVAL → catalog check → CLAIM if miss → battery → residual classification).

Compare:
- Agent's catalog-miss-survival rate (signal-class)
- Null's catalog-miss-survival rate (signal-class)

**The agent's discovery rate is meaningful only insofar as it exceeds the null.** If equal, the LLM prior provides no value beyond random sampling and the architecture's contribution to discovery is zero. If agent > null by a statistically significant margin, the architecture is participating in discovery rather than simulating it.

**Purpose:** distinguish discovery from sampling.
**Sufficient for:** the substrate-grade claim that the architecture produces discoveries.
**NOT sufficient for:** claims about importance or mathematical significance (those require human or future Aporia-class judgment).

ChatGPT's sharper formulation, adopted as canonical:

> **A discovery engine must rediscover known results, rediscover withheld results, AND produce novel candidates that outperform null baselines under adversarial verification.**

The previous version of this doc treated stage 1 as if proving discovery worked. It doesn't. All three stages are required.

## 4. Connection to bottled-serendipity — sharper falsifiability

The current statement of the bottled-serendipity thesis (in [`bottled_serendipity.md`](bottled_serendipity.md)) leans on historical analogy: "most LLM hallucinations are wrong; some are wrong in interesting ways; a vanishingly small fraction is wrong in ways that turn out to be true outside the training distribution." This is rhetorically strong but empirically vague — what's the rate? what's the test?

The discovery-via-rediscovery framing gives a concrete empirical test:

> Run the agent for N episodes. Count: catalog hits (rediscovery), catalog misses that survive battery as signal-class (discovery candidates), catalog misses classified as noise (artifacts), catalog misses classified as drift (instrument issues). Report all four counts.

The bottled-serendipity thesis now has a measurable consequence: the rate of (signal-class catalog miss) / (total episodes) is the empirical rate of LLM-mutation-driven discovery in the chosen domain. If the rate is zero across many domains and many models, the bottled-serendipity thesis is wrong. If the rate is non-zero and stable, the thesis is positively supported.

This is a much stronger empirical anchor than the thesis previously had. The pilot becomes natural: run discovery_env for 10K episodes; report the four counts; iterate on agent / prior / cross-check coverage.

## 5. Failure modes

Four worth naming explicitly so the discipline is clear about what the unification doesn't claim.

### 5.1 Adjacency limit

"Adjacent" undiscovered math is reachable via mutation; non-adjacent is not. LLM priors trained on existing math reach only as far as the prior shape allows. This is an important neighborhood — most actual mathematical discoveries ARE adjacent to existing work — but a real bound. Vast tracts of math may be unreachable by any prior-shaped mutation no matter how much compute is thrown at the loop. The architecture's discovery surface is bounded by the union of (a) what the LLM prior can hallucinate near, (b) what non-LLM mutation sources can reach via combinatorial extension, and (c) what the falsification battery can recognize as signal-class. None of these is the universe of mathematics.

### 5.2 Catalog-as-ground-truth-via-absence is weaker than positive verification

A polynomial absent from Mossinghoff's snapshot might just be missing from the snapshot, not actually new. Mossinghoff's catalog is curated, not exhaustive. For real discovery claims, "absent" must be cross-checked against multiple catalogs (LMFDB labels, OEIS A-numbers, arXiv titles, full Lehmer literature). This is engineering work — Techne's tool-forging needs to handle multi-catalog consistency checks before any discovery_candidate is promoted past the candidate stage.

### 5.3 Most "discoveries" will be trivial

Polynomial-in-known-band ≠ mathematical contribution. The architecture finds *candidates*; humans (or future Aporia-class agents with mathematical-significance evaluators) judge interestingness. The substrate doesn't yet have a "is this interesting?" filter — that's a different problem from "is this real?", and conflating them is how you get cold-fusion-class enthusiasm for trivial findings. The discipline: discovery_candidate@v1 PROMOTE means "real and not in the catalog," not "important." Importance is a separate downstream judgment requiring its own machinery.

### 5.5 Rediscovery competence does not entail discovery competence

ChatGPT's structural critique. A system can be excellent at closed-world search and fail completely at open-world search — the loops have different statistical structure. Rediscovery operates against a fixed target distribution (the catalog); discovery operates against a target distribution that doesn't yet exist. The skills overlap but aren't identical:

- Rediscovery rewards exploitation of known structure
- Discovery rewards productive exploration of unmapped structure
- A system tuned for the first may have catastrophically narrow search behavior for the second

The validation ladder (§3.5) is the discipline that prevents stage-1 success from being mistaken for stage-3 success. Without the ladder, the discovery_via_rediscovery framing collapses into "we built a clever rediscovery system" and the "via" loses its content.

### 5.4 The mutation prior may systematically miss undiscovered space

Interesting unsolved problems have resisted human imagination for reasons. If undiscovered math has different statistical shape than discovered math (which by definition it must — interesting unsolved problems have resisted exactly because they don't fit existing shapes), LLM priors trained on existing math may be poorly tuned to that shape. The correlated-hallucinations problem from the v2 thesis review applies in spades: every LLM agent's prior shares the same blind spots, so the discovery rate may saturate at the LLM prior's coverage rather than at the universe's actual structure.

Mitigation: non-LLM mutation sources (random program synthesis, symbolic perturbation of existing PROMOTEd symbols, parameter sweeps over existing structure) are not optional for discovery work. They're load-bearing. The architecture must inject these alongside LLM-generated proposals, not just rely on the LLM prior.

## 6. Concrete engineering steps

In order, smallest first:

### 6.1 Promote DISCOVERY_CANDIDATE to a substrate CLAIM (Techne's lane, ~1 day)

In `prometheus_math/discovery_env.py`, the current code logs `DISCOVERY_CANDIDATE` as a side note:

> "Any polynomial that earns the jackpot reward is auto-checked against the prometheus_math.databases.mahler snapshot (178 known small-M entries). If it's a known Salem, the env logs the match; if it's *not* known, the env logs DISCOVERY_CANDIDATE and the run is flagged for manual verification (almost certainly numerical artifact, but the discipline is to record and check)."

The recommendation: replace the log-and-flag pattern with a kernel CLAIM. The CLAIM's hypothesis is "this polynomial has Mahler measure M ∈ [1.001, 1.18] AND is not in Mossinghoff's snapshot AND is irreducible AND is reciprocal." The kill_path runs F1+F6+F9+F11 + multi-catalog consistency check. If the CLAIM survives, it's PROMOTEd as `discovery_candidate_<hash>@v1`. If it's killed, the kill_pattern is captured (artifact / known-in-other-form / reducible / etc.) as substrate.

This single change converts the current "we'll check by hand later" discipline into mechanical substrate-grade processing. Techne's call.

### 6.2 Run the four-counts pilot WITH null baseline (Charon's lane, ~5 days once 6.1 lands)

Once DISCOVERY_CANDIDATE is a CLAIM, run discovery_env for 10K episodes under TWO conditions:

**Condition A (system):** LLM-driven REINFORCE agent operating through BIND/EVAL.
**Condition B (null):** Uniform random sampler over the same coefficient action space, no policy gradient, no LLM prior. Same number of episodes.

For each condition, report:
- Total episodes
- Catalog-hit rate (rediscovery)
- CLAIM-into-kernel rate (catalog-miss)
- PROMOTE rate (signal-class survival)
- Battery-kill rate (artifact / drift)

The substrate-grade comparison: **agent PROMOTE rate vs. null PROMOTE rate, statistically significant difference?** If agent PROMOTE rate ≤ null PROMOTE rate, the LLM prior is not contributing to discovery; the architecture is sampling, not discovering. If agent > null with significance, the architecture is participating in discovery — by ChatGPT's stage-3 standard.

Even if both rates are zero in 10K episodes, that's a useful joint upper bound on discovery rate at this configuration; it suggests the action space, the prior, or the battery is too tight.

### 6.2.5 Build the withheld-rediscovery benchmark (Charon's lane, ~2 days)

Per ChatGPT's stage-2 requirement. Take Mossinghoff's 178-entry snapshot. Randomly partition: 142 entries (80%) remain visible to the catalog-check; 36 entries (20%) are withheld and treated as "unknown" during evaluation. Run the agent. Measure:
- Withheld-recovery rate: how many of the 36 withheld entries does the agent rediscover?
- Withheld-PROMOTE rate: of those rediscoveries, how many survive the full pipeline as if they were genuine discoveries?

The withheld set provides a "discovery-shaped" target (real entries the system shouldn't have memorized) where ground truth is known. The withheld-recovery rate is a more honest discovery-capability number than the open-discovery rate, because we can verify it. Run before the open-discovery pilot in §6.2 — it's faster and gives a calibration estimate for what stage-3 numbers should look like.

### 6.3 Multi-catalog cross-check (Techne's lane, ~1 week)

Currently `discovery_env.py` checks Mossinghoff only. Production discovery work requires LMFDB + OEIS + arXiv-title fuzzy match + Lehmer-literature catalog (Boyd, Smyth, Mossinghoff, Borwein-Mossinghoff). Techne forges the tool; each external catalog becomes a typed `catalog_consistency_check@v1` that EVAL through the substrate.

### 6.4 Non-LLM mutation source (Charon + Techne, ~1 week)

Add at least one non-LLM mutation source to the agora's proposal pool: random reciprocal polynomial generation in the discovery_env's coefficient space, with no LLM prior shaping. Run in parallel with LLM-prompted agents. Compare PROMOTE rates. If non-LLM source produces signal-class survivors at higher rate than LLM source, the LLM prior is too tight; if LLM source dominates, the prior is well-tuned to the search problem.

### 6.5 Cross-domain replication (later, after ~2 months of Lehmer pilot)

Once the discovery pipeline is validated on Lehmer / Mahler-measure, replicate on a second domain with similar structure (BSD rank, modular-form coefficients, OBSTRUCTION_SHAPE pattern detection on held-out OEIS sequences). Cross-domain replication is the test that the loop is the architecture, not a Lehmer-specific artifact.

## 6.6 Shadow Catalog (added 2026-05-03 from Gemini review)

Gemini's contribution. The architecture currently has two states for a candidate post-evaluation: PROMOTE-as-canonical-symbol or REJECT-as-artifact. This is a false dichotomy. Many candidates that survive the battery as signal-class are *neither* canonical truths *nor* artifacts — they are well-formed mathematical structures that haven't been recognized in any external catalog yet.

Define a third state: **Shadow Catalog membership.** A typed substrate object that holds candidates that:
- Survived the falsification battery as signal-class
- Are not in any consulted external catalog (Mossinghoff / LMFDB / OEIS / arXiv-title-fuzzy)
- Outperform the null baseline on the same pipeline (per §6.2)
- But have not yet been independently verified or recognized

Shadow Catalog membership is a substrate-grade typed status. It's content-addressed (same provenance machinery as PROMOTE). It's queryable (Aporia can scan for cross-claim residual patterns within the Shadow Catalog). It's promotable (a Shadow Catalog entry that gains independent verification — formal proof, external publication, additional cross-modality concordance — is promoted to canonical PROMOTE-as-symbol).

The Shadow Catalog avoids the cold-fusion failure mode (treating every catalog-miss-survivor as canonical truth) while preserving the candidate for downstream investigation. It is the holding pen between "this might be discovery" and "this IS discovery" — and the substrate keeps it addressable across years.

Engineering: this is a kernel extension proposal. Status: spec-stage; recommend folding into Techne's residual_primitive_spec.md as a third typed status alongside REFINE-able RESIDUAL and noise-class archive.

## 7. Worked example — Techne's M=1.458 result through the discovery pipeline

Techne's discovery experiment of 2026-05-02 produced a polynomial with M=1.458 in the Salem cluster band after two algorithm failures and one breakthrough. Currently this is logged as a successful rediscovery (Salem cluster is well-known). Run through the discovery pipeline:

1. **Generative action.** Agent constructs polynomial coefficient-by-coefficient over 6 steps. Final polynomial has M=1.458.
2. **BIND/EVAL.** Polynomial evaluated through the substrate; output_repr = 1.458, actual_cost recorded, provenance link to binding.
3. **Catalog check.** Mossinghoff snapshot consulted. M=1.458 is in the Salem band but the specific polynomial may or may not match an existing entry.
4. **If catalog hit:** reward fires; rediscovery logged; nothing further.
5. **If catalog miss:** CLAIM minted with hypothesis "this polynomial is reciprocal, irreducible, in Salem band, not in Mossinghoff." kill_path runs F1+F6+F9+F11 + irreducibility check (cypari `polisirreducible`) + reciprocity check + multi-catalog consistency.
6. **Battery + classification.** If the claim survives all kills with signal-class residual structure: PROMOTE as `salem_polynomial_candidate_<hash>@v1` with provenance from generative env back through every step. If killed: substrate-eligible kill-pattern (`PATTERN_NUMERICAL_ARTIFACT_NEAR_CYCLOTOMIC` or similar typed reason).
7. **Substrate output.** Either way, durable typed artifact addressable by content hash.

This single example converts what was logged as "rediscovery" into a substrate-grade run-through that produces either a discovery candidate or a typed kill-pattern, with the four counts (hit / miss / promote / kill) contributing to the empirical anchor of the bottled-serendipity thesis.

The architecture doesn't currently do this; it would after step 6.1 ships.

## 8. Why this is foundational

Three reasons.

**First — it sharpens the bottled-serendipity thesis from rhetorical to empirical.** The discovery rate becomes a measurable quantity per domain per configuration. The thesis was previously vague about magnitudes; this gives it a positive test.

**Second — it unifies what the field has been treating as two distinct programs into one.** Rediscovery validation and discovery research collapse into a single loop with one extra gate. Same code, same battery, same agents. Compute spent on rediscovery automatically subsidizes discovery, and vice versa. The substrate's compounding rate roughly doubles.

**Third — it makes the architecture's discovery claims falsifiable.** The four-counts pilot gives a number. If the number is zero across many domains and many configurations, the thesis is wrong. If it's non-zero and stable, the thesis is supported. Either outcome is substrate-grade. The architecture can be wrong about itself in a recoverable way — which is, ultimately, what falsification machinery is for.

## 9. The engine that populates the pipeline

This document specifies the *gate* (catalog miss → CLAIM → battery → classify) and the *measurement* (four-counts pilot per mutation operator class). It does not specify the *engine* that produces the candidates flowing through that gate.

That engine is the Ergon learner, designed in [`pivot/ergon_learner_proposal_v3.md`](../../../pivot/ergon_learner_proposal_v3.md) (design-freeze version, supersedes v1 and v2). The two documents are complementary:

- **This doc** is the architectural skeleton — what the discovery pipeline is, why rediscovery and discovery are the same loop, how the four-counts pilot quantifies the bottled-serendipity thesis.
- **The Ergon learner doc** is the engine design — a hybrid neural-plus-evolutionary mutation system with seven lineage-tagged operator classes contributing to a single MAP-Elites archive over typed compositions of the math arsenal, every CLAIM rewarded by an agreement-weighted combination of substrate-pass + cross-model + held-out-battery, plug-compatible with `BindEvalKernelV2` + `DiscoveryPipeline` + Residual primitive.

The seven mutation operator classes the Ergon learner specifies (`structural` / `symbolic` / `neural` / `external_llm` / `anti_prior` / `uniform` / `structured_null`) are each a different shape of mutation feeding the same gate. The four-counts pilot reports per-class PROMOTE rates with statistical comparison; the substrate-grade discovery rate per class is the empirical anchor for the thesis.

The architecture is operative once both docs ship: the gate (this doc, §6.1 + §6.2 already implemented as of commit 1666c4a4) and the engine (the Ergon learner, MVP build pending design freeze).

---

*Rediscovery proves the loop closes. Discovery is the same loop run forward. The catalog is the discriminator, not the reward. The architecture finds candidates; the substrate filters; the pipeline produces either typed survivors or typed kill-patterns. Either is durable. Both compound.*
