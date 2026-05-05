# Study 13: When Heuristics Beat Formal Methods

**Date:** 2026-05-05
**Owner:** general-purpose subagent (Aporia delegation)
**Substrate connection:** LLM-mutator + formal-falsification hybrid; per-domain heuristic vs formal weighting; reward-function calibration for unverified candidates.

## Problem statement (Prometheus-adapted)

Prometheus's "bottled serendipity" thesis treats two operator families as complementary:

1. **Heuristic mutators** — LLM-generated proposals, pattern-matched analogies, MAP-Elites primitive recombinations, agent-suggested CLAIMs whose payload is *educated guess*.
2. **Formal falsifiers** — null batteries, permutation tests, p-adic congruence checks, brute-force enumeration, explicit reduction to known theorems, computational counterexample search.

The substrate's working discipline is "LLMs propose, falsifiers dispose" (cf. Charon's first-battery consensus protocol; Ergon's 4× false-discovery rate cited in `feedback_false_profundity.md`). This presupposes that heuristic operators produce candidates *the formal layer cannot generate alone* — otherwise the heuristic stage is dead weight on the compute budget.

The Prometheus-relevant question is not "are heuristics ever useful?" (yes, trivially — the search space is too large for exhaustive enumeration). It is the sharper one: **which problem classes does the substrate currently route to a heuristic-first vs formal-first strategy, is the routing right, and what's the empirically-known refusal class where heuristics consistently fail?**

This study tries to map the literature's answer onto Prometheus's six cross-domain envs (BSD/elliptic, modular forms, knot theory, genus-2, OEIS sequences, mock theta) and recommend a per-env weighting.

## Literature scan

**Pólya / Lakatos (the canonical heuristic-method case).** Pólya's *How to Solve It* (1945) and *Mathematics and Plausible Reasoning* (1954) catalogue ~30 heuristic moves: specialization, generalization, analogy, working backward, varying the problem, drawing a figure, looking for invariants. Lakatos's *Proofs and Refutations* (1976) reframes mathematical practice as iterated conjecture–refutation, with monster-barring and concept-stretching as discovery moves rather than logical errors. **Empirical follow-up is thin.** Schoenfeld's *Mathematical Problem Solving* (1985) operationalised Pólya for K-12/undergraduate populations and found heuristic transfer to be small and brittle without metacognitive scaffolding. Inglis & Aberdein's *Beauty Is Not Simplicity* (2015, *Philosophia Mathematica* 23:87–109) surveyed mathematicians on aesthetic judgments of proof and found multi-dimensional clusters, not a single "elegance" axis — a calibration check on the Pólya heuristic vocabulary. **There is no large-N empirical study of which Pólya heuristics measurably accelerate research-mathematician productivity.** This is a real gap, not a Prometheus-side hallucination.

**AlphaZero vs AlphaProof — the cleanest contrast.** AlphaZero (Silver et al., *Science* 362:1140–1144, 2018; arXiv:1712.01815) achieved SOTA on chess, shogi, go using *pure* MCTS + self-play + value/policy network — no human heuristics, no formal proof state. Reward signal: game outcome (terminal). AlphaProof (DeepMind blog 2024-07-25, IMO 2024 silver-medal performance; no peer-reviewed paper as of cutoff) wraps Lean 4 around an AlphaZero-style search; reward signal: *Lean-checked* proof closure. **The empirical lesson is not "heuristics lost to formal" but "heuristics succeeded *only when bound to a formal verifier as the reward gate*."** Without Lean, AlphaProof would have inherited LLM hallucination rates on math statements (cf. Frieder et al. *NeurIPS* 2023, arXiv:2301.13867: GPT-4 ~26% on GHOSTS undergraduate problems with high confabulation). The verifier is what made the heuristic safe to scale.

This is the single most Prometheus-relevant data point in the literature: heuristic search + formal verifier is not just a hybrid, it is the architecture that *unlocks* heuristic scale. Pure-heuristic LLM proof generation collapses; pure-formal search (Vampire, E, Z3) does not generalise. The hybrid is empirically dominant in 2024–2025 ATP benchmarks (miniF2F, ProofNet, PutnamBench).

