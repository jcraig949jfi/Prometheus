# Holdout D2 firewall re-audit v6: adversarial findings

- **Task / attempt:** tsk-8dd16e12e036 / att-28ac96448b2a (audit.security.adversarial v1)
- **Audited commit:** 7c7b0b8361a54b2e8088960c1ae8a7a055b64db9. It is on `remotes/origin/main` (`rogit branch -a --contains`). No file in `prometheus/cosmos/{c3,c3_holdout_D,c3_holdout_D2}` or the `prometheus/__init__` files differs from the v6 repair commit ab2a3efcb (`rogit diff --stat ab2a3efcb 7c7b0b836` is empty).
- **Method:** static reading plus git history only. No code was executed; the self-tests were not run by this worker.
- **Scope:** the firewall layer only. No law and no science.

## Headline

The v6 BP-1 repair moved the package hash, members, metadata and AST audit, plus the preflight child probe, ahead of the key read (`runner.py:609-612`). Recoverable, package-controlled failures still happen AFTER the key has been read (`runner.py:612`) and deleted (`:614`), and after the run directory has been created (`:643`). At that point:

- a rerun is refused, because the run directory exists (`runner.py:950-951`);
- a second release is refused, by the custody log (`custody.py:186`) and the committed KEY_RELEASED record (`custody.py:188`).

So the spec_id deadlocks, exactly as in v5's BP-1. Two of these paths can be triggered on purpose by the declared adversary (Cosmos, through the frozen package), and neither has a self-test:

- **V6-B1:** a member-path collision in the package makes extraction fail. It passes `validate_package`.
- **V6-B2:** the predictor reaches the raw pipe through the name-mangled attribute `_HiddenWorldStub__conn`, which the AST audit does not flag. A malformed message then raises an uncaught `KeyError`/`IndexError` in the parent during PREDICT. This goes beyond DoS: after the package has observed the hidden worlds through the System interface, it can choose to abort the run, so no sealed result ever exists (a selective abort).

**V6-B3:** the isolation probes that `_start_worker` runs during PREDICT (read and append on `run_<nonce>/receipts.jsonl`) check conditions that the preflight cannot check, because the file does not exist yet. A failure there is raised after the key is consumed.

**Verdict:** FAIL. The v5 criterion "every package check and every probe completes BEFORE the key is read" (v5 VERDICT.md:69-70) is not met.

---

## Claim 1: Opacity. Verdict: HOLDS (declared length residual only)

**Attacks tried:**

1. **Manifest fields.** I read every field (`MANIFEST_D2.json:1-36`). None carries a world, knob, seed or nonce.
   - `iv_hex` is a public GCM IV.
   - `ciphertext_bytes` reveals the plaintext length (declared, FIREWALL.md:149, 257).
   - The `d2_src_sha256_at_draw` and version strings are public code metadata.
2. **New v6 public record: `PREFLIGHT_<nonce>.json`** (`runner.py:691-698`). Its fields are format, verdict, run_nonce (already public in the designation), spec_id, package hash, runner id, account, host and utc. It contains nothing derived from the hidden set: the preflight never holds the key, and it runs before `sealbox.decrypt`.
3. **Receipt format.**
   - The worlds are named by index plus `world_tag = HMAC(key, …)` (`runner.py:622-623`).
   - `_summ` strips `r['system']`, whose name encodes the knobs (`runner.py:528-533`).
   - Error replies to the child carry the type name only (`runner.py:781-782`).
   - Receipts stay on M1 until the result seal (FIREWALL.md:98).
4. **Commitment brute force.** The commitment is salted with 32 secret bytes (`sealbox.py:64-67`, `SALT_BYTES = 32` at `:22`). The AAD binds the family hash (`sealbox.py:60-61, 76-80`).

Timing and length side channels are as declared (FIREWALL.md:254, 257).

## Claim 2: Secrets never in git. Verdict: HOLDS (repository side); CANNOT-VERIFY (M1 side)

**Attacks tried:**

