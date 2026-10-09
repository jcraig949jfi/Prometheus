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

ERRATUM (2026-10-08T05:58Z): s5's header says "frozen 2026-10-08T06:30Z"; the freeze is commit ebc3daaaa, pushed at
05:57Z. W4 is queued behind the W2 -> W1 v2 chain (~/bel48h_runs/chain_w4.sh waits for CHAIN_DONE).

ERRATUM (2026-10-08T06:02Z): the W4 freeze commit is ebc3daaae (ebc3daaaea3b2770bf9fa9ffbbedf698877cced6); the previous
erratum and the ledger row wrote "ebc3daaaa" by typing error. The queued script uses the correct pin directory.

## 6. WINDOW 3 -- replication reachability (W3a frozen 2026-10-08T08:15Z, before any W3 run)

Seen before this freeze: the W2 frozen analysis (BEL_48H_CORRECTED results to come; ~/bel48h_runs/analysis/w2.json),
incl. that 24/27 H1 first-FUNC tapes arose IN_PLACE (lazy detection), and the reach summaries (origin-event counts,
LDIR critical 27/27, portability, ramp flags). W3a therefore re-measures the SAME 27 origins with an eager instrument;
its rules below are partly informed by W2 and are labelled DISCOVERY. Confirmation on fresh, unseen origins is W6.

W3a plan: tools/plan_w3.py -> 27 replays of the W2 H1 runs with a first FUNC tape, sha256
e52ba28da5c0ec69007286bd186cba389dc712b964224c83be8879ecf91b8444, instrument tools/origin.py (eager change tags m/s/u/v/i;
first-FUNC event dissection; per-byte reversion; carrier history). Each replay must reproduce its W2 end-state hash.

Frozen classification of each origin event (unit = run = independent origin):
  CAUSE      origin_event.kind: MUTATION | SELF_CONSTRUCT | UPTAKE | SELF_MOVE | BORN_<class>
  STEPS      number of changed critical bytes whose individual reversion kills FUNC (necessary_changed)
  PRECURSOR  old_copy_extent (own-position bytes the tape laid down just before the event): 0 = none; 1..57 = partial
             copier; >= 58 = near-copier that failed the 0.9 L bar for another reason
  ASSISTED   the carrier was born by another organism's writes (carrier_mech != init) AND >= half of its critical bytes
             were acquired by inheritance at birth (critical_via 'i')
  PATHWAY    ATOMIC if PRECURSOR == 0 and STEPS >= 2; SINGLE_STEP_FROM_NOTHING if PRECURSOR == 0 and STEPS == 1;
             INCREMENTAL if PRECURSOR > 0; ASSEMBLY if CAUSE in (UPTAKE, BORN_ASSEMBLY, BORN_CONSTRUCT)
