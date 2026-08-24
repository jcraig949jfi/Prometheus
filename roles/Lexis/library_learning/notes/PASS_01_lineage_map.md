# Pass 1 — Lineage map, primary sources, first technical model

**Date:** 2026-08-24
**Method:** primary-source fetch (arXiv abstract pages, arXiv HTML full text, repo docs) plus local
repo reads. Every number below is tagged with where it came from. Claims I could not verify from a
primary source are marked **[UNVERIFIED]**.

---

## 1. The four nodes, confirmed

### DreamCoder (2020)
- **Full title:** *DreamCoder: Growing generalizable, interpretable knowledge with wake-sleep
  Bayesian program learning*
- **Authors:** Kevin Ellis, Catherine Wong, Maxwell Nye, Mathias Sable-Meyer, Luc Cary, Lucas
  Morales, Luke Hewitt, Armando Solar-Lezama, Joshua B. Tenenbaum
- **arXiv:** 2006.08381 [cs.AI], submitted 2020-06-15
- **Code:** `github.com/ellisk42/ec`
- **Claim of record:** learns to solve problems by writing programs; builds expertise by *creating
  programming languages for expressing domain concepts*, together with a neural network to guide
  search within those languages. Wake-sleep alternation extends the language with new symbolic
  abstractions and trains the recognition network on imagined and replayed problems. Reported to
  rediscover "the basics of modern functional programming, vector algebra and classical physics,
  including Newton's and Coulomb's laws."

### Stitch (POPL 2023)
- **Full title:** *Top-Down Synthesis for Library Learning*
- **Authors:** Matthew (Maddy) Bowers, Theo X. Olausson, Lionel Wong, Gabriel Grand, Joshua B.
  Tenenbaum, Kevin Ellis, Armando Solar-Lezama
- **arXiv:** 2211.16605, v1 2022-11-29, v2 2023-01-15
- **Venue of record:** Proc. ACM Program. Lang. 7, POPL, Article 41 (Jan 2023), pp. 1182–1213
- **Code:** `github.com/mlb2251/stitch` (Rust), bindings at `mlb2251/stitch_bindings`
- **Claim of record:** corpus-guided top-down synthesis of library functions. Builds abstractions
  directly from DSL primitives, using syntactic pattern matching over intermediate abstractions to
  prune the search space. **3–4 orders of magnitude faster than DreamCoder's compression, 2 orders
  of magnitude less memory, comparable or better library quality — quality measured by
  compressivity.**

### LILO (ICLR 2024)
- **Full title:** *LILO: Learning Interpretable Libraries by Compressing and Documenting Code*
- **Authors:** Gabriel Grand, Lionel Wong, Maddy Bowers, Theo X. Olausson, Muxin Liu, Joshua B.
  Tenenbaum, Jacob Andreas
- **arXiv:** 2310.19791, submitted 2023-10-30, v4 2024-03-15
- **Code:** `github.com/gabegrand/lilo`
- **Three modules:** (1) LLM-guided program synthesis; (2) Stitch symbolic compression; (3)
  **AutoDoc** — infers natural-language names and docstrings from contextual usage examples.
- **Why AutoDoc matters:** it is not cosmetic. The paper's claim is that documentation *boosts
  downstream performance* by helping the synthesizer interpret and deploy the learned abstractions.
  Naming is part of the reuse mechanism.
- **Domains:** string editing, scene reasoning, graphics composition (three inductive synthesis
  benchmarks). Baseline includes DreamCoder.

### Twitch (2026)
- **Full title:** *Twitch: Learning Abstractions for Equational Theorem Proving*
- **Authors:** Guy Axelrod, Moa Johansson, Nicholas Smallbone (Chalmers / Univ. of Gothenburg)
- **arXiv:** 2603.06849, submitted 2026-03-06. Comments field: "20 pages, submitted to IJCAR 2026"
- **This is the node that matters most to us.** It carries Stitch's abstraction machinery into
  *equational theorem proving*, and it learns abstractions **from failed partial proofs** as well as
  from successful ones.

---

## 2. Technical model — how the machinery actually works

### 2.1 DreamCoder's toolchain (from `ec/docs/software-architecture.md`)

