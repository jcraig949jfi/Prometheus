# Pass 3 — the admission-criterion taxonomy, the field's own kill, and the frontier that is still open

**Date:** 2026-08-24
**New primary sources this pass:** DreamProver (arXiv 2604.26311), the compute-matched TroVE
re-evaluation (arXiv 2507.22069), babble (arXiv 2212.04596), LaSR (arXiv 2409.09359).
**New local evidence:** `apollo/src/genome.py`, `apollo/src/gene_extractor.py`.

---

## 1. The lineage is wider than four nodes

Add to the map:

**babble — *Learning Better Abstractions with E-Graphs and Anti-Unification*** (arXiv 2212.04596,
2022). Developed **concurrently** with Stitch and closely related; uses e-graphs and anti-unification
rather than top-down corpus-guided search. Same objective family (compression), different machinery.

**LaSR — *Symbolic Regression with a Learned Concept Library*** (Grayeli, Sehgal, Costilla-Reyes,
Cranmer, Chaudhuri; NeurIPS 2024, arXiv 2409.09359). Induces a library of **abstract textual
concepts** via zero-shot LLM queries over high-performing hypotheses, then conditions both
evolutionary steps and LLM-guided hypothesis generation on those concepts. Outperforms SOTA symbolic
regression on Feynman equations; used to discover novel LLM scaling laws. **The concepts are natural
language, not lambda terms** — a materially different representation choice.

**DreamProver — *Evolving Transferable Lemma Libraries via a Wake-Sleep Theorem-Proving Agent***
(Zhang, Sun, Bi, Geng, Ma, Li, Si; arXiv 2604.26311, 2026-04-30). **This is DreamCoder for
mathematics, four months old, and it is now the most relevant node in the study** — more relevant
than Twitch.

---

## 2. DreamProver in detail — the closest thing to what Prometheus wants

**Substrate:** Lean + Mathlib. Provers exercised include GPT-5.3-Codex, Gemini variants,
DeepSeek-Prover-V2-7B, Goedel-Prover-V2 (8B/32B), against a Hilbert baseline.

**Wake stage:** attempt theorems from a training set using the current lemma library; identify
"learnable theorems" (provable directly with current lemmas); use **recursive theorem decomposition**
via LLM prompting to break harder problems into intermediate theorems.

**Sleep stage:** cluster theorems by semantic meaning (embeddings + K-Means), propose candidate
lemmas per cluster, then three library-update steps — LRU eviction of unused lemmas, duplicate
rejection by **tree edit distance**, and formal verification of each candidate.

**Admission criteria (all must hold):** structural similarity to the cluster's theorems above a
threshold; provable via direct LLM prompting under a *small sampling budget*; non-duplicate by tree
edit distance; library capped at **fewer than 100 lemmas**.

**Use at proof time:** direct prompting with the library first; on failure, fall back to
sketch-and-prove — generate a proof sketch, then discharge each subgoal, using the library in both.

**Results.** Improvement over Hilbert: inequalities +20%, number theory +114%, combinatorics +50%,
**average +61%** across domains. On underrepresented domains vs proprietary LLM baselines: plane
geometry +64%, machine learning theory +161%. Efficiency: **48% reduction in output tokens, 50%
reduction in proof length**. Reuse: **58% of lemmas learned on training sets are reused on test
sets, contributing to proofs of 71% of all successfully proved theorems.**

**And the sentence that matters most to us:**

> Cross-domain transfer: the paper does **not** report library transfer across different mathematical
> domains. Each domain received its own dedicated training library.

---

## 3. The consequence: the cloud-spend criterion is an open problem in the field

The operator's stated precondition for real compute spend, and the advisor's Pass-3 proposal, are the
same thing: *structures discovered in earlier environments become inherited primitives that reduce
search complexity in later, unfamiliar environments.*

As of pass 3, the literature demonstrates:

- **Within-domain reuse** — strongly. DreamProver: 58% reuse, 71% of proofs. Twitch's domain
  abstractions: easy problems in a TPTP theory → hard problems in the same theory, ~25 more solved
  inside 300 s, runtime roughly halved. DreamCoder: multi-layered libraries within a domain.
