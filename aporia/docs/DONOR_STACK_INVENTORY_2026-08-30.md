# Donor-stack inventory — what Prometheus has already done with the prior-art tools

**Compiled:** 2026-08-30 by Aporia, in answer to an operator question arising from a
ChatGPT-side proposal to raid POET/PAIRED/pyribs/QDax/DreamCoder/Stitch/egglog/DisCoPy/
TensorLy/Hypothesis/MiniZinc/cvc5/Lean as donor machinery.

**Method:** ripgrep passes over the tree, `importlib.util.find_spec` checks per package, and
`git log` on each hit. Evidence-graded; nothing inferred from memory. This is an inventory
enumeration, per the standing rule that a scope claim is a measurement needing the same
evidence as a headline.

## Grading scale

    RUNNING   installed AND consumed by committed code or experiments
    SPIKED    installed, one demo/spike run, verdict recorded, not adopted
    STUDIED   literature raided from primary sources, verdict recorded, no code
    NATIVE    we built our own instead of taking the donor
    ABSENT    verified not installed and no code

## 1. Headline answers

**DreamCoder was STUDIED, not installed.** No DreamCoder or Stitch code exists in the repo and
neither package is installed. What exists is a closed 8-pass archaeology at
`roles/Lexis/library_learning/` (opened and closed 2026-08-24, committed `85c982f9`) plus a
standing `role: comparison` citation to arXiv:2006.08381 across WORKLOG passes P156-P162.

**RAID then WRAP is already policy.** "Standing Order #1: Wrap, don't rewrite" is on the books,
quoted in `techne/lib/mahler_measure.py` and
`techne/loop/rung_notes/CYCLE051_SQUAREFREE_MAHLER_PREREG.md`. The proposal's PHASE 0 is
existing doctrine, applied unevenly.

**The posture was concluded 2026-08-24** in CONSUMPTION.jsonl: "adopt the field's cheap
synthesis and keep our own expensive scoring; the assay is the asset."