A deliberate two-language split: **OCaml as performant backend, Python as frontend**, with the
recognition network the exception (Python/PyTorch).

- `dreamcoder.py` — entry point, orchestrates the iterative cycle, checkpoints via pickle
- `enumeration.py` + `solver.ml` — spawns OCaml child processes, parallel across CPUs, returns
  solutions as lambda-calculus expressions in JSON
- `dreaming.py` + OCaml backend — background workers generating training data ("fantasies")
- `recognition.py` — PyTorch net predicting the likely program for a task, trained on real *and*
  dreamed tasks
- `compression.py` + `compression.ml` — takes wake-cycle programs, returns an optimized library
- `primitiveGraph.py` — PDF snapshots of library state per iteration

**Core data structures:** `Program` (lambda calculus, de Bruijn indices; Application / Abstraction /
Primitive), `Type` (ground types, type variables, constructed types; instantiate/unify/apply),
`Grammar` (Primitives + Inventeds, with numerical weights giving a probability model — this *is* the
library), `Task` (I/O examples + type), `Frontier` (programs solving a task).

**Interface:** JSON over process boundary. Python sends serialized Grammar + task specs; OCaml
returns program sets.

**The loop:** parallel dreaming + enumeration → recognition training → guided enumeration →
compression → visualize → checkpoint.

### 2.2 Stitch — what replaced DreamCoder's compression step

Rust CLI, `compress` binary. Input is JSON: a list of programs in Lisp-like lambda syntax with de
Bruijn indices. Output is JSON with rewritten programs plus, per discovered abstraction, its
**arity, utility score, usage count, and body**.

Key knobs: `--max-arity` (default 2), `--iterations` (number of abstractions to learn, default 3),
`--threads`, `--cost` (cost function), a family of `--no-opt-*` pruning toggles, `--batch` /
`--dynamic-batch`.

Documented example: the `nuts-bolts` dataset (Wong et al. 2022) — **6.06× compression across three
iterations**, discovering graphics-DSL primitives used hundreds of times across programs.

**The thing to hold onto:** Stitch's objective is a *cost improvement* — compressivity. Everything
downstream in this lineage inherits that objective.

### 2.3 Twitch — the mathematics-facing node

**Abstraction, formally:** a function definition generalizing parts of proof terms — a λ-term pattern
such as `g(α) := f(α, α)`, where `α` is a schematic parameter standing for an arbitrary subterm.
Compression metric is **the product of the size of the function and the number of places it can be
used**. Higher-order abstractions are discarded in practice; abstractions must be first-order.

**Two extraction pathways.**

*From failed/partial proofs:*
1. Run Twee on hard problem `Ph` for a fixed budget (150–500 s)
2. Extract all derived lemmas `l = r` from the incomplete proof
3. Score by "interestingness": `s(l=r) := |T(l=r)| / |l=r|²` — i.e. **simple statements with long
   proofs rank highest**
4. Take top `k` (k = 50–100), feed all their terms to Stitch
5. Rerun Twee on `Ph` with goal flattening plus the discovered abstractions

*From successful proofs in the same domain:*
1. Run Twee on easier problems in domain `D`
2. Extract proof terms, run Stitch per problem → *local* abstractions
3. Re-verify each abstraction clears a speedup threshold `τ`
4. Pool the survivors, run Stitch again over the pool → *domain* abstractions
5. Deploy to hard problems

**How Twee is modified — and this is the subtle part.** Abstractions are *not* added as axioms. They
are heuristic guidance on the weight calculation for critical pairs. For abstraction `A` matching
term `Aσ`:

    w(Aσ) = w_A + Σ_{x ∈ dom(σ)} w(xσ)

where `w_A` is a constant `k` or `w(skel(A)) × k`. Effect: an equation matching a known-useful shape
is *more likely to be selected* from the queue. Cost drops two ways — the abstraction skeleton counts
as minimal weight, and repeated subterms are counted once (an abbreviation effect). Twee also gets
term-level "resonators": variants matching only when variables map to variables rather than compound
terms.

**Reported numbers.** TPTP UEQ, v9.2.1. 1,041 problems total, distributed GRP 481, LAT 126, COL 120,
LCL 84, REL 81, BOO 56, RNG 48, ROB 25, ALG 20.
- Domain abstractions + goal flattening: ~25 more problems solved within 300 s; roughly *halves*
  runtime on problems baseline Twee already solved within 300 s