- **Cross-domain transfer** — **not demonstrated.** DreamProver explicitly trains a separate library
  per domain. Twitch's own stated limitation is that "domain construction is quite crude — restricted
  to the same TPTP theory with shared symbols." Neither crosses.

This rebalances the two readings from pass 1 and 2. Diomedes is right that library learning is an old
idea we would be re-entering rather than inventing. But **the specific property Prometheus needs from
it is not one the neighbours have delivered.** It is their frontier too. That is a materially
different situation from "we are about to reinvent a solved thing," and it is the strongest argument
yet that the contact is worth something beyond a reading list.

It is also a warning: if five years and four labs have not produced cross-domain primitive transfer,
the prior that Prometheus gets it by pointing Stitch at its corpus should be low.

---

## 4. The field's own negative control — read this before believing any library-learning number

**A Compute-Matched Re-Evaluation of TroVE on MATH** (Sesterhenn, Berlot-Attwell, Zenkner, Bartelt;
arXiv 2507.22069, 2025-08-10).

TroVE is LLM tool-use plus in-context learning: the model dynamically acquires and applies reusable
code abstractions while solving problems. The original paper reported that library induction
substantially outperformed baselines on MATH.

The re-evaluation equalizes compute across conditions and finds **the library-induction advantage
does not survive**. The gap substantially diminishes or disappears; the reported improvements were
artifacts of unequal resource allocation rather than genuine methodological advantage.

**How this must be applied here.** Any Prometheus library-learning result — including the transfer
experiment in §3 — is uninterpretable unless the no-library arm receives the same total compute,
counted in the same currency. Apollo already models the right discipline: O1 chose *organism
evaluations*, not wall time, as the comparator, and stated openly that the evaluation-count metric
flatters evolution while the engineering-cost comparison does not. Whatever currency is chosen, fix
it before the run and report both arms in it.

This is the field independently arriving at the program's own doctrine. It should raise confidence in
the doctrine and lower confidence in the headline numbers of §2.

---

## 5. The admission-criterion taxonomy is now five-way

What actually decides whether a discovered structure enters the library:

1. **Compressivity** — DreamCoder, Stitch, babble, LILO. Corpus cost improvement; MDL/Bayesian
   justification.
2. **Measured speedup on the target** — Twitch's `τ` re-verification. A reachability proxy.
3. **Semantic clustering + verified provability under budget + non-duplication, with LRU eviction
   and a hard size cap** — DreamProver. Notably *not* compression at all; it is a curated,
   size-bounded working set.
4. **LLM-judged conceptual salience over high-performing hypotheses** — LaSR. Natural-language
   concepts, no formal compression criterion.
5. **Verifier-gated correctness from a typed diagnosis** — Prometheus H2 precondition 3 (W3-shaped),
   untested locally and unoccupied in this lineage.

Pass 1 called this a three-way split and pass 2 narrowed it. That was wrong in an instructive
direction: the field is **not** monolithically compression-selected. Compression dominates the
program-synthesis branch; the two mathematics-facing nodes (Twitch 2026, DreamProver 2026) both moved
off it, independently, in the same year. The honest statement is that **compressivity is the
program-synthesis lineage's criterion, and the mathematics-facing descendants are already abandoning
it** — which weakens the "compression of yesterday vs reachability of tomorrow" framing considerably,
since the frontier of the field has already made that move.

DreamProver's size cap deserves note on its own. Fewer than 100 lemmas, LRU-evicted. Nobody in this
lineage is accumulating an unbounded library; the working set is deliberately small.

---

## 6. Local find: Prometheus already built a macro extractor, and never wired it in

`apollo/src/gene_extractor.py` — *"Parse forge tools into a two-tier gene library. Tier 1:
Fine-grained genes (high portability) — individual methods. Tier 2: Macro-genes (low portability) —
bundled PARSER+SCORER methods."*

Its `Gene` dataclass carries: `gene_type` ∈ {PARSER, SCORER, FALLBACK, UTILITY, MACRO}, `is_macro`,
`portability_score`, `dependencies`, `parameters`, `imports_needed`, and — directly relevant —
`reads_keys` / `writes_keys`, the same read/write slot discipline the blackboard operators use. There
is a `_create_macro_gene()` that bundles methods into a MACRO gene, and a
`compute_portability_score()` that is its admission signal.

