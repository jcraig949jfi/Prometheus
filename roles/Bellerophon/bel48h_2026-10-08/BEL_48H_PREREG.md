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

### AMENDMENT 1 to s3 (2026-10-08 ~06:00Z) -- instrument defect found by Review A; W1 re-frozen as W1 v2

Review A (independent adversarial implementation review of d36012f0b) found DEF-BEL-008 PROVENANCE one-hop
(window-sourced copies always credited to the target; scratch-staged copies read as constructed) and a DEF-BEL-010
zero-sweep hole. belinst's byte vector shared the one-hop logic. Repaired at dc1833bc2 (multi-hop material origin in
the VM, measurement only; byte-identity re-verified on 478 cases + golden replay). The W1 run of 5618bd275 was stopped
at 128 results (~/bel48h_runs/w1_SUPERSEDED_def008_onehop; excluded; only lane-A end-hash identity was looked at:
A1 11/11 identical). W1 v2 = the same plan with fresh seeds (SEED_BASE 48.1e12): 3,240 runs, sha256
2212e6aa5c700b368cadd3529fc1cc17a97547a9dac8a8fab48e8788c246fd1d, code dc1833bc2. Definitions changed by the repair
(s1): vec and prov use the multi-hop origin; FUNC counts window bytes whose material origin is the tape's own byte at
the same position, written by its own code (equality implied; zero filler cannot count). Predictions W1-P1..P9 are
unchanged.

## 4. WINDOW 2 -- heredity and genetic provenance (frozen 2026-10-08 ~06:00Z, before any W2 run)

Plan: tools/plan_w2.py -> 1,050 runs, sha256 47dde14c8c030db8b9fe4edd20c93877358e6cd57abb35ae144e90fafb8d2d84, code
dc1833bc2. Instruments: tools/heredity.py (byte founder tags, FUNC-birth classes, causal anatomy), tools/reach.py
(first-FUNC reachability; used here on H1 and analysed in W3).
  H1  fresh random worlds, WELL_MIXED, 500 ticks, historical physics: PARTIAL 150, PAIR 150, COPY 150, COPY/VM_COPY 100.
  H2  fragment complementation, PAIRED init, 300 ticks, 100 seeds per arm: PARTIAL x {AB, A, B, none} + COPY x AB.
      A = prefix writer (copies its LD T,64 into partner window 0-1; not FUNC); B = LD A,1; LDIR (not FUNC).

Pilot disclosure (12 runs, seeds 77.2e6, old one-hop code; excluded): A and AB both produced a FUNC child at tick 0-1
in 3/3 runs (first FUNC = BORN_ASSEMBLY), followed by ~40-58k COPY births; B and none produced no FUNC in 300 ticks.
So A ALONE suffices: the LDIR is supplied by random background material. The H2 predictions below are written with
this known; the confirmatory content is the attribution and heredity analysis, not the existence of assembly.

Definitions: see heredity.py docstring. Critical byte = nonzero byte whose NOP knockout breaks FUNC (zero bytes never
critical). CAUSAL_ASSEMBLY = FUNC child, neither writer-only nor target-only reconstruction FUNC, critical set holds W
and non-W bytes. Unit = run.

Predictions (confirmatory):
- W2-P1 (origin mode, H1): among H1 runs with a first FUNC tape, the share whose first FUNC was BORN (any class) rather
  than FOUNDER/IN_PLACE is >= 0.9 (the grounding G6a 'built by copying' claim under the corrected rulers).
- W2-P2 (multi-source origins depend on physics, H1): the share of first-FUNC origins that are CAUSAL_ASSEMBLY (or whose
  critical bytes have >= 2 distinct origin events) is higher under ENDOGENOUS_PARTIAL than under ENDOGENOUS_COPY
  (Fisher exact, one-sided, alpha 0.05), provided each cell has >= 5 runs with a first FUNC. If a cell has < 5 the test
  is reported NOT_TESTABLE.
- W2-P3 (H2 attribution): in PARTIAL/AB runs with >= 1 CAUSAL_ASSEMBLY event, the critical LD T,64 bytes of the FIRST
  assembly come from an A founder in >= 90% of runs, and the critical LDIR comes from a B founder in a MINORITY (< 50%)
  of runs (the pilot says random background supplies it). Falsified if B supplies the LDIR in >= 50%.
