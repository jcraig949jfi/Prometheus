# C-017-T030 PREREGISTRATION v1.0.0 -- Z80 Atlas: can the Observatory attribute WHO WROTE THE BYTES?

Author: Argus[harry1-6668fa07], claude-opus-5-5 (Q2), headless on harry1, 2026-10-11. Branch argus/c017-t030 from base
1f85d6d62. Committed BEFORE the freeze (FREEZE.md) and before ANY confirmatory run. No confirmatory seed (17_050_xxx) has been
executed by anyone. Read-only against archaeon/, prometheus/z80atlas/, roles/Archaeon/; no Archaeon seed or bundle file used.
Coordinator decision being implemented: ops/campaigns/C-017/tasks/C-017-T030/TASK.json `problem` (from rso/z80/SELECTION.md s1).

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

A run with no functional organism (s4.3) has no class to score; it leaves the Q1 denominator and is reported per arm.

**Ground truth drifts with evolution, and the horizons were chosen to keep it (disclosed design choice, dev seeds 17_03x_1xx,
none of which is in DEV_CHECK.json):** under task reward, RECON populations converted to genuine endogenous transmission (a copier
operand mutated so the parent writes the function) in 3/12 runs by epoch 100 (competence_gated), 0/12 under implicit_survival
(ENV share >= 13/14 in every run); H and seeded populations at 200 epochs were partly taken over by a reproducer that copies only
by executing the target cell's code (zero writes with a zeroed neighbour, 224 foreign steps; tags K) in 2/16 dev runs, and 0/36
at 80 epochs. H_EXT_SHORT was cut from 30 to 10 epochs because by 30 epochs mutation (rate .03/byte/birth) had broken most
runner-written copiers. The instrument reported the drifted mechanisms correctly; the horizons only keep the CONSTRUCTED answer
the true one. This is itself a finding (ONBOARDING.md s3).

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
3. **Functional organism:** F0 = solves the run's 8 probe ECHO cases (own SplitMix64 stream "z80attr", seed) with a ZEROED
   neighbour; or situ = at its last observed opportunity it read or executed neighbour memory and solves the same 8 probe cases
   WITH the neighbour it had. Neither is the engine's score.
