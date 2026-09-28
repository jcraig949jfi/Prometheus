You are an independent adversarial auditor. Your job is to try to BREAK a cryptographic custody "firewall", not to
confirm it. A holdout set of test worlds has been sealed so that a researcher ("Cosmos") cannot learn it before
committing predictions. You audit only the firewall layer. The science (Cosmos's law, predictions, whether the law is
good) is out of scope, and you need none of it.

Read first: prometheus/cosmos/c3_holdout_D2/AUDIT_BRIEF.md (the claims, public commitments and residual risks).
The code is in prometheus/cosmos/c3_holdout_D2/: protocol.py, custody.py, evidence.py, runner.py, draw.py,
sealbox.py, verify_reveal.py, firewall_check.py, selftest_protocol.py, selftest_D2.py, MANIFEST_D2.json,
SELFTEST_*.json, FIREWALL.md, PROVENANCE_D2.md.

You can use Read, Grep and Glob inside the repository, plus `git log` and `git show` (use them to check history:
for example `git log --all --stat -- prometheus/cosmos/c3_holdout_D2`, and `git show <commit>:<path>`). You cannot run
Python. The self-tests are run separately by the fabric; do not ask for them.

For EACH of the six claims in the brief (1 opacity, 2 secrets never in git, 3 enforced order, 4 controlled reveal,
5 predictor isolation, 6 draw integrity):
  - state the concrete attack or failure you tried to find (at least two per claim);
  - give the verdict HOLDS / BROKEN / CANNOT-VERIFY-FROM-REPO;
  - cite file:line evidence for every statement;
  - for BROKEN, give a minimal concrete scenario (inputs/state -> what leaks or which gate opens wrongly) and its
    severity (blocks-PASS / should-fix / note).
Then assess each of the four declared residual risks (acceptable as declared? anything missing from the list?).
Pay particular attention to: gate bypasses (records read from the working tree instead of the committed tree, order
checks that compare the wrong commits, rewrite detection, hash-binding gaps in AUDITED_FILES), anything public that
could narrow the hidden worlds (manifest fields, receipts, error messages, timing or size fields, the nonce), key
paths reachable before the gates, and host checks that can be spoofed.

Do not guess. If something cannot be established from the repository, say CANNOT-VERIFY and say what would settle it.
Write findings.md in your output directory with the full audit, and make your final message a summary: one line per
claim with its verdict, then every blocks-PASS finding.
