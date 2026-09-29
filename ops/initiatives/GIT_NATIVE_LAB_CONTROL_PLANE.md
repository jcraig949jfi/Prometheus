# Git-native lab control plane

> **STATUS: STRATEGIC INITIATIVE — PILOT / EVOLVING — NOT A UNIVERSAL OPERATING MANDATE**
>
> The presence of these files or commits does not authorize any seat to migrate its current workflow, stop current
> science, rewrite existing queues, or adopt this operating model on its own initiative. Existing scientific work
> continues under its current contracts unless the operator explicitly selects a seat or campaign for transition.

Captured by Harmonia[m2-475d761f], 2026-09-27, at the operator's strategic-direction request.
Harmonia's role here is to **capture and structure** the initiative. Harmonia does not direct any seat by this document.
Companion files in this directory:
`GIT_NATIVE_OPEN_QUESTIONS.md` (design questions deliberately left open) and
`GIT_NATIVE_EXISTING_MACHINERY.md` (queue, lease and fleet mechanisms already in Prometheus to mine, not rewrite).

---

## 0. Transition policy (read this first)

- **Existing science is grandfathered.** Do not stop, repackage or migrate active experiments to conform to this initiative.
- **Pilot before adoption.** The operator may explicitly select one seat or campaign at a time; nothing else transitions.
- **No self-migration.** Reading this initiative in Git does NOT authorize a seat to convert its queue, journals,
  experiment formats or running work.
- **Learn before automating.** Start with conventions and a small pilot. Build the smallest CLI that observed repetition
  justifies. Build an autonomous scheduler only after real Task traffic shows what it needs.
- The directory layout in s4 is a **draft**. Only `ops/README.md` and `ops/initiatives/` exist. Creating `ops/tasks/`,
  `ops/campaigns/`, etc. is a pilot action for an explicitly selected seat, not something any seat should do because the
  layout is written down here.

## 1. Purpose

A proposed future operating model in which:

- **GitHub is the durable source of truth for laboratory coordination**;
- work decomposes as **Thread → Campaign → Experiment → Task → Attempt**;
- named Claude/agent seats are initially **Task executors/subscribers**, not the durable identity of the work;
- Tasks can later be executed by specialized discrete tools **without changing the scientific work model**;
- **Git-native leases** coordinate Task ownership and resource use;
- **Combined Work Orders (CWOs)** select and publish work;
- **resource constraints are explicit**;
- **cleanup is part of completion**;
- **Atlas indexes and reasons over the science but is not the runtime scheduler**.

Current science continues while the model is piloted incrementally.

## 2. The work hierarchy

| Level | What it is | Owns | Is NOT |
|---|---|---|---|
| **Thread** | A durable unresolved scientific or operational question. May stay open for weeks or months; preserves potentially important work without forcing execution. | the question, pointers to evidence, why it matters, status (open / parked / promoted / closed) | automatically an Experiment |
| **Campaign** | A bounded body of work. Its experiments may be related without all testing one hypothesis. | goal, budget, time window, resource constraints, operating policy, owners, stop conditions | a hypothesis |
| **Experiment** | A scientific question or hypothesis. | question/hypothesis, design identity, controls, preregistration where applicable, falsifiers, interpretation boundaries, **scientific verdict** | an execution attempt |
| **Task** | The smallest durable schedulable unit of work; small enough that interruption, agent reset or reassignment is cheap. **The future pub/sub object.** | type, inputs, required outputs, dependencies, resource needs, cleanup requirements | the science's identity |
| **Attempt** | One actual effort by one executor to complete one Task. A Task may have several. | executor, host, start/end, terminal state (s12), receipt | a new Task (retries stay Attempts unless the requested work itself changes) |

Thread examples: B6 code material vs code location; unexplained BAND0 establishments; host-conditioned reproduction;
a suspected instrumentation defect; a mining opportunity in historical evidence.

Task examples: write/freeze a preregistration; replay three fossils; execute seeds 0-7; run a control arm; inspect a
specific artifact; produce a manifest; adversarially review one result; archive evidence; clean up a host.

