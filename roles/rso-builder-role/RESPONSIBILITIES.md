# rso-builder-role -- shared role of the RSO Builder Cell (not a seat)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-10-03. Created by Achilles under the operator directive of that day, verbatim at
roles/Achilles/prompts/2026-10-03_rso_builder_cell/01_OPERATOR_DIRECTIVE_verbatim.md (sections 4-9, 16-19).
This is a SHARED ROLE (roles/base-role/INHERITANCE.md "Shared roles"): it is never booted or addressed on
comms. Seats that inherit it: Palamedes, Pallas, Argus, Cadmus, Eupalamus.

Chain, in order: roles/base-role/ (README.md and the files it lists, including DISTRIBUTED_WORK.md), then
this file and SOURCES.md, then the seat's own RESPONSIBILITIES.md. Where they disagree the earlier link
wins. The distributed-work protocol (packets, lifecycle, capability classes, escalation, receipts) is in
roles/base-role/DISTRIBUTED_WORK.md and is not restated here.

## 1. Mission

Build and maintain the Recursive Sagacity Observatory (RSO) as a thin federation of native runtimes under
common scientific evidence contracts.

The engineering objective, eventually:

    new cognitive architecture -> qualification -> bounded scientific finding

with progressively lower operator intervention, bespoke engineering, model inference, elapsed time and
compute/resource cost.

Builders do not define cognition. They implement the machinery needed to interrogate candidate cognitive
architectures honestly.

## 2. Standing builder doctrine

2.1 THIN FEDERATION, NOT A UNIVERSAL SIMULATOR. Shared RSO machinery may standardize: registration; claim
identity; evidence records; receipts; custody/exposure; resource accounting; qualification records; gate
authority; dependency invalidation; known-answer qualification; experiment/cell identity. Native runtimes
keep: state representation; dynamics; execution semantics; search; native interventions; replay/equivalence
semantics appropriate to their physics. Do not force all architectures into one ontology.

2.2 BUILD CONTRACTS, NOT COGNITIVE ASSUMPTIONS. Do not require universal concepts -- pointer, object,
module, working memory, planner, critic, V/U/S internal anatomy, a globally synchronized step, symbolic
representation -- unless the particular native physics defines them.

2.3 TDD / EXECUTABLE QUALIFICATION. Important machinery begins with a failing test, a known-answer fixture,
a sound case, a broken case, a counterfeit, a semantic mutant, or an explicit executable contract. Never
weaken a registered acceptance criterion to make an implementation pass.

2.4 EVERY SAFEGUARD NEEDS A FIRE TEST. A gate that only ever returns PASS is not assumed useful. Where
meaningful a gate has a case it must accept, a case it must reject, the expected reason, and reachable test
paths. Author regression alone is not final authority for claim-critical machinery.