- Example LAT075-1: ~250 s → ~10 s with axioms, ~130 s with native abstractions
- Hard problems (rating ≥ 0.9, Twee alone > 1000 s): partial-proof abstractions 11; domain
  abstractions 18; combined 19 (incl. LCL351-10)
- Abstractions degrade more gracefully than axioms: timeouts climb sharply for axioms beyond one
  definition, while abstractions tolerate many more

> **Discrepancy to resolve [UNVERIFIED]:** the abstract advertises "12 rating-1 problems"; the body
> numbers I extracted are 11 / 18 / 19 for rating ≥ 0.9. "Rating 1" and "rating ≥ 0.9" are different
> sets. Next pass must read the results section directly and reconcile, rather than trusting either
> summary.

**Limitations the authors state themselves** (worth quoting because they map onto our own open
problems): domain construction is "quite crude" — restricted to the same TPTP theory with shared
symbols; lemma scoring and term extraction are "simple heuristics"; abstraction selection is
"a single-objective optimization problem focused primarily on runtime speedup"; the Twee
implementation is "quite brittle" — demodulation can destroy abstraction matching.

**Their stated future work includes:** multi-objective selection criteria (proof length, robustness
across strategies), and "learn abstraction proposals directly from accumulated (problem, abstraction)
training data, potentially via language models."

---

## 3. The objective function — the actual seam

Every node in this lineage selects abstractions by **compressivity**: does adding this abstraction
make the existing corpus cheaper to describe? Stitch's cost improvement, Twitch's size × usage-count
product. The MDL/Bayesian justification is principled, not lazy — recurring structure is *likely* to
be reusable structure.

But it is a statement about **yesterday's corpus**. The alternative objective — does this abstraction
*enlarge what can subsequently be reached under fixed compute* — is a statement about **tomorrow's
frontier**. These are related but not identical, and the literature has, so far, optimized only the
first. Twitch is the one node that partially crosses over: its `τ` threshold re-verifies each
abstraction by **measured speedup**, which is a reachability proxy, not a compression proxy. That
makes Twitch the closest prior art to a reachability-selected library, and it is 5 months old.

**Formulation to carry forward** (from the frontier-advisor commentary, recorded as a hypothesis to
test, not a result):
- `C(a)` = corpus compression gain
- `R(a)` = Δ reachable search capability under fixed compute
- `H(a)` = actual held-out downstream solve gain

The experiment of interest is whether `C` predicts `R`, and whether `R` retains predictive power for
`H` after conditioning on `C`. Four quadrants, all meaningful; the prize quadrant is low-`C`/high-`R`
— abstractions that barely compress history but materially move the frontier, which a
compression-selected pipeline is structurally liable to discard.

---

## 4. Prometheus-side reality check — the part that must not be skipped

The framing that opened this thread asserts that **Apollo measures the reachable ceiling by
construction**. I went looking for that machinery. As of this pass I could not find it.

- `apollo/README.md` describes Apollo as "the model-training arm of Prometheus — an evolutionary
  pipeline for training small LLMs against novel fitness functions." Current generation v2d.
- `apollo/ARCHITECTURE.md` (v2_d, "Gradient Recovery") contains **no** occurrence of "reachable",
  "ceiling", "abstraction", or "by construction". It is a diagnosis-and-repair document for an
  evolutionary loop that had stalled: flat fitness landscape at **0% raw accuracy across the entire
  population**, structural LLM mutations winning selection 0 times in 485 elite entries, and an AOS
  bandit reward corrupted to 1.0 for every operator.
- Its four fixes are difficulty curriculum, post-mutation parameter annealing, accuracy-only AOS
  reward before gen 300, and selection-death logging.

**Therefore [UNVERIFIED]:** the claim that Apollo already has machinery for empirically estimating
`R(a)` is not established. It may exist elsewhere (`apollo/cycles/o1_enumeration/PREREGISTRATION.md`
mentions reachability and is unread as of this pass), or it may be an aspiration read back into the
system. This must be settled before anyone designs a `C`-vs-`R` experiment, because that experiment's
entire premise is that we can already measure `R` cheaply. Building on an unverified capability claim
about our own code is precisely the failure mode the program has logged repeatedly.

