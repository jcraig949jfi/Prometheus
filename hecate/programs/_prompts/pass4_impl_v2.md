# Hecate implementer prompt: Pass 4 (first falsification), round 2, v2

Placeholders {TID}, {W}. Bound by
roles/Hecate/prereg/2026-09-30_pass4_round2/PREREG.md (and round1 for the common rules).

----------------------------------------------------------------------

You are an implementer working for Hecate in the Prometheus repository.
Working directory: F:/Prometheus-worktrees/hecate-base-role (cd there in
every shell call). Your job is to ATTACK a signal, faithfully, and let it
die if it should.

Read, in order:
1. roles/Hecate/prereg/2026-09-30_pass4_round2/PREREG.md (and round1 for the common rules) -- the common
   rules and the section for {TID} {W}. Its R, ORIG and ALT attacks and
   their thresholds are fixed; you may not change them.
2. roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md (the faithfulness
   guard and outcome vocabulary).
3. hecate/programs/{TID}/worlds/{W}/ (spec.json, controls.py, ATTAINABILITY.json, DESIGN_NOTES.md, probe/)
   and, in hecate/programs/{TID}/program.json, only experiment {W} and
   the mechanisms/lenses it names.

No search; nothing else in the repository.

Build under hecate/programs/{TID}/worlds/{W}/pass4/ only:
- NOTES.md BEFORE any run: how R, ORIG and ALT are implemented; every
  ambiguity and the reading chosen; seeds; parameters (reused from round
  1 unless ALT requires a new world, in which case say exactly what
  changed and why that follows from the PREREG text).
- attack.py writing rows.jsonl (one row per attack x arm x seed, all
  parameters, flushed per row), with positive and cheat controls for
  each world variant you run.
- evaluate.py: prints and writes the positive/cheat control status
  FIRST; only if both are detected does it compute the treatment
  statistics. Writes PASS4_OUTCOME.json:
  {"triplicateId","world","R":{"reproduced":bool,"stats":{}},
   "ORIG":{"fired":bool,"stats":{}},
   "ALT":{"status":"PASS"|"FAIL"|"NOT_ELIGIBLE","stats":{}},
   "controls":{"positive_detected":bool,"cheat_detected":bool},
   "predicate":"SURVIVES"|"ORIG_FOSSIL_ALT_PASS"|"PARK",
   "anomalies":[...],"core_minutes":n,"attempts":n,"notes":"..."}
  The predicate is computed in code from the PREREG rules.

Rules: no threshold or parameter change after any treatment statistic is
printed; <= 10 CPU core-minutes; write only in pass4/; no git; no
deleting files outside pass4/.

Report in under 150 words: predicate, R/ORIG/ALT results with the key
numbers, control status, and the strongest remaining alternative.

v2 additions (binding): build the ALT world control-first -- run its
positive control, cheat and null twin and write pass4/ALT_ATTAINABILITY.json
(every ALT clause attainable and discriminating, cheat detected) BEFORE any
ALT treatment code exists; if not, ALT is NOT_ELIGIBLE. Write
stupid_explanations_status-like fields as lists of objects, never bare
strings. Do not edit anything outside pass4/.
