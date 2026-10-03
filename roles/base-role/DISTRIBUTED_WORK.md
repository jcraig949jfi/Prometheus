# Distributed work: executable work graphs over A2A / Fabric / Git

Adopted 2026-10-03 by operator directive (verbatim at
roles/Achilles/prompts/2026-10-03_rso_builder_cell/01_OPERATOR_DIRECTIVE_verbatim.md,
section 3). Written by Achilles. Every seat inherits this file through roles/base-role/README.md. It adds to
RESPONSIBILITIES.md and WORKING_CONTRACT.md and may not contradict them; where they disagree, they win.

It is a capability, not a migration order. Existing science, queues and journals continue under their
current contracts (ops/README.md transition policy). A seat uses this protocol for work that is published as
task packets, and a coordinator may publish work this way for any campaign the operator assigns to it.

It is not a scheduler and adds nothing to Fabric (fabric/FREEZE.md). It is the Git-native control-plane
layout (ops/initiatives/GIT_NATIVE_LAB_CONTROL_PLANE.md s4-s5) made concrete and validated by a small
stdlib tool, `python -m workgraph` (workgraph/), with JSON instead of YAML so that no seat needs a package
it may not have.

## 1. Work is an executable graph, not managed agents

A coordinator decomposes an objective into task nodes joined by dependencies, then stops managing people.
A task packet is self-contained: a fresh qualified agent that has never seen the conversation can claim it
and finish it from the packet, the repository and the documents the packet names. If a packet needs an
oral briefing, the packet is defective; fix the packet, not the agent.

Layout (one file per object, so independent claims do not collide):

    ops/campaigns/<C-id>/CAMPAIGN.json            the graph: objective, coordinator, authority,
                                                  capability classes, dependency semantics
    ops/campaigns/<C-id>/CAMPAIGN.md              why (prose); CAMPAIGN.json says what
    ops/campaigns/<C-id>/tasks/<TASK_ID>/TASK.json      the packet
    ops/campaigns/<C-id>/tasks/<TASK_ID>/LEASE.json     exists only while claimed
    ops/campaigns/<C-id>/tasks/<TASK_ID>/attempts/<A-id>/RECEIPT.json
    ops/campaigns/<C-id>/escalations/<TASK_ID>_<n>.md   committed escalation bodies

Markdown-only campaigns that predate this file are not work graphs and are not converted.

## 1a. Where a campaign sits (operator, 2026-10-03)

    Epic -> Thread -> Campaign -> [Experiment] -> Task -> Attempt

- EPIC: the operator-level container for a long-lived strategic program (ops/epics/<EP-id>/EPIC.json and
  README.md). Thin: objective, start date, status, governing constraints, exit conditions, thread ids,
  resource references, major operator decisions, deferred areas. Nobody claims an epic; it holds no tasks,
  leases, receipts or claims.
- THREAD: a durable question or capability (ops/threads/<id>.md). It names its epic on an `epic:` line.
- CAMPAIGN: a bounded attempt to advance a thread. CAMPAIGN.json names its `thread_id`.
- EXPERIMENT is optional. A scientific campaign may run Campaign -> Experiment -> Tasks; an engineering
  campaign may run Campaign -> Tasks. Do not manufacture an experiment to fit the tree; a packet may carry
  `experiment_id` when one exists.
- All links are optional for older work: a campaign without thread_id and a thread without epic stay valid.

EVIDENCE ROLLS UPWARD; AUTHORITY DOES NOT. An experiment's receipt may support a campaign conclusion,
several campaigns may change a thread's status, several threads may advance an epic. But a parent's name
or objective never lends its interpretation to a child: a claim stays attached to the cell/experiment
where it was earned.

## 2. Task packet fields

Required (schema prometheus.workgraph.task.v1):

    task_id, campaign_id, title
    objective                 what done means, in one or two sentences
    owner_role                the seat that owns it (or a coordinator-chosen seat)
    quality_class             a capability class the campaign declares (section 4)
    can_downgrade             true only if a lower class may do it
    escalate_to               class or role to escalate to
    depends_on                task ids that must be satisfied first
    problem                   the problem statement
    non_goals                 what this task must not do
    evidence_required         tests or evidence that must exist at the end
    acceptance                {command and/or condition} that decides GREEN
    deliverables              files, interfaces or records produced
    status, history           lifecycle (section 3); history is append-only