Discovery predictions (from the grounding round's G6 reading "short ramp ending in a small step"):
- W3-P1: STEPS == 1 in >= 60% of origins.
- W3-P2: PRECURSOR > 0 (INCREMENTAL) in >= 40% of origins.
- W3-P3: replay identity 27/27 (a failure is INSTRUMENT_FAILURE and voids W3a).
- W3-P4: LDIR is among the critical bytes in 27/27 (dependence on LDIR); NOP-slide dependence (FUNC lost when zero
  bytes become HALT) in >= 50%.

ERRATUM (2026-10-08T08:03:47Z): s6 says "W3a frozen 2026-10-08T08:15Z"; the freeze is commit 4995e8b45, W3a launched 2026-10-08T08:03:32Z.
Timestamps in this file are from now on taken from the shell clock, never written by hand.

### AMENDMENT 2 (2026-10-08T08:44:22Z) -- independence: seeds are shared across cells within a lane

Found while reading W3a (four 'independent' origins carried the same founder machine): every plan in this campaign
seeds a run as SEED_BASE + lane * 1e9 + k, so run k of EVERY cell in a lane starts from the SAME initial population and
world-RNG stream (H1: 550 runs / 150 distinct seeds; W1 v2 B lanes: 2,300 runs / 400 seeds; W4: arms of a lane share k
by design). The pattern is inherited from the grounding plan (G1: 7 cells x 400 runs on 400 seeds). Within a cell runs
are independent; ACROSS cells they are not.
Rules from now on (W1 v2 results not yet read; W2/W3a already reported are corrected in their reports):
  (1) the independent unit for any claim pooled across cells is the DISTINCT SEED (initial population); pooled counts
      are reported per run AND per distinct seed (a seed counts once, positive if positive in any of its cells), and
      'independent origins' = distinct seeds;
  (2) per-cell results are primary; the frozen pooled tests (W1-P4..P7) are still computed and reported, flagged
      CLUSTER_DEPENDENT, with the per-seed version beside them;
  (3) W4 arms that share a seed are PAIRED by construction: the frozen Fisher tests stay primary (conservative under
      positive pairing) and an exact McNemar on seed-pairs is reported beside each;
  (4) every NEW plan uses a distinct seed per (lane, cell, k) unless pairing is the stated design.

## 7. WINDOW 5 block 1 -- complementation repair and its ablation (frozen 2026-10-08T08:47:44Z, before any W5 run)

Motivation (seen before this freeze, all W2/W3a): causal assemblies continue after the fragment founders die (A: 223 of
407 by later-born non-FUNC writers); function persists while first-assembly lineages die (W2 s2.D); W3a origins are
completed by single changes in copy-born carriers. Hypothesis COMPLEMENTATION REPAIR: under ENDOGENOUS_PARTIAL the
target's surviving bytes complete the defects of degraded copiers, so functional machinery is re-made continually.
Intervention: the kernel's target_fill = "zero" (unwritten child bytes are fresh zeros, not the target's): births still
happen, target material does not survive. Plan tools/plan_w5.py: 240 runs, sha256
a35cc27ba461bec4c9b454e15e0444518546a8d12cbbca693ee42fe7ebe9457e; arms paired by seed; distinct seeds per block/level.
Endpoints (unit = seed-pair): FUNC_END = func_alive > 0 at the last tick; REPAIR_BIRTHS = FUNC-child births whose writer
pre-tape is NOT FUNC (heredity classes ASSEMBLY + CAPTURE + CONSTRUCT) per run.
- W5-P1: E5a HIGH, FUNC_END preserve > zero: exact McNemar on discordant pairs, two-sided p < 0.05 with preserve-only >
  zero-only. (MED reported; prediction only for HIGH, where repair should matter most.)
- W5-P2: E5a, REPAIR_BIRTHS higher under preserve in each mutation level: sign test over pairs (ties dropped),
  one-sided p < 0.05 per level.
- W5-P3: E5b, causal assembly in >= 90% of preserve runs and <= 5% of zero runs.
Exploratory block: findings are PROVISIONAL until confirmed on fresh seeds in W6.

## 8. WINDOW 5 block 2 -- reachability consequence of target material (frozen 2026-10-08T12:09:20Z, before any run)

Plan tools/plan_w5b2.py: 400 runs (200 seed-pairs, arms paired by seed = same initial population), sha256
84c0ceda246e08474e64f8560265aa8707450d68bcb242bc531891ffa873f5a8; RANDOM init, ENDOGENOUS_PARTIAL, WELL_MIXED, 500 ticks;
target_fill preserve vs zero; OriginWorld. Analysis tools/analyze_w5b2.py (committed with this section).
- W5-P4: a first FUNC event occurs more often under preserve than zero: exact McNemar on seed-pairs, p < 0.05 with
  preserve-only > zero-only. (Reasoning: chimeric births complete cryptic precursors; uptake is unaffected by
  target_fill because the partner is in the window either way.) Causes and pathways per arm are descriptive.

## 9. WINDOW 6 block 1 -- confirmation on unseen independent populations (frozen 2026-10-08T12:09:20Z, before any run)

Plan tools/plan_w6.py: 1,300 runs, one DISTINCT seed per run, sha256
c1c9c39550f4091f344b36f9e668c20ad5b3aa453bad5360466d1cfadfc5e7fa. Analysis tools/analyze_w6.py (committed with this
section; classification = analyze_w3.classify, unchanged). Unit = run = independent population.
C1 (origin pathway, from W3a discovery; 400 runs each PARTIAL / PAIR / COPY, WELL_MIXED):
- C1-P1: completing event is a MUTATION in >= 50% of origins.
- C1-P2: among in-place origins, exactly one necessary changed byte in >= 50%.
- C1-P3: the pre-event tape copies 0 own bytes (cryptic precursor) in >= 60% of origins.
- C1-P4: >= 1 UPTAKE origin whose taken-up bytes are individually necessary (steps >= 1).
- C1-P5: ASSISTED (copy-born carrier, >= half its critical bytes inherited at birth) in >= 50%.
- C1-P6: LDIR critical in >= 95%.
C2 (distributed persistence, W2 s2.D post-hoc there; 100 fresh A-fragment worlds):
- C2-P1: FUNC alive at the end in >= 95% of runs AND the first assembly event's TRB lineage alive at the end in < 50%
  of runs with an event AND function alive with NO assembly event's TRB lineage alive in >= 20% of runs.

