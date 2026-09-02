# PROPOSAL V2-T03 (arm A)

## Hypothesis

Given a family of procedurally generated world instances, each carrying one
or more designated goal (terminal, "win") states reachable from a
designated start, the candidate learner reaches goal states at a rate that
exceeds the *best of a matched-budget suite of generic, history-free
baselines* — not merely a uniform-random action-selector — and that this
excess survives (a) a degeneracy check on the world itself, (b) a
remoteness stratification of goals so the comparison is read where chance
is actually low, and (c) a winner-curse correction for having chosen the
strongest baseline in the suite as the comparator.

The claim under test is narrow and comparative: "this learner's goal-hit
rate exceeds the best generic-search floor, stratified by goal remoteness,
under identical metered budget." It is not a claim of planning, understanding,
or general competence.

## Motivating evidence

Three internal precedents converge on the same design pattern and are the
basis for this arm (see Operation log for how each was found):

1. `F:\Prometheus\ludus\baselines.py` implements exactly the doctrine named
   in memory as `feedback_counter_baseline_discriminator` and
   `feedback_gate_must_be_shown_reachable`: before any model/learner is
   pointed at a rung, compute the attainable range with zero learner calls
   — random-legal rate, one-ply-greedy rate, and majority-class rate — and
   flag any rung where a cheap floor already sits near the ceiling as
   `DEGENERATE`, ineligible to carry a reading. The explicit rule in that
   module: "the bar is never 'beats random'."
2. `F:\Prometheus\agent_d4_blind\PREREG-PHASE1.md` and its
   `VERDICT-PHASE1.md` operationalize goal-reaching-under-procedural-
   generation at scale: targets are drawn from an *independent* random-walk
   seed (not the learner's own occupancy), stratified into near/mid/far by
   measured remoteness, with a hit-ball filter (`EPS_HIT + 0.05`) that
   removes targets a naive draw could hit for free. The comparator is a
   *suite* of four history-free navigators (restart-walk, hillclimb,
   novelty, recombiner) run at an identical metered budget, and the verdict
   explicitly discloses "winner-curse": the navigator chosen as "best pair"
   is selected on the same rows that feed the gates, so both navigators'
   full statistics are reported regardless of selection.
3. The same generation adds an oracle (reverse BFS over the *observed*
   transition graph) used only to attribute a miss to topology
   (unreachable) vs. search weakness (reachable but not found) — never fed
   back to any navigator — plus counterfactuals (representation re-coding,
   mechanism ablation, menu reweighting) to check the passing margin isn't
   an artifact of one privileged mechanism or encoding.

## Prospective predictions

1. H0 (null): the learner's pooled goal-hit rate, at matched budget, does
   not exceed the upper cluster-bootstrap CI bound of the best generic
   baseline in the suite, on the far-remoteness stratum.
2. H1 (target claim): the learner's pooled far-stratum hit rate exceeds the
   best generic baseline's far-stratum hit rate by an absolute margin
   >= 0.15 with a two-proportion z >= 1.96, AND this margin is not
   attributable to a single ablatable learner mechanism (no single-
   mechanism ablation cell recovers the baseline rate).
3. Near-stratum hit rates are expected to compress toward 1.0 for
   everything (learner and baselines alike) and are reported but never
   gate the verdict — this is the predicted degenerate region.
4. If the world's cheap floor (random-legal, greedy-1-ply, or majority-
   class analogue for this world family) already sits >= 0.80 on any
   stratum, that stratum is predicted to be DEGENERATE and is dropped from
   the gate before the learner is ever run — a prediction about the
   instrument, checked with zero learner calls, per `ludus/baselines.py`.
5. Representation-recoding (bijective relabeling of state/action encoding)
   is predicted to change the learner's hit rate by less than the same
   margin/z threshold used for G5 below — i.e., the effect is not an
   artifact of the specific encoding.

## Experiment