Attempt example: attempt 1 aborted on host memory; attempt 2 succeeded unchanged; attempt 3 blocked on missing evidence.
**The Task/Attempt split is what separates execution failure from scientific identity.** An OOM is an Attempt fact,
never an Experiment fact.

## 3. Git as durable authority

**Principle:** Git is the durable laboratory transaction history and the source of truth for coordination. Durable
laboratory intent, claims, receipts and decisions should be reconstructable from Git.

Other systems keep their specialized runtime roles: Postgres, comms, Redis, local evidence stores, RunPod, Azure,
Atlas, OS schedulers. Nothing here retires them.

**Not everything belongs in Git.** Git records meaningful state transitions and checkpoints (a Task became READY, a lease
was taken, an Attempt ended DONE_CLEAN, a verdict was issued), **not heartbeat spam**, high-frequency runtime events or
bulk evidence. Bulk evidence stays in its stores; Git carries its manifest and hash.

## 4. Proposed directory model (DRAFT; do not instantiate fleet-wide)

```
ops/
  README.md
  initiatives/
    GIT_NATIVE_LAB_CONTROL_PLANE.md
  threads/
  campaigns/
    <campaign-id>/
      CAMPAIGN.yaml
  experiments/
    <experiment-id>/
      EXPERIMENT.yaml
      PREREG.md
  tasks/
    <task-id>/
      TASK.yaml
      LEASE.yaml               # only while claimed
      attempts/
        <attempt-id>/
          RECEIPT.yaml
          LOG.md
  resources/
    FLEET.yaml
    hosts/
      <host>.yaml
    leases/
  cwo/
    CWO-0000.md
    CWO-0000.yaml
```

Design notes:
- **One file per object**, not a single giant mutable queue file. Independent files mean independent Task claims don't
  conflict in Git, which gives safer concurrency.
- **Don't over-engineer the schema.** The pilot should discover which fields are actually needed. The sketches below
  are illustrations, not a schema.

```yaml
# ops/tasks/<task-id>/TASK.yaml -- ILLUSTRATIVE ONLY
task_id: T-...
thread: TH-...        # optional
campaign: C-...       # optional
experiment: E-...     # optional
task_class: SCIENCE_RUN          # s11 vocabulary
state: READY                     # e.g. DRAFT | READY | LEASED | DONE | BLOCKED | CANCELLED
depends_on: []
dispatch:                        # s7 envelope
  allowed_engines: []
  required_capabilities: []
  resources: {cpu_workers: 2, ram_gb: 4, gpu: 0, wall_time: 2h}
inputs: []
required_outputs: []
freeze_refs: []                  # prereg / hypothesis freezes this Task must honour (path + sha256)
cleanup: []                      # s12
```

```yaml
# ops/tasks/<task-id>/LEASE.yaml -- ILLUSTRATIVE ONLY; exists only while claimed
task_id: T-...
attempt_id: A-...
executor: Archaeon[m2-xxxxxxxx]   # seat[instance], or a tool id later
host: SPECTREX5
claimed_at: 2026-..Z
expires_at: 2026-..Z             # renewed by long jobs (open question Q1)
resource_lease: ops/resources/leases/<id>.yaml   # optional, s6
```

## 5. Git-native claim model (to PILOT; not a proven scheduler)

A worker:
1. fetches/pulls current canonical state;
2. verifies the Task is READY and unleased;
3. creates the Task's `LEASE.yaml` and an Attempt record;
4. commits;
5. pushes;
6. **begins work only if that push succeeds.**

If another worker claimed the same Task first, the rejected push (non-fast-forward) and the rebase expose the conflict,
and the second worker backs off. This is an **optimistic compare-and-swap** on the Git ref. It relies on the push being
atomic, and on both claims touching the same path so the rebase conflicts (or on the second worker re-checking for
`LEASE.yaml` after rebasing).

