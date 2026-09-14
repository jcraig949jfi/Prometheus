# CORONER RUN -- proposed execution contract (PROPOSED, not doctrine)

Status: PROPOSED by Rhadamanthus (Keeper), 2026-09-13, under the harvest
charter section V.  This file legislates nothing.  It names a class of
execution the Necropolis needs, states what it may and may not do, and
describes the enforcement the workshop provides.  Whether a CORONER RUN
requires HITL approval per run, per plan, or per class is a ruling for
James; until that ruling exists every plan in coroner_plans/ carries
hitl_status PROPOSED and coroner_run.py refuses to execute it.

## 1. Definition

A CORONER RUN is a bounded, read-only-with-respect-to-the-corpse execution
whose purpose is to answer, about a dead experiment, one of:

  WHAT ACTUALLY KILLED THIS EXPERIMENT?
  CAN WE TEST THAT CLAIM WITHOUT RESURRECTING THE ORGANISM?

It is distinct from a resurrection (the organism runs again), from a
Frankenstein lightning experiment (a repaired organism runs), and from a
Necromancer reading (nothing executes).

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

  plan_id, question, target (dossier / monster ids), hitl_status
  (PROPOSED | APPROVED | REFUSED | EXECUTED), approval (who / when / where
  recorded; null while PROPOSED), inputs [{path, sha256_lf, bytes}]
  (fingerprinted at plan time and re-fingerprinted at run time; mismatch
  aborts), tools [tool_id ...] (every id READY / READY_WITH_CAVEAT in
  TOOLS.jsonl), actions [{step, may: M1..M10, tool_id, invocation, writes}]
  (every action names the MAY clause it is under; an action naming none is
  refused), controls (positive, negative, repetition -- each with its
  pre-registered pass rule), kill_criteria (pre-registered, numbered),
  expected_outputs (files + schema), non_resurrection_argument (why X1-X8
  hold, clause by clause), pre_run_findings (anything learned on synthetic
  data BEFORE the plan is approved; a plan whose kill criterion already
  fires on synthetic data says so here).

## 5. Enforcement (coroner_run.py)

  - refuses any plan whose hitl_status is not APPROVED, and any APPROVED plan
    whose approval record file is missing;
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

## 6. Open ruling for James

  R-CR-1  Is HITL approval per plan (recommended), per run, or per class?
  R-CR-2  May M7 (live read-only DB) be executed without a per-run approval
          when credentials come from the environment?
  R-CR-3  Does a plan whose pre_run_findings already satisfy a kill
          criterion still need approval to record the death, or is the
          synthetic finding itself the record (recommended: record as
          DEAD_BEFORE_RUN against the proposer without execution)?
