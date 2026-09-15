"""E-R5-2: GPU job queue + arbiter (SWARM_R5 s3 E-R5-2, operator 19 s6).

  queue     pm:gpu:jobs (consumer group gpu-arbiter); a job = F's envelope (fabric/envelope.py) + {fn 'module:function',
            venv 'w'|'u'|'p', kwargs, exp_id, rows, job_key}
  admission F's envelope.admit(env, kind="gpu", clock=round_clock.read(r)); a refusal is F's envelope.refuse()
            (STAGE_BUDGET_REFUSAL / NO_NEW_WORK_REFUSAL event + PRODUCTION_CANDIDATE stub). No second ceiling table.
  cap       max_gpu_wall_s = min(gpu_budget_s, 600)
  lease     the O5 lease (bus.gpu_lease) is held for the WHOLE child lifetime, so every timing row is taken under it;
            each row is stamped with the lease holder/token/since and `lease_lost`. A busy lease = a LEASE_BUSY row
            and the job is requeued (attempt + 1, at most MAX_ATTEMPTS).
  child     `<nv venv python> -m primordial.nv.gpu_child fn kwargs out.jsonl`; fn(emit, **kwargs) appends rows.
  recorded  per 19 s6. Host-side (arbiter): gpu_device, driver (nvidia-smi), vram_before_mib, vram_peak_mib (polled
            nvidia-smi memory.used), cpu_load_pct. Measurement-side (the job must put them on every timing row):
            batch_size, transfer_included, warm_state, comparison_backend, exactness. A timing row missing any of
            them, or taken with the lease lost, or whose exactness is not true/PASS, gets speed_status INDETERMINATE.
  timeout   at the cap the child tree is killed: rows emitted so far are kept, a status=timeout row carries the child's
            checkpoint path if it wrote one (<out>.ckpt), a TIMEOUT event goes to pm:events and a PRODUCTION_CANDIDATE
            with the measured cost to pm:production_candidates. Never extended.

    python -m primordial.nv.gpuq serve [--max-jobs N]
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time
import uuid

QUEUE, DONE, GROUP = "pm:gpu:jobs", "pm:gpu:jobs:done", "gpu-arbiter"
MAX_GPU_WALL_S = 600
MAX_ATTEMPTS = 3
ROOT = pathlib.Path(__file__).resolve().parents[2]
NV_HOME = pathlib.Path(os.environ.get("PM_NV_VENVS", "C:/Users/jcrai/lab"))
VENVS = {"w": "nv-venv-w", "u": "nv-venv-u", "p": "nv-venv-p"}
MEASURE_FIELDS = ("batch_size", "transfer_included", "warm_state", "comparison_backend", "exactness")
HOST_FIELDS = ("gpu_device", "driver", "vram_before_mib", "vram_peak_mib", "cpu_load_pct")


def venv_python(v: str) -> str:
    if v == "local":                                  # tests: the current interpreter
        return sys.executable
    if v not in VENVS:
        raise ValueError(f"unknown GPU venv {v!r} (w, u, p); gw-venv is never a GPU venv")
    return str(NV_HOME / VENVS[v] / "Scripts" / "python.exe")


def submit(r, fn: str, venv: str, envelope: dict, exp_id: str, rows: str, kwargs: dict | None = None,
           job_key: str = "", attempt: int = 0) -> str:
    job_id = uuid.uuid4().hex[:12]
    r.xadd(QUEUE, {"job_id": job_id, "fn": fn, "venv": venv, "kwargs": json.dumps(kwargs or {}, sort_keys=True),
                   "envelope": json.dumps(envelope, sort_keys=True), "exp_id": exp_id, "rows": rows,
                   "job_key": job_key or job_id, "attempt": str(int(attempt)), "ts": f"{time.time():.3f}"})
    return job_id


def gpu_snapshot() -> dict:
    """nvidia-smi: device, driver, memory used (MiB), utilization. Missing GPU -> nulls."""
    try:
        q = subprocess.run(["nvidia-smi", "--query-gpu=name,driver_version,memory.used,utilization.gpu",
                            "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=5)
        name, drv, mem, util = [x.strip() for x in q.stdout.splitlines()[0].split(",")]
        return {"gpu_device": name, "driver": drv, "vram_used_mib": int(mem), "gpu_util_pct": int(util)}
    except Exception:
        return {"gpu_device": None, "driver": None, "vram_used_mib": None, "gpu_util_pct": None}


def cpu_load_pct() -> float | None:
    try:
        import psutil
        return float(psutil.cpu_percent(interval=0.2))
    except Exception:
        return None


def _kill_tree(pid: int) -> None:
    try:
        import psutil
        p = psutil.Process(pid)
        for q in reversed([p] + p.children(recursive=True)):
            try:
                q.kill()
            except psutil.Error:
                pass
    except Exception:
        pass


class _Writer:
    def __init__(self, path, exp_id, repo):
        from primordial.fabric.rows import RowWriter
        self.w = RowWriter(path, exp_id, commit_every_s=60, repo=repo)

    def write(self, row):
        self.w.write(row)

    def close(self, note=""):
        self.w.close(note=note)


class Arbiter:
    def __init__(self, r, lane: str = "E", repo=ROOT, snapshot=gpu_snapshot, cpu_load=cpu_load_pct, writer=None,
                 max_wall_s: float = MAX_GPU_WALL_S, lease_wait_s: float = 30.0, lease_ttl_s: float = 120.0,
                 poll_s: float = 1.0, log=print):
        self.r, self.lane, self.repo = r, lane, pathlib.Path(repo)
        self.snapshot, self.cpu_load, self.max_wall_s = snapshot, cpu_load, float(max_wall_s)
        self.lease_wait_s, self.lease_ttl_s, self.poll_s, self.log = lease_wait_s, lease_ttl_s, poll_s, log
        self.writer = writer or (lambda path, exp_id: _Writer(path, exp_id, self.repo))
        try:
            r.xgroup_create(QUEUE, GROUP, id="0", mkstream=True)
        except Exception as e:
            if "BUSYGROUP" not in str(e):
                raise

    def _base(self, job: dict, env: dict) -> dict:
        return {"job_id": job["job_id"], "job_key": job.get("job_key") or job["job_id"], "fn": job["fn"],
                "venv": job.get("venv"), "exp_id": job["exp_id"], "campaign_stage": env.get("campaign_stage"),
                "cohort": env.get("cohort"), "predicate_id": env.get("predicate_id"), "queue": QUEUE}

    def _done(self, out: dict) -> dict:
        self.r.xadd(DONE, {"json": json.dumps(out, sort_keys=True, default=str)})
        self.log(f"gpu job {out['job_id']} {out.get('fn')} -> {out['status']}")
        return out

    def run_job(self, job: dict) -> dict:
        from primordial.bus import bus
        from primordial.fabric import envelope as EV
        from primordial.ops import round_clock as RC
        try:
            env = json.loads(job.get("envelope") or "null")
        except ValueError:
            env = None
        clock = RC.read(self.r)
        verdict = EV.admit(env, kind="gpu", clock=clock)
        env_d = env if isinstance(env, dict) else {}
        base = self._base(job, env_d)
        w = self.writer(self.repo / job["rows"], job["exp_id"])
        try:
            if not verdict["ok"]:
                ev = EV.refuse(self.r, self.lane, job, verdict, env)
                w.write({**base, "kind": "gpu_job_end", "status": "aborted", "reason": ev["event"],
                         "reasons": verdict["reasons"]})
                return self._done({**base, "status": "refused", "event": ev["event"], "reasons": verdict["reasons"]})
            cap = min(float(env["gpu_budget_s"]), self.max_wall_s)
            try:
                with bus.gpu_lease(f"gpuq {job['exp_id']} {job['fn']}", ttl_s=self.lease_ttl_s,
                                   wait_s=self.lease_wait_s, r=self.r) as lease:
                    return self._run_leased(job, env, base, cap, lease, w)
            except bus.LeaseBusy as e:
                attempt = int(job.get("attempt", 0) or 0) + 1
                w.write({**base, "kind": "gpu_job_end", "status": "aborted", "reason": "LEASE_BUSY",
                         "detail": str(e)[:300], "attempt": attempt})
                requeued = None
                if attempt < MAX_ATTEMPTS:
                    requeued = submit(self.r, job["fn"], job["venv"], env, job["exp_id"], job["rows"],
                                      json.loads(job.get("kwargs") or "{}"), job_key=base["job_key"], attempt=attempt)
                return self._done({**base, "status": "lease_busy", "attempt": attempt, "requeued_job_id": requeued})
        finally:
            w.close(note=f"(gpu job {job['job_id']})")

    def _run_leased(self, job, env, base, cap, lease, w) -> dict:
        from primordial.fabric import envelope as EV
        before, cpu = self.snapshot(), self.cpu_load()
        peak = before.get("vram_used_mib")
        tmpdir = tempfile.mkdtemp(prefix="gpuq-")
        out = pathlib.Path(tmpdir) / f"{job['job_id']}.jsonl"
        cmd = [venv_python(job["venv"]), "-m", "primordial.nv.gpu_child", job["fn"], job.get("kwargs") or "{}", str(out)]
        penv = dict(os.environ, PYTHONPATH=str(self.repo) + os.pathsep + os.environ.get("PYTHONPATH", ""))
        t0 = time.monotonic()
        errf = open(pathlib.Path(tmpdir) / "stderr.txt", "w+", encoding="utf-8")
        p = subprocess.Popen(cmd, cwd=str(self.repo), env=penv, stdout=subprocess.DEVNULL, stderr=errf)
        status = "ok"
        while p.poll() is None:
            if time.monotonic() - t0 > cap:
                _kill_tree(p.pid)
                p.wait(timeout=30)
                status = "timeout"
                break
            s = self.snapshot().get("vram_used_mib")
            if s is not None and (peak is None or s > peak):
                peak = s
            time.sleep(self.poll_s)
        wall = time.monotonic() - t0
        rc = p.returncode
        errf.seek(0)
        err = errf.read()[-800:]
        errf.close()
        rows = []
        if out.exists():
            for line in out.read_text(encoding="utf-8").splitlines():
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    rows.append({"kind": "bad_row", "raw": line[:300]})
        host = {"gpu_device": before.get("gpu_device"), "driver": before.get("driver"),
                "vram_before_mib": before.get("vram_used_mib"), "vram_peak_mib": peak, "cpu_load_pct": cpu}
        lease_stamp = {"lease_holder": lease.get("holder"), "lease_token": lease.get("token"),
                       "lease_since": lease.get("since"), "lease_lost": bool(lease.get("lost"))}
        n_valid = 0
        for row in rows:
            row = {**base, **host, **lease_stamp, **row}
            if row.get("kind") == "timing":
                missing = [f for f in MEASURE_FIELDS if f not in row]
                exact = row.get("exactness") in (True, "PASS")
                row["missing_fields"] = missing
                row["speed_status"] = "VALID" if (not missing and exact and not row["lease_lost"]) else "INDETERMINATE"
                n_valid += row["speed_status"] == "VALID"
                row["status"] = "record" if row["speed_status"] == "VALID" else "dev"
            else:
                row.setdefault("status", "control")                   # oracle / info / skip rows
            w.write(row)
        end = {**base, **host, **lease_stamp, "kind": "gpu_job_end", "wall_s": round(wall, 3), "cap_s": cap,
               "rows_from_child": len(rows), "timing_rows_valid": n_valid, "returncode": rc}
        if status == "timeout":
            ckpt = pathlib.Path(str(out) + ".ckpt")
            end.update(status="timeout", reason="GPU_WALL_CAP", checkpoint=str(ckpt) if ckpt.exists() else None)
            w.write(end)
            ev = {"event": "TIMEOUT", "lane": self.lane, "job_id": job["job_id"], "job_key": base["job_key"],
                  "fn": job["fn"], "exp_id": job["exp_id"], "cap_s": cap, "wall_s": round(wall, 3),
                  "envelope": env, "ts": round(time.time(), 3)}
            self.r.xadd(EV.EVENTS, {"event": "TIMEOUT", "json": json.dumps(ev, sort_keys=True)})
            stub = {"kind": "PRODUCTION_CANDIDATE", "status": "STUB", "source_event": "TIMEOUT", "lane": self.lane,
                    "job_key": base["job_key"], "fn": job["fn"], "exp_id": job["exp_id"], "reasons": ["GPU_WALL_CAP"],
                    "question": env.get("predicate_id"), "experiment_class": env.get("experiment_class"),
                    "cohort": env.get("cohort"),
                    "requested_cost": {k: env.get(k) for k in ("wall_budget_s", "cpu_budget_s", "gpu_budget_s")},
                    "measured_cost": {"gpu_wall_s": round(wall, 3), "rows_before_cap": len(rows),
                                      "vram_peak_mib": peak}, "checkpoint": end["checkpoint"],
                    "dependencies": [], "ts": ev["ts"]}
            self.r.xadd(EV.CANDIDATES, {"json": json.dumps(stub, sort_keys=True)})
        elif rc != 0:
            end.update(status="aborted", reason="CHILD_ERROR", stderr_tail=err)
            w.write(end)
        else:
            end.update(status="control")
            w.write(end)
        return self._done({**base, "status": end["status"] if end["status"] != "control" else "ok", "wall_s": end["wall_s"],
                           "rows": len(rows), "timing_rows_valid": n_valid, "lease_lost": lease_stamp["lease_lost"]})

    def serve(self, max_jobs: int | None = None, block_ms: int = 5000, idle_exit_s: float | None = None) -> list:
        done, idle0 = [], time.monotonic()
        consumer = os.environ.get("PM_TAG", "gpu-arbiter")
        while max_jobs is None or len(done) < max_jobs:
            got = self.r.xreadgroup(GROUP, consumer, {QUEUE: ">"}, count=1, block=block_ms)
            msgs = [m for _, ms in (got or []) for m in ms]
            if not msgs:
                if idle_exit_s is not None and time.monotonic() - idle0 > idle_exit_s:
                    break
                continue
            mid, job = msgs[0]
            done.append(self.run_job(job))
            self.r.xack(QUEUE, GROUP, mid)
            idle0 = time.monotonic()
        return done


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("serve")
    s.add_argument("--max-jobs", type=int)
    s.add_argument("--idle-exit-s", type=float)
    a = ap.parse_args(argv)
    from primordial.bus import bus
    import redis
    r = redis.Redis.from_url(bus.URL, decode_responses=True, socket_timeout=30)
    Arbiter(r, lane=os.environ.get("PM_LANE", "E")).serve(a.max_jobs, idle_exit_s=a.idle_exit_s)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
