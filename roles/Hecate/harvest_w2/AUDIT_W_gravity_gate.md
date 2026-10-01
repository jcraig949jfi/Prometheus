# AUDIT W -- gravity detector calibration gate (meta v1, M1)

Auditor: Hecate subagent, 2026-09-30. Read-only. No model/API calls. All values
recomputed locally from committed rows by importing
hecate.gravity.run.calibration_gate (scratch script outside the repo).

Inputs: hecate/gravity/run.py, controls_v1.json (14), calibration_rows_v1.jsonl
(14 rows), gate_v1.json, calibration_v1.json, detector_v1.md, hecate/meta/scrub.py,
PREREG.md (M1 gate, lines 55-62), roles/Hephaestus/HEPHAESTUS_2_0_GRAVITY_PILOT.md
("Calibration Control", lines 111-131; the PREREG cites it as the design),
hecate/meta/REPORT_v1.md, hecate/meta/detector/detect_rows_v1.jsonl (format only).

## Summary

The gate as frozen was computed correctly and PASSES (8/8 knowns, 0/4 nonsense
FAMILIAR). No reported decision changes under the frozen PREREG. But the gate
does not calibrate the one boundary M1's result turns on (FAMILIAR vs
COMPOSITE), cannot fail on its composite controls, has no coherent-unfamiliar
control, and is passed by a two-rule lexical labeller with a fixed prior
string. The detector's only evidence on the FAMILIAR/COMPOSITE boundary is 0/2.

## (1) Re-derivation

- 14 rows, 14 distinct items, one row each; all ok=True, rc=0, scrub_leaks=[],
  model claude-opus-5-5, detector_sha256 91fbe8f2b9.. == sha of current
  detector_v1.md.
- scrub(controls_v1.text) == recorded blind_text for 14/14 (confirms K3).
- Re-derived {table, gate} == calibration_v1.json exactly; == gate_v1.json
  except gate_v1.json carries an extra hand-added "note" key (run.py never
  writes it). Gate: knowns 8/8, nonsense FAMILIAR 0/4, composites 2/2,
  all_calls_ok True, PASS True.
- Stricter reading "correct family = closest prior (rank 1)": still 8/8
  (every known's rank-1 name matches). Changes a reported decision: NO.

## (2) Clause-by-clause vs PREREG text

W1 "at least 12 controls per the Hephaestus 2.0 design" -- 14 present. But the
   design source lists, besides disguised knowns and nonsense, "weird mixtures
   of two familiar mechanisms" with expected result "novel composites ->
   intermediate/uncertain". The PREREG dropped any composite requirement; code
   (run.py:83-85) counts composites_detected but omits it from PASS
   (run.py:94). Code matches PREREG; PREREG does not carry the design's
   composite expectation. Decision change: NO under frozen text (see W6).
W2 "Disguised familiar mechanisms (PID, TCP, Hebbian, Kalman, reaction-diffusion,
   stigmergy, finite-state control, autocatalysis) must be classified FAMILIAR
   in >= 7 of 8 with the correct family named" -- run.py:80-82, threshold
   known_hit >= 7 (integer, no float). Matches. "Correct family named" is
   implemented as case-insensitive substring of ANY of the nearest_priors names
   (run.py:78-79), not the closest one; nearest_priors length is not checked
   (prompt says "exactly 3"). Decision change: NO (rank-1 also 8/8).
W3 Substring family match is loose. Cross-matching each control's accept list
   against every row's prior names: C06 accept "ACO" hits C02 via
   "Jacobson" (false positive); C07 "automata/automaton" hits C05, C11, C14;
   C05 "Turing/reaction-diffusion" hits nonsense C11; C01 "PID" hits C09;
   C04/C10 "Kalman" cross-hit. On the actual rows every known also has a
   genuine match, so NO decision change; the matcher would accept wrong-family
   answers on other data (e.g. any name containing "aco", "tcp", "oja", "ltp").
W4 "incoherent/nonsense controls must be classified FAMILIAR in <= 1 of 4" --
   run.py:86-88, nonsense_fam <= 1. Matches. Note the clause is one-sided:
   nonsense called COMPOSITE or UNFAMILIAR passes. Since M1 counts only
   FAMILIAR, a detector that calls junk UNFAMILIAR would make junk look
   "novel" (lower M1) and still pass. Observed 4/4 INCOHERENT, so NO change.
W5 "If the gate fails, M1 is INDETERMINATE" -- enforced at detection time only
   (run_arms.py:173-176 reads gate["PASS"]; at run time it read
   CALIBRATION_v1.json, same file as calibration_v1.json on this FS).
   analyze.py:140 hardcodes the string "CALIBRATION_v1.json (gate PASS)" into
   RESULTS_v1.json instead of reading the gate, and cites a path that does not
   exist on a case-sensitive checkout. Fail-closed paths are sound: a missing
   row gives ok=None -> all_calls_ok False; a scrub leak gives ok=False; a
   parse failure or class outside CLASSES gives ok=False (run.py:43-45,
   93-94). No failed call is silently dropped here. Decision change: NO.

## (3) Constant and near-constant labellers (computed via calibration_gate)

OMNI = one fixed prior name "PID AIMD Hebbian Kalman reaction-diffusion
stigmergy finite-state autocatalytic genetic algorithm bandit" on every item.

  labeller                                          K/8  NF/4  C/2  PASS
  const FAMILIAR, empty priors                       0    4     0    no
  const FAMILIAR, OMNI                               8    4     2    no
  const COMPOSITE, OMNI                              0    0     2    no
  const UNFAMILIAR                                   0    0     0    no
  const INCOHERENT                                   0    0     0    no
  FAMILIAR on 10 coherent, UNFAMILIAR on nonsense    8    0     2    YES
  FAMILIAR on 10 coherent, COMPOSITE on nonsense     8    0     2    YES
  FAMILIAR except 3 nonsense INCOHERENT              8    1     2    YES
  observed, but composites -> COMPOSITE              8    0     2    YES
  observed, but composites -> INCOHERENT             8    0     0    YES

