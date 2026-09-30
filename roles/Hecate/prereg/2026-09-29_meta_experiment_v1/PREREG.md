# PREREG -- Hecate FIRST META-EXPERIMENT, v1 (HECATE-10)

Frozen: 2026-09-30Z, in the same commit as the first selection, BEFORE
any pass content or any arm output exists. Author: Hecate[m1-dd0c3882].
Charter section: FIRST META-EXPERIMENT.

## Question v1 can answer (and the one it cannot)

v1 asks: given the same generator, template and budget, do concept
TRIPLICATES yield candidate mechanisms that are (a) less compressible
into familiar known machinery and (b) actually shaped by their labels,
compared with single concepts, pairs, a single-discipline research
prompt, and a concept-free brainstorm?

v1 does NOT answer whether triplicate mechanisms survive falsification
more often. That needs every arm taken through Pass 3-4, which is v2 and
is preregistered separately after v1 reports. Unfamiliar is not useful;
a low-gravity result is not a novelty claim (Hephaestus 2.0 design).

## Units and arms

Units: 8 of the 16 frozen triplicates -- the first 8 ids of
random.Random(20260929 + 100).shuffle(sorted(FROZEN ids)). Within a
unit, concept order A, B, C = random.Random(20260929 + 200 + i).shuffle
of its three names (i = unit index). Arms per unit:

    T  triplicate        A x B x C
    P  pair              A x B
    S  single            A
    O  ordinary prompt   "a researcher in <field of A>" -- no concept names
    G  generic           no concepts, no field

40 generations. Every generation: generator model claude-sonnet-5
(fresh context, no tools, no search), one frozen template differing
only in the seed paragraph, output exactly 10 candidate mechanisms in
the Pass 1 schema (form; the charter's eight questions; a one-paragraph
minimal world with its null twin). Template text and its sha256 are
committed under hecate/meta/ before the first arm runs; if the template
must change after any arm has run, all arms are regenerated.

The generator is deliberately NOT the model that writes the Pass 0-2
programs and NOT the scorer, so no instance grades its own output.

## Measures

M1 (primary) FAMILIAR FRACTION. The fraction of a unit-arm's 10
mechanisms that the gravity detector (HECATE-13) classifies FAMILIAR.
The detector sees only a blinded description: concept names, fields,
invented names and novelty words removed by a deterministic scrubber
(hecate/meta/scrub.py, committed with the template), then a check that
none of the 95 dictionary names or 20 field names survive. Detector
model: claude-opus-5-5, fresh context per item, order randomised
across arms and units so arm identity is not inferable from position.

  Detector calibration gate (must pass before M1 is read): at least 12
  controls per the Hephaestus 2.0 design. Disguised familiar mechanisms
  (renamed PID, TCP congestion control, Hebbian, Kalman,
  reaction-diffusion, stigmergy, finite-state control, autocatalysis)
  must be classified FAMILIAR in >= 7 of 8 with the correct family
  named; incoherent/nonsense controls must be classified FAMILIAR in
  <= 1 of 4. If the gate fails, M1 is INDETERMINATE (instrument
  uninterpretable) and that failure is the reported result.

M2 (primary) LABEL DEPENDENCE, arms T and P only. A blinded matcher
(claude-opus-5-5, fresh context) sees one mechanism with its concept
names and fields removed by the same scrubber, and four candidate concept
sets (the true one and three drawn from the other 15 frozen triples,
seeded), and picks the source. Chance = 0.25. 80 T items, 80 P items.

M3 (secondary) STRUCTURAL SPECIFICITY, deterministic code on the
structured fields: state named (what_exists lists >= 2 items), a change
rule stated, an intervention stated in the world, a comparator in the
distinguishing observable (baseline / null / control / versus / than /
compared). Reported per arm; no decision rule.

M4 (secondary) FAMILY SPREAD: number of distinct nearest-known families
the detector names across a unit-arm's 10. Reported; no decision rule.

## Decision rules (frozen; ties count as NOT lower)

M1, for each comparison arm X in {S, P, O} separately:
  ADDS_VALUE_vs_X   T's familiar fraction < X's in >= 7 of 8 units
                    (one-sided sign test p <= 0.035)
  NO_ADDED_VALUE_vs_X  T < X in <= 4 of 8 units
  INDETERMINATE     otherwise (5 or 6 of 8)
G is reported against T by the same rule, but G is one concept-free
draw per unit, not matched, so its row is descriptive.
Overall "triplicates reduce familiarity" only if ADDS_VALUE vs S, P
and O all hold; "they do not" if NO_ADDED_VALUE vs O holds (the charter's
conventional single-discipline baseline); else INDETERMINATE.

M2:
  LABELS_SHAPE_OUTPUT   accuracy >= 0.45 (36 of 80; binomial p < 0.001 vs 0.25)
  LABELS_DECORATIVE     accuracy <= 0.32 (<= 25 of 80)
  INDETERMINATE         otherwise
T and P reported separately; T below P is itself informative (a third
concept diluting rather than shaping).

## Eligibility and attainable range

8 paired units: the sign test's smallest attainable one-sided p is
1/256, so the M1 rule is attainable; its power is for large effects
only, and INDETERMINATE is a likely and legitimate outcome, stated in
advance. M2 has 80 items per arm; both thresholds are attainable.
Everything runs inside the MWO-0004 R2 envelope (no local compute to
speak of; model calls are ordinary session use).

## Known contamination, declared

The author of this rubric chose the 16 and will write Pass 0-2 for
them before the arms run, so it knows the triples. Mitigations: the
arms use a different generator; the scorer is blind to arm and unit;
the thresholds are frozen here. Residual risk: the template wording is
the author's and could favour triples; the O and G arms use the same
wording, which bounds that.

## Outputs

hecate/meta/{template, scrub.py, arms/*.jsonl, detector/*, matcher/*,
REPORT.md}. REPORT.md states each rule's outcome with its rows, and
recommends "not worth continuing" if M1 is NO_ADDED_VALUE vs O and M2 is
LABELS_DECORATIVE.
