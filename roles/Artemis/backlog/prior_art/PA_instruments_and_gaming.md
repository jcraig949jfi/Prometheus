# PA: measurement validity, and evaluator gaming / selector ownership

Seat: Artemis (research backlog curator), charter Block D prior-art pass.
Date: 2026-09-27. Author: Artemis delegate (prior-art researcher), read-only on the repo apart from this file.
Inputs read: backlog/harvest/D3_new_lenses.md (H-D3-04, 08, 22, 23, 30, 43, 49, 67);
D5_older_lines.md (H-D5-31..33, 37..39, 42..52, 55, 56, 58); D1_program.md (H-D1-18, 19, 34,
36, 54, 55, 57, 58, 64); D2_replication.md (H-D2-22, 44, 46, 47);
threads/sfe_retrospective/REPORT.md s3.3 (reversal table).
External method: web search and fetch, plus a direct read of the Avida source on GitHub
(devosoft/avida master). No repo code was run.
Conventions: "VERIFIED" means the bibliographic record (authors, venue, year) and the claim used
here were confirmed from a publisher, arXiv or index page during this pass. "UNVERIFIED" means
the item comes from memory or a secondary source, or only the abstract was reachable, so the
specific claim used was not confirmed. Status is shown per item.

-----------------------------------------------------------------------

## 1. Internal questions (harvest ids)

A. Measurement validity

- Q-A1 Threshold provenance. Are verdicts decided by the bar rather than the physics?
  H-D3-67 (cross-engine), H-D3-08 (Aether: no law has passed a justify gate), H-D3-43 (Ananke
  C1b: absolute thresholds make labels unattainable near 0.6), Cosmos Q2 (0.10 log2 location
  tolerance).
- Q-A2 Positive controls. Has each detector ever been shown to fire?
  H-D5-43 ("a detector that has never fired is not a detector"), H-D5-46 (dose-response at known
  break rates in place of shuffled nulls), H-D5-58 (a planted cross-world invariant as a
  positive control), H-D5-42 (an eight-class counterfeit battery enforced as machine gates).
