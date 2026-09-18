"""Out-of-process dead-man check for the Vivarium consumer (backlog C11b).

WHY THIS EXISTS. The consumer died twice in three days and nobody saw it:
2026-09-13 18:12 local (a Windows Terminal crash; found 11.9 h later) and
2026-09-14 19:55 local (the M1 reboot; found 35.9 h later by a seat booting).
Rule 10 lives INSIDE the consumer, so a dead process cannot park, and the
MONITORS.md dormancy threshold ("15 min without a heartbeat while no row is
current") had no reader. This is the reader. It is a one-shot the Task
Scheduler fires every few minutes; it keeps no process of its own to die.

WHAT ONE TICK DOES, in order:

    1. read the consumer's heartbeat row from the CANONICAL store
       (viv.db.connect() proves the cluster; a wrong store is a refusal,
       never a "no heartbeat");
    2. decide LIVE / BUSY / DEAD / PARKED / STOPPING:
         PARKED    the consumer's own park record exists in var_dir ->
                   nothing is relaunched; a parked loop resumes only on
                   `viv.cli unpark` (base rule 10);
         STOPPING  a stop flag exists -> the operator asked it to stop;
                   nothing is relaunched until the flag is gone;
         LIVE      heartbeat younger than `fresh_s`;
         BUSY      heartbeat older, but the row's pid is a live process on
                   THIS host (the heartbeat does not fire during a row,
                   backlog C2, and rows run 160-630 s) -> not dead;
         DEAD      heartbeat older than `fresh_s` AND the pid is gone;
    3. on DEAD, check the LAUNCH PRECONDITION (base rule 9): the engine the
       consumer is configured for answers GET /v2/version with the expected
       engine_instance_id. If it does not, the consumer is NOT relaunched
       (it would only halt on its own gate); the tick records
       UPSTREAM_DEAD and counts as failed;
    4. on DEAD with the upstream live, run the launcher, wait, re-read the
       heartbeat; a fresh heartbeat is a PRODUCTIVE tick (state advanced);
    5. after `bound` CONSECUTIVE failed ticks, PARK: typed record, disable
       the scheduled task, post exactly ONE comms report to the accountable
       seat, exit 3. A parked dead-man never resumes on its own.

Every tick overwrites a small STATE file (last_probe_at, last_success_at,
consecutive_failures, verdict, parked) so freshness is readable without
running anything (base rule 7). The log keeps transitions only.

WHAT THIS IS NOT. Not a retry of anything scientific: a consumer that died
mid-row leaves that row STRANDED and its own restart leaves it so (charter
invariant 6); this only restarts the process. Not a second consumer: it
relaunches only when the recorded pid is gone from this host, so it cannot
race a slow row (the BUSY verdict). Not a judge of productivity: the
consumer's rule-10 bound covers "alive but useless"; this covers "not
alive", the case that bound cannot see.

Test hooks (tests/test_deadman.py; never set by the task): every external
observation -- heartbeat, pid liveness, upstream, launcher, task disable,
comms post -- is a function the caller can replace.
"""
from __future__ import annotations

import datetime
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from . import daemon as _daemon
from . import db as _db
from . import vardir as _vardir

SEAT_NAME = "Vivarium"
STATE_SCHEMA = "vivarium_deadman_state.v1"
PARK_SCHEMA = "loop_park.v1"


def _utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class Config:
    worker_id: str = "vivarium@m2"
    task_name: str = "VivariumDeadmanM2"
    launcher: Optional[str] = None            # cmd file; None -> no relaunch
    fresh_s: float = 900.0                    # MONITORS.md: 15 min
    pid_grace_s: float = 60.0                 # younger than this: never pid-check (a launch settles)
    #: Campaign 4 (operator PROMPT 3, 2026-09-17): the two operator commands
    #: after an engine stall or a worker death -- `viv.cli unpark` and
    #: `viv.cli release <id> --new-attempt` -- become a BOUNDED automatic
    #: state transition of this loop. At most this many auto-recoveries per
    #: rolling 24 h; the (n+1)th stays parked for a person. The park record
    #: and its notice are unchanged (evidence first); the clearance is
    #: recorded like a human one, with the engine's answer as the reason.
    auto_recover_bound: int = 3
    auto_recover_window_s: float = 86400.0
    settle_s: float = 25.0                    # after launch, before re-read
    bound: int = 3
    accountable_seat: str = "Archaeon"
    upstream_seat: str = "Daedalus"
    expected_engine_instance_id: Optional[str] = None
    sfe_version_url: Optional[str] = None     # None -> cfg sfe_base_url
    sfe_cacert: Optional[str] = None
    var_dir: Optional[Path] = None
    post: bool = True
    disable_task: bool = True


