# D-10 — Endogenous Memory Organization: Phase 1 report

**The main experiment has NOT been run. No preregistration is frozen. No
scientific verdict exists.**

Workspace `F:\SerendipityE`. Instrument: Prometheus Serendipity Foundry 0.1.0,
clean-room copy, **source unmodified**. All D-10 material is under `d10/`.

**Recommendation: `REVISE_BEFORE_FREEZE`.** Reasoning in §15.

---

## 1. Operational definition of endogenous memory organization

A **corpus** `C` is a frozen ordered list of artifacts (StackVM genotype byte
strings) with pre-freeze execution history. A **query** is a `TaskEvidence`
(train examples only).

An **organization** is a pair of total functions
`KA : genotype bytes -> 64-bit key` and `KQ : train examples -> 64-bit key`,
plus a supplied retrieval rule: return the `k` corpus artifacts minimising
Hamming distance between their `KA` key and the query's `KQ` key. The
organization *is* the induced structure — which artifacts share a key, which
are Hamming-near, which of the 64 bits are live, and what they separate.

It is **endogenous** iff:

- **E1 substrate provenance** — `KA`, `KQ` are substrate programs with complete
  Foundry lineage terminating in `create_random` with recorded seeds; no
  human- or LLM-authored byte; no `import` op in any organizer lineage.
- **E2 consequence selection** — every survival event's only input was measured
  downstream acquisition outcomes on fitting tasks; the GA replays
  byte-identically from its seeds.
- **E3 no privileged information** — nothing outside the declared encoded input
  reaches `KA`/`KQ`; in particular not `task_id` (a content hash of train *and*
  test), family identity, generator parameters, difficulty, or chronology.
- **E4′ unrestricted function class, supplied geometry** — the key functions are
  unrestricted substrate programs, **but the retrieval geometry (a shared
  64-bit space, Hamming, top-`k`) is supplied and is itself a human-designed
  organizational schema.**

`E4′` replaces a draft `E4` that claimed no distance function, dimensionality
or similarity notion was supplied while the same document supplied all three.
Reviewer A caught the contradiction; it is the single most important correction
in this phase.

## 2. The strongest claim the experiment could actually support

> In one substrate, on one distribution of substrate-generated exact
> program-synthesis tasks, a 64-bit retrieval key function produced by
> substrate search under selection on downstream acquisition consequences
> causes a higher held-out exact-solve rate than no memory, unorganized memory,
> a shipped human-designed organization, a machine-fitted human-designed
> organization, a compute-matched organizer whose selection signal was
> decoupled from the query, **and a compute-matched cold search given the same
> total budget** — surviving ablation, stratified scrambling, query-shuffling
> and transplantation.

Bounded, in advance, by: it cannot show the *notion of nearness* is
machine-created (only the key assignment); it cannot generalise beyond this
substrate and task distribution; it cannot distinguish "groups by family" from
"groups by something correlated with family"; and it cannot show economic
value. Nothing about intelligence, cognition, concepts, or language is in
scope.

## 3. Major contamination / leakage routes

Sixteen threats are enumerated in `d10/prereg/PREREG_DRAFT.md` §3. The ones
that turned out to be **real, present, and measured in my own code**:

| route | status |
|---|---|
| genotype **length** supplied as key-function input word 0, in register `R0` | **CONFIRMED live leak** (§8) |
| the acquisition GA's **byte-lexicographic tie-break** deciding whether injected memory survives | **CONFIRMED live confound** (§8) |
| the organizer fitness **shaping term** being the planted-positive oracle's own relevance criterion | **CONFIRMED ontology smuggle** (§8) |
| corpus **duplicates** breaking "exactly `k` genotypes" | confirmed by reviewer |
| fitting tasks ⊆ history tasks ⇒ organizer degenerates to solver lookup | confirmed as a live ambiguity |
| the `R` null's derangement landing inside the same family | confirmed |
| `task_id` leakage | **closed**, structurally, verified 200/200 |
| held-out test-split reconstruction | judged infeasible (Mersenne Twister inversion needs 624 outputs; 12 are available) |

## 4. Experiment and control architecture

Every arm runs the **identical** acquisition procedure — a fixed-size
population of which exactly `k` members are injected genotypes, identical
budget, identical trial seeds. Arms differ *only* in which `k`.