**It appears to be unwired.** A scoped search over `apollo/src/` and `agents/hephaestus/src/` finds
references only in the file itself and its `__pycache__`. *(Scoping caveat: the repo-wide search
timed out at 120 s and was not completed, so "unused anywhere in the repo" is not established —
only "unused in the two directories that would call it.")*

If that holds, it is a significant fact for this study: the O4 macro mechanism the Apollo review
proposes as *new architecture*, and which the advisor ranked as the thing that would make Apollo
interesting, **exists in the tree in prototype form already** — with a portability-based admission
criterion that is a sixth entry for §5's taxonomy and belongs to nobody else. Whether it works is
unknown; it has apparently never been run in a loop.

Pass 4 should establish: was it ever executed, what corpus did it consume, and does
`compute_portability_score` encode anything a Stitch-style utility does not.

---

## 7. Representation mismatch — first concrete statement of the adoption cost

Stitch consumes **JSON lists of programs in Lisp-like lambda-calculus syntax with de Bruijn indices**,
space-separated primitive tokens, explicit parentheses around lambda bodies. It is untyped at the
interface; the pruning is syntactic pattern matching over intermediate abstractions.

Prometheus offers two candidate corpora, and they are differently shaped:

- **Apollo pipelines.** `apollo/src/genome.py` documents organisms as *"primitive routing DAGs over
  25 Frame H primitives. Evolution searches routing strategies; primitives are fixed atoms"* — a flat
  `PRIMITIVE_CATALOG` of 25 names across 8 categories (logic, probability, graph_causal, constraints,
  arithmetic, temporal, belief_tracking, meta), with signatures loaded from
  `agents/hephaestus/src/forge_primitives.py`. *(Note: the Apollo review describes 27 registered
  operators on a blackboard substrate; `genome.py` describes 25 Frame-H primitives. There appear to
  be two representations in the tree — `blackboard_ops*.py` vs `genome.py`. Which one O1 enumerated
  should be confirmed, not assumed.)* Translating an operator sequence into a lambda term is
  mechanical — an operator with declared reads/writes is a function on a state record — but the
  translation is where the semantics live, and `relations_from_facts` **overwriting** `relations`
  (the ordering bug O1 surfaced) is exactly the kind of effect a naive functional encoding erases.
  **A state-mutating pipeline is not a lambda term without an explicit state-threading encoding.**
- **The failure corpus.** 132M verdict-labelled records. This is not a corpus of *programs* at all.
  Stitch has nothing to compress here without first constructing program-shaped objects from traces.

The code's own docstring — *"primitives are fixed atoms"* — is RC7 written into the source. Nothing
in the current representation can invent a primitive; the extractor in §6 is the only component in
the tree that even proposes to.

---

## 8. Standing corrections to earlier passes

- **Pass 1 §3 and pass 2 §6 overstated the compression/reachability delta.** The mathematics-facing
  frontier of this lineage has already left compressivity behind (§5). The delta that survives is
  narrower: *verifier-gated admission from a typed diagnosis*, plus the corpus asset.
- **Pass 2 §7's claim that the transfer experiment "has positive prior art in the literature" was
  wrong.** Within-domain reuse has prior art. Cross-domain transfer — the actual cloud-spend
  criterion — does not (§3). I stated this too strongly and it should not be carried forward.

---

## 9. Carried forward to pass 4

1. `gene_extractor.py` — execution history, corpus consumed, and what `compute_portability_score`
   actually computes. Highest value item; it is ours and unexamined.
2. Which substrate O1 enumerated — `blackboard_ops*.py` or the `genome.py` Frame-H catalog.
3. Stitch's formal utility function from source (the arXiv PDF fetch returned binary; try the
   POPL author copy at `mlb2251.github.io/stitch_jul11.pdf` or the repo source).
4. Twitch rating-1 vs rating ≥ 0.9 reconciliation — carried from pass 1, still open, twice deferred.
5. babble's anti-unification approach in detail — it may suit *state-mutating pipelines* better than
   Stitch's lambda-term assumption, which is the §7 blocker.
