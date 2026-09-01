# D-10 - Endogenous Memory Organization
## DRAFT preregistration - NOT FROZEN - SUPERSEDED BY REVIEW

> **STATUS: pre-review artifact, retained UNEDITED on purpose.**
> Adversarial review produced 38 findings, 15 of them blocking, which supersede
> this draft in ~30 places. See `d10/PHASE1_REPORT.md` section 12 for the change
> list and `d10/review/REVIEW_RECORD*.md` for the findings and adjudications.
> This file is kept as-written so the review record can be audited against what
> was actually reviewed. Do NOT freeze it. Known-superseded highlights: `E4`
> (false as written), the `+0.01x` fitness shaping term, `E - R` as the primary
> contrast, `evaluations-to-solve` as the secondary endpoint, and the absence of
> an `N+` compute-matched arm.


**Status: DRAFT. The main experiment has NOT been run. No verdict exists.**

Instrument: Prometheus Serendipity Foundry 0.1.0, clean-room copy at
`F:\SerendipityE` (transferable-subset tree hash `71feebc474be88696695ac653eaa3ea23fddb5a5e3f2d780ca63e7d13ed471d7`,
full gate 465 passed / 0 failed, twice). Instrument source is **unmodified**.
All D-10 material lives in `d10/` and is experimental, not instrument.

---

## 0. The claim ceiling

The strongest claim this design could support is:

> In one substrate (`stackvm-v1`), on one distribution of substrate-generated
> exact program-synthesis tasks, a 64-bit retrieval key function that was
> itself produced by substrate search under selection on downstream
> acquisition consequences causes a higher held-out exact-solve rate than
> (a) no memory, (b) unorganized memory, (c) a shipped human-designed
> organization, (d) a machine-fitted instance of a human-designed
> organization, and (e) an identically-evolved, compute-matched organizer
> whose selection signal was decoupled from the query task — and the effect
> survives bit ablation, statistics-preserving scrambling, and transplantation
> to held-out task families.

It could **not** support any claim about intelligence, cognition, concepts,
language, abstraction, understanding, world-models, or "alien reasoning". It
could not support a claim about other substrates, other scales, or other task
distributions. A maximal positive result is: *a machine-produced hash function
beat every control we could build.* That is intended to sound narrow.

---

## 1. Operational definition

Let a **corpus** `C` be a frozen, ordered list of artifacts (StackVM genotype
byte strings) with their pre-freeze execution history. A **query** is a
`TaskEvidence` — train examples only — for a new exact task.

An **organization** is a pair of total functions

    KA : genotype bytes  ->  64-bit key
    KQ : train examples  ->  64-bit key

together with the supplied retrieval rule: return the `k` corpus artifacts
minimising Hamming distance between their `KA` key and the query's `KQ` key,
ties broken by a deterministic hash of `(seed, artifact_id)`.

The organization **is** the induced structure on `C`: which artifacts share a
key, which are Hamming-near, which of the 64 bits are live, and what those
bits separate. It answers, mechanically, every question the charter poses:
what is retrieved (top-`k`), what is near or far (Hamming), which distinctions
are preserved (live bits) and which are discarded (collapsed bits and key
collisions).

An organization is **endogenous** iff all four hold:

- **E1 — substrate provenance.** `KA` and `KQ` are substrate programs whose
  bytes have a complete Foundry lineage terminating in `create_random` events
  with recorded seeds. No byte was authored by a human or an LLM. No `import`
  creation-op appears anywhere in an organizer lineage. *Mechanically checked
  by `store.lineage()` traversal; a gap raises.*
- **E2 — consequence selection.** Every surviving organizer survived selection
  events whose only input was measured downstream acquisition outcomes on
  *fitting* tasks. *Checked by replaying the recorded organizer GA from its
  seeds and reproducing the identical lineage.*
- **E3 — no privileged information.** Neither `KA` nor `KQ` can read anything
  outside its declared encoded input. In particular `KQ` cannot read
  `task_id`, family identity, generator parameters, difficulty, chronology,
  archive occupancy, or admin metadata. *Structural: the encoders in
  `d10/lib/organizer.py` take those values nowhere; asserted by a source audit
  test and by a differential test (two tasks with identical train examples but
  different held-out splits must produce byte-identical query keys).*