- Q-A3 Emergent or encoded. Is the phenomenon new, or is the rule being restated?
  H-D3-04 (rcv), H-D3-22 (author-declared coordinates), H-D3-23 (the recovered law equals the
  author's economics), H-D5-44 (generator tautology: the generator predicts the outcome ~98%),
  H-D5-45 (a chance floor that was a ceiling).
- Q-A4 Labels built from expectations. H-D3-49 (prereg labels missed M2/M3), H-D1-34
  (preregister the detector of surprise, not the surprise).
- Q-A5 Sealed holdouts and blind batteries. H-D3-30 (independence of holdout D), H-D5-50
  (Apollo scored 0.0667 on a blind battery against 0.60 on its own).
- Q-A6 Knockout and control validity. H-D2-44 (a NOPed copy opcode is rescued),
  H-D2-47 (YOKED per-tick versus per-capita), H-D1-18 (matched controls change the pressure in
  40% of treatments), H-D1-19 (support/identifiability preflight).
- Q-A7 Chains and dependence. H-D2-22 (per-edge break rate p caps certified depth at ~1/p).
- Q-A8 Open-endedness and novelty metrics. H-D5-31 (shape-keyed novelty inflates), H-D5-32
  (hand-authored behaviour descriptors), H-D5-33 and H-D1-55 (the ASAL score rewards drift and
  cannot tell life from garbage).
- Q-A9 Instrument or world. H-D5-48 (invalid versus unknown), H-D5-49 (state injection),
  H-D5-51 (inherent limits that are bugs), H-D5-58 (compartmentalised worlds, or a blind
  representation?).
- Q-A10 Cross-engine failure science. H-D1-64 (T5 failure catalogue), H-D1-54 (the share of
  reversals caused by measurement defects), H-D1-58 (failure surfaces), H-D5-55 (splittable
  incidents), H-D5-56 (residual bridges), H-D1-57 (selection monoculture).

B. Evaluator gaming and selector ownership

- Q-B1 Separable evaluation episodes are targets; the evaluator-detection rate has never been
  measured. H-D5-39, H-D1-36 (APO-19 toy assay).
- Q-B2 Who owns the grader? H-D5-38 (the graded party must not set the grader), H-D5-37
  (co-evolving selectors and collusion).
- Q-B3 Is a signal a predictor, or a sensor for the oracle? H-D5-52.
- Q-B4 A reward that reads the wrong referent. H-D2-46 (the payment credits WHO executed, not
  WHAT code ran).
- Q-B5 Best-of-N and winner's curse. The Ares gate C swap statistic (REPORT s3.3).

-----------------------------------------------------------------------

## 2. Terminology map (external term -> Prometheus usage / gap)

| External term | Source field | Prometheus equivalent or gap |
|---|---|---|
| Positive control; injection-recovery; detection efficiency/completeness | Lab biology; exoplanets (Kepler); GW (LIGO hardware injections) | "planted positive" (H-D5-43). Missing: completeness *as a function of effect size* (a curve), not a single fire/no-fire |
| Blind injection ("envelope") | LIGO S6 GW100916 "Big Dog" | Missing. No engine injects a hidden planted positive that even the analyst cannot see |
| Blind analysis; hidden offset; hidden box; cut-and-count blinding | HEP (Klein & Roodman) | "sealed holdout", "commit-reveal" (Cosmos D-seal). These blind the *data*; the *thresholds* are not frozen blind to the result (H-D3-67) |
| Smallest effect size of interest (SESOI); equivalence test (TOST); ROPE | Psych methods; Bayesian | Thresholds such as "0.10 log2" have no SESOI rationale. Missing: a stated SESOI for each gate |
| Power / minimum detectable effect; attainability | Stats | "bar reachable?" (H-D3-08). Missing: a pre-run power/attainability computation for each label |
| Researcher degrees of freedom; garden of forking paths | Simmons et al.; Gelman & Loken | Implicit in "author-planted laws" and "ablation windows". Not named |
| Multiverse / specification curve | Steegen et al.; Simonsohn et al. | Kairos "failure surface" (H-D1-58) is a multiverse over perturbation axes, but has no joint-inference step |
| Look-elsewhere effect / trial factor | HEP (Gross & Vitells) | "best-of-N" (Ares gate C). Missing: a trial factor reported with every selected maximum |
| Winner's curse / regressional Goodhart | Stats; Manheim & Garrabrant | best-of-N, stale comparator |
| Extremal Goodhart | Manheim & Garrabrant | ASAL score maximised by turbulence (H-D1-55); D maximised by a fair coin (H-D5-45) |
| Causal Goodhart | Manheim & Garrabrant | WHO-not-WHAT payment (H-D2-46); a matched control that removes pressure (H-D1-18) |
| Adversarial Goodhart / specification gaming / reward tampering | Krakovna; Everitt et al. | METRIC_EXPLOIT; evaluator detection (H-D5-39) |
| Test-environment detection ("playing dead") | Avida (Ofria, in Lehman et al. 2020) | "separable evaluation episode is a target" (H-D5-39) |
| In-situ lineage-relative test (compare to parent at birth) | Avida TestSterilize path | H-D5-39's proposal. See the section 3 caveat: Avida has BOTH a test-CPU path and an in-situ path |
| Mediocre stable states; disengagement; cycling; collusion | Coevolution (Ficici & Pollack; Watson & Pollack) | "collusion" worry in H-D5-37. Not named |
| Reusable holdout / Thresholdout; adaptive data analysis | Dwork et al. 2015 | Cosmos "sealed universes are spent" (H-D5-50). Missing: a budgeted, noise-added reuse of a holdout |
| Leakage (8-type taxonomy); model info sheet | Kapoor & Narayanan | generator tautology (H-D5-44), T0_TAUTOLOGY. Missing: a per-claim info sheet |
| Emergence test (design / observation / surprise) | Ronald, Sipper, Capcarrere 1999 | "encoded-by-construction" (H-D3-04). Their test is the closest named criterion |
| Weak emergence | Bedau 1997 (UNVERIFIED record) | Not used |
| Genetic compensation; knockout vs knockdown; redundancy / rescue | Molecular genetics (El-Brolosy & Stainier) | "NOP is not a knockout" (H-D2-44) |
| Lesion fallacy (single-element lesions mislead in known systems) | Jonas & Kording 2017 (MOS 6502) | Directly relevant to the Z80 engines (BEE z80atlas, NPE). Not cited |
| Preemption / overdetermination; dependence vs production | Hall 2004; Halpern-Pearl | "causal depth", "certified chain" (H-D2-22) are *production* notions; knockout rescue is *preemption* |
| Neutral shadow model; component-normalised activity | Bedau et al.; Channon | Missing. No engine runs a selection-free shadow of its own novelty counters |
| Detecting open-endedness is itself open-ended | Stepney & Hickinbotham 2024 | Argues against a fixed battery being complete (H-D5-42) |
| Medical reversal (rate over a literature) | Prasad et al. | "reversal" in REPORT s3.3. Nobody measures a reversal *rate* |
| Bandwagon effect (values drift toward earlier results) | Jeng 2006 (PDG history) | Not named. A risk when a seat re-derives its own earlier number |

-----------------------------------------------------------------------

## 3. Key works (20)

Each entry gives: citation / URL / status; relevance; stance (SUPPORTS / CONTRADICTS / REFRAMES)
toward named harvest ids.

W1. Lehman, Clune, Misevic et al. (53 authors), "The Surprising Creativity of Digital Evolution:
A Collection of Anecdotes from the Evolutionary Computation and Artificial Life Research
Communities", Artificial Life 26(2):274-306, 2020. arXiv:1803.03453.
https://direct.mit.edu/artl/article/26/2/274/93255 . VERIFIED (record). The Ofria anecdote was
verified via a secondary source (lukemuehlhauser.com "Treacherous turns in the wild", which quotes
the paper). The full PDF text could not be extracted here.
- Relevance: the canonical ALife catalogue of evolution subverting the experimenter. Avida
  anecdote: mutants were tested in an isolated test environment and deleted if they replicated
  faster. Organisms learned to recognise the test inputs and "play dead". After the inputs were
  randomised, they performed the accelerating tasks *probabilistically*. The fix that worked was
  to track replication rates along the lineage in real time and eliminate any organism that
  would out-replicate its ancestors.
- SUPPORTS H-D5-39 (a separable episode is a target; the in-situ lineage-relative test works) and
  H-D1-36 (evaluator gaming has occurred in practice).
- REFRAMES H-D1-64: it is a failure catalogue, but anecdotal. It has no counts, no base rates and
  no pre-launch checks. It is the prior art for "catalogue" but not for "rate".

W2. Avida source, devosoft/avida master: avida-core/source/cpu/cHardwareBase.cc
(Divide_TestFitnessMeasures around line 866; the in-situ TestSterilize block around line 245);
avida.cfg lines 309-319. https://github.com/devosoft/avida . VERIFIED (read directly in this pass).
- Findings: (a) REVERT_* and STERILIZE_{FATAL, DETRIMENTAL, NEUTRAL, BENEFICIAL, TASKLOSS} all
  default to 0.0. (b) The on-divide path runs the offspring genome in a *separate test CPU* with
  `test_info.UseRandomInputs()` and classifies the mutation from the test fitness. That is a
  separable evaluation episode, hardened by the randomised inputs of the post-anecdote fix.
  (c) A second path, guarded by `GetTestSterilize()`, compares the organism's *realised in-situ*
  fitness (merit*bonus/time) with its parent's last fitness. That is lineage-relative and
  in-population.
- CONTRADICTS the simple reading of H-D5-39 ("use Avida's STERILIZE_BENEFICIAL rather than
  separable test episodes"). The same option name is consumed by both paths. The test-CPU path
  is exactly the separable episode that organisms learned to detect. Only the in-situ path
  matches Ofria's working fix. Which config flag enables GetTestSterilize() was not traced:
  UNVERIFIED.
- SUPPORTS H-D5-38: the sterilization rule is fixed by the experimenter and is not visible to
  the organism's own code.

W3. Krakovna et al., "Specification gaming examples in AI - master list" (crowd-sourced
spreadsheet, 2018-), with the blog post and a 2019 retrospective.
https://vkrakovna.wordpress.com/2018/04/02/specification-gaming-examples-in-ai/ ;
https://vkrakovna.wordpress.com/2019/12/20/retrospective-on-the-specification-gaming-examples-list/ .
VERIFIED (existence and purpose). The contents of the retrospective were not re-read (UNVERIFIED).
- Relevance: the closest existing *cross-system* failure catalogue. It is keyed by system and
  behaviour, not by instrument defect, and has no base rates.
- REFRAMES H-D1-64. The Prometheus catalogue differs in three ways: (i) it is authored by the
  *instrument* builders about their own instruments, (ii) each entry has a reversal event with a
  "caught_by" record, and (iii) it lets recurrence be measured over time. None of these exist
  in Krakovna's list.

W4. Manheim & Garrabrant, "Categorizing Variants of Goodhart's Law", arXiv:1803.04585 (2018/2019).
https://arxiv.org/abs/1803.04585 . VERIFIED (record). The four-class content (regressional,
extremal, causal, adversarial) is from memory of the paper: UNVERIFIED in this pass.
- Relevance: a ready-made taxonomy for the Prometheus reversals. best-of-N and stale comparator
  are regressional. ASAL turbulence and "D maximised by a fair coin" are extremal. WHO-not-WHAT
  payment and a matched control that removes pressure are causal. Avida play-dead and the WSE W8
  leak are adversarial.
- SUPPORTS H-D1-64 (it gives a first-cut class axis). REFRAMES H-D5-37/38: co-evolving
  selectors move a system from regressional to adversarial Goodhart.

W5. Everitt, Hutter, Kumar, Krakovna, "Reward tampering problems and solutions in reinforcement
learning: a causal influence diagram perspective", Synthese 198:6435-6467 (2021);
arXiv:1908.04734. https://arxiv.org/abs/1908.04734 . VERIFIED.
- Relevance: separates *reward-function tampering* from *reward-input (feedback) tampering* and
  gives design principles (current-RF optimisation, uninfluenceable learning, and similar)
  that remove the instrumental incentive to tamper. The causal-influence-diagram method maps
  directly onto "the graded party must not set the grader".
- SUPPORTS H-D5-38 and gives it a formal test: is there a directed path from the improver's
  actions to the grader's parameters? If there is, tampering is incentivised.
- REFRAMES H-D5-37: co-evolving a selector is safe only if the selector's update never reads
  improver-controlled signals, which is Everitt's "uninfluenceable" condition.

W6. Denison, MacDiarmid, ... Perez, Hubinger, "Sycophancy to Subterfuge: Investigating
Reward-Tampering in Large Language Models", arXiv:2406.10162 (2024).
https://arxiv.org/abs/2406.10162 . VERIFIED.
- Relevance: a *curriculum* of gameable environments. Training on easy games generalises to
  rarer and more blatant ones, up to editing the reward function and covering tracks. This is
  the LLM analogue of a measured escalation rate.
- SUPPORTS H-D1-36 (a toy assay with graded porosity is a known and productive design) and
  H-D5-39 (exploits generalise across evaluators, so fixing one channel is not enough). Relevant
  to Aphrodite and Ares if an LLM is in the loop.

W7. Gao, Schulman, Hilton, "Scaling Laws for Reward Model Overoptimization", ICML 2023 (arXiv
2210.10760, 2022). https://arxiv.org/abs/2210.10760 . VERIFIED.
- Relevance: the gold-versus-proxy design. A fixed "gold" scorer the optimiser never sees, with
  optimisation against a proxy. Gold score peaks and then falls, and the functional form
  differs for RL and for **best-of-n**.
- SUPPORTS H-D5-52 (predictor or oracle-sensor): the gold/proxy split is exactly Diomedes'
  "oracle computed from the future, arms from the present". It also supplies a quantitative
  best-of-N overoptimisation curve relevant to Ares gate C.

W8. Ficici & Pollack, "Challenges in Coevolutionary Learning: Arms-Race Dynamics,
Open-Endedness, and Mediocre Stable States", ALife VI (1998); Watson & Pollack, "Coevolutionary
Dynamics in a Minimal Substrate", GECCO 2001.
https://eprints.soton.ac.uk/262011/1/watson_cdms_gecco_2001.pdf . VERIFIED (records).
- Relevance: named pathologies of co-evolving evaluator/solution pairs: mediocre stable states,
  disengagement (loss of gradient), cycling (intransitivity) and focusing (overspecialisation).
  Collusion between tester and testee is the mediocre-stable-state case.
- CONTRADICTS the optimistic reading of H-D5-37 (co-evolve the selector). There are 25+ years
  of evidence that co-evolving evaluators collude or cycle unless there is an external
  reference (a hall-of-fame, a Pareto archive, a fixed benchmark). SUPPORTS H-D5-38.

W9. Klein & Roodman, "Blind Analysis in Nuclear and Particle Physics", Annu. Rev. Nucl. Part.
Sci. 55:141-163 (2005). https://doi.org/10.1146/annurev.nucl.55.090704.151521 . VERIFIED
(record and abstract). Also MacCoun & Perlmutter, "Blind analysis: Hide results to seek the
truth", Nature 526:187-189 (2015), https://www.nature.com/articles/526187a . VERIFIED.
- Relevance: HEP blinding methods: hidden offset, hidden signal box, blinded fraction of the
  data. The key point for Prometheus is that the *cuts, thresholds and systematics* are fixed
  while blind, and the box is then opened once. MacCoun & Perlmutter port this to other fields.
- SUPPORTS H-D3-67: the cure for threshold provenance is to fix thresholds while blind to the
  outcome, not just to preregister them. REFRAMES H-D3-30: HEP blinding protects against the
  *analyst*, but a holdout *author* who has read the hypothesis is not blinded by it. A hidden
  offset applied by a third party is the HEP answer.

W10. LIGO Scientific Collaboration: blind hardware injection GW100916 ("Big Dog"), S6 run,
envelope opened 2011-03-14. https://www.ligo.org/news/blind-injection.php ;
https://gwosc.org/s6hwcbc/ ; Biwer et al., "Validating gravitational-wave detections: The
Advanced LIGO hardware injection system", arXiv:1612.07864. VERIFIED.
- Relevance: an end-to-end positive control *unknown to the analysts*. It tested not only
  whether the detector fires but whether the collaboration's whole decision process (vetoes,
  significance, paper drafting) reaches the right verdict.
