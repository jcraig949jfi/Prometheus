I audited the D2 firewall at commit `a823b596c` (v10 code: `784d55b63`) by reading the code and history only. I did not run the self-tests or any code: the self-test booleans I cite are the committed values, not ones I reproduced. I found no new blocks-PASS issue. Overall it is still FAIL, because S1 is still open. The full audit is in `out/findings.md`.

**Verdict per claim**
- **1. Opacity:** HOLDS. The only leak is the plaintext length (`ciphertext_bytes`), which is already declared. Both the manifest and ciphertext sha256 match the brief.
- **2. Secrets never in git:** HOLDS for what the repo can show: no key, salt or plaintext file has ever been committed. The key-holder scan on M1 can't be checked from the repo.
- **3. Enforced order:** HOLDS mechanically. BROKEN on authentication: S1 (#925), known OPEN, blocks-PASS.
- **4. Controlled reveal:** HOLDS. Two minor notes: `reveal` still re-reads the manifest by ref name after the gates (N8), and result-seal checks only RESULT.json's chain head, not its full content (N10).
- **5. Predictor isolation:** HOLDS for isolation. A package can bypass the per-world deadline (V10-1, should-fix).
- **6. Draw integrity:** HOLDS for the repo-checkable part. `draw.py`, `sealbox.py`, `__init__.py` and `medium.py` hash to the at-draw values in the manifest.
- **v10-a. Attribution labels truthful:** HOLDS, with one should-fix (V10-2) and notes. For example, a failed child restart pairs a null exit code with the previous child's world (N3), and `current_world` lags by one while a world is being built (N4).
- **v10-b. seal-terminal seals every spent run and never removes or forges a verifying record:** BROKEN, should-fix (V10-3, V10-4). It does seal every spent run and cannot forge records. It can remove a verifying one.

**Should-fix findings (new in v10)**
- **V10-1: a package can hang the runner indefinitely after it has seen a world.**
  - The deadline covers only the parent's `poll`. The reply send at `runner.py:986-989` blocks without limit.
  - The package requests `init(200000)`, which returns a multi-MB reply, then never reads again.
  - No TIMEOUT fires and no receipt is written. Whether Ctrl-C then gives a labelled abort or a per-world error needs a run on M1 to confirm.
- **V10-2: no receipt records exposure.** Only the runner's own abort carries `exposed`.
  - If the runner is killed (after a V10-1 hang, or by the declared child-signals-parent residual) and the custodian runs seal-terminal, the record shows `exposed=null` with zero predictions.
  - That looks exactly like an honest crash before any world was delivered.
  - Integrity then depends on Harmonia reading null as exposed (FORFEIT). Fix: write a `deliver` receipt before the first predict send.
- **V10-3: nothing stops seal-terminal from running on a live run.**
  - If the runner is only slow, it can later append `close` after the custodian's abort, and a second seal-terminal truncates that genuine `close`.
  - In the other direction, the runner's `repair()` truncates the custodian's abort.
  - Either way a verifying record is removed. Fix: the runner holds an OS lock for its lifetime, and seal-terminal must take it first.
- **V10-4: seal-terminal drops a complete final record that lacks its trailing newline** (`runner.py:1153`), although `verify_receipts` accepts it.
  - A power-loss tear of just the newline of `close` would turn a CLOSED run into a custodian ABORTED.

**blocks-PASS findings**
- **S1** (known OPEN, #925). Records are authenticated only by the custodian allow-list (`protocol.py:461-473`), which is fed from comms messages whose `sender` field is client-supplied. Anyone who can push to main and post on comms can produce "allow-listed" records. Branch protection on main is also off; both are operator decisions.

OVERALL: FAIL