# Vivarium backlog — H0–H5

*Opened 2026-09-10. One row per item, each with what it is blocked ON and who
owns the blocker. A row with no blocker is work I can start; a row with one is
work I must not start, and saying which is the point of the file.*

**The rule this file follows.** Vivarium owns kind CONTRACTS and the execution
path. It does not own semantics. So every row below that wraps another seat's
library is blocked until that seat has handed over a definition — not a
library, a *definition*: what the kind measures and what its result means. Two
items today (the eca scorer, the per-cell criterion) sat exactly there, and one
of them is still there.

Status: `READY` startable now · `BLOCKED` waiting on a named seat ·
`PARTIAL` landed with a stated gap · `DONE` for reference.

---

## A. Kinds the roadmap names that have no Vivarium entry

| # | Item | Status | Blocker |
|---|---|---|---|
| A1 | `ca_stream_v2` under D-18 — a NEW KIND, never a flag on `ca_stream_v1`. D-18 changes the reset/injection semantics, and a rule whose meaning changed under the same name would silently re-read every earlier row. | BLOCKED | Herakles: D-18 amendment is the operator's decision and the horizon is not fixed. Need the alternative-1 semantics frozen, plus relaxation AND driven-response measured, before a contract can be written. |
| A2 | `nk_landscape_v0` — engine half is on main (b91880a2d). Kind, params, dispatch, and the permutation-direction pin. | BLOCKED | Daedalus: I could not find the inbox entry naming the payload/result contract. Need the parameter list and, specifically, which direction the permutation is applied — see D1 below, it is not cosmetic. |
| A3 | `eca_rule_eval_v1` SCORED variant — the current kind reports the observable (behaviour digest + equivalence class) and scores nothing. | BLOCKED | Herakles: needs a target and a metric. A scored kind is a new name, never a flag on the unscored one. |
| A4 | `encoding_search_v1` for H5 beta — consumes a FROZEN decoder as a C1 artifact slot and applies it repeatedly inside the kind. | BLOCKED | Herakles + Archaeon: needs the decoder artifact type, its interface id, and whether the search is over genomes or over decoders. The loader half is ready. |
| A5 | `curriculum_discrete_v1` for H4 — adaptive challenge selection sealed inside the kind. | BLOCKED | Harmonia: H4's adaptive protocol must be distinct from M-SIGNAL and is not yet written. |
| A6 | The TEMPORAL PROGRAM INTERFACE for H0/H2 1.1 — sequence counterexamples and stateful components through one interface. This is the piece that makes "H1 transports sequences" and "H2 contributes stateful components" the same experiment instead of two. | BLOCKED | Proteus + Herakles jointly. The design is explicit that a full H1–H2 integration claim waits for H2 reuse evidence AND this adapter, and that the Boolean alpha must not be described as evidence for dynamical transfer. |
| A7 | `boolean_cegis_v2` with 4–6 input tasks or a bounded bit-vector extension (H1 beta). | BLOCKED | Harmonia: beta widens only after a disjoint pilot, and the alpha has not been read. |
| A8 | A named EXTERNAL PROCESS contract (Z3, DreamCoder, any process tree). Process-tree cancellation, lease renewal, limits, repeatability, explicit output validation. | READY to design, BLOCKED to build | Operator: the design forbids smuggling it through an in-process wrapper and requires an explicitly bounded contract. Techne's tools land first. |

## B. The loader and the execution path

| # | Item | Status | Blocker |
|---|---|---|---|
| B1 | RUNTIME LOADER for H3 1.0 — H3's replay is offline today and deliberately does not need the loader. 1.0 needs retained candidates resolved at execution time. | BLOCKED | Archaeon: needs the candidate-stream artifact type and whether a stream is one artifact or a closure of many. |
| B2 | Raise the per-artifact ceiling above 4 MiB, deliberately. The engine now allows 32 MiB; my loader refuses on the DECLARED size first. Correct order, but it means MY limit is the one a large campaign meets. | READY | none — but it must be a versioned change, not a quiet one. |
| B3 | A second codec. `canonical-json-v1` is the only one; a numeric array corpus will want a binary codec with the same round-trip-strict property. | READY | none |
| B4 | Cross-client artifact consumption via a registered topology group. Today every pack must be published by the client the consumer runs as, or the import is refused. | READY | none, but no campaign needs it yet |
| B5 | Dependency closures deeper than one level in a real campaign. The code handles depth 3; nothing has exercised more than 2. | READY | none |

