# RECON — Does Prometheus preserve navigational information?

**Seat:** Diomedes (shell, unratified) · **Filed:** 2026-08-24 · **Assignment:** James, this session.
**Status:** reconnaissance. No new machinery built. No thesis change proposed.
**Rows:** every number tagged **[M]** is measured this session or read from a committed artifact;
the command and population are named at first use. Numbers tagged **[A]** are argued, not measured,
and should be weighed lower. Per `feedback_verdict_without_rows_is_an_assertion`, the census script
and its output ship beside this file.

---

## 0. Verdict up front

**The concern is substantive, and it is a correction to the instrument rather than to the thesis.**

The thesis already contains the edge idea — twice, in writing, since June. What the corpus contains
is different from what the protocols specified. Precisely:

> Prometheus specified `(x, a, outcome_label)` and stored the outcome label instead of `x′`. The
> kernel's one true `(x, a, x′)` opcode has **0 rows in production [M]**. The one corpus field named
> `step_trace` records **332,883 of 332,886 steps as the same action, on an input that varies only
> by RNG seed [M]** — a trajectory with essentially no action variance. And yet **~37% of the corpus
> [M]** turns out to be reconstructable edges with named actions and deterministic oracles that
> nobody has ever assembled into a graph or measured.

So the answer to *"did Prometheus store vertices or edges?"* is: **it stored vertices, plus an
unassembled edge corpus of ~48M records that it has never looked at as edges.** That is a better
starting position than the concern assumes, and a worse one than the protocols claim.

The single most decisive finding is negative and cheap to state: **the corpus's only trajectory
field has H(action) ≈ 0.** Exactly **one** traced record in 66,747 is a genuine multi-action
trajectory [M]. Everywhere else the action was held fixed and the seed was varied. `I(Z; A*)` is not
small there — it is undefined, because `A*` has essentially no support.

---

## A. Thesis impact

**Verdict: modest correction to the thesis; substantial correction to the instrument.** Not
evidence that a premise is wrong.

**Why it is not new to the thesis.** Three prior program artifacts already state the concern:

1. `aporia/docs/failure_signal_protocol_v0.1.md` §1 (2026-06-04) froze an atomic record of
   `{inputs, move, outcome_type, magnitude, null_p, provenance, emitter_version}` — `inputs` is x,
   `move` is a. The datum was specified as a transition, not a vertex.
2. `aporia/docs/reasoning_steering_protocol_v0.2.md` §1 (2026-06-06) is explicit: *"These records
   define a directed weighted graph: states are nodes, moves are edges."* §2 then runs a
   combinatorial Hodge decomposition on the edge flow. That is the user's §2 formulation, filed
   ten weeks ago.
3. Thesis v4.2 §9 already anticipates the *quantitative* half: `B_eff ≈ independent consequence
   bits / search cost`, and *"360M nearly context-free verdicts may be metabolically poorer than
   10,000 rich counterexample traces."*

**What the concern adds, and it is real.** v4.2 §9 asks *how many bits per verdict*. This
assignment asks **bits about what** — and that is a different axis that the program has not
separated. `I(Z;F)` is measured and nonzero; `I(Z;A*)` has never been estimated on any Prometheus
corpus. The program has been treating "the residue is rich" and "the residue is navigable" as one
claim. They are two.

**Where the June work actually stopped, which sharpens the correction.** The edge formulation was
tested exactly once — Aporia's H-R1, `verdict: NULL` twice [M]
(`stage0b_relational_hodge_report.json`: non_gradient_mass 0.201 vs null 0.251, p=0.818, n=21;
`stage0b_g2c_relational_report.json`: 0.171 vs 0.164, p=0.355, n=30). But those flows were built
over **mathematical objects compared pairwise across falsifier criteria** — polynomials and curves —
not over `(state, move, state′)` search transitions, which is what §1 of the same protocol
specified. The edge hypothesis was killed on a population it was not written about. That is
`feedback_wrong_population_statistics`, and it is why this reconnaissance finds a live question
where the record says "closed."

**Restated as one sentence for the record:** *the thesis said verbs; the schema said verbs; the
generators wrote nouns with verdict labels, except for four of them that wrote verbs and were never
read.*

---

## B. Prior art — be conservative about novelty

**None of the machinery proposed here is new. One framing may be.** Mapping, with the seven
questions compressed. All Tier-2 per `feedback_verify_upstream_attributions` — pin to primary
sources before any promotion.

