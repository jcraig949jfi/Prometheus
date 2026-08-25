# Campaign 2026-08-25 — review disposition + preregistration for four experiments

> **Apollo (M2).** Written before any experiment code exists. CPU-only, no paid API.
> **Reviewer:** the shadowing frontier reviewer, 2026-08-25. **All findings accepted.**
> **Campaign:** `E3 → E9 → E1 → E11`, then stop. E5 is *earned*, not scheduled.

---

## 1. Disposition of the review — every finding, and what it changed

| # | Finding | Disposition |
|---|---|---|
| 1 | **E11 missing** — the ceiling decomposition is *observational*; every downstream experiment assumes it is causally true, and nobody intervened on it | **ACCEPTED.** E11 added and placed above E2 and E5. It is the experiment I should have found. |
| 2 | **E9 before E2** — E2 attacks "0.833 is an expressivity ceiling"; E9 attacks the more basic "0.833 measures a capability at all" | **ACCEPTED.** Reordered. |
| 3 | **E3 and E9 are not the same test** — E3 asks whether individual successes survive counterfactual transformation; E9 asks whether the task *distribution* survives removal of author/substrate co-adaptation | **ACCEPTED**, both retained, neither collapsed. |
| 4 | **E1's kill rule is arbitrary** — "<50% of equivalence classes" overcounts, because static noncommutativity ≠ semantic distinction; the target is *semantic schedule classes* | **ACCEPTED.** Kill rule rewritten (§4). |
| 5 | **E4 should die** — after E2/E11 it is integration testing | **ACCEPTED.** Deleted as an experiment; demoted to an engineering acceptance test inside E5. |
| 6 | **E2 as written gives a muddy negative** — porting three primitives at once admits ≥7 competing explanations for "no movement" | **ACCEPTED.** E2 is superseded by E11, which intervenes one at a time. E2 survives only as a fallback if E11 leaves something unresolved. |
| 7 | **E5 over E6, decisively** — E6's negative has too many escape hatches (macro useless / this macro / this target / representation / threshold / search can't exploit / atomicization / power) | **ACCEPTED.** E6 deferred out of the campaign. |
| 8 | **E7 out** — transfer failure multiplies causes; worse negative than E6 | **ACCEPTED.** Not run this campaign. |
| 9 | **E8 correctly demoted, spend nothing on it** | **ACCEPTED.** Zero budget. |
| 10 | **E10's experiment is real, its kill claim is overbroad** — it tests "given *this* telemetry representation, under *this* setup" and telemetry legibility may dominate model capability | **ACCEPTED.** Target renamed and controls added (§6). Deferred behind the first four. |

**One dependency I am not silently reordering around.** E9 requires a battery authored by
another seat, blind to Apollo's registry. I cannot author it myself without defeating its
purpose. I am filing the request now and running the experiments I own while it is
outstanding. **Execution order becomes `E3 → E1 → E11`, with E9 slotted the moment the
battery arrives** — not dropped, and not silently demoted.

## 2. Verified before preregistering (independent replication)

I re-executed Aporia's decomposition rather than citing it. The canary carries a `category`
field — which my earlier survey missed by grepping for `subtype`/`type`/`kind`, another
instance of interpreting before reading.

| category | solved | abstained | guard fires on unsolved |
|---|---|---|---|
| numeric_comparison | 10/10 | 0 | 0 |
| numeric_stated_premise | 10/10 | 0 | 0 |
| transitivity | 10/10 | 0 | 0 |
| all_but_n | 0/5 | 5 | 0 |
| temporal_ordering | 0/5 | 5 | 0 |
| vacuous_truth | 0/5 | 5 | 0 |
| consistency_check | 0/5 | 5 | 0 |

**30/50 = 0.6000, 20 abstentions, zero scorers firing.** Matches Aporia exactly. The
decomposition is now replicated by two seats independently.

---

## 3. E3 — solved-for-the-right-reason audit  *(runs first)*

**Question.** Are the 100 solved tasks solved by the intended derivation, or by a regularity
we authored in?

**Two arms, because the strongest transformation is available only for generated subsets.**

- **Arm A — regeneration (provably derivation-preserving).** `synth`, `inference` and
  `cross_tier` come from *seeded generators*. Re-draw at 10 fresh seeds. Same generator,
  same derivation, different surface. If accuracy holds, those 70 solves are not
  instance-specific.
- **Arm B — perturbation (canary, a static file).** Three transformations, each
  provably answer-preserving: entity renaming to unseen names applied consistently across
  prompt, candidates and gold; candidate-order permutation; and order-preserving numeric
  rescale for numeric categories. Applied to the 30 solved canary tasks.

**Pre-committed kill.** If **>10%** of currently-solved tasks fail derivation-preserving
transformation, **0.833 is retracted as a capability number** and restated as
battery-artifact-contaminated. Reported per category, because a category-localised failure
is a different finding from a diffuse one.