| arm | injected `k` | isolates |
|---|---|---|
| `N` | fresh random genotypes | no memory |
| `N+` | fresh random, at `B + C_org/(T·S)` | **compute-matched cold search** |
| `U` | uniform corpus sample | unorganized memory |
| `U-len` | random, length/diversity matched to `E`'s retrieved set | material, not relevance |
| `H-fixed` | Foundry Q3 (AURORA-like) top-`k` | human-designed organization |
| `H-fit` | key = `sign(features · W)`, `W_A` (278x64) and `W_Q` (83x64) evolved on the same signal and budget | machine-fitted human organization |
| `R` | E's machinery, family-block-disjoint derangement of fitting evidence | compute-matched, non-task-conditional |
| `R2` | **E's own winner**, query key from another eval task's evidence | **task-conditionality, nothing else varying** |
| `E` | evolved `KA`/`KQ` | the hypothesis |

**Primary contrast: `E − R2`** (adopted from reviewer C over the draft's
`E − R`: it is within-organizer, exactly compute-matched, costs zero extra
construction, and isolates task-conditionality alone). `R` is retained as the
compute-matched secondary null. Secondaries run in a **fixed-sequence
gatekeeping** family, stopping at first non-rejection, so they cost zero α.
Counterfactuals are **gates with pre-declared thresholds, not tests**.

## 5. The information boundary

Exhaustive, machine-hashed in `SUPPLIED_MANIFEST.json`, re-verified after the
run; anything outside it that influenced an organizer's survival invalidates
the run. Supplied: the substrate and its meters; the acquisition procedure; the
endpoint predicate; the raw input encodings; the 64-bit key width; Hamming;
top-`k`; the retrieval step cap; `k` and the budgets; the organizer variation
operators and GA shape; the organizer fitness definition; the task generator,
its filters and its shortcut screen; the corpus construction rule. Emergent:
the key content, which artifacts collide, partition granularity, which bits are
live and what they separate, and what makes an experience relevant.

The boundary is now *tested*, not asserted — `d10/tests/test_boundary.py`,
9/9 passing, including 200/200 identical query keys across differing `task_id`s
and confirmation that scrambling preserves key multiset, granularity and
entropy. Reviewer B correctly notes those tests **cannot fail** and must be
supplemented by *reconstruction probes* (decode family / source-task /
corpus-position from keys alone, against chance, a length-only decoder, and an
oracle-relevance decoder).

## 6. Provenance / origin accounting

Every structural degree of freedom is either in the hashed supplied manifest
(experimenter) or in an organizer genome (machine) — there is no third place.
Per-lineage `ORIGIN_LEDGER.json` records, for each surviving organizer:
`artifact_id`, parents, creation op, `op_seed`, generation, fitness,
`n_distinct_keys`, `live_bits`, `key_entropy_bits`, `retrieval_steps`.
Questions of the form *supplied / learned / selected-on-consequences / random /
inherited / mutated / privileged / LLM-influenced* are answered from the ledger
plus a byte-identical GA replay from seeds.

**Instrument limitation found:** the Court **cannot** adjudicate E1.
`build_blind_view` never exposes `creation_op`, so `run_provenance` cannot
distinguish a lineage rooted in `create_random` from one rooted in `import`.
The audit therefore runs outside the Court and its output is committed into the
case manifest so `_case_commit_hash` binds it.

## 7. Cost model

Four separately metered ledgers, pre-declared: `C_hist` (identical across arms,
charged to none); `C_org` (zero for N/U/U-len/N+, index-build for `H-fixed`,
equal for `E`/`H-fit`/`R`); `C_eval` (**cap-parity**: identical `B`, realised
≤ `B`, reported descriptively); and retrieval key computation in **VM steps**,
never silently converted to evaluations.

Pre-declared in advance: a total-cost loss does **not** invalidate the
mechanism claim (settled by the equal-marginal-budget primary contrast) but
**does** invalidate every efficiency claim. And if **`N+ ≥ E`**, the
organization is dominated by simply searching longer — the mechanism claim
survives, the utility claim fails, and that wording is fixed now rather than
improvised later.

## 8. Preflight measurements and shortcut ceilings

