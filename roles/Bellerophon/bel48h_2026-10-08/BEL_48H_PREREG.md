# BEL-48H PREREGISTRATION -- Bellerophon, campaign BEL-48H-2026-10-08

Directive: roles/Bellerophon/prompts/2026-10-08_bel48h/00_OPERATOR_DIRECTIVE_verbatim.md (MANIFEST beside it).
Campaign clock: started 2026-10-08T05:14Z; ends 2026-10-10T05:14Z. Host: ubu005 (8 cores, 22 GB). The prometheus-worker
service on this host is left untouched: at most 6 campaign workers.
Kernel under test: prometheus/z80atlas at d36012f0b (DEF-BEL-008/009/010 switches), branch
bellerophon/def-bel-008-010-2026-10-06. Instrument: tools/belinst.py (measurement-only; invariance-tested).

This file is append-only. Each window's section is committed BEFORE that window's first confirmatory run; a
later change is a dated AMENDMENT below the section, never an edit of it.

## 1. Rulers and definitions (all windows)

- res      historical RESEMBLANCE lineage label (writer vs target by which the child resembles more).
- prov     DEF-BEL-008 PROVENANCE label: writer / target / constructed, from recorded write provenance.
- vec      per-child-byte provenance: W writer-copied, T target material, C constructed (non-copy write),
           X copied from outside [0,2L), E fresh memory. MIXED-ORIGIN birth: W >= L/8 AND T >= L/8.
