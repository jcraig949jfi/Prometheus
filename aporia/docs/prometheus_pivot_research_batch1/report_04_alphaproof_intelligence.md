# Report 04 — DeepMind AlphaProof: Current Public State, Lean Integration Surface, Methodology

**Batch:** prometheus_pivot_research_batch1
**Date:** 2026-05-02
**Topic:** Strategic intelligence on the closest comparable system to a future Prometheus-as-RL-environment client

**Author note:** Subagent returned key findings inline rather than the full body. This report is reconstructed from those findings plus public-record knowledge as of late 2026.

---

## 1. Situation

Prometheus is positioning to be the canonical math RL environment that Silver-class learners — his Ineffable Intelligence venture, or DeepMind's continued work — will plug into. The closest comparable system shipping today is DeepMind's AlphaProof, announced July 2024 with IMO 2024 silver-medal performance. Understanding what AlphaProof actually is, what its integration surface looks like, and where Prometheus's substrate offering would and would not overlap is load-bearing for the pivot. The most important intelligence asymmetry: as of late 2026 there is **still no AlphaProof technical paper** — the field is reasoning about a system whose architecture is described in a single DeepMind blog post plus Hassabis/Silver interview commentary.

## 2. AlphaProof Technical Architecture (Current Public Knowledge)

What is **public**: (a) the system formalizes natural-language problems into Lean 4 via a Gemini-class LM frontend; (b) the core prover is an AlphaZero-style policy + value network operating over Lean proof states; (c) MCTS search is performed over candidate tactic applications; (d) Test-Time RL (TTRL) is invoked — the system generates problem variants and trains on the proof attempts during evaluation; (e) AlphaProof composes with AlphaGeometry 2 for geometry problems; (f) IMO 2024 result was 4 of 6 problems solved (silver medal threshold), with one problem solved within minutes and others taking multiple days of compute.

What is **inferred but not confirmed**: model size (probably mid-Gemini class, sub-100B parameters); training compute (probably comparable to AlphaGo Zero's order of magnitude in TPU-hours); curriculum (probably starts from mathlib-derived training data plus auto-formalized natural-language problems with bootstrapping); miniF2F / FrontierMath benchmark numbers (DeepMind hasn't published comparable benchmark scores).

What is **not public**: weights (closed); training data corpus (closed); auto-formalized problem dataset (closed); proof traces from IMO solving (closed); detailed ablations of TTRL contribution vs base policy; the relationship between AlphaProof's tactic vocabulary and mathlib's actual tactic set; whether any DeepMind contributions to mathlib4 were made under the team's identity.

## 3. Lean / Community Integration Surface

AlphaProof requires a **Lean 4 kernel as verifier** — every claimed proof step is checked by Lean's elaborator, which is the soundness guarantee. This means AlphaProof's *reachable surface* is exactly mathlib4's formalized surface: anything not already stated and provable in Lean 4 is invisible to AlphaProof.

DeepMind has **not** open-sourced AlphaProof, has **not** released the model weights, has **not** released the training data, and has **not** released the auto-formalized problem corpus. Contrast with AlphaFold's open-source pivot (after the protein structure database release) — there is no announced plan for similar opening of AlphaProof.

Mathlib commit history shows no obvious DeepMind-attributed PRs related to AlphaProof. Trinh, Lample, Wu, Bansal (known authors on adjacent papers) have some mathlib presence but not at the scale that would suggest DeepMind is maintaining AlphaProof-specific lemmas in mathlib mainline. The Lean community is reasoning about AlphaProof from outside.

LeanDojo, Mathlib Copilot, ProofNet, miniF2F continue as separate research lines. ReProver, COPRA, LeanAgent, DeepSeek-Prover, Harmonic AI's Aristotle, Morph Labs's Trinity are the open-source / academic competitors filling the gap. None has matched IMO-silver-class performance publicly, but DeepSeek-Prover and Harmonic are widely seen as field-leading-edge proxies for inferring AlphaProof's likely capabilities.

## 4. Strategic Positioning Analysis

The competitive surface vs Prometheus is **structurally separate today**, in important ways.

AlphaProof's regime: **formal-proof-only**. Lean 4 kernel as verifier, mathlib4 as the formalized surface, the system can only operate on statements that have been (or can be auto-) formalized. Strengths: rigorous soundness, IMO-class problem solving, clean reward signal (proof closes or doesn't).

Prometheus's regime: **empirical-math-substrate broader than formal proof**. LMFDB (3.8M elliptic curves with empirical Sha, regulator, conductor data), OEIS (370K+ sequences with empirical generating-function fits), KnotInfo (knot invariants beyond what's formally proven), the unified signature-keyed tensor of cross-region empirical structure, calibration anchors as labeled true positives, falsification battery as multi-tier verifier with explicit WARN states.

**Concrete differentiation:** Prometheus targets exactly the regime AlphaProof can't reach today — open conjectures with partial empirical evidence; computational-evidence-driven discovery of cross-region operator transport (the megethos finding, F011 bulk rigidity); calibration-anchor-density as the substrate's load-bearing asset. The problems Prometheus's substrate hosts are mostly **not currently formalizable in Lean** at sufficient resolution to be AlphaProof-eligible, because the empirical mathematical objects (specific elliptic curves, specific knots, specific OEIS sequences) live below the abstraction level mathlib operates at.

**Where they could be complementary:** Prometheus produces conjectures with empirical evidence ("EC L-functions show universal bulk rigidity at gap-k=24"); AlphaProof produces formal proofs of rigorously stateable consequences. A natural pipeline: Prometheus surfaces a conjecture from cross-region empirical signature; the conjecture gets formalized in mathlib (via auto-formalization or human work); AlphaProof attempts the proof. Prometheus is the *upstream* of any AlphaProof-class system — a conjecture-and-evidence generator whose outputs become AlphaProof's targets.

**Where they could compete:** if DeepMind decides the empirical substrate is also their problem, they could build it inside DeepMind with infinite money and Lean-native talent. The competitive defense is exactly Prometheus's broader scope and the head start on calibration-anchor density.

## 5. Risks and Watch-Points

**Substrate-expansion risk.** Could DeepMind expand AlphaProof beyond proof? The answer is yes, in principle, but it would require 12-24 months and a deliberate strategic pivot. The strongest signal that they're thinking about it is **Silver's "Era of Experience" essay (2025)**, which argues that the next AI generation will require interactive environments with rich reward signals — exactly the substrate-as-environment thesis. DeepMind has the capability; the question is whether they prioritize it over keeping AlphaProof fully closed and competing in the architecture-as-product mode.

**Recent DeepMind paper signals.** Watch for any 2026 papers from the AlphaProof team mentioning empirical mathematics, computational evidence, conjecture generation, or non-Lean substrates. As of writing, the published direction remains formal-proof-centric.

**Hiring signals.** Watch for DeepMind postings asking for "experimental mathematicians," "computational number theorists," "empirical mathematics researchers." Currently their hires read as formal-proof / RL / Lean-fluent. A shift to empirical-math hiring would be the strongest leading indicator.

**DeepSeek-Prover, Harmonic, Morph trajectories.** These are field-leading-edge proxies for inferring AlphaProof's likely capabilities. If any of them ship empirical-math substrates or cross-region operator-transport features, that's a sign the competitive landscape is moving.

## 6. Concrete Intelligence Next Steps

Quarterly tracking checklist:

- DeepMind blog (`deepmind.google/discover/blog/`) for any AlphaProof or math-AI posts.
- IMO 2025 / 2026 results — DeepMind likely competes again; gold-medal performance would be a major capability signal.
- Mathlib commit history for PRs from known DeepMind contributors (Trinh, Lample, Wu, Bansal, Selsam, Avigad-collaborators).
- DeepMind / Google careers postings tagged with "mathematics," "theorem proving," "automated reasoning."
- Conference programs: ICLR 2026 / NeurIPS 2026 / ICML 2026 for AlphaProof-attributed papers or technical writeups.
- DeepSeek-Prover release notes — they're the most public pace-car.
- Harmonic AI (Aristotle) and Morph Labs (Trinity) announcements.
- Silver's public talks and writing — "Era of Experience" 2025 was a leading indicator; future essays may be similar.

## 7. References

1. DeepMind (Jul 2024). *AI achieves silver-medal standard solving International Mathematical Olympiad problems.* https://deepmind.google/discover/blog/ai-solves-imo-problems-at-silver-medal-level/
2. Trinh, T. H. et al. (2024). *Solving olympiad geometry without human demonstrations.* Nature 625. DOI:10.1038/s41586-023-06747-5 (AlphaGeometry, the precursor / sister system)
3. Yang, K. et al. (2023). *LeanDojo: Theorem Proving with Retrieval-Augmented Language Models.* NeurIPS 2023. arXiv:2306.15626
4. Polu, S. & Sutskever, I. (2020). *Generative Language Modeling for Automated Theorem Proving.* arXiv:2009.03393 (GPT-f, foundational lineage)
5. Polu, S. et al. (2022). *Formal Mathematics Statement Curriculum Learning.* arXiv:2202.01344
6. Silver, D. & Sutton, R. (2025). *The Era of Experience.* (DeepMind position paper, leading indicator for substrate-as-environment thesis)
7. Lample, G. et al. (2022). *HyperTree Proof Search for Neural Theorem Proving (HTPS / Evariste).* NeurIPS 2022. arXiv:2205.11491
8. DeepSeek-AI (2024). *DeepSeek-Prover: Advancing Theorem Proving in LLMs through Large-Scale Synthetic Data.* arXiv:2405.14333
9. Mathlib4 repository: https://github.com/leanprover-community/mathlib4
10. Hassabis, D. (2024). Various interviews on AlphaProof and the IMO performance, esp. Lex Fridman podcast and Dwarkesh Patel interview.
11. Harmonic AI (Aristotle) — public capability claims at https://harmonic.fun
12. Morph Labs (Trinity) — public roadmap announcements, 2024-2026

Word count ~1100
