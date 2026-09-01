# D-10 adversarial review record (pre-freeze)

Three independent hostile reviewers were given `d10/review/DESIGN_BRIEF.md`
and the actual code, with disjoint mandates: (A) ontology smuggling and
circularity, (B) leakage and control adequacy, (C) statistics, power and cost
accounting. Findings below are recorded whether or not they were repaired.
**Findings I reproduced myself are marked CONFIRMED-BY-REPRODUCTION**; agent
claims taken on trust are marked ACCEPTED-UNVERIFIED.

Verification script: `/tmp/verify.py` (re-runnable); outputs quoted inline.

---

## Reviewer A — ontology smuggling and circularity

### A-F1 — `E4` is false as written, and contradicts the design's own boundary table
`SEVERITY: FATAL — BLOCKS FREEZE` · **CONFIRMED (by inspection)**

`E4` claims the hypothesis space carries "no distance function, no
dimensionality, no clustering criterion, no similarity notion", while the
supplied column of the same table supplies exactly those three things:
64-bit key width (dimensionality), Hamming (distance function), top-`k`
(selection/clustering criterion). Retrieval is
`argmin_a popcount(KA(a) XOR KQ(q))` — a unary artifact code, a unary query
code, a shared space, and a symmetric bitwise-additive metric. That *is* the
semantic-hashing / LSH schema. The machine chooses coordinates inside a
geometry it did not choose.

The reviewer measured, holding the evolved key programs fixed and swapping
only the supplied comparison, a mean top-4 overlap with Hamming of 0.52
(numeric `|KA−KQ|`), 0.50 (shared high-bit prefix) and 0.40 (bitwise
Jaccard) — i.e. roughly half of "which experience is relevant" is decided by
the designer's metric. *(ACCEPTED-UNVERIFIED as to the exact overlaps; the
structural point needs no measurement.)*

**Adjudication: accepted in full.** `E4` must be deleted and replaced by an
honest `E4′` ("the key functions are unrestricted substrate programs; the
retrieval geometry is supplied and is a human-designed schema"), and the
headline claim demoted accordingly. A comparison-robustness arm (rerun the
winner under ≥2 alternative supplied comparisons) is added.

### A-F2 — the object is a unary embedding; calling it "an organization" is claim inflation
`SEVERITY: FATAL — BLOCKS FREEZE` · **CONFIRMED (by inspection)**

`KA` maps one artifact in isolation to a code (`d10/lib/organizer.py:159`).
There is no `f(a_i, a_j)` term, so no relation between accumulated
experiences can be represented except through proximity to a shared query
point. The design defines "organization" to mean "embedding + metric" and
then reports the machine finding an embedding as the machine having created
an organization.

**Adjudication: accepted.** Rename the object throughout to *endogenous
relevance keying*, and state that the experiment tests a strictly weaker
proposition than the charter's question. (I do not accept the stronger form
of the objection — the charter forbids *assuming* the answer's shape, not
choosing one — but the naming and the claim must match the object.)

### A-F3 — the supplied `sha256` tiebreak, not the evolved key, decides retrieval in the modal case
`SEVERITY: FATAL — BLOCKS FREEZE` · **CONFIRMED-BY-REPRODUCTION**

My own re-measurement (120 random organizers, N=300 corpus, k=4, 300 query
keys each):

```
median distinct keys = 2.0
median artifacts EVER retrievable = 8.0 / 300
fully collapsed organizers = 54 / 120  (45%)
```

Within a key class every artifact is interchangeable for every query, so the
order is the fixed global `sha256(seed/artifact_id)` ranking
(`organizer.py:176-188`). In the modal regime the "organization" is a
designer-supplied hash ranking with an evolved one-bit gate on top.

Worse, the tiebreak is **shoppable**: an organizer is rewarded for splitting
the corpus so a globally good artifact lands at the head of its class's
sha256 order — a fitness gradient with no organizational content, available
to arm `E` and not symmetrically to `R`, so it contaminates the primary
contrast.

**Adjudication: accepted in full.** Repairs: (1) make the tiebreak
query-dependent (`sha256(seed, query_key, artifact_id)`) so it cannot be
shopped; (2) record `n_distinct_keys` and reachable-set size for every
surviving organizer as a mandatory descriptive; (3) preregister a minimum
granularity gate, with the collapsed regime analysed separately.

### A-F4 — the retrieval `seed`'s scope is unspecified, so the null `E` is compared against is undefined
`SEVERITY: SERIOUS — BLOCKS FREEZE` · **CONFIRMED (by inspection)**

If `seed` varies per trial, a collapsed organizer behaves as arm `U`; if it
is fixed across eval tasks, a collapsed organizer is "always inject the same
four artifacts" — a materially different strategy. **Adjudication: accepted**
— the derivation must be preregistered and the collapsed-organizer/`U`
equivalence verified empirically.