- SR_res / SR_prov   the historical self-copy classifier (world._is_self_copy) given the res / prov label.
- FUNC(tape)  independent functional test: the tape executed ALONE (empty window, panel input 42,7,99,3, the
           world's budget and chemistry) lays down >= 0.9 L window bytes copied from its own tape by its own code AND
           the written bytes equal the tape at >= 0.9 L. Uses neither lineage ruler nor the DEF-BEL-010 rule.
- TRB      TRUE REPLICATIVE BIRTH: FUNC(writer pre-tape) AND FUNC(child) AND prov == writer.
- trb_depth   TRB chain length through writers. SUSTAINED_TRB: trb_max_depth >= 3 AND >= 1 alive organism with
           trb_depth > 0 at the end. (The historical analogue is sr_max_depth >= 3 AND sr_alive_end > 0.)
- SPONT_res / SPONT_TRB   a RANDOM-init, no-transplant run with >= 1 SR_res birth / >= 1 TRB.
- Mechanism signature (DETECTOR level only): (dominant window-writing opcode, lowest writing PC // 4, executed own
  PCs // 4) of a FUNC tape. Counts of signatures are descriptive and never a claim of distinct mechanisms.
- Geometry rulers: geometry._eval replicates under rep_rule v1 and written, seed 7, the configured task.

Independence (directive s4): the unit for every rate is the RUN (an independent random start). Births inside a
run are never counted as independent; pooled birth counts are descriptive only. Independent ORIGINS = runs whose
first TRB arose with no transplanted or seeded replicator in the run. A specimen measured twice is one specimen.

Finding classes (directive s7): CAUSALLY_CONFIRMED, REPRODUCED, PROVISIONAL, DETECTOR_ONLY, CONFOUNDED, FALSIFIED,
INSTRUMENT_FAILURE. Historical physics and corrected measurement are always reported side by side; no historical
row is relabelled.

Instrument self-tests (tools/tests/test_belinst.py, run before freeze): hook invariance (end-state hash with and
without DualWorld over 5 reproduction modes x 2 inits); FUNC positive (replicator, COPYALL replicator), negative
(all-NOP), cheat (bare LDIR, self-smear, 1-byte capture) all as expected; a seeded world yields TRB with depth >= 3
and a smear-transplant world yields 0 TRB; driver stepping == World.run(); lockstep controls.

## 2. Pilot disclosure

Before this freeze a 44-run calibration pilot ran (seeds 77,000,000+; ~/bel48h_runs/pilot; excluded from every
analysis). Seen: run times (LOCAL 4-12 s; WELL_MIXED up to 170 s); in non-SR births res and prov disagree often
and 'constructed' births are common (e.g. COPY/WELL_MIXED 3,025 of 3,507 births res=writer, prov=constructed);
PARTIAL/WELL_MIXED has ~59% mixed-origin births; SR_res, SR_prov and FUNC-child counts nearly coincide (102 / 102
/ 103). These observations are therefore NOT confirmatory hypotheses below; they are re-measured as descriptive
quantities. The pilot's seeded control ran under EXTERNAL reproduction by my error (reproduction unset); the plan
sets every field explicitly.

## 3. WINDOW 1 -- corrected baseline (frozen 2026-10-08, before any W1 run)

Plan: tools/plan_w1.py -> 3,240 runs, sha256 cd08ec6314484482394f5fba069b99459a7630cdbd94580dc432a98796923e9a
(A1 200, A2 80, A3 200, A4 40 plain; B1 1,800, B2 500, B3 120 dual; C1 300 lockstep). Seeds 48e12 + lane*1e9 + k.
Physics v2, GRID, 256 cells, 500 ticks (C1: 300), budget 256, IMPLICIT unless stated.

The directive's five arms (historical / provenance only / paired init only / written-byte only / all three) are
realised as follows, and lane A establishes empirically which of them can differ at all:
  - provenance only and written-byte only are MEASUREMENTS on the historical trajectory where A1 shows the switch
    is physics-invariant: lanes B compute res+prov and v1+written on the same run (exact pairing, no seed noise);
  - paired init only can change a trajectory only when the init layout contains a transplant or seed (A3, A4);
    its scientific content is the pairing quality, measured in C1;
  - all three: lane C1's PAIRED arm runs with every switch's corrected measurement in shadow.

Predictions (confirmatory; each states what would falsify it):
- W1-P1 (008 physics-invariance under IMPLICIT): A1 RESEMBLANCE vs PROVENANCE end-state hashes identical in 100/100
  pairs. Falsified by any differing pair.
- W1-P2 (008 changes physics where replications feed selection): A2 differs in >= 1 of 40 pairs. If 0/40 the switch
  is measurement-only there as well (reported, not a failure of the switch).
- W1-P3 (009 no-op without transplant/seed): A3 identical in 100/100 pairs. A4 differs in >= 19/20 pairs.
- W1-P4 (SR robustness): pooled over B1+B2, SR_res and SR_prov differ in < 1% of SR_res births, and the fraction of
  SR_res births whose child is not FUNC is < 5%. Falsified by either bound failing.
- W1-P5 (spontaneity survives): pooled B1, SPONT_TRB > 0 (Wilson lower bound > 0) and SPONT_TRB <= SPONT_res run-
  wise; McNemar on (SPONT_res, SPONT_TRB) per run reported. Per cell, a historical "P(spontaneous) > 0" claim (G1a,
  G1b) SURVIVES if SPONT_TRB >= 1 in that cell.
- W1-P6 (sustained, G2): the SUSTAINED_TRB rate among SPONT_TRB runs is within +-10 points of the historical
  sustained rate measured on the same runs. Reported either way.
- W1-P7 (G6a, origin by copying): >= 90% of first-TRB writers in SPONT_TRB runs were themselves born by an
  endogenous birth (writer_mech != init).
- W1-P8 (pairing value, 009): under PAIRED, the world RNG diverges within <= 5 ticks in >= 90% of C1 pairs, and the
  variance of the paired difference in final_alive is NOT reduced by PAIRED relative to HISTORICAL by more than a
  factor 0.8 (bootstrap 95% CI of the variance ratio PAIRED/HISTORICAL includes values >= 0.8). The prediction is
  that init-only CRN pairing buys little at 300 ticks. Falsified if the CI upper bound is < 0.8.
- W1-P9 (010): among first-SR_res writers and dominant SR tapes, geometry v1 and written agree on >= 95% of
  ENDOGENOUS_COPY specimens; disagreements concentrate in ENDOGENOUS_PARTIAL (descriptive).
Controls (B3): pos_seeded_replicator SUSTAINED_TRB in >= 27/30; cheat lanes 0 TRB in 30/30 each. A control failure
voids the B lanes' interpretation until diagnosed (INSTRUMENT_FAILURE).

Descriptive (no prediction): res x prov confusion per cell; mixed-origin fraction; constructed fraction; alive
genetic roots and depths under each ruler; fraction of alive organisms whose genetic root differs between rulers;
TRB mechanism signatures per cell; C1 transplant effect estimate under each arm.

Review gate: the two adversarial reviews of d36012f0b run in parallel with W1. If either finds a defect in a switch
used here, the affected lane is rerun after the repair and both versions are reported.
