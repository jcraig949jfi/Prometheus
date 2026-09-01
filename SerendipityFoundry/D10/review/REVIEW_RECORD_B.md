# Reviewer B — leakage and control adequacy (findings + adjudication)

Companion to `REVIEW_RECORD.md` (Reviewer A). Same convention:
**CONFIRMED-BY-REPRODUCTION** = I re-measured it myself; **CONFIRMED** = verified
by inspection; ACCEPTED-UNVERIFIED = taken on the reviewer's measurement.

---

## B-A1 — `artifact_words` supplies genotype LENGTH as word 0, in register R0, and the docstring denies it
`SEVERITY: FATAL — BLOCKS FREEZE` · **CONFIRMED-BY-REPRODUCTION**

`d10/lib/organizer.py:53` sets `words = [len(g)]`. The docstring two lines above
claims "Raw content only: no histogram, entropy, **length bucket**, execution
statistic or any other summary." Word 0 *is* an unbucketed length statistic, and
because `vm.run_program` mirrors the first inputs into `R0..R7`, it sits in `R0`
where a **2-byte** program reads it directly. My reproduction:

```
KA = bytes([OP["LDR"], 0])   # LDR R0
len   7 -> key   7
len  16 -> key  16
len  40 -> key  40
len  96 -> key  96
len 250 -> key 250
```

The key is *exactly* the genotype length. And length is a strong channel to
source-task and chronology — my reproduction over three real history runs:

```
task0: n=800 mean_len=22.1  first_half=30.6  second_half=13.7
task1: n=800 mean_len=85.5  first_half=78.4  second_half=92.7
task2: n=800 mean_len=15.1  first_half=26.7  second_half= 3.5
```

Source-task means span **5.7x**; within-run position shifts length by up to
**7.6x**. So the one summary statistic I supplied is a cheap, 2-byte-reachable
route to exactly the chronology and source-task identity that `E3` forbids.
Reviewer B further measured that ~1.7% of *uniformly random* organizer genomes
already key by length exactly, making "organize by length" the single most
common non-degenerate organization in the space — which means p6's "58/60 walks
reach a grouping regime" was probably reporting, in large part, the discovery of
length-keying.

**Adjudication: accepted in full.** This is my error and it is the second
instance (with A-F5) of the charter's central failure mode inside my own design.
Repair: delete `len(g)` from `artifact_words`; add mutual information between the
shipped artifact key and (length, corpus-position quartile, source history task)
as a mandatory reported adjudication statistic.

## B-A2 — the `E3` self-test cannot fail
`SEVERITY: SERIOUS — BLOCKS the E3 claim as evidenced` · **CONFIRMED**

`d10/tests/test_boundary.py` and `audit.organizer_source_audit` test only that
identical train splits yield identical query keys (true by inspection of
`evidence_words`, cannot fail) and grep two function bodies for a forbidden-name
list. `len` is not on that list, so B-A1 passes the audit cleanly.

**Adjudication: accepted.** The audit must be replaced by *reconstruction
probes*: fit the best available decoder of (family, source history task,
corpus-position quartile) from artifact keys alone and report accuracy against
chance, against a length-only decoder, and against an oracle-relevance decoder.

## B-A4 — held-out split reconstruction is genuinely infeasible
`SEVERITY: MINOR` · ACCEPTED-UNVERIFIED. Train and test inputs come from one
Mersenne Twister stream; inverting MT needs 624 32-bit outputs and twelve
`randint(0,255)` draws are nowhere near, with `KEY_MAX_STEPS` foreclosing brute
force. **Adjudication: accepted** — the argument belongs in the prereg rather
than being left for a reviewer to redo.

## B-B1 — corpus duplicates break "exactly k genotypes"
`SEVERITY: FATAL — BLOCKS FREEZE` · ACCEPTED-UNVERIFIED