4. **Organism label** (assay.label), by sufficiency, other bytes zeroed: P bytes alone carry F0 -> ENDO; else R alone -> EXT; else
   I alone -> INS; else if the bytes WITHOUT K do not carry F0 -> ENV; else OTHER. Not F0 but situ -> ENV. A parent-written copy
   outranks a kept copy (a converted reconstructor is ENDO).
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
- **Q2** origin, same rule, pooled over every unforged functional run of an arm with a GT origin.
- **Q3** forgeries (assay.forge), zero tolerance, every kind present. Built from the first 8 records of their source arm:
  LABELS (H_EXT_SHORT: every stored label claims endogenous / clean; spec init "random") and PLANT (NH_ENDO_SHORT: every
  stored label claims discovered) must leave class AND origin equal to the source record's; PHYS (H_EXT_SHORT reproduction
  edited to ENDOGENOUS_COPY; NH_ENDO_SHORT transplant removed, init random), TAPE (H_EXT_GATED: one final tape replaced, "a
  child window the parent's execution did not write") and GEN (NH_ENDO_SHORT: generations raised to >= 12) must be refused with
  REPLAY_MISMATCH.
- **Q4** the label reader b1 (engine score, generation, spec physics label) and the bytes-only detector b2 (F0, generation, "writes
  a functional copy of itself into a zeroed window": the T020 D reading) are scored by Q1 on the same rows; EACH must fail Q1.
- **Verdict:** NOT_QUALIFIED if Q1, Q2 or Q3 fails; else UNDERPOWERED if a Q1 class or Q2 is unpowered; else UNINFORMATIVE if a
  baseline passes Q1; else ATTRIBUTION_QUALIFIED (scope s11). Power at the expected n (48 ENV / INS, ~72 ENDO): a detector with a
  true per-run error rate of 2% passes Q1 with probability .985 / .999, at 5% with .78 / .93, at 10% with .28 / .41.

## 6. Seeds and N

seed = base + 1000 * arm index (subjects.NAMES) + k, k = 1..N. Bases: dev 17_030_000, challenge 17_040_000 (Pallas, free use),
confirmatory 17_050_000. Disjoint from 16_020-16_031_xxx, 16_3xx_xxx, 17_020-17_022_xxx and every integer below 10^6
(tests Seeds). Confirmatory N: 24 per arm, 48 for RECON_ENDO_IMPL and NH_ENDO_SHORT (assay.CONFIRM_N); forgeries on the first 8
records of each source arm.

## 7. Development evidence (dev partition only; disclosed)

- dev/DEV_CHECK.json: the s5 rule applied to dev rows (8 per arm, 48 for the two powered arms): ATTRIBUTION_QUALIFIED on dev, 0
  class errors (ENDO 24, EXT 25, ENV 48, INS 48), 0 origin errors (145), 48/48 forgeries right, b1 wrong on ENV 48/48, b2 wrong
  on ENV 48/48 and EXT 7/25. Rows sha256 6e04917a8e0f676edd81eac3c661d614fd36d6a3f1ff5e0baec257335857c78e.
- red/red_rows.jsonl: suite baseline 42/42 GREEN; each of 27 decision-rule mutants (red/RED_EDITS.json; observe 9, assay 9,
  analysis 9) turns its named test RED.
- The design changes made on dev evidence, in order: counterfactual P (s4.2); origin from founder SOURCE, after a random founder
  that already echoed was called INSERTED (1 dev run); situ on the 8 probe cases instead of the 3 opportunity cases, after a
  RED-row survivor showed a half-competent organism passes 3 cases by luck; the horizons of s3.

## 8. Blinding

The detector receives a blinded record (seed, spec with scheduler_reason "blinded", engine output; assay.blinded); the arm and its
ground truth are joined to the classification afterwards. The classifier is frozen code that reads no arm or label field, so the
blinding is procedural: it prevents a per-run rule change after seeing which arm a run came from, not knowledge of the design.

## 9. Resources (directive s13) and the confirmatory command (NOT run in this packet)

    python -m rso.z80.assay confirm rso/z80/runs/CONFIRM --cleared-by <Pallas challenge ref> i/6     for i = 0..5, two at a time
    python -m rso.z80.analysis rso/z80/runs/CONFIRM.*-6.jsonl.gz

Expected: ~0.8 core-h (dev: 634 CPU-s for 80 records + 40 forgeries; 900 CPU-s for 96 powered records), ~25 min wall at <= 2
processes, < 100 MB per process; local CPU only; no checkpointing (each run is a pure function of (spec, seed), seconds long; a
killed shard is re-run whole). `confirm` refuses on any FROZEN.json mismatch, another Python major.minor, or no --cleared-by
REF; each shard writes CONFIRM.i-6.meta.json (cleared_by, FROZEN.json sha256, environment, rows sha256) beside its rows.
Stopping: all shards complete. Reproducibility: rows are byte-identical on re-run (dev rows reproduced byte-identically across
two code revisions that did not change outcomes); the rows sha256 is printed per shard.

## 10. Controls against the directive's distinctions and the C-016 lessons

| Requirement | Here |
|---|---|
| no self-relative contrast (ONBOARDING s5.1) | every class is scored against arms built differently, never against the subject with one feature off |
| an endpoint no fixed prior satisfies | a constant detector fails >= 3 classes; the spec-label reader (b1) and the bytes-only reader (b2) are registered to FAIL |
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
5. The P tag rests on two counterfactual pre-windows; a parent whose output depends on the target cell only for other contents
   would be tagged P wrongly. Not observed; a challenge target.
6. The label zeroes non-writer bytes; zero is NOP in this VM. A function that needs a specific non-zero filler would be OTHER.
7. ECHO_forced only; the functional bar is 8 probe cases (a half-competent organism passes with probability 1/256).
8. Run-level majority: a run whose functional organisms are mixed (e.g. 4 ENV in 124 in an ENDO run) is classed by majority; the
   per-label counts are in every row.

## 12. Challenge and repair

No confirmatory run before Pallas (Q3) challenges the frozen surface (directive s9). Pallas may use the dev and challenge
partitions freely, never 17_050_xxx. At most one bounded repair round; a defect found after it is narrowed and recorded as a
limitation, not repaired again.
