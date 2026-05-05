# Claude-fresh response #1 — frontier review of attack-paradigm strategy

**Date received:** 2026-04-26
**Model:** Claude (fresh instance, browser session A)
**Prompt:** `whitepapers/attack_strategy_frontier_prompt_20260426.md`
**Document attached:** `whitepapers/attack_strategy_for_frontier_review_20260426.md`
**Constraint compliance:** Full. Tightest §8.7 quantitative table of any response.

---

## 8.1 Validate or refine the 18+3 paradigm list

Keep P19. Keep P21. **Demote P20** — it's not a paradigm, it's a search policy *over* paradigms. Calling MAP-Elites a paradigm in the same slot as Cohomological Obstruction is a category error: the others are *lenses for perceiving a problem*, P20 is *how you traverse the space of lens-applications*. Move it to §7's feedback-loop machinery where it belongs (Maieutēs is already operationally where it lives).

In the freed slot, add **P22 — ML-Saliency-Guided Conjecture**: train a learned predictor on a structured corpus, interpret the predictor's saliency or representation geometry to read off a candidate analytic relationship, then prove that relationship by classical means. This is genuinely distinct from P09 (exhaustive verification), P10 (formal proof), and P21 (corpus stratification). Davies–Juhász–Lackenby–Tomašev (Nature 2021, knot signature ↔ representation-theoretic invariant), AlphaTensor (Nature 2022, new matrix multiplication algorithms), and the AlphaGeometry/AlphaProof line (2024) have all produced *theorems* via this paradigm in the last five years that the existing 18 do not natively express. P22 directly fits the substrate: TOOL_MATH_KNOWLEDGE_GRAPH already encodes the relational structure a graph net would consume, KnotInfo+HFK at 12,965 entries is at exactly the scale where DJLT-style saliency interpretation works, and the result-class is operator-nameable (it's "find a function of invariants A,B,C that predicts D").

## 8.2 Per-paradigm tactical advice

[Highlights — full text in source response:]
- **P10:** Stop trying to formalize results. Build a one-way pipeline that takes any 5/5 battery-passed claim and emits a Lean 4 *blueprint stub* (theorem statement + dependency list) — no proofs.
- **P15:** Ship the unified signature-keyed tensor. Stop building per-region tensors; the cross-region splice is where every other paradigm gets leverage.
- **P21:** Build a one-shot "predicate × corpus → stratified histogram" runner.
- **P22 (new):** Train a small graph net on KnotInfo's 12,965-knot HFK feature set predicting τ from Khovanov+signature; interpret saliency to find the missing analytic relationship. DJLT-replication on existing data, no new infrastructure.

## 8.3 The data gap

**Mathlib4 declaration graph as TT-compressible data.** Mathlib4 is *already* mirrored locally (per §3, "Mathlib4 mirrored locally; LeanDojo + DeepSeek-Prover-V2-7B installable per Batch 4 #80"), but the doc treats it as a Lean-bridge target, not as a *corpus*. This is the miss. Mathlib4 has ~150K declarations as a use-graph; ingested as nodes-and-edges, every theorem becomes a queryable substrate object with an explicit dependency signature.

§2 has invariant data and *problem* data. It has zero machine-readable *theorem* data. P10 is paradigm 10 of 18 with no native data substrate. P18 (operadic/categorical) is operating against a substrate that doesn't contain the very category it's reasoning about — Mathlib4 is exactly that category, encoded.

Bloom-Erdős widens the *problem* attack surface; Mathlib4-as-data widens the *operator* attack surface. The latter is more load-bearing because the bottleneck per the doc's own §6 is "operator implementation completeness."

## 8.4 The Techne gap

**Structural signature canonicalization** (the proposal at `stoa/proposals/2026-04-26-aporia-structural-signature-v1.md`). Stop dithering, ship it. The doc itself names this as the ceiling alongside operator completeness. Without it, no TT bond rank is honestly comparable across regions, no P19 transport is rigorous, no F011 generalization is automated, and NULL_BSWCD's "preserves marginals" guarantee can't extend beyond conductor decile to other invariants.

This dominates a Lean bridge, a SAT wrapper, and even cross-region TT splicing in priority. SAT (REQ-026) is blocking three Batch 9 reports; canonicalization is blocking *every cross-region claim ever*.

## 8.5 The symbolic-library gap

**OPERATOR_RANK_PARITY_NULL_CONTROL** (paired with **PATTERN_RANK_PARITY_LEAK** as its anti-pattern enforcement). Currently NULL_BSWCD@v2 preserves conductor-decile marginals; nothing in the registry preserves analytic-rank parity. This is the single biggest hole because every BSD-adjacent finding is rank-conditional, and the canonical finding F011 — "+46–51% bulk deficit at k=24 across non-CM EC, CM EC, and G2C with USp(4)" — does not state whether the three populations have matched rank-parity distributions. Non-CM EC, CM EC, and G2C have *systematically different* rank-distribution profiles (CM curves over-represent rank 0; G2C populations skew differently from elliptic). Without rank-parity control, the deficit's three-class agreement could be partly a rank-distribution artifact or, more importantly, *masking* a stronger rank-stratified signal.

This would not have been caught by PATTERN_30, PATTERN_NULL_CONSTRAINT_MISMATCH, etc.

## 8.6 Tensor-train preprocessing

(1) **Analytic-rank distribution.** Rank 0 dominates EC populations; without flattening rank before TT compression, bond ranks will report "rank 0 connects to rank 0" as the substrate's deepest structure, which is just the corpus's center of mass. Rank detrending is to BSD-region data what prime detrending is to multiplicative-region data.

