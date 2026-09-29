Audit complete. Full write-up is at `/home/jcraig/fabric-work/worker.ubu001/attempts/att-ab2a11c2ec85/out/findings.md`.

**Environment caveat:** this worker could run no shell (`git` and `python` both denied), so every claim requiring history-walking, hash recomputation, or *re-running* the selftests is marked CANNOT-VERIFY-FROM-REPO — I reviewed the code paths and the recorded `SELFTEST_*.json` but did not regenerate them.

**Per-claim verdicts**
- Claim 1 Opacity — HOLDS (AES-256-GCM + AAD, salted+nonce-embedded commitment, no world/knob/seed/nonce/summary public; `ciphertext_bytes` length leak is declared, N1).
- Claim 2 Secrets never in git — CANNOT-VERIFY-FROM-REPO (code sound; needs `firewall_check --all-history` + `git log --all` on M1).
- Claim 3 Enforced order — HOLDS mechanically (fully-qualified ref, `--full-history` add-once/no-merge, strict-ancestor stages, pinned seal, records-dir purity, loaded-closure); one should-fix on the authentication backing (F-COMMS).
- Claim 4 Controlled reveal — HOLDS (release/seal/reveal all gated, hashes-only until seal, M2 blocked, once-per-spec_id).
- Claim 5 Predictor isolation — HOLDS (spawn child, pickle-free codec, type-name-only errors, fail-closed empirical probe, key deleted after read).
- Claim 6 Draw integrity — HOLDS in code (CSPRNG nonce, lattice-uniform + exposed-D rejection, redraw check); at-draw hash equality and "family unchanged" sub-points CANNOT-VERIFY here.

**blocks-PASS findings:** none.

**should-fix findings**
- **F-COMMS** (`allowlist.py:38-65` via `comms/api.py:150-166`, `comms/identity.py`): S1's record authentication requires a comms message "from Odysseus/Cosmos/operator", but comms senders are unauthenticated — `post()` takes the seat name as a free parameter and `identity.py` proves only *which database*, never *who wrote a row*. Anyone with comms-write access can forge an author, which (with branch protection OFF) allows an attacker-authored PASS audit to be allow-listed. Human/host steps (custodian runs `allowlist.py`; Cosmos not stated to hold comms-write-as-Odysseus) keep it below blocks-PASS — **but if Cosmos can post as another seat, it rises to blocks-PASS**; that ACL is outside the audited package and I could not verify it.
- **F-ACCT** (`runner.py:806`): the designated-account check uses spoofable `getpass.getuser()` (env-derived). It's defence-in-depth only; the non-spoofable file isolation probe is the real backstop, so it cannot actually expose secrets. FIREWALL.md slightly over-credits the name check.
- **N1** (note, declared): `ciphertext_bytes` reveals plaintext length.

Neither authentication weakness is listed among the declared residuals; they should be added so the S1 allow-list is not over-trusted.

**OVERALL: PASS**

(Recording note: per the brief a PASS record is committed by the Odysseus seat; as a read-only disposable worker forbidden from modifying the repo, I did not commit `FIREWALL_AUDIT_1.json`. The record content would be format `c3-D2-firewall-audit/2`, `n:1`, verdict PASS, auditor Odysseus, `audited_commit f4cde414d74eb3cfa4a3cd50014b4c04ee1b2604`, with `code_sha256` from `python -m prometheus.cosmos.c3_holdout_D2.protocol --code-hashes --ref <commit>` — the seat should generate that map on a machine where python runs, since I could not, then post the record's LF sha256 to Nestor for the S1 allow-list.)