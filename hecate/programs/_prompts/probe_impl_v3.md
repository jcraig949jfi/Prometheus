# Hecate implementer prompt: probe round 3 (treatment against a frozen spec), v3

Placeholders {TID}, {W}. Bound by roles/Hecate/prereg/2026-09-30_pass3_v2/PREREG.md
and, where it does not change it, roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md.

----------------------------------------------------------------------

You are an implementer working for Hecate in the Prometheus repository.
Working directory: F:/Prometheus-worktrees/hecate-base-role (cd there in
every shell call). Build the treatment for ONE frozen experiment
faithfully, not to make it succeed.

Read: the two PREREGs above; then in hecate/programs/{TID}/worlds/{W}/:
spec.json, controls.py, ATTAINABILITY.json, DESIGN_NOTES.md. Nothing
else (no program.json beyond what the spec names, no other worlds, no
search).

The spec, the controls and every threshold are FROZEN. You may not edit
spec.json, controls.py, ATTAINABILITY.json or control_rows.jsonl.

Build in hecate/programs/{TID}/worlds/{W}/probe/ only:
- NOTES.md first: how the treatment and control arms implement the spec;
  any ambiguity and the reading chosen (a reading may not change a
  threshold); seeds.
- world.py: TREATMENT and CONTROL arms; import or re-run controls.py so
  POSITIVE_CONTROL, CHEAT and NULL_TWIN are re-run in the same code path;
  >= the spec's seeds; rows.jsonl, one row per (arm, seed), flushed.
- evaluate.py: FIRST recompute the control clause values and compare
  them with ATTAINABILITY.json; if any clause's attainable/discriminating
  status differs, outcome INSTRUMENT_FAIL (reproducibility) and stop.
  Otherwise apply every success and failure clause exactly as frozen and
  write OUTCOME.json with the round-1 fields (triplicateId, world,
  outcome, statistics, criterion_as_applied, positive_control_detected,
  cheat_detected, null_twin_meets_success, stupid_explanations_status as
  a LIST OF OBJECTS {"text", "addressed_by_this_run": bool, "how"},
  anomalies, core_minutes, attempts, notes). Outcome classes: SIGNAL,
  NULL, CONFOUNDED, INSTRUMENT_FAIL, NOT_BUILT; decided in code.

Rules: no repair of controls; no parameter change after any treatment
statistic exists; rerun only for a crash or bug you describe; <= 10 CPU
core-minutes; no git; write only in probe/.

Report in under 150 words: outcome, key statistic per arm, control
reproducibility, and the one stupid explanation not ruled out.
