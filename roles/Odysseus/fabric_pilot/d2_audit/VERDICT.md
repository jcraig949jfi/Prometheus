# Holdout D2 firewall audit: verdict FAIL (no audit record committed)

- **Auditor:** Odysseus (ubu001), operator-designated, via brief `prometheus/cosmos/c3_holdout_D2/AUDIT_BRIEF.md`
  @ e66f57208.
- **Date:** 2026-09-28.
- **Audited commit:** bec1d275c (origin/main). The package is byte-identical to e66f57208, the last commit touching
  `c3_holdout_D2`.
- **Scope:** the firewall layer only. No law, predictions or science were read or needed.
- **Per the brief:** a FAIL is not recorded in `protocol/`. These findings go to Nestor (cc operator), Nestor
  fixes, and the re-audit binds the new code hashes.

## Method (Agent Fabric science pilot)

1. **Two independent reviewers.** Fabric tasks tsk-fe7759a0e631 (A) and tsk-04cdac1aa3be (B) each ran an isolated
   Claude worker (claude-opus-5-5):
   - empty context, no seat memory, read-only repository;
   - same adversarial prompt (`roles/Odysseus/prompts/2026-09-28_fabric/03_D2_AUDIT_WORKER_PROMPT.md`);
   - no Python, no knowledge of each other.

   Their full reports are `reviewer_A_findings.md` and `reviewer_B_findings.md`.
2. **Self-tests.** They ran as fabric `script` tasks on a worker advertising `python.numpy python.scipy`:
   - tsk-f25890f733c7 `selftest_protocol`: PASS, 34 checks plus 3 defect controls, `hidden_set_or_key_touched`
     false;
   - tsk-fd55d207035f `selftest_D2`: PASS, 10 checks plus 13 negative controls.

   Both outputs are in this directory. The self-tests pass, but none of them exercises the attacks below.
3. **Odysseus's adjudication.** I independently derived F1 (the import-closure analysis) before reading either
   report. I then reproduced every blocking mechanism myself on synthetic fixtures (`odysseus_verify.py`, output
   `odysseus_verify_output.json`). No secret, key or hidden-set file was touched.

## Claims

| # | claim | verdict |
|---|---|---|
| 1 | Opacity | HOLDS. Note: `ciphertext_bytes` reveals the unpadded plaintext length, one aggregate of well under 1 bit per world. Pad before a future seal. |
| 2 | Secrets never in git | HOLDS for files across all history (`git log --all`: no key/salt/plaintext-shaped files). Content-level CANNOT-VERIFY without the key holder, because `firewall_check` searches branch tips only. |
| 3 | Enforced order | **BROKEN**: F1, F3, F4 |
| 4 | Controlled reveal | HOLDS in its own logic, but inherits F1, F3 and F4 because it relies on `check_gates` |
| 5 | Predictor isolation | **BROKEN**: F2. The literal sub-claims hold (no key in the child's memory, pickle-free pipe, type-name errors), but the child can read the secrets from disk. |
| 6 | Draw integrity | HOLDS. Verified: `draw.py`, `sealbox.py` and `__init__.py` on main hash (LF) to the at-draw values in the manifest, and `medium.py` to `family_src_sha256`. Note: a redraw after reveal needs numpy 2.2.6, which has no wheel for Python 3.14. |

## Blocking findings (all reproduced by Odysseus)

**F1: the audit's hash binding does not cover code that runs in the key-holding processes.**
- **Found by:** A, B and Odysseus independently.
- **Gap:** `AUDITED_FILES` (`protocol.py:58-64`) omits five files that the runner, custody and evidence processes
  import before any gate: `prometheus/cosmos/c3/probe.py`, plus the `__init__.py` of `prometheus/`,
  `prometheus/cosmos/`, `prometheus/cosmos/c3/` and `prometheus/cosmos/c3_holdout_D/`.
- **Who can change them:**
  - `probe.py` and `c3/__init__.py` were committed by Cosmos (940b486f2), and `cosmos/__init__.py` by 70ce535a2.
  - `probe.py` computes the P1 statistic (`certify.py:15`).
- **Attack:** after an audit PASS, an edit to any of these files leaves the audit fresh, and the edited code then
  runs in the key-holding runner process, since `runner.py:72` imports it and `runner.py:460` decrypts. That code
  could read the plaintext or change certification results.
- **Variant (A):** committing `c3_holdout_D2/protocol/__init__.py` (in the records directory) shadows
  `protocol.py`, which replaces the gate module itself. Reproduced as V5.
- **Fix:**
  - At the start of every entry point (runner, custody, evidence), after imports and before any gate, fail closed
    unless every loaded `prometheus.*` module file is in `AUDITED_FILES` and hash-matches.
  - Add the five files to `AUDITED_FILES`.
  - Refuse if any `.py` exists under `protocol/`.

**F2: the prediction package can read the secrets, and the AST audit can be bypassed.**
- **Found by:** A and B. Reproduced as V1 and V2.
- **Access:** the child is a `spawn` process running as the same OS account as the custodian, so the secret paths
  (public in `custody.py:39-40`) and the released key file are readable.
- **The AST audit only flags bare-name calls:**
  - `np.fromfile('/.../hidden_D2.plain.json')` gives 0 flags;
  - `f=[open][0]; f(path)` gives 0 flags;
  - a bare `open()` is flagged (control).
- **The audit only reads `.py` files, but every zip member is extracted.** A sourceless `.pyc` on the package
  path imports and runs (V2), so it is never audited and cannot be read by Nestor either.
- **Declared residual risk 2 is not acceptable as written.**
- **Fix:**
  - Reject package members other than `.py`, `.json` and `.txt`.
  - Run the child under a dedicated low-privilege account that cannot read the secrets directory, the released
    key, the receipts or the repo.
  - Have the runner **verify** this: the child must fail to open the key path before it is given any world.

**F3: `origin/main` can be shadowed by a tag.**
- **Found by:** B. Reproduced as V4.
- **Cause:** `DEFAULT_REF = "origin/main"`, and a tag named `origin/main` takes precedence over the
  remote-tracking branch. A default fetch pulls tags.
- **Attack:** pushing that tag makes every gate read a history of the attacker's choosing, for example one
  containing a forged PASS audit.
- **Fix:** use `refs/remotes/origin/main` everywhere, and refuse if the short name is ambiguous.

**F4: a record can be replaced through a merge and still count as "added once".**
- **Found by:** A and B. Reproduced as V3.
- **Cause:** `_commits_touching` uses `git log ref -- path` with default history simplification.
- **Reproduction:** a side branch forked before the record adds a forged version, and a merge taking the side's
  version leaves the forged content on main. Plain `git log` then sees 1 commit, so the gate accepts it;
  `--full-history` sees 3.
- **Fix:** use `--full-history` (and refuse any merge commit that touches a record path).
- **Severity:** B graded this should-fix. I grade it blocking, because it directly defeats "added once and never
  modified", which claim 3 depends on.

## Should-fix (same round)

- **S1: records are unauthenticated.** Every commit uses the same git identity, and anyone who can push can commit
  `FIREWALL_AUDIT.json`. Because records are immutable, a forged early PASS would also block the real audit
  forever.

  Options:
  - signed commits;
  - Nestor confirms the audit record's sha256 out of band (comms from Odysseus) and the gate checks it against a
    custodian allow-list on M1.
- **S2: there is no re-audit path after a PASS.** Add-once plus the stale check means any code change after a PASS
  deadlocks D2. Use versioned audit records (the newest one wins, and the order constraints apply to it).
- **S3: custody reveal re-verification is thin.** `custody.reveal` should re-verify the receipt chain, that the run
  closed, and the package hash, not only `RESULT_SEAL.json` (B-F6).
- **S4: runs can be cherry-picked.** The runner can be run many times with unbound parameters, and the custodian
  picks which run to seal. Bind the run parameters in the designation, and allow one run per designation.
- **S5: freshness and hygiene.**
  - Fetch before the gate check, and pin the seal commit and `spec_id` in code.
  - Delete the released key copy after the run.
  - `firewall_check --git-ref $(git rev-list --all)` should cover all history.
  - Check that `.pyc` caches and installed libraries are not writable by the package account.

## Booleans requested from Nestor (key-holder checks)

1. `firewall_check` over all history (`git rev-list --all`) is all clean.
2. The secrets directory is not synced by any cloud client.
3. GitHub branch protection on main blocks force-push and deletion.
4. Once the key is released, no copy of it remains after the run (confirm this when the runner is used).

## What this audit does not establish

- It says nothing about Cosmos's law or predictions.
- The self-tests ran with numpy 2.5.3 (ubu001 has Python 3.14, and numpy 2.2.6 has no wheel for it). That is fine
  for synthetic fixtures, but it is not the at-draw environment.
- Residual risk 1 (the key holder can decrypt directly) is accepted as declared. It should say explicitly that
  "key holder" includes any repo code that the operator account runs on M1. That is F1's lesson.
