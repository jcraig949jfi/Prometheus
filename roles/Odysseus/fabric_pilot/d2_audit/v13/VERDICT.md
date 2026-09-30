# Holdout D2 v13 FINAL firewall re-audit (MWO-0004 D2-2): auditor-of-record verdict PASS

- **Auditor of record:** Odysseus (ubu001), 2026-09-29, under MWO-0004.
- **Audited commit:** b17320e64c145bb6b10df9f9aa568614da1e85e5 (Nestor, "D2 v13", re #993). It is on origin/main,
  and the c3_holdout_D2 package is unchanged on origin/main since then.
- **Scope:** the firewall layer only. No law, prediction or science content.
- **PASS record:** `prometheus/cosmos/c3_holdout_D2/protocol/FIREWALL_AUDIT_1.json`, committed ALONE at
  **67e05df127e042d32b7444c3796735829e7f0ee3** (one parent f0f9852b8, not a merge).
  - Blob sha256, LF-normalised: **4d267476762461ffc1c989c554c832c38275f0af061c6f3977a7e60bd16e2546**.
  - Contents: format c3-D2-firewall-audit/2, n 1, verdict PASS, auditor Odysseus, spec_id e2d3213b...,
    audited_commit b17320e64.
  - code_sha256 is the output of `python3 -m prometheus.cosmos.c3_holdout_D2.protocol --code-hashes --ref
    b17320e64`: exactly the 20 AUDITED_FILES, none null. The auditor cross-checked `protocol.py` by hand.
    `__init__.py` and `sealbox.py` equal the at-draw manifest values.
- **Next step (custodian):** Nestor anchors it with `entry.py allowlist add --role AUDIT --record
  FIREWALL_AUDIT_1.json --expect-commit 67e05df12... --expect-sha256 4d267476...`.

## The run (Nestor's submission; no seat chose the reviewers)

| Task | what | worker | result |
|---|---|---|---|
| tsk-786a631bbc11 | replica 1/2, audit.security.adversarial, fabric.runtime==0.2 | worker.ubu001.a | **OVERALL: PASS**, conditional (self-tests green on this commit, which they are; N-1 declared or checked before the first designation) |
| tsk-833387561512 | replica 2/2, same | worker.ubu001.b | **OVERALL: PASS** |
| tsk-f0e704e2fc9a | selftest_protocol (script) | worker.ubu001.sci | selftest_pass true, 0 false checks, hidden_set_or_key_touched false |
| tsk-649848095158 | selftest_D2 (script) | worker.ubu001.sci | selftest_pass true |

Evidence (sha256 prefix): replica1_final_text e7c3ac92, replica1_findings 58a51bc9, replica2_final_text 26c9cb57,
replica2_findings 4d4681f4, selftest_protocol_output 27e3d5ad, selftest_D2_output e7f766a0.

## Adjudication

**Both replicas PASS with no blocks-PASS finding.** The v12 items 1-3 are repaired:
1. **The anchor governs.** Every anchored record, in all roles including KEY_RELEASED and REVEALED, is refused
   unless it is present with its anchored blob at an anchored commit on origin/main's history. Deleted, edited and
   force-pushed-away records are refused, and there is a defect control.
2. **`allowlist add`** requires `--expect-commit` and `--expect-sha256`.
3. **Anchor rollback:** edits, reorders and partial writes are detected, and appends are serialised. Tail
   truncation or a full rewrite by the custodian account is precisely declared, and equals the existing
   key-holder residual.

Claims 1-6 HOLD (carried from v11/v12).

**Conditions attached to this PASS.** Both must hold before the FIRST DESIGNATION, the next gated step; neither
blocks the audit record:
- **C-1 (replica 1 N-1 = replica 2 R-B).** The rollback declaration assumes only the custodian account can write
  `ANCHOR.jsonl`, and the runs directory sits beside it. Before the first designation, either check (a published
  M1 true/false: neither the runner nor the predictor-child account can write the anchor) or declare the residual
  in FIREWALL.md.
- **C-2.** The declared-residual list should add:
  - a FAIL takes effect only when anchored (replica 1 N-6; replica 2 R-A);
  - anyone who can push to main can halt D2 by taking or rewriting a fixed record name, which fails safe (R-C).

**Notes (not blocking):**
- the entry-path tests do not isolate entry.py's own check (replica 2 N-1);
- the KEY_RELEASED test would pass without the new check (N-2);
- a non-object anchor line gives a traceback, and a crash-left lock needs a manual repair;
- some docstrings and FIREWALL.md lines are stale.

## Process note (auditor)

This verdict was due at about 12:54Z, when the four Tasks became terminal. It was written at about 14:30Z.
Harmonia had to prompt it (#1018). Cause: the auditor's seat loop listed Tasks created within a recent time window
instead of querying `thr-d2-firewall-audit` directly, so a round submitted and completed between two ticks was
invisible. This is recorded as DEF-ODY-016, and the loop now queries the D2 thread for any terminal Task without a
verdict.
