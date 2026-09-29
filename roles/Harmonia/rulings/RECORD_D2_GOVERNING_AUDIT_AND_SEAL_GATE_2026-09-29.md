# Holdout D2: governing firewall audit recorded, and a SEAL-gate defect (Harmonia record)

Harmonia[m2-475d761f], 2026-09-29, under MWO-0001 (HARMONIA section: "preserve the D2 custody/order guarantees
already committed; receive and record the independent D2 audit evidence when it lands"; s12 incident rule).
Base: origin/main 60f2ea1f32293f05d2d2bb667f8f5bd21083eefd. MWO blob sha256 007054ad...88f3, commit 7e4c09f2c.

Scope: the firewall/order layer only. Harmonia read no hidden-set content, key, salt or plaintext, and holds none.
Nothing is released, revealed, designated or sealed by this record. No D2 code or protocol record is edited.

## 1. The governing audit (recorded)

| Item | Value |
|---|---|
| Auditor of record | Odysseus[ubu001] (designated by the operator; Nestor #829) |
| Verdict file | `roles/Odysseus/fabric_pilot/d2_audit/v2/VERDICT.md`, blob sha256 `aa2c904c7cf69956c8de282a7cf1707d253c62dabe19faa12755cec0b8e59d64` (LF, as committed) |
| Verdict commit | f8eedbbce0d28e05908ceaed36abef03177fd953 (2026-09-29 03:09Z) |
| Audited code | f4cde414d74eb3cfa4a3cd50014b4c04ee1b2604 |
| **Governing verdict** | **FAIL** (replicas split PASS / FAIL; adjudicated FAIL on S1 allow-list authentication resting on the client-supplied comms `sender` field, with branch protection off; B1 import control recorded OPEN) |
| Protocol record | **None.** No `prometheus/cosmos/c3_holdout_D2/protocol/FIREWALL_AUDIT_<n>.json` exists on origin/main. Odysseus left the choice of a FAIL record to Nestor (custodian). |

Harmonia's reading of the consequence: with no governing PASS, the AUDIT gate cannot pass, so nothing after it
(COMMITMENT, DESIGNATION, RESULT_SEAL, key release, reveal, evidence bundle) is permitted. This is the correct,
fail-closed state, and Harmonia preserves it.

**Evidence bundle:** `evidence.py` refuses unless `check_gates(..., "RESULT_SEAL")` passes. It cannot be built now, and it
must not be. When a governing audit record exists, the bundle carries every `FIREWALL_AUDIT_<n>.json` version (the
FAIL history included), so this record is the durable pointer until then.

## 2. Measured gate status on origin/main (executed, public)

`python -m prometheus.cosmos.c3_holdout_D2.protocol` (the module's own public status; reads no secrets), from a
clean worktree at 60f2ea1f3:

    {"SEAL": "RecordRewritten: prometheus/cosmos/c3_holdout_D2/hidden_D2.enc is touched by a merge commit;
              records may not arrive or change through merges"}

The gate stops at **SEAL**, before AUDIT is even evaluated.

## 3. DEFECT DEF-HARM-D2-001: the SEAL gate cannot pass on the real history

**Exposed by:** Harmonia's MWO-0001 D2 custody duty (recording the governing audit); first executed status check.

**Expected:** the sealed ciphertext and manifest, unchanged since the seal commit 95b31a30d (pinned `SEAL_COMMIT`),
pass SEAL on origin/main.

**Observed:** `_added_once` (protocol.py) runs `git log --full-history -- <path>` and refuses if ANY listed commit is a
merge (`npar > 1`). `--full-history` lists every merge whose result differs from at least one parent. That includes
every ordinary integration merge where one side did not yet have the file. On origin/main:

| Commit | Parents | Blob of hidden_D2.enc per parent | Merge result blob |
|---|---|---|---|
| 95b31a30d (seal, 1 parent) | 7c018d92b | added | 10c7b6007de5... |
| ebe1307ea "Merge origin/main into D2 seal branch" | 95b31a30d, c7a71efbf | 10c7b600 / ABSENT | 10c7b600 |
| 85b198a5b (Artemis branch integration) | d78413835, 7720539d4 | ABSENT / 10c7b600 | 10c7b600 |
| e5b95744f (Nestor branch integration) | f443bcef0, e66f57208 | ABSENT / 10c7b600 | 10c7b600 |

MANIFEST_D2.json shows the same pattern (same four commits). **The content never changed:** every commit carries blob
10c7b6007de575d70b1ee10b83208612e0cd97b9, and the ciphertext hashes to
f75ba333efea147a351c3364aa7eb690a4970546bb717c99fcf86809b5fdfc9f, the committed value Nestor gave in #796.

**All three merges are ancestors of the audited commit f4cde414d**, so SEAL was already unpassable there. The first
of them (ebe1307ea) is the seal branch's own integration into main, so **no ref descended from origin/main can ever
pass SEAL under the current rule.**

**Why nobody saw it:**
- the v1 audit recommended "use --full-history (and refuse any merge commit that touches a record path)";
- the self-tests build synthetic repositories where the only merge is the F4 attack fixture;
- both v2 replicas ran without git (CANNOT-VERIFY on every history claim).

**Direction:** fails CLOSED. It blocks the protocol; it does not leak. It is not a custody breach. It does mean the
enforced order cannot complete as committed, which is a D2 readiness blocker. **Science is not blocked** (nothing may run
before a PASS audit anyway). **Safety is not reduced.**

**What a repair must keep (the F4 guarantee) while fixing this, offered to the owners, not applied:** refuse only a
merge whose result blob for a record path differs from the blob it had at the seal (or first-record) commit. Put
differently, every commit in the full history that touches the path must carry the one sealed blob, and exactly one
non-merge commit adds it. A merge that carries the unchanged blob from one side is not a rewrite. A replacement through a
merge is still caught, because the merge result's blob would differ. This is D2 code in AUDITED_FILES: any change is
Nestor's to make and needs a fresh governing audit (v3). Harmonia edits no D2 file.

**Add to Odysseus's v3 list:** the re-audit should execute `protocol.status` on the real origin/main history (the
post-D12 runtime has git), not only on synthetic repositories.

## 4. What Harmonia did not do

- No release, reveal, key access, designation, result seal or protocol record.
- No edit to any file under `prometheus/cosmos/c3_holdout_D2/`.
- Nothing forwarded to Cosmos about hidden content (there is none in this record; the defect is about Git history only).
- No adjudication of D2 science. Harmonia remains the adjudicator after a result seal, from the `evidence.py` bundle.

## 5. Status for the next MWO review

D2 = **BLOCKED (fail-closed)** on two independent grounds:
1. the governing audit is FAIL (v3 needed: allow-list authentication, B1, runtime with git);
2. DEF-HARM-D2-001: the SEAL gate is unpassable on the real history (a code repair plus a re-audit are needed).

Operator decision possibly required: branch protection on main (Odysseus's v3 item 1 names it as an operator setting).

## Addendum A (2026-09-29, same instance): DEF-HARM-D2-001 CLOSED, verified by execution

- Nestor's D2 v3 (742243972; comms #935) redefines "added once" as one blob across the full history (each merge diffed
  against each parent), exactly one non-merge add, and no non-merge modification, deletion or rename.
- **Executed** on origin/main 7c12fb175 (clean worktree, fast-forwarded):
  `python -m prometheus.cosmos.c3_holdout_D2.protocol` -> `SEAL: PASS`, `AUDIT: AuditMissing (no allow-listed
  FIREWALL_AUDIT_<n>.json)`. The ciphertext still hashes to f75ba333; its only non-merge commit is still 95b31a30d.
- **F4 kept.** Harmonia's own probes of `protocol._added_once` on throwaway repositories outside every worktree (no
  broker mode, no secrets):
  - an integration merge carrying the sealed blob unchanged: **PASS**;
  - delete, re-add with forged content, then merge: **RecordRewritten**;
  - a merge whose conflict resolution replaces the record's content: **RecordRewritten** ("3 different contents").
- Not run: `selftest_protocol` (67 checks + 4 defect controls), which is broker-only (`COSMOS_BROKER=1`). Harmonia does
  not assume that role on M2. Nestor reports it PASS.
- **D2 remains BLOCKED (fail-closed):**
  1. no allow-listed governing audit (the v3 Fabric re-audit is running; Odysseus adjudicates);
  2. S1, the root of trust for record authentication, is an open operator decision (#925).
  Harmonia records the next governing verdict when it lands, and releases nothing on a comms message alone.

## Addendum B (2026-09-29): governing v3 audit recorded, FAIL

| Item | Value |
|---|---|
| Verdict file | `roles/Odysseus/fabric_pilot/d2_audit/v3/VERDICT.md`, blob sha256 `e254a12156f23b229c24f7ff745f66f052837433ef388a10c0392ce70e071fb2` |
| Verdict commit | 2d7517600a314af7f177b5bb97408ff43c77a29a (2026-09-29 04:03Z) |
| Audited code | 742243972 (Nestor #935; the package is unchanged on origin/main since, last touched by 05211e20b) |
| **Governing verdict** | **FAIL.** The replicas agree: B1 import control around `entry.py` is broken in two places. The auditor confirmed an entry record-name deadlock (MUST-FIX). S1 is still OPEN (operator #925). |
| Protocol record | None. `prometheus/cosmos/c3_holdout_D2/protocol/` does not exist on origin/main. |

- **Harmonia check (by reading code at origin/main):**
  - `entry.py` `FIXED = {PREDICTION_COMMITMENT, RUNNER_DESIGNATION, RESULT_SEAL}`;
  - `protocol.py` `FIXED_RECORDS` also contains `KEY_RELEASED.json` and `REVEALED.json`.
  - The deadlock claim is **confirmed as stated.**
- **Not executed by anyone:** the verdict says the B1 import-path findings were reasoned from documented interpreter
  behaviour (workers cannot execute code, and the auditor did not run them). This is recorded so it is not later read as
  a measured result. A v4 re-audit should demonstrate the shadowing exploit and its refusal by execution.
- The DEF-HARM-D2-001 repair **holds** (both replicas; Addendum A).
- **D2 remains BLOCKED, fail-closed:**
  1. v4 is needed (import control; record names with an end-to-end self-test through `entry.py`);
  2. S1 (#925).
  Nothing released, revealed or built.

## Addendum C (2026-09-29): governing v4 audit recorded, FAIL

| Item | Value |
|---|---|
| Verdict file | `roles/Odysseus/fabric_pilot/d2_audit/v4/VERDICT.md`, blob sha256 `a33dd8cbbfd44e76a052c644409bcd92046defcaa9e6c250c123b603074c5b81` |
| Verdict commit | d3600b21e1fd9986d1f87258b811fd6b1b71bbfd (2026-09-29 05:04Z) |
| Audited code | e6e482ae6 (Nestor #942). Harmonia checked: `git diff e6e482ae6 origin/main -- prometheus/cosmos/c3_holdout_D2` is empty, and e6e482ae6 is on main. |
| **Governing verdict** | **FAIL.** The replicas agree. B-1: `icacls` is run by bare name in the key-release process. B-2: `allowlist.py` runs `git` by bare name and imports working-tree `comms` as the custodian. S-1: a runner started through `entry.py` cannot complete, and fails only AFTER the one-time key release is consumed. S1 still OPEN (#925). |
| Protocol record | None. |

- **Harmonia check (by reading code):**
  - `custody.py` lines 139-142 run `subprocess.run(["icacls", ...])` by bare name under `os.name == "nt"`, and take `me` from
    `os.environ["USERNAME"]`. **B-1 is confirmed as stated.**
- **Custody note, in Harmonia's own lane:** S-1 is the most serious item from the custody side. A failure that fires after
  the irreversible key release would burn the one release this spec_id allows. **Harmonia will not treat any v5 PASS as
  sufficient for release unless the end-to-end run through `entry.py` has been shown to complete BEFORE release** (v5 item
  2), by execution, on M1.
- The coverage note stands: Windows-specific behaviour was not executed on the (Linux) fabric nodes.
- **D2 remains BLOCKED, fail-closed:** v5 needed; S1 (#925). Nothing released, revealed or built.

## Addendum D (2026-09-29): governing v5 audit recorded, FAIL

| Item | Value |
|---|---|
| Verdict file | `roles/Odysseus/fabric_pilot/d2_audit/v5/VERDICT.md`, blob sha256 `11112c1f512b1ec884bbd7e125e07ee1ba3ac5c9262e18032a1d05d505069586` |
| Verdict commit | 01ac0fedf4da752edbb3b6094924825146aca11b (2026-09-29 06:08Z) |
| Audited code | 57c809387 (Nestor #949). Harmonia checked: the package is identical on origin/main. |
| **Governing verdict** | **FAIL.** BP-1/F1 (both replicas): the one-time key release is consumed before the package is validated. `selftest_protocol` FAILS at the audited commit (`v4_DEST_key_acl_restricted`, 3 of 3 attempts). S1 still OPEN, and widened: allowlist.py takes its database host from committed config. |
| Protocol record | None. |

- **Harmonia check (by reading code):**
  - `runner.py` line 607 reads the key and line 609 deletes it; `load_package` (hash, members, AST audit) runs only at
    line 641.
  - The optional `preflight()` at line 606 precedes the key read, but it does not validate the package.
  - **BP-1 is confirmed as stated.**
- **This is the failure named in Addendum C's custody condition** (written after v4, before v5 existed): "no release on
  any PASS unless end-to-end completion through `entry.py` is shown to complete BEFORE release, by execution, on M1". The
  condition stands unchanged for v6, and it is stricter than v6 item 1: a self-test proving that a refused package does
  not consume the release is necessary; an executed end-to-end run on M1 before release is also required.
- `selftest_protocol` failing at the audited commit means the package's own instrument is red. A PASS on a red self-test
  would be recorded by Harmonia as NOT GOVERNING until the failure is explained or fixed (v6 item 2).
- **D2 remains BLOCKED, fail-closed:** v6 needed; S1 (#925). Nothing released, revealed or built.

## Addendum E (2026-09-29): governing v6 audit recorded, FAIL; Harmonia adjudication position on voided evaluations

| Item | Value |
|---|---|
| Verdict file | `roles/Odysseus/fabric_pilot/d2_audit/v6/VERDICT.md`, blob sha256 `d7695a8b32ac9d385928dac83e5e2febb849069967af6fd5fd96ba1bb8b024b9` |
| Verdict commit | 7567a018ba9511abde613ec197ef32be4a2e07e9 (2026-09-29 06:52Z) |
| Audited code | 7c7b0b836 (Nestor #958). Harmonia checked: the package is identical on origin/main. |
| **Governing verdict** | **FAIL.** The replicas agree. (1) Extraction happens after the key read. (2) The receipts probe runs after the key read. (3) **A package can void an evaluation after seeing the hidden worlds** (a deliberate parent crash during PREDICT, so there is no seal and no result). `selftest_protocol` is red (`v6_account_sid_equality`). S1 still OPEN. |
| Protocol record | None. |

- **Harmonia check (by reading code):**
  - `runner.py`: `validate_package()` at line 609, then `preflight()` at 611, then the key read at 612 and the delete at
    614, then `load_package(..., self.out / "package", ...)`, the extraction, at 646.
  - **Item (1) is confirmed.** The v5 BP-1 validation fix holds.
- **Harmonia adjudication position on (3), stated now, before any exposure and independent of how v7 repairs it:**
  1. A D2 attempt that consumed the key release (a committed KEY_RELEASED record exists) is an **evaluation of record**.
  2. If it ends without a result seal, for any cause attributable to the package or to the predictor side, Harmonia's
     adjudication records it as **FORFEIT (not passed)**, never as "no data".
  3. A later attempt under a new spec_id is adjudicated only with every earlier consumed attempt disclosed beside it.
  4. Infrastructure crashes (power, disk, out of memory not caused by the package) are recorded as **VOID (infrastructure)**
     with their evidence. Whether a VOID may be retried is the protocol's declared crash-after-release policy (v7 item 3).
     Harmonia does not invent it.
  - Reason: without this, the adjudicated result is subject to optional stopping by the predicted party, which is the
    selection this holdout exists to prevent.
  - This is Harmonia's reading rule as adjudicator. It changes no D2 code, hypothesis or endpoint. The operator may
    overrule it **before** any key release. After a release it binds.
- **D2 remains BLOCKED, fail-closed:** v7 needed; S1 (#925). Nothing released, revealed or built.

## Addendum F (2026-09-29, before any exposure): Addendum E aligned with the D2 v7 terminal states

Nestor's v7 (e4efb487e, #962) introduces:
- PROTOCOL_ERROR and CERTIFY_ERROR, recorded per world;
- a terminal `abort` receipt with RESULT ABORTED, result-sealable;
- `receipts.jsonl` as the consumption marker;
- crash-after-release as an EXPLICIT RESIDUAL (no resume, no second release; D2 spent).

Addendum E is read against these states as follows. **This clarifies Addendum E; it widens nothing.**

1. **Exposure point = the `open` receipt** (the package may meet the hidden worlds only after it). A release after which
   no `open` receipt exists (bad key, crash before open) is **VOID (pre-exposure)**. The package saw nothing, so there is no
   optional-stopping risk. D2 is still spent under v7's once-only release; Harmonia records that fact, not a result.
2. **After `open`:**
   - a sealed normal RESULT is adjudicated on its content;
   - per-world PROTOCOL_ERROR / CERTIFY_ERROR count as **failed worlds** for that world (not dropped from the denominator);
   - a sealed **RESULT ABORTED is FORFEIT** unless its abort receipt carries evidence that the cause lay outside the
     package's control (for example host power loss). The burden of that evidence is on the run record, not on the
     adjudicator. A MemoryError, a timeout or a pipe failure the package could have induced is FORFEIT.
3. **No terminal record after `open`** (a crash that left no abort/close receipt) = evaluation of record, adjudicated
   **FORFEIT** under the same burden rule. v7 declares that D2 is then spent.
4. The adjudication bundle must show every consumed attempt (receipts files present) for this spec_id and any later
   spec_id. That is Addendum E item 3, unchanged.

As before: the operator may overrule before any key release; after a release this binds.

## Addendum G (2026-09-29): governing v7 audit recorded, FAIL; how Addendum F bears on V7-B

| Item | Value |
|---|---|
| Verdict file | `roles/Odysseus/fabric_pilot/d2_audit/v7/VERDICT.md`, blob sha256 `3cc28628d337c3cda8b0f3666e6d2d6ade9b84ea1486d618e8c96f07078bf352` |
| Verdict commit | 8efddb4b70b13bf6b8a77acc3c24195a34fcf132 (2026-09-29 08:00Z) |
| Audited code | e4efb487e (Nestor #962). Harmonia checked: the package is identical on origin/main. |
| **Governing verdict** | **FAIL.** V7-1: an unsealable spend (the key read happens before the `open` record exists). V7-B: a package-initiated end is unattributed. V7-A: a probe gap, OPEN. S1 still OPEN. **Both self-tests PASS** (the first time since v4). |

- **Harmonia check (by reading code):**
  - `runner.py` `open()`: key read at line 677, then `Receipts(..., create=True)` at 679, then `append("open", ...)` at 681.
  - **V7-1 is confirmed as stated.** A failure between 677 and 681 leaves a consumed release with no sealable record.
    Neither VOID nor FORFEIT can be recorded, and Harmonia cannot adjudicate a state the chain cannot seal.
- **V7-B and Addendum F:**
  - The audit weighed Addendum E (#960). Addendum F (6da0d5b5f, #965) was pushed at about 07:58Z, while the re-audit was
    already running on e4efb487e. Under F, a sealed ABORTED after `open` is **FORFEIT unless the record evidences a
    cause outside the package's control**, so an unattributed abort **cannot** be recorded as VOID.
  - V7-B's optional-stopping path is therefore closed **at the adjudication layer** by F.
  - What V7-B still costs is the opposite error: a genuine infrastructure failure after `open` would be scored FORFEIT,
    because the record cannot prove otherwise.
  - Attribution (v8 item 2) remains **desirable for fairness to the predictor**; under F it is no longer required for
    integrity.
  - The auditor's severity ruling is the auditor's. Harmonia records this interaction and does not overrule it.
- V7-F (package-induced resource pressure that looks like an infrastructure OOM): under F it is FORFEIT unless evidenced
  otherwise. The burden sits where F placed it.
- **D2 remains BLOCKED, fail-closed:** v8 needed (V7-1 at minimum); S1 (#925). Nothing released, revealed or built.

## Addendum H (2026-09-29): governing v8 audit recorded, FAIL; two pre-exposure clarifications of Addendum F

| Item | Value |
|---|---|
| Verdict file | `roles/Odysseus/fabric_pilot/d2_audit/v8/VERDICT.md`, blob sha256 `5ac26fc7a8ee5cc365458a47afde26839e66e6e261b11a6c7daba9e3f3711ecb` |
| Verdict commit | bea18a398a685bd565acd27583f4a1f666cf24d3 (2026-09-29 08:35Z) |
| Audited code | a02b9b20c (Nestor #968). Harmonia checked: the package is identical on origin/main. |
| **Governing verdict** | **FAIL.** V8-1 (replica 1): a wrong but well-formed key spends the release, CONFIRMED. V8-1 (replica 2): an interrupted record write leaves an unsealable chain, OPEN. Should-fix V8-2 (`child_exitcode` always null) and V8-3 (a restart-probe failure is labelled `in_predictor_io=false`). S1 OPEN. Self-tests PASS. v7 blockers repaired. |

- **Harmonia check (by reading code):**
  - `runner.py` `open()`: `read_hex_file` (format and length only) -> `Receipts.create_with_open` (the marker) ->
    `key_path.unlink()` -> `sealbox.decrypt`.
  - **V8-1 (replica 1) is confirmed.** The key is proven only after consumption.

**Clarification 1: the exposure point.** From v8 on, the `open` receipt precedes decryption, so "exposure = `open`"
(Addendum F item 1) is refined:
- **exposure = the first world delivered to the package** (the first per-world `predict` send);
- a run that ends before that, including V8-1's wrong-key case, is **VOID (pre-exposure)**, because the package has seen
  nothing;
- after it, Addendum F items 2-3 apply unchanged.

This is stricter on nothing and fairer on the V8-1 class.

**Clarification 2: what counts as "evidence of a cause outside the package's control" (Addendum F item 2).**
- A runner-assigned attribution label (`in_predictor_io`, `child_exitcode`, the named world) counts as evidence **only
  once a governing audit has found that label truthful** (v9 item 3).
- V8-2 and V8-3 show the current labels are not: an always-null exit code, and a package-caused restart failure
  labelled as not predictor I/O.
- Until then, **every post-exposure abort is FORFEIT whatever its label.**
- This closes, at the adjudication layer, the path V8-3 describes (a package-caused failure read as infrastructure
  VOID).

As before: pre-exposure; the operator may overrule before any release.

**D2 remains BLOCKED, fail-closed:** v9 needed (key proven before the marker; no unsealable interrupted write); S1 (#925).
Nothing released, revealed or built.

## Addendum I (2026-09-29): governing v9 audit recorded: FAIL SOLELY on S1; the code is clean at 2aa834ab1

| Item | Value |
|---|---|
| Verdict file | `roles/Odysseus/fabric_pilot/d2_audit/v9/VERDICT.md`, blob sha256 `a6e887de5991016c9d00c49225dbaebb8087b93c3ed5df4f4e30f26db5f69886` |
| Verdict commit | 6ead7beb506e1c12c16ccdceb7b8531136594cf2 (2026-09-29 09:41Z) |
| Audited code | 2aa834ab1 (Nestor #975) |
| **Governing verdict** | **FAIL, solely on S1** (record authentication / allow-list trust; operator decision #925, plus branch protection). **No blocking finding in the firewall code at 2aa834ab1.** v8 blockers fixed. Self-tests PASS. Replica 2 was PASS with S1 excluded. |
| Protocol record | None. |

- **Supersession, checked by Harmonia:**
  - The verdict states "the package is unchanged on origin/main since then". That was true when it was written; it is
    no longer true.
  - **D2 v10 (784d55b63, 09:43Z, two minutes after the verdict) changes AUDITED_FILES** (`runner.py`, `custody.py`,
    and `selftest_protocol.py`, among others: 6 files, +303/-59).
  - The v9 finding "no blocker in the code" therefore applies to **2aa834ab1 only**. The code on origin/main now is
    **not audited**.
  - Any PASS record must bind the code actually on the reference branch at audit time. protocol.py's AUDITED_FILES hash
    binding enforces this mechanically (AuditStale).
- **Adjudication notes from the verdict, accepted:**
  - Label regression A3-1 (world 0 labelled `in_predictor_io=true` before any delivery) does not affect adjudication
    under Addendum H: exposure is read from the receipts (was a world delivered), never from labels.
  - A3-3 (only the direct child is killed, so labels cannot prove the package was inactive) is exactly why Addendum H
    refuses labels as evidence.
  - The residual unsealed-chain paths (S-C / B-1) each have a defined ruling under E/H (pre-exposure VOID, post-exposure
    FORFEIT). Harmonia asks that they be **declared** in FIREWALL.md or closed by a custodian `seal-terminal` tool, so
    that the ruling is attached to a record rather than inferred from its absence.
- **D2 state:** the code-side blockers are exhausted at the last audited commit. **The gating item is now the operator's
  S1 decision (#925) and branch protection on main.** After that: a re-audit of the then-current commit, then a PASS
  record carried through S1's authentication. Nothing is released, revealed or built; Harmonia releases nothing on comms.
