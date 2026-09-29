# Holdout D2 v4 firewall re-audit: auditor-of-record verdict FAIL

- **Auditor of record:** Odysseus (ubu001), 2026-09-29, under MWO-0001.
- **Audited commit:** e6e482ae6 (Nestor #942). The c3_holdout_D2 package is unchanged on origin/main since then.
- **Scope:** the firewall layer only. No law, prediction or science content.
- **Protocol record:** NONE written.

## The run (Nestor's submission; no seat chose the reviewers)

| Task | what | worker / model | result |
|---|---|---|---|
| tsk-c69dc6012c70 | replica 1/2, audit.security.adversarial, fabric.runtime==0.2 | worker.ubu001, claude-opus-5-5 | **OVERALL: FAIL**: blocking B-1 (icacls), B-2 (allowlist.py runs unaudited repository code) |
| tsk-93bad7474ae7 | replica 2/2, same | worker.ubu001, claude-opus-5-5 (2nd attempt; the 1st was lost to DEF-ODY-011) | **OVERALL: FAIL**: blocking B-1 (icacls) |
| tsk-c889e48bc5f1 | selftest_protocol (script) | worker.ubu001.sci | selftest_pass true, hidden_set_or_key_touched false. The two Windows current-directory controls are `not_applicable_on_this_os` on the Linux fabric node. |
| tsk-ca86196f783b | selftest_D2 (script) | worker.ubu001.sci | selftest_pass true |

Evidence (sha256 prefix): replica1_final_text 9695b070, replica1_findings 9ba09623, replica2_final_text d9de2092,
replica2_findings d12345b3, selftest_protocol_output 653b58f0, selftest_D2_output e7f766a0.

## Adjudication

**The replicas AGREE: FAIL.**

1. **B-1: the v4 current-directory repair (F-CWD) covers git but not icacls. Blocks PASS.**
   - Both replicas find it independently. `custody.py:141` runs `icacls` by bare name inside the key-release
     process (confirmed by the auditor).
   - On M1 (Windows) the current directory is searched first. The project's own control records this:
     `SELFTEST_PROTOCOL.json:77`, `v4_CWD_control_cwd_git_exe_is_found: true`.
   - With branch protection off, one committed file at the repository root would run as the custodian account in
     the process that has just copied the key.
   - The fix the replicas name is to call it by absolute system path, or to use the Win32 API.
2. **B-2 (replica 1): `allowlist.py` runs `git` by bare name and imports working-tree `comms` code as the
   custodian.** It is the same class. Replica 2 grades the git part should-fix (S-4). It is carried as MUST-FIX
   together with B-1.
3. **S-1 (both replicas), MUST-FIX before any real run.**
   - A runner started through `entry.py` cannot complete: the predictor child cannot import the package.
   - The failure comes AFTER the one-time key release has been used up and recorded, which is irreversible for
     this spec_id. The declared ChildNotIsolated refusal also fires late.
   - No test runs the runner through `entry.py`.
4. **S1, root of trust for protocol records: still OPEN.** It is an operator decision (#925).

**Should-fix items in common:**
- `firewall-check` always runs the code committed on origin/main (not the audited code) with the secrets loaded;
- the key copy is left behind if the ACL step fails;
- the account name comes from the environment;
- `once_record_present` treats a git error as "no record";
- git grafts, shallow files and config are not neutralised.

The full lists are in the findings files.

**Holds (per replica 2):** F-GOV, F-FETCH, F-ONCE; F-GITENV as stated. The v3 blocking items P1/P2/P3 are
repaired according to both replicas.

## Coverage note (adoption evidence, not a D2 finding)

The fabric's script nodes are Linux. The Windows-specific controls are recorded as not applicable there, and the
replicas relied on M1's committed control output. Windows-behaviour checks of the D2 package need an M1 run: a
Windows fabric node does not exist in v0.2.

## What would change the verdict (v5)

1. Every executable the key-holding tools start (custody, allowlist, firewall-check, runner) is called by absolute
   path with a sanitised environment, and none of them imports working-tree code outside the audited set.
2. S-1: the runner completes through `entry.py` BEFORE the release is consumed. Check child importability and
   isolation before key release, and add an end-to-end self-test through `entry.py`.
3. S1: resolved by the operator's #925 choice.
