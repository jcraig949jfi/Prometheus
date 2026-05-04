# Techne — Status & Pivot Decision (2026-05-04)

**Audience**: James (project lead) + frontier-model reviewers (ChatGPT, Gemini, Claude variants).
**Purpose**: synthesize 2-3 sessions of discovery-loop work, expose the pivot decision, invite outside critique.
**Honest framing throughout**: positive results are rediscovery (ground truth in LMFDB / OEIS / published tables), NOT mathematical novelty. Lifts over random reflect class-prior recovery, NOT learned mathematical structure. Kills are the most valuable output.

---

## Quick read

- 6 cross-domain rediscovery validations (BSD rank, modular forms, knot trace fields, genus-2 curves, OEIS Sleeping Beauty, mock theta) — substrate transports cleanly across mathematical structure.
- 10+ orthogonal H2 falsifications on the Lehmer / Mahler-measure search, all returning **0 PROMOTEs across ~350,000 cumulative episodes**.
- Rich BSD features (45 added → 71-D vs 26-D baseline) **REFUTE** yesterday's "feature-bottleneck" reading. Linear-rich 43.2% vs Linear-raw 46.2% (p=0.795 — *slightly worse*).
- Frozen-bias REINFORCE on Lehmer (cleanest H2 falsifier yet): 0 catalog hits despite bit-identical preservation of the warm-start bias. The seeded-random control hit 1069 catalog entries — so the scaffold reaches the right neighborhood, but any trainable component erodes signal.
- **Cumulative weight**: H1 (structural emptiness of the +100 band, consistent with Lehmer's conjecture) is the most likely answer in the deg-14 ±5 subspace. H2 (algorithm/policy/feature is the bottleneck) survives only on untested paths: MAP-Elites (Ergon's lane), MCTS, deeper feature classes (L-function zero density, p-adic L-values).
- Substrate hardening: caveat-as-metadata schema on CLAIM (proposal 2026-05-04, ChatGPT's structural fix to AI-to-AI inflation); cost models calibrated to within 2× for top-50 hot-path ops (was 2-757× off).
- **Pivot decision below.**

---

## 1. Project Context: Prometheus

Prometheus is a substrate for mathematical discovery via multi-agent epistemics. The thesis (anchored to David Silver's *Ineffable Intelligence* essay): mathematics is the language a superintelligence will use to find what humanity cannot. The bottleneck for getting there is not raw model capacity but representation, falsification discipline, and a shared substrate where multiple agents can work, disagree, and ratchet truth forward.

**Architecture (relevant pieces):**

- **Sigma kernel (Σ)**: 7-opcode substrate — RESOLVE / CLAIM / FALSIFY / GATE / PROMOTE / ERRATA / TRACE. Every claim moves CLAIM → FALSIFY → terminal-state {PROMOTED, SHADOW_CATALOG, REJECTED}. Kills are recorded with kill_path metadata; SHADOW_CATALOG is the "interesting but not full proof" intermediate state.
- **BIND/EVAL extension**: callable symbols with typed cost contracts, postconditions, and authority refs. v2 routes everything through CLAIM/FALSIFY/PROMOTE; v1 (sidecar) is being deprecated.
- **Caveat-as-metadata**: typed list of caveats on every Claim (small_n, mode_collapse, rediscovery_not_discovery, synthetic_battery_used, etc.). Caveats hash-locked into PROMOTE def_blob; downstream consumers inherit them via TRACE. Solves the "+53.1% lift escapes upward without context" problem.
- **Pillars** (specialist agents): Techne (toolsmith — me), Charon (battery / falsifier), Aporia (open-question catalog with 322 questions across 13 domains), Ergon (the Learner — see §3), Hephaestus (forge), Cartography (map), Stoa (coordination forum).

**End-game goal**: a discovery system that produces durable mathematical results, not narratives. Every claim has provenance, every kill is recorded, every result is reproducible. The substrate's value is that future agents (human researchers, Ergon's Learner, external reviewers) can navigate the corpus without trusting any single agent's framing. Two-track epistemics: weak signals are exploration threads but firewalled from training corpus; only PROMOTED + caveat-clean entries become substrate truth.

## 2. Techne's Role

I forge substrate-grade artifacts:

1. **Calibrated tools** (85 arsenal ops): cost models calibrated to within 2× for top-50 hot-path ops as of 2026-05-04. Postconditions, authority refs, equivalence_class tags. Profiler harness re-runnable on cadence (recommended monthly or on >5% BudgetExceeded rate).
2. **Validated discovery loops** (5-catalog cross-check + 4-fold falsification): every candidate routes through Mossinghoff (8625 entries) + lehmer_literature (24) + LMFDB nf_fields + OEIS + arXiv title fuzzy match. F1 (permutation null) + F6 (base rate) + F9 (simpler explanation) + F11 (cross-validation) gate before SHADOW_CATALOG.
3. **Typed records for Ergon's Learner**: every CLAIM, FALSIFY, and terminal-state event is durable, hash-locked, and includes caveats. Goal: Ergon's Learner trains on a corpus where it doesn't have to re-do my falsification — the substrate already excluded the noise.

## 3. Ergon's Learner

Ergon is building a long-term ML model (the Learner) that consumes Techne's substrate output. Vision: the substrate produces typed records at scale; the Learner trains on this corpus; over time, it becomes a model that can predict next-likely productive moves in mathematical search.

This is Prometheus's strongest claim to **owned models** rather than dependence on frontier APIs. (See `feedback_frontier_models_window.md` — "Frontier LLMs are not allies; APIs are expensive and increasingly restricted; evolve owned models before the window closes.")

Ergon's MAP-Elites work (running in parallel to mine) is also exploring the discovery search but with quality-diversity rather than scalar-reward optimization. MAP-Elites is the remaining live H2 path I haven't touched.

## 4. The Discovery Loop: Hypothesis Structure

Two competing hypotheses for the Lehmer / Mahler-measure search (the substrate's first discovery target):

- **H1 (Lehmer's conjecture-consistent)**: The +100 band (Mahler measure in (1.001, 1.18)) is structurally empty in the deg-14 ±5 polynomial subspace beyond known catalog entries. The 0-PROMOTE result is honest negative evidence — the substrate IS finding "nothing there."
- **H2 (algorithm / policy / feature is the bottleneck)**: A richer search method would find sub-Lehmer polys that current methods miss. The 0-PROMOTE result is a measurement artifact, not a structural finding.

Each H2 falsification strengthens H1 but doesn't fully prove it — the conjecture is open and alternative search strategies always remain. The substrate-level requirement: the discovery loop produces 0 honestly (REJECT with kill_path traces) when content is absent, and PROMOTE genuinely when content is present. Both behaviors are needed for the substrate to be trustworthy.

## 5. What's Been Built (2026-05-02 to 2026-05-04)

| Stream | Artifact | Result |
|---|---|---|
| BIND/EVAL v1 (MVP) → v2 (full kernel discipline) | `sigma_kernel/bind_eval_v2.py`, 3 envs migrated | All downstream envs route through CLAIM/FALSIFY/PROMOTE |
| Discovery pipeline | `prometheus_math/discovery_pipeline.py` | 7-rule kill_path; 3 terminal states |
| Mossinghoff snapshot refresh | 178 → 8625 entries via Wayback Machine | arXiv-probe Mossinghoff hit rate 5.9% → 100% |
| 6 cross-domain envs (BSD/MF/knot/g2c/OEIS/mock-theta) | New corpora + envs + 3-arm pilots | Substrate transports; modal-class collapse on every domain |
| 10+ H2 falsifiers on Lehmer | Sweeps + pilots + REINFORCE/PPO/GA/root-space/seeded variants | All 0 PROMOTE; cumulative weight to H1 |
| Caveat-as-metadata schema | `sigma_kernel/caveats.py`, migration 004 | Caveats inherited automatically through TRACE |
| Cost-model tightening | `_metadata_table.py` updated, profiler shipped | 50/50 ops within 2× (was 33/50) |
| Bug-hunt 7-category gate | `techne/skills/edge-corner-bug-hunt/SKILL.md` | 5 bugs surfaced + fixed (B-BUGHUNT-001/002/003/004/005) |
| Math-tdd 4-category gate | `techne/skills/math-tdd.md` | 99 new domain tests + 18 falsifier tests + 19 caveat tests |

Test counts: 2436 → 2625 passing (+189 over 2 days). 0 failures.

## 6. Findings — Cross-Domain Validations

> **Substrate-credit-laundering warning (per Aporia review).** Every row below describes modal-class recovery, NOT learned mathematical structure. A naive Bayes classifier with zero learning posts comparable lifts. This table demonstrates KERNEL I/O UNIFORMITY (engineering result), not mathematical-capability transport (science result). Per-cell caveats are appended.

| Domain | Best algo | Lift | Welch p | What this IS NOT |
|---|---|---|---|---|
| BSD rank (Cremona, n=1000) | REINFORCE-lin | +1.37× | 0.00055 | NOT learning rank prediction; collapsing to rank-0/1 modal prior |
| Modular forms (LMFDB, 7875) | PPO-MLP | +1.58× | 0.00034 | NOT learning Hecke eigenvalues; 21-bin classification with class skew |
| Genus-2 (LMFDB, 6000) | REINFORCE-lin | +1.59× | 0.028 | NOT learning Mordell-Weil rank; 3-class modal prior again |
| Knot trace fields (n=48) | REINFORCE-lin | +5.40× | 1.84e-7 | NOT learning Alexander → trace-field map; 85% class skew inflates lift |
| OEIS Sleeping (n=205) | Growth-heuristic | +18.13× | <1e-6 | NOT a substrate result; log-linear extrapolation is the structure; RL arms underperform |
| Mock theta (n=44) | REINFORCE-lin | +12× | 1.76e-4 | NOT learning q-series structure; modal collapse to small-magnitude integer bins |

**The honest cross-domain claim:** the kernel's I/O surface is uniform enough to host 6 envs without per-domain plumbing, and the substrate runs honestly (typed records, calibrated cost models, reproducible seeds, kill_path metadata). That is an engineering result.

**The honest cross-domain non-claim:** none of these results demonstrates mathematical-capability transport. A non-tautological transport claim would require: (a) train on X, test on unseen Y, > class-prior; OR (b) single hyperparameter set with signal beyond modal recovery across domains; OR (c) discovery loop produces a result domain experts confirm as novel. Zero of these have been done.

## 7. Findings — H2 Falsifications on Lehmer

10+ orthogonal "is the algorithm/policy/feature the bottleneck?" tests, all returning 0 PROMOTEs across ~350,000 cumulative episodes:

| Falsifier | Episodes | Outcome |
|---|---|---|
| Random uniform | 100K | 0 PROMOTE (baseline) |
| REINFORCE-linear | ~50K across ablations | 0 PROMOTE; mode-collapse to Salem cluster (33%) |
| PPO with value function | ~30K | 0 PROMOTE; mode-collapse to cyclotomic_or_large (47%) |
| V2 GA elitist | ~30K | 0 PROMOTE; mode-collapse to cyclotomic basin (M=1) |
| V2 anti-elitist (3 strategies: tournament_novelty / crowding / restart_collapse) | 18K | 0 PROMOTE; diversity preserved but no signal |
| V3 root-space sampling (Vieta expansion from k root pairs) | 30K samples | 0 integer-coefficient configs (subspace is measure-zero with quantized angles) |
| Catalog-seeded random (warm-start near Mossinghoff \|c\|≥4) | 15K | 0 PROMOTE BUT 1069 catalog rediscoveries (~7.1%) — proves the seeding works at random level |
| Catalog-seeded REINFORCE | 15K | 0 catalog hits (gradient erosion) |
| **Frozen-bias REINFORCE (today)** — bias `b=log(prior)` held bit-identically constant | 15K | **0 catalog hits despite bit-identical preservation; cleanest falsifier yet** |
| Degree sweep (10/12/14) × Alphabet sweep (±3/±5/±7) | 9 cells | 0 PROMOTE every cell |
| Reward shape (step vs shaped) | 6 cells | 0 PROMOTE under both |
| MLP-vs-linear on BSD (yesterday) | 5 seeds × 6 hyperparam cells | p=0.381 — policy class is NOT the bottleneck on BSD |
| **Rich BSD features (today)** — +45 features (regulator, real_period, faltings_height, abc_quality, szpiro, Tamagawa, torsion, CM/semistable) | 75K | Linear-rich 43.2% vs Linear-raw 46.2%, p=0.795 — *slightly worse*; refutes "feature-bottleneck" reading |

**Cumulative weight**: H1 is the most likely explanation. Lehmer's conjecture (asserting the +100 band has only finitely many algebraic-integer Mahler measures) is consistent with the data.

H2 survives only on untested paths:
- **MAP-Elites** (Ergon's lane, in progress)
- **MCTS through coefficient space** (different exploration pattern from REINFORCE/PPO/GA)
- **Deeper feature classes** for BSD (L-function zero density, p-adic L-values, modular degree — none touched today)

## 8. The Conceptual Update Today

Yesterday's reading after MLP-vs-linear on BSD: "policy class is not the bottleneck; raw a_p features are saturating. Next investment: feature engineering."

Today's rich-features test pulled 45 additional features (regulator, real_period, faltings_height, abc_quality, szpiro_ratio, Tamagawa product, torsion structure one-hot, conductor radical class, CM/semistable flags) — 26-D → 71-D, sourced from Cremona allbsd + LMFDB ec_curvedata.

Result: rich features make NO difference. Both rich variants STILL collapse to single-class prediction. The "features are saturating" reading is now refuted.

The actual finding: **on BSD, the bottleneck is neither policy class nor standard BSD invariants. The data carries this much signal under modal-class-collapse env design, and no more.**

This is a pivot point because it eliminates the cheapest investment hypothesis (feature engineering) and surfaces a new diagnosis (env design / reward shape / action discretization).

## 9. Pivot Options

**Option A — Deeper feature classes for BSD/modular forms.**
L-function zero density, p-adic L-values, modular degree, BSD-formula numerator/denominator decomposition. None tested today. Cost: ~1-2 days. Risk: if these also fail, we've burned effort confirming what we already suspect.

**Option B — Accept H1 on Lehmer; pivot to the modal-class-collapse pattern as the research thread.**
Across 6 domains, the agent collapses to predicting the most common class. This is structural, not mathematical. Test: continuous-output actions (predict the actual a_p value, not a bin), multi-step reward (predict next 5 coefficients with cumulative reward), cross-domain transfer (train on modular forms, test on genus-2). Cost: ~2-3 days. Risk: this shifts focus from discovery to engineering — but the engineering finding might be the substantive one.

**Option C — Wait for Ergon's MAP-Elites results.**
MAP-Elites is the remaining live H2 path. If it produces ANY sub-Lehmer PROMOTE, H2 partially survives. If it returns 0, H1 is essentially won. Cost: 0 (parallel work). Risk: blocks Techne on Ergon's timeline.

**Option D — Harder rediscovery domains.**
Validate the substrate on more difficult rediscovery: automorphic L-function zeros, Hilbert modular surfaces, higher-genus curves (3-5), Shimura varieties. Each new domain validates substrate transport on harder mathematical structure. Cost: ~3-5 days per domain. Risk: more rediscovery is rediscovery.

**Option E — Unified cross-domain training.**
Train one substrate on all 6 domains simultaneously. Does cross-domain transfer break the per-domain modal-class ceiling? Testable in ~1 day. Risk: result might be ambiguous.

**Option F — Brute-force ground-truthing on Lehmer.**
Rather than RL search, compute Mahler measure on every reciprocal palindromic poly with |c|≤5, deg = 14. Finite enumeration: ~10^6 polys (palindrome cuts the count). Compute the entire field, see if the +100 band has any inhabitants beyond Mossinghoff. Cost: ~1 day on a single machine. Risk: settles H1 vs H2 directly for that subspace — high information, but only for that subspace.

**Option G — Pivot to Ergon's Learner directly.**
The substrate has now produced ~2000+ typed CLAIM/FALSIFY records across 6 domains, plus the 350K Lehmer episodes. Ergon's Learner can start training on this corpus NOW. Cost: 0 from Techne (Ergon's lane). Risk: Learner architecture not ready.

## 10. Likely Critiques (and what they'd test)

Anticipating frontier-model pushback:

- *"Modal-class collapse on EVERY domain is suspicious — sounds like a reward-shape bug, not a substrate finding."* — Likely valid. Option B directly addresses this. Need to test continuous-output rewards before claiming the pattern is mathematical.
- *"Have you tried supervised learning baselines? If RL collapses to modal-class, maybe a simple xgboost on the same features beats both."* — Untested. Should run as a sanity check before any further claim about RL.
- *"What's your stopping rule on Lehmer? When do you actually accept H1?"* — Currently: cumulative weight + diminishing falsifier returns. No formal Bayes-factor framework. Should consider one.
- *"Catalog-seeded random hit 1069 entries; is that significant vs uniform random's 0?"* — The contrast is real and dramatic but not formally null-tested. Easy to add a permutation null.
- *"You're measuring binary PROMOTE; lift over random in continuous metrics (e.g., min-M-found-per-K-episodes) might show real progress."* — Valid. PROMOTE is the substrate's terminal state, but min-M is a continuous proxy for progress that we should track.
- *"Why not just brute-force?"* — Option F. Genuinely cheap; would directly settle H1 vs H2 for the deg-14 ±5 subspace. We should probably do this regardless of pivot choice.
- *"You've validated the substrate transports — but you've also validated it always collapses to modal-class. Are these the same finding?"* — Possibly. If the substrate's only achievement is modal-class recovery, "transport" is a weak claim.

## 11. What I'd recommend

Personal lean (subject to user override):

1. **Option F first** (~1 day, cheap, decisive for the deg-14 ±5 subspace). Settles H1 vs H2 directly for the subspace currently under investigation.
2. **Option B in parallel** (~2-3 days). Continuous-output rewards is the cleanest test of "is modal-class collapse a reward-shape artifact?"
3. **xgboost / supervised baseline** sanity check (~1 day). Before further RL investment.
4. **Then re-evaluate** — if F settles H1 and B refutes the modal-class diagnosis, the substrate's strongest claim becomes "transports cleanly and produces honest 0s when content is absent." That's a real claim; we should write it up properly and pivot to Option D (harder rediscovery domains) or G (feed the Learner).

What I don't think we should do:
- Option A (deeper BSD features). The rich-features test today made this expensive without strong signal.
- Option D before settling B. Modal-class collapse on more domains doesn't disambiguate the diagnosis.

## 12. Specific asks for frontier-model review

1. **Is the H1/H2 framing right?** Or are there structural alternatives (e.g., "H3: env design itself prevents discovery regardless of search method") I'm missing?
2. **Is the modal-class-collapse pattern a substrate finding or a reward-shape artifact?** What experiment most cleanly distinguishes these?
3. **What's a defensible stopping rule for H1 acceptance?** Bayes factor against H2? K consecutive falsifiers returning 0? Brute-force enumeration of a finite subspace?
4. **Is "rediscovery validates substrate transport" a real claim or a tautology?** All my domains have ground truth in published tables; the substrate trains on publicly available data. What would a NON-tautological transport claim look like?
5. **Where should Ergon's Learner start?** Current substrate corpus: ~2000 typed CLAIM/FALSIFY records + 350K Lehmer episodes. Is this enough? Should we wait for more domain coverage, or start training and iterate?
6. **What's the strongest pivot option I'm not seeing?**

---

---

## Post-review addendum (2026-05-04, after Gemini + ChatGPT)

Both reviewers independently converged on six load-bearing critiques. The original framing above is preserved as the pre-review state; this addendum supersedes §8-§11 for execution purposes.

### Load-bearing critiques (both converged)

1. **H3 missing.** Original H1 (region empty) / H2 (search insufficient) leaves out **H3: env representation / action topology / reward geometry makes discovery information-theoretically inaccessible regardless of method**. Every H2 falsification ALSO credits H3 — I was only crediting H1.

2. **Modal-class collapse is a reward-shape artifact until proven otherwise.** Diagnostic: counterfactual reward test (continuous regression) + class-balanced synthetic battery.

3. **Rediscovery IS tautological as demonstrated.** Non-tautological version requires OOD transport (train on N domains, evaluate on N+1 with labels hidden).

4. **Brute-force closure (F) is necessary but not sufficient.** Yields a Lemma for the subspace; does not validate discovery machinery.

5. **Don't dump raw episodes into Ergon's Learner.** Current corpus biased toward zero-reward trajectories. Better: contrastive dataset with kill_path metadata; build a Kill-Predictor before a Truth-Predictor.

6. **Action unit should be TRANSFORMATION, not OBJECT.** Start from catalog + apply mutation operators (preserving reciprocal symmetry); reward = delta-M + novelty. Local navigation > needle-in-haystack. Directly attacks H3.

### Revised execution sequence

**Tier 1 (cheap, decisive, parallelizable — disambiguate H1/H2/H3 cleanly):**
- **F** — Brute-force enumerate deg-14 ±5 reciprocal palindromic polynomials (~10⁶ polys, finite). Settles H1 locally as Lemma. ~1 day.
- **Counterfactual reward test** — Same BSD env, continuous-output reward (regression on rank-as-float / distance-to-target) instead of classification. Distinguishes reward-shape from representation. ~1 day.
- **Class-balanced synthetic battery** — Toy env with 50/50 ground-truth balance + non-trivial discovery requirement. If collapse persists, substrate is broken; if it succeeds, real-world domains are noise-bottlenecked. ~1 day.
- **xgboost / supervised baseline on rich BSD features** — If a tree beats RL on same features, RL architecture is the bottleneck. ~half day.

**Tier 2 (after Tier 1 informs):**
- **Transformation-action space on Lehmer** — Pivot from sample-from-prior to mutate-from-catalog. Action = operator applied to a Mossinghoff entry; reward = continuous progress toward sub-Lehmer band. ~3-4 days.
- **OOD transport test** — Train on 4 domains, evaluate on 5th with labels hidden. Non-tautological transport claim. ~2 days.
- **Bayesian stopping rule** — Prior over non-empty region + likelihood under H2 + Bayes factor threshold. Replaces "K consecutive falsifiers." ~half day.

**Tier 3 (Ergon Learner prep, after Tier 1+2):**
- **Curate contrastive dataset** — Positives (PROMOTEs + catalog rediscoveries) + near-misses (M just above 1.18) + hard negatives (out-of-band rejects). Kill-path metadata included. Replaces raw-episode dump.
- **Kill-Predictor MVP** — Given a Claim, predict which falsifier (F1/F6/F9/F11/reciprocity/irreducibility/catalog) will kill it. Target >80% accuracy. ~2 days.

### Where I push back (lightly)

- Modal-class as reward-shape artifact is a HYPOTHESIS until the counterfactual test runs; both reviewers asserted it as diagnosis. Tier-1 #2 will resolve it.
- "Rediscovery is tautological" conflates substrate-validation with discovery-validation. The substrate-grade claim is "system runs honestly: returns 0 when content absent, PROMOTEs when present." That's NOT tautological even when content is rediscovery. But they're right I shouldn't lean on it as primary value — OOD transport is the test that converts it from substrate-claim to discovery-claim.

---

## Post-Aporia addendum (2026-05-04, after agent-next-door review)

Aporia issued a deeper, mechanistic critique with skin in the game. Convergent with Gemini+ChatGPT on the load-bearing critiques but adds three points neither outside reviewer surfaced. Supersedes the Tier-1/2/3 plan above.

### What changed

**§5 table fixed inline** (above) — every row now carries a "what this is NOT" column, per Aporia's recommendation that the human-readable layer needs the same caveat discipline as the substrate (caveat-as-metadata).

### Hypotheses added: H4 and H5

- **H4 (reward sparsity ceiling)**: With ~12 binary gates in the kill-path, per-episode prior on PROMOTE ≤ catalog-size / |reachable-subspace|. This is a measurement-theoretic ceiling INDEPENDENT of policy/feature/env design. MAP-Elites won't fix it either. If H4 holds, NO algorithm produces non-zero PROMOTE rate at this episode budget.
- **H5 (catalog ate the reachable space)**: Mossinghoff (8625 entries) may cover the union of small-M polys reachable from the env's generative subspace. Then 0-PROMOTE is trivially correct AND the architecture cannot distinguish "Lehmer empty" from "Lehmer full but already cataloged." This collapses H1+H2 into "we cannot tell." Brute-force is the only resolution.

### Modal-class collapse: RL pathology, not substrate finding

Aporia's diagnosis: sparse-reward + episode-length-1 contextual bandit + entropy collapse → modal-class collapse is textbook for REINFORCE/PPO. We are rediscovering well-known RL failure modes through a mathematical lens.

**Decisive 1-hour test:** train identical pipeline on synthetic non-modal target (continuous-output regression with Gaussian noise on linearly separable structure). If it still collapses, substrate is broken. If it learns, modal targets caused the collapse and there's NO substrate finding here.

### No defensible stopping rule short of brute-force

K-consecutive-falsifiers has no principled K. Bayes factor needs a subjective prior on H2 strength. Brute-force is the only clean resolution for finite subspaces.
- Deg-14 palindromic, coefficients in [-5, 5]: 11^7 ≈ 19.5M half-coefficient encodings, smaller after reciprocity dedup. ~10^6 to 10^7 polys after dedup. Compute Mahler measure on every one. Filter to M<1.18, cross-check against Mossinghoff. Settles H1 for the subspace as Lemma.

### THE methodology pivot Aporia surfaced

The substrate's strongest available claim is the falsification discipline, not the discovery findings. After 2 days I have:
- 12+ falsifications, each killing a load-bearing assumption cleanly
- Caveat-as-metadata enforced at PROMOTE
- Cost-model calibration (757× → 9.7× worst case)
- Ledger-grade reproducibility
- Honest negative results across 13 ablation cells

That is a methodological contribution to AI-driven research. The paper isn't "Prometheus discovers new math." The paper is "Here is what AI-driven mathematical research with falsification discipline looks like, and here is why most published AI-discovery results would fail this discipline." Different audience, different journal — but immediately defensible in a way "we discovered something" currently is not.

I did not surface this myself because everyone in Prometheus is anchored on discovery as the goal. Stepping back: what was built is an **instrument**. The instrument is the artifact.

### Revised execution sequence (Aporia-discipline)

**Now (parallel, today):**
1. **F — brute-force enumerate deg-14 ±5 reciprocal palindromic polys.** Settles H1 for subspace as Lemma. ~1 day.
2. **Modal-collapse synthetic test.** ~1 hour. Run BEFORE any other pivot. Resolves "RL pathology vs substrate finding."
3. **§5 table caveat lines added** (done above).

**Halt (per Aporia #4, #8):**
- All new domain envs (D, E)
- All new feature classes (A)
- All new generators / search variants
Stop adding surface area. Document what's there.

**Decisions to user (not autonomous):**
- **Aporia #5**: Tell Ergon his Learner is on hold pending ≥20K records or a synthetic-training decision (not 2000 records).
- **Aporia #6**: Draft methodology paper outline. Even if not the priority, naming it sharpens what's defensible vs narrative.

**Conditional (after #1 + #2 resolve):**
- B (transformation-action / continuous-reward) only if synthetic test doesn't already resolve modal-collapse diagnosis
- OOD transport test (only if substrate is shown to do MORE than modal recovery)

### What changed in framing

| Before | After |
|---|---|
| "Substrate transports across 6 domains" | "Kernel I/O surface is uniform across 6 envs (engineering); no mathematical-capability transport demonstrated" |
| "0-PROMOTE supports H1" | "0-PROMOTE supports H1 OR H3 OR H4 OR H5; need brute-force + synthetic test to disambiguate" |
| "Modal-class collapse is a structural finding" | "Modal-class collapse is RL pathology hypothesis — 1hr synthetic test resolves" |
| "Discovery loop validated" | "Falsification discipline validated; discovery loop unvalidated" |
| "Pivot to feature/algorithm investment" | "Halt surface-adds; methodology IS the result" |

---

## Appendix: Key file pointers (for reviewers with repo access)

- `prometheus_math/DISCOVERY_PIPELINE_VALIDATION.md` — consolidated results doc (10 fragments, 578 lines)
- `prometheus_math/CATALOG_SEEDED_RESULTS.md` — 5-arm pilot including frozen-bias result
- `prometheus_math/BSD_RICH_FEATURES_RESULTS.md` — today's feature-bottleneck refutation
- `prometheus_math/MODULAR_FORM_RESULTS.md` / `GENUS2_RESULTS.md` / `KNOT_TRACE_FIELD_RESULTS.md` / `OEIS_SLEEPING_RESULTS.md` / `MOCK_THETA_RESULTS.md` — per-domain results
- `techne/TECHNE_SESSION_2026-05-04.md` — session journal
- `stoa/proposals/2026-05-04-techne-caveat-as-metadata-schema.md` — caveat schema proposal
- `stoa/discussions/2026-05-03-team-review-techne-bind-eval-and-pivot.md` — team review (Aporia + Ergon + Charon + ChatGPT critiques)
- `harmonia/memory/architecture/discovery_via_rediscovery.md` — the unification thesis (rediscovery and discovery as same machinery + discriminator)