- **E4 — no human function class.** The hypothesis space of `KA`/`KQ` is "all
  substrate programs executable within `KEY_MAX_STEPS`", not a
  human-parameterised family: no feature list, no distance function on
  features, no dimensionality, no clustering criterion, no similarity notion.

This definition is deliberately narrow and auditable. It says nothing about
whether the organization is interpretable, elegant, or concept-like — those
are different questions (charter §5).

---

## 2. The information boundary

Exhaustive. Everything in the left column is enumerated in
`d10/prereg/SUPPLIED_MANIFEST.json`, content-hashed before the run, and
re-verified after. **Anything not in that manifest that influenced an
organizer's survival is a preregistration violation and invalidates the run.**

| SUPPLIED (frozen, identical in every arm) | MAY EMERGE |
|---|---|
| substrate `stackvm-v1`, `EngineLimits(max_steps=200, timeout_s=5.0)` | the byte content of `KA` and `KQ` |
| acquisition procedure: elitist GA, `POP_SIZE=24`, `N_ELITES=2`, `TOURNAMENT_K=3`, `P_CROSSOVER=0.5` | which artifacts collide into one key |
| endpoint predicate: exact equality on the held-out split | the granularity of the partition (`n_distinct_keys`) |
| input encodings `artifact_words`, `evidence_words` | which of the 64 bits are live |
| key width = 64 bits | what the live bits separate |
| comparison = Hamming; selection = top-`k`, hash tiebreak | which artifacts are near / far |
| retrieval step cap `KEY_MAX_STEPS` | which distinctions are preserved vs discarded |
| `k` = number of injected genotypes; budgets `B_hist`, `B_org`, `B_eval` | what makes an experience relevant to a query |
| organizer variation operators (substrate `mutate`/`recombine`) and organizer GA shape | |
| organizer fitness *definition* (§5.3) | |
| task generator, its filters, and the trivial-program shortcut screen | |
| the corpus construction rule (§4.3) | |

**Declared limitation.** Perfect independence is impossible (charter §3). The
supplied comparison (Hamming on 64 bits) is a real, non-trivial piece of
supplied structure, and the claim is explicitly bounded by it: this experiment
can say that the *key assignment* was machine-created, never that the
*notion of nearness* was.

---

## 3. Threat model

Each threat maps to a named control or detector.

**T1 Task-identity leakage.** `TaskEvidence` carries `task_id`, a content hash
over *all* train and test cases — a perfect task fingerprint. *Control:*
`evidence_words` never touches it. `test_no_task_id_leak` asserts this by
source audit and by a differential test.

**T2 Generator-family leakage.** Family identity is oracle-side only
(`admin_metadata`), stripped by `FrozenStoreView`, never encoded. Recovering
family *from raw evidence* is the phenomenon, not a leak, provided nothing
hands it over. *Control:* no learner-, index-, or organizer-visible surface
carries a family label; the transfer endpoint uses families absent from
history and fitting.

**T3 Chronology / occupancy proxies.** Execution counts, archive residency and
event order correlate with which history task an artifact was evolved on.
*Control:* `artifact_words` encodes genotype bytes only — no execution
statistic reaches `KA` at all. This is a deliberate tightening beyond the
Foundry's own `features.py`, which does encode execution aggregates.

**T4 More material / bigger memory.** *Control:* every arm injects **exactly**
`k` genotypes into an identically-sized population under an identical budget
with identical trial seeds. The no-memory arm injects `k` fresh random
genotypes. Arms differ only in *which* `k`.

**T5 More compute.** *Control:* `E`, `H-fit`, `R` receive byte-identical
organizer search budgets. `org_evals` is metered per arm and equality is
asserted; inequality invalidates the run.

**T6 Retrieval-time search smuggling.** A key program could run a search
inside itself. *Control:* capped at `KEY_MAX_STEPS` per key; total retrieval
steps metered and reported per arm.

**T7 Selection on the endpoint.** *Control:* organizer fitness uses
*train*-exact success on *fitting* tasks; the endpoint is *test*-exact success
on *eval* tasks. The pools are disjoint by construction and their seed
derivations are recorded.

**T8 Overfitting the endpoint by luck.** With `n_train=6` and outputs in
`[0,255]`, the chance a random program matches all 6 train cases is
`~(1/256)^6`. Preflight measured a real train/test gap at longer reference
programs (L=20: train 0.25 vs test 0.021), so the endpoint is **always** the
held-out split and the gap is reported.

