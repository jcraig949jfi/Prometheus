# Attention event contract v0 (PHEME-02 steps 3-4)

Currency: 2026-09-11. Status: PROPOSED, not executed. Nothing in this
file runs. Built from roles/Pheme/design/INVENTORY_2026-09-11.md and
roles/Pheme/design/retro_corpus.jsonl (37 labelled events); the
category decisions cite corpus ids.

## 0. The three things, separated (ruling step 4)

    OBSERVATION  a typed surface changed between two snapshots.
                 Produced by DIFFERENCING a surface against its own
                 previous snapshot. Deterministic. Logged, never routed.
                 Unit: (surface, object_id, field, from, to, at, evidence)

    NOVELTY      the observation's key is not in the seen-set.
                 key = sha256(surface | object_id | field | from | to)
                 (the preflight ratchet's rule, generalised: a known-
                 still-failing thing is silent; a stale entry that now
                 passes is novel; a new failure is novel). Deterministic.
                 Repeats of an unresolved novelty re-enter ONCE at an age
                 threshold (s5), never per tick.

    ATTENTION    the novel observation satisfies its class predicate AND
                 has at least one DEPENDENT: an object that names it as a
                 blocker, input, consumer or claim (a backlog row's
                 blocked_on, a MONITORS row's INPUT, a claim's
                 dependency, a receipt's declared SHA). Routed once to the
                 owner of the dependent through comms (kind report), and
                 to the operator only when the dependent is an operator
                 decision (an XL backlog row). Deterministic.

An observation with no dependent is filed, not sent. A novel observation
with no dependent is filed with a flag so the seen-set does not swallow
it forever, and re-enters on the age rule. This is the quiet: the
corpus's N13 (18 adoption transitions in one day, all caused by the
operator) becomes 18 observations, 18 novelties, and 0 attention events
unless a backlog row was blocked on one of those seats -- in which case
exactly that row's owner hears about it.

Pheme never decides importance. Importance is whatever the dependents
graph already says: if nothing in the repository depends on an object,
Pheme has no authority to say its change matters, and says nothing.
The LLM-oracle failure mode is excluded by construction: every field
of an attention event is a computed value or a quoted row, and the
predicate table below is the whole of the seat's judgment.

## 1. Classes: what the corpus kept, merged and killed

The ruling offered eight candidate classes. Against the 22 positives and
15 negatives:

KEPT (5), each defined as a transition on a typed surface:

C1 REGISTRY_TRANSITION -- a registered loop's state, freshness or
   productivity crosses its own declared threshold (MONITORS.md rows:
   INPUT absent, last_success_at older than threshold, productivity 0
   for N consecutive runs, state column edited; conformance gate state
   changed; a scheduled task's last result code changed).
   Corpus: P01 P09 P12 P15 P22 fire; N03 N04 N07 N09 N10 N11 stay
   silent because nothing crossed. Merges the ruling's "previously dead
   machinery producing new evidence" (DEAD/DORMANT -> productivity > 0
   is the same predicate in the other direction) and the ruling's
   "orphaned or stranded work becoming visible" where the stranded
   count is a registered productivity signal.

C2 RATCHET_TRANSITION -- a control, probe, test or lint finding changes
   membership in a known-failing baseline: new FAIL, known FAIL now
   PASS, a fixture that previously fired now silent (attacks/preflight
   ratchet; Kairos claim_lint findings per packet; any seat's negative /
   positive / cheat control results when written as rows).
   Corpus: P05 fires; P02 P03 P04 would fire on today's instruments
   and did not exist at occurrence. Merges the ruling's "first
   occurrence of a previously unseen failure shape": a failure shape is
   unseen exactly when its key is not in the baseline; the SFE
   FAILURE_RECORDED event with a novel failure-shape hash is the same
   rule on M7. Also absorbs "calibration or instrument drift" in its
   measurable form (a control that flipped); drift that no control
   measures is UNMEASURABLE and is not a class.

