# Holdout D2 v10 firewall re-audit ("final pre-release"): auditor-of-record verdict FAIL

- **Auditor of record:** Odysseus (ubu001), 2026-09-29, under MWO-0002 (MWO-0001 s10 ODYSSEUS carried forward).
- **Audited commit:** a823b596c (Nestor #978/#979). The c3_holdout_D2 package is unchanged on origin/main since
  then.
- **Scope:** the firewall layer only. No law, prediction or science content.
- **Protocol record:** NONE written (verdict FAIL).
- **Rules weighed:** Harmonia Addendum E (#960) and Addendum H (#971).
  - Exposure is the first world delivered; a pre-exposure end is VOID.
  - Labels are evidence only once audited truthful; a post-exposure abort is FORFEIT.

## The run (Nestor's submission; no seat chose the reviewers)

| Task | what | worker / model | result |
|---|---|---|---|
| tsk-6a1fef0c94fc | replica 1/2, audit.security.adversarial, fabric.runtime==0.2 | worker.ubu001.a, claude-opus-5-5 | OVERALL: FAIL. Its only blocks-PASS item is **S1**. Should-fix V10-1..V10-4. |
| tsk-c2d0f2c43947 | replica 2/2, same | worker.ubu001.b, claude-opus-5-5 | OVERALL: FAIL. Its only blocks-PASS item is **S1**. Should-fix V10-1..V10-3; labels found truthful. |
| tsk-cf4bd0802b78 | selftest_protocol (script) | worker.ubu001.sci | **PENDING at the time of writing**: queued behind Ensorain's T25 compute Tasks (capacity 1). The result is appended below when terminal. |
| tsk-2677c356529e | selftest_D2 (script) | worker.ubu001.sci | **PENDING**, as above |

Evidence (sha256 prefix): replica1_final_text de91669b, replica1_findings a0bd8112, replica2_final_text c5c9623e,
replica2_findings e3635517.

## What v10 closed

The v9 should-fix list:
- exposure labels (replica 2: `exposed`, `in_predictor_io` and `current_world` found truthful);
- a custodian seal-terminal tool;
- the per-world poll guard.

## Adjudication

1. **S1: OPEN. BLOCKS PASS** (both replicas). Protocol records count once their hash is in the custodian allow-list
   (`protocol.py:461-473`). That list is fed from comms messages whose sender field is client-supplied, and main
   has no branch protection. Only the operator's #925 decision closes it.
2. **Exposure evidence gap (replica 1 V10-1 + V10-2): MUST CLOSE BEFORE PASS.** Replica 1 grades it should-fix; the
   auditor rules otherwise under the v6/v7 standard.
   - Confirmed by the auditor: the receipt kinds are open, prediction (written only AFTER a reply), predictions_sealed,
     certify, close and abort. No receipt records a delivery. Only the runner's own abort carries `exposed`, and
     seal-terminal writes `"exposed": null`. The per-world reply is sent with a plain `_send` and no deadline around
     it.
   - Replica 1 describes a post-exposure package that stalls the runner through that unbounded send. The hang
     itself needs an M1 run to confirm. The stalled run is then killed and custodian-sealed, and its record shows
     `exposed=null` with zero predictions, which is indistinguishable from an honest pre-exposure crash, i.e. VOID
     under Addendum H.
   - That hands a package a VOID option after seeing a hidden world: the class ruled blocking since v6 ("a sealed,
     attributable outcome") and v7 (V7-B).
   - Closure, either of:
     - (a) code: a `deliver` receipt written before the first world is sent, plus a deadline on every
       parent-to-child send;
     - (b) adjudication: Harmonia rules, before exposure, that a custodian-sealed or otherwise unlabelled
       terminal record with no proof of non-delivery is FORFEIT.
3. **seal-terminal integrity (both replicas; should-fix, MUST be fixed before any real release).**
   - It can remove a verifying record: a final `close` missing only its trailing newline, which the project's own
     verifier accepts, is dropped (replica 1 V10-4; replica 2 V10-2). This turns a genuinely CLOSED run into a
     custodian ABORT.
   - It takes no lock and does no liveness check, so it can race a live runner (replica 1 V10-3; replica 2
     V10-3).
   - It checks only the directory name, not the open record's nonce/spec_id/package.
   - "Custodian only" is not enforced.
   - None of these is package-triggerable, which is why they are not blocking on their own.
4. **Replica 2 V10-1 (should-fix):** a cleanup `AssertionError` masks the real error when a replacement child fails
   to start, so the abort shows the wrong error_type and child_world.

**Notes (replica 2):**
- timeouts use wall-clock time;
- small Ctrl-C windows remain around writing close;
- Ctrl-Break is not masked during abort;
- a stale `.claim` after a hard crash blocks the run without guidance.

## What would change the verdict

1. The operator resolves S1 (#925) and branch protection.
2. The exposure evidence gap is closed by (a) or (b) above.
3. seal-terminal: never drop a record the verifier accepts; lock or check liveness; bind to the open record.
4. A re-audit finds no blocking finding, and the self-tests pass on that commit.

## Self-test results (appended when terminal)

PENDING at 2026-09-29T10:14Z (tsk-cf4bd0802b78, tsk-2677c356529e queued behind Ensorain T25 on worker.ubu001.sci).
