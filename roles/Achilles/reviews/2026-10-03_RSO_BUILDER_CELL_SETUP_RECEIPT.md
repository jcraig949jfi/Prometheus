# Setup receipt -- Phase 3 RSO Builder Cell (Achilles, 2026-10-03)

Directive: roles/Achilles/prompts/2026-10-03_rso_builder_cell/01_OPERATOR_DIRECTIVE_verbatim.md (MANIFEST beside it).
Built from base 2af086e79 on branch achilles/rso-builder-cell-2026-10-03 in Prometheus-worktrees/achilles-rso-cell
(host ELSA, model claude-opus-5-5). Every commit below is an ancestor of origin/main (verified after each push).

## Commits

    9e5282f42  A  base-role distributed work graphs (DISTRIBUTED_WORK.md, workgraph/, shared-role convention,
                  README/WAKE short form, comms/census/self-test skip *-role, directive saved verbatim)
    876891a92     merge of enceladus/rso-synthesis-2026-10-02 at 3bd02f393, unchanged (30 added files under
                  docs/phase3/: synthesis/ENCELADUS-DIONYSUS-v0.4/ and reviews/ASTRA-6.0/)
    7ca96a828  B  roles/rso-builder-role/ (RESPONSIBILITIES.md, SOURCES.md) + ops/campaigns/C-004/ (CAMPAIGN.json,
                  CAMPAIGN.md, seed task C-004-T000)
    65ad33a9f  C  five seats + INHERITANCE.md rows + cell discovery tests + Achilles records
    422ee5fa9  D  fixes from the fresh-session bootstrap simulation
    (integration merges of concurrent main: 3a6bd8cdd, 1f7c28ff2, 601808dd4; D pushed without one)

## Files

- Global (base role): roles/base-role/DISTRIBUTED_WORK.md (new); RESPONSIBILITIES.md (dated amendment note,
  s2b, one sentence closing boot step 9); README.md; INHERITANCE.md (Shared roles section and table; five seats'
  register and entry-file rows); WAKE_DIRECTIVE.md (short form). README.md (repo): "Starting a seat session".
  ops/README.md: dated note.
- Tooling: workgraph/ (stdlib; validate, ready, status, show, transition, check-receipt, check-escalation,
  escalation-template). comms/api.py roster(), archaeon/tests/test_base_role.py _roles(),
  achilles/census/sources.py roles_on_ref(): skip roles/*-role.
- Shared role: roles/rso-builder-role/RESPONSIBILITIES.md, SOURCES.md.
- Seats: roles/{Palamedes,Pallas,Argus,Cadmus,Eupalamus}/ -- RESPONSIBILITIES.md (entry, two banners),
  WAKE.md, WORK_STATE.json, STATUS.md, prompts/2026-10-03_creation/00_README.md.
- Work graph: ops/campaigns/C-004/ (RSO-METHODS-SLICE-001), seed C-004-T000 READY for Palamedes.
- Achilles: RESPONSIBILITIES.md s7 (outside the cell), journal/2026-10-03.md, calibration/LEDGER.md row,
  comms/2026-10-03_TO_ENCELADUS_merge_notice.md (posted as comms #1267), this receipt.

## Global amendments (base role)

Executable work graphs: self-contained task packets; lifecycle PROPOSED..CLOSED + BLOCKED / ESCALATED /
SUPERSEDED / FAILED_AS_DESIGNED (non-software RED/GREEN = preregistered failure/success evidence); abstract
capability classes with product names only in campaign data and charters (Q1/Q2/Q3 default ladder); inference
economy; six-part structured escalation; attempt receipts (Achilles-consumable); finish-in-place with review at
named edges; claim = fast-forward push of a LEASE.json state commit (Git-native control-plane initiative s5).
Fabric untouched (frozen); comms carries notification only. Shared roles: roles/<name>-role/ is a layer.

## Tests (worktree, merged tree, before each push)

archaeon/tests/test_shared_roles.py (7: shared roles are not seats; registered and inherit the base; declared
chains resolve; entry rows resolve; fresh-session pointers; cell discoverable; C-004 names real seats),
archaeon/tests/test_base_role.py (incl. DISTRIBUTED_WORK.md ASCII), workgraph/tests (21: lifecycle legality,
capability-class parsing, ready/lease/dependency discovery, claim refusal, receipt shape, escalation shape,
repository graphs validate), comms/tests (EW_DB_HOST=M1, throwaway schema), achilles/census/tests.
Full set before A: 90 passed, 8 skipped. Before C: 69 passed. Before D: 43 passed. `python -m workgraph validate`:
1 campaign, 1 task, OK. `python -m comms roster` (M1): the five listed, base-role and rso-builder-role absent.

## Bootstrap simulation (directive s24)

Five independent read-only sessions with no conversation context, each told only "You are <Seat>. Bootstrap from
Prometheus." and pointed at the repository. Result: all ten questions answered from repository files for every
seat, with every design path verified to exist. Palamedes found C-004-T000 READY; the other four correctly found
nothing READY. Defects found and fixed in D: invalid `comms status ... idle`; no concrete heartbeat command; no
concrete A2A/Fabric command; no-work wording vs base 2a; escalation for a missing packet had no TASK_ID; Palamedes
escalated to itself; runtime-model vs preferred-model class at boot; how to tell M1; README short form missing
--model. Remaining "needs the operator" items were the open decisions below and the host choice (by design: seats
are not bound to machines).

## Seat status at handover

    Palamedes  READY  (C-004-T000 READY for it)
    Pallas     READY  (idle by design until a Q3 attack packet exists)
    Argus      READY  (no packet until Palamedes decomposes)
    Cadmus     READY  (no packet until Palamedes decomposes)
    Eupalamus  READY  (no packet until Palamedes decomposes)
None booted: booting would register presence that does not exist.

## Deliberately not done

- No RSO scientific or runtime code; no packets beyond the seed (decomposition is Palamedes's first task).
- No change to fabric/ (frozen) or to the comms protocol; no Fabric worker on Windows.
- The closure review was already canonical on main (09dc8c38b); nothing re-captured.
- Not decided (operator's): C-004 OP-1 slice caps; OP-2 anchor keeper (C5); OP-3 the S1 expected-answer author and
  S3/S4 first-sight reviewer (closure review F names Dionysus).
- Not fixed (pre-existing, other lanes): base WAKE_DIRECTIVE (boot, then read CURRENT.md) vs base boot step 1
  (read CURRENT.md first); INHERITANCE.md lists Icarus twice; roles/Hermes/science/convergence/signature.py still
  treats every roles/* except base-role as a seat (Hermes's lane).
- Achilles's own WORKING_CONTRACT s1/s3 violation (canonical-checkout pulls and commits, 2026-10-01..03) is in its
  calibration ledger.
