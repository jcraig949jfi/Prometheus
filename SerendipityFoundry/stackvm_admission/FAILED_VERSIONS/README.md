# Preserved failed versions

* `ENTROPY_RUN1_shannon_gate_failed.txt` — the run in which the proposed
  0.5-bit Shannon gate PASSED the mandatory offline-oracle negative control
  (H=0.869 >= 0.5) while the attacker predicted the verdict 71% of the time.
  This run is the empirical refutation of the proposed standard and is kept
  as the primary evidence for it.
* `VERDICT_ENTROPY_HARNESS.py` — the harness as first written, whose DEFAULT
  configuration (n_refs=3, n_blocks=24, K=1000) is miscalibrated by ~160x
  (empirical level p0=0.16 against a 1e-3 target). Kept because the shipped
  spec would have inherited that configuration had the level check not been
  run.
