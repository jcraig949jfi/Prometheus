# ROBUST01 preregistration: is contest arbitration what makes composition fragile?

Seat Aether[m2-fa1b3051], M2 (SPECTREX5, RTX 5060 Ti). Branch aether/robust01-2026-10-17 cut from origin/main
aef5dbd5b. Follows REACH01 (72H_SYNTHESIS.md, item 10). This file and everything it hashes are frozen in their own
commit before any TEST unit runs.

## Question
REACH01's binding constraint: every composition in the XOR physics was position-fragile.
- The planted combiner certified COMPOSE at 26% of tile positions.
- The three discovered compositions certified at 16-51%.
- Promoted-reuse solutions kept COMBINE3 at a median of 1.6% of positions.
- The one autonomous mechanism (LADDER01 s7) was a single-pathway value detector, not a composition.

REACH01's diagnosis was that when two continuous streams merge on one site, the contest law keeps ONE writer, chosen by
a coordinate- and seed-keyed hash. ROBUST01 changes exactly that rule and nothing else, then asks three things again,
with the same planted combiner, the same LADDER01 G1 search and the same reuse protocol:
1. Does the planted COMPOSE become autonomous?
2. Does autonomous composition become discoverable (REACH01: 0/40)?
3. Do promoted-reuse solutions become position-robust, and does genuine reuse clear necessity 0.8 (R4c: 0.66)?

## The one change: aeth01.op_xor_fold (fold_physics.py)
- **Frozen law aeth01.op_xor:** a site written by several valid writers in one tick stores existing ^ winner, where the
  winner comes from the arbitration hash.
- **New law, template fields (opcode, arg0, arg1, payload):** the site stores existing ^ v1 ^ v2 ^ ..., the
  XOR-fold of EVERY valid incoming write. XOR is commutative and associative, so no order and no arbiter is needed.
  With at most one contender the two laws are identical.
- **Unchanged, declared:**
  - the energy field (a winner is still hash-chosen, and every transfer source still pays);
  - energy settlement, write cost, starvation, the 4-slot torus gather, tick order, the execution-only regime
    (write cost 1, maintenance 0, no rain), mutation 0;
  - same-byte cancellation (v ^ v = 0) belongs to the new law.
- **Consequence (invariance theorem, r01_lib.py):** in this regime the energy-field contest is the only path left that
  is keyed to coordinates or seeds.
  - A tile with no energy-field contest therefore behaves identically at every position and under every seed.
  - The certifier's position fraction is no longer an independent robustness test for such mechanisms. It is a
    consequence of the law.
  - ROBUST01 therefore adds a non-trivial generalization test: the held-out input alphabet
    IN_H = (0x12, 0x6D, 0xB4, 0xE9), disjoint from IN = (0x0F, 0x33, 0x55, 0xAA). It also counts energy contests per
    certified candidate, and uses the theorem as an instrument gate.
- **Implementation:**
  - A wrapper, like express01.step: the frozen kernel runs untouched, then each template field becomes existing ^ fold
    where it has at least one contender.
  - fold_physics.install() makes op "XOR" mean the fold law inside a ROBUST01 process; any other op raises. The frozen
    REACH01 search, certifier and reducers therefore run byte-identical, because they look the step up as
    express01.step.
  - r01_run.py wraps each unit and stamps its output with the semantics id and the number of fold ticks executed. It
    refuses express01.py as a script, because that script calls its own step and would bypass the patch.

## Fixtures (test_fold_physics.py: 15 passed at freeze, CPU and GPU)
- The frozen REACH01 files match the hashes their own preregistrations recorded (listed below).
- Fold = the law text, checked against an independent per-site loop on random worlds that have contested template
  writes.
- Fold = contest at every uncontested (site, field); the two differ only at contested sites; the energy field and
  energy settlement are bit-identical to the contest law.
- With no energy writes the fold law is translation- and seed-invariant, while the contest law on the same world is
  not (non-vacuous). The energy-field contest count from gather() equals the loop reference.
- install() maps XOR to fold and raises for REPLACE, ADD and ROTX; uninstall() restores the contest law; the contest
  observer is refused under fold.
- The frozen r3_frontier.Evaluator and r4_accum.Eval3 execute exactly 16 x T_EVAL (resp. 8 x T_EVAL) fold ticks per
  batch, and their final patch states leave the contest law's.
- R2's planted ladder C0-C4 (timed one-shot gadgets, which never have two writers on one site-field in one tick) has
  identical tables under both laws.
- GPU (CuPy) fold is bit-identical to CPU over 3 random 48x48 worlds x 16 ticks.

## Stages, in order, on spectrex5:gpu0 under a Fabric lease
Data root: C:/Prometheus-data/aether_robust01.
Driver: `../REACH01/reach_flight.py <plan> <outdir> --jobs 2 --drain --deadline <ISO>`, which is resume-safe.