All numbers measured in this workspace; probes and raw logs in
`d10/preflight/`.

**Instrument throughput** — ~1250 evals/s at `max_steps=200`, 20 cases/eval;
2100–2500 evals/s at 10 cases. Genotype length under the acquisition GA:
p50 ≈ 61–79 bytes, max 475.

**The shipped task families are unusable.** All five Foundry synthetic families
give cold-start held-out solve **0.000** at budgets to 2000 (`p4`, `p4b`).
`conditional` reaches 0.45 *train*-exact at 0.000 *test*-exact — pure
overfitting, and the reason the endpoint is always the held-out split.

**A substrate-generated environment was built** (`d10/lib/progtasks.py`): tasks
defined by reference programs in the same substrate, families by mutational
descent. With unbounded 64-bit outputs the landscape is gradient-free (seeding
the population with same-family reference programs yields 0.021). Bounding
reference outputs to `[0,255]` restores gradient through the instrument's own
`cases_passed` fitness — no bespoke shaping function.

**Shortcut ceiling.** The frozen trivial-program screen (all ≤2-instruction
programs + 2000 fixed random programs) rejects **~85 %** of candidate tasks as
trivially solvable. This is a recorded property of the environment.

**Operating point** (`p8` budget curve): only `L_REF = 8` is workable —
cold-start held-out solve 0.000 / 0.042 / 0.167 / 0.208 at `B` = 200 / 800 /
3200 / 12800. `L_REF` 10 and 12 plateau at 0.042.

**Realisable headroom** — the decisive measurement, end-to-end with a real
history phase and the declared corpus rule:

| configuration | history | `N` | `U` | `PP1` (oracle) |
|---|---|---|---|---|
| `n_train=6`, `B_hist=3200`, 48 trials | 1 solve | 0.000 | 0.000 | 0.042 |
| `n_train=10`, `B_hist=3200`, 48 trials | 3 solves | 0.010 | 0.010 | 0.188 |
| **`n_train=10`, `B_hist=12800`, 96 trials** | **11 solves, 25 solver genotypes, corpus 3,962** | **0.021** | **0.031** | **0.344** |

A properly provisioned history phase is what makes the assay viable:
**11× dynamic range, 0.313 absolute**. The first two rows are recorded because
they show how easily this experiment could have been run in a regime where
nothing was measurable.

**Organizer-space reachability** (`p6`, 600 random genomes over a 300-artifact
corpus): 273 collapse to one key, 60 coarse, 68 middle, 142 fine, 57
injective; median distinct keys **2**. 58/60 mutation walks reach a grouping
regime within 40 mutations. Reviewer A rightly notes this shows an undirected
walk reaches a *regime*, not that selection can hill-climb.

**Three confirmed live defects in my own code**, each reproduced independently:

1. **Length leak.** `artifact_words` supplies `len(g)` as word 0, which the VM
   mirrors into `R0`, so the 2-byte program `LDR R0` has key exactly equal to
   genotype length — while the function's own docstring claimed "no length
   bucket". Length separates source history task by **5.7×** (means 22.1 / 85.5
   / 15.1) and within-run position by up to **7.6×** (30.6 → 13.7; 26.7 → 3.5).
   A direct, trivially-reachable channel to chronology and source task.
2. **Tie-break confound.** `acquire` sorts `(-fitness, genotype_bytes)`, and at
   cold start essentially all fitness is tied, so the early GA is a
   lexicographic sort on bytes. Measured over 400 replicates with injected
   genotypes differing only in their leading byte: mean rank 1.55/24 and
   **97.9 %** of elite slots at `0x00`, versus 21.47/24 and **0.0 %** at `0xFF`.
   One content-free byte decides whether retrieved memory survives at all.
3. **Court gates simultaneously unreachable and unfailable.**
   `DEFAULT_MARGINS` are `exact_effect 0.25`, `transfer 0.25` (against a
   measured maximum attainable delta of 0.313 — passable only by a near-oracle
   organizer), `control 0.10` (a control passes iff `|delta| ≤ 0.10`, so it
   cannot fail at realistic deltas), `cost 0.0` (COST passes on any positive
   delta at any cost), `selection_penalty 0.0` (the multiple-comparison
   mechanism is inert), `n_trials` default 8.
   Plus: `_two_arm_effect` requires exact budget equality while `acquire`
   early-stops, so **a real effect fails the gate precisely because it is
   real**; and `run_key` passes `timeout_s=5.0`, making the organization itself
   wall-clock-dependent and therefore not reproducible.