Measured 20.2% duplicate corpus slots, max multiplicity 100. Since `KA` is a pure
function of bytes, every copy gets the same key, so a winning key can return *k
copies of one program*. Organized arms concentrate; `U` does not — so effective
distinct material differs systematically by arm, and `U` is silently
multiplicity-weighted (a free global-quality prior).

**Adjudication: accepted.** The corpus becomes the *distinct* content-addressed
genotype set — which is already the instrument's own identity rule
(`schemas.py`: "identity is content, not history") — with de-duplication
continuing down the ranking inside top-`k`, and per-trial distinct-count reported
as a covariate.

## B-B2 — the corpus is substantially trivial-screen material
`SEVERITY: SERIOUS` · ACCEPTED-UNVERIFIED. 5.3% of corpus slots have length ≤ 2,
i.e. they are members of the frozen trivial-program set and are *provably
incapable* of solving any admitted task. **Adjudication: accepted** — report the
corpus length distribution and trivial-set overlap as a frozen environment
property. Root cause is B-C2.

## B-B3 — where the leak/phenomenon line actually is
`SEVERITY: SERIOUS (definitional)` · **Adjudication: accepted and adopted.**
The reviewer's criterion is better than mine and is adopted verbatim into the
preregistration: *a channel is a leak if it lets an organizer recover source-task
identity more accurately than a task-relevance-only decoder does.* Under it,
length (B-A1) fails, and execution features fail for the H arms (B-D2b). Corpus
*order* does not leak (order never reaches `KA`; `_tiebreak` is a sha256, so
retrieval order is pseudorandom rather than chronological).

## B-B4 — fitting tasks may be a subset of history tasks
`SEVERITY: FATAL — BLOCKS FREEZE` · **CONFIRMED (as a real ambiguity)**

If fitting ⊆ history, the corpus contains each fitting task's own train-exact
solver; `acquire` evaluates injected genotypes first and halts on the first
train-exact hit, so an organizer that memorises `evidence(i) → key of solver(i)`
scores fitness 1.0 at a cost of one evaluation. 64 bits accommodates that
trivially. Organizer selection then optimises a hash table, not an organization.

**Adjudication: accepted.** My prereg §4.2 already specifies a three-way split,
but the reviewer is right that it was not enforced and that the probe code
(`p7_pipeline.py`) does not implement it. Repair: enforce the three-way split
mechanically, **and** exclude from the corpus every genotype that is train-exact
on any fitting task, recording the count excluded.

## B-C1 — fitness ties are broken by genotype bytes: a content-free lever on whether injected memory survives at all
`SEVERITY: FATAL — BLOCKS FREEZE` · **CONFIRMED-BY-REPRODUCTION**

`d10/lib/acquire.py` sorts `key=lambda m: (-m[1], m[0])` and `_tournament` takes
`min(idxs, key=lambda i: (-fitness, i))` over that already-sorted list. Fitness
takes only `n_train+1` values and at cold start essentially the whole population
is tied at 0.0 — so the early GA is a **lexicographic sort on genotype bytes**,
not a search.

My reproduction (400 replicates, `POP_SIZE=24`, `N_ELITES=2`, all fitness tied,
injected genotypes differing only in their leading byte):

```
lead=0x00: mean rank of injected = 1.55 / 24 | 0.979 of elite slots
lead=0xFF: mean rank of injected = 21.47 / 24 | 0.000 of elite slots
```

**One content-free byte decides whether injected memory survives into the next
generation at all.** (Reviewer B reported a 65x swing in parent-slot share; my
first reproduction attempt used a different statistic — exact membership in the
final population — and returned 0.0000 for both, so I do not confirm that
specific figure. The mechanism and its severity are confirmed by the measurement
above.)

An organizer can learn this directly: `artifact_words` word 1 is `g[0..7]`
little-endian, so `g[0]` is its low byte and a `KA` keying on low bits of word 1
*is* a first-byte sorter. It also defeats the scramble counterfactual, since
scramble destroys the key↔`g[0]` correlation.