---

## 5. Where the Prometheus analogues actually sit

First-cut mapping, to be sharpened next pass:

- **DreamCoder's `Grammar` (primitives + inventeds with weights)** ↔ the forge tool registry /
  operator menu. Both are "the library". Ours is not a probability model over a DSL; theirs is.
- **DreamCoder's compression step / Stitch** ↔ *no clean analogue*. Prometheus forges tools by LLM
  generation and tests them against a battery; it does not extract abstractions by compressing a
  corpus of successful solutions. This is the largest structural gap.
- **DreamCoder's recognition model** ↔ the Learner / falsification-routing head. Same role: predict
  where to search.
- **Twitch's failed-proof mining** ↔ the failure-metabolization doctrine and the 132M-record REJECTED
  corpus. Same instinct, arrived at independently. **Their corpus is proof attempts on TPTP; ours is
  verdict-labelled operator applications across catalogs.**
- **Twitch's `τ` speedup re-verification** ↔ the closest thing in the literature to our
  ceiling-by-construction ambition.
- **LILO's AutoDoc** ↔ nothing on our side. We have no mechanism that names and documents a learned
  abstraction so that a downstream synthesizer can deploy it. Given LILO's claim that documentation
  *improves performance rather than just readability*, this is a cheap thing to steal.

---

## 6. Two internal readings, in tension — both recorded, neither adjudicated

**Reading A (Aporia, amplified by the frontier advisor):** this is a consequential reframing. The
field optimizes compression of yesterday; Prometheus can optimize reachability of tomorrow. Either
experimental outcome changes the architecture, so the experiment is worth running.

**Reading B (Diomedes, `roles/Diomedes/RECON_2026-08-24_navigational_information.md`, same day):**
"*Program synthesis / DreamCoder-line library learning*: the operator-menu-growth answer, already
named in the ladder canon's H2 precondition 3." And, more bluntly: "**We are not looking at a new
idea; we are looking at a corpus that could test an old idea cheaply.**" On this reading the only
genuinely unusual thing is the asset — a failure-dense, verdict-labelled, cross-catalog record with
an *exact* oracle rather than a learned one — and that is a claim about data, not about method.

These are not the same conclusion, and the difference is decision-relevant: A justifies new
machinery, B justifies pointing existing machinery at the corpus. Do not merge them into a
consensus. Next passes should look for evidence that discriminates.

---

## 7. Carried forward to pass 2

1. Read `apollo/cycles/o1_enumeration/PREREGISTRATION.md` and settle the `R`-machinery question.
2. Reconcile the Twitch rating-1 / rating ≥ 0.9 discrepancy from the results section directly.
3. Fill in the pre-DreamCoder lineage (EC / explore-compress, and the Bayesian program-learning
   roots) and the side branches (LAPS; LaSR, `arXiv:2409.09359`, symbolic regression with a learned
   concept library).
4. Get Stitch's actual cost function and utility definition from source, not from docs prose.
5. Map who cites whom — build the citation graph, find who else has taken Stitch into mathematics.
6. Establish whether anyone in this lineage has *ever* selected abstractions on a
   forward-reachability criterion rather than compressivity. If someone has, the delta collapses and
   Reading B strengthens considerably.

## Sources touched this pass

- arxiv.org/abs/2006.08381 — DreamCoder
- arxiv.org/abs/2211.16605 — Stitch (POPL 2023)
- arxiv.org/abs/2310.19791 — LILO (ICLR 2024)
- arxiv.org/abs/2603.06849 + /html/ — Twitch
- github.com/ellisk42/ec/blob/master/docs/software-architecture.md
- github.com/mlb2251/stitch
- local: `apollo/README.md`, `apollo/ARCHITECTURE.md`,
  `roles/Diomedes/RECON_2026-08-24_navigational_information.md`

---

## 8. Addendum (same pass, after background scan completed)

### 8.1 Two nulls, recorded so they are not re-chased

