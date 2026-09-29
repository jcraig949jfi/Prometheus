The v8 re-audit fails: a receipt write that is interrupted partway can leave the run's record chain unverifiable, so it can never be sealed. The full audit is in `out/findings.md`. I only read code and git history; I ran no repository code, and the shell was denied, so I could not recompute any sha256 myself.

**Claims**
1. **Opacity: HOLDS.** One note: after an abort, `n_receipts` in the public result seal shows which world the run ended at. The package controls that point, so it is a small channel of the same kind as the declared timing channel.
2. **Secrets never in git: HOLDS** for everything the repository can show. `rogit log --all` finds no key, salt or plaintext file ever added. Whether the secrets exist only on M1 can't be checked from the repo; only Nestor's `firewall-check` on M1 can settle it.
3. **Enforced order: HOLDS.** v8 only changed `runner.py` and the self-tests. The added-once, tag-shadowing, grafts, stale-code and import-guard checks all still hold.
4. **Controlled reveal: HOLDS.** The reveal order is intact. V8-1 only makes the result seal unreachable.
5. **Predictor isolation: HOLDS as declared.** The new v8 attribution evidence is partly broken (V8-2, V8-3).
6. **Draw integrity: HOLDS.** `draw.py`, `sealbox.py`, `__init__.py`, `medium.py` and the sealed files are byte-identical to the seal commit 95b31a30d.
7. **v8 items:**
   - The open record now appears atomically with `receipts.jsonl`: HOLDS.
   - The stand-in is probed for read and append before the key: HOLDS.
   - A closed pipe is a per-world failure: HOLDS on Linux, with one narrow Windows race (V8-5).
   - "No ordinary exception can spend the designation unsealed" (`FIREWALL.md:334`): **BROKEN** (V8-1).

**Blocks-PASS finding**
- **V8-1: an exception mid-write makes the abort record unverifiable.**
  - **Where:** `runner.py:398-406`, `Receipts.append` writes the line, flushes and fsyncs it, and only then adds it to the in-memory list.
  - **Trigger:** any exception after the bytes reach the file but before that last step. Examples are an `OSError` from `os.fsync`, a Ctrl+C during the fsync, or a `MemoryError`.
  - **Effect:** the record is on disk but not in memory. `abort()` then writes a record with a duplicate sequence number, and the chain fails verification ("seq break").
  - **Consequence:** result-seal, reveal and evidence all refuse. A re-run and a second key release are also refused. The spec_id is spent with no sealable outcome, VOID or FORFEIT.
  - **How a package can trigger it:** the child can send Windows console control events to the parent, which v8 itself declares. Sent right after its prediction, the event lands inside the parent's fsync.
  - **Same window in `open()`:** a Ctrl+C just after the atomic rename leaves a chain holding only the open record, with no terminal record.
  - **Why it blocks:** this is the class the v7 auditor ruled blocking "whatever the likelihood" (V7-1). No self-test covers it.
  - **Fix:** on any failure, truncate the file back to its size before the write, or have `abort()` re-read the chain from disk first. Add a test that makes `os.fsync` fail after a prediction record is written.

**Other findings**
- **V8-2 (should-fix):** the abort's `child_exitcode` is always `None`. `abort()` kills the worker and clears its handle before reading the exit code, and the self-test only checks that the field exists.
- **V8-3 (should-fix):** after a timeout or crash, the worker restart re-runs the isolation probe after the key was read. If that probe fails, the abort names the previous world with `in_predictor_io: false`. A restart failure caused by the package would then look like infrastructure, which the adjudication rule makes VOID.
- **V8-6 (should-fix):** nothing checks, before the key is read, that the child can read the staged package. If the run directory's permissions deny it, every world becomes a predictor crash and the run closes on a configuration error.
- **Declared residuals (note):** the "child can signal or pressure the parent" wording is incomplete.
  - Two control events in a row interrupt `abort()` itself, so no terminal record is written.
  - Disk exhaustion by the child account isn't listed.
  - RESULT.json is written non-atomically, and a failed write after close causes a `KeyError` in the CLI.
- **V8-5 (note):** on Windows, a child that exits in a narrow timing gap can abort the whole run instead of failing one world. This is inferred from how Python's Windows pipe `poll()` behaves; the fix-round self-test can't hit it. It can be settled on M1 with a package that raises `SystemExit` after one System call.
- **Still open:** S1 (#925) and branch protection are operator decisions and were not assessed further.

OVERALL: FAIL