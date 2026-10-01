# explib: a shared below-engine experiment library (W2-F draft, 2026-10-01)

`explib/` is pure Python plus numpy. No engine module is imported anywhere in it.
`checks/core_isolation.py` enforces this: it makes `prometheus` and `torch` unimportable and then runs every
core test. Engines plug in through two small protocols, `LockstepEngine` and `Experiment`/`MutationOperator`,
or by handing over plain arrays. `adapters/pte.py` is the only file that imports `prometheus.ananke`.

Run (from W2-F/, CPU only):

    PYTHONDONTWRITEBYTECODE=1 python checks/core_isolation.py                 # 35 core tests, engine-free
    CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -p no:cacheprovider   # + 5 PTE tests

## 0. What already exists, and how explib fits it

| existing piece | what it does | how explib relates |
|---|---|---|
| `prometheus/toolbox` (Bellerophon, Worlds Kernel) | content-hashed chained receipts; controls with POWER tests (MET / NOT_MET / INDETERMINATE); admission probes; a mutation ledger (`tests/mutants.py`); `Intervention` data; `ext.snapshot.v1` | The closest thing to a shared library. explib is the AUDIT layer it lacks: lockstep difference tracing, reach certificates, identity audits over specimen panels, gate attainability and statistical units. See the promotion path, s5. |
| `harvest/H-INST/pte_trace.py` | the exact PTE tracer (`diff_trace`, `reach_certificate`, `ProvenanceWorld`) | `explib.trace` and `explib.reach` generalise it. `adapters/pte.record_from_difftrace` converts a PTE trace, and the tests show the verdicts agree on all four hold_latch hooks. |
| `roles/Harmonia/qualification/primitives/audit_primitives.py` (AP-1.1.0) | R-A reachability, R-B absence_control, R-C baseline_gaming, R-D ceiling, F6 freeze_precedes | Keys are compatible. `attainable.attainable_labels` uses R-A semantics; G2 adversary uses R-C semantics. R-B and R-D are not duplicated; use Harmonia's. |
| `research/tools/freeze_check.py` (BX-1), `research/deposit.py` (BX-5) | plan-before-results proof from git; verbatim deposit with sha256 provenance | `provenance.plan_precedes` has the same semantics, with the same known answers (REL4 PASS, W-O FAIL). `provenance.Ledger` gives the same immutability guarantees. |
| H-INST B1-B6 (REPORT s5) | proposals | B1 is `stats.stratified`. B2 is `controls`. B3 phase keys are strata supplied by an adapter. B4 is `stats.replication_label` (corrected; see s4 row 8). B5 is `authority.difference_vs_use`. B6 is `reach`. |
| W2-B `attain.py` (PTE certifier) | runs programs by role over cells; verdicts UNREACHABLE / DEGENERATE / CHEATABLE / SOUND / NO_PLANT | `attainable.certify_gate` is the engine-free decision layer it can feed. `map_w2b()` names the corresponding check. |
| W2-C `pte_mut` (PTE mutation operators) | operator x stage x fixture classification | `metamorphic.classify_mutant` / `run_operator_suite` adopt W2-C's vocabulary verbatim (read-only coordination). |
| Nestor B1-B8 (NPE heredity specs) | engine-neutral contracts for heredity | B2/B5 (whose write, execution context vs owner) map to `authority.WriteLedger` (`writer` vs `owner`, `foreign_writes`). B1/B3/B4/B6-B8 are out of scope here. |

## 1. Shared outcome vocabulary (`explib.outcomes`)

- `PASS`, `FAIL`, `NOT_VERIFIED`, and `Check(name, outcome, detail)`.
- `worst(checks)` orders them FAIL > NOT_VERIFIED > PASS.
- `all_pass(checks)` is fail-closed. NOT_VERIFIED is never counted as a pass.
- Toolbox mapping: MET = PASS, NOT_MET = FAIL, INDETERMINATE = NOT_VERIFIED.

## 2. The engine protocol (`explib.lockstep`)