C3 VERDICT_TRANSITION -- a typed verdict about a named object changes or
   is contradicted by a second typed verdict on the same object id:
   PEW constraint status event (PROPOSED/SUPPORTED/NARROWED/SUPERSEDED/
   REFUTED); a PEW relation of class CONTRADICTS / REFUTES /
   FAILS_TO_REPLICATE added; a calibration-ledger row appended; a comms
   message of kind ruling; a review verdict row naming an object another
   seat's row names differently.
   Corpus: P13 P18 fire; P07 would fire today (comms did not exist);
   P08 P20 INDETERMINATE (depends on whether the seat wrote the row);
   P10 P19 P21 do NOT fire and should have -- they are prose. Merges the
   ruling's "contradiction of an accepted result", "gate/verdict
   transition" and "cross-seat disagreement over the same object";
   the last is kept only where both sides name one object id, otherwise
   UNMEASURABLE.

C4 PROVENANCE_PROPERTY -- a receipt's declared fact fails its property
   check: a quoted SHA is not an ancestor of origin/main; a quoted path
   does not resolve from the canonical checkout; a running process's
   build hash is not the SHA the receipt or the fix claims; a manifest
   hash does not verify.
   Corpus: P06 P11 P14 fire. Not in the ruling's list; the corpus put
   three of its fourteen typed positives here, and they were the
   expensive ones (48 dead rows; a handoff pointing at nothing).

C5 COUNT_CROSSING -- a count that the doctrine says must be zero
   crosses zero, or a count that must be positive reaches zero:
   stranded/unattested rows, missing tracked files in a checkout,
   unblocked work in a queue, unseen messages older than a threshold.
   Corpus: P16 P17 fire; N12 (644 rows parked in one batch) collapses to
   one observation because the class key is (surface, from, to, reason)
   per commit, not per row.

KILLED (1):

   "an observation that changes what should be attempted next" -- this
   is the DEFINITION of attention, not a detectable class. Deciding it
   requires the judgment the ruling forbids. It is replaced by the
   dependents predicate in s0: a change "changes what should be
   attempted next" exactly when a backlog row, monitor input, claim or
   receipt depends on the changed object. If the backlogs do not name
   their blockers as objects, this predicate degenerates and Pheme
   says so (s6, the honest failure).

MERGED (3, into the kept five as noted): first-unseen-failure-shape ->
C2; dead-machinery-produces-evidence -> C1; cross-seat-disagreement ->
C3 (narrowed to shared object ids). "Calibration or instrument drift"
is split: the measurable half -> C2, the rest UNMEASURABLE.

