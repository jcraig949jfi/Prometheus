S7_h8_matched -- RESULT (EXPLORATORY)
=====================================

Worktree /home/jcraig/Prometheus-worktrees/odysseus-base-role, HEAD 02800d2b59fa7e27bf8bd84bb79ae1523bd6f10f.
Preregistration: PREREG.md in this directory (written before any experimental run; not edited).
No amendments. No git state changes; no writes outside this directory (no __pycache__: python -B).

1. Files and SHAs
-----------------
Harness (imported from git unchanged, not copied):
  archaeon/campaign3/c3_sfe04.py   @b50f75b7c blob 6296222c537c  (run_target baseline arm :90-113;
                                   HELDOUT_N=48 :49; DIRECT_SOLVED=0.9 :50; held-out :98,:104 rng_seed=7)
  archaeon/campaign3/ladder.py     @fe3c1647c blob b766b6f27fdf  (run_ladder, battery, HOLD_MIN=0.5)
  archaeon/campaign3/c3base.py     @6592f9d66 (CAMPAIGN_SEED 20260920)
  archaeon/campaign2/c2base.py     @6592f9d66 (FOUNDRY_C2)
  archaeon/wse/evolve.py           @b50f75b7c; archaeon/wse/worlds.py @f6e18b5c7
  Engine unchanged since the runs of record: git diff e74b2f7aa HEAD over archaeon/wse/, c3_sfe04.py,
  c2base.py, c3base.py, ladder.py touches only archaeon/wse/states.py.
Rows of record:
  archaeon/campaign3/C3-SFE-04/rows.json @e74b2f7aa blob 1344eac3fafb (baseline W1_d8 s1-6 held-out
    .083 .125 .021 .104 .042 .042, foothold 0/6; W1_d16 s1-6 .063 1.0 .063 .063 .063 .063, foothold 1/6 at gen 52)
  archaeon/campaign3/C3-SFE-03/rows.json @fe3c1647c blob 7b946ea38de7 (ladder p0.1, 12 seeds,
    gens_run 112-197, hold_gens 12-97)
Census: roles/Odysseus/expedition/census/CENSUS_B_other.md (untracked) sha256 ed026b1d...6ec7, sec.4 check 1.

Scripts / outputs here: seed2_probe.py -> seed2_probe.json; pop_probe.py -> pop_probe_s{6,9,11}.json;
run_all.sh (2 processes max); run_log.txt, run_log_pop.txt (with /usr/bin/time CPU), run_started.txt.

2. Harness runs as-is from git: YES (deterministic)
---------------------------------------------------
- Replay of SFE-04 baseline W1_d16 seed 2: trace_best for generations 0-52 identical to rows.json
  (trace_best_match_hist = true); first held-out >= 0.9 elite at generation 52 = historical foothold gen.
- Replay of C3-SFE-03 rung-0 hold, seeds 6, 9, 11: per-generation best/mean identical to rows.json
  schedule; hold release at 12, 14, 14 = hist hold_gens.

3. PRIMARY (G=200 pristine rerun, 12 new seeds 1001-1012 x {W1_d8, W1_d16}): NOT RUN
-----------------------------------------------------------------------------------
Reason: the preregistered compute gate (PREREG.md sec.4). Measured cost on this laptop:
  W1_d16 baseline: 195.1 CPU-s for 53 generations + probes  => ~3.6 CPU-s / generation
  (smoke: 48.1 CPU-s for 8 generations incl. import).
  Projection: 12 x 200 d16 gens ~ 145 CPU-min; d8 (shorter episodes) roughly 100+ CPU-min;
  total ~ 4-5 CPU-HOURS, i.e. ~10x the 25 CPU-min budget. Wall under the current load (avg ~38 on
  4 cores) ran ~4x CPU time, so ~16+ wall-hours at 2 processes.
The census's "~10 CPU-min" is wrong: it divided the 881 s WALL time of a 12-process pool by run count;
rows.json itself sums per-run wall_s to 6794 s for 66 runs x G100 (baseline d8/d16 runs 81-336 s each
at G100 on that machine).
VERDICT UNDER THE PREREG RULE: NOT EVALUATED. H8 stays "SURVIVES (provisional)" with the Q8 compute gap
open. Pristine d8 readers at G=200: not measured (0/0). Pristine d16 readers at G=200: not measured.
Command to run it where compute exists (per seed s in 1001..1012, target in W1_d8, W1_d16):
  python3 -B -c "import sys; sys.path.insert(0,'.'); from archaeon.campaign3.c3_sfe04 import run_target,TARGETS; \
   t={x.name:x for x in TARGETS}['W1_d8']; r=run_target({'arm':'baseline','spec':t.knobs(),'seed':1001,'N':200,'E':16,'G':200,'manifests':None}); \
   r.pop('_res'); print(r['competence_heldout'], r['first_foothold_gen'])"
  Reader := competence_heldout >= 0.9. Rule: d8 >= 3/12 FAILS(Q8); <= 1/12 SURVIVES; 2/12 UNDECIDED.