Known concerns, deliberately **not solved in this round** (see `GIT_NATIVE_OPEN_QUESTIONS.md`): lease expiry; branch
strategy; clock assumptions; recovery after worker death; concurrent independent Task claims (push contention on one
branch even when the files are disjoint); conflicts touching a shared host resource ledger; how long jobs renew leases;
how cleanup releases them.

## 6. Task lease vs resource lease (kept separate)

- **Task lease:** *this executor currently owns responsibility for this Task Attempt.*
- **Resource lease:** *this Attempt is authorized to consume a declared portion of a host or cloud resource.*

A resource lease should eventually describe: host; CPU cores/workers; RAM ceiling; GPU count; VRAM requirement;
disk/network requirements; wall-time cap; cloud spend ceiling; expiration; owning Task/Attempt.

**A seat does not permanently "own" a machine** merely because it normally runs there. Resources are leased per Attempt.
**Existing placements remain unchanged during the pilot** (the topology ruling of 2026-09-16 and every seat's current host
stay as they are).

## 7. Task pub/sub (intended evolution; no broker now)

Each Task should eventually carry a machine-readable **dispatch envelope**: task_id; thread/campaign/experiment;
task_type; allowed engines; required capabilities; dependencies; resource requirements; inputs; required outputs;
scientific freeze references; cleanup requirements.

**Stage 1: named seats consume Tasks.** Conceptual subscriptions, as illustrations, not assignments:
Archaeon → causal-lens / forensic / Archaeon experiment Tasks; Bellerophon → BEE execution Tasks;
Aether → GPU / RunPod Tasks; Atlas → index / harvest Tasks.

**Stage 2: specialized deterministic workers subscribe to the same task types:** a replay worker, an artifact hasher, a
RunPod launcher, an Atlas harvester, a causal provenance tracer, an analysis reducer. The Experiment doesn't change
when its executor does; that is the point of the Task/Attempt split.

**Do not implement a generalized broker now.**

## 8. Combined Work Order (CWO)

The CWO is the **operator-level portfolio selection artifact**. A CWO:
- selects the Threads worth advancing now;
- creates or activates Experiments and Tasks;
- states dependencies;
- assigns initial owners or subscriber classes;
- specifies resource ceilings;
- preserves deferred Threads without losing them;
- distinguishes **integrity, mining, frontier science and infrastructure** work.

**The Markdown CWO explains WHY; the machine-readable Task files specify WHAT.** Agents shouldn't have to infer
execution details from a long prose strategy document. Only the operator (or an operator-issued CWO) promotes work to
active.

## 9. Atlas boundary

Atlas **remains**: the historical/scientific index; the evidence graph; the proposition/defect/blind-spot system; a
mining/proposal source; a portfolio-analysis aid.

Atlas is **not automatically**: the task queue; the resource scheduler; the lease manager; the execution authority.

Atlas may **nominate** Threads or Experiments for a CWO. Operator/CWO promotion decides what becomes active work.

## 10. Evidence maturity (exploratory policy, not a schema)

A ladder so that an LLM observation cannot promote itself into established fact through prose:

| State | Meaning (proposed) |
|---|---|
| SUGGESTED | Inferred or proposed; no machine evidence yet |
| CODE_LOCATED | The claimed mechanism is pinned to specific code/artifact (path + commit) |
| REPRODUCED | The effect recurs when re-run |
| REPLAY_MATCHED | A deterministic replay matches the recorded artifact (byte- or hash-level) |
| INTERVENED | A controlled intervention changes the effect as predicted |
| CROSS_IMPLEMENTATION | It holds in an independent implementation |
| AUDITED | An adversarial/independent audit passed |

**Principle: inference may propose; machine evidence promotes.** Contrary evidence and uncertainty are preserved beside
the claim, never overwritten. This lines up with existing Prometheus doctrine (the permanence ladder P0-P4;
"positive results are provisional"; "executing lens beats reading lens"). The pilot should reconcile the ladders rather
than add a competing one.

## 11. Task classes (pilot vocabulary)

