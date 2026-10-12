# C-014 -- Phase 2-B re-entry: Ensorain WTP-05 / DESERT CROSSING (post-Hestia re-entry)

Thread TH-P2B-ENGINE-HARDENING, epic EP-PHASE2B. Coordinator: Ensorain. Instantiated 2026-10-10 by Ensorain[ubu006-4b001784] from
ops/templates/P2B-ENGINE-REENTRY/.

Authority:
- Operator directive 2026-10-10, "ENSORAIN -- WTP-05 DESERT CROSSING: STATEFUL DEVELOPMENTAL TENSOR WORLDS".
  Verbatim with MANIFEST at roles/Ensorain/prompts/2026-10-10_wtp05_directive/.
  - s31: "This is Ensorain's Phase 2-B restart campaign".
  - "This is not a continuation of WTP-04's map stage."
- The epic authority is the operator directive of 2026-10-03
  (roles/Achilles/prompts/2026-10-03_epics_phase2b/).

Experiment: E-ENS-WTP05 (prereg ensorain/PREREG_WTP05.md, committed before any eval row).
Deliverable: ensorain/ENSORAIN_WTP05_DESERT_REPORT.md.

## Sources actually used (task A)

| source | path | contributes |
|---|---|---|
| WTP-04 map result (preserved exactly; verdict ISLANDS_MAPPED, not reinterpreted) | ensorain/RESULTS_WTP04_MAP.md @87965d589; review packet ensorain/arc3/reviews/WTP04_MAP_REVIEW_2026-10-07.md @5d6427a97 | F-W4a, F-W4b, F-W4c |
| Hestia Ensorain dossier (verdict SALVAGE_COMPONENT) | roles/Hestia/audit/2026-10-06/dossiers/ensorain.md (s3a-s3c matrix, s4 brick walls, seed viability, roadmap, HSNA) | F-H1..F-H8 |
| Hestia composition-wall diagnosis | roles/Hestia/audit/2026-10-06/REPORT.md Part 2: W1 composition wall, W2 world-demand deficit, W3 promotion gap, W4 scalar-credit bottleneck; Part 5 Steps 1-3 (ladder R0-R4; escapes E-a/E-b/E-c) | F-H9, design |
| Hestia amendments M1-M7 | roles/Hestia/audit/2026-10-06/RESPONSE_TO_EXTERNAL_REVIEWS_2026-10-08.md s6 (annotated on REPORT.md "AMENDMENTS 2026-10-08") | M1 (W1 is a strong prior, not a theorem); M4 (named bottleneck per failed rung); M5 (cognitive accounting; archive off at final eval; shuffled-history and random-library controls); M6 (cheap exploration, expensive proof) |
| Operator direction for longer and deeper reachability testing | directive 2026-10-10 s18-s19 (PROBE -> SCREEN -> DEEP -> EXTENDED <= 72 h; run-length telemetry) | run structure |
| Phase 3 forensic intake (Tantalus) and the M1 drain re-entry manifest | docs/phase3/intake/tantalus/seats/Ensorain.md; ops/fleet/M1_DRAIN_2026-10-03/P2B_REENTRY_MANIFEST.jsonl (Ensorain row) | F-T1, F-T2 |
| Seat history | ensorain/ENSORAIN_WTP03_REPORT.md s3 (W1-W4); roles/Ensorain/DEFECTS.md | F-W3 |

Each finding below is marked as fitting the implementation or not, with the reason.

## Triage table (task B)

