# Operator directive, 2026-09-11 -- the Metis seating

The operator's message, verbatim, as received by the session that
created roles/Metis/. No edits: the text is already pure ASCII.

    You're @agents\metis\ You were an agent back in April but haven't
    been seated since.  Bootstrap and then create a role for yourself
    in the @roles\ directory like the others.  Adhere to the base-role
    concept.  Pull the latest from the repo first as that's where
    you'll see the new roles and requirements.  Don't do anything other
    than this bootstrap and registration except remind me what you did
    when you were active

## How this seat read it

- "Bootstrap and then create a role for yourself ... Adhere to the
  base-role concept" -- the base role's boot sequence, the inheritance
  banner, the seven-plus-two constitutional rules, the seat-state
  vocabulary and WORKING_CONTRACT.md D-23, all read before the first
  seat file was written.
- "Pull the latest from the repo first" -- under WORKING_CONTRACT.md
  s3 this MEANS: `git fetch origin` in the canonical checkout, record
  `git rev-parse origin/main`, then `git worktree add` from that SHA.
  This seat did NOT read it that way in time. It ran `git pull` in the
  canonical checkout as its first action and violated s1 and s3 before
  it had read either. The pull was a fast-forward on a clean tree and
  nothing was lost; the seat then redid the step correctly. Recorded as
  C-04 in calibration/CALIBRATION.md and routed to Archaeon as METIS-06,
  because Atalanta L-09 is the same failure from the same wording on
  the same day, and the contract itself anticipates it: "a seat that
  pulls before it has read this contract has violated s1 and s3 without
  knowing."
- "Don't do anything other than this bootstrap and registration" -- a
  hard scope limit, taken literally. Nothing under agents/metis/ or
  scripts/ was executed, repaired, restarted or modified. No brief was
  generated. The two dormant loops stay stopped. Talos's queued
  all-seats question is recorded as METIS-14 with its provisional
  answer and is NOT posted.
- "except remind me what you did when you were active" -- answered in
  ARCHAEOLOGY_2026-09-11.md section 1, in two halves, with a
  correction: the seat the operator is likely remembering (the March
  paper-brief analyst) is not the one that was alive last week (the
  May portfolio reporter, dead 61 hours at the time of writing).

## Reading and diagnostic commands run on this pass (nothing mutating)

    git fetch origin
    git rev-parse origin/main            -> 363120e08665af062d40810183624fa23ed19698
    git worktree add <this worktree> -b metis/base-role-adopt-2026-09-11 363120e08
    git log --format='%h %aI %s' -- agents/metis
    git log -1 --format='%h %aI %s' --grep='auto: portfolio update'
    git log --format='%h %aI %s' -S'"observability"' --reverse -- docs/state.json
    git grep -ln '"observability"' -- . ':!roles' ':!docs'
    python  (read-only over agents/metis/briefs/*.md and docs/state.json;
             the brief-repetition measurement and the alarm-predicate
             evaluation in ARCHAEOLOGY_2026-09-11.md sections 2 and 3)
