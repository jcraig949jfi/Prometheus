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
