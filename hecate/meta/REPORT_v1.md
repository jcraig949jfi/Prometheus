# Meta-experiment v1 -- report

PREREG: roles/Hecate/prereg/2026-09-29_meta_experiment_v1/PREREG.md (e0bd2e312).
Analysis code frozen before any detector or matcher row was read:
hecate/meta/analyze.py (65e0fcf80). Numbers: hecate/meta/RESULTS_v1.json.
Rows: hecate/meta/arms/arms_v1.jsonl (40 unit-arms, 400 mechanisms),
hecate/meta/detector/detect_rows_v1.jsonl, hecate/meta/matcher/match_rows_v1.jsonl.
Generator claude-sonnet-5; detector and matcher claude-opus-5-5; all calls
isolated (hecate/llm.py). Detector calibration gate PASS
(hecate/gravity/CALIBRATION_v1.json).

## Preregistered outcomes

M1 familiar fraction (detector FAMILIAR / items), mean over 8 units:
T 0.088, P 0.140, S 0.775, O 0.838, G 0.850.

    vs S  T lower in 8/8 units  p = 0.0039  ADDS_VALUE_vs_S
    vs P  T lower in 5/8 units  p = 0.363   INDETERMINATE
    vs O  T lower in 8/8 units  p = 0.0039  ADDS_VALUE_vs_O
    vs G  T lower in 8/8 units  (descriptive only)
    OVERALL (needs S, P and O): INDETERMINATE

M2 label dependence (4-way blinded matcher, chance 0.25):
T 80/80 = 1.000, P 78/80 = 0.975 -> LABELS_SHAPE_OUTPUT for both.

The "not worth continuing" trigger (M1 NO_ADDED_VALUE vs O AND M2
LABELS_DECORATIVE) did not fire.

## What the rows show beyond the verdicts (descriptive; no new verdict)

Detector classifications, 399 scored items (1 detector call failed, unscored):

    arm   FAMILIAR  COMPOSITE  UNFAMILIAR  INCOHERENT
    T         7        73          0           0
    P        11        68          0           0
    S        62        18          0           0
    O        67        11          0           2
    G        68        12          0           0

1. Zero mechanisms in any arm were UNFAMILIAR. The entire M1 "gain" of
   T and P over S, O and G is a shift from ONE known mechanism to a
   COMBINATION of known mechanisms. Prompting with several concepts
   produces composites of known machinery, close to by construction.
2. T and P are indistinguishable on M1 (5/8; means 0.088 vs 0.140). On
   this measure the third concept adds nothing detectable.
3. M2 is saturated: concept vocabulary survives name-scrubbing (e.g.
   avalanches, oscillators, primes) and the decoys come from distant
   triples, so matching succeeds on vocabulary. It shows outputs carry
   their concepts' vocabulary, not that concepts shape causal structure.
4. M4 (distinct nearest families per unit-arm) is 10/10 almost
   everywhere: saturated, uninformative.
5. M3 (deterministic structure): T has the most comparators in its
   distinguishing observable (0.75 vs 0.44-0.60) and the fewest named
   state variables (0.75 vs 0.875-1.0).

## Instrument problems found

- The detector called both known COMPOSITE calibration controls
  FAMILIAR, yet calls most arm outputs COMPOSITE. Its FAMILIAR/COMPOSITE
  boundary is unstable, and M1 counts only FAMILIAR; so M1 partly
  measures "how many mechanisms a description mentions".
- The calibration set had no coherent-but-unfamiliar control, so the
  detector's ability to say UNFAMILIAR at all is untested. Zero
  UNFAMILIAR calls in 399 items may be a property of the detector, not
  of the arms.
- Same generator family for all arms, single run per unit-arm, 8 units.

## Answer to the charter's meta question, as of v1

Does triplicate collision generate candidates that conventional
single-discipline search would not? v1 finds: multi-concept prompts
(pairs and triplicates alike) yield composites of known mechanisms
where single-concept and single-discipline prompts yield single known
mechanisms; nothing in any arm was judged unfamiliar; triplicates were
not distinguishable from pairs. Together with the probe results (no
candidate survived first falsification; see
hecate/programs/PASS4_ROUND1_REPORT.json), there is NO evidence yet
that triplicates add value beyond pairs. This is not evidence that they
cannot: the rulers were weak where it matters (no unfamiliar control,
saturated M2).

## v2 (proposed, to be preregistered separately)

- Calibration must include coherent-but-unfamiliar controls (e.g.
  hand-built rules with no standard name) and the detector must be
  able to call them UNFAMILIAR, or M1 stays uninterpretable at the top.
- Score COMPOSITE and FAMILIAR together as "compressible into known
  machinery" and report UNFAMILIAR separately.
- M2 decoys drawn from triples sharing a field or mechanism class with
  the true set.
- Usefulness: take the top world from each arm through Pass 3 v2 and a
  probe, so the arms are compared on falsifiable output, not description.