No strictly constant labeller passes. But a labeller that never outputs
COMPOSITE or UNFAMILIAR on coherent text passes with a fixed prior string,
and the composite controls cannot move the verdict under any output (last two
rows). The gate has no coherent item whose truth is not FAMILIAR (no
coherent-unfamiliar control, and composites are ungated), so "always FAMILIAR
on coherent input" -- the failure M1 most needs to exclude -- is undetectable.

## (4) Do blind texts reveal category by vocabulary?

- scrub() is a no-op on all 14 controls: 0 [X]/[NAME] masks, text unchanged.
  The controls were hand-written to avoid the dictionary, so the scrubber was
  never exercised by calibration.
- Lexical separation is perfect. A regex of 17 mentalistic/abstract words
  (meaning, belief, intelligence, understanding, remember*, surprised,
  elegant, observer, question, reason, nothing, tomorrow, absences, rhyme,
  doubted, forgetting) hits nonsense C11-C14 with 6, 6, 5, 2 matches and the
  10 coherent controls with 0. Combined with "FAMILIAR + OMNI" otherwise, that
  rule passes the gate (table row 6/7 shape).
- Calibration inputs are off-distribution from measured items: arm items are
  field-formatted ("statement: ... what exists: ...") 400/400 and carry masks
  307/400; controls are free prose 14/14 ending "Predicted behaviour:", 0/14
  masked. The gate certifies the detector on a format M1 never presents.
- Disguised knowns contain no accept-list string in their blind text (0/10),
  so family recovery is not a string leak. Good.
Decision change: NO (instrument-validity finding).

## (5) Both COMPOSITE controls called FAMILIAR, gate PASSED -- allowed?

Yes, by construction, twice over:
 a) The PREREG gate has no composite clause; run.py:94 PASS uses only
    all_calls_ok, known_hit >= 7, nonsense_fam <= 1.
 b) Even the reported composite count treats FAMILIAR as a hit
    (run.py:83-84: cls in ("FAMILIAR","COMPOSITE") and family named), so
    C09/C10 = FAMILIAR were tallied "composites_detected 2/2". The
    controls_v1.json note states this ("COMPOSITE also accepted").
    gate_v1.json therefore reports 2/2 for an outcome that is 0/2 on the
    question "does the detector say COMPOSITE for a known composite".
    C09 is also matched on "PID" alone, so a plain-PID answer would count.
W6 Why it matters: REPORT_v1 says the whole M1 gain of T and P over S/O/G is a
   FAMILIAR -> COMPOSITE shift (T 7 F/73 C; S 62 F/18 C). M1's ADDS_VALUE_vs_S
   and ADDS_VALUE_vs_O verdicts therefore rest entirely on the FAMILIAR/
   COMPOSITE boundary, which the gate never tested and on which the only
   calibration evidence is 0/2 in the direction OPPOSITE to the arm calls
   (known composites -> FAMILIAR; arm outputs -> COMPOSITE).
   Changes a reported decision: NO under the frozen PREREG (gate PASS is
   correct as written). Counterfactual: had the PREREG carried the cited
   design's "composites -> intermediate" expectation with any threshold >= 1
   of 2, the gate FAILS and M1 is INDETERMINATE (ADDS_VALUE_vs_S/O would
   not be reportable). Record as a PREREG-vs-design-source omission, not a
   code defect.

## Other

W7 Original run.py read controls from calibration_v1.json and wrote the gate to
   CALIBRATION_v1.json -- one file on NTFS, so `calibrate` destroyed its own
   input on first run (root cause of K3; already corrected in 684ffbbd1).
W8 gate_v1.json is not byte-reproducible by run.py (extra "note" key). Minor
   provenance; re-running calibrate would drop the note. Decision: NO.
W9 Design source also lists un-disguised "known familiar mechanisms -> HIGH
   gravity"; none present. Minor. Decision: NO.

## Findings table

  id  location                       finding                              decision change
  W1  PREREG 55-62 / run.py:94       design's composite clause dropped    NO
  W2  run.py:78-82                   family = any of priors, len unchecked NO
  W3  run.py:79 substring match      "ACO" in "Jacobson" etc.             NO
  W4  run.py:86-88                   nonsense UNFAMILIAR passes           NO
  W5  analyze.py:140                 gate PASS hardcoded, dead path       NO
  W6  run.py:83-85, REPORT_v1 62-65  M1 boundary uncalibrated, 0/2        NO (frozen) /
                                                                          YES if design clause
  W10 run.py:94                      lexical 2-rule labeller passes       NO
  W11 scrub.py on controls           scrub no-op; controls off-format     NO
  W7  run.py (pre-684ffbbd1)         self-overwrite of controls           NO (fixed)
  W8  gate_v1.json                   hand-added note, not run output      NO
  W9  controls_v1.json               no undisguised knowns                NO

Recommendation for v2 gate (consistent with REPORT_v1 v2 list): add coherent-
unfamiliar and composite controls with two-sided clauses (COMPOSITE required
for composites, FAMILIAR forbidden); run controls through mechanism_text-style
field formatting with dictionary words so scrub() masks them; match family on
rank-1 with word-boundary regex; read the gate in analyze.py, fail closed.