```
class LockstepEngine(Protocol):          # all arrays batched [U units, N nodes, ...]
    n_units: int; n_nodes: int
    make(arm: "A"|"B") -> world          # B may differ ONLY by a documented input schedule
    step(world, t) -> None
    trace(world) -> {component: [U,N,...]}
  optional:
    inputs(world, t)     -> [U,N,...]     exogenous input applied at t (leaf)
    arrivals(world, t)   -> [U,N,...]     content delivered at the start of t
    inflight(world, t)   -> [H,U,N,...]   content in flight after t (index h arrives at t+1+h)
    edges(wa, wb, t)     -> [(u,src,te,dst,ta)]   difference-bearing transport emitted at t
    intervene(world, target, t)           between ticks, after t (applied to B only)
    readout(world, t)    -> [U,...]       read after step t, BEFORE the interventions of t
    local_only = True                     no transport at all
run_lockstep(engine, T, interventions={t: target | [targets]}) -> LockstepResult(rec, read_a, read_b, crn_violation)
crn_check(engine, T) -> {outcome, differing_node_ticks, first}    # two arm-A worlds must never differ
```

Common random numbers are part of the contract: arms A and B draw every exogenous number from the same
streams. The contract is CHECKED in two ways:
- `crn_check` catches hidden state and unseeded randomness.
- The closure invariant catches state-dependent draws and nonlocal reads.

Each absent optional method makes the matching closure check NOT_VERIFIED.

## 3. Primitives

### (1) Reachability certification (`explib.reach`)
`reach_certificate(rec, ro_tick[U], ro_node[U], out_a[U], out_b[U]) -> dict`

Per unit:
- UNAPPLIED: nothing changed.
- NOT_REACHED: something changed, but no difference reached the readout node by the readout tick.
- ABSORBED: the readout node was touched and the value was unchanged.
- REACHED: the readout value changed. `path` is LOCAL, TRANSPORTED or BOTH.
- INCONSISTENT: the value changed with no recorded path. This is an instrument bug, and the batch result fails closed.

Batch result: INCONSISTENT > REACHED > ABSORBED > NOT_REACHED > UNAPPLIED.

Burden symmetry: NOT_REACHED and ABSORBED are negative claims. They are certified only if `rec.closure()` is
PASS; otherwise the result is NOT_CERTIFIED and carries the uncertified `reading`. Only ABSORBED is an
admissible null (`null_admissibility`).

`certify(engine, T, interventions, ro_tick, ro_node)` runs the lockstep and certifies in one call.
`applied_ticks(rec)` reproduces `lens.applied_ticks`; it exists only so the difference can be shown.

### (2) Causal tracing and difference cones (`explib.trace.DiffRecord`)
Inputs: `held/post/inp/arr/edges/hook_node/hook_flight/comp_post/comp_held`.

`closure()` returns C1 node closure, C2 arrival closure and C3 edge sources, each PASS / FAIL / NOT_VERIFIED.
They certify engine locality and tracer correctness in one check.

The record also provides:
- `paths()` / `path_class(t,u,n)`: LOCAL / TRANSPORTED / BOTH / NO_DIFF.
- `cone(u,n,t)`: the backward difference cone, with nodes, edges, and leaves of kind ENV, HOOK_NODE,
  HOOK_FLIGHT or UNRESOLVED_ARRIVAL.
- `cone_cut(cone, tau)`: what is held and what is in flight at tau.
- `first_touch(u, n, t0, t1)`.
- `component_causes()`, used by primitive (3).

Semantics:
- Outside the cone means the contrast cannot be carried there (sound, given closure).
- Inside the cone is NOT use.

### (3) State and write authority (`explib.authority`)
- Dynamic write authority: `DiffRecord.component_causes()` classifies writes as SENSED / TRANSPORTED /
  CARRIED / HOOK / UNEXPLAINED.
- Declared authority: `check_authority(causes, declared)`. It turns a code-only assumption such as "w is
  written only from SENSE" into a fail-closed check.
- `WriteLedger([WriteEvent(t, unit, writer, node, component, source, owner)])` offers `who_wrote`,
  `authority_map` and `foreign_writes` (the writer is not the owner: hijack, Nestor B5).
- Difference vs use: `component_difference(rec, comp, ro_tick, ro_node)` feeds
  `difference_vs_use(diff_frac, use_tests)`, which returns USED / DIFFERENT_UNUSED / UNTESTED /
  NOT_DIFFERENT / NOT_DECIDABLE. `carrier_claims()` returns only the USED components.

### (4) Control competence (`explib.controls`)
`identity_audit(control_stats, treatment_stats, raw, rule, witness_stats, evidence)` runs four checks:
- **A1 not a no-op.** Control outputs differ from treatment outputs somewhere.
- **A2 not constant.** Over a panel whose treatment statistic varies.
- **A3 no design identity.** Built in: the MIRROR identity. When outputs are identical within every pair and
  the targets are negated, every pair mean is exactly 1/2.