**S0, instrument and planted controls** (plan_s0.json; r01_stage0.py, one law per process)
- Contest law (REPRODUCTION gate). It must give back REACH01 exactly:
  - the R3 planted combiner's certificate (COMPOSE, not AUTONOMOUS, position fraction 0.2578125, seeds
    [false, false], a_only 13, b_only 10, shared 0);
  - R4 task 1's transplant table;
  - every REACH01 G1 arm-C discovery's COMPOSE, AUTONOMOUS and position fraction.
  - If it does not, the disposition is INSTRUMENT_DEFECT and nothing further runs until repaired.
- Fold law:
  - P: the planted combiner's certificate, table, held-out rung and invariance check;
  - T: R4 task 1 transplant, 6 offsets x 256 positions;
  - D: the first certified candidate of each of the 7 REACH01 G1 arm-C seeds that found COMBINE (s2, s6, s7, s22,
    s27, s28, s30), certified again. D is descriptive: these were discovered under the contest law.

**S1, discovery** (plan_s1_search.json, then plan_s1_certify.json, then r01_reduce_s1.py)
- LADDER01 geometry G1: inputs (8,1) and (10,1), output (9,6).
- Arms C (certificate-guided) and A (ordinary).
- Seeds 0-39, the same seeds as REACH01. Each unit is 20 x 1024 evaluations; up to 10 COMBINE candidates per unit are
  certified.
- The search code is r3_frontier.py v2, unchanged, so arm A evaluates exactly the same 20,480 candidate patches per
  seed as REACH01's arm A did. Its RNG stream depends only on seed and arm, which makes arm A a paired comparison of the
  two laws.
- One reducer counts both laws. It must reproduce REACH01's published G1 numbers before it decides anything:
  - arm C: COMBINE 7/40, COMPOSE 3/40, autonomous COMPOSE 0/40, autonomous 1/40;
  - arm A: 0/40 throughout.
  - The pre-freeze check below passes this gate on REACH01's own data.

**S2a, assisted reuse** (plan_s2a_search.json, then plan_s2a_reduce.json)
- R4's 32 units exactly: planted component, R3 tile, third input C (9,1), alphabet (0x33, 0xCC), arms N S U P,
  seeds 0-7, 20 x 1024.
- Run under the fold law, and reduced by the frozen r4_reduce.py with S0's fold transplant table.