- W2-P4 (H2 heritability of assembled machinery): in PARTIAL/A and PARTIAL/AB, the first assembly event has alive TRB
  descendants at tick 300 in >= 50% of runs where it occurred.
- W2-P5 (H2 physics control): COPY/AB produces 0 CAUSAL_ASSEMBLY events in >= 95/100 runs (a 2-byte write is not a
  viable birth under ENDOGENOUS_COPY).
- W2-P6 (H2 B and none): FUNC appears in <= 5/100 runs of each.
Descriptive: FUNC-birth class mix per cell; distinct origin events and founders among critical bytes of the dominant
FUNC tape at the end; relocated founder bytes; novel kinds (n/c/x) among critical bytes.

ERRATUM (2026-10-08T05:55Z): amendment 1 and s4 say "~06:00Z"; the freeze commit 7133438e5 is the authority, and the
chain was launched at 05:52:58Z (execution ledger). No content changed.

## 5. WINDOW 4 -- computation x reproduction (frozen 2026-10-08T06:30Z, before any W4 run)

Recovered disposition of the coupling campaign (COUPLING_CAMPAIGN_REPORT.md, frozen c9bed96de): READY_FOR_MULTIDAY;
P1 contingent computation raises reproduction HOLDS (40/40), P2 competence enriched HOLDS, P3 heritability HOLDS
(copy fidelity of whole-window copiers, not an evolved property), P4 extinction HOLDS, P5 preservation FAILS at
ceiling, P6 conflict repair FAILS underpowered (4/60 vs 0/60, p 0.125). Scope limit: maintenance of seeded task code;
de novo gain only for ECHO copiers at K40 (29/150 ON vs 6/150). Multi-day E-BEL-MD: LADDER1 and COPIER HOLD, LADDER2
FAILS. None of this is assumed below; each W4 test re-measures under the corrected instruments.

Plan: tools/plan_w4.py -> 1,050 runs, sha256 d2d458f8c8f5402c7e968c7b1925e61d1c8d39678cc4cda219222b7d60d9edba.
Instrument tools/comp.py (CompWorld = HeredityWorld + competence x FUNC per birth + anatomy; invariance-tested).
  M1  REP + BAD fixtures, INC, K16, ON vs OFF, 300 seed-pairs (historical COMMON + V3 configuration).
  M2  SEEDED_REPLICATOR, ECHO, K40, ON / OFF / SHUFFLED, 150 seeds each.
Endpoint COMP_SR_END: >= 1 alive organism that is competent AND FUNC at tick 500 (comp_func_alive > 0). Unit = run.

Predictions:
- W4-P1 (P6 powered): M1 COMP_SR_END ON > OFF, Fisher exact one-sided p < 0.05. FALSIFIED if p >= 0.05 with the ON
  rate <= OFF rate + 0.02; otherwise (p >= 0.05, ON higher) SIGNAL_WEAK.
- W4-P2 (M2 acquisition replicates): COMP_SR_END ON > OFF and ON > SHUFFLED, each Fisher one-sided p < 0.05 (Holm over
  the two).
- W4-P3 (anatomy of repair, M1 ON runs with COMP_SR_END): classify the dominant competent FUNC tape:
  CROSS_LINEAGE if its FUNC-critical bytes include >= 1 REP-founder byte (transplant0) AND its competence-critical bytes
  include >= 1 BAD-founder byte (transplant1); SINGLE_LINEAGE_BAD if every founder byte in both critical sets is BAD's;
  SINGLE_LINEAGE_REP if every founder byte is REP's (task code re-invented in a copier); OTHER. Prediction: the modal
  class is SINGLE_LINEAGE_BAD (repair by in-place change of the BAD machine). Reported with counts either way.
- W4-P4 (protection): among births from competent FUNC writers, the per-run task_loss fraction is lower in M1 ON than
  M1 OFF (Mann-Whitney one-sided over runs with >= 20 such births per arm). Descriptive if fewer than 10 runs qualify.
- W4-P5 (M2 origin of competence): in ON runs with COMP_SR_END, the competence-critical bytes of the dominant tape
  include >= 1 novel-event byte (n or c) in >= 80% of runs (competence is newly made, not found in founder material).