**Adjudication: accepted in full.** Repair (must land before freeze): break
fitness ties by a seeded per-individual hash in both places.

## B-C2 — the same tiebreak causes length collapse in the history phase
`SEVERITY: SERIOUS` · **CONFIRMED-BY-REPRODUCTION** (see B-A1: 30.6→13.7 and
26.7→3.5 within single runs). Shorter strings sort before longer ones sharing a
prefix, so the zero-fitness regime is a length-minimising drift. This is the root
cause of B-B2 and of B-A1's exploitable signal. **Adjudication: accepted** —
re-measure the length trajectory after the B-C1 repair and freeze the corpus
length distribution as an environment property.

## B-C3 — no length / diversity / mutability matched control
`SEVERITY: SERIOUS` · **CONFIRMED.** Injecting `k` genotypes does not neutralise
material: `mutate`'s indel and `dup_block` operators scale with genotype length,
so injected length changes offspring variance and effective mutation rate; and
total injected *bytes* differ by an order of magnitude across corpus regions
while `k` is fixed. **Adjudication: accepted** — the `U-len` arm (already in the
prereg for T16) is strengthened to match E's retrieved *length multiset and
distinct-count*, with per-arm length, distinct-count and total injected bytes
reported as covariates.

## B-D1 — `R` is under-specified as a null
`SEVERITY: SERIOUS — (a) BLOCKS` · **CONFIRMED**

(a) If the fitting list is family-ordered with contiguous members and the
"fixed derangement" is a cyclic shift by one, then `(m−1)/m` of tasks map
*inside their own family* — **67% same-family at m=3**. `R` then learns genuine
family-conditional relevance and `E−R` is biased toward null. Even a uniformly
random derangement gives ~12%.
(b) `R` can memorise `evidence(σ(i)) → key good for i` during fitting, so `E` and
`R` can reach very different *fitting* ceilings on identical compute:
compute-matched is not selection-pressure-matched.
(c) Degenerate collapse floors cleanly at arm `U` — good behaviour, but it should
be stated and the collapsed fraction reported.

**Adjudication: accepted.** σ becomes a derangement of *family blocks* with the
realised same-family rate recorded and required to be exactly 0; organizer-fitness
trajectories, winner fitting-set fitness and fitting→eval generalisation gaps are
reported for both `E` and `R`.

## B-D2 — `H-fixed` is rigged to lose, twice
`SEVERITY: SERIOUS — (b) BLOCKS any "beats human organization" claim` · **CONFIRMED**

(a) Q3's query side is a `seeded_projection`, which the instrument itself
documents as "pure seeded noise — carries no learned structure". So `H-fixed`
returns approximately the same `k` artifacts for every eval task, and
`H-fixed − U` is answered by construction rather than by measurement. The
instrument is honest about this in `query_path_doc`; the *experiment* was not.

(b) **`evented=False` does not exist in `acquire.py`.** I wrote that mode into
the module docstring and never implemented it — `acquire()` has no such parameter
and emits no ledger events at all. Since `features.py` aggregates execution
features from `ARTIFACT_EXECUTED` events, the H arms would silently run with 20
of 278 feature dimensions identically zero: an undeclared amputation of the human
arm.

**Adjudication: accepted in full.** Repair: run the history phase through the
Foundry's real evented path so the shipped builders receive their declared
inputs; fix the false docstring; and record the converse asymmetry (evented H
arms gain per-artifact behaviour measured against the source history task, a
task-conditional channel `E` does not have).

## B-D3 — `H-fit` is a straw man; the steel man is specified
`SEVERITY: SERIOUS` · **CONFIRMED.** My `H-fit` let the genome pick only a
feature mask and a *projection seed*; a seed indexes a random matrix, so mutation
jumps to an unrelated matrix and the genome cannot hill-climb the alignment at
all. Worse, artifact features are 278-dim and evidence features 83-dim, so there
is no correspondence feature-masking could recover. `E` beats this by
construction. **Adjudication: accepted; the reviewer's steel man is adopted** —
the genome decodes totally into real matrices `W_A` (278x64) and `W_Q` (83x64),
selected on the identical downstream signal, fitting tasks, budget and variation
operators. Without that substitution the `E − H-fit` contrast is dropped rather
than reported.

