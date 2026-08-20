# Aporia Standing Loop — resumable by any session

**Principle:** the loop is state, not a process. If the session dies, any new Aporia session
resumes by reading this file + the queues. Armed via self-paced wakeups; work-paced, not
watch-paced — every pass does one real item.

## The four loop layers (who moves what)

1. **Deterministic layer — Windows Scheduled Tasks** (dumb-reliable, no LLM):
   weekly backup (pg_dump fire+sci → Z:\ + robocopy F: corpus, per DECISION 2, precedent:
   PrometheusRekeyObjectZeros); daily DR dispatcher fire (per DECISION 5) once deck exists.
2. **Aporia session loop (this file) — M1's working heartbeat.** Each pass, in order:
   a. `git pull` — ingest fleet commits; if probe results/verdicts landed, **rescore the
      market** (BOTTLENECKS confidences per MOVES expected_if_* preregistrations) and update
      MOVES statuses. Market upkeep is by hand until CI exists.
   b. Execute **one** item from the runnable backlog (below), emitting typed objects.
   c. Commit + push. Report to James only when something changed (noop passes collapse).
3. **Probe seats** — Ergon/Charon/Harmonia B/Techne/Hephaestus sessions, human-kicked
   (kickoff-prompt practice). Not this loop's job; this loop *watches* and rescores.
4. **Weekly HITL page** — Monday: one page (market state, telemetry consumed/emitted computed
   by hand pre-CI, pending DECISIONS by staleness). Alethelia takes this over when built.

## Runnable backlog (priority order; all in-harness, $0)

1. **DR deck #1 + firing cadence** — build the first 20-prompt deck (consumers named at
   firing): ladder Canon §4 literature-grounding pass + market-bottleneck evidence pulls.
   Then hand daily firing to layer 1.
2. **Back-corpus mining** — 442 unread DR reports, slices of ~20/pass; yield → anti-anchors,
   probe templates, catalog updates. (The Pythia consumer test, finally.)
3. **R4 probe generator** — Canon build-debt #1, phase0 pattern, deterministic grading.
4. **Repair ledger + citation-chain base rate** — my own pre-committed self-audits.
5. **M-004 kill-resurrection + detector-band audit** — **APPROVED 2026-08-17.** Prereg LOCKED
   (`pivot/PREREG_M004_kill_resurrection_2026-08-17.md`) before any data touched. Next steps in
   order: co-sign (Charon + Harmonia B/Techne) -> independent synthetic injection (Aporia must
   NOT be the injector) -> 5% calibration set -> 80% recovery gate -> blinded hold-out run.
6. **Plumbing sessions** (gateway, queue client, germline schema, CI, decoys, Alethelia) —
   as capacity allows; schema + backup job first (DECISION 2 makes backup non-deferrable).


## HARD RULE — shadow worklog (James, 2026-08-20)

**Every pass appends one record to `engine/shadow/WORKLOG.jsonl` and includes it in the
pass's commit.** Schema and rules: `engine/shadow/WORKLOG_SCHEMA.md`. Non-negotiables per
record: pre-stated readings, exact evidence numbers, claims typed with strength, citations
with links (primary literature for math content), a non-empty self_identified_weaknesses
list, and a falsifier. An external reviewer (Elenchus, M2 — charter in
`engine/shadow/REVIEW_AGENT_PROMPT.md`) writes `engine/shadow/REVIEWS.jsonl`; at pass start
read any unaddressed reviews and respond in-log (fixed / acknowledged / rebutted). The
reviewer never blocks this loop; this loop never edits REVIEWS.jsonl. A pass without a
worklog entry is an incomplete pass.

## HARD RULE — default-continue (James, 2026-08-18)

**A pass that ends by asking James a question is a FAILED pass.** Seven months and ~20
attempts produced the same failure: an agentic loop pauses because the model owns control
flow and a check-in disposition takes "report" over "continue" every turn. The mechanism to
prevent this (DECISIONS.jsonl) was designed, written into three documents, and then never
used once — I asked in chat instead, every time.

Operating rules, mechanical:

1. **Ambiguity resolves to option A. Log it, continue.** James: *"when I want A, then B.
   Almost always."* A logged wrong choice is reversible; a stall is not.
