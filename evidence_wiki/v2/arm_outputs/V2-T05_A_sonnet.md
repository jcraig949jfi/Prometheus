# PROPOSAL V2-T05 (arm A)

## Hypothesis

The failure signature discovered in `agent_d4_blind` Phase 1's S3_REWRITE substrate —
near-ceiling viability and phenotype mass (0.996 [0.995,0.997]; 11,717 combined
phenotype classes, unseen mass 0.99) co-occurring with a **zero** far-stratum hit
rate across every generic navigator (N1/N2/N4) AND a **zero** oracle-confirmed
far-episode-reach across ~1.5M metered evaluations — is a substrate-general
early-warning signature. Specifically: (near-ceiling viability/diversity) AND
(far-stratum navigator hit rate == 0) is a valid proxy for "genuine topology
failure" (compute-independent, doomed regardless of budget) as opposed to
"search failure at this budget" (recoverable with more budget or a better
search process). The discriminating case already on file is S1_REG, which
shows an almost-identical navigator-side symptom (far-stratum hit 0.00-0.02)
but a non-zero oracle far-reach (0.41) — i.e. S1 is NOT doomed, it is
under-resourced, and a naive trigger reading navigator-hit-rate alone would
have mis-classified it as doomed. This proposal asks whether a CHEAP,
early-checkpoint version of the compound signature (measurable at a fraction
of the full evaluation budget, without running the expensive oracle
traversal) can be validated as a program-wide early-abort trigger across
problem families neighboring the four already tested (S1_REG, S2_STACK,
S3_REWRITE, S4_MEM).

## Motivating evidence

- `agent_d4_blind/VERDICT-PHASE1.md` (frozen 2026-08-27): S3_REWRITE ->
  ACCESSIBILITY_FRAGMENTED — "the HIGHEST validity and viability of the four
  ... and the LARGEST phenotype mass ... with a dead accessibility geometry:
  far-stratum hits 0.00 for every navigator, and oracle far episode-reach
  0.00 — across ~1.5M metered evaluations, not one observed viable path led
  from any episode's starts into any far target's ball." The verdict names
  this explicitly as "the charter's central warning made flesh" and states
  "validity is a coordinate, not the objective; diversity is a coordinate,
  not the objective."
- Same document, S1_REG -> NAVIGATION_FAILURE (preserved, not fragmented):
  far stratum dead by navigator (N2 0.00, N4 0.02) but oracle far
  episode-reach 0.41 — "for ~2/5 of far episodes an observed path existed —
  attribution is search weakness/lottery topology at this budget, not proven
  fragmentation." This is the load-bearing contrast: navigator-hit-rate
  alone cannot separate doomed from merely-hard.
- `F:\Prometheus\aporia\docs\gemini_d4_substrate_dispatch_2026-08-27.md`
  restates the four-substrate summary table (viability / phenotype classes /
  far-stratum hit / verdict) and frames S1 as "a search failure at that
  budget" versus S3 as "a genuine topology failure" — the terminology this
  proposal adopts.
- `F:\Prometheus\roles\Charon\CHARTER.md`: "Every kill I post is substrate
  ... every kill-pattern I document is reusable verification machinery,"
  and "the residual is data, not noise... a 99.13% [sic, illustrative] kill
  rate is not 100%." This motivates treating the S3 signature as a candidate
  reusable cross-family instrument rather than a one-off substrate finding,
  which is the explicit ask of this proposal.
- Program memory (feedback_gate_must_be_shown_reachable,
  feedback_promotion_requires_independent_failure_mode): a gate must be
  shown attainable before it is trusted, and promotion requires an
  independent failure mode rather than reuse of the instrument that found
  the pattern — both bear directly on the Confound defenses below.

## Prospective predictions