SCIENCE_RUN · FORENSIC_MINE · ANALYSIS · INTEGRITY · REVIEW · ENGINEERING · INFRASTRUCTURE · ARCHIVE · INDEX ·
CLEANUP · OPERATOR_DECISION

Purpose: later, resource-aware scheduling (an INDEX Task and a SCIENCE_RUN Task compete for different things).
Vocabulary is pilot material, not a fleet mandate.

## 12. Cleanup contract (target principle)

**A Task Attempt is not complete merely because its scientific command ended.** Terminal Attempt states should distinguish
clean completion from dirty termination:

DONE_CLEAN · FAILED_CLEAN · BLOCKED_CLEAN · ABORTED_CLEAN · **DIRTY**

"Clean" may require: owned worker processes gone; cloud pods/VMs terminated **and absence verified**; resource leases
released; evidence archived or intentionally retained; manifest/hash produced where required; temporary resources removed;
worktree clean or explicitly preserved; cost/resource accounting recorded.

**A DIRTY Attempt should create or require a CLEANUP Task.** Existing campaigns are **not** retrofitted during this capture.

## 13. Journal / receipt / report

| Record | Carries |
|---|---|
| **Journal** | Why the seat made its decisions; what changed conceptually |
| **Task Attempt receipt** | Mechanical execution history (what ran, where, when, exit, cleanup) |
| **Scientific report** | Evidence, analysis, conclusions |

Write each fact once, in the record it belongs to, and link the others to it rather than triple-writing. Atlas can index
all three later.

## 14. Fleet inventory (seed from Odysseus; don't compete)

Known fleet at capture time: M1 / SKULLPORT · M2 / SPECTREX5 · M3 / GANDALF · M4 / HARRY1 · BUCKKEEP · ubu001 · ubu002 ·
DESKTOP-RUAPVAI · RunPod · future Azure.

**Proposal:** Odysseus's existing fleet inventory becomes the **seed** for a machine-readable resource catalog
(`ops/resources/FLEET.yaml` + `hosts/<host>.yaml` in the draft layout). **Odysseus's charter is not changed in this round.**

The future inventory should capture: OS; CPU/core count; RAM; GPU model/VRAM; disk/free capacity; network constraints;
installed runtimes; service-critical responsibilities (what must not be starved); safe execution/resource envelopes;
cloud-controller capabilities. **No secrets or credentials belong in the inventory.**

(Existing per-host fact sheets are inputs to that seed, e.g. Harmonia's ubu001/ubu002 hardware log at `infra/ubuntu_nodes/ubuntu_server_machines.md`.)

## 15. First pilot (recorded intent only)

The operator (with ChatGPT) currently intends to evaluate **Archaeon on M2** as the first candidate pilot, **subject to a
separate, explicit operator directive.**

- **This Harmonia commit does not direct Archaeon.** No Archaeon Tasks, leases or Attempts are created here.
- Reasoning as given: Archaeon's Contract v0.2 round just closed; it has no heavy campaign running; its next B6/B1
  semantic-hardening work is naturally divisible; Bellerophon currently uses substantial M2 resources; Ensorain has a
  frozen, launch-sensitive campaign; Cosmos is finishing a sealed-holdout sequence.
- **The pilot must stay lightweight while Bellerophon's active campaign is using M2.** The pilot's first resource lease
  should declare an envelope that leaves Bellerophon's allocation untouched.

## 16. What the pilot should produce before anything scales

1. Real Task files for one seat's real work, and a list of which draft fields were used, unused or missing.
2. Observed claim/push contention (or its absence) under the s5 protocol.
3. Attempt receipts with honest terminal states, including at least one non-DONE_CLEAN case if one occurs.
4. The smallest helper (script/CLI) that the repetition justifies, and nothing more.
5. A written go / change / stop recommendation back to the operator.

## 17. Existing machinery

See `GIT_NATIVE_EXISTING_MACHINERY.md`. The Vivarium canonical queue, comms claims, GPU reservation patterns, the
Archaeon/Vivarium queue history, the orchestration forensics and Odysseus's inventory are **to be mined, not silently
replaced.**