## C. Observability and operations

| # | Item | Status | Blocker |
|---|---|---|---|
| C1 | A CONSUMER STATUS ENDPOINT Archaeon can read instead of `ps`. Today they infer liveness from heartbeat staleness — which reported a live consumer as DEAD today, because the heartbeat only fires between stages and a 227s row outlives the window. | READY | none. **Highest-value item in this file.** |
| C2 | Heartbeat DURING a long row, not only between stages. Fixes the same defect from the other side. Reproduced cleanly 2026-09-11: heartbeat 158s stale while a healthy `eca_rule_eval_v1` row was 190s into a normal execution (peers run 160–620s), so `health` reported `alive: false` for a consumer doing exactly what it should. | READY | none |
| C3 | Distinguish "worker is slow" from "worker is gone" in `stranded()`. A staleness threshold cannot do it; a monotonically advancing per-attempt counter can. | READY | none |
| C4 | Restart the consumer WITHOUT stranding the in-flight row: a stop-after-this-tick flag the loop checks. Today the only stop is `taskkill /F`, which is why phase 2 ran on a 4h47m-old interpreter. | READY | none. Second-highest value. |
| C5 | A durable home for the consumer. It runs from a `.claude/worktrees/` path because the main checkout is parked on another branch. That path can be pruned. **DONE 2026-09-11 (fa14903d7 + launch 17:13 local):** pinned detached worktree `F:/Prometheus-worktrees/vivarium-consumer`, state dir `F:/Prometheus-data/vivarium/var` outside any worktree, launched by Task Scheduler task `VivariumConsumer` so no chat session is its parent. | DONE | none |
| C6 | **DONE 2026-09-11 (fa14903d7):** `build.code` = base_sha/branch/detached/worktree_path/dirty, plus `build.instance.tag`. Record the CODE REVISION in the worker heartbeat. Had the running SHA been visible, today's 404 would have been diagnosed in one query instead of a traceback and a process-start-time comparison. **Hit a second time on 2026-09-11**: I had told Archaeon the commit/boundary window was fixed, and it was — on main, while the pinned consumer ran a build without it. A running SHA in the heartbeat turns "is the fix live?" from an inference into a field. | READY | none. Promote: this is now twice. |
| C7 | **DONE 2026-09-11 (fa14903d7):** `viv/vardir.py` resolves the state dir (env > config `var_dir` > package default), the heartbeat carries `build.var_dir`, `stop` writes there and REFUSES (exit 1) with no live heartbeat unless `--force`. Original text: **The stop flag is per-checkout, and `stop` reports success either way.** `_VAR` is `Path(__file__).parent.parent/"var"`, so a stop issued from any checkout but the daemon's own writes a flag nothing reads — and prints "stop requested" with the path it just wrote. Under D-23 the daemon runs from a PINNED worktree while every seat works in another, so the wrong directory is now the DEFAULT case. Hit for real 2026-09-11; the stop only landed when re-issued from the daemon's own worktree. Wanted: one flag location independent of the checkout, and `stop` refusing rather than reporting success when it cannot see the worker it addresses. | READY | none. Mine. |

## C'. Rule 10 (added 2026-09-11)

| # | Item | Status | Blocker |
|---|---|---|---|
| C8 | Rule-10 bound (17280 non-productive ticks, accountable Archaeon) and halt on the first FAILED row of class ENGINE_TRANSPORT (accountable Daedalus); typed park record; `unpark` clearance; MONITORS.md row declared. fa14903d7. | DONE | none |
| C9 | The park's comms post runs `python -m comms post` as a subprocess from the repo root the daemon runs from. Untested against the live queue (the test injects `notify`); the first real park will show whether the pinned worktree's comms can reach the database with the daemon's environment. Positive control wanted: a deliberate park of a `vivarium-test` worker against the live comms. | READY | none |
| C10 | The daemon logs the CONFORMANT gate result only when it is not CONFORMANT; the stamp lives on each row's `result_summary.conformance`. A one-line `stage=conformance CONFORMANT` at first tick would make the launch precondition (rule 9) readable from the log. | READY | none |

