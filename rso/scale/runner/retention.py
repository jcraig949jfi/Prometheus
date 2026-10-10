"""Checkpoint retention (C-013-T024; architecture s3.6 retained store, s3.8 verified resume).

The policy is declared in the run manifest (RUN_MANIFEST.json "checkpoint_retention", frozen with the run):

    {"keep_every": K, "keep_last": M}

A chain's output checkpoint at epoch k is KEPT when any of these holds, otherwise it is pruned:
    genesis        k = 0 (the control and every replay start from it; never pruned)
    every Kth      k % K == 0
    last M         head_index - M < k <= head_index   (M >= 2, so the head AND its input stay: resume needs the
                   head checkpoint, s3.8 replay of the head epoch needs the checkpoint before it)
    contest        k or k-1 for any row of the chain's contests.jsonl. The runner records no resolution of a
                   contest, so every recorded contest is treated as open (the conservative reading); k-1 because
                   a challenger or an audit re-executes epoch k from its input.

Only checkpoint objects are pruned. Epoch MANIFEST/SPEC/TRACE objects, the lineage, events and every digest stay:
the chain remains verifiable through its digests, and only the ability to restore state at a pruned epoch is
given up. The object store is shared and content addressed, so an object is deleted only if no chain keeps it.
Each pass is recorded in partitions/<chain>/retention.jsonl (what, how many bytes, under which policy).
"""
import os

from rso.scale.runner import run as RUN
from rso.scale.runner import store as S


def validate_policy(policy):
    if policy is None:
        return None
    if (not isinstance(policy, dict) or set(policy) != {"keep_every", "keep_last"}
            or not all(isinstance(policy[k], int) and not isinstance(policy[k], bool) for k in policy)
            or policy["keep_every"] < 1 or policy["keep_last"] < 2):
        raise ValueError("checkpoint_retention must be {{keep_every: int >= 1, keep_last: int >= 2}}, got {!r}"
                         .format(policy))
    return {"keep_every": policy["keep_every"], "keep_last": policy["keep_last"]}


def _contest_epochs(run_dir, chain_id):
    rows, _ = S.read_jsonl(RUN._log(run_dir, chain_id, "contests.jsonl"))
    out = set()
    for r in rows:
        k = r.get("epoch_index")
        if isinstance(k, int):
            out.update((k - 1, k))
    return {k for k in out if k >= 0}


def keep_epochs(run_dir, chain_id, policy=None):
    policy = policy or validate_policy(RUN.load_manifest(run_dir)[0].get("checkpoint_retention"))
    head = RUN.head(run_dir, chain_id)["head_index"]
    keep = {0, head}
    keep.update(k for k in range(1, head + 1) if k % policy["keep_every"] == 0)
    keep.update(range(max(0, head - policy["keep_last"] + 1), head + 1))
    keep.update(_contest_epochs(run_dir, chain_id))
    return keep


def prune(run_dir, policy=None, dry_run=False):
    """One pass over every chain. policy defaults to the manifest's; a run that declares none is left untouched."""
    manifest, _ = RUN.load_manifest(run_dir)
    policy = validate_policy(policy or manifest.get("checkpoint_retention"))
    if policy is None:
        return {"policy": None, "pruned": [], "dry_run": dry_run}
    store = RUN.object_store(run_dir)
    with S.FileLock(os.path.join(run_dir, ".retention.lock")):
        keep_shas, candidates = set(), []
        for chain_id in RUN.chain_ids(manifest):
            keep = keep_epochs(run_dir, chain_id, policy)
            keep_shas.add(RUN.genesis_checkpoint_sha(run_dir, chain_id))
            h = RUN.head(run_dir, chain_id)
            keep_shas.add(h["head_checkpoint_sha256"])
            for k, row in RUN.publications(run_dir, chain_id).items():
                if k in keep:
                    keep_shas.add(row["output_checkpoint_sha256"])
                else:
                    candidates.append((chain_id, k, row["output_checkpoint_sha256"]))
        # A chain that advances during this pass only widens its keep set, so the snapshot above is conservative.
        pruned, seen = [], set()
        for chain_id, k, sha in sorted(candidates):
            p = store.path(sha)
            if sha in keep_shas or sha in seen or not os.path.exists(p):
                continue
            seen.add(sha)
            pruned.append({"chain_id": chain_id, "epoch_index": k, "sha256": sha, "bytes": os.path.getsize(p)})
        if not dry_run:
            for item in pruned:
                os.remove(store.path(item["sha256"]))
            by_chain = {}
            for item in pruned:
                by_chain.setdefault(item["chain_id"], []).append(item)
            for chain_id, items in by_chain.items():
                S.append_jsonl(RUN._log(run_dir, chain_id, "retention.jsonl"),
                               {"policy": policy, "pruned": items, "kept_epochs": sorted(keep_epochs(
                                   run_dir, chain_id, policy)), "at_utc": RUN.utc_now()})
        return {"policy": policy, "pruned": pruned, "dry_run": dry_run}
