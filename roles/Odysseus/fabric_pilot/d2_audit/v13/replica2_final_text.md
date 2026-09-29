I found no blocking defect in v13. All three v12 repair items are implemented correctly, and the six standing claims still hold. I audited commit b17320e64, which has the same D2 code as the v13 repair commit 2a552834d. This was a static audit only: I read the code and git history but did not run the self-tests or the `--code-hashes` command. The full audit is in `out/findings.md`.

**Verdict per item**
- **V12-1 (the anchor governs):** HOLDS. `protocol.verify_anchor_state` (`protocol.py:515-543`) runs inside `check_gates` for every stage after SEAL. `entry._verify_anchor_state` (`entry.py:238-260`, called at :342) does the same before any code is bound. Deleting, editing or force-pushing away an anchored FAIL is refused in both places. So is re-adding a deleted record with the same content, and so is an unanchored higher-numbered PASS. Every step that touches the key or a record goes through this check.
- **V12-3 (KEY_RELEASED and REVEALED are anchored; one run location):** HOLDS. Custody refuses at `custody.py:199` and `:306`, before the key is read or the secrets are copied. The runner's output root is fixed at `runner.py:1321`.
- **V12-4 (`allowlist add` needs the published commit and sha256):** HOLDS. Both values are required and matched exactly (`allowlist.py:63-66, 90-92`).
- **V12-2 (anchor rollback):** HOLDS as declared. Edited, reordered or torn entries break the chain. Concurrent appends are blocked by a lock. Truncation or a full rewrite by the M1 custodian account is precisely declared as undetected.
- **Claim 1, opacity:** HOLDS. One note: the ciphertext size reveals the plaintext length.
- **Claim 2, secrets never in git:** HOLDS. No key-, salt- or plaintext-shaped file appears anywhere in history. I can't check the M1 scan from the repository.
- **Claim 3, enforced order:** HOLDS. The seal has exactly one non-merge add (95b31a30d), and no tag or branch shadows origin/main.
- **Claim 4, controlled reveal:** HOLDS.
- **Claim 5, predictor isolation:** HOLDS. `runner.py` is unchanged apart from the two out-root lines.
- **Claim 6, draw integrity:** HOLDS. `draw.py`, `sealbox.py`, `medium.py` and the package `__init__.py` are unchanged since the seal commit. I couldn't recompute the sha256 values here.

**blocks-PASS findings:** none.

**Notes (not blocking):**
- **N-1:** The entry-path v13 tests only look for a message both entry.py and protocol.py print, so removing entry.py's own check wouldn't fail them. That check is the only protection for `firewall-check` and `allowlist`.
- **N-2:** The anchored KEY_RELEASED test would pass without the new check, because the committed record already refuses a second release.
- **R-A:** An auditor's FAIL only takes effect once the custodian anchors it, and nothing authenticates who published the record. This fits MWO-0004 but should be written down.
- **R-B:** The runs directory sits next to `ANCHOR.jsonl`. If M1's permissions let the runner or predictor-child account write there, a non-custodian could alter the anchor. I can't see M1 permissions from the repository. A published M1 true/false check that neither account can write to the anchor would settle it.
- **R-C:** Anyone who can push to main can halt D2 permanently by deleting or rewriting a record. It fails safe but should be declared.
- **R-D:** A crash during an anchor append leaves a broken line or a leftover lock. It fails safe, but the repair is a manual rewrite.
- **R-E:** `FIREWALL.md:414` overstates the "adding commit" check; it applies only to the governing records. This is not exploitable.

**Still to settle outside the repository:**
- The separate self-test runs at b17320e64. The committed `SELFTEST_PROTOCOL.json` shows all checks passing, but the custodian produced it.
- The `--code-hashes` output needed for `FIREWALL_AUDIT_1.json`.
- Whether b17320e64 is on origin/main; the local copy of origin/main is out of date.

OVERALL: PASS