"""The worker: one process, one partition chain, epochs until the chain completes (C-013-T022).

    acquire the partition lease (fenced publication; renewed by a heartbeat thread)
    verify the resume point (resume.py, s3.8); refuse on INVALID, stop on CONTESTED
    for each next epoch k:  refuse if the run's CPU cap is spent (s3.7: caps enforced, not declared)
                            START row -> Moonshot execute() with the engine as runtime, PROGRESS rows at every
                            trace point -> publish (generation CAS) -> END row with the outcome and CPU charged

Rows follow the RSO ledger's semantics (rso/slice001/ledger.py:7-30): every attempt is charged, a START with no END
is INTERRUPTED (its CPU is metered only up to its last PROGRESS row: a lower bound, never zero).
"""
import os
import threading
import time
import uuid

from moonshot.epoch import canonical as C
from moonshot.epoch import model as M
from rso.scale.runner import engine as E
from rso.scale.runner import lease as L
from rso.scale.runner import resume as RS
from rso.scale.runner import run as RUN

EXIT = {"COMPLETE": 0, "PARTIAL": 0, "LEASE_HELD": 3, "HALTED": 4, "CONTESTED": 4, "DISAGREEMENT": 4,
        "INVALID": 5, "CAP_REFUSED": 6, "STALE": 7}


class SimulatedCrash(Exception):
    """Tests only: the worker dies mid-epoch without any cleanup (lease kept, START without END)."""


def moonshot_runtime(engine, progress=None):
    """A Moonshot runtime (input_checkpoint, spec) -> (trace, output_checkpoint) over any engine
    (moonshot/epoch/runtime.py:1-4: pure; the trace carries no clock, host or attempt metadata).

    One epoch = params.ticks_per_epoch engine steps, taken trace_every at a time; after each chunk one canonical
    trace line {"t": ticks into the epoch, "d": engine digest}. progress(ticks_done) is called after each line."""
    def run(input_checkpoint, spec):
        p = spec["params"]
        tpe, every = p["ticks_per_epoch"], p["trace_every"]
        state = engine.load_state(p, input_checkpoint)
        lines, done = [], 0
        while done < tpe:
            n = min(every, tpe - done)
            state = engine.step(state, n)
            done += n
            lines.append(C.canonical_bytes({"t": done, "d": engine.digest(state)}) + b"\n")
            if progress is not None:
                progress(done)
        return b"".join(lines), engine.save_state(state)
    return run


class _Renewer(threading.Thread):
    def __init__(self, run_dir, chain_id, token, every):
        super().__init__(daemon=True)
        self.args_, self.every, self.stop_ = (run_dir, chain_id, token), every, threading.Event()
        self.lost = False

    def run(self):
        while not self.stop_.wait(self.every):
            if not L.renew(*self.args_):
                self.lost = True
                return


def cpu_charged(run_dir, manifest):
    """CPU seconds already charged to the run: every END plus every replay, plus interrupted attempts metered to
    their last PROGRESS row."""
    from rso.scale.runner import account as A
    return A.cpu_totals(run_dir, manifest)["total_cpu_s"]


def work(run_dir, chain_id, *, max_epochs=None, crash_after_ticks=None, ttl_s=L.DEFAULT_TTL_S, force_replay=False):
    m, _mid = RUN.load_manifest(run_dir)
    engine = E.get_engine(m["engine"]["runtime"])
    token = L.acquire(run_dir, chain_id, ttl_s=ttl_s)
    if token is None:
        return {"status": "LEASE_HELD"}
    renewer = _Renewer(run_dir, chain_id, token, max(0.5, ttl_s / 3.0))
    renewer.start()
    crashed = False
    try:
        h = RUN.head(run_dir, chain_id)
        if h["state"] != RUN.OPEN:
            return {"status": h["state"]}
        verdict = RS.verify_resume(run_dir, chain_id, engine, force_replay=force_replay,
                                   attempt_id="{}-resume-{}".format(chain_id, uuid.uuid4().hex[:8]))
        if verdict["verdict"] != "VALID":
            return {"status": verdict["verdict"], "resume": verdict}
        g = RUN.genesis(run_dir, chain_id)
        inp = RUN.object_store(run_dir).get(h["head_checkpoint_sha256"])
        cap = m["caps"]["cpu_core_s"]
        ticks_seen, published = [0], 0
        while h["head_index"] < h["epochs"] and (max_epochs is None or published < max_epochs):
            k = h["head_index"] + 1
            attempt = "{}-e{}-{}".format(chain_id, k, uuid.uuid4().hex[:8])
            used = cpu_charged(run_dir, m)
            if used >= cap:
                RUN.event(run_dir, chain_id, {"kind": "REFUSED", "run_id": attempt, "cap": "cpu_core_s",
                                              "used": round(used, 3), "limit": cap, "at_utc": RUN.utc_now()})
                return {"status": "CAP_REFUSED", "resume": verdict}
            RUN.event(run_dir, chain_id, {"kind": "START", "run_id": attempt, "launch_kind": "EPOCH",
                                          "epoch_index": k, "start_utc": RUN.utc_now()})
            c0, w0 = time.process_time(), time.time()
            base = ticks_seen[0]

            def progress(done, k=k, attempt=attempt, c0=c0, base=base):
                RUN.event(run_dir, chain_id, {"kind": "PROGRESS", "run_id": attempt, "epoch_index": k,
                                              "ticks_done": done, "cpu_s": round(time.process_time() - c0, 6),
                                              "at_utc": RUN.utc_now()})
                ticks_seen[0] = base + done
                if crash_after_ticks is not None and ticks_seen[0] >= crash_after_ticks:
                    raise SimulatedCrash("crash after {} ticks".format(ticks_seen[0]))

            res = M.execute(g.obj, k, inp, runner=moonshot_runtime(engine, progress))
            outcome = RUN.publish(run_dir, chain_id, res, expected_generation=h["generation"], lease_token=token,
                                  attempt_id=attempt)
            RUN.event(run_dir, chain_id, {"kind": "END", "run_id": attempt, "epoch_index": k, "outcome": outcome,
                                          "status": "COMPLETED" if outcome in ("PUBLISHED", "DUPLICATE") else "FAILED",
                                          "cpu_s": round(time.process_time() - c0, 6),
                                          "wall_s": round(time.time() - w0, 6),
                                          "ticks": m["epoch_budget"]["ticks_per_epoch"],
                                          "epoch_digest": res.epoch_digest, "end_utc": RUN.utc_now()})
            if outcome not in ("PUBLISHED", "DUPLICATE"):
                return {"status": outcome, "resume": verdict}
            published += 1
            inp = res.checkpoint
            h = RUN.head(run_dir, chain_id)
        return {"status": "COMPLETE" if h["head_index"] == h["epochs"] else "PARTIAL", "resume": verdict,
                "head_index": h["head_index"]}
    except SimulatedCrash:
        crashed = True
        raise
    finally:
        renewer.stop_.set()
        if not crashed:
            L.release(run_dir, chain_id, token)


def main(run_dir, chain_id):
    r = work(run_dir, chain_id)
    print(r["status"], flush=True)
    return EXIT.get(r["status"], 1)