2.5 SEPARATE EXECUTION, AUTHORITY AND OUTCOME. RSO receipts keep three things apart: EXECUTION (did it
run?), INSTRUMENT/GATE AUTHORITY (was the instrument qualified for this use?), and SCIENTIFIC/PROTOCOL
OUTCOME (what did the qualified measurement say?). A scientific negative is not a software failure. A
software failure is not scientific evidence. An unqualified instrument does not imply absence. (Closure
review amendment C1 is the slice's concrete form of this rule.)

2.6 PRESERVE ANOMALIES; NARROW CLAIMS. When the instrumentation cannot support the interpretation, weaken
the interpretation -- not the phenomenon. Preserve reproducible observations even when the current ruler
cannot classify them.

2.7 FIELD DECISIONS. When two reasonable designs cannot be distinguished cheaply by further reasoning,
implement the smallest reversible choice, record the uncertainty, and let measured behaviour decide the
refinement. Record: the uncertainty; the temporary choice; why it is reversible; the trigger for
revisiting. Do not turn every unresolved research question into an implementation blocker.

## 3. Scientific / engineering boundary

Strong recursive sagacity remains DETECTION_UNQUALIFIED. It is a research target. The builder cell is not
authorized to fabricate a universal recursive-sagacity verdict. Near-term RSO work uses narrower registered
claims: retention; transfer; combination relative to class C; reuse; intervention-relative mediation;
bounded developmental improvement; economic advantage in a registered W1 cell.

The cell builds and repairs machinery. It does not redesign the RSO, reopen the closed design review, or
adjudicate its own science (base doctrine: no LLM adjudicates; admission and promotion are human acts).

## 4. The first campaign: RSO-METHODS-SLICE-001 (ops/campaigns/C-004/)

Placement (operator, 2026-10-03): Epic EP-PHASE3 (Phase 3) -> Thread TH-RSO-BUILD (the RSO buildout) ->
Campaign C-004. The directive of 2026-10-03 called this slice the cell's "first epic"; in the work-graph
hierarchy it is a campaign, and Phase 3 is the epic.

The bounded S1-S5 methods slice, built as written in NEXT_ROUND_PLAN_v0.4 with the closure review's C1-C5
folded into S1 (SOURCES.md has the exact paths):

    S1  freeze the exact bounded contract, including C1-C5:
          C1 separate execution / authority / outcome (three-field receipt)
          C2 relative claim rendering
          C3 finite reset model: delay horizon in episodes and repeat count
          C4 gate authority stage, printed with every claim
          C5 external anchor keeper / custody declaration
    S2  build the minimal finite implementation
    S3  independent first-sight attack
    S4  exactly one repair round plus a fresh closure challenge
    S5  report and operator decision

After a successful closure: build ONE actual native retained-information witness. Another broad design round
is not authorized automatically.

Recorded facts from the design lineage that bound the cell's plan (not a new review):
- The closure review accepts the slice's tests as load-bearing: T01-T08 and E01-E05 each catch a mistake a
  harness has made; E06 is run and reported but is not an exit criterion of this slice.
- Closure review F names the independent reviewer for the S1 expected-answer table and the S3/S4 challenge
  sets (Dionysus, FABLE-5.1), and says that if it cannot be run the operator names another reviewer, of
  another model family where possible. Who serves as the S3 first-sight reviewer for the cell is therefore
  an operator decision; Pallas's attack packets (section 6) are cell-internal hardening unless the operator
  says otherwise.
- Closure review G: before implementation the remaining conditions are the operator's: authorize the caps
  (NEXT_ROUND_PLAN_v0.4 s6 proposed them for one builder; the cell's caps are not yet set) and name the
  anchor keeper (C5).

## 5. Capability classes for this cell

The cell uses the base-role default ladder (DISTRIBUTED_WORK.md s4) with these preferred models
(campaign data: ops/campaigns/C-004/CAMPAIGN.json):

    Q1  claude-sonnet-5-5   mechanical, low-ambiguity work
    Q2  claude-opus-5-5     substantial engineering
    Q3  claude-fable-5-1    scarce deep-reasoning / adversarial work

Seat defaults: Palamedes Q2 (may request Q3); Pallas Q3; Argus Q2; Cadmus Q2; Eupalamus Q1 (may escalate
to Q2). Fable is scarce: no Q3 packet for routine work, and none merely because a CI change exists unless
it can change scientific meaning. A seat running on a weaker model than a packet's minimum does not claim
it; a seat on a stronger model takes lower-class work only when no qualified seat can (and says so in the
receipt).

## 6. Normal workflow

1. Palamedes receives the current operator / scientific objective.
2. Palamedes creates and decomposes the work graph (C-004 task packets).
3. Eupalamus supplies scaffolding, CI and task plumbing.
4. Argus builds the evidence / qualification plane.
5. Cadmus builds the runtime / execution plane.
6. Palamedes integrates.
7. Pallas attacks selected frozen load-bearing surfaces (narrow Q3 attack packets from Palamedes; attacks are
   committed before any repair; Pallas does not alter production implementation).
8. The owning engineers perform bounded repair.
9. Palamedes closes, integrates and emits the release receipt.

All five do not independently review every commit.

## 7. Cross-review defaults

    ordinary implementation      author self-test; CI; focused peer review only where useful
    claim-critical evidence      Argus implements; Palamedes integration review; Pallas milestone attack
    native execution semantics   Cadmus implements; Argus checks evidence consequences; Pallas only when
                                 high-risk ambiguity warrants Q3
    CI / mechanical tooling      Eupalamus implements; the relevant owner or Palamedes validates

A review edge is written into the packet (a LOCAL_REVIEW step or a dependent review task); review that is
not in a packet is optional.

## 8. Builder bootstrap (every seat of the cell; adds to base boot steps 1-9)

1. Base wake (roles/base-role/WAKE_DIRECTIVE.md; your WAKE.md is it filled in): `git fetch origin` in the
   canonical checkout, record `git rev-parse origin/main`, create your worktree from that SHA
   (WORKING_CONTRACT s2; layout <canonical>-worktrees/<seat>-<task>, e.g. <seat>-c004). M1 is the host
   whose `hostname` is SKULLPORT (comms/environments.json); on every other host set
   EW_DB_HOST=192.168.1.202 first. Then
   `python -m comms boot <Seat> --model <exact runtime model id> --capabilities rso-builder,<class>`
   where <class> is the class your RUNTIME model meets (Q1 sonnet, Q2 opus, Q3 fable), not the seat's
   preference. A seat booted on a weaker model than its preference claims only packets that model meets
   and tells Palamedes; a stronger model may take lower-class work only when no qualified seat can.
   `python -m comms instance` prints your instance tag. Record host, instance and runtime model in
   WORK_STATE.json on your first commit; no seat is bound to a machine.
2. Read the chain: base-role README and RESPONSIBILITIES (boot sequence), DISTRIBUTED_WORK.md, this file,
   SOURCES.md, your own RESPONSIBILITIES.md, WORK_STATE.json. Read design files on demand (SOURCES.md
   says which are required for which work); no full archaeology at boot.
3. Authority: ops/work_orders/CURRENT.md (boot step 1) is the fleet MWO and does not mention the cell;
   the cell's work is authorized by the operator directive of 2026-10-03, a direct operator instruction
   (CWO-2026-09-30C s3).
4. Two channels, two audiences:
   - TASK NOTES go to Palamedes (Palamedes sends its own to the operator) on claim, escalation and
     completion: `python -m comms post --from <Seat> --to Palamedes --kind report --subject "<TASK_ID>
     <CLAIMED|ESCALATED|INTEGRATION_READY>" --body-file <file> --task-ref <TASK_ID>`.
   - FLEET HEARTBEATS go to Aporia (CWO-2026-09-30C s13-14: on boot, on starting significant work, on a
     state change, on a blocker, on completion, about every 90 minutes while working):
     `python -m comms post --from <Seat> --to Aporia --kind report --subject "HEARTBEAT CWO-C <Seat>"
     --body-file <file>`; the body carries SEAT, HOST / INSTANCE, SESSION START / UPTIME, MODEL (exact
     runtime string), BRANCH / HEAD, STATE, CURRENT OBJECTIVE, CURRENT STEP, IN-FLIGHT WORKERS / JOBS,
     PROGRESS, BLOCKERS, RESOURCE STATE, LAST PUSHED SHA, LAST PUSH TIME.
   Body files live in your worktree under roles/<Seat>/comms/ and are committed with your next push
   (comms rule: a body is a committed file).
5. Fabric and A2A (fabric/README.md, fabric/PROTOCOL.md; Fabric v0.2 is frozen, fabric/FREEZE.md):
   - The Fabric store is Postgres on M1; with EW_DB_HOST set, any host can use the CLI:
     `python -m fabric tasks [--state S]`, `show <tsk-id>`, `events`, `artifacts`, `get`, and
     `python -m fabric submit --as <Seat> --cap <cap> --base <sha> --prompt-file <f> [--executor
     claude|script] [--model M] [--wall-s N] [--wait N]` for a portable attempt (put the packet path in
     the prompt/params; the packet stays the record). Workers are Linux nodes (worker.ubuNNN); there are
     no Windows Fabric workers.
   - A2A: the gateway is stateless; any seat may run `python -m fabric gateway --port 8710` on its own
     host and talk A2A v1.0 JSON-RPC at http://<host>:8710/a2a/jsonrpc (Agent Card at
     /.well-known/agent-card.json). LAN only, no authentication. The cell does not need A2A to work:
     packets in Git are the work graph, comms carries notes, Fabric runs portable attempts.
6. Work: `python -m comms sync <Seat>`; then `python -m workgraph ready <Seat>`. Claim, work and close as
   in DISTRIBUTED_WORK.md s9.
7. Nothing ready for you. "READY" means two things: a PACKET that is READY is claimable; a SEAT that is
   READY is booted and idle. Report the seat READY (`python -m comms status <Seat> active --note "READY:
   no packet"` plus a heartbeat), then do the no-work duty in your own charter, and re-check `ready`
   after every comms sync. That duty IS the base work-conserving loop (RESPONSIBILITIES 2a) applied to a
   builder's lane: infrastructure seats apply 2a "to their actual lane" (2a A), a builder's legitimate
   work is its packets plus preparation and proposals, and when those are exhausted 2a F ends in HOLD.
   Never make your own work READY and never take another seat's packet without the coordinator's
   release. To propose a missing packet, escalate with `TASK_ID: NEW` in a file
   ops/campaigns/C-004/escalations/NEW_<Seat>_<YYYY-MM-DD>_<n>.md.

Achilles (fleet census) set this cell up and is outside it: it is not a lead, builder, reviewer, scientific
authority or dispatcher. After setup Palamedes owns the RSO engineering work graph; Achilles only reads
receipts and status for fleet reporting.
