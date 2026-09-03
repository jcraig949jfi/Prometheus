# V0.4 Reversibility Crucible — PREREGISTRATION. Frozen before any V0.4 arm runs.

Brief: `roles/Proteus/PROMPT_PROTEUS_V0_4_REVERSIBILITY_CRUCIBLE_2026-09-03.txt`, sha256
`da514fda91630c07512dbf4c088d9512f5cf2af81da2e669b97633865737afd8`.
Grammar under test: `proteus.grammar.v0.4`. Runners refuse any other grammar or runtime hash.

## 0. The question

When a mutation walks from one valid structural state to another, does the grammar make the road
point somewhere — beyond the geometry of the valid joint manifest space?

Nothing here is optimized. No coordinate is a score. The Foundry does not landscape what it measures.

## 1. The one authorized change

Inside `op_config_perturbation`, the tape transition. The V0.2 half-tape occupancy rule is
removed. A proposed tape transition is valid iff (a) the destination is inside the published
bounds and (b) the existing genome fits in it. Nothing else changes: no weight, no limit, no
operator added or removed, no occupancy threshold, no compensation probability, no automatic
resizing of genome or tape.

`GRAMMAR_HASH` changes; `GRAMMAR_HASH_V0_3` and `GRAMMAR_HASH_V0_2` are retained as constants and
asserted distinct. The v0.2 operator TABLE stays executable. The v0.3 tape RULE is not retained as
a live code path: v0.3 and v0.4 share the operator table and differ only in the body of one
operator, and keeping both bodies would require exactly the kind of conditional the brief forbids.
V0.3 is reproduced from its committed rows and from git history. This is disclosed, not hidden.

## 2. Paired tape symmetry — the property to be proved, not asserted

For every adjacent pair `(t, 2t)` the primitive proposal probability of `t → 2t` must equal that
of `2t → t` before rejection. Rejection may be caused only by a published bound or by manifest
validity. Verified **exhaustively** over all 2,044 valid `(genome_length, tape_words)` states
(tape ∈ {16…4096}, genome_length ∈ [1, tape/4]), and additionally against the LIVE operator by
sampling, so the model is checked against the code rather than describing it.

## 3. NC5 — joint reversible manifest walk

Structural coordinates only: `genome_length × tape_words`. Every other configuration field is
excluded because none of them gates the validity of a structural proposal; that exclusion is
computed, not asserted. NC5 uses the published bounds, the grammar's own step sizes, the same
validity constraints and the same no-op rejection semantics, but its primitive paired moves are
symmetric by construction: the length kernel is symmetrized as `p_sym(d) = (p(d)+p(-d))/2` and
tape doubling and halving are equiprobable. NC5 inherits no asymmetric V0.4 rule. A
machine-readable transition audit is published for `v0_3`, `v0_4` and `nc5`, with every asymmetric
directed-edge pair classified as PUBLISHED_BOUNDARY, MANIFEST_VALIDITY, OPERATOR_DESIGN or UNKNOWN.

## 4. Null assignment

- `genome_length`, `config_log2_tape_words` → **NC5** (coupled structural geometry)
- other configuration coordinates → **NC1B** (symmetric bounded config walk, V0.3)
- content coordinates (opcode, class, operand, NOP share) → **NC4**, the length-matched geometry
  reference. NC3 is reported alongside as the V0.3-preregistered comparison, and where the two
  disagree the length-matched null decides. NC3's length-freezing confound is a known V0.3 defect.
- phenotype coordinates (status, executed fraction, silence, occupancies, mutation-touch) → **NC4**

NC4 answers conditional endpoint questions only. It is not claimed to establish mutation-path
reachability; that is what NC5 is for.

## 5. Decision rule