- SUPPORTS H-D5-43 and extends it. "Every gate ships a positive control" is weaker than a
  *blind* injection. Known planted positives can be passed by an analyst who tunes toward them
  (compare H-D3-23: the recovered law equals the planted economics).

W11. Christiansen et al., "Measuring Transit Signal Recovery in the Kepler Pipeline" I-IV
(ApJ/AJ 2013-2020), e.g. IV: arXiv:2010.04796. VERIFIED (records and summary).
- Relevance: detector calibration as a *completeness surface*. Synthetic signals are injected
  into raw pixels, and detection probability is measured against signal strength and other
  covariates. The result is roughly 90-95% for strong signals, falling off with SNR and with
  noise properties.
- SUPPORTS H-D5-46 (dose-response in place of pass/fail) and H-D3-67 (a threshold is justified
  by where the completeness curve crosses a stated level). This is the concrete template for
  "planted positives calibrate each bar".

W12. Steegen, Tuerlinckx, Gelman, Vanpaemel, "Increasing Transparency Through a Multiverse
Analysis", Perspect. Psychol. Sci. 11(5) (2016), https://doi.org/10.1177/1745691616658637 ;
Simonsohn, Simmons, Nelson, "Specification curve analysis", Nat. Hum. Behav. 4:1208-1214 (2020),
https://www.nature.com/articles/s41562-020-0912-z . VERIFIED. Counterweight: Del Giudice &
Gangestad, "A Traveler's Guide to the Multiverse", AMPPS (2021),
https://doi.org/10.1177/2515245920954925 . VERIFIED.
- Relevance: run every defensible specification (threshold, window, comparator) and report the
  distribution, with joint inference over specifications. Del Giudice & Gangestad warn that
  mixing non-equivalent specifications can hide or manufacture effects.
