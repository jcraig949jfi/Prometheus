"""D4 transport-study tooling (C-008 T003/T004; ops/campaigns/C-008/prereg/D4_PREREG.md).

    calibrate      synthetic.v1 iterations per second on this host
    make_chains    the coordinator creates a run's chains (fresh namespace)
    bench_worker   one timed worker: sticky round-robin, periodic receipt flush, a WORKER_SUMMARY at exit
    validate_all   the validator byte-verifies every chain, replay-verifies every 10th epoch
    report         the preregistered metrics M1-M7 and bounds B1-B5, from the remote alone

This module only drives the protocol modules and reads what they wrote; it changes none of their rules.
Interpretation fixed before any D4 data (journal 2026-10-06): B2 counts ALL contention retries -- inside
attempts, during polls and during receipt flushes -- the stricter reading of the prereg's M2."""
import platform
import statistics
import time
import uuid

from . import model
from . import runtime as R
from .gitio import AuthError, GitError, RateLimited
from .validate import validate_chain
from .worker import Outcome, Worker

BOUNDS = {"B1": 0.05, "B2": 0.05, "B3": 0.10, "B4": 0.01, "B5": 0}
TRIPWIRE_BYTES_30D = 1 << 30
_PROGRESS = (Outcome.PUBLISHED, Outcome.DUPLICATE, Outcome.DISAGREEMENT, Outcome.STALE,
             Outcome.ABANDONED_RECOVERED)
_FINAL = (Outcome.COMPLETE, Outcome.HALTED, Outcome.REFUSED_UNAPPROVED)


def calibrate(seconds=3.0) -> dict:
    g = model.make_genesis("CAL", epochs=1, params={"work_iterations": 100000, "trace_every": 100000,
                                                    "checkpoint_bytes": 64},
                           approved_code_sha="0" * 40, initial_checkpoint=b"calibration")
    spec, n, t0 = model.derive_spec(g.obj, 1), 0, time.perf_counter()
    while time.perf_counter() - t0 < seconds:
        R.run_synthetic_v1(b"calibration", spec)
        n += 100000
    return {"host": platform.node(), "iterations_per_s": int(n / (time.perf_counter() - t0)),
            "python": platform.python_version(), "platform": platform.platform()}


