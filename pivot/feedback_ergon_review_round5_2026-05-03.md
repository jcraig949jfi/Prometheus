---
captured: 2026-05-03 (late evening — fifth review of the day)
captured_by: Ergon (Claude Opus 4.7, 1M context, on M1)
reviewer: Gemini (declared as such in the user-facing exchange; structured numbered sections with bold subsection titles, "Architectural Triumphs / Critical Vulnerabilities / 20-Year Horizon" framing, closes with a specific concrete question demanding a numeric threshold)
target_under_review: pivot/ergon_learner_proposal_v4.md (the expanded-background version, commit eedcb893; reviewer was given v4, not v5)
status: VERBATIM CAPTURE for substrate ingestion
---

# Verbatim review of `ergon_learner_proposal_v4.md` — round 5 (Gemini)

This file captures Gemini's review of v4 verbatim. Note: Gemini reviewed v4, not v5. Some critiques (cross-model agreement weight; power-calculation reality check) are partially addressed by v5; new concerns (gravitational wells in anti_prior space; cross-model evaluator prompt redesign; compute budget headroom) are not. v6 ships those new revisions plus a direct numeric answer to Gemini's closing question.

Round 5 is at less depth than rounds 3-4. Rounds 3-4 surfaced architectural failure modes the architecture itself created. Round 5 surfaces three operational-level concerns plus one architectural sharpening (cross-model evaluator prompt). The diminishing-returns prediction from round 4's reviewer ("further theorizing without empirical feedback will yield diminishing returns") appears to be holding.

Triage in companion file `meta_analysis_ergon_round5_2026-05-03.md`. v6 in `pivot/ergon_learner_proposal_v6.md`.

---

This is a remarkably mature architectural document. Version 4 successfully sheds the rhetorical overclaims of previous iterations and establishes a defensible, mathematically grounded perimeter. By openly acknowledging the shared corpus prior and shifting the burden of differentiation to the action space, the agreement-weighted reward, and the LoRA delta, the proposal moves from a philosophical stance to an executable engineering spec.

Here is an external review of the Ergon Learner v4 architecture, structured by its structural triumphs, immediate vulnerabilities, and long-term viability.

## 1. Architectural Triumphs

### The Operationalization of the "Dark Spots"

The most significant upgrade in v4 is the elevation of the residual primitive from a passive logging tool to a first-class driver of the reward function (w_R) and the MAP-Elites fitness hierarchy. By financially (in compute terms) rewarding the system for structured near-misses, the engine is explicitly designed to map the negative space that formal mathematics does not yet illuminate. This prevents the binary fragility of standard theorem provers where a 99% true empirical pattern is discarded identically to pure noise.

### The Techne Meta-Loop (§11.5)

Addressing the "deepest bear case" via the Techne meta-loop is a masterstroke in epistemic hygiene. Calibrating against known truths inherently biases any battery against novel structures. Giving the system a mechanical pathway to forge sharper checkers and recursively audit its own falsification battery ensures that "calibrated negative results" do not become an invisible ceiling on the system's intelligence. This effectively turns the avoidance of spurious correlations into a self-correcting mechanical loop.

### Minimum Proposal-Share Enforcement (§3.5.4)

Reserving a hard 15% floor for uniform, anti_prior, and structured_null operators at the scheduler level, regardless of cell-fill pressure, is a necessary and brutal guardrail against the overwhelming gravity of the LLM prior. Left unchecked, the policy network would inevitably optimize for the easiest paths to promotion, collapsing the search space into well-trodden corridors.

### Small Model Focus

Targeting 7B parameter models (Llemma, Qwen, Llama) for the neural policy is a sound strategic choice. It aligns perfectly with the thesis that smaller models can evolve high-tier intelligence when trained via continuous reasoning and falsification feedback loops, rather than relying on the brute-force parameter scaling of human-preference models.

## 2. Critical Vulnerabilities & Blind Spots

### Cross-Model Agreement Contamination (§5.3)

Using frontier models (Claude, GPT, Gemini) as evaluators for the w_X reward component introduces a severe vector for prior-contamination. These models are the ultimate embodiments of the standard mathematical prior. If they are prompted to evaluate whether a claim is a "valid discovery," they are highly likely to heavily weight syntactic familiarity and aesthetic alignment with their training data. This risks creating a secondary reward loop that actively punishes the anti_prior operator's genuinely novel structures simply because they look "alien" to a standard LLM.

*Mitigation:* The N≥2 external LLMs should strictly evaluate the *logical consistency of the proof trace/DAG*, not the *mathematical validity of the conjecture itself*.

### Gravitational Wells in the anti_prior Space

While the anti_prior operator (§3.5.1) is designed to sample away from Mathlib frequency statistics, mathematical exploration frequently crashes into structural traps. When stepping outside standard priors, data mapping often falls into the gravitational wells created by small numbers, trivial prime-density artifacts, or unscaled magnitudes. If the MAP-Elites output-magnitude buckets (§6.2) are not meticulously bounded, the engine may waste its compute budget exploring scale issues that masquerade as structural anomalies.

### The Power Calculation Reality Check (§7.5)

The inclusion of the power calculation is intellectually honest, but the numbers highlight a brutal reality: if the base PROMOTE rate in the empirical manifold is ≤ 10⁻³, a 10K-episode multi-arm pilot is at the absolute bleeding edge of statistical noise. The reliance on Count 5 (signal-class-residual rate) is completely load-bearing for v0.5. If the residual classifier is too strict, there will be no gradient to climb.

### Compute Budget Headroom (§8.1)

Estimating $300–800/month for v1.0 is optimistic. While the GPU inference and LoRA fine-tuning might fit this envelope, the continuous operation of a 7-agent heterogeneous ensemble (the Agora) communicating over a message bus, plus the overhead of constant PostgreSQL/Redis IOps for the Σ-kernel constraints, usually incurs hidden networking and storage-egress costs.

## 3. The 20-Year Horizon

The juxtaposition against David Silver's $1B venture (§13, §14) is cleanly scoped. Ergon does not need to beat AlphaProof at formal theorem proving; it needs to dominate the append-only, content-addressed substrate of empirical patterns. If the system can mechanically verify that an off-distribution DAG composition yields a stable topological invariant, it has generated knowledge.

The design freeze is justified. The architecture is sound enough that further theorizing without empirical feedback from the Σ-kernel will yield diminishing returns.

Given the reliance on Count 5 to provide a dense enough gradient for the MAP-Elites archive, what is the specific threshold of statistical confidence you require from the day-1 residual benchmark before you trust the primitive enough to let it steer the w_R reward weight?