Optional:

    parent_objective, eligible_roles (other seats that may claim it), preferred_model, minimum_model,
    requires_shas (exact commits/blobs it builds on), owns (files/interfaces it may change),
    reads (read-only files/interfaces), resource_ceiling, escalation_triggers, kind
    (software|science|document|review|operations), red_required, satisfied_states, receipt (path),
    notes, authority (the directive or ruling that authorised it), experiment_id (when the campaign has one)

A packet may write only what it `owns`; what it `reads` is frozen for it. An unknown field is a validation
error: say it in `notes` instead of inventing a key.

## 3. Lifecycle

    PROPOSED -> READY -> CLAIMED -> RED -> IMPLEMENTING -> GREEN -> LOCAL_REVIEW
             -> INTEGRATION_READY -> INTEGRATED -> CLOSED

Also BLOCKED and ESCALATED (resume to the state they interrupted), SUPERSEDED and FAILED_AS_DESIGNED
(terminal). CLOSED, SUPERSEDED and FAILED_AS_DESIGNED are terminal. GREEN may skip LOCAL_REVIEW when the
task has no review edge; LOCAL_REVIEW and INTEGRATION_READY may return to IMPLEMENTING; CLAIMED may return
to READY (lease released, no work). workgraph/core.py TRANSITIONS is the executable table.

- Only the coordinator (or the operator) moves PROPOSED -> READY. A seat never makes its own work READY.
- RED is the observed expected failure before the work: a failing test, a known-answer fixture that the
  current code gets wrong, a broken case that must be rejected. For non-software work RED/GREEN mean the
  preregistered failure and success evidence states; set `kind` accordingly, or set red_required false
  with the reason in notes. Do not force software words onto a review or an analysis.
- FAILED_AS_DESIGNED is a legitimate outcome: the work showed the design cannot meet its acceptance. It
  closes with a receipt and is evidence, not a defect.
- A dependency is satisfied when the upstream task is INTEGRATED or CLOSED unless the campaign or packet
  sets satisfied_states.

## 4. Capability class is part of the task

A task names the capability it needs, not a person. A campaign declares its classes in CAMPAIGN.json
(`quality_classes`: id, description, rank, default_model, optional minimum_model and escalate_to). Product
names live in that data and in charters, never in this protocol.

The default ladder, which campaigns may adopt or extend:

    Q1  low-ambiguity / mechanical work: CI wiring, manifests, schemas following a settled design,
        repetitive fixtures, generated documentation, deterministic wrappers, simple adapters,
        mechanical refactors protected by strong tests
    Q2  substantial engineering: subsystem design inside a frozen contract, complex TDD, state machines,
        evidence graphs, runtime adapters, reset/restart machinery, integration, complex debugging
    Q3  scarce deep reasoning / adversarial work: adversarial test design, epistemic ambiguity,
        counterfeit construction, cross-abstraction attacks, difficult first-sight review, failures that
        survived strong Q2 attempts

Packet fields: quality_class, preferred_model, minimum_model, can_downgrade, escalate_to.
`python -m workgraph show <task>` prints the effective requirement (packet fields, else class defaults).

## 5. Inference economy (fleet rule)

Use the cheapest capability class likely to complete the task correctly. A stronger model does not take
routine work because it is available. An underpowered model does not improvise around semantic ambiguity to
save inference: it escalates (section 6).

A useful inference should leave behind something that makes the same reasoning unnecessary next time: a
regression test, a fixture, a rule, a schema, a deterministic checker or reusable code. Prefer that
residue to prose.

## 6. Structured escalation

"I am blocked" is not an escalation. An escalation has six parts, in this order:

    TASK_ID:           the packet
    BLOCKER:           what stops the work, in one sentence
    EVIDENCE:          the failing command, receipt, file:line, or the ambiguous text
    OPTIONS:           the alternatives you see (numbered), each with its cost and reversibility
    RECOMMENDATION:    which option, and why
    CAPABILITY_NEEDED: the class or role that can decide (e.g. Q3, the coordinator, the operator)

