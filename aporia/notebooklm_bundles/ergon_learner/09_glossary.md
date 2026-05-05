# Glossary — Terms Used Across the Ergon Learner Bundle

**Date:** 2026-05-03

This glossary defines every term that appears in two or more of the other bundle sources. NotebookLM grounds its answers better when key terms are defined in their own source and cited consistently.

---

**agent.** A candidate-generator in the discovery loop. Examples: Ergon's MAP-Elites engine, Techne's REINFORCE baseline, a hypothetical Silver-class learner. Multiple agents can run against the same env, battery, and null world.

**AlphaZero.** Silver et al., Nature 2017/2018. Reinforcement-learning agent that masters chess, shogi, and Go through self-play with no human-game training data. The structural pattern Ergon adopts (search engine + mechanical referee + diversity-preserving population), at miniature scale.

**arsenal.** The 85-op metadata table at `prometheus_math.arsenal_meta`. Each op is a typed callable with cost annotations, postconditions, authority references, and an equivalence-class tag. The action space for any agent in the discovery loop.

**BIND/EVAL.** Two opcodes added to the Σ-kernel as a sidecar by Techne in commit 2026-05-02. BIND attaches a callable to a substrate symbol with cost+postconditions+authority refs. EVAL runs the bound callable under a budget, returns evaluation symbol with output, actual cost, provenance link. Hash-drift detection on every EVAL. Ergon's hypothesis schema maps near-trivially to (BIND, EVAL) typed kernel actions.

**Bottled serendipity.** Charon's foundational thesis (`bottled_serendipity.md`). LLM-hallucination understood as prior-shaped stochastic samples from compressed human conceptual space. Distinguished from RNG (uniform serendipity, zero prior) and from deterministic search (no serendipity). The mutation operator's value is in its off-modal samples that land outside the training distribution AND inside the truth.

**Canonicalizer subclass.** One of {group_quotient, partition_refinement, ideal_reduction, variety_fingerprint}. Per Charon's `canonicalizer.md` spec. Used as one of the 5 axes of Ergon's behavior descriptor and as the typology for residual classification.

**CLAIM.** Σ-kernel opcode that allocates a provisional claim with hypothesis, evidence, and a kill path. Born at lowest tier unless overridden. The first stage of the falsification pipeline.

**discovery_env.** Techne's generative reciprocal-polynomial environment in `prometheus_math/discovery_env.py`. Sparse reward (only `1.001 < M < 1.18` pays the +100 jackpot — strict sub-Lehmer territory). Ran ~117K trajectories on 2026-05-02; best result M=1.458 (Salem cluster band rediscovery).

**ECE (Expected Calibration Error).** Standard ML metric for classifier calibration. Trial 1 acceptance includes ECE ≤0.05.

**F1, F6, F9, F11.** Specific kill-tests in Charon's falsification battery. F1 = permutation null. F6 = base rate. F9 = simpler explanation. F11 = cross-validation. The "unanimous battery" requires all four to fire for a kill verdict.

**F_TRIVIAL_BAND_REJECT.** A kill-test specific to Ergon's MVP. Catches outputs that match one of 6 trivial-pattern signatures (4 static + 2 temporal). Implemented in `ergon/learner/triviality.py`. Real-time alert if trigger rate falls outside [5%, 30%].

**FALSIFY.** Σ-kernel opcode that dispatches a claim + kill_path to the Ω oracle subprocess. Returns VerdictResult. Fails closed: any oracle error becomes BLOCK with rationale.

**five-counts diagnostic.** Trial 3 measurement framework. Extends the existing four-counts pilot with a fifth count: signal-class-residual rate (battery-killed CLAIMs with residual classifier confidence ≥0.7). Welch t-test + Holm correction on both PROMOTE rate and signal-class-residual rate.

**GATE.** Σ-kernel opcode. Three-valued return: CLEAR, WARN (with rationale bubbled), BLOCK (raises BlockedError). Short-circuits the pipeline on BLOCK.

**Genome.** A typed DAG over arsenal atoms. Implemented as `Genome` dataclass in `ergon/learner/genome.py`. Deterministic content hashing via sha256 over canonical DAG serialization. The atomic unit of Ergon's evolutionary search.

**Hot-swap protocol.** Per v5 §6.2. If a behavior-descriptor axis exceeds 70% concentration in one bin, swap that axis with a pre-specified replacement candidate from `descriptor_config.toml`. Defense against descriptor degeneracy.

**HITL (Human-in-the-loop).** Decisions requiring human input. v8 adopts a 24-hour auto-escrow SLA: any HITL decision not answered within 24 hours auto-escrows the claim (status `HITL_ESCROW_TIMEOUT`); the system continues. Escrowed claims surface in a weekly HITL queue.

**Kill-battery survival.** Ergon's reward signal. A genome's reward equals the number of falsification-battery kill-tests it survives. Selection pressure favors high-survival genomes.

**LiteLLM.** Library for cross-model API standardization. Used by Ergon's cross-model evaluator (v0.5+, not MVP).

**Llemma.** A 7B-parameter open-weight math-specialized language model. Target for LoRA fine-tuning at v1.0 (not MVP).

**LoRA (Low-Rank Adaptation).** Parameter-efficient fine-tuning method. Hugging Face PEFT + bitsandbytes stack. v0.5+ feature.

**MAP-Elites.** Mouret & Clune (2015), arXiv 1504.04909. Quality-diversity evolutionary algorithm. Maintains an archive keyed on behavior characteristics; each cell holds the highest-fitness individual with that behavior. Ergon's core search algorithm.

**Mossinghoff catalog.** Maintained by Michael Mossinghoff at https://www.mossinghoff.info/lehmer/. ~178 small-Mahler-measure polynomials with M < 1.3 to degree 180; complete to degree 44 for Salem numbers M < 1.3. The canonical ground-truth catalog for Lehmer-related discovery work. Last substantive refresh traces to 2008 (Rhin-Mossinghoff-Wu).