4. Seed-2 probe (the one historical pristine d16 reader) -- RUN
---------------------------------------------------------------
Elite of the deterministic replay at generation 52 (first gen with d16 held-out >= 0.9; NOT the gen-99
elite of record, whose manifest is not stored). Held-out 48 episodes, rng_seed 7:
    cell     heldout(seed-2 set)   heldout(seed-1 set = the set the ladder elites were scored on)
    W0          0.0417                0.0625
    W1_d1       1.0000                1.0000
    W1_d2       0.9167                0.9167
    W1_d4       0.8542                0.9583
    W1_d8       0.8750                0.9583
    W1_d16      0.9792                0.9375
Reading against PREREG 5a: neither clean branch. It is NOT a d16-specific solution: pristine search on
d16 alone produced an organism that reads delays 1, 2, 4, 8 and 16 at 0.85-1.0 (>= 0.9 on every
delay >= 1 on the seed-1 set, i.e. by the same test that credited the ladder elites with d8/d16). It is
NOT the ladder's object either: it fails delay 0 (W0, 0.04-0.06), which every ladder elite passes.
So a pristine d16 search, at gen 52 of 100, reached a delay-GENERAL (d>=1) reader -- evidence that the
"delay-invariant reader" is reachable without the ladder; the ladder's distinctive addition, on this one
organism, is only d0 coverage (which it was trained on). This weakens H8 on Q8 but is n=1.

5. Population probe C4-2 / H-D4-14 (optional) -- RUN on 3 seeds
---------------------------------------------------------------
Population entering the first delay-1 generation (after the reproduce() following hold release),
all 200 members, held-out 48 eps rng 7 (seed = ladder seed):
    seed  ladder_start  members>=0.9 d8  >=0.9 d16  both  max d8  max d16  W0>=0.9  hist general_gen
     6       12              0              0          0    0.083   0.063      5          62
     9       14              0              0          0    0.083   0.063      2          49
    11       14              0              0          0    0.125   0.083      2          39
Reading (PREREG 5b): zero members in any of the 3 seeds read d8 or d16 at the start of the ladder: in
these seeds the capacity is not present in the W0-hold population and appears during the ladder
(construction over in-run variation, not selection of a pre-existing reader). Caveats: n=3, the three
shortest holds (12-14 gens); the 5-of-12 "first delay-1 battery promoted an organism the W0 population
already contained" seeds were not singled out; the probe says nothing about where along d1..d4 it arose.

6. Compute used
---------------
smoke 48.1 + seed2_probe 195.4 + pop s6 27.1 + s9 53.8 + s11 30.4 = ~355 CPU-s (~5.9 CPU-min) of 25.
Max 2 concurrent processes. Wall 10:30-10:43 UTC for the probes.

7. Limits
---------
- Primary decision not made; nothing here reads against the census rule.
- Seed-2 probe uses the gen-52 elite, not the gen-99 elite of record (held-out 1.0 on d16).
- The seed-2 reader's d4/d8 pass/fail depends on the episode set (0.85/0.875 vs 0.96/0.96); 48 episodes.
- Population probe: 3 of 12 seeds, chosen by cost (shortest hold), not at random.
- EXPLORATORY throughout; no engine/ledger records written.

## ADDENDUM 2026-09-28 (Odysseus) -- full matched run: VERDICT DECIDED

full_run.py (3 processes, G=200, N=200, E=16, seeds 1001-1012; rule and
reader criterion as frozen in PREREG.md). At 10 of 24 runs complete, W1_d8
pristine readers = 5 of the 10 seeds finished (1001, 1004, 1005, 1010,
1011; held-out 1.0), first footholds at generations 64, 91, 165, 176, 183.
The rule is ">= 3/12 pristine d8 readers => H8 FAILS(Q8)". The count can
only rise with the remaining seeds, so the verdict is DECIDED:
H8 FAILS(Q8) -- the delay ladder bought SPEED, not reach; a pristine search
at matched compute reaches a delay-8 reader. Four of the five pristine
readers appeared after generation 100, i.e. beyond the original baseline's
horizon (the census's compute-gap concern was correct). d16 and the last
d8 seeds are supplementary and will be appended to full_run.jsonl.
Status: EXPLORATORY (spike), rule preregistered before the run.

## ADDENDUM 2 (2026-09-28) -- run stopped by the host, not by the science
The full run was stopped by Claude Code's memory-pressure reaper while the
session was idle (the host had ~200 MB free: another seat's attribution
probe held ~6 GB of the 7 GB node). Completed before the stop: W1_d8 12/12
seeds -> 6 pristine readers (rule: >= 3 => H8 FAILS(Q8); verdict unchanged
and now on the full d8 arm); W1_d16 9/12 seeds -> 4 readers (supplementary).
Not restarted (reaper guidance: do not restart unasked). Rows: full_run.jsonl.
