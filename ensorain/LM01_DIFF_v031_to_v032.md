# WTP-LM01 v0.3.1 -> v0.3.2: every scientific change and why it is permitted pre-result

Authority: the operator amendment of 2026-09-28 (roles/Ensorain/prompts/2026-09-28_lm01_v032_amend/, verbatim). Source of
every change: the independent pre-result review (ensorain/arc3/reviews/LM01_ADVERSARIAL_REVIEW.md, findings F1-F15),
written with NO campaign data. No campaign seed was ever derived and no campaign row exists.

Preserved unchanged as the audit trail:
- v0.3.1: freeze commit 768ea8ce9e84a1a078bba34813908d4fafbb268b, FREEZE.json at 87d06770c; file copies in
  ensorain/lm01/archive_v031/;
- the review;
- the pre-data adjudication addendum (ensorain/arc3/LM01_ADJUDICATION_ADDENDUM.md) and its script. They applied to
  v0.3.1 and are superseded by the in-code gates below. They are not modified.

Permission rule used for every row: fix a DEFECT or add a MISSING MEASUREMENT identified before any result, without
changing LM01's question, worlds, families, levels, arms-as-selected (FROZEN_SELECTION.json), rung grid, DELTA, the
dev TESTABLE frame, or campaign size. NOT retrofitted (operator): PKG-F, HMM, Bayes-oracle and causal-state findings.

