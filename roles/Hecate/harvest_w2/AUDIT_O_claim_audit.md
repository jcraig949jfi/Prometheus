# AUDIT O -- numeric claim audit of Hecate prose artifacts (read-only)

Auditor: Claude agent (subagent of Hecate[m1-dd0c3882]). No model/API calls,
no git writes; this file is the only write. Worktree HEAD when the audit ended:
7ab70b843 (the tree moved during the audit: CORRECTIONS gained K12-K14/C8 and
LEDGER gained Q15-Q22; the classes below use the files as they stood at the end).
Every value below was recomputed with fresh python from committed rows/JSON
unless the class says otherwise. CORRECTIONS K1-K14 and C1-C8 are not re-reported.
Where a file still carries a value that a K-item superseded without a note in
that file, it is listed as STALE, with the K number.

## Scope and coverage

Files: roles/Hecate/STATUS.md; journal/2026-09-29.md; journal/2026-09-30.md;
REVIEW_PACKET_2026-09-30_first_cycle.txt; calibration/LEDGER.md (rows 1-7; rows
8-12 only restate K1-K6 and are excluded); hecate/programs/{PROBE_ROUND1-3,
PASS4_ROUND1-2}_REPORT.json (no *REPORT*.md exists under hecate/programs);
hecate/autopsy/AUTOPSY.md; harvest_w2/LEDGER.md Q1-Q14 (Q15-Q22 were appended
during the audit and are NOT covered).
Coverage: every numeric claim in these files was checked. A table row or a
tuple such as "111/243/109/64" counts as one claim per number group.
Excluded as identifiers, not claims: commit SHAs, comms message ids,
timestamps and file names. Not checked (about 3%): packet ">= 5 seeds"
(per-world seed counts), journal "Backlog 24 rows" and "BACKLOG 5 rows".

## Summary counts (242 claims)

    MATCH ............................ 196
    STALE (superseded, not annotated)   14   (all from K1, K3 or K4)
    MISMATCH ............................ 5   (none changes a verdict)
    UNSOURCEABLE ....................... 10
    ANNOTATED (wrong/stale, but the file
      already carries the correction)     8   (K13, K14, LEDGER Q5-ANNOTATION)
    TRANSCRIBED-ONLY .................... 9   (match a committed analysis doc;
                                               not recomputed from rows, because
                                               the aggregation code is uncommitted)

Headline numbers that recompute exactly (selection): corpus 6,939 / 95 /
6,661 / 385 / 6,276 / 2,861 / 6,651 / 5,918 / 5,727, FEP 742, Graph Theory 77,
fields 20, mechanism classes 38/28/15/14, sha d78f9d66...313885; 16 triples,
48 concepts, 4 S5_random; 111 interpretations / 243 mechanisms / 109 lenses /
64 v1 worlds (+16 v2 = 80); index 607 nodes at 00c99410b; 13 cheat controls;
27 tests at fefb095b2 (1+13+1+5+3+4); gate 8/8, 0/4, 2/2; round outcome
tables and core-minutes 16.86 / 10.83 / 3.83 / 0.29 / 0.73, total 32.55;
meta v1 class counts, familiar fractions (P 0.1403 = mean of unit fractions;
P has 79 items), sign tests 8/8, 8/8, 5/8, M2 80/80 and 78/80, 0 of 399
UNFAMILIAR; Pass 4 values 0.74355 vs 0.7437, 0/20 strata, OR 0.443, 1278 = 1278
seed for seed, ALT 0.601/0.856, r=0.2 LLE -0.63 and 0/10; round-3 controls
reproduced 8/8; 056d W4 0.823 (mean of 0.975, 0.876, 0.618) vs 0.618;
alien 320 calls, 28/32, 20/20, RULE 19/30, COHERENT 24/30, pairs 23/30,
FAMILIAR 16/32, prose 0.914->0.778 vs 0.994->0.994; gpt-oss 29/100 at 061d5cba8
and 30/100 at ce1eb65b1; R1 28/4/0, Wilson upper 0.107; flow 243 -> 58 -> 38
-> 6 -> 0 and the by-form admission ratios; Q5 median 0.252 and Spearman 0.421;
Q7 622 rows with 0 inner-object parses; Q9 50/109; Q10 0.833 vs 0.395, 0.481
vs 0.481, 0.05/12; Q13 4/22 vs 53/71 at zero masks, and [X]/item T 5.09 vs
S 1.76; Q14 79.3% of e106 W5 treatment blocks at the cap.

