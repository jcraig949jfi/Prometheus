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

| 16 | 1 | F5 | EXACT_RETENTION_PAYS required L-R to WIN over EVERY rung incl. 2c (37-73% of the history) | the WIN rule uses the genuinely BOUNDED rungs, B <= c (at most one record per cell). 2c is still measured and reported, and used for B*/NULL | FIXTURE-DEMONSTRATED DEFECT: the new headline positive control (planted noisy rank<=3 worlds) could NOT fire under v0.3.1's rule at any level. L2 dev: L-R minus c/8..c had CI.lo .78-1.13, but L-R minus 2c only .25; L3: .70-1.28 vs 2c .13. A comparison that cannot fire in its own positive control is an instrument defect (operator item 1). THIS IS THE ONE v0.3.2 CHANGE TO A HEADLINE CRITERION; flagged to the operator and the reviewer. |

Not changed (and why):
- The rung grid incl. 2c (still run and reported). The EXACT_RETENTION_PAYS comparison set changed (row 16), with
  fixture evidence.
- The frozen arm selection.
- DELTA .30.
- TESTABLE (dev) frame.
- N = 48.
- Families, levels and seeds.
- The fixed rank-3 readout (F11): a data-adaptive lossless readout would change the experiment, so it goes to LM02.
