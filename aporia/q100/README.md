# Q100 — the hundred unsolved questions, as a Prometheus research loop

**Opened:** 2026-08-31 by Aporia, on operator instruction. **Source list:** operator-supplied,
2026-08-31, 100 questions across 24 categories with three falsification tests each.

**Registry:** `REGISTRY.jsonl` — 100 rows, machine-readable, one per question. Question and
test fields are OPERATOR INPUT AND FROZEN. Only the underscore-prefixed triage fields may be
edited by this seat.

**Dossiers:** `dossiers/QNNN.md`, written one per loop pass.

---

## 0. What this loop is for, and the trap it must avoid

The operator's ask: document these, research them, and produce for each one **(a)** what
Prometheus experiments and tools can answer it, **(b)** historical attempts, **(c)** the
prerequisite tools, data and tests that must pass *before* the question can be answered at
all, **(d)** a falsification battery, and **(e)** how the question could be answered with
human language subtracted out as far as possible.

**The trap, named up front.** Ninety-eight of these hundred questions are stated in the
field's own vocabulary, and that vocabulary is what fragmented the field. A loop that produces
100 literature summaries filed by category reproduces the fragmentation and adds a search box.
Two standing rules apply:

- `feedback_substrate_passive_consumer_warning` — every document must trace to a behaviour
  delta. `LOOP_APORIA` records 30 paradigm trees produced by exactly the pattern of writing
  documents with no consumer.
- **Consume before duplicate** (Rule Zero). Several of these questions Prometheus has already
  built an instrument for, and two it has already partly answered. Those come first, and the
  loop reports what we measured before it reports what the field says.

## 1. Loop protocol

Each pass takes ONE question or one tightly-coupled cluster and produces a dossier with a
fixed section order. Passes are resumable; the registry carries the state.

    1. TRIAGE          tier, existing instrument, prior Prometheus result
    2. PRIOR ART       historical attempts and WHAT THEY ACTUALLY MEASURED
    3. PREREQUISITES   the tools, data, and tests that must pass BEFORE an answer is possible
    4. FALSIFICATION   the battery, with each control stated WITH the input that fails it
    5. LANGUAGE-FREE   the restatement with human language subtracted, and what remains
    6. VERDICT         answerable now / answerable after prerequisites / not answerable here

Section 3 is the load-bearing one and is the reason this is not a literature review. A
question whose prerequisite instrument does not exist cannot be answered by more reading.

## 2. Triage — the three tiers

**TIER A — instrument exists AND Prometheus has already produced a bearing result (7).**
These are researched last, not first, because the existing result must be written down before
the literature is allowed to frame it.

    Q047  infer a missing primitive, propose a minimal new one
    Q060  expand the reasoning language, prove strictly increased expressivity
    Q100  metabolize falsified hypotheses into new reachable discoveries
    Q046  same underlying defect behind different-looking failures
    Q098  genuine progress vs self-generated metrics
    Q085  evaluation-aware deception
    Q050  independent validators not sharing the solver's failure modes

**TIER B — instrument exists, no bearing result yet (13).**

    Q002 Q005  lemma / proof-abstraction invention
    Q024       macro-actions that reduce search and stay reusable
    Q029       compact sufficient state representation
    Q039 Q040  algorithm induction; heuristic -> synthesised exact algorithm
    Q044       discriminative falsifying experiment design
    Q045       search insufficiency vs representational insufficiency
    Q054 Q055 Q056  representation changes search complexity; bisimulation; operator equivalence
    Q097       auditable long-running world model with provenance
    Q033       compositional depth extrapolation

**TIER C — no instrument; prerequisite build required (80).** Not deprioritised as science,
deprioritised as *loop order*, because a dossier on a question with no instrument produces
prerequisites and nothing else — which is useful once, in bulk, not one at a time.

## 3. The Tier-A mapping, stated now so the literature cannot reframe it

### Q047 and Q060 — and the result that already bites

Both ask whether a system can add to its own reasoning vocabulary and *prove* the addition
bought something. Prometheus's instrument is Apollo's O1 expressivity assay:

    E(C,T) = max over type-correct compositions g in G(C) of score(g,T)
    dE(p)  = E(C union {p}, T) - E(C,T)

