# Prometheus Pivot Research — Batch 1 Index

**Date:** 2026-05-02
**Status:** Complete (20/20 reports saved)
**Author:** Aporia
**Trigger:** James asked for 20 deep-research topics informing the Silver-thesis pivot, fired 3 at a time.
**Companions:** `pivot/aporia.md`, `pivot/Charon.md`, `pivot/harmoniaD.md`, `pivot/techne.md`, `aporia/docs/prometheus_pivot_research_batch1_seeds.md`.

**Local-only note:** This directory and its contents live under `aporia/docs/` which is gitignored (matches the policy applied to `deep_research_batch1..10/`). The reports are durable on disk but not in git. The session journal at `roles/Aporia/SESSION_JOURNAL_20260502.md` and the pivot doc at `pivot/aporia.md` are tracked and committed as the canonical reference handles into this work.

---

## Reports

### Substrate-as-environment engineering

- **[01](report_01_gymnasium_env_design.md)** — Gymnasium env design patterns for symbolic-reasoning RL. Recommends discrete typed `op_id` action space, two-level `(op_family, callable)` factorization (AlphaGeometry pattern), graph observation, shaped reward via intermediate falsification gates, MCTS-compatible `env.clone()` API, DreamCoder-style `env.promote_skill()` hook, permutation-null reward sanity check.
- **[02](report_02_reward_design_partial_verifiers.md)** — Reward design for partially-verifiable claims. Decompose GATE into `(verdict, per_falsifier_score, rationale_embedding)`; asymmetric cost `w_BLOCK / w_PROMOTE ≈ 3-5`; PATTERN_30 as hard constitutional penalty; held-out F11 tripwire; phase-in shaping in three stages.
- **[05](report_05_action_space_typed_symbolic.md)** — Action space design (Lean / Coq / Wolfram / AlphaProof / AlphaGeometry / DreamCoder comparison). Recommends Option C: substrate-resident slots + explicit `MINT` op for new values. Concrete Gymnasium `action_space` spec.
- **[06](report_06_state_representation_graph.md)** — State representation. PyTorch Geometric `HeteroData` with node types `{claim, symbol, evidence, op_application, calibration_anchor, aporia}`. k-hop NeighborLoader, contrastive pretraining on existing kills, persistent embedding table keyed by hash.
- **[07](report_07_provenance_cost_patterns.md)** — Provenance + cost annotation. Bazel action-graph + Nix purity + Datomic temporal indexing + cost-of-cost provenance. Concrete schema extensions for `Symbol`, `op_application`, `Claim`, new `CostRecord` type.
- **[11](report_11_append_only_substrates.md)** — Append-only collaborative substrates. CIDs as identity, provenance-DAG as merge mechanism, capability tokens as authorization, per-agent append-streams with Lamport ordering, IPFS-style pinning policy. Concrete Redis-Streams migration plan.
- **[14](report_14_linear_capability_tokens.md)** — Linear capability tokens / object-capability security. Biscuit-style attenuated capabilities + Macaroon caveats, confused-deputy prevention via pass-by-reference, short TTL + rotation. Concrete `SigmaCapability` schema.
- **[19](report_19_tensor_decomposition_substrates.md)** — Tensor decomposition for symbolic substrates. TT first (gauge-fixed bond ranks, TT-cross sampling), then HT for transport detection, then hypergraph spectral for paradigm coupling. Mandatory prime-detrending and permutation-null gates before any "low bond rank" claim.

### Calibration corpus expansion

- **[03](report_03_bloom_erdos_ingestion.md)** — Bloom-Erdős ingestion architecture. **Major finding:** `b-mehta/erdos-problems` GitHub mirror bypasses Cloudflare entirely, CC-BY licensed. Two-layer paradigm tagging with `llm_proposed → verified` status field. 7-day execution plan.
- **[08](report_08_mathnet_ingestion.md)** — MathNet ingestion. **Major finding:** `ShadenA/MathNet` on HuggingFace, CC-BY 4.0 with national-copyright override clause. Six-stage pipeline. **REQ-002 collision warning** — existing `techne/queue/requests.jsonl` REQ-002 is fulfilled (TOOL_ALEXANDER_POLYNOMIAL); rename new request to `REQ-MATHNET-001`. Multi-language paradigm extraction via translate+LLM+weak-supervision ensemble.
- **[09](report_09_calibration_corpus_landscape.md)** — Calibration corpus landscape. Top-5 ranked: miniF2F → PutnamBench → ProofNet → LeanDojo/Mathlib4 → NaturalProofs. FrontierMath gated; OpenWebMath/MathPile firewalled to pretrain track only. Target N ≥ 10⁵ verified anchors by end of Phase 1.
- **[13](report_13_paradigm_tagging_methodology.md)** — Solution-paradigm tagging methodology. Snorkel-style weak supervision + LLM ensemble with cross-method agreement + Aporia hand-review queue + held-out evaluation. Gate: macro-F1 ≥ 0.75 and ECE ≤ 0.10 before any tag flows to RL training.

### Competitive intelligence

- **[04](report_04_alphaproof_intelligence.md)** — DeepMind AlphaProof current state. **Key intelligence asymmetry:** no AlphaProof technical paper exists; only the July 2024 blog post + interviews. Fully closed (no weights, no API, no proof corpus). Structural separation from Prometheus is clean today (Lean-bounded vs broader empirical substrate).
- **[10](report_10_oss_math_substrate_landscape.md)** — OSS math substrate competitive landscape. The wedge is real and uncontested — no entry ships a signature-keyed operator-transport tensor with falsification + calibration layers. Highest-probability competitive risk: Mathlib-side empirical extension. Three-verb SDK (`lookup` / `transport` / `falsify`) is minimum shippable surface.
- **[20](report_20_silver_ineffable_intelligence.md)** — Silver / Ineffable Intelligence methodology intel. Inferred MuZero-class architecture; first-target domain probably mathematics; needs autoformalization beyond Lean's surface (substrate gap Prometheus fills); 12-18 month time-to-first-demo. **Position as complement, not competitor — Common Crawl analogy.**

