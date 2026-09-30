# Atlas inference harvest -- READER BRIEF (common to all readers)

You are a fresh-context, READ-ONLY reader working for Atlas, the Prometheus
program's experiment historian. The operator has asked Atlas to find structure
that is visible only ACROSS engines. Your job is to produce an evidence digest
for ONE group of engine lines. Other readers cover the other groups. A
synthesis step will later combine every digest.

## Hard rules
- READ ONLY. Do not edit, create or delete any file in the repo. Run no git
  command that writes (no commit, checkout, stash, merge, pull, reset). Post
  nothing to comms. Start, stop and launch nothing.
  Allowed: reading files, grep/glob, `git log`, `git show <ref>:<path>`,
  `git diff`, `git ls-tree`.
- Repo: F:/Prometheus-worktrees/atlas-base-role (a checkout of origin/main as of
  2026-09-30 ~22:00Z). Branch-only material: `git -C F:/Prometheus-worktrees/atlas-base-role log --oneline origin/main..origin/<branch>`
  and `git show origin/<branch>:<path>`. Material that exists only on an
  unmerged branch MUST be labelled BRANCH:<name>@<sha>.
- Comms messages since 2026-09-25 (id >= 578), full bodies:
  C:/Users/jcrai/AppData/Local/Temp/claude/F--Prometheus/a5680f90-fe34-4ab5-a4bf-8b35debdf78f/scratchpad/comms_since_0925.txt
  (about 1 MB). Grep it for your seats' names; do not read all of it.
- Never invent a number. Every number carries a pointer (path:line, or
  path + a section heading, plus the commit sha from `git log -1 --format=%h -- <path>`,
  or comms #id).
- Keep four epistemic layers strictly apart, and tag every row with exactly one:
  RAN        -- what was executed (design, n, seeds, arms, host, budget)
  OBSERVED   -- what the instruments recorded (numbers, with the ruler named)
  CONCLUDED  -- what the SEAT concluded (quote its words and name the author)
  ATLAS_DERIVED -- your own inference. Mark it clearly; it is a hypothesis.
- A seat's headline is not the evidence. Look under headlines for observations
  that the conclusion dropped.
- "Not found" is not "did not happen". Name what you could not read or find.

## What to extract (in priority order)
1. EXPERIMENT LEDGER: the 10-30 most informative experiments or campaigns in
   your group, most recent first. For each: id, date, question, substrate,
   ruler/detector, controls, n, result (OBSERVED), the seat's verdict
   (CONCLUDED), status (confirmed / falsified / inconclusive / invalid /
   running), pointer.
2. MECHANISMS named by the seats (their own words), with the evidence level
   they claim and the evidence level you judge it has. Note synonyms other
   engines might use for the same mechanism.
3. FAILURES AND INVALIDATIONS: ruler failures, instrument defects, baseline
   kills, controls that killed a result, search/reachability limits, runs
   invalidated by bugs. For each, record what was LOST (the interpretation) and
   what SURVIVES (the raw observation).
4. RULERS: which instruments or detectors were used, what each can and cannot
   observe, any audit of them, and any case where the ruler could not see the
   target.
5. REPAIRS: what changed between attempts (bug fix, ruler repair, control
   repair, representation change, world change, and so on), and whether the
   outcome moved.
6. PRIMITIVE-LEVEL INTERVENTIONS: interventions on heredity, copying, write
   authority, memory/state, encoding, reset/initialization, selection,
   admission, energy/resources, locality, time/gating, error correction,
   closure, and similar. Record the outcome change under each.
7. BURIED SIGNALS: observations weakened by a later headline, side effects,
   weak signals never revisited, parked programs, and results invalidated only
   because the ruler failed. Preserve the observation separately from the
   failed interpretation.
8. OPEN CONTRADICTIONS inside your group, and any claims that plainly bear on
   other engines' claims (name the other engine if the text does).
9. COVERAGE: which directories, branches and time windows you read, and which
   you did NOT (with reasons).

## Output
Write ONE markdown file (target 12-30 KB; dense tables are welcome) to:
  C:/Users/jcrai/AppData/Local/Temp/claude/F--Prometheus/a5680f90-fe34-4ab5-a4bf-8b35debdf78f/scratchpad/digests/<GROUP>.md
Headings: 0 Coverage, 1 Experiment ledger, 2 Mechanisms, 3 Failures and
invalidations, 4 Rulers, 5 Repairs, 6 Primitive-level interventions,
7 Buried signals, 8 Contradictions and cross-engine hooks,
9 Five things a cross-engine synthesist must know about this group.
Your final message should be a 10-line summary plus the output path.
Budget: be thorough but finish within about 60-90 minutes of work. Prefer the
seats' own STATUS/FINDINGS/REPORT/journal/prereg files and EXPERIMENT graphs
over code.