1,737,000 pipelines enumerated, ceiling 0.8333, positive control PASSED,
`single_primitive_baseline = 0.0000` so composition is mandatory. Two nulls read **exactly
zero** (`null_noop`, `op_check_transitivity`), which is what licenses any non-zero reading.

**Q060's T2 is the decisive test in the whole list** — *exhaustively search bounded
compositions of old operators; PASS if the new operator's behaviour is NOT reproducible within
the bound.* Prometheus has a standing result bearing directly on it, from
`AMENDMENT_1_LEVELS_AND_INSTRUMENT_RULE_2026-08-27.md`:

> If `M = g(p1..pk)` with `g` in `G(C)`, then `G(C union {M}) = G(C)` extensionally, given
> arbitrary composition and no resource bound. **Adding M adds a NAME, not a denotation.**

So for any invented operator that is itself a composition, **T2 cannot be passed — not for
want of effort, but definitionally.** A system can only pass T2 with a **non-conservative
semantic extension**: machinery outside `G(C)` — induction from observations, a new oracle,
recursion, quantification, variable binding, or a new type constructor.

That reframes both questions. As written they conflate three levels, and Prometheus has the
vocabulary for the distinction already:

    Level 0  DEFINITIONAL CHUNKING   nothing newly representable; legitimate gain is SEARCH
                                     COMPRESSION and must be called that
    Level 1  OPERANDIZATION          M becomes an object other operators consume; alters the
                                     program graph available under the architecture
    Level 2  NON-CONSERVATIVE        behaviour not definable in the existing closure

**Q060 as stated is only passable at Level 2. Most of the literature it is aimed at operates
at Level 0 and reports compression.** That is a contribution to the question's formulation,
and it is why the first research fire targets this cluster.

Relevant measured artifacts: `aporia/iq/RESULT_IQ_PORT_1.json` (dE = 5/120 exactly, novelty
ZERO, verdict ADAPTER), `RESULT_IQ_NULL.json` (both nulls exactly 0; three of 27 registered
operators are structurally dead), `RESULT_TRANSFER_1.json` (parser fires 0/200 on both
independent construction routes — **whatever the port demonstrated, it was not a transferable
capability**).

### Q045 — search insufficiency vs representational insufficiency

**Prometheus may already have the cleanest instrument in existence for this**, and it was
built for another purpose. D-4's per-episode **viable-only oracle** performs reverse BFS over
ONLY the edges observed during the run, giving reachability that the navigator failed to
exploit. On four substrates at a 1,200-evaluation budget:

    substrate   far-stratum achieved   oracle far-reach   attribution
    S1_REG      0.00-0.02              0.41               SEARCH weakness at this budget
    S2_STACK    0.15                   0.50               substantial navigation regret
    S4_MEM      0.53                   0.73               moderate regret
    S3_REWRITE  0.00                   0.00               TOPOLOGY failure, not search

That is exactly Q045's T1 discrimination — *matched problems where one requires more search
and another requires a missing primitive* — realised on real substrates rather than on matched
synthetic pairs. The gap versus Q045 as written: D-4 attributes at the SUBSTRATE level, not
per-problem, and the oracle is a lower bound because it sees only observed edges.

### Q046 — one defect behind different-looking failures

`engine/ledger/AUTOPSY_TAXONOMY.md`: 21 agents autopsied, 11 raw class labels merged into 5
clusters plus a singleton, each cluster terminating in **the design invariant that would have
prevented it**, with a named consumer. Q046's T1 failure mode — *FAIL if clusters form by
domain or text* — is precisely what that document avoids by clustering on mechanism.

Q046's T1 asks for clustering ARI >= 0.9 against known latent fault classes. **We have the
clustering and no ground-truth fault labels**, so the ARI has never been computed. That is a
concrete, cheap prerequisite: plant known defects, re-derive the taxonomy blind, compute ARI.

### Q098 and Q085 — already researched this week, with numbers

