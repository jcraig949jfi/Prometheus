"""Verified resumption (C-013-T022; architecture s3.8).

Resuming a chain from its head k is accepted only if:
  (1) bytes        the head checkpoint re-hashes to its key, and (k > 0) epoch k's four files pass
                   moonshot.epoch.model.verify_epoch with the lineage link to their input;
  (2) round_trip   engine.load_state then save_state reproduces the checkpoint bytes exactly;
  (3) replay       on the first resumption of the chain, and on a deterministic 1-in-replay_every sample after it,
                   restore checkpoint k-1, re-execute epoch k and require the published epoch_digest
                   (split-run equality, CHECKPOINT_REPLAY_SURVEY.md s3, now across a process boundary);
  (4) environment  this host's engine.probe() equals the manifest's EnvironmentSpec (s3.2).
(1), (2) or (4) failing is INVALID: the worker refuses to resume. (3) failing is CONTESTED and HALTS the chain:
a disagreement fails closed (moonshot/epoch/CONTRACT.md s9 shape); it is never retried into agreement.
"""
import hashlib
import time

from moonshot.epoch import canonical as C
from moonshot.epoch import model as M
from rso.scale.runner import run as RUN
from rso.scale.runner import store as S


def _sampled(manifest_id, chain_id, k, every):
    if every <= 1:
        return True
    h = hashlib.sha256("{}/{}/{}".format(manifest_id, chain_id, k).encode("ascii")).hexdigest()
    return int(h, 16) % every == 0


def _replayed_before(run_dir, chain_id):
    rows, _ = S.read_jsonl(RUN.events_path(run_dir, chain_id))
    return any(r.get("kind") == "RESUME_CHECK" and r.get("replayed") for r in rows)


def verify_resume(run_dir, chain_id, engine, force_replay=False, attempt_id=None, record=True):
    from rso.scale.runner import worker as W                    # the epoch runtime adapter lives with the worker
    m, mid = RUN.load_manifest(run_dir)
    h = RUN.head(run_dir, chain_id)
    k = h["head_index"]
    params = next(p["params"] for p in m["partitions"] if p["chain_id"] == chain_id)
    store = RUN.object_store(run_dir)
    checks = {"environment": engine.probe() == m["environment"]}
    ckpt = None
    try:
        ckpt = store.get(h["head_checkpoint_sha256"])
        ok = True
        if k > 0:
            files = RUN.epoch_files(run_dir, chain_id, k)
            man = C.parse_canonical(files["manifest"])
            prev = RUN.publications(run_dir, chain_id).get(k - 1)
            link = prev["output_checkpoint_sha256"] if prev else RUN.genesis(run_dir, chain_id).obj[
                "initial_checkpoint_sha256"]
            ok = (M.verify_epoch(files, link) == [] and man["epoch_digest"] == h["head_epoch_digest"]
                  and man["output_checkpoint_sha256"] == h["head_checkpoint_sha256"])
        checks["bytes"] = ok
    except (S.IntegrityError, KeyError, ValueError):
        checks["bytes"] = False
    try:
        checks["round_trip"] = ckpt is not None and engine.save_state(engine.load_state(params, ckpt)) == ckpt
    except ValueError:
        checks["round_trip"] = False
    verdict, replayed, replay_cpu = ("VALID" if all(checks.values()) else "INVALID"), False, 0.0
    if verdict == "VALID" and k > 0 and (force_replay or not _replayed_before(run_dir, chain_id)
                                         or _sampled(mid, chain_id, k, m["replay_every"])):
        files = RUN.epoch_files(run_dir, chain_id, k)
        inp = store.get(C.parse_canonical(files["manifest"])["input_checkpoint_sha256"])
        c0 = time.process_time()
        again = M.execute(RUN.genesis(run_dir, chain_id).obj, k, inp, runner=W.moonshot_runtime(engine))
        replay_cpu = time.process_time() - c0
        replayed = True
        checks["replay"] = again.epoch_digest == h["head_epoch_digest"]
        if not checks["replay"]:
            verdict = "CONTESTED"
            RUN.halt(run_dir, chain_id, {"kind": "AUDIT_MISMATCH", "epoch_index": k,
                                         "published": h["head_epoch_digest"], "replay": again.epoch_digest,
                                         "attempt_id": attempt_id})
    out = {"verdict": verdict, "head_index": k, "checks": checks, "replayed": replayed,
           "replay_cpu_s": round(replay_cpu, 6)}
    if record:
        RUN.event(run_dir, chain_id, dict(out, kind="RESUME_CHECK", run_id=attempt_id, at_utc=RUN.utc_now()))
    return out