1. `rogit log --all --name-only --diff-filter=A -- "*.key*" "*.salt*" "*plain.json" "*nestor_secrets*" "*hidden_D2*"`. It lists only `hidden_D2.enc`, in 95b31a30d.
2. `rogit log --all --name-status -- prometheus/cosmos/c3_holdout_D2`:
   - `.gitattributes`, `MANIFEST_D2.json`, `PROVENANCE_D2.md`, `SELFTEST_D2.json`, `hidden_D2.enc` and code/doc files are added only in 95b31a30d;
   - `SELFTEST_PROTOCOL.json`, `AUDIT_BRIEF.md` and the protocol-layer code are added after it;
   - no key, salt or plaintext file appears in any commit.
3. Holdout D is byte-identical to its seal (`rogit diff --stat a56ef7787 7c7b0b836 -- prometheus/cosmos/c3_holdout_D` is empty).

**Cannot verify from the repository:** the M1 facts (where the secrets directory is, that it is not synced, that it is not a repository) and the key-holder scan `entry.py firewall-check` (`all_clean`). Those need Nestor's published booleans from M1.

## Claim 3: Enforced order. Verdict: HOLDS for the order and records, except S1 (declared open); BROKEN for "the runner refuses before touching the key" (see V6-B1..B3)

**Attacks tried:**

1. **Record forgery and rewrite.**
   - `_added_once` over `--full-history -m` rejects any second blob, any deletion or rename, and any non-merge modification (`protocol.py:334-358`).
   - The ref is resolved once (`protocol.py:488-489`). Shadow refs are refused (`protocol.py:305-307`). Grafts and shallow repositories are refused (`protocol.py:209-219`). Replace objects are disabled and `GIT_*` variables removed (`protocol.py:185-191`).
   - No new hole found. Records remain unauthenticated: S1, declared open.
2. **Stale-code binding.** `code_sha256` must equal exactly AUDITED_FILES (`protocol.py:534-535`), in the committed tree and in the working tree (`:536-542`). The loaded closure is checked (`:543-547`). The entry guard compiles from the hashed bytes (`entry.py:161-172`). This holds.
3. **Refuse before the key.**
   - The gates, manifest, family hash, package validation and preflight all precede `read_hex_file` (`runner.py:588-612`). That much is repaired.
   - But the steps after `:612` still include package-controlled and environment-controlled failures. See V6-B1, V6-B2 and V6-B3.

## Claim 4: Controlled reveal. Verdict: HOLDS in code order; one note on the preflight record

**Attacks tried:**