Q098 (genuine progress vs self-rewarding metrics) and Q085 (evaluation-aware deception) were
the subject of three deep-research passes on 2026-08-28/29, all committed:

- `report_SELECTION_DISCOVERED_CONCEALMENT.md` — Ofria & Wilke 2004 verbatim: organisms under
  a measurement-keyed kill rule "purposefully downgraded their own performance so as not to be
  killed", with **no survival, self-preservation or deception term** anywhere. Q085 has a
  DEMONSTRATED positive instance that predates the deep-learning literature by two decades.
- The mitigation result, which bears on Q085's T1: **distribution-matching the evaluation
  environment FAILED** — the population moved to probabilistically expressing the trait. The
  fix that held was structural: selection moved off the separable test episode entirely.
  **Q085's T1 presumes hidden evaluation contexts are constructible; the one documented
  attempt to construct them was defeated.**
- `report_GRADIENT_HACKING_AND_CONTAINMENT.md` — eval-awareness is causally linked to reduced
  covert behaviour, so every measured scheming rate is a lower bound.
- Q098's T3 (*agent creates an independent validator predicting the hidden objective*) is
  `feedback_promotion_requires_independent_failure_mode`: promotion requires an INDEPENDENT
  FAILURE MODE, not merely a non-synthetic adjudicator; same-model audit is ~zero strength.
  That is also Q050's answer in one line.

### Q100 — the charter's own thesis

`aporia/CHARTER_MUTABLE_LANGUAGE_OF_THOUGHT_2026-08-26.md` as amended is Q100 restated. The
current state: TINYPROG (`aporia/lot/world3.py`) is **WORLD_ADMISSIBLE** on five unused seeds —
solvable, non-trivial, 734x search headroom, five classes nuisance-matched, separated on the
reuse axis at p 0.0005. Q100's T2 (*equal-compute search without failure-derived representation
change*) is the A3 rung, preregistered but not yet run. Q100's T3 (transfer to >=3 unrelated
worlds) is unbuilt.

## 4. The language-subtraction axis, which is the loop's through-line

The operator's fifth requirement — subtract human language — is the sharpest discriminator in
the list, and Prometheus is unusually well placed on it because D-3, D-4, D-5 and TINYPROG are
all substrates with **no natural-language labels, no human-named categories, and no
human-authored task descriptions**. Distances are intrinsic behavioural fingerprints; scoring
is verifier-confirmed solvability and metered evaluation counts.

Three classes, to be assigned per question in its dossier:

    NATIVE     already posable in a language-free substrate (Q033 Q039 Q047 Q054-56 Q060 Q100)
    RESTATABLE language enters only through task framing and can be replaced by a generator
    BOUND      the question is ABOUT language or human categories; subtraction changes it

**And the caution that governs all three**, from `report_ENDOGENOUS_MEMORY_GEOMETRY.md`:
construction can be language-free but **evaluation almost never is**. The one clean end-to-end
case in that report (BIGANN) removed labels from both codebook and correctness criterion, and
still could not remove the human choice of metric, feature space and corpus. So a dossier
claiming a language-free formulation must state its scoring criterion first and defend THAT,
not the encoder. The deeper bottleneck is the **similarity relation** — what counts as the same
outcome — which in every examined system was imported rather than discovered.

## 5. First fire

Run `wf_17f1a37b-646`, 2026-08-31: prior art and measurement discipline for the
Q002/Q005/Q047/Q060/Q100 cluster, with the non-redundancy test and the definitional objection
as explicit targets, plus which claims could be evaluated language-free and which falsification
controls the field actually runs.

## 6. Standing cautions for every dossier in this loop

- A question's three tests are the operator's and are frozen. Where a test is **unreachable**
  as written — as Q060's T2 is for any composition — say so and prove it, rather than
  quietly restating the test.
- Report **evaluations, not generations**, in anything touching search budgets.
- No dossier may claim a prerequisite is satisfied without naming the artifact and its commit.
- `feedback_llm_convergence_is_gravity_amplifier` — where a frontier model and this list agree,
  that is corpus gravity, not validation.
