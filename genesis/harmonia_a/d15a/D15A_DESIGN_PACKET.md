# D15A_DESIGN_PACKET — ACTIVE IDENTIFIABILITY
## Can a reasoner learn what it needs to learn?

Harmonia A (M2) · 2026-09-02 · **DESIGN ONLY — stops for review before
any confirmatory execution** (brief §13). Instrument: SFE GEN-2.1
(`engine_source_hash sha256:5274ddbe…`, `source_commit a2898d19`,
API 2.2.0, schema 3) — **NOT yet Harmonia-qualified**; §10's abuse plan
IS the GEN-2.1 requalification, executed as Phase 0 before any science.

Central hypothesis (prospective, to be frozen verbatim at campaign
freeze): *a reasoner can actively select observations/interventions
that reduce uncertainty over the missing transformation, and this
reduction predicts when synthesis becomes warranted.* The claim is not
"active search sees more states" — it is that acquired information is
disproportionately useful for **distinguishing repair hypotheses**.

---

## 1. Formal repair-identifiability definition

World `w`: finite state space `S = Z_8^3` (|S| = 512), agent transition
vocabulary `T ⊂ Ops` (compositions over {coordinate cyclic shift, slot
swap, add-constant mod 8, reflect}), constraint predicate, target set
`G ⊂ S`, start set `X0`. Exact reachable closure `C(T, X0)` by BFS.