2. **Reversible ⇒ just do it.** No permission for anything undoable by a later commit.
3. **Irreversible items block THEMSELVES, never the queue.** File to DECISIONS.jsonl with
   status PENDING-HITL and keep working on everything else.
4. **Reports say what was done and decided — never what is needed.** "What's next?" is not
   a question for James; it is the next queue item.
5. **The driver owns continuation** (`engine/driver/run.py`). Inference answers bounded
   questions and returns; it is never asked whether to keep going.
6. **Violation is checkable:** grep a pass's output for a question directed at James. If
   present, the pass failed regardless of what else it produced.


## Steering protocol (James, 2026-08-18)

- **Every pass STARTS by reading `engine/STEERING.md`** and obeying it before pulling work.
  Processed entries move to `STEERING_LOG.md` with what was done. Empty file = full speed.
- **Every pass ENDS by regenerating `engine/PULSE.md`** (`python engine/driver/pulse.py`) and
  committing it — the skimmable, query-traceable state page James reads at 5-hour or 3-day
  granularity. Nothing in it is narrated; north-star judgment is his to make from computed state.
- Steering is BY STATE, never by conversation: edit bottleneck confidences, kill/add moves, veto
  AUTO-TAKEN rows, drop a STEERING line. None of it blocks the loop; all of it redirects the next
  pass.


## The backlog mandate (James, 2026-08-18)

- **Target: ~1000+ prioritized threads, continuously regenerated.** `engine/driver/backlog_gen.py`
  materializes threads ONLY from verified on-disk sources (722 at first run; catalog threads
  expand x30 paradigms on execution — ceiling ~16K). Rerun the generator each pass; it is
  idempotent. Reprioritization is deterministic (score in the generator) plus market linkage.
- **PARK, DON'T ASK — the stuck protocol:** when a thread blocks (gate unmet, error, needs a
  seat), set status=PARKED with parked_reason, and MOVE ON to the next thread by priority. Never
  stop the loop; never ask James in chat. Parked threads surface automatically in his 6x/day M4
  email ("Parked threads — yours to unstick", grouped by gate) and in PULSE.md. James unsticking
  a gate = editing the thread or STEERING.md; the next pass picks it up.
- **Sub-agent fan-outs pull from the top of BACKLOG.jsonl** for their seat (kickoff prompts name
  the thread ids). A fan-out that finishes its thread files results and pulls the next.


## Stash discipline (hardened 2026-08-18 after an incident)

A blind `git stash` + `git stash pop` pair popped an ANCIENT stash (May-era Hecate WIP)
when the tree happened to be clean, conflicting other agents' journals. Rule: only stash
when dirty, with a tagged message, and pop only your own tag:

    [ -n "$(git status --porcelain -uno)" ] && git stash push -q -m aporia-loop
    ... pull/push ...
    git stash list | grep -q aporia-loop && git stash pop -q

Never `stash pop` unconditionally. Old stashes in the list belong to other agents/eras —
never drop them; they may hold uncommitted work (one held two never-committed DR batches).

## Standing rules
- **Every gate ships an ELI5 (James, 2026-08-18):** any thread parked on a NEW gate string gets
  a two-sentence plain-English entry in `engine/queues/GATE_ELI5.jsonl` the same pass, and every
  PENDING-HITL decision carries an `eli5` field at filing. The email renderer displays these
  verbatim (still zero LLM in the email path — the loop authors them at creation time, committed
  as data). A gate rendering "(no ELI5 yet)" in the email is a failed pass item.
LAW 1 at every emission (consumer named); trace-vector shape for failures; decoy discipline
once assembled; no germline ignition (gates: constitution + probe verdict + co-signer seat);
irreversibles → DECISIONS, never blocked on.

**Model-tier rule (James, 2026-08-17):** this loop runs on **Opus-tier** (or lower when a pass
is purely mechanical). Fable's limited pool is reserved for the divergence seats — the
Hephaestus meta-analysis role on M3 — and for occasional high-stakes passes (spec audits,
verdict adjudications, constitution review). The gateway's cheapest-sufficient principle
applies to our own sessions, not just to children. Model provenance stays stamped per commit.
