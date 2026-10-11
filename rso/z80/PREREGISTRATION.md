# C-017 PREREGISTRATION v1.1.0 -- Z80 Atlas: can the Observatory attribute WHO WROTE THE BYTES?

Author: Argus[harry1-6668fa07], claude-opus-5-5 (Q2), headless on harry1, 2026-10-11. Branch argus/c017-t030 from base
1f85d6d62. Committed BEFORE the freeze (FREEZE.md) and before ANY confirmatory run. No confirmatory seed (17_050_xxx) has been
executed by anyone. Read-only against archaeon/, prometheus/z80atlas/, roles/Archaeon/; no Archaeon seed or bundle file used.
Coordinator decision being implemented: ops/campaigns/C-017/tasks/C-017-T030/TASK.json `problem` (from rso/z80/SELECTION.md s1).

**v1.1.0** (this text): Argus[harry1-0d3b5331], claude-opus-5-5 (Q2), headless on harry1, 2026-10-11, branch argus/c017-t041
from fe5d0d2d1 (C-017-T041, THE ONE bounded repair round, directive s9). Amends v1.0.0 (frozen at e41fff917, FROZEN.json
cad362fa) in answer to the Q3 challenge rso/z80/challenge/REPORT.md (Pallas, C-017-T040). Committed BEFORE the re-freeze
(FREEZE.md v1.1.0) and before any confirmatory run; no 17_050_xxx / 17_080_xxx seed has been executed by anyone. There is no
second repair round: a defect found after v1.1.0 is narrowed and recorded as a limitation (s12).

## 0. Amendment v1.1.0 (what changed, why, and what was decided rather than repaired)