@dataclass
class Hooks:
    """Every observation and act, replaceable in tests."""
    heartbeat: Optional[Callable[[], Optional[dict]]] = None
    pid_alive: Optional[Callable[[int, str], bool]] = None
    upstream: Optional[Callable[[], dict]] = None
    launch: Optional[Callable[[], bool]] = None
    disable: Optional[Callable[[str], bool]] = None
    post: Optional[Callable[[dict, Path], dict]] = None
    sleep: Callable[[float], None] = time.sleep
    release: Optional[Callable[[str, str], dict]] = None       # (experiment_id, reason) -> record
    stranded_rows: Optional[Callable[[str], list]] = None      # worker_id -> [experiment_id, ...]
    extra: dict = field(default_factory=dict)


# --------------------------------------------------------------- observations

def read_heartbeat(worker_id: str) -> Optional[dict]:
    """The consumer's row, from the canonical store, or None if it never
    heartbeated. Age is computed against the DATABASE clock, not this
    host's, so two machines' clocks cannot invent a death."""
    conn = _db.connect()
    try:
        with _db.dict_cur(conn) as cur:
            cur.execute("SELECT worker_id, host, pid, started_at, last_seen, "
                        "current_experiment, build, "
                        "EXTRACT(EPOCH FROM (now() - last_seen)) AS age_s "
                        "FROM " + _db.schema() + ".worker_heartbeat "
                        "WHERE worker_id = %s", (worker_id,))
            row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def stranded_rows_of(worker_id: str) -> list:
    """Rows this worker holds claimed/running (its process is gone when this
    is asked): the ones a NEW ATTEMPT must release before a relaunch would
    otherwise leave them stranded until a person notices."""
    conn = _db.connect()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT experiment_id::text FROM " + _db.schema() + ".research_experiment_queue "
                        "WHERE claimed_by = %s AND status IN ('claimed', 'running') ORDER BY claimed_at", (worker_id,))
            return [r[0] for r in cur.fetchall()]
    finally:
        conn.close()


def release_new_attempt(experiment_id: str, reason: str) -> dict:
    """`viv.cli release <id> --new-attempt`, as a call: the stranded (or
    ENGINE_TRANSPORT-failed, migration 010) row returns to queued for attempt
    n+1. The queue's own rules decide; a refusal is returned, not raised."""
    from . import queue as _q                                   # noqa: PLC0415
    conn = _db.connect()
    try:
        row = _q.release_stranded(conn, experiment_id, actor="VivariumDeadmanM2", reason=reason,
                                  new_attempt=True)
        conn.commit()
        return {"experiment_id": experiment_id, "released": True, "status": row.get("status") if row else None}
    except Exception as exc:                                     # noqa: BLE001
        conn.rollback()
        return {"experiment_id": experiment_id, "released": False, "error": str(exc)[:300]}
    finally:
        conn.close()


def pid_alive_here(pid: int, host: str) -> bool:
    """Is `pid` a live python process on THIS host? A heartbeat written from
    another host cannot be checked here and is reported NOT alive, which is
    the conservative reading for a relaunch decision only because the
    launcher runs here too: a consumer on another host would have its own
    dead-man."""
    if not pid or (host or "").upper() != os.environ.get("COMPUTERNAME", "").upper():
        return False
    try:
        out = subprocess.run(["tasklist", "/FI", "PID eq %d" % int(pid),
                              "/FO", "CSV", "/NH"],
                             capture_output=True, text=True, timeout=20)
    except Exception:                                    # noqa: BLE001
        return False
    line = (out.stdout or "").strip().splitlines()
    if not line or "No tasks" in line[0]:
        return False
    return line[0].lower().startswith('"python')