**T9 Deterministic shortcut in the environment.** Preflight found **~85 % of
candidate tasks are solvable by a trivial program**. *Control:* every task is
screened against a frozen trivial-program set (all ≤2-instruction programs +
2000 fixed random programs); the rejection rate is a recorded property and the
pass-through rate is the declared shortcut ceiling.

**T10 Selection over lineages.** *Control:* all lineages count; none is
dropped after seeing its result; the primary test's unit is the lineage.

**T11 Multiple comparisons.** *Control:* one named primary contrast;
everything else secondary with Holm correction inside a declared family.

**T12 Non-independence.** *Control:* the primary analysis reduces each lineage
to a single paired difference before testing. No trial-level test is used for
the primary endpoint.

**T13 Instrument fabricating signal.** *Control:* a planted-negative organizer
and the Court's `NULL` predicate must both show no effect. If either shows
one, every measured effect is suspect and the verdict is `ASSAY_PERMISSIVE`.

**T14 LLM influence on survival.** The only LLM-authored bytes are harness
code and the two planted controls (explicitly flagged). No LLM inspects,
ranks, selects, edits, or interprets an organizer at any point. *Checked by
E1 plus the no-`import` lineage audit.*

**T15 Degenerate-organizer aliasing.** An organizer assigning every artifact
the same key reduces retrieval exactly to `U`; one assigning all-distinct keys
reduces it to an arbitrary content-hash neighbourhood. Preflight found these
regimes dominate random initialisation (273/600 collapsed; 57/600 injective).
*Control:* `n_distinct_keys`, `live_bits` and `key_entropy_bits` are recorded
for every shipped organizer, so a "win" produced by collapsing into a control
arm is visible rather than mysterious.

**T16 Injected-genotype length/diversity confound.** Retrieved genotypes could
help merely by being longer, shorter, or more mutable. *Control:* a
length-matched random control (`U-len`) injects random genotypes whose lengths
match the winning arm's retrieved lengths, and injected-set length and
pairwise-distance statistics are recorded per arm.

---

## 4. Environment, corpus, and splits

### 4.1 Task generation (`d10/lib/progtasks.py`)

A task is defined by a **reference program** in the same substrate the learner
searches. Declared rationale: exact solvability is guaranteed by construction
(so a null is a hypothesis failure, not an unreachable target), difficulty has
a mechanical dial, family members share reusable substructure by descent, and
no human semantic category enters the environment.

- A **family** = a random reference program (`root`, length `L_REF`) plus its
  mutational neighbours (`N_MUT` substrate mutations). "Same family" is a fact
  about substrate descent; no learner, index or organizer can read it.
- A **task** = a family member program, `N_TRAIN=6` train cases and
  `N_TEST=20` disjoint test cases, inputs uniform on `[0,255]^2`.
- Reference programs are filtered to: halt within `MAX_REF_STEPS=64`; produce
  outputs in `[0, 255]`; and yield ≥ 16 distinct outputs over 40 probe inputs.
- Every task is **shortcut-screened** and rejected if any member of the frozen
  trivial-program set reproduces train+test exactly.

### 4.2 Splits

| pool | families | members | used for |
|---|---|---|---|
| **history** | `F_SEEN` seen families | members 0…`H-1` | the history phase that builds the hoard |
| **fitting** | the same `F_SEEN` families | members `H`…`H+G-1` | organizer fitness only |
| **eval-primary** | the same `F_SEEN` families | members `H+G`… | the primary endpoint |
| **eval-transfer** | `F_NEW` families never used anywhere | all | the transfer endpoint |

All four pools are disjoint at the *task* level; history/fitting/eval-primary
share family structure by design (that is the reusable structure the
organization is supposed to find); eval-transfer shares nothing.

### 4.3 Corpus construction (supplied, arm-neutral)