## B-D4 — the scramble control preserves none of the joints that matter
`SEVERITY: SERIOUS` · **CONFIRMED.** `Organization.scrambled` preserves the key
multiset, granularity, entropy and bit marginals — exactly and only what my own
test checks — while destroying key↔length, key↔first-byte, key↔multiplicity,
key↔source-block, and key↔global-quality. So "E > scramble" licenses only *"the
key assignment carries information"*, never *"task-conditional relevance"*. My
docstring ("Preserves every superficial statistic of the organization") is false
as written. **Adjudication: accepted.** Repairs: correct the interpretation; add
a **stratified scramble** (permute within length-decile x first-byte-octile x
multiplicity strata); and add a **query-shuffle** control that holds the artifact
side entirely fixed and pairs each eval task with another's query key — the
sharpest available null for the actual claim.

## B-E — the Court: adequate for effect and provenance integrity, blind to information hygiene
`SEVERITY: SERIOUS` · **CONFIRMED (important)**

- **`E1` is unadjudicable by the Court as shipped.** `build_blind_view` exposes
  per node only label, parents, `genotype_len`, `recorded_hash`, genotype bytes,
  `dangling_parents`, `record_ok` — **`creation_op` never crosses the blind
  surface**, so `run_provenance` cannot distinguish a lineage rooted in
  `create_random` from one rooted in `import`. My claimed no-`import` audit
  therefore cannot be checked by the Court.
  *Repair:* run `audit.lineage_audit` outside the Court and commit its output
  into the case manifest so `_case_commit_hash` binds it. (Exposing `creation_op`
  in `BlindNode` would be the cleaner fix but is an instrument change, which is
  out of scope for D-10.)
- The information boundary itself is entirely outside the Court: it never sees
  the encoders, the corpus, or σ, and `run_bag_control`/`run_shuffle_control`
  simply invoke whatever callable the claimant supplies — **the Court cannot
  verify that the shuffle is a shuffle.**
- `_budget_equal` counts `evaluate` calls only; organizer-construction compute,
  retrieval compute and the H arms' fit are outside that meter.
- `n_candidates_considered` is self-reported and nothing can detect an
  understated count. *Repair:* set it to the mechanically-metered total number of
  organizer genomes evaluated across all lineages and arms, commit it into the
  hashed manifest, and require `selection_penalty > 0`.
- `n_trials` defaults to **8**, and `_two_arm_effect` applies no statistical test
  at all — only a point-estimate-vs-margin comparison. D-10's statistical plan
  must live in the preregistration, not in the Court.
- D-10 must declare `claim_type = index_effect` or `relational_organization`, or
  both organization controls are silently inapplicable while
  `CURRENT_UTILITY` is still reachable.

**Adjudication: accepted in full**, and it changes how the Court is used: it
adjudicates *effect and provenance integrity*, and the preregistration —
not the Court — carries information hygiene and the statistics.

## B-F1 — the design measures within-family generalisation
`SEVERITY: SERIOUS` · **Adjudication: accepted.** Transplantation to held-out
families is promoted from an adjudication-time counterfactual to a
**co-primary endpoint with its own power calculation**, or the claim is scoped to
"generalises to new members of families present in its experience".

---

## Reviewer B's note in the design's favour

The two leaks B expected to find are absent: `evidence_words` genuinely never
touches `task_id`, and the held-out split is genuinely unreconstructible from
train evidence within the step cap. Degenerate key collapse also floors cleanly
at arm `U` rather than at something pathological. **The leaks that exist are on
the artifact side and in the harness — the opposite of where my defences were
concentrated.**