def probe_upstream(url: str, cacert: Optional[str], expected_id: Optional[str],
                   timeout_s: float = 10.0) -> dict:
    """GET /v2/version; the launch precondition is answered AND the expected
    ledger identity, not merely 'a port answered'."""
    import ssl
    ctx = ssl.create_default_context()
    if cacert and Path(cacert).exists():
        ctx.load_verify_locations(str(cacert))
    else:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(url, timeout=timeout_s, context=ctx) as r:
            body = json.loads(r.read().decode("utf-8"))
    except Exception as exc:                             # noqa: BLE001
        return {"ok": False, "reason": "UNREACHABLE",
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:200]),
                "url": url}
    got = body.get("engine_instance_id")
    if expected_id and got != expected_id:
        return {"ok": False, "reason": "WRONG_ENGINE", "expected": expected_id,
                "observed": got, "url": url}
    return {"ok": True, "reason": "ANSWERED", "observed": got,
            "schema_version": body.get("schema_version"),
            "engine_source_hash": body.get("engine_source_hash"), "url": url}


def launch_via(launcher: str) -> bool:
    """Start the consumer's launcher detached from this one-shot. True means
    the launch was ISSUED, not that the consumer lives; the heartbeat says."""
    try:
        flags = getattr(subprocess, "DETACHED_PROCESS", 0) | \
            getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        subprocess.Popen(["cmd.exe", "/c", launcher], creationflags=flags,
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, close_fds=True)
        return True
    except Exception:                                    # noqa: BLE001
        return False


def disable_task(task_name: str) -> bool:
    try:
        out = subprocess.run(["schtasks", "/Change", "/TN", task_name,
                              "/DISABLE"], capture_output=True, text=True,
                             timeout=30)
        return out.returncode == 0
    except Exception:                                    # noqa: BLE001
        return False


# ----------------------------------------------------------------- the tick