## 10. WINDOW 5 block 3 -- entangled vs separated architecture (frozen 2026-10-08T15:31:32Z, before any run)

Motivation: W4 found 16/20 evolved ECHO machines ENTANGLED (competence- and copy-critical bytes shared; answer produced
through the child copy) and one SEPARATED form. Question: does selection favour entanglement, and does it depend on
payment for the computation? Plan tools/plan_w5b3.py: 192 runs, sha256
94e7bbd0de22185ea3113de6ddb01a35ed70a52ae731a66cbe56082e0571b7c4; E = w4_00735, S = w4_00963 (both FUNC and competent,
verified); physics v3 ECHO K40, PAIRED init, 300 ticks; coupling ON/OFF x mutation MED/HIGH x slot order ES/SE; 24
seeds per level shared by the four arms. Census (comp.founder_census): every living FUNC organism is attributed to E or
S by the founder mechanisms of its FUNC-critical bytes (mixed / neither excluded). E_share per seed = mean over the two
slot orders of E/(E+S). Analysis tools/analyze_w5b3.py (committed with this section; smoke-tested).
- W5-P6: under ON + HIGH, E_share > 0.5 in more seeds than < 0.5: one-sided sign test p < 0.05 (entanglement favoured
  where mutation threatens the separated computation and the computation is paid).
- W5-P7: pooled over both levels, E_share(ON) > E_share(OFF) within seed in more seeds than the reverse: one-sided sign
  test p < 0.05 (the advantage depends on payment).
Exploratory; specimens are single representatives of each architecture (generality limit).

## 11. WINDOW 6 block 2 -- generality of two-fragment complementation (frozen 2026-10-08T18:16:03Z, before any run)

Plan tools/plan_w6b2.py: 720 runs, sha256 d093d10956b27bbfd2515075bb171c75ace7cbd305af1e2e4258d2b0810a02c1. Three
confound-free variants from evolved machine shapes, asserted at build time (A, B non-FUNC; composite FUNC; 0 single-
substitution FUNC mutants of A and B in both physics; A holds NO LDIR and writes its 2 bytes by CONSTRUCTED writes):
V0 = LD T,0x40 @13 + LDIR @34; V1 = LD T,0xA0 @4 + LDIR @10; V2 = LD T,0x40 @30 + LDIR @45. Arms per variant (40 paired
seeds): PARTIAL {AB, A, B, none}, PARTIAL target_fill zero AB, ENDOGENOUS_COPY AB. Endpoint FUNC_ANY = a first FUNC tape
occurs. Analysis tools/analyze_w6b2.py (committed with this section; smoke-tested on 18 short runs; before freezing,
the smoke run showed A-only reaching FUNC, as W2 had, so the draft rule 'A <= 10%' was removed: A is reported only).
Each prediction must hold in EVERY variant:
- G-P1: FUNC_ANY in AB >= 80% of seeds; in B and in none <= 10%.
- G-P2: AB > AB_zero (target material ablated): McNemar on seed-pairs p < 0.05, AB-only > zero-only.
- G-P3: AB > AB_copy (complete-overwrite physics): McNemar p < 0.05, AB-only > copy-only.
- G-P4: in AB runs, the first assembly/construct event is two-source in >= 80%: the child is FUNC, the child with its
  target bytes zeroed is not, and the pre-birth target tape is not.

## 12. WINDOW 6 block 3 -- fresh-seed confirmation of W4's provisional mechanisms (frozen 2026-10-08T18:26:36Z, before any run)