**The closest field, and the one to steal from outright: Local Optima Networks (LON).** Object: a
search space compressed to a graph whose nodes are local optima / basins and whose edges are
transition probabilities under a named operator. That *is* `G=(V,E)` over `(x,a,x′)`, built for
exactly the diagnostic purpose §7 asks for (basins, funnels, corridors). It brings ready-made
metrics — funnel structure, basin size distribution, escape rate. Prometheus should reuse the
construction and the vocabulary rather than reinvent them. What fails on transfer: LONs assume a
cheap neighbourhood operator and a scalar fitness; mathematical search has neither.

**The exact `I(Z;F)` vs `I(Z;A*)` distinction is established, not novel.** It is the
action-sufficiency / bisimulation line in representation-learning-for-control: representations that
preserve value can still fail by collapsing action distinctions, while representations that keep
action-relevant structure succeed despite discarding other detail
([Action-Sufficient Goal Representations](https://arxiv.org/pdf/2601.22496)). Treat the concern as
**a known failure mode of learned representations, newly applied to a failure corpus** — that is
the honest novelty claim, and it is small.

**Successor representations / successor features.** Object: a state encoded by *what follows it*
under a policy, at a discount. This is the canonical formal answer to "represent states by
transitions rather than by properties"
([Gershman 2018](https://gershmanlab.com/pubs/Gershman18_SR.pdf),
[Frans explainer](https://kvfrans.com/successor-representations-explained/)). x = proof/search
state, a = operator, reachability = discounted occupancy. Does it solve the problem? It solves the
*representation* half given trajectories; it does not solve "we have no trajectories."

**Empowerment.** Max mutual information between an action sequence and the resulting state,
conditioned on the start state — the formal version of the assignment's §8 intuition, and closer to
what is wanted than "distance to solution"
([Unified Bellman / empowerment line](https://arxiv.org/pdf/1907.12392),
[UCT empowerment](https://arxiv.org/pdf/1803.09866)). A state preceding a breakthrough is one where
future actions retain influence. Directly reusable as a scoring function; expensive to estimate.

**Automated theorem proving.** The proposal's canonical existing form is **next-tactic prediction
conditioned on proof state** — x = proof state, a = tactic, x′ = resulting goals, reachability =
closes the goal. Premise selection and watchlist guidance (`ProofWatch`,
[arXiv:1802.04007](https://arxiv.org/pdf/1802.04007)) are the retrieval half. **This field has
already solved the version of the problem Prometheus is proposing**, on formal corpora with exact
oracles. What fails on transfer: ATP has a proof kernel that supplies x′ for free; Prometheus's
generators mostly do not emit x′.

**Heuristic-search topology — the cautionary result.** Fitness-distance correlation is the classic
attempt to define "distance to solution" as a navigation signal, and its classic result is that it
is unreliable and easily inverted. This is independent external support for the assignment's §8
warning against scalar distance, and it is a reason to prefer action-entropy framings.

**Remaining areas, briefly.** *Value of information / Bayesian experimental design / active
learning*: the correct formalism for "which experiment next," directly applicable to choosing which
falsifier to run, and cheap to steal. *RL / model-based planning*: `Q(x,a)` in §9 is literally the
action-value function; the assignment is right to defer building an RL system. *Causal
representation learning*: relevant to K5 (leakage), supplies the intervention-vs-observation
discipline the program already has via v4. *Program synthesis / DreamCoder-line library learning*:
the operator-menu-growth answer, already named in the ladder canon's H2 precondition 3.

**What appears genuinely unusual about the Prometheus formulation.** Only one thing, and it is
modest: the corpus is a **failure-dense, verdict-labelled, cross-catalog** record where the action
alphabet is mathematical operators over heterogeneous object types (knots × elliptic curves), and
the oracle is exact rather than learned. Nobody has an equivalent corpus. That is an asset claim
about data, not a novelty claim about method. **We are not looking at a new idea; we are looking at
a corpus that could test an old idea cheaply.**

---

## C. Repository reality — vertices or edges?

**Method [M]:** authoritative corpus-wide figures are from `ergon/probe/ledgers/corpus_scan/
full_scan.json` (Ergon's 165/165-file scan, committed 2026-08-22). Cell-level structure is from my
own stratified sample this session: 10 files at even index stride over the 100 `batch-*.jsonl.gz`
present on M1, ≤40,000 lines each, **360,003 records, 24 cells**.

### C.1 The authoritative corpus numbers [M]

- `theseus/corpus/` — **132,566,162 records**, 165 batch files, 346 GB. 132,312,039 REJECTED (99.81%).
- **`with_parent_share` = 0.3661** → **48,442,688 records carry `parent_record_id`.**
- `with_step_trace_share` = 0.172 → 22,761,197 carry `step_trace`.
- 131,649 distinct kill_patterns over **43 cells**; `kill_patterns_crossing_a_cell` = **0**;
  cell_pairs_zero_overlap 690/903; H(kill_pattern) 7.105 bits, H(kill_pattern | cell) 3.119 bits.

The zero-crossing figure is the important one for this assignment: **no kill_pattern label ever
appears in two different (generator, claim_kind) cells.** At the label level there is no
cross-generator transfer to navigate with, by construction.

### C.2 The record schema has the right fields; most are null [M]

Top-level keys include `parent_record_id`, `step_trace`, `kill_vector`, `sigma_claim_id`,
`sigma_symbol_ref`, `info_density`, `novelty_estimate`, `training_weight`. In a typical `a1` record
**all of these are `null`**. The ladder canon independently records `kill_vector` at **0% populated
across 5.4M records**. The schema was designed for navigation; the generators did not fill it.

### C.3 The `step_trace` field is not a trajectory — the hardest finding [M]

From the persisted census (`recon_census.json`, reproducible via `recon_census.py`):

- **332,883 of 332,886 steps** have `step_kind` = `resample` (99.9991%). The remaining **3** are
  `method_variant`.
- **332,883 of 332,886 steps** use `step_method` = `numpy_polyfit`. The other three are one each of
  `polyfit_linear_small`, `polyfit_quadratic_mid`, `polyfit_cubic_large`.
- `step_input` is identical modulo `child_seed` in **66,746 of 66,747** traced records. **Exactly one
  record** in the sample varies its input.

Every trace comes from a single generator (`d3`). There is no operator choice, no state
transformation, and no branching anywhere except in that one record. The action variable is a random
seed. **H(a) ≈ 0 by construction, so `I(Z; A*)` is undefined on the only trajectory field Prometheus
has** — not measured-and-small, but structurally unavailable. Any claim that Prometheus holds
"trajectory data" is false as stated.

*(An earlier ad-hoc pass this session reported 100%/575,204 on a different file stride. The persisted
census above supersedes it; the three `method_variant` steps do not change the conclusion.)*

### C.4 The kernel's true edge opcode was never populated [M]

`sigma_kernel.REWRITE(src_expr, tgt_expr, rewrite_rule_id, invariants_preserved, …)` records
`src_def_hash`, `tgt_def_hash`, `rewrite_rule_id`, with both endpoints in provenance. That is an
exact `(x, a, x′)`. Migration `006_add_rewrite_equiv_opcodes.sql` exists; contract tests exist.

Production row counts in `prometheus_fire` [M]: **`sigma.symbols` = 0**, `sigma.refinements` = 0,
`sigma.residuals` = 0, `sigma.evaluations` = 0, `sigma.bindings` = 0, `sigma.claims` = 1,079. The
two local kernel `.db` files hold 5 and 6 symbols, opcode field unset.

**The program built the edge primitive, migrated a schema for it, tested it, and wrote zero edges
through it.**

### C.5 But ~37% of the corpus IS a reconstructable named edge [M]

Sample census, 360,003 records — the property is **cell-deterministic** (every cell is 0% or ~100%,
never in between), so per-cell figures are exact and only the corpus-wide mix is uncertain:

- parent link present: **50.0%** of sample
- named action in payload: **45.0%** of sample
- **both — a full named edge: 36.9%** of sample

**Population caveat, applied to my own number** (`feedback_wrong_population_statistics`): my
sample's parent share is 50.0% against the full scan's authoritative 36.6%, so **my sample
over-represents edge-bearing cells.** The corpus-wide named-action share is therefore *not* 45%; it
is bounded roughly between the full scan's 36.6% and my 45%, and needs a full-corpus recount before
anyone quotes it. The per-cell classifications below are unaffected.

**Cells that write true edges, ranked by action quality:**

1. **`h1/kill_neighborhood` — the best navigation corpus in Prometheus.** Payload carries
   `parent_object_a/b`, `parent_relation`, `parent_value_a/b`, `hunter_varied_side` ∈ {a,b},
   `hunter_object_a/b`, `hunter_value_a/b`, `hunt_budget` = 10, `hunter_success`. That is
   x = survivor state, a = which side was varied and to what, x′ = resulting state, plus a
   **deterministic success oracle**. It is a directed counterexample hunt — an actual search.
   Both classes present [M], from the persisted census: **success 47,891 / failure 3,420** (93.3% /
   6.7%); varied side **b 31,839, a 16,052**. The majority-side baseline any action-ranker must beat
   is therefore **66.5%**.
2. **`c4`, `c5` / `mutation`** — `original_relation` → `relation` (e.g. `abs_diff_le_3` →
   `abs_diff_le_16`) with `parent_record_id` and `self_consistent` / `weak_holds` oracles. A named
   relation-weakening action.
3. **`g5` / `symmetry_transform`** — `scale_factor`, with raw and scaled values and a
   `scale_invariant` oracle. Self-contained edge inside one record.
4. **`b1`–`b5`** — `operator_rotation`, `composition_test`, `conservation_law`. Fully
   self-contained edges: `{operator: knot_mirror, n_applications: 5, original_value: 7,
   predicted_value: 7, actual_value: 7, matches: True}`, and composition records carrying both
   `fg_result` and `gf_result`. **Real operator algebra, tiny volume** (b1+b2+b3+b4+b5 ≈ 8.9K in
   sample ≈ 2.5%), and the operators are mostly generic scalar functions — `abs`, `log2_floor`,
   `mod_3` — which is precisely the failure `project_verbs_must_be_native` measured (7 generic
   operators → 0 relations; 1 native verb → 4,476).
5. **`d3` / `kill_neighborhood` — largest edge contributor, weakest action.** The action recoverable
   by diffing parent and child is a *generator hyperparameter* (`poly_3` → `poly_2`, or a reseed),
   not a mathematical transformation. 100% parent, 100% "action", and the action is a fit setting.

**Cells that write pure vertices:** `a1`, `f1`–`f3` (invariant_equality — the single largest slice),
`a2`, `a4`, `a5`, `e1`/`e3`/`e4` (literature_mined), `g2`, `g3`. `c1`, `c2`, `c3`, `d1`, `d2` carry
a parent pointer but **no named action** — the transition exists and the verb is missing.

**Note on my census criterion:** counting "both parent AND action" undercounts the b-series and
`a3`/`g5`, whose edges are self-contained in one record and need no parent link. Two distinct edge
encodings exist and any assembly job must handle both.

### C.6 Other stores [M]

- `charon_duckdb.graph_edges` = **396,150** — but these are *mathematical object relations*
  (`edge_type: 'isogeny'`, `weight`, `iso_class`), not search transitions. A relation graph over
  objects, not a `(state, action, state′)` graph. Do not mistake it for one.
- `noesis.chains` 100 / `noesis.chain_steps` 400 (≈4 steps/chain) — genuine derivation chains with
  `step_order`, `structure_type`. Correct shape, negligible volume.
- `noesis.transformations` 295, `noesis.operations` 1,714, `noesis.damage_operators` 9,
  `noesis.cross_domain_edges` 20,502.
- **`apollo/lineage/lineage_v2.jsonl` — 890 records, and the cleanest edge corpus in the repo.**
  Each record: `parent_ids`, **`mutations_applied`** (the action, named explicitly — e.g. `drift`),
  `genome_id`, `primitive_names`, `wiring_hash`, and a 6-dimensional `fitness` from a deterministic
  evaluator plus `ablation_details`. Explicit action labels and a measured outcome vector. Small,
  April-vintage, and from the falsified output-wiring genome — but structurally correct.
- `kill.taxonomy`, `kill.shadow_cells`, `charon_duckdb.failure_log`, `signals.battery_results`,
  `results.hypotheses`, `results.ergon_runs` — **all 0 rows**.

---

## D. Best retrospective opportunities

Three, ranked. All local, all with outcomes already known, none requiring new generation.

**D1 — `h1` counterexample hunts. The recommended one.** ~48M parent-linked records corpus-wide, of
which the h1 slice carries the richest action semantics and a real success/failure split (90.9% /
9.1% in sample). Known outcome: whether the hunt found a counterexample, and which side it varied.
The retrospective question is exactly the assignment's: *given only the parent survivor state as
Prometheus recorded it, could anything have ranked the beneficial variation above chance?* And
because the underlying invariants are in LMFDB and the knot catalogs, the **complete ground truth
for every candidate the hunter did not try is exactly computable** — which converts a logged search
into a full `A*` set without ever showing the representation a label.

**D2 — Apollo lineage.** 890 explicit `(parent, mutation, child, fitness)` edges with a
deterministic multi-objective evaluator and ablation details. Tiny, but the only corpus where the
action is a *named symbolic mutation* and the outcome is a *measured capability delta*. Best used as
the positive control: if a navigation signal cannot be found here, the method is broken, not the
corpus. Caveat: it is the genome Apollo later falsified, so a null here is ambiguous.

**D3 — Lehmer / Mahler brute force.** `LEHMER_BRUTE_FORCE_FULL_RUN_RESULTS.md` enumerated all
97,435,855 degree-14 ±5 palindromic reciprocal polynomials, and Techne's Mahler tooling is live this
week (cycle 052). Complete enumeration means **the oracle is total** — the assignment's "god knows
the solution" condition holds absolutely rather than approximately. This is the right substrate for
*constructed* perturbation neighbourhoods (§4 of the brief) rather than for retrospective mining,
because the search that produced it was exhaustive, so there is no interesting trajectory to recover.

**Explicitly not recommended:** streaming the 346 GB corpus. D1 needs the h1 slice only, which is a
single filtered pass and can be capped at a few hundred thousand records.

---

## E. Minimal decisive experiment

**Name: the h1 counterfactual-hunt test. One filtered pass, local, exact oracle, no model calls.**

It separates failure information from navigational information on the same rows, which is the thing
the assignment asks for and the thing no Prometheus experiment has done.

**Construction.**
1. Extract h1 records with `hunter_success = true` and a resolvable `parent_record_id`. Target
   n ≈ 5,000 hunts (bounded; not the whole slice).
2. For each, the state `x` is the parent survivor: `(object_a, object_b, invariant_a, invariant_b,
   relation, value_a, value_b)`.
3. Fix a candidate action pool of size **k = 100**: replacement objects drawn from the same catalog
   as the varied side, sampled once with a frozen seed, held identical across all arms.
4. **Compute `A*` exhaustively from the catalogs** — for each of the k candidates, look up the
   invariant and evaluate whether the relation breaks. Deterministic, exact, no model in the loop.
   `A*` = the set of candidates that break it. This is evaluation-only ground truth and is never
   shown to any representation (§5 of the brief).
5. `Z(x)` = only what Prometheus recorded about the parent: `kill_pattern`, `claim_payload` fields,
   `verdict`, `claim_kind`, `generator_id`, `convergence_status`, `method`. Nothing derived from
   step 4.

**The question.** Can a ranker over `Z(x)` place members of `A*` above the 1/k chance baseline, and
above the §G baselines?

**Why this is the cheapest decisive design.** The oracle is table lookup, not proof search. The
negative class is free (the k−1 candidates the hunter never tried). No LLM appears anywhere, so K6
is structurally excluded. `A*` is a *set*, not a single logged choice, so it measures beneficial-edge
ranking rather than imitation of what the hunter happened to do. And the whole thing runs against
LMFDB on M1 with no paid lane.

**Secondary, free with the same rows:** the `varied_side` ∈ {a,b} prediction, k=2, majority-class
baseline **66.5%** [M] (31,839 of 47,891 successful hunts varied side b). Weak on its own, and it
measures imitation of the hunter's policy rather than recovery of geometry — useful only as a sanity
channel.

**Pre-registration discipline required before running** (`feedback_gate_must_exceed_measurement_error`,
`feedback_gate_must_be_shown_reachable`): compute the standard error and the attainable range of
every metric **before** choosing any threshold, and verify the decision was eligible to change.
Freeze the candidate pool seed, the n, and the metric set in the prereg.

---

## F. Metrics

Primary, in the order they should be reported:

1. **`I(Z; A*)` vs `I(Z; F)` on identical rows** — the headline comparison. `F` = kill_pattern class.
   Estimate both with the same estimator and the same binning, and report the **random-pairing null**
   for each (`feedback_mi_bias` — MI on sparse histograms is biased upward). The result that matters
   is the *ratio*, and the pre-registered interesting outcome is `I(Z;F) ≫ 0` with `I(Z;A*) ≈ null`.
2. **Top-1 and top-10 accuracy against the 1/k floor**, with the floor published beside the value.
3. **NDCG@10** over the k-candidate ranking, and **AUC** for beneficial-edge classification.
4. **Action entropy reduction** `H(A*) − H(A* | Z(x))`, reported in bits with its null.
5. **Transfer**, as the assignment's ladder: T0 same states → T1 held-out neighbourhoods of the same
   parent → T2 held-out parent within the same invariant pair → T3 held-out invariant pair → T4
   cross-catalog (knot-varied → EC-varied). **Report T0/T1 before touching T3/T4.**

Every metric ships with its permutation null (`feedback_permutation_null`), ≥5 seeds
(`feedback_replicate_seeds`), and its confidence interval beside the point estimate.

---

## G. Baselines that could embarrass us

Listed worst-case-first, because **the most likely single outcome of this experiment is that a
one-line arithmetic rule wins.**

1. **Relation-margin distance** — rank candidates by how far their invariant value sits from
   satisfying `relation`. For `abs_diff_le_3` this is `|v_a − v_b|`, a subtraction. If Prometheus's
   coordinates cannot beat this, that is K3 and it is the honest headline.
2. **Invariant magnitude / value rarity** — rank by |value| or by inverse catalog frequency.
3. **Random operator ranking** — the 1/k floor.
4. **Global per-relation success rate** — ignore `x` entirely; rank by how often each candidate
   object breaks relations across the whole corpus. A pure base-rate model.
5. **Catalog-adjacency** — rank by proximity in the object's own catalog ordering (knot table
   position, EC conductor).
6. **Raw kill_pattern one-hot** — the existing coordinate, unenriched. This is the incumbent, and
   the experiment is partly a test of whether anything beats *it*.

The elaborate representation only matters if it adds **incremental** ranking information over
baselines 1 and 4 jointly.

---

## H. Falsifiers and the decision rule

Pre-committed. No "interesting, continue exploring" branch exists.

- **KILL** — if `I(Z;A*)` fails to exceed its random-pairing null at T0, on the corpus slice with
  the richest action semantics Prometheus possesses, with an exact oracle and a free negative class.
  That is the strongest available version of the test; a null there means the recorded coordinates
  are autopsy coordinates, full stop, and the edge-mining line closes rather than being re-specified.
- **REDESIGN** — if `A*` is predictable from cheap ground-truth features (baseline 1 wins clearly)
  but `Z` cannot recover it. Geometry exists; the coordinate system cannot see it. This is K2, it
  challenges the schema and not the thesis, and the follow-on is the §5 trace-vector rebuild the
  ladder canon already specifies — **not** a new architecture.
- **PARK** — if the signal exists at T0/T1 but collapses at T2 (held-out parent). Within-problem
  navigation that does not survive a held-out problem is a curiosity; park it against a future corpus
  with a real operator menu rather than spending more on this one.
- **ADVANCE** — only if `Z` beats both the 1/k floor **and** baselines 1 and 4 at T0 **and** the
  advantage survives to T2, across ≥5 seeds, with the CI reported. Anything less is not advance.

**Revisions to the assignment's kill conditions, from what the audit found:**

- **K0 (new, and it already fired) — no action variable.** Wherever `step_trace` is the data source,
  the test is impossible rather than negative: `step_kind` is constant, so `A*` has no support. Any
  future navigation claim must state its action alphabet and that alphabet's entropy **before**
  reporting a metric. This is the audit's main contribution and it kills one whole candidate corpus.
- **K5 is the live hazard here and needs naming precisely.** The h1 design puts ground truth in the
  oracle and never in `Z`, but there is a subtler leak: h1 records were *generated by a hunter that
  was already searching*, so `hunter_varied_side` reflects the generator's own policy. Predicting
  the logged choice is imitation of a policy, not recovery of geometry — which is why the primary
  metric ranks against the exhaustively computed `A*` and only the secondary channel uses
  `varied_side`.
- **K7 stays as written** and is cheap to check: if ranking requires evaluating the invariant for all
  k candidates, the ranker has already done the work the search was supposed to save. Report
  oracle-calls-per-decision alongside accuracy, or the result is sterile by construction.
- **K3 is the modal outcome.** Baseline 1 is subtraction. Say so before running.

---

## Appendix — what I did not do

- Did not process the 346 GB corpus; all figures are from Ergon's committed full scan plus a
  bounded stratified sample, both named in §C.
- Did not build, propose, or design any new architecture — the heredity rule binds, and everything
  in §E is a read-only pass over existing records.
- Did not resolve whether this attaches to an active metabolic cycle (A6). It does not, yet. On
  current evidence the natural attachment is **R2-5** (residue representation — verdict vs
  located-description vs mechanistic trace), because §E is precisely a measurement of *which
  representation carries*, one level more concrete than R2-5 states it.
- Did not verify Ergon's full-scan numbers independently. They are read from a committed artifact,
  not re-derived, and the corpus-wide shares in §C.1 inherit whatever that scan's accuracy is.

*— Diomedes, 2026-08-24.*
