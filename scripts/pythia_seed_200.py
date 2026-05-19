"""One-shot: seed Pythia's research_queue with 200 substrate-priority prompts.

50 bespoke prompts hand-authored against Prometheus's ~20 active theses
(falsification-routing-first Learner, substrate types A-E, tensor-first,
attack-paradigm refinement, reasoning ladder, Apollo compositional premise,
anti-anchor verification, silent islands / sleeping beauties) +
150 highest-priority unfired entries from
aporia/docs/gemini_research_queue/queue.jsonl.

Run once. Pythia picks them up via next_pending_research as slots open.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import agora_persist
from pythia_daemon import seed_from_default_queue


# Each tuple: (priority, tier, title, prompt_body, substrate_type)
# priority 1=urgent, 2=high, 3=normal. Tier T1=top, T2=substrate, T3=adjacent.
# substrate_type: A=falsification, B=attack-angles, C=strategies, D=step-tagged, E=meta-circuits
BESPOKE_PROMPTS = [
    # === Falsification-routing-first Learner thesis (5) ===
    (1, "T1", "FALS-01: Training LLMs to recognize false math claims",
     "Survey 2025-2026 work on training language models to identify false mathematical claims rather than verify true ones. Datasets, methods, eval benchmarks, comparative architectures. What's the strongest evidence that falsification-first training produces better calibrated reasoning than verification-first? Cite primary papers (arXiv, NeurIPS, ICLR).", "A"),
    (1, "T1", "FALS-02: Retracted-paper benchmarks for math verification",
     "What benchmarks exist (2024-2026) for evaluating ML systems' ability to detect mathematical errors in published-then-retracted papers? Include arXiv withdrawals, RetractionWatch math entries, journal-level retractions. What gaps remain in coverage by domain (NT, AG, CO, AT)?", "A"),
    (1, "T1", "FALS-03: Falsification routing in LLMs — prompting + fine-tuning",
     "Latest techniques for inducing falsification-first behavior in LLMs: contrastive prompting, reflexion, debate, RL from verification signals. Compare effectiveness on math vs general reasoning. What's the strongest empirical evidence for each approach?", "A"),
    (1, "T1", "FALS-04: Synthetic anti-anchor corpus generation",
     "Methods for generating false-but-plausible mathematical claims for training data: counterfactual perturbation, hypothesis softening, citation-form mimicry, prove-by-similarity attacks. What's been tried, what scales, what fails?", "A"),
    (1, "T1", "FALS-05: Claim-graph construction from math literature",
     "Existing tools (2024-2026) for extracting claim graphs from primary mathematical literature: Mathlib4 metadata, NLProlog, ProofNet, Lean-Dojo claim mining. Scalability per million-paper corpora. Open problems in claim normalization across citation styles.", "A"),

    # === Substrate types A-E refinement (5) ===
    (2, "T1", "SUBSTR-01: What makes a top-tier anti-anchor?",
     "Attestation requirements for mathematical anti-anchors (verified-false claims) per top-tier journal editorial standards: Annals, JAMS, Inventiones. What primary-source guarantees are required to call a published claim 'killed'? Compare with Lean Mathlib provenance norms.", "A"),
    (2, "T1", "SUBSTR-02: Attack-angle taxonomy surveys",
     "Existing systematic surveys of 'what people tried before solving X' across mathematics: solved-problem genealogies, Aporia-style breakthrough chain documents in academic literature, post-mortem analyses of decades-long unsolved problems. What classification frameworks have stuck?", "B"),
    (2, "T1", "SUBSTR-03: Pedagogical frameworks for math reasoning",
     "Polya-Lakatos-Tao pedagogical lineage as a reasoning-strategy substrate. What modern (2020-2026) computational instantiations exist? Compare Pólya patterns to recent LLM heuristic libraries (auto-CoT, plan-and-solve, least-to-most). Which patterns transfer to substrate-style verification?", "C"),
    (2, "T1", "SUBSTR-04: Step-by-step proof annotation datasets",
     "Existing datasets of theorem proofs annotated step-by-step with reasoning labels: Mathlib4 tactic traces, AFP step-grading, MiniF2F annotations, ProofWiki structured proofs. Coverage stats by domain. What's needed for reasoning-ladder calibration?", "D"),
    (2, "T1", "SUBSTR-05: Public meta-reasoning circuit corpora",
     "What public corpora of meta-reasoning circuits exist comparable to Apollo's Frame-H gene library output? AlphaEvolve elites, OpenEvolve archives, EvoPrompt circuits, AutoML-Zero programs. Compare size, quality, license, archival accessibility.", "E"),

    # === Tensor-first priority (10) ===
    (1, "T1", "TENS-01: Asymptotic spectrum 2025-2026 state",
     "Latest progress on Strassen-Christandl-Vrana-Zuiddam asymptotic spectrum theory of tensors: new spectral points discovered, open problems, structural results since 2024. Cite arXiv specifically.", "C"),
    (1, "T1", "TENS-02: Border rank LBs beyond apolarity",
     "What lower-bound techniques for border rank of tensors have emerged beyond Buczyńska-Buczyński apolarity since 2023? Landsberg-Michałek extensions, machine-checked bounds, new algebraic-geometric obstructions.", "C"),
    (1, "T1", "TENS-03: Tensor network expressivity classes",
     "Theoretical characterization of which quantum states / functions can be captured by MPS, PEPS, MERA at fixed bond dimension. Latest 2025 results on expressivity gaps and approximation hardness.", "C"),
    (1, "T1", "TENS-04: Salmon problem status",
     "Status of the Salmon problem (defining equations of σ_4(P^3 × P^3 × P^3) in 4×4×4 tensor space). Recent computational attacks, partial results, any 2024-2026 progress.", "C"),
    (1, "T1", "TENS-05: Quantum functional bounds frontier",
     "Christandl-Vrana-Zuiddam 2017 quantum functional bounds: what extensions and refinements have appeared since? Universal points, new monotones, applications to matrix multiplication exponent ω.", "C"),
    (1, "T1", "TENS-06: Slice / partition / analytic / geometric rank dominance",
     "Empirical comparison of slice rank, partition rank, analytic rank, geometric rank across tensor families. Which dominates for cap-set, sum-free sets, multilinear circuit complexity? Recent results.", "C"),
    (1, "T1", "TENS-07: Tensor-train decomposition for ML 2025",
     "Tensor-train decomposition advances in machine learning 2024-2026: compressed transformers, TT-LoRA, MERA-style attention, theoretical guarantees on expressivity vs rank. Open questions on rank-adaptive training.", "C"),
    (1, "T1", "TENS-08: Permanent vs determinant via tensor methods",
     "Latest lower-bound techniques on permanent vs determinant problem (Valiant's conjecture) using tensor decomposition. What 2024-2026 papers attack this via secant varieties, border rank, or tensor networks?", "C"),
    (1, "T1", "TENS-09: Algebraic complexity 2025 tensor frontier",
     "Algebraic complexity theory's tensor-related advances 2025: matrix multiplication ω bounds, depth-3 circuit lower bounds via tensor rank, ACC^0 vs P, tensor PCP. Cite primary literature.", "C"),
    (1, "T1", "TENS-10: Alexander-Hirschowitz extensions",
     "Extensions of the Alexander-Hirschowitz theorem on non-defective secant varieties to higher-degree tensors, Segre-Veronese embeddings, and partially symmetric tensors. Open cases as of 2025-2026.", "C"),

    # === Attack-paradigm refinement (10) ===
    (2, "T1", "PARA-P01: Modularity-lifting 2025",
     "Latest modularity-lifting techniques (2024-2026): extensions beyond GL_2, Calegari-Geraghty-style automorphy, recent Sato-Tate-class proofs. Which open potential-modularity cases are now within reach?", "C"),
    (2, "T1", "PARA-P04: L-function GUE statistics 2025",
     "Random-matrix-theory advances on L-function zero statistics (2024-2026): proven cases of GUE prediction, finite-N corrections, deviations observed empirically. Cite recent arXiv preprints.", "C"),
    (2, "T1", "PARA-P07: Infinite descent in modern AG",
     "Modern applications of infinite-descent technique in algebraic geometry and arithmetic: Faltings-style height descent, Vojta-conjecture progress, recent rational-point bounds via descent (2024-2026).", "C"),
    (2, "T1", "PARA-P12: Uniform bounded heights frontier",
     "Status of the Uniform Boundedness Conjecture for rational points on curves and varieties of higher genus. What progress since Dimitrov-Gao-Habegger 2021? Bounds on heights, on counts.", "C"),
    (2, "T1", "PARA-P15: CP decomposition uniqueness 2025",
     "Kruskal-style uniqueness conditions for CP tensor decomposition: latest refinements, generic uniqueness ranges, computational identifiability tests as of 2024-2026.", "C"),
    (2, "T1", "PARA-P16: Bhargava-style techniques 2025",
     "Bhargava-Shankar-style arithmetic statistics techniques (2024-2026): Selmer-group distributions, average ranks, geometry-of-numbers extensions. New families analyzed.", "C"),
    (2, "T1", "PARA-P18: Infinity-categories in number theory",
     "Recent applications of infinity-categorical methods to number theory (2024-2026): Fargues-Scholze geometrization extensions, derived L-functions, ∞-categorical Iwasawa theory.", "C"),
    (2, "T1", "PARA-P22: Polynomial method on signed graphs since Huang",
     "Extensions of Huang's signed-graph polynomial method (2019) since publication: which sensitivity-style problems have fallen, what generalizations have appeared 2020-2026.", "C"),
    (2, "T1", "PARA-P25: Recent pivotal-negative-result catalog",
     "Catalog of 'surprising' negative results in mathematics 2022-2026 that reoriented their fields (Manolescu-style triangulation falsifications, Tsirelson-style operator-algebra falsifications). Each: claim, who killed, citation.", "C"),
    (2, "T1", "PARA-P30: Tensor networks meet machine learning 2025",
     "Tensor-network methods intersecting machine learning (2024-2026): TN-as-architecture (TN-Bert, MERA-attention), TN-for-compression, TN-PINN. State of the art on expressivity vs trainability.", "C"),

    # === Reasoning ladder calibration (5) ===
    (2, "T1", "LAD-01: R3-R5 transitions in published proofs",
     "Empirical studies (2020-2026) attempting to label reasoning levels (rule-execution, deduction, abstraction, search, counterfactual) across step transitions in published mathematical proofs. Datasets, methodologies, findings.", "D"),
    (2, "T1", "LAD-02: ARC-AGI 2025 saturation",
     "Status of ARC-AGI benchmark 2025-2026: top solvers, scoring methods, saturation rate, criticism of the benchmark (contamination, distribution-shift attacks). What does saturation tell us about R3 abstraction?", "C"),
    (2, "T1", "LAD-03: Causal vs counterfactual eval 2025",
     "Latest benchmarks for evaluating LLM causal vs counterfactual reasoning (2024-2026): CausalGym, CRASS, novel Pearl-tier intervention probes. Which models distinguish observational from interventional?", "C"),
    (2, "T1", "LAD-04: Self-monitoring + error correction in LLMs",
     "Frontier work (2025-2026) on LLM self-monitoring and error correction: Reflexion variants, verifier-loop architectures, formal-proof self-check. Compare empirical gain on math benchmarks.", "C"),
    (2, "T1", "LAD-05: Open-ended conjecture-formation systems compared",
     "Compare existing systems for automated conjecture formation (2024-2026): IRIS, AlphaEvolve, OpenEvolve, AlphaGeometry. Methodology, output quality, evaluation framework, claimed novelties.", "C"),

    # === Apollo compositional premise (5) ===
    (2, "T1", "APO-01: AlphaEvolve / OpenEvolve / CodeEvolve frontier",
     "Detailed comparison of AlphaEvolve (DeepMind 2024), OpenEvolve (open-source), CodeEvolve, and similar LLM-evolutionary program synthesis systems. Architectures, ablation gates, scaling, demonstrated discoveries 2024-2026.", "C"),
    (2, "T1", "APO-02: Compositional generalization 2025 evidence",
     "Empirical work on compositional generalization vs memorization in neural networks 2024-2026: structured-prediction tests, novel-composition benchmarks, scaling-law analyses. What's the strongest evidence for or against compositional generalization in large models?", "C"),
    (2, "T1", "APO-03: NSGA-II vs NSGA-III for many-objective program synthesis",
     "Comparative empirical evidence on NSGA-II vs NSGA-III for program synthesis with >3 objectives (2024-2026). Where does NSGA-II break, what NSGA-III tweaks help, alternatives (MO-CMA-ES, MOEA/D-AWA).", "C"),
    (2, "T1", "APO-04: MAP-Elites quality-diversity at scale 2025",
     "Large-scale MAP-Elites empirical results 2024-2026: archive sizes, illumination quality, niche selection, hybrid QD-RL methods. What scaling trends and failure modes are documented?", "C"),
    (2, "T1", "APO-05: Ablation-gate methodology prior art",
     "Methodologies prior-art for using ablation as an admission gate in compositional / program-synthesis systems (2020-2026): named methods, threshold-selection criteria, comparative effectiveness vs novelty gates.", "C"),

    # === Anti-anchor verification + cross-cutting (5) ===
    (1, "T1", "AA-VERIFY-01: AA-005 through AA-016 re-verification batch",
     "Re-verify registered Prometheus anti-anchors AA-005 through AA-016 against current primary literature (2025-2026). For each, confirm or refute the kill, cite the verifying / falsifying primary source.", "A"),
    (1, "T1", "AA-VERIFY-02: 2025-2026 arXiv withdrawal patterns",
     "Statistical patterns in arXiv mathematics withdrawals 2025-2026: counts per subject category, average time-to-withdrawal, common failure modes (computation error, gap in proof, prior art). Cite a recent withdrawal-tracker.", "A"),
    (1, "T1", "AA-VERIFY-03: Saxl conjecture status mid-2026",
     "Status of Saxl's conjecture (staircase tensor-power positivity) as of mid-2026. Confirm: was Lee 2025 (arXiv:2512.15035) withdrawn? What replaced it? Cite primary preprints.", "A"),
    (1, "T1", "AA-VERIFY-04: Lehmer Mahler measure 2025 progress",
     "Any progress beyond Mahler measure lower bound 1.176280... at the Lehmer polynomial (2024-2026)? New computational searches, new theoretical bounds. Cite specifically.", "A"),
    (1, "T1", "AA-VERIFY-05: Schinzel-Zassenhaus follow-ups",
     "Follow-ups to Dimitrov 2022 (Schinzel-Zassenhaus conjecture proof). Sharper constants, extensions to totally-real case, generalizations to other height functions. Cite 2022-2026 preprints.", "A"),

    # === Silent islands + sleeping beauties (5) ===
    (2, "T1", "ISL-01: OEIS Sleeping Beauty activation 2025-2026",
     "OEIS sequences that gained cross-references / connections between 2024 and 2026: 'sleeping beauty' awakenings. Sample 10 most-cited recent additions, identify the bridge each makes.", "B"),
    (2, "T1", "ISL-02: Knot theory ↔ number theory bridges 2025",
     "Recent (2024-2026) results bridging knot theory and number theory via TQFT, arithmetic topology, or Mazur knot-prime analogies. Cite primary papers, identify which bridges are computable.", "B"),
    (2, "T1", "ISL-03: Genus-2 uniformity status 2025",
     "Status of Bombieri-Lang uniformity for rational points on genus-2 curves as of 2025-2026. Computational results from LMFDB / Bhargava-Skinner-Wei searches. Bounds achieved.", "B"),
    (2, "T1", "ISL-04: Bianchi modular forms 2025 advances",
     "Advances in Bianchi modular forms 2024-2026: new modularity-lifting results over imaginary quadratic fields, computational table extensions, paramodular Bianchi.", "B"),
    (2, "T1", "ISL-05: Fungrim integration with math databases",
     "Status of Fungrim (formula database) integration with other structured mathematical resources (LMFDB, OEIS, Mathlib) as of 2025-2026. API maturity, coverage, downstream uses.", "B"),
]


def main():
    inserted_bespoke = 0
    for prio, tier, title, prompt, substrate_type in BESPOKE_PROMPTS:
        rid = agora_persist.enqueue_research(
            title=title,
            prompt_text=prompt,
            requested_by="Aporia",
            priority=prio,
            tier=tier,
            queue_ref=title.split(":")[0],  # use the BESPOKE-CODE as queue_ref
            target_substrate_type=substrate_type,
            tags={"source": "bespoke_thesis_seed_2026-05-19", "thesis_cluster": title.split("-")[0]},
        )
        if rid:
            inserted_bespoke += 1
    print(f"Seeded {inserted_bespoke} bespoke thesis prompts.")

    inserted_default = seed_from_default_queue(150)
    print(f"Seeded {inserted_default} from default queue.")

    print(f"Total new pending: {inserted_bespoke + inserted_default}")


if __name__ == "__main__":
    main()