## 9. Planted-instrument designs

- **PP1 — assay sensitivity (privileged).** Retrieve the `k` corpus artifacts
  with highest true train fitness. Exercises the whole pipeline and sets the
  ceiling. Measured: 0.344 vs `U` 0.031. Never admitted as evidence.
- **PP2 — mechanism-faithful positive.** A hand-written `KA`/`KQ` pair using no
  privileged information. **Promoted to a hard pre-freeze gate**: if no
  hand-written pair can beat the null under the frozen interface, the interface
  — not the hypothesis — is what would be measured, and the design must change.
- **PN1 — id-hash key.** `KA = sha256(artifact_id)`, constant `KQ`. Must not
  beat `U`.
- **PN2 — scrambled winner.** Must not beat `U`.
- **Stratified scramble and query-shuffle** replace the naive scramble, which
  reviewer B showed preserves only the statistics my own test checked while
  destroying key↔length, key↔first-byte, key↔multiplicity and key↔quality — so
  "E > scramble" licenses only *"the key assignment carries information"*, never
  *"task-conditional relevance"*.

## 10. Statistical design and experimental units

**Unit: the lineage.** Every trial in a lineage-arm cell is driven by one draw
of an organizer, so `L` is the sample size — not `L × T × S`. Naive pooling
gives a simulated 29–49 % Type-I error under a true null.

Per lineage `l`, paired trial indicators under common random numbers give
`d_l`. Primary test: exact one-sided **sign-flip permutation** over `{d_l}`;
CI by **two-way cluster bootstrap** over lineages *and* eval families; GLMM as
sensitivity only, with non-convergence pre-declared as "not a result"; and the
invalid pooled analysis reported and labelled invalid.

Hard floor `L ≥ 8` (minimum attainable one-sided `p = 2^-L`). `F_eval ≥ 24`
distinct eval families, ≥ 8 expected successes per lineage-arm cell.
**`L` cannot be set until `σ_org` — the between-lineage sd of organizer quality
— is measured**, because once `σ_org ≥ 2Δ` the required `L` is ~30 and adding
tasks or seeds buys nothing. Provisional design point pending that
measurement: `L = 16`, `F = 24`, `T = 48`, `S = 5`.

Secondary endpoint: **held-out test cases passed (0–20)** by the final
best-by-train individual. The draft's "evaluations-to-test-solve" is *not
measurable* — `acquire` halts on first *train*-exact success.

## 11. Causal interventions

Bit ablation on live bits; stratified scramble; query-shuffle; bag control;
transplantation across lineages; held-out families; matched-random organizer at
matched granularity. All at cap-parity budget. Court claim type must be
declared `index_effect` or `relational_organization`, or both organization
controls are silently inapplicable while `CURRENT_UTILITY` remains reachable.

## 12. Adversarial review and resulting changes

Three independent hostile reviewers with disjoint mandates. Records preserved
in `d10/review/REVIEW_RECORD.md`, `REVIEW_RECORD_B.md`, `REVIEW_RECORD_C.md`,
with every finding marked CONFIRMED-BY-REPRODUCTION, CONFIRMED, or
ACCEPTED-UNVERIFIED. **Thirty-eight findings; fifteen judged blocking.** I
reproduced the six most consequential myself rather than taking them on trust
(and failed to reproduce one reviewer's specific 65× figure using a different
statistic — recorded as such).

Changes made or committed to as a result:

| change | source |
|---|---|
| `E4` deleted; replaced by `E4′`, which admits the supplied geometry | A-F1 |
| the object renamed *endogenous relevance keying*; claim scope reduced | A-F2 |
| query-dependent tiebreak; granularity gate; reachable-set reporting | A-F3 |
| retrieval seed derivation preregistered | A-F4 |
| **no-shaping organizer arm becomes primary**; shaped arm demoted, coefficient capped | A-F5 |
| acquisition spends the full budget and collects *all* train-exact solutions | A-F6 |
| PP2 promoted to a hard pre-freeze gate | A-F7 |
| encoding constants and padding dropped; positional bias recorded; encoding-variant arm | A-F8 |
| two independent organizer chromosomes; fitness-autocorrelation check | A-F9 |
| family generation uses a different mutation config from the searcher's | A-F10 |
| `len(g)` deleted from `artifact_words`; MI-to-oracle-variables reported | B-A1 |
| audit replaced by reconstruction probes | B-A2 |
| corpus de-duplicated by content address | B-B1 |
| three-way task split enforced; fitting-task solvers excluded from corpus | B-B4 |
| **seeded-hash fitness tie-break** in both sort sites | B-C1 |
| σ deranges *family blocks*; realised same-family rate required to be 0 | B-D1 |
| history phase runs evented so the H arms get their declared features | B-D2b |
| `H-fit` steel-manned: real evolved `W_A`, `W_Q` matrices | B-D3, A-F12 |
| stratified scramble + query-shuffle replace the naive scramble | B-D4 |
| lineage-audit output committed into the hashed case manifest | B-E |
| sign-flip permutation + two-way cluster bootstrap | C-1 |
| `F_eval ≥ 24`; `F` reported as the task-side sample size | C-2 |
| `σ_org` pilot made a pre-freeze requirement | C-5 |
| test-cases-passed replaces the unmeasurable time-to-solve endpoint | C-9 |
| fixed-sequence gatekeeping; counterfactuals become gates; cell frozen first | C-11 |
| **`R2` adopted as the primary null**; `R`'s `KQ` sensitivity reported | C-12 |
| winner sealed and hashed before the eval process starts; shrinkage reported | C-13 |
| all Court margins re-derived from the measured range; `selection_penalty > 0`; CI bounds instead of point estimates | C-14 |
| **arm `N+` added**; cold-start curve extended to `B'` | C-17 |
| cap-parity replaces realised-count budget equality | C-V3 |
| key metering made purely step-based | C-V5 |

## 13. The draft preregistration

`d10/prereg/PREREG_DRAFT.md` — complete but **superseded in the ~30 places
listed in §12**. It is retained unedited as the pre-review artifact so the
review record is auditable against what was actually reviewed. A revised draft
incorporating every accepted repair is the first deliverable of the next phase.

## 14. Unresolved threats

1. **`σ_org` is unmeasured.** `L` cannot honestly be preregistered without it.
   Requires ≥ 4 pilot lineages through the full pipeline.
2. **Capacity is unproven.** Random key programs execute a median of ~20 VM
   steps; `KA` cannot compute the byte histogram that `features.py` hands the
   H arms for free. Until a hand-written `KA`/`KQ` beats the null under the
   frozen interface, a null result would measure the interface, not the
   hypothesis. **This is the one open item that could still make the assay
   non-viable.**
3. **The transfer ceiling is entirely unmeasured.** Only the same-family
   condition has a measured ceiling (0.344).
4. **The supplied Hamming geometry does a large share of the selection work.**
   Mitigated by a comparison-robustness arm, not eliminated. The claim is
   bounded accordingly.
5. **Organizer-genome modularity** — ~32 % of single mutations rewrite both
   `KA` and `KQ`. The two-chromosome repair is specified but not yet validated
   by a fitness-autocorrelation measurement.
6. **`H-fixed` is answered by construction** — Q3's query side is documented by
   the instrument itself as pure seeded noise, so `H-fixed − U` measures the
   instrument's declared design, not a fact about human-designed organization.
7. **The Court cannot verify information hygiene** — it never sees the
   encoders, the corpus, or σ, and cannot check that a shuffle is a shuffle.
   The preregistration, not the Court, must carry this.
8. **Preflight already swept 72 operating-point cells.** The chosen cell must be
   frozen before any eval task is generated, and results reported for that cell
   only.

## 15. Recommendation

**`REVISE_BEFORE_FREEZE`.**

Not `READY_TO_FREEZE`: fifteen blocking findings survived review, three of them
confirmed live defects in my own code that would each independently have
produced a contaminated positive or an uninterpretable null — a supplied
genotype-length channel straight into the key function, a content-free byte
that decides whether retrieved memory survives at all, and an organizer fitness
shaping term that is literally the planted-positive oracle's own relevance
criterion. That last one is the charter's central failure mode occurring inside
the design meant to prevent it. Beyond my own code, the Foundry Court's default
margins make its gates simultaneously unreachable and unfailable, and its
budget-equality requirement fails an effect *because* it is real.

