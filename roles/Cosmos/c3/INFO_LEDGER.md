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
Residual risk: the M2 worktree files are readable on disk by a seat on M2; D_CONTRACT s7 forbids reading
them and requires an attestation.

## D (development holdout) -- requested 2026-09-24 (comms), not yet sealed
Author seat: Bellerophon (directive s3 recommendation), request prompts/2026-09-24_c3_D_request/.
| date | channel | fact | class |
|---|---|---|---|
| 2026-09-24 | this repo | nothing about D exists yet; D's author has been sent only the contract | -- |

## E (final adjudicator) -- not yet commissioned
Author seat: (not requested; directive recommends Aether; only after D and final freeze).
| date | channel | fact | class |
|---|---|---|---|

## Standing withholding list (never sent to D/E authors; directive s3)
candidate law; coefficients; latent coordinates; expected phase boundary; A/B/C implementations and
results; surviving grammar expressions; known failure regions; the intended intervention; any hint.
