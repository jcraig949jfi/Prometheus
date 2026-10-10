"""Run manifest, partition chains and publication (C-013-T022; architecture s3.1, s3.3, s3.5).

Run directory (everything the job needs to resume lives here, none of it in a conversation):

    RUN_MANIFEST.json                 canonical JSON; manifest_id = sha256 of these bytes (s3.1)
    objects/<sha[:2]>/<sha>           content-addressed, write-once, verified on read (s3.6 local layout)
    partitions/<chain_id>/
        GENESIS.json                  moonshot.epoch.genesis.v1, canonical (moonshot/epoch/model.py:53-66)
        HEAD.json                     head_index, head_epoch_digest, head_checkpoint_sha256, generation, state
        publications.jsonl            lineage, one row per head advance (moonshot `publications`)
        outcomes.jsonl                one classification per publication attempt (moonshot `attempts`)
        events.jsonl                  START / PROGRESS / END / RESUME_CHECK / REFUSED (RSO ledger semantics)
        LEASE.json                    lease.py
    supervisor/                       SUPERVISOR.json, events.jsonl, logs
    FINAL_ACCOUNT.json                written once, when every chain is COMPLETE (account.py)

Epoch identity is Moonshot's, computed by Moonshot's code: genesis, SPEC, MANIFEST, work_id and epoch_digest come
from moonshot.epoch.model (make_genesis, derive_spec, execute, verify_epoch), imported, not restated. Publication
follows the moonshot.publish guard (moonshot/nf/INTERFACE_CONTRACT.md:83-92): advance only if the chain is OPEN,
generation = expected, head_index = k-1 and the head checkpoint is the manifest's input; otherwise DUPLICATE /
DISAGREEMENT (chain HALTED) / STALE; bytes that fail verify_epoch are INVALID; a HALTED chain answers HALTED.
"""
import datetime
import json
import os
import subprocess

from moonshot.epoch import canonical as C
from moonshot.epoch import model as M
from rso.scale.runner import engine as E
from rso.scale.runner import lease as L
from rso.scale.runner import store as S

MANIFEST_SCHEMA = "rso.runner.run_manifest.v1"
OPEN, HALTED, COMPLETE = "OPEN", "HALTED", "COMPLETE"
DEFAULT_CAPS = {"cpu_core_s": 3600, "gpu_s": 0, "artifact_bytes": 1 << 30, "cloud_usd_micros": 0}


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _git(args, cwd):
    try:
        return subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, timeout=60,
                              check=True).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def code_identity(code_root=E.REPO):
    sha = _git(["rev-parse", "HEAD"], code_root)
    dirty = _git(["status", "--porcelain", "--", "rso/scale/runner", "moonshot/epoch"], code_root)
    return {"code_sha": sha or "unknown", "runner_paths_dirty": bool(dirty)}


def pdir(run_dir, chain_id):
    return os.path.join(run_dir, "partitions", chain_id)


def object_store(run_dir):
    return S.ObjectStore(os.path.join(run_dir, "objects"))


def events_path(run_dir, chain_id):
    return os.path.join(pdir(run_dir, chain_id), "events.jsonl")


def _head_lock(run_dir, chain_id):
    return S.FileLock(os.path.join(pdir(run_dir, chain_id), ".head.lock"))


def create_run(run_dir, *, name, runtime, params, partitions, epochs, replay_every=10, caps=None,
               question_ref=None, stop_rules=None, code_root=E.REPO):
    """Freeze a run. A change to anything here is a new manifest_id, i.e. a new run (s3.1)."""
    if os.path.exists(os.path.join(run_dir, "RUN_MANIFEST.json")):
        raise FileExistsError("{} already holds a run".format(run_dir))
    engine = E.get_engine(runtime)
    ident = code_identity(code_root)
    store = object_store(run_dir)
    parts, geneses = [], []
    for part in partitions:
        chain_id = "{}-{}".format(name, part["partition_id"])
        cparams = dict(params, **part.get("params", {}))
        init = engine.save_state(engine.init(cparams))
        g = M.make_genesis(chain_id, epochs=epochs, params=cparams, approved_code_sha=ident["code_sha"],
                           initial_checkpoint=init, runtime=runtime)
        store.put(init)
        geneses.append(g)
        parts.append({"partition_id": part["partition_id"], "chain_id": chain_id, "params": cparams,
                      "genesis_sha256": C.sha256_hex(g.bytes)})
    manifest = {
        "schema": MANIFEST_SCHEMA, "name": name, "question_ref": question_ref,
        "engine": {"runtime": runtime, "code_sha": ident["code_sha"], "runner_paths_dirty": ident["runner_paths_dirty"],
                   "entry": "python -m rso.scale.runner", "adapter_tier": "C"},
        "environment": engine.probe(),
        "partitions": parts, "epochs": epochs,
        "epoch_budget": {"unit": "ticks", "ticks_per_epoch": params["ticks_per_epoch"]},
        "checkpoint_every": 1,
        "stop_rules": stop_rules or {"halt_on": ["DISAGREEMENT", "CONTESTED"], "max_worker_starts_per_chain": 8},
        "caps": dict(DEFAULT_CAPS, **(caps or {})),
        "replay_every": replay_every,
        "canonical_digest": {"epoch": C.TAG_RESULT,
                             "run": "rso.runner.run.v1 over manifest_id and each chain's head_epoch_digest and "
                                    "final engine state digest"},
    }
    mbytes = C.canonical_bytes(manifest)
    for g, part in zip(geneses, parts):
        d = pdir(run_dir, part["chain_id"])
        S.atomic_write_bytes(os.path.join(d, "GENESIS.json"), g.bytes)
        S.atomic_write_json(os.path.join(d, "HEAD.json"), {
            "chain_id": part["chain_id"], "head_index": 0, "head_epoch_digest": None,
            "head_checkpoint_sha256": g.obj["initial_checkpoint_sha256"], "head_manifest_sha256": None,
            "generation": 0, "epochs": epochs, "state": OPEN})
    S.atomic_write_bytes(os.path.join(run_dir, "RUN_MANIFEST.json"), mbytes)   # last: its presence = created
    return manifest


def load_manifest(run_dir):
    with open(os.path.join(run_dir, "RUN_MANIFEST.json"), "rb") as f:
        data = f.read()
    return C.parse_canonical(data), C.sha256_hex(data)


def chain_ids(manifest):
    return [p["chain_id"] for p in manifest["partitions"]]


def genesis(run_dir, chain_id):
    with open(os.path.join(pdir(run_dir, chain_id), "GENESIS.json"), "rb") as f:
        gbytes = f.read()
    obj = C.parse_canonical(gbytes)
    return M.Genesis(obj, gbytes, object_store(run_dir).get(obj["initial_checkpoint_sha256"]))


def head(run_dir, chain_id):
    return S.read_json(os.path.join(pdir(run_dir, chain_id), "HEAD.json"))


def _log(run_dir, chain_id, name):
    return os.path.join(pdir(run_dir, chain_id), name)


def publications(run_dir, chain_id):
    """Live lineage rows by epoch index, reconciled with HEAD: HEAD is written first, the row second, so a kill
    between them leaves HEAD one row ahead; the missing row is rebuilt from HEAD's manifest object."""
    rows, _ = S.read_jsonl(_log(run_dir, chain_id, "publications.jsonl"))
    live = {r["epoch_index"]: r for r in rows if not r.get("rejected")}
    h = head(run_dir, chain_id)
    if h["head_index"] > 0 and h["head_index"] not in live:
        m = C.parse_canonical(object_store(run_dir).get(h["head_manifest_sha256"]))
        row = _row(m, h["head_manifest_sha256"], h["generation"], attempt_id=None, reconciled=True)
        S.append_jsonl(_log(run_dir, chain_id, "publications.jsonl"), row)
        live[h["head_index"]] = row
    return live


def _row(m, manifest_sha, generation, attempt_id, reconciled=False):
    return {"chain_id": m["chain_id"], "epoch_index": m["epoch_index"], "work_id": m["work_id"],
            "epoch_digest": m["epoch_digest"], "manifest_sha256": manifest_sha, "spec_sha256": m["spec_sha256"],
            "trace_sha256": m["trace_sha256"], "input_checkpoint_sha256": m["input_checkpoint_sha256"],
            "output_checkpoint_sha256": m["output_checkpoint_sha256"], "generation": generation,
            "attempt_id": attempt_id, "reconciled": reconciled, "at_utc": utc_now()}


def epoch_files(run_dir, chain_id, k):
    """The four canonical files of live epoch k (the shape moonshot.epoch.model.verify_epoch takes)."""
    row = publications(run_dir, chain_id)[k]
    st = object_store(run_dir)
    return {"manifest": st.get(row["manifest_sha256"]), "spec": st.get(row["spec_sha256"]),
            "trace": st.get(row["trace_sha256"]), "checkpoint": st.get(row["output_checkpoint_sha256"])}


def _outcome(run_dir, chain_id, attempt_id, k, outcome, digest, detail=None):
    S.append_jsonl(_log(run_dir, chain_id, "outcomes.jsonl"),
                   {"attempt_id": attempt_id, "epoch_index": k, "outcome": outcome, "epoch_digest": digest,
                    "detail": detail, "at_utc": utc_now()})
    return outcome


def publish(run_dir, chain_id, result, *, expected_generation, lease_token, attempt_id):
    """Classify and, if it is the expected successor, publish one epoch result. Returns the outcome."""
    st = object_store(run_dir)
    files = result.files()
    msha = st.put(files["manifest"])                           # bytes stored first: evidence even if refused
    for key in ("spec", "trace", "checkpoint"):
        st.put(files[key])
    k = result.epoch_index
    g = genesis(run_dir, chain_id)
    errs = M.verify_epoch(files)
    try:
        if C.canonical_bytes(M.derive_spec(g.obj, k)) != files["spec"]:
            errs.append("SPEC is not the one the genesis derives at {}".format(k))
    except ValueError as e:
        errs.append(str(e))
    if result.chain_id != chain_id:
        errs.append("result is for chain {}".format(result.chain_id))
    if errs:
        return _outcome(run_dir, chain_id, attempt_id, k, "INVALID", result.epoch_digest, errs)
    m = C.parse_canonical(files["manifest"])
    with _head_lock(run_dir, chain_id):
        live = publications(run_dir, chain_id)
        h = head(run_dir, chain_id)
        if h["state"] == HALTED:
            return _outcome(run_dir, chain_id, attempt_id, k, "HALTED", m["epoch_digest"])
        if not L.is_holder(run_dir, chain_id, lease_token):
            return _outcome(run_dir, chain_id, attempt_id, k, "STALE", m["epoch_digest"], "not the lease holder")
        if (h["state"] == OPEN and h["generation"] == expected_generation and h["head_index"] == k - 1
                and h["head_checkpoint_sha256"] == m["input_checkpoint_sha256"]):
            new = dict(h, head_index=k, head_epoch_digest=m["epoch_digest"],
                       head_checkpoint_sha256=m["output_checkpoint_sha256"], head_manifest_sha256=msha,
                       generation=h["generation"] + 1, state=COMPLETE if k == h["epochs"] else OPEN)
            S.atomic_write_json(os.path.join(pdir(run_dir, chain_id), "HEAD.json"), new)
            S.append_jsonl(_log(run_dir, chain_id, "publications.jsonl"),
                           _row(m, msha, new["generation"], attempt_id))
            return _outcome(run_dir, chain_id, attempt_id, k, "PUBLISHED", m["epoch_digest"])
        prior = live.get(k)
        if prior and prior["work_id"] == m["work_id"]:
            if prior["epoch_digest"] == m["epoch_digest"]:
                return _outcome(run_dir, chain_id, attempt_id, k, "DUPLICATE", m["epoch_digest"])
            _halt_locked(run_dir, chain_id, h, {"kind": "DISAGREEMENT", "epoch_index": k, "work_id": m["work_id"],
                                                "published": prior["epoch_digest"], "challenger": m["epoch_digest"],
                                                "attempt_id": attempt_id})
            return _outcome(run_dir, chain_id, attempt_id, k, "DISAGREEMENT", m["epoch_digest"])
        return _outcome(run_dir, chain_id, attempt_id, k, "STALE", m["epoch_digest"])


def _halt_locked(run_dir, chain_id, h, grounds):
    S.append_jsonl(_log(run_dir, chain_id, "contests.jsonl"), dict(grounds, at_utc=utc_now()))
    S.atomic_write_json(os.path.join(pdir(run_dir, chain_id), "HEAD.json"), dict(h, state=HALTED))


def halt(run_dir, chain_id, grounds):
    """Fail closed: a disagreement stops the chain until someone resolves it (CONTRACT.md s9 shape)."""
    with _head_lock(run_dir, chain_id):
        _halt_locked(run_dir, chain_id, head(run_dir, chain_id), grounds)


def event(run_dir, chain_id, row):
    S.append_jsonl(events_path(run_dir, chain_id), dict(row, chain_id=chain_id, host=S.HOST, pid=os.getpid()))


def latest_progress(run_dir, chain_id):
    """The newest PROGRESS row of the chain (a worker's position inside its current epoch), or None."""
    p = events_path(run_dir, chain_id)
    if not os.path.exists(p):
        return None
    with open(p, "rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(max(0, size - 8192))
        tail = f.read()
    for raw in reversed(tail.split(b"\n")):
        try:
            row = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            continue
        if row.get("kind") == "PROGRESS":
            return row
    return None