The corpus is, per lineage:

    C = (union of the FINAL POPULATION of every history search)
      ∪ (every history search's solver genotype, if any)
      ∪ (a uniform random subsample of size N_SUB of all history artifacts)

All three components are recorded separately. This rule is **supplied** and
identical for every arm, so it cannot differentially favour any arm; it is
declared rather than disguised as "raw experience", because a purely uniform
subsample of a large history contains almost no useful material (preflight
`p7`: 0 solvers in 36 history trials at `B=800`; realizable oracle ceiling
only 0.130 vs 0.019 uniform).

The corpus is frozen as a Foundry `FrozenCorpus` (content-hashed, with a
ledger high-water mark) before any organizer is built.

---

## 5. Arms

Every arm runs the **identical** acquisition procedure (`d10/lib/acquire.py`):
a population of `POP_SIZE`, of which exactly `k` members are injected
genotypes and the rest fresh random, under an identical budget `B_eval` and
identical trial seeds. The endpoint is test-split exact solve, checked
oracle-side and never visible to the search.

| arm | which `k` genotypes | organizer compute |
|---|---|---|
| **N** | `k` fresh random genotypes | none |
| **U** | `k` uniformly sampled corpus artifacts | none |
| **U-len** | `k` fresh random genotypes, lengths matched to `E`'s retrieved set | none |
| **H-fixed** | top-`k` from the Foundry's shipped Q3 (AURORA-like) index on the same frozen corpus | Q3 build cost |
| **H-fit** | top-`k` by Hamming over a 64-bit key formed as `sign(standardised features.py vector · seeded projection)`, where an evolved byte genome selects the active-feature mask and the projection seed | identical to `E` |
| **R** | identical machinery to `E`, identical compute, but during organizer fitness the evidence given to `KQ` comes from a fixed derangement of the fitting-task list | identical to `E` |
| **E** | top-`k` by Hamming over evolved `KA`/`KQ` key programs | the reference budget |

### 5.1 What each contrast isolates

| contrast | isolates | charter category |
|---|---|---|
| `U − N` | does accumulated experience help at all | 1 vs 2 |
| `H-fixed − U` | does a human-designed organization help | 3 |
| `H-fit − H-fixed` | does fitting parameters inside a human ontology help | 4 |
| `R − U` | does compute-matched, non-task-conditional organization help | 2/3 boundary |
| **`E − R`** | **primary**: does selection on downstream consequences *for this query* add causal utility, with function class and compute matched | 5 |
| `E − H-fit` | does the universal function class add utility, with selection signal and compute matched | 5 vs 4 |
| `E-transfer − R-transfer` | does the structure generalise to unseen families | 6 |

### 5.2 Organizer search (arms E, R, H-fit — byte-identical shape)

Population `P_ORG`, `G_ORG` generations, elitism 2, tournament 3,
`p_crossover 0.5`, variation by the substrate's own `mutate` / `recombine`.
Every organizer genome is registered in the Foundry `FossilStore` with real
parents, creation op and seed, and every creation emits a ledger event — so
E1/E2 are auditable from the ledger alone.

### 5.3 Organizer fitness (supplied)

    fitness(org) = mean over fitting trials of [ train-exact solved ]
                 + 0.01 * mean over fitting trials of [ best train fitness ]

Fitting trials = `N_FIT_TASKS × N_FIT_SEEDS` acquisition trials at budget
`B_ORG`, seeded with the organizer's own top-`k` retrieval. The `0.01` term is
a **supplied shaping tiebreak**, declared in the supplied manifest, and is
identical in `E`, `R` and `H-fit`. Its necessity is empirical: preflight shows
the un-shaped landscape is near-flat at these budgets.

---

## 6. Provenance / origin accounting

For every structural degree of freedom of a shipped organization, the
following must be answerable *after* the run from recorded evidence alone:

| question | mechanism |
|---|---|
| who chose this degree of freedom? | it is either in `SUPPLIED_MANIFEST.json` (experimenter) or in an organizer genome (machine). There is no third place. |
| was it supplied before the run? | manifest hash recorded in the ledger before the first history event |
| was it learned from experience? | organizer lineage: `ARTIFACT_CREATED/MUTATED/RECOMBINED` events with `op_seed` and `parent_ids` |
| was it selected because of downstream consequences? | the recorded per-generation fitness table + full GA replay from seeds |
| was it random? | `create_random` op with a recorded seed, replayable |
| was it inherited? | `parent_ids` chain in `FossilStore.lineage` |
| was it mutated? | `ARTIFACT_MUTATED` event with `op_seed`; the exact byte diff is recomputable |
| derived from privileged information? | E3 source audit + differential key test; plus a post-hoc mutual-information check between shipped keys and each oracle-side variable (family id, difficulty, chronology index, history-task id) — reported, not gating |
| could an LLM or human interpretation have influenced survival? | no `import` op in any organizer lineage; the GA replay reproduces the identical winner from seeds alone |

An **`ORIGIN_LEDGER.json`** is emitted per lineage: one row per surviving
organizer, with `{artifact_id, parents, op, op_seed, generation, fitness,
n_distinct_keys, live_bits, key_entropy_bits, retrieval_steps}`.

---

## 7. Cost model (declared before results)

Three meters, all pre-declared:

1. **`acq_evals`** — engine evaluations inside acquisition trials.
   **Must be exactly equal across arms at evaluation time.** Inequality
   invalidates the run.
2. **`org_evals`** — engine evaluations spent constructing the organization.
   Must be exactly equal across `E`, `H-fit`, `R` by construction; `N`, `U`,
   `U-len` have zero; `H-fixed` has its Q3 build cost.
3. **`ret_steps`** — VM steps spent computing keys (corpus-side at build,
   query-side per query) plus Hamming comparisons. Reported per arm; bounded
   by `KEY_MAX_STEPS`.

**Primary accounting rule.** The primary endpoint compares arms at *matched
`acq_evals`*. **Secondary accounting rule.** The amortised total
`acq_evals + org_evals / n_eval_trials` is reported for every arm.

**Declared in advance:** at this scale `E` is *expected to lose* on amortised
total cost. That loss does **not** invalidate the primary result; it bounds
the claim to *"organization has causal utility at matched retrieval-time
cost"* and forbids the claim *"memory organization is economical"*.

---

## 8. Planted instruments (must pass before the main run)

### PP1 — assay sensitivity (privileged, never admitted as evidence)
Retrieve the `k` corpus artifacts with the highest **true** train fitness on
the eval task (oracle-side ranking). This exercises the entire
retrieval → injection → acquisition → endpoint pipeline and gives the
achievable ceiling. **Gate:** PP1 must beat `U` by a pre-registered margin
with the pre-registered test. Preflight (`p7`) measured PP1 = 0.130 vs
`U` = 0.019 vs `N` = 0.000 on a real corpus.

### PP2 — mechanism-faithful positive (hand-written key program)
A hand-written StackVM key program pair, using **no privileged information**,
that computes keys from raw encoded words only and is known to group
same-family material above chance. **Gate:** PP2 must beat `U`. PP2's role is
to separate *hypothesis failure* from *search failure*: if `E` fails but PP2
succeeds, the mechanism is measurable and evolution did not find it →
`HYPOTHESIS_FAILURE_SEARCH`, not `ASSAY_INSENSITIVE`. PP2 is authored by the
experimenter and is flagged `origin=HUMAN_AUTHORED`; it is never counted as
endogenous.

### PN1 — planted negative (id-hash key)
`KA(g) = sha256(artifact_id)[:8]`, `KQ` constant. Keys are maximally
informative about identity and maximally uninformative about content or
relevance. **Gate:** PN1 must **not** beat `U` by the margin. If it does,
verdict `ASSAY_PERMISSIVE` and the main run does not happen.

### PN2 — planted negative (scrambled winner)
Take PP2's key assignment and permute keys across artifacts, preserving key
multiset, entropy, bit marginals and granularity exactly. **Gate:** must not
beat `U`.

**Instrument sanity checks** (all must pass, recorded):
`ledger.verify()` clean; corpus hash reproducible; organizer GA replays
byte-identically from seeds; `acq_evals` equality across arms; E3 differential
key test; no-`import` lineage audit; `SUPPLIED_MANIFEST.json` hash unchanged
before and after.

---

## 9. Statistical design

**Experimental unit: the lineage.** A lineage is one independent history
phase, its own corpus, and its own separately-evolved organizers. Lineages are
independent by construction (disjoint seed streams, disjoint history tasks).
Trials within a task, and tasks within a family, are correlated and are
**never** treated as independent.

**Reduction.** For lineage `ℓ` and arm `a`, let `p̂(ℓ,a)` be the test-exact
solve rate over the full eval-primary trial grid (`N_EVAL_TASKS × N_EVAL_SEEDS`
trials, identical seeds across arms). The per-lineage paired difference for a
contrast `a−b` is `d(ℓ) = p̂(ℓ,a) − p̂(ℓ,b)`.

**Primary endpoint.** `E − R` on eval-primary. Test: two-sided Wilcoxon signed
rank over the `L` per-lineage paired differences, α = 0.05, with an
accompanying bootstrap CI over lineages. **Effect-size requirement:** the
point estimate of mean `d` must additionally exceed `Δ_MIN` (a pre-registered
absolute solve-rate difference set from the PP1 ceiling, §11) — a
statistically significant but negligible difference is recorded as
`NULL_EFFECT_TOO_SMALL`.

**Secondary endpoints** (Holm-corrected within one declared family):
`E − H-fit`, `E − U`, `R − U`, `H-fit − H-fixed`, `H-fixed − U`, `U − N`,
`E − U-len`, and the transfer contrast `E − R` on eval-transfer.

**Secondary continuous endpoint** (pre-declared because the binary endpoint
sits near the floor): evaluations-to-first-test-exact-solve, censored at
`B_eval`, compared by a log-rank test on per-lineage pooled trials with the
lineage as a stratum. Reported alongside; never substituted for the primary.

**Selection-of-the-winner correction.** Each lineage's shipped organizer is
the winner of its own GA, i.e. a selected statistic. Two mitigations, both
pre-registered: (i) the winner is selected **on fitting tasks only** and
measured on disjoint eval tasks, so the selection is not on the endpoint;
(ii) the Court's `n_candidates_considered` is set to the number of organizer
candidates evaluated per lineage and the multiple-comparison margin inflation
in `foundry/court/predicates.py` is applied.

**Power.** `L`, `N_EVAL_TASKS` and `N_EVAL_SEEDS` are fixed in §11 from the
measured PP1 ceiling so that the design has ≥ 80 % power against a true effect
of `Δ_MIN`. If the realised PP1 ceiling in the planted-instrument phase is
below the value assumed, the run is declared `UNDERPOWERED` **before**
unblinding and is not run.

**Stopping rule.** No interim looks at the primary endpoint. The full grid is
run to completion or the run is invalid.

---

## 10. Causal interventions

Applied to each lineage's shipped `E` organizer, all at matched `acq_evals`:

1. **Bit ablation.** For each live bit `b`, mask bit `b` on both sides and
   re-run the full eval grid. Reports which coordinates carry the effect.
2. **Statistics-preserving scramble.** Permute keys across artifacts,
   preserving key multiset, entropy, bit marginals and granularity. The effect
   must vanish. *(This is the Court's `SHUFFLE_CONTROL`.)*
3. **Bag control.** Same retrieved *material*, no organization: for each eval
   task, inject `k` artifacts sampled uniformly from the union of everything
   `E` ever retrieved across eval tasks. The effect must vanish.
   *(Court `BAG_CONTROL`.)*
4. **Transplantation.** Apply lineage `ℓ`'s organizer to lineage `ℓ'`'s corpus
   and eval grid. Effect surviving transplantation is stronger evidence of
   reusable structure; failing it bounds the claim to lineage-local structure.
5. **Held-out families.** The eval-transfer pool.
6. **Matched-random organizer.** A random organizer genome drawn from the
   same generator as the GA's initial population, matched on
   `n_distinct_keys` to the winner. *(Court `MATCHED_RANDOM_CONTROL`.)*

Adjudication runs through the Foundry's Court (`foundry/court/`) with the
`index_effect` claim type, which requires `PROVENANCE`, `EXACT_EFFECT`,
`ABLATION`, `MATCHED_RANDOM_CONTROL`, `NULL`, `BAG_CONTROL` and
`SHUFFLE_CONTROL` all applicable and passed. Missing or failed prerequisite ⇒
`FOSSIL_ONLY`.

---

## 11. Frozen quantities

*(To be filled from the final preflight calibration before freeze. Every value
below must be a measured or derived number, never a convenient one.)*

| symbol | value | source |
|---|---|---|
| `L_REF` | TBD | p8 budget curve |
| `N_MUT` | TBD | p5b / p9 |
| `N_TRAIN`, `N_TEST` | 6, 20 | p5b (zero train/test gap at short `L`) |
| `MAX_REF_STEPS` | 64 | fixed |
| output bound | `[0,255]` | p5b (restores fitness gradient) |
| `KEY_MAX_STEPS` | TBD | p6 re-run at the chosen cap |
| `k` | 4 | p5b/p7 |
| `POP_SIZE` | 24 | fixed |
| `B_hist`, `B_org`, `B_eval` | TBD | p8 budget curve |
| `F_SEEN`, `F_NEW` | TBD | p9 |
| `N_SUB` | TBD | p9 (organizer-fit build cost) |
| `P_ORG`, `G_ORG` | TBD | throughput |
| `N_FIT_TASKS`, `N_FIT_SEEDS` | TBD | throughput |
| `L` (lineages) | TBD | power vs measured PP1 ceiling |
| `N_EVAL_TASKS`, `N_EVAL_SEEDS` | TBD | power |
| `Δ_MIN` | TBD | 25 % of the measured PP1−U gap |
| root seed | TBD | drawn and recorded at freeze |

---

## 12. Verdict vocabulary (closed, machine-readable)

Exactly one **primary** verdict is emitted. None asserts anything about
intelligence, cognition, language, or consciousness.

| verdict | meaning |
|---|---|
| `INSTRUMENT_FAILURE` | an instrument sanity check failed; nothing was measured |
| `ASSAY_INSENSITIVE` | PP1 or PP2 not detected; the assay cannot see a known positive |
| `ASSAY_PERMISSIVE` | PN1 or PN2 admitted; the assay fabricates signal |
| `INVALID_RUN` | a preregistration condition was violated (§13) |
| `UNDERPOWERED` | the pre-declared power condition was not met |
| `NULL_NO_MEMORY_EFFECT` | `U ≈ N`: accumulated experience gives no advantage |
| `MEMORY_WITHOUT_ORGANIZATION` | `U > N`, but no organized arm beats `U` |
| `HUMAN_ORGANIZATION_EFFECT` | `H-fixed > U`; `E` does not beat `H-fit` |
| `FITTED_ORGANIZATION_EFFECT` | `H-fit > H-fixed`; `E` does not beat `H-fit` |
| `UNCONDITIONAL_SELECTION_EFFECT` | `R > U` but `E` does not beat `R` |
| `NULL_EFFECT_TOO_SMALL` | `E > R` statistically but below `Δ_MIN` |
| `ENDOGENOUS_ORGANIZATION_EFFECT_LOCAL` | `E > R` and `E > H-fit` by ≥ `Δ_MIN` on eval-primary, with ablation, scramble, bag and matched-random controls all passing |
| `ENDOGENOUS_ORGANIZATION_EFFECT_TRANSFER` | as above **and** holding on eval-transfer |
| `MIXED_INCONCLUSIVE` | the pattern matches no row above |

`HYPOTHESIS_FAILURE_SEARCH` is emitted as a **secondary** annotation when `E`
fails but PP2 succeeds: the mechanism is measurable and the organizer search
did not find it.

---

## 13. Invalidation conditions

The run is `INVALID_RUN` if any of these is true, regardless of results:

1. `acq_evals` differ across arms at evaluation time by more than 0.
2. `org_evals` differ between `E`, `R` and `H-fit` by more than 0.
3. `ledger.verify()` fails, or any corpus hash is not reproducible.
4. Any organizer GA does not replay byte-identically from its recorded seeds.
5. The E3 differential key test fails, or an `import` op appears in any
   organizer lineage.
6. `SUPPLIED_MANIFEST.json` hashes differently before and after the run.
7. Any eval-primary or eval-transfer task appears in the history or fitting
   pools.
8. Any parameter in §11 is changed after the freeze hash is recorded.
9. A verdict is assigned by inspecting an artifact rather than by the
   predicates in §9 and §12.

---

## 14. What this design cannot do

Stated in advance, so it is not discovered afterwards:

- It cannot show that the *notion of nearness* (Hamming on 64 bits) is
  machine-created. Only the key assignment is.
- It cannot show that the input encoding is neutral; the encoding privileges
  the first ~56 genotype bytes (VM register mirroring) and the first 8 train
  examples.
- It cannot generalise beyond `stackvm-v1` and this task distribution.
- It cannot distinguish "the organization groups by family" from "the
  organization groups by something correlated with family" — only the
  mutual-information report (§6) speaks to that, and it is descriptive.
- It cannot show economic value; see §7.