Not `ASSAY_NOT_VIABLE`: the environment works at a measured operating point
with an 11× dynamic range (`N` 0.021, `U` 0.031, oracle 0.344) and a history
phase that deposits real material; the shortcut ceiling is measured (~85 % of
candidate tasks rejected); the information firewall on the query side holds
structurally and is tested; the organizer's grouping regime is reachable; and
**every blocking finding has a concrete, named, affordable repair**. Total
compute is ~10–14 hours on this hardware.

Two hard gates must be passed before any freeze, in this order:

1. **Capacity gate.** Exhibit a hand-written `KA`/`KQ` pair that beats the
   null under the frozen interface. If none can be constructed by hand,
   evolution will not find one, and the honest verdict becomes
   `ASSAY_NOT_VIABLE` for this interface.
2. **`σ_org` gate.** Measure between-lineage organizer-quality variance from
   ≥ 4 pilot lineages and set `L` from it. Preregistering `L` without this is
   preregistering a guess.

The desired outcome of this phase was an experiment in which, if organization
appears, we can tell who put it there. It is not there yet — but the three
places where *I* had put it are now identified, measured, and have repairs.

---

## Addendum — a preserved failure, and one more cost-model defect

The `p11` (k x budget) sweep **crashed** and is preserved rather than
discarded (`d10/preflight/p11.log`). Two separate facts came out of it.

**1. Determinism cross-check (unplanned, and it passed).** `p11` and `p10` ran
the identical history phase in two separate processes and produced
byte-identical summaries: `history_trials=96 history_test_solves=11
n_solver_genotypes=25 all_artifacts=1011559 corpus=3962`. That is an
independent confirmation that the history phase and the corpus rule are
deterministic in their seeds across processes.

**2. `MemoryError` in the eval phase**, inside
`StackVMAdapter.recombine` (`a[:cut_a] + b[cut_b:]`) at `B=6400`:

```
File "d10/lib/acquire.py", line 99, in acquire
    child = engine.recombine(pa[0], pb[0], recombine_s.next())
File "foundry/engines/gp/stackvm/adapter.py", line 158, in recombine
    return a[:cut_a] + b[cut_b:]
MemoryError
```

*Cause not isolated.* The probe retained all ~1.01 M history genotypes in
memory while a second process did the same concurrently, so the most likely
cause is probe-level memory pressure rather than runaway genotype growth — the
measured maximum genotype length (below) is far too small to exhaust memory on
its own. Recorded as unexplained rather than explained away.

*Practical implication for the main run:* the corpus rule cannot hold a
lineage's full history in memory. At `L = 16` lineages x ~1 M artifacts the
history must be streamed and subsampled online, and the corpus written to the
fossil store rather than accumulated in a list.

**3. A cost-model defect this exposed: steps per evaluation is not constant.**
Measured on a single cold-start acquisition run:

| budget `B` | mean genotype length | max | **VM steps / evaluation** |
|---|---|---|---|
| 1,600 | 23.2 | 110 | **247** |
| 6,400 | 118.9 | 415 | **1,130** |
| 25,600 | 157.9 | 561 | **1,481** |

`EngineLimits.max_genotype_bytes` defaults to 1,000,000 and the adapter only
*penalises* an oversize genotype after the fact — nothing bounds growth. So
**a 6x swing in VM steps per evaluation**, driven by genotype length, sits
inside a budget the cost model treats as matched.

This is a genuine addition to threat **T16** and to the cost model in section 7:
matched `acq_evals` does **not** imply matched compute, and an arm can gain by
retrieving *longer* genotypes that buy more VM steps per evaluation — with no
task-conditional relevance whatsoever. The `U-len` arm partially controls for
it, but only for length, not for realised steps.

**Repairs added to the pre-freeze list:** meter **VM steps as a first-class
budget alongside evaluations**, report steps-per-evaluation per arm, bound
genotype length explicitly in the acquisition harness, and stream the history
phase instead of retaining it.
