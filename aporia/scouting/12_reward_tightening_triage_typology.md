# Scout #12 — Reward tightening + candidate-triage typology

**Tier:** T2 (methodology research, ~1500 words)
**Front:** Reward shaping + candidate classification (env / battery / catalog axis)
**Cost:** ~½ day Aporia validation; ~2 days Techne implementation
**Techne's framing (commit f76d3974):** *"shaped reward + wider alphabet; structural ceiling confirmed."* Triple #3 fixed the algorithm, not the ceiling.
**Status:** Drafted. Pairs with Scout #5 (HITL triage) and Scout #2/#11 (catalog widening). Together they form the **understand-the-failure-mode** wing while #2/#11 are the **expand-the-input** wing.

---

## 1. Situation (~150 words)

`discovery_env` currently uses a **binary terminal reward**: `+100` if the candidate polynomial hashes to a known catalog entry, `0` otherwise. Three independent algorithm changes (REINFORCE → PPO → shaped REINFORCE; original alphabet → wider alphabet; per-Scout-#7 logic) all hit the same PROMOTE-rate ceiling. Per Techne's confirmation, the bottleneck is now in the env / battery / catalog combination, not the policy.

What's needed:

1. A **continuous reward signal** that scores candidates on a `discovery_likelihood` axis without introducing new gameable surfaces.
2. **Typed classification** of the SHADOW_CATALOG: today it accumulates as an undifferentiated pile, throwing away the very information the policy needs to learn from. The 5-class typology proposed in Scout #5 (`numerical_artifact | catalog_omission | known_in_noncanonical_form | adjacency_extension | genuine_novelty`) needs decision rules, base-rate estimates, and a recommendation on hierarchy/exclusivity before it becomes a substrate symbol kind.

This scout researches both moves against analogous systems (AlphaProof, CodeRL, OEIS submission triage, Galaxy Zoo, HTS hit-confirmation) and returns concrete recommendations.

---

## 2. State of the art on reward-shaping + triage in sparse-reward symbolic discovery (~400 words)

**AlphaProof's intermediate-reward design.** Per Aporia Pivot Research Report 4 (and reconstructed from the DeepMind blog plus Hassabis interviews), AlphaProof uses an AlphaZero-style value+policy network whose **terminal** signal is QED/no-QED but whose **action-level** signal is a "tactic plausibility" score from a smaller LM acting as auxiliary critic. The two-tier stack is the published anti-hacking pattern: the policy can game the small LM only by producing tactics that the **Lean kernel** then verifies — the kernel is the un-gameable backstop, the LM is the dense gradient. The published-but-not-papered detail is that DeepMind's TTRL (test-time RL) generates *problem variants* and trains on the variants' proof attempts, which provides a curriculum that re-grounds the auxiliary critic against fresh ground truth on each evaluation.

**Davies et al. (DeepMind, Nature 2021, "Advancing mathematics by guiding human intuition with AI").** The published pipeline is: (1) train a model to predict invariant Y from features X, (2) use **gradient saliency** to identify which features X most influence the prediction, (3) inspect the high-saliency features and ask whether their relationship to Y suggests a conjecture. The recommended pattern is *not* to deploy the trained model as an oracle but to use **attribution as a hypothesis-generator** that mathematicians then prove. For Prometheus this maps to: don't treat shaped reward as truth, treat it as attribution that points at where the analyst should look.

**HumanEval-RL / CodeRL (Le et al. 2022).** Per-line credit assignment from execution traces. The methodology converts a binary `tests pass / fail` into shaped intermediate signal by training a critic network to predict per-line probability-of-eventual-pass from partial execution traces. The reward decomposition is: terminal {compile, public-test pass, private-test pass}, intermediate {per-line critic value}, with the critic regressed against eventual outcome. **Direct template for discovery_env.**

**OEIS submission-triage workflow.** Sloane's editor process (per OEIS docs at oeis.org/wiki/Editing) has multi-tier review: format check → content check → original-research check → integration. Reject rates are not formally published but editorial commentary suggests **30-50% of submissions are rejected or returned for revision**, mostly format/duplicate issues. Median human-time-per-decision is on the order of minutes for trivial cases, hours for ambiguous mathematical-content cases. The typology in practice is roughly: `duplicate | format_violation | not_a_sequence | already_present_under_different_name | original_research`.

**Galaxy Zoo (Lintott et al. 2008+, MNRAS).** The morphological typology was validated against Schawinski/Bamford expert classifications with **inter-rater agreement ~80%** for clean morphologies, ~50% for edge cases. Failure modes at scale: (a) anchoring on early classifications (mitigated by random-order presentation), (b) class imbalance pulling marginal cases toward majority (mitigated by class-balanced active learning), (c) "task drift" — meaning of categories shifting as raters accumulate experience.

**HTS hit-confirmation (Inglese et al. 2007, Nature Chemical Biology).** The standard chemistry/biology pipeline: primary screen (high false-positive rate accepted) → orthogonal-assay confirmation → dose-response → counter-screen (rule out off-target). Industry false-positive rate at primary screen is **30-50%**; after orthogonal confirmation it falls to **~5%**; after counter-screen, **<1%**. The doctrine is **calibrate the false-positive budget per stage** rather than expecting any single stage to be clean.

---

## 3. Recommended candidate-classification typology (~300 words)

Validate-and-refine the 5-class proposal:

| Class | Decision rule (mechanical) | Analogous system | Expected base rate (of SHADOW_CATALOG) |
|---|---|---|---|
| `numerical_artifact` | Mahler measure recomputed at 2× working precision shifts by > tolerance; OR `irreducibility` flag flips under exact-arithmetic recheck; OR coefficient norm exceeds env's allowed range. | HTS primary-screen artifact (precipitation, fluorescence interference). | **40-60%** (analogous to HTS primary-screen FPs). |
| `catalog_omission` | Polynomial fingerprint hashes to a record in any **extended** catalog (LMFDB BMF, OEIS A073011 / A002965 / Salem-related, Mossinghoff supplement, arXiv-mined per Scout #2) not in the original 5. | OEIS "duplicate-under-different-name" rejections. | **15-25%** (per Scout #2 finding: catalog landscape is genuinely thin beyond Mossinghoff). |
| `known_in_noncanonical_form` | Mahler-measure-preserving canonicalization (`f(x^k)`, palindrome reversal, root-of-unity multiplication, sign flip) lands the polynomial on a known catalog entry. **Scout #6 noted `f(x^k)` is unhandled** — adding it is prerequisite. | OEIS "duplicate after b-file rescaling." | **10-20%**. |
| `adjacency_extension` | Polynomial differs from a known entry by **one** parameterized operation: degree-shift by ±1, single-coefficient perturbation, twist by a small Dirichlet character, root-of-unity multiplication of *one* root. | Chemistry "analog series" — same scaffold, decorated. | **10-20%**. |
| `genuine_novelty` | None of the above fire. **Default class only after the four mechanical filters have excluded it.** | HTS confirmed hit after counter-screen. | **<5%**, likely **<1%**. |

**Hierarchy vs flat.** Recommend **flat with priority ordering** (artifact → omission → noncanonical → adjacency → novelty), where each rule is checked in order and the first match wins. `genuine_novelty` does not subdivide at v1 — premature subdivision is a Sphinx-category trap (per `feedback_operator_precedents.md`). Subdivide only after >50 confirmed `genuine_novelty` instances accumulate.

**Exclusive vs labels.** Recommend **exclusive at the typology level**, with **secondary labels** allowed in metadata (e.g., a `genuine_novelty` may *also* carry the label `adjacency_extension_to:<known>` for narrative purposes; the primary class drives the reward, the labels drive downstream review). This matches Galaxy Zoo's "primary morphology + decoration tags" pattern.

---

## 4. Reward-shaping recommendations specific to discovery_env (~300 words)

**Replace the binary reward.** Concrete proposal for `r(candidate)`:

```
r = w_class * class_score(typology)
  + w_shape  * shaping_terms
  - w_caveat * caveat_penalty
```

where:

```
class_score = {
    numerical_artifact:        -1.0,     # actively penalized — they pollute SHADOW_CATALOG
    catalog_omission:          +0.2,     # small positive — useful calibration but not novel
    known_in_noncanonical_form:+0.4,     # modest — system did real canonicalization work
    adjacency_extension:       +1.0,     # meaningful — surfaces neighborhood structure
    genuine_novelty:          +10.0,     # rare; the optimization target
}
```

Multipliers chosen so that **a single `genuine_novelty` outweighs ten `adjacency_extension`s**, which matches the asymmetric-cost doctrine from Pivot Report 02 §3 (`w_BLOCK / w_PROMOTE ≈ 3-5`) inverted for the positive direction.

**Where to attach.** Keep the **terminal** reward as the primary (per AlphaProof / CodeRL pattern: terminal is un-gameable, intermediate is the dense-gradient auxiliary). Add **per-step intermediate** signal only as small bonuses for: (a) generating a polynomial that survives the irreducibility check (+0.05), (b) generating a polynomial whose Mahler measure lands inside the canonical Lehmer band [1.001, 1.18] (+0.10). These are anti-collapse anchors, not the optimization target.

**Reward-hacking failure modes after [1.001, 1.18] restriction.** Ergon's catch (any M ∈ [1, 5)) is closed; the next gameable surfaces are: (1) **degree-collapse** (agent finds a tiny set of low-degree polynomials in the band and reuses them) — mitigation: novelty-distance penalty per Pivot Report 02 §3; (2) **canonicalization-arbitrage** (agent generates trivial palindromes of known entries to farm `known_in_noncanonical_form`'s +0.4) — mitigation: cap per-episode reward from non-novel classes; (3) **classifier-blind-spot** (agent finds polynomials that the typology decision rules can't classify, defaulting to `genuine_novelty`) — mitigation: a sixth class `unclassifiable` with reward `0`, never `+10`.

**Caveat-as-metadata pattern.** Borrow from ChatGPT external commentary: each reward carries a `caveat_vector` (e.g., `precision_low`, `catalog_partial`, `null_thin`). Downstream RL gradient inherits the caveats; if the per-episode caveat magnitude exceeds a threshold, the reward is downweighted by a sigmoid `1/(1+exp(caveats - threshold))`. This is the **substrate-side** version of the WARN verdict from Pivot Report 02.

**Per-class differentiation magnitude.** The 10× ratio between `genuine_novelty` and `adjacency_extension` is the single most load-bearing tunable. Start at 10×; if PROMOTE rate stays zero after 10K episodes, raise to 20×; if PROMOTE rate becomes >5% (suspicious for true novelty), lower to 5× and re-validate triage.

---

## 5. Anti-patterns (~150 words)

- **Single-class typology** ("found / didn't find") collapses the information downstream learning needs. The point of the 5-class split is that the policy gradient sees *different* signals for *different* failure modes; binary reward sees only the failure.
- **Reward shaping that introduces new gameable surfaces.** Per Skalse et al. (2022), every shaping component is a Goodhart-vulnerable proxy. The defense is the `unclassifiable` sixth class plus a held-out falsifier (Scout #6's red-team panel) that the policy never sees during training.
- **Triage that's too slow.** Per Scout #5, 100K episodes producing 1K SHADOW entries at 1 minute/triage = 16 hours — already beyond Aporia's daily budget. Decision rules **must** be mechanically decidable so a script does the bulk; Aporia's role is calibration on the first ~50 cases and adjudication of disagreements thereafter.
- **Typology classes that aren't mechanically decidable.** Same failure mode as the residual primitive's stopping rules (per Techne's stoa proposal): if "is this novel?" requires analyst judgment at every case, the loop never closes. The 5-class rules above are mechanical by construction.
- **Per-class rewards that reward analyst-time rather than discovery.** If Aporia routinely overrides `genuine_novelty` → `adjacency_extension`, the system learns to ship borderline cases for the human's review rather than to filter. Counter-incentive: log override rate and downweight if Aporia's correction rate exceeds 30%.

---

## 6. Concrete next moves for Techne + Aporia (~150 words)

**Aporia (~½ day):** Pull the SHADOW_CATALOG dump from triple #3 (commit f76d3974). Hand-classify the first 50 entries against the 5-class typology. Record (a) inter-class base rates, (b) cases where the mechanical rule disagrees with my classification (these become rule refinements), (c) any class proposals that need a sixth bucket. Return refined decision rules and base-rate estimates as a follow-up annotation to this scout.

**Techne (~2 days):**

1. **Day 1.** Implement the 5-class typology as a typed substrate symbol kind (per Scout #5 §"The candidate-classification typology"). Wire decision rules into the catalog-check oracle. Add `f(x^k)` canonicalization to close the Scout #6 gap.
2. **Day 2.** Replace binary reward with the shaped reward from §4. Add the `unclassifiable` sixth class. Add `caveat_vector` metadata to each reward record. Wire the held-out falsifier (Scout #6's red-team panel) as the un-trained tripwire.
3. **Run.** 10K episodes × 3 seeds with the new reward and typology. Compare PROMOTE rate, SHADOW class distribution, and caveat-vector magnitude against triple #3 baseline.

If PROMOTE rate is still zero **and** SHADOW is dominated by `numerical_artifact`/`catalog_omission`, the structural ceiling is in catalog coverage (escalate to Scout #2/#11). If SHADOW shifts toward `adjacency_extension`/`genuine_novelty` even at PROMOTE rate zero, the typology is doing real work and the next move is widening the catalog so adjacency cases get checked against more known territory.

---

## 7. References

1. Polu, S. & Sutskever, I. (2020). *Generative Language Modeling for Automated Theorem Proving (GPT-f)*. arXiv:2009.03393.
2. Polu, S. et al. (2022). *Formal Mathematics Statement Curriculum Learning*. arXiv:2202.01344.
3. DeepMind (2024). *AI achieves silver-medal standard solving IMO problems* (AlphaProof writeup). https://deepmind.google/discover/blog/ai-solves-imo-problems-at-silver-medal-level/
4. Davies, A., Veličković, P., Buesing, L., et al. (2021). *Advancing mathematics by guiding human intuition with AI*. Nature 600, 70-74. DOI:10.1038/s41586-021-04086-x
5. Le, H., Wang, Y., Gotmare, A. D., et al. (2022). *CodeRL: Mastering Code Generation through Pretrained Models and Deep Reinforcement Learning*. NeurIPS 2022. arXiv:2207.01780.
6. Li, Y. et al. (2022). *Competition-Level Code Generation with AlphaCode*. Science 378(6624), 1092-1097.
7. Christiano, P. et al. (2017). *Deep Reinforcement Learning from Human Preferences*. NeurIPS 2017. arXiv:1706.03741.
8. Gao, L., Schulman, J. & Hilton, J. (2023). *Scaling Laws for Reward Model Overoptimization*. ICML 2023. arXiv:2210.10760.
9. Pan, A., Bhatia, K. & Steinhardt, J. (2022). *The Effects of Reward Misspecification: Mapping and Mitigating Misaligned Models*. ICLR 2022. arXiv:2201.03544.
10. Skalse, J., Howe, N., Krasheninnikov, D. & Krueger, D. (2022). *Defining and Characterizing Reward Hacking*. NeurIPS 2022. arXiv:2209.13085.
11. Krakovna, V., Uesato, J., Mikulik, V., et al. (2020). *Specification gaming: the flip side of AI ingenuity*. DeepMind blog + arXiv companion.
12. Lintott, C. J. et al. (2008). *Galaxy Zoo: morphologies derived from visual inspection of galaxies from the Sloan Digital Sky Survey*. MNRAS 389(3), 1179-1189. arXiv:0804.4483.
13. Bamford, S. P. et al. (2009). *Galaxy Zoo: the dependence of morphology and colour on environment*. MNRAS 393(4), 1324-1352. arXiv:0805.2612.
14. Inglese, J., Johnson, R. L., Simeonov, A., et al. (2007). *High-throughput screening assays for the identification of chemical probes*. Nature Chemical Biology 3, 466-479. DOI:10.1038/nchembio.2007.17.
15. Sloane, N. J. A. & OEIS Foundation. *Editing the OEIS* (style sheet + reviewer guidelines). https://oeis.org/wiki/Style_Sheet and https://oeis.org/wiki/Editing
16. Mossinghoff, M. J. (2008+). *Lehmer's Problem* — small-Mahler-measure polynomial tables. https://www.cecm.sfu.ca/~mjm/Lehmer/
17. Aporia Pivot Research Report 02. *Reward Design for Partially-Verifiable Mathematical Claims*. Prometheus internal, 2026-05-02. (`F:/Prometheus/aporia/docs/prometheus_pivot_research_batch1/report_02_reward_design_partial_verifiers.md`)
18. Aporia Pivot Research Report 04. *DeepMind AlphaProof: Current Public State*. Prometheus internal, 2026-05-02. (`F:/Prometheus/aporia/docs/prometheus_pivot_research_batch1/report_04_alphaproof_intelligence.md`)
19. Scout #5 — *HITL SHADOW_CATALOG triage*. (`F:/Prometheus/aporia/scouting/05_hitl_shadow_catalog_triage.md`)
20. Scout #6 — *Adversarial red-team*; `f(x^k)` Mahler-invariance gap. (`F:/Prometheus/aporia/scouting/06_adversarial_red_team.md`)
21. Scout #7 — *Stronger algorithm than REINFORCE*; structural-ceiling logic. (`F:/Prometheus/aporia/scouting/07_stronger_algorithm.md`)

---

*Aporia, 2026-04-28. Self-authored T2 doc per Techne's commit f76d3974 follow-up. Pairs with Scout #5 (triage interface) and Scouts #2/#11 (catalog widening) — together they form the **understand-the-failure-mode + expand-the-input** response to the structural ceiling. Recommend Aporia takes the first 50-entry hand-classification batch immediately to calibrate the typology before Techne hard-wires the decision rules.*
