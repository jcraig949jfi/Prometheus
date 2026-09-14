# Pronoia -- queue archaeology, 2026-09-11

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. Built from 363120e08 in
Prometheus-worktrees/pronoia-base-role on M2.

Booting an old seat is an archaeological event, not an instruction to
resume its last queue (base role, seat states). Every item of both
historical queues is classified below against the CURRENT north star and
ecosystem. Only STILL_LIVE is executable work; NEEDS_REPREMISE must be
re-stated before it can be; the rest are recorded and left navigable.

Totals: 1 STILL_LIVE, 3 NEEDS_REPREMISE, 1 PARKED, 3 SUPERSEDED,
3 RETIRED. Existing backlog is not permission to resume an obsolete
mission.

## Era 1 -- the serial research-scanning pipeline (pronoia.py)

Source for the queue: agents/pronoia/README.md at 363120e08, which
documents nine steps and four commands.

### E1-1 | Chain Eos -> Aletheia -> Skopos -> Metis -> Clymene -> Hermes
RETIRED.
The chain was archived as a unit by two program reviews without ever
being adjudicated agent by agent: aporia/docs/program_audit_2026-06-10.md
line 137 and aporia/docs/STATUS_2026-06-15_reset.md line 105. Of the six
links, Eos is BLOCKED (EOS-01), Clymene is BLOCKED (CLY-01), Hermes was
deprecated 2026-05-17 and re-seated today, and the orchestrator that
called them is deleted. Nothing here is a running system to restart.
Residue kept: the six-stage contract itself, which is the only place the
program wrote down what an "intelligence pipeline" stage owed its
successor.

### E1-2 | Step 7, the pipeline health audit
NEEDS_REPREMISE.
The FUNCTION is now constitutional -- base rules 7, 8 and 9 say exactly
what this step was groping at, and roles/base-role/MONITORS.md is the
registry it should have written to. The IMPLEMENTATION is falsified in
detail (RESPONSIBILITIES.md section 0.1): it graded self-reported stdout,
never returned HEALTHY in 37 runs, shipped two detectors that could not
fire and one that fired on another process's GPU memory. Re-premising
means keeping the question ("is this loop producing, not merely
running") and discarding every line of the answer. The re-premised form
is PRON-03 in the backlog.

### E1-3 | Step 8, Titan Council prompt generation on a score-4 trigger
SUPERSEDED.
Superseded by doctrine, not by a newer tool: "No LLM adjudicates. The
model proposes; a deterministic predicate or a human decides"
(base role, section 2). A step that fires because an LLM scored an
entity 4 out of 5, to generate a prompt for five more LLMs to commit
positions, is the shape that rule forbids. Recorded, not revived.

### E1-4 | Step 9, auto-publish reports to main
RETIRED, and actively forbidden.
publish_reports() (pronoia.py:69) runs `git add` over nine path globs,
commits without a message file, and pushes to main from its working
directory. About 40 such commits are in the history, 2026-03-23 to
2026-04-01. Under D-23 this violates section 1 (mutating git in the
canonical checkout), section 2 (no worktree), and section 5 (pathspec
commit, no message file, straight to main). The capability is not to be
re-premised; the need it served -- the operator reading briefs on a
phone -- is met by Era 2 and by the base role's paste-block rule.

### E1-5 | `scan --every N`, continuous mode
RETIRED.
A bare interval loop with no productivity signal is the exact case base
rule 8 was written for, and base rule 9 now requires an owner to show
the upstream is live before launching one. Era 1's own history is the
argument: it fired 37 times in ten days and its own audit never once
said the pipeline was healthy.

### E1-6 | The surviving untracked pronoia.py on M2
STILL_LIVE -- as a hazard to resolve, not as a mission to resume.
This is the only STILL_LIVE row in either queue. The file is runnable,
gitignored, invisible to any seat reading the tree, and its publish step
breaches D-23 three ways the moment anyone runs it from the canonical
checkout. It needs a decision, not an investigation. PRON-02, with the
recommendation attached; no deletion was performed on this pass because
removing an untracked file on a shared host is destructive and
outward-facing.

## Era 2 -- the fleet-visibility loop (scripts/intelligence_loop.py)

Source for the queue: the module docstring at 363120e08 and the measured
stage rows in agora.intelligence_outputs.

### E2-1 | Hourly portfolio refresh + LLM brief
NEEDS_REPREMISE.
Both stages have written 0 rows since 2026-09-09 against 6 per day
before. Before this is restarted, base rule 9 applies: its owner shows
the upstream is live NOW. On this pass the upstream WAS shown live --
agora.agent_heartbeats and agora.intelligence_outputs both took writes
within minutes of the measurement, which contradicts the MONITORS.md row
calling them dead May-era tables. So the launch precondition is
satisfiable; what is missing is a reason the brief should exist, i.e. a
named consumer. Re-premise = name the consumer first.

### E2-2 | Daily email digest (send_brief_email.py)
PARKED.
Hermes claimed the delivery hop on its own adoption pass today
(HERMES-01) and explicitly declined to own its input (HERMES-XL-2).
This seat owns the input and does not touch the hop. Parked pending
PRON-01 and Hermes's own queue; it is routable and its state is
truthful.

### E2-3 | Four-hourly dashboard push to main
NEEDS_REPREMISE.
About 15 consecutive missed cycles; newest push 64de18126 at
2026-09-09T02:15:10Z. Beyond the liveness question, the mechanism is a
loop that auto-commits to main from wherever it is launched, which is
the same D-23 shape as E1-4 and was written before D-23 existed. Any
re-premise lands it on a pinned worktree (D-23 section 6) or it does not
land.

### E2-4 | The 60-second Agora heartbeat with Postgres dual-write
SUPERSEDED as a liveness signal; STILL the thing to repair.
Superseded because comms.agents is now the table the program reads to
know who is online (comms/README.md, base role boot step 1), and because
the base role has ruled that "old Agora heartbeat 'online' fields are
labels whose meaning has expired" -- a ruling this seat's own loop is
the live specimen of. Not retired, because the fix is cheap and the
columns exist: populating last_work_attempt_at, last_work_success_at
and health would turn this from a label into a measurement. PRON-04.

### E2-5 | Friday weekly recap (pronoia_weekly_recap)
SUPERSEDED.
The stage is declared and has written 0 rows in the entire 9-day window
examined, including the five healthy days when every other stage wrote 6
per day. It is a declared capability that never executed -- the same
shape as Clymene's 0-of-8 datasets. Recorded as a documented
non-capability rather than carried forward as work.

## What this classification does NOT do

It does not retire another seat, close another seat's row, or adjudicate
the six agents Era 1 chained. Eos, Aletheia, Skopos, Metis, Clymene and
Hermes each own their own disposition; where this file names their state
it cites their own seat files, dated today.

It does not mark anything dead. RETIRED and SUPERSEDED here are
annotations with reasons, and every residue named above stays reachable:
the six-stage contract, the audit-check schema, the six documented
instrument failures, and the two eras' shared lesson that a throughput
metric satisfies itself.
