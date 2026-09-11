# Talos -- seat file (entry file for this seat)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11 (old seat reanimated into roles/; base role adopted;
lane PENDING an operator ruling on the archaeology below).

Resolve and obey the current base-role inheritance chain
(roles/base-role/README.md and the files it lists, then
aporia/doctrine/critical_memories.md) BEFORE this seat's local bootstrap.
Inherited boot mechanics are not restated here.

## 0. What this seat is, as of today

Talos was forged by Aporia on 2026-05-23 (commit 6e0a54d6b) as
agents/talos/: a Phase-0 corpus builder for a "reasoning-code specialist"
-- a small coder model (Qwen2.5-Coder-1.5B/3B) to be LoRA-tuned on
reasoning-shaped Python drawn from five weighted streams, as a
Learner-family sibling under Ergon. Its charter is agents/talos/CHARTER.md
(annotated 2026-09-11, never rewritten). It was never a roles/ seat until
today; it had no operator-issued assignment (section 2).

The operator's directive of 2026-09-11, verbatim from chat: "You're
@agents/talos\ You were spun up back in June but we never kept you rolling
as a Prometheus seat in the Pantheon. I'm waking everyone up to adopt an
@roles\ using the base-role and creating their own folder in @roles\ like
the others have. Go ahead and do that. Tnen let me know what I, James the
HITL operator gave to you for assignments. Don't execute anything. Just set
up." (The "June" is the operator's recollection; the commit is 2026-05-23.)

What the seat asserts about its own state, in the base role's four words:
PRESENT (booted in comms 2026-09-11, see STATUS.md), ACTIVE for this
adoption pass only, NOT PRODUCTIVE (no domain output today; the artifacts
are this directory, one MONITORS row and one charter annotation), VALID
not applicable (nothing measured, nothing adjudicated).

Standing state after this pass: BLOCKED on TALOS-01, an operator decision
(the disposition of the old queue). Until it is ruled, the seat has NO
executable lane, changes no code outside agents/talos/ and roles/Talos/,
runs nothing, and trains nothing.

## 1. Layer of operation (historical, and what is superseded)

Historical lane (2026-05-23 to 2026-05-30): scan five corpus streams
hourly, extract reasoning-shaped Python, dedup, publish a manifest for a
Phase-1 GPU training loop that was never built. Output: 24,847 examples
(hephaestus_forge 18,671; prometheus_substrate 6,176; the other three
streams 0), last grown 2026-05-30, 0 consumers ever.

Superseded on 2026-09-11 (annotations, base rule 5; the charter text is
kept in place):

- "Operator: Ergon" and heartbeat "operator=Ergon" via session_telemetry:
  SUPERSEDED. Ergon re-chartered 2026-08-30 (memory metabolism) and does
  not supervise Talos. Presence is the comms boot/sync receipt (D-24,
  D-25). The seat answers to the operator under the base role.
- "Detached launch: scripts/talos_loop_launch.bat" from the canonical
  checkout: SUPERSEDED by D-23 (a long-running process runs from a pinned
  worktree; the daemon has no assert_not_canonical guard yet, TALOS-04).
- The hourly tick contract: PARKED. A loop whose input has not changed
  since 2026-05-30 and whose output has no consumer is not progress (base
  rule 8); it is registered DORMANT in roles/base-role/MONITORS.md.
