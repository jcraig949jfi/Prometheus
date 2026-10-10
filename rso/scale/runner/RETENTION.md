# Checkpoint retention (C-013-T024, roadmap P-5)

Declared in the run manifest, frozen with the run (a different policy is a different `manifest_id`):

    "checkpoint_retention": {"keep_every": K, "keep_last": M}      # null = keep everything (the T022 behaviour)

`create_run(..., retention={"keep_every": K, "keep_last": M})`. K >= 1, M >= 2 (anything else raises ValueError before
a byte is written). Code: `retention.py` (`validate_policy`, `keep_epochs`, `prune`); the worker calls `prune` after each
head advance (`worker.py _prune`); `python -m rso.scale.runner prune <run_dir> [--dry-run]` applies it by hand.

An epoch's output checkpoint is kept if: it is the genesis checkpoint (the control and every replay start there);
k % K == 0; k is within the last M of the head (M >= 2 keeps the head and its input, which is what resume and the s3.8
replay of the head epoch read); or k / k-1 is named by a row of the chain's `contests.jsonl`.

Choices (reversible, recorded):
- "Open contest": the runner records no contest resolution, so every recorded contest counts as open.
- A contest recorded AFTER its epoch was pruned cannot bring the checkpoint back. With M >= 2 the epochs a fresh
  contest can name (the head, or the head's successor whose input is the head) are always still kept.
- Only checkpoint objects are deleted. Manifest/spec/trace objects, lineage, events and digests stay, so every chain
  keeps its full digest history; what is given up is restoring state at a pruned epoch.
- The store is shared and content addressed: an object is deleted only if no chain keeps it. A pass takes
  `<run>/.retention.lock`; each pass writes `partitions/<chain>/retention.jsonl` (policy, pruned shas and bytes).
- Orphan checkpoints from refused publications (INVALID/STALE bytes are stored before classification) are not
  pruned: they are not in any lineage and are rare.

Evidence: `tests/test_retention.py` (11 tests; fire test `TestFireAfterPruning`: worker killed at head 9 after
epochs 1-3, 5-7 were pruned, forced s3.8 replay VALID, resumed, finished, final replay VALID, run digest == control),
`evidence/MUTATION_RETENTION_T024.json` (4/4 mutants killed), `evidence/GREEN_T024.txt` (whole runner suite).