### A-F5 — the `+0.01 x` shaping term is a supplied gradient *and* is the planted-positive oracle's own relevance criterion
`SEVERITY: FATAL — BLOCKS FREEZE` · **CONFIRMED-BY-REPRODUCTION**

Two separate defects.

*Arithmetic.* The term is a strict tiebreak only while the minimum
solve-rate increment `1/(N_fit x trials)` exceeds `0.01`:

```
n_fit_units=  16  min increment=0.06250  tiebreak_valid=True
n_fit_units=  54  min increment=0.01852  tiebreak_valid=True
n_fit_units= 100  min increment=0.01000  tiebreak_valid=False
n_fit_units= 160  min increment=0.00625  tiebreak_valid=False
```

At any realistic fitting-set size the term can overturn a genuine one-solve
difference. Calling it a tiebreak was arithmetically false.

*Ontology — the more serious half.* `best_train_fitness` is
`cases_passed/n_train`. The shaping term therefore asserts *an experience is
relevant to a query if it passes more of that query's train cases* — which is
precisely the planted-positive PP1 ranking criterion
(`d10/preflight/p9_operating_point.py`, `train_fit`). The organizer is handed
a smoothed version of the ceiling it is supposed to discover. Since the
un-shaped landscape is near-flat at these budgets (p5b), this term is
plausibly the only usable gradient, and it is query-conditional, so it is
exploitable by `E` and not by `R` — it does **not** difference out of the
primary contrast.

**Adjudication: accepted in full.** This is the single worst finding: it is
the charter's central failure mode (the experimenter supplying the important
ontology indirectly) occurring inside my own design. Repairs: the
**no-shaping** organizer arm becomes primary; if a shaped arm is run at all
it is a declared secondary with the coefficient capped strictly below
`1/(N_fit x trials)`, and any effect present only under shaping is reported
as an effect *of the shaping term*.

### A-F6 — early stop makes the endpoint non-monotone in retrieval quality
`SEVERITY: SERIOUS — BLOCKS FREEZE` · **CONFIRMED-BY-REPRODUCTION**

```
raises _Done on first exact_success: True
test checked only on the single stored solver: True
```

`d10/lib/acquire.py` halts on the first *train*-exact solution and evaluates
the held-out split on that genotype alone, discarding the remaining budget.
A run that finds an overfitting train-exact solution at evaluation 3 reports
`solved_test=False` and stops with 397 evaluations unspent. Better retrieval
finds train-exact sooner, so **better retrieval can lower the endpoint.** My
own preflight shows this regime is real (p4b: 0.45 train / 0.000 test;
p9 at `N_TRAIN=6`: PP1 train 0.135 vs test 0.042).

**Adjudication: accepted in full.** The harness must spend the full budget,
collect every train-exact solution, and define the endpoint as "any
train-exact solution found within `B` that is also test-exact", reporting
first-solve-evaluation separately as efficiency.

### A-F7 — no syntax/semantics bridge; a null would very likely be uninterpretable
`SEVERITY: SERIOUS — BLOCKS FREEZE` · ACCEPTED-UNVERIFIED (measurements),
CONFIRMED (structural)

`KA` sees genotype bytes and cannot execute them; `KQ` sees I/O numbers and
cannot execute anything. For `E` to beat `R`, some pair must correlate syntax
with semantics inside `KEY_MAX_STEPS`. Reviewer-measured capacity of random
key programs: median **20** steps executed (`KA`) and **14** (`KQ`); 33% /
27% hit the 300 cap. Extracting bytes from packed words costs ~3 steps/byte,
so `KA` structurally cannot compute the 256-bin byte histogram that
`features.py` hands to `H-fit` for free.

**Adjudication: accepted.** This does not make the hypothesis false; it makes
a null uninterpretable. Promoted to a **hard pre-freeze gate**: a
hand-written `KA`/`KQ` pair (PP2) must be exhibited that beats `R` under the
frozen interface. If none can be constructed by hand, the interface — not the
hypothesis — is what would be measured, and the design must change.

### A-F8 — the "raw" encoding has a large positional bias and wastes half the register file
`SEVERITY: SERIOUS` · ACCEPTED-UNVERIFIED

`R0 = n_examples` and `R1 = arity` are constant for every task in the
experiment; `R4`, `R5` are zero padding. So 4 of 8 cheap registers carry no
information. Reviewer-measured sensitivity of random key programs is ~4x
higher for the last train example than the first, and ~3x higher for the
genotype tail than its head. `MAX_ARTIFACT_WORDS=24` also blinds `KA` past
byte 192, while history-phase `dup_block` mutations grow genotypes past that
(my own diagnostic: genotype length p90 = 128, max = 475 bytes).

**Adjudication: accepted.** Drop the constant and padding slots; record the
positional bias in the boundary table instead of describing the encoding as
neutral; add an encoding-variant robustness arm.

