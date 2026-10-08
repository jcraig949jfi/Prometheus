# Cosmos BOOTSTRAP -- the entry file for a fresh session (read before anything else in roles/Cosmos/)

Currency: 2026-10-08 (v0.3). Governing texts, newest first:
- operator 48H autonomous campaign 2026-10-08: roles/Cosmos/prompts/2026-10-08_operator_48h_campaign/DIRECTIVE_VERBATIM.md
  (live campaign state: roles/Cosmos/campaigns/48H_2026-10-08/CAMPAIGN_STATE.json; resume from its next_action)
- operator C4 review 2026-09-30: roles/Cosmos/prompts/2026-09-30_operator_c4_review/DIRECTIVE_VERBATIM.md
- operator C3 disposition 2026-09-30: roles/Cosmos/prompts/2026-09-30_operator_c3_disposition/DIRECTIVE_VERBATIM.md
- CWO-2026-09-30B finish-in-place (ops/fleet/CWO_2026-09-30B_FINISH_IN_PLACE.md, blob sha256 e62cb5ee...)
- CWO-2026-09-30 fleet activation (ops/fleet/CWO_2026-09-30_FLEET_ACTIVATION.md, blob sha256 ab93f646...)
- MWO-0004 (ops/work_orders/CURRENT.md); the research-structure directive 2026-09-28 (Cosmos = LAW FOUNDRY)
Live state of record: roles/Cosmos/WORK_STATE.json. This file says how to resume; it does not track progress.

## 0. Boot (inherited mechanics, pointers only)
Base role s1 (roles/base-role/RESPONSIBILITIES.md): refuse the canonical checkout. HOST: ubu003 since 2026-10-06
(moved from M2; do not restart Cosmos on M2). Worktree /home/jcraig/Prometheus-worktrees/cosmos-base-role; python is
~/venvs/prometheus/bin/python (system python3 lacks psycopg2); `EW_DB_HOST=192.168.1.202 <python> -m comms boot Cosmos
--model <id>`, then `... -m comms sync Cosmos`; then this file, WORK_STATE.json, STATUS.md. COSMOS_HOME defaults to
~/cosmos_runs (= /home/jcraig/cosmos_runs, copied from M2 C:/Users/James/cosmos_runs).
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
- 2026-10-08: foreign family DONE (Theseus theseus_sediment 79dc4c4b8, verified); C3 Session 1 PUBLISHED on main
  (merge d75fb45ef, V1-V5 PASS). The C4 queue below is superseded by the 48H directive.
- C4 (new campaign, successor to C3; thread T-C4 thr-cac8c079f216): DESIGN v0.2 (c4/DESIGN_C4.md), revised
  after the operator review. It is under two independent reviews (brief c4/REVIEW_BRIEF_v0.2.md) and a
  foreign visible family is commissioned (c4/VISIBLE_FAMILY_CONTRACT.md). F-0002 and the build are NOT
  authorized until the reviews are reconciled and the operator authorizes. No holdout is authorized.
- D2 incident (2026-09-30 ciphertext grep): Harmonia ruled NO_INFORMATION (#1110). D2 compatibility is
  pending and no C4 decision depends on it.

## 2. The withheld material (READ THIS)
The C3 law, coordinates, visible substrates, results, substitution attacks, Session 1 review packet and
operator notes exist ONLY on LOCAL branches, now in the ubu003 store (moved 2026-10-06 by git bundle over scp, never pushed;
M2 keeps a fallback copy). A local pre-push hook refuses both unless COSMOS_PUBLISH_C3=1:
- `cosmos/c3-s1-2026-09-24` (head e73e5eb26; early head 0ecafed1 hash-committed in c3/INFO_LEDGER.md and
  FREEZES F-0000). Preserve EXACTLY: no new commits.
- `cosmos/c3-autopsy-2026-09-30` (branched from e73e5eb26): the WITHHELD technical autopsy. Local only.
Rules (2026-10-08: c3-s1 is now PUBLISHED; the rules below still bind the AUTOPSY branch): NEVER push either branch or merge it into a pushed branch. Publication needs an EXPLICIT operator
trigger. (The 2026-09-28 conditions, seal on main and successor commitment on main, are already met,
so the trigger is now the only condition.) Do not paste withheld content into comms, main or any public
file. The public autopsy (research/reviews/AUTOPSY_C3_PUBLIC_2026-09-30.md) carries only abstract
failure modes and hashes.

## 3. Queue (mirrored in WORK_STATE.json)
Wait for Aporia's reviewer and author assignments -> reconcile the reviews (c4/reviews/RECONCILIATION_v0.2.md)
-> report to the operator -> on authorization: F-0002 freeze, then the instrument build with planted
calibration. Open for the operator: Q-A (publish the C3 withheld branch after the foreign family is
committed) and Q-B (build authorization).

## 4. Research program
roles/Cosmos/research/ (README, THREADS, RESULTS, GRAVEYARD, FREEZES, PRE_RESULT_REVIEW). The other
threads (T-A1 .. T-I1) stay OPEN. Under CWO-B they are not started without an assignment.

## 5. Where to check for news
`python -m comms sync Cosmos`; ops/fleet/QUEUE.json (Aporia's view); roles/Nestor/ and roles/Harmonia/ for D2
custody. No standing watch.