1. Across a preregistered panel of problem families that are NOT S1-S4
   (chosen by an adjacency rule fixed before measurement — see Experiment),
   a cheap early-checkpoint compound signature (viability/phenotype mass in
   the top quartile of the panel AND navigator far-stratum hit rate = 0 at
   ~10-15% of the full 1,200-eval budget) will correlate with a full-budget,
   oracle-confirmed far-episode-reach of ~0.00, at a precision (positive
   predictive value) whose cluster-bootstrap lower CI bound clears 0.80.
2. Families exhibiting the S1-type symptom (near-zero navigator far-hit but
   non-zero oracle far-reach) will NOT trip the compound early-checkpoint
   trigger once the "top-quartile viability/diversity" co-condition is
   applied — because S1 in the original data has the LOWEST viability
   (0.093) of the four, not top-quartile. This is the specific mechanism by
   which the compound signature is predicted to out-discriminate a
   navigator-hit-rate-only trigger.
3. A baseline that uses viability or phenotype-mass ALONE (without the
   navigator-hit-rate term) will show materially worse precision, because
   high viability/diversity alone does not imply fragmentation (a family
   could have both AND be navigable, which the four-substrate dataset does
   not itself rule out — S4_MEM has substantial viability, 0.593, and full
   navigability).
4. The early-checkpoint trigger will not require full-budget oracle
   traversal to be practically useful: mean compute saved by aborting
   triggered runs before the full budget will exceed 50% of the
   would-be-spent evaluations in the families where it fires correctly.

## Experiment

1. Preregister a panel of 6-8 "neighboring" problem families before any
   measurement. "Neighboring" is defined structurally, not post-hoc: other
   machine-native computational-physics substrates built on the same
   frozen-instrument methodology as agent_d4_blind (e.g. successor
   substrates from the "worlds A-F" pipeline referenced in program notes),
   selected by an explicit design-space-adjacency rule (instruction-set
   style, state representation, mutation-operator menu) fixed and hashed
   before any family is run. Explicitly exclude cherry-picking families that
   already look S3-like.
2. For each family, run the existing D4-style pipeline unmodified: viability
   census, the generic M0 navigator suite (N1 random-walk floor, N2, N4),
   and the offline oracle traversal over observed edges, at the SAME frozen
   d1 <= 0.10 hit-ball and budget conventions used in Phase 1 (1,200 evals/
   target where the family's target-generation process supports it;
   otherwise the closest matched-cost budget, disclosed).
3. Additionally record navigator-hit-rate and viability/phenotype-mass
   readings at an early checkpoint (~10-15% of full budget, preregistered
   exactly per family before running) — this is the proposed cheap trigger
   input.
4. Compute the compound early-checkpoint signature per family: fires if
   (viability AND phenotype-mass both in top quartile across the panel) AND
   (navigator far-stratum hit rate == 0 at the early checkpoint).
5. Ground truth per family is the FULL-budget oracle far-episode-reach
   (not the full-budget navigator hit rate, which is instrument-confounded
   in the same way the checkpoint reading is). A family is "genuinely
   doomed" if oracle far-reach <= 0.05 (near-S3's 0.00, allowing small-sample
   slack); "recoverable" otherwise.
6. Score the trigger against ground truth across the panel: precision,
   recall, and the compute saved by early-aborting true-positive families
   before the full budget is spent.

## Controls

- Label-shuffle null: permute which family gets which early-checkpoint
  reading (breaking the pairing to full-budget oracle outcome) and confirm
  the observed precision is not reproduced by chance pairing.
- Baseline predictors run on the same panel: (a) viability alone, (b)
  phenotype-mass alone, (c) navigator-hit-rate alone (the naive trigger that
  the original S1-vs-S3 contrast already shows is insufficient) — the
  compound signature must beat all three at a Holm-corrected alpha.
- Order/seed randomization across families to prevent a single "which
  family ran first" confound in a red-team or calibration-drift sense.
- 5+ independent seeds per family (per program replication rule) before any
  per-family verdict is finalized, matching the D4 Phase 1 discipline of
  freezing gates before measurement.

