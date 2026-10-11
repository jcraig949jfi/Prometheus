# C-017-T040 -- Q3 challenge of the frozen Z80 attribution assay (FREEZE_Z80_ATTRIBUTION v1.0.0): REPORT

Reviewer: Pallas[harry1-b22b3a2d], claude-fable-5-1 (Q3; runtime verified at comms boot, tier heavy), headless on
harry1 (M4), 2026-10-11. Surface: rso/z80 at v1.0.0 (FROZEN.json cad362fa, 27 files; integrated on main 843c2b4e9 = the
base of branch pallas/c017-t040). 27/27 pinned hashes verified by `freeze check` before the claim and recomputed
independently from git blobs and disk (S1); `freeze check` OK after every edit was restored. No confirmatory record
exists (seeds 17_050_xxx untouched; `assay confirm` never called). Caveats printed with every record: cell member; writes
no production code; an INFORMED review (every frozen test body and the 27 mutants were read; EXPOSURE.md); same vendor,
different model family from the builder (Argus, claude-opus-5-5). One VM-level scratch check preceded the set (EXPOSURE s2).

## 1. Ordering evidence (git, UTC)

    6970f0355  main    CLAIMED (LEASE.json)                                                        17:46Z
    e229df290  branch  the SET: CHALLENGE_SET.md, expected.json, edits.json, subjects_c.py, cases.py,
                       witnesses.py, run_edits.py, EXPOSURE.md                                      18:05:39Z
    5199b6ca5  main    IMPLEMENTING                                                                 18:10Z
    shards     first harness: records 0/4 and 1/4 ran (rows computed; the digest print crashed on
               a float field of MINE; the rows were read)                                           18:10-18:19Z
    5daa7745f  branch  harness fixes (int timing field; the extra-tape audit was my error, s6.1) and the
                       POST-HOC probe B1h with its prediction, BEFORE it ran                        18:22:10Z
    shards     records 0/4 .. 3/4 under the fixed harness (120 jobs, 132 rows)                      18:22-18:43Z
    edits      run_edits: baseline 42/42, E1-E5, witnesses; score; dev shard 0/2; run_red 27          18:43-18:55Z
    (this)     rows.*.jsonl.gz, results.jsonl, red_rows.jsonl, this report, receipt -- one commit;
               INTEGRATION_READY on main