1. **Release without a real preflight.**
   - `protocol.preflight_ok` (`protocol.py:263-274`) reads a plain, unsigned JSON file from `RUN_OUT_ROOT` (`protocol.py:58`). Every field in it is public (the designation's run_nonce, spec_id, package hash, runner id, account).
   - Anyone who can create a file in `C:/Users/jcrai/nestor_receipts/holdout_D2` can forge it. That includes the custodian (the declared same-account residual) and, beyond that residual, the **designated runner account**. That account is by construction NOT the custodian (`protocol.py:576-577`), but it must be able to write there: the runner makes `run_<nonce>` and the PREFLIGHT file in that directory (`runner.py:706, 949, 962`).
   - `preflight_ok` also ignores `host`, and binds neither the code (entry sha256 or governing audit) nor any time.
   - Impact: a forged record only lets the key be released into a run that then fails its own probes, which is a self-inflicted deadlock. No secret leaks, and Cosmos cannot write to M1. **Severity: should-fix** (bind host and code, and keep the record where only the custodian can accept it).
2. **The runner's write access to the allow-list directory.**
   - `RUN_OUT_ROOT` (`protocol.py:58`) is the SAME directory as `DEFAULT_ALLOWLIST` (`protocol.py:57`, `entry.py:57`) and `CUSTODY_LOG` (`custody.py:42`).
   - The v6 procedure therefore needs the non-custodian runner account to have create rights in the directory that holds the custodian's allow-list, custody log and lock.
   - Whether that account can also modify or delete `ALLOWLIST.json` or `custody.jsonl` depends on the host ACLs: **CANNOT-VERIFY** from the repository.
   - **Severity: should-fix.** Use a separate output root, and state its ACL.
3. **Reveal and result seal** (`custody.py:225-297`).
   - The chain is re-verified; close is at the sealed head; package, spec and nonce must match; the RESULT sha is checked. There is a lock and a once-only git record.
   - No new break found beyond S1 (RESULT_SEAL is allow-listed, `protocol.py:600`).

## Claim 5: Predictor isolation. Verdict: BROKEN (V6-B2); the process separation itself holds

**Attacks tried:**

1. **Reach the raw pipe from package code.**
   - `_HiddenWorldStub` stores the pipe as `self.__conn` (`runner.py:217-218`). Name mangling makes it `system._HiddenWorldStub__conn`.
   - The AST audit flags only dunder attributes, those that both start AND end with `__` (`runner.py:444-446`), or names in `FORBIDDEN_ATTRS` (`:109-112`). `_HiddenWorldStub__conn` and `send_bytes` pass.
   - The package can then write any bytes to the parent. That leads to V6-B2.
2. **Pickle and code injection over the pipe.** JSON plus `np.load(allow_pickle=False)` (`runner.py:185-200`). No code injection is possible. This HOLDS.
3. **Error-text leak.** The parent replies with the type name only (`runner.py:781-782`). This HOLDS.
4. **Isolation of the child's account.**
   - Spawn children run as the runner's account (`runner.py:667-670`). No code path starts the child as another account (grep for CreateProcessAsUser / LogonUser / child_account: none).
   - With the audited code, the preflight therefore always refuses (mkfile in `out.parent`, `runner.py:567-568, 707`). That is declared (FIREWALL.md:249-251, 281).
   - Consequence: the separate-child-account repair necessarily changes bound code and needs a re-audit.

## Claim 6: Draw integrity. Verdict: HOLDS (static); numeric hash equality CANNOT-VERIFY without execution

**Attacks tried:**

1. **CSPRNG.** `secrets.token_hex(32)` (`draw.py:154`). The world rng is `default_rng(int(nonce,16) % 2**128)` (`draw.py:63`). This is deterministic from the nonce, so a redraw is possible.
2. **Exposed-D rejection.** `draw_hidden(..., exposed_d_worlds())` (`draw.py:57-62, 156`).
3. **At-draw code hashes.** `draw.py`, `sealbox.py` and `__init__.py` were never modified after 95b31a30d (no M entry in `rogit log --name-status`), so they are byte-identical to the at-draw files. I did not recompute the sha256 values against `MANIFEST_D2.json:11-15`, because no execution was available. `verify_reveal` redraw reports `redraw_code_matches_manifest` (FIREWALL.md:204).

Single-draw provenance is a custodian statement (declared).

---

## BLOCKS-PASS findings

### V6-B1: a package member-path collision fails extraction AFTER the key is read and deleted (blocks-PASS)

**Evidence:**

- `validate_package` → `load_package(..., extract_to=None)` checks members only for:
  - a leading `/` or `\`, `..`, or `:`;
  - the suffix `.py/.json/.txt` (`runner.py:462-470`).

  It returns before extracting anything (`:498-499`).
- The extraction runs later (`runner.py:646-647`), after:
  - the key is read (`:612`);
  - the key is deleted (`:614`, `delete_key=True` from the CLI at `:956`);
  - the run directory is created (`:643`).
- The extraction itself is `extract_to.mkdir(exist_ok=False)` and then, per member, `p.parent.mkdir(parents=True, exist_ok=True)` and `p.write_bytes(b)` (`runner.py:500-505`).

**Scenario (cross-platform):**

1. Cosmos's zip holds `package.json`, `m.py` (the entry), `notes.txt` and `notes.txt/x.txt`. All suffixes are allowed, there is no `..` and there is no `:`, so the AST audit is clean.
2. The hash is committed, the preflight PASSES (it validates and never extracts), and custody releases the key.
3. `run.open()` reads and deletes the key and makes `run_<nonce>`. Extraction writes `notes.txt` as a file. Then `mkdir('notes.txt')` raises `FileExistsError`. In the reverse order, writing to a directory raises `IsADirectoryError` / `PermissionError`.
4. That is an `OSError`, which `main` does not catch (`runner.py:937-941` catches only RunnerRefusal and GateRefusal), so the process ends with a traceback.
5. Every later attempt is refused: the rerun because `run_<nonce>` exists (`:950-951`), the release by the custody log and KEY_RELEASED (`custody.py:186-189`), and resume by design (`runner.py:584-585`).

**Result:** the spec_id is permanently deadlocked by the declared adversary.

**Windows-only variants:** the same failure happens for:

- members containing `<>|?*"`;
- members whose names differ only in case (`A.txt` + `a.txt/x.txt`);
- a member path longer than MAX_PATH under `RUN_OUT_ROOT/run_<nonce>/package/`.

**Fix:** extract (stage) the package into its final directory, or a temporary one, BEFORE the key is read. Better still, reject any member set that is not a valid, collision-free tree for Windows (case-folded, reserved characters and names, a length bound). Add a self-test that such a package consumes nothing.

### V6-B2: the predictor can crash the parent runner mid-PREDICT through the leaked pipe (blocks-PASS; enables a selective abort)

**Evidence:**

- The pipe is reachable as `system._HiddenWorldStub__conn` (`runner.py:218`), and the AST audit does not flag it (`runner.py:442-448`).
- The parent's loop in `_predict_one` (`runner.py:772-792`) catches exceptions only around `_recv`. It then evaluates `msg[0]`, `msg[1] == i` and `msg[2]` unguarded.

**Scenario:**

1. `predict(system, task, seed)` calls `system._HiddenWorldStub__conn.send_bytes(b"{}")`.
   - Alternatives with the same effect: `b"[]"` or `b"5"`, or `b'["done"]'` (`msg[1]` raises IndexError), or a first element that is an `{"__nd__": …}` array (array truth raises ValueError).
2. In the parent, `msg[0]` on a dict raises `KeyError`. It is not caught by `_predict_one`, not by `predict_all` (try/finally only, `:801-808`), and not by `main` (`:939`). The runner dies after the key read and delete and the directory creation. Result: the V6-B1 deadlock.
3. **The stronger form (integrity, not only DoS):**
   - The package first queries the hidden worlds through the legitimate System interface (declared to reveal physics, FIREWALL.md:46-47).
   - It applies its own criterion ("my predictions on these worlds look weak").
   - It then either predicts normally or sends the malformed message.
   - In the abort case, no `predictions_sealed` or `close` record is ever written. There can be no RESULT_SEAL (`custody.py:233-234`) and no result, and no retry is possible.
   - Cosmos thus gets an option to void an unfavourable evaluation after seeing the hidden set. This holds even with the future separate child account, because it needs only the pipe.

**Also:** the `_send(self._conn, ["err", …])` in the except branch (`:782`) and `_send(… ["predict", …])` (`:765`) are unguarded against `BrokenPipeError` when the child exits right after a reply.

**Fix:**

- Validate the message shape strictly and treat ANY exception in the reply-handling loop as PREDICTOR_CRASH / PROTOCOL_ERROR for that world, recorded as the prediction.
- Do not give the package an object that holds the pipe: expose a closure, or a separate object without an attribute path to the pipe. Flag `_<Class>__x` mangled names in the audit.
- Add a hostile-message self-test.

### V6-B3: the run's isolation probes run AFTER the key is consumed and are not covered by the preflight (blocks-PASS under the v5 criterion)

**Evidence:**

- `_start_worker` (`runner.py:712-716`) runs `_spawn_probe` with:
  - read probes that include `run_<nonce>/receipts.jsonl` (`extra_probe_paths`, `:957`);
  - append probes on the same file (`write_probe_paths`, `:563-564`).
- It is called from `predict_all` (`:763-764`), after `:612/:614/:643`.
- In the preflight that file does not exist yet, so the read probe returns "missing" and passes (`runner.py:299-300`), and the preflight sends no append probe (`:707`, `[]`).
- `ChildNotIsolated` or `PredictorChildFailed` raised at this point (`:677-683`) is a refusal AFTER consumption.

**Scenario:**

1. The host's out-root ACL satisfies the preflight's mkfile probe (no file creation at the `RUN_OUT_ROOT` top level for the child) but lets the child read what inherits into `run_<nonce>/`.
2. The preflight passes and the key is released.
3. The run creates `receipts.jsonl`, the probe finds it "opened", ChildNotIsolated is raised, and the spec_id is deadlocked.

**Structural point:** `receipts.jsonl` and `package/*.py` both inherit the same ACEs from `run_<nonce>`. The runner sets no per-file ACL, so a child that can read the package it must import can also read the receipts. A child that cannot read them cannot import the package, and every world becomes PREDICTOR_CRASH: the one run is wasted, and the preflight never sends `go`, so it never tests the import.

A transient probe timeout (120 s, `:674-675`) when a child is respawned after a crash has the same effect.

**Fix:**

- Create the run directory, receipts and package with explicit ACLs in the preflight, or before the key read. Run the full set of run-time probes, including append and read on the real receipts path and an import of the entry module in the child, before the key is read.
- Make any probe failure after the key read a recorded per-world outcome, not an abort.

## Other findings

- **SF-1 (should-fix):** certification errors are uncaught.
  - The `certify(...)` calls in `certify_world` (`runner.py:853, 866-867`) are uncaught for anything but `ValueError` from `intervene`.
  - A numerical exception on some world, possibly influenced by Cosmos's in-range `intervention.to`, aborts after predictions are sealed, with the same deadlock.
  - Whether `certify` can raise on in-range values is CANNOT-VERIFY without reading and executing `c3/certify.py` on the hidden set.
- **SF-2 (should-fix):** the forgeable, unbound preflight record and the shared out-root/allow-list directory (Claim 4, attacks 1 and 2).
- **N-1 (note):** `--key` is unlinked on any path the runner gives (`runner.py:613-614`), before decryption verifies it. A mistyped existing file is deleted.
- **N-2 (note):** the preflight probes `out.parent/no_key_in_preflight.hex` (`runner.py:952`), never the real release destination. That is harmless only because the key is deleted before any run-time child exists.
- **N-3 (note):** a killed or interrupted runner process after `:614` also consumes the release. There is no recovery procedure, and it is not in the declared residuals.

## Standard check classes

1. **Unbound code with secrets.** The guard is unchanged since v5 (`entry.py:125-172, 175-180`). The spawn child re-imports entry as `__mp_main__` with `-I` inherited (the entry refusal at `:34` would otherwise fire). Nothing new found. F-3P (site-packages, `.pth`) is declared.
2. **Same-account readability.** Declared. The spawn child is the same account, so the preflight refuses (claim 5).
3. **Static-audit bypass.** NEW: mangled private attributes such as `_HiddenWorldStub__conn` (V6-B2). The audit remains a heuristic, as declared.
4. **Git reference ambiguity and history.** No new break (`protocol.py:301-358`, `entry.py:212-238`).
5. **Unauthenticated records.** S1 is open (declared). NEW: the PREFLIGHT file is unauthenticated and writable by the runner account (SF-2).
6. **Public fields narrowing hidden content.** The plaintext length and timing are declared. The preflight record has no hidden-set content.
7. **Spoofable host checks.** `socket.gethostname()` (`protocol.py:581`) is an unauthenticated host name. It is same-host state, within the account residual. `preflight_ok` does not check the host (SF-2).

## Declared residual risks

| declared residual | acceptable as declared? |
|---|---|
| Key holder / operator account can decrypt | Yes. |
| AST audit is a heuristic; read the package | Yes, but the audit is also relied on to keep the pipe private, and V6-B2 shows it does not. Pipe integrity must not depend on it. |
| Single-draw provenance | Yes. |
| The System interface reveals physics | Yes. But combined with V6-B2 it lets the package condition an abort on the hidden set, which is not declared. |
| S1 open; branch protection off | Declared. Out of this audit's decision. |

**Missing from the list:**

- an interrupted run consumes the release (N-3);
- the runner account's write access to the custodian's allow-list and custody-log directory (SF-2);
- the protocol cannot currently complete at all without a code change for the child account (claim 5). Any such change needs a re-audit.

## What would change the verdict

1. Stage and extract the package, and create the run directory, receipts and ACLs, before the key is read. Or reject member collisions and invalid Windows names in `validate_package`. Add a self-test.
2. The parent's reply loop must treat every malformed message as a recorded per-world outcome. Remove the pipe from the package's reach, and add a hostile-message self-test.
3. Every run-time probe (receipts read and append, and the child importing the package) must run before the key is read, or its failure must be recorded, not abort.
4. S1 (#925), unchanged.

OVERALL: FAIL
