I audited commit 57c809387 and found one blocking defect, so the verdict is FAIL. I could not execute anything in this session (Bash was denied; only `rogit` worked). So neither selftest was run, `entry.py gates SEAL` was not run against the real history, and `--code-hashes` was not run. Everything below comes from reading the code and the git history, plus the committed M1 selftest output. The full audit is in `out/findings.md`.

**Verdicts per claim**
- **Claim 1, opacity:** HOLDS. The plaintext length in the manifest and timing after predictions are frozen are both already declared.
- **Claim 2, secrets never in git:** HOLDS for file names; `rogit log --all` shows no key, salt or plaintext file ever committed. CANNOT-VERIFY for content, which needs the key-holder `firewall-check` booleans from M1.
- **Claim 3, enforced order:** HOLDS, with S1 excluded as asked. From the history, the seal files are added by exactly one non-merge commit (95b31a30d) and four merges carry the same blobs, so SEAL should pass; I did not run it. Notes: a forged commit-graph file can re-parent history the way grafts can, and it is not checked (needs the same account).
- **Claim 4, controlled reveal:** HOLDS for confidentiality. It fails on the one-time release being used up; see BP-1.
- **Claim 5, predictor isolation:** HOLDS because it fails closed (SF-2). The code can only start the predictor child under the runner's own account. So the declared remedy, a separate child account, needs a code change and a re-audit, not just a host setting. Until then no real run through `entry.py` can complete.
- **Claim 6, draw integrity:** HOLDS. `draw.py`, `sealbox.py`, `__init__.py` and `medium.py` are unchanged since the seal; the v1 audit checked their hashes by running code, and I did not recompute them.
- **B-1, executables by bare name:** HOLDS inside the tools. SF-4: the documented `python -I -B ...` call is itself a bare name that cmd.exe looks up in the current directory first.
- **B-2, allowlist runs only bound code:** HOLDS for code. SF-3: the database settings it trusts come from unbound working-tree files (`evidence_wiki/config*.json`). Anyone who can push to main could point it at their own server and forge an allow-list entry, which widens S1.
- **S-1, spawn child loads only bound code:** HOLDS.
- **S-1, "a refusal consumes nothing":** **BROKEN (BP-1).**
- **S-2, pre-audit pinning:** HOLDS as stated. SF-1: pins can never be revoked, files from different pinned commits can be mixed, and `entry.py` itself is not pinned.
- **S-3, S-4, S-6, key hygiene:** HOLD. Note: the "not the custodian" check compares names, so an alias like `SKULLPORT\jcrai` passes it.
- **S-5, git hardening:** HOLDS for `entry.py` and `protocol.py`. `firewall_check`'s git calls lack the hardening flags, though none of those commands runs hooks.

**Blocks-PASS finding**
- **BP-1: the runner can still refuse after the one-time key release is used up.**
  - `FirewallRun.open` runs the preflight, then reads the key (`runner.py:607`), deletes it (`:609`) and creates `run_<nonce>` (`:638`).
  - Only after that does `load_package` check the zip bytes against the committed hash, the member rules and the AST audit (`:641`, `:454-495`).
  - The AST audit flags any `.load` or `.loads` attribute (`runner.py:109`), so an innocent `json.loads` in Cosmos's package is enough.
  - The same happens if the operator passes the wrong zip file.
  - `--preflight` never checks the package (`runner.py:937-940`), and custody does not require a preflight before release.
  - After such a refusal, a second release is blocked by the custody log and the committed KEY_RELEASED record (`custody.py:183-186`), and a rerun is blocked because the run directory exists (`runner.py:929`). D2 is then deadlocked for this spec_id.
  - Cosmos, the declared adversary, can trigger this on purpose.
  - A second path: an output-root ACL that lets the account create folders but not files gets a same-account child past the preflight. The child then fails the receipts probe only after the key is spent.
  - No selftest covers either path.
  - Fix: validate the package before the preflight and inside `--preflight`, and make custody require that check before release.

OVERALL: FAIL