Plan tools/plan_w6b3.py: 600 runs, sha256 56c76cfb766f947a034b50060207b6d5096eaeb17335160493a91db6e9286b9e; K1 ECHO K40 ON,
300 fresh distinct seeds; K2 REP+BAD INC K16 ON, 300 fresh distinct seeds. Analysis tools/analyze_w6b3.py (committed with
this section). Before freezing, the draft E-P2 ('OUT executed from the child copy') was tested on the 20 W4 machines and
found false in 0/20 (see the W4 CORRECTION); it is replaced by the budget-coupling test.
- E-P1: competent dominant machines with >= 1 shared competence/copy-critical byte >= 50%.
- E-P2: BUDGET_COUPLED (a shared byte whose knockout kills competence at budget 256 but not at 512) >= 35% of competent
  dominant machines (W4 post-hoc: 10/20).
- E-P3: repaired machines (K2): modal class SINGLE_LINEAGE_BAD.

## 13. WINDOW 6 block 4 -- uptake necessity, replay receipts, independent architecture pair (frozen 2026-10-08T21:49:07Z, before any run)

Plans tools/plan_w6b4.py: U 1,600 runs sha256 9ee2bd822f5de3ae462893bb06019c484a6d659e1486d1132948ee9ad1266117; R 202
replays sha256 e9e4df127d932d316c2f30780db2ca67211fc518c23fc0449c8855f9351df4ae; X 192 runs sha256
00152553d16726677b5c7a3924f5b93e5ef2abd857464d6ee5243e28e8d25a34 (E = w6b3_00001 BUDGET_COUPLED, S = w6b3_00020 SEPARATED,
first of each class by run id). New ablation tools/uptake_block.py (tested: partner bytes imported into the own tape are
reverted and counted). Analysis tools/analyze_w6b4.py (committed with this section; smoke-tested on all three lanes).
- U-P1 (instrument check): 0 UPTAKE origins in blocked worlds; >= 5 in normal worlds.
- U-P2 (route substitutability): pooled origin count blocked >= 0.7 x normal (falsified if blocking uptake removes more
  than 30% of origins). McNemar on seed-pairs and per-cell counts reported.
- U-P3 (descriptive): MUTATION share of origins per arm.
- R-P1: every replayed run reproduces its recorded end-state hash with the current code (0 voids).
- X-P6: under ON + HIGH, E share > 0.5 in more seeds than < 0.5 (sign test p < 0.05) -- W5-P6 on an independent pair.
- X-P7: at MED, E share ON < OFF in more seeds than ON > OFF (sign test p < 0.05) -- W5 block 3's post-hoc MED reversal
  turned into a confirmatory prediction on an independent pair.

## 14. N1 -- operator-matched completion, predictive test of CL-17 (frozen 2026-10-08T21:54:16Z, before any run)

