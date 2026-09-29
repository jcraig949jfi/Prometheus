# Holdout D2: brief for the independent firewall audit (Odysseus)

- **From:** Nestor, holdout custodian, 2026-09-28.
- **Authority:** operator directive "COSMOS C3 SUCCESSOR-SEAL" (verbatim:
  roles/Nestor/prompts/2026-09-28_cosmos_c3_successor_seal/).
- **Scope:** the coordinate/firewall layer ONLY: custody, opacity, commitments, the enforced order, leak behaviour.
- **Out of scope:**
  - Cosmos's law, its predictions and any scientific interpretation. None of it is needed for this audit, none of it is
    given here, and nothing in this package depends on it.
  - Whether the law is good.

## Public commitments (all on main)
| item | value |
|---|---|
| original seal (holdout D, EXPOSED, never reused) | a56ef7787, merged into main by merge commit 7c018d92b; files byte-identical |
| successor seal commit | 95b31a30d (the only commit that adds `hidden_D2.enc` and `MANIFEST_D2.json`) |
| spec_id | e2d3213b02aae58b0b20bbd6b5a296545b6335078ae6a0a382ceaf346dc0d9fe |
| commitment = sha256(salt ‖ plaintext) | 69f911535303dd3fd1b7f7a60f5b598d899c1ecb9572e149c495431f6d419c4b |
| sha256(hidden_D2.enc) | f75ba333efea147a351c3364aa7eb690a4970546bb717c99fcf86809b5fdfc9f |
| sha256(MANIFEST_D2.json file) | 78874e9de66714683b3e6a76e41974670995f577a1b8324672c8863cb82a71fe |
| protocol layer | 06f53ae24 (protocol.py, custody.py, evidence.py, selftest_protocol.py; runner gated) |

## Claims to test (try to break each)
1. **Opacity.**
   - Ciphertext: AES-256-GCM, random 256-bit key, AAD bound to the family source hash.
   - Commitment: salted with 32 secret bytes, so candidate worlds cannot be confirmed by brute force.
   - Nothing public carries world identities, knob values, seeds, the nonce or distributional summaries. Check the
     manifest fields, `SELFTEST_*.json` (booleans only) and the receipt format (`runner.py`, `receipts_ok` in
     `selftest_D2.py`).
2. **Secrets never in git.**
   - Key, salt and plaintext live only on M1 (SKULLPORT), outside every repository.
   - Check `git log --all --stat -- prometheus/cosmos/c3_holdout_D2`, and grep the history for key/salt-shaped files.
   - Key-holder-only checks (`firewall_check.py`) run on M1 by Nestor; the latest pass was all clean. Ask for any
     boolean you want re-run.
3. **Enforced order** (`protocol.py`): seal < audit PASS < Cosmos commitment < designation < result seal.
   - Records are read from the COMMITTED tree of origin/main, added once and never modified.
   - The audit binds the sha256 of every file in `AUDITED_FILES`, so any later change makes it stale.
   - The runner and custody refuse before touching the key.
4. **Controlled reveal** (`custody.py`, `evidence.py`):
   - key release only to the designated runner/host (never M2 = SPECTREX5);
   - results public as hashes only until the result seal;
   - reveal and the Harmonia bundle only after it.
5. **Predictor isolation** (`runner.py`): separate process without the key; pickle-free pipe; error replies carry type
   names only.
6. **Draw integrity** (`draw.py`):
   - CSPRNG nonce;
   - uniform over the unchanged public family lattice, with rejection of exposed-D duplicates;
   - reproducible from the nonce after reveal (`verify_reveal --redraw`);
   - `draw.py`/`sealbox.py` on main hash to the at-draw values recorded in the manifest.

## Synthetic fixtures and how to run
- `COSMOS_BROKER=1 python -m prometheus.cosmos.c3_holdout_D2.selftest_protocol` builds throwaway sets from PUBLIC
  nonces, throwaway keys, and throwaway git repositories holding the protocol records. It runs:
  - 18 runner-gate cases;
  - 17 custody/evidence cases;
  - 3 injected-defect controls.

  Expected output: `SELFTEST_PROTOCOL.json`.
- `COSMOS_BROKER=1 python -m prometheus.cosmos.c3_holdout_D2.selftest_D2` covers the runner machinery: hash pinning,
  predict-before-certify, receipts, isolation, the AST audit and the commitment round trip.
- Your own fixtures: `draw.draw_hidden(<your nonce>, n, draw.exposed_d_worlds())` + `draw.seal(...)` into a temp
  directory. `selftest_protocol.GateRepo` shows how to lay out a gate repository.

## Declared residual risks (please assess)
- The gates are not a boundary against the key HOLDER: anyone with the operator account on M1 can decrypt directly. The
  boundary against Cosmos is custody plus the public order record.
- The prediction package is Python running as the operator account on M1. The AST audit is a heuristic, not a sandbox.
  Mitigation: read the package before running it, or run it under a low-privilege account.
- Single-draw provenance ("draw.py ran once") is a custodian statement, not cryptographically verifiable.
- The System interface exposes a world's physics to the predictor by the contract's design.

## Recording your verdict
- Findings go by comms to Nestor (cc operator).
- **On PASS only**, commit in ONE commit on main (your branch merged, or direct) the file
  `prometheus/cosmos/c3_holdout_D2/protocol/FIREWALL_AUDIT.json`:
  ```json
  {"format": "c3-D2-firewall-audit/1", "verdict": "PASS", "auditor": "Odysseus",
   "spec_id": "e2d3213b02aae58b0b20bbd6b5a296545b6335078ae6a0a382ceaf346dc0d9fe",
   "audited_commit": "<the commit you audited>",
   "code_sha256": <output of: python -m prometheus.cosmos.c3_holdout_D2.protocol --code-hashes --ref <that commit>>}
  ```
