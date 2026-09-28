# Research-ready packets -- read this first (any fresh worker, any machine)

Currency: 2026-09-27. Issued by Odysseus (physics-of-intelligence frontier,
roles/Odysseus/frontier/poi/). Pure ASCII.

"Here. Go mine this for several hours." Each packet R*.md is enough to start
without asking anyone. If it is not, that is a defect in the packet: write
down what was missing (it is a finding for the frontier) and carry on with
your best reading.

## Authority and rules (inherited from roles/base-role/, stated briefly)

- Work in your own git worktree from a fetched origin/main SHA; never
  `git pull` in a canonical checkout (roles/base-role/WORKING_CONTRACT.md).
- You change nothing in another seat's lane (their code, results, docs).
  You write only under the output path your packet names. If you find a
  defect in someone's lane, report it; do not fix it.
- Preregister before touching data: commit your prediction, decision rule
  and eligible count BEFORE the run, in its own commit.
- Every measured claim ships with a NEGATIVE control (can the method say
  "nothing"?), a POSITIVE control (does it detect a planted real effect?)
  and, where feasible, a CHEAT control (does it reject a planted fake?).
- Matched baselines: a random-sampling and a random-walk arm at the same
  budget wherever "search/selection/interaction found X" is claimed
  (EXTERNAL.md s1, BFF 2026).
- Prefer NULL to a fabricated cell. A null with its eligible count is a
  result. A reversal of the packet's framing is the best possible result.
- Stdlib Python unless the packet says otherwise; state the host, Python
  version, wall time and peak RSS of every run.
- Commit rows with verdicts. Pure-ASCII reports.
- Do not write to any agent memory directory; if your harness has one, say
  in your report that context isolation was imperfect.

## Before designing anything (added after the first packet trial, R4_A-001)

- SEARCH THE REPOSITORY FOR PRIOR RUNS OF YOUR QUESTION FIRST
  (git log --all --grep, git grep over campaign/attempt directories, the
  owning seat's journal). The first worker to use a packet found that
  earlier campaigns had already run the same walks (C4-05, C3-SFE-02) and
  the packet did not say so. Cite them; build on them.
- If the packet says an artifact exists ("the summit is known", "the data
  are in git"), verify it before relying on it; say so if it does not.
- Where the packet leaves a control, threshold, baseline or budget
  undefined, define it in your PREREG and list it in PACKET_GAPS.md.

## Reporting

- Write RESULT.md in your output directory: question, what you ran
  (commands, SHAs), numbers, controls, what changed in the packet's
  framing, next questions, limits.
- Post a comms report to Odysseus (python -m comms post --from <you>
  --to Odysseus --kind report ...), or, if you have no comms, leave the
  commit and tell the operator the path.
- Update nothing in roles/Odysseus/ yourself; Odysseus folds results into
  BACKLOG.md.

## Status (2026-09-28): see roles/Odysseus/expedition/READY_PROTOCOL.md

READY is now an empirical status. R4 was cold-start-tried and was NOT
ready; R1, R2, R3, R5, R6 are DRAFT until a worker who did not draft them
runs them. Run expedition/prior_work_search.sh for your packet's key terms
before designing.

## Packets

    R1 copier encoding law            territory C   stdlib, laptop, 3-6 h
    R2 no-gift soup design study      territory D   reading + design, 4-8 h
    R3 control-fires harness          territory E   stdlib, laptop, 4-8 h
    R4 neutral shelf walks            territory C   stdlib, laptop, 2-4 h
    R5 acquisition census             territory D   repo mining, 3-5 h
    R6 content vs influence matrix    territories A/B  stdlib, laptop, 3-5 h