Unchanged from V0.3 in form, with the corrected multiplicity machinery. Drift is the per-lineage
change from checkpoint 0 to the final checkpoint; the matched null's drift is computed identically;
the reported quantity is the difference with a lineage-cluster bootstrap 95% interval (2,000
resamples, seeded). A coordinate shows a directional effect beyond null iff the interval excludes
zero AND the sign persists over the second half. Multiplicity uses `holm_agree`, which runs two
independent Holm implementations and RAISES on any disagreement — uncertainty is never a vote.
No per-coordinate tolerance is invented.

## 6. Crucible design

Cohorts by starting genome length **1, 8, 32, 128, 256**; **100 lineages per cohort**;
**400 generations**; battery checkpoints **0, 25, 50, 100, 200, 400**; tape 1024 words at start.
Arms: `V0_4`, `NC5`, `NC1B`, `NC2`, `NC3`, `NC4`. Every arm uses the same cohorts, lineage counts,
horizon and checkpoints. The full V0.3 battery is used unchanged; no coordinate may be removed.

## 7. Acceptance-rate maps

For each structural operator (insertion, deletion, duplication, splice, unreachable_removal, and
the tape/other configuration moves) report the acceptance probability conditional on manifest
state, over a grid of `(genome_length, tape_words)`. The question is not only whether marginal
drift is zero but whether some region systematically permits one direction of a reversible-looking
operation while suppressing its reverse.

## 8. Limited diffusion repeat

400 lineages, checkpoints 0/1/10/100/1000/10000, identical to V0.3 except for the grammar, so the
two are directly comparable on: genome-length distribution, tape-size distribution,
transcript-class concentration, knockout concentration, cumulative discovery, recurrence. More
diversity is not a better result. The desired result is no unexplained directional effect.

## 9. Audit identity

Every audit claim binds git commit and tree, grammar hash, runtime hash, affordance hash, a digest
of every covered source file, and the audit result hash. `audit_identity.py verify` reports STALE
automatically if any covered source changes after the stamp. Mechanical, not prose.

## 10. Adjudication order, fixed here

1. **G1 instrument integrity** — replay, audit identity, shadow execution, multiplicity agreement,
   required nulls. Any invalid ⇒ `INSTRUMENT_INSUFFICIENT_TO_ADJUDICATE`, stop.
2. **G2 known tape asymmetry** — if the V0.3 half-tape asymmetry is still present ⇒
   `NOT_QUALIFIED_KNOWN_TAPE_ASYMMETRY_REMAINS`.
3. **G3 joint structural neutrality** — persistent corrected structural effect beyond NC5 ⇒
   `NOT_QUALIFIED_DIRECTIONAL_MUTATION_PRIOR_REMAINS`. Every coordinate reported.
4. **G4 content neutrality** — persistent corrected content effect beyond its valid matched null ⇒
   `NOT_QUALIFIED_DIRECTIONAL_MUTATION_PRIOR_REMAINS`.
5. **G5 diffusion collapse** — concentration materially beyond the geometry reference ⇒
   `NOT_QUALIFIED_BEHAVIORAL_SPACE_COLLAPSES_UNDER_NEUTRAL_DIFFUSION`.
6. **G6** — otherwise `QUALIFIED_AS_NEUTRAL_FOUNDRY_WITH_STATED_GEOMETRIC_EFFECTS`.

A separate, non-verdict classification is reported if it applies: if the historical
V0/V0.1/V0.2 genome-length drift returns under V0.4 **and NC5 reproduces it**, report
`HISTORICAL_V0_LENGTH_FAILURE_RECLASSIFIED_AS_JOINT_GEOMETRY`. The old verdicts are not altered;
they were correct under the rules they declared.

## 11. Commitments

Nothing in section 1 changes after a result is seen. No coordinate removed, no tolerance
introduced, no filtering, seeding, balancing, curriculum, fitness, novelty reward or survival
criterion. Failed results are kept under their own identity and never repaired. The grammar is
not changed after seeing the transition graph. If the verdict is negative, the packet says so and
the seat stops.
