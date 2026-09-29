# W-M LOG (T-INS-6)

A0 03:25Z  Read COMMON_RULES*.md, lens.py, envs.py, plants.py (parts), engine
    checkpoint API, W-I traj.py/identity_check.py/main.py, W-I out/identity_check.json,
    traj_table.csv, traj_<JOINT cells>.json (phi), designed_echoes PLAN/design.py/
    run.log/instruments.json. Context contamination: traj_table.csv letter
    columns are W-I's labels. Not read: W-I REPORT/LOG/PLAN, designed_echoes/
    RESULT.md, research/*.md syntheses.
A1 03:40Z  PLAN.md frozen (algebra, decision rule, KA1-KA7, P1-P4).
A2 03:41Z  lens_ins6.py written (Arm/run_arms EVERY+SINGLE with early stop,
    selfcheck, pair_trial_table/census/classify, mixture_scan, twin_profile).
A3 03:42Z  smoke.py (timing/plumbing, c1b echo physics, HOLD gap 8, 32 worlds,
    trials 1..11, n_boot 200): selfcheck all 5 arms bit-identical to lens.run.
    latch: o=-1,0 IDENTITY-BROKEN (swap before the 2nd cue tick; the cue then
    rewrites both partners: identity 0), o=1..9 SITE fS=1, identity 1.
    echo: o=-1 IDENTITY-BROKEN, o=0..9 CHANNEL fC=1. null: UNDEFINED everywhere
    (normal 0.5, no eligible pair-trials). ~22-42 s per plant.
A4 03:43Z  Fabric lease: `python -m fabric lease acquire skullport:cpu8 --as Ananke`
    -> lse-10ae2cf693e4 (token held), expires 04:43Z. (First call without
    --as refused: "say who you are".)
A5 03:43Z  apply.py launched as 4 background procs x 2 threads (logs/apply_*.log):
    [E2 E1] [78f3b0ec 2dccdaa5] [369f5a5b c16d5231] [4781b0a1 8c37f32e e06701a5].
    Offsets -1..ro_off-1, trials 1..n-1 for BOTH modes (all trials; no subset
    needed at this cost), n_boot 2000, seeds 0x5EE (cells) / 0x5F1 (E1, E2).
    Note: the application was launched before test_lens_ins6.py was written
    (plumbing already checked in A3); the KA tests are written in parallel and
    any KA failure is reported, not repaired post hoc.
A6 03:45-03:50Z  First application pass, EVERY mode only (killed before SINGLE):
    369f5a5b EVERY IDENTITY-BROKEN at all 17 offsets (P2 as predicted);
    4781b0a1 EVERY IDENTITY-BROKEN at o=-1..5,7, NEITHER o6, UNRESOLVED 8-11,14,15,
    CHANNEL 12,13; E2 EVERY CHANNEL o0-2,4-6, MIXTURE o3,o7, SITE o8-12;
    78f3b0ec UNDEFINED at every offset. Diagnosis: 78f3b0ec is a one-sided
    abstainer (normal: 0 pair-trials with BOTH partners correct; A 115, B 142
    correct, 511 of 768 world-trials are ties S0=0). The frozen census requires
    both partners correct, so it cannot see this specimen.
    DEVIATION D1 (after seeing this result): added a SECONDARY "follow" census
    (lens_ins6.census_follow): eligible iff the partners' normal readout SIGNS
    differ (incl. 0); an arm follows its partner iff its readout sign equals
    the partner's normal sign. Same classify() thresholds. It reduces to the
    frozen census when both partners are correct (tested). The FROZEN census
    stays primary; follow-census classes are reported separately and marked.
    Also: apply.py now saves raw arrays (out/raw_<spec>_<mode>.npz).
    Killed the 4 procs; relaunched 03:51Z with the same groups.
A7 03:56Z  BUG in D1 code found on E2 EVERY output: census_follow's identity used
    RAW S0 equality while census() uses outcome (sign) identity, so follow read
    IDENTITY-BROKEN at E2 o0-3, 12 where frozen read CHANNEL. In HOLD, mirror-
    signed distractors arrive after the swap, so the two copies of a chimera
    differ in S0 magnitude but not sign. Fixed: follow identity = sign-level;
    raw equality kept as identity_s0. The running procs use the old code, so
    the follow census is RECOMPUTED from out/raw_*.npz in summarize.py (no
    rerun). Frozen census unaffected.
A8 04:07Z  Lease renewed (ttl 5400 s). Added twin_profile test (bit-equal to W-I
    traj.twin_profile on the echo plant; latch vs echo separation) - passes.
A9 04:19Z  E2 done (EVERY 219 s, SINGLE 1448 s). KA7 PASSES in both modes:
    channel-dominant o0-2,4-6, SITE run from o8 (lag -5) to o12, handoff rule
    a,b,c,d all true. MIXTURE at o3 (fS .42 fC .51, phi -0.88 [-0.94,-0.80])
    and o7 (fS .48 fC .50, phi -0.98 [-1.00,-0.95]). o7 = lag -6, where
    designed_echoes/instruments.json had site_all CHANCE + channel_all CHANCE:
    the census resolves that "both at chance" as a per-trial S/C mixture (echo
    return time jitters by trial), not NEITHER. o3: the relay neighbour's
    inbox (a SITE array) vs the in-flight packet, the same kind of split one
    stage earlier. SINGLE == EVERY class at every E2 offset. Identity (outcome)
    0.95-1.00 at o>=0 even though HOLD distractors arrive after the swap.
A10 04:30Z  369f5a5b, 4781b0a1, 78f3b0ec, E1 done (SINGLE ~1830 s each for the
    delta-16 cells). E1 EVERY/SINGLE computed (KA7 must-fail input, see summary).
    04:34Z  e06701a5 launched solo (logs/apply_e06701a5_solo.log) to finish
    sooner; the group-3 proc (pid 33223) is killed by PID once
    census_8c37f32e.json exists, so it never runs e06701a5 twice.
A11 04:40-04:44Z  2dccdaa5, c16d5231, 8c37f32e, e06701a5 done (group-3 proc killed
    by PID after 8c37f32e; e06701a5 ran once, solo, with the fixed code).
    pytest: `python -m pytest roles/Ananke/research/workers/W-M/test_lens_ins6.py -q`
    -> 20 passed in 227.81 s, RC=0 (logs/pytest.log).
    Lease lse-10ae2cf693e4 RELEASED 04:44Z (fabric status no longer lists it).
    NOTE: the 'follow' blocks inside out/census_<spec>.json for the 8 specs
    launched at 03:51Z carry the pre-A7 raw-identity bug; out/summary.json and
    out/summary.txt hold the recomputed (fixed) follow census and supersede them.
    Contamination note on KA7: the frozen KA7 windows were written after
    reading designed_echoes/instruments.json (E2 site FLIP at lags -4..-1,
    CHANCE at -6; E1 channel FLIP at -4, -3), so KA7 (b) and the E1 must-fail
    were partly known in advance; (a), (d) and the MIXTURE at lag -6 were not.
A12 Outcome vs predictions: P1 HELD (SINGLE identity 1.00 at every o >= 1 in all
    7 cells; o = 0 broken as expected). P2 WRONG (EVERY identity also broke in
    c16d5231 .87, 8c37f32e .52-.79, 4781b0a1 .72-.94 at o<=7, e06701a5 follow
    .72-.89; only 2dccdaa5 and 78f3b0ec stayed 1.00). P3 WRONG (W-I 'M'
    offsets resolve as MIXTURE or UNRESOLVED, never NEITHER). P4 PARTLY: where
    both modes are informative the classes agree 100%, but most EVERY offsets
    of 5/7 cells are identity-broken, so the disagreement is not confined to
    369f5a5b.
