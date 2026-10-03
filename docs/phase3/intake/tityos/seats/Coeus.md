# Coeus -- forensic dossier (Tityos Phase 3 intake)

Crawler: Tityos worker g2 (Nyx/Coeus). Worktree read: F:/Prometheus-worktrees/tityos-phase3 (HEAD 36ffe8073 =
origin/main 5c98f59f1 + Tityos charter commit). Epistemic labels per the Tityos brief. All paths repo-relative.
Searches excluded **/*holdout*/** and **/nestor_secrets/**; no such path opened.

## 0. Summary

- Coeus was a March 2026 pipeline stage ("Causal Intelligence Layer") written in three days (2026-03-25..27,
  commits da42cc7e0..8af6ba9e5, author James Craig) between Nous (concept-triple generator/scorer) and Hephaestus
  (LLM code forge). It encoded each Nous triple as 122 concept + 20 field indicators + 4 Nous sub-scores, joined them
  to the forge ledger outcome (forged/scrap), and published per-concept "forge_effect", pair "synergy",
  "interventional" drops, adversarial survival rates and "goodhart_indicators" [IMPLEMENTATION FACT]
  (agents/coeus/src/*.py, agents/coeus/graphs/*.json).
- Its outputs steered selection in three places: Hephaestus forge-queue priority (_forge_priority), Hephaestus
  code-generation prompts (4,031 enrichment files of directives), and Nous's GENERATIVE sampling weights
  (agents/nous/src/nous.py:113 _load_coeus_weights) [IMPLEMENTATION FACT per roles/Coeus/FINDINGS_2026-09-11.md].
- Its rulers were uncalibrated and mislabelled: the README advertised NOTEARS/GES/LiNGAM/FCI/DAGMA; the shipped
  artifact records method "lasso_regression", empty confounders, empty dagma_divergences; the "interventional"
  block is raw P(forge|with) - P(forge|without), self-described in code as an "observational proxy for do-calculus"
  [IMPLEMENTATION FACT] (agents/coeus/src/causal_graph.py:530-577; graphs/causal_graph.json).
- The outcome variable was dominated by instrument state: api_call_failed rows scored as scrap (2,176-2,553 rows),
  and the trap battery changed 15 -> 186 traps on 2026-03-27; leave-one-forge-day-out AUC 0.461/0.338 -- Coeus
  learned the forge calendar [REPORTED RESULT -- UNVERIFIED; single investigator]
  (engine/necropolis/dossiers/coeus.dossier.json, disposition MEASUREMENT_FAILURE, 2026-09-10).
- Revived as a seat 2026-09-11 only for a residue-and-routing pass, then PARKED the same day; its self-autopsy
  (F1-F6) is exemplary: README 12/12 claims contradict artifacts incl. a sign reversal; 11 of 16 concepts at 2.5x
  Nous sampling weight were set by survival rates on n <= 5; but no recoverable evidence that any of it changed
  forge yield [REPORTED RESULT -- UNVERIFIED] (roles/Coeus/FINDINGS_2026-09-11.md).
- Strength of machinery: the 2026-03 instrument was weak and decorative-causal; the 2026-09 forensic machinery around
  it (Necropolis attacks harness, reorder-null, magnitude-matched noise null, denominator trace) is strong and reusable.

## 1. Charter and role evolution

- Aliases: coeus, "causal intelligence layer" (dossier identity block). No charter in March: it was a pipeline
  module, not an agent seat (roles/Coeus/RESPONSIBILITIES.md s0: "Charter: NONE, and this file does not invent one")
  [IMPLEMENTATION FACT].
- 2026-03-25..27: built and wired (da42cc7e0 "Forge pipeline v2: Coeus causal intelligence"; fbb92a11a "Coeus dual
  graph"; 8af6ba9e5 "Nous weights"). Graph built 2026-03-27 06:49 on 4,031 observations / 352 forged.
- Auto-triggered by Hephaestus every 50 forges (CoeusRebuildTrigger, an in-process call; DORMANT since the forge died
  2026-05-28) (roles/Coeus/STATUS.md).
- 2026-06-24 component dossier: "RETIRE-after-HITL: decorative-causal, open-loop, exhaust" (pivot/COMPONENT_DOSSIERS_2026-06-24.md)
  [HISTORICAL CLAIM].
- 2026-08-20 Aporia autopsy P47 / Elenchus P50: NO-DESIGN-FAILURE-ESTABLISHED, "consumption REORDERS the forge queue:
  10,094/10,105 positions change" (engine/ledger/AGENT_AUTOPSIES.jsonl) [LATER CORRECTION: overturned 09-10].
- 2026-09-10 Necromancer pass #1 (Mnemosyne M2 acting as Necromancer, branch necropolis/coeus): MEASUREMENT_FAILURE.
- 2026-09-11 seat created (699c9395d), base role adopted, residue pass (da62d70bd), PARKED by operator ruling
  COEUS-XL-01 (cb31b4e64); host SPECTREX5 (M2); routing comms #81-85 [HISTORICAL CLAIM].
- Terminal state: PARKED; reactivation only if a NAMED selection consumer needs outcome-variable hygiene not owned
  elsewhere AND a dedicated seat is preferable (STATUS) [DESIGN INTENT].
- Relations: Nous (producer + generative consumer), Hephaestus (outcome source + priority/prompt consumer), Nemesis
  (adversarial results feeding adversarial_survival), Necropolis/Mnemosyne (autopsy), Kairos (nominated LAW N13
  second lens, COEUS-XL-02).

## 2. Code/system architecture

- agents/coeus/src/coeus.py (402 lines): load_all_nous, load_forge_entries, compute_adversarial_survival (from
  Nemesis results), goodhart_indicators (thresholds forge_eff > 0.1 & adv < 0.4 => "warning"; forge_eff < 0.1 &
  adv > 0.6 => "undervalued"), writes graphs/*.json and enrichments [IMPLEMENTATION FACT].
- agents/coeus/src/causal_graph.py (686 lines): _encode_dataset (design matrix X (n,126)); _regression_influence
  (LogisticRegression/Lasso alpha=0.01); optional _notears_analysis/_lingam_analysis/_fci_confounder_analysis/
  _dagma_analysis behind try-imports that silently degrade; _compute_interventional (rate difference, min n_with >= 3)
  [IMPLEMENTATION FACT].
- agents/coeus/src/enrichment.py (297 lines): prescriptive directive text per triple -> agents/coeus/enrichments/
  (4,031 JSON files) [IMPLEMENTATION FACT].
- graphs/: causal_graph.json (95 concept_influence, 50 pair_synergy, 0 confounders, 85 interventional),
  concept_scores.json (95 influence, 1,009 synergy, 97 adversarial_survival, 30 goodhart_indicators),
  adversarial_graph.json (n_adversarial_tasks 92) (dossier outputs block) [IMPLEMENTATION FACT per dossier].
- Consumers: hephaestus.filter_results L1122-1124 sorts by _forge_priority = composite + sum(forge_effect) +
  sum(pair_synergy); hephaestus.load_enrichment L626 -> build_code_gen_prompt L1186/L1432; nous._load_coeus_weights
  L113, used at L237-239; agents/hephaestus/src/rlvf_fitness.py L70-100 (never imported) (FINDINGS F3-F6).
- Scale: one batch fit; ~6,651 ledger entries; no persistence beyond JSON in git; no tests found under agents/coeus.
- 2026-09 seat code: roles/Coeus/science/trace_defects.py + ledgers/defect_trace_2026-09-11.json (re-runnable,
  refits nothing).

## 3. Inputs and outputs

Inputs: agents/nous/runs/*/responses.jsonl (concept triples + composite), agents/hephaestus/forge/*.json ledger
(status forged/scrap with reason), Nemesis adversarial results. Outputs: graphs (3), enrichments (4,031), sampling
weights consumed by Nous, priority boost consumed by Hephaestus [IMPLEMENTATION FACT].

## 4. Claim class it was meant to police

Coeus was not an auditor; it was a selection signal claiming CAUSAL knowledge: "which concepts causally drive forge
success vs just correlate", "are correlations confounded", "what happens if we remove a concept" (agents/coeus/README.md)
[DESIGN INTENT]. It also claimed to police Goodharting (forge success without adversarial robustness) via
goodhart_indicators [DESIGN INTENT]. In Phase 3 terms it is a case study of a ruler that produced its own claims
and steered selection with them.

## 5. Measurement methodology

Lasso/logistic regression of a binary forge label on concept/field indicators and Nous sub-scores, pooled across
all forge days; pair synergies from interaction terms fit on 352 positives; in-sample AUC 0.887 for synergies,
stratified-CV AUC 0.72 (+0.05 over composite) [REPORTED RESULT -- UNVERIFIED, dossier contradictory_evidence]. No
held-out split by time or by instrument version; no exclusion of api_call_failed rows (roles/Coeus/CALIBRATION.md
C-02, C-03) [IMPLEMENTATION FACT per dossier].

## 6. Null/control generation

March: none found in agents/coeus/src (searched for permutation/null/shuffle) [IMPLEMENTATION FACT: grep of src shows
no null]. September (by others/self): Necropolis label-permutation nulls (20 draws within-day; flagged as too few),
leave-one-forge-day-out, reorder-null (1e-3 Gaussian noise on the composite reorders 99.7% of queue positions)
(engine/necropolis/dossiers/coeus_evidence/coeus_attacks.py, coeus.dossier.json); Coeus F4 magnitude-matched
Gaussian noise null on top-k churn, 200 draws, seed 20260911; permutation test on attempted vs never-attempted boost
(p = 0.305) (FINDINGS F4) [REPORTED RESULT -- UNVERIFIED].

## 7. Positive controls

None in the March instrument. The Necropolis descendant design coeus-d1 specifies one (a batch-id decoy feature must
reach AUC ~1.0 to prove the harness can see batch) but it was never run -- RESOURCE-gated on a live forge
(coeus.dossier.json descendant_candidate) [DESIGN INTENT, never executed].

## 8. Negative controls

None in March. Designed for coeus-d1: permuted concept labels must sit in the null; random score vector reorder
fraction ~99.7% (dossier) [DESIGN INTENT]. The reorder-null itself is an executed negative control that overturned
P47/P50 [REPORTED RESULT -- UNVERIFIED].

## 9. Neutral/intermediate controls

"Causally neutral" was the most common emitted directive (7,243 of 12,093 directive strings) -- a label, not a
control (FINDINGS F5) [IMPLEMENTATION FACT per findings].

## 10. Qualification criteria / gates / thresholds

forge_effect branches in nous._load_coeus_weights: > 0.3 -> 3.0, > 0.05 -> 2.0, < -0.2 -> 0.3, goodhart warning
x0.5, adv_rate > 0.6 and forge_effect < 0.1 -> 2.5 (FINDINGS F6). goodhart thresholds 0.1/0.4/0.6 hard-coded
(coeus.py L322-337). _compute_interventional min n_with/n_without = 3, reports |drop| > 0.01. No minimum denominator
anywhere in the chain [IMPLEMENTATION FACT].

## 11. Statistical methods

L1-regularised regression, logistic regression, raw rate differences; optional causal-discovery packages never
executed on the shipped artifact. Effective sample size misreported: per-concept n_tasks sums to 37,035 while
n_adversarial_tasks is 92 (pairings counted as tasks) (FINDINGS F2) [REPORTED RESULT -- UNVERIFIED]. 1,009 synergies
on 352 positives with no multiplicity control [IMPLEMENTATION FACT per dossier].

## 12. Independence assumptions

Assumed independence of concept identity from forge regime -- false: forge-day base rates 58% / 23% / 10.5% / 2-3%
driven by battery version and API health (dossier). Shared data: the same forge ledger was Coeus's label and
Hephaestus's success metric; Nemesis's adversarial results fed survival rates (shared with Nemesis's own claims).
Shared authorship: Coeus, Nous, Hephaestus were all written by the same author in the same March push. Autopsy
independence: the MEASUREMENT_FAILURE kill is single-investigator (Mnemosyne); LAW N13 independent re-run delegated
to Kairos (comms #81, COEUS-XL-02) -- no Kairos re-run found in roles/Kairos or git log [IMPLEMENTATION FACT of
absence, within my search]. Coeus declared a standing conflict of interest about its own lineage (CALIBRATION.md).

## 13. Provenance tracking

Failures: ledger stores no priority/rank/queue-position, no enrichment_used, no judge/battery-version, no API-status
field; Nous records no weight vector -- so effect on yield is PERMANENTLY unrecoverable (FINDINGS F4-F6). README
quoted an example enrichment that never existed (0 regex matches over 4,031 files) and a wrong path. Wins: the
committed graphs/enrichments allowed exact replay of every consumer path in September; the 2026-06-24 dossier caught
the method mismatch and named the Nous consumer correctly [HISTORICAL CLAIM].

## 14. Known defects

C-01 causal label on regression; C-02 unvalidated synergies into a live priority; C-03 forge-calendar leakage;
C-04 README contradicts artifacts (sign reversal on implementability: +0.221 claimed vs -0.467 shipped); C-05
denominators stripped in goodhart_indicators (7 rows at 1.0 on n <= 4); C-06 (Sept) truncated grep piped through head
reported "no external consumer" -- wrong; C-07 (Sept) assumed a top-N queue cut that does not exist in continuous mode
(roles/Coeus/CALIBRATION.md) [IMPLEMENTATION FACT per ledger; C-04 and C-05 checkable against graphs/].

## 15. Historical audits performed (by and on this seat)

On: 06-24 component dossier (decorative-causal; PARTIALLY_UPHELD); 08-20 P47/P50 autopsy (NO-DESIGN-FAILURE;
OVERTURNED by reorder-null); 09-10 Necropolis pass (MEASUREMENT_FAILURE; primary MEASUREMENT_ERROR, contributing
DESIGN/CONFIGURATION/INSTRUMENT/INTERPRETATION). By: 09-11 self-archaeology (roles/Coeus/ARCHAEOLOGY_2026-09-11.md,
D1-D3b) and forward trace F1-F6.

## 16. Historical findings

- March: "only implementability predicts working code", "Criticality +1.155 unconfounded mechanical advantage",
  "Topology inhibitor" [LATER OVERTURNED -- README contradicts artifacts; artifacts themselves calendar-contaminated].
- Necropolis: concept-level signal does not transfer across forge days (AUC 0.461/0.338); within-day 0.501 vs null
  0.493 on 03-26 [REPORTED NEGATIVE/NULL, single investigator]; hypothesis itself "VALID, untested at power"
  (fair_test UNFAIR) [INCONCLUSIVE].
- F6: generative distribution tilted 2.5:1 by unreplicated rates [REPORTED POSITIVE (defect found)].
- F3: rlvf_fitness would mis-weight 47/366 tools; never imported [REPORTED RESULT -- latent].
- F4: queue-order effect inside magnitude-matched null at operative cut [REPORTED NEGATIVE/NULL].
- F5: <= 21 surviving tools could have been generated under a Coeus directive (upper bound) [UNKNOWN].

## 17. Later corrections (timelines)

- "Coeus reorders the queue => it has effect" (08-20) -> reorder-null shows noise reorders 99.7% (09-10) -> claim
  overturned; design failure established.
- "decorative-causal" (06-24) -> confirmed as claim/method mismatch but decisive defect is the contaminated outcome
  (09-10).
- Coeus self-claim "goodhart_indicators has no external consumer" (09-11 a.m.) -> nous.py:113 found -> retracted F6
  (09-11 p.m.).
- Coeus self-claim "queue cut at top-N" -> continuous mode sorts the whole backlog (args.all = True) -> redesigned test
  (C-07).

## 18. Pivots

Pipeline stage (March) -> dormant (April-May; forge dies 05-28) -> autopsy subject (Aug-Sep) -> one-day seat whose
product is a draft invariant (roles/Coeus/residue/OUTCOME_VARIABLE_HYGIENE.md: label provenance + exclusions;
denominator and effective n; temporal/instrument regime; ...) -> PARKED.

## 19. Journals / TODOs / backlogs

roles/Coeus/journal/2026-09-11.md; roles/Coeus/BACKLOG_H0H5.md (11 items, FROZEN, deliberately below the 20-item
floor); roles/Coeus/STATUS.md; roles/Coeus/prompts/2026-09-11_park_routing/. They reveal a seat refusing to
manufacture work to survive.

## 20. Research reports

- roles/Coeus/ARCHAEOLOGY_2026-09-11.md -- what Coeus was, commits, defects D1-D3b.
- roles/Coeus/FINDINGS_2026-09-11.md -- F1-F6 forward trace to consumers.
- roles/Coeus/CALIBRATION.md -- seven wrong calls.
- roles/Coeus/residue/OUTCOME_VARIABLE_HYGIENE.md -- draft invariant (not adopted).
- engine/necropolis/dossiers/coeus.dossier.json + coeus_evidence/ -- the autopsy (not Coeus-authored).
- pivot/COMPONENT_DOSSIERS_2026-06-24.md (### Coeus) -- earlier review (not read in full here).

## 21. Failure cases

False positives: causal language on a regression; synergies with in-sample AUC presented as structure; rates on n=1
labelled "undervalued, BOOST"; a reorder count read as effect (by its auditors). Plausible false negatives (FN): the
premise (concept-level structure under a frozen judge) was never tested at power because no clean window exists
(>=500 rows, >=50 forged, one battery version, no API failures) -- the kill is of the INSTRUMENT, not the HYPOTHESIS;
the within-day nulls on 03-25/03-27 (0.62/0.64 vs null-max 0.57/0.61 from only 20 permutations) were marginal and
undersampled (dossier uncertainty block).

## 22. Mechanism archaeology

Partly relevant: Coeus claimed "mechanical advantage" of concepts with "interventional" estimates. No lesion was ever
performed; the "do(remove X)" block is an observational rate difference with no adjustment set
(causal_graph.py:530-577) [IMPLEMENTATION FACT]. Purely correlational, and confounded by time/instrument.

## 23. Novelty/prior-art audit

Not applicable (none found; searched agents/coeus and roles/Coeus for novelty/prior-art).

## 24. Lens inventory

- Reusable: _encode_dataset design-matrix builder; the Necropolis coeus_attacks harness (leave-one-run-out,
  leave-one-forge-day-out, within-day nulls) for any Nous->forge scorer; reorder-null; magnitude-matched noise null;
  denominator/effective-n audit. Resolution ceiling set by the outcome variable, which was instrument-dominated.
- Toy-grade/obsolete: the Lasso "causal graph", enrichment directives.
- Unknown: whether concept-level structure exists at all under a frozen judge (coeus-d1 never run).

## 25. What I did not read / open questions

Did not read: enrichment.py in detail, the 4,031 enrichments, coeus_attacks.py source, the 06-24 component dossier
section, AGENT_AUTOPSIES.jsonl records, roles/Coeus/journal, BACKLOG items. Did not execute anything. Open: was the
Kairos LAW N13 re-run (COEUS-XL-02) ever performed? Did OUTCOME_VARIABLE_HYGIENE get adopted by any consumer (the
conformance gate)? Did the Hephaestus ledger ever gain battery-version / api-status fields (Hephaestus HEPH-31 reply
c6b19d048 suggests ledger schema rows were added to a DISPOSITION_LEDGER; not verified)?