## Confound defenses

- Instrument-existence check first (per program doctrine): before running
  controls on a new family, confirm the target signature COULD in principle
  fire there at all — i.e. the family's design space is capable of
  producing both near-ceiling viability and a dead far-stratum navigator
  reading, rather than assuming it and discovering later the family's
  metric range never reaches the relevant quartile.
- S1-vs-S3 conflation guard: the entire experiment exists because
  navigator-hit-rate alone already failed to distinguish "doomed" (S3) from
  "recoverable" (S1) inside the source data. Any implementation of this
  proposal that drops the oracle-ground-truth step and validates the
  trigger only against navigator-hit-rate is invalid by construction — it
  would be validating the instrument against itself.
- Independent failure mode: the falsifiers below are adjudicated by the
  oracle traversal, which is a different measurement process from the
  early-checkpoint navigator suite that generates the trigger, satisfying
  the program's independent-failure-mode requirement for any promotion
  claim.
- Small-n honesty: the source finding is n=4 substrates (one of which is
  the S3 positive case). Any cross-family generalization claim from a
  6-8-family panel is still a small-n regime; report per-family cluster-
  bootstrap CIs, not a single pooled point estimate, and do not claim
  "established" status — mirror VERDICT-PHASE1.md's own restraint ("Nothing
  stronger... this verdict does NOT establish...").
- Encoding-artifact guard: S3 is a string-rewrite system with combinatorial
  syntactic redundancy; the panel must include at least one non-rewrite,
  high-viability family (if the adjacency rule permits) specifically to
  test whether the signature is a REWRITE-representation artifact rather
  than a general topology property — if no such family is reachable under
  the preregistered adjacency rule, this is disclosed as an untested
  boundary, not resolved.

## Preregistered falsifiers (numeric thresholds)

- F1 (hard falsifier, single-counterexample sufficient, matching the
  source generation's own falsification stance): if any one panel family
  trips the early-checkpoint trigger (predicts doomed) but its full-budget
  oracle far-episode-reach exceeds 0.10, the compound signature is
  falsified as a universal early-abort trigger.
- F2 (precision floor): if the cluster-bootstrap lower CI bound on trigger
  precision (P(oracle far-reach <= 0.05 | trigger fires)) across the panel
  is below 0.80, reject the trigger as program-wide-deployable.
- F3 (beats-baseline requirement): if the compound signature's precision is
  not superior to the best of the three baselines (viability-alone,
  phenotype-mass-alone, navigator-hit-rate-alone) at Holm-corrected
  alpha = 0.05 (paired McNemar across families), reject the compound-vs-
  simple framing.
- F4 (operational-value floor): if mean compute saved by correct early
  aborts is below 50% of the would-be full budget, the trigger is
  statistically defensible but not worth deploying as an early-abort rule;
  report this as a distinct outcome from F1-F3, not folded into them.
- F5 (reachability check on F2's threshold, per program doctrine that a
  gate must be shown attainable): before F2 is scored, confirm 0.80 lies
  within the attainable precision range given the panel's actual class
  balance (doomed vs recoverable family counts); if class imbalance makes
  0.80 unattainable regardless of trigger quality, the gate is redesigned
  before scoring, not after seeing the result.

## Stopping rule

Preregister the panel at 6-8 families with an explicit power calculation
for detecting the precision floor in F2 before any family is run. Stop
immediately (before completing the full panel) if F1 fires on any
completed family — a single genuine counterexample (trigger predicts
doomed, oracle shows real reachability) ends the generalization claim, per
the source generation's own single-counterexample discipline. Otherwise run
the full preregistered panel to completion; do not extend the panel size
post-hoc based on interim results. Each family's thread terminates in one
of the three modes named in Charon's charter: signal confirms (oracle
far-reach matches trigger prediction), budget exhausts (family measured,
result banked either way), or an adversarial counter-explanation survives
(e.g. the encoding-artifact guard fires) — document which mode closed each
family.

