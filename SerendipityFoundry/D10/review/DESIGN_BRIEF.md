# D-10 design brief for adversarial review (pre-freeze)

You are reviewing a DRAFT experimental design. Nothing has been frozen and the
main experiment has not been run. Your job is to kill it.

Working directory: `F:\SerendipityE`. Instrument source: `foundry/` (a
validated, unmodified release of the Prometheus Serendipity Foundry).
Experiment-side code: `d10/lib/*.py`, probes in `d10/preflight/*.py`, results
in `d10/preflight/*.json` and `*.log`.

---

## 1. The question

Can a computational system construct its own useful organization of its
accumulated computational experience, rather than having that organization
specified by humans?

## 2. Operational definition being used

A **corpus** `C` is a frozen ordered list of artifacts (StackVM genotype byte
strings) produced by a prior *history* phase. A **query** is a `TaskEvidence`
(train examples only) for a new exact task.

An **organization** is a pair of total functions

    KA : genotype bytes -> 64-bit key       (artifact key)
    KQ : train examples -> 64-bit key       (query key)

plus a supplied retrieval rule: return the `k` corpus artifacts minimising
Hamming distance between their `KA` key and the query's `KQ` key, ties broken
by a deterministic hash of `(seed, artifact_id)`.

The **organization** is the induced structure on `C`: which artifacts share a
key, which are Hamming-near, which of the 64 bits are live and what they
separate.

Endogenous means all four of:
- **E1** `KA`, `KQ` are substrate programs with complete Foundry lineage
  terminating in `create_random` events with recorded seeds; no byte human- or
  LLM-authored; no `import` creation-op anywhere in an organizer lineage.
- **E2** every surviving organizer survived selection whose only input was
  measured downstream acquisition outcomes on *fitting* tasks.
- **E3** no privileged information reaches `KA`/`KQ` — in particular `KQ`
  cannot read `task_id` (a content hash of the whole task, train AND test),
  family identity, generator parameters, difficulty, chronology, or admin
  metadata. Structural, not conventional.
- **E4** the hypothesis space is "all substrate programs within a step cap",
  not a human-parameterised family (no feature list, distance function,
  dimensionality, clustering criterion, or similarity notion).

## 3. Information boundary

| Supplied (frozen, identical in every arm) | May emerge |
|---|---|
| substrate StackVM-v1 and its meters | content of `KA`, `KQ` |
| acquisition procedure (elitist GA: `POP_SIZE=24`, `N_ELITES=2`, `TOURNAMENT_K=3`, `P_CROSSOVER=0.5`) | which artifacts collide into one key |
| endpoint predicate (exact equality on a held-out split) | partition granularity (how many keys are used) |
| raw input encodings `artifact_words`, `evidence_words` (`d10/lib/organizer.py`) | which of the 64 bits are live, and what they separate |
| key width 64 bits | which artifacts are near / far |
| comparison (Hamming), selection (top-k, hash tiebreak) | which distinctions are preserved vs discarded |
| retrieval step cap `KEY_MAX_STEPS` | what makes an experience relevant to a query |
| `k` (injected genotypes), acquisition budget `B` | |
| organizer search operators (substrate mutate/recombine) and its budget | |
| organizer fitness *definition* (mean train-exact solve rate on fitting tasks; `+0.01 x` mean best train fitness as tiebreak) | |
| task generator, its filters, and the trivial-program shortcut screen | |

## 4. Environment (substrate-generated tasks)

`d10/lib/progtasks.py`. A task is defined by a *reference program* in the same
substrate the learner searches:

- a **family** is a random reference program (`root`, length `L`) plus its
  mutational neighbours (`n_mut` substrate mutations); "same family" is a fact
  about substrate descent, never a label any learner/organizer can read;
- a **task** = a family member program + `n_train=6` train cases + `n_test=20`
  disjoint test cases, inputs uniform in `[0,255]^2`;
- reference programs are filtered to halt within `MAX_REF_STEPS`, produce
  bounded outputs in `[0,255]`, and be non-degenerate (>= 16 distinct outputs
  over 40 probe inputs);
- every task is **screened**: rejected if any member of a frozen trivial-program
  set (all <=2-instruction programs + 2000 fixed random programs) reproduces
  train+test exactly.

Rationale: exact solvability is guaranteed by construction, difficulty has a
mechanical dial, family members share reusable substructure by descent, and no
human semantic category enters the environment.

## 5. Arms — all differ ONLY in which `k` genotypes are injected

Every arm runs the identical acquisition procedure: population of `POP_SIZE`,
of which exactly `k` are injected genotypes and the rest fresh random, under an
identical evaluation budget `B` and identical trial seeds. Endpoint =
test-split exact solve.