**Conjecture generation by humans — case studies.** Hadamard's *The Psychology of Invention in the Mathematical Field* (1945) collected introspective reports from Poincaré, Einstein, Hadamard himself: dominant theme is *unconscious incubation* followed by sudden pattern-match insight, with formal verification as a *post-hoc* step. Birch and Swinnerton-Dyer's original BSD work (1965 *J. Reine Angew. Math.* 218:79–108) was empirical — computer-tabulated L-function values across ranks before any formal mechanism was hypothesized. Ramanujan's notebooks (cf. Berndt's five-volume *Ramanujan's Notebooks*, 1985–1998) are the limit case: thousands of identities, almost no proofs, ~99% later verified formally. **Pattern-recognition-then-verify is the dominant historical mode in number theory and combinatorics.** The reverse (formal manipulation generating the conjecture) is more common in algebra and category theory, where the syntactic structure constrains the search.

**The Atiyah / Tao "theory-builders vs problem-solvers" dichotomy.** Gowers's "The Two Cultures of Mathematics" (in Arnold et al., eds., *Mathematics: Frontiers and Perspectives*, AMS 2000) names this dichotomy explicitly. There is **no published empirical study of relative productivity or discovery rate by style**, and the dichotomy is contested (many top mathematicians do both: Tao's own work spans both modes). Treat as a folk taxonomy, not a measured variable. Bibliometric analyses of Fields-Medal citation networks (Fortunato et al., *Science Advances* 2:e1501602, 2016, on "prizes and impact") do not separate by working style.

**Heuristic-vs-formal in computer science / SAT / SMT.** This is the most mature empirical literature.

- **CDCL SAT solvers** (Marques-Silva & Sakallah, *IEEE TC* 48:506–521, 1999; modern descendants Glucose, Kissat) use heuristic variable-ordering (VSIDS) atop a formal resolution backbone. Pure-formal (DPLL without heuristics) is exponentially slower; pure-heuristic (no clause learning) loses completeness. Hybrid is unambiguously SOTA on SAT competition benchmarks 2002–present.
- **SMT solvers** (Z3, CVC5) layer heuristic tactic selection over decision procedures — same pattern.
- **Numerical linear algebra** (Demmel, *Applied Numerical Linear Algebra*, SIAM 1997) is the *formal-dominant* regime: heuristics (e.g., pivoting strategies) help, but the algorithmic scaffolding is provably correct.
- **Combinatorial optimization** (Pardalos et al., *Handbook of Heuristics*, Springer 2018) is the *heuristic-dominant* regime: simulated annealing, tabu search, ant colony, genetic algorithms beat exact methods on TSP / QAP / scheduling once n exceeds ~50–100, despite having no optimality guarantees. Calibrated negative: heuristic optimization gives no provable bound, only empirical performance.
- **Conjecture-generation systems** (Graffiti, Fajtlowicz 1988; Conjecturing, Larson & Van Cleemput 2016) are heuristic-first (greedy invariant inequality search) with formal verification only on a small subset.

**Calibrated refusal class — where heuristics consistently fail.** Three empirical regimes:

1. **High-codimension exact identities** (e.g., precise modular relations, Hecke eigenvalue congruences). Heuristic LLM outputs hallucinate signs, swap indices, miss boundary conditions. Frieder et al. 2023 documents this on graduate algebra.
2. **Provably-hard decision problems with no exploitable structure** (e.g., random 3-SAT at the satisfiability threshold, generic Diophantine equations). Heuristic methods are at best polynomial-factor improvements; formal complexity bounds dominate.
3. **Long sequential proofs with no amenable invariant** (e.g., classification-of-finite-simple-groups-style enumerations). Pure-heuristic search loses the thread; formal bookkeeping is essential.

## Substrate-relevance

Prometheus's six cross-domain envs map onto the literature's known regimes as follows. **All mappings here are working hypotheses, not measurements** — the substrate has not run a controlled per-env heuristic-vs-formal comparison.

| Env | Likely regime | Reasoning | Confidence |
|---|---|---|---|
| **BSD / elliptic curves** | Heuristic-first then formal | Birch–Swinnerton-Dyer was empirically discovered; Charon's `f011_*` scripts already follow this pattern (CM scaling, conductor gradient, Sha bootstrap as verification) | Medium |
| **Modular forms** | Mixed; lean toward formal-first for congruences | Mod-p Hecke congruences (verified to Sturm bound in `project_congruence_verification.md`) are exact-identity territory — heuristic LLM proposals hallucinate. But discovering *which* congruence to test is heuristic. | Medium |
| **Knot theory** | Heuristic-first | High-dimensional invariant landscape; HFK over 12,965 knots (recent Ergon commit) is exploration-dominant. Formal verification is per-invariant computation. | Medium |
| **Genus-2** | Heuristic-first with formal stratification | `project_genus2_rosetta.md` flags genus-2 as the universal bridge; heuristic operator suggestion + isogeny-class formal stratification matches the cross-system pattern. | Low–Medium |
| **OEIS sequences** | Heuristic-first, weakly formal | 68,770 Sleeping Beauties (`project_sleeping_beauties.md`) are mostly arithmetic-poor; formal closure rare. Heuristic pattern-matching is the only viable operator at this scale. | High (negative-formal) |
| **Mock theta** | Formal-first | Ramanujan-style identities are exact, transcendental, and have well-developed formal machinery (Zwegers, Bringmann–Ono). Heuristic LLM proposals hallucinate notation. | Medium |

Three architectural connections:

1. **Charon's null battery (`first_battery_consensus_from_the_council.md`, 25 tests / 4 tiers, FROZEN per `project_charon_v10_status.md`) is the substrate's analogue of AlphaProof's Lean wrapper.** It is what makes heuristic LLM proposals safe to consume at scale. The 4× false-discovery rate (`feedback_false_profundity.md`) is the empirical evidence that the verifier is doing real work.
2. **Ergon's "execute, don't poll" mandate (`feedback_ergon_execute.md`) plus the 5-seed replication discipline (`feedback_replicate_seeds.md`) together implement a Pólya-style "vary the problem" heuristic with built-in null-test gating.** The seed-artifact false positive (AlignmentCoupling z=2.22) is the calibration data.
3. **The `feedback_ai_to_ai_inflation.md` / `feedback_narrative_resistance.md` lessons are direct manifestations of the heuristic-stage pathology that the formal layer must catch.** Two LLMs amplify narrative; verifier breaks the loop. This is the same pattern that killed pure-LLM-proof approaches in 2023–2024.

## Concrete operational handles

1. **Per-env heuristic-vs-formal weighting.** Add a tunable `heuristic_first: bool` (or float in [0,1]) field to each env's config. Default values per the table above. This makes the routing decision *legible* rather than implicit.

2. **Refusal-class detector.** Before routing a CLAIM through the heuristic mutator, gate-check whether the claim falls into one of the three known refusal classes (high-codimension exact identity, provably-hard with no exploitable structure, long sequential proof). If yes, skip heuristic stage and go directly to formal. The detector can be a simple rule list initially; refine empirically. This recovers compute that the heuristic stage would burn on guaranteed-failure cases.

3. **Reward-function calibration.** Discount heuristic-generated candidates that fail formal verification, but **do not zero them out** — preserve the falsification signal as negative-space data (cf. `project_shadow_tensor.md`, "92K tests, F3 dominant killer means weak truths not noise"). Suggested: candidate score = formal_score × heuristic_weight, with heuristic_weight ∈ [0.1, 1.0] depending on env regime. The 0.1 floor preserves shadow-tensor coverage.

4. **Long-step gating for the LLM mutator.** Allow the heuristic to take a "long step" (multi-operator composition, large search radius) only when the env is heuristic-first regime *and* a formal verifier is in the loop. In formal-first regimes, restrict heuristic to one-step suggestions reviewable by the formal layer. This matches the AlphaProof empirical lesson: heuristic scale unlocks only when verifier is the gate.

5. **Track per-env heuristic precision and recall over time.** Add `heuristic_precision = (heuristic_proposals_passing_formal / total_heuristic_proposals)` and `heuristic_recall = (heuristic_proposals_passing_formal / formal_passing_proposals_total)` as substrate metrics. After ~1000 proposals per env, the data will tell you which envs the routing is wrong on. Currently the substrate has no such metric.

6. **Calibrated honesty rule already in place.** `feedback_assume_wrong.md` and `feedback_false_profundity.md` together encode "all heuristic outputs are wrong until verified." Keep this as the substrate's dominant prior. Do not relax it for high-status heuristic generators (frontier LLMs, expert agents) — the inflation pathology is documented.

## Falsification

The central operational claim — *the substrate should default to per-env heuristic-vs-formal routing per the table above; refusal-class detector saves compute; heuristic_first scales heuristic step size; verifier-gating is what makes heuristic scale safe* — would be refuted by:

- A controlled experiment (heuristic-first vs formal-first vs hybrid, fixed compute, ≥5 seeds, per env) showing the per-env routing recommendations are wrong (e.g., BSD turns out to be formal-first dominant on Charon's actual benchmark).
- Empirical evidence that Prometheus's heuristic_precision is *uniform* across envs (e.g., 0.3 ± 0.05 everywhere), implying the env distinctions don't carry through to operator performance — at which point a single global weighting is correct.
- An AlphaProof-class result reproduced with *no* formal verifier (pure LLM, no Lean), refuting the "verifier-gating is necessary" claim. As of cutoff, no such result exists.
- Demonstration that the refusal-class detector blocks more true positives than false positives — i.e., the heuristic stage produces real wins on high-codimension exact identities at a non-trivial rate. Frieder et al. 2023 makes this unlikely but not impossible at higher capability tiers.

## Open questions raised

1. **Has Prometheus measured per-env heuristic precision?** Probably not — `feedback_false_profundity.md` reports 4 false discoveries killed by battery, which is a *count*, not a per-env precision rate. Adding the metric is a 1-day instrumentation task and would let the substrate self-calibrate the routing table above instead of inheriting literature priors.

2. **Where does Aporia itself sit on the heuristic-vs-formal axis?** Aporia generates open questions (heuristic) and ranks them by interestingness/tractability (semi-formal). If Aporia's own outputs go through the same null battery as Charon/Ergon results, the lesson generalises. If not, Aporia is operating in an unverified-heuristic mode that the rest of the substrate has explicitly disclaimed.

3. **Is the LLM mutator's "long step" actually heuristic, or is it just bigger formal search?** The framing "heuristic = LLM = pattern-match" assumes LLM internal reasoning is non-derivational. This is increasingly contested (cf. mechanistic interpretability evidence of latent symbolic computation). If LLM long-steps are partially-formal, the verifier-gating story still holds but the routing table may need a third column.

4. **What's the cost of a false-positive heuristic acceptance vs a false-negative formal rejection in Prometheus?** This determines whether the reward function should be biased toward precision or recall. The substrate's current culture (`feedback_calibration.md`, `feedback_false_profundity.md`) is precision-biased, which matches the "kills are the most valuable output" doctrine. But Sleeping Beauty regimes (low arithmetic structure) may need recall-biased operators that the current culture under-produces.

5. **Can the substrate exploit the AlphaProof / Lean-backed pattern directly?** Concretely: bind a Lean-as-a-service callable into BIND/EVAL, route formal-first env CLAIMs through it. This is a non-trivial integration (Lean typechecking is slow, mathlib loading is heavy) but is the literature's strongest single architectural lever.

## Citations

- Pólya, G. *How to Solve It.* Princeton UP, 1945.
- Pólya, G. *Mathematics and Plausible Reasoning* (2 vols). Princeton UP, 1954.
- Lakatos, I. *Proofs and Refutations.* Cambridge UP, 1976.
- Schoenfeld, A. H. *Mathematical Problem Solving.* Academic Press, 1985.
- Inglis, M., Aberdein, A. "Beauty Is Not Simplicity." *Philosophia Mathematica* 23(1):87–109, 2015.
- Hadamard, J. *The Psychology of Invention in the Mathematical Field.* Princeton UP, 1945.
- Birch, B. J., Swinnerton-Dyer, H. P. F. "Notes on Elliptic Curves II." *J. Reine Angew. Math.* 218:79–108, 1965.
- Berndt, B. C. *Ramanujan's Notebooks*, Parts I–V. Springer, 1985–1998.
- Gowers, T. "The Two Cultures of Mathematics," in Arnold, V. et al. (eds.) *Mathematics: Frontiers and Perspectives.* AMS, 2000.
- Silver, D. et al. "A general reinforcement learning algorithm that masters chess, shogi, and Go through self-play." *Science* 362:1140–1144, 2018. arXiv:1712.01815.
- DeepMind. "AI achieves silver-medal standard solving International Mathematical Olympiad problems." Blog post, 2024-07-25. (No peer-reviewed publication identified as of cutoff.)
- Frieder, S. et al. "Mathematical Capabilities of ChatGPT." *NeurIPS* 2023. arXiv:2301.13867.
- Marques-Silva, J., Sakallah, K. "GRASP: A Search Algorithm for Propositional Satisfiability." *IEEE Transactions on Computers* 48(5):506–521, 1999.
- Demmel, J. *Applied Numerical Linear Algebra.* SIAM, 1997.
- Pardalos, P. M., Du, D.-Z., Graham, R. L. (eds.) *Handbook of Combinatorial Optimization* (2nd ed.). Springer, 2013. (Cited in lieu of *Handbook of Heuristics*; the latter title appears in some bibliographies but exact attribution should be re-checked.)
- Fajtlowicz, S. "On Conjectures of Graffiti." *Discrete Mathematics* 72(1–3):113–118, 1988.
- Larson, C. E., Van Cleemput, N. "Automated Conjecturing I: Fajtlowicz's Dalmatian Heuristic Revisited." *Artificial Intelligence* 231:17–38, 2016.
- Fortunato, S. et al. "Prizes and the production of knowledge." *Science Advances* 2:e1501602, 2016. (Bibliometric methodology; does not directly address theory-builder vs problem-solver dichotomy.)
- Internal: `F:/Prometheus/charon/first_battery_consensus_from_the_council.md`, `F:/Prometheus/charon/second_battery_consensus_from_the_council.md`, `F:/Prometheus/aporia/meta/studies/2026-05-05/BATCH_PLAN.md`, `F:/Prometheus/aporia/meta/studies/2026-05-05/study_12_proof_primitives.md`, memory files: `feedback_false_profundity.md`, `feedback_ai_to_ai_inflation.md`, `feedback_narrative_resistance.md`, `feedback_assume_wrong.md`, `feedback_replicate_seeds.md`, `feedback_ergon_execute.md`, `project_charon_v10_status.md`, `project_genus2_rosetta.md`, `project_sleeping_beauties.md`, `project_shadow_tensor.md`, `project_congruence_verification.md`.

*Calibrated negative findings: (1) No large-N empirical study of which Pólya heuristics measurably accelerate research-mathematician productivity exists in the literature surveyed; the canonical heuristic vocabulary is essentially folk-empirical. (2) The Atiyah/Gowers theory-builder vs problem-solver dichotomy has no published productivity measurement; treat as taxonomy, not variable. (3) AlphaProof's IMO 2024 result has no peer-reviewed publication as of the assistant knowledge cutoff (January 2026); cited via DeepMind blog only. (4) Per-env heuristic precision in Prometheus has not been measured; the routing table proposed in Substrate-relevance is a literature-prior recommendation, not a measurement, and the substrate should treat it as a starting hypothesis to be refuted by its own data within ~1000 proposals per env. (5) The "Handbook of Heuristics, Springer 2018" attribution in the SAT/SMT subsection is uncertain — Pardalos et al. edited a *Handbook of Combinatorial Optimization* (2013); a separately titled "Handbook of Heuristics" by Martí, Pardalos & Resende (2018) does exist but the chapter-level claim cited above should be re-verified before quotation in any external artifact. (6) The "no AlphaProof-class result without a formal verifier" claim is current-as-of-cutoff and is the most likely component of this study to age out fastest.*