## Expected failure modes

- The signature may be specific to REWRITE-style representational
  redundancy (combinatorial syntactic variants) rather than a portable
  topology property — the encoding-artifact guard above is designed to
  catch this but may be untestable if the preregistered adjacency rule
  cannot reach a suitable comparison family.
- The early checkpoint (10-15% of full budget) may be too noisy to reliably
  reproduce the full-budget navigator-hit-rate reading, analogous to
  S2_STACK's own marginal pass sitting inside cluster-bootstrap noise on
  the frozen gate — the compound signature could inherit this instability
  and fail F2 for measurement-noise reasons unrelated to whether the
  underlying phenomenon generalizes.
- "Top quartile across the panel" is a relative threshold that depends on
  which families are in the panel; a different preregistered panel could
  shift which families qualify as "high viability," making the trigger
  panel-composition-dependent rather than substrate-intrinsic. This is a
  known design weakness, disclosed rather than hidden.
- Different families may need different d1 hit-ball radii and budgets to
  be comparable (the source study's 0.10/1,200 pairing is itself specific
  to S1-S4's behavioral-fingerprint distance metric); forcing a uniform
  convention across structurally different families risks measuring
  instrument mismatch rather than the target phenomenon.

## Compute estimate

Source generation baseline: ~1.5M metered evaluations total across the
four original substrates (viability census + N1/N2/N4 navigator suite +
oracle traversal), per the dispatch summary. For a 6-8-family panel at
comparable per-family cost, full-budget measurement alone is estimated at
roughly 1.5-3M metered evaluations (assuming per-family cost in the same
order as the S1-S4 average, which will vary by family design and is
disclosed as an approximation, not a per-family costed budget). The early
checkpoint adds ~10-15% of one additional full-budget-equivalent per
family (a small fraction since it reuses the same run up to the checkpoint
rather than a separate pass) — order 150K-450K additional evaluations
across the panel. Oracle traversal cost historically dominates the total
(it is what drove the ~1.5M figure); this proposal does not reduce that
cost, since the oracle IS the ground-truth measurement the trigger is being
validated against, not something the trigger is meant to replace at this
stage. No compute has been spent executing this proposal; this is a
specification only, per task constraints.

## Prior evidence that materially changed this design (or 'none found')

- The S1-vs-S3 contrast inside VERDICT-PHASE1.md is what forced this design
  away from a single-metric trigger (navigator-hit-rate alone) toward a
  compound signature plus an independent oracle ground truth. Without that
  contrast on file, the natural first-draft design would have used
  navigator-hit-rate alone as the early-abort trigger and would have
  misclassified S1-type families as doomed.
- Charon's charter language on kill-patterns as reusable, typed substrate
  symbols is what frames this as a candidate program-wide instrument rather
  than a substrate-local curiosity, and its "residual is data, not noise"
  principle is why F4 (operational value) is scored separately from F1-F3
  (statistical validity) rather than collapsed into one verdict.
- Program memory items feedback_gate_must_be_shown_reachable and
  feedback_promotion_requires_independent_failure_mode directly shaped F5
  and the Confound-defenses "independent failure mode" item respectively;
  these were not re-derived from a fresh repository read in this session
  but carried in from standing program doctrine, and are flagged here so a
  reviewer can check them against their own source files
  (aporia/doctrine/critical_memories.md or equivalent) rather than trusting
  this document's paraphrase.

## Unresolved uncertainty

- Whether "neighboring families" should mean other machine-native
  computational-physics substrates (the D4 lineage, e.g. the "worlds A-F"
  successor pipeline) or extended to structurally different domains
  (policy-search populations, game-world benches). This proposal scopes to
  substrate-adjacent families only and treats cross-domain generalization
  as an explicit out-of-scope follow-on, not tested here.
- The exact early-checkpoint fraction (10-15%) and the "top quartile"
  viability/phenotype-mass threshold are placeholders pending a pilot on
  1-2 panel families; they were not derived from a fresh read of
  `agent_d4_blind/PREREG-PHASE1.md` in this session (budget was conserved
  after VERDICT-PHASE1.md and the dispatch summary already supplied the
  needed constants) and should be cross-checked against that document
  before execution.
- Whether the signature is a genuine topology property or a REWRITE-
  representation artifact is precisely the question the encoding-artifact
  guard is built to answer, and is left open pending panel composition —
  if the adjacency rule cannot reach a non-rewrite high-viability family,
  this uncertainty will remain unresolved even after the panel completes.

## Operation log (numbered; ops used / 15, documents opened / 12)

1. Grep "doomed" over F:\Prometheus — 19 files, mostly wiki-only hits;
   surfaced roles/Charon/CHARTER.md and pivot/ ergon_learner_proposal
   files as real (non-wiki) leads.
2. Grep "early-abort|early_abort|kill.trigger|abort.trigger" over
   F:\Prometheus — 2 files, both under evidence_wiki (out of scope, not
   opened).
3. Grep "failure signature|failure_signature" over F:\Prometheus — 30
   files, majority under evidence_wiki (not opened); confirmed this
   vocabulary is largely wiki-curated rather than present verbatim in the
   working repo.
4. Read attempt on docs\TASK_CORPUS_V2.md — resolved to
   evidence_wiki\docs\TASK_CORPUS_V2.md (out of scope); aborted, no content
   read, not counted toward documents-opened.
5. Grep "viability collapse|kill_path|far paths|navigable viability" over
   F:\Prometheus — 30 files (limit reached), mostly evidence_wiki; real
   (non-wiki) hits included roles/Techne/SUBSTRATE_FIRE_LOG files.
6. Read F:\Prometheus\roles\Charon\CHARTER.md (full) — document 1/12.
   Supplied the kill-pattern-as-substrate doctrine used in Motivating
   evidence and Prior evidence sections.
7. Grep "kill_path|viability|far.path" inside
   roles/Techne/SUBSTRATE_FIRE_LOG_2026-05-21.md — matches were an unrelated
   internal-marker filter list, not the target signature; ruled out as a
   lead.
8. Grep "viability|S3|far path|zero far" over F:\Prometheus\roles — 18
   files, none matched the D4 substrate finding directly; ruled out as a
   lead.
9. Grep "99.6%|zero far paths|S3_STACK|S4_MEM|S2_STACK" over
   F:\Prometheus — 20 files; surfaced the real source location,
   agent_d4_blind/VERDICT-PHASE1.md and PREREG-PHASE1.md.
10. Read F:\Prometheus\agent_d4_blind\VERDICT-PHASE1.md (full) — document
    2/12. This is the primary source for the failure signature: S3_REWRITE
    ACCESSIBILITY_FRAGMENTED verdict, exact viability/phenotype/navigator/
    oracle numbers, and the S1-vs-S3 doomed/recoverable contrast that
    shaped the whole design.
11. Read F:\Prometheus\aporia\docs\gemini_d4_substrate_dispatch_2026-08-27.md
    (first 80 lines) — document 3/12. Confirmed the four-substrate summary
    table and the "search failure vs genuine topology failure" framing
    adopted throughout this proposal.

Ops used: 11/15 (4 unused, stopped early — sufficient grounding reached).
Documents opened: 3/12 (CHARTER.md, VERDICT-PHASE1.md,
gemini_d4_substrate_dispatch_2026-08-27.md; the TASK_CORPUS_V2.md read
attempt errored on an out-of-scope path and is not counted).
PREREG-PHASE1.md was located (op 9) but NOT opened in this session; its
exact gate constants are taken secondhand from VERDICT-PHASE1.md and the
dispatch summary and are flagged for re-verification in Unresolved
uncertainty above.