### Multi-agent coordination

- **[12](report_12_maieutes_weak_signal_incubator.md)** — Maieutēs design. Hedge-fund research/production split is the closest precedent. **Track:A | track:B schema field with CI-enforced exclusion is single most important mechanism.** MAP-Elites cell structure, kill-ledger → auto-fork hook, periodic graduation review. Five concrete first-implementation steps.

### High-leverage math content

- **[15](report_15_verifier_rich_domains.md)** — Verifier-rich math domains catalog. Tier-1 (gold verifier): Lean/Mathlib, Metamath, OEIS, GAP small-groups, KnotInfo, SAT/SMT, LMFDB exact-arithmetic. Tier-2 (partial): LMFDB numerical, Sato-Tate moments, BSD ranks. Tier-3 (verifier-adjacent): essay proofs, physics, foundations — exploration-only.
- **[16](report_16_operator_transport_catalog.md)** — Cross-domain operator transport benchmarks. Ten canonical anchors: modularity, Langlands transfer, Sato-Tate, Katz-Sarnak, monstrous moonshine, Selberg trace, Riemann-Roch, Gauss-Bonnet, Atiyah-Singer, mirror symmetry. Frontier candidates: geometric Langlands, p-adic Langlands, motivic conjectures, volume conjecture. Top-5 ingest priority specified.
- **[17](report_17_higher_genus_ag_corpora.md)** — Higher-genus AG computational corpora. Ingest priority: BSSVY g=3 hyperelliptic L-functions → Costa-Mascot-Sijsling-Voight g=3 endomorphism certificates → paramodular wt2/wt3 → Bianchi BMF + Hilbert HMF. **Costa-MSV g=3 End-rings are the only gold-standard higher-genus corpus.**
- **[18](report_18_falsification_battery_design.md)** — Falsification battery design via replication-crisis lessons. Battery v11 priority: per-claim preregistration registry + multiverse operator + TRAIN/TEST anchor split + forking-paths audit + red-team adversarial agent (KPI = kills/week, reporting to Pronoia).

---

## Cross-batch convergent recommendations

Five themes appear in multiple reports as load-bearing:

1. **Mnemosyne ingest is the single highest-leverage bottleneck.** Bloom-Erdős (#3) and MathNet (#8) and miniF2F (#9 first pick) together multiply calibration density 4-5 orders of magnitude. All three have permissive licenses and clean ingest paths.

2. **The Σ-kernel needs DISTILL/COMPOSE before anything else compounds.** Reports #1, #2, #5, #7, #11, #14, #19 all assume DISTILL exists and reference it as the operator that converts the registry into a language. Without it, every analysis script is Python-around-the-kernel rather than kernel-program.

3. **Content-addressed provenance + capability tokens + temporal indexing is the right architecture spine.** Reports #7, #11, #14 converge on Bazel + Nix + Datomic + Biscuit pattern composition.

4. **TRAIN/TEST anchor split + multiverse analysis + red-team agent are the single biggest battery upgrade.** Reports #2, #18 both call for these; the replication-crisis literature is mature and Prometheus has been operating without it.

5. **Position as complement to Silver/Ineffable, not competitor.** Reports #10, #20 converge: Common Crawl is the analogy. The substrate is the *open* asset closed labs train against. Ship the public read-only dump + three-verb SDK before Ineffable demos.

---

## Action items surfaced

Direct REQ-tier items added to the recommended-next-steps queue:

- **REQ-001** Bloom-Erdős git-mirror ingest (Mnemosyne, this week per #3)
- **REQ-MATHNET-001** MathNet HF ingest (Mnemosyne, post-Bloom; rename per #8 ID-collision finding)
- **REQ-003** miniF2F ingest (Mnemosyne, after Bloom + MathNet, per #9)
- **REQ-004** PutnamBench ingest (per #9)
- **REQ-005** ProofNet ingest (per #9)
- **REQ-006** LeanDojo / Mathlib extraction (per #9)
- **REQ-007** Frontier-eval gateway via Epoch AI (per #9)
- **Σ-kernel DISTILL opcode** (per #1, #5, #7, #19)
- **Σ-kernel COMPOSE opcode** (per #1, #5, #19)
- **Battery v11 preregistration registry** (per #2, #18)
- **Battery v11 multiverse operator** (per #18)
- **Maieutēs `track:A|B` schema + CI firewall** (per #12)
- **Public substrate read-only HTTP API + Parquet dump** (per #10)
- **`prometheus-py` SDK with `lookup` / `transport` / `falsify` verbs** (per #10)

---

## Stats

- 20 reports
- ~22,000 words of strategic research
- ~280 citations across 20 distinct domains
- 5 fronts: substrate engineering, corpus expansion, competitive intel, multi-agent coordination, math content
- All reports follow 6-section structure (Situation, State of the art, Patterns, Anti-patterns / Failure modes, Concrete next steps, References)

---

*Aporia, 2026-05-02. Companion to `pivot/aporia.md`. Reports stay local per `aporia/docs/` gitignore policy; this index + session journal in `roles/Aporia/SESSION_JOURNAL_20260502.md` are the tracked reference handles.*
