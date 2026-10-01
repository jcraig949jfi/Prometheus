# W6 probe round 3 -- implementation notes (HT-55162c0ac0)

Written before any treatment statistic exists. Prompt: probe_impl_v3.md
(sha256 a34a8c61...1685). Spec, controls.py, ATTAINABILITY.json and
control_rows.jsonl are frozen and are not modified.

## Arms (world.py)

All arms go through `controls.run_arm` (imported, not copied), so the
map, trajectory, FTLE readout, correlation readout, average linkage and
ARI are the identical code path for every arm.

- TREATMENT: group partners (`controls.group_partners()`), eps_g = 0.05
  (spec; = controls.EPS_G_TWIN), kappa = 0.10. Readout = FTLE grouping;
  row carries ari_ftle (and ari_corr on the same trajectory).
- CONTROL: correlation grouping on the SAME treatment trajectory (spec
  "control"). Implemented as a separate row per seed whose statistic is
  ari_corr from the treatment run (same trajectory, same clustering).
  S2/F2 use per-seed ari_ftle - ari_corr from the treatment row.
- POSITIVE_CONTROL, CHEAT, NULL_TWIN, NULL_TWIN_NOLEAK: re-run exactly as
  controls.main defines them (same partners, seeds 500+seed for random
  partners, same eps_g), but written to probe/rows.jsonl, not to the
  frozen control_rows.jsonl (controls.main is not called because it
  would overwrite that file).

Seeds: 0..9 (spec's 10 seeds); v0 ~ U(-1,1)^12 from default_rng(seed).
Rows: probe/rows.jsonl, one row per (arm, seed), flushed per row.

## Evaluator (evaluate.py)

1. Recompute S1 (mean ari_ftle) and S2 (mean ari_ftle - ari_corr) on
   rerun POSITIVE_CONTROL, NULL_TWIN, NULL_TWIN_NOLEAK and CHEAT. Status
   attainable = positive meets clause; discriminating = NULL_TWIN (and
   NULL_TWIN_NOLEAK, as recorded in ATTAINABILITY.json) does not meet it.
   If any clause's status differs from ATTAINABILITY.json ->
   INSTRUMENT_FAIL (reproducibility), stop. Value differences with equal
   status are recorded as anomalies only.
2. positive_control_detected = PC meets S1 and S2; cheat_detected = CHEAT
   meets S1 and S2. Either false -> INSTRUMENT_FAIL.
3. null_twin_meets_success = NULL_TWIN meets S1 and S2 -> CONFOUNDED.
4. SIGNAL iff treatment meets S1 and S2 (and no failure clause fires).
5. Otherwise NULL.

## Ambiguities and readings chosen (no threshold changed)

- DESIGN_NOTES item 4 calls the band between F and S thresholds
  INCONCLUSIVE, but the round-1 classes have no such class. Round-1 PREREG
  says NULL = "treatment fails the criterion (or meets failure
  criterion)". Reading: not meeting every success clause -> NULL; the
  evaluator also records which failure clauses fire and whether the
  treatment sits in the DESIGN_NOTES INCONCLUSIVE band, in notes and
  statistics, so a reader can distinguish "failure clause fired" from
  "success not reached".
- "Null twin meets success" = meets ALL success clauses (the conjunction
  that defines success).
- Comparison thresholds applied exactly: S >= 0.8 / >= 0.5; F < 0.3 / < 0.2.
- CONTROL arm has no success clause of its own; it enters via S2/F2.
