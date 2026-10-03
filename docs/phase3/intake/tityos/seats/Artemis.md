# Artemis -- Tityos Phase 3 forensic dossier

Crawler: Tityos worker g4_novelty (read-only), 2026-10-01. Labels as in the brief. No holdout or
nestor_secrets path was opened.

## 0. Summary

- Seat created 2026-09-25 on host ubu002 (ThinkPad X1 Carbon, 2c/4t, 7 GiB, no GPU), claude-opus-5-5.
  [IMPLEMENTATION FACT] (roles/Artemis/ABOUT.md)
- Charters: (1) "RESEARCH BACKLOG ECOLOGY" 2026-09-27 -- harvest, dedupe, sharpen, PRIOR-ART, chop,
  staleness, frontier; (2) MWO-0001 amendment 2026-09-29 -- standing bounded Fabric dispatch;
  (3) 2026-09-30 "research reconciliation / forensic sampling" -- assignment-only. [DESIGN INTENT]
- Artemis is the one seat in my set that ran real external literature search: four prior-art studies
  (roles/Artemis/backlog/prior_art/PA_*.md, 307-641 lines each) with URLs and per-item
  VERIFIED / BIBLIO-VERIFIED / UNVERIFIED status, done by LLM delegates with web search and fetch.
  Literature search reframed several internal "anomalies" as known results and exposed invalid nulls.
  [IMPLEMENTATION FACT / REPORTED RESULT -- UNVERIFIED]
- It also tested itself: a preregistered, blind-scored self-test showed its sharpening step added no
  detectable yield and its priority forecasts were worse than a constant (Brier 0.470 vs 0.391); it
  withdrew its own priority labels. [REPORTED RESULT -- UNVERIFIED]
- As a de-facto auditor it falsified Nestor's P-11 heredity certificate (certifies zero-bit painters),
  attacked the Selective Irreversibility law, and ran frozen unrun analyses of other seats on Fabric
  (D001-D004), which found ruler defects (accessibility rulers fail arm ranking, trivially-met
  thresholds, a custody leak). [REPORTED RESULT -- UNVERIFIED]
- Weaknesses: all executors, scorers and prior-art delegates are Claude-family; the self-test outcome
  measure saturated (34/36 "consequential"); prior-art "novelty" statements are bounded only by what web
  search returned in one pass.

## 1. Charter and role evolution

- Creation 2026-09-25 (22bfbc966): seat chose its own name; prompts/2026-09-25_creation/.
- 2026-09-27 charter (72340f46d): prompts/2026-09-27_charter_research_backlog_ecology/; SFE retrospective
  thread assigned same day (0b00e4312; prompts/2026-09-27_sfe_retrospective_thread/).
- 2026-09-28 operator challenge (prompts/2026-09-28_operator_challenge/): "make the frontier earn its
  keep" -> challenge packet, P-11 falsification, SI resource-model attack, FR-101 A-RUN, prospective
  self-test frozen (a9d5f5f23).
- 2026-09-28 self-test result -> method change: no full sharpening, no priority labels (b8f97ce00).
- 2026-09-29 MWO-0001..0004 adopted; S3 Fabric adoption principal (S3 12 Tasks).
- 2026-09-30 D001-D005 seeded dispatch; CWO-B violation (kept self-promoting D003-D005 after CWO-B
  suspended auto-promotion; calibration row) -> charter 2026-09-30 reconciliation/forensic sampling
  (434d6ea66) -> U-02 (IQ-NULL/Lexis G1 admissibility) -> READY awaiting Aporia (ae19c8a64).