To propose work that has no packet yet, write `TASK_ID: NEW` and name the file escalations/NEW_<Seat>_<date>_<n>.md.
`python -m workgraph escalation-template <task>` prints it; `check-escalation <file>` validates it. Commit
the body under the campaign's escalations/, move the task to ESCALATED (or BLOCKED for a named external
dependency), and post it on comms to the escalation target with `--task-ref <TASK_ID>`. A reversible
engineering choice is not an escalation (section 8).

## 7. Receipts

Every attempt that ends writes attempts/<A-id>/RECEIPT.json (schema prometheus.workgraph.receipt.v1),
committed with the work:

    task_id, campaign_id, attempt_id, role, model (exact runtime string), quality_class
    start_sha, end_sha (WORKING_CONTRACT s4), files_changed
    evidence_added, evidence_executed (commands and their results)
    red_observed (the expected failure seen before implementation, or null with a reason)
    result: DONE_CLEAN | FAILED_CLEAN | BLOCKED_CLEAN | ABORTED_CLEAN | DIRTY  (initiative s12)
    known_escapes, unresolved, unblocks (downstream task ids), created_at_utc
    optional: instance, host, branch, worktree_path, resources (where measurable), cleanup, notes

The receipt records mechanics; science goes in the report and reasons in the journal (initiative s13).
Receipts are read-only inputs for fleet observability (the census); observers do not steer the graph.

## 8. Finish in place; keep coordination cheap

- Builders work independently inside frozen task boundaries and need no peer permission for ordinary
  implementation.
- Review happens at explicit dependency and review edges named in packets, not on every commit. Nobody
  reviews everything.
- Scientific or semantic ambiguity escalates (section 6). An ordinary reversible engineering choice is made
  locally and recorded in the receipt or notes: the uncertainty, the choice, why it is reversible, and what
  would trigger revisiting it.
- Do not recreate coordination churn: no status meetings by message, no permission-seeking for work
  already in a READY packet you own.

## 9. Mechanics: discover, claim, report, close

    python -m workgraph ready <Seat>          what you may claim now
    python -m workgraph show <TASK_ID>        the packet and its capability requirement
    python -m workgraph transition <TASK_ID> CLAIMED --by <Seat[instance]>

    STATE COMMITS touch only the task directory and go straight to main: make them in a small state
    worktree checked out at a fresh origin/main (e.g. <worktrees>/<seat>-ops, re-based by `git fetch
    origin; git checkout --detach origin/main` before each one), then `git add <task dir>; git commit -F
    <msg>; git push origin HEAD:main`. THE PUSH IS THE CLAIM (initiative s5, optimistic compare-and-swap).
    If it is rejected: fetch, re-read the packet on origin/main; if it is no longer READY you lost the race --
    take another task; otherwise redo the transition on the new origin/main and push again.
    WORK COMMITS stay on your task branch (WORKING_CONTRACT s2: created from a recorded base SHA) and reach
    main only through integration.

    move the packet through RED / IMPLEMENTING / GREEN with state commits as each becomes true; Git
        carries meaningful transitions, not heartbeats
    end: write the receipt; transition to INTEGRATION_READY (or LOCAL_REVIEW if the packet has a review
        edge); the coordinator integrates and moves INTEGRATED -> CLOSED
    python -m workgraph validate              must pass before any push that touches ops/campaigns/
    python -m workgraph status [<C-id>]       counts, and READY tasks still waiting on dependencies

Comms carries notification, not state: post a short report with `--task-ref <TASK_ID>` on claim,
escalation and completion (`python -m comms post --from <Seat> --to <coordinator> --kind report --subject
"<TASK_ID> <STATE>" --body-file <f> --task-ref <TASK_ID>`). Executable, portable attempts may run as
Fabric Tasks (`python -m fabric submit ...`, fabric/README.md s3) with the packet path in the prompt or
params; the packet stays the record. Fabric's A2A v1.0 gateway (fabric/PROTOCOL.md; stateless, run with
`python -m fabric gateway --port 8710`) exposes the same Fabric Tasks to A2A clients. A stale lease (holder gone, no push for
an unreasonable interval) is reported to the coordinator, who releases it with a history note; nobody
deletes another seat's lease silently.

If `ready` shows nothing for you: report READY through the usual heartbeat, run the inherited
work-conserving loop (RESPONSIBILITIES.md 2a) within your own charter, and check `ready` again after
every comms sync. Do not create work for yourself in the graph; ask the coordinator with an escalation if
you believe a task is missing.
