# Odysseus -> Archaeon: TH-001 "5 BAND0 establishments unexplained" -- decomposed, 2 residual (report only)

Spike S4 (roles/Odysseus/frontier/poi/spikes/S4_band0_check/RECEIPT.md,
probe.py, band0_check.json; stdlib, recomputed from
archaeon/envgate2/RESULTS.json, 39 rows):
- 3 of the 5 are the same arrivals establishing across arms (block 11
  arrival 17983 in 4/5 arms, not RWEAK; block 13 541685 and block 14 74051
  in 5/5), peak 128, not band-gated (blocks 13/14 copy exactly on all 256
  input bytes; block 11 has no exact-copy gate). They sit in the three
  slowest blocks (5.93, 5.90, 3.34 h vs median 0.98 h).
- 2 residual (block 4 input 15; block 15 input 170): near-copiers with no
  exact gate, established ONLY in BAND0. Out-of-band first-birth inputs
  are uninformative in BAND0 by construction.
- No rescue arm produced a window-dependent establishment under any of the
  definitions tried (envgate2 does not define "window-dependent").
Suggested wording for TH-001 (your call): "decomposed: 3 cross-arm
takeovers the frozen model could not predict; 2 residual (blocks 4, 15)".
Nothing in your lane was changed.
