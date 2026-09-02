# PROPOSAL PILOT-1 (arm A)

## Hypothesis

Within the D-5 M1 learner's developmental artifact library (`agent_d5_blind/learner/m1.py`),
an individual artifact's AGE — the number of tasks elapsed between its admission to the
library and the task it is tested against — negatively predicts that artifact's causal
usefulness on that later task. Concretely: injecting a single library genotype as the
sole immigrant source (`extra_pool = {g}`) into an otherwise-frozen M1 search confers a
solve-rate lift over the library-free baseline (M0-equivalent, `extra_pool = None`) that
decays as a function of admission-to-test-task offset ("age"), holding artifact identity
fixed and varying only which future task it is tested against.

This is a different, finer-grained question than anything D-5 already answered. D-5's
G9 gate tested whether the ORDER in which a fixed set of artifacts accumulates changes
the AGGREGATE solve rate (it does not: shuffled-history retains 100% of the advantage).
PILOT-1 asks whether, within one fixed accumulation order, an individual artifact's own
elapsed age predicts ITS OWN future usefulness — a per-artifact, not per-run, question
that G9's aggregate comparison cannot see either way.

## Motivating evidence

- `agent_d5_blind/VERDICT.md`: HISTORY_FINDABILITY_ADVANTAGE established
  (M1 − M0 = +10.95pp CFR, p=0.0007, task-level n=42, SE≈3.4pp). Decomposition (G9):
  shuffled-history retains 100% of the advantage; random-library retains 39%. Verdict:
  "library-content effect... not a developmental-correspondence effect." G6: no
  developmental trend (late-vs-early ≈ 0, p=0.49).
- `agent_d5_blind/learner/m1.py` (read directly, lines 1-120): library is capped at 64
  genotypes, most-recent-first eviction, genotype-deduped; each task admits the solver
  (if any) plus up to 4 behavior-distinct best-scoring candidates from the last scored
  generation (`admissions()`, `ADMIT_K=4`); 50% of immigrant draws sample UNIFORMLY at
  random from the current library (`extra_pool[rng.randrange(len(extra_pool))]`) — the
  draw mechanism is mechanically age-blind by construction.
- `agent_d5_blind/developmental_history/run_m1_lineage.py` (read directly): the frozen
  evidence harness logs `library_size_at_start` per row but does NOT persist per-artifact
  admission position/age or which genotype ended up as the solver. `accumulate_pass()`
  does build per-position snapshots, but only for reconstructing the M1-shuffled-history
  arm, not as a general per-artifact provenance ledger.
- `agent_d5_blind/developmental_history/final_libraries/lineage_{0..4}.json` exist
  (listed, not opened) — final library states for 5 developmental lineages; whether
  they carry per-position (not just final) snapshots is unconfirmed (see Unresolved
  uncertainty).

## Prospective predictions

1. Age-decay (primary stand): mean single-artifact solve-rate lift, aggregated over a
   preregistered offset ladder (+1, +3, +6, +12 tasks past admission) and a fixed
   navigator-seed repeat count, is a decreasing function of offset. Predicted primary
   statistic: Spearman rho(age offset, solve-rate lift) <= -0.15, one-sided.
2. Null-consistent-with-G9 (live alternative): because the draw mechanism is uniform
   and G6 already found no aggregate developmental trend, age may show NO relationship
   to per-artifact usefulness (|rho| < 0.05, not significant) — usefulness would then be
   a fixed property of an artifact's content, invariant to how long it has sat in the
   library, extending G9's order-invariance down to the individual-artifact level.
3. Veteran-effect (opposite-direction, also falsifiable): rho >= +0.15 significant would
   mean older admitted artifacts are systematically MORE useful — plausible if early-
   admitted artifacts happen to be generically more reusable seed material rather than
   task-specific, since eviction here is pure FIFO (no fitness re-ranking), so any such
   effect would reflect selection into what got admitted early, not survival-of-fitness
   among old artifacts.

## Experiment

Phase 0 (preflight, engineering seeds 1000-1999 only, per the existing D-5 seed-stream
policy):
1. Confirm `update_library()`'s exact eviction/dedup body (docstring only was read;
   the body was not) to verify most-recent-first FIFO eviction and to check whether an
   artifact genotype-identical to an old library entry can be re-admitted and thereby
   get a fresh (younger) age stamp — if so, age must be defined as FIRST admission
   position, not most recent, and this must be fixed before freezing anything.