- Records are immutable, so do NOT commit a FAIL record: post the findings instead. Nestor fixes them, and the re-audit
  binds the new code hashes.


## RE-AUDIT (v2, 2026-09-28): what changed and how to record the verdict
- Fixes for F1-F4 and S1-S5: FIREWALL.md, last section (each with its refusal test in selftest_protocol.py).
- Record a PASS as `prometheus/cosmos/c3_holdout_D2/protocol/FIREWALL_AUDIT_1.json` (versioned records now; a FAIL MAY be
  recorded too, it no longer deadlocks), in ONE commit, no merge:
  ```json
  {"format": "c3-D2-firewall-audit/2", "n": 1, "verdict": "PASS", "auditor": "Odysseus",
   "spec_id": "e2d3213b02aae58b0b20bbd6b5a296545b6335078ae6a0a382ceaf346dc0d9fe",
   "audited_commit": "<the commit you audited>",
   "code_sha256": <python -m prometheus.cosmos.c3_holdout_D2.protocol --code-hashes --ref <that commit> ; exactly AUDITED_FILES>}
  ```
- Then post on comms (to Nestor) the sha256 of the committed record bytes (LF-normalised): the custodian adds it to the
  allow-list only from a message whose sender is Odysseus and which contains that sha256 (S1).


## RE-AUDIT v3 (2026-09-29)
Scope: everything in FIREWALL.md, section "v3".
- S1 (authenticating records) is KNOWN OPEN, pending the operator's root-of-trust decision (#925). Please assess
  everything else so that the remaining gap is S1 alone.
- Your replicas run with read-only git (--cap fabric.runtime==0.2). Please execute
  `COSMOS_BROKER=1 python -m prometheus.cosmos.c3_holdout_D2.protocol` against the REAL history
  (Harmonia DEF-HARM-D2-001), and verify B1 by trying to make the entry path load unbound code.
- Record format, allow-listing and hashes are unchanged from the v2 section. The next record is FIREWALL_AUDIT_1.json
  (no audit record exists yet).

## RE-AUDIT v4 (2026-09-29)

**Scope:** everything in FIREWALL.md, section "v4". The v3 verdict is at roles/Odysseus/fabric_pilot/d2_audit/v3/VERDICT.md.

**Still open:** S1 (authenticating records, #925) and branch protection on main. Both are operator decisions. Please assess everything else, so that the remaining gap is S1 and the declared host capabilities alone.

**What to try:** break P1, P2 and P3 again.
- Plant a module anywhere the entry path or a key-holding process could import it: the package directory, the repository root, the cwd, a `.pth` file or a `.pyc`.
- Try `-S`, PYTHONPATH and GIT_* variables, replace refs, and a `git.exe` in the cwd.
- Check that the end-to-end path through entry.py completes with the once-only records committed.

**How to run (M1, or any host with the repo):**

```
COSMOS_BROKER=1 python -m prometheus.cosmos.c3_holdout_D2.selftest_protocol
COSMOS_BROKER=1 python -m prometheus.cosmos.c3_holdout_D2.selftest_D2
python -I -B prometheus/cosmos/c3_holdout_D2/entry.py gates SEAL
```
- **selftest_protocol:** 98 checks + 4 defect controls. It builds throwaway repos with a bare origin, runs entry.py by path in subprocesses, and runs the P1/P2/F-CWD/F-GITENV positive controls.
- **selftest_D2:** 10 checks + 13 negative controls.
- **entry.py gates SEAL:** expected to be REFUSED on the real repo, because no allow-listed audit exists yet. That is the correct refusal. SEAL itself passes on the real history via protocol.check_gates.
- **The key-holder scan:** Nestor runs `entry.py firewall-check` on M1 and publishes the booleans only.

**Record:** format, allow-listing and hashes are unchanged from the v2 section. The next record is FIREWALL_AUDIT_1.json (no audit record exists yet).

## RE-AUDIT v5 (2026-09-29)

**Scope:** FIREWALL.md, section "v5". The v4 verdict is at roles/Odysseus/fabric_pilot/d2_audit/v4/VERDICT.md.

**Still open:** S1 (#925) and branch protection on main, both operator decisions. Please assess everything else.

**What to try:**
- Find ANY executable or module that a key-holding tool (runner, custody, evidence, firewall-check, allowlist) starts or imports by bare name, from the working tree, or unbound.
- Break the pre-audit pinning (pin-tools runs no repository code).
- Make the runner fail AFTER it consumes anything.
- Make the spawn child load unbound code.

**How to run:**

```
COSMOS_BROKER=1 python -m prometheus.cosmos.c3_holdout_D2.selftest_protocol
COSMOS_BROKER=1 python -m prometheus.cosmos.c3_holdout_D2.selftest_D2
```
- **selftest_protocol:** 118 checks + 4 defect controls. It runs entry.py (`-I -B`) in subprocesses, including the runner end to end through entry. The Windows-only controls report `not_applicable_on_this_os` on Linux; their M1 values are in the committed SELFTEST_PROTOCOL.json.
- **selftest_D2:** 10 checks + 13 negative controls.

**Record:** format and allow-listing are unchanged. The next record is FIREWALL_AUDIT_1.json.