**Already-clean control.** Candidate-order permutation via `PYTHONHASHSEED` moved the dumb
heuristics (0.325–0.358) but left organism accuracy at 0.8333 across 8 seeds, so that one
dimension is pre-tested.

**Sham control.** An answer-*destroying* transformation (permute the gold label) must drop
accuracy to ≈chance. If it does not, the audit instrument is broken, not the organism.

---

## 4. E1 — semantic schedule classes  *(runs second)*

**Question.** Did O1 cover essentially all *behaviourally distinct* schedules, or an unknown
fraction of them?

**Reviewer's correction, adopted.** Static noncommutativity overcounts: two orderings can
differ statically and be semantically identical. The unit is a **semantic schedule class** —
orderings that produce the same `selected_answer` across the whole battery.

**Method.** Build the static conflict graph from `@blackboard_op` declarations (write-write
and read-after-write). That gives an upper bound on distinct classes. Then, for a sample of
subsets, *execute* orderings and cluster by battery-answer-vector to measure how far the
static bound overcounts.

**Pre-committed outcome — one of two clean statements, chosen in advance:**
- **"O1 covered essentially all behaviourally distinct schedules"** if the executed
  semantic-class count at k≥8 is ≤ the 48 orderings O1 sampled per subset; or
- **"O1 sampled an unknown fraction of behaviourally distinct schedules"** otherwise —
  in which case **O1's ceiling is downgraded from measured to conjectured** and E11's
  interpretation is caveated accordingly.

Secondary, and owed: the write-write hazard that invalidated two O1 runs must be derivable
by this checker. If the checker cannot rediscover a hazard I already know exists, it is
broken.

---

## 5. E11 — causal ceiling decomposition  *(runs third; the reviewer's experiment)*

**Question.** Is the proposed causal anatomy of the ceiling correct? Not *can Apollo acquire
anything* — this experiment **makes no acquisition claim whatsoever**.

**Method — intervention matrix, one at a time, never combined.** For each of the four
abstention classes, inject the capability claimed missing and require **task-level identity**,
not score movement.

| intervention | predicted newly solved |
|---|---|
| `all_but_n` capability | its designated 5, and only those |
| temporal-ordering capability | its designated 5, and only those |
| consistency-check capability | its designated 5, and only those |
| vacuous-truth capability | its designated 5, and only those |
| **sham primitive** (type- and complexity-matched, semantically irrelevant) | **0** |

**Provenance labelling, absolute.** Three interventions adapt existing forge primitives; the
vacuous-truth one is a hand-authored reference implementation. **All are labelled
`ORACLE/DIAGNOSTIC`, NEVER `ACQUISITION`**, and this experiment may never be cited as
evidence of minting. That is precisely what makes it immune to the counterfeit problem that
would have contaminated the original E2/E4.

**Pre-committed success.** Each intervention recovers **exactly** its predicted five, with
**zero collateral movement** — no previously-solved task lost, no unrelated task gained. The
beautiful result is 100 → 105 → 110 → 115 → 120 with clean attribution at every step.

**Pre-committed failure, and it is the valuable one.** If a known-correct semantic primitive
**cannot** recover its predicted wall, then "missing primitive" was **not** the causal
explanation, and the bottleneck lies somewhere in routing, blackboard state, composition or
scoring. **That would redirect E5 before effort is wasted teaching a system to synthesize
something it could not exploit if handed the answer.**

**Partial-credit reading, declared in advance:** +5 accompanied by two losses and seven
unrelated gains is a **failure**, not a success. Task-level identity is the criterion.

---

## 6. Deferred, with their revised targets recorded

- **E9 — independent battery.** Requested from another seat; slotted on arrival. Unchanged
  otherwise; the reviewer calls it the most valuable catastrophic negative available.
- **E5 — vacuous-truth synthesis.** *Earned* only if E3, E9, E1, E11 all survive. E4 is
  folded in as its engineering acceptance test.
- **E10 — retargeted.** No longer "can LLMs perform widening diagnosis." Now: *can wall
  state be represented compactly enough that an external reasoner predicts the appropriate
  intervention class?* Mandatory controls: raw telemetry · deliberately impoverished
  telemetry · shuffled/non-causal telemetry · a simple-classifier baseline. Without those, a
  positive may only mean I wrote "missing temporal reasoning" in everything but those words.
- **E2** — fallback only, if E11 leaves something unresolved. **E6, E7, E8** — out of this
  campaign.

## 7. Standing conditions

Preregistered before code. Every positive starts at one kill-path family of three,
`UNDER-ATTACKED`, never established. Any result favouring Apollo gets a mandatory
independent attack before write-up — O1 produced two false wins for Apollo, both caught only
by continuing to attack a favourable result. Wall-clock and engineering cost reported
alongside evaluation counts.

**Campaign stop rules, committed now:** if E3 or E9 fails badly, stop and repair the
measurement target before calling any later movement "capability acquisition." If E1 fails,
stop describing O1 as an exhaustive ceiling result. If E11 fails, stop describing the four
abstention classes as demonstrated missing primitives and investigate the coupling layer.
