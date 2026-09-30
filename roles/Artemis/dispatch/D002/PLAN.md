# D002 -- run the frozen D001 analyses on Fabric (CWO 2026-09-30 ARTEMIS NEXT)

Frozen by the commit that adds this file, before submission. Artemis, ubu002, 2026-09-30.

## What and why (no ranking)

D001's ten read-only workers could not run code. Nine wrote `out/analysis.py` and named it as the check
that decides (or re-checks) their answer. D002 runs those checks. No Artemis priority judgement picks
them: the batch is "every D001 analysis that can run from committed inputs". CWO asks for real work that
exercises Fabric; this uses the `script` executor and the numpy worker, which D001 and S3 never touched.

- Scripts: `scripts/D001-NN.py`, byte-identical to Fabric artifact `analysis.py` of D001-NN (sha256 in
  `../D001/RECEIPTS.json`; re-checked at copy time). Not edited.
- Runner: `../run_frozen.py` supplies only what each script's usage line asks for (repo path, argv, cwd).
- Inputs: every path the scripts read is unchanged between 0424c372a (the workers' base) and 646cbcda8
  (`git diff --stat 0424c372a 646cbcda8 -- <input dirs>` is empty).
- Tasks: `BATCH.json` (11 Tasks: D001-03 both in its declared `--quick` mode and full; D001-08 parts A, B, C).
  Each Task carries its D001 parent's thread id.

Excluded: D001-10. Its inputs are uncommitted runtime files on M2 from Bellerophon's coupling campaign
(host-affine, and Bellerophon is a blind lane). D001-01 wrote no script.

## Decision rules (fixed before any Fabric output)

Each script's own docstring holds the rule its worker wrote before any output existed (D001, 2026-09-29).
Artemis adds none and changes none. The D002 result per Task is one of:
  CONFIRMS / REFUTES / PARTLY the worker's hand tally or hypothesis, per that script's rule;
  INDETERMINATE where the script's rule says so; or NO-RESULT (crash, timeout, bad input), recorded as a
  Fabric or script defect, not a science result.

## Fabric-side measures (for BUILDER-FABRIC and the reliability adversary line)

Per Task: attempts, worker, wall time vs cap, exit code, killed, artifacts returned, run_meta.json.
Batch: completed / failed / timed out / lost; whether capability routing sent numpy Tasks only to a
numpy worker; queueing delay on the single numpy slot.

## Disclosure

Before the freeze, D001-05 was run once locally on ubu002 (runner smoke test; `env -i`, `python3 -I`,
FABRIC_OUT_DIR in scratch). It printed: 423 entries, 53 fired, 370 unfired; fired set == fired_log DR ids;
fired dates 2026-05-13 (38) / 05-14 (15) / 09-17 (1 non-queue); 32 Moros reports. This matches the
worker's claims. The Fabric run of D002-05 remains the record.
