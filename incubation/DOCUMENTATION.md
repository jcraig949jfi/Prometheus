# The Incubation Program — Full Documentation

**v1: Executable Symbolic Learning · v2: Operator Genesis**
Program dates: 2026-08-26 → 2026-08-27. Status: both experiments run to verdict.

This is the deep record. The per-experiment `README.md` files state only hypothesis /
design / preregistered metrics / kill conditions / observed results, per their specs;
this document records everything else: the complete design lineage including every
rejected design with its numbers, the mechanics of each subsystem, the full results,
the scope boundaries, and the artifact registry. Companion files:
`docs/LESSONS.md` (transferable methodology, each lesson traced to the observation
that forced it) and `docs/REPRODUCING.md` (exact commands, runtimes, determinism).

Everything quantitative below is recomputable from committed JSON:
`results/census_v0..v2.json`, `results/incubation_v1.json`,
`v2/results/census_meta_v0..v4.json`, `v2/results/operator_genesis_v1.json`.

---

## 0. The program in one page

**Question.** Can "learning" be operationalized — without an LLM judge, without an
English ontology, without semantic names — as the verified creation, retention,
transfer, ablation, and revision of reusable executable symbolic structure?

**v1 answer** (commit `4cf4ab0d`): yes, at the level of *concepts*. A solver mined a
recurring composition from its own solutions, the composition was admitted only on a
preregistered utility gate, it transferred frozen to a surface-dissimilar world
(nodes ratio 0.169 / 0.170 vs baseline), a random-macro control proved content
specificity (a useless concept costs 3.3x), flat controls proved the advantage lives
in *reification* (the composition slot) rather than possession of the composition,
negative transfer was detected from 2.1M runtime failures (zero in clean worlds),
and a learned guard — recovering the world's hidden trap boundary exactly — bounded
the concept. Verdict per the spec's section 9: **executable symbolic learning with
revision** (A–G all true).

**v2 answer** (commit `6f2abe32`): yes, one level up, at the level of *algorithms*.
A learner that begins as a fixed forward searcher, given meta-primitives that
describe computation (processes, frontiers, observables, meets) but no bidirectional
token, constructed meet-in-the-middle search from its own cost pathology, tied the
omniscient ceiling exactly (capture 1.000), transferred it frozen to an alien domain
family, was genuinely harmed by a world with unreliable inverse information, bounded
itself with a learned one-probe routing predicate, and — the strongest result —
having learned the operator, acquired the solution to a structurally new world class
at candidate #2 where a naive learner exhausted 1,200 candidates and found nothing.
Verdict on the conservative five-tier enum: **RECURSIVE_LEARNING_EFFECT**.

**The meta-result.** Across both experiments, the most valuable outputs were the
rejections: five world/DSL designs and two full experimental runs were killed by
their own preregistered censuses and anti-cheat batteries before any verdict was
allowed to stand. The instruments failed loudly and were repaired at the instrument
level; no gate was ever moved to let a result through.

---

## 1. Commit trail

    3b5e310f  v1 FIRST ACTION: world triple census passed on the third design
    935773a0  v1 framework + preregistration (committed before the run)
    4cf4ab0d  v1 VERDICT: 16/16 gates, A-G complete; first full run thrown out
              by its own anti-cheat battery
    a469a414  v2 FIRST ACTION: DSL census passed on the third design
    28395c99  v2 framework + preregistration (committed before the run)
    6f2abe32  v2 VERDICT: RECURSIVE_LEARNING_EFFECT; trap redesigned once after
              a full-run rejection, re-censused, rerun from scratch

Discipline held in both experiments: census → framework+prereg commit → run →
verdict commit, with result rows shipped in the same commit as the verdict.

---