- **A4 can fail.** An admissible witness specimen reverses the control's decision on the evidence specimens.

Verdicts:
- FORCED if A2, A3 or A4 fails.
- NO_OP if A1 fails.
- COMPETENT only if all four PASS.
- Otherwise NOT_VERIFIED.

`excluded_specimens` lists specimens whose control value is pinned by the identity.

Relation checks:
- `relation_audit(relation, instrument, null_sets)` returns INFORMATIVE only if the relation's hold rate is
  <= alpha under at least two null specimen sets. Otherwise it is FORCED.
- `data_identity(arrays, fn)` is an observation-level screen. It flags IDENTITY_SUSPECTED when a relation
  holds at every element of every specimen.

### (5) Metamorphic experiment testing (`explib.metamorphic`)
Relations:
- `Relation(name, transform(x, rng), check(y, y2, x, x2) -> bool|None, kind)`, with kind one of invariant,
  equivariant, must_change or causal.
- `run_relations` and `run_suite(experiment, inputs, relations, mutants)` build the kill matrix.
- `adequate` requires three things: the experiment passes every relation, every relation kills at least one
  mutant, and every mutant is killed.
- Engine-neutral relations over the pair-table convention (`outputs [U,K]`, `targets [U,K]`, `pair [U]`):
  `permute_units`, `relabel_pairs`, `negate_world`, `cue_blind_must_be_half(key)`.

Operators (W2-C vocabulary):
- `MutationOperator` (`name`, `active()` context manager) and `StageResult(verdict, alarms, fingerprints, numeric)`.
- `classify_mutant` returns KILLED(A) / KILLED(D) / EQUIVALENT / SURVIVED / UNRESOLVED / FRAGILE.
- `run_operator_suite(stage, fixtures, operators, expect)` builds the expectation table before any mutant runs.
- `patched_attr` is a minimal operator helper.

### (6) Attainable-range certification of a gate (`explib.attainable`)
`certify_gate(gate, null_sampler, adversaries, plants, ceilings, threshold, min_eligible, verdict_fn,
design_space, gated)` runs these checks:
- **G1 null.** False-pass rate with an exact Clopper-Pearson upper bound. FAIL only when the observed rate
  exceeds alpha. When the bound is too loose, the result is NOT_VERIFIED.
- **G2 adversary.** Committed non-construct policies.
- **G3 positive.** A plant passes.
- **G4 eligibility.** The count of cells whose ceiling exceeds the threshold, against the prereg's minimum.
- **A attainable labels.** Harmonia R-A semantics.

The result is CERTIFIED only if every check PASSes. Fail-closed: anything missing gives NOT_VERIFIED.

### (7) Intervention provenance (`explib.provenance`)
Record construction:
- `hook_digest(fn, params)` is a sha256 over the source (or the bytecode), the qualified name, the closure
  values, the simple globals the hook reads, and the params.
- `seeds_digest(ns, seeds)`.
- `make_record(...)` returns a frozen `InterventionRecord`. Its fields are experiment, arm, kind,
  seed_namespace, seeds_digest, hook_name/digest/basis, params, plan_path, plan_commit, code_sha, parent and
  created_utc. `record_id` = sha256 of the canonical JSON.

Verification:
- `verify_record` runs R1 id, R2 live hook digest, R3 `plan_precedes` (read-only git: strict ancestor plus
  an unchanged blob), R4 the plan_commit link, and R5 the namespace check.
- `seed_reuse(records, independent_groups)`.
- `support_check(claim, records)`. Default policy: `search_null` needs `evolve`, `transfer_null` needs
  `transfer`, and so on.
- `Ledger(path)`: an append-only JSONL file. It refuses duplicates and verifies every hash on read.

### (8) Independence units and a Simpson guard (`explib.stats`)
`Units.of(ids, name)` and `Units.mirror_pairs(U)` declare the independence unit. Every interval function
requires a declaration.
- `count_check(claimed_n, units)`.
- `cluster_bootstrap_ci(values, units)`.
- `stratified(values, strata, units, arm=None)`. Flags: SIMPSON, MIXED and THIN. The label is
  MIXED_ACROSS_STRATA or POOLED_OK.