class Deadman:
    def __init__(self, cfg: Config, hooks: Optional[Hooks] = None,
                 log: Callable[[str], None] = print):
        self.cfg = cfg
        self.h = hooks or Hooks()
        self.log = log
        self.var = Path(cfg.var_dir) if cfg.var_dir else _vardir.resolve()
        self.var.mkdir(parents=True, exist_ok=True)
        tag = _daemon._safe(cfg.worker_id)
        self.state_path = self.var / ("deadman-%s.state.json" % tag)
        self.park_path = self.var / ("deadman-%s.park.json" % tag)
        self.log_path = self.var / ("deadman-%s.log" % tag)

    # -- io -------------------------------------------------------------
    def _log(self, msg: str) -> None:
        line = "%s  %s" % (_utc(), msg)
        self.log(line)
        try:
            with self.log_path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")
                f.flush()
        except OSError:
            pass

    def _read_state(self) -> dict:
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                return {}
        return {}

    def _write_state(self, **kw) -> dict:
        # the rolling auto-recovery ledger survives every rewrite
        try:
            prev = self._read_state()
        except Exception:                                      # noqa: BLE001
            prev = {}
        if "auto_recoveries" not in kw and prev.get("auto_recoveries"):
            kw["auto_recoveries"] = prev["auto_recoveries"]
        st = {"schema": STATE_SCHEMA, "task": self.cfg.task_name,
              "worker_id": self.cfg.worker_id, "host": os.environ.get("COMPUTERNAME"),
              "last_probe_at": _utc(), "bound": self.cfg.bound,
              "accountable_seat": self.cfg.accountable_seat}
        st.update(kw)
        tmp = self.state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(st, indent=2, default=str), encoding="utf-8")
        os.replace(tmp, self.state_path)
        return st

    # -- observations ---------------------------------------------------
    def _heartbeat(self) -> Optional[dict]:
        fn = self.h.heartbeat or (lambda: read_heartbeat(self.cfg.worker_id))
        return fn()

    def _pid_alive(self, pid: int, host: str) -> bool:
        return (self.h.pid_alive or pid_alive_here)(pid, host)

    def _upstream(self) -> dict:
        if self.h.upstream:
            return self.h.upstream()
        url = self.cfg.sfe_version_url
        if not url:
            base = _db.load_config().get("sfe_base_url", "")
            url = base.rstrip("/") + "/v2/version"
        return probe_upstream(url, self.cfg.sfe_cacert,
                              self.cfg.expected_engine_instance_id)

    def _launch(self) -> bool:
        if self.h.launch:
            return self.h.launch()
        if not self.cfg.launcher:
            return False
        return launch_via(self.cfg.launcher)

    def verdict(self, hb: Optional[dict]) -> dict:
        """LIVE / BUSY / DEAD / PARKED / STOPPING / NEVER, with the evidence."""
        park = _daemon.read_park(self.var, self.cfg.worker_id)
        if park is not None:
            return {"verdict": "PARKED", "park": park}
        if _daemon.stop_file_for(self.var, self.cfg.worker_id).exists():
            return {"verdict": "STOPPING"}
        if hb is None:
            return {"verdict": "NEVER", "note": "no heartbeat row for this worker_id"}
        age = float(hb.get("age_s") or 0.0)
        ev = {"age_s": round(age, 1), "pid": hb.get("pid"), "host": hb.get("host"),
              "current_experiment": hb.get("current_experiment")}
        if age < self.cfg.fresh_s:
            # A heartbeat can be young and the process gone: the s14 canary
            # killed the consumer mid-row and the dead-man read LIVE for the
            # whole fresh_s (15 min) before it would even look at the pid.
            # Past a short grace, a heartbeat FROM THIS HOST whose pid is not
            # a live python here is DEAD now, not in 15 minutes.
            same_host = (str(hb.get("host") or "").upper()
                         == os.environ.get("COMPUTERNAME", "").upper())
            if (age >= self.cfg.pid_grace_s and same_host and hb.get("pid")
                    and not self._pid_alive(int(hb["pid"]), str(hb["host"]))):
                return {"verdict": "DEAD", **ev,
                        "note": "heartbeat young but its pid is gone from this host"}
            return {"verdict": "LIVE", **ev}
        if self._pid_alive(int(hb.get("pid") or 0), str(hb.get("host") or "")):
            return {"verdict": "BUSY", **ev,
                    "note": "heartbeat stale but the pid is a live python on this host (C2)"}
        return {"verdict": "DEAD", **ev}

    # -- one tick ---------------------------------------------------------
    def tick(self) -> dict:
        prev = self._read_state()
        if prev.get("parked"):
            self._log("PARKED since %s; refusing to run until %s is cleared"
                      % (prev.get("parked_at"), self.park_path))
            return {"exit": 3, "verdict": "DEADMAN_PARKED", "state": prev}
        consecutive = int(prev.get("consecutive_failures") or 0)
        last_success = prev.get("last_success_at")

        try:
            hb = self._heartbeat()
        except Exception as exc:                          # noqa: BLE001
            # A store that cannot be read (or proved) is a failed tick of
            # THIS loop, never a verdict about the consumer.
            consecutive += 1
            st = self._write_state(verdict="STORE_UNREADABLE",
                                   error="%s: %s" % (type(exc).__name__, str(exc)[:300]),
                                   consecutive_failures=consecutive,
                                   last_success_at=last_success, parked=False)
            self._log("store unreadable (%d of %d): %s" % (consecutive, self.cfg.bound,
                                                          type(exc).__name__))
            return self._maybe_park(consecutive, last_success, st,
                                    reason="the canonical store could not be read or proved")

        v = self.verdict(hb)
        recovery = None
        if v["verdict"] == "PARKED":
            recovery = self._auto_recover_park(v.get("park") or {}, prev)
            if recovery and recovery.get("cleared"):
                v = self.verdict(hb)                       # the record is gone; the consumer exited when it parked
        if v["verdict"] in ("LIVE", "BUSY", "PARKED", "STOPPING"):
            if consecutive:
                self._log("%s again after %d failed tick(s)" % (v["verdict"], consecutive))
            st = self._write_state(consecutive_failures=0, last_success_at=_utc(),
                                   parked=False, **v, **({"auto_recovery": recovery} if recovery else {}))
            return {"exit": 0, **v, "state": st}

        # DEAD or NEVER: rule 9 before any launch.
        up = self._upstream()
        if up.get("ok") and v["verdict"] == "DEAD":
            # a dead worker's claimed/running rows are stranded by definition:
            # release them to a NEW ATTEMPT before the relaunch (bounded with
            # the same counter; the queue's rules decide each release)
            released = self._release_stranded(v)
            if released:
                v = dict(v, released_before_relaunch=released)
        if not up.get("ok"):
            consecutive += 1
            st = self._write_state(consecutive_failures=consecutive,
                                   last_success_at=last_success, parked=False,
                                   upstream=up, **dict(v, verdict=v["verdict"]))
            self._log("consumer %s and upstream %s (%s); NOT relaunched (%d of %d)"
                      % (v["verdict"], up.get("reason"), up.get("url"),
                         consecutive, self.cfg.bound))
            return self._maybe_park(consecutive, last_success, st,
                                    reason="consumer %s; launch precondition failed: %s"
                                    % (v["verdict"], up.get("reason")),
                                    seat=self.cfg.upstream_seat, upstream=up)

        issued = self._launch()
        if issued:
            self.h.sleep(self.cfg.settle_s)
            try:
                hb2 = self._heartbeat()
            except Exception:                              # noqa: BLE001
                hb2 = None
            v2 = self.verdict(hb2)
            if v2["verdict"] in ("LIVE", "BUSY"):
                extra = {k: v[k] for k in ("released_before_relaunch",) if k in v}
                if recovery:
                    extra["auto_recovery"] = recovery
                st = self._write_state(consecutive_failures=0, last_success_at=_utc(),
                                       parked=False, relaunched=True, **v2, **extra)
                self._log("consumer was %s; relaunched via %s; now %s (pid %s)"
                          % (v["verdict"], self.cfg.launcher, v2["verdict"], v2.get("pid")))
                return {"exit": 0, "relaunched": True, **v2, **extra, "state": st}
        consecutive += 1
        st = self._write_state(consecutive_failures=consecutive,
                               last_success_at=last_success, parked=False,
                               relaunched=False, launch_issued=issued, **v)
        self._log("consumer %s; relaunch %s (%d of %d)"
                  % (v["verdict"], "issued but no heartbeat" if issued else "not issued",
                     consecutive, self.cfg.bound))
        return self._maybe_park(consecutive, last_success, st,
                                reason="consumer %s and %d consecutive relaunches did not "
                                       "produce a heartbeat" % (v["verdict"], consecutive))

    # -- Campaign 4: bounded auto-recovery -----------------------------------
    def _recoveries_in_window(self, prev: dict) -> list:
        cutoff = time.time() - self.cfg.auto_recover_window_s
        out = []
        for t in prev.get("auto_recoveries") or []:
            try:
                ts = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc).timestamp()
            except Exception:                                  # noqa: BLE001
                continue
            if ts >= cutoff:
                out.append(t)
        return out

    def _note_recovery(self, prev: dict) -> list:
        lst = self._recoveries_in_window(prev) + [_utc()]
        prev["auto_recoveries"] = lst
        self._write_state(**dict(prev, auto_recoveries=lst))   # persisted NOW; later writes carry it forward
        return lst

    def _auto_recover_park(self, park: dict, prev: dict) -> Optional[dict]:
        """A consumer parked on the ENGINE_TRANSPORT halt (rider #136) is
        cleared automatically when the engine answers again -- at most
        auto_recover_bound times per window. Everything else stays parked."""
        if park.get("kind") != "FAILURE_CLASS_HALT":
            return None
        fc = ((park.get("last_tick") or {}).get("failure_class")) or ((park.get("last_productive") or {}).get("failure_class"))
        if fc != "ENGINE_TRANSPORT":
            return {"cleared": False, "why": "park is %s/%s, not the transport halt; a person clears it" % (park.get("kind"), fc)}
        used = self._recoveries_in_window(prev)
        if len(used) >= self.cfg.auto_recover_bound:
            self._log("transport park NOT auto-cleared: %d auto-recoveries in the last %.0f h (bound %d); a person clears it"
                      % (len(used), self.cfg.auto_recover_window_s / 3600, self.cfg.auto_recover_bound))
            return {"cleared": False, "why": "auto-recovery bound reached", "used": used}
        up = self._upstream()
        if not up.get("ok"):
            self._log("transport park NOT auto-cleared: engine still %s" % up.get("reason"))
            return {"cleared": False, "why": "engine not answering", "upstream": up}
        eid = (park.get("last_tick") or {}).get("experiment_id") or (park.get("last_productive") or {}).get("experiment_id")
        n = len(used) + 1
        reason = ("auto-recovery %d of %d by %s: the ENGINE_TRANSPORT halt's engine answers again (%s %s at %s); "
                  "the halted row %s is released to a NEW ATTEMPT (migration 010); the park notice stands as evidence"
                  % (n, self.cfg.auto_recover_bound, self.cfg.task_name, up.get("reason"), up.get("observed"), _utc(), eid))
        # the clearance, recorded exactly like `viv.cli unpark` records it
        park_path = _daemon.park_file_for(self.var, self.cfg.worker_id)
        rec = dict(park); rec["cleared"] = {"by": self.cfg.task_name + " (auto)", "at": _utc(), "reason": reason}
        dest = park_path.with_name("%s.cleared-%s.json" % (park_path.stem, _utc().replace(":", "").replace("-", "")))
        try:
            dest.write_text(json.dumps(rec, indent=2, default=str), encoding="utf-8")
            park_path.unlink()
        except OSError as exc:
            return {"cleared": False, "why": "could not record the clearance: %s" % exc}
        released = None
        if eid:
            released = (self.h.release or release_new_attempt)(eid, reason)
        self._note_recovery(prev)
        self._log("transport park AUTO-CLEARED (%d of %d): %s; release %s" % (n, self.cfg.auto_recover_bound, dest.name, released))
        return {"cleared": True, "n": n, "clearance": str(dest), "released": released, "upstream": up}

    def _release_stranded(self, v: dict) -> list:
        try:
            rows = (self.h.stranded_rows or stranded_rows_of)(self.cfg.worker_id)
        except Exception as exc:                                   # noqa: BLE001
            self._log("stranded-row lookup failed (%s); relaunching anyway" % str(exc)[:120])
            return []
        out = []
        for eid in rows:
            r = (self.h.release or release_new_attempt)(
                eid, "worker %s is DEAD (pid %s gone from %s); its claimed/running row is released to a NEW ATTEMPT "
                     "before the relaunch (%s)" % (self.cfg.worker_id, v.get("pid"), v.get("host"), self.cfg.task_name))
            self._log("stranded row %s: %s" % (eid[:8], "released" if r.get("released") else "NOT released: %s" % r.get("error")))
            out.append(r)
        return out

    # -- rule 10 ----------------------------------------------------------
    def _maybe_park(self, consecutive: int, last_success, st: dict, *,
                    reason: str, seat: Optional[str] = None, **extra) -> dict:
        if consecutive < self.cfg.bound:
            return {"exit": 1, "verdict": st.get("verdict"), "state": st}
        seat = seat or self.cfg.accountable_seat
        rec = {"schema": PARK_SCHEMA, "kind": "DEADMAN_BOUND", "loop": self.cfg.task_name,
               "worker_id": self.cfg.worker_id, "host": os.environ.get("COMPUTERNAME"),
               "parked_at": _utc(), "bound": self.cfg.bound,
               "consecutive_non_productive_ticks": consecutive,
               "last_success_at": last_success, "reason": reason,
               "accountable_seat": seat,
               "clearance": "delete %s, then schtasks /Change /TN %s /ENABLE; "
                            "never on restart" % (self.park_path, self.cfg.task_name),
               **extra}
        self.park_path.write_text(json.dumps(rec, indent=2, default=str), encoding="utf-8")
        self._write_state(**dict(st, parked=True, parked_at=rec["parked_at"],
                                 park_record=str(self.park_path)))
        self._log("PARKED: %s; record %s" % (reason, self.park_path))
        disabled = None
        if self.cfg.disable_task:
            disabled = (self.h.disable or disable_task)(self.cfg.task_name)
            self._log("task %s disable: %s" % (self.cfg.task_name, disabled))
        posted = None
        if self.cfg.post:
            body = self.park_path.with_suffix(".report.md")
            body.write_text(self._report_text(rec), encoding="utf-8")
            posted = (self.h.post or self._post)(rec, body)
        return {"exit": 3, "verdict": "PARKED_DEADMAN", "park": rec,
                "disabled": disabled, "posted": posted}

    def _report_text(self, rec: dict) -> str:
        return ("Vivarium dead-man %s PARKED on %s (%s)\n\n"
                "consumer %s: %s\nlast dead-man success: %s\n"
                "consecutive non-productive ticks: %d of %d\n"
                "upstream: %s\n\nrecord: %s\nclearance: %s\n"
                % (rec["loop"], rec["host"], rec["parked_at"], rec["worker_id"],
                   rec["reason"], rec["last_success_at"],
                   rec["consecutive_non_productive_ticks"], rec["bound"],
                   json.dumps(rec.get("upstream")) if rec.get("upstream") else "not probed",
                   self.park_path, rec["clearance"]))

    def _post(self, rec: dict, body: Path) -> dict:
        subject = ("Vivarium dead-man PARKED: consumer %s %s"
                   % (rec["worker_id"], rec["reason"][:100]))
        cmd = [sys.executable, "-m", "comms", "post", "--from", SEAT_NAME,
               "--to", str(rec["accountable_seat"]), "--kind", "report",
               "--subject", subject, "--body-file", str(body)]
        try:
            out = subprocess.run(cmd, cwd=str(_daemon._workspace.REPO),
                                 capture_output=True, text=True, timeout=90)
            res = {"posted": out.returncode == 0, "returncode": out.returncode,
                   "stdout": (out.stdout or "")[-300:], "stderr": (out.stderr or "")[-300:]}
        except Exception as exc:                          # noqa: BLE001
            res = {"posted": False, "error": str(exc)[:300]}
        self._log("park notice to %s: %s" % (rec["accountable_seat"],
                                             "posted" if res["posted"] else "NOT POSTED"))
        return res


