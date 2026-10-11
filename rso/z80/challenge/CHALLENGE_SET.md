# C-017-T040 -- Q3 challenge set against FREEZE_Z80_ATTRIBUTION v1.0.0 (committed BEFORE any outcome)

Pallas[harry1-b22b3a2d], claude-fable-5-1 (Q3; comms boot tier heavy), headless on harry1 (M4), 2026-10-11. Surface:
rso/z80 at FREEZE_Z80_ATTRIBUTION v1.0.0 (FROZEN.json cad362fa, 27 files; freeze e41fff917 on argus/c017-t030; integrated
on main 843c2b4e9 = this branch's base). `freeze check` OK before the claim. Authority: operator Continuous Observatory
directive 2026-10-11 s9 (freeze, attack, one bounded repair, re-check); packet ops/campaigns/C-017/tasks/C-017-T040/TASK.json;
Palamedes launch note (claim-critical surfaces only). Rules: no production file changed in any commit; mutants applied to
THIS worktree's working copy only and restored byte for byte; challenge seeds 17_040_xxx only (subjects_c.seeds_used(),
conflicts() == [] checked before any record); no 17_050_xxx; no `assay confirm`; archaeon/, prometheus/z80atlas/,
roles/Archaeon/ read-only; <= 2 processes; python -B. Exposure: EXPOSURE.md (informed review; one VM-level scratch check).

## 1. Scoring

    case    AS_EXPECTED       the frozen machinery does what PREREGISTRATION v1.0.0 says and the prediction held
            SURVIVOR          a demonstrated gap between what the registered instrument / inference / reading CLAIMS and
                              what the frozen machinery can SUPPORT (the predicted fault appeared)
            NOT_AS_PREDICTED  the prediction failed; reported with the observed value
            RECORDED          a probe with its prediction checked; bears on the interpretation, not on a verdict
    edit    RED               the named frozen test fails on the mutant (behaviour pinned)
            SURVIVES          the 42-test suite passes on the mutant; the witness shows the behaviour that moved
    surface CLOSED            no survivor whose bearing requires a narrowing, a limitation or a repair before the
                              confirmatory result is read; NOT CLOSED otherwise (with exactly what the result must state)

The mechanical check of each prediction is the `check` expression in expected.json (cases.judge); the narrative verdict
and the bearing are in REPORT.md.

## 2. Subjects (subjects_c.py)

| Name | Definition | For |
|---|---|---|
| CDIST | RECON's IN/OUT/NOP head; child[0] = circdist(target[0], target[2]), child[1] = child[0]+1, COPY own 2..28, keep 29..31 | B1: the counterfactual-invariant reconstructor (s11.5) |
| CDIST_ENDO_IMPL | 128 planted CDIST, ENDOGENOUS_COPY, implicit_survival, 100 epochs: the ENV arm's own settings | B1 arm (GT ENV by observe.py:12-14) |
| XORW | child[0] = target[0] XOR target[2]; COPY own 1..29 | W1: complement-invariant only |
| INPW | child[0] = the parent's input byte; COPY own 1..31 | W5 and probe: ENV is the target cell, not the environment |
| JROP | IN A; JR +byte2; OUT A; HALT | W2: a kept operand under the zero filler |
| DORMANT | [IN A, OUT A, NOP] then [IN A, OUT A] | PD: sufficiency vs expression |
| HALF | the frozen tests' half-solver (echoes inputs < 128) | PL: the per-run probe-case lottery |
| b3 | b1 plus ENV when donor_mixed_births * 2 > births_endo (the engine's own donor counter) | B6 |
| b4 | a fixed table from subjects.ARMS keyed on the blinded spec's (reproduction, init, planted tape) | B6: the recipe reader |

## 3. Cases and predictions (expected.json is the answer key)

### Sound

S1 FREEZE-HASHES. The 27 pins recomputed without freeze.py from the git HEAD blobs and from disk (LF); FROZEN.json's own
LF sha256 = cad362fa..; grammar digest 63ffdeca16db3333; freeze.mismatches() == []. Unscored: the files under rso/z80/ that
FROZEN.json does not list (this directory, demand/, smoke/, pivot/, the four .md records, make_edits.py, red_rows.jsonl,
the DEV_*.jsonl.gz rows). PREDICTION: all hold.

S2 W_MAX. From first principles (math.comb, Fractions): w_max(n) for n in {20, 21, 24, 25, 30, 40, 48, 60, 72, 80, 144,
180, 200, 240, 243, 264} equals analysis.w_max and the PREREGISTRATION s5 table; the smallest n with w_max(n) >= 24.
PREDICTION: agree everywhere; n* <= 200. Bearing (INFERENCE): Q2's ARISEN rows come only from RANDOM_EXT_GATED (<= 24 at
the confirmatory N); at the confirmatory n (240..264; w_max 33..37) a constant INSERTED origin cannot fail Q2 whatever the
run produces. Q2 does not test ARISEN detection.

S3 REPLAY + CLASS on challenge seeds. 6 seeds per registered arm at its registered horizon (17_040_001.. per arm slot):
engine.run vs observe.replay byte-equal (final population AND births); 0 refused; the frozen class and origin vs the arm's
truth (unpowered n, counts reported); record-field audit: a record stripped to (seed, spec, final_population[cell, tape,
generation]) and a record with every spec field neither side reads edited (scheduler_reason, stage, parents, family,
grammar, transplant.from_run, an extra tape beyond N) classify identically. PREDICTION: 60/60 equal, 0 refused, 0 class
and 0 origin errors, 60/60 invariant.

