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