| # | operator item | review | v0.3.1 | v0.3.2 | why permitted pre-result |
|---|---|---|---|---|---|
| 1 | 1 | F4 | 6.1 was read in every TESTABLE stratum, with TESTABLE gated on the best of S/L/H, not on the headline pair | G1: 6.1 is read only if CI.lo(L-R - N1) > .30 on campaign rows; equivalence readings also need rung - N1 lo > 0; else UNTESTED_HEADLINE_NOT_LEARNABLE | reconciles the declared comparison with its gate. Without it, "equivalent" can mean "both learned nothing" |
| 2 | 1 | F5, F15a | no headline positive control; NULL borrowed the eviction control | HEADLINE POSITIVE CONTROL fixture per level (planted noisy rank<=3 worlds, dev seeds 9_890_000-007): if it cannot fire, a non-firing headline reads UNRESOLVED_INSTRUMENT_CANNOT_FIRE. NULL requires this control | a missing control; the headline's power was untested. It adds no world to the campaign |
| 3 | 1 | F15h | B* was the first EQUIVALENT rung from the bottom (non-monotone curves possible) | B* = the smallest rung from which ALL larger rungs are EQUIVALENT (and above the N1 floor) | code-prose defect: the prose "B*" presumes monotone sufficiency |
| 4 | 2 | F6, F14 | SELECTIVE charged ALL-parameter reads per training batch; LOSSLESS charged one store read per query; ALS reads not multiplied by iterations. 6.2 eligibility used these | COMMON READ CONVENTION record_reads (records touched x record_bytes x passes/iterations) for every arm; 6.2 eligibility = persistent bytes AND record_reads, used identically for SELECTIVE_ADVANTAGE and the secondary COUNTERMODEL. Declared query convention Q = 1 evaluation of the full headline test set per life. query_ops recorded separately | the accounting defect made 6.2 unreadable in 33 of 38 strata by convention, not by resource use |
| 5 | 3 | F7 | the declared candidates were called "relevance-selective"; keep_worst behaves as a recency buffer; no recency reference | the candidates are named SURPRISE-DRIVEN heuristics. A FIFO RECENCY reference arm runs at both eviction points. Labels: HEURISTIC_ADVANTAGE / HEURISTIC_BUYS_BYTES / RECENCY (beats random, not FIFO) / RANDOM_BEATS_HEURISTIC / HEURISTIC_EQUIVALENT_TO_RANDOM. F-C scope: surprise-driven retention | implementation vs prose disagreement (operator item 3); the reference is a missing measurement |
| 6 | 3,4 | F15b | only INDISCRIMINATE_EQUIVALENT was gated on E6, although prose s7 said "every 6.3 label" | EVERY 6.3 label is UNRESOLVED_E6 where E6 fails. E6 is computed on the CAMPAIGN rows (per-world oracle vs random, already measured) | code-prose defect |
| 7 | 4 | F8 | F-C@c could fire from saturation | HEADROOM gate per eviction point: CI.lo(random@full - random@B) > .30, else UNTESTED_NO_HEADROOM | missing gate; without it a falsifier can fire from a ceiling |
| 8 | 4 | F10 | matched-HR2 used the factor readout's in-sample fit; clamped interpolations silently matched to the full store | the reservoir's reconstruction map is MEMORY-BASED (the buffered exact record where retained, else the factor readout); clamped matches are UNMATCHED | the matched quantity must measure memory, not training fit |
| 9 | 4 | F9, F15g | N_REP from the wrong variance (warm reservoir) and not TOST; falsifiers not marked pending replication | N_REP per reading from THAT reading's paired SD on the campaign rows (win: one-sided 80% at 2 x DELTA; equivalence: TOST 80%), floor 8, cap 64 -> UNREPLICATED. Falsifiers AND supports carry the replication status | defect in the replication rule; symmetry was stated but not implemented |
| 10 | 4 | F15d, f | CROSSOVER / INSTRUMENT_FAILURE / UNREPLICATED not implemented; sensitivity reused the 0.30 frame | implemented; GENERATOR_DEPENDENT over every reading type; sensitivity uses each delta's own dev frame | code-prose defects |
| 11 | 5 | F13 | curves only in a separate plan | analysis.curves() ALWAYS emitted per stratum, incl. UNTESTED: rung AC CIs, B as a fraction of history, HR2, the three loci, record_reads, query/fit ops | operator item 5; no rule depends on it |
| 12 | 6 | F14 | loci not recorded | per arm: stored_record_bytes, hypothesis_bytes (persistent learned state), transient_hypothesis_bytes (L-R's per-query fit), query_ops vs fit ops | operator item 6; measurement only |
| 13 | - | F1 | records admitted after the reservoir's last periodic refit were never fitted | END-OF-LIFE REFIT (BufferALS.finalize) before any prediction, for every reservoir arm incl. dual and E6 | measurement defect (an unfitted tail of up to ~100 records) |
| 14 | - | F12 | F5 SELECTIVE ladder scale counted the nuisance mode; F1 trigger compared L-K with the per-world MAX ladder point | F5 ladder on the real-cells scale (as the reservoir, operator 2026-09-26 item 3); F1 trigger vs the fixed cap nearest cells/4 | consistency defect; winner's-curse defect in a calibration check |
| 15 | - | F15e | prose s4/s5 said RandomMerge IM-rate/IM-bytes and the relative selectivity reading were part of LM01; campaign.py never computed them | prose corrected: those readouts belong to the instrument calibration (fixtures), not to the campaign rows | documentation defect; nothing removed from the measured data |

| 16 | 1 | F5 | EXACT_RETENTION_PAYS required L-R to WIN over EVERY rung incl. 2c (37-73% of the history) | the WIN rule uses the genuinely BOUNDED rungs, B <= c (at most one record per cell). 2c is still measured and reported, and used for B*/NULL | DESIGN DEFECT: 2c holds 37-73% of the history, so it is not a bounded state. Evidence, stated as it fell: in the degenerate SD 1.0 control (disclosed) no level could fire. In the declared SD 0.3 control (after R1) the v0.3.1 rule would fire at L2 (L-R - 2c = .491 [.344, .638]) but NOT at L3 (.157 [.113, .201]), while the <= c rule fires at both. So the repair rests on the design argument plus the L3 result (pre-freeze confirmation, ensorain/arc3/reviews/LM01_V032_CONFIRM.md). THIS IS THE ONE v0.3.2 CHANGE TO A HEADLINE CRITERION; flagged to the operator and the reviewer. |


## Rows 17-25: the pre-freeze review of the v0.3.2 draft (ensorain/arc3/reviews/LM01_V032_PREFREEZE_REVIEW.md)

The review recommended FREEZE AFTER LISTED FIXES; its findings are N1-N8.

| # | review | change | why permitted pre-result |
|---|---|---|---|
| 17 | R1 | the WIN rule also requires every bounded rung above the N1 floor. The headline positive control was rerun at a DECLARED noise SD 0.3: the first control (SD 1.0) was degenerate, "firing" against rungs below N1 | the same floor the sufficiency readings already had; removes an asymmetry favouring the lossless label |
| 18 | R2 | LTC rescoped to "beats a random-subsample reservoir". The per-cell sufficient-statistic identity is stated as a limitation. SUFFSTAT table readout REPORTED ONLY (a deterministic function of the stored records; no verdict uses it) | wording overclaimed; the reported readout measures operator item 6 (loci) without a new world or arm in any verdict |
| 19 | R3 | disclosure of #16's dev projection: 4 dev strata UNRESOLVED -> LTC (F2-L3-spectral, F5-L3 cp/tt/spectral; bounded rungs above N1). The v0.3.1-set label is reported as a descriptive column | full disclosure of a rule change made with dev rows in hand |
| 20 | R4 | fixtures_v032.json, FIXTURE_RERUN_v032.json and this diff added to the freeze list; a missing fixtures file raises; the draft status word is DRAFT until the freeze commit | freeze mechanics |
| 21 | rec. | symmetric recency attribution: RECENCY_LOSES (random beats heuristic AND FIFO; heuristic EQUIVALENT to FIFO) is not a falsifier | FIFO could previously block only supports, not falsifiers |
| 22 | rec. | GENERATOR_DEPENDENT, CROSSOVER and multiplicity count LIVE readings only | gate outcomes are not verdicts; chance counts were inflated |
| 23 | rec. | the 6.2 confound label widened (optimizer, model class, regularization, tuning point); the 4 L-K strata are declared structurally ineligible in 6.2 | disclosure |
| 24 | N5 | G1, E6 and headroom read campaign rows (disclosed). New labels are listed: INDEX_NOT_REQUIRED, UNRESOLVED_UNMATCHED, RECENCY, RECENCY_LOSES, UNRESOLVED_E6, UNTESTED_NO_HEADROOM, UNTESTED_HEADLINE_NOT_LEARNABLE, UNRESOLVED_INSTRUMENT_CANNOT_FIRE | disclosure |
| 25 | minor | dual-matching clamp flagged at BOTH ends of the random ladder; comment fixed ("highest buffer slot", not "most recent") | code-prose accuracy |

Not changed (and why):
- The rung grid incl. 2c (still run and reported). The EXACT_RETENTION_PAYS comparison set changed (row 16), with
  fixture evidence.
- The frozen arm selection.
- DELTA .30.
- TESTABLE (dev) frame.
- N = 48.
- Families, levels and seeds.
- The fixed rank-3 readout (F11): a data-adaptive lossless readout would change the experiment, so it goes to LM02.
