I found no finding that blocks PASS, so my verdict is PASS. This was a read-only audit of b17320e64 (the D2 code last changed in 2a552834d, compared against the v12 commit b0763ebaa). I could not run code: both self-tests and the real-history run are **not verified** here. Their results come from the committed `SELFTEST_PROTOCOL.json` (179 checks + 4 defect controls, all true) and need the script replicas to confirm them. The full audit is in `out/findings.md`.

**Verdict per claim**
- **Item 1, V12-1 (the anchor governs, not the tree): HOLDS.** Every anchored record must be present on origin/main with its anchored blob, anchored at a commit on origin/main's history, and that commit must hold the same blob. Otherwise the check refuses. It runs in `protocol.check_gates` (`protocol.py:515-543`, `605-617`) and in `entry.verify` (`entry.py:238-260`, `342`), for all six record roles. Attacks that failed:
  - deleting, editing or force-pushing away an anchored FAIL;
  - making an anchored FAIL drop out of the audit set without deleting it (gitlink or symlink directory, mode change, modify-then-revert, merged re-add, look-alike names);
  - an unanchored later PASS.
  
  No gated step skips the check, and it adds no refusable check after the key is read.
- **Item 1, V12-3 (KEY_RELEASED and REVEALED are anchored): HOLDS.** Custody refuses a second release or reveal (`custody.py:199`, `306`). A force-push that removes an anchored copy makes every later gate refuse. The runner's output root is now fixed (`runner.py:1321`).
- **Item 2, V12-4 (`allowlist add` needs `--expect-commit` and `--expect-sha256`): HOLDS.** Both are required and checked before anything is appended (`allowlist.py:63-66`, `90-92`). A record landed first by someone else is refused.
- **Item 3 (anchor rollback): HOLDS.** Edited, reordered and half-written entries are detected, and a lock file serialises concurrent appends. FIREWALL.md:439 declares precisely that tail truncation by the custodian account goes undetected. That equals the existing key-holder residual, provided finding N-1 below holds.
- **Claims 1–6 (carried from v11/v12): HOLD.** v13 changes them only where noted, and every changed file is in `AUDITED_FILES`.

**Blocks-PASS findings:** none.

**Should-fix**
- **N-1:** the rollback declaration assumes only the custodian account can write `ANCHOR.jsonl`, and nothing checks that.
  - The anchor's hash chain uses no secret, so any account that can write the file can truncate it or append entries that verify.
  - The runner account has to write `holdout_D2/runs`, which sits in the same directory as the anchor. Granting it Modify on `holdout_D2` would be an easy mistake.
  - Fix: either check the anchor's permissions (in custody or firewall-check) or declare this residual before the first designation.
  - It cannot be reached in production today: every run fails at preflight until the separate runner and child accounts exist.

**Notes (N-2 to N-9)**
- The KEY_RELEASED test does not isolate the new anchor check, because the record is still committed.
- An anchor line that is valid JSON but not an object gives a traceback instead of a clean refusal (it still fails safe, before the key).
- A lock file left by a crash blocks all appends until it is removed by hand.
- Some docs are stale (FIREWALL.md:400, `allowlist.py` and `protocol.py` docstrings).
- A FAIL audit takes effect only when the custodian anchors it, and the anchor is not in the Harmonia evidence bundle.
- Anyone who can push to main can take a fixed record name first; this blocks that name but fails safe.
- Nothing forces the custodian to anchor KEY_RELEASED or REVEALED promptly.
- `reveal` and `evidence` re-read files by ref name after the gates (existed before v13).

**Declared residuals:** acceptable as declared. Two items are missing from the list: N-1 (who else can write the anchor) and N-6 (third parties cannot see what was anchored).

OVERALL: PASS (conditions: the script replicas confirm both self-tests green on this commit, and N-1 is declared or checked before the first designation)