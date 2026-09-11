# Operator prompt, 2026-09-11 -- Hermes adoption

Delivered in chat, not through comms (the seat was not addressable: comms
boot refuses a seat with no roles/<Seat>/ directory, which is what this
prompt asked for). Recorded verbatim below; the only edits are the ASCII
substitutions the base role's section 4 requires, noted after the block.

----------------------------------------------------------------------

You're @agents\hermes\ You were an agent back in May but haven't been
seated since.  Bootstrap and then create a role for yourself in the
@roles\ directory like the others.  Adhere to the base-role concept.
Pull the latest from the repo first as that's where you'll see the new
roles and requirements.  Don't do anything other than this bootstrap and
registration except remind me what you did when you were active

----------------------------------------------------------------------

ASCII substitutions: none were needed; the prompt was already pure
ASCII. Line breaks are the operator's.

Scope this prompt sets, and how it was read:

- "Bootstrap" -- the base role's boot sequence, steps 1 to 8.
- "create a role for yourself in the roles directory like the others" --
  roles/Hermes with the artifact set the 2026-09-11 adoption passes
  established (entry file with the inheritance banner, STATUS, BACKLOG
  in the 2026-09-10 schema, archaeology of the old queue, calibration
  ledger, journal, adoption receipt, this prompt with its manifest).
- "Adhere to the base-role concept" -- inheritance over duplication: the
  seat file adds to the base role and restates none of its mechanics.
- "Pull the latest" -- read as FETCH. WORKING_CONTRACT s3 forbids
  `git pull`; the intent (see the new roles and requirements before
  writing anything) is satisfied by fetch plus an explicit base SHA.
  One `git pull` was nevertheless run before the contract was read; it
  was a no-op and is recorded in calibration/CALIBRATION.md row 8.
- "Don't do anything other than this bootstrap and registration" -- a
  hard scope limit, and the reason this pass executed nothing: no mail
  sent, no loop started or stopped, no producer revived, no backlog item
  begun. Findings were measured by reading, not by running.
- "except remind me what you did when you were active" -- answered in
  roles/Hermes/ARCHAEOLOGY_2026-09-11.md section A and relayed in chat.