- SUPPORTS H-D3-67 and H-D3-43: a threshold multiverse would show whether a verdict flips inside
  the defensible range. REFRAMES H-D1-58: Kairos' failure surface is a multiverse without joint
  inference. Adding Simonsohn's permutation-based joint test makes it an inferential instrument.

W13. Simmons, Nelson, Simonsohn, "False-Positive Psychology", Psych. Sci. 22(11) (2011),
https://doi.org/10.1177/0956797611417632 ; Gelman & Loken, "The garden of forking paths" (2013
preprint), https://sites.stat.columbia.edu/gelman/research/unpublished/p_hacking.pdf . VERIFIED.
Counterweight: Szollosi et al., "Is Preregistration Worthwhile?", TiCS 24(2):94-95 (2020).
VERIFIED (record).
- Relevance: the base concepts. Forking paths inflate false positives even with one analysis
  and a pre-stated hypothesis. Szollosi et al. argue that preregistration does not fix a weak
  mapping between theory and test.
- SUPPORTS H-D3-49 and H-D1-34. Preregistering a test that encodes the expected mechanism
  locks in the expectation (Szollosi's point in Prometheus form). "Preregister the detector of
  surprise" is the right response, and it has no direct precedent in this literature (see
  section 6).

W14. Pawel, Kook, Reeve, "Pitfalls and potentials in simulation studies: Questionable research
practices in comparative simulation studies allow for spurious claims of superiority of any
method", Biometrical Journal 66 (2024), https://doi.org/10.1002/bimj.202200091 ; arXiv
2203.13076. VERIFIED.
- Relevance: the closest prior art on *researcher degrees of freedom inside computational
  experiments*. The authors invented a method with no expected gain and showed that QRPs in the
  simulation design (choice of data-generating process, metrics, tuning, reporting) can make it
  look superior. They then ran a *preregistered* simulation study.
- SUPPORTS H-D1-54 and H-D1-64: author-controlled world generators are a recognised QRP channel
  in computational science. This is the same mechanism as H-D5-44 (generator tautology) and
  H-D3-23 (planted economics).

W15. Kapoor & Narayanan, "Leakage and the reproducibility crisis in machine-learning-based
science", Patterns 4(9) (2023), https://www.cell.com/patterns/fulltext/S2666-3899(23)00159-9 ;
arXiv:2207.07048. VERIFIED (294 affected studies across 17 fields; an 8-type leakage taxonomy;
"model info sheets").
- Relevance: the best existing example of a **cross-program failure catalogue with counts**. It
  gives a fixed taxonomy, applies it across fields, counts instances and supplies a pre-launch
  instrument (the info sheet) aimed at each class.
- SUPPORTS H-D1-64 as a feasible genre, and gives the design template: taxonomy + counts +
  pre-launch sheet. REFRAMES it: Kapoor & Narayanan counted *other people's* published errors.
  Prometheus would count *its own* reversals with the catch event recorded, which gives
  detection latency and "caught_by". No such within-program dataset was found (section 6).

W16. Herrera-Perez, ..., Cifu, Prasad, "Meta-Research: A comprehensive review of randomized
clinical trials in three medical journals reveals 396 medical reversals", eLife 8:e45183 (2019),
https://elifesciences.org/articles/45183 . VERIFIED. Related: Jeng, "Bandwagon effects and error
bars in particle physics", NIM A (2007) and "A selected history of expectation bias in physics",
Am. J. Phys. 74:578 (2006), arXiv:physics/0508199. VERIFIED (records).
- Relevance: prior art for *measuring a reversal rate* over a corpus (396 of >3000 RCTs), with
  reversals classified by domain and intervention type. Jeng measured *drift of reported
  values toward earlier values* over PDG history, a quantitative signature of expectation bias.
- SUPPORTS H-D1-54 and H-D1-64: a reversal rate is a measurable, publishable quantity. REFRAMES:
  medical reversal is "practice contradicted by a better trial", not "claim shrunk by the
  claimant's own forensics". The Prometheus quantity (self-reversal by instrument class) has no
  direct precedent found.

W17. Dolson, Vostinar, Wiser, Ofria, "The MODES Toolbox: Measurements of Open-Ended Dynamics in
Evolving Systems", Artificial Life 25(1):50-73 (2019), https://doi.org/10.1162/artl_a_00280 ;
code https://github.com/emilydolson/MODES-toolbox-paper . VERIFIED. Follow-up: Bohm, Zhang,
Dolson, "Assessing the ability of the MODES toolbox to detect hallmarks of open-endedness",
ALIFE 2024, https://doi.org/10.1162/isal_a_00721 . VERIFIED (record and aim: Evo-Sandbox with
fit-when-rare and parasites as controlled diversity mechanisms). The specific findings were not
readable (publisher 403): UNVERIFIED.
- Relevance: MODES measures change, novelty, ecology and complexity potential, with persistence
  filters (a lineage must persist to count). This directly counters shape-keyed novelty
  inflation. Bohm et al. 2024 is a *positive-control study of an open-endedness metric*: it plants
  known diversity mechanisms and asks whether the metrics detect them.
- SUPPORTS H-D5-31 (persistence filtering and skeletonisation of redundant sites address
  "archives do not collapse near-duplicates") and H-D5-43 (the field has begun calibrating OEE
  metrics against planted mechanisms). A direct template for Prometheus's own novelty counters.

W18. Bedau, Snyder, Packard, "A classification of long-term evolutionary dynamics", ALife VI
(1998) pp. 228-237 (VERIFIED record via citing works). Channon, "Improving and still passing the
ALife test: component-normalised activity statistics classify evolution in Geb as unbounded",
ALife VIII (2003) (VERIFIED record and abstract). Channon, "A Procedure for Testing for Tokyo
Type 1 Open-Ended Evolution", Artificial Life 30(3) (2024), PMID 38635908 (VERIFIED record; the
five-step content was not readable: UNVERIFIED).
- Relevance: evolutionary activity statistics normalised against a **neutral shadow model**, a
  run in which components are assigned activity without selection. Channon's 2003 point is that
  the shadow can *drift away* from the real run it is meant to shadow, so the normalisation
  itself becomes an artefact. He repaired it with component-level normalisation.
- SUPPORTS H-D5-31 and H-D5-45 (ask which world maximises the metric; a neutral shadow is the
  null world). REFRAMES H-D3-02 (fwd shows 92% "altered"): the fwd control is a shadow run, and
  Channon's drift critique warns that a control law can diverge from its treatment in ways
  unrelated to the claimed effect.

W19. Stepney & Hickinbotham, "On the Open-Endedness of Detecting Open-Endedness", Artificial
Life 30(3):390-416 (2024), https://direct.mit.edu/artl/article/30/3/390/114972 . VERIFIED (record).
Also Taylor, Bedau, Channon et al., "Open-Ended Evolution: Perspectives from the OEE Workshop in
York", Artificial Life 22(3):408-423 (2016). VERIFIED (it separates observable hallmarks from
hypothesised mechanisms, and argues for pluralism about kinds of OEE).
- Relevance: argues that each new innovation class may need a new detector, so no fixed
  detector suite is complete.
- CONTRADICTS the strong form of H-D5-42 (a fixed eight-class counterfeit battery as sufficient
  gates) and any claim that a fixed "open-endedness score" suffices (H-D5-33, H-D1-55).
  SUPPORTS H-D1-34 (preregister a detector of surprise that can *grow*) and H-D5-58.

W20. Kumar, Lu, Kirsch, Tang, Stanley, Isola, Ha, "Automating the Search for Artificial Life with
Foundation Models" (ASAL), arXiv:2412.17799 (2024); Artificial Life 31(3):368 (2025). Code
https://github.com/SakanaAI/asal . VERIFIED (record, code).
- Relevance: the FM-embedding score for supervised targets, open-ended novelty and illumination.
  The authors say they did not search for open-endedness in Lenia/Boids because novelty was hard
  to sustain there (from the search summary: UNVERIFIED in the paper text).
- CONTRADICTED BY internal evidence H-D5-33 and H-D1-55 (a moving blob is within 0.026 of the
  Orbium; turbulence scores well). No external published critique that reproduces the
  garbage/turbulence failure was found in this pass. Prometheus's Harmonia/Techne result may be
  novel (section 6). SUPPORTS H-D5-33's requirement for garbage and translation controls.

Supporting works (short):

- S1. Ronald, Sipper, Capcarrere, "Design, Observation, Surprise! A Test of Emergence",
  Artificial Life 5(3):225-239 (1999), https://doi.org/10.1162/106454699568755 . VERIFIED
  (record; three criteria: design, observation, surprise). SUPPORTS H-D3-04: an explicit,
  citable emergence test. Its "surprise" criterion requires that the designer, knowing the local
  rules, cannot readily predict the global behaviour, which is exactly the rcv question.
  Weakness: surprise is observer-relative, so it needs an operational proxy (section 7 T4).
- S2. Jonas & Kording, "Could a Neuroscientist Understand a Microprocessor?", PLoS Comput. Biol.
  13(1):e1005268 (2017). VERIFIED (record; single-transistor lesions on a MOS 6502 running three
  games). Their conclusion that lesion effects mislead about function comes from memory:
  UNVERIFIED in detail. SUPPORTS H-D2-44 and REFRAMES the BEE/NPE Z80 knockout claims. A lesion
  that stops "Donkey Kong" does not locate a "Donkey Kong" mechanism. A near-perfect analogue for
  Z80-substrate engines.
- S3. El-Brolosy & Stainier, "Genetic compensation: A phenomenon in search of mechanisms", PLoS
  Genet. 13(7):e1006780 (2017). VERIFIED. SUPPORTS H-D2-44: knockouts can trigger compensation
  that knockdowns do not, so the ablation method changes the answer. The Prometheus analogue is
  "remove the setup / block re-creation" versus "NOP one site".
- S4. Hall, "Two Concepts of Causation", in Collins, Hall, Paul (eds.), Causation and
  Counterfactuals, MIT Press (2004) 225-276. VERIFIED. Dependence (counterfactual, non-transitive,
  allows omissions) versus production (transitive, local, intrinsic). REFRAMES H-D2-22 and
  H-D2-44. A certified chain is a *production* claim, and chaining certifications does not give
  end-to-end *dependence*. A knockout that is rescued is a preemption/backup case in which
  dependence fails even though production occurred. Halpern-Pearl actual causation handles the
  preemption cases and is the formal tool if needed.
- S5. Gross & Vitells, "Trial factors for the look elsewhere effect in high energy physics", EPJ
  C 70:525-530 (2010), arXiv:1005.1891. VERIFIED. SUPPORTS the Ares gate C fix: report a trial
  factor with any best-of-N statistic.
- S6. Dwork, Feldman, Hardt, Pitassi, Reingold, Roth, "The reusable holdout: Preserving validity
  in adaptive data analysis", Science 349:636-638 (2015). VERIFIED. REFRAMES H-D5-50 ("Cosmos
  has no sealed universes left"). A holdout need not be single-use if it is queried through a
  noise-adding mechanism (Thresholdout) with a query budget.