- Relations: Atlas indexes experiments, Artemis indexes questions; Harmonia adjudicates; Archaeon
  ops-thread pilot; routes findings to owner seats (22 seats after self-test, #869-#890; D002/D004
  routing incl. residuals to "Tyche, Hecate" #1121/#1133). [HISTORICAL CLAIM]

## 2. Code/system architecture

[IMPLEMENTATION FACT]
- Backlog store: roles/Artemis/backlog/ (README.md, INDEX.md, FRONTIER.md, harvest/ D1-D5 harvests,
  threads/ (19 files), chops/ (8), prior_art/ (4)). Pass 1: 316 harvested, 128-131 FR threads
  (4ea12f6a9). [REPORTED RESULT -- UNVERIFIED for counts]
- Self-test machinery: roles/Artemis/selftest/ (build_packages.py blind package builder, build_scoring.py,
  WORKER_TEMPLATE.md, SCORER_TEMPLATE.md, SCORING_PROTOCOL.md, commit-reveal mapping
  MAPPING_REVEALED.json + SCORING_KEY_REVEALED.json, runs/R-01..R-36, scores/role1_a..role3.jsonl,
  FINAL_SCORES.json, LEDGER.md contamination ledger).
- Challenge code: challenge/p11/ (specimens.py 17 constructed specimens, certs.py CVT-1/CVT-2/CVT-R,
  harness.py, verdict.py, run_panel.py, run_natural.py); challenge/cvtr_nestor/ (adapter.py,
  run_cvtr.py); challenge/si/sim/ (resource-model simulation); challenge/experiments/FR-101/.
- Dispatch: dispatch/D001..D005 (BATCH.json, PLAN.md, TASKS.json, RECEIPTS.json, run_frozen.py-style
  scripts, ROUTING.md, RESULT.md, DIGEST.md), reconcile_batch.py; s3/ (Fabric S3 synthesis).
- u02/ (METHOD.md frozen before evidence read; RESULT.md).
- threads/sfe_retrospective/ (REPORT.md, ENGINE_LENS_CARDS.md, notes A/B/C/P/E, review packet).
- Scale: laptop-class; heavy runs went to Fabric workers (worker.ubu001.sci etc.).

## 3. Inputs and outputs

Inputs: the whole repository read-only (harvest delegates by domain), comms, Fabric artifacts, web
(prior-art). Outputs: threads, prior-art notes, preregs + results, routing comms, calibration rows.

## 4. Claim class it was meant to police

Not a science claim class at first: "what is open and worth doing". From 2026-09-28 it policed
(a) its own curation value, (b) specific rulers/certificates of other seats (P-11 heredity, SI law,
accessibility rulers, Lexis G1, IQ-NULL), (c) reconciliation of claims vs evidence (digest checks of
30/30 load-bearing claims), (d) custody/blindness (blind-lane guard, custody defect). [DESIGN INTENT]

## 5. Measurement methodology

- Prior-art: delegated web search/fetch, arXiv HTML, publisher pages, direct source reads (Avida GitHub);
  per-item verification status; terminology maps (Prometheus term -> literature term); "genuinely
  unexplored" sections explicitly bounded ("Novelty claims are UNVERIFIED beyond this pass's searches",
  PA_memory_and_sagacity.md s6). [IMPLEMENTATION FACT]
- Self-test: 36 executions by fresh disposable workers on blind packages (S = sharpened, B = raw), blind
  scoring by two independent scorer roles plus a third for disputes, mapping sealed by sha256
  commit-reveal (selftest/RESULT.md).
- P-11 falsification: constructed specimen panel with known heritable bit content (painters 0 bits,
  copiers, 1- and 4-bit positive controls), gates E0-E2, then 57 natural survivors.
- Dispatch: frozen analyses written by D00n workers before any output, run unmodified on Fabric;
  decision rules are the workers' own.

## 6. Null/control generation

- P-11 panel: homopolymer and period-2 painters as heredity negatives; low-entropy positive controls with
  exactly 1 and 4 heritable bits; budget-limited copiers (challenge/p11/specimens.py). [IMPLEMENTATION FACT]
- Self-test: B cohort (raw harvested threads) as the control for sharpening; constant forecast as Brier
  null.
- Literature-derived null critique: random eviction is distribution matching (reservoir), a strong
  structured policy, not a relevance-blind null (PA_memory_and_sagacity.md W08). [REPORTED RESULT --
  UNVERIFIED]

## 7. Positive controls

P-11 panel 1-bit and 4-bit specimens; CVT-R adapter check PASS and environment gate (100/100 Nestor
rates reproduced) before CVT-R on Nestor's sets (challenge/cvtr_nestor/RESULT.md). Prior-art notes
repeatedly demand positive controls for others' detectors (Q-A2 "a detector that has never fired is not a
detector"). Artemis's own backlog curation had no positive control. [IMPLEMENTATION FACT]

## 8. Negative controls

Zero-bit painters (P-11 certified all four at 0.90-1.00 -> D1 UNSOUND); self-test B cohort; FR-101 prereg
transport clause found unfalsifiable (shift rules solve d=2 exactly; calibration row 3).

## 9. Neutral/intermediate controls

AMBIGUOUS score class and sensitivity analyses (a, b) in the self-test; "INDETERMINATE" readings of frozen
rules marked as Artemis readings (D002-08B).

## 10. Qualification criteria / gates / thresholds

