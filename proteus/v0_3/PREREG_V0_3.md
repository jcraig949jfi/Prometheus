# V0.3 Neutrality Crucible — PREREGISTRATION. Frozen before any V0.3 grammar run.

Brief: `roles/Proteus/PROMPT_PROTEUS_V0_3_NEUTRALITY_CRUCIBLE_2026-09-03.txt`, sha256
`78ed8284294b33abea3f7b1a4c0f89f3d95582ea22b337bb3b4e4357ff5679d9`.
Grammar under test: `proteus.grammar.v0.3`, hash recorded in `PREREG_V0_3.json`. The runners
refuse to execute against any other grammar or runtime hash.

## 0. The question

Does repeated mutation produce a reproducible directional attractor that cannot be explained by
finite-state boundaries, representation geometry, or an explicitly characterized null process?

This is not a question about whether organisms are good. No coordinate below is a score, and no
coordinate is optimized. The Foundry is not permitted to landscape the space it measures.

## 1. The one authorized grammar change

`zeroing` (weight 0.04 in v0.2) is removed. It is not replaced. No nulling operator is
introduced. The remaining twelve weights are renormalized mechanically, in their v0.2 order:

```
DENOM = 1.0 - 0.04 = 0.96 ;  w'_i = w_i / DENOM
```

executed in code from the retained v0.2 table, so the code is the record. `reference_redirection`
is retained. The VM, the opcode alphabet, the manifest bounds, the initialization and the probe
ensembles are untouched. `op_zeroing` remains defined solely so the v0.2 grammar stays executable
for reproduction of frozen evidence; it is absent from the active operator table and cannot be
selected by weight or forced by name.

## 2. The battery — every coordinate observed, none removable after the fact

Measured on the same populations at every checkpoint. Vector coordinates are reported per
component; nothing is collapsed into a single score.

1. `genome_length` — mean, median, min, max, variance
2. `opcode_frequency` — 25 components
3. `opcode_class_frequency` — 9 components
4. `operand_distribution` — mean (normalized), fraction below 2^16, zero fraction, 16-bin
   top-nibble histogram
5. `config_fields` — n_regs, log2 tape_words, code_writable fraction, log2 tick_budget,
   log2 out_cap, and the four persist-policy shares
6. `status_proportions` — halt / yield / budget-exhaustion over all probe ticks
7. `executed_instruction_fraction` — fraction of an organism's genome instructions fetched at
   least once across the ensemble (mean, min, max)
8. `transcript_silence_fraction`
9. `transcript_occupancy` — distinct classes, top-class share, entropy, ceiling
10. `knockout_occupancy` — distinct vectors, top share, entropy
11. `status_sequence_occupancy` — distinct sequences, top share, entropy
12. `nop_share` — reported separately because it is the coordinate that failed in V0
13. `mutation_touches_executed_fraction` — fraction of mutation events whose directly altered
    parent instruction indices intersect the parent's executed set

Coordinate 13 needs a definition fixed in advance. The touched set is the set of parent
instruction indices the operator **directly writes, deletes, moves, or copies from**, as recorded
in its own argument record: insertion is charged its boundary index only; deletion, randomization
and splice their whole region; duplication and movement their source region plus destination
index; replacement, reference_redirection and operand_perturbation their single index;
region_swap both regions; config_perturbation nothing. Positional shifting of downstream
instructions is deliberately NOT counted, because under that reading almost every mutation
touches executed code and the coordinate carries no information.

Coordinate 7 requires an instruction trace and the VM may not be altered. A shadow decoder
(`battery.py`) mirrors the VM and additionally records fetched indices; it is differentially
tested against the authoritative VM on every organism measured, and any mismatch of outputs,
status or final state aborts the measurement and is reported as an instrument defect.

## 3. Null controls, published before the V0.3 run

- **NC1 symmetrized reflected walk** — the grammar's own measured length kernel, symmetrized
  (`p_sym(d) = (p(d) + p(-d))/2`), walked under the same reflecting no-op bounds, with no
  content and no VM. Zero drift by construction in an unbounded space, so all NC1 drift is
  boundary and finite-support geometry.
- **NC2 whole-genome uniform resampler** — every mutation redraws the entire genome uniformly at
  fixed length. Stationary content distribution uniform by construction; the analytic opcode
  reference is the exact multinomial from `op = word mod 25`, namely 171798692/2^32 for opcodes
  0..20 and 171798691/2^32 for 21..24 (2^32 = 25·171798691 + 21).
- **NC3 single-site uniform resampler** — every mutation overwrites one uniformly chosen
  instruction with four uniform words; length frozen. Same stationary content law as NC2.
- **NC4 geometry reference** — no mutation at all. Fresh uniform genomes drawn at the *same
  length distribution* the V0.3 population has at that checkpoint. Gives the phenotype
  coordinates implied by length and geometry alone.

