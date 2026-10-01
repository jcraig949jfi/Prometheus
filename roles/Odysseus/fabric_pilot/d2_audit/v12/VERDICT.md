# Holdout D2 v12 firewall re-audit (MWO-0004 D2-2, the bounded re-audit): auditor-of-record verdict FAIL

- **Auditor of record:** Odysseus (ubu001), 2026-09-29, under MWO-0004.
- **Audited commit:** b0763ebaa (Nestor #992). The c3_holdout_D2 package is unchanged on origin/main since then.
- **Scope:** the firewall layer only. No law, prediction or science content.
- **Protocol record:** NONE written (verdict FAIL).
- **Governing order:** MWO-0004 (P = 25a486d44; blob 925660b2...99df).
  - D2-1: #925 is resolved by the order itself. The root of trust is Git object identity, plus immutable blob
    hashes, plus an append-only M1 anchor. "A mismatch fails closed." No branch protection is required.
  - D2-2: one bounded re-audit. If it fails on an ordinary implementation defect, one final bounded repair and one
    final re-audit are allowed. After that: PASS, or HOLD.
- **Rules weighed:** Harmonia Addenda E/H/J.

## The run (Nestor's submission; no seat chose the reviewers)

| Task | what | worker / model | result |
|---|---|---|---|
| tsk-e33a0c5600d7 | replica 1/2, audit.security.adversarial, fabric.runtime==0.2 | worker.ubu001.b, claude-opus-5-5 | **OVERALL: PASS**, conditional: self-tests green, and SF-1..SF-3 fixed or declared before anchoring |
| tsk-314baabdb741 | replica 2/2, same | worker.ubu001.a, claude-opus-5-5 | **OVERALL: FAIL**: blocking V12-1 |
| tsk-87e6fef17919 | selftest_protocol (script) | worker.ubu001.sci2 | selftest_pass true, 0 false checks, hidden_set_or_key_touched false |
| tsk-35aae2ef2123 | selftest_D2 (script) | worker.ubu001.sci | selftest_pass true |

Evidence (sha256 prefix): replica1_final_text 6fde2fe9, replica1_findings acb6f7df, replica2_final_text 0e3c0934,
replica2_findings c83325fc, selftest_protocol_output c521ae9b, selftest_D2_output e7f766a0.

## What v12 does right (both replicas)

- D2-1 is implemented as an M1 anchor, and the comms-sender allow-list is removed.
- The anchor holds identifiers and hashes only.
- Claims 1-6 HOLD, as recorded through v11; `runner.py` is unchanged since v11.
- Before a gated step, the re-verification of the AUDIT, COMMITMENT, DESIGNATION and RESULT_SEAL records runs
  after the fetch.
- Both self-tests pass.

## Adjudication (the replicas disagree; the auditor rules)

**V12-1 (replica 2): an anchored record that no longer verifies is SKIPPED, not refused. CONFIRMED by the auditor.
BLOCKS PASS.**
- `protocol.check_gates` builds the audit set from the files present in the tree at origin/main (`_proto_tree`)
  and then filters them through `_is_allowlisted`. `entry.verify` does the same.
- An anchored audit record that has been deleted from the tree, or whose blob no longer matches its anchor entry,
  therefore simply drops out of consideration.
- With an anchored PASS (FIREWALL_AUDIT_1) followed by an anchored FAIL (FIREWALL_AUDIT_2), an ordinary commit that
  deletes or edits FIREWALL_AUDIT_2 makes the PASS govern again, and the gates open.
- This contradicts MWO-0004 D2-1 ("verify ... the record at that commit still has the confirmed blob hash ... A
  mismatch fails closed") and the protocol's own S2 ("a later FAIL supersedes a PASS").
- Replica 1 did not examine this path. Its PASS does not refute it.
- Under D2-2 this is an ordinary implementation defect: ONE final bounded repair and ONE final re-audit are
  allowed.

**Also in scope for that same final repair (D2-1 conformance and integrity; the replicas agree on the substance):**
- **V12-3 = SF-3: KEY_RELEASED.json and REVEALED.json are not anchored.** D2-1 applies to "each protocol record
  participating in D2". A force-push removing them goes undetected by the gates, and only the unchained custody
  log still refuses a second release.
- **V12-4 = SF-1: `allowlist add` anchors by file name only**, with no expected commit or sha256. Whoever lands a
  fixed-name record first gets it anchored. Add `--expect-commit` and `--expect-sha256`, and have the auditor's
  posted commit checked against them.
- **V12-2 = SF-2: anchor rollback** (truncating the tail) is undetected. Either publish each new chain head (for
  example in the next record commit) or declare the residual precisely. FIREWALL.md currently overstates it.
- **Notes:**
  - concurrent anchor appends can corrupt the chain (fail-closed lock-up);
  - a malformed anchor line produces a traceback instead of a clean refusal (still before the key read);
  - the anchor file's permissions on M1 cannot be seen from the repository.

## What would change the verdict (the FINAL round under MWO-0004 D2-2)

1. Build the governing audit set from the ANCHOR, not the tree. Refuse if any anchored record (all roles,
   including KEY_RELEASED and REVEALED) is missing, altered, or no longer on origin/main's history. Unanchored
   files are ignored as before. Apply the same rule in `entry.py`. Add self-tests for: a deleted anchored FAIL, an
   edited anchored FAIL, and a force-push past an anchored record.
2. `allowlist add` takes an expected commit and sha256.
3. Anchor rollback is detectable, or precisely declared.
4. The final re-audit (both replicas, `fabric.runtime==0.2`) finds no blocking finding. Then the auditor commits
   `FIREWALL_AUDIT_1.json` (format c3-D2-firewall-audit/2) in ONE commit, per the brief, and posts the commit. If
   it fails, D2 goes to HOLD with the remaining defect recorded (MWO-0004 D2-2). No further rounds.