| # | REPORT | Change | Where | Pinned by (RED mutant) |
|---|---|---|---|---|
| A1 | s4.1 P tag (CDIST) | REPAIRED: a parent whose res0 READ the window (reads_nbr > 0: the engine's donor predicate engine.py:33 without exec_foreign / sealed) writes no P byte; every byte it wrote is K. The two-sample counterfactual is kept for parents that did not read (foreign execution, SEAL) | observe.py endo_tags | test_a_parent_that_reads_the_window_writes_no_parent_byte (R1); test_running_into_its_own_fresh_copy_stays_parent_written (R2: exec_foreign must NOT force K -- the 4/21 shape of ONBOARDING s3.2) |
| A2 | s4.2 recipe-separability (coordinator suggestion) | ACCEPTED, with b4 defined mechanistically (below): arm CDIST_ENDO_IMPL registered and scored (gt ENV, recipe reads ENDO); b4 registered as a third Q4 baseline that must fail, with an ENV output | subjects.py ARMS / CDIST / seeds; assay.b4; analysis.BASELINES | test_cdist_arm_is_environmental_where_its_recipe_says_endogenous (R1); test_recipe_reader_reads_the_construction (R3); test_the_recipe_reader_is_a_registered_baseline (R4); test_partitions_are_disjoint_from_every_registered_namespace (R5) |
| A3 | s4.2 Q2 | DECIDED: NARROWED, no ARISEN arm. Q2 is a test of INSERTED origin; ARISEN detection is not tested (s5) | text only | -- (the rule is unchanged) |
| A4 | s4.4 E1 | PINNED: the +0x55 sample is load-bearing (an exec-only parent, XEXEC, whose write follows the target under +0x55 only) | tests | test_both_counterfactual_samples_are_load_bearing (E1 verbatim; also O1, O6) |
| A5 | s4.4 E3 | PINNED: an unforged REFUSED run counts as wrong in Q1 | tests | test_an_unforged_refusal_counts_as_wrong (E3 verbatim) |
| A6 | s4.4 E5 | PINNED: the counterfactual keeps the parent's input; an input-dependent write is P (ENV means the target cell) | tests | test_the_counterfactual_keeps_the_parents_input (E5 verbatim) |
| A7 | s4.4 E2 | PINNED AND STATED: the sufficiency filler is zero; the label is filler-dependent (s11.6) | tests; s11.6 | test_the_sufficiency_filler_is_zero (E2 verbatim) |
| A8 | s4.3 | NARROWING TEXT: s4.2, s4.4, s5, s8, s11 (what ENDO, ENV, origin and ATTRIBUTION_QUALIFIED license) | text | -- |

"Verbatim" = the find / replace strings of rso/z80/challenge/edits.json, loaded by red/make_edits.py, not retyped. E4 was
already S6. Every new or re-pinned test turns RED on its mutant: red/red_rows.jsonl, baseline 51/51 GREEN, 36/36 RED on the
named test (27 v1.0.0 + R1-R5 + E1 E2 E3 E5). O1 and O6 (the counterfactual mutants) were pinned in v1.0.0 by the
copy-the-window-onto-itself parent; that parent READS the window, so since A1 it is K whatever the counterfactual says, and
both are now pinned by XEXEC instead (still RED; the re-pin is recorded in make_edits.py).

**Why the reads rule and not more counterfactual samples (A1).** More alterations (REPORT s4.1 repair i) narrow the set of
invariants but cannot close it; a read is the only way a parent's write can depend on the target's bytes without executing
or sealing them, and the VM counts it. Cost, measured on dev: the rule is coarse in the safe direction. reads_nbr counts ANY
window read, including a read of a byte the parent itself just wrote. In H_ENDO_GATED dev seed 17_030_004, 98 of 3,187
endogenous births had a window-reading parent; under 8 random pre-windows only 7 of those 98 wrote target-dependent values,
and the rule tags all 98 K. Effect on the 208 dev rows common to v1.0.0 and v1.1.0: 0 class and 0 origin changes; organism
counts moved in 2 runs (H_ENDO_GATED 17_030_004: 10 of 125 functional organisms ENDO -> ENV; RECON_ENDO_IMPL 17_037_040: 5
ENDO -> ENV). ENDO can be UNDER-counted at the organism level by this rule, never over-counted (s11.5).

**Why b4 is a mechanistic recipe reader and not Pallas's lookup table (A2).** A table keyed on (physics, init, planted
tape) and filled from the registered arms is the ground-truth table itself: it is right on every arm whose recipe is in it,
including CDIST once CDIST is registered, so it cannot fail and says nothing. b4 instead reads the recipe the way a designer
does: the planted tape (transplant tape 0, or the engine's seeded replicator), executed once over a kin window (itself) --
no copier -> INS; a copier whose WRITTEN bytes alone (unwritten zeroed) carry F0 -> ENDO; a copier that leaves its function
bytes to the target -> ENV; nothing planted -> EXT under EXTERNAL, else NONE; origin INSERTED iff something was planted. It is
right on all ten v1.0.0 recipes (test), has an ENV output (RECON), and reads CDIST -- a planted copier that writes its own
function bytes -- as ENDO, while the replay shows the head was computed from the target. That is the scored row 'recipe says
X, instrument says Y, truth is Y' that the v1.0.0 set lacked. It does NOT make the arm set immune to recipe reading: a reader
that knew CDIST would be right on it too (s11.9).

**Why Q2 is narrowed rather than repaired (A3).** ARISEN function must arise at local budget: about 1 in 8 RANDOM_EXT_GATED
runs at 200 epochs (dev 1/8; REPORT 1/6). For a constant 'INSERTED' detector to fail Q2 at the expected confirmatory n of ~267
(w_max 38), more than 38 ARISEN functional runs are needed: ~300 extra 200-epoch runs of an arm whose arising mechanism is
itself uncontrolled. A seeded bare replicator under EXTERNAL (REPORT s4.2) adds supplied founders that are not F0, but arising
is still the same lottery. Decided before the run: Q2 stays as registered and is reported as a test of INSERTED origin only.

## 1. Question, and what is not claimed

Given a Z80 Atlas run whose final population carries a working ECHO function, can the Observatory say who wrote the bytes that
carry it -- the parent's own execution (ENDO), the runner (EXT), the environment / previous occupant / neighbour (ENV), or nobody
since insertion (INS) -- and whether the function was supplied by insertion or arose in the run (origin), WITHOUT trusting the
engine's provenance, origin, score, `mech` or `spontaneous_replication` fields?

The object is the INSTRUMENT, not an organism. A qualified result means: on constructed populations whose answer is known, the
detector's per-run class and origin are right at the bound in s5, its refusals and invariances hold, and two simpler detectors
fail where it does not. It does NOT mean: that any Z80 organism discovered heredity (the T020 finding stands: the join
"discovered AND endogenously heritable" is unreachable at local budget); that attribution transfers to other worlds, physics or
tasks (s11); or that the bytes alone identify the writer (they do not, s4.1).

## 2. Carrier and pin

World `well_mixed / none / unlimited / fixed`, substrate `vmcopy`, G = 32, layout shared, mutation `local_byte`, task
`ECHO_forced`, N = 128 (T020 carrier; grammar.py FROZEN constants unchanged). Physics ENDOGENOUS_COPY or EXTERNAL; pressure
competence_gated or implicit_survival. Engine: archaeon/z80atlas/{engine,vm,tasks,grammar}.py as of 863d34a55 (unchanged
through base 1f85d6d62), grammar digest in FROZEN.json; proteus/foundry/prng.py. Every pinned file is in FROZEN.json.

## 3. Ground-truth arms (by construction; rso/z80/subjects.py ARMS)

| Arm | GT class | GT origin | Construction | Epochs | Why the class is fixed by construction |
|---|---|---|---|---|---|
| H_ENDO_GATED | ENDO | INSERTED | 13 cells of `task_then_replicate` (tasks.py:90), transplant path | 80 | ENDOGENOUS_COPY: only a parent's execution writes a child (engine.py:317-338, integrity halt :433) |
| SEEDED_ENDO_GATED | ENDO | INSERTED | the engine's seeded-replicator path, init_hybrid (engine.py:176-188) + random fill | 80 | same; insertion through the other native path |
| H_ENDO_IMPL | ENDO | INSERTED | as H_ENDO_GATED, implicit_survival (no task reward: the stochastic copy-noise null of T020) | 80 | same; function not selected |
| H_EXT_GATED | EXT | INSERTED | 13 cells of H, EXTERNAL | 200 | the runner writes every child (engine.py:351-367) |
| H_EXT_SHORT | EXT | INSERTED | as H_EXT_GATED | 10 | same, while most runner-written children still carry an INTACT copier (s4.1) |
| NH_EXT_GATED | EXT | INSERTED | 13 cells of the WITNESS (no copier) | 200 | same |
| RANDOM_EXT_GATED | EXT | ARISEN | random founders only | 200 | same; a function, when present, arose from RNG material |
| RECON_ENDO_IMPL | ENV | INSERTED | all 128 cells RECON: IN/OUT/NOP at 0..2, a copier of bytes 3..31 only (29/32 >= .9) | 100 | the parent never writes bytes 0..2; a child is functional only where the target cell already held them |
| NH_ENDO_SHORT | INS | INSERTED | 13 cells of the WITNESS under ENDOGENOUS_COPY | 30 | no copier: no birth; founders (age < 30 + 30 <= 60) survive max_age |
| RANDOM_ENDO_GATED | NONE | -- | random founders only | 200 | the lottery arm (census 9.6e-6): no function expected; reported, not scored |
| CDIST_ENDO_IMPL (v1.1.0) | ENV | INSERTED | all 128 cells CDIST: IN/OUT/NOP at 0..2; the head WRITTEN as circdist(t0, t2) of the target, then +1; COPY own 2..28 (29/32) | 5 | the head's value is computed from the target cell's bytes 0 and 2 (read): kin target -> IN A / OUT A, empty -> dead. The RECIPE (a copier that writes its own function bytes) reads ENDO |

A run with no functional organism (s4.3) has no class to score; it leaves the Q1 denominator and is reported per arm.

**Ground truth drifts with evolution, and the horizons were chosen to keep it (disclosed design choice, dev seeds 17_03x_1xx,
none of which is in DEV_CHECK.json):** under task reward, RECON populations converted to genuine endogenous transmission (a copier
operand mutated so the parent writes the function) in 3/12 runs by epoch 100 (competence_gated), 0/12 under implicit_survival
(ENV share >= 13/14 in every run); H and seeded populations at 200 epochs were partly taken over by a reproducer that copies only
by executing the target cell's code (zero writes with a zeroed neighbour, 224 foreign steps; tags K) in 2/16 dev runs, and 0/36
at 80 epochs. H_EXT_SHORT was cut from 30 to 10 epochs because by 30 epochs mutation (rate .03/byte/birth) had broken most
runner-written copiers. The instrument reported the drifted mechanisms correctly; the horizons only keep the CONSTRUCTED answer
the true one. This is itself a finding (ONBOARDING.md s3).
CDIST's 5 epochs (v1.1.0): its written head is inside the copy-noise mask and non-21 head states are absorbing per cell, so the
construction decays (REPORT s4.1: F0 125 / 96 / 38 / 14 at epochs 1 / 5 / 10 / 20 on one challenge seed; NONE 8/8 at 100). On
dev, 5 epochs gave 64-107 functional organisms in 8/8 runs (and ENV 4/4 at 10). b2's registered EXT failure likewise rests on
H_EXT_SHORT's 10-epoch horizon (REPORT s4.2: b2 ENDO 6/6 at 10 epochs, EXT 6/6 at 30).

## 4. The instrument (rso/z80/observe.py, assay.py)

1. **Trust root = replay.** The detector's input is a RECORD, the engine's own output for (spec, seed). It replays (spec, seed)
   under observe.replay -- engine.run's population loop re-implemented for the s2 subset, every RNG draw in the engine's order
   with the engine's own SplitMix64, vm.execute, tasks, mutate, copy_noise, random_tape, World.neighbour -- and REFUSES
   (REPLAY_MISMATCH) unless the replayed final population (cell, tape, generation) equals the record's byte for byte; a spec
   outside the subset is refused (UNSUPPORTED). Byte-equality with engine.run is a test (tests Replay, 5 specs) and held at full
   length on every one of the 176 unforged dev records (none refused).
   **4.1 Why replay and not bytes:** a child the runner copied from a copier is byte-identical to one the copier wrote itself; no
   probe of the final bytes can tell them apart. The bytes-only detector (b2, s5 Q4) credits runner-written copiers as endogenous
   in 7/8 dev runs of H_EXT_SHORT. The replay observes WHICH CODE PATH wrote each byte; that is the evidence a label only claims.
2. **Per-byte writer tags** (observe.py:endo_tags, counterfactual): I founder bytes (founder source S = transplant / seeded path,
   R = random_tape); R runner (EXTERNAL birth); M changed by copy noise or background mutation; for an ENDOGENOUS_COPY child, P
   iff the byte is in the parent's res0 write mask AND re-executing the parent (same tape, same input) over two altered
   pre-windows (bitwise complement; +0x55) writes the same value there; otherwise K (kept, or dependent on the target cell's
   prior content: reads, foreign execution, SEAL). The engine's own read / foreign counters are NOT used: they also fire when a
   parent runs its own fresh copy (the reason for the counterfactual; dev check before it: 4/21 ENDO runs mislabelled).
   **v1.1.0 (A1):** and NO byte is P when the parent's res0 read the window (reads_nbr > 0): every byte it wrote is K. Foreign
   execution and SEAL are still decided by the counterfactual (a parent running its own fresh copy stays P). What P now
   licenses: 'written by the parent's execution, which did not read the window, with value and mask invariant under the two
   registered alterations of the target' -- not 'independent of the target' in general: a dependence entering only through
   foreign execution or SEAL and invariant under x -> ~x and x -> x + 0x55 would still pass (s11.5).
3. **Functional organism:** F0 = solves the run's 8 probe ECHO cases (own SplitMix64 stream "z80attr", seed) with a ZEROED
   neighbour; or situ = at its last observed opportunity it read or executed neighbour memory and solves the same 8 probe cases
   WITH the neighbour it had. Neither is the engine's score.
4. **Organism label** (assay.label), by sufficiency, other bytes zeroed: P bytes alone carry F0 -> ENDO; else R alone -> EXT; else
   I alone -> INS; else if the bytes WITHOUT K do not carry F0 -> ENV; else OTHER. Not F0 but situ -> ENV. A parent-written copy
   outranks a kept copy (a converted reconstructor is ENDO). Precedence is SUFFICIENCY, not expression: an organism whose scored
   output comes from kept bytes while a parent-written copy behind them also carries F0 is ENDO (REPORT probe PD; the registered
   rule). Other bytes are zeroed (the filler is pinned: zero, A7).
5. **Run class** = the label held by a strict majority of functional organisms; NONE if none; MIXED otherwise.
   **Origin** = INSERTED iff a founder supplied by the transplant or seeded path carries F0; else ARISEN (a lucky random founder
   is not insertion). Computed only for functional runs.
6. **Never read:** signals, provenance, founders, events, snapshots, telemetry, final_population fields other than cell / tape /
   generation, spec init / scheduler_reason, the record's arm name (test test_classify_reads_no_label_field).

## 5. Decision rule (rso/z80/analysis.py; unit = the run; integers only)

- **Q1** per GT class c in {ENDO, EXT, ENV, INS}: over the unforged runs of c's arms with >= 1 functional organism, the number of
  runs whose class is not c (MIXED, OTHER, REFUSED included) is <= w_max(n_c), the largest w with P(X <= w | Binomial(n_c, 1/5))
  <= 1/100 (rso/witness/ruler.py tail_le, exact). The claim: each class's misattribution rate is below 1 in 5. w_max: n 21-30 -> 0,
  40 -> 2, 48 -> 3, 60 -> 4, 72 -> 6, 80 -> 7. n_c < 21 -> UNPOWERED. Intersection-union over the four classes: no correction.
- **Q2** origin, same rule, pooled over every unforged functional run of an arm with a GT origin. **v1.1.0 (A3): Q2 is a test of
  INSERTED origin.** ARISEN rows come only from RANDOM_EXT_GATED's functional runs (~3 expected at confirmatory N); a detector
  that always says INSERTED passes Q2 for every outcome the run can produce (REPORT s4.2: w_max(n) >= 24 once n >= 184). The
  result must say: 'ARISEN detection is not tested by Q2'. Origin INSERTED = 'a supplied founder was functional'; it is not a
  statement about the lineage of the final population.
- **Q3** forgeries (assay.forge), zero tolerance, every kind present. Built from the first 8 records of their source arm:
  LABELS (H_EXT_SHORT: every stored label claims endogenous / clean; spec init "random") and PLANT (NH_ENDO_SHORT: every
  stored label claims discovered) must leave class AND origin equal to the source record's; PHYS (H_EXT_SHORT reproduction
  edited to ENDOGENOUS_COPY; NH_ENDO_SHORT transplant removed, init random), TAPE (H_EXT_GATED: one final tape replaced, "a
  child window the parent's execution did not write") and GEN (NH_ENDO_SHORT: generations raised to >= 12) must be refused with
  REPLAY_MISMATCH.
- **Q4** the label reader b1 (engine score, generation, spec physics label) and the bytes-only detector b2 (F0, generation, "writes
  a functional copy of itself into a zeroed window": the T020 D reading) are scored by Q1 on the same rows; EACH must fail Q1.
  **v1.1.0 (A2):** and the recipe reader b4 (s0; assay.b4) is a third baseline that must fail Q1. b1 and b2 have no ENV output,
  so each fails Q1:ENV whenever an ENV arm has a functional run: their failure is guaranteed, not tested. b2's failure on EXT is
  the 10-epoch horizon of H_EXT_SHORT (s3). b4 has an ENV output and is right on every v1.0.0 recipe; it can fail ONLY through
  CDIST_ENDO_IMPL (ENV class, n ~72, w_max 6: b4 fails if more than 6 CDIST runs are functional; dev 8/8). If b4 passed, the
  verdict would be UNINFORMATIVE: the instrument would not have been shown to separate the mechanism from the recipe.
- **Verdict:** NOT_QUALIFIED if Q1, Q2 or Q3 fails; else UNDERPOWERED if a Q1 class or Q2 is unpowered; else UNINFORMATIVE if a
  baseline passes Q1; else ATTRIBUTION_QUALIFIED (scope s11). Power at the expected n (48 ENV / INS, ~72 ENDO): a detector with a
  true per-run error rate of 2% passes Q1 with probability .985 / .999, at 5% with .78 / .93, at 10% with .28 / .41. v1.1.0: ENV
  n is now ~72 (RECON 48 + CDIST 24; w_max 6), the power of ENDO; Q2 n ~267 (w_max 38).

## 6. Seeds and N

seed = base + 1000 * arm index (subjects.NAMES) + k, k = 1..N. Bases: dev 17_030_000, challenge 17_040_000 (Pallas, free use),
confirmatory 17_050_000. Disjoint from 16_020-16_031_xxx, 16_3xx_xxx, 17_020-17_022_xxx and every integer below 10^6
(tests Seeds). Confirmatory N: 24 per arm, 48 for RECON_ENDO_IMPL and NH_ENDO_SHORT (assay.CONFIRM_N); forgeries on the first 8
records of each source arm. **v1.1.0:** arm index >= 10 (CDIST_ENDO_IMPL) takes base2 + 1000 * (index - 10) + k with base2 dev
17_060_000, challenge 17_070_000, confirmatory 17_080_000 (base + 10_000 would be the next partition's arm 0); N 24; no CDIST
forgeries (the five kinds keep their v1.0.0 source arms). Confirmatory records: 11 arms, 312 runs (v1.0.0: 288) + 48 forgeries.

## 7. Development evidence (dev partition only; disclosed)

- dev/DEV_CHECK.json: the s5 rule applied to dev rows (8 per arm, 48 for the two powered arms): ATTRIBUTION_QUALIFIED on dev, 0
  class errors (ENDO 24, EXT 25, ENV 48, INS 48), 0 origin errors (145), 48/48 forgeries right, b1 wrong on ENV 48/48, b2 wrong
  on ENV 48/48 and EXT 7/25. Rows sha256 6e04917a8e0f676edd81eac3c661d614fd36d6a3f1ff5e0baec257335857c78e.
- red/red_rows.jsonl: suite baseline 42/42 GREEN; each of 27 decision-rule mutants (red/RED_EDITS.json; observe 9, assay 9,
  analysis 9) turns its named test RED.
- **v1.1.0 re-check (dev only):** DEV_CHECK.json regenerated under the repaired rule, CDIST at n = 8 (dev 17_060_001..008):
  ATTRIBUTION_QUALIFIED on dev, 0 class errors (ENDO 24, EXT 25, ENV 56, INS 48), 0 origin errors (153), 48/48 forgeries
  right; b1 and b2 wrong on ENV 56/56 (b2 also EXT 7/25); b4 wrong on ENV 8/56 (the CDIST runs; w_max(56) = 4) and right
  everywhere else. CDIST ENV 8/8 (731 of 740 functional organisms ENV). Rows sha256
  9275147ce340e1f16b559aeb88357217349d9324a45d0ec189608e6851b13d25. Against the v1.0.0 dev rows: the 208 common rows keep
  every class and origin (organism counts moved in 2 runs, s0 A1). red/red_rows.jsonl: 51/51 GREEN, 36/36 RED (s0).
- The design changes made on dev evidence, in order: counterfactual P (s4.2); origin from founder SOURCE, after a random founder
  that already echoed was called INSERTED (1 dev run); situ on the 8 probe cases instead of the 3 opportunity cases, after a
  RED-row survivor showed a half-competent organism passes 3 cases by luck; the horizons of s3.

## 8. Blinding

The detector receives a blinded record (seed, spec with scheduler_reason "blinded", engine output; assay.blinded); the arm and its
ground truth are joined to the classification afterwards. The classifier is frozen code that reads no arm or label field, so the
blinding is procedural: it prevents a per-run rule change after seeing which arm a run came from, not knowledge of the design.
**v1.1.0:** blinding hides the arm NAME, not the RECIPE: the blinded spec still carries physics, init and the planted tapes, which
is exactly what b4 reads (and why a table of recipes would be right on every registered arm, s11.9).

## 9. Resources (directive s13) and the confirmatory command (NOT run in this packet)

    python -m rso.z80.assay confirm rso/z80/runs/CONFIRM --cleared-by <Pallas challenge ref> i/6     for i = 0..5, two at a time
    python -m rso.z80.analysis rso/z80/runs/CONFIRM.*-6.jsonl.gz

v1.1.0: CDIST adds 24 records of 5 epochs (~1 s each). Expected: ~0.8 core-h (dev: 634 CPU-s for 80 records + 40 forgeries; 900 CPU-s for 96 powered records), ~25 min wall at <= 2
processes, < 100 MB per process; local CPU only; no checkpointing (each run is a pure function of (spec, seed), seconds long; a
killed shard is re-run whole). `confirm` refuses on any FROZEN.json mismatch, another Python major.minor, or no --cleared-by
REF; each shard writes CONFIRM.i-6.meta.json (cleared_by, FROZEN.json sha256, environment, rows sha256) beside its rows.
Stopping: all shards complete. Reproducibility: rows are byte-identical on re-run (dev rows reproduced byte-identically across
two code revisions that did not change outcomes); the rows sha256 is printed per shard.

## 10. Controls against the directive's distinctions and the C-016 lessons

| Requirement | Here |
|---|---|
| no self-relative contrast (ONBOARDING s5.1) | every class is scored against arms built differently, never against the subject with one feature off |
| an endpoint no fixed prior satisfies | a constant detector fails >= 3 classes; the spec-label reader (b1), the bytes-only reader (b2) and (v1.1.0) the recipe reader (b4) are registered to FAIL; a constant INSERTED origin passes Q2 (s5) |
| a stochastic null analogue | H_ENDO_IMPL (copy noise, no selection), RANDOM_ENDO_GATED (lottery), the half-solver tests (luck on few cases) |
| structure from liveness | F0, situ and the counterfactual re-execute bytes; generation is verified by replay, not read |
| behavioural pins | 27 mutants, each RED on a named test (s7) |
| a control the rule gets wrong | b2 on H_EXT_SHORT (runner-written intact copiers) and both baselines on RECON |
| capacity / demand / search / retention / causal / qualification (directive s4) | capacity, demand and search: T020 (SELECTION.md s3), not re-litigated; causal: the sufficiency label is a bytes-level knock-in; qualification: this packet |

## 11. Scope and known limits (what ATTRIBUTION_QUALIFIED would and would not license)

1. Replay-dependent: the instrument qualifies attribution for records whose (spec, seed) it can replay -- the s2 subset of this
   pinned engine. Without replay, writer attribution of copier lineages is not identifiable from bytes (s4.1); that is a property
   of the engine, not of the detector.
2. Horizon-bounded ground truth (s3): qualification is on populations within 10-200 epochs of insertion, horizons chosen so the
   constructed mechanism still holds. Longer evolution produces mechanisms (kin-dependent reproduction, converted reconstructors)
   whose class is not fixed by construction; the instrument labels them, but no arm here checks that label against truth.
3. One ENV construction at population scale (RECON, kept bytes). Neighbour-dependent function (a parasite running a host) is
   covered by unit known answers only: a parasite / host population does not persist (hosts one mutation from self-function,
   pilot 6 runs; parasites cannot reproduce under ENDOGENOUS_COPY).
4. ARISEN is scored only through RANDOM_EXT_GATED's functional runs (about 1 in 8 at dev); Q2 is dominated by INSERTED arms.
5. (v1.1.0) The P tag. A parent that READ the window writes no P byte (reads_nbr > 0, A1); for the rest, P rests on two
   counterfactual pre-windows, so a target dependence entering only through foreign execution or SEAL and invariant under both
   alterations would still be P (none constructed; CDIST, the constructed case, enters through reads). The reads rule is coarse
   in the safe direction: a parent that reads back its own fresh write is K (dev: 91 of 98 reader births in one H_ENDO_GATED run
   were target-independent), so ENDO organism counts are lower bounds. ENDO also includes writes that depend on the world's
   INPUT (pinned, A6): 'environment' in ENV means the target cell's prior content, nothing else.
6. (v1.1.0) The label zeroes non-writer bytes; zero is NOP in this VM, and the label is FILLER-DEPENDENT where a kept byte is an
   operand (REPORT W2: a kept jump operand, zeroed, is a no-op -> ENDO; filled with the other NOP opcode 0x1E -> ENV). The zero
   filler is pinned (A7), not shown to be the only reasonable choice. A function that needs a specific non-zero filler is OTHER.
7. ECHO_forced only; the functional bar is 8 probe cases (a half-competent organism passes with probability 1/256).
8. Run-level majority: a run whose functional organisms are mixed (e.g. 4 ENV in 124 in an ENDO run) is classed by majority; the
   per-label counts are in every row. The 8-probe-case bar is per RUN: one challenge seed in 999 makes every half-solver
   'functional' (REPORT s4.3); registered arms carry no half-solvers; an evolved one would be judged by its run's eight cases.
9. (v1.1.0) What ATTRIBUTION_QUALIFIED would license (REPORT s4.3): the frozen rule agrees with construction on eleven arms at
   their registered horizons (Q1) -- ten of them recipe-separable, one (CDIST) where the recipe reads ENDO and the truth is ENV --
   label edits cannot move it and byte / physics / generation edits are refused (Q3), it is replay-dependent and engine-pinned,
   and three simpler readers fail (Q4): two of them for want of an ENV output and a horizon (b1, b2), one (b4) on the CDIST rows
   only. It does NOT license: 'independent of the target' for ENDO (s11.5); 'ARISEN detectable' for origin (s5 Q2); 'better
   than the recipe' in general -- a recipe table that included CDIST would be right on all eleven arms; the instrument's
   separation from such a reader rests on Q3, on the replay itself, and on the single CDIST construction.

## 12. Challenge and repair

No confirmatory run before Pallas (Q3) challenges the frozen surface (directive s9). Pallas may use the dev and challenge
partitions freely, never 17_050_xxx. At most one bounded repair round; a defect found after it is narrowed and recorded as a
limitation, not repaired again. **v1.1.0 IS that round** (C-017-T041, s0). The re-check of the repaired surface is C-017-T042
(dev 17_06x / challenge 17_04x and 17_07x seeds; never 17_050_xxx or 17_080_xxx); what it finds is narrowed, not repaired.
