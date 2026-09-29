The v12 anchor fails. A later FAIL audit that is anchored and supersedes a PASS can be undone by one ordinary push to main, after which the earlier PASS governs again. This was a static audit only: I could not run the self-tests, `entry.py gates SEAL` or `--code-hashes`. The full audit is in `out/findings.md`.

**v12 anchor claims:**
- **A. A record governs without a verifying anchor entry:** HOLDS for the record that governs. Every governing role needs a verifying entry, and every command-line tool uses the real anchor. But V12-1 lets a record govern wrongly because a later anchored record gets ignored.
- **B. Forge, edit, reorder or truncate the anchor undetected:** BROKEN (should-fix). Cutting entries off the end, or editing an entry and recomputing the chain, is not detected. This sits inside the declared risk that the anchor is protected only by the M1 account.
- **C. Anchored commit is a non-ancestor, or not the adding commit:** BROKEN through V12-1. It is refused for the governing record. For a later FAIL audit it is silently ignored instead of refused.
- **D. A gated step skips re-verification:** HOLDS for the four governing roles. Should-fix: the once-only records (KEY_RELEASED, REVEALED) are never checked against the anchor.

**Brief claims:**
1. **Opacity:** HOLDS. The manifest and anchor carry no hidden content, error replies carry type names only, and the manifest and ciphertext hashes match the brief.
2. **Secrets never in git:** HOLDS as far as the repository shows. The M1 key-holder scan can't be verified from here.
3. **Enforced order:** BROKEN (V12-1, blocks PASS).
4. **Controlled reveal:** HOLDS, with should-fix V12-3.
5. **Predictor isolation:** HOLDS. `runner.py` is unchanged since v11.
6. **Draw integrity:** HOLDS. `draw.py`, `sealbox.py` and `__init__.py` on main match the at-draw hashes in the manifest, and the nonce comes from `secrets.token_hex(32)`. The redraw can't be checked until the nonce is revealed.

**Blocks-PASS finding: V12-1.** Both `protocol.check_gates` (`protocol.py:582-588`) and `entry.verify` (`entry.py:305-309`) only look at audit files present in the tree at origin/main. An anchored record that no longer verifies is treated as "not anchored" and skipped, rather than refused.
- **Scenario:** the anchored records are A1 (FIREWALL_AUDIT_1, PASS), then the commitment, the designation, and A2 (FIREWALL_AUDIT_2, FAIL); today the gates correctly refuse. Anyone who can push to main then does one of these:
  - deletes FIREWALL_AUDIT_2.json in a normal commit;
  - edits any byte of it;
  - force-pushes main back to before A2.
- **Result:** A1 PASS governs again and `check_gates` through DESIGNATION passes, so key release and the run go ahead. No force-push is needed for the first two, and branch protection is off by MWO-0004.
- **What it contradicts:** S2 ("a later FAIL supersedes a PASS", FIREWALL.md:137) and "any mismatch fails closed" (FIREWALL.md:414 and MWO-0004 D2-1).
- **Why the tests miss it:** the self-tests never delete, edit or drop an anchored audit.
- **Fix:** build the audit set from the anchor rather than the tree. Refuse if any anchored AUDIT record is missing, changed, or not on origin/main's history. Keep ignoring audit files that have no anchor entry at all. Apply the same rule in `entry.py`.

**Should-fix:**
- **V12-2:** the anchor's hash chain doesn't stop anyone who can write the file (see B above). Publishing the chain head after each append would make cuts and rewrites detectable.
- **V12-3:** KEY_RELEASED and REVEALED aren't anchored. After a force-push removes them, only the unchained custody log stops a second release. The runner's `--out-root` is also chosen on the command line, so a second release could lead to a second run.
- **V12-4:** `allowlist add` has no expected-commit or expected-hash argument. It anchors whatever is on main, the anchor can't be undone for fixed-name records, and nothing mechanical ties a record to its author.

There are also six notes in the findings, including a fail-closed lock-up if two anchor appends run at once and the anchor file's permissions on M1, which the repository can't show.

Under MWO-0004 D2-2, V12-1 is an ordinary implementation defect, so one final repair and one final re-audit are allowed.

OVERALL: FAIL