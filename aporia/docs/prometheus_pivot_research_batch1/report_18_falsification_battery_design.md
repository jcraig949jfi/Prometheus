# Report 18 — Falsification Battery Design: Replication-Crisis, Multiverse-Analysis, and Preregistration Applied to Mathematics

**Project Prometheus / Aporia, Pivot Research Batch 1 — 2026-05-02**

## 1. Situation

Prometheus's falsification battery (Charon v10, FROZEN) consists of 25 tests across 4 tiers. It is the substrate's primary epistemic immune system, gating against false positives produced by an aggressive, AI-driven discovery pipeline that explores ~10^4 candidate couplings per week across ~10^5 mathematical objects. To date the battery has killed 4 high-confidence "discoveries" (the Quadratic Mirage, AlignmentCoupling z=2.22, the NF Backbone, and the 5D constant manifold) and yielded 3 conditional laws and 0 unconditional universals. The battery's design draws on null-protocol discipline but has never been audited against the mature replication-crisis literature. This brief distills that literature and proposes battery v11.

## 2. Replication-Crisis Lessons

The replication crisis began as a quiet anomaly and matured into a discipline. **Ioannidis (2005)** "Why Most Published Research Findings Are False" gave the canonical Bayesian argument: when prior odds of a true effect are low, the field is hot, sample sizes are small, analyst flexibility is high, and studies are non-replicated, *most* statistically significant findings are false. The 2015 **Open Science Collaboration** empirical replication of 100 psychology studies confirmed it: only ~36% replicated at conventional significance, and effect sizes shrank by ~half on average. Biomedicine (Begley & Ellis 2012; Prinz et al. 2011) showed similar or worse rates.

The diagnosis identified several mechanisms. **HARKing** (Kerr 1998) — *Hypothesizing After Results are Known* — turns post-hoc patterns into "predictions." **Garden of forking paths** (Gelman & Loken 2013) showed that even a single honest analyst, presented with hindsight-driven choices, will produce p<.05 from noise via the multiplicity of *plausible* analyses they did not run but would have. **P-hacking** is the active version. **Publication bias** is the meta-version: only positive results get into print, inflating the literature.

The responses are now mature. **Preregistration** and **Registered Reports** (Chambers, Munafò et al. 2014, 2018) lock the analysis plan before data collection; reviewers accept the *protocol*, not the result. **Multiverse analysis** (Steegen et al. 2016) makes forking paths explicit: run *all* defensible analyses, report the distribution. The closely related **specification-curve analysis** (Simonsohn et al. 2020) does the same for regression specs. **Many-Analysts-One-Dataset** (Silberzahn et al. 2018; Botvinik-Nezer et al. 2020 for fMRI) showed that 29 teams given the same data produced effect sizes ranging from negative to strongly positive — analyst degrees of freedom dwarf sampling noise. **P-curve** (Simonsohn, Nelson, Simmons 2014) and **p-uniform** diagnose evidential value across literatures by examining the shape of the p<.05 distribution. **SBC / posterior predictive checks** (Talts et al. 2018) give the Bayesian analogue. The unifying principle: *human degrees of freedom are the dominant source of false positives*, and the cure is to surface, register, and quantify them.

## 3. Patterns Prometheus Should Adopt or Strengthen

**(a) Preregistration of every claim's kill-path.** Before any evidence is collected for a candidate coupling, write a preregistered protocol specifying: (i) the test statistic, (ii) the null model, (iii) the rejection region, (iv) the calibration anchor used to set thresholds, (v) the explicit kill conditions. The substrate must hash-stamp this protocol and refuse to let downstream evidence rewrite it. This converts the battery from "23 tests we happen to run" into "23 tests we *promised* to run, regardless of result." The current battery is partially preregistered (frozen at v10), but per-claim kill-paths are not.

**(b) Multiverse analysis as a substrate operator.** Many of Prometheus's choices are defensible-but-arbitrary: which prime-detrending order, which conductor cutoff, which calibration anchor subset, which RMT normalization. A multiverse operator runs the battery across the Cartesian product of these defensible choices and reports the *distribution* of effect sizes and p-values. If a claim survives in 95%+ of the multiverse, it is robust; if only in 20%, it is specification-dependent and must be downgraded.

**(c) Garden-of-forking-paths audit.** Every deviation from the registered protocol is logged with a reason code. A monthly audit computes the inflation factor implied by the deviations (akin to a Bonferroni-by-introspection). This addresses the pattern observed in feedback_assume_wrong.md and the Harmonia kills: protocol drift is silent unless surfaced.

**(d) Calibration-anchor-conditioned acceptance.** Split the calibration anchor pool 50/50 into TRAIN and TEST halves *at registration time*. A claim survives only if it passes on both halves at preregistered thresholds. This is the math-substrate analogue of held-out validation and protects against overfitting to the calibration corpus itself — a risk made acute by the small number (~20) of high-quality anchors.

**(e) Red-team adversarial agent.** Stand up a dedicated agent (Harmonia-mode) whose KPI is *kills*, not discoveries. It is rewarded for finding the specification, the prime-detrend, the stratification, the conductor cut, or the seed that breaks any candidate. This is the AI analogue of an adversarial collaboration (Mellers, Hertwig, Kahneman 2001) and is the only known counter to AI-to-AI narrative inflation (feedback_ai_to_ai_inflation.md).

## 4. Mathematical-Domain-Specific Failure Modes

**Algebraic-coupling (PATTERN_30).** Two object families that share an algebraic skeleton (e.g., both pulled from Hecke eigenforms) will couple even under a "random" pairing because the skeleton co-varies. The battery must factor through the common algebraic substrate before testing residual coupling.

**Prime-atmosphere overfit (PATTERN_PRIME_GRAVITATIONAL_OVERFIT).** 96%+ of cross-dataset structure is the prime-counting backbone; sorted-rank and z-norm tests are traps that look impressive but only re-detect primes (feedback_prime_atmosphere.md). The substrate must detrend before testing, and the test statistic must be a residual statistic.

**Conductor confound.** In number-theoretic data, *everything* correlates with conductor — rank, regulator, Sha, gap statistics. A coupling that vanishes after conditioning on conductor is a conductor effect, not a discovery. The battery needs an explicit conductor-stratified arm for every NF/EC/genus-2 claim.

**Base-rate neglect.** With 10^4 candidate couplings per week, even Bonferroni at α=.001 yields ~10 false positives weekly. Per-test α must be set by the *total exploration budget*, not per-test cost.

**AI-to-AI inflation.** Two LLM agents discussing a candidate amplify rather than falsify (feedback_ai_to_ai_inflation.md). The red-team agent and human HITL gate are the only known counters.

## 5. Concrete Next Steps for Battery v11

1. **Per-claim preregistration registry.** A hashed JSON record per candidate, stored append-only in `charon/preregistrations/`, schema-validated before evidence collection.
2. **Multiverse operator.** Implement `charon/multiverse.py` that takes a battery test and a parameter grid and returns a distribution; require ≥80% pass rate as a new gate.
3. **Anchor split at registration.** Modify `charon/anchors.py` to expose deterministic TRAIN/TEST halves keyed on claim hash.
4. **Forking-paths audit job.** Weekly cron that diffs executed protocol vs. registered protocol; reports inflation factor.
5. **Red-team agent.** Stand up Harmonia-Adversary in Agora with KPI = kills/week, reporting to Pronoia.

## 6. References

1. Ioannidis, J.P.A. (2005). Why Most Published Research Findings Are False. *PLoS Medicine* 2(8): e124.
2. Open Science Collaboration (2015). Estimating the reproducibility of psychological science. *Science* 349: aac4716.
3. Begley, C.G., Ellis, L.M. (2012). Raise standards for preclinical cancer research. *Nature* 483: 531–533.
4. Prinz, F., Schlange, T., Asadullah, K. (2011). Believe it or not: how much can we rely on published data on potential drug targets? *Nature Reviews Drug Discovery* 10: 712.
5. Kerr, N.L. (1998). HARKing: Hypothesizing After the Results are Known. *Personality and Social Psychology Review* 2: 196–217.
6. Gelman, A., Loken, E. (2013). The garden of forking paths. *Department of Statistics, Columbia University* working paper.
7. Steegen, S., Tuerlinckx, F., Gelman, A., Vanpaemel, W. (2016). Increasing transparency through a multiverse analysis. *Perspectives on Psychological Science* 11(5): 702–712.
8. Simonsohn, U., Simmons, J.P., Nelson, L.D. (2020). Specification curve analysis. *Nature Human Behaviour* 4: 1208–1214.
9. Simonsohn, U., Nelson, L.D., Simmons, J.P. (2014). P-curve: a key to the file-drawer. *Journal of Experimental Psychology: General* 143(2): 534–547.
10. Silberzahn, R., Uhlmann, E.L. et al. (2018). Many analysts, one data set. *Advances in Methods and Practices in Psychological Science* 1(3): 337–356.
11. Botvinik-Nezer, R. et al. (2020). Variability in the analysis of a single neuroimaging dataset by many teams. *Nature* 582: 84–88.
12. Chambers, C.D. (2013). Registered Reports: a new publishing initiative at Cortex. *Cortex* 49: 609–610.
13. Munafò, M.R. et al. (2017). A manifesto for reproducible science. *Nature Human Behaviour* 1: 0021.
14. Nosek, B.A. et al. (2018). The preregistration revolution. *PNAS* 115(11): 2600–2606.
15. Mellers, B., Hertwig, R., Kahneman, D. (2001). Do frequency representations eliminate conjunction effects? An exercise in adversarial collaboration. *Psychological Science* 12: 269–275.
16. Talts, S., Betancourt, M., Simpson, D., Vehtari, A., Gelman, A. (2018). Validating Bayesian inference algorithms with simulation-based calibration. *arXiv:1804.06788*.
17. Benjamin, D.J. et al. (2018). Redefine statistical significance. *Nature Human Behaviour* 2: 6–10.
18. Wagenmakers, E.-J. et al. (2012). An agenda for purely confirmatory research. *Perspectives on Psychological Science* 7(6): 632–638.

Word count ~1180