| arm | which `k` |
|---|---|
| **N** | `k` fresh random genotypes (no memory) |
| **U** | `k` uniformly sampled corpus artifacts (unorganized memory) |
| **H-fixed** | top-`k` from the Foundry's shipped Q3 (AURORA-like) index, built on the same corpus |
| **H-fit** | top-`k` by Hamming over a key = sign of (standardised `features.py` vectors x a seeded projection), where an evolved byte genome selects the active feature mask and projection seed — *machine-fitted instance of a human-designed organization* |
| **R** | identical machinery to **E**, identical compute, but during organizer fitness the evidence handed to `KQ` comes from a fixed derangement of the fitting task list — the organizer can still learn "retrieve globally good artifacts", it cannot learn task-conditional relevance |
| **E** | top-`k` by Hamming over evolved `KA`/`KQ` key programs, selected on downstream acquisition consequences |

Adjudication-time counterfactuals on **E**'s winner: bit ablation (mask bits on
both sides), statistics-preserving **scramble** (same key multiset, permuted
across artifacts), and **transplantation** to held-out families.

Contrasts and what they isolate:
- `U - N`: does accumulated experience help at all
- `H-fixed - U`: does a human-designed organization help
- `H-fit - H-fixed`: does fitting parameters inside a human ontology help
- `R - U`: does compute-matched, non-task-conditional organization help
- `E - R`: **primary** — does selection on downstream consequences *for this
  query* add causal utility, with function class and compute matched
- `E - H-fit`: does the universal function class add utility, with selection
  signal and compute matched

## 6. Preflight results so far (real measurements in this workspace)

- `p2`: StackVM throughput ~1250 evals/s at `max_steps=200` (20 cases/eval).
- `p4`, `p4b`: **all five Foundry synthetic task families are at the floor**
  (cold-start test-exact solve 0.000 at budgets up to 2000). `conditional`
  showed 0.45 *train*-exact with 0.000 *test*-exact — pure overfitting. This is
  why the environment is substrate-generated and the endpoint is the held-out
  split.
- `p5`: with unbounded 64-bit outputs the landscape is gradient-free: even
  seeding the population with same-family reference programs gives 0.021.
- `p5b` (bounded outputs, L=12, n_mut=1, B=600): cold **0.000**, matched
  foreign-family material **0.091**, same-family reference programs **0.568**.
  At B=2000: cold 0.023. Large, clean headroom.
- `p5b` also: at L=20 there is a large train/test gap (train 0.25 vs test
  0.021); at L=12 the gap is zero.
- Shortcut screen rejects **~85%** of candidate tasks as trivially solvable —
  a recorded property of the environment.
- `p6` (organizer space, 300 artifacts, 600 random organizer genomes):
  collapsed-to-one-key 273, coarse 60, middle 68, fine 142, injective 57;
  median distinct keys 2. Mutation walks: **58/60** reach a grouping regime
  within 40 mutations. So the useful middle is reachable from random init and
  by mutation — a null would not obviously be a reachability failure.
- `p7` (end-to-end: real history phase, real corpus, oracle-retrieval ceiling)
  is running; its numbers set the operating point and the power calculation.

## 7. What to attack

Search specifically for, and give a concrete mechanism for each hit:

1. **Ontology smuggling** — where does a human concept enter the *organization*
   (not the environment or the endpoint)? Is the supplied/emergent table honest?
   Is `E4` actually true given the fixed input encoding and Hamming comparison?
2. **Circularity** — does any arm's advantage follow from the design rather
   than from measurement?
3. **Leakage / privileged information** — anything reaching `KA`/`KQ` that
   fingerprints the task, family, chronology, or the held-out split. Check
   `d10/lib/organizer.py` `evidence_words` and `artifact_words` directly.
4. **Weak or defeated controls** — is `R` really compute- and class-matched? Is
   the derangement the right null? Is `H-fit` a straw man or a steel man of
   "machine-fitted human organization"? Is the scramble control actually
   statistics-preserving?
5. **Hidden compute advantages** — organizer construction cost, retrieval-time
   cost, corpus-size effects, number of engine evaluations per arm.
6. **Deterministic shortcuts** — in the environment, in the acquisition
   procedure, or in retrieval; is the trivial-program screen adequate?
7. **Statistical malpractice** — units of analysis, non-independence, multiple
   comparisons, selection over lineages, post-hoc endpoint choice, power.
8. **Impossible or trivial positive controls**, unreachable gates.
9. **Claim inflation** — is the strongest supportable claim actually what the
   design measures?
10. **Ways the "endogenous" mechanism is really designer-specified.**

Read the actual code before asserting a defect. For each finding give:
`SEVERITY (fatal / serious / minor)`, the concrete failure mechanism, the file
and line if applicable, and a specific repair. Say clearly which findings, if
unrepaired, should block preregistration.

Do not be diplomatic. A clean null is a fine outcome; a contaminated positive
is not.
