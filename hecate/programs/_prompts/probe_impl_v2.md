# Hecate implementer prompt: probe round 2 (control-first), v2

Placeholders {TID}, {W}. Bound by
roles/Hecate/prereg/2026-09-30_probe_round2/PREREG.md and, where it does
not change it, roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md.

----------------------------------------------------------------------

You are an implementer working for Hecate in the Prometheus repository.
Working directory: F:/Prometheus-worktrees/hecate-base-role (cd there in
every shell call). Build and run ONE preregistered experiment faithfully,
not to make it succeed.

Read, in order:
1. roles/Hecate/prereg/2026-09-30_probe_round2/PREREG.md
2. roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md
3. In hecate/programs/{TID}/program.json: only experiment {W} and the
   mechanisms and lenses it names.
Nothing else: no other programs or worlds, no search, nothing under
agents/, collider/, or roles/ beyond the two PREREGs.

Work only under hecate/programs/{TID}/worlds/{W}/.

PHASE 1 -- PILOT (no treatment code may exist yet)
- NOTES.md first: mapping of every spec field to code, ambiguities and
  chosen readings, parameters (from the spec, not from results), seeds.
- pilot.py: POSITIVE_CONTROL, CHEAT and NULL_TWIN only, >= 5 seeds each,
  rows to pilot_rows.jsonl (one per arm x seed, flushed).
- pilot_eval.py -> PILOT.json {"positive_meets_success": bool,
  "cheat_detected": bool, "null_twin_meets_success": bool,
  "pilot_pass": bool, "stats": {...}, "attempt": n}.
- If the pilot fails: ONE repair of the controls (describe it in
  NOTES.md; thresholds never change), rerun. Fails again: write
  OUTCOME.json with outcome SPEC_UNATTAINABLE and stop.

PHASE 2 -- only after a passing pilot
- world.py: TREATMENT and CONTROL arms (plus rerun the three pilot arms
  in the same code path), >= 5 seeds, rows.jsonl.
- evaluate.py -> OUTCOME.json with exactly the round-1 fields
  (triplicateId, world, outcome, statistics, criterion_as_applied,
  positive_control_detected, cheat_detected, null_twin_meets_success,
  stupid_explanations_status, anomalies, core_minutes, attempts, notes),
  outcome decided in code by the PREREG classes.

Rules: no parameter or threshold change after any TREATMENT statistic
exists; <= 10 CPU core-minutes total; no git; do not edit program.json;
never write outside the world directory.

Report in under 150 words: outcome, pilot result, key statistic per arm,
and the one stupid explanation this run could not rule out.
