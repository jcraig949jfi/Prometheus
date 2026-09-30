# Cosmos BOOTSTRAP -- the entry file for a fresh session (read before anything else in roles/Cosmos/)

Currency: 2026-09-30. Governing texts, newest first:
- operator C3 disposition 2026-09-30: roles/Cosmos/prompts/2026-09-30_operator_c3_disposition/DIRECTIVE_VERBATIM.md
- CWO-2026-09-30B finish-in-place (ops/fleet/CWO_2026-09-30B_FINISH_IN_PLACE.md, blob sha256 e62cb5ee...)
- CWO-2026-09-30 fleet activation (ops/fleet/CWO_2026-09-30_FLEET_ACTIVATION.md, blob sha256 ab93f646...)
- MWO-0004 (ops/work_orders/CURRENT.md); the research-structure directive 2026-09-28 (Cosmos = LAW FOUNDRY)
Live state of record: roles/Cosmos/WORK_STATE.json. This file says how to resume; it does not track progress.

## 0. Boot (inherited mechanics, pointers only)
Base role s1 (roles/base-role/RESPONSIBILITIES.md): refuse the canonical checkout; work in the M2 worktree
D:/Prometheus-worktrees/cosmos-base-role; `python -m comms boot Cosmos --model <id>` with
EW_DB_HOST=192.168.1.202; `python -m comms sync Cosmos`; then this file, WORK_STATE.json, STATUS.md.
The worktree is normally on the PUBLIC branch `cosmos/c3-public-2026-09-24`. Fast-forward it from
origin/main (never `git pull`). `python -m prometheus.cosmos.research_check` must PASS before any
research-workspace commit. Under CWO-B a finished item is reported to Aporia (completion message, s11);
the seat does not self-promote beyond what the operator has authorized.

## 1. Where things stand (public facts)
- C0 (CWE qualification) CLOSED PERMANENTLY at af2af37f4 (roles/Cosmos/campaigns/).
- C3 (causal accessibility of past information) is CLOSED / KILLED BEFORE HOLDOUT (operator 2026-09-30).
  The coordinate-layer audit returned REJECT (research/reviews/COORD_AUDIT_C3_2026-09-29.md). The main
  cross-substrate coordinate restated the P2 certificate, and the others carried family identity. A
  zero-parameter certificate rule reproduced 104/120 classes. The preliminary law is GRAVEYARD G-0006.
  It is a SCAR: it must not be revived, re-tuned or repaired.
- Holdout D2 (Nestor): SEALED / UNREAD / UNSPENT, reserved for a possible future compatible claim. Its
  governing firewall audit PASSED (FIREWALL_AUDIT_1 @67e05df12). Cosmos never reads, runs or spends it.
  The original D (seal a56ef7787) is treated as EXPOSED (operator 2026-09-28 D4).
  E is reserved for Aether from M4 only and is not commissioned.
- C4 (new campaign, successor to C3; thread T-C4 thr-cac8c079f216) is AUTHORIZED FOR DESIGN ONLY. It asks
  what upstream physical properties of a world make history reliably and causally accessible. It must
  pass gates S0-S4 of the 2026-09-30 directive on visible worlds. No holdout, old or new, is authorized.

## 2. The withheld material (READ THIS)
The C3 law, coordinates, visible substrates, results, substitution attacks, Session 1 review packet and
operator notes exist ONLY on LOCAL branches in the M2 worktree store:
- `cosmos/c3-s1-2026-09-24` (head e73e5eb26; early head 0ecafed1 hash-committed in c3/INFO_LEDGER.md and
  FREEZES F-0000). Preserve EXACTLY: no new commits.
- `cosmos/c3-autopsy-2026-09-30` (branched from e73e5eb26): the WITHHELD technical autopsy. Local only.
Rules: NEVER push either branch or merge it into a pushed branch. Publication needs an EXPLICIT operator
trigger. (The 2026-09-28 conditions, seal on main and successor commitment on main, are already met,
so the trigger is now the only condition.) Do not paste withheld content into comms, main or any public
file. The public autopsy (research/reviews/AUTOPSY_C3_PUBLIC_2026-09-30.md) carries only abstract
failure modes and hashes.

## 3. Queue (operator 2026-09-30; mirrored in WORK_STATE.json)
1 state reconciliation -> 2 C3 autopsy (withheld + public) -> 3 documentation -> 4 C4 protocol DESIGN
-> 5 visible-data baseline analysis for C4 gate S0. Then send the completion message to Aporia and wait.
STOP conditions for C4 are in the directive; "no successor law earned" is an acceptable result.
D2 eligibility for C4 is decided separately, only after C4 passes its visible-world gates.

## 4. Research program
roles/Cosmos/research/ (README, THREADS, RESULTS, GRAVEYARD, FREEZES, PRE_RESULT_REVIEW). The other
threads (T-A1 .. T-I1) stay OPEN. Under CWO-B they are not started without an assignment.

## 5. Where to check for news
`python -m comms sync Cosmos`; ops/fleet/QUEUE.json (Aporia's view); roles/Nestor/ and roles/Harmonia/ for D2
custody. No standing watch.