## STALE (true when written; superseded by a committed K-item; file not annotated)

S1  STATUS.md:10 "PARK 15, PROBING 1". K4 (and K13): now PARK 14, PROBING 1,
    SPECULATIVE 1. Recomputed from 16 program.json currentVerdict fields.
S2  STATUS.md:12 "Pass 3 v1 produced untestable worlds (12 of 29)". K4: 13 of
    29 (r1 IF 3 + NB 3; r2 SU 7).
S3  journal/2026-09-29.md:69-70 "b15a475b8 instruments (... gravity detector
    v1 + 14 controls ...)". K3: the controls were never in that commit.
S4  journal/2026-09-29.md:109 "Round 2: 0 SIGNAL, 7 NULL, 6 SPEC_UNATTAINABLE".
    K4: 6 NULL, 7 SPEC_UNATTAINABLE.
S5  journal/2026-09-29.md:110 "PARK 11, SPECULATIVE 4, PROBING 1" (state after
    round 2 and Pass 4 r1). K4: PARK 10, SPECULATIVE 5, PROBING 1.
S6  journal/2026-09-29.md:116 the inline CORRECTION "the count is 12 of 29".
    Superseded again by K4: 13 of 29. The annotation itself now needs a note.
S7  journal/2026-09-29.md:141 "(rounds 1-2: 12 of 29)". K4: 13 of 29.
S8  journal/2026-09-29.md:145-146 "my ORIG prediction was wrong (ledger row
    4)". K1: the prediction held.
S9  journal/2026-09-29.md:147 "End state: PARK 15, PROBING 1". K4: PARK 14,
    PROBING 1, SPECULATIVE 1.
S10 journal/2026-09-30.md:42 (restart handoff) "PARK 15, PROBING 1". As S1.
S11 REVIEW_PACKET:95 table row "Probe round 2 ... NULL 7 ... SU 6". K4: NULL 6,
    SU 7. (Its source, PROBE_ROUND2_REPORT.json, is annotated; the packet is not.)
S12 REVIEW_PACKET:102 "Program state (16): PARK 15 PROBING 1". As S1.
S13 REVIEW_PACKET:166-167 "a wrong ORIG prediction (ledger row 4)". K1: it was
    not wrong.
S14 calibration/LEDGER.md:12 (row 3) "12 of 29 (round 1 IF 3 + NB 3; round 2
    SU 6)". K4: 13 (round 2 SU 7). Row 21 records K4 but does not annotate
    row 3's count.
Note: the K4 claims also feed Q5/Q9-type denominators, and those still hold:
37 probed worlds and 5 SIGNAL are unchanged by K4.

## MISMATCH

M1  journal/2026-09-29.md:163 "no false noise/incoherence on aliens", and
    journal/2026-09-30.md:49 "no false-noise on aliens".
    Source: hecate/alien/runs/claude/RESULTS.json summary.confusion and
    failure_taxonomy. Recomputed: true for the 32 standard aliens (group A:
    t1 RULE 32/32; coherence 31 COHERENT + 1 UNCLEAR, 0 INCOHERENT). This is
    H2's group. It is not true for all aliens: adversarial alien SYS-41174
    (answer_key adversarial=true) got t1 RANDOM, so AADV is RULE 7, RANDOM 1,
    and the pilot's own taxonomy tags it FALSE_NOISE. Fix: say "standard
    aliens". Counted as 2 MISMATCH (one per file).
M2  REVIEW_PACKET:84-85 "ADDS_VALUE at >= 7/8 (p <= 0.035)". The PREREG
    (meta_experiment_v1 PREREG:82-83) has the same text. Exact one-sided sign
    test at 7/8 = 9/256 = 0.03516, which is > 0.035. Cosmetic: the frozen rule is
    the count (>= 7 of 8), and the observed 8/8 gives p = 0.0039 either way.