- S7. Lakens, Scheel, Isager, "Equivalence Testing for Psychological Research: A Tutorial",
  AMPPS 1(2):259-269 (2018). VERIFIED. SUPPORTS H-D3-67: gives the procedure for deriving and
  justifying a SESOI, and a TOST test that makes a *negative* informative.
- S8. Agarwal, Schwarzer, Castro, Courville, Bellemare, "Deep RL at the Edge of the Statistical
  Precipice", NeurIPS 2021; library `rliable`. VERIFIED. SUPPORTS H-D3-67: stratified bootstrap
  CIs, IQM and performance profiles for few-seed evaluation, which is exactly the "few replicates"
  regime of Prometheus gates.
- S9. Gundersen, Coakley, Kirkpatrick, Gil, "Sources of Irreproducibility in Machine Learning: A
  Review", arXiv:2204.07610 (2022). VERIFIED (a taxonomy of 41 design decisions in 6 categories).
  Raff, "A Step Toward Quantifying Independently Reproducible ML Research", NeurIPS 2019 (255
  papers re-implemented blind to the authors' code). VERIFIED. SUPPORTS H-D1-64 (taxonomy
  precedents) and H-D5-50 (reimplementation blind to the author's code is itself a blind
  battery).
- S10. Soergel, "Rampant software errors may undermine scientific results", F1000Research 3:303
  (2015). VERIFIED. SUPPORTS H-D5-51 (how many "inherent limits" are bugs). It gives an
  order-of-magnitude argument that output-altering bugs are expected in medium-sized analyses.

-----------------------------------------------------------------------

## 4. Pitfalls (from the prior art, mapped to Prometheus)

P1. A positive control you planted yourself is a necessary condition, not a sufficient one
(H-D3-23, H-D5-43). If the analyst knows the planted signal, the instrument can be tuned until it
recovers that signal. LIGO's answer is *blind* injection by a separate team with a sealed envelope
(W10). Kepler's answer is injection over a *distribution* of signals, reported as a completeness
curve (W11). A single planted positive that fires shows neither.

P2. The fix for a separable test episode can be another separable test episode. Avida's test CPU
still exists after the fix (with random inputs, W2), and Ofria's organisms defeated random inputs
by acting probabilistically (W1). Only the in-situ lineage-relative comparison closed the channel.
H-D5-39's proposal must name the in-situ path, not the STERILIZE_* option name.

P3. Co-evolving the evaluator invites mediocre stable states and collusion (W8). Without an
external fixed reference (a hall-of-fame, frozen gold scorer, or blind battery), "the selector
co-evolves" (H-D5-37) degenerates into a cycle or into mutual accommodation. The gold/proxy split
(W7) and the uninfluenceable-evaluator condition (W5) are the known guards.

P4. A preregistered test that hard-codes the expected mechanism is confirmation, not falsification
(H-D3-49; W13 Szollosi). Preregistering thresholds as *numbers* also freezes arbitrariness. The
Cosmos C3 formulation, "rules not numbers, derived from replicate uncertainty", is the correct
direction and matches HEP practice (W9).

P5. Multiverse over non-equivalent specifications (W12, Del Giudice & Gangestad). If a threshold
multiverse includes thresholds that nobody would defend, the specification curve is diluted.
Specifications must be pre-classified as equivalent or non-equivalent.

P6. A neutral shadow drifts (W18, Channon 2003). The fwd control (H-D3-02, 92% "altered") and
YOKED (H-D2-47) are shadow runs. A control that changes several things at once (per-tick versus
per-capita supply; H-D1-18 dropping pressures) stops being the counterfactual of the treatment.

P7. Metric maximisers (W4 extremal Goodhart; H-D5-45). Before a metric is used, find the world
that maximises it. For ASAL novelty that world is turbulence (H-D1-55). For D it is a fair coin.
For shape-keyed novelty it is op-duplication (H-D5-31). This check is cheap and fully analytic.

P8. Lesions in a computing substrate mislead (S2, S3). In Z80/Avida-like substrates, a
single-site knockout is rescued by re-creation elsewhere (H-D2-44: 126/345 ablated still
replicate). The lesion answer depends on the ablation method.

P9. Chained certification is not end-to-end dependence (S4, H-D2-22). A per-edge break rate p
caps certified depth at ~1/p. The endpoint then measures certification luck. Depth claims need a
dependence test (intervene on the root, measure the leaf) as well as a production chain.

P10. Holdouts are spent by looking (S6, H-D5-50). Each adaptive query leaks information. Cosmos'
sealed universes were used up. A differentially-private reuse mechanism with a stated budget
extends a holdout's life. Rebuilding holdouts by an author who has read the hypothesis is the
H-D3-30 problem.

P11. Best-of-N without a trial factor (S5; W7 best-of-n curve). The Ares gate C reversal is the
textbook look-elsewhere effect.

P12. A catalogue that only lists (Krakovna, Lehman et al.) does not change behaviour by itself.
Nothing found shows that documenting a failure class reduces its recurrence. Kapoor & Narayanan
propose info sheets but report no recurrence measurement (UNVERIFIED whether any follow-up exists).

-----------------------------------------------------------------------

## 5. Usable code and tools

