This audit ends in **OVERALL: FAIL**, but the only blocker is S1 (records aren't authenticated), which was already declared open. Apart from S1, v9 fixes both v8 blockers; what remains is three should-fix items and five notes.

I did a read-only static review of commit 2aa834ab1. I could not run anything, so neither the self-tests nor `entry.py gates` against the real history were re-run. Only `runner.py` and `custody.py` changed in code since the v8-audited commit a02b9b20c; the other files are byte-identical, so their v8 verdicts carry forward. `hidden_D2.enc` and `MANIFEST_D2.json` still hash to the committed values, and no key, salt or plaintext file appears anywhere in the history.

**Verdicts, one line per claim**
- Claim 1, opacity: **HOLDS**. The new abort fields are indexes and exit codes only; the plaintext length is visible, as declared.
- Claim 2, secrets never in git: **HOLDS** from the repo. The key-holder booleans are CANNOT-VERIFY here; Nestor running `entry.py firewall-check` on M1 settles them.
- Claim 3, enforced order: **BROKEN** by S1 (declared open, #925). The code binding and the refusals before the key is read hold.
- Claim 4, controlled reveal: **HOLDS**. Custody now test-decrypts the key before release (`custody.py:202-203`).
- Claim 5, predictor isolation: **HOLDS** as declared (the AST check is a heuristic; the OS account is the boundary).
- Claim 6, draw integrity: **HOLDS**, carried from v8 (code unchanged and bound by `AUDITED_FILES`).
- v9, no recoverable error spends the release without a verifiable terminal record: **HOLDS** for argument, key and ordinary I/O errors.
  - The wrong-key spend is fixed: the key is proven before the consumption marker (`runner.py:750-769`).
  - An interrupted write is rolled back (`runner.py:401-431`).
  - Residual S-C remains (should-fix).
- v9, attribution labels are truthful: **BROKEN** (should-fix, S-A and S-B).

**Should-fix findings**
- **S-A:** the first child start at world 0 is labelled `in_predictor_io=true, current_world=0` (`runner.py:927-929`), even though no package code has run and no world has been sent.
  - Under Harmonia Addendum H, an infrastructure failure there is VOID (before exposure), but the label reads as package-side after exposure, i.e. FORFEIT.
  - The v9 self-test `v9_3_restart_failure_labelled_with_world` checks for this wrong label.
  - It is only should-fix because the truth can be worked out from `error_type` and `n_predictions_recorded=0`, and the package cannot trigger it.
  - Fix: add an explicit `delivered` flag, set after the first successful predict send.
- **S-B:** FIREWALL.md v9 says "a per-world poll failure is a per-world status". That is false: `self._conn.poll` is still outside the per-world guard (`runner.py:938`).
  - This is the v8 V8-4 note, still unfixed. On Windows, a child that raises `SystemExit` would most likely turn a per-world event into a whole-run abort. That Windows behaviour is inferred from CPython and can't be checked from the repo.
- **S-C:** a spent release can still end with no sealable terminal record, and no tool closes it. Three paths:
  - the abort record itself fails to write (disk full, or a transient antivirus lock);
  - RESULT.json fails to write after close, after which `_run_cli` raises `KeyError` (`runner.py:1154`);
  - a Ctrl+C in the tiny window after the receipts file is renamed into place.
  - Also, disk exhaustion caused by the package (through the child account) is not among the declared residuals.
  - Fix: a custodian `seal-terminal` tool that appends an `abort` record and rebuilds RESULT.json from the receipts would close the whole class.

**Notes**
- `abort()` ignores `repair()`'s return value (`runner.py:813`).
- The post-key probe at the world-0 start is still there; it is declared.
- Stale `current_world` and `child_exitcode` values appear outside the predict phase.
- A malformed custody key file leaves a stale custody lock.
- Custody's test-decrypt reads the reference by name, not the commit the gates resolved.

**blocks-PASS findings:**
- S1: protocol records are not authenticated (declared open, #925).

OVERALL: FAIL

Files are in /home/jcraig/fabric-work/worker.ubu001.a/attempts/att-155ff2e50749/out:
- findings.md