# Holdout D2 v4 firewall re-audit (commit e6e482ae6)

**Result: FAIL, on one blocking finding (B-1).** I read the code and ran read-only git (`rogit`) only. Nothing was executed, and hash checks were denied in this sandbox. The full audit is in `/home/jcraig/fabric-work/worker.ubu001/attempts/att-64d56c6c4816/out/findings.md`.

**Per-claim verdicts**
- **Claim 1, Opacity: HOLDS.** RESULT.json embeds the HMAC world tags, so the public result hash and chain head can't be brute-forced.
- **Claim 2, Secrets never in git: HOLDS in the repository.** The key-holder scan can't be checked from the repo (CANNOT-VERIFY; see S-2).
- **Claim 3, Enforced order: HOLDS** as gate logic. Grafts and shallow clones are not covered (S-5).
- **Claim 4, Controlled reveal: BROKEN.** B-1 blocks PASS; S-3 is also here.
- **Claim 5, Predictor isolation: HOLDS** for the narrow properties. S-1 (the run can't complete) is an availability problem, not a leak.
- **Claim 6, Draw integrity: HOLDS** for the code. `draw.py`, `sealbox.py` and `__init__.py` are touched only by 95b31a30d, and holdout D is byte-identical to a56ef7787. I couldn't compare the sha256 values myself.

**v4 re-audit items**
- **P1: HOLDS** under `-I -B`. The claim that plain `python entry.py` also works is overstated (N-1): PYTHONPATH, `sitecustomize` and user-site files run before entry.py starts.
- **P2: HOLDS** for Python imports. It depends on no site-packages `.pth` adding a path inside the repo (N-2), which I couldn't check.
- **P3:** the record names match. Running the runner end to end through entry.py fails (S-1).
- **F-GOV, F-FETCH, F-ONCE: HOLD.**
- **F-GITENV: HOLDS as stated** (GIT_* removed, replace refs off), but is incomplete (S-5).
- **F-CWD: BROKEN** (B-1, S-4).
- **F-KH and F-DEST: partial** (S-2, S-3).

**Blocking finding**
- **B-1:** the F-CWD fix covers git but not `icacls`. `custody.py:141` runs `icacls` by bare name inside the key-release process, right after the key is copied to `--dest`. The process environment doesn't set `NoDefaultCurrentDirectoryInExePath`, because `git_env()` only builds a copy for git.
  - **Scenario:** an `icacls.exe` sits at the repo root (committed to main, where branch protection is off, then pulled). The custodian runs the documented repo-relative command `python -I -B prometheus/cosmos/c3_holdout_D2/entry.py custody release-key ...`. The planted file runs as the custodian account with the key path as its first argument, and custody logs a clean release.
  - **Evidence the current directory is searched on M1:** the project's own control, `v4_CWD_control_cwd_git_exe_is_found: true` in `SELFTEST_PROTOCOL.json:77`.
  - **Fix:** call icacls by absolute path from `GetSystemDirectoryW`, or set the file's permissions through the Win32 API.

**Should-fix before any real run**
- **S-1:** through entry.py, the runner can never finish. It also fails after the released key has been read and deleted and the run directory created, so the one-time release is used up permanently.
  - The predictor child can't import `prometheus`: there's no repo path and no import guard in that process.
  - The declared `ChildNotIsolated` refusal fails at that same late point.
- **S-2:** `firewall-check` always runs whatever is committed on origin/main, never the audited code, even after an audit exists. It loads the key, salt and plaintext while doing so.
- **S-3:** if restricting the key file's ACL fails, the key copy is left behind. The file is created with inherited permissions first. The custodian's name is taken from `USERNAME`. The designated account isn't checked to be a single user, so `Everyone` would be accepted.
- **S-4:** `allowlist.py` runs `git` by bare name with the full environment, so the planted-`git.exe` attack works there.
- **S-5:** grafts, shallow files, repo/global git config and fetch hooks are not neutralised.

The notes (N-1 to N-8) and the residual-risk assessment are in findings.md. The declared-risk list leaves out B-1, the irreversibility in S-1, S-2, and the fact that anyone who can push can permanently block the fixed-name records.

No FIREWALL_AUDIT record should be committed.

OVERALL: FAIL