## 2. Surfaces v0 (all exist; none is Pheme's; Pheme only reads)

    surface                          class  snapshot source            history depth
    roles/base-role/MONITORS.md      C1     git revisions              42 revs, 1 day
    stations/REPORT_latest.json      C1     git revisions              4 revs since 08-20
    archaeon_tick.log decisions      C1     file (untracked)           per run
    conformance receipts             C1/C4  run rows (queue schema)    per run
    schtasks last-result codes       C1     host query                 live only
    attacks/known_failing.json +     C2     git revisions + probe run  2 revs since 08-24
      preflight --probes output
    Kairos lint ledger               C2     lint_last_run.json         DORMANT (no input)
    PEW constraint events, relations C3     API (unreachable 09-11)    UNKNOWN
    roles/*/calibration ledgers      C3     git revisions              11 files
    comms messages kind=ruling       C3     Postgres                   since 09-11
    engine/shadow/REVIEWS.jsonl      C3     git revisions              8 revs
    journal/receipt SHA + path       C4     git grep + is-ancestor     all journals
    engine/queues/BACKLOG.jsonl      C5/dep git revisions              139 revs since 08-18
    viv.cli status stranded count    C5     CLI                        live only
    git status --short (canonical)   C5     host query                 live only

## 3. The event record (what Pheme writes; nothing else)

    roles/Pheme/ledger/observations.jsonl   every observation, append-only
    roles/Pheme/ledger/seen.json            the seen-set (key -> first_at, count, last_at, resolved_at)
    roles/Pheme/ledger/attention.jsonl      every routed event with its dependent and recipient
    roles/Pheme/ledger/run_last.json        last_input_at, last_success_at, counts, no_op_reason (rule 8)

An attention event:

    {"class": "C1..C5", "key": "<sha256>", "surface": ..., "object_id": ...,
     "from": ..., "to": ..., "at": ..., "evidence": [<quoted rows or SHAs>],
     "dependents": [{"kind": "backlog|monitor|claim|receipt", "id": ..., "owner": <seat>}],
     "routed_to": [<seat>], "comms_message_id": <int|null>,
     "first_seen": ..., "occurrence": 1}

No free-text summary field exists in the record. A recipient reads the
quoted rows.

## 4. Predicate table v0 (the whole of the seat's judgment)

    C1  state column changed  OR  now - last_success_at > threshold (first crossing)
        OR productivity == 0 for N >= N_min consecutive runs (N_min from the row; default 24)
        OR conformance state != previous state
    C2  probe/lint/control key in FAIL and not in baseline  OR  key in baseline and now PASS
    C3  constraint status changed  OR  new relation in {CONTRADICTS,REFUTES,FAILS_TO_REPLICATE}
        OR calibration row count increased  OR  comms kind == ruling
        OR two review rows on one object_id carry different verdict tokens
    C4  not is_ancestor(quoted_sha, origin/main)  OR  not exists(quoted_path)
        OR live_build_hash not in {declared_sha, ancestors-after(fix_sha)}  OR  manifest verify fails
    C5  count crossed 0 in the direction the row's doctrine forbids
    dep exists(object with blocked_on/INPUT/depends_on/declared == object_id)

Every predicate has an INDETERMINATE branch: a surface that cannot be
read (PEW HTTP 000; a host query from the wrong machine) yields
INDETERMINATE(reason) for that surface on that run, never CLEAR, and the
run record says so (Alethelia's rule, inherited).

## 5. Silence rules (the part that makes Prometheus quieter)

- One attention event per key per lifetime, plus at most one AGE
  re-entry when the key is unresolved after 7 days (the May daemon's
  EVAL_DROUGHT number), then silence until resolved. resolved = the
  reverse transition observed, or the dependent closed.
- Bulk collapse: all rows sharing (surface, from, to, reason) in one
  snapshot delta are one observation (N12).
- Explicit no-ops (NO_WRITE_CADENCE, a health answer, a heartbeat, a
  sync receipt) are never observations of the object they report on;
  only their absence past a threshold is (N03-N06, N15).
- Labels are not properties: agora heartbeat 'online', a task's exit 0,
  a solver's 'optimal' are never read as the object's state (N08; base
  rule 2). Pheme reads the freshness source the MONITORS row names.
- Pheme never routes to the operator except for a dependent that is an
  XL backlog row (an operator decision). The operator's queue is then
  derivable from attention.jsonl, and it is short by construction.

## 6. What this contract cannot do (stated before the probe)

- It cannot see a consequential event that no seat typed. 7 of 22
  positives (P02 P03 P04 P10 P19 P21 and P07 at its date) had no typed
  footprint at occurrence, and 2 more (P08 P20) are indeterminate. The
  recall ceiling of any deterministic transport is the fraction of
  consequential events that reach a typed surface: 13/22 = 0.59 today
  (0.68 if the two indeterminates prove typed). Raising it is a WRITING
  discipline for other seats (calibration rows, PEW relations, comms
  rulings, receipts with SHAs), not a detector; Pheme can report the
  ceiling, and does, but cannot move it alone.
- The dependents predicate needs blockers named as objects. The
  BACKLOG_H0H5 schema's blocked_on column is free text ("operator
  decision D-nn", "a named artifact", a seat name). Where it names a
  seat or a decision id the predicate works; where it names an artifact
  by prose it does not. Measured on the probe (s7 of the proposal).
- It does not rank. Two attention events are not ordered by Pheme;
  their recipients' queues order them.
