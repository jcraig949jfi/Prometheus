# Holdout D2 v2 firewall re-audit: auditor-of-record verdict FAIL

- **Auditor of record:** Odysseus (ubu001), 2026-09-29. Recorded under MWO-0001 (ODYSSEUS section: "adjudicate
  the existing D2 Fabric re-audit").
- **Audited commit:** f4cde414d74eb3cfa4a3cd50014b4c04ee1b2604 (Nestor #860/#862).
- **Scope:** the firewall layer only. No law, prediction or science content was read or is recorded here.
- **Protocol record:** NONE written under `prometheus/cosmos/c3_holdout_D2/protocol/`. v2 permits recording a
  FAIL, but I told Nestor (#895) I would consult before doing so. This file and the comms pointer carry the
  verdict. Nestor decides whether a FAIL record is also committed.

## How the re-audit ran (the loop the operator specified; no seat chose the reviewers)

| Task | what | worker | result |
|---|---|---|---|
| tsk-6989ee1b86bd | replica 1/2, skill audit.security.adversarial | worker.ubu001 att-ab2a11c2ec85 | **OVERALL: PASS**, 0 blocking, 2 should-fix (F-COMMS, F-ACCT) |
| tsk-b43d70a88ce7 | replica 2/2, same skill | worker.ubu001 att-909dc9fd2546 | **OVERALL: FAIL**, 2 blocking (B1, B2). Its full findings file was not written (the worker reports its output was stopped mid-write); only its final summary exists. |
| tsk-a07e46edb489 | selftest_protocol (script, sci node) | worker.ubu001.sci | selftest_pass true, hidden_set_or_key_touched false |
| tsk-65f1de3d76f7 | selftest_D2 (script, sci node) | worker.ubu001.sci | selftest_pass true, hidden_set_or_key_touched false |

- Nestor submitted all four at 2026-09-28 21:16Z, and all were terminal by 21:28Z.
- Evidence copies are in this directory. Their sha256 prefixes match the fabric artifacts: replica1_final_text
  df7f0da4, replica1_findings 482e7774, replica2_final_text 38359c96, selftest outputs 004d9ab7 and e7f766a0.
- **Limitation of both replicas:** they ran on runtime 3ba6fcc0c, which predates the D12 rogit repair. Both
  report that git and Python were unavailable, so every history-dependent or hash-dependent sub-claim is
  CANNOT-VERIFY in their reports.

## Adjudication

The replicas disagree, so the auditor of record decides.

**Decisive finding: authentication of the S1 allow-list (R2 B2, R1 F-COMMS). BLOCKS PASS.**
- Both replicas identify the same fact. The v2 repair for S1 (records must be allow-listed by the custodian from
  a comms message sent by Odysseus) authenticates that message only by the comms `sender` field.
- The field is supplied by the posting client (`comms/__main__.py` `--from`; `comms/api.py` post), and seats share
  the database credentials. I confirm this from my own use: every comms post names its own sender.
- Branch protection on main is OFF (Nestor #860, boolean 3 = FALSE).
- R1 set the condition for escalating to blocks-PASS as "if Cosmos can post as another seat". Under the current
  comms design, any seat can set any sender, so R1's condition is met.
- Consequence: the S1 allow-list does not establish who authored a governing audit record. The order gate therefore
  does not yet provide the assurance claimed for it.
- This is the same class as v1 S1 (records unauthenticated). The v2 repair moved the trust onto a field that is not
  authenticated.

**R2 B1 (import control around the verified entry point): OPEN, not independently verified by the auditor this
round.**
- R2 asserts that the F1 repair verifies the bytes of the audited files but does not fully control which code the
  interpreter loads.
- R1 examined the same area and found it adequate ("loaded-closure").
- I have not completed an independent verification. The re-audit must settle it.
- The direction R2 names is: run in isolated interpreter mode without bytecode writing, and refuse any import
  source outside the audited tree.

**Should-fix items raised by one replica** (not adjudicated individually; to be addressed or explicitly accepted
in v3):
- **R2:** `firewall_check.py` passes secret-derived search strings as command-line arguments on M1, which are
  visible to process listing. It fixes nothing about the order gate, but conflicts with the module's own stated
  rule.
- **R2:** `RESULT_SEAL.json` is not allow-listed, and a later unauthenticated FAIL record can supersede the
  governing audit. Both are denial-of-service paths.
- **R2:** the "once only" property rests on an editable custody log.
- **R2:** the production isolation probe includes a file the same-account child can open, so the real run
  fail-closes with ChildNotIsolated unless the child runs under a separate account. That is safe, but it should be
  intentional and documented.
- **R2:** the receipt chain has no key, and the same-account child can write it.
- **R1:** the designated-account check uses an environment-derived user name (defence in depth only).
- **Both:** the plaintext-length note N1 is already declared.
- **Both:** `allowlist.py` and other custodian-run tools import code outside `AUDITED_FILES`.

**Claims that both replicas found to HOLD in code at f4cde414d:**
- opacity (1);
- controlled reveal, in its gating logic (4);
- predictor isolation, in its three stated narrow properties (5);
- draw integrity in code (6).

Claim 2 is CANNOT-VERIFY by both replicas, whose workers had no history access. Nestor's all-history scan is
reported CLEAN (#867).

## What would change this verdict (for v3)

1. The allow-list is authenticated by something a seat cannot forge by naming itself: for example, the custodian
   confirming the auditor's record sha256 through a channel not writable by other seats, or signed commits.
   Branch protection on main would also remove the push path the finding relies on. That is an operator setting.
2. B1 resolved: either repaired as R2 describes, or shown inapplicable by a replica able to run the entry point.
3. The re-audit runs on the post-D12 runtime (`fabric.runtime==0.2`, which includes rogit) so that the history
   and hash sub-claims can be checked rather than marked CANNOT-VERIFY. Nestor should add
   `--cap fabric.runtime==0.2` to the submit.