Matching: `genome_length` and the numeric configuration coordinates are read against NC1; content
coordinates (2, 3, 4, 12) against NC2/NC3 and the analytic reference; phenotype coordinates
(6, 7, 8, 9, 10, 11) against NC4 at the matched length distribution.

## 4. Decision rule — comparison to nulls, not invented tolerances

No per-coordinate tolerance is declared, because a tolerance chosen by this seat is exactly the
manufactured pass the brief forbids. Instead, for each coordinate:

- drift is the per-lineage change from checkpoint 0 to the final checkpoint, averaged over
  lineages, with a 95% interval from a **lineage-cluster bootstrap** (2,000 resamples, seeded);
- the matched null's drift is computed identically on its own lineages;
- the reported quantity is **Δ = V0.3 drift − matched null drift**, with a bootstrap interval on
  the difference;
- a coordinate is declared to show a **directional effect beyond null** iff that interval
  excludes zero **and** the same sign persists over the second half of the horizon.

Multiplicity is handled and reported both ways: the raw count of coordinates whose interval
excludes zero, the number expected by chance at 95%, and the Holm-corrected set. The
Holm-corrected set is what the verdict uses.

## 5. Crucible design

Cohorts by starting genome length: **1, 8, 32, 128, 256** instructions — 1 and 256 are
bound-adjacent (the cap at a 1024-word tape is 256), 8 and 128 are near-boundary, 32 is interior.
**100 independently seeded lineages per cohort**, **400 generations**, one operator per
generation chosen by the frozen weights, splice mate drawn from another lineage in the same
cohort. Battery checkpoints at generations **0, 25, 50, 100, 200, 400**. Every null control runs
the same cohorts, lineage counts, horizon and checkpoints.

A bounded coordinate moving away from a reflecting wall is **not** a failure by itself; that is
what NC1 measures and it is subtracted. Only movement beyond the matched null is declared.

## 6. Neutral diffusion census (separate experiment)

**400 independent lineages** from the existing frozen uniform initialization (the default Foundry
manifest, unchanged), each undergoing neutral mutation with no selection, no world, no fitness.
Signatures measured at **0, 1, 10, 100, 1,000, 10,000** accepted mutation events. Reported:
cumulative unique transcript classes and knockout vectors, new-class discovery rate per
checkpoint interval, class-occupancy concentration (top share, entropy, Gini), lineage overlap,
independent convergence (classes reached by unrelated lineages), silent/non-silent occupancy,
status-sequence occupancy, phenotype recurrence after departure (a lineage returning to a class
it had left), and the observed transition connectivity between phenotype classes.

No desired answer is defined. A desert is a result, an ocean is a result, islands are a result.
Whether the space *collapses* is judged against NC4 at the same length distribution, not against
an invented floor.

## 7. Probe-ensemble robustness

Six ensembles from public seeds, frozen in `ensembles.py` before any result is examined: E0 (the
V0 ensemble), E1, E2, E3 (same shape, seeds = the committed brief / addendum / affordance-table
hashes), E4 (8 probes) and E5 (2 probes). Each is reported separately. Ensembles are not merged.

## 8. Cross-host replay

A frozen subset is re-executed on every independent runtime available on this machine: CPython
3.11.9 on Windows and CPython 3.12.3 on Linux (WSL2), against CPython 3.12.10 on Windows as the
reference. Byte-level comparison of the same artifacts. A divergence stops the run and is
reported with the first divergent artifact; it is not explained away.

## 9. Verdict, and the order in which conditions are checked

Fixed here so it cannot be chosen afterwards. Multiple failure conditions may be reported; the
final classification is the first that applies, in this order:

1. Shadow divergence, cross-host divergence, or qualitative disagreement between probe ensembles
   about whether phenotype structure exists at all ⇒ `INSTRUMENT_INSUFFICIENT_TO_ADJUDICATE`.
2. Any content or phenotype coordinate with a Holm-corrected directional effect beyond its
   matched null, persisting over the second half of the horizon ⇒
   `NOT_QUALIFIED_DIRECTIONAL_MUTATION_PRIOR_REMAINS`.
3. Diffusion census shows the reachable phenotype set concentrating below the NC4 geometry
   reference — new-class discovery rate falling below NC4's and occupancy concentrating above
   NC4's, both with intervals excluding zero ⇒
   `NOT_QUALIFIED_BEHAVIORAL_SPACE_COLLAPSES_UNDER_NEUTRAL_DIFFUSION`.
4. Otherwise ⇒ `QUALIFIED_AS_NEUTRAL_FOUNDRY_WITH_STATED_BOUNDARY_EFFECTS`, with the boundary
   effects measured by NC1 stated explicitly in the packet.

Boundary effects are expected and are not a failure; they are stated, quantified, and carried.

## 10. Commitments

Nothing in section 1 changes after a result is seen. No coordinate is removed. No tolerance is
introduced. No filtering, seeding, balancing, curriculum, fitness, novelty reward or survival
criterion is added. Failed results are kept under their identity and never repaired. If the
verdict is negative, the packet says so and the seat stops.
