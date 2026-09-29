The v6 re-audit fails. The runner still reads and deletes the released key before steps that can fail and that Cosmos's package can deliberately trigger. The spec_id then locks up for good: a rerun is refused because the run directory exists, and a second key release is refused by the custody log and the committed KEY_RELEASED record. This is the same class of defect as v5's BP-1.

I audited commit 7c7b0b836, which is on origin/main; no audited file differs from the v6 repair commit ab2a3efcb. I only read code and git history and did not run the self-tests. The full audit is in `out/findings.md`.

**Verdict per claim**
1. **Opacity:** HOLDS. The only exposures are the declared ones: plaintext length in the manifest and timing. The new PREFLIGHT record contains public fields only.
2. **Secrets never in git:** HOLDS on the repository side. The only secret-shaped file ever added is `hidden_D2.enc`, in 95b31a30d. The M1 facts and Nestor's key-holder scan can't be verified from the repo; Nestor's published booleans would settle them.
3. **Enforced order:** HOLDS for the order and the records, apart from S1, which is declared open. BROKEN for "the runner refuses before touching the key" (B1, B2 and B3 below).
4. **Controlled reveal:** HOLDS in code order. Should-fix: the PREFLIGHT record custody requires is unsigned. The designated runner account, which is not the custodian, can forge it. That account must also be able to write to the directory holding the custodian's allow-list and custody log.
5. **Predictor isolation:** BROKEN (B2). The separate process and the pickle-free pipe hold, but the package can reach the pipe itself.
6. **Draw integrity:** HOLDS. `draw.py`, `sealbox.py` and `__init__.py` are unchanged since the seal commit. I did not recompute their hashes against the manifest because I executed nothing.

**Blocks-PASS findings**
- **B1: a package with colliding member paths fails after the key is gone.**
  - A zip holding both `notes.txt` and `notes.txt/x.txt` passes all package checks, including the preflight, because nothing is extracted then (`runner.py:462-499`).
  - Extraction happens only at `runner.py:646`, after the key is read (`:612`) and deleted (`:614`) and the run directory is created (`:643`).
  - The resulting `FileExistsError` is not caught (`:939`), so the spec_id deadlocks.
  - On Windows, member names with `<>|?*"`, names that differ only in case, or paths longer than MAX_PATH do the same.
- **B2: the package can crash the runner through the pipe, and use that to void an unfavourable run.**
  - The package can reach the raw pipe as `system._HiddenWorldStub__conn` (`runner.py:218`). The AST audit only flags names that start and end with `__` (`:444-446`), so this passes.
  - Sending `b"{}"` makes `msg[0]` raise an uncaught `KeyError` in the parent during PREDICT (`runner.py:772-792`), which deadlocks the spec_id.
  - Worse, the package can first probe the hidden worlds through the System interface and only abort when its predictions look weak. No seal and no result ever exist, so Cosmos can void an evaluation after seeing the hidden set. This still works once the child runs as a separate account.
- **B3: some isolation probes run only after the key is gone.**
  - The read and append probes on `run_<nonce>/receipts.jsonl` run in `_start_worker` during PREDICT (`runner.py:712-716`, `:957`).
  - The preflight cannot test them, because the file doesn't exist yet (`:299-300`, `:707`).
  - A `ChildNotIsolated` there comes after consumption. The receipts and the package files inherit the same access rules, so a child that can read the package it must import can also read the receipts. This fails the v5 condition that every probe completes before the key is read.

None of these three has a self-test. The v6 tests cover only a wrong-hash package and an AST-flagged package.

**Should-fix**
- Exceptions from `certify` other than the intervention `ValueError` are uncaught after the predictions are sealed.

The notes are in `findings.md`.

**Residual risks**
- **Accepted as declared:** the key holder can decrypt, single-draw provenance is a custodian statement, and S1 and branch protection remain open as operator decisions.
- **Accepted with a caveat:** the AST heuristic and the physics exposed by the System interface are acceptable only once B2 is fixed.
- **Missing from the list:**
  - An interrupted runner consumes the release.
  - The runner account can write to the custodian's allow-list directory.
  - No code can start the child under a separate account. With the audited code the preflight therefore always refuses, and the required change will need a re-audit.

No protocol record was written.

OVERALL: FAIL