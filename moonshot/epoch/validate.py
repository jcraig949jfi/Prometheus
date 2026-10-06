"""Validation, audit replay, contest / taint resolution (CONTRACT s6, s7). Never a worker's act.

PUBLISHED says only "these bytes are at the head". VALIDATED is written by a validator to
validation/<chain>. A disagreement fails closed (CONTESTED, or TAINTED when descendants exist) until a
resolver replays the disputed work deterministically: UPHELD, OVERTURNED (rewind + archive), or UNRESOLVED."""
import re
import uuid
from enum import Enum

from . import model
from .canonical import canonical_bytes
from .gitio import GitError
from .store import OPEN_CONTEST_STATES, RESOLVER, VALIDATOR


class Resolution(str, Enum):
    UPHELD = "UPHELD"
    OVERTURNED = "OVERTURNED"
    UNRESOLVED = "UNRESOLVED"


def _require(store, role):
    if store.role != role:
        raise PermissionError("a {} store may not do this (needs {})".format(store.role, role))


def chain_status(store, chain_id) -> str:
    """OPEN | COMPLETE | CONTESTED | TAINTED | UNRESOLVED."""
    v = store.chain_view(chain_id)
    if v.halted:
        return v.contest["state"]
    return "COMPLETE" if v.complete else "OPEN"


def _previous_output(store, head, k, genesis_obj):
    if k == 1:
        return genesis_obj["initial_checkpoint_sha256"]
    return (store.manifest(store.commit_at(head, k - 1)) or {}).get("output_checkpoint_sha256")


def validate_chain(store, chain_id, *, replay_indices=(), runner=None) -> dict:
    """Lane C policy: every published epoch byte-verified (digests recompute, lineage links, derived spec);
    the listed epochs also replay-verified by an independent execution."""
    _require(store, VALIDATOR)
    view = store.chain_view(chain_id)
    g, head = view.genesis_obj, view.head_commit
    contest = view.contest if view.halted else None
    prev_ckpt = store.checkpoint(store.commit_at(head, 0))
    entries = []
    for k in range(1, view.head_index + 1):
        c = store.commit_at(head, k)
        pub = store.published(c)
        files = store.epoch_bytes(c)
        errs = model.verify_epoch(files, _previous_output(store, head, k, g))
        if not errs and files["spec"] != canonical_bytes(model.derive_spec(g, k)):
            errs.append("SPEC is not the derived spec")
        if not errs and pub.manifest.get("epoch_index") != k:
            errs.append("manifest epoch_index is not the lineage position")
        checks, state = ([], "INVALID") if errs else (["BYTES"], "VALIDATED")
        if not errs and k in replay_indices:
            if model.execute(g, k, prev_ckpt, runner).epoch_digest == pub.epoch_digest:
                checks.append("REPLAY")
            else:
                state = "MISMATCH"
        if contest and k >= int(contest.get("taint_root", contest.get("epoch_index", 0))):
            state = contest["state"]
        entries.append({"epoch_index": k, "epoch_digest": pub.epoch_digest, "commit": c, "checks": checks,
                        "state": state, "errors": errs})
        prev_ckpt = files["checkpoint"] or b""
    record = {"schema": "moonshot.epoch.validation.v1", "chain_id": chain_id, "head_epoch_index": view.head_index,
              "head_commit": head, "validator": store.actor, "replay_indices": sorted(replay_indices),
              "policy": "lane-c: every epoch byte-verified; listed epochs replay-verified", "epochs": entries}
    store.write_validation(chain_id, record)
    return record


def audit(store, chain_id, epoch_index, *, runner=None, auditor_id="") -> dict:
    """Re-execute one published epoch independently. A mismatch quarantines the auditor's result and opens
    a contest: CONTESTED at the head, TAINTED when descendants exist."""
    _require(store, VALIDATOR)
    view = store.chain_view(chain_id)
    g, head = view.genesis_obj, view.head_commit
    on, parent = store.commit_at(head, epoch_index), store.commit_at(head, epoch_index - 1)
    if epoch_index < 1 or on is None:
        raise ValueError("epoch {} is not published on {}".format(epoch_index, chain_id))
    pub = store.published(on)
    r = model.execute(g, epoch_index, store.checkpoint(parent), runner)
    out = {"chain_id": chain_id, "epoch_index": epoch_index, "auditor": auditor_id,
           "published_epoch_digest": pub.epoch_digest, "audit_epoch_digest": r.epoch_digest}
    if r.epoch_digest == pub.epoch_digest:
        return dict(out, result="MATCH")
    aid = "AUD-{}-{}".format(re.sub(r"[^A-Za-z0-9_-]", "-", auditor_id or "auditor")[:40], uuid.uuid4().hex[:8])
    qref = store.quarantine(chain_id, epoch_index, aid, store.epoch_commit(r, parent, aid))
    state = "TAINTED" if view.head_index > epoch_index else "CONTESTED"
    store.open_contest(chain_id, {
        "schema": "moonshot.epoch.contest.v1", "chain_id": chain_id, "state": state, "epoch_index": epoch_index,
        "taint_root": epoch_index, "work_id": pub.work_id, "published_commit": on,
        "published_epoch_digest": pub.epoch_digest, "reason": "AUDIT_MISMATCH",
        "challengers": [{"epoch_digest": r.epoch_digest, "quarantine_ref": qref, "by": auditor_id,
                         "attempt_id": aid}],
        "detected_by": auditor_id, "head_index_at_detection": view.head_index})
    return dict(out, result="MISMATCH", contest_state=state, quarantine_ref=qref)


def resolve(store, chain_id, *, runners) -> Resolution:
    """Deterministic replay decides; nothing else does. Every runner must agree (independent executors)."""
    _require(store, RESOLVER)
    view = store.chain_view(chain_id)
    c = view.contest
    if not c or c.get("state") not in OPEN_CONTEST_STATES:
        raise ValueError("no open contest on " + chain_id)
    g, head, k = view.genesis_obj, view.head_commit, int(c["epoch_index"])
    on, parent = store.commit_at(head, k), store.commit_at(head, k - 1)
    pub = store.published(on)
    bytes_ok = not model.verify_epoch(store.epoch_bytes(on), _previous_output(store, head, k, g))
    inp = store.checkpoint(parent)
    replays = [model.execute(g, k, inp, run).epoch_digest for run in runners]
    challengers = {ch.get("epoch_digest") for ch in c.get("challengers", [])}
    if not replays or len(set(replays)) != 1:
        verdict = Resolution.UNRESOLVED
    elif bytes_ok and replays[0] == pub.epoch_digest:
        verdict = Resolution.UPHELD
    elif replays[0] in challengers or not bytes_ok:
        verdict = Resolution.OVERTURNED
    else:
        verdict = Resolution.UNRESOLVED
    base = dict(c, resolver=store.actor, replay_digests=replays, resolution=verdict.value)
    if verdict == Resolution.OVERTURNED:
        if not store.rewind(chain_id, head, parent, k).applied:
            raise GitError("chain {} moved during resolution; nothing was rewound".format(chain_id))
        store.close_contest(chain_id, dict(base, state="RESOLVED_OVERTURNED", rejected_head=head))
    elif verdict == Resolution.UPHELD:
        store.close_contest(chain_id, dict(base, state="RESOLVED_UPHELD"))
    else:
        store.close_contest(chain_id, dict(base, state="UNRESOLVED"))
    return verdict
