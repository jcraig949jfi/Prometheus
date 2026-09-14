# CORONER RUN -- execution contract (v1.0, rulings R-CR-1..3 applied 2026-09-14)

Status: CONTRACT.  Proposed by Rhadamanthus (Keeper) 2026-09-13 under the
harvest charter section V; the three open rulings in section 6 were decided
by James on 2026-09-14 (roles/Rhadamanthus/prompts/2026-09-14_court/
CHARTER_verbatim.md, "KEEPER RULINGS").  The v0 text (hash 282a769ef2...
in FREEZE_2026-09-13.json) is superseded by this file; the FREEZE reader
will report DRIFT on CORONER_RUN.md from now on, which is correct.

## 1. Definition

A CORONER RUN is a bounded, read-only-with-respect-to-the-corpse execution
whose purpose is to answer, about a dead experiment, one of:

  WHAT ACTUALLY KILLED THIS EXPERIMENT?
  CAN WE TEST THAT CLAIM WITHOUT RESURRECTING THE ORGANISM?

It is distinct from a resurrection (the organism runs again), from a
Frankenstein lightning experiment (a repaired organism runs), and from a
Necromancer reading (nothing executes).

The scientific object of a CORONER RUN is not the tool that executes.  It
is the relationship

  grave + evidence + question + instruments + controls + decision rule

and that relationship is what a plan freezes and what approval is given to.

## 2. A coroner MAY

  M1  load preserved outputs, ledgers, fixtures, receipts and manifests;
  M2  replay deterministic transforms of the corpse's own code UNCHANGED
      (a fresh interpreter, historical cwd convention, no edits);
  M3  recompute statistics from preserved inputs;
  M4  build nulls, permute, bootstrap, resample from preserved inputs;
  M5  compare against synthetic controls (signal, null, corrupt, cheat);
  M6  execute a preserved judge or producer on FIXED fixtures;
  M7  read a live database inside a READ ONLY transaction with an identity
      check (adapters/pg_readonly_probe.py), never write to it;
  M8  call an external oracle (z3, truth table, sympy, Lean if present) on
      the claim's own inputs, with append-only ledgers redirected
      (adapters/z3_receipt_redirect.py);
  M9  compute a missing denominator (chance floor, p floor, coverage);
  M10 attempt to reproduce a published number from historical inputs.

No MAY clause carries standing approval (R-CR-1).  M1-M6 are cheap and
read-only; they are still executed only inside an approved plan.

## 3. A coroner may NOT

  X1  restart the agent, daemon or loop that produced the corpse;
  X2  mutate the corpse: no edits to its code, state, ledgers or receipts;
  X3  resume a daemon from saved state;
  X4  generate descendants (new organisms, new archive entries, new elites);
  X5  optimise any objective (no search, no selection, no evolution);
  X6  change the corpse's inputs and call the result history;
  X7  represent a NECROPOLIS ADAPTER's corrected number as the original
      instrument's number (charter IV);
  X8  write outside the plan's declared output directory.

## 4. Plan contract (coroner_plans/CR-NNN_<slug>.json)

  plan_id, question, target (dossier / monster ids), target_grave,
  invocation, hitl_status (PROPOSED | APPROVED | REJECTED | EXECUTED --
  written in the plan file; DEAD_BEFORE_RUN is NEVER written in the plan
  file, see section 7), approval (null while PROPOSED; otherwise {by, when,
  record} where record is a file written under section 8), inputs [{path,
  sha256_lf, bytes}] (fingerprinted at plan time and re-fingerprinted at run
  time; mismatch aborts), tools [tool_id ...] (every id READY /
  READY_WITH_CAVEAT in TOOLS.jsonl), actions [{step, may: M1..M10, tool_id,
  invocation, writes}] (every action names the MAY clause it is under; an
  action naming none is refused), controls (positive, negative, repetition
  -- each with its pre-registered pass rule; the positive control must be
  one the instrument CAN pass -- a control pinned at the alpha rate is a
  kill, see DISP-001), kill_criteria (pre-registered, numbered),
  expected_outputs (files + schema), non_resurrection_argument (why X1-X8
  hold, clause by clause), pre_run_findings (anything learned on synthetic
  data BEFORE the plan is approved; a plan whose kill criterion already
  fires on synthetic data says so here), parent_plan (descendants only:
  {plan_id, sha256_lf} of the dead or superseded parent, section 7).