**World family.** A parametrized generator produces world instances from a
frozen seed family (analogous to `ludus.worlds.WORLDS` / D4's
`substrates`): each instance has a discrete state space, a legal-action
function, a deterministic (or fixed-seed stochastic) transition function,
and one or more designated goal/terminal states. Generation parameters
(size, branching, goal count) are themselves drawn from a frozen
distribution and disclosed, so "procedurally generated" is a measured
population, not a single instance.

**Step 0 — attainable range (zero learner calls).** For each world
instance, before any learner run: sample >= 300 eligible states (branching
>= 2, per `MIN_BRANCHING` in `ludus/baselines.py`) and compute (a) random-
legal hit rate, (b) one-ply-greedy hit rate, (c) majority-class rate, (d)
where the state space is small enough to enumerate, an exact solver ceiling
(`solve`/`reachable_states` pattern). Any instance where the cheap floor is
degenerate (defined in Preregistered falsifiers) is excluded from the gated
battery and reported separately.

**Step 1 — goal stratification.** From each eligible instance, draw 64
start states via a dedicated RNG stream independent of any learner
consumption; run uniform-random-legal walks of fixed length to build a
pool of visited (candidate-goal) states; compute remoteness of each
candidate as mean distance to a fresh independent reference sample; filter
out candidates inside the hit-ball of an ab-initio draw (trivial goals);
stratify the remainder into near/mid/far by remoteness decile, matching
the D4 protocol exactly.

**Step 2 — comparator suite.** Run, at an identical metered evaluation
budget per goal: (i) random-legal-action baseline, (ii) restart-random-walk,
(iii) greedy/hillclimb-style local descent on a declared distance-to-goal
proxy, (iv) a population/recombination-style search, (v) majority-class /
fixed-policy baseline. All five are history-free and share one evaluation
meter with the learner (cache hits metered identically for every
consumer).

**Step 3 — learner run.** The candidate learner is run on the same goal
set, same budget, same start-state draws, with identical instrumentation.
Its hit is scored under the same distance-to-goal-state criterion used for
the comparators (exact state match, or a disclosed tolerance ball if the
world has a continuous or near-continuous state component).

**Step 4 — oracle attribution (analysis only, post-hoc).** Reverse-BFS
over the union of all observed transition edges (comparators + learner) to
label each miss as topologically unreachable (from any observed start) or
reachable-but-not-found. Never fed back into any run.

**Sample sizes.** Matched to D4 scale as a starting point: ~30-40 world
instances after the degeneracy filter; 36 goals per instance (12 per
stratum) as in D4; >= 5 seeds per comparator and per learner condition per
goal; budget per run set so that the cheapest comparator (random-legal)
achieves a non-trivial near-stratum hit rate (attainability check, done
before freezing the budget).

## Controls

- **Random-legal-action control** — the absolute floor; establishes that
  "better than chance" is measured against this only as a lower bound, never
  as the sole comparator.
- **Suite of generic history-free searchers** (restart-walk, hillclimb,
  novelty/coverage, recombiner) — the actual comparison bar; matched budget,
  matched meter, matched goal set.
- **Majority-class / fixed-policy control** — catches worlds where one
  action or state dominates goal-reaching regardless of state-reading.
- **Exact-solver ceiling control** (where tractable) — establishes the
  attainable range so a pass can't be read on a rung where the ceiling
  itself is trivially low or trivially high.
- **Representation-recoding control** — a frozen bijective relabeling of
  state/action encoding applied at decode time (same physics, different
  surface encoding); checks the learner isn't exploiting an accidental
  encoding artifact rather than world structure.
- **Single-mechanism ablation of the learner** — remove/disable each
  distinct mechanism the learner uses (e.g., a memory component, a
  scoring/heuristic component) one at a time and re-measure; a privileged-
  corridor analogue for the learner itself, mirroring D4's G5.
- **Oracle-reachability control** (analysis-only) — never used to pass or
  fail a gate directly; used only to attribute misses to topology vs.
  search weakness.

## Confound defenses

