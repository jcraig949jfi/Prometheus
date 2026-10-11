"""E3-R driver (E3R-A1 item 9 = red-team A9): executes the frozen run order RESUMABLY (every search is cached in the
per-world KPA1 files; re-invoking continues), with <= `--workers` concurrent worker processes (never two on the same
world file), a memory check before a second concurrent worker, the OE-scratch rules of A1, a hard stop and the compute
envelopes. Then writes <out>/E3R_RESULT.json (e3r.analyse) with UTC start / end.

ORDER (A9):
  1. off_xabs, seed 0. Reproduction ASSERT (halts on failure, status HALT_REPRODUCTION): the re-used off_frozen cell
     equals the frozen pooled file and --expect-off-frozen (7). off_xabs vs --expect-off-xabs (9) is EXPECTED, pending
     reproduction: reported, NOT asserted (independent review v2: the reviewer's 9/15 used hand-spelled stones).
  2. the OE R1 searches, then the OE chains of on_frozen and on_xabs, seed 0 (the two cells share the OE R1 searches).
  3. OE scratch, LAZILY (A1.4): only while it is NEEDED (some OE cell, at a seed whose cells are complete, has
     5q >= 4n) and the label is NOT DETERMINED (its LO and HI bounds differ at some seed). Order: Int-output families
     first, then family_id. Cap 3,600 CPU-s each (CENSORED above). Searches never needed stay NOT_RUN ("not needed" is
     complete for the label).
  4. seeds 1 and 2: off_xabs, on_frozen, on_xabs (R1 + chain; the scratch re-uses seed 0); off_frozen rows of the
     frozen E3-KP are re-used (run only if absent). Then step 3 again (the need can change).
  5. ONE extension (A1.5): if the label is still bound-indeterminate, each CENSORED OE scratch (same order) is re-run
     once with cap 14,400 CPU-s (deterministic search: a re-run equals continuing; the 3,600 s already spent is lost
     and is debited), until the label is determined.
  6. priority 2 (A8, `--with-fallback-off`): on_xabs with the readout fallback OFF, seed 0.
ENVELOPES: OE scratch <= 16 core-h (a search is started only if spent + its cap fits); the driver's whole spend
<= --envelope-core-h minus --debit-core-h (concurrent E2 / AR-1 load). HARD STOP (--deadline, default
2026-10-13T09:27Z): no job starts after it; running jobs (this driver's own processes) are stopped at it; the result
is then computed from what is complete (REPAIR_CLASS = INCOMPLETE with bounds where required items are missing).
NOT BEFORE (--not-before, default 2026-10-11T11:30Z): the driver exits with status WAIT before it.

Production (from roles/Aphrodite/beta04; OMP_NUM_THREADS=1):
  python -m tfs1.e3.e3r_run --root foundry/production --kp-frozen runs/kp_production --out runs/e3r_production \\
      --workers 2 --expect-off-frozen 7 --expect-off-xabs 9 --with-fallback-off
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from tfs1.e3 import e3_known_positive as KP
from tfs1.e3 import e3r as R
from tfs1.e3 import worlds as WD

BETA04 = Path(__file__).resolve().parents[2]


def _ts(s: str) -> float:
    return datetime.strptime(s.replace("Z", ""), "%Y-%m-%dT%H:%M" + (":%S" if s.count(":") == 2 else "")) \
        .replace(tzinfo=timezone.utc).timestamp()


class Driver:
    def __init__(self, a):
        self.a = a
        self.root, self.out, self.frozen = a.root, Path(a.out), a.kp_frozen
        self.out.mkdir(parents=True, exist_ok=True)
        man = WD.world_manifest(self.root)
        self.worlds = a.worlds.split(",") if a.worlds else sorted(
            w for w in man["worlds"] if KP.KP(self.root, w).admitted())
        self.state_p = self.out / "E3R_STATE.json"
        self.state = json.loads(self.state_p.read_text()) if self.state_p.exists() else {
            "utc_start": R.utc_now(), "jobs": [], "ledger_s": {"oe_scratch": 0.0, "other": 0.0}}
        self.state.setdefault("invocations", []).append(R.utc_now())
        self.running: List[Dict] = []
        self._frozen_keys: Dict[str, set] = {}
        self.deadline = _ts(a.deadline)
        self.stopped = None

    # ---------------------------------------------------------------- bookkeeping
    def save(self):
        self.state["utc_last_write"] = R.utc_now()
        tmp = self.state_p.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.state, indent=1, sort_keys=True))
        os.replace(tmp, self.state_p)

    def spent(self) -> float:
        return sum(self.state["ledger_s"].values())

    def envelope_left(self) -> float:
        return (self.a.envelope_core_h - self.a.debit_core_h) * 3600.0 - self.spent()

    def _snapshot(self, w) -> Dict:
        d = KP._load(self.out, w)
        return {"s": set(d["searches"]), "c": {k: v["row"].get("cpu_s", 0) for k, v in
                                               d.get("censored_searches", {}).items()}}

    def _debit(self, job):
        d = KP._load(self.out, job["world"])
        before = job["snap"]
        if job["world"] not in self._frozen_keys:          # searches imported from the frozen cache are not debited
            self._frozen_keys[job["world"]] = set(KP._load(self.frozen, job["world"])["searches"])
        fk = self._frozen_keys[job["world"]]
        cpu = sum(v.get("cpu_s", 0) or 0 for k, v in d["searches"].items() if k not in before["s"] and k not in fk)
        cpu += sum(v["row"].get("cpu_s", 0) for k, v in d.get("censored_searches", {}).items()
                   if before["c"].get(k) != v["row"].get("cpu_s", 0))
        self.state["ledger_s"][job["cat"]] = round(self.state["ledger_s"].get(job["cat"], 0) + cpu, 2)
        job["rec"]["cpu_new_searches_s"] = round(cpu, 2)

    # ---------------------------------------------------------------- jobs
    def argv(self, world, cell, seed, stage, family=None, cap=None, fallback=True) -> List[str]:
        cfg = R.cell_cfg(cell, seed, self.a.budget, fallback)
        v = [sys.executable, "-m", "tfs1.e3.e3_known_positive", "--root", str(self.root), "--world", world,
             "--out", str(self.out), "--seed-cache-from", str(self.frozen), "--budget", str(self.a.budget),
             "--seed", str(seed), "--stage", stage, "--extract", cfg.extract]
        if cfg.oe:
            v.append("--oe")
        if not fallback:
            v += ["--fallback", "off"]
        if family:
            v += ["--family", family]
        if cap:
            v += ["--scratch-cpu-cap", str(cap)]
        return v

    def _start(self, job):
        import psutil
        if any(r["world"] == job["world"] for r in self.running):
            return False
        if self.running and psutil.virtual_memory().available < self.a.min_free_gb * 1e9:
            return False                                   # memory check before a 2nd concurrent worker
        job["snap"] = self._snapshot(job["world"])
        logd = self.out / "logs"
        logd.mkdir(exist_ok=True)
        job["log"] = open(logd / ("%s_%s.log" % (job["name"].replace("/", "_"), int(time.time()))), "w")
        env = dict(os.environ, OMP_NUM_THREADS="1")
        job["rec"] = {"name": job["name"], "world": job["world"], "cat": job["cat"], "utc_start": R.utc_now()}
        job["cmds"] = list(job["cmds"])
        job["proc"] = subprocess.Popen(job["cmds"].pop(0), cwd=str(BETA04), env=env, stdout=job["log"],
                                       stderr=subprocess.STDOUT)
        self.running.append(job)
        return True

    def _poll(self):
        import psutil
        for job in list(self.running):
            rc = job["proc"].poll()
            if rc is None:
                continue
            if rc == 0 and job["cmds"]:
                env = dict(os.environ, OMP_NUM_THREADS="1")
                job["proc"] = subprocess.Popen(job["cmds"].pop(0), cwd=str(BETA04), env=env, stdout=job["log"],
                                               stderr=subprocess.STDOUT)
                continue
            job["log"].close()
            job["rec"].update({"utc_end": R.utc_now(), "returncode": rc})
            self._debit(job)
            self.state["jobs"].append(job["rec"])
            self.running.remove(job)
            self.save()
            if rc != 0 and not self.stopped:
                self.stopped = "JOB_FAILED (%s, rc %s; see %s)" % (job["name"], rc, job["log"].name)
        if time.time() >= self.deadline and self.running:
            self.stopped = "HARD_STOP"
            for job in list(self.running):             # this driver's OWN processes only
                try:
                    p = psutil.Process(job["proc"].pid)
                    for c in p.children(recursive=True):
                        c.kill()
                    p.kill()
                except psutil.NoSuchProcess:
                    pass

    def run_jobs(self, jobs: List[Dict], gate=None):
        """Run jobs with <= workers concurrency; `gate()` (if given) is re-checked before each start: a job is started
        only while gate() is True. Stops at the hard stop and when the envelope is exhausted."""
        queue = list(jobs)
        while queue or self.running:
            self._poll()
            if self.stopped:
                while self.running:
                    time.sleep(1)
                    self._poll()
                return
            started = False
            if queue and len(self.running) < self.a.workers:
                if time.time() >= self.deadline:
                    self.stopped = "HARD_STOP"
                    continue
                if self.envelope_left() <= 0:
                    self.stopped = "ENVELOPE_EXHAUSTED"
                    continue
                for job in list(queue):
                    if gate is not None and not gate(job):
                        queue.remove(job)
                        continue
                    if self._start(job):
                        queue.remove(job)
                        started = True
                        break
            if not started:
                time.sleep(1)

    # ---------------------------------------------------------------- analysis hooks
    def analyse(self) -> Dict:
        return R.analyse(self.root, self.worlds, self.out, self.a.budget, self.frozen, self.a.expect_off_frozen,
                         self.a.expect_off_xabs, self.state["utc_start"], self.state["ledger_s"])

    def need_and_determined(self):
        res = self.analyse()
        need = det = False
        need = any(res["per_seed"][s]["cells"][c]["chain_ge_80pct"] for s in R.SEEDS for c in ("on_frozen", "on_xabs"))
        det = all(res["per_seed"][s]["label"]["determined"] for s in R.SEEDS)
        return need, det, res

    def scratch_order(self) -> List[tuple]:
        out = []
        for w in self.worlds:
            kp = KP.KP(self.root, w)
            for f in kp.admitted():
                out.append((kp.task(f)["output_type"] != "Int", f, w))
        return [(f, w) for _i, f, w in sorted(out)]

    def lazy_scratch(self, cap):
        """Run OE scratch in the fixed order, one decision at a time, while needed and not determined."""
        oe_env = self.a.oe_scratch_envelope_core_h * 3600.0
        for f, w in self.scratch_order():
            if self.stopped:
                return
            need, det, _res = self.need_and_determined()
            if not need or det:
                return
            st = R.scratch_state(KP._load(self.out, w), f, True, self.a.budget)
            if st["state"] in ("FAILED", "SOLVED"):
                continue
            if st["state"] == "CENSORED" and st.get("cap_s", 0) >= cap:
                continue
            if self.state["ledger_s"].get("oe_scratch", 0) + cap > oe_env:
                self.state.setdefault("notes", []).append("OE scratch envelope: %s/%s not started" % (w, f))
                return
            self.run_jobs([{"name": "oe_scratch/%s/%s/cap%d" % (w, f, cap), "world": w, "cat": "oe_scratch",
                            "cmds": [self.argv(w, "on_frozen", 0, "scratch", f, cap)]}])

    # ---------------------------------------------------------------- the order
    def go(self) -> Dict:
        a = self.a
        if time.time() < _ts(a.not_before):
            return self.finish("WAIT (not before %s)" % a.not_before)
        # 1. off_xabs seed 0 + reproduction checks
        self.run_jobs([{"name": "off_xabs/s0/%s" % w, "world": w, "cat": "other",
                        "cmds": [self.argv(w, "off_xabs", 0, "all")]} for w in self.worlds])
        if self.stopped:
            return self.finish(self.stopped)
        res = self.analyse()
        chk = res["reproduction_checks"]
        bad = [k for k, v in chk.items() if (isinstance(v, bool) and not v) or (isinstance(v, dict) and
                                                                                  v.get("pass") is False)]
        self.state["reproduction_checks"] = chk
        if bad:
            return self.finish("HALT_REPRODUCTION (%s)" % ", ".join(bad))
        # 2. OE R1 + chains, seed 0
        self.run_jobs([{"name": "oe_chains/s0/%s" % w, "world": w, "cat": "other",
                        "cmds": [self.argv(w, "on_frozen", 0, "chain"), self.argv(w, "on_xabs", 0, "chain")]}
                       for w in self.worlds])
        # 3. lazy OE scratch
        self.lazy_scratch(R.OE_SCRATCH_CAP_S)
        # 4. seeds 1, 2 (+ off_frozen seed rows if absent), then lazy scratch again
        if not self.stopped:
            self.run_jobs([{"name": "seeds/%s" % w, "world": w, "cat": "other",
                            "cmds": [self.argv(w, c, s, "chain") for s in (1, 2)
                                     for c in ("off_xabs", "on_frozen", "on_xabs", "off_frozen")]}
                           for w in self.worlds])
            self.lazy_scratch(R.OE_SCRATCH_CAP_S)
        # 5. one extension for label-deciding censored searches
        if not self.stopped:
            self.lazy_scratch(R.OE_SCRATCH_EXTENSION_S)
        # 6. priority 2: fallback-off on_xabs
        if not self.stopped and a.with_fallback_off:
            self.run_jobs([{"name": "fb0/%s" % w, "world": w, "cat": "other",
                            "cmds": [self.argv(w, "on_xabs", 0, "chain", fallback=False)]} for w in self.worlds])
        return self.finish(self.stopped or "COMPLETE")

    def finish(self, status) -> Dict:
        res = self.analyse()
        res["driver_status"] = status
        res["driver"] = {"utc_start": self.state["utc_start"], "utc_end": R.utc_now(),
                         "invocations": self.state["invocations"], "ledger_s": self.state["ledger_s"],
                         "envelope_core_h": self.a.envelope_core_h, "debit_core_h": self.a.debit_core_h,
                         "oe_scratch_envelope_core_h": self.a.oe_scratch_envelope_core_h,
                         "deadline": self.a.deadline, "workers": self.a.workers, "notes": self.state.get("notes", [])}
        if status.startswith("HARD_STOP") or status.startswith("ENVELOPE"):
            res["REPAIR_CLASS_note"] = "run stopped (%s): label from complete required items only" % status
        self.state["status"] = status
        self.save()
        p = self.out / "E3R_RESULT.json"
        p.write_text(json.dumps(res, indent=1, sort_keys=True, default=str))
        return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--kp-frozen", required=True, help="dir with the FROZEN E3-KP KPA1 caches (re-used, never written)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--worlds")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--budget", type=int, default=KP.BUDGET, help="development only; the prereg budget is 1e6")
    ap.add_argument("--deadline", default=R.HARD_STOP_UTC)
    ap.add_argument("--not-before", default=R.NOT_BEFORE_UTC)
    ap.add_argument("--envelope-core-h", type=float, default=14.0)
    ap.add_argument("--debit-core-h", type=float, default=0.0, help="concurrent E2 / AR-1 load to pre-debit")
    ap.add_argument("--oe-scratch-envelope-core-h", type=float, default=R.OE_SCRATCH_ENVELOPE_S / 3600.0)
    ap.add_argument("--min-free-gb", type=float, default=6.0)
    ap.add_argument("--expect-off-frozen", type=int)
    ap.add_argument("--expect-off-xabs", type=int, help="EXPECTED off_xabs count: reported, never asserted")
    ap.add_argument("--with-fallback-off", action="store_true")
    ap.add_argument("--analyse-only", action="store_true")
    a = ap.parse_args()
    d = Driver(a)
    res = d.finish("ANALYSE_ONLY") if a.analyse_only else d.go()
    print(json.dumps({k: res.get(k) for k in ("driver_status", "REPAIR_CLASS", "stability", "reading",
                                              "reproduction_checks")}, indent=1, default=str))


if __name__ == "__main__":
    main()