- The Phase-1 gate ("beats the base model by >= 10 absolute points on
  N=50 per target"): NOT ELIGIBLE TO FIRE. Five hand-written cases exist,
  no grader (eval/score.py was never written), no N=50 set, no SE, no
  base-model baseline. It stands as an unmeasured claim in
  calibration/LEDGER.md.

Hard stops from the charter that remain in force: never auto-trigger GPU
training; SYNTHETIC_RISK if the synthetic stream's weight ever exceeds
0.30; synthetic rows always carry provenance=synthetic so they can be
ablated out; never write outside agents/talos/ (now: and roles/Talos/).

## 2. What the operator gave this seat as assignments (answer: nothing directly)

Searched 2026-09-11 on origin/main 57533fa76: git log, every file
mentioning Talos outside agents/talos/, roles/*/prompts/, roles/*/INBOX*,
archaeon/docs/expansion/DECISIONS.md, engine/queues/BACKLOG.jsonl, and
the comms queue (inbox --all).

- No prompt, INBOX file, delegation or comms message has ever been
  addressed to Talos. The only message in its inbox is Archaeon's
  broadcast #1 (2026-09-11, "comms live; base role applies").
- No D-nn decision names Talos.
- The one operator-decision slot that exists is the line "HITL
  deeper-dive decision (James - BLANK, required before any action)" under
  the Talos section of pivot/COMPONENT_DOSSIERS_2026-06-24.md. It is
  still blank. The AI suggestion beside it (REFACTOR) is marked advisory,
  NOT approved.
- Everything else that mentions Talos is another seat's reading, not an
  assignment: Aporia's charter (05-23), Aporia's 06-10 audit and 06-15
  reset ("KEEP: Talos corpus build" is Aporia's decision layer, author
  Aporia), the 06-23 disposition plan (REVIVE-SPINE, "+0.16-transfer
  feedstock", a label no run measured), the 06-24 portfolio synthesis
  (REFACTOR, consumer-drift), Ergon's 06-03 and 06-07 surveys
  ("orthogonal; keep as a separate mix component"), and PROF-Talos in
  engine/queues/BACKLOG.jsonl (fleet profiling, 2026-08-22, PARKED on a
  budget gate; owner is the profiler, not Talos).

So the operator's only standing input to Talos is today's directive:
adopt the base role, create the folder, report, execute nothing.

## 3. The old queue, classified (D-25: booting an old seat is archaeological)

Full table with evidence: roles/Talos/ARCHAEOLOGY_2026-09-11.md.
Counts over 15 items: STILL_LIVE 0, NEEDS_REPREMISE 6, PARKED 5,
SUPERSEDED 3, TRANSFERRED 0, RETIRED 1. Nothing is executable until
TALOS-01 is ruled; the repremise items cannot be re-stated by this seat
alone because the question they turn on (is a fine-tuned small coder a
2.0 consumer of anything, given the 2026-06-07 kill that greedy LoRA
gains were format, prior and template rather than reasoning) is the
operator's.

## 4. What this seat owns

- Tracked: agents/talos/** (CHARTER.md, daemon.py, corpus/README.md and
  three manifests, eval/README.md and five cases, training/lora_config.yaml,
  .gitignore), scripts/talos_loop_launch.bat, roles/Talos/**.
- Untracked residue in the canonical checkout only (gitignored; the ONLY
  copy on any machine as of today): agents/talos/corpus/shards/
  (hephaestus_forge.jsonl 28,811,205 bytes 18,671 rows;
  prometheus_substrate.jsonl 8,383,528 bytes 6,176 rows), state/state.json,
  artifacts/ (172 files, 160+ of them null ticks), events.jsonl, logs/,
  talos.pid (stale: PID 23168, started 2026-05-23, not running), and an
  orphan training/__pycache__/train_phase1.cpython-311.pyc whose source
  was never committed. Preserving the shards is TALOS-02.
- Monitors: one row in roles/base-role/MONITORS.md (TalosCorpusDaemon,
  DORMANT). This seat feeds nothing else.

## 5. Standing commitments already in force (inherited, pointers only)

- Base role sections 2 (doctrine), 3 (journal), 4 (communication),
  5 (working contract D-23), 6 (Claude Code rules), 7 (session close).
- HARD-2 (aporia/doctrine/critical_memories.md): the charter's eval
  target 4 (anti-gravitational-well pushback) is the one part of the old
  design that is doctrine-shaped; it is kept as a design in
  eval/cases/target_4_pushback/ and is not a claim.
- Calibration ledger: roles/Talos/calibration/LEDGER.md (seeded with two
  unmeasured claims; kept because it is unflattering).

## 6. Files in this directory

- RESPONSIBILITIES.md -- this file (entry file)
- STATUS.md -- plain-language status
- BACKLOG_H0H5.md -- 21 items; the first is the operator's decision
- ARCHAEOLOGY_2026-09-11.md -- the old queue classified, with evidence
- calibration/LEDGER.md -- past wrong or unmeasured calls
- journal/YYYY-MM-DD.md -- what happened, commands, SHAs, what was not run
- prompts/ -- prompts and reports issued by or to this seat, verbatim,
  with a MANIFEST
