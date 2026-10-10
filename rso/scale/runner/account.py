"""Final account (C-013-T022; architecture s3.7): resources, outcome classes and wasted work, from the event shards.

Attempt classes (RSO ledger semantics, rso/slice001/ledger.py:7-30):
    productive     END with outcome PUBLISHED
    rejected       END with any other outcome (DUPLICATE, STALE, INVALID, HALTED, DISAGREEMENT)
    interrupted    START with no END: the worker died. Metered only to its last PROGRESS row (ticks and CPU are
                   LOWER BOUNDS; the remainder after that row is unmetered, never counted as zero)
    verification   s3.8 replays at resume (overhead of verified resumption)
Wasted work = interrupted + rejected: compute that produced no published epoch, the price of worker loss.
Cloud dollars: estimated and billed are two fields that are never merged (both 0 here: local CPU only).
"""
import collections
import os

from moonshot.epoch import canonical as C
from rso.scale.runner import engine as E
from rso.scale.runner import run as RUN
from rso.scale.runner import store as S

RUN_TAG = "rso.runner.run.v1"


def run_digest(manifest_id, chains):
    """chains: [{chain_id, head_epoch_digest, final_state_digest}] in manifest order."""
    return C.tagged_digest(RUN_TAG, {"manifest_id": manifest_id, "chains": chains})


def _attempts(run_dir, chain_id):
    rows, torn = S.read_jsonl(RUN.events_path(run_dir, chain_id))
    att = collections.OrderedDict()
    replay_cpu, refused = 0.0, 0
    for r in rows:
        kind = r.get("kind")
        if kind == "START":
            att.setdefault(r["run_id"], {"start": r, "end": None, "progress": None})
        elif kind == "PROGRESS" and r["run_id"] in att:
            att[r["run_id"]]["progress"] = r
        elif kind == "END" and r["run_id"] in att:
            att[r["run_id"]]["end"] = r
        elif kind == "RESUME_CHECK":
            replay_cpu += r.get("replay_cpu_s") or 0.0
        elif kind == "REFUSED":
            refused += 1
    return att, replay_cpu, refused, torn


def cpu_totals(run_dir, manifest):
    tot = collections.Counter()
    for c in RUN.chain_ids(manifest):
        att, replay_cpu, _, _ = _attempts(run_dir, c)
        tot["verification_cpu_s"] += replay_cpu
        for a in att.values():
            if a["end"]:
                tot["productive_cpu_s" if a["end"]["outcome"] == "PUBLISHED" else "rejected_cpu_s"] += a["end"]["cpu_s"]
            elif a["progress"]:
                tot["interrupted_cpu_s_lower_bound"] += a["progress"]["cpu_s"]
    out = {k: round(tot[k], 6) for k in ("productive_cpu_s", "rejected_cpu_s", "interrupted_cpu_s_lower_bound",
                                         "verification_cpu_s")}
    out["total_cpu_s"] = round(sum(out.values()), 6)
    return out


def final_account(run_dir, write=False):
    m, mid = RUN.load_manifest(run_dir)
    engine = E.get_engine(m["engine"]["runtime"])
    outcomes = collections.Counter()
    wasted = {"interrupted_attempts": 0, "ticks_lower_bound": 0, "cpu_s_lower_bound": 0.0,
              "rejected_attempts": 0, "rejected_cpu_s": 0.0}
    chains, digest_rows, states, torn_total, refused_total = {}, [], set(), 0, 0
    interrupted = []
    for p in m["partitions"]:
        c = p["chain_id"]
        att, _, refused, torn = _attempts(run_dir, c)
        torn_total += torn
        refused_total += refused
        for rid, a in att.items():
            if a["end"]:
                outcomes[a["end"]["outcome"]] += 1
                if a["end"]["outcome"] != "PUBLISHED":
                    wasted["rejected_attempts"] += 1
                    wasted["rejected_cpu_s"] += a["end"]["cpu_s"]
            else:
                outcomes["INTERRUPTED"] += 1
                wasted["interrupted_attempts"] += 1
                pr = a["progress"]
                wasted["ticks_lower_bound"] += pr["ticks_done"] if pr else 0
                wasted["cpu_s_lower_bound"] += pr["cpu_s"] if pr else 0.0
                interrupted.append({"run_id": rid, "chain_id": c, "epoch_index": a["start"]["epoch_index"],
                                    "pid": a["start"].get("pid"), "metered_ticks": pr["ticks_done"] if pr else 0,
                                    "metered_cpu_s": pr["cpu_s"] if pr else 0.0,
                                    "unmetered_remainder": True})
        h = RUN.head(run_dir, c)
        states.add(h["state"])
        final_state = None
        if h["head_index"] > 0:
            ck = RUN.object_store(run_dir).get(h["head_checkpoint_sha256"])
            final_state = engine.digest(engine.load_state(p["params"], ck))
        chains[c] = {"head_index": h["head_index"], "epochs": h["epochs"], "state": h["state"],
                     "generation": h["generation"], "head_epoch_digest": h["head_epoch_digest"],
                     "final_state_digest": final_state}
        digest_rows.append({"chain_id": c, "head_epoch_digest": h["head_epoch_digest"],
                            "final_state_digest": final_state})
    state = "COMPLETE" if states == {RUN.COMPLETE} else ("HALTED" if RUN.HALTED in states else "INCOMPLETE")
    cpu = cpu_totals(run_dir, m)
    wasted["cpu_s_lower_bound"] = round(wasted["cpu_s_lower_bound"], 6)
    wasted["rejected_cpu_s"] = round(wasted["rejected_cpu_s"], 6)
    wasted["note"] = ("interrupted attempts are metered to their last PROGRESS row only; ticks and CPU after it are "
                      "unmetered (a lower bound, never zero)")
    acct = {
        "schema": "rso.runner.final_account.v1", "manifest_id": mid, "state": state,
        "run_digest": run_digest(mid, digest_rows) if state == "COMPLETE" else None,
        "chains": chains,
        "outcomes": {k: outcomes.get(k, 0) for k in ("PUBLISHED", "DUPLICATE", "STALE", "INVALID", "HALTED",
                                                    "DISAGREEMENT", "INTERRUPTED")},
        "wasted": wasted, "interrupted": interrupted,
        "resources": dict(cpu, gpu_s=0, artifact_bytes_retained=RUN.object_store(run_dir).total_bytes(),
                          cloud_usd_estimated=0, cloud_usd_billed_reconciled=0,
                          cpu_cap_s=m["caps"]["cpu_core_s"], within_cpu_cap=cpu["total_cpu_s"] <= m["caps"]["cpu_core_s"]),
        "refused_by_cap": refused_total, "torn_event_rows": torn_total,
    }
    if write and state == "COMPLETE":
        p = os.path.join(run_dir, "FINAL_ACCOUNT.json")
        if not os.path.exists(p):                               # written once
            S.atomic_write_json(p, dict(acct, written_utc=RUN.utc_now()))
    return acct