- **Selection-relation independence** (`feedback_control_must_break_the_
  selection_relation`): goal states and start states must be drawn from an
  RNG stream independent of the learner's own rollouts/training data. A
  goal set built from the learner's own visited states IS the treatment,
  not a control.
- **Common reference distribution, not self-occupancy**
  (`feedback_onpolicy_score_conflates_exposure_and_competence`): remoteness
  and difficulty strata are computed against a fixed, shared reference
  sample (the independent 64-start / fresh-48-reference pool), identical
  for the learner and every comparator — never a distribution built from
  what the learner itself visits, and never uniform over states the world
  never actually exhibits.
- **Attainable-range-before-gate** (`feedback_gate_must_be_shown_reachable`,
  `feedback_gate_must_exceed_measurement_error`): the cheap-floor and
  ceiling computation happens with zero learner calls, before any
  threshold is frozen, and every frozen threshold is checked for
  attainability and checked against its own standard error before it is
  written down.
- **Budget symmetry**: identical `evaluate()` metering and cache-hit
  metering across learner and all five comparators; no post-budget
  success counted for anyone.
- **Winner's-curse guard**: the "best comparator" label is diagnostic only;
  full statistics (rate, CI, cluster-bootstrap CI) for every comparator are
  reported regardless of which one is nominally "the bar," matching D4's
  explicit disclosure practice.
- **Hit-ball filtering**: goals inside a fresh ab-initio draw's hit radius
  are removed and counted, so "reaching a goal" cannot be scored on a goal
  that was never actually remote.
- **Degeneracy-then-freeze ordering**: worlds/strata failing the
  degeneracy check are dropped from the gate before the learner is run —
  this ordering itself is part of the preregistration, not a post-hoc
  exclusion.

## Preregistered falsifiers (numeric thresholds)

- **G0 WORLD_DEGENERATE**: cheap floor (max of random-legal, one-ply-
  greedy, majority-class) on a stratum >= 0.80, OR random-legal rate on a
  stratum >= 0.75 with no state-reading required. Any such (world,
  stratum) cell is excluded from the gate and reported separately, per
  `ludus/baselines.py` headroom doctrine.
- **G1 NAVIGATION_FAILURE (comparator sanity)**: fewer than 2 of the 4
  generic searchers reach pooled hit rate >= 0.25 with Wilson 95% CI, on
  the eligible (non-degenerate) pool. If this fires, the world family
  itself is not a valid test bed for "better than chance" and the arm is
  preserved as a null result about instrument choice, not about the
  learner.
- **G2 LEARNER_PASS**: learner's far-stratum pooled hit rate exceeds the
  best generic comparator's far-stratum pooled hit rate by an absolute
  margin >= 0.15, two-proportion z >= 1.96, AND the cluster-bootstrap CI
  (cluster unit = goal instance) computed over the same margin excludes 0.
- **G3 PRIVILEGED_MECHANISM**: any single learner-mechanism ablation cell
  with baseline far-stratum rate >= 0.15, relative drop > 0.60, and
  two-proportion z >= 1.96 downgrades a G2 pass to
  "mechanism-dependent, not general" in the verdict narrative — reported,
  never silently dropped.
- **G4 REPRESENTATION_SENSITIVE**: |pooled hit rate under recoded
  representation - baseline pooled hit rate| > 0.15 with z >= 1.96
  downgrades a G2 pass to "encoding-sensitive."
- **G5 REFINDABILITY_FAILURE**: for goals hit by k of S seeds, re-find
  ratio (k-1)/(S-1) averaged over once-hit goals < 0.40 — a pass driven by
  single lucky seeds does not count as reproducible reaching.
- Overall PASS label ("reaches goal states better than chance") requires
  G1 to NOT fire (comparators are sane), G2 to fire, and neither G3 nor G4
  to fire; a G2 pass with G3 or G4 firing is reported as a downgraded,
  narrower claim, never suppressed.
- Family-wise correction: Holm–Bonferroni across all gated (world x
  stratum) cells in the battery, stated with the total hypothesis count
  before any test is run.