S4 FORGERIES. The five registered kinds on the first 2 records of their source arms. PREDICTION: LABELS 2/2 and PLANT 2/2
invariant; PHYS 4/4, TAPE 2/2, GEN 2/2 refused with REPLAY_MISMATCH. (A record edit that moves class or origin while the
replay matches does not exist: classify is a function of (spec, seed) and the match pins the final population; the only
spec fields that change tags without changing the simulation are the ones the LABELS forgery already covers. Stated as a
reading of assay.classify:79-92, checked by the audit above.)

S5 DEV-REPRODUCE. `python -m rso.z80.assay dev <scratch>/DEV_ROWS 8 0/2` re-executed in this worktree. PREDICTION: rows
sha256 equal to the committed shard.

S6 RED-REPRODUCE. `python -m rso.z80.red.run_red <scratch>/red_rows.jsonl`. PREDICTION: baseline 42/42 GREEN, 27/27 RED on
the named test, identical to red/red_rows.jsonl.

### Broken (constructed populations and readers)

B1 CDIST. Unit: over a kin target the child's bytes 0..1 are (21, 22) = IN A / OUT A and the tags are P P; over an empty
target they are (0, 1): the value CHANGES with the target cell's prior content, which observe.py:12-14 defines as K. Arm
CDIST_ENDO_IMPL, 8 seeds 17_040_501..508. PREDICTION: class ENDO in >= 7/8 (RECON at the same settings is ENV 48/48 on
dev), n_pp_func > 0 in every run, replay-equal 8/8. Bearing: INSTRUMENT NOT CLOSED on the P tag (s11.5 realised); the
two-sample counterfactual admits any target-dependence invariant under x -> 255-x and x -> x+85.

B5 HORIZON. RECON_ENDO_IMPL at 20 / 40 / 60 epochs (seeds 17_047_601..606); H_ENDO_GATED at 200 (17_040_601..612);
H_EXT_SHORT at 30 (17_044_601..606). PREDICTION: RECON@20 INS 6/6; @40 INS or MIXED >= 4/6; @60 ENV >= 4/6;
H_ENDO_GATED@200 >= 1/12 not ENDO; H_EXT_SHORT@30 instrument EXT 6/6 and b2 EXT >= 3/6. Bearing (INFERENCE /
INTERPRETATION): the ground truth of every arm is a statement about the population at the chosen horizon; the horizons
were chosen on dev outcomes (s3); b2's registered failure on EXT is horizon-selected.

B6 READERS. Static: assay.b1 (:144-152) and assay.b2 (:165-168) have no ENV output, so Q4 fails on ENV whenever RECON has
a functional run; a baseline cannot make the set UNINFORMATIVE through ENV. Dynamic, on the S3 rows: b4 (recipe table) and
b3 (donor counter) scored by Q1 and on origin. PREDICTION: b1 / b2 never ENV; b4 0 class errors in all four classes and 0
origin errors; b3 0 wrong on ENV / INS / EXT and <= 2 of 18 on ENDO. Bearing (INFERENCE): the arm set is separable by
the blinded record's recipe; Q1 cannot distinguish 'reads the mechanism' from 'reads the recipe', and no scored row has
recipe != truth (PHYS forgeries are refused, not re-attributed).

B7 CONSTANT-INSERTED on the S3 rows. PREDICTION: wrong = the functional RANDOM_EXT_GATED runs (~1 of 6) <= w_max.

### Probes and frozen witnesses

PL PROBE-LOTTERY. Seeds 17_049_001..999 where HALF passes all 8 probe cases (~1/256); planted HALF x 64, EXTERNAL,
implicit_survival, 1 epoch at a lucky and an unlucky seed. PREDICTION: >= 1 lucky seed; lucky n_func >= 64, unlucky 0.
Bearing: s11.7's 1/256 is per RUN and shared by every organism in it.

W1f XORW over kin: byte 0 K. W5f INPW: byte 0 P with input 7 and 21; with 21 the child is functional and ENDO. W2f JROP
with tags PPKPP..: ENDO. PD DORMANT with tags KKK+P..: ENDO and P-alone F0.

## 4. Edits (edits.json; run_edits.py; witnesses.py)

| Id | Edit | Prediction | Witness |
|---|---|---|---|
| E1 | counterfactual keeps only the complement sample | SURVIVES | W1: XORW byte 0 K -> P |
| E2 | sufficiency filler 0x1E instead of 0 | SURVIVES | W2: JROP ENDO -> ENV |
| E3 | Q1 drops unforged REFUSED rows | SURVIVES | W3: 5 refused ENV rows NOT_QUALIFIED -> ATTRIBUTION_QUALIFIED |
| E4 | control: RED_EDITS S6 (non-strict majority) | RED on test_run_class_is_a_strict_majority | none |
| E5 | counterfactual also empties the input | SURVIVES (judged likely) | W5: INPW byte 0 P -> K |

## 5. Ordering

This file, expected.json, edits.json, subjects_c.py, cases.py, witnesses.py, run_edits.py and EXPOSURE.md are committed
in one commit before `cases records`, `cases score`, `run_edits`, `run_red` or `assay dev` is run. Results: rows.*.jsonl.gz,
results.jsonl, red_rows.jsonl, REPORT.md, in later commits on this branch.