The set's data files (expected.json's original keys, edits.json, subjects_c.py, witnesses.py, run_edits.py, CHALLENGE_SET.md,
EXPOSURE.md) are unchanged since e229df290 except as 5daa7745f records: cases.py (timing int, the extra-tape audit split
into its own field, B1h jobs and aggregation, and one later one-token fix to the judge's eval namespace) and
expected.json (the B1h key added; the S3 `what`/`check` extended for the extra-tape field). No prediction of the
original set was altered.

## 2. Score (the packet's denominators: >= 1 sound, 2 broken, 2 semantic edits, adversarial populations)

    sound    6 scored: S1 S2 S3 S4 S5 S6 all AS_EXPECTED (s3).
    broken   4 scored: B1 NOT_AS_PREDICTED at the registered horizon (unit fault held exactly; population NONE at
             100 epochs, s4.1) with the labelled post-hoc B1h SURVIVOR (ENDO 8/8 at 5 and at 10 epochs);
             B6 NOT_AS_PREDICTED on its b3 sub-prediction, SURVIVOR on its structural and recipe-reader claims (s4.2);
             B7 SURVIVOR (a constant INSERTED origin passes Q2); B5 NOT_AS_PREDICTED on RECON and H_ENDO@200 (the
             constructed ground truth is MORE stable than I predicted: evidence for the builder's horizons), held on
             H_EXT_SHORT@30 (b2's registered failure on EXT is the 10-epoch horizon, s4.2).
    probes   PL RECORDED (main prediction held, one sub-prediction missed by one mutant organism); W1f W2f AS_EXPECTED;
             W5f PD RECORDED.
    edits    5 applied (find count 1 each), 5 restored and verified (sha256, git diff --quiet), freeze check OK after
             each, the hash guard fired on every mutant (recorded with the mutant in place). E1 E2 E3 E5 SURVIVE the
             frozen suite (42/42 on each mutant) and every witness moved exactly as predicted; E4 (control) RED on the
             predicted test only.
    predictions: 20 committed checks: 12 held as written (S1-S6, B7, W1f, W2f, W5f, PD, B1h); 4 missed (B1 population,
             B5 RECON/H_ENDO parts, B6 b3 part, PL 'other = 0'); the 4 misses are reported with the observed values and
             none of them hides a fault -- three of them are the frozen machinery being RIGHT where I predicted drift.
    cost     ~35 CPU-min (rows 2081 s, dev shard 241 s, 27 + 5 mutants ~6 min, scoring), <= 2 processes, ~90 min wall
             from boot to INTEGRATION_READY; 0 paid; 0 requests to Archaeon; 0 operator interventions.

## 3. CLOSED / NOT CLOSED per surface

    INSTRUMENT       NOT CLOSED on one bounded point: the P tag. PREREGISTRATION s11.5 ('a parent whose output depends
                     on the target cell only for other contents would be tagged P wrongly. Not observed; a challenge
                     target') is now CONSTRUCTED: CDIST (s4.1) writes its child's function bytes as a function of the
                     target cell's bytes, invariant under both frozen alterations; every one of its functional
                     children is tagged P at the head, labelled ENDO, and the run class is ENDO 8/8 at 5 and at 10
                     epochs, where the ground truth is ENV by observe.py's own definition (lines 12-14) and by the
                     engine's own donor predicate (reads_nbr = 2 on every birth). CLOSED: the replay trust root (106
                     records byte-equal incl. births; 0 refusals; stripped and noise-edited records invariant 60/60; a
                     14th transplant tape is placed and refused; S5 reproduces a dev shard bitwise; S6 reproduces the 27
                     RED rows); the forgeries (10/10 as registered; no moving forgery exists, s5.3); the sufficiency
                     label as registered, with two recorded limitations (the zero filler is unpinned and label-changing
                     where a kept byte is an operand, E2/W2; sufficiency credits a dormant parent-written copy over the
                     expressed kept copy, PD -- the registered rule, PREREG s4.4). situ was not challenged by a new
                     construction (the frozen parasite/host unit answers stand).
    INFERENCE        NOT CLOSED on three points, none of which blocks the run: (1) Q2 is passed by a constant INSERTED
                     origin for EVERY possible confirmatory outcome (S2: w_max(n) >= 24 for n >= 184; at the registered
                     n 240..264, w_max 33..37; at most 24 ARISEN rows exist; on the 49 scored challenge rows a constant
                     is wrong once, w_max 3): Q2 does not test ARISEN detection. (2) Q4 cannot fail through ENV (b1 and
                     b2 have no ENV output: assay.py:144-152, :165-168) and b2's registered EXT failure is the 10-epoch
                     horizon (b2 ENDO 6/6 at 10 epochs, EXT 6/6 at 30); a recipe reader on the blinded spec (b4) makes
                     0 errors in all four classes and on origin (54 rows): the arm set is recipe-separable, so Q1 cannot
                     distinguish reading the mechanism from reading the recipe, and no scored row has recipe != truth
                     (PHYS forgeries are refused, not re-attributed). (3) 'REFUSED counts as wrong' (PREREG s5) is
                     unpinned (E3 survives; W3 turns NOT_QUALIFIED into ATTRIBUTION_QUALIFIED). SOUND: w_max is the exact
                     binomial threshold (S2), the intersection-union needs no correction, Q1 makes 0 errors on 49 scored
                     challenge rows across all four classes, and the constructed ground truth held at every horizon I
                     tried (RECON ENV 18/18 at 20-60 epochs; H_ENDO_GATED ENDO 12/12 at 200): the horizons of s3 are
                     not a selection on outcomes in the direction I predicted.
    INTERPRETATION   NOT CLOSED: the result must carry the narrowing in s5.1 (what ENDO, ENV, origin and
                     ATTRIBUTION_QUALIFIED license). Nothing in it changes the registered rule or the run.

Bearing on the run as frozen: NONE (no registered arm is CDIST-like; the registered rule on the registered arms behaves
on challenge seeds exactly as on dev). Bearing on the claim: the one bounded repair round is WARRANTED for the P tag
(an instrument fault inside the preregistered meaning of P), and the Q2/Q4 text must be narrowed whether or not the
repair is made.

## 4. Survivors and their bearing

### 4.1 Instrument: the two-sample counterfactual admits target-dependent writes (CDIST)

The P tag (observe.py:65-70) calls a written byte parent-written iff the parent, re-executed over the complement of the
pre-window and over the pre-window + 0x55, writes the same value with the same mask. These two maps generate the affine
group x -> +-x + c on Z/256; its invariants on a PAIR of target bytes are the functions of +-(a - b), e.g. the circular
distance. CDIST (subjects_c.py) is RECON with the head written instead of kept: child[0] = circdist(target[0],
target[2]), child[1] = child[0] + 1, then COPY of its own bytes 2..28 (29/32 written, >= copy_min_frac). Over a kin target
(21, ?, 0) the head is IN A / OUT A; over an empty target it is (0, 1); over an H target (21, ?, 33) it is (12, 13).

    unit (B1u, as predicted):  kin tags PPPPPPPPPPPPPPPPPPPPPPPPPPPPPKKK, child (21, 22), F0 True, label ENDO;
                               empty child (0, 1) not F0; over H (12, 13); reads_nbr 2 (the engine's donor_contributes is True)
    arm CDIST_ENDO_IMPL        epochs   class      n_ENDO (= n_pp_func, every run)   n_ENV    n_INS   n_func
    (8 seeds 17_040_501..508)  5        ENDO 8/8   74..106                            4..13    0..1    87..113
                               10       ENDO 8/8   25..67                             2..20    0       31..87
                               100      NONE 8/8   0                                  0        0       0  (pop 125..128, ~11,000 births)
    b3 (engine donor counter)  5, 10    ENV 8/8 -- the engine's own reads_nbr-based predicate sees what the counterfactual does not

What the 100-epoch rows mean (post-hoc diagnosis, disclosed in 5daa7745f): the fault is per organism and total (at epoch
1 of seed 17_040_501, 76 of 76 children with a clean head carry PPP; F0 125), but the CONSTRUCTION decays: a written head
byte is inside the copy-noise mask (0.4 % per byte per birth), and a target whose byte 2 drifted (e.g. (21, 22, 234),
itself functional) makes every child written over it dead (circdist(21, 234) = 43); non-21 head states are absorbing per
cell. RECON's kept head is OUTSIDE the mask, so it decays only through deaths. F0 count on that seed: 125 / 96 / 38 / 14
at epochs 1 / 5 / 10 / 20. The post-hoc horizon (5, 10) was chosen on that replay (F0 counts and head tags; the class
was not looked at before the B1h prediction was committed). I am doing to my own arm what s3 does to the builder's:
the honest statement is 'at 5-10 epochs the instrument calls this population ENDO; at 100 it has nothing to call'.

Bearing. The preregistered meaning of P ('written by the parent's own execution ... not dependent on the target cell's
prior content', PREREG s4.2; observe.py:10-14) is not what the code computes: the code computes 'invariant under two
affine alterations'. Any target-dependence that is an affine invariant (circdist; equality of two target bytes; the
parity of a difference) passes as P. ENDO therefore licenses: 'the function-carrying bytes were written by the parent's
execution with values invariant under the two registered alterations of the target' -- not 'independent of the target'.
Repair candidates (the owner's): (i) more alteration samples, including random pre-windows -- defeats affine invariants,
not equality-gated writes (if t0 == t2 write X else Y is invariant under any bijection applied to all bytes); (ii) tag the
whole window K when res0["reads_nbr"] > 0 (a neighbour READ before the write; the engine's own donor predicate,
engine.py:33, minus exec_foreign and sealed which the counterfactual already handles) -- CDIST reads (2), H / seeded /
RECON's copier never read the window (RECON keeps, it does not read), and the 4/21 ENDO dev runs mislabelled by the
counter rule (ONBOARDING s3.2) were exec_foreign cases, not reads; (iii) register a CDIST-like arm at a short horizon
(or the unit answer in tests) so that the repaired tag is pinned. (ii) + (iii) is my recommendation; it is small.

### 4.2 Inference: what Q1, Q2 and Q4 can and cannot establish

Q2 (origin). Origin is INSERTED iff a SUPPLIED founder is F0. ARISEN rows come only from RANDOM_EXT_GATED's functional
runs (1 of 6 here; 1 of 8 on dev; at most 24 at the confirmatory N). S2: w_max(n) >= 24 once n >= 184; the confirmatory
Q2 n is 240..264 (w_max 33..37). A detector that always says INSERTED therefore passes Q2 for every outcome the run can
produce; on the 49 scored challenge rows it is wrong once (w_max 3). Q2's pass is a statement about INSERTED arms. The
result must say 'ARISEN detection is not tested by Q2 (expected ~3 ARISEN rows)'. A repair, if wanted: an ARISEN-rich
arm (e.g. seeded bare replicator under EXTERNAL, where the function must arise) or simply the limitation.

Q4 (baselines). b1 outputs NONE / EXT / INS / ENDO and b2 outputs INS / ENDO / EXT (plus NONE / MIXED through
run_class): neither can say ENV, so 'each baseline must fail Q1' is satisfied by the ENV class whenever RECON has one
functional run, i.e. always; UNINFORMATIVE cannot be reached through the registered baselines. The informative part of
dev's Q4 -- b2 wrong on EXT 7/25 -- is manufactured by H_EXT_SHORT's 10-epoch horizon (chosen, PREREG s3, 'because by
30 epochs mutation had broken most runner-written copiers'): here b2 is ENDO 6/6 at 10 epochs and EXT 6/6 at 30. That is
a real demonstration of s4.1 (bytes cannot tell a runner-written copier from a self-written one) but it is not a test
the detector could fail. b4, a fixed table on the blinded record's (reproduction, init, planted tape), makes 0 class
errors in all four classes (ENDO 0/18, EXT 0/24, ENV 0/6, INS 0/6) and 0 origin errors (0/54): the blinded record
carries the arm's construction (blinding hides only scheduler_reason), the arm set is recipe-separable, and no scored row
has recipe != truth (the PHYS forgeries, where the recipe lies, are REFUSED rather than re-attributed, so the instrument
never demonstrates 'recipe says X, bytes say Y, instrument says Y' on a scored row). What distinguishes the instrument
from the recipe reader is therefore Q3 (label edits refused or invariant) and the replay-equality itself -- not Q1.
b3 (b1 plus ENV when the engine's donor_mixed_births exceed half of births_endo) does NOT recover ENV on RECON (donor
mixing is ~7.6 % of births: ancestry sets merge within a few epochs) -- my sub-prediction missed; b3 says ENV on CDIST
8/8 at 5 and 10 epochs because reads_nbr fires there. Repair / narrowing: state that Q4 is vacuous on ENV and that the
arm set is recipe-separable; if a baseline control is wanted that can fail, give it an ENV output (e.g. the engine's
donor predicate per organism) and match b2's horizon.

Q1 and the horizons. I predicted the constructed truth would drift (RECON INS at 20, MIXED at 40; H_ENDO_GATED at 200
partly taken over). It did not: RECON is ENV 18/18 at 20 / 40 / 60 epochs with n_INS = 0 everywhere (the founders are
OVERWRITTEN within the first epochs under ENDOGENOUS_COPY -- ~128 births per epoch over random cells -- not dead by
max_age, which is what I had assumed), and H_ENDO_GATED is ENDO 12/12 at 200 epochs (n_ENV 0..4 of ~120; dev saw 2/16
kin-dependent takeovers, I saw 0/12). This is evidence for the builder's horizons, recorded against my prediction.

E3 (REFUSED leaves the Q1 denominator) survives the suite: the preregistered 'REFUSED included' is a sentence, not a
pinned behaviour. Immaterial as long as the frozen analysis.py runs the confirmatory analysis (FROZEN.json pins it).

### 4.3 Interpretation: what ATTRIBUTION_QUALIFIED would license (narrowing text, s5.1)

- ENDO: the function-carrying bytes were written by the parent's execution with values and mask invariant under the two
  registered pre-window alterations. It includes writes that depend on the world's INPUT (W5f: the input writer's
  child is P-tagged and, with input 21, a functional ENDO organism) and target-dependent writes that are affine
  invariants (s4.1). 'Environment' in ENV means the target cell's prior content, nothing else.
- ENV: the function needs bytes the parent left unwritten or wrote with target-dependent values detectable by the two
  alterations, or exists only with the live neighbour (situ). One population-scale construction (RECON, kept bytes).
- ENDO over ENV precedence is sufficiency, not expression: PD shows an organism whose scored output comes from kept
  bytes and whose parent-written copy behind them is credited (the registered rule, PREREG s4.4; recorded, not a fault).
- Origin INSERTED = 'a supplied founder was functional'; it is not a statement about the lineage of the final
  population. ARISEN is not tested by Q2 (s4.2).
- The 8-probe-case bar is per RUN: one seed in 999 (17_049_230) makes every HALF organism 'functional' (75 of 128 in a
  one-epoch planted run; the other seed had 1 functional organism, an EXT child that mutated into a full echo in one
  epoch). Registered arms carry no half-solvers; an evolved one would be judged by its run's eight cases, correlated
  across the population.
- The zero filler of the sufficiency restriction is a choice (E2 survives; W2 flips ENDO -> ENV where a kept byte is a
  jump operand); s11.6 should say 'filler-dependent', not only 'zero = NOP'.
- ATTRIBUTION_QUALIFIED = the frozen rule agrees with construction on ten recipe-separable arms at their registered
  horizons (Q1), label edits cannot move it and byte / physics / generation edits are refused (Q3), it is replay-
  dependent and engine-pinned, and its separation from two label readers rests on an output class those readers lack
  (Q4) and on a horizon (b2 / EXT). It does not license 'independent of the target' for ENDO, 'ARISEN detectable' for
  origin, or 'better than the recipe' for these arms.

### 4.4 Edits: what the frozen suite does not pin

    E1 one counterfactual sample      SURVIVES 42/42   W1 XOR writer: byte 0 K (frozen) -> P (E1)
    E2 filler 0x1E                    SURVIVES 42/42   W2 JR-operand tape: ENDO -> ENV
    E3 REFUSED leaves the denominator SURVIVES 42/42   W3 5 unforged refused ENV rows: NOT_QUALIFIED -> ATTRIBUTION_QUALIFIED
    E4 control (RED_EDITS S6)         RED              test_run_class_is_a_strict_majority only (harness valid)
    E5 counterfactual empties input   SURVIVES 42/42   W5 input writer: byte 0 P -> K
The hash guard (`freeze check`) named the mutated file on every mutant and printed OK after every restore; it protects
the run, it pins no behaviour (C-016 lesson 3 holds here too). E1 and E5 are not defects of the frozen rule; they show
that the second sample and the kept input are each load-bearing and unpinned: a repair that touches counterfactual()
needs tests for both. E2 and E3 are unpinned registered sentences.

## 5. Recommendations for the one bounded repair round (owner's, not mine)

1. P tag: add `reads_nbr > 0 on res0 -> K for every written byte` (or the owner's equivalent), keep the counterfactual,
   and pin it with the CDIST unit answer (kin: head K) plus a short-horizon CDIST arm or test; re-check the 4/21
   exec_foreign cases of ONBOARDING s3.2 stay P. Expected effect on the registered arms: none (H, seeded, RECON and NH
   never read the window).
2. PREREGISTRATION text: s4.2 and s11.5 (P = invariant under the registered alterations; CDIST constructed); s5 Q2 ('does
   not test ARISEN; expected ~3 ARISEN rows'); s5 Q4 ('b1 / b2 cannot emit ENV; b2's EXT failure is the 10-epoch horizon;
   the arm set is recipe-separable'); s11.6 ('filler-dependent'); s8 (blinding hides the arm name, not the recipe).
3. Tests: pin the second counterfactual sample (W1), the input (W5), the filler (W2) and 'REFUSED counts as wrong' (W3)
   if those are intended.
4. Nothing blocks the confirmatory run on v1.0.0; if the repair round runs first, the re-check is small (the four unit
   witnesses + one short CDIST arm + the suite).

## 6. Escapes, misses and tooling

6.1 Two harness errors of mine, both fixed in 5daa7745f after the first two shards were seen: (a) a float timing field
    in the rows (receipt-canonical refuses floats; the rows had been written, only the digest print crashed); (b) the
    'extra transplant tape beyond N' audit edit -- the registered arms plant 13 of 128 cells, so an appended 14th tape is
    PLACED at cell 13 and the instrument correctly REFUSED those records (20 of 30 in the first shards). It is now its
    own check (`extratape`): placed -> REPLAY_MISMATCH for the 13-tape arms, beyond N -> same for the 128-tape arm, as
    predicted in the amendment. The first-harness rows were discarded and every job re-run; the judge's eval namespace
    lacked `set` for the amended S3 check and was given it (one token) after the first score.
6.2 B1's registered horizon (100 epochs) was my design error (s4.1); B1h is post-hoc and labelled; the unit fault is
    the committed, first-sight evidence.
6.3 B5: my mechanism for founder persistence was wrong (overwritten, not aged out). B6: the donor-majority rule was
    wrong. PL: 'other = 0' missed by one mutant organism. All reported with their values.
6.4 Scratch: C:/Prometheus-worktrees/pallas-scratch/{vmcheck.py, t040/} (DEV_ROWS shard, red_rows; not committed).
6.5 Tooling lessons: a row digest must be int/str-only from the first draft (reuse assay.row's discipline); check
    `len(tapes) < N` before calling anything 'beyond N'; a judge that evals committed check strings needs the full set
    of builtins the checks use; two 600 s foreground shards of ~30 jobs each fit the headless limit with margin.

## 7. Files

rso/z80/challenge/: CHALLENGE_SET.md, EXPOSURE.md, expected.json (answer key; B1h post-hoc key marked), edits.json,
subjects_c.py, cases.py, witnesses.py, run_edits.py, rows.{0,1,2,3}-4.jsonl.gz (132 rows; sorted rows sha256
fb7721da4edb637d36c65cee073b6da078c17c59d43ff5e6e9d62c48df3026c0), results.jsonl (20 cases, observed + verdict),
red_rows.jsonl (baseline, 4 witness baselines, E1-E5), this REPORT.md. Receipt: ops/campaigns/C-017/tasks/C-017-T040/
attempts/A-001/RECEIPT.json. Journal: roles/Pallas/journal/2026-10-11.md. Registry (Palamedes's): candidate entry
z80-replay-writer-attribution (ONBOARDING s5) should carry `counterexamples` += CDIST (affine-invariant target
dependence passes the P tag) and `not_qualified_for` += 'ARISEN origin (Q2 unpowered by construction)'.
