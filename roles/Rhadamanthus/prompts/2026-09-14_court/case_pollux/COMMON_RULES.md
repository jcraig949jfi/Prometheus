# Common rules for every reader in case POLLUX (court cycle 2026-09-14)

Working tree (read-only for you): D:/Prometheus-worktrees/rhadamanthus-base-role
All paths below are relative to it.  Use absolute paths in your commands.

## What you may do
- Read, with your eyes, every file in the PRIMARY ARTIFACT SET and any file in
  the tree you reach by grep EXCEPT the forbidden paths.
- Run these three admissible STATIC instruments (they read the tree / git object
  store and write nothing into it; import them from Python with
  sys.path.insert(0, "<tree>/engine/necropolis/workshop/adapters") after reading
  their docstrings for the call signature):
    engine/necropolis/workshop/adapters/git_history_census.py   (git log / git show into a scratch dir)
    engine/necropolis/workshop/adapters/consumer_trace.py       (who imports / mentions a path; never piped through head)
    engine/necropolis/workshop/adapters/literal_verdict_lint.py (functions that return one verdict unconditionally)
- Use plain read-only git (git log, git show, git blame) on the tree.
- Write your OWN scratch scripts, stdlib only, over SYNTHETIC data you generate,
  to test a formula you have READ (label any such result RE-IMPLEMENTATION, not
  replay: it is evidence about the design, never about the original instrument).
- Write files ONLY under the output directory named in your prompt and under
  C:/Users/James/AppData/Local/Temp/claude/D--prometheus/73954ab7-6db7-4809-b206-7543b299f62b/scratchpad/<your_role>/

## What you may NOT do (a CORONER RUN needs a frozen plan and operator approval;
## you have neither -- propose, do not execute)
- import or execute charon.agents.pollux or any charon daemon, tick, executor.
- import, load or execute prometheus_math/databases/mahler.py or any dataset it
  loads (it is the grave's INPUT; recomputing a statistic over it is a coroner
  action M3).
- connect to any database, Redis, network service, or set EW_DB_HOST.
- read any file matching *.env, *Key*, *secret*, *credential*, or the contents of keys.py.
- open ANY path under: engine/necropolis/  (except the three adapter files above)
                        roles/
                        comms/
                        C:/Users/James/.claude/
  If a search returns hits under those paths, do NOT open them; list the hit
  paths under "excluded_by_charter" in your report.
- modify, create or delete any file in the tree (no git write commands).
- optimise anything, resurrect anything, or run anything in the background.

## Evidence classes (tag every factual sentence in your report)
  [READ path:lines]        code or prose inspected, not executed
  [EXECUTED instrument]    a static instrument or your own synthetic script ran; give the command
  [QUOTED path:lines]      a historical number repeated from a document, NOT re-measured
  [RE-IMPLEMENTATION]      your own stdlib re-coding of a formula you read, on synthetic data
  [INFERRED]               your reasoning; name the premises by their tags
  [NEEDS_CORONER]          could only be settled by executing the corpse / loading its inputs / reading the DB

Prior verdicts in historical documents are to be read at ZERO weight: record
them, cite them, but every claim you make must rest on your own tags above.
Do not report a pass/fail summary; report the SHAPE of every failure you find.
When you cannot examine something, say NOT_EXAMINED, never "no evidence of".

## PRIMARY ARTIFACT SET (Pollux, Charon swarm, May 2026)
  charon/agents/pollux/daemon.py                (the organism; 2 commits: 8c619443a, 43b094552)
  charon/agents/pollux/__init__.py
  charon/agents/_base.py
  charon/agents/_shared_queues/                 (stygian_priority_queue)
  charon/agents/stygian/daemon.py, charon/agents/stygian/executor.py
  charon/agents/hecate/daemon.py
  charon/agents/erebos/daemon.py
  ergon/learner/greedy/sources.py
  prometheus_math/databases/mahler.py           (READ ONLY; do not import)
  charon/agents/DESIGN_2026-05-19.md, charon/agents/v02_PROPOSAL_2026-05-19.md
  charon/CHARON_SESSION_2026-06-03.md, charon/CHARON_SESSION_2026-06-15.md, charon/CHARON_SESSION_2026-08-12.md
  pivot/charon_swarm_diminishing_returns_2026-05-25.md
  pivot/agent_roster_2026-05-28.md
  aporia/docs/program_audit_2026-06-10.md
  pivot/REASSESSMENT_2026-06-22_consolidated.md
  pivot/COMPONENT_DISPOSITION_PLAN_2026-06-23.md
  pivot/COMPONENT_DOSSIERS_2026-06-24.md
  aporia/docs/PROF_TRIAGE_2026-08-20.md, engine/queues/PROF_TRIAGE.jsonl
  engine/ledger/AGENT_AUTOPSIES.jsonl, engine/ledger/AUTOPSY_TAXONOMY.md
  docs/state.json, engine/queues/BACKLOG.jsonl (grep for pollux only)
Anything else you find by consumer_trace / grep is fair, subject to the
forbidden list.
