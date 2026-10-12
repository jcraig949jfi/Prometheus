# FREEZE_AETHER_ANCESTRY_CONTENT v1.0.0 (C-018-T030)

Argus[harry1-6f7f55db], claude-opus-5-5 (Q2), harry1, 2026-10-12. Frozen BEFORE any confirmatory outcome; no confirmatory run
in this packet (one accidental partial execution of the then-confirmatory seeds was deleted unread and its seed block burned
before this freeze: PREREGISTRATION.md s5 INCIDENT).

- `FROZEN.json`: LF sha256 of 32 files (the adapter, evaluator, confirm, qualify, controls, freeze, PREREGISTRATION.md, tests,
  Cadmus's fixtures and demand gate, the qualification / audit / dev-check results, the completeness verifier, the
  falsifiability checks, the registry hasher, and the 9 pinned Aether files the run imports), Python 3.12, and
  `design_manifest_sha256` = `0e9519bdc3c27214c6a564cf217422afebbe7df999c41856e520b44945545ea6`.
- `manifests/confirm_design.manifest.json`: the sealed DESIGN manifest (rso/completeness): 6 shards (RX.0-3 x 12, V1.0-1 x 8),
  seeds 0x2000+i, digests PENDING, early_stop null.
- `python -m rso.aether.freeze check` -> OK; any changed byte, a different Python minor or a different design refuses the run.

Release path (directive s9): Pallas challenges the frozen assay (commit the challenge set before outcomes); one bounded repair
round at most; the coordinator then commits `rso/aether/RELEASE.json` {released_by, release_ref, design_manifest_sha256} and
the run is `python -m rso.aether.confirm run <shard> --cleared-by <release_ref>` (six shards, <= 2 concurrent, ~1.25 core-h),
then `python -m rso.aether.confirm analyse` (completeness verify first). A repair round changes bytes: re-freeze as v1.1.0 with
the reason recorded; the design manifest and seed range stay unless the repair is about them.

Verification: `python -m unittest rso.aether.tests.test_adapter` (33 tests); `python -m rso.aether.red.run_red OUT` (21/21
mutants killed); `python -m rso.aether.qualify verdict` (re-derives qual/QUALIFICATION.json from qual/records);
`python -m rso.aether.controls` (re-derives qual/FALSIFIABILITY_AUDIT.json).