# ------------------------------------------------------------------ CLI

def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="viv.deadman",
                                 description="one dead-man tick for the consumer")
    ap.add_argument("--worker-id", default="vivarium@m2")
    ap.add_argument("--task-name", default="VivariumDeadmanM2")
    ap.add_argument("--launcher", default=None)
    ap.add_argument("--fresh-s", type=float, default=900.0)
    ap.add_argument("--settle-s", type=float, default=25.0)
    ap.add_argument("--bound", type=int, default=3)
    ap.add_argument("--expected-engine", default=None,
                    help="engine_instance_id the launch precondition requires (default: the production descriptor's)")
    ap.add_argument("--sfe-version-url", default=None)
    ap.add_argument("--sfe-cacert", default=None)
    ap.add_argument("--var-dir", default=None)
    ap.add_argument("--no-post", action="store_true")
    ap.add_argument("--no-disable", action="store_true")
    ap.add_argument("--no-launch", action="store_true",
                    help="observe and record only; never start anything")
    a = ap.parse_args(argv)
    if a.expected_engine is None:
        # PRODUCTION_DESCRIPTOR.md s3: the target comes from the descriptor,
        # not a command line someone typed once
        from . import production as _prod                    # noqa: PLC0415
        try:
            a.expected_engine = (_prod.load().get("engine") or {}).get("engine_instance_id")
        except Exception:                                     # noqa: BLE001
            a.expected_engine = None
    cfg = Config(worker_id=a.worker_id, task_name=a.task_name,
                 launcher=None if a.no_launch else a.launcher,
                 fresh_s=a.fresh_s, settle_s=a.settle_s, bound=a.bound,
                 expected_engine_instance_id=a.expected_engine,
                 sfe_version_url=a.sfe_version_url, sfe_cacert=a.sfe_cacert,
                 var_dir=Path(a.var_dir) if a.var_dir else None,
                 post=not a.no_post, disable_task=not a.no_disable)
    res = Deadman(cfg).tick()
    print(json.dumps({k: v for k, v in res.items() if k != "state"},
                     indent=2, default=str))
    return int(res.get("exit", 1))


if __name__ == "__main__":
    sys.exit(main())