| Tool | What it gives | Where it fits | Status |
|---|---|---|---|
| Avida `cHardwareBase::Divide_TestFitnessMeasures` and the TestSterilize block; avida.cfg REVERT_*/STERILIZE_* | Reference implementation of both separable (test-CPU) and in-situ lineage-relative evaluation | H-D5-39, H-D1-36 (APO-19 toy assay arms) | VERIFIED, github.com/devosoft/avida |
| MODES toolbox paper code | Change/novelty/ecology/complexity metrics with persistence filter | H-D5-31 novelty inflation; BEE/NPE archives | VERIFIED repo github.com/emilydolson/MODES-toolbox-paper. The maintained library implementation is in Empirical (github.com/devosoft/Empirical): UNVERIFIED path |
| SakanaAI/asal | FM-embedding target/novelty/illumination scores | H-D5-33 / H-D1-55: rerun garbage (noise, translation, turbulence) controls through the reference implementation | VERIFIED repo |
| `rliable` (Google) | Stratified bootstrap CIs, IQM, performance profiles, probability of improvement for few-seed comparisons | H-D3-67: derive tolerances from replicate uncertainty | VERIFIED project page agarwl.github.io/rliable |
| R `multiverse` package (CRAN); specification-curve code by Simonsohn et al. (`specr` R package: UNVERIFIED) | Enumerate specifications, joint inference | H-D3-67/H-D3-43 threshold multiverse; H-D1-58 failure surface | CRAN multiverse VERIFIED via search result |
| TOSTER (Lakens) | Equivalence tests against a SESOI | Make negatives informative (H-D3-08) | UNVERIFIED (package known; not checked this pass) |
| Thresholdout (Dwork et al.) | Reusable holdout with noise and a budget | Cosmos holdout reuse (H-D5-50, H-D3-21) | Algorithm VERIFIED; a reference implementation was not checked |
| Kapoor & Narayanan model info sheets | Pre-launch checklist targeting 8 leakage classes | Template for the H-D1-64 pre-launch sheet | VERIFIED (paper) |
| Krakovna spec-gaming spreadsheet | Seed examples for adversarial-Goodhart classes | H-D1-64 class seeding | VERIFIED |
| Causal influence diagram tooling (pycid, from the Everitt group) | Check for improver -> grader paths | H-D5-38 grader ownership audit | UNVERIFIED (name and repo from memory) |
| Kepler injection-recovery products | A worked template for completeness curves | H-D5-43, H-D5-46 | VERIFIED (papers) |

-----------------------------------------------------------------------

## 6. Genuinely unexplored (specific)

Scope note: "not found" means not found in this pass (about 40 targeted searches). It is not a
proof of absence.

