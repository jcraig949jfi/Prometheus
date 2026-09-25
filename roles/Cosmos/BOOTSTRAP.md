# Cosmos BOOTSTRAP -- the entry file for a fresh session (read before anything else in roles/Cosmos/)

Currency: 2026-09-25T10:50Z. Written before an operator-requested context reset.

## 0. Boot (inherited mechanics, pointers only)
Base role s1 (roles/base-role/RESPONSIBILITIES.md): refuse the canonical checkout; work in the M2 worktree
D:/Prometheus-worktrees/cosmos-base-role; `python -m comms boot Cosmos --model <id>` with
EW_DB_HOST=192.168.1.202; `python -m comms sync Cosmos`; then this file, RESPONSIBILITIES.md, STATUS.md.

## 1. Where things stand (public facts)
- C0 (CWE qualification) CLOSED PERMANENTLY at af2af37f4. Record: roles/Cosmos/campaigns/
  (HANDOFF_2026-09-23.md, REVIEW_PACKET_CWE_2026-09-23.txt). Atlas harvest pending (ATLAS-37, #544/#558/#562).
- C3 (causal accessibility of past information) Session 1 COMPLETE. Public: the P1/P2 certificate v3
  (qualified), the D contract, the information ledger. Everything else is WITHHELD (s2).
- Holdout D: requested from Nestor on M1 (comms #561). Bellerophon's earlier request was withdrawn (#560).
  E reserved for Aether working from M4 only; not commissioned.
- Seat state: BLOCKED on D's seal. No methodological change is permitted before D (operator 2026-09-25:
  "freeze behavior, preserve the scars, and let the foreign world do the talking").

## 2. The withheld branch (READ THIS)
The C3 law, coordinates, visible substrates, results, substitution attacks, Session 1 review packet and
two operator notes exist ONLY on the LOCAL branch `cosmos/c3-s1-2026-09-24` in the M2 worktree above.
Its early head 0ecafed1... is hash-committed in roles/Cosmos/c3/INFO_LEDGER.md on main.
- To resume: `git switch cosmos/c3-s1-2026-09-24` in that worktree and read roles/Cosmos/c3/RESUME_WITHHELD.md
  (the exact next steps and how to read D).
- NEVER push that branch, and never merge it into a branch that is pushed, until D's seal commit is pushed
  by D's author AND is an ancestor of origin/main. Public edits are made on `cosmos/c3-public-2026-09-24`
  (branched from origin/main) and fast-forwarded to main.
- Do not paste withheld content into comms, main, or any public file.

## 3. The sequence after D seals (detail on the withheld branch)
1 publish the withheld branch (verify the committed head is an ancestor) -> 2 Harmonia audits ONLY the
frozen A/B/C coordinate construction and normalisation -> 3 on AUDIT_PASS freeze law, uncertainty,
translation into D-native measurements and one intervention, hash + push -> 4 spend D once ->
5 only then consider E (Aether/M4).

## 4. Where to check for news
`python -m comms sync Cosmos` (Nestor's seal report; Atlas on ATLAS-37); roles/Nestor/ on origin/main.
