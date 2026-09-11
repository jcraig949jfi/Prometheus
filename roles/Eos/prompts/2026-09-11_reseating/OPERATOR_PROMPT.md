# Operator prompt, 2026-09-11, verbatim

Committed verbatim as received in chat. The hash of this file is in
MANIFEST.md beside it. No edits: the text below is the operator's, and
where it differs from any summary of it, it wins (base s1 step 2).

    You're @agents\eos\ You were an agent back in May but haven't been
    seated since.  Bootstrap and then create a role for yourself in the
    @roles\ directory like the others.  Adhere to the base-role concept.
    Pull the latest from the repo first as that's where you'll see the
    new roles and requirements.  Don't do anything other than this
    bootstrap and registration except remind me what you did when you
    were active

## How the seat read it

- "Bootstrap" -- the base role's boot sequence, in order, from a
  worktree that is not the canonical checkout.
- "create a role for yourself in the roles directory like the others" --
  roles/Eos/, entry file RESPONSIBILITIES.md carrying the inheritance
  banner, plus the artifacts the sibling adoption passes established:
  archaeology, backlog, calibration ledger, status, journal, this
  prompt with its manifest, and the residue archive.
- "Adhere to the base-role concept" -- inherit, do not restate; the
  seat file adds to the base and may not contradict it.
- "Pull the latest from the repo first" -- done once at the session's
  start in the canonical checkout (a read-only no-op: already up to
  date). All subsequent transitions used explicit fetch, per D-23 s3.
- "Don't do anything other than this bootstrap and registration" --
  read as an execution ban on the seat's science. Nothing under
  agents/eos/ was run. The only commands executed were comms sync and
  boot, two read-only database probes, hash comparisons over the
  seat's own archived residue, and git.
- "except remind me what you did when you were active" -- answered in
  roles/Eos/ARCHAEOLOGY_2026-09-11.md and summarised in chat.
