# AUDIT M -- do recorded program verdicts follow the frozen consequence tables?

Auditor: subagent of Hecate[m1-dd0c3882], 2026-09-30 (read-only; this file only).
Inputs read: roles/Hecate/prereg/{2026-09-29_probe_round1, 2026-09-30_probe_round2,
2026-09-30_pass3_v2, 2026-09-30_pass4_round1, 2026-09-30_pass4_round2}/PREREG.md;
hecate/programs/HT-*/program.json (16), every worlds/*/OUTCOME*.json and
pass4/PASS4_OUTCOME.json, DOSSIER.md "CURRENT VERDICT" lines,
PROBE_ROUND{1,2,3}_REPORT.json, PROBE_ROUND{2,3}_SELECTION.jsonl,
PASS4_ROUND{1,2}_REPORT.json, harvest_w2/CORRECTIONS_2026-10-01.md.
Method: rebuilt each program's sequence (R1 probe -> R2 probe -> R3 probe ->
Pass 4) from world outcome classes alone, applied each governing table in
order, compared with program.json currentVerdict (post-K4).

## 1. Discrepancies

### 1a. Program verdicts: NONE

All 16 re-derived verdicts equal the recorded currentVerdict (a9e2 taken
after K4). Final tally, recorded = re-derived: PARK 14, PROBING 1 (321a),
SPECULATIVE 1 (a9e2).

### 1b. World outcome classes outside the governing prereg's set: NONE

  R1 (probe_round1) allowed {SIGNAL, NULL, CONFOUNDED, INSTRUMENT_FAIL,
     NOT_BUILT}: all 16 recorded classes are in the set.
  R2 (probe_round2) allowed R1 set + SPEC_UNATTAINABLE: all 13 in set.
  R3 (pass3_v2: "classifies with the round-1 classes") : all 8 are
     NULL/SIGNAL; no SPEC_UNATTAINABLE or INCONCLUSIVE was recorded.
  Pass 4 r1/r2: recorded ALT statuses PASS/FAIL/NOT_ELIGIBLE and
     predicates ORIG_FOSSIL_ALT_PASS/PARK are all named by the tables.
  Recorded vs evaluator class differs in 3 places, each by an allowed rule:
     e106 W2, faa9 W2: OUTCOME.json INSTRUMENT_FAIL (attempt 2) -> program
       NOT_BUILT ("a second INSTRUMENT_FAIL -> NOT_BUILT"). Correct.
     a9e2 W3: OUTCOME.json NULL -> program SPEC_UNATTAINABLE (K4,
       annotated). Correct by the R2 definition.

### 1c. Record-keeping defects (verdict unchanged; reason/provenance wrong)

  D1 HT-55162c0ac0 and HT-8a87057933: evidenceSummary.note and DOSSIER
     "CURRENT VERDICT" say "Pass 4 round 1: PARK". Both were Pass 4
     ROUND 2 (PASS4_ROUND2_REPORT.json; prereg 2026-09-30_pass4_round2).
     Before: "Pass 4 round 1: PARK". After: "Pass 4 round 2: PARK".
  D2 HT-71b65251aa: pass4_round1 says "ALT NOT_ELIGIBLE twice / controls
     fail -> PARK with reason recorded". The note says only "Pass 4 round
     1: PARK"; the reason (ALT_V1 gap 0.0000, ALT_V2 gap 0.0003, both
     < 0.02 -> NOT_ELIGIBLE twice) is only inside the pass4 block.
     Before: "Pass 4 round 1: PARK". After: "Pass 4 round 1: PARK (ALT
     NOT_ELIGIBLE twice: L2-L1 gap 0.0000 and 0.0003 < 0.02)".
  D3 PROBE_ROUND2_REPORT.json still reads a9e2 W3 NULL / PARK and counts
     NULL 7, SU 6, PARK 9, SPECULATIVE 4 with no annotation. Post-K4:
     NULL 6, SU 7, PARK 8, SPECULATIVE 5. (Originals stay visible by
     policy; the report has no pointer to K4.)
  D4 HT-a9e2ba7618 is SPECULATIVE with eligible worlds left (W1, W2) but
     is in no later round: pass3_v2's 8-program list was frozen before
     K4. Not a derivation error; it is the only open program nobody has
     scheduled.
  D5 HT-55162c0ac0 Pass 4 r2: R "reproduced": false (corr-grouping mean
     ARI -0.111 fails the frozen |mean| <= 0.1 reading). No table row
     covers "R fails"; the verdict is still PARK because ALT failed
     (A1 0.00 < 0.2, A2 0.369 < 0.6). Gap in the table, not in the verdict.

## 2. Governing rule text (quoted)

  [R1] probe_round1: "SIGNAL program -> PROBING; world goes to Pass 4" /
       "NULL ... the triplicate stays SPECULATIVE ... two NULL worlds ->
       PARK" / "CONFOUNDED counts as NULL for the world" /
       "INSTRUMENT_FAIL one instrument repair allowed, then rerun; a second
       INSTRUMENT_FAIL -> NOT_BUILT" / "NOT_BUILT next eligible world in
       round 2".
  [R2] probe_round2: "NULL / CONFOUNDED -> world claim killed with rows;
       with the round-1 world also NULL/CONFOUNDED -> program PARK" /
       "SPEC_UNATTAINABLE / NOT_BUILT -> world recorded; if round 1 was
       also not a valid reading (IF / NB), the program is PARK with reason
       'Pass 3 produced no testable world in two tries'".
  [R3] pass3_v2: "Consequences: as round 2's table, counting only valid
       readings. A revived PARK program that reads NULL goes back to PARK
       with two reasons."
  [P4a] pass4_round1: "ORIG fires, ALT passes  original-world claim FOSSIL
       with rows; program stays PROBING" / "ALT fails  program -> PARK
       (two worlds, no surviving signal)" / "ALT NOT_ELIGIBLE twice /
       controls fail -> PARK with reason recorded".
  [P4b] pass4_round2: "Consequences as round 1 (SURVIVES -> PROMISING;
       ORIG_FOSSIL_ALT_PASS -> PROBING; ALT fails or NOT_ELIGIBLE -> PARK)".

## 3. Per-program table (recorded vs re-derived)

IF = INSTRUMENT_FAIL, NB = NOT_BUILT, SU = SPEC_UNATTAINABLE.
"valid" = SIGNAL/NULL/CONFOUNDED probe readings.

| program | R1 | R2 | R3 | Pass 4 | recorded | re-derived | last rule | valid |
|---|---|---|---|---|---|---|---|---|
| HT-056d3ac561 | W1 IF | W4 NULL | W5 NULL | - | PARK | PARK | R3 (2 valid NULL) | 2 |
| HT-2a8a3aedeb | W4 NULL | W1 NULL | - | - | PARK | PARK | R2 NULL+NULL | 2 |
| HT-321a8fd8e0 | W1 SIGNAL | - | - | r1: R yes, ORIG fired, ALT PASS | PROBING | PROBING | P4a ORIG fires, ALT passes | 1 |
| HT-37e311ce05 | W1 IF | W4 SU | W5 NULL | - | PARK | PARK | R2 IF+SU, then R3 revived->NULL | 1 |
| HT-47f4c02be4 | W4 CONF | W1 NULL | - | - | PARK | PARK | R2 CONF+NULL | 2 |
| HT-55162c0ac0 | W3 IF | W2 SU | W6 SIGNAL | r2: R no, ORIG not fired*, ALT FAIL | PARK | PARK | P4b ALT fails | 1 |
| HT-5b0b3ebb8d | W4 SIGNAL | - | - | r1: R yes, ORIG fired, ALT FAIL | PARK | PARK | P4a ALT fails | 1 |
| HT-71b65251aa | W3 SIGNAL | - | - | r1: R yes, ORIG fired, ALT NOT_ELIG x2 | PARK | PARK | P4a NOT_ELIGIBLE twice | 1 |
| HT-79e904e13a | W4 NULL | W1 NULL | - | - | PARK | PARK | R2 NULL+NULL | 2 |
| HT-8a87057933 | W1 NB | W4 SU | W5 SIGNAL | r2: R yes, ORIG fired, ALT FAIL | PARK | PARK | P4b ALT fails | 1 |
| HT-974471f045 | W3 NULL | W1 SU | W6 NULL | - | PARK | PARK | R3 (2 valid NULL) | 2 |
| HT-a9e2ba7618 | W4 NULL | W3 SU (K4; was NULL) | - | - | SPECULATIVE | SPECULATIVE | R2 NULL+SU: world recorded | 1 |
| HT-ae38c641b1 | W3 NULL | W4 SU | W5 NULL | - | PARK | PARK | R3 (2 valid NULL) | 2 |
| HT-e106e1603b | W2 NB (IF x2) | W1 NULL | W5 NULL | - | PARK | PARK | R3 (2 valid NULL) | 2 |
| HT-e743909f97 | W1 NULL | W3 NULL | - | - | PARK | PARK | R2 NULL+NULL | 2 |
| HT-faa9277e02 | W2 NB (IF x2) | W1 SU | W6 NULL | - | PARK | PARK | R2 NB+SU, then R3 revived->NULL | 1 |

(*) recorded fired=false; K1 says fired in substance. Verdict unaffected.

Intermediate states, checked against the round reports (all agree):
  after R1: PROBING 3 (321a, 5b0b, 71b6), SPECULATIVE 13.
  after R2: PARK 9 / SPECULATIVE 4 as recorded; 8 / 5 after K4.
  after R3: 4 SPECULATIVE + 4 revived -> PARK 6, PROBING 2 (5516, 8a87).
  pass3_v2 program list (4 SPECULATIVE + 4 "no testable world" PARKs)
  matches the post-R2 states exactly.

## 4. Outcome-class counts per round

| round (prereg) | n | SIGNAL | NULL | CONF | IF | NB | SU |
|---|---|---|---|---|---|---|---|
| R1 probe_round1 | 16 | 3 | 6 | 1 | 3 | 3 (2 via IF x2) | - |
| R2 probe_round2 (recorded) | 13 | 0 | 7 | 0 | 0 | 0 | 6 |
| R2 probe_round2 (post-K4) | 13 | 0 | 6 | 0 | 0 | 0 | 7 |
| R3 pass3_v2 | 8 | 2 | 6 | 0 | 0 | 0 | 0 |

| Pass 4 round | n | R reproduced | ORIG fired | ALT PASS / FAIL / NOT_ELIG | predicate |
|---|---|---|---|---|---|
| r1 (pass4_round1) | 3 | 3 | 3 | 1 / 1 / 1 | ORIG_FOSSIL_ALT_PASS 1, PARK 2 |
| r2 (pass4_round2) | 2 | 1 | 1 recorded (2 per K1) | 0 / 2 / 0 | PARK 2 |

pass3_v2 falsification rule (>= 3 of 8 unattainable/IF/NO_FREEZABLE): 0 of
8 -> repair not falsified, as recorded.

## 5. Verdicts resting on a single world reading

Count of valid probe readings per program (column "valid" above):
  - 8 of 16 verdicts rest on ONE probed world: 321a, 37e3, 5516, 5b0b,
    71b6, 8a87, a9e2, faa9.
  - Of those, Pass 4 added a second, different-construction reading
    (ALT) for 5b0b, 5516, 8a87 (all FAIL) and 321a (PASS, but C2: fixed
    by counting, Kmaj = 0 for any allocation).
  - Strictly one reading, nothing else read: 37e3 (PARK; W5 NULL),
    faa9 (PARK; W6 NULL), a9e2 (SPECULATIVE; W4 NULL), 71b6 (PARK; ALT
    never read, NOT_ELIGIBLE twice) = 4. Adding 321a's degenerate ALT: 5.
  - The 8 two-reading PARKs: 056d, 2a8a, 47f4, 79e9, 9744, ae38, e106,
    e743. Two of them have a contested reading: ae38 W5 (C1) and 79e9 W4
    (C3, instrument-weak). If either reading fell, that program would be
    SPECULATIVE on one NULL.

## 6. Procedural observations (no verdict effect)

  - R1 IF worlds 056d W1, 37e3 W1, 5516 W3 have attempts = 1: the one
    permitted repair was declined, with reasons, in each
    IMPLEMENTATION_NOTES.md ("allowed", not required). R2's table then
    treats IF and NB alike, so taking the repair could not have changed
    37e3 or 5516. For 056d it could have: a repaired W1 reading NULL
    would have PARKed 056d after R2 instead of R3. Same end state.
  - Round-3 world choice (lower cost of W5/W6) was not re-derived here.

## 7. Position on K1-K11 and C1-C7 (verdict-relevant items only)

  K1  agree; no verdict change (5516 PARK via ALT FAIL either way).
  K4  agree. R2 defines SU as "cannot be reached even by a construction
      that has the effect by design"; with the deciding clause
      unattainable, NULL+SU -> SPECULATIVE is the table's output.
  C1  agree it is a ruling, not a derivation error. ae38 W5 clause values
      S1 = F1 = 0.334, S2 = 0.277; no S or F clause met. Under R1's NULL
      definition ("treatment fails the criterion") that is NULL, so PARK
      follows from the frozen text. If the spec's INCONCLUSIVE band is
      ruled to govern: ae38 PARK -> SPECULATIVE.
  C2  agree. PROBING is the correct output of [P4a], which has no
      counting check; the implementer's own anomaly line already says
      "ALT pass is guaranteed by counting". Under [P4b]'s arithmetic rule
      it would be NOT_ELIGIBLE -> PARK. Needs a ruling.
  C3  agree; 79e9's PARK rests on it (section 5).
  C4  not re-verified; it does not decide ae38's verdict (W3 and W5 do).
  K2, K3, K5-K11, C5-C7 concern the alien pilot / gravity / autopsy, not
  program verdicts; not audited here.
