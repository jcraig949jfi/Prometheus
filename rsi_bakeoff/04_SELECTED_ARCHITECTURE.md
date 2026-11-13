# 04 — Selected architecture: the Reflexive Library Learner (RLL)

## 0. One-paragraph statement

RLL is a deterministic, CPU-only program-synthesis learner. Its improvement machinery φ is a set of small programs written **in the same typed DSL** as its task solutions, executed by the same metered interpreter. Improving φ is posed to the system as **one more search problem**, solved by the *current* φ's own search procedure, with the current library θ as its vocabulary. A fixed kernel K, which φ cannot read or write, evaluates every proposed φ′ from a reset knowledge state at matched charges on fresh development families, and accepts or rolls back.

Recursion is possible, but not guaranteed, by two named channels. The point of the experiments in 06 is to cut each channel and watch what happens:

1. **Reflexive reuse.** A change to φ's search procedure also changes the search over φ-edits.
2. **Operational knowledge.** Abstractions learned from tasks become one-node moves in φ-edit space.

```
 ┌──────────────────────────────── K: FIXED KERNEL (owned by RSO; φ has no handle to it) ─────────────────────────┐
 │ typed interpreter + charge meter │ task oracle (dev only) │ ACCEPT(φ,φ′) from θ₀, paired CRN │ ledger │ rollback│
 │ sealed held-out registry (RSO)   │ budget split C_obj:C_meta fixed │ type/size/novelty filters on φ′          │
 └───────▲───────────────────▲────────────────────────▲───────────────────────────▲───────────────────────────────┘
         │ charges            │ pass/fail on dev ex.    │ accept/reject (+screen deltas)
 ┌───────┴────────────────────┴────────────────────────┴───────────────────────────────────────────────────────────┐
 │  OBJECT LEVEL                                        META LEVEL (same machinery)                                 │
 │  tasks ──► SOLVE(φ.score, φ.key, φ.schedule, θ)      "improve φ" ──► SOLVE(φ.score, φ.key, ·, θ) over EDITS(φ)   │
 │              │ solutions, failure traces                         │ candidate φ′ ──► φ.screen ──► top-m ──► K   │
 │              ▼                                                    ▼                                             │
 │  φ.abstract(corpus) ─► K.MDL gate ─► promote ─► θ.L   accepted φ′ pushed on rollback stack; φ ← φ′              │
 │  φ.reweight(counts, θ) ─► θ.G                                                                                    │
 └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
          θ = (L library, G grammar weights, M episodic store)        φ = (score, key, schedule, abstract, reweight, screen)
```

## 1. The DSL (substrate)

A strongly typed, purely functional, total (fuel-bounded) language. Its values:

- `Int` (bounded, ±2⁴⁰ with saturation)
- `Bool`
- `List a`
- `Tree` (labelled S-expression)
- `Prog` (a quoted AST, readable as `Tree`)
- records of `Int` features

Primitive set P₀ (designer-supplied; listed so nothing is hidden). Roughly 40 primitives in five groups:

| Group | Primitives |
|---|---|
| Arithmetic / logic | `+ - * div mod min max == < not and or if` |
| Lists | `nil cons head tail len map filter fold range rev sort sort_by take drop zip sum count index` |
| Trees / ASTs | `label children size depth subtrees replace_at` |
| Hashing / equality | `hash : a → Int` (a fixed structural hash), `dedup_by : (a→k) → List a → List a`, `group_count` |
| Introspection, φ-only | `run_on_examples : Prog → List Int` (an output vector, metered), `logp : Prog → θ → Int` (grammar log-probability), `features : Node → Record` |

Two design choices carry the architecture:

1. **The same language for task programs and improver programs.** φ's slots have DSL types, are type-checked, and run in the metered interpreter. Their compute is charged to the generation's budget, so an improver that "thinks" longer pays for it.
2. **Promotion with an exact-expansion contract.** This follows Aphrodite W5P (`roles/Aphrodite/engine/w5p/promote.py`). A promoted abstraction is a content-addressed node `A_<hash>` whose evaluation *equals* its expansion. A library entry is therefore pure vocabulary, with no hidden capability; it changes description length and search depth only. The contract is verified by an independent call-by-value evaluator, as W5P does.