## Stopping rule

All thresholds, budgets, world-generation parameters, and the comparator
suite are frozen and hash-recorded before the learner is run — matching
the binding-commit discipline in `PREREG-PHASE1.md`. After freeze: no
threshold movement, no comparator swap, no goal-set repair, no rerun-to-
positive. If an engineering failure (crash, resource exhaustion) occurs
before any binding measurement exists, the run is preserved as invalid and
relaunched once from the identical frozen seed with a disclosed,
measurement-equivalent fix (per D4's E1 amendment pattern) — never patched
after a result is seen. The battery is run once; all gates are evaluated
in the fixed causal order above (G0 -> G1 -> G2 -> G3 -> G4 -> G5); the
first disqualifying gate is the primary flag, but every gate's value,
margin, and CI is reported regardless of where the primary flag lands.

## Expected failure modes

- The world generator produces instances that are degenerate at the
  intended difficulty parameter (G0 fires broadly) — the generator's
  difficulty knob doesn't track actual navigational difficulty.
- The comparator suite itself cannot clear G1 on far goals (fragmented
  topology, S3_REWRITE-style: high validity/diversity but zero far-stratum
  reachability for anyone) — this would be a finding about the world
  family, not the learner, and must not be reframed as a learner success.
- A G2 pass driven almost entirely by one learner subsystem (G3 fires) —
  the "learner reaches goals" claim collapses to "one hard-coded heuristic
  reaches goals."
- A G2 pass that inverts or vanishes under representation recoding (G4
  fires) — the learner was reading an accidental encoding regularity, not
  world structure.
- Winner's-curse inflation from selecting the strongest of four
  comparators as "the bar" without correction — mitigated by reporting all
  four and by the margin/z threshold in G2 being computed against the
  single strongest one specifically (a conservative, not lenient, choice).
- Oracle undersampling: the observed transition graph undersamples the
  true reachability graph, so a "fragmented" attribution is a statement
  about demonstrated topology at this budget, not a proof of true
  unreachability — must be disclosed exactly as D4 discloses it, not
  overstated.

## Compute estimate

Scaled from the D4 precedent as a starting order-of-magnitude, pending the
new world family's actual state-space size: attainable-range profiling
(zero learner calls) over ~300 sampled states x ~30-40 world instances;
goal generation ~64 starts x 150-step walks x ~30-40 instances; comparator
suite ~5 methods x 5 seeds x 36 goals x ~30-40 instances x <=1,200 metered
evaluations per run (order 10^6-10^7 metered evaluations total, matching
D4's ~1.5M-evaluation scale on its densest substrate); learner run at the
same per-goal budget and seed count; ablation/recoding counterfactuals add
a further ~20-30% of the comparator-suite compute. All of this is CPU-only,
no external model calls, consistent with an evaluation-harness-only
compute profile.

## Prior evidence that materially changed this design (or 'none found')

Materially changed this design (all found within the 15-op / 12-doc budget
for this task, none from evidence_wiki):

- `F:\Prometheus\ludus\baselines.py` — supplied the exact "cheap floor
  before any gate" mechanic (random-legal / one-ply-greedy / majority-class)
  and the explicit doctrine that the bar is never "beats random," directly
  shaping G0 and Step 0.
- `F:\Prometheus\agent_d4_blind\PREREG-PHASE1.md` and
  `VERDICT-PHASE1.md` — supplied the remoteness-stratified target design,
  the hit-ball filter against trivial goals, the four-navigator comparator
  suite, the oracle-attribution pattern, the winner's-curse disclosure
  practice, and the ablation/recoding counterfactual battery — this arm's
  Experiment, Controls, and gate structure are a direct adaptation of that
  precedent to a single-learner "reaches goal states" claim rather than
  D4's accessibility-geometry claim.
- Memory feedback entries `feedback_counter_baseline_discriminator`,
  `feedback_gate_must_be_shown_reachable`,
  `feedback_gate_must_exceed_measurement_error`,
  `feedback_control_must_break_the_selection_relation`, and
  `feedback_onpolicy_score_conflates_exposure_and_competence` — each maps
  onto one specific defense above (respectively: the comparator suite
  rather than a single random baseline; the attainable-range step ordered
  before any threshold is frozen; the SE-vs-threshold check in G0/G2; the
  independent-RNG-stream requirement for goal/start sampling; and the
  shared-reference-distribution requirement for remoteness strata).

## Unresolved uncertainty

- Whether the new world family's state space is small enough to compute an
  exact solver ceiling (Step 0d); if not, the design falls back to the
  oracle-BFS-over-observed-graph proxy only, which is a weaker ceiling
  statement and must be disclosed as such, exactly as D4 discloses that
  "accessible mass" is measured against phenotypes the physics itself
  exhibited under an independent seed, not against all mathematically
  existing states.
- Whether the world generator's declared difficulty parameter actually
  tracks measured remoteness — this is itself an empirical question Step 0
  answers, not an assumption; if it doesn't track, the stratification must
  be built from measured remoteness alone (as D4 does) rather than the
  generator's nominal difficulty label.
- Whether 5 comparator seeds and ~30-40 world instances give adequate
  cluster-bootstrap power for G2 at the far stratum specifically (D4's own
  S2_STACK result shows a pooled pass can sit inside cluster-level noise);
  a power check against the D4-observed CI widths should be run before
  freezing sample sizes, not assumed adequate by analogy alone.
- Whether "goal state" for the new world family is a single exact state or
  a tolerance ball; this changes the hit criterion and must be settled by
  the world's own state topology (discrete vs. near-continuous) before
  freeze, not left implicit.
- Whether mechanism-PAIR privilege in the learner (vs. single-mechanism,
  per G3) matters for this learner's architecture — D4 explicitly leaves
  this combinatorial gap open and this arm inherits the same gap.

## Operation log (numbered; ops used / 15, documents opened / 12)

1. Grep "procedurally generated" over F:\Prometheus — TIMED OUT (no
   result; repo too large for an unscoped recursive search).
2. Grep "better than chance" over F:\Prometheus — TIMED OUT (no result).
3. Glob "*" over F:\Prometheus (top level) — TIMED OUT (no result).
4. Bash `ls -1` at F:\Prometheus — success; oriented to top-level
   directories (found `ludus`, `incubation_d`, `agent_d4_blind`, etc.).
5. Bash `ls -1` at F:\Prometheus\ludus — success; found `baselines.py`,
   `worlds.py`, `docs/`.
6. Bash `ls -1` at F:\Prometheus\incubation_d — success; found
   `design_manifest.md`.
7. Bash `ls -1` at F:\Prometheus\ludus\docs — success (one file, not
   opened; not central to this arm).
8. Read F:\Prometheus\ludus\baselines.py — success. [document 1/12]
9. Read F:\Prometheus\incubation_d\design_manifest.md — success.
   [document 2/12]
10. Grep "terminal|goal|win_|is_win|reward" in
    F:\Prometheus\ludus\worlds.py (content mode) — success; located
    `is_terminal` / goal-site definitions.
11. Bash `ls -1` at F:\Prometheus\agent_d4_blind — success; found
    `PREREG-PHASE1.md`, `VERDICT-PHASE1.md`.
12. Read F:\Prometheus\agent_d4_blind\PREREG-PHASE1.md — success.
    [document 3/12]
13. Read F:\Prometheus\agent_d4_blind\VERDICT-PHASE1.md — success.
    [document 4/12]

Ops used: 13 / 15 (3 failed timeouts counted; 10 productive). Documents
opened: 4 / 12. Stopped early once the comparator-suite / degeneracy-check
/ remoteness-stratification pattern was corroborated across two
independent internal precedents (LUDUS and Agent D4); unused budget (2 ops,
8 documents) was not spent chasing a third precedent, since the two found
already converge on the same mechanism and the marginal value of a third
was judged low against the remaining budget.
