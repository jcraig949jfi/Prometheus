# W-G LOG  retention confirmation (adversarial, preregistered)

Attempt 0 (2026-09-28, before PLAN): read handoffs COMMON_RULES.md,
COMMON_RULES_ARC3.md, W-G_retention_confirmation.md; engine.py, lens.py,
physics.py, envs.py, assays.py (evaluate), plants.py, c1b_run.py (load,
d_wave_cells); W-E raw evidence: PLAN.md, LOG.md, ret_census.py,
explore_hist.py, probe_trace.py, out/census.log; PRIOR_ART s3.1, s4.2-4.4.
Context contamination (ARC3 rule 2): W-E's LOG.md contains W-E's own
descriptive interpretation (e.g. "FROZEN single-element scars" in w / Kp / S
for f7e62fe3, fresh3, 0ad7dc00, 6a47bd68; "INTERFERES (unsigned)" for
fresh2/3). I read that before writing PLAN. I did NOT read W-E REPORT.md,
SYNTHESIS*, C1B_REVIEW*, PTE_ENGINE_CARD.md, ARC3_PRIORITIES.md or any other
worker's REPORT.md. The confirmation namespace 0x5EC has not been used.

Attempt 1 (PLAN v1 written; wg.py written). Smoke: controls on 0x5EB with
nperm 200 (tag _smoke, out/0x5eb_smoke/). Host is contended: GPU leased by
W-H and cpu8 by W-I (4 procs x 2 threads), both until ~02:52 EDT; one run of
64 worlds takes ~20 s at 2 threads. Leases not requested (both BUSY; I stay
at ONE process x 2 threads, which needs no lease). Smoke results (3 of 5
controls finished before I stopped the smoke to start the real run):
C-NEG all levels null, every probe g == 0 exactly (merge at trial k+1);
C-INT L1 32/32 frozen S1 scar, PAIR 1.0, D2 0.81, L3 g == 0, P1-P4 g == 0,
RELOC fires via sign(S1) at the actuator, sufficient store S, history
ratio 1.17 (-> ACCUMULATION, as designed: it integrates every cue);
C-EFF L3, BLANK, PING fire; CLEAR probes 0 (they wipe the S0 integrator,
as expected). Guards pass. All as preregistered.
Code change before the real run (efficiency, not a rule change): a heal of
a carrier group with no differing element in any pair at the heal tick is a
no-op, so its outcome is taken from the baseline run instead of re-running.
Attempt 2: discovery run 0x5EB, nperm 20000: 5 controls, then 16 specimens,
one process, 2 threads (out/disc_controls.log, out/disc_specimens.log).
Attempt 2a (discovery controls, 0x5EB, nperm 20000; out/0x5eb/C-*.json):
all five behave as preregistered at unadjusted alpha 0.01.
C-NEG: merged by k+1, all tests p = 1, every probe g == 0.
C-INT: L1 frozen, PAIR p 5e-5, D2 0.81 p 5e-5, D1 0.64 p 0.005, L3 and P1-P4
exactly 0, RELOC p 0.002 (sign(S1)). Class ACCUMULATION in S (ratio 1.17).
C-EFF: L3 p 0.0034, BLANK p 4e-4 (PING p 0.03, not required), CLEAR probes 0.
C-AVL: L3 exactly 0 in normal operation; CLEAR_S0 and CLEAR_FAST p 4e-4
(the Kp integrator re-drives S0 after the readout register is wiped);
BLANK/PING 0; sufficient store Kp. The L4 instrument works on a latent
store that normal operation never expresses.
C-CHAOS: L1 32/32, PAIR 0.75 p 0.036 (NS) -> CHAOTIC; L3 p 0.75 although
answers differ unsigned; D1/D2 NS; probes NS. frozen fraction 0.53.
Attempt 2b (discovery specimens 0x5EB; out/0x5eb/, out/0x5eb_summary.json):
guards pass in all 16. After Holm: L3 none; L4-dyn none; L4-readout none;
L2 only D_f7e62fe3 (D2 0.953, w_sum, raw p 5e-5); L1 persistent in 8.
Smallest raw L4 p: D_e79e72df BLANK 0.022. f7e62fe3: under EVERY probe the
twins give identical answers (g == 0 exactly) although w differs in 32/32.
Two defects of the mechanism-class rules found on reading (F1, F2 in PLAN
Addendum F); fixed before confirmation. Decision rule unchanged.
Attempt 3: PLAN frozen; sha256 in out/freeze_sha256.txt. Confirmation run 0x5EC launched (controls then specimens, 1 proc x 2 threads).
Attempt 3a (CONFIRMATION 0x5EC, nperm 20000; out/0x5ec/, out/0x5ec_summary.json,
out/conf_*.log): all guards pass in 21/21. Controls: C-NEG null; C-INT, C-EFF,
C-AVL, C-CHAOS each as preregistered (C-AVL CLEAR_S0/CLEAR_FAST p 1.5e-4;
C-EFF L3 p 0.0038, BLANK p 1.5e-4; C-CHAOS PAIR p 0.39).
DECISION RULE APPLIED: no specimen has L3 or any L4-dyn probe after Holm
(every specimen's L3 and P1-P4 adjusted p = 1). Verdict: NO nontrivial
retention regime. L2 in 0x5EC: D_f7e62fe3 (D2 0.906, adj 0.0016) and
M2_fresh2 (D2 0.719, adj 0.0016; NOT significant in discovery, adj 0.76).
Instrument defect seen after the fact: F2's 0.75 gate misclassifies the
integrator controls in 0x5EC (in-sample 0.72) as "specificity
undetermined"; class labels are descriptive and do not enter the decision.
Attempt 4 (POST-HOC EXPLORATORY, discovery namespace 0x5EB only):
explore.py -- scar anatomy at end of k+6 and heal-all-but-X regeneration
tests for f7e62fe3, 0ad7dc00, 6a47bd68, e79e72df, fresh2, fresh3.
Attempt 4 result (out/explore_0x5eb.json/.log, EXPLORATORY): f7e62fe3: the
w difference (c*dw in {8..52}, all positive; 27 of the listed elements at
the actuator site) stays confined to w after healing everything else, and
no later answer differs. fresh3: w scar = exactly +8 (x c) at the SENSOR
site in 32/32; healing all but w -> fast carriers RE-DIVERGE by trial k+4
and 4-9 answers per trial differ, sum_g ~ 0 (unsigned); healing all but Kp
-> stays Kp-only, no answer differs. fresh2 same pattern via w. 0ad7dc00: S
and Kp each keep a persistent difference alone (c*dKp ~ -300, 28/28
negative), inert. 6a47bd68: S residues c*d in {5, 7, 22}, all positive,
at non-sensor non-actuator sites (decay_shift 3 floor), inert. e79e72df:
Kp-only after heal, inert.
Context after the rule was applied: read W-E REPORT.md, ARC3_PRIORITIES.md,
SYNTHESIS_2026-09-28_ARC2.md and PTE_ENGINE_CARD.md retention passages to
write DISAGREEMENTS (after freezing and applying the rule).
No git operations. Leases: none taken (one 2-thread process throughout;
GPU and cpu8 were held by W-H / W-I / W-J during the whole session).
REPORT delivered in the final message (ARC3 rule 1).
