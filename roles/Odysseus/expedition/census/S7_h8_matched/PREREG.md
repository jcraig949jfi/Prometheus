S7_h8_matched -- PREREGISTRATION (EXPLORATORY spike; written before any experimental run)
=========================================================================================

Written: 2026-09-28, worktree /home/jcraig/Prometheus-worktrees/odysseus-base-role,
HEAD 02800d2b59fa7e27bf8bd84bb79ae1523bd6f10f (branch odysseus/expedition-1-2026-09-28).
Status: EXPLORATORY. Never edited after writing; amendments go in AMENDMENTS.md.

0. Source of the rule
---------------------
roles/Odysseus/expedition/census/CENSUS_B_other.md (untracked; sha256
ed026b1da21f64541e5c25495a181c9e8672d7f823402107c4de25e6977d6ec7), section 4 check 1, lines 312-318,
verbatim:

  "1. H8 matched-compute recompute arm (minutes). Rerun C3-SFE-04's baseline arm on W1_d8 and W1_d16 at
   G=200 (>= the ladder's max 197 generations), N=200, E=16, 12 seeds each; SFE-04's 66 runs x G100 took
   881 s, so ~24 runs x G200 is ~10 CPU-min. Also probe the one pristine d16 reader (SFE-04 baseline seed
   2) on d0/1/2/4/8 (0.3 s direct probe). Decides Q8: >= 3/12 pristine d8 readers => H8 FAILS(Q8) (the
   ladder is speed); <= 1/12 => H8 SURVIVES at matched compute. Add, in the same session, the never-run
   population-level probe (C4-2 / H-D4-14): evaluate the W0-hold populations' members on d8/d16 before
   the first delay-1 battery (selection vs construction, Q5)."

Decision rule (primary, on W1_d8 pristine readers out of 12 at G=200):
  >= 3/12 => H8 FAILS(Q8) (the ladder is speed)
  <= 1/12 => H8 SURVIVES at matched compute
     2/12 => UNDECIDED
W1_d16 count is reported alongside (secondary; the rule is stated on d8).

1. Harness (unchanged engine; files @ commit / blob)
----------------------------------------------------
- archaeon/campaign3/c3_sfe04.py @b50f75b7c (blob 6296222c537c): run_target() baseline arm, lines 90-113.
- archaeon/wse/evolve.py @b50f75b7c; archaeon/wse/worlds.py @f6e18b5c7; archaeon/campaign2/c2base.py
  @6592f9d66 (FOUNDRY_C2); archaeon/campaign3/c3base.py @6592f9d66 (CAMPAIGN_SEED 20260920).
- Historical run of record: C3-SFE-04 a03 committed at e74b2f7aa (rows.json blob 1344eac3fafb).
  `git diff e74b2f7aa HEAD` over archaeon/wse/, c3_sfe04.py, c2base.py, c3base.py, ladder.py touches
  only archaeon/wse/states.py (typed-state bookkeeping, not on the search path).
- Ladder of record: C3-SFE-03, archaeon/campaign3/ladder.py @fe3c1647c, rows.json @fe3c1647c
  (blob 7b946ea38de7): gens_run 159,131,174,151,197,112,122,181,114,112,114,135 (max 197).

The rerun will call c3_sfe04.run_target() directly (imported from git, no copy) with
job = {"arm":"baseline","spec":<W1_d8|W1_d16 knobs>,"seed":s,"N":200,"E":16,"G":200,"manifests":None}.
It does NOT go through Experiment3 (no ledger / engine / reachability writes).

2. Held-out criterion (the SAME one the historical runs used)
-------------------------------------------------------------
c3_sfe04.py:49   HELDOUT_N = 48
c3_sfe04.py:50   DIRECT_SOLVED = 0.9            # an edge with direct competence >= this needs no search
c3_sfe04.py:98   ho = episodes_for(spec, CAMPAIGN_SEED, "heldout", seed, HELDOUT_N)
c3_sfe04.py:104  e = evaluate(res["elite"]["manifest"], ho, rng_seed=7)
c3_sfe04.py:106  "competence_heldout": round(e["reward"], 4)
The ladder elites' d8/d16 "reads at held-out 1.0" is direct_probe (c3_sfe04.py:81-86: same 48 held-out
episodes family, rng_seed=7) counted as "solved" iff >= DIRECT_SOLVED (0.9).
READER (primary) := final-elite competence_heldout >= 0.9 on the target (48 held-out episodes, rng_seed 7).
Also reported (not decisive): foothold (c3_sfe04.py:109, first_solved_gen: elite training reward >= 0.5,
evolve.py:285), level, first_summit_gen, and the first generation whose training best >= 0.9.