(2) **CM / non-CM dichotomy.** CM L-functions follow unitary symmetry; non-CM follow orthogonal/symplectic. A unified tensor that pools them will produce TT bond ranks that conflate two genuinely different bond-rank topologies, and the strongest "bridge" the substrate finds will be the trivial CM ↔ non-CM partition.

(3) **Class-number-1 dominance for number fields.** Of LMFDB's 22M NF, the small-class-number fields are over-studied, over-populated, and over-connected. NF analog of rank-0 EC.

## 8.7 Feedback-loop refinement

| Mandatory battery | Substrate-hours on this problem | Cross-region linkages opened (P19 hits) | Routing |
|---|---|---|---|
| 5/5 | any | any | Promote, harvest as calibration anchor, **switch problem** |
| 4/5 | ≤6h | any | **Same problem**, single operator swap (max 2 swaps total) |
| 3/5 | ≤4h | ≥1 | **Same problem**, refine null and re-run battery |
| 3/5 | ≤4h | 0 | **Switch problem**, route residue to Maieutēs |
| ≤2/5 | any | any | Kill ledger, residue to Maieutēs, **switch problem** |
| any | >6h with no movement to ≥4/5 | — | **Mandatory switch**, regardless of intuition |
| any | any | — | If same Techne gap surfaces ≥2× across distinct attacks → **escalate to Techne, freeze problem** |

## 8.8 One specific problem-paradigm pairing

**Lehmer's conjecture on Mahler measure × P19.** Substrate fit: TOOL_MAHLER_MEASURE forged. Mossinghoff Mahler tables embedded. TOOL_GALOIS_GROUP, TOOL_LLL_REDUCTION, TOOL_HILBERT_CLASS_FIELD, TOOL_KNOT_SHAPE_FIELD all forged. KnotInfo's 12,965 hyperbolic knots have trace fields that share arithmetic structure with Salem splitting fields (Boyd, Smyth, Reid lineage — literature lock-in is pre-loaded). Hyperbolic volume distribution near the Weeks manifold (vol ≈ 0.94) and Mahler measure distribution near Lehmer (M ≈ 1.17628) are both "near-extremal rigidity" phenomena.

[6-hour P19 attack with hour-by-hour breakdown — Reid's commensurability invariants as candidate operator name.]

## 8.9 The question I'm not asking but should be

**What is the substrate's null model for itself?**

The falsification battery requires every claim to be matched against a null. The substrate has no matched null for its own productivity. If a single competent number-theorist with raw LMFDB access ran for 6 months without the 18+3 paradigm taxonomy, the operator-derived partitioning, the TT compression doctrine, or the falsification battery, would the same fraction of "discoveries" survive 5-of-5? F011 is offered as canonical, but you have not shown that F011 was unfindable without the substrate architecture — only that the substrate found it. Without a substrate-level null, the doctrine that distinguishes the substrate from a clever solo workflow is unfalsifiable. This is the substrate-level analog of `feedback_prime_atmosphere`: you have not yet detrended your own contribution from the corpus's natural background productivity.

---

## Aporia scorecard

| Section | Verdict | Notes |
|---|---|---|
| 8.1 | **NEW: P22 ML-Saliency-Guided Conjecture (5th unique replacement)** | DJLT 2021, AlphaTensor 2022, AlphaProof 2024 as evidence. Genuinely outside P09/P10/P21. Sharp argument that result-class is operator-nameable ("find function of A,B,C predicting D"). |
| 8.2 | **STRONGEST per-paradigm pragmatism** | "Build Lean 4 *blueprint stub* pipeline" — no proofs, just dependency list. "Stop building per-region tensors" — most direct ship-the-unified-tensor call. |
| 8.3 | **NEW DATA GAP — Mathlib4 declaration graph** | 5th distinct data gap proposed. Argument that we have invariant data and problem data but ZERO theorem data is sharp. ~150K Mathlib4 declarations as use-graph, already mirrored locally — cost is low. |
| 8.4 | **6/6 CONVERGENCE WITH ALL PRIOR MODELS — ship the canonicalizer** | "Stop dithering, ship it." Both Claude instances + ChatGPT + Gemini + Grok + DeepSeek all point at signature canonicalization as the highest-leverage missing primitive. **This is the strongest convergence in the entire frontier review.** |
| 8.5 | **NEW PATTERN/OPERATOR — RANK_PARITY_LEAK** | F011-direct critique: did F011 control for rank-parity distribution differences across non-CM/CM/G2C? Answer is "the doc doesn't say." This is a sharp, actionable new pattern. **6th distinct pattern proposed across the review.** |
| 8.6 | **3 wells: rank distribution, CM/non-CM, class-number-1** | Some overlap with prior models (CM appeared in DeepSeek's; class-number-1 is Grok-adjacent). Net unique wells across 6 responses now ~12-15. |
| 8.7 | **MOST DETAILED ROUTING TABLE** | Cycle-budgeted with explicit substrate-hour caps. 6h cap is load-bearing for 10-hour session preventing single-problem time-sink. Tool-gap escalation rule (≥2 same Techne gap → escalate, freeze problem) is a substrate-level pattern in its own right. |
| 8.8 | **READY-TO-FIRE seed #5** — Lehmer × P19 | Best substrate-fit argument of any §8.8: Reid commensurability invariants as candidate operator name, Boyd-Smyth-Reid literature pre-loaded, Mahler measure ↔ hyperbolic volume both "near-extremal rigidity" phenomena. |
| 8.9 | **SHARPEST QUESTION OF THE REVIEW** — substrate's null model for itself | "Has F011 been shown to be unfindable without the substrate architecture, or only that the substrate found it?" This is the substrate-level analog of prime-atmosphere detrending. **Demands a real answer.** |