## 5. Enforcement (coroner_run.py)

  - refuses any plan whose hitl_status is not APPROVED, and any APPROVED plan
    whose approval record file is missing or does not name an operator
    authority (section 8);
  - refuses any plan that has a DEAD_BEFORE_RUN disposition in
    coroner_plans/DISPOSITIONS.jsonl, and refuses any plan whose bytes no
    longer match the fingerprint under which it was disposed (a plan
    repaired in place has lost its identity: section 7);
  - refuses a descendant whose parent_plan does not cite an existing plan
    by plan_id AND sha256_lf, or cites a hash that matches no disposition or
    freeze record;
  - re-fingerprints inputs and aborts on mismatch;
  - refuses actions that name no MAY clause, or a tool_id whose registry
    status is not READY / READY_WITH_CAVEAT;
  - confines writes to <plan_dir>/<plan_id>/runs/<timestamp>/ and records the
    git head, interpreter, inputs and every tool's source_commit in
    RESULT.json;
  - never imports a daemon's run loop: adapters are invoked, not agents.

  Enforcement is structural, not moral: it cannot detect a MAY-labelled
  action that is actually a resurrection.  That is what the HITL read of
  the non_resurrection_argument is for.

## 6. Rulings (James, 2026-09-14)

The questions posed in v0 and the rulings returned are not numbered
identically; the mapping is recorded here so the record is not read as
answering a question that was not asked.

  v0 question                          | ruling
  -------------------------------------+---------------------------------------
  R-CR-1 per plan / per run / per class| R-CR-1 APPROVED: PER-PLAN AUTHORIZATION.
                                       | "M1-M6 reads do NOT receive standing
                                       | approval.  Every CORONER RUN requires a
                                       | frozen plan and explicit approval."
                                       | Reason: standing permission would turn
                                       | CORONER into an exploratory shell.
                                       | "Keep approval cheap, but explicit."
  R-CR-2 may M7 run without per-run    | subsumed by R-CR-1: no clause has
         approval on env credentials   | standing approval, M7 included.  The
                                       | ruling text titled R-CR-2 is the
                                       | DEAD_BEFORE_RUN ruling (next row).
  R-CR-3 is a synthetic kill itself    | R-CR-2 APPROVED: DEAD_BEFORE_RUN IS A
         the record?                   | VALID OUTCOME, "a first-class scientific
                                       | product.  Record exactly what killed it.
                                       | Never silently repair the plan and
                                       | retain its identity.  A repaired
                                       | descendant receives a new plan/version
                                       | and cites its dead parent."
  (not asked)                          | R-CR-3 APPROVED: APPROVAL RECORD IS
                                       | OPERATOR/HITL AUTHORITY.  Agents may
                                       | propose, preregister, dry-check,
                                       | challenge, compute fingerprints,
                                       | identify DEAD_BEFORE_RUN, recommend
                                       | execution.  "They may NOT manufacture
                                       | their own execution authority."
                                       | "Fail closed."

## 7. Dispositions (coroner_plans/DISPOSITIONS.jsonl, append-only)

A disposition is a record ABOUT a plan, written beside it, never into it.
Schema necropolis.coroner.disposition/1:

  disposition_id, plan_id, plan_file, plan_sha256_lf, plan_bytes_lf,
  disposition (DEAD_BEFORE_RUN | SUPERSEDED | WITHDRAWN), killed_by
  {finding, kill_criterion, control_case, control_result_file,
  control_result_sha256_lf, control_git_head, measured, mechanism,
  grave_touched, what_died}, hypothesis_status, ruled_by, ruling_source,
  ruling_quote, ruled, recorded_by, recorded, plan_modified_in_place
  (must be false), descendant_requirements, descendants [plan_id ...].

Rules:

  D1  The plan file is not modified.  Its hash in the disposition must
      match its bytes forever; validate_workshop.py errors on mismatch.
  D2  DEAD_BEFORE_RUN is established when the plan's own preregistered
      logic, controls, mathematics, dependencies or identifiability
      requirements falsify its ability to answer its question, without
      touching the grave.  The record names the control case and result
      file (fingerprinted) that fired.
  D3  A disposition says what died: the DESIGN.  It must state the status
      of the target hypothesis separately (for CR-001: UNTESTED).
  D4  A repaired design is a new plan with a new plan_id and a parent_plan
      citation {plan_id, sha256_lf}.  Its hitl_status starts at PROPOSED.
      The parent's disposition lists it under descendants.
  D5  Agents may write dispositions of kind DEAD_BEFORE_RUN (identifying a
      death is within agent authority, R-CR-3).  The ruled_by field records
      who accepted it; a disposition without an operator ruling carries
      ruled_by "PENDING_HITL" and still blocks execution (fail closed).

## 8. Approval records (R-CR-3)

An approval record is a file coroner_plans/<plan_id>.APPROVAL.json written
only after explicit operator/HITL authorization, containing:

  plan_id, plan_sha256_lf (must match the plan bytes at execution),
  authorized_by (an operator identity, never an agent role name),
  authorization_source (path to or quote of the operator's words),
  authorized (date), recorded_by (the agent that transcribed it), scope
  (this plan_id + hash only).

coroner_run.py refuses execution when the record is absent, when
plan_sha256_lf does not match, or when authorized_by names an agent role
(Rhadamanthus, Necromancer, Cleric, Techne, ...).  An agent that has
authority to recommend does not thereby have authority to approve.