3. Seeds
--------
Historical baseline seeds were 1..6 (and harvest used 9000+seed; C3-SFE-03 used 1..12).
New seeds (disjoint): 1001, 1002, ..., 1012 for BOTH W1_d8 and W1_d16 (24 runs, G=200, N=200, E=16).

4. Compute feasibility gate (declared up front)
-----------------------------------------------
Budget given: <= 25 CPU-minutes total, <= 2 processes. A pre-run smoke (NOT an experimental run;
disclosed here) replayed the historical W1_d16 baseline seed 2 for 8 generations to check determinism
and cost: trace_best [0,0,.125,.125,.125,.25,0,.125] == rows.json trace_best[:8] (exact match), cost
48.1 CPU-s for 8 generations (~6 CPU-s/generation incl. import) on this laptop under load avg ~38.
Primary arm = 24 x 200 = 4800 generations ~= 480 CPU-min at the measured rate (~20x over budget; even
at the historical machine's ~1.1 wall-s/generation it would be ~88 CPU-min). The census estimate
"~10 CPU-min" divided pooled wall time by run count and ignored the 12-process pool.
GATE: the primary arm is run only if its projected cost fits the remaining budget. At the measured rate
it does NOT. Pre-declared consequence: primary arm NOT RUN; verdict under the rule = NOT EVALUATED
(H8 stays "SURVIVES (provisional)" with the Q8 compute gap open); RESULT.md gives the exact command
and cost to run it elsewhere. No reduced-G or reduced-seed substitute will be read against the rule.

5. Secondary probes that fit the budget
---------------------------------------
5a. Seed-2 probe. The historical pristine d16 reader's manifest is not stored in rows.json. Replay the
    SFE-04 baseline W1_d16 seed 2 search deterministically (same Evolution args as run_target) and, from
    generation 52 (historical first foothold) through at most generation 70, test the elite each generation
    on W1_d16 held-out (seed 2, 48 eps, rng 7); take the FIRST elite with held-out >= 0.9. Probe it on
    W0, W1_d1, W1_d2, W1_d4, W1_d8 (and W1_d16) with (i) episodes_for(spec, CAMPAIGN_SEED, "heldout", 2, 48)
    and (ii) the direct_probe set used for the ladder elites (seed 1). Report per-delay held-out.
    Reading: >= 0.9 on all of d0/1/2/4/8 => the pristine d16 reader is itself delay-invariant (the
    ladder's object is reachable by pristine search); failing on the short delays => a d16-specific
    solution, not the same object. Caveat: generation <=70 elite, not the gen-99 elite of record.
5b. Population probe (C4-2 / H-D4-14), optional, on the three cheapest C3-SFE-03 seeds by hold length:
    seeds 6 (hold 12), 9 (hold 14), 11 (hold 14) (all three became delay-general). Replay the ladder's
    rung-0 hold exactly (ladder.run_ladder's loop: ev.spec=W0, battery(g, seed, 0, p=0.1, E) episodes),
    verify schedule best/mean against rows.json, and take the population entering generation ladder_start
    (i.e. after the reproduce() that follows the hold-release generation, before the first delay-1
    battery). Evaluate every member (N=200) on W1_d8 and W1_d16 held-out (seed = ladder seed, 48 eps,
    rng 7). Report count of members >= 0.9 on d8, on d16, and on both, plus max.
    Reading: any member >= 0.9 on d8 and d16 => the capacity pre-exists in the W0 population (selection);
    zero members => it appears during the ladder (construction) for that seed. n=3 seeds, descriptive only.
Processes: at most 2 concurrent. Stop any job that would push the total past 25 CPU-min.