### (9) Pairing-aware intervals (`explib.stats`)
- `joint_arm_ci(arms, units, contrasts)` resamples units once per draw for every arm, so arms that share a
  normal run stay paired. Non-finite contrast draws are counted, not dropped silently.
- `ratio_guard(Estimate, Estimate)` requires the same estimator and unit, at least 2 draws, and a
  denominator interval that excludes 0.
- `margin(ci, bars)`.
- `replication_probability(margin, level, inflation)` and `replication_label(ci, bars, n_namespaces, k |
  p_min, inflation)` return MARGINAL / NEEDS_AGREEMENT / CLEAR.
- `mirror_pair_means`.

## 4. "Would have caught": historical defects mapped to primitives

Each row is reproduced by a test. "Real" means the test uses the real engine, real recorded rows, real git,
or a real measurement. "Toy" means a numpy fixture with the same structure.

| # | historical defect (record) | primitive / check | what fires | test (real / toy) |
|---|---|---|---|---|
| 1 | zero_comm counted as COMM evidence; exactly .500 in 213/213 RELAY, 174/174 MAJ, 95/95 XOR C1 rows (PTE_INSTRUMENT_GAPS rank 1) | (4) A2 + A3 + A4 | FORCED; mirror identity on the engine | test_pte_adapter P4 (real rows + engine), test_controls (toy) |
| 2 | "applied" is not "reached": lens.verify_reach counted 85 applied ticks for an edit that never reached the readout (H-INST s4) | (1) | NOT_REACHED is a NON-TEST, not a null | test_pte_adapter P1 (real engine, agrees with H-INST), test_reach |
| 3 | window miss: a hook after the readout tick is still "applied" (W-D 1a, C1 D-A) | (1) + (5) causal relation | NOT_REACHED; the digest-applied mutant is killed | test_reach, test_metamorphic B |
| 4 | difference is not use: "readout Kp differs 78-98%" was Kp[0], never read (W-Y vs W-V) | (3) difference_vs_use | DIFFERENT_UNUSED; UNTESTED is never a carrier | test_authority (toy) |
| 5 | W-S P3 frozen cone counted re-broadcast copies the readout ignores | (2) backward cone | the cone is exactly the path; extra edges fall outside | test_trace (toy); PTE cone equals H-INST in test_pte_adapter P2 |
| 6 | census SITE verdicts on a transported bit (W-I) | (2) path_class | TRANSPORTED vs LOCAL | test_trace, test_pte_adapter P2 |
| 7 | site_acc + chan_acc = 1 forced by the mirror design (W-M) | (4) relation_audit / data_identity | FORCED in toy; IDENTITY_SUSPECTED on 93/93 real W-Z RELAY/MAJ groups at offset >= 1 (0/13 at offset <= 0) | test_controls, test_pte_adapter (real) |
| 8 | single-draw certificates near the bar flipped across namespaces (AUDIT3 A3b, 22 rows) | (9) replication_label (predictive) | MARGINAL on 20/20 certified flips (inflation 2). H-INST B4's one-half-width rule catches 0/20: it cannot fire on an issued certificate | test_stats + test_pte_adapter (real W-Z arrays, swap_rel H2) |
| 9 | 22 inconsistent rows are 10 events; W-O's "42 transfers" were 20 groups (W-Q) | (8) Units / count_check | FAIL (22 claimed > 10 units) | test_stats (real W-Z rows) |
| 10 | ratio of unlike estimators (fleet GPU "reversal"); single-draw z ratios | (9) ratio_guard | FAIL | test_stats |
| 11 | pooled classes that match no stratum (W-R phase split) | (8) stratified | SIMPSON / MIXED | test_stats (toy) |
| 12 | plan first committed together with its results (W-O, Harmonia G1) | (7) plan_precedes | FAIL (93e2e544b = 93e2e544b); REL4 PASS | test_provenance (real git, read-only) |
| 13 | transfer cell fac4aaa23 read as "C1 search failed multi-hop at d9cc" | (7) support_check | refused: kind transfer | test_provenance (real C1 rows) |
| 14 | one-flag XOR readout passes C1 SIGNAL (.763, lo99 .748) (H-PLANT disagreement 4) | (6) G2 adversary | FLAGGED; the twin gate is CERTIFIED with a plant | test_attainable (toy + the real H-PLANT number) |
| 15 | P3 "zero XOR SIGNAL" confirmed on rows no program can pass (light-cone) | (6) G4 eligibility | ring 2/19 eligible -> FAIL; global 81/81 | test_attainable (real lc_census) |
| 16 | Tyche v0 H1 PASS unreachable (Harmonia R-A) | (6) attainable_labels | flag | test_attainable |
| 17 | arms treated as independent while sharing a seed stream / normal run | (7) seed_reuse | FAIL | test_provenance |
| 18 | hook code changed after the intervention was recorded (provenance hole) | (7) R2 hook digest | FAIL | test_provenance |
| 19 | state-dependent RNG / nonlocal read (would silently corrupt every lockstep contrast) | (2) closure C1, lockstep crn_check | FAIL | test_trace |
| 20 | a must-fail guard that cannot fire (fleet `guard_that_cannot_fire`) | (5) mutation adequacy | idle relations / surviving mutants -> not adequate | test_metamorphic |