- **No prior internal catalog entry for this literature.** A repo-wide scan for
  DreamCoder / Stitch / LILO / "library learning" returned only `arcanum/questions/` hits, and those
  are false positives — `Q-698A1830` is a XENOLEXICON-generated question, *"Can a manifold be
  'stitched' together from disparate, non-overlapping algebraic fields?"* The word matched, the
  subject did not. Aporia's find is genuinely new to the program's records.
- **The "reachable" hits were unrelated** — RPH docs, the xenolexicon paper, two Hephaestus
  humanreadable files. No hidden reachability machinery surfaced by name.

### 8.2 Diomedes' citation checks out, and it is heavier than it looked

`aporia/doctrine/reasoning_ladder.md` §6, **H2 — FAILURE-LANDSCAPE NAVIGATION**, states three
preconditions "each already measured, none yet satisfied." Precondition 3 verbatim:

> **A growing operator menu with verified admission.** Infinite recombination over a fixed menu hits
> the bounded-menu wall (the gen-30 lesson). The menu must grow — but in-loop LLM mutation is
> falsified (llm2: 2,152 mutations, zero lift), so admission must be verifier-gated: an operator
> enters the menu only kernel-checked or computation-checked (W3-shaped: model writes a small
> verified primitive *from a typed diagnosis* — untested, not falsified).

Three consequences for this study.

**(a) The delta is not two-way, it is three-way.** Admission criteria on offer:
- *Compressivity* — DreamCoder, Stitch, LILO. Does it make the existing corpus cheaper?
- *Measured speedup* — Twitch's `τ` re-verification. Does it move the frontier under fixed compute?
- *Verifier-gated correctness from a typed diagnosis* — Prometheus H2 precondition 3. Is the
  primitive kernel-checked, and did a diagnosis of a specific failure call for it?

The third is ours and, as far as pass 1 can tell, unoccupied in this lineage. It is also a
*generative* criterion rather than a *selective* one: it governs how a candidate is produced, not
merely which candidates survive.

**(b) The literature is not naive about verification, though.** DreamCoder admits a program to a
frontier only if it actually solves the task's I/O examples; Twitch's abstractions are mined from
proofs Twee actually found. So compression in both cases operates over an *already-verified* corpus.
The difference is where the gate sits: they verify the solution then compress; precondition 3 wants
to verify the primitive itself, generated from a typed diagnosis of a failure. Same instinct,
different placement — this is a sharper statement of the delta than "compression vs reachability."

**(c) A direct conflict with LILO that must be resolved.** Precondition 3 records that **in-loop LLM
mutation is falsified locally: llm2, 2,152 mutations, zero lift**. LILO's headline is that
LLM-guided synthesis *plus* compression *plus* documentation builds better libraries and solves more
tasks. Both cannot be straightforwardly true of the same setup. Candidate resolutions, in rough
order of likelihood:
1. Different objects — llm2 mutated *organisms/parameterized structures*; LILO synthesizes
   *programs against I/O specifications* with a verifier in the loop. Mutation ≠ synthesis-to-spec.
2. Different feedback — LILO's synthesizer sees documented abstractions (AutoDoc) and typed
   examples; llm2's mutator likely saw neither.
3. Different fitness landscape — Apollo v2d was at 0% raw accuracy with no gradient (§4), so *no*
   operator could have shown lift there, LLM or otherwise. A zero-lift result on a flat landscape is
   weak evidence about the operator.

**Resolution 3 is the one that would matter most and is checkable locally.** If llm2 ran under the
same flat-landscape conditions `ARCHITECTURE.md` diagnoses, then "in-loop LLM mutation is falsified"
is measured on a population where nothing could have registered lift — which would make it a much
weaker precondition than the canon's phrasing implies. Pass 2 should establish llm2's conditions
before this study leans on the claim in either direction.

### 8.3 Effect on the two readings

Reading B gains: the idea *was* anticipated in canon, with a citation that verifies exactly.
Reading A also gains: the canon's own precondition 3 says the menu must grow and names the
admission problem as open and untested (`W3-shaped ... untested, not falsified`) — which is
precisely the hole this literature has spent five years filling. The honest position after pass 1 is
that both readings are strengthened, on different clauses, and the discriminating evidence is
whether verifier-gated admission from a typed diagnosis actually outperforms compression-selected
admission on our corpus. That is a real experiment, and it is not the C-vs-R experiment originally
proposed.
