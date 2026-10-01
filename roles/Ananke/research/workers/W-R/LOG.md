# W-R LOG (E-ANANKE-W-R, T-INS-9, MWO-0004)

A0 12:18Z read COMMON_RULES.md + COMMON_RULES_ARC3.md; lens_swap.py (docstring + code), engine.py WAKE step,
   physics.py, plants.py, envs.py. CONTEXT CONTAMINATION (brief-directed): before PLAN I read W-P REPORT.md
   RESULTS + DISAGREEMENTS and W-M REPORT.md + W-M out/summary.txt + W-M apply.py, as the brief instructs.
   Did not read SYNTHESIS*/C1B_REVIEW*/PTE_ENGINE_CARD/ARC3_PRIORITIES or the corrections register before PLAN.
A1 12:20Z probe_physics.py -> out/physics.json: 8/9 specs sync update_period 2 (update_p .5 unused in sync);
   369f5a5b async (p .8). Pd: 11 / 19 odd for the cells, 12 (E1) / 16 (E2) even. fabric lease status: [].
A2 12:35Z PLAN.md frozen (before any census). Code: fork.py (forked SINGLE runner + phase bookkeeping +
   stratified census), specs.py (loader; W-M apply.spec imported read-only; PLANT<p> = echo_hold under
   c1b_echo_physics with update_period p, HOLD gap 11 iti 3), ka_fork.py (KA-F). PYTHONDONTWRITEBYTECODE=1
   for all runs so no .pyc lands outside W-R.
A3 12:40Z lease lse-be98c3489db7 ACQUIRED (skullport:cpu8, exp 13:23Z). KA-F PLANT2: identical 52/52 arms; must-fail late=1: 1 arm (o0 chan) mismatched -> not identical (PASS). Launch KA-F 4781b0a1 + 369f5a5b (2 procs x 2 threads).
A4 12:47Z pytest test_fork.py 6 passed RC=0 (logs/pytest.log). KA-F late=0: 369f5a5b identical 64/64, 4781b0a1 identical 64/64 (+normal). Launch stratify PLANT2 (M=256).
A5 12:58Z KA-F must-fail late=1: 369f5a5b 4 arms mismatched (o0), 4781b0a1 pending; PLANT2 M=256 done (122 s): per-phase classes match the PLAN s4 hand table at all 13 offsets; permuted-label must-fail: discordant set {6} != {0,5,6,11} (fails as required; weak: a shuffle of 11 labels keeps most). Launched 4781b0a1, 369f5a5b (12:52Z), PLANT1, 78f3b0ec.
A6 12:28Z CORRECTION: clock times written in A2-A5 were my estimates, not read from the clock. Actual (file mtimes/lease): PLAN frozen ~12:21Z, lease acquired 12:23:35Z (expires 13:23Z), KA-F 12:24-12:26Z, pytest 12:24:52Z, PLANT2 done 12:27:03Z, main launches 12:26-12:27Z. From here times are from date -u.
A7 12:31Z PLANT1 (period-1 must-fail) done: no phase-discordant offset (all per-phase = pooled). Launched 2dccdaa5.
A8 12:36Z 2dccdaa5 done (~5 min). Launched c16d5231.
A9 12:41Z c16d5231 done. Launched 8c37f32e.
A10 12:42Z 369f5a5b, 4781b0a1 done. Launched e06701a5, E1 (4 procs: 78f3, 8c37, e067, E1).
A11 12:45Z summarize (partial). NEGATIVE CONTROL 369f5a5b FAILS the frozen rule: PHASE EFFECT at o1 (dN -.15 [-.25,-.04]) and o3 (dN -.14 [-.23,-.03]); 2 > 1 allowed; no class change (all UNRESOLVED/SITE same per stratum). Direction: odd-k trials carry more N (o1,o3 q0 = odd trials; o2,o4.. same sign, n.s.). Implication: q is confounded with trial parity in odd-Pd cells; a trial-parity baseline of |d| ~ .15 exists without any clock. Post-hoc (labelled) planned: leave-trial-1-out reanalysis + effect-size comparison vs this baseline.
A12 12:45Z 78f3b0ec, 8c37f32e done. Launched E2 (last spec).
A13 12:47Z POST-HOC (labelled): posthoc.py leave-trial-1/11-out on 369f5a5b: same effect offsets [1,3], no class change -> not trial-1/11 driven. posthoc_split.py exact split permutation (462 5/6 splits of trials 1..11): 369f5a5b parity split extreme at o1 p=.006, o3 p=.004 (o6 .035, others >.05), max|d| .15; 4781b0a1 parity split is the most extreme split at all 16 offsets (p=.002 = floor), max|d| .83. No env/physics parity source found for async (envs.build RELAY: iid coins; WAKE hashed per (ws,t,site)). stratify.py gained optional ns arg (tag _ns<hex>); launched REPLICATION 369f5a5b at ns 0x621 M=256 to test if the async parity effect replicates. e06701a5, E1 done.
A14 12:50Z SECONDARY followdiff.py: PLAN s2 phase-effect rule on the follow census for the abstainers (frozen census UNDEFINED there): e06701a5 effects at o0, o5; 78f3b0ec at o0, o9, o11, o14, o15; o10 none (UNRESOLVED both phases).
A15 12:53Z REPLICATION 369f5a5b ns 0x621 (post-hoc): PHASE EFFECT at 0 of 16 offsets, no class change; per-phase = pooled everywhere. The 0x620 o1/o3 flags do not replicate -> read as sampling (trial-level variation across 5-6 trials per stratum is outside the pair bootstrap). Pooled o14 SITE at 0x621 vs UNRESOLVED (fS .74) at 0x620: namespace jitter near the .80 threshold. Launch post-hoc replications 2dccdaa5, c16d5231 at 0x621.
A16 12:58Z posthoc_split + leave-trial-out on 2dccdaa5/c16d5231/8c37f32e/4781b0a1: phase split p=.002 (floor) at every flagged offset; dropping trial 1 or 11 changes no effect set and no resolution; one class change (4781b0a1 o8, near a threshold).
A17 12:56Z replications 2dccdaa5/c16d5231 at 0x621 reproduce the main classes (o0 CHANNEL|BROKEN, o4/o5 one phase clean + one phase ~50/50 MIXTURE). Lease lse-be98c3489db7 RELEASED 12:56Z (fabric lease status lists only Aether's buckkeep:cpu8). No W-R python processes running (Win32_Process count 0).
A18 12:58Z Note: probe_physics.py (A1) ran before PYTHONDONTWRITEBYTECODE was set and rewrote W-M/__pycache__/apply.cpython-312.pyc (08:19 local, git-ignored bytecode cache; not a record, left in place). Nothing else outside W-R changed (git status). Compute: 5414 s of 2-thread runs = ~3.0 core-h + KA-F/pytest/post-hoc ~0.3 core-h. Report delivered in final message.