### A-F9 — the organizer genome has no modularity
`SEVERITY: SERIOUS` · ACCEPTED-UNVERIFIED

`decode` (`organizer.py:92`) derives the KA/KQ split from two bytes modulo
the body length, so any indel relocates the boundary. Reviewer-measured:
51.8% of single mutations change genome length, and 31.6% non-locally rewrite
both KA and KQ. p6's "58/60 walks reach a grouping regime" does not rebut
this — reaching a regime under an undirected walk is not evidence that
selection can hill-climb.

**Adjudication: accepted.** Two independent chromosomes with independent
operators, plus a pre-freeze fitness-autocorrelation check under single
mutation.

### A-F10 — the family relation is defined by the searcher's own mutation operator
`SEVERITY: SERIOUS` · **CONFIRMED (by inspection)**

`progtasks.py` generates family members with `_ENG.mutate(...)` under
`_DEFAULT_MUTATE`; `acquire.py` varies candidates with the identical
operator. "Same family" therefore means "reachable in `n_mut` applications of
the operator the searcher already samples from". This does not bias `E` over
`R`, but it manufactures the headroom the design rests on and caps external
validity.

**Adjudication: accepted.** Family members must be generated under a
*different* mutation configuration from the acquisition GA's, with the
headroom measured under both and the difference reported.

### A-F11 — history and eval families overlap
`SEVERITY: SERIOUS` · **CONFIRMED (partially misdirected)**

The reviewer read `p7_pipeline.py`, a preflight probe. The preregistration
already specifies eval-primary as same-family (deliberately, since shared
structure is what the organization is meant to find) and eval-transfer as
disjoint. **Adjudication: partially accepted** — the finding is correct about
the probe and about the risk; the repair is to make the same-family /
held-out-family split an explicit *stratified factor of the main design*
rather than a footnote and an adjudication-time counterfactual.

### A-F12 — `H-fit` is a straw man, and the E/H-fit information boundary is unequal
`SEVERITY: SERIOUS` · **CONFIRMED (by inspection)**

`H-fit` as specified fits only a feature mask and a projection *seed* over
`features.seeded_projection`, which the instrument itself documents as "pure
seeded noise — carries no learned structure". Seed-shopping is not a steel
man of "machine-fitted human organization". Separately, `H-fit` receives a
256-bin byte histogram and Shannon entropy that A-F7 shows `KA` cannot
compute at all, so `E − H-fit` is confounded by fitting capacity and by
feature access, not by function class.

**Adjudication: accepted.** Replace with a genuinely fitted metric (a learned
projection / ranking model trained on the same downstream signal and the same
`org_evals` budget), and record the feature-access asymmetry explicitly.

### A-F13 — the scramble control has near-zero power at the achieved granularity
`SEVERITY: SERIOUS` · **CONFIRMED-BY-REPRODUCTION** (median 2 distinct keys)

Permuting a key multiset that is ~99% one value is nearly the identity.
**Adjudication: accepted** — scramble is preregistered as uninformative below
a granularity threshold, and is always reported next to `n_distinct_keys`.

### A-F14 — `decode` degenerate case undeclared
`SEVERITY: MINOR` · **CONFIRMED**

For `len(g) < 3`, `decode` returns `(g, g)`: the same program runs on two
incommensurable encodings. **Adjudication: accepted**, declare or return
`(b"", b"")`.

### What Reviewer A found sound
The `E3` information firewall holds **structurally**, not by convention:
`evidence_words` touches only `train_examples`; `TaskEvidence`/`TaskView` are
`extra="forbid"`; `machine_view()`/`evidence()` never carry `admin_metadata`
or `provenance`; `task_id` provably hashes train *and* test and is never
read. My own boundary tests agree (`d10/tests/test_boundary.py`, 9/9 pass,
including 200/200 identical query keys across differing `task_id`s).

---

## Reviewer B — leakage and control adequacy

*(pending at the time of writing; findings to be appended verbatim with
adjudications)*

## Reviewer C — statistics, power and cost accounting

*(pending at the time of writing; findings to be appended verbatim with
adjudications)*

---

## Consolidated blocking list (Reviewer A only, so far)

| # | finding | status |
|---|---|---|
| A-F1 | `E4` false; supplied metric does ~half the selection | **blocks** |
| A-F2 | unary embedding described as "an organization" | **blocks** |
| A-F3 | supplied `sha256` tiebreak decides retrieval; shoppable | **blocks** |
| A-F4 | retrieval seed scope undefined ⇒ undefined null | **blocks** |
| A-F5 | shaping term is a supplied gradient == PP1's own oracle criterion | **blocks** |
| A-F6 | early stop makes the endpoint non-monotone in retrieval quality | **blocks** |
| A-F7 | no syntax/semantics bridge ⇒ uninterpretable null | **blocks (gate)** |
| A-F8…A-F13 | repair before freeze | repair |
| A-F14 | declare | record |