## 2. State: exact contents

| Component | Contents | Who writes it | Persistent? |
|---|---|---|---|
| θ.L library | ≤ 64 promoted abstractions: typed λ-terms over P₀ ∪ L, each with an id, expansion, type, birth generation, and parent provenance | φ.abstract proposes; **K's fixed MDL gate admits** | yes |
| θ.G grammar | Contextual weights: for each (parent production, argument slot, requested type), a log-probability over P₀ ∪ L productions | φ.reweight | yes |
| θ.M episodic store | Solved (task-id, program, charges); failures (task-id, frontier summary, charges); capped FIFO of 4,096 | kernel logs; φ reads | yes (capped) |
| φ.score | `Node × Ctx → Int`: the priority of a frontier node (default φ₀: `logp`) | meta-search | yes |
| φ.key | `Cand → Int`: the equivalence key for frontier pruning (default φ₀: `hash` of syntax, i.e. syntactic dedup only) | meta-search | yes |
| φ.schedule | `List TaskStat → List Int`: the order of task attempts and budget shares (default φ₀: round-robin) | meta-search | yes |
| φ.abstract | `Corpus → List Prog`: candidate abstractions (default φ₀: all closed subtrees of size 2–4 occurring in ≥ 2 solutions; **single-hole only**) | meta-search | yes |
| φ.reweight | `Counts × θ.G → θ.G` (default φ₀: add-one unigram counts, no context) | meta-search | yes |
| φ.screen | `Edit × History → Int`: the meta-level pre-ranking (default φ₀: `logp` of the edit) | meta-search | yes |
| I identity | `sha256(canon(θ)) ‖ sha256(canon(φ))` + generation + ledger head | kernel | yes |
| K | interpreter, oracle, ACCEPT, MDL gate, budgets, held-out registry, ledger, rollback | **nobody at runtime**; versioned by RSO | frozen per comparison |

**Observation vs action.** The ledger has two record types, enforced by the kernel.

- **ACTION** records — things this (θ, φ) chose:
  - each candidate program submitted to an oracle (charged);
  - each abstraction proposal;
  - each φ-edit submitted for acceptance.
- **EVENT** records — things that happened to it:
  - task arrivals;
  - oracle verdicts on dev examples;
  - accept/reject decisions with their returned statistics.

φ can read its own ACTION and EVENT history through θ.M and the `History` argument. It cannot read K's sealed state:

- held-out families;
- confirm-panel family identities;
- acceptance thresholds, beyond the published constant;
- other arms' ledgers.

## 3. Interfaces (planned Python signatures, M0)

```python
# kernel (frozen; RSO-owned module, imported read-only)
class Kernel:
    def run(self, prog: Ast, inputs: list, meter: Meter) -> Value | Fail          # metered, total
    def oracle(self, task_id: str, prog: Ast, meter: Meter) -> bool               # dev examples only
    def mdl_admit(self, corpus: list[Ast], cand: Ast, lib: Library) -> bool        # fixed MDL gain > τ
    def accept(self, phi: Phi, phi_new: Phi, gen: int) -> AcceptRecord             # §4; uses θ₀, fresh panels
    def ledger_append(self, rec: ActionRec | EventRec) -> str                      # hash-chained JSONL
    def heldout_eval(self, phi: Phi, theta: Theta, registry_key: str) -> Report    # RSO-run only, never in-loop

# engine (the organism; everything here may be edited only through Phi, by accepted edits)
def solve(tasks, phi: Phi, theta: Theta, budget: int) -> SolveTrace              # best-first, φ.score/φ.key/φ.schedule
def sleep(trace, phi: Phi, theta: Theta, kernel) -> Theta                         # φ.abstract → mdl_admit → promote; φ.reweight
def meta(phi: Phi, theta: Theta, history, kernel, budget: int) -> Phi             # SOLVE over EDITS(φ) → φ.screen → accept
def generation(state: State, kernel) -> State                                     # wake; sleep; meta (fixed order)
```

`EDITS(φ)` is a fixed, kernel-defined, type-preserving edit grammar:

- replace a subtree of one slot by a well-typed term enumerated from G over P₀ ∪ L;
- wrap a subtree in a typed combinator;
- delete an optional argument.

Edits are enumerated by `solve` itself, with the edit "task" defined as "a well-typed φ′ ≠ φ". So the frontier priority is φ.score and the pruning key is φ.key, applied to φ′ ASTs. **This is the reflexive channel.**

## 4. The acceptance test (the only door into φ)

`ACCEPT(φ, φ′, g)` is fixed, deterministic, and RSO-owned:

1. **Filters.**
   - φ′ type-checks;
   - |φ′| ≤ |φ| + 12 nodes;
   - φ′ ≠ φ syntactically;
   - φ′ ≠ φ *behaviourally* on a fixed probe battery of 64 recorded frontier states, so it is not an inert wrap (the A21 lesson);
   - φ′ was not previously rejected (content hash).
2. **Screen panel.** 16 dev families freshly drawn from the dev generator with an entropy domain keyed by (g, attempt), never reused.
   - Run φ and φ′ each from **reset θ₀** for R = 3 wake–sleep rounds at identical charges C_eval per round, with common random numbers: keyed task order and keyed enumeration tie-breaks, as in `fair.py`.
   - Metric per family: area under the solved-fraction curve on that family's held-in queries.
   - Returned to φ: per-family deltas. This dense signal is the screen's purpose.
3. **Confirm panel.** 40 *different* fresh dev families. Same protocol. Accept iff the one-sided sign test across families gives p < 0.01 **and** the mean AUC delta > δ = 0.02.
   - Returned to φ: one bit.
   - Families are never reused across attempts, so the improver cannot fit the panel.
4. **Continuation non-inferiority.** φ′ run from the *current* θ_g on 16 more fresh families must not be worse than φ by more than δ. This blocks edits that help a blank learner but break the inherited library: the R8 interaction.
5. **Accounting.** All evaluation charges for both arms count against the generation's C_meta. φ's own slot executions count, metered by the same interpreter. There is no other compute.
6. **Rollback stack (SSA).** Each accepted edit is pushed with its confirm statistics. At every later generation the kernel re-tests the top k = 3 stacked edits by knock-out, on fresh panels. An edit whose knock-out no longer costs ≥ δ/2 is popped (reverted) and logged. This removes edits that only helped transiently or whose effect is subsumed.

Why "from θ₀". It separates *machinery* from *knowledge*. An edit that only helps given the current library would be a θ-dependent tweak, and the continuation test catches that separately. An edit that helps a blank learner learn faster changed **how learning happens**. This is the brief's distinction between stored knowledge and durable changes to learning machinery, made operational.

## 5. Fixed vs evolvable

| Fixed (K or designer constant; disclosed) | Evolvable (through accepted edits only) |
|---|---|
| Interpreter, types, meter, P₀ | φ.score, φ.key, φ.schedule, φ.abstract, φ.reweight, φ.screen |
| Edit grammar EDITS(·) | Which edits get tried, and in what order, since that is computed by φ.score/key/screen |
| MDL admission gate for abstractions | Which abstractions are proposed (φ.abstract) |
| ACCEPT protocol, panels, thresholds | — |
| Budget split C_obj : C_meta = 1 : 1 per generation | How φ spends inside each share (φ.schedule) |
| Order wake → sleep → meta | — |
| Dev generator, held-out registry (RSO) | — |
| Rollback re-test rule | — |

The budget split is fixed on purpose. A learned split is a reward-hacking channel: shifting compute to wherever acceptance is easiest. OOPS-style time-sharing optimality argues a fixed constant ratio costs at most a constant factor.

## 6. Designer-supplied intelligence: full disclosure

The organism gets no credit for any of these:

- P₀, including `dedup_by`, `run_on_examples`, `hash`, `logp`, `sort_by`, and the tree primitives. These make some known-good improver edits short: OE pruning is `key := λc. hash(run_on_examples(c))`, 4 nodes.
- φ₀ — a deliberately plain DreamCoder-like improver.
- The edit grammar, the MDL gate and the acceptance protocol.
- The task generators, and therefore what structure recurs.