**S2b, genuine reuse** (r01_stage2b.py: deterministic from S1's reduction, then its own two plans)
- Candidate pool: arm-C certified candidates that are AUTONOMOUS and free of energy contests. COMPOSE candidates come
  first, then COMBINE-only ones; within each group, order by (seed, discovery eval).
- The first candidate that passes both checks below becomes the component (Na U Nb with exact states):
  1. SUFFICIENT: the component alone is COMBINE at G1.
  2. KNOWN ANSWER on R4c's task (G1 + input C at (12,1)): strictly dependent on a and b, not on c, with
     in2 = (0x55, 0xAA). Only if that fails, try (0x33, 0xCC).
- R4c's 32 units are then run under the fold law and reduced by r4_reduce.py with this component's own transplant
  table.
- No such component: REUSE_NOT_TESTABLE.
- Note: r4_reduce.py stamps its label as "ASSISTED CONTROL" in both stages. S2b is GENUINE, and the result document
  carries that label.

## Decision rules (RULES.json)
**S0**
- PLANTED_COMPOSE_AUTONOMOUS iff the fold certificate is COMPOSE and AUTONOMOUS (r3_certify definitions); otherwise
  PLANTED_NOT_AUTONOMOUS.
- Transplant: R4's rule, COMBINE >= 0.2 at >= 2 non-zero offsets.

**S1** (k = arm-C seeds out of 40 with >= 1 certified candidate that is COMPOSE and AUTONOMOUS)
- Gates first, in this order:
  - INCOMPLETE: a unit or certificate is missing;
  - REDUCER_DEFECT: the reproduction gate fails;
  - INSTRUMENT_DEFECT: a candidate with zero energy-field contest events has non-identical seeds, or a position
    fraction outside {0, 1}; or a unit is not stamped with the fold semantics.
- Then by k:
  - k >= 12: ROBUST_COMPOSITION_COMMON (the x4 "archive-assisted" bar, 12/32, applied to 40 seeds)
  - 2 <= k <= 11: ROBUST_COMPOSITION_DISCOVERABLE (LADDER01's ">= 2 seeds" discovery bar)
  - k = 1: ROBUST_COMPOSITION_RARE
  - k = 0, arm-C COMPOSE >= 1: COMPOSITION_STILL_FRAGILE
  - k = 0, no COMPOSE: NO_COMPOSITION
- Qualifier on a ROBUST_COMPOSITION_* label: HELDOUT_GENERAL if >= 2 arm-C seeds have such a candidate that is also
  COMBINE on IN_H; otherwise HELDOUT_NOT_GENERAL.
- Reported with Wilson 95% intervals for both laws and both arms: COMBINE, COMPOSE, AUTO_COMPOSE, AUTO_ANY.

**S2a / S2b**
- r4_reduce.py's frozen dispositions under REACH01/R4/RULES.json:
  - CUMULATIVE_ACQUISITION_ADVANTAGE, COMPOSITION_REUSE_SUPPORTED, TRANSPLANT_SUPPORTED or REUSE_NOT_SUPPORTED;
  - the main thresholds: seeds_min 6/8, controls <= 2/8, necessity >= 0.8, P cost <= 0.5 x U's.
- Plus ROBUST_REUSE iff P acquires COMBINE3 in >= 6/8 seeds AND P solutions' median position fraction is >= 0.9.
  - R4 under the contest law: 0.016.

## Predictions, written before any fold-law run of the planted combiner or of any discovered mechanism
- **P-S0-1, planted combiner under fold:** the position-0 table is exactly a ^ b (7 distinct outputs over IN x IN);
  the held-out rung is 2.
  - Derivation: under either law a relay chain obeys p_k(t+1) = p_k(t) ^ p_(k-1)(t). That is linear over GF(2), so
    p_k(t) = a * C(t-1, k-1) mod 2.
  - The fold law makes the combiner linear too. Over T_EVAL = 24 ticks the output carries a with coefficient
    C(23, 19) and b with C(23, 20).
  - 23 = 10111b. Neither 19 = 10011b nor 20 = 10100b has bit 3, so by Lucas both coefficients are odd.
- **P-S0-1b:** COMPOSE with a_only = 18, b_only = 19, shared = 1.
  - a_only is the 18 A-path cells: row 6 cols 2-17, then (7,17) and (8,17). b_only is the 19 B-path cells.
  - shared is the combiner. Inerting any of these breaks its chain outright.
  - AUTONOMOUS, with position fraction exactly 1.0 and both alternative seeds COMBINE.
  - energy_multi = 0, template_multi > 0 (the merge).
  - Disposition: PLANTED_COMPOSE_AUTONOMOUS.
- **P-S0-2, transplant under fold:** 1.0 at (0,0) and 0.0 at all 5 non-zero offsets. TRANSPLANT still fails.
  - The planted interface is GEOMETRIC: the inputs write into fixed cells. It is not a contest artefact, and the fold
    law cannot repair it.
- **P-S0-3, D:** descriptive. No prediction registered.
- **P-S1:**
  - Fold arm C finds COMBINE in more than 7/40 seeds, and fold arm A in more than 0/40, on A's identical candidates.
  - Disposition ROBUST_COMPOSITION_DISCOVERABLE (k between 2 and 11).
  - Instrument gate passes (0 violations).
  - Not every candidate is autonomous: random search material contains energy writers (arg1 % 5 == 4 in ~1/5 of
    writers), so energy contests remain.
- **P-S2a:**
  - CUMULATIVE_ACQUISITION_ADVANTAGE again (P >= 6/8, N and S <= 2/8, necessity >= 0.8).
  - Plus ROBUST_REUSE: the median P position fraction is >= 0.9, against 0.016 under the contest law.
- **P-S2b:** if testable, COMPOSITION_REUSE_SUPPORTED or better (necessity >= 0.8, against R4c's 0.66).

Interpretation is fixed in advance:
- If S0 and S1 come out as predicted but S2a's robustness does not, contest semantics was the bottleneck for designed
  and discovered composition, but not for search-built reuse solutions. Energy contests and surroundings would then be
  next.
- If S1 gives NO_COMPOSITION or COMPOSITION_STILL_FRAGILE, contest arbitration was not what kept discovery at 0/40.

## Budget, stopping, disclosure
- **Compute:** GPU only, one card, spectrex5:gpu0 leased and renewed, --jobs 2.
  - REACH01 measured ~350 s per G1 search unit at --jobs 2. Fold adds a gather pass of unknown cost.
  - Estimate: S1 ~4-6 h of search plus certification; S2a ~1-1.5 h; S2b ~1-1.5 h. Hard stop 48 h after the freeze
    (driver --deadline).
  - Archaeon holds spectrex5:cpu12 (8 processes); ROBUST01 takes no CPU lease and uses about 2 cores.
- **Operator priority:** if the operator's GPU work (ComfyUI, D:/skullport-gfx) returns, the running plan is stopped.
  Units are resume-safe; it resumes when the card is idle.
- **No escalation is preregistered.** A 4x replication of S1 would need its own preregistration.
- **Seen before this freeze:**
  - The fixtures above, which include fold runs on random worlds and on R2's C0-C4 gadgets.
  - Plumbing smoke runs through r01_run.py: seed 999 (outside 0-39), 16- and 32-evaluation units, a fake random-patch
    candidate, and plan writing with forced checks. None produced a COMBINE or touched a planted or discovered
    object under fold.
  - The S1 reproduction gate, run on REACH01's own G1 data (no fold data): it reproduces 7/3/0/1 and 0/0/0/0.
  - Not run under the fold law before the freeze: the R3 planted combiner, the R4 component, any REACH01-discovered
    mechanism, and any seed 0-39.
- **Not done here:** no RunPod, no paid compute. The shared RunPod account is in use by the Skullport seat.

## Hashes (sha256)
Filled at freeze; see FREEZE.sha256 in the same commit.
