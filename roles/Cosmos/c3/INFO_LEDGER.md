# C3 information ledger for foreign holdouts (directive 2026-09-24 s17)

Currency: 2026-09-28T08:55Z. Every fact about a foreign holdout that reaches Cosmos is entered here
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

## D (development holdout) -- SEALED 2026-09-25 by Nestor (M1); original seal NOT yet on main; opaque successor REQUESTED 2026-09-28
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
| 2026-09-25 | comms #596 | Nestor[m1-7438ee6f] accepts #561 (operator ruling 09-25, parallel lane); M1 worktree nestor-c3-d, branch nestor/c3-holdout-d-2026-09-25 cut from origin/main 815cdb32a; reads only D_CONTRACT s7 inputs | KNOWN_TO_COSMOS_BEFORE_FREEZE |
| 2026-09-25 | comms #599 | SEALED: sha256(sealed_spec_D.json) = ae4479c6125a29cfa53624013c7f4ba5d322205c2ef442ce7371d5fd812e57ac; sealed commit a56ef778722b35bd425c59f9647194a8927477dd on origin/nestor/c3-holdout-d-2026-09-25; package prometheus/cosmos/c3_holdout_D/ (broker-gated); 128 hidden worlds (count only); M1, Python 3.12.10, numpy 2.2.6; native parameter NAMES/UNITS/RANGES (L, D, v, p_decay, kappa, q, sigma, x_in, d_patch, w_patch, V, k) and knob API names; selftest booleans all as required, pytest 15 passed. No outcomes | KNOWN_TO_COSMOS_BEFORE_FREEZE |
| 2026-09-26 | this repo (Cosmos M2 check) | commitment VERIFIED: git blob a56ef7787:prometheus/cosmos/c3_holdout_D/sealed_spec_D.json hashes to ae4479c6...57ac (hashed only, contents not opened by Cosmos). Branch head 5e05307b2 adds only roles/Nestor/C3_HOLDOUT_D_REPORT.md. Seal commit IS pushed; it is NOT an ancestor of origin/main (main 51638e216). Cosmos has read no D source, world list or outcome | -- |
| 2026-09-26 | operator (to Nestor, direct) | operator elevates #561 to Nestor's immediate priority; Nestor's own campaign to pause for D. Recorded as given; the seal above had already been pushed on 09-25, so this prompt post-dates it. Not relayed through Cosmos | -- |
| 2026-09-26 | comms #737 | Bellerophon confirms #550 closed on its side: nothing built or read | -- |
| 2026-09-28 | operator directive (roles/Cosmos/prompts/2026-09-28_operator_research_structure/) | D1: the pushed branch + hash is NOT sufficient, so Nestor is to merge seal a56ef7787 into main (original commitment kept unchanged). D4/H5: the original hidden set is readable in plaintext and is treated as EXPOSED; Nestor is to build an OPAQUE successor (fresh hidden set, ciphertext + salted commitment, key off M2, independent firewall check). Cosmos predictions are frozen only after that, and Cosmos never runs D | -- |
| 2026-09-28 | comms #788 | Cosmos -> Nestor: the two requests above, verbatim in REQUEST_TO_NESTOR_D_SEAL.md; asks for public commitments only, no D information | -- |
| 2026-09-30 | operator C3 disposition (roles/Cosmos/prompts/2026-09-30_operator_c3_disposition/) | C3 CLOSED / KILLED BEFORE HOLDOUT; D2 SEALED / UNREAD / UNSPENT, reserved for a possible future compatible claim; any later use of D2 needs a separate compatibility determination (contract, leakage, freeze-without-inspection, protocol match) | -- |
| 2026-09-30 13:42:15Z-13:44:13Z (between commit receipts c9f8aff17 and 9bdfd85e1; the first entry said "~14:10Z", an estimate, corrected the same day) | this repo (Cosmos M2, INCIDENT, self-reported) | during a public-file leak scan, `git grep -E <coordinate-name regex> -- roles/Cosmos prometheus/cosmos` in worktree cosmos-base-role also searched the tracked D2 CIPHERTEXT prometheus/cosmos/c3_holdout_D2/hidden_D2.enc. Output was the single line "Binary file ... matches". No bytes were displayed, and nothing was decrypted (the key is off M2). Information obtained: the file path (already public on main) and a regex hit on ciphertext (content-free). Cosmos judges it NO INFORMATION about D2 and does not declare D2 compromised. The ruling belongs to the D2 custodian/auditor (Nestor, Harmonia), who are told on comms. Prevention: from now on, every Cosmos search excludes prometheus/cosmos/c3_holdout_D*/ | REPORTED_FOR_RULING |
| 2026-09-30 | comms #1110 (Harmonia) + operator C4 review s10 | RULING on the incident: NO_INFORMATION (Harmonia Addendum R, ca7d354f4; ciphertext f75ba333 verified unchanged since seal 95b31a30d). Operator provisional reading: CONTACT_WITH_PACKAGE_PATH / NO CONTENT REVEALED (not "no contact"). The custodian (Nestor, #1105) has not replied yet. D2: SEALED / UNREAD / UNSPENT / COMPATIBILITY PENDING. No C4 decision depends on D2 | RULED_NO_INFORMATION |
| 2026-09-30 | operator Q-A ruling (prompts/2026-09-30_operator_c4_review2_publication/) | (1) Harmonia NO_INFORMATION ruling on the incident ACCEPTED for the record; D2 SEALED / UNREAD / UNSPENT; D2 compatibility is NOT assessed until C4 has an earned claim. (2) Publication of the withheld C3 branch (head e73e5eb26) is AUTHORIZED AFTER the foreign C4 visible family is committed with an immutable provenance receipt, for C4 visible-development use only, subject to checks V1-V5 (c3/PUBLICATION_PLAN.md). Dry run on this date: V1 PASS, V2 PASS, V3 PASS, V4 = 23 added / 1 modified (the calibration LEDGER, union at merge), V5 PASS. NOT YET PUBLISHED | -- |

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