## D. Contracts and correctness

| # | Item | Status | Blocker |
|---|---|---|---|
| D1 | PERMUTATION DIRECTION pin for `nk_landscape_v0`, in the docstring and in a test. Two conventions differ by an inverse; a landscape built under one and scored under the other is not detectably wrong from its own outputs. | BLOCKED | Daedalus: theirs to declare, mine to pin. |
| D2 | Admission-time validation of payload VALUES, not just keys. Archaeon lost 24 rows of `cs-c3-1` to `"ic_density_set": null` where the contract wants `[null]` — C3-null 12, C3-base 6, C3-hist 6, i.e. every failed row in the set, proportional to arm size. My validator refused correctly — at EXECUTION, after each run had already created and **committed** a world and an experiment, and a failed row is terminal. Confirmed 2026-09-11: all 24 are committed-but-unobserved orphans in the ledger. | READY | none. Directly prevents a repeat. |
| D3 | An `INDETERMINATE` outcome path for a kind that ran but could not decide. Today a kind either returns a result or raises. | READY | none |
| D4 | Reduction support for the `record` vector element. `witnesses` is a vector of records whose inner shape is deliberately unvalidated; E16 cannot reduce over it. | READY | none |
| D5 | The `stable` criterion under `transform` — the symmetry tests cover `at_T`; `stable` is asserted equal but the composition with a transform is not separately proved. | READY | none |
| D6 | A pinned fixture for `cegis_boolean_v1` WITH both slots occupied. The current fixture is the S00 cell (both null), so the artifact-consuming path of that kind has no parity anchor. | READY | none |
| D7 | **The runner can commit to the ledger with no register row behind it.** 7 orphans from 2026-09-06 carry my derived world name (`viv-<spec_hash[7:23]>`) and match no spec in my register. A run entered through a tool or a direct call instead of the queue, so the experiment exists and **nobody can ever adjudicate it — not Daedalus, not me**. Worse than the boundary-flag window fixed on 09-11, which at least left a row. Wanted: the execution path refuses to create a world unless it is executing a claimed row, and the tools that legitimately need a one-off go through a declared, marked identity. | READY | none. Mine end to end. |

## E. Reconciliation and accounting

| # | Item | Status | Blocker |
|---|---|---|---|
| E1 | `cost_report().by_artifact` is empty for every shape I could construct on schema 8, and the refusal its note describes does not fire. My events are accepted and not indexed. | BLOCKED | Daedalus: reported 2026-09-10 with four probed combinations. |
| E2 | TRACKA-RECON-2: the producer names the act `transfer`, the executor and engine name it `retrieval`, so a (attempt_id, stage) join reports one byte movement as producer-only AND executor-only. | BLOCKED | Archaeon: proposed joining on the digest instead; theirs to accept or name a shared stage. |
| E3 | Three-way reconciliation once E1 and E2 close: producer ↔ executor ↔ engine on one key. | BLOCKED | E1, E2 |
| E4 | Counterfactual attribution under a declared reuse horizon, from the executor side. Archaeon does it producer-side; nothing does it for execution cost. | BLOCKED | Harmonia: the horizon is a declared quantity, not mine to pick. |

---

## Ordered next three, if nobody says otherwise

1. ~~**C4** (stop-after-tick)~~ DONE 09-10; **C1** (status endpoint) and **C2** (heartbeat during a row) -- the dormancy threshold in MONITORS.md is written around C2's absence.
2. **D2** (admission-time value validation) — one arm was lost to a payload shape that a check at enqueue would have refused for free.
3. **B2** — decide the artifact ceiling deliberately before a campaign discovers it.

## Not in this file on purpose

Scheduling intelligence, scientific interpretation, contrast computation,
retry policy for scientific failure, and anything that would have Vivarium
choose what to run next. Those are Archaeon's and Harmonia's, and the whole
value of this seat is that they stay so.
