# Alien-lawful structure assay -- pilot report (Family A complete; B, C incomplete)

> CORRECTIONS 2026-10-01 (roles/Hecate/harvest_w2/CORRECTIONS_2026-10-01.md; text below is unchanged):
> K2 "affine (0.44) beats Claude (0.33)" is KILLED -- unlike subsets/metrics; like-for-like Claude 0.51 vs affine 0.49.
> K7 the sandbox rejected 4 correct-style programs (local lambdas, str join/split); headline 28/32 unchanged (sensitivity only).
> K8 the "textbook standard map" story is contradicted by the code; both FALSE_COLLAPSE cases are classifier artefacts (H5: 0/32 genuine).
> K9 families ran concurrently, a deviation from PREREG s10. ATTACK_C revises: alien learning tracks how much of the rule table the
> observations cover; "over-attribution" is low-confidence literal RULE; the prose effect is mostly one map system.


PREREG: roles/Hecate/prereg/2026-09-30_alien_lawful_assay/PREREG.md (frozen 1fed85d95,
before any model saw a pilot system). Scores come only from the frozen scorer
(hecate/alien/score.py, analyze.py) against the simulator and exhaustive checks.
Numbers: hecate/alien/runs/<model>/RESULTS.json. Raw calls: runs/<model>/*.jsonl.
Qualitative explanations were read only after scoring (directive step 11).

## Family A: claude-opus-5-5 (isolated `claude -p`), 320/320 calls parsed

Behaviour (group means):

    group        n  T1 RULE  T2 exact  T2 comp  trivial bar  code held-out exact  learned
    K           20    1.00     0.98      1.00       0.57             0.98            1.00
    A (std)     32    1.00     0.80      0.93       0.52             0.80            0.88
    A (adv)      8    0.88     0.20      0.33       0.25             0.21            0.25
    N CONJ       7    0.71     0.08      0.28       0.32             0.08            0.00
    N DSCRAMBLE 11    0.45     0.11      0.50       0.46             0.09            0.09
    N SCRAMBLE   4    0.75     0.00      0.32       0.31             0.04            0.00
    N SEDUCTIVE  8    0.75     0.01      0.27       0.35             0.05            0.00
    N DESTROY   10    1.00     0.52      0.79       0.47             0.56            0.60

Discrimination (AUC vs the 30 incompressible nulls): T1 score K 1.00, A 0.98,
A incl. adversarial 0.94; behavioural score K 1.00, A 0.97. Adversarial vs
seductive: T1 0.69, behavioural 0.80. Pairs (alien vs its null): CONJ 7/7,
DSCRAMBLE 10/11, SCRAMBLE 2/4, SEDUCTIVE 4/8, DESTROY 5/10; incompressible
23/30 = 0.767.

Invariants (every claim checked on the full state space): standard aliens 26
TRUE, 0 FALSE (78 untestable prose); planted recall 17/32 = 0.53. Known: 38
TRUE, 2 FALSE, 2 TRIVIAL. Adversarial: 0 testable claims, recall 0/6.

Labels (behavioural outputs, not truth): standard aliens RULE 32/32, COHERENT
31/32 (1 UNCLEAR), FAMILIAR yes 16/32. Incompressible nulls RULE 19/30,
COHERENT 24/30; exactly 1 of 100 systems was ever called INCOHERENT.

Preregistered decisions:

    H1 t1 (K-vs-noise minus A-vs-noise >= .10) ...... INDETERMINATE (+0.019)
    H1 behavioural ................................... INDETERMINATE (+0.026)
    H2 (A false noise/incoherence elevated) .......... NOT_SUPPORTED (0 vs 0)
    H3 (active closes the gap) ....................... INDETERMINATE
         (A learned 0.8 -> 0.9 on the 10-alien subset; noise 0/6 under active)
    H4 (revealed rule closes the gap) ................ INDETERMINATE
         (with the rule: coherent 100%, T2 exact 1.00 for K, A and DESTROY)
    H5 (false familiar collapse elevated on A) ....... INDETERMINATE (2/32 vs 0/20)
    H6 (learnable yet called RANDOM/INCOHERENT) ...... NOT_SUPPORTED (0 strict, 1 soft)
    DETECTOR ......................................... NOVELTY_DETECTOR_NOT_VALIDATED
         (T1 AUC 0.98, CI low 0.95 -- passes; pair accuracy 0.767 < 0.80 -- fails,
          entirely on adversarial/seductive and scramble pairs)

Failure taxonomy (11 alien misses; primary tag): RIGHT_STRUCTURE_WRONG_MECHANISM
5, PARTIAL_STRUCTURE 3, FALSE_NOISE 1, EXPLANATORY_WITHOUT_PREDICTION 1,
PREDICTIVE_WITHOUT_EXPLANATION 1; secondary RECOVERED_AFTER_RULE_REVEAL 2,
RECOVERED_AFTER_EXPERIMENTATION 1.

Representation ablation (T2 component accuracy, 10 systems per group, descriptive):
aliens tuple 0.91 vs prose 0.78; known 0.99 vs 0.99. Prose hurt the unfamiliar
systems only.

## What the rows say (and what they do not)

1. The hypothesised failure did not appear for Claude on standard aliens. It
   did not pull lawful unfamiliar systems toward noise or incoherence (0 of 32),
   and it learned them almost as well as named mechanisms (88% vs 100%),
   writing executable rules that generalise to held-out states (0.80 exact).
2. The failure that did appear runs the other way: OVER-ATTRIBUTION. It called
   19/30 incompressible nulls RULE and 24/30 COHERENT. Read after scoring, its
   evidence is accurate: it names exactly the regularities each null was built
   to preserve (+-1 steps, per-position increment distributions, fixed points
   and 2-cycles), and its predictions on those systems stay at or below the
   trivial bar. It saw regularity, found no law, and still said RULE. The T1
   question as written ("a stable underlying rule?") does not separate
   "regularity" from "compact predictive law" -- an instrument defect of mine.
   Its confidence and its predictions discriminate (AUC 0.98); its labels do not.
3. FAMILIAR was given to half the standard aliens, but the names are
   formalisms ("string rewriting / semi-Thue system", "register machine",
   "cellular automaton on a graph", "standard map") -- correct at the
   construction-class level, which our own generator notes record. The frozen
   analogy classifier credits CORRECT_ANALOGY when the model names the
   formalism and then implements its own inferred rule; that category is
   partly a formalism-naming score. The two FALSE_COLLAPSE cases are
   informative: for a shear map it described the structure correctly, then,
   asked to implement "the standard map", wrote the textbook map (18%
   component accuracy) while its own inferred rule was right. The collapse is
   in the analogy, not the reasoning.
4. Structure hidden by a linear change of coordinates defeats it (learned 2/8)
   -- and defeats the local baselines too; a plain affine-search baseline
   (0.44) beats Claude (0.33) there. Reading guide Outcome E for this subset:
   hard, not shown to be LLM-specific.
5. Reading-guide classification for Family A: closest to OUTCOME A on
   standard aliens (behavioural discrimination strong), with a verbal
   over-attribution failure that the guide did not anticipate, and OUTCOME E
   on the adversarial subset. Not B, not C (lawful systems were not called
   incoherent), not D.

## Relation to Hecate meta v1 (not reinterpreting its rows)

Directive question: was the detector category valid? For this model family,
its categorical labels are not: FAMILIAR is applied at the level of
formalism (to half of operationally alien systems), and COHERENT is applied to
most incompressible noise. A zero-UNFAMILIAR count from such a labeller is
uninformative about mechanism novelty. With the detector formally
NOVELTY_DETECTOR_NOT_VALIDATED, Hecate novelty conclusions must rest on
behavioural and predictive tests (which did discriminate here), never on LLM
classification alone.

## Families B and C: incomplete (instrument and quota failures)

- gpt-oss-120b (Groq free tier): 29/100 blind calls before a 200k token/day
  limit. Descriptive only: verdict UNCERTAIN on 21/29; it abstained ("?" /
  "unknown" predictions) on about 10/29 systems, which the frozen scorer counts
  as wrong. On its subset: aliens learned 1/8, known 3/5; T1 AUC K-vs-noise
  0.80, A-vs-noise 0.56 -- a different failure mode (abstention), possibly the
  H1 pattern; too few rows to test.
- gemini-3.6-flash (free tier): daily request quota exhausted after 10 calls;
  every successful reply was TRUNCATED (~1.5k chars; thinking likely consumed
  the output budget) and the shared JSON extractor then accepted an inner
  object as the whole reply. No valid Gemini reading exists. Fix before any
  rerun: require the task's top-level keys, raise the output budget.
- Completing B and C needs either ~5 days of free-tier trickle or a paid tier
  (estimated well under $5 in tokens). That is a spending decision for James.

## Limits

One run per system per task; one model version per family; Claude's harness
is `claude -p` (not a raw API call); 100 systems; the reveal/active subsets are
small (H3, H4 underpowered by design); the T1 wording conflates regularity and
law; the analogy classifier partly scores formalism naming.