2. Deterministically REPLAY the frozen M1 evidence seeds (same `seed_base`, same
   `tasks`, same physics/oracle — all already frozen and hashed in
   `anti_cheat/frozen_hashes.json`) with one added instrumentation: at every task
   position, snapshot `(genotype, admission_position)` for every library entry. This is
   pure replay of already-frozen, already-verdicted computation with extra bookkeeping;
   it does not alter or re-open PREREG-EVIDENCE.md's frozen results.
3. From the reconstructed per-position library, measure empirical artifact survival
   horizon (how many admission-events before a given genotype is evicted under the
   cap-64 FIFO policy) across the 5 lineages. This fixes which offsets in the ladder
   are actually populated (Falsifier F3 below) before any evidence run.
4. Preregister the exact artifact sample: for each of the 5 frozen lineages, the first
   N solver-admitted genotypes with a full complement of populated offsets from step 3
   (target N disclosed after step 3, not adjusted afterward).
5. Size the per-cell navigator-seed repeat count from the existing D-5 CFR SE estimate
   (SE≈0.034 at task-level n=42, per VERDICT.md G4) to reach a target SE ≤0.05 on the
   single-artifact solve-rate-lift statistic, run on engineering seeds only, then freeze.

Phase 1 (evidence, seed streams 4000-4999/7000-7999 per existing policy, never
engineering seeds):
For each preregistered (artifact g, offset o) cell: draw the task at position
(admission_position(g) + o) from the frozen task battery; run `m1_rx(view, rng, TOP,
library=[g])` and `m1_rx(view, rng, TOP, library=None)` under matched navigator seeds
(the fixed repeat count from Phase 0); record solved/first_solve for both arms; the
cell statistic is the paired solve-rate (or first-solve) lift, single-artifact
attributable, exactly analogous to the FOUNDRY residue-ablation heredity test already
used elsewhere in the program.

## Controls

- Matched-seed paired design: every injected-artifact run has a same-seed
  library-free (M0-equivalent) counterpart on the identical task, so the lift is a
  paired within-task delta, not a between-task or between-arm-population comparison.
- Family/stratum-matched control arm: for each tested (artifact, offset) cell, also run
  the SAME artifact against a task drawn from a DIFFERENT family/stratum at the same
  offset, to separate "age" from "family adjacency in the frozen task sequence" (see
  Confound defenses).
- Structureless-control-style floor: report the same statistic for artifacts drawn from
  `SEED_REPERTOIRE` (the frozen, non-developmental starting genotypes) injected at
  matched offsets, as a zero-age-signal floor comparable to D-5's own CTRL arm (G8).

## Confound defenses

- Absolute-position confound: raw task index and library size/maturity both grow
  together over a lineage, so comparing artifacts admitted at different absolute
  positions would confound age with "how much library existed yet." Defense: PILOT-1
  never compares across artifacts at different absolute positions — it compares the
  SAME artifact across MULTIPLE future offsets, so age varies while artifact identity
  is held fixed (within-artifact repeated measures).
- Task-family adjacency confound: the frozen task sequence may place family-similar
  tasks near each other in position order, which would let "age" silently proxy for
  "family similarity to the admitting task" rather than elapsed time per se. Defense:
  the family/stratum-matched vs. mismatched control arm above directly tests this; if
  the apparent age effect disappears once family is matched, the primary hypothesis is
  rejected in favor of a family-similarity account.
- Admission-filter selection: only the solver plus up to 4 behavior-distinct top
  candidates from a scored generation are ever admitted (`ADMIT_K=4`) — already a
  competence-filtered, non-representative sample of all attempted genotypes. Defense:
  report solver-admitted vs. runner-up-admitted artifacts as an explicit disclosed
  factor/interaction, not pooled, since the two admission routes may carry different
  quality distributions.
- Eviction/turnover truncation: FIFO cap-64 eviction guarantees the oldest offsets in
  any naive ladder will be systematically under-populated or empty for lineages with
  fast turnover. Defense: Phase 0 step 3 measures the empirical survival horizon BEFORE
  the offset ladder is frozen (Falsifier F3), so the ladder is only frozen once it is
  known to be reachable — mirroring the D-5 doctrine that a gate must be shown
  reachable before it is read.
- Mutation-intervening confound: usefulness is measured on `mutate(g, rng)`, not on the
  raw genotype `g` itself, since `fresh()` always mutates before use. This is disclosed
  as a property of what "usefulness" means here (the artifact's local mutational
  neighborhood, exactly as the live M1 mechanism actually uses it), not corrected away.
- Multiple-comparisons: 5 lineages x N artifacts x 4 offsets x 2 control arms is a
  large cell count. Defense: Holm correction across the 4-offset ladder within the
  primary rho statistic; the family-matched/mismatched and SEED_REPERTOIRE-floor arms
  are reported as disclosed secondary checks, not folded into the primary p-value.

