# DEVIATION_01 -- runner changes for Families B and C (2026-09-30)

Recorded beside the frozen PREREG; the PREREG text, dataset, answer key,
prompts and scoring rules are unchanged. Authority: CWO 2026-09-30 queue
NEXT for Hecate ("runner key check + Gemini output budget recorded as a
deviation"; comms #1029, ops/fleet/QUEUE.json).

What changed in hecate/alien/runner.py, and why:
1. A reply is parsed only if it contains the task's required top-level keys
   (blind/active: t1..t5; fam: coherence, familiar; reveal: coherence, t2;
   pair: choice; prose: t2). Before, the shared extractor accepted the first
   parseable object, and truncated Gemini replies yielded their inner t1
   object as if it were the whole answer. Existing rows without the keys
   are no longer counted as done and are re-asked.
2. Gemini output budget 16000 -> 65536 tokens (its thinking tokens count
   against the budget; replies were cut at ~1.5k characters). gpt-oss
   unchanged. finish_reason is now recorded per API call.
3. A daily-quota error stops the run cleanly (no retry storm); the next run
   resumes from the rows already written. Free-tier trickle is the CWO
   default; a paid tier is an optional operator spend decision.

Effect on Family A (Claude): none. All 320 Claude rows already carry the
required keys; they are not re-run. Analysis crash fix of the same day
(non-object parses treated as unparseable) is also not a scoring change.