Credit is given only for **Δ = φ_g − φ₀**: the accepted edits, their discovery cost, and their measured causal effects.

The withheld-mechanism battery (06 §3) uses known-good edits as positive controls. Rediscovering them is **not** novelty. Its purpose is to prove the meta channel can find something at all.

## 7. Why this design could plausibly reach things the record could not

| Record failure | RLL answer | Status |
|---|---|---|
| Composition wall: parts individually worthless (Hestia W1) | Improver edits are judged by their *own* effect from θ₀, and the useful classes are single edits of 1–6 nodes. No multi-part needle is required for L2. For L3, channel 2 makes edits shorter as θ grows | Hypothesis; tested by the edit-depth census (06 §5) |
| Scalar credit (W4) | The screen panel returns per-family deltas; the ledger keeps per-edit attribution; RSI toy E1 showed attributable feedback beats scalar by a factor growing with size | Mechanism known |
| Promotion gap (W3) | W5P-style exact promotion into θ.L, usable in both task and φ programs | Implemented in Aphrodite for the fold DSL; to be re-implemented |
| Inheritance substitutes for improvement (R8) | Acceptance from θ₀ + continuation non-inferiority + the "inheritance disabled" arm | Test built in |
| Improver levers inert (RB-6) | φ is a program, not a menu. Edits change the algorithm (pruning keys, schedules, abstraction proposers), not one of four preset values | Hypothesis |
| Gains bought with compute | Every arm draws on one meter; the compute-matched φ₀ arm gets C_meta as extra object-level budget | Test built in |
| Leaky accounting exploited in one generation (RSI toy X2) | φ cannot touch K. The meter is in the interpreter that runs φ, and the adversarial kit gets an RLL target | Test built in |

## 8. Resource model (estimates; M0 measures them first)

| Quantity | Estimate | Basis |
|---|---|---|
| Interpreter throughput | 2e5–1e6 node evals/s/core (pure Python, memoised) | Typical for tree interpreters; **unmeasured** |
| One φ evaluation (3 rounds × 16 families) | 1–4 core-min | 16 families × 20 tasks × ~5e3 candidates × ~10 nodes |
| One meta generation | screen ≤ 64 candidates + confirm ≤ 4 → 2–6 core-h | |
| M0 (≤ 10 generations, 3 seeds, all control arms) | 300–800 core-h | ≈ 1–2 days on a 32-core fleet slice |
| M1 (meta-knockout replicates, 30/arm × 4 meta arms) | 1.5–4k core-h | Fabric fan-out |
| M2 (second domain + transfer) | 2–5k core-h | |
| GPU | none required | |
| Memory | < 2 GB/process | Capped stores |

If measured throughput falls below 1e5 node evals/s/core, the M0 plan reduces families per panel before it touches statistics. Either way the measurement is recorded.

## 9. Reuse map (exact sources)

| Need | Source | Mode |
|---|---|---|
| Charge meter / escrow | `roles/Aphrodite/engine/engine.py:82` (`Escrow`) | Re-implement the pattern (≈20 lines) |
| Disjoint entropy domains | `engine.py:52-66` | Copy the pattern with new domain strings `RLL/...` |
| Keyed CRN ordering | `roles/Aphrodite/engine/fair.py` `key`, `keyed`, `Cell`, `paired_summary` | Re-implement; same semantics |
| Exact-expansion promotion | `roles/Aphrodite/engine/w5p/promote.py` (content id, independent evaluator test) | Port the contract to the new DSL |
| Sham donors / R8 enable-vs-substitute | `roles/Aphrodite/engine/tier3d.py` shams; Beta-02 R8 protocol | Re-specify as arms (06) |
| Adversarial evaluator check | `rso/adversary` (attacks.py, core.py; `python -m rso.adversary run`) | Add a target `rll_accept` |
| Fan-out | `fabric/` (worker, store; pinned SHA worktrees) | M1 onward |
| MDL compressor reference | `mlb2251/stitch` (MIT) | M0 cross-check of the kernel's MDL gate only |
| Fixed-improver baseline | Same kernel, φ frozen; optional external check against `ellisk42/ec` on one shared domain | M2 |