## 2. RUNNING

    hypothesis    6.165.10   30+ files (search cap hit); prometheus_math/tests/*,
                             techne/ladder_circuits/*, adversarial_fixtures.py,
                             adversarial_registry.py; persistent DB at .hypothesis/
    z3-solver     5.0.0.0    30+ files
    sympy         1.14.0     30+ files; owns exact decomposition under SO#1
    networkx      3.6.1      30+ files
    quimb         1.15.0     prometheus_math/tensor_train.py wraps
                             MatrixProductState.from_dense
    torch         2.11.0+cu128
    numpy 2.2.6 / scipy 1.17.1 / scikit-learn 1.9.0 / pandas 3.0.5 / autoray 0.10.1

The Adversary-bench donor (Hypothesis) is already the backbone of the math test suite.

## 3. SPIKED

    egglog        13.2.0     exactly ONE consumer: techne/loop/egglog_saturation_demo.py,
                             commit 631ee060, 2026-08-21, "loop cycle 007 ... saturation PASS"

Recorded verdict from the file's own docstring: equality saturation proves `(a*2)/2 == a` with
UNORDERED rules, the noncanonical-composition capability fixed pipelines lack. R2 proper is
overkill; R2.5+ earns rent exactly when multiple equivalent intermediate forms must coexist and
a later rewrite depends on which form exposes a match; R4 — extraction over a saturated e-graph
IS strategy selection with search externalized; R5 — an e-graph is branch-holding at scale, but
saturation needs the whole term and is not a streaming mechanism.

The Lens Lab e-graph idea is therefore not speculative here. It was tested and parked with a
stated re-entry condition.

## 4. STUDIED — the library-learning archaeology

`roles/Lexis/library_learning/` — 8 passes; README, SIDE_BY_SIDE, RETROSPECTIVE, SOURCES and 7
pass notes, every source graded primary/secondary. Four families mapped, not one:

    A  MIT           DreamCoder 2020 -> LAPS 2021 -> Stitch POPL23 -> LILO ICLR24
    B  UW PLSE       egg -> Ruler OOPSLA21 -> babble POPL23 -> Enumo OOPSLA23 (+ShapeCoder)
    C  Chalmers      QuickSpec -> Hipster CICM14 -> Lemmanaid -> Twitch 2026
    D  LLM libraries LATM -> Voyager -> TroVE(+refutation) -> ReGAL -> DreamProver

Measured verdicts:

- **Stitch is the wrong tool** for Apollo pipelines: it consumes lambda terms with de Bruijn
  indices and prunes by syntactic pattern matching; an Apollo pipeline is a state-mutating
  operator sequence.
- **babble is architecturally right**, and the equational theory it needs is derivable today
  from decorators already in the tree.
- Static audit of all 26 declared blackboard operators: **zero undeclared writes** (one
  undeclared read, in `select_nth`), so a Bernstein-conditions commutativity theory from
  `@blackboard_op(reads=..., writes=...)` is sound.
- Over the ten transformers of O1's ceiling pipeline: **39 of 45 operator pairs commute freely;
  only 6 are order-dependent.** The six are the semantic spine, and the write-write hazard
  between `parse_names_and_relations` and `relations_from_facts` is exactly the bug that
  invalidated two of O1's runs — statically derivable from metadata already present.
- O1 sampled 48 orderings per subset against 166,320 because it treated ordering as opaque.
- **Family B is more relevant than Family A**: Ruler infers the rewrite theory (5.8x smaller
  rulesets, 25x faster than a CVC4-based comparator), Enumo handles undecidable equality
  (derived 90% of Halide's handwritten rules), babble abstracts modulo the theory.
- ShapeCoder is the closest published setting to "a pile of forge tools, not a clean DSL."
- **Self-correction in the study:** the claim that our verifier-gated admission criterion was
  "unoccupied in that lineage" is wrong and has been since 2014 — Hipster's proof mode
  discovers the missing lemmas needed to pass a specific goal, the same shape as W3.

Aporia cycles 151-S / 155-S (2026-08-24), the Stitch objective audit: full PDF fetched, 135,431
characters over 42 pages, keyword census over the entire text — `compression 44, compressive 17`
against `downstream 0, accuracy 0, success rate 0, synthesis time 0`. The field assumes
compressivity and never validates it against reachability. Prometheus is ahead on the
measurement axis, behind on synthesis machinery.

**The limit, still binding:** better abstraction tooling over a substrate whose ceiling is
0.833 by construction cannot exceed 0.833. Raising it requires growing the operator set, and
none of this machinery does that on its own.

## 5. NATIVE

- `agent_d5_blind/` — **the library-learning experiment, run.** Cap 64, most-recent-first
  eviction, genotype-deduped, no labels or oracle data; admission is the solving genotype plus
  up to 4 behavior-distinct best-scoring candidates; 50% of immigrant draws come from the
  library, mutated, every candidate metered identically. Ablations: no-history, random-library,
  shuffled-history, frozen-half. Verdict HISTORY_FINDABILITY_ADVANTAGE, +10.95pp CFR, p=0.0007,
  task-level n=42; shuffled-history retains 100% and random-library 39%, so the advantage is
  library CONTENT, not developmental correspondence. **This is the compute-matched control the
  literature's own re-evaluation demands, and it was run.**
- `prometheus_math/symbolic_tensor_decomp.py` — CP (ALS) and Tucker hand-rolled, NOT TensorLy.
- `prometheus_math/tensor_train.py` — TT wrapped from quimb under Standing Order #1, with the
  correct structure-destroying null baked in (slice permutation is provably rank-invariant).
- `incubation/` v1, v2, v3 — operator and lens genesis lines, all closed with verdicts.

## 6. ABSENT (verified by import check, 2026-08-30)

    tensorly   discopy   pyribs/ribs   qdax   evotorch
    stitch/stitch_core   minizinc   cvc5   leandojo   dreamcoder

POET / PAIRED / ACCEL: zero code, document mentions only. No QD or MAP-Elites layer of any
kind. D-4/D-5 navigators use population + tournament-3 + 10% immigrants — a plain EA, not
MAP-Elites and not novelty search.

Lean: toolchain installed system-wide (`elan, lake, lean, leanc, leanchecker, leanmake,
leanpkg` in `~/.elan/bin`) but no Lean project directory in the repo. Installed, unused.
Exact-oracle load is carried entirely by z3 + sympy.

## 7. The four gaps

1. **Inconsistent wrap discipline.** TT wraps quimb under SO#1 while CP and Tucker are
   hand-rolled ALS in the same package. TensorLy would replace the hand-rolled half. This is
   the clearest instance of the failure the proposal worries about, already inside
   `prometheus_math`.
2. **babble/Ruler recommended, never installed.** The study named the tool, proved the theory
   it needs is already derivable, and stopped.
3. **No QD layer at all.** Nothing has ever been run against a MAP-Elites archive here.
4. **Worlds has no donor code.** The bench with the strongest prior art has the least
   Prometheus machinery.

## 8. What the proposal gets right, and where it double-counts

Right: the donor-stack posture (already SO#1); babble/e-graph relevance, independently reached
here on 08-21 and 08-24 from the Apollo side; and "do not hand-roll tensor decompositions" —
which lands on CP/Tucker, not on TT.

Double-counts: the library-learning raid has already been run to ground over 8 passes with a
measured tool-fit verdict and a stated ceiling limit. Re-commissioning it as PHASE 0 repeats
work finished 2026-08-24.

**Caution from our own ledger:** the study's pass 2 found that the advisor's macro mechanism —
typed I/O, frozen internals, atomicity under mutation, retained provenance, recursive formation
— "derived from Apollo's document alone" is DreamCoder's mechanism, specified accurately and
uncited. Per `feedback_llm_convergence_is_gravity_amplifier` that is corpus gravity, not
independent validation, and the same check should be applied to the present proposal before its
convergence is read as confirmation.
