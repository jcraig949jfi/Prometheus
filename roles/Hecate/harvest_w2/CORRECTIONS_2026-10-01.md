# Hecate corrections, 2026-10-01 (Wave 2) -- each verified by Hecate from rows

Sources: Harmonia audit roles/Harmonia/audits/EVIDENCE_AUDIT_2026-09-30.md
(comms #1037); Hecate W2 audits roles/Hecate/harvest_w2/AUDIT_B_world_evaluators.md,
ATTACK_C_alien_headlines.md, ATTACK_D_autopsy_R1.md. Originals stay
visible; corrections are annotations.

K1 HT-55162c0ac0 W6 Pass 4 ORIG: recorded "fired: false" -> FIRED in substance.
   Verified: ALT_TREATMENT rows at r = 0.65 (Lyapunov -0.956..-0.853) and
   r = 0.8 (-0.057..-0.034): 10/10 seeds LLE < 0 and 10/10 ARI >= 0.8, non-
   degenerate trajectories. Caveat: those levels ran at noise sigma 0.05;
   the original world used sigma 0. Program stays PARK (ALT failed); prior
   art KNOWN_ANALOGUE_FOUND (perturbation-response network inference).
   Calibration ledger row 4 ("my ORIG prediction was wrong") is itself
   wrong: the prediction held; the attacker ran ORIG at one carrier only.
K2 REPORT_pilot "affine baseline (0.44) beats Claude (0.33)": KILLED.
   Verified: unlike subsets and metrics. Same 5 adversarial systems:
   Claude T2 comp 0.512 vs affine T2 comp 0.487; Claude code eval comp 0.513
   vs affine eval comp 0.436. The affine baseline did not run on the 3 map
   systems (silently absent from its group mean).
K3 hecate/gravity/calibration_v1.json never held the 14 detector controls:
   on this case-insensitive filesystem the gate writer's CALIBRATION_v1.json
   overwrote it before commit b15a475b8, whose message claimed "+ 14
   controls". Restored as hecate/gravity/controls_v1.json; verified 14/14
   restored texts scrub to the recorded blind texts, and the gate re-derived
   from calibration_rows_v1.jsonl equals the committed gate and table
   exactly. run.py now reads controls_v1.json and writes gate_v1.json;
   regression tests forbid case-colliding paths under hecate/.
K4 HT-a9e2ba7618 W3 (round 2): recorded NULL -> SPEC_UNATTAINABLE. Verified:
   osc - comp ARI max 0.000 over 50 PC and 50 treatment seeds (null twin
   exceeds it on 35/50): the pilot repair (KC = 1.6, above every clique's
   locking bound) made the deciding clause unattainable; the round-2 pilot
   checked only absolute ARI. Program PARK -> SPECULATIVE (one valid NULL,
   W4), by the round-2 consequence table.
K5 Novelty autopsy Part A "largest loss at admission; admission skewed by
   form": REVISED. Verified: 126/243 mechanisms never appear in any
   specified world; admission among those that do is 58/117. The by-form
   skew does not survive a permutation test (p ~ 0.18, ATTACK_D). The
   largest loss is at world SPECIFICATION.
K6 Novelty autopsy Part B input was not "exact rule text": the meta v1
   scrubber was applied and erased every rewrite rule ("YZ -> XW" -> "[X] ->
   [X]"). R1 still fires without the 8 rewrite aliens (0/24). R1 is a
   property of the definition on fully specified rules (FAMILIAR is literally
   correct at construction-class level), so it supports C6, not C4; it does
   not transfer to meta v1's prose inputs as argued. Meta v1's zero stays
   uninformative on better evidence: no item was ever labelled UNFAMILIAR at
   any prior_fit, and all 22 items with prior_fit <= 0.50 went COMPOSITE.
K7 Alien pilot sandbox rejected 4 Claude step programs (local lambda calls
   f, h; str join/split). Frozen scorer unchanged; sensitivity rescore with
   those allowed: 2 standard map aliens' code becomes eval exact 1.0 (both
   were already LEARNED via T2), 1 scramble null stays 0.0. Headline
   learned 28/32 unchanged; alien code-eval exact rises (reported as
   sensitivity only).
K8 REPORT_pilot, false-collapse story ("asked to implement the standard
   map, wrote the textbook map"): contradicted by the code (its own
   lookup-table shear; ATTACK_C item 6). Both FALSE_COLLAPSE cases are
   classifier artefacts; H5 reads 0/32 genuine collapses.
K9 Also from #1037 (minor, accepted): families ran concurrently, contrary
   to PREREG s10 ("A, then B, then C") -- recorded here as a protocol
   deviation; the Gemini RESULTS verdict now reads NOT_ELIGIBLE (missing
   inputs), Claude's verdict unchanged.

K10 Alien pilot descriptive counts (AUDIT_A F06, F10, F11; verified by re-run
   in the audit; frozen scorer and RESULTS.json unchanged, these are
   sensitivity readings): vector-valued conserved claims crashed the SCORER
   (set() on lists) and were filed UNTESTABLE -> A std TRUE 26 -> 30, planted
   recall 17/32 -> 18/32; K TRUE 38 -> 42. Two lambda-using programs (K7) ->
   alien code held-out exact 0.80 (n=30, 2 rows silently dropped) -> 0.81
   (n=32). Eval bar computed on 100 of the 200 scored states: behavioural
   AUC 0.974 -> 0.976. No decision changes.
K11 REPORT_pilot taxonomy label RIGHT_STRUCTURE_WRONG_MECHANISM (5 cases, the
   largest tag) tests nothing about structure: all 5 are adversarial aliens
   at or below the trivial bar with 0 TRUE claims -> read as "RULE claimed,
   no structure detected" (AUDIT_A F09). The second FALSE_COLLAPSE case
   (SYS-60800) is an unattainable threshold (bar 0.803 + 0.2 > 1), so H5's
   genuine count stays 0/32 as K8 says (AUDIT_A F07).

K12 Meta v1 M3 (descriptive, no decision rule; AUDIT_L F3, F4): "state named"
   missed three unit-arms that wrote what_exists as a comma-separated
   string -> T 0.75 -> 1.00, P 0.875 -> 1.00; REPORT_v1 "T has the fewest
   named state variables" is FALSE. The comparator check accepted "vs",
   not in the PREREG list -> S 0.4625 -> 0.400, P 0.600 -> 0.5625.

K13 Verdict derivation (AUDIT_M; all 16 verdicts re-derived from the governing
   consequence tables: none differs; final PARK 14, PROBING 1, SPECULATIVE 1;
   8 of 16 rest on one probed world). Record errors only: PROBE_ROUND2_REPORT
   counts are pre-K4 (now 6/7/8/5, annotated in the JSON, verified); 5516 and
   8a87 PARK reasons cite "Pass 4 round 1" for round 2; 71b6 PARK lacks the
   reason the rule requires (ALT NOT_ELIGIBLE twice, L2-L1 gap 0.0000, 0.0003
   < 0.02); a9e2 is SPECULATIVE with no later round scheduled (none may start
   under CWO-C); 5516's failed Pass-4 replication is a case the table does not
   cover (PARK stands on the failed ALT).

K14 Autopsy Part A was derived before K4 and never re-run (AUDIT_Z3 Z3-1;
   re-derived by unchanged flow.py into hecate/autopsy/FLOW_postK4.json,
   FLOW.json kept): mechanisms read validly 38 -> 36, worlds untestable as
   specified 12 -> 13, NULL 19 -> 18, SPEC_UNATTAINABLE 6 -> 7, PARK 15 ->
   14 + SPECULATIVE 1. Definition note (Z3-2): "admitted" includes 3
   NOT_BUILT worlds, contrary to flow.py's own "built" docstring; excluding
   them, admitted 58 -> 53, probed 37 -> 34, never tested 76% -> 78%. Of
   the 13 untestable worlds, 6 are build/instrument failures, not
   specification failures (Z3-3). Wilson bound, joins, Part B: clean.

K15 Prose claim audit (AUDIT_O: 242 numeric claims, 196 MATCH, 14 STALE, 5
   MISMATCH, 10 UNSOURCEABLE). Journals and the 09-30 review packet are
   records and stay unchanged; read them with K1/K3/K4/K14 (PARK 15 -> 14 +
   SPECULATIVE 1; untestable 12 -> 13; round-2 row 7/6 -> 6/7; "wrong ORIG
   prediction" -> K1; "+14 controls" -> K3). MISMATCH: "no false noise on
   aliens" (journal 09-29, 09-30) holds for the 32 STANDARD aliens only --
   adversarial SYS-41174 was called RANDOM (verified, conf 0.45); packet
   "p <= 0.035" is 9/256 = 0.0352; LEDGER Q2 tally sums to 41 of 42 (one
   "fragile" item dropped); LEDGER Q13 "1-2% words" is 0.6-1.9%.
   UNSOURCEABLE: Q14 "ARI 1.0"/"97%" (auditor scratch runs, not committed).
   STATUS.md (live state) rewritten 2026-10-01.

K16 Derived files that do not reproduce from their generators (test
   hecate/tests/test_derived_reproduce.py, pinned in KNOWN_NONREPRODUCING):
   gemini RESULTS.json (row SYS-10088 never scored in); HT-55162c0ac0 W3
   OUTCOME.json, HT-5b0b3ebb8d W4 OUTCOME.json and its pass4
   PASS4_OUTCOME.json (hand-appended anomalies/notes). Records kept.
K17 Erratum to K9 (REDTEAM_Y, verified): the committed gemini RESULTS.json
   still reads NOVELTY_DETECTOR_NOT_VALIDATED (all inputs None); only
   analyze.py was fixed to say NOT_ELIGIBLE, RESULTS was not re-run.
K18 HT-55162c0ac0 W6 Pass 4 "R reproduced: false" is wrong in substance
   (AUDIT_Z1 F1): code required |corr ARI| <= 0.1, so -0.111 (below chance)
   failed; round-3 S2 holds (1.11 >= 0.5). PARK stands on the failed ALT.
   Also Z1: 8a87 and 321a ORIG attacks decided by construction (round-2
   PREREG forbids such attacks); 71b6 ALT eligibility gap 0.02 unreachable
   (best of 42 variants 0.004). No verdict changes.

REDTEAM_Y on this file (read it with every APPLY recommendation): numbers
recompute, but the readings lean in Hecate's favour -- favourable fixes
were applied or recommended APPLY (K1, K4, C1, C5), unfavourable ones
ANNOTATE-ONLY (C2, H4, strict C6); K4's stated cause is false (the clause
was unreachable before the KC=1.6 repair) and K4 moved PARK -> SPECULATIVE
without a ruling; exact arithmetic flips only H3, toward SUPPORTED; C1's
reading would also flip 9744/W6, K4's 79e9/W1 and 47f4/W1, and C5's
H4 -> NOT_SUPPORTED. Hecate WITHDRAWS its APPLY recommendations in
RULING_REQUEST_C1_C8.md and asks that K4 be treated as contested too.

## Contested items -- NOT applied (recommendations; would change a frozen decision rule's outcome -> CWO-C s4 escalation class)

C1 HT-ae38c641b1 W5 (round 3): frozen spec says values between F1 and S1
   (0.15-0.40) are INCONCLUSIVE, "not a falsification"; the pass3_v2 PREREG
   classifies with round-1 classes (no INCONCLUSIVE), giving NULL; the
   program was PARKed on "two valid NULL readings". Recommendation: a ruling
   that a frozen spec's explicit INCONCLUSIVE band is not a valid NULL
   reading for consequence counting -> ae38 would return to SPECULATIVE.
   Owner: Aporia/operator ruling (changes a frozen rule's outcome).
C2 HT-321a8fd8e0 (Pass 4 r1): PROBING rests on an ALT fixed by counting
   (alt_pass = Kc > Km; majority vote K = 0 for any allocation). Correct
   under the round-1 PREREG (no counting rule); under round 2's rule the ALT
   is NOT_ELIGIBLE -> PARK. Recommendation: annotate PROBING as "degenerate
   ALT, prior art KNOWN_ANALOGUE_FOUND"; ruling needed to change to PARK.
C3 HT-79e904e13a W4 (round 1): entropy observable saturates by T ~ 6-9; the
   positive control never reaches the ceiling, so NULL is likely but not
   shown by an in-range control. Stays NULL; flagged INSTRUMENT-WEAK.
C4 HT-ae38c641b1 W4 (round 2): SPEC_UNATTAINABLE rests on an undefined-ratio
   aggregation reading; stays as recorded; flagged.
C5 Alien H3 (AUDIT_A F01; verified with exact fractions): recorded
   INDETERMINATE because 0.2 - 0.1 = 0.0999... in floats; under the PREREG s6
   text, (1 - 8/10) - (1 - 9/10) = 1/10 >= 0.10 -> SUPPORTED. The effect is
   ONE alien (SYS-19722) on a 10-alien subset. Recommendation: rule that the
   frozen text governs (SUPPORTED, reported as n=1 fragile).
C6 Alien detector verdict (AUDIT_A F03; verified: CONJ 7/7 + DSCRAMBLE 10/11
   + SCRAMBLE 2/4 = 19/22 = 0.864): the AUC leg uses standard aliens, the
   pair leg also includes the 8 adversarial-matched SEDUCTIVE pairs. The code
   follows PREREG s7 literally. Consistent standard-only -> VALIDATED;
   consistent all-aliens -> NOT_VALIDATED (AUC 0.940). Recorded verdict
   stands; ruling needed on which consistent set is primary.
C7 Alien H4 / H2 (AUDIT_A F02, F04): H4 code uses a binary rule instead of
   the s6 general rule (which gives NOT_SUPPORTED on a degenerate [0,0] CI);
   H2's NOT_SUPPORTED rests on a zero-variance bootstrap (Clopper-Pearson
   upper for 0/32 is 0.109 > 0.075 -> INDETERMINATE). Both stay as recorded.
   Design note (F05): with K at ceiling, H1/H2/H5 can never read
   NOT_SUPPORTED; their INDETERMINATE means "small positive, below
   threshold".
C8 Meta v1 M1 vs P (AUDIT_L F1; verified from rows): detector call u4-P-m8
   was refused and never retried; code divides P's unit 4 by 9 scored items
   (2/9 = 0.222 > T 2/10), literal "FAMILIAR / items" gives 2/10 = T ->
   tie -> NOT lower (PREREG ties rule) -> T lower in 4/8 (p 0.637) ->
   NO_ADDED_VALUE_vs_P (recorded INDETERMINATE, 5/8). Overall M1 unchanged
   (INDETERMINATE). Recommendation: rule on the denominator for a failed
   call; a single re-scoring of u4-P-m8 would be post-hoc data collection
   and also needs the ruling.
Note on K4 (applied): it enforces the frozen round-2 definition of
SPEC_UNATTAINABLE ("cannot be reached even by a construction that has the
effect by design") that the round-2 pilot failed to check; it is listed
here for Aporia/operator review all the same.