## Preregistered falsifiers (numeric thresholds)

- F1 (primary): one-sided Spearman rho(age offset, solve-rate lift) <= -0.15,
  Holm-corrected alpha=0.05 across the 4-cell offset ladder. If not met: AGE_ADVANTAGE
  NOT ESTABLISHED.
- F2 (floor): mean solve-rate lift at the nearest offset (+1) must exceed twice its
  bootstrap SE; if it does not, the instrument itself cannot detect single-artifact
  usefulness at all and the result is INSTRUMENT_INSUFFICIENT (mirrors D-5's own G5
  underpowered pattern), not a negative finding about age.
- F3 (reachability-of-design, checked in Phase 0 before any evidence row is read): if
  more than 50% of the preregistered offset-ladder cells are empty because artifacts
  are evicted before that offset is reached, the ladder is OFFSET_LADDER_INVALID and
  must be redesigned before Phase 1 — never adjusted after evidence is read.
- F4 (opposite-direction, always reported if triggered): rho >= +0.15 significant
  (Holm-corrected) falsifies the age-decay hypothesis in favor of a veteran effect and
  must be reported as such, not suppressed or reframed as consistent with F1.
- F5 (confound check): if the apparent age effect (F1) survives in the family-matched
  control arm but VANISHES in the family-mismatched arm, the effect is attributed to
  family adjacency, not age, and the primary hypothesis is rejected regardless of F1's
  outcome in the pooled data.

## Stopping rule

Fixed-N, not sequential. The per-cell navigator-seed repeat count and the artifact
sample (N per lineage) are both fixed in Phase 0 on engineering seeds only, then
hashed and frozen before a single evidence-stream (4000+/7000+) row is read — identical
discipline to D-5's own PREREG-EVIDENCE freeze and "no within-generation rescue" rule
(§44 in the D-5 manifest lineage). No early stopping on a favorable interim rho; no
added artifacts, offsets, or seeds after the freeze regardless of interim results.

## Expected failure modes

- Admission-filter ceiling: because admitted artifacts are already the fittest
  candidates of their generation, most single-artifact injections may show near-zero
  lift at ANY age, making the whole age-decay curve statistically silent — this is
  exactly the shape of D-5's own G5 (HACR underpowered, 90% CI touches 1.0 at n=13).
- Family-adjacency masquerading as age: if the frozen task sequence clusters
  same-family tasks at nearby positions (unconfirmed — task_manifest.json was not
  opened in this budget), any apparent "age" effect could be pure family-similarity in
  disguise; F5 is designed to catch this but only if it is actually triggered.
- Turnover-truncated ladder: if empirical survival horizon (Phase 0 step 3) is short
  relative to the intended ladder, the outer offsets (e.g. +12) may be systematically
  unpopulated across most lineages, collapsing statistical power to the inner offsets
  only — must be disclosed, not patched by silently dropping cells post hoc.
- Mutation-operator confound dominates: since usefulness is measured post-mutation, a
  finding of "no age effect" could reflect the mutation operator erasing most
  age-dependent structure in a single step, rather than age being causally irrelevant
  to the raw artifact — a genuinely different mechanism than the stated hypothesis,
  disclosed as an alternative reading of any null result.

## Compute estimate

All substrate/physics/oracle code is already frozen, hashed, and known-fast from this
generation's own engineering-seed sizing runs (`results/sizing_probe.json`,
`results/sizing_probe2.json` exist but were not opened in this budget). Order-of-
magnitude: 5 lineages x ~8-10 preregistered artifacts/lineage x 4 offsets x 2 control
arms x (fixed seed-repeat count, likely 20-30 to reach SE≤0.05 given VERDICT.md's
SE≈0.034 at coarser aggregation) is on the order of a few thousand bounded GA runs,
each capped at TOP=30000 evaluations against the already-fast `FastTask` oracle. This
is comparable in scale to D-5's own full M1 developmental-evidence run, i.e. expected
to be single-machine, CPU-only, on the order of low hours, not requiring new compute
infrastructure. This estimate is provisional pending the Phase 0 engineering-seed
timing pass, which must occur before Phase 1 is sized precisely.

## Prior evidence that materially changed this design (or 'none found')

- G9 (`agent_d5_blind/VERDICT.md`): shuffled-history retains 100% of the aggregate
  advantage. This closed off "does accumulation order matter in aggregate" and is the
  direct reason PILOT-1 targets a different, individual-artifact-level question rather
  than re-running an order-manipulation at the aggregate level.
