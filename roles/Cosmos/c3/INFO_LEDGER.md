# C3 information ledger for foreign holdouts (directive 2026-09-24 s17)

Currency: 2026-09-24T07:08Z. Every fact about a foreign holdout that reaches Cosmos is entered here
with a date, the channel, and the class. Accidental leakage declares the holdout COMPROMISED; it is
not rationalised away.

Classes: KNOWN_TO_COSMOS_BEFORE_FREEZE | WITHHELD_UNTIL_REVEAL | REVEALED_AT_ADJUDICATION |
LEARNED_POST_HOLDOUT

## Engineered barrier (2026-09-24 ~07:55Z)
Everything on origin/main is readable by every seat, so Cosmos keeps the withheld material UNPUBLISHED
until D's seal is pushed: prometheus/cosmos/c3/{substrates,geometry,maps,law,attack}.py, tests/test_c3.py,
roles/Cosmos/c3/{S1_PREREG_LAW,S1_RESULT}.md, roles/Cosmos/c3/runs/maps_s1/. It lives on the local branch
cosmos/c3-s1-2026-09-24 (M2 worktree cosmos-base-role), committed and hash-committed on main (below).
Published to main now: the contract (D_CONTRACT.md), the P1/P2 definitions and reference certificate
(task.py, system.py, probe.py, certify.py, calib.py, gate.py, S1_PREREG_P1P2_GATE.md), this ledger, the
directive and the D request. Harmonia's coordinate audit runs AFTER D's seal is pushed (its report would
otherwise publish the coordinates) and BEFORE D is adjudicated (directive s3 item 6 / s10).
Residual risk (stated exactly): every M2 worktree shares the canonical clone's .git object store, so the
withheld local branch ref is visible to any seat working on M2 (git show <branch>:<path>), and the
worktree files are readable on disk. For a seat off M2 the barrier is real (nothing is on origin); for
an M2 seat it is HONOR + ATTESTATION (D_CONTRACT s7 forbids reading it and requires an attestation).
Resolved for D by moving its author off M2 (see below): for an M1 author the barrier is technical.

## D (development holdout) -- REASSIGNED 2026-09-24 to Nestor (M1), not yet sealed
Operator decision 2026-09-24: honor + attestation is not acceptable when avoidable; D authorship moves
OFF M2. Request to Bellerophon (comms #550) WITHDRAWN -- Bellerophon's last sync (03:34Z) preceded the
request (07:51Z), so it never received it. New author: Nestor, all of whose instances run on SKULLPORT
(M1), a separate clone that cannot see M2-local git objects. Request: prompts/2026-09-24_c3_D_reassign/.
E (final) is to be kept available for Aether (M4); Aether also has an M2 instance, so E's author must
work from M4 only.
| date | channel | fact | class |
|---|---|---|---|
| 2026-09-24 | this repo | nothing about D exists yet; D's author has been sent only the contract | -- |
| 2026-09-24 | comms | D reassigned to Nestor (M1); Bellerophon request withdrawn before it was read | -- |

## E (final adjudicator) -- not yet commissioned
Author seat: (not requested; directive recommends Aether; only after D and final freeze).
| date | channel | fact | class |
|---|---|---|---|

## Standing withholding list (never sent to D/E authors; directive s3)
candidate law; coefficients; latent coordinates; expected phase boundary; A/B/C implementations and
results; surviving grammar expressions; known failure regions; the intended intervention; any hint.

## Hash commitment of the withheld material (published 2026-09-24)
Local branch cosmos/c3-s1-2026-09-24 head 0ecafed159f9bc9756baefd55ec37fd75b83b822 (git commit id; SHA-1 over the whole tree and history).
When D's seal is pushed, this exact commit is published; anyone can check that it is unchanged.