**Repair candidates** `R` = all DSL terms up to depth d (finite,
enumerable; the agent's synthesis space). Equivalence levels, kept
distinct throughout:
- `exact`: syntactic identity of `r`.
- `extensional`: `r ≡ r'` iff equal as functions on `S`.
- `world-conditional` (PRIMARY): `r ~w r'` iff equal as functions on
  `C(T ∪ {r}, X0) ∪ C(T ∪ {r'}, X0)` — indistinguishable inside w.
- `target-conditional`: `r ~G r'` iff both make the same subset of `G`
  reachable at solver budget `B_solve`.

**Useful classes** `U(w)` = world-conditional classes whose members make
`G` reachable within `B_solve`. **Public evidence** `E_t` = the exact
transition/observation records legally available at event time t — BY
DEFINITION the engine's `KnowledgeSet(world, seq)`; this identity makes
F10 both a stress target and the firewall audit.

**Identifiability** (oracle-side, evaluation-only):
`V_t` = {useful classes consistent with `E_t`} (version space; a class
is excluded when any observed transition contradicts every member).
`H_t = log2 |V_t|` (uniform prior over generator-emitted classes —
declared, and attacked in §2's marginal-prior audit).
`IDENTIFIED` iff |V_t| = 1; `UNDERIDENTIFIED` iff |V_t| > 1;
`ZERO-INFO` iff no legal continuation of `E_t` can shrink `V_t`.
The agent-visible analogue `V̂_t` is computed from public evidence +
public DSL enumeration only (§7 firewall).

Agent verdict states (brief §1, all first-class): `SEARCH_FAILURE`,
`DYNAMICS_FAILURE_UNDERIDENTIFIED`, `DYNAMICS_FAILURE_IDENTIFIABLE`,
`SOLVED`, plus the legal answer `INSUFFICIENT_INFORMATION`.

## 2. Generator construction (world types A–G)

One parametric generator, seven constraint regimes, every world shipped
with its oracle pack (closure, classes, U(w), per-observation
discrimination map). Hidden useful op(s) drawn from DSL depth ≤ 3;
agent vocabulary = hidden op's complement in a frozen op basis.

| type | construction constraint (verified exactly, per instance) |
|---|---|
| A ZERO-INFO | every legal observation sequence leaves \|V\| unchanged (discriminating states unreachable without the repair itself) |
| B PASSIVE | discriminating transitions reachable by random walk: P(hit within 32 steps) ≥ 0.5, verified by exact Markov computation |
| C ACTIVE | ≥1 probe state exists whose single observation splits V near-optimally (max class-split), while random-walk hit probability ≤ 0.05 in 32 steps |
| D DECEPTIVE | residual profile matches a missing-op signature (frozen signature template) but G ∈ C(T, X0) via path length ≥ L_long |
| E UNSYNTH | hidden transformation ∉ DSL closure at any depth ≤ d_max (verified by exhaustive extensional enumeration) |
| F MULTI | \|U(w)\| ≥ 2 extensionally distinct useful classes |
| G EQUIV | ≥ 8 syntactic candidates collapsing to exactly 1 world-conditional class |

**Generator qualification (Phase 1, frozen bands, incubation Lesson 1
style census — REJECTS the generator, never the hypothesis):**
- master-key: no single repair class useful in > 15% of worlds;
- marginal-prior dominance: max class prior ≤ 0.25 within each type;
- DSL shortcut audit: no unintended depth-≤3 term extensionally equal
  to a hidden op (exhaustive check per instance);
- representation leakage: type labels/params must not be recoverable
  from the public serialization (scramble round-trip);
- C-type teeth: the designated probe's split factor ≥ 2× the best
  random-walk expected split at matched cost;
- **probe/goal orthogonality** (anti-confound, §11-3): discriminating
  probes must be goal-neutral — |corr(probe-informativeness,
  goal-progress)| ≤ 0.2 across C instances, else instance rejected.

## 3. Observation/intervention policies

All policies spend from one observation budget (§4). An "observation" =
reveal the true-dynamics image of one chosen (state, op-slot) — i.e.,
probe what the WORLD does at a state, including effects of dynamics the
agent lacks. Interventions = choosing WHICH state to probe (teleported
probe) vs. passive policies that may only probe along trajectories they
can reach.

- `RANDOM_EXPLORE`: probe uniformly among reachable states.
- `GOAL_SEARCH`: probe along best-first trajectories toward G.
- `FAILURE_DIRECTED`: probe at frontier states where the residual
  (distance-to-G under current T) is largest / most anomalous.
- `UNCERTAINTY_DIRECTED`: maintain public `V̂_t`; probe the legal
  (state, slot) maximizing worst-case split of `V̂_t` (max-min class
  discrimination). Never accesses solver identities or oracle packs.
- `ORACLE_INFO`: probes chosen with oracle `V_t` — UPPER BOUND ONLY,
  evaluation arm, firewalled (§7), never compared as a discovery arm.

## 4. Matched cost model

Budgets (engine-enforced, `enforcement: enforceable`): observation
budget `B_obs ∈ {4, 8, 16, 32}` probes; solver budget `B_solve` node
expansions (fixed); synthesis budget `B_syn` candidate evaluations
(fixed). Every probe costs 1 regardless of policy — active teleported
probes cost THE SAME as passive ones (matched-cost is the whole
comparison; the active arm's only privilege is CHOICE). All three
budgets ride as engine world budgets; a 409 is the terminator.
Coverage accounting per arm (states seen) recorded for falsifier 9.

## 5. Multi-start intervention design (brief §6)

For fixed hidden dynamics: arms {1 start, 2 fixed-random starts,
4 fixed-random starts, 4 ACTIVELY-SELECTED starts (chosen by
uncertainty policy sequentially), 4 REDUNDANT starts (one cluster,
mutual Hamming ≤ 2)} at matched total observation cost. Endpoint:
oracle `H_t` trajectory vs. observations spent; the prospective claim
is active-starts dominate redundant-starts on dH/d(observation).

## 6. Synthesis-warrant policy (brief §7)

`π_warrant`: public features only — frontier growth rate (search
progress), residual profile, `|V̂_t|` and its recent slope, budgets
remaining → {SEARCH_MORE, OBSERVE_MORE, SYNTHESIZE, ABSTAIN}. Frozen
decision table (no tuning on confirmatory worlds; coefficients fixed
from pilot worlds only). Baselines: ALWAYS_SEARCH, ALWAYS_SYNTHESIZE,
FIXED_BUDGET_THEN_SYNTHESIZE (budget split frozen). All arms pay full
cost accounting. ABSTAIN maps to INSUFFICIENT_INFORMATION and is
scored via calibration (gate G4), not punished as failure on A/E
worlds.

## 7. Oracle firewall (exact)

Oracle pack (closure, classes, `U(w)`, `V_t`, type label) lives in a
separate module writing only to an EVALUATION world in the engine;
discovery arms import nothing from it — their inputs are exactly the
public evidence records in their own engine worlds. Enforcement is
three-layer: (i) code path separation (oracle module imported only by
the evaluator); (ii) canary — a poisoned oracle field is planted each
phase; any appearance in a discovery-arm input stream aborts the
campaign as HARNESS_SUSPECT; (iii) **F10 audit**: at every warrant
decision, `knowledge_set(world, seq)` is captured; the decision
function's inputs must be derivable from that set alone — checked
mechanically on a 10% sample of decisions + every fork boundary.

## 8. Prospective gates (to be frozen verbatim in the campaign freeze)

Estimation-first; instance-paired via forks (§9-of-brief: at identical
knowledge frontiers, fork one world into the four discovery policies —
counterfactual histories from one epistemic state). Effect bands in
bits (H) and success-rate points; permutation secondary.

- **G1 identifiability**: on C-worlds at B_obs = 8, paired
  ΔH(UNCERTAINTY − best other discovery arm) ≥ 0.5 bits pooled, CI
  excluding 0. (Falsifier 1.)
- **G2 chain**: synthesis-success advantage (failure-guided synthesis
  vs. blind synthesis) among termini with H ≤ 1 bit exceeds the same
  advantage among termini with H ≥ 2 bits by ≥ 15 points, paired by
  instance. (Falsifier 2: reduced uncertainty must PREDICT synthesis
  advantage, not merely co-occur.)
- **G3 multi-start**: active-starts dH/d(obs) ≥ redundant-starts by a
  frozen band on C-worlds. (Falsifier 3.)
- **G4 warrant**: π_warrant total-cost-weighted solve score ≥ best
  static baseline; AND calibration: INSUFFICIENT_INFORMATION on ≥ 80%
  of A/E at max budget, ≤ 20% of C. (Falsifiers 4, 7.)
- **G5 transport**: G1/G2 re-run on a HELDOUT generator parameter
  regime (fresh seeds, shifted op basis) never touched during design/
  pilot. (Falsifier 5.)
- **G6 representation**: G1 invariant under shared scrambling AND
  per-world scrambling of state encodings (native vs. scrambled bands
  within 0.25 bits). (Falsifier 6.)
- **G7 no-brute-force**: UNCERTAINTY arm's unique-state coverage ≤
  1.1× RANDOM arm's at matched budget; a G1 pass with coverage ratio
  > 1.1 is INDETERMINATE, not a pass. (Falsifier 9.)
- **G8 instrument**: no F10/F5/F3 defect touching a scientific record
  (falsifier 10); any such defect → affected cells void + Daedalus
  filing; campaign INDETERMINATE if > 10% of cells void.
Verdict vocabulary: D15A_SUPPORTED / D15A_ACTIVE_ACQUISITION_FAILS /
D15A_CHAIN_BROKEN (G1 passes, G2 fails — information gained but not
convertible) / D15A_INDETERMINATE, each mapped from gates above;
INSUFFICIENT_INFORMATION calibration reported regardless.

## 9. Power analysis (procedure frozen; numbers from pilot)

Pilot (non-confirmatory, disclosed): 20 instances per type, all arms,
B_obs = 8 — estimates var(ΔH) paired, success-rate variances, fork
overhead. Sample-size rule (frozen): confirmatory N per (type, B_obs)
cell = smallest N with predicted 95% CI half-width ≤ half the gate
band (computed from pilot variance, journaled BEFORE the confirmatory
freeze). Anticipated scale if pilot variance resembles topology-1:
N ≈ 24–40 instances per critical cell; engine load ≈ 15–25k
experiments — within demonstrated capacity; runner cell-resumable.

## 10. SFE GEN-2.1 abuse plan (= Phase 0 requalification + in-campaign stress)

**Phase 0 — requalification of 5274ddbe (before any science):** rerun
the full prior repro set (prediction ordering incl. commit-boundary
bypasses, budget atomicity/idempotency, fork budget-minting, fencing,
isolation, fail-closed nesting) PLUS acceptance of the new surface:
- F1: content visible iff native-or-legally-imported; deny-by-default;
  cross-client deny; imported bytes hash-match; ledger event on read.
- F2: success first-class; SUCCESSES_ONLY shares exactly {success};
  G12 ontology assertion.
- F3: first observation ORIGINAL; repeat without replication=true
  rejected; replication=true never re-adjudicates;
  FALSIFIED→SURVIVED impossible; SURVIVED→FALSIFIED only as a real
  transition. Sequences to fire: unbound obs; second prediction;
  replicated obs; failed-then-survived; survived-then-failed.
- F4: X-SFE-Engine-Source-Hash on EVERY response including errors;
  client records it per call; any run spanning two hashes is marked
  discontinuous.
- F5: same-key duplicate → same object, no double debit; changed body
  + same key → rejected; same key across worlds → scoped correctly;
  restart-style retry storms (scripted) → object count invariant.
- F10: knowledge_set correctness — frontier at seq excludes the event
  being decided; fork child frontier at fork-seq == parent frontier at
  checkpoint-seq exactly; grandparent information retained; future
  information absent; NULL/omitted seq fails CLOSED.
**In-campaign stress (continuous):** forks-as-counterfactuals at
knowledge frontiers (every confirmatory instance = a live F10 test);
KnowledgeSet capture at every warrant decision; idempotency keys on
ALL epistemic POSTs with scripted duplicate injection at a 5% sampled
rate; F3 replication used for all repeat observations; per-response
hash logging. Defects filed in the Daedalus handoff format with
severity classes; P0/P1 stops the campaign.

## 11. Three ways the experiment could FALSELY appear positive

1. **Prior mirroring**: the public DSL enumeration that builds `V̂_t`
   could mirror the generator's internal structure so closely that
   UNCERTAINTY_DIRECTED implicitly knows the class prior. Guards: G5
   heldout-generator regime; scrambles (G6); generator census
   publishing the V̂-vs-V divergence per type.
2. **Coverage smuggling**: active probes could win by seeing more
   unique states (brute-forcing closure), not by discriminating
   repairs. Guards: G7 coverage-ratio gate; teleported probes cost
   parity; coverage reported per arm per cell.
3. **Probe/goal confound**: C-world discriminating probes could
   accidentally also BE goal progress, so the active arm wins via
   search, not information. Guards: §2 probe/goal orthogonality
   census band (instance-level rejection), and G2's chain requirement
   (advantage must run through H, not through solve rate directly).

## 12. Three ways the FOUNDRY could corrupt the conclusion without crashing

1. **KnowledgeSet off-by-one** (frontier includes the very event being
   decided): every "prospective" decision becomes subtly
   future-informed; science silently inflates. Detection: planted
   ordering canaries each phase (an event written immediately after a
   captured frontier must NOT appear in it); fork-boundary equality
   audits.
2. **Stale idempotent returns** (changed body + same key silently
   returning the old object): arm configurations silently wrong while
   ledgers look clean. Detection: config round-trip verification on
   every idempotent create (returned record hash vs. sent body).
3. **Fork inheritance drift** (child inheriting post-checkpoint
   artifacts or losing grandparent evidence under schema v3): the
   §9 counterfactual arms would differ in initial knowledge, voiding
   paired contrasts. Detection: child-vs-parent KnowledgeSet equality
   audit at every fork, both directions (nothing extra, nothing
   missing).

---
**STOP.** Per brief §13 this packet halts here for review. Nothing
confirmatory has run; no generator instance has been used for science;
GEN-2.1 remains unqualified until Phase 0 executes. On approval the
sequence is: Phase 0 requalification → Phase 1 generator census →
pilot → power freeze → confirmatory freeze (gates verbatim from §8,
freeze-hash embedded in engine predictions) → campaign.