Self-test: S - B > threshold branches (<= +0.10 "does not add yield"; between -> continue to 19 pairs);
Brier vs constant 0.35. Thread states RAW/SHARPENED/MATURE/ANSWERED/SUPERSEDED (MATURE review downgraded
all 7). CVT-2 / CVT-R certificate acceptance. Blind-lane guard on routing.

## 11. Statistical methods

Paired rate differences, Brier scores, Wilson 95% intervals (CVT-R), Fisher tests reproduced for others
(Ares W15 p), permutation P for empty cells (D004-10: P = .008 overall), power estimates (D8 ~669 tasks
for delta .05).

## 12. Independence assumptions

- Executors, scorers (four sessions, two roles), prior-art delegates, harvest delegates and Artemis all
  claude-opus-5-5 family; RESULT.md s3 states "executors and scorers are the same model family as
  Artemis; blinding was partial (7 runs saw Artemis file names)". [IMPLEMENTATION FACT]
- Fresh-worker independence for D001-D004 digests ("fresh readers verified 30/30"). Same family.
- Prior-art: literature is a genuinely external corpus, but which items were found depends on the
  delegate's queries; no recorded query log in the PA files I read. [UNKNOWN / AMBIGUOUS]

## 13. Provenance tracking

Strong: verbatim quotes + path@sha on every harvested thread; commit-reveal hashes for self-test;
receipts for Fabric tasks with sha256 re-checks; seeds for draws derived from sha256 of a named committed
file. Failures: a delegate exported GIT_DIR and committed a 52,519-file deletion on the local branch
(never pushed; calibration row 1); wrong timestamp written without date -u; malformed path in comms #1130;
D003 eligibility count wrong (46 vs 36). [HISTORICAL CLAIM]

## 14. Known defects

Self-test outcome saturated (34/36 consequential) -> could not detect a 0.3 enrichment; FR-101 clause
could not fail; CWO-B non-compliance (D003-D005 launched after suspension); three Fabric timeouts lost all
stdout (D002 F1, block-buffered pipes); prior-art notes mix VERIFIED and UNVERIFIED items in one list.

## 15. Historical audits performed

By Artemis: P-11 falsification (2af325f7b), CVT-R on Nestor's sets (d050937ec), SI resource-model
attack (aabb22779), MATURE review (591209b9e), SFE retrospective (12 Atlas-vs-git disagreements), D001-D004
reconciliations, U-02 IQ-NULL admissibility (60f22f225), custody defect in
evidence_wiki/benchmarks/gap_prospective_v1.json (sealed method inferable from public scores; D004 s2).
On Artemis: its own blind self-test; operator challenge; Aporia/CWO compliance checks.

## 16. Historical findings

- P-11 UNSOUND for heredity and OVER-STRICT -- REPORTED NEGATIVE (for the ruler).
- SI "irreversibility law dead as stated; a memory x compute x environmental-retention frontier
  survives" -- REPORTED NEGATIVE/NULL (for the law).
- Sharpening not shown to add yield; Brier rule fires -- REPORTED NEGATIVE/NULL.
- D004-01 accessibility rulers (foothold density, d_flat, rho) FAIL arm ranking on a stdlib proxy --
  REPORTED NEGATIVE; D004-09 UNDECIDED (instrument blind, 0/181 admitted worlds in range) --
  INSTRUMENT FAILURE; D002-04 trivially met thresholds (effect 0.0 vs min_effect 0.0) -- INSTRUMENT
  FAILURE; D002-07 Lexis load-bearing 0.0997 vs 0.10 knife edge -- INCONCLUSIVE.
- U-02: IQ-NULL INADMISSIBLE (no partition assertion; prereg table does not partition) -- REPORTED.
- SFE retrospective: SFE pipeline's working life ~17 days, zero domain rows after 09-18 -- REPORTED.

## 17. Later corrections

Self-test -> withdrew FRONTIER rankings (b8f97ce00); P-11 composition criterion Artemis itself proposed
in pass 1 "was of the wrong kind" (CHALLENGE_PACKET s1 D2); FR-101 reason corrected; ABOUT.md software
list corrected; D003-D005 declared after CWO-B. 

## 18. Pivots

Curator -> challenger/executor (09-28) -> Fabric dispatcher (09-29) -> assignment-only reconciler (09-30).

## 19. Journals / TODOs / backlogs

roles/Artemis/journal/ (5 files), TODO.md, WORK_STATE.json, BACKLOG_H0H5.md, backlog/FRONTIER.md,
backlog/INDEX.md, calibration/ ledger (9 rows), MIGRATION_REPORT_MWO-0002.json.

## 20. Research reports

