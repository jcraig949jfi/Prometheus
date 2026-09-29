# Holdout D2 v3 firewall re-audit: auditor-of-record verdict FAIL

- **Auditor of record:** Odysseus (ubu001), 2026-09-29, under MWO-0001.
- **Audited commit:** 742243972 (Nestor #935). The c3_holdout_D2 package is unchanged on origin/main since then.
- **Scope:** the firewall layer only. No law, prediction or science content.
- **Protocol record:** NONE written.

## The run (Nestor's submission; no seat chose the reviewers)

| Task | what | worker / model | result |
|---|---|---|---|
| tsk-d0454ab252b9 | replica 1/2, audit.security.adversarial, **fabric.runtime==0.2** (rogit) | worker.ubu001, claude-opus-5-5 | **OVERALL: FAIL**: blocking P1, P2 (import control), P3 (entry deadlock), S1 open |
| tsk-ddfc5156be0d | replica 2/2, same | worker.ubu001, claude-opus-5-5 | **OVERALL: FAIL**: blocking B1-a, B1-b (import control); the same deadlock as should-fix S-1 |
| tsk-1674e7e0fdc8 | selftest_D2 (script) | worker.ubu001.sci | selftest_pass true, hidden_set_or_key_touched false |
| tsk-9913738c30c2 | selftest_protocol (script) | worker.ubu001.sci | selftest_pass true, hidden_set_or_key_touched false |

- The key-holder all-history scan is reported CLEAN (Nestor #937).
- Both replicas had read-only git this time (DEF-ODY-002 resolved). One replica checked public hashes with
  `sha256sum`: all match. The files that must not change since the seal are unchanged. The sealed files have one
  content version, added only by 95b31a30d, the pinned seal commit.
- Evidence (sha256 prefix): replica1_final_text 0b29bfef, replica1_findings 19f95098, replica2_final_text
  e1422427, replica2_findings c0fd3553, selftest outputs e7f766a0 and c5c8637a.

## Adjudication

**The replicas AGREE: FAIL.**

1. **B1, import control around `entry.py`: BROKEN, blocks PASS.** Both replicas independently find it, in the same
   two places:
   - the unisolated first stage imports standard modules before any check, with the script directory first on
     the import path (replica 1 P1; replica 2 B1-a);
   - inside the verified key-holding process, the repository root comes first on the import path, and the guard
     and loaded-module check cover only `prometheus.*` (replica 1 P2; replica 2 B1-b).

   In both, one additional ordinary file on main would load unverified code into a process that can read the
   key. Branch protection is off. The replicas reasoned from documented interpreter behaviour. They did not run
   it, because workers cannot execute code, and I did not run it either.
2. **Protocol deadlock: CONFIRMED by the auditor.** `entry.py:33` FIXED = {PREDICTION_COMMITMENT,
   RUNNER_DESIGNATION, RESULT_SEAL} omits `KEY_RELEASED.json` and `REVEALED.json`, which `protocol.py:63-64`
   defines as v3 records. Once the key-release record is committed, `entry.py` refuses every later run, reveal and
   evidence step. Replica 1 grades this blocks-PASS; replica 2 grades it should-fix. It is a correctness failure
   of the gate, not a leak, so I record it as MUST-FIX before a PASS can be meaningful. It does not change the
   verdict on its own.
3. **S1, root of trust for protocol records: still OPEN.** It is an operator decision (Nestor #925). Both replicas
   note that it is unchanged.

**Should-fix items in common:**
- `entry.py` picks the highest-numbered audit before filtering by the allow-list (denial of service);
- a failed `git fetch` is ignored and a stale reference is checked;
- custodian-run tools (`firewall_check`, `allowlist`, `result-seal`, `evidence`) run outside `entry.py`;
- the predictor child always shares the runner's account, so a real run always refuses (fail closed, but it cannot
  complete as coded);
- `--dest` accepts any path.

The full lists, with file:line evidence, are in the findings files.

**Holds:** claims 1, 4 (gate logic), 5 (narrow properties) and 6. Claim 2 holds on the repository side, and the
key-holder scan is CLEAN. The DEF-HARM-D2-001 repair holds.

## What would change the verdict (v4)

1. **Import control.** Start in isolated mode, refuse any unaudited file in the package directory and at the
   repository root that could shadow a module, and bind or refuse whatever the key-holding process loads outside
   `prometheus.*`. The replicas name the specific shapes.
2. **Record names.** The allowed record set matches the protocol's (KEY_RELEASED, REVEALED), and an end-to-end
   self-test runs through `entry.py`.
3. **S1.** Resolved by the operator's #925 choice.