## 2. Repository map

    incubation/
      primitives.py            v1: 4 executable primitives, polymorphic over Z_m^k
      diagnostics.py           v1: omniscient exact machinery (min-dist, solution
                               enumeration); never importable by solver code
      worlds/families.py       v1: wA/wB/wC + family filters (v2 design, see §3.3)
      solver/boundary.py       v1: the observation boundary (equality-only oracle)
      solver/engine.py         v1: tree-IDDFS + BFS engines, honest cost semantics
      concepts/concept.py      v1: Concept + executable Guard
      concepts/mine.py         v1: function-grouped n-gram miner
      concepts/guard.py        v1: eval-cost-aware exact-cover guard learner
      ledger/ledger.py         v1: append-only ledger; entries/ c0001, c0002
      experiments/census_v0-2.py, incubation_v1.py
      tests/test_incubation.py 20 tests (import boundary is the load-bearing one)
      results/                 census_v0-2.json, incubation_v1.json (3,125 rows)
      README.md                v1 spec-constrained summary
      v2/
        domains.py             dA/dB/dC/dD/dE/dW0 (trap lineage documented inline)
        runtime.py             metered meta-runtime: processes, meets, verification,
                               strict budgets, backward-edge audit
        dsl.py                 program grammar, frozen enumeration, classifier
        learner.py             trigger, construction, router learning, E-orders
        ledger_v2.py + ledger/ o0001, o0002
        experiments/census_meta_v0-4.py, operator_genesis_v1.py
        tests/test_v2.py       15 tests
        results/               census_meta_v0-4.json, operator_genesis_v1.json
                               (1,640 rows)
        README.md              v2 summary
      DOCUMENTATION.md         this file
      docs/LESSONS.md          transferable methodology
      docs/REPRODUCING.md      exact reproduction

---

## 3. v1 — Executable Symbolic Learning

### 3.1 Claim structure

A concept earns existence only through the causal chain of the spec's section 9:
(A) absent initially, (B) created from executable experience, (C) survives its
creating task, (D) improves preregistered future computation, (E) ablation removes
the improvement, (F) not explained by privileged information, (G) failure in a later
environment modifies applicability or structure. Interpretability is never a
criterion; concepts carry arbitrary ids (c0001, c0002).

### 3.2 Substrate

