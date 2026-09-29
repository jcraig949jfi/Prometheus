# Holdout D2 v8 firewall re-audit: auditor-of-record verdict FAIL

- **Auditor of record:** Odysseus (ubu001), 2026-09-29, under MWO-0002 (MWO-0001 s10 ODYSSEUS carried forward).
- **Audited commit:** a02b9b20c (Nestor #968). The c3_holdout_D2 package is unchanged on origin/main since then.
- **Scope:** the firewall layer only. No law, prediction or science content.
- **Protocol record:** NONE written.
- **Rule weighed:** Harmonia's pre-exposure adjudication rule (#960; Addendum E @9f6abdce6): a consumed release
  without a result seal is FORFEIT; an infrastructure crash is VOID.

## The run (Nestor's submission; no seat chose the reviewers)

| Task | what | worker / model | result |
|---|---|---|---|
| tsk-40522d68e5fc | replica 1/2, audit.security.adversarial, fabric.runtime==0.2 | worker.ubu001.a, claude-opus-5-5 | **OVERALL: FAIL**: one blocking finding (V8-1, wrong-key spend) |
| tsk-f3fcbe5f914b | replica 2/2, same | worker.ubu001.b, claude-opus-5-5 | **OVERALL: FAIL**: one blocking finding (V8-1, interrupted record write) |
| tsk-3c95bd906b18 | selftest_protocol (script) | worker.ubu001.sci | selftest_pass true, 0 false checks |
| tsk-a27c34185a7d | selftest_D2 (script) | worker.ubu001.sci | selftest_pass true |

- Every Attempt succeeded on its first try. This is the first re-audit without a lost Attempt since the
  DEF-ODY-011 stop-gap (distinct worker names .a/.b).
- Evidence (sha256 prefix): replica1_final_text 114959c1, replica1_findings 22cd1337, replica2_final_text
  c7520955, replica2_findings 6b6e934e, selftest_protocol_output 8031e386, selftest_D2_output e7f766a0.

## What v8 fixed

Both replicas report the v7 blockers repaired:
- V7-1: the consumption marker is now written atomically with a pre-built open record;
- V7-B: a closed pipe counts as a per-world crash, and the abort carries attribution;
- V7-A: the stand-in is now read-probed.

Both self-tests pass.

## Adjudication

Both replicas FAIL, each on a different blocking finding in the same class the auditor has ruled blocking since
v5: a recoverable error that consumes the one-time release without a meaningful outcome.

1. **Replica 1 V8-1: a wrong, but well-formed, key file spends the release. CONFIRMED by the auditor. BLOCKS
   PASS.**
   - In `FirewallRun.open()` the key is read with a format/length check only. Then the consumption marker and open
     record appear, and the released key file is deleted. Only after that does `sealbox.decrypt` prove the key is
     the D2 key.
   - `custody.py` copies the key to the destination without a test decryption.
   - An operator passing a well-formed wrong `--key` file therefore spends D2 (sealed as an abort, i.e. VOID) with
     no package code ever run, and the real released key is left on disk.
   - This is a recoverable argument error that consumes the release. The v5-v7 standard applies.
   - Fix (replica 1): decrypt and run the manifest consistency checks BEFORE the marker is written, or have custody
     test-decrypt before release. Add a self-test with a well-formed wrong key.
2. **Replica 2 V8-1: an interrupted record write leaves a chain that cannot be sealed. Blocking class; OPEN, not
   independently verified by the auditor this round.**
   - Replica 2 describes an interruption during a record's write/fsync, including a console control event the
     child can send, which v8 itself declares. It leaves a partial or unterminated chain that result-seal cannot
     seal.
   - It is the same class as V7-1 (unsealable spend), which was ruled blocking "whatever the likelihood". v9 must
     either repair it (for example truncate to the pre-write size on failure, or have `abort()` re-read the chain
     from disk) or show it does not apply, with a self-test that fails fsync after a record write.

**Should-fix items the replicas agree on (both relevant to Addendum E attribution):**
- **V8-2:** the abort's `child_exitcode` is always null, because the worker handle is cleared before the exit code
  is read. The self-test checks only that the field exists.
- **V8-3:** after a per-world crash, the fresh child's isolation probe runs outside the per-world guard. If it
  fails, the abort names the previous world with `in_predictor_io=false`, so a package-caused restart failure would
  read as infrastructure (VOID).

**Notes:**
- A Windows `poll` timing gap could turn a per-world failure into a whole-run abort (plausible, unverified; M1
  can settle it).
- A failed RESULT.json write after close has no rebuild tool.
- An aborted run can leave the released key copy on disk.
- The staged-package readability by the child is not checked before the key read (replica 2 V8-6).

**S1 (root of trust for protocol records) and branch protection:** still OPEN, operator decisions (#925; MWO-0002
s8).

## What would change the verdict (v9)

1. The key is proven correct (decrypt plus manifest consistency) before the consumption marker exists. Custody
   test-decrypts before release. Add a self-test with a well-formed wrong key.
2. No interrupted write can leave an unsealable chain: repair it or show it inapplicable, with a self-test.
3. Abort attribution is truthful: the real `child_exitcode`, and the restart probe runs inside the per-world
   guard.
4. S1: resolved by the operator's #925 choice.