M3  harvest_w2/LEDGER.md:10 (Q2) "35 stand, 2 change, 4 contested" adds to 41 of
    the "42 world evaluators". Source: AUDIT_B_world_evaluators.md:79-86:
    35 same + 1 class change + 1 attack-result change + 4 indeterminate + 1
    "same class with a fragile path" (ae38/W3) = 42. The ledger drops the
    fragile item.
M4  harvest_w2/LEDGER.md:21 (Q13) "damage real but light (1-2% words ...)".
    Source: INV_G_scrubber_damage.md:95 and the detect_rows_v1 [X] counts.
    Words masked per arm: T 1.89%, P 1.41%, S 0.64%, O 0.85%, G 0.71%. Only T
    and P fall in 1-2%; the single-concept arms are under 1%. This does not
    change the conclusion ("light"); the range is wrong.

## UNSOURCEABLE (no committed rows support the number)

U1  journal/2026-09-29.md:31-33 "93 new (... through #988), 0 queued". The
    comms bus is not in the repo.
U2  journal/2026-09-29.md:79 "8/16 generators ran a read-only git status".
    Generator transcripts were not committed.
U3  journal/2026-09-29.md:92 "CPU load 5% at launch". No load record.
U4  journal/2026-09-29.md:124 "M1 pending on the detector (83/400 at this
    entry)". A progress snapshot; detect_rows_v1 holds only the final 400.
U5  journal/2026-09-29.md:165 "gpt-oss ... (200k tokens/day cap)". A provider
    limit with no committed record. The 29/100 count matches.
U6  journal/2026-09-30.md:54 "HECATE-SPEND (optional < $5 paid tier)". Also
    in WORK_STATE.json:60 as "est. < $5". No committed derivation.
U7  harvest_w2/LEDGER.md:17 (Q9) "10/109 names contain a stock-discipline
    word". Neither the word list nor the script is committed.
U8  harvest_w2/LEDGER.md:17 (Q9) "Jaccard ... (mean 0.014)". The tokenizer is
    not committed. A re-run (lowercase alpha tokens >= 3 chars over
    observables + transformation, 5,568 cross-program pairs) gives mean 0.031
    and max 0.241. The companion claim "0 pairs >= 0.35" is reproduced and
    counted as MATCH.
U9  harvest_w2/LEDGER.md:22 (Q14) "the spec-named simpler alternative scores
    ... ARI 1.0" (5516 W6). This is the tau = 1 knockout [A2], which
    INV_J_v2_clause_reachability.md:121 ran in the scratchpad only. The
    committed analogue (Pass 4 ALT non-chaotic carriers, ARI >= 0.8 in 10/10
    seeds per K1) supports "non-discriminating" but not this exact
    simpler-alternative number. The committed field
    simpler_alternative for M12 ("correlation or MI clustering") scores mean
    ARI -0.11 in PASS4_OUTCOME R stats, so the sentence must name tau = 1
    rather than the field.
U10 harvest_w2/LEDGER.md:22 (Q14) "e106 W5/W6 setup-decided (... 97% failing
    epochs)". The W6 figure comes from scratch auditor run [A4]
    (INV_J:206-208); e106 W6 was never probed and has no committed rows for
    it. The W5 79% is reproduced (11,892/15,000 = 0.793) and counted as MATCH.

## ANNOTATED (wrong or stale, but the file already carries the correction)

A1-A5 hecate/autopsy/AUTOPSY.md:29-37 "read validly 38", "12 untestable",
    "19 NULL", "programs PARK 15", "12/37 probed worlds could not be read".
    Annotated by the K14 banner (lines 3-8): 36, 13, 18, PARK 14 + SPEC 1,
    13/37.
A6-A7 hecate/programs/PROBE_ROUND2_REPORT.json:4-9 counts (NULL 7, SU 6) and
    verdicts (PARK 9, SPEC 4). Annotated at :195-200 (K4/K13: 6/7/8/5).