| finding | source | class | evidence | next packet |
|---|---|---|---|---|
| F-H1 Prescribed organisms: 490 menu types, all f(index) -> R regressors with hand-coded policies; no working state, program, module or promotion | dossier s3b, s4 wall 1 | SCIENTIFIC_LIMITATION (fits; the seat reached the same conclusion: WTP-03 "known physics", N6 beats 9/9) | ensorain/wtp/organism.py; collider.py:241 "no symbolic-rule substrate" | E1: TAPE organism (working state + LTM + typed module graph + duplication/promotion + bounded plasticity) |
| F-H2 Worlds without necessity: payoff = static harvest + squared error; credit delay is a no-op; lookahead never paid | dossier s3b, s4 wall 2 | CONFIRMED (fits). The WTP-04 eval confirms it: credit delay is flat 0..64 (6-7 of 12 pay at every level); rollout policy is 0 paying | RESULTS_WTP04_MAP.md s2 | E1: worlds A/B/C with hidden state, delayed action-contingent payoff, composition |
| F-H3 Reachability desert made of NOISE: field-op chains destroy information; weirdness and learnability anti-correlated by construction | dossier s3a, s4 wall 3; WTP-03 s4 | SCIENTIFIC_LIMITATION (fits) | 0/2000 random admissible; 3/181 wild | E1: weirdness from hidden state, composition, delay and law switches, never added noise or masks (directive s27) |
| F-H4 Free addressing: the organism is handed the global cell index | dossier s3c | CONFIRMED (fits; organism.py ravel_multi_index) | -- | E1: WTP-05 worlds give LOCAL observations only; the junction identity is ambiguous by design |
| F-H5 Off-lattice topologies trap the organism | dossier s4 wall 4 | CONFIRMED, preserved as recorded in WTP-04 (32 TRAPPED cells). Not repaired: out of scope | eval_score.json | none (WTP-04 record stands) |
| F-H6 Throughput: per-sample python loops; open-ended organism search out of reach | dossier s4 wall 5 | CONFIRMED_DEFECT for WTP-05's purpose (resource) | WTP-04 eval: ~29 s wall per unit at 3 workers (~86 core-s per unit; corrected 2026-10-10) | E1: a new small vectorised world/organism engine; throughput measured in PROBE before any sizing (directive s18, s30) |
| F-H7 N6 omitted from PREREG_WTP04 s10 | dossier s5 | ALREADY_DISCLOSED in WTP-04 s10/s7; WTP-04 not reinterpreted | RESULTS_WTP04_MAP.md s4 | E1: null ladder includes N6 where meaningful (directive s11) |
| F-H8 Dossier: "no WTP-04 eval rows on main" | dossier s0, s5 | ALREADY_REPAIRED | ensorain/runs/wtp04/eval.jsonl @87965d589 | none |
| F-H9 HSNA (hidden-state necessity assay) with a kill criterion: if a menu organism or null already captures H >= .6, the world does not need state | dossier roadmap | ADOPTED as WTP-05 admission discipline | -- | E1: Goldilocks admission (directive s12), with the HSNA kill clause carried into the prereg |
| F-W4a Single-axis perturbation shrinks or preserves inherited islands; it does not create them | RESULTS_WTP04_MAP.md s1 | SCIENTIFIC result (preserved) | 4 dead families 0-1/53 | E2: two-axis revival sub-assay on F01/F06/F11 (directive s25) |
| F-W4b All WTP-03/04 matter is tensor-native completion | RESULTS_WTP04_MAP.md s4-s5 | SCIENTIFIC_LIMITATION | -- | E1: >= 1 non-tensor-native family (directive s26) |
| F-W4c active_sensing baseline not policy-matched; long-life SPLIT/TRAP undiscriminated | RESULTS_WTP04_MAP.md s4 | OPEN (WTP-04 instrument debt; recorded, not repaired here) | -- | none in C-014 unless WTP-05 reuses that axis |
| F-W3 WTP-03 W1 (tautological same-field transfer), W2 (admission pre-selects completion), W3 (founder concentration) | ENSORAIN_WTP03_REPORT.md s3 | SCIENTIFIC_LIMITATION; superseded by the WTP-05 design | -- | E1: transfer to reskinned/reordered/novel compositions (directive s22) |
| F-T1 DEF-ENS-001 (LM01 launch gate cannot accept an MWO carrier); DEF-ENS-002 (REPLICATED not gated on replay) | P2B_REENTRY_MANIFEST.jsonl | OPEN, NOT_APPLICABLE to WTP-05 (LM01 on HOLD) | roles/Ensorain/DEFECTS.md | none |
| F-T2 Gitignored results/ | P2B_REENTRY_MANIFEST.jsonl | ALREADY_REPAIRED in practice: cited rows are force-added; runs/wtp04 is tracked | git ls-files ensorain/runs/wtp04 | none |
| F-M5 Controls: archive off at final evaluation; shuffled history; random library; cognitive accounting ledger | Hestia M5 | ADOPTED | -- | E1 |
| F-M4 Every failed rung names its bottleneck (expressible / reachable / rewarded / credited / detected) | Hestia M4; directive s17 | ADOPTED | -- | E1 (reachability assays) |
| F-COI Same model family as the auditor; agreement is weak evidence | dossier s5 | OPEN | -- | the WTP-05 report requests a non-Claude adversarial review |

## Packets

- C-014-A feedback ingestion -- this section "Sources actually used".
- C-014-B triage -- the table above.
- C-014-E1 WTP-05 DESERT CROSSING: build, prereg, PROBE, SCREEN, DEEP (EXTENDED only if justified).
- C-014-E2 WTP-04 two-axis revival sub-assay (F01/F06/F11), inside WTP-05.

## Outcome
OPEN.