**Null-world generator.** A mutation source that samples from the same distribution as the agent but without selection pressure or prior-shaping. Used as the comparison baseline for discovery claims. K=10 publishable / K=5 interesting per Aporia Scout #9.

**Operator class.** A category of mutation operator. Ergon ships 5: structural, symbolic, anti_prior, uniform, structured_null. Minimum-share enforcement: uniform ≥5%, anti_prior ≥5%, structured_null ≥5%; total non-prior ≥15%.

**pyribs.** Python library for quality-diversity algorithms including MAP-Elites. Ergon's archive backend; pointer-storage discipline (heavy data in Postgres, pyribs holds pointers + descriptor coordinates).

**PROMOTE.** Σ-kernel opcode. Atomic transaction: verify capability unconsumed, verify claim has non-BLOCK verdict, consume capability, append symbol, update claim status. The terminal stage of the falsification pipeline; the substrate's "this passed" event.

**Residual.** Per Techne's stoa proposal `2026-05-02-techne-on-residual-aware-falsification.md`. A typed object representing what was almost-killed-but-survived in the falsification battery. The substrate's spectral verdict — replaces binary PROMOTE/BLOCK with structured "how the claim failed" metadata.

**Residual classifier.** A model that classifies residuals into {signal-class, noise-class, instrument-drift-class}. Implemented in `sigma_kernel/residuals.py` (commit 4872bb4a). Trial 1 of Ergon's MVP benchmarks this classifier on 200 curated samples.

**REINFORCE.** Williams (1992). Pure policy-gradient reinforcement-learning algorithm. Techne's baseline algorithm in `discovery_env`. v8's Trial 3 will compare REINFORCE against Ergon's MAP-Elites in v0.5+ (currently three-arm without REINFORCE).

**Salem cluster band.** Region of small-Mahler-measure space around M=1.4 to 1.5 — corresponds to Salem numbers, a specific class of algebraic integers. Techne's discovery_env reached M=1.458 in this band on 2026-05-02 — rediscovery, not novelty.

**Selection pressure.** The mechanism by which higher-fitness genomes are preferentially propagated in evolutionary search. In Ergon, selection pressure comes from kill-battery survival rates per cell.

**Sigma kernel (Σ-kernel).** Project Prometheus's substrate-discipline runtime. Implements seven opcodes (RESOLVE, CLAIM, FALSIFY, GATE, PROMOTE, ERRATA, TRACE) with append-only storage, content-addressed provenance, capability-linear authorization, three-valued GATE semantics, and falsification-first promotion. v0.1 shipped 2026-04-29; BIND/EVAL extension shipped 2026-05-02.

**Silver, David.** DeepMind alumnus, lead author on AlphaGo lineage. Founded Ineffable Intelligence in early 2026, raised $1B at $4B pre-money on the thesis that LLMs are dead-ended for reaching superintelligence. The triggering context for Prometheus's pivot framing.

**Stage-3.5 proxies.** Aporia's proposed extensions to ChatGPT's three-tier validation ladder. Permutation-distance and frequency-weighted recall as additional stage-3 (open discovery) proxies that test whether the agent's PROMOTE rate is uncorrelated with the prior's training coverage.

**Substrate symbol.** A unit of substrate state. Created by PROMOTE (or bootstrap_symbol). Content-addressed (sha256 of canonical serialization), append-only, provenance-tracked. Substrate symbols compound: each promoted symbol becomes reusable verification machinery for future claims.

**Three-tier validation ladder.** ChatGPT's framework for distinguishing rediscovery from discovery: (1) closed-world rediscovery, (2) withheld rediscovery (blind test), (3) open discovery + null baseline. Each tier is a necessary-but-not-sufficient condition for the next.

**Trial 1 / 1.5 / 2 / 3.** Ergon's MVP trial sequence. Trial 1 = adversarial residual benchmark (Days 1-4). Trial 1.5 = adversarial optimization probe (Days 5-7). Trial 2 = evolutionary engine with bounded buckets (Days 8-17). Trial 3 = five-counts diagnostic three-arm pilot (Days 18-22).

**TRACE.** Σ-kernel opcode. Recursive walk of a symbol's provenance dependency hashes. Cycle-safe via visited set. Returns ProvenanceGraph.

**Unsloth.** Library for faster LoRA training, less VRAM than alternatives like Axolotl. Ergon's MVP-tier LoRA stack (deferred to v0.5+).

**v8.** Ergon's design freeze. Focused delta from v7 (commit 9cafeb35). Adds Trial 1.5 (adversarial optimization probe), revises Trial 2 + Trial 3 acceptance criteria, adds risks R11/R12/R13, strengthens anti_prior with KL+descriptor enforcement, ties magnitude axis to perturbation stability, extends trivial-pattern detector temporally. The genuine pre-MVP design freeze.

**vLLM.** High-throughput LLM inference serving library. Used by cross-model evaluator (v0.5+).

**w_R.** The weight on the residual-signal component of Ergon's reward function. Tier-conditioned on Trial 1 outcomes: full at ≥85% accuracy + ≤2% FP on structured-noise; half at ≥85% accuracy + 2-5% FP; zero at <85% accuracy or >5% FP.

**Where to find more**

- v8 spec: `pivot/ergon_learner_proposal_v8.md`
- Foundational architecture: `harmonia/memory/architecture/sigma_kernel.md`, `bottled_serendipity.md`, `discovery_via_rediscovery.md`
- Pivot framing: `pivot/Charon.md`, `pivot/harmoniaD.md`, `pivot/techne.md`, `pivot/ergon.md`