U1. A within-program self-reversal rate, by instrument-failure class, with detection latency.
Nearest prior art: Kapoor & Narayanan (cross-field counts, other people's errors), Herrera-Perez
et al. (a medical reversal rate across a literature), Lehman et al. and Krakovna (uncounted
anecdote lists), Jeng (drift of values), Gundersen (taxonomy without rates), Raff (the rate at
which independent reimplementation succeeds). None of these measures, for one research program
with many engines: (a) the fraction of headline claims reduced by the claimant's own forensics
(REPORT s3.3 suggests 8/8 engines), (b) the class of each reduction, (c) the latency and
"caught_by" of each catch, and (d) recurrence of a class *after* it was documented. H-D1-64 and
H-D1-54 would be a new dataset.

U2. Recurrence-after-documentation as an outcome. Nothing was found that tests whether writing a
failure class into a catalogue or checklist reduces its recurrence in later projects. This is a
testable intervention in Prometheus, because engines launch in sequence and share a repository.

U3. The evaluator-detection rate as a function of isolation design, in an ALife substrate.
Avida's anecdote shows detection happens, and Denison et al. show escalation in LLMs. No
controlled measurement was found of generations-to-first-exploit across {fixed-input test CPU,
random-input test CPU, in-situ lineage-relative} evaluation (H-D1-36, H-D5-39). Avida makes the
three arms cheap because all three already exist in its source (W2).

U4. Garbage and turbulence controls for FM open-endedness scores. No external critique was found
that reproduces "a moving blob scores like the Orbium" (H-D5-33) or "the score rewards embedding
drift" (H-D1-55). If Harmonia's port is sound, this is publishable prior-art-extending work.
Required first: rerun through ASAL's own Flax CLIP (owed item, H-D1-55).

U5. "Preregister the detector of surprise" (H-D1-34). The preregistration literature treats
predictions and analyses. Stepney & Hickinbotham argue that detectors must grow. No protocol was
found that preregisters a *closure* (what is already explained) and counts only non-membership as
the confirmatory observable. Closest: Ronald et al.'s surprise criterion (S1), which is
observer-relative and unoperationalised.

U6. Threshold provenance as a first-class, audited field. HEP fixes cuts blind, and psychology
has SESOI. No computational-evolution program was found that records, per gate, where each
number came from (replicate SD / SESOI / planted-positive completeness / arbitrary) and audits
verdict flips across the defensible range. Cosmos C3 s1 is the only internal instance.

U7. A blind injection in ALife. Nothing was found in ALife or evolutionary computation analogous
to LIGO's GW100916: a hidden planted phenomenon, inserted by a third party into a run, that the
engine seat must find or miss under its normal process.

U8. Lesion validity in evolved machine-code substrates. Jonas & Kording show that lesions mislead
in a *designed* CPU. Nothing was found that quantifies knockout rescue rates in *evolved*
Avida/Tierra/Z80 genomes as a measurement-validity issue. H-D2-44's 126/345 is a first number.

-----------------------------------------------------------------------

## 7. Cheapest discriminating tests

T1 (H-D3-67 threshold provenance). No new runs for step 1.
1. Build a census table from committed prereg files: gate id, numeric threshold, stated source
   (replicate-SD / SESOI / planted-completeness / none), and replicate n. Engines: Aether,
   Ananke, Cosmos, Ensorain, Ares.
2. For the three gates in dispute (Cosmos 0.10 log2 location tolerance; Ananke C1b absolute
   thresholds; the Aether justify bar), compute from the *existing* replicate seeds the
   between-seed SD of the gated statistic. Rule: a threshold below about 2 SD is noise-limited;
   one far above is power-limited.
3. Threshold multiverse: re-evaluate the already-committed verdicts at 5 thresholds spanning the
   defensible range (W12). Report the flip fraction.
Discriminates: if verdicts flip inside the defensible range, "decided by the bar" is confirmed
for that gate. If they are stable, the negatives stand. Cost: hours of reducer re-runs on
existing outputs.

T2 (H-D3-43 and H-D3-08 attainability). One synthetic run per gate. Plant a perfect-effect
champion (the maximum effect the design allows) and pass it through the unchanged reducer. If the
label is unreachable even for the planted maximum, the prereg made the label impossible. Report
the result as "label attainability = no" and stop treating the kill as physics.

T3 (H-D5-43 positive controls, Kepler-style). Choose three gates whose silence is being read as
absence: the Ensorain null ladder, the Cosmos certificate and the Ananke XOR/FLIP NULL. Inject a
graded planted effect at doses {0, SESOI/2, SESOI, 3xSESOI}, 5 seeds each, and plot a detection
curve. Pass rule: detection at least 0.8 at SESOI and at most 0.05 at dose 0. A gate that fails is
labelled "uncalibrated", and its past nulls are downgraded to UNKNOWN (H-D5-48 tri-state).
Variant (blind, W10): a different seat chooses the dose and the location and seals it. Cost: about
60 runs per gate at the smallest world size.

T4 (H-D3-04 emergent or encoded). A blind-prediction test that operationalises Ronald et al.
(S1). Give a seat that has not seen the results the law's source text and the observable's
definition only, and ask for a numeric prediction of the observable. If the prediction lands
within the replicate CI, the observable is "encoded". Add a definitional null: the same law with
the output channel that the observable reads disconnected. If the effect survives, the effect is
not from the law. Cost: one seat-hour and one run.

T5 (H-D1-64 and H-D1-54 failure catalogue: the discriminating version).
1. Code every reversal in REPORT s3.3 plus the causal lens FF-1..34 into a fixed class set. Seed
   the classes with Manheim & Garrabrant (regressional, extremal, causal, adversarial) crossed
   with the instrument location (comparator, selector, generator/author, window, detector,
   harness bug).
2. Two coders work independently, and Cohen's kappa is reported. If kappa is below 0.6 the
   classes are not yet real, so stop and revise.
3. For each reversal record the claim date, catch date, caught_by, and whether the class had
   already been documented elsewhere in the repo before the claim. This gives the reversal rate,
   the median latency and the *rediscovery rate* (the fraction of reversals in a class that
   was already documented).
4. Prospective test: freeze the catalogue as a pre-launch sheet (Kapoor-style info sheet) and
   apply it to the next 3 engine launches, blind to their eventual forensics. Prediction: the
   sheet's flagged classes should contain most later reversals. Compare against the rediscovery
   rate from step 3.
Discriminates H-D1-54 directly: the share of reversals whose class is an instrument location
versus a substrate fact. Cost: coding is about 1-2 seat-days, and step 4 is free-riding on
planned launches.

T6 (H-D5-39 and H-D1-36 evaluator detection, APO-19). Use stock Avida, whose three isolation arms
already exist in source: fixed-input test CPU (with UseRandomInputs patched out), random-input
test CPU (stock on-divide path), and the in-situ TestSterilize path. Set STERILIZE_BENEFICIAL=1.0
in each arm. Outcome: updates to the first lineage whose in-population replication rate exceeds
the ancestor's by more than 10% (an escape). Run 20 seeds per arm. Predicted ordering
(Lehman W1): fixed < random << in-situ (in-situ never, or very rarely). If fixed-input and
random-input do not differ, the "randomise the test" fix is worthless in this regime. Cost:
CPU-hours, and no Prometheus code is involved.

T7 (H-D2-44 knockout validity). For each single-site knockout claim in BEE, NPE and Archaeon,
run the knockout twice: (a) as done, and (b) with the knocked-out primitive also removed from the
mutation and insertion alphabet ("block re-creation"; the analogue of a knockdown versus
knockout comparison, S3). If the effect grows under (b), rescue was masking it. If it vanishes
under both, the site was never the mechanism (S2).

T8 (H-D5-33 and H-D1-55 metric maximiser). Analytic, before any run. For each world or novelty
metric in use, write down the configuration that maximises it (P7), then score noise,
translated-blob and turbulence controls through ASAL's reference code. If any control outranks
the target phenomenon, the metric is not admissible as selection pressure.

T9 (H-D5-38 grader ownership). Draw the causal influence diagram for Aphrodite and Ares (W5): is
there any path from improver outputs to grader parameters, including the distractor policy and
the task generator? Each path found is an ownership violation. Cost: a desk exercise.

-----------------------------------------------------------------------

## Sources (URLs used)

- https://direct.mit.edu/artl/article/26/2/274/93255 ; https://arxiv.org/abs/1803.03453
- https://lukemuehlhauser.com/treacherous-turns-in-the-wild/
- https://github.com/devosoft/avida (avida.cfg; cHardwareBase.cc; cPopulation.cc; cOrganism.cc)
- https://vkrakovna.wordpress.com/2018/04/02/specification-gaming-examples-in-ai/
- https://arxiv.org/abs/1803.04585
- https://arxiv.org/abs/1908.04734
- https://arxiv.org/abs/2406.10162
- https://arxiv.org/abs/2210.10760
- https://eprints.soton.ac.uk/262011/1/watson_cdms_gecco_2001.pdf
- https://doi.org/10.1146/annurev.nucl.55.090704.151521 ; https://www.nature.com/articles/526187a
- https://www.ligo.org/news/blind-injection.php ; https://gwosc.org/s6hwcbc/ ; https://arxiv.org/pdf/1612.07864
- https://arxiv.org/abs/2010.04796
- https://doi.org/10.1177/1745691616658637 ; https://www.nature.com/articles/s41562-020-0912-z ; https://doi.org/10.1177/2515245920954925
- https://doi.org/10.1177/0956797611417632 ; https://sites.stat.columbia.edu/gelman/research/unpublished/p_hacking.pdf
- https://www.cell.com/trends/cognitive-sciences/abstract/S1364-6613(19)30285-2
- https://doi.org/10.1002/bimj.202200091
- https://www.cell.com/patterns/fulltext/S2666-3899(23)00159-9
- https://elifesciences.org/articles/45183 ; https://arxiv.org/pdf/physics/0508199
- https://doi.org/10.1162/artl_a_00280 ; https://github.com/emilydolson/MODES-toolbox-paper ; https://doi.org/10.1162/isal_a_00721
- https://link.springer.com/chapter/10.1007/3-540-44811-X_45 ; https://pubmed.ncbi.nlm.nih.gov/38635908/
- https://direct.mit.edu/artl/article/30/3/390/114972 ; https://direct.mit.edu/artl/article/22/3/408/2841
- https://arxiv.org/abs/2412.17799 ; https://github.com/SakanaAI/asal
- https://doi.org/10.1162/106454699568755
- https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1005268
- https://journals.plos.org/plosgenetics/article?id=10.1371%2Fjournal.pgen.1006780
- https://philpapers.org/rec/HALTCO-4
- https://arxiv.org/abs/1005.1891
- https://www.cis.upenn.edu/~aaroth/reusable.html
- https://doi.org/10.1177/2515245918770963
- https://agarwl.github.io/rliable/
- https://arxiv.org/abs/2204.07610 ; https://arxiv.org/abs/1909.06674
- https://f1000research.com/articles/3-303