- G6: no aggregate developmental trend (late-vs-early ≈ 0). This means any age effect,
  if real, must be small and would be invisible to G6's aggregate methodology — it
  materially motivated the single-artifact ablation design (paired, within-artifact)
  instead of reusing G6's aggregate-trend approach.
- The R==E structural theorem (P1, `agent_d5_blind/VERDICT.md`): in this INSERT-complete
  substrate, reachability can never be the failure mode. This let PILOT-1 skip building
  a new reachability oracle entirely — any observed usefulness/age relationship is
  attributable purely to search/findability dynamics, not existence or reachability
  differences.
- `m1.py`'s uniform-random draw from `extra_pool` (read directly): this rules out
  sampling-probability bias as a mechanism for any age effect PILOT-1 might find — an
  effect, if present, must arise downstream in GA selection dynamics, not at the draw
  step. This sharpened the hypothesis from "does age affect draw probability" (already
  mechanically answered: no) to "does age affect what happens after the draw."
- `LIB_CAP=64` most-recent-first eviction + genotype dedup (`m1.py` docstring): this
  directly produced Falsifier F3 and Phase 0 step 3 — without checking empirical
  survival horizon first, the offset ladder could not be shown reachable before being
  frozen.

## Unresolved uncertainty

- Whether `agent_d5_blind/developmental_history/final_libraries/lineage_{0..4}.json`
  already contain per-position library snapshots (in which case Phase 0's replay step
  is redundant) or only final states (in which case replay is required) — the files
  were listed but not opened in this budget.
- The exact body of `update_library()` was not read (only its call sites and the
  docstring's "most-recent-first eviction, genotype-deduped" claim). Whether a
  genotype-identical re-admission resets an artifact's age stamp is unconfirmed and
  must be resolved in Phase 0 step 1 before age is defined precisely.
- Whether `results/task_manifest.json` or `PREREG-TASKS.md` place family-similar tasks
  at nearby positions in the frozen sequence — neither was opened in this budget; this
  is the single largest open confound risk (see Expected failure modes) and must be
  checked before the family-matched/mismatched control arm (F5) can be implemented.
- Whether the single-injection ablation (`extra_pool = {g}`) is a faithful enough proxy
  for "usefulness" compared to tracking full multi-generation lineage propagation of an
  immigrant's descendants — PILOT-1 deliberately uses the simpler, cheaper design first;
  a lineage-propagation follow-up is deferred pending PILOT-1's outcome.

## Operation log (numbered; ops used / 15, documents opened / 12)

1. Grep "D-5|D5 findability|d5_findability" over F:\Prometheus — timed out, no result.
2. Glob "**/*d5*" over F:\Prometheus — timed out, no result.
3. Glob "*d5*" under roles/ — no files found.
4. Glob "**/*findability*" over F:\Prometheus — timed out, no result.
5. Glob "*" (top level) over F:\Prometheus — timed out, no result.
6. Bash `ls` top-level F:\Prometheus — success; located `agent_d5_blind/`.
7. Bash `ls` agent_d5_blind/ — success; found MANIFEST/VERDICT/PREREG docs + subdirs.
8. Read `agent_d5_blind/VERDICT.md` — doc 1; verdict, G-gate table, causal decomposition.
9. Read `agent_d5_blind/MANIFEST.md` — doc 2; blind protocol, claim ladder, seed policy.
10. Bash `ls` developmental_history/, results/, learner/ — success; located m1.py,
    run_m1_lineage.py, final_libraries/.
11. Grep m1.py for age/generation/timestamp/reuse keywords — weak hits (only comment
    mentions of "generation" in the docstring sense), motivated a direct read instead.
12. Read `agent_d5_blind/learner/m1.py` (lines 1-120) — doc 3; library cap/eviction,
    uniform-random draw, admissions() filter (solver + top-4 behavior-distinct).
13. Bash `ls` final_libraries/ — success; lineage_0..4.json filenames only, not opened.
14. Read `agent_d5_blind/developmental_history/run_m1_lineage.py` — doc 4; confirmed
    per-artifact admission-position provenance is NOT persisted by the frozen harness,
    only `library_size_at_start`; confirmed shuffled-history snapshot mechanism.

Operations used: 14/15. Documents opened: 4/12. One operation and eight document-opens
of budget were left unused; stopped once the mechanism (library sampling, admission,
eviction) and the two directly relevant prior gates (G6, G9) were grounded directly
against source rather than spending remaining budget on files (task_manifest.json,
PREREG-TASKS.md, update_library() body) that are needed for Phase 0 implementation but
not for specifying the design itself — these are carried forward as Unresolved
uncertainty instead.