def make_chains(store, prefix, count, *, iterations, checkpoint_bytes, epochs, approved_code_sha) -> list:
    ids = []
    for i in range(count):
        cid = "{}{:03d}".format(prefix, i)
        g = model.make_genesis(cid, epochs=epochs,
                               params={"work_iterations": iterations, "trace_every": max(1, iterations // 16),
                                       "checkpoint_bytes": checkpoint_bytes},
                               approved_code_sha=approved_code_sha,
                               initial_checkpoint=("moonshot d4 genesis " + cid).encode())
        store.create_chain(g)
        ids.append(cid)
    return ids


def bench_worker(store, worker_id, chains, *, code_sha, approved, spool_dir, leases, duration_s, lease_ttl_s=60,
                 flush_every=10, idle_sleep=0.5, start=0, host_label=None) -> dict:
    """Run until the deadline; then finish the attempt in flight, flush receipts and append one
    WORKER_SUMMARY (the polls and flushes no attempt receipt carries)."""
    w = Worker(store, worker_id, code_sha=code_sha, approved=approved, spool_dir=spool_dir, leases=leases,
               lease_ttl_s=lease_ttl_s, host_label=host_label)
    t_start, deadline = time.time(), time.time() + duration_s
    polls, flags, attempts, since_flush, detail = {}, set(), 0, 0, ""
    order = chains[start % len(chains):] + chains[:start % len(chains)]
    try:
        attempts += len(w.recover())
        done, i, idle = set(), 0, 0
        while time.time() < deadline and len(done) < len(order):
            cid = order[i % len(order)]
            if cid in done:
                i += 1
                continue
            r = w.run_attempt(cid)
            if r.receipt:
                attempts += 1
                since_flush += 1
            else:
                polls[r.outcome.value] = polls.get(r.outcome.value, 0) + 1
            if r.outcome in _FINAL:
                done.add(cid)
            if r.outcome != Outcome.PUBLISHED:
                i += 1                                       # sticky: stay on a chain while it publishes
            idle = 0 if r.outcome in _PROGRESS else idle + 1
            if idle >= len(order):
                time.sleep(idle_sleep)
                idle = 0
            if since_flush >= flush_every:
                w.flush_receipts()
                since_flush = 0
    except RateLimited as e:
        flags.add("rate_limited")
        detail = str(e)[:500]
    except AuthError as e:
        flags.add("auth_error")
        detail = str(e)[:500]
    try:
        w.flush_receipts()
    except GitError as e:
        flags.add("final_flush_failed")
        detail = detail or str(e)[:500]
    summary = summarize(w, t_start=t_start, attempts=attempts, polls=polls, flags=flags, detail=detail)
    store.append_receipts(worker_id, {summary["attempt_id"]: summary})
    return summary


def summarize(w, *, t_start, attempts, polls=None, flags=(), detail="") -> dict:
    """A worker's WORKER_SUMMARY: every git operation its store ran (polls and flushes included), and the
    attempts still pending in its spool. Call after the last flush; its own append is not counted."""
    store, ops = w.store, w.store.ops.ops
    return {
        "schema": "moonshot.epoch.worker_summary.v1", "kind": "WORKER_SUMMARY",
        "attempt_id": "S-{}-{}".format(w.worker_id, uuid.uuid4().hex[:8]), "worker_id": w.worker_id,
        "host": w.host_label or platform.node(), "platform": platform.platform(), "python": platform.python_version(),
        "code_sha": w.code_sha, "layout": store.layout, "leases": bool(w.leases), "lease_ttl_s": w.lease_ttl_s,
        "started_unix": int(t_start), "ended_unix": int(time.time()), "attempts": attempts, "polls": dict(polls or {}),
        "executions": w.executions, "pending_attempts": sum(1 for a in w._spooled() if a.state != "TERMINAL"),
        "flags": sorted(flags), "detail": detail,
        "git_ops_total": len(ops), "push_attempts_total": store.push_attempts,
        "contention_retries_total": store.contention_retries,
        "coordination_wall_total_s": round(sum(o.wall_s for o in ops), 6),
        "bytes_pushed_total": sum(o.bytes_sent for o in ops), "bytes_fetched_total": sum(o.bytes_received for o in ops),
        "note": "totals exclude this summary's own append push",
    }


def validate_all(store, prefix, replay_every=10) -> dict:
    counts, chains = {}, sorted(s[len("chains/"):] for s in store.list_slots("chains/") if s.startswith("chains/" + prefix))
    for cid in chains:
        head = store.chain_view(cid).head_index
        rec = validate_chain(store, cid, replay_indices=[k for k in range(1, head + 1) if k % replay_every == 0])
        for e in rec["epochs"]:
            counts[e["state"]] = counts.get(e["state"], 0) + 1
    return {"chains": len(chains), "states": counts}


def _pct(xs, q):
    xs = sorted(xs)
    if not xs:
        return None
    k = max(0, min(len(xs) - 1, int(round(q * (len(xs) - 1)))))
    return xs[k]


def report(store, prefix, *, wall_s, repo_bytes=None, refs=None, extra=None) -> dict:
    """The preregistered metrics (D4_PREREG s5) and bounds (s6). Reads the remote only."""
    records = store.read_receipts()
    summaries = [r for r in records if r.get("kind") == "WORKER_SUMMARY"]
    receipts = [r for r in records if r.get("kind") != "WORKER_SUMMARY"]
    chains = sorted(s[len("chains/"):] for s in store.list_slots("chains/") if s.startswith("chains/" + prefix))
    published, validated, states = 0, 0, {}
    for cid in chains:
        published += store.chain_view(cid).head_index
        v = store.validation(cid)
        for e in (v or {}).get("epochs", []):
            states[e["state"]] = states.get(e["state"], 0) + 1
            validated += e["state"] == "VALIDATED"
    outcomes = {}
    for r in receipts:
        outcomes[r["outcome"]] = outcomes.get(r["outcome"], 0) + 1
    executed = [r for r in receipts if "execute_s" in r.get("timings", {})]
    started = [r for r in receipts if r["outcome"] not in ("REFUSED_UNAPPROVED", "HALTED")]
    pending = sum(s.get("pending_attempts", 0) for s in summaries)
    coord = sum(s["coordination_wall_total_s"] for s in summaries)
    execute = sum(r["timings"]["execute_s"] for r in executed)
    retries = sum(max(0, r.get("push_attempts_cas", 0) - 1) for r in receipts) + \
        sum(s.get("contention_retries_total", 0) for s in summaries)
    claim = [r["timings"]["claim_s"] for r in executed if "claim_s" in r["timings"]]
    med_exec = statistics.median([r["timings"]["execute_s"] for r in executed]) if executed else None
    abandoned = outcomes.get("ABANDONED_RECOVERED", 0) + outcomes.get("STALE", 0) + pending
    moved = sum(s["bytes_pushed_total"] + s["bytes_fetched_total"] for s in summaries)
    rate_limited = sum(1 for s in summaries if "rate_limited" in s.get("flags", []))
    m = {
        "M1_coordination_fraction": coord / (coord + execute) if coord + execute else None,
        "M2_retries_per_published": retries / published if published else None,
        "M3_claim_latency_ratio": (_pct(claim, 0.95) / med_exec) if claim and med_exec else None,
        "M4_abandonment_rate": abandoned / (len(started) + pending) if started or pending else None,
        "M5_bytes_per_published": moved / published if published else None,
        "M5_bytes_per_validated": moved / validated if validated else None,
        "M6_repo_bytes_per_published": repo_bytes / published if repo_bytes is not None and published else None,
        "M6_repo_bytes_per_validated": repo_bytes / validated if repo_bytes is not None and validated else None,
    }
    m["M7_projected_bytes_30d"] = m["M6_repo_bytes_per_published"] * (published / wall_s) * 86400 * 30 \
        if m["M6_repo_bytes_per_published"] is not None and wall_s else None
    checks = {
        "B1": m["M1_coordination_fraction"] is not None and m["M1_coordination_fraction"] <= BOUNDS["B1"],
        "B2": m["M2_retries_per_published"] is not None and m["M2_retries_per_published"] <= BOUNDS["B2"],
        "B3": m["M3_claim_latency_ratio"] is not None and m["M3_claim_latency_ratio"] <= BOUNDS["B3"],
        "B4": m["M4_abandonment_rate"] is not None and m["M4_abandonment_rate"] <= BOUNDS["B4"],
        "B5": rate_limited == BOUNDS["B5"],
    }
    failed = [b for b, ok in checks.items() if not ok]
    out = {
        "schema": "moonshot.epoch.d4_report.v1", "namespace": store.namespace, "layout": store.layout,
        "prefix": prefix, "wall_s": wall_s, "workers": len(summaries), "chains": len(chains),
        "published": published, "validated": validated, "validation_states": states, "outcomes": outcomes,
        "attempts": len(receipts), "executed": len(executed), "pending_at_end": pending,
        "wasted_execution_share": outcomes.get("DUPLICATE", 0) / len(executed) if executed else None,
        "disagreements": outcomes.get("DISAGREEMENT", 0), "coordination_wall_s": round(coord, 3),
        "execute_s": round(execute, 3), "median_execute_s": med_exec, "p95_claim_s": _pct(claim, 0.95),
        "retries_counted": retries, "bytes_moved": moved, "repo_bytes": repo_bytes, "refs": refs,
        "rate_limited_workers": rate_limited, "metrics": m, "bounds": BOUNDS, "checks": checks,
        "verdict": "ADEQUATE" if not failed else "RECONSIDER", "failed_bounds": failed,
        "tripwire_T1_ok": None if m["M7_projected_bytes_30d"] is None else m["M7_projected_bytes_30d"] <= TRIPWIRE_BYTES_30D,
        "per_host_median_execute_s": _per_host(executed),
    }
    if extra:
        out.update(extra)
    return out


def _per_host(executed) -> dict:
    by = {}
    for r in executed:
        by.setdefault(r.get("host", "?"), []).append(r["timings"]["execute_s"])
    return {h: round(statistics.median(v), 3) for h, v in sorted(by.items())}