A8  harvest_w2/LEDGER.md:13 (Q5) "ALL 5 SIGNALs are the cheapest worlds".
    Recomputed: false. The two cheapest valid worlds are NULL: 2a8a W4 at
    0.0060 and 47f4 W1 at 0.0094 core-min, from the round reports and
    OUTCOME.json. Also "MWU p = 0.006 (claimed cost p = 0.085)" are ONE-SIDED
    values (two-sided 0.0122 and 0.1695; n = 5 SIGNAL vs 20 valid). Both are
    now annotated at LEDGER.md:28 (Q5-ANNOTATION, from INV_N), which was
    committed while this audit ran. The annotation agrees with this
    recomputation.

## TRANSCRIBED-ONLY (match the committed analysis document; not recomputed)

Q12 (INV_E) pooled 0.50 vs oracle 0.58; uncovered RF 0.99/0.81 vs 0.59/0.53;
poly maps 1.00 vs 0.05; vm_long 0.53 vs 0.18. These match the INV_E tables
(:69-82, :132-143). The committed INV_E script produces per-component records
only. Its aggregation, and the table snippets it relies on, are not committed,
so these were not re-derived. (88% = 28/32 is a MATCH.)
Q13 (INV_G) 73% acronym collateral, word-overlap matcher 145/160, v2 0/400
leaks, 136 v1 flags. These match INV_G (:68, :171-172, :220). Not re-run,
because the matcher code is in INV_G's scratch.
Q14 (INV_J) the category counts 4/5/3/3/1. They match INV_J's table and sum to
16. Not re-derived, because they are judgement classes.

## Notes (MATCH, with a caveat worth recording)

- REVIEW_PACKET:85-86 "M2: 36/80 correct vs chance 0.25" is the PREREG's
  pass threshold (meta v1 PREREG:93, accuracy >= 0.45 = 36 of 80), not a
  result. It reads like a result. The results are 80/80 and 78/80 (line 117).
- REVIEW_PACKET:137-138 "resistance step exactly at floor((d-1)/2)+1 for d =
  3, 5, 7". The step location is exact, but the step height is partial at
  d = 5 (k=3 rate 0.882) and at d = 7 (k=4 rate 0.589 in R, 0.6025 in ALT).
  PASS4_OUTCOME anomalies already say "partial".
- LEDGER Q6 quotes 71b6's simpler_alternative as "fixed level reasoning". The
  field says "fixed level-2 reasoning". Fixed L2 ties the treatment exactly
  (0.7437 = 0.7437), so the match is stronger than the ledger's "fixed-L1
  tie".
- LEDGER Q7 "every reply began with a top-level object". 62 of 622 replies
  open with a ``` fence, and 1 detector reply (the failed call) starts with
  text. The substantive claim holds: in every parsed reply the outer object
  equals the stored parse, so there are 0 inner-object parses.
- journal/2026-09-30.md:33 "gptoss blind 30/100 valid ... gemini 0/100" was
  correct at ce1eb65b1. Later progress commits (47/100, then 48/100 ok at
  931784f94) are progress, not corrections, so this is not STALE.
- LEDGER Q13 "12 regression cases" counts the cases_preserve list
  (scrub_v2_proposal.py:177-190). The file also has 10 mask cases and 2
  coinage cases.

## Method pointers (for re-running)

Program states: hecate/programs/HT-*/program.json currentVerdict.
Q5 rows: world = (round report core_minutes, program.json experiment
cost_estimate). Parse the text estimates by their "N CPU core-minute(s)"
number. Valid = NULL or CONFOUNDED. scipy mannwhitneyu with 'less' and
'two-sided'.
Q9/Q10: experiments[].lens_ids / mechanism_ids. Probed = the 37 (triplicate,
world) pairs in the three round reports. Position = mechanism id number <= 3.
Q13: count "[X]" in detect_rows_v1 blind_text, and take FAMILIAR from parsed
at zero masks, multi = T/P arms.
Corpus: agents/hephaestus/ledger.jsonl, agents/nous/src/concepts.py
CONCEPTS, and hecate/corpus/CORPUS_RECEIPT.json.