CL-17 was found POST-HOC (precursor neighbourhoods vs completing cause). This turns it into a prediction on the SAME 55
specimens re-placed in new worlds (not new origins: it tests the mechanism's operator dependence, not its prevalence).
Plan tools/plan_n1.py: 440 runs, sha256 7486853d6b9ec202a4c007c56464bcf02b3e9a201219da1744fe2a71ded6b975; 39 NEEDLE
precursors (completed by mutation, 0 move routes), 16 MOVE_RICH (completed by uptake/self-move, >= 100 move routes);
each transplanted into its origin physics, WELL_MIXED, PAIRED init, 100 ticks, mutation VLOW vs HIGH, 4 paired seeds.
Endpoint: a first FUNC event within 100 ticks. Analysis tools/analyze_n1.py (committed with this section).
- N-P1: NEEDLE precursors complete more under HIGH: mean per-precursor rate difference HIGH - VLOW >= 0.20.
- N-P2: the mutation sensitivity is larger for NEEDLE than MOVE_RICH: bootstrap (over precursors) 95% CI of
  [NEEDLE diff - MOVE_RICH diff] lies above 0.
- N-P3: at VLOW, MOVE_RICH completions are mostly non-mutational (UPTAKE + SELF_MOVE + BORN_ASSEMBLY > MUTATION).

DISCLOSURE (2026-10-08T21:54:31Z): the N1 analysis smoke run (8 runs, pilot seeds 77,995,000+, 20 ticks, 2 precursors per class,
excluded) printed per-class rates before the real runs: NEEDLE VLOW 0.0 / HIGH 0.5, MOVE_RICH 1.0 / 1.0 -- the predicted
direction, at n far too small to inform the frozen thresholds above, which were written before the smoke run.

## 15. B1 -- budget coupling versus the execution budget (frozen 2026-10-09T01:51:36Z, before any run)

Plan tools/plan_b1.py: 600 runs, sha256 bafb99833cf4facc90ab0ea9ee1722000184fe50a860a06c2a2eacdb7724a945; W4 M2 setting
(seeded copiers, v3, ECHO, K40, ON) at budget 192 / 256 / 384, 200 seeds each (seed k shared across budgets).
Classifier tools/analyze_b1.budget_class_b: BUDGET_COUPLED at the run's budget b = a shared byte whose knockout kills
competence at b but not at 2b. Noted before freezing: on w4_00735 the unbounded copy (C = 0) is budget-rescued at 256 but
not at 384 (at 384 it is classified OTHER_SHARED): the 256-byte copy also wraps over the organism's own code and the
inputs, so 'coupling' has a COST component (budget) and a DAMAGE component (wrap-around). B1 does not separate them.
- B-P1: the BUDGET_COUPLED share of competent dominant machines is larger at budget 192 than at 384 (Fisher one-sided
  p < 0.05).
- B-P2 (descriptive): shares at 192 / 256 / 384 monotone non-increasing.

## 16. U2 -- fresh-seed replication of 'blocking uptake raises origination' (frozen 2026-10-09T02:47:36Z, before any run)

Plan tools/plan_u2.py: the W6 block 4 U design with new seeds (57e12 +), 1,600 runs; sha256 printed at freeze in the
execution ledger. Analysis tools/analyze_u2.py (committed with this section; same origin endpoint as U).
- U2-P1: blocked-only discordant seed-pairs exceed normal-only, exact one-sided sign (McNemar) test p < 0.05.

## 17. UF -- mechanism of uptake's net suppression (frozen 2026-10-09T05:01:42Z, before any run)

Hypothesis (from W6 block 4 U): imports mostly destroy the importer's raw copy parts. Plan tools/plan_uf.py: 300 c2fa6a5cef8b4c55f4d7f19e7872a8bf4cac3c8470458cb9e59d9731b4201d00;
instrument tools/uptake_fate.py (invariance-tested); analysis tools/analyze_uf.py (committed with this section). Unit =
run (distinct seeds).
- UF-P1: pooled BREAK > MAKE events (precursor proxy: LDIR AND LD T present), and runs with BREAK > MAKE outnumber the
  reverse (one-sided sign test p < 0.05).
- UF-P2: pooled FUNC_LOSS > FUNC_GAIN on uptake events, and runs with more losses outnumber the reverse (p < 0.05).

## 18. P1 -- architecture-payment effect across a specimen panel (frozen 2026-10-09T07:43:31Z, before any run)

CL-16's reproduced part (paying for computation lowers the budget-coupled share at MED) rests on two specimen pairs.
Plan tools/plan_p1.py: 512 runs, sha256 fe53b694843dd3235d80179bca6188591be7fa03550b8bd0e7a688e3e9db2a22; 4 BUDGET_COUPLED x
4 SEPARATED machines from W6 block 3 K1 (excluding the X pair; first by run id), 16 pairings, MED, ON/OFF x order, 8
seeds per pairing. Analysis tools/analyze_p1.py (committed with this section). Unit = pairing.
- P1-P1: across decided pairings, mean E share ON < OFF in more pairings than the reverse (one-sided sign test p < 0.05).

## 19. S1 -- substrate perturbation of the strongest causal findings (frozen 2026-10-09T09:34:21Z, before any run)

Plan tools/plan_s1.py: 1,760 runs, sha256 0471ecae666050ff40bc0bed5d2fb7a2b335d93041f5633fab98a57ee27cab35. Analysis
tools/analyze_s1.py (committed with this section; smoke-tested 8 runs, 0 voids).
- S1-P1 (CL-20 under a changed world model and step budget): pooled over SOUP/WELL_MIXED and GRID/WELL_MIXED/budget 384,
  blocked-only discordant pairs exceed normal-only (one-sided p < 0.05); per-substrate results reported.
- S1-P2 (CL-04 under changed topology): in BOTH SOUP/WELL_MIXED and GRAPH/LOCAL, AB-only (PARTIAL) exceeds copy-only
  (COPY) FUNC_ANY discordant pairs, one-sided p < 0.05 each.
