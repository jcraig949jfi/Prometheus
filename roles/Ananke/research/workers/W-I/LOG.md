# W-I LOG

A0 2026-09-28 ~01:10  Read COMMON_RULES, COMMON_RULES_ARC3, brief, both instrument
   cards, lens/engine/envs/physics, c1b.ticks, W-F census_table.csv + PLAN.md,
   W-C wc_probe.py + x12.json head. Did NOT read SYNTHESIS*, C1B_REVIEW*,
   PTE_ENGINE_CARD, ARC3_PRIORITIES, or any worker REPORT.md before PLAN.
A1 smoke (GPU lease ee52d0b4c9d7, comms 772/773): traj.selfcheck bit-identical
   to lens.run for normal / site_all@3 / channel_all@3 on 4ab2ba01 and 0a23398f.
   Timing: 48-arm block 3-9 s, twin profile 1.4-2.9 s, peak 1 GB. No verdicts read.
A2 PLAN.md frozen.
A3 05:12Z GPU acquire -> BUSY (W-H until 06:50Z). Queued in QUEUE.md (Q1). Acquired cpu8
   lease b8cbd0e651f1 (comms 775) and started the SAME frozen experiment on CPU: 4 procs x
   2 threads (main.py; per-specimen lock files so a later GPU process only takes what is
   left). CPU cost: ~8-10 min per delta-8 specimen, ~30 min per delta-16.
A4 05:24Z analyze.py first run failed (ModuleNotFoundError: prometheus; sys.path) -> fixed
   path line only. No rule/threshold changes.
A5 06:05Z partial read (15 panel RELAY cells): EVERY panel RELAY specimen has >= 1 C label;
   the frozen robustness classes therefore give SITE-ONLY n=0 in the panel -> the primary
   robustness test will be INCONCLUSIVE (too few) by the frozen eligibility rule. Not changed.
   Any within-panel robustness analysis on other trajectory features will be labelled
   EXPLORATORY (post hoc), not a test of H1-H3.
A6 07:07Z main complete: 33/33 specimens (CPU, 4x2 threads). cpu8 released 07:10Z (comms 784).
   robust.py started 07:00Z on CPU (2 threads, no lease needed).
A7 07:12Z POST-HOC instrument check (identity_check.py, not in PLAN): M/J rows had
   site_acc + chan_acc = 1.00 almost exactly even where phi ~ +0.1 (369f5a5b, 4781b0a1).
   Reason: mirror partners share all physics randomness, so after a swap world B's
   site-swapped state (site_A, chan_B) equals world A's channel-swapped state; with no
   input between swap and readout (RELAY/MAJ, and 4ab2ba01) the readout of the current trial
   is identical and targets are opposite -> sum = 1 per trial. Measured: 100% of trials
   for 2dccdaa5, 4ab2ba01, 78f3b0ec; 98% 4781b0a1; 62-68% 369f5a5b (history-carrying
   mechanism: every-trial swaps make the arms' histories differ). So sum~1 is (near-)forced
   by the design and is NOT evidence of a per-trial mixture (contradicts the F5' reading).
   The frozen M rule's operative clause is phi (= -corr of partners' site-swap failures).
   Labels NOT changed.
A8 07:30Z after all main+robust runs and analysis, read SYNTHESIS_2026-09-28_ARC2.md s1-3, ARC3_PRIORITIES item 2, PTE_ENGINE_CARD lines 40-62 to write DISAGREEMENTS (post-PLAN; no rule changes).
A9 07:25Z robust.py complete (33/33, CPU). analyze.py final: out/traj_table.csv, out/table_<cell>.csv
   (33 per-specimen per-offset tables), out/motifs.json, out/robust_tests.json,
   out/analyze_console.txt. Frozen decisions: panel robustness INCONCLUSIVE (SITE-ONLY n=0);
   all-specimen H1-H3 NOT SUPPORTED (diffs .09/.03/.13 < .20; physics-confounded).
   explore.py (EXPLORATORY, post hoc): census mid-tick replication and latency
   retention vs 'slack' (Spearman .52, n=23) -> out/explore.json.
A10 GPU never used (W-H then W-J held it); Q1 in QUEUE.md is VOID (run completed on CPU).