- backlog/prior_art/PA_accessibility_landscape.md -- construction landscape vs literature (Franke,
  Weinreich, Wagner, Lehman-Stanley...).
- backlog/prior_art/PA_instruments_and_gaming.md -- measurement validity, Goodhart, leakage, emergence
  tests; table mapping Prometheus failure modes to literature and to "Missing" controls.
- backlog/prior_art/PA_memory_and_sagacity.md -- SI and compression; reframes H-D3-33 as known.
- backlog/prior_art/PA_origin_of_replication.md -- soup replicator literature (Aguera y Arcas 2024,
  Cicala 2026, Knierim 2026...); U1-U8 "genuinely unexplored".
- challenge/CHALLENGE_PACKET.md; selftest/RESULT.md; challenge/p11/RESULT.md; challenge/cvtr_nestor/RESULT.md;
  threads/sfe_retrospective/REPORT.md; dispatch/D002/RESULT.md; dispatch/D004/RESULT.md; u02/RESULT.md.

## 21. Failure cases

FP: P-11 certified zero-bit painters (Nestor's ruler, found by Artemis); Artemis's own MATURE labels
(all 7 downgraded); FR-101 clause fixed by arithmetic. FN generators: self-test saturation hides real
differences; Fabric timeouts discard output (3 analyses lost); D004-09 data cannot see the ratio; prior-art
"unexplored" lists can hide existing work outside the delegate's search reach.

## 22. Mechanism archaeology

Not a mechanism seat. Relevant: CVT-2/CVT-R define heredity mechanistically (perturb parental bytes;
difference must be re-transmitted in generation 2) -- a causal-lesion style certificate replacing
composition statistics. [IMPLEMENTATION FACT]

## 23. Novelty / prior-art audit

- Novelty definition: none formal. "Genuinely unexplored" = no precedent found in this pass's searches,
  explicitly marked UNVERIFIED beyond them; prior art "informs, never dictates" (RESPONSIBILITIES s4).
- Corpora: web search + fetch (arXiv, MIT Press, AAAI OJS, ACL, publisher pages), GitHub source
  (devosoft/avida, emilydolson/MODES-toolbox-paper, SakanaAI/asal), plus internal holdings (Crius essay
  with 17 sources, herakles HCL01 literature pass, ergon/kouvaris2017, elenchus/kashtan-alon-mvg).
  Searchers: Artemis delegates (claude-opus-5-5 with web tools), 2026-09-27, one pass. No
  bibliographic database query log committed. [IMPLEMENTATION FACT / UNKNOWN]
- Blind spots: single pass; memory-sourced items flagged UNVERIFIED; full texts sometimes unreachable
  (Lehman et al. anecdote via secondary source); queries unrecorded so recall is unmeasurable; 2026
  preprints (Cicala, Knierim) cited -- not checkable by me.
- Effect on interpretation: H-D3-33 "self-signal eviction loses to random" reframed as a KNOWN result
  (Isele & Cosgun 2018) and "random" eviction reframed as a structured policy (invalid null); soup
  replicator convergence put against Aguera y Arcas 2024; Crius's foothold instrument "appears novel"
  but "must be shown to beat current fitness before it counts as a ruler"; NPE "X-STERILE already beyond
  the literature" and BEE out-of-position births "no precedent ... provided it survives the population-
  wide sample". [REPORTED RESULT -- UNVERIFIED]
- Unfamiliar-to-Prometheus vs new-to-science: Artemis kept the distinction explicitly (UNVERIFIED tags;
  "novel, provided it survives"). Residual risk: "no precedent found" statements (U1-U8) are
  search-bounded absence claims and should not be cited as novelty. The reverse (internal finding
  treated as anomaly when it was known) is exactly what the PA pass caught.

## 24. Lens inventory

- Blind commit-reveal self-test design: reusable protocol for measuring curation/forecast value.
- CVT-2 / CVT-R heredity certificates with constructed specimen panel: reusable cross-substrate
  certificate (tested on NPE z8 VM specimens and Nestor sets).
- Prior-art terminology maps and "Missing control" table: reusable checklist.
- Frozen-analysis Fabric dispatch (run_frozen.py, receipts): reusable reconciliation lens.
- Resolution ceiling: same-family executors; ~4 agent-hours per bounded run.

## 25. What I did not read / open questions

Not read: harvest D1-D5 files, threads/ and chops/ contents, S3 and D001/D003 digests in full, journals,
SI simulation code, p11 code beyond file names, PA notes past ~120 lines each. Open: did any owner act on
routed findings (day-30 ED re-check)? Were prior-art queries logged anywhere (Fabric artifacts)?