States are tuples over Z_m (length k). Four primitives with arbitrary ids and exact
semantics, polymorphic in (k, m), each invertible (inverses are diagnostic-side
only, never in the solver's action alphabet):

    r00  (x0..xk-1) -> (x1..xk-1, x0)         rotate left
    r01  swap slots 0,1
    r02  slot0 <- slot0 + slot1   (mod m)
    r03  slot0 <- 2*slot0 + 1     (mod m)     [v2 of the design; see lineage]

The planted composition (diagnostic-side; the solver must find it):
M = (r01, r02, r01), effect slot1 <- slot1 + slot0 — a conjugation identity valid at
every (k, m), not available as any primitive, with no equivalent of length <= 2 and
a unique length-3 realization (verified by exhaustive functional audit each census).

### 3.3 Worlds and the design lineage (the load-bearing part)

Final worlds: wA discovery (k=6, m=997, int-tuple surface), wB transfer (k=7, m=673,
string surface at two letters per slot), wC adversarial (k=8, m=809, entering any
state with slot1 < m//5 = 161 fails at runtime; execution still costs). Tasks are
`{start, target}` and nothing else. Family filters (omniscient, generation-side):
generic witness path (every step changes the state and is locally distinguishable
from every other primitive's effect); embed tasks: minimal solution length equals
witness length AND every minimal solution contains M contiguously; null tasks: same
length condition AND no minimal solution contains M.

Lineage, each step forced by a preregistered census:

- **census_v0 REJECTED.** Original r03 was slot0+1, which commutes with r02. Monoid
  growth collapsed to ~2.8^d; 85% of witnesses were non-minimal (L < |w|); among
  minimal-length witnesses only 31% forced M; solver headroom vanished (P0 median
  5.2k nodes; macro ratio 1.09). What survived: M's uniqueness, the null contrast,
  and — completely — world C (fail rate 0.2525, exact 2-atom guard found, negative
  transfer 1.64).
- **census_v1 REJECTED.** Affine r03 plus explicit family filters fixed forcing
  (verified 1.0) but embed acceptance was 0.9–2.8% against a pre-stated 0.10 floor.
  Diagnosis by direct inspection of collapsed witnesses: with small moduli, words of
  length <= 9 touch only 2–4 slots, so the effective space is m^2..m^3 and same-
  length value-coincidences are common — collapse scales ~1/m. (This is the v1
  program's rediscovery of "the marginal criterion rejected my TARGET SHAPE" from
  the prior Aporia LoT work, now with a mechanism.)
- **census_v2 PASSED.** Large prime moduli (997/673/809), generic-path condition,
  and the band trap. Acceptance 0.495/0.481/0.240; forcing 1.0 everywhere; ambient
  M rate 0–3.3%; random-pair prevalence 0.000 at these depths (the task promise is
  maximally informative — nothing is trivially solvable); P0 median 91,391 nodes
  with reference macro ratio 0.174; wC macro runtime-failure rate 0.3975 with the
  exact guard `comp0(s)<165 OR comp0(r02(s))<162` found by the census's own
  learner-shaped search (designed boundary: 161).

### 3.4 Solver, boundary, cost model

The solver touches a task only through `Boundary`: `start`, equality-only
`is_goal`, counted `apply`, `read`. No world identity, no distances, no witnesses,
no inverse primitives. Engines: iterative-deepening tree search (baseline) and BFS
graph search with duplicate elimination (strongest primitive-only control). Cost
semantics fixed in code and preregistration: a **reified** concept occupies one
composition slot (one node, one candidate test) but always pays full execution cost
per invocation; a **flat inline** block pays per-step nodes and depth. Runtime
failures abort actions, record evidence, and never crash a solve. Metrics per task:
nodes (primary), candidate tests, primitive executions; solutions verified by replay
through a fresh boundary.

### 3.5 Arms

    P0   primitives only, IDDFS (baseline; also the ablated form of P3)
    P1   primitives only, BFS with visited set
    P2a  flat control: execute the discovered composition once as a candidate
         solution, then fall back to P0
    P2b  unreified inline control: the composition usable anywhere but paying
         per-step nodes and depth
    P3   c0001 reified
    P3R  random length-matched reified macro (content-specificity control),
         resampled per seed, verified non-equivalent to the candidate and non-identity
    P3G  c0002 = c0001 + learned guard

### 3.6 Mechanics of learning

**Discovery**: P0 solves 30 wA training tasks per seed; contiguous n-grams (2–4) of
its own solutions are grouped by *function* (execution fingerprints on the episodes'
own start states, all counted), scored support x (len-1). The top group's shortest
member becomes the candidate. All 5 seeds mined `(r01, r02, r01)` independently.

**Admission**: preregistered gates on held-out wA tasks with fresh seed streams
(gate list verbatim in `incubation_v1.py::PREREG`, committed before the run).

**Negative transfer and revision**: wC runs collect (state, outcome) evidence
through the engine's Evidence channel (capped, deterministic). The guard learner
fits threshold/equality atoms over executable probes (the concept's own prefixes
plus single primitives), takes the cheapest exact cover, with two structural
subtleties that themselves required fixes during engineering (see LESSONS.md §8):
eval-cost-aware selection, and a per-(probe,slot) pair pool because equality atoms
sharing a failing probe inherit its base coverage and flood any top-N pool.

### 3.7 Results (pooled over 5 master seeds; 3,125 task rows)

- Admission: P3/P0 nodes 0.1689 [95% CI 0.1643–0.1705], per-seed medians
  0.163–0.174; correctness 1.0 in every arm everywhere.
- Content specificity: P3/P3R 0.0409; P3R is 3.3x WORSE than P0 (median 230,626 vs
  70,088 nodes) — carrying a useless concept has real cost, so the gain cannot be an
  accounting artifact of having any macro.
- Storage vs computation: P2a node-identical to P0 (the flat expression never
  solves alone at these depths); P2b ~10% worse than P0; P3/P2b 0.1535. The
  advantage is the composition slot.
- Transfer (frozen, hash-checked): wB P3/P0 0.1704 [0.1677–0.1727]; vs BFS P1
  0.4263; correctness 1.0; ablation restores P0 counter-identically on every
  checked task in both worlds.
- Negative transfer: wC hostile blind 2.8531 [2.7175–3.0052]; friendly 0.1541.
  Detection without labels: 2,102,725 runtime failures / 6,978,052 attempts in wC
  (rate 0.3013) vs exactly 0 in wA and wB.
- Revision: learned guard `comp0(s)<161 OR comp0(r02(s))<161` — the trap boundary
  m//5 = 161 recovered exactly from failure evidence. Out-of-sample failure
  prediction by seed: 1.0 / 0.9975 / 1.0 / 1.0 / 1.0. Guarded validation: 0 runtime
  failures vs 2,207,501 blind; node ratio exactly 1.0 (zero false positives ⇒
  identical search tree); exec overhead 1.0348; friendly advantage kept (0.1617).
- Bounded, not repaired: hostile node harm persists under the guard (2.9097)
  because hostile tasks are hostile at the *task* level (their minimal solutions
  avoid M) — unreachable by any state predicate. Recorded as c0001's failure region.

### 3.8 Kill conditions and the K2 scoping

All ten spec kill conditions evaluated in `incubation_v1.json["KILL_CONDITIONS"]`;
nine SURVIVED, one answered by scoping in the open: **K2** — bidirectional search
over inverse primitives solves these tasks in ~1e3 node visits; inverses are
excluded from the solver class by design, so every v1 cost claim is relative to the
forward-composition solver class. K2 was not fixed in v1; it became v2's target.

### 3.9 The run that was thrown out

The first full 5-seed run passed every preregistered gate — and failed the
anti-cheat battery: 6 witness-word collisions between wA and wB cells. Not a
solver-visible leak; a measurement-independence defect: tree-search cost is nearly a
deterministic function of the witness word, so shared words made transfer cells
partially re-test wA search trees. Fix: witness words sampled without replacement
across every cell of a replicate, wired into the generator; full rerun from scratch.
The discarded run's numbers were materially identical — which is precisely why the
battery, not judgment, had to be the referee.

---

## 4. v2 — Operator Genesis

### 4.1 The one changed variable

In v1, learned artifacts could change the *contents of a composition slot*. In v2,
learned artifacts may change the *organization of computation*: how many search
processes exist, from which roots, over which generators, scheduled by what policy,
halted by what condition, sequenced in how many stages. Everything else — exact
oracles, metered cost, preregistration, ablation, frozen transfer, hostile world,
append-only ledger, five seeds — is held fixed. K2's known opportunity
(bidirectional search) is used as the omniscient ceiling A3, harness-side only,
never learner-visible, never a gate.

### 4.2 Meta-runtime

A search *program* declares: 1–2 processes per stage, each `(root ∈ {A: stage
start, Z: stage goal}, gen ∈ {S: successors, P: predecessors})`; a schedule
(`ONLY i`, `ALT`, or `IF obs(proc0) op obs(proc1)` over FSIZE/DEPTH/DUPS — "expand
the smaller frontier" is a *constructed* policy, not a token); a halt (`GOAL`,
`MEET`, `ANY`); optionally `SEQ` of two stages, well-typed only on via-tasks.

Runtime guarantees, all mechanical: strict meters (an expansion that crosses the
budget can never claim a goal — this was a real bug the first census caught);
orientation algebra (a candidate word is only constructible from an (A,S) process
reaching the goal, a (Z,P) process reaching the start, or a meet between one of
each; every other organization produces no candidates and dies on the meter — forced
by information, not by hint); every candidate verified by replay before being
believed; and a post-run **backward-edge audit** (replay claimed predecessor edges)
available as failure analysis, metered.

Cost model: meter += len(result) per generator call, += 1 per replay step. Budget
400k; probe budget 20k.

### 4.3 The DSL leakage census (the hard requirement)

Before any learner existed, the census quantified whether the language spells the
answer, with pre-stated bands:

- Space: 634 one-stage programs; canonical (size, serial) enumeration frozen by
  sha `c44f6a4f09094537`, pinned into the preregistration and re-verified by the
  anti-cheat battery at run time.
- Diversity: 78 behaviorally distinct organizations, measured by instrumented
  traces on probe tasks (not syntax).
- Not-spelled: the meet-in-the-middle class (solves deep probes via 'meet' with
  both processes expanded >= 2) is 16 programs = 2.52% of the space (band <= 8%);
  first member at canonical rank 49 (band >= 25): `STAGE[AS+ZP|ALT|ANY]`.
- Reachable: all 16 meet-class programs solve every deep probe within the 20k
  probe budget — the v1 lesson (prove the gate reachable) applied to program space.
- Recursion structure: no 1-stage program can satisfy a via-task; `SEQ(fwd,fwd)`
  busts the meter; `SEQ(meet,meet)` solves; the first via-solving SEQ sits at
  canonical rank 4,831 of 401,956 — far beyond the naive budget, so the naive
  learner's failure in phase E is a property of the space, measured in advance.

The preregistered classifier (`dsl.classify`) is structural AND behavioral: a word
of primitives is MACRO; the baseline is NOT_NEW; a single forward process with GOAL
halt is PARAMETRIC whatever its tokens; >= 2 processes, any predecessor generator,
any non-GOAL halt, or multi-stage sequencing is ARCHITECTURAL — and when a trace is
supplied, the behavioral record must agree (an unexercised structural claim does not
count).

### 4.4 Domains and the trap lineage

dA pressure: registers Z_997^6, deep tasks (10–11); forward search exhausts the
budget (measured growth 3.55^d — not 4^d; swap/rotation relations). dB
reinforcement: Z_1013^7, five primitives, string-pair surface, independent
generator; planted composition kept so the macro control is fair. dC alien transfer:
permutations of 12 elements under a 12-cycle plus three fixed pseudo-random
generators. dE recursion probe: via-tasks, both halves depth 10. dW0 control:
shallow only — the construction trigger must never fire there.

**dD, the architectural trap**, took four designs to earn its census:

1. DROP 40% / SPURIOUS 3 (census meta_v2 passed on the *reference*): the first
   inspection during experiment design showed meet-search still WON (ratio 0.896) —
   true meets survived the thinning.
2. The first full run at DROP 70 / SPURIOUS 6 failed D_HARM (pooled 1.42 vs gate
   1.5) and D_DETECT (anomaly 28.6% in two seeds vs gate 30%).
3. DROP 85 / SPURIOUS 8 (census meta_v3) still only 1.405 — which produced the
   structural insight: **the backward root is always meetable**. When the forward
   tree reaches the target it "meets" the backward root with an empty backward
   path, so a starved backward tree degrades meet-search to forward-plus-waste
   (~1.4x) rather than failure. Drop rate is the wrong lever.
4. The right lever is backward expansion COST: spurious volume. A recorded sweep
   (8/16/24 spurious): frontier-balancing reference 1.40 / 1.33 / 2.08; alternating
   reference 15.2 / 28.8 / 28.8 with solve-loss. DROP 85 / SPURIOUS 24 passed
   census meta_v4 and held in the full run.

### 4.5 The learner

Starts as the fixed baseline. Preregistered trigger: >= 30% budget failures over
>= 10 tasks, evaluated on its own experience (fired 5/5 on dA+dB at 65% failures;
fired 0/5 on dW0 — the counterfactual half of "arises from experience").
Construction: exhaustive metered evaluation of the frozen 634-program space on the
learner's own budget-failed tasks (probes: 3 failed dA + 2 failed dB), ~62M metered
ops per seed; cheapest probe-solver wins. Revision: anomaly (budget failure or ops
> 5x the seed's clean solved median) triggers the backward-edge audit; the router
learner picks the cheapest executable task feature exactly separating bad evidence
from good — in every seed: `AUDIT_T > 0`, one predecessor-consistency probe at the
target (~14 ops). Recursion orders: naive = frozen canonical enumeration; 
experienced = library members, then SEQ pairs over the library, then SEQ pairs over
one-token mutants, then canonical fallback.

### 4.6 Results (pooled over 5 seeds; 1,640 task rows)

- Construction: winners `STAGE[AS+ZP|IF:FSIZE:LE:FSIZE|ANY]` (4 seeds) and
  `STAGE[AS+ZP|ALT|ANY]` (1 seed) — meet-in-the-middle, constructed from cost
  pressure. Classifier: ARCHITECTURAL 5/5. ~12 of 634 programs were probe-admissible.
- Admission (held-out dA/dB, n=150): A2 solve 1.0 vs A0 0.30; A2/A0 ops 0.0115
  [0.0114–0.0125], per-seed medians all 0.0115; capture vs ceiling exactly 1.000 in
  every seed. Ablation restores A0 result-identically.
- The macro control is real and still loses: A1 mined the planted composition
  (dB literally `(q01,q02,q01)` = swap-add-swap) and lifted solve rate to 0.62 —
  but macros cannot fix exponential depth: A2/A1 = 0.0126. On dC, macros do not
  transfer at all (A1 0.325 ≈ A0 0.3125); A2/A1 there = 0.0068.
- Transfer (frozen): dC A2 solve 1.0, A2/A0 = 0.0171, capture 1.000.
- Trap: pooled blind harm 2.2559 [2.124–4.8563]; per-seed medians 33.16 (the ALT
  seed), 3.16, 1.39, 3.60, 2.16; blind solve rate fell to 0.9143. World D
  distinguished operator variants that admission scored identical — see §4.7.
  Detection: 9–14 of 14 blind runs anomalous per seed; audit flagged 100% of
  anomalous runs; 0 anomalies and 0 flags in clean worlds.
- Revision: on fresh dD, o0002 routes 100% to fallback (solve 1.0; ratio vs A0
  1.0085 — harm erased to the +0.9% probe overhead); on fresh dA it routes 100% to
  the operator (overhead 1.0028).
- Recursion: naive burned all 1,200 candidates (~72M ops) without a via-solving
  program in 5/5 seeds; experienced found `SEQ(o0001, o0001)` at candidate #2 in
  5/5 (>= 600x acquisition-cost separation); found program solves 50/50 held
  via-tasks; ARCHITECTURAL; contains o0001 verbatim as both stages.
- Verdict: all twenty gates true → **RECURSIVE_LEARNING_EFFECT**.

### 4.7 Honest wrinkles, recorded

1. `o0001_consistent: false` — construction selects among behaviorally equivalent
   meet organizations (ALT vs frontier balancing tie exactly in clean worlds, both
   capture 1.000) and seeds differ. The trap then split them 33x vs ~2–3x.
   **Operator equivalence is world-relative**; admission in clean worlds cannot see
   differences a hostile world exposes. This is an argument for D-style worlds in
   any admission pipeline, not a blemish on this one.
2. Blind trap solve rate 0.87–0.91: the trap costs solve rate as well as ops; the
   routed successor restores 1.0.
3. Per-seed blind harm spread is wide (1.39–33.16); the pooled gate carried. The
   seed at 1.39 held the best operator variant — consistent with (1).
4. MEET_VERIFY_CAP (200 verifications/run) bounds verification storms by
   construction; without it blind operators would fare strictly worse in dD, so the
   recorded harm is a lower bound under this runtime policy.
5. The single-seed smoke passed all twenty gates; the 5-seed run then failed two.
   Smoke runs are engineering, never evidence.

---

## 5. Scope — what these results do and do not claim

- **Solver-relative.** All cost claims are relative to the declared solver class:
  v1 to forward composition over the given primitives (K2 SCOPED — bidirectional
  diagnostics solve those tasks in ~1e3 nodes); v2 to the declared program space
  over the given meta-primitives. Neither claims optimality against unrestricted
  computation.
- **Bounded construction, not open-ended invention.** v2's learner selects from an
  enumerable, pre-censused space. The census guarantees the answer is neither
  spelled (2.5%, rank 49, 78 organizations) nor unreachable — but the space is
  finite and designed. The recursion result shows learned structure re-orders an
  intractable space; it does not show unbounded operator invention. The gen-30
  bounded-menu wall applies to this design at the next level up: the menu of
  organizations is fixed; what grew was the efficiency of searching it.
- **Designed pressure.** Worlds were engineered (and iterated under census) so that
  the phenomena are measurable: forcing filters in v1; planted compositions for the
  macro control; trap parameters chosen so harm clears measurement error. The
  claims are about the learning machinery under real pressure, not about pressure
  arising naturally.
- **Synthetic microscope.** Tiny exact-oracle worlds, by design (the spec's
  choice): every claim is exact, replicated over 5 seeds, and cheap to rerun; none
  of this establishes transfer to natural task distributions.
- **No semantics anywhere.** No artifact carries a semantic name; nothing was
  admitted for being interpretable; the guard atoms, routing features, and operator
  serials are executable structure only. That the learned guard recovered `161`
  and the learner reinvented meet-in-the-middle are read off by us, outside the
  boundary, from omniscient diagnostics.

---

## 6. Artifact registry

    c0001  v1 concept  (r01, r02, r01)          status: bounded
           mined 5/5 seeds from solver's own solutions; admitted (0.169);
           transferred frozen (0.170); failure region: constrained-dynamics worlds
           (runtime-failure rate 0.30 blind; task-level hostile harm 2.85 not
           state-predictable). File: ledger/entries/c0001.json
    c0002  v1 concept  c0001 + guard            status: admitted
           guard comp0(s)<161 OR comp0(r02(s))<161, learned from failure evidence,
           OOS >= 0.9975; erases runtime failures at 1.035x exec.
           File: ledger/entries/c0002.json
    o0001  v2 operator STAGE[AS+ZP|IF:FSIZE:LE:FSIZE|ANY] (4 seeds; ALT|ANY in 1)
           status: bounded. Constructed from cost pathology; capture 1.000;
           frozen transfer to dC; failure region: unreliable-predecessor worlds.
           File: v2/ledger/o0001.json
    o0002  v2 operator ROUTE(AUDIT_T > 0 -> baseline, else o0001)  status: admitted
           one-probe routing; dD harm to 1.0085; clean overhead 1.0028.
           File: v2/ledger/o0002.json

Live consumers: c0001 appears in ~100% of P3 solutions in wA/wB; o0001 is the
executing architecture of every A2 solve and both stages of the dE program. No
artifact exists without a consumer; total artifact count 4.

---

## 7. Open edges (not commitments)

Recorded so the next seat starts where this one stopped; none of these are claims.

- **Menu growth.** Both experiments select from fixed spaces. The natural v3
  question is whether admitted operators can *extend the operator language* itself
  (new observables, new combinators earned from failure), attacking the bounded-menu
  wall directly rather than the search-efficiency layer.
- **Operator libraries and selection.** With >= 2 admitted operators, routing
  becomes a selection problem over a library; v2's single learned route is the
  degenerate case. The v1 lesson that admission cannot rank behaviorally-equivalent
  operators (until a hostile world splits them) suggests library curation needs
  adversarial worlds as first-class citizens.
- **Cross-level interaction.** v1 concepts (macro edges) and v2 operators
  (organizations) were never combined: does a constructed operator with macro-
  augmented generators beat either alone, and can that combination be *learned*?
- **Trap taxonomies.** The meet-at-root analysis (§4.4) generalizes: every
  organization has a degradation mode, and traps must attack that mode. A catalog of
  degradation modes for the 78 organization classes is cheap to build and would
  make future trap design principled instead of iterative.