The guards also caught two defects in this library while it was being built, before any result was read:
- The lockstep runner first recorded readouts after interventions. `reach` returned INCONSISTENT for a
  post-readout flip, and the runner now reads before interventions, as PTE's trace does.
- `stats._boot_arm_stat` first used row counts in place of arm counts. The Simpson known-answer test failed
  until this was fixed.

## 5. Promotion path

1. **Now: draft in `roles/Ananke/research/harvest/wave2/W2-F/`.** Nothing outside this directory changes.
2. **Core: `prometheus/toolbox/audit/`**, owned by Bellerophon. The toolbox README already separates
   "designers own what to run" from "the toolbox makes it executable and conformance-tested". explib is
   conformance machinery, not science.
   - Bring `checks/core_isolation.py` in as a conformance test: no engine import.
   - Add one mutation-ledger entry per primitive to `prometheus/toolbox/tests/mutants.py`. Examples: drop
     the closure gate in `reach_certificate`; disable A3; make `replication_label` use B4's rule; make
     `plan_precedes` non-strict. Each mutant must be CAUGHT.
   - If Bellerophon declines, use a sibling package `prometheus/explib/` with the same rules.
3. **Adapters live with their engines:**
   - `prometheus/ananke/audit_adapter.py` comes from `adapters/pte.py`. It depends on promoting H-INST
     `pte_trace.py` to `prometheus/ananke/trace.py`, which is PTE_INSTRUMENT_GAPS s3 item 1.
   - A toolbox adapter maps a Worlds-Kernel world with `ext.snapshot.v1` and replay_class BIT to a
     `LockstepEngine`.
   - An NPE adapter for Nestor's B2/B5 is the third.
4. **One copy of each rule.**
   - `provenance.plan_precedes` replaces the three copies of the freeze rule: Ananke
     `tools/freeze_check.py`, Harmonia `freeze_precedes`, and this file.
   - Harmonia R-B and R-D stay Harmonia-owned and are re-exported.
   - `InterventionRecord` becomes an `intervention` block in toolbox receipts, so its content hash enters the
     receipt chain.
5. **Order, each item plan-first with known answers and no campaign:**
   1. trace + reach, with closure as a conformance test;
   2. controls (identity audit as a test utility; PTE_INSTRUMENT_GAPS s3 item 4);
   3. stats units + replication label, before any further intermediate-z carrier claim;
   4. attainable, fed by W2-B's certifier;
   5. provenance into receipts;
   6. metamorphic protocol, with W2-C's operators as the first client.

   Each promotion commit carries a BX-7 transition table on real saved inputs. Example: excluding zero_comm
   as evidence changes the C1 COMM_DEPENDENT / CAUSAL_SUPPORT verdicts.

## 6. Known limits (draft)

- `reach` accepts one readout node per unit. Multi-node readouts, such as MAJ actuator sets, need `ro_node`
  sets.
- The trace is node-granular. Component-level cones are not built; `component_causes` covers write authority.
- `hook_digest` does not digest objects reached through attributes. Pass what matters as `params`.
- `relation_audit` needs null specimen SETS. Row shuffling across specimens cannot detect within-specimen
  design identities, so it is deliberately not offered (see the disagreement with H-INST B2 in the report).
- The predictive replication rule assumes a normal replicate shift. Its `inflation` must be estimated from a
  replicate-seed run; on AUDIT3 the observed flip rate implies about 2.
- Cost: the PTE adapter inherits diff_trace's cost. It is unmeasured on dense champions (H-INST open question 1).
