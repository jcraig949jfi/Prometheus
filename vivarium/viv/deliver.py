"""The PEW outbox deliverer -- a scheduler one-shot, like viv/deadman.py
(point release; PEW_OUTBOX_DESIGN.md s3).

One tick: take PENDING rows in (producer, stream, sequence) order, post each
through the existing PEW client (world anchor, encounter, read-back), mark
DELIVERED on 2xx or on PEW's duplicate answer, REJECTED on a 4xx that is not
409/429 (the payload is wrong; never retried; a corrected fact is a NEW
event), leave PENDING on transport / 5xx / 429 and STOP THE STREAM there
(delivering ahead would create a gap the 009 trigger refuses anyway).

Rule 10: consecutive ticks that delivered nothing while PENDING rows exist
are counted in a state file; at the bound the deliverer parks itself
(record + task disable + ONE comms report to the accountable seat) and
refuses to run until cleared. A backlog above `park_backlog` rows parks
the same way: never drop, never compact, report (design s4).

The consumer never imports this module; the tick path is asserted free of
the HTTP client by tests/test_deliver.py.
"""
from __future__ import annotations

import datetime
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from . import daemon as _daemon
from . import db as _db
from . import outbox as _outbox
from . import pew as _pew
from . import vardir as _vardir

STATE_SCHEMA = "vivarium_deliverer_state.v1"
SEAT_NAME = "Vivarium"


def _utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class Config:
    producer: str = "vivarium@m2"
    task_name: str = "VivariumOutboxDelivererM2"
    batch: int = 200
    bound: int = 12                       # ticks with pending rows and zero deliveries (one hour at 5 min)
    park_backlog: int = 10000
    accountable_seat: str = "Mnemosyne"
    var_dir: Optional[Path] = None
    post: bool = True
    disable_task: bool = True


class Deliverer:
    def __init__(self, cfg: Config, *, client_factory: Optional[Callable] = None,
                 post: Optional[Callable] = None, disable: Optional[Callable] = None, log=print):
        self.cfg = cfg
        self.log = log
        self.client_factory = client_factory
        self.post_hook = post
        self.disable_hook = disable
        self.var = Path(cfg.var_dir) if cfg.var_dir else _vardir.resolve()
        self.var.mkdir(parents=True, exist_ok=True)
        tag = _daemon._safe(cfg.producer)
        self.state_path = self.var / ("deliverer-%s.state.json" % tag)
        self.park_path = self.var / ("deliverer-%s.park.json" % tag)
        self.log_path = self.var / ("deliverer-%s.log" % tag)

    # -- io -----------------------------------------------------------------
    def _log(self, msg: str) -> None:
        line = "%s  %s" % (_utc(), msg)
        self.log(line)
        try:
            with self.log_path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")
        except OSError:
            pass

    def _read_state(self) -> dict:
        try:
            return json.loads(self.state_path.read_text(encoding="utf-8")) if self.state_path.exists() else {}
        except (OSError, ValueError):
            return {}

    def _write_state(self, **kw) -> dict:
        st = {"schema": STATE_SCHEMA, "task": self.cfg.task_name, "producer": self.cfg.producer,
              "last_probe_at": _utc(), "bound": self.cfg.bound, "park_backlog": self.cfg.park_backlog,
              "accountable_seat": self.cfg.accountable_seat}
        st.update(kw)
        tmp = self.state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(st, indent=2, default=str), encoding="utf-8")
        os.replace(tmp, self.state_path)
        return st

    # -- one tick ------------------------------------------------------------
    def tick(self, conn=None) -> dict:
        prev = self._read_state()
        if prev.get("parked"):
            self._log("PARKED since %s; refusing to run until %s is cleared" % (prev.get("parked_at"), self.park_path))
            return {"exit": 3, "verdict": "PARKED"}
        own = conn is None
        conn = conn or _db.connect()
        try:
            ob = _outbox.Outbox(schema=_db.schema(), producer=self.cfg.producer, log=self.log)
            if not ob.enabled(conn):
                st = self._write_state(verdict="NO_OUTBOX", consecutive_idle=0, parked=False)
                return {"exit": 0, "verdict": "NO_OUTBOX", "state": st}
            stats = ob.stats(conn)
            pending_total = stats.get("pending", 0)
            if pending_total > self.cfg.park_backlog:
                return self._park(conn, prev, reason="backlog %d exceeds %d" % (pending_total, self.cfg.park_backlog), stats=stats)
            rows = ob.pending(conn, limit=self.cfg.batch)
            delivered = rejected = left = 0
            stopped_streams = set()
            client = None
            for r in rows:
                key = (r["producer"], r["stream"])
                if key in stopped_streams:
                    left += 1
                    continue
                if client is None:
                    client = self._client()
                    if client is None:
                        conn.rollback()
                        return self._idle(prev, stats, reason="no PEW client (no credential)")
                state, http, err, ref = self._deliver_one(client, r)
                ob.mark(conn, r["event_id"], state=state, http=http, error=err, pew_reference=ref)
                if state == "DELIVERED":
                    delivered += 1
                elif state == "REJECTED":
                    rejected += 1
                else:
                    left += 1
                    stopped_streams.add(key)          # in-order: nothing after a non-delivery in this stream
            conn.commit()
            consecutive = 0 if delivered or not rows else int(prev.get("consecutive_idle") or 0) + 1
            st = self._write_state(verdict="DELIVERED" if delivered else ("IDLE" if not rows else "STUCK"),
                                   delivered=delivered, rejected=rejected, left_pending=left,
                                   pending_total=pending_total, consecutive_idle=consecutive,
                                   last_success_at=_utc() if delivered or not rows else prev.get("last_success_at"),
                                   parked=False)
            if rows:
                self._log("delivered %d, rejected %d, left %d of %d pending" % (delivered, rejected, left, pending_total))
            if consecutive >= self.cfg.bound:
                return self._park(conn, st, reason="%d consecutive ticks with %d pending and no delivery" % (consecutive, pending_total), stats=stats)
            return {"exit": 0 if not left else 1, "verdict": st["verdict"], "delivered": delivered,
                    "rejected": rejected, "left": left, "state": st}
        finally:
            if own:
                conn.close()

    def _idle(self, prev, stats, *, reason):
        consecutive = int(prev.get("consecutive_idle") or 0) + 1
        st = self._write_state(verdict="STUCK", reason=reason, pending_total=stats.get("pending", 0),
                               consecutive_idle=consecutive, last_success_at=prev.get("last_success_at"), parked=False)
        self._log("no delivery: %s (%d of %d)" % (reason, consecutive, self.cfg.bound))
        if consecutive >= self.cfg.bound:
            return self._park(None, st, reason=reason, stats=stats)
        return {"exit": 1, "verdict": "STUCK", "state": st}

    def _client(self):
        if self.client_factory is not None:
            return self.client_factory()
        try:
            cfg = _db.load_config()
            token = cfg.get("pew_token")
            if not token or not cfg.get("pew_base_url"):
                return None
            return _pew.PewClient(cfg["pew_base_url"], token, agent="vivarium", namespace=cfg.get("pew_namespace", "prod"))
        except Exception as exc:                                       # noqa: BLE001
            self._log("PEW client unavailable: %s" % exc)
            return None

    def _deliver_one(self, client, r: dict):
        """(state, http, error, pew_reference)."""
        kind = r["event_kind"]
        payload = r["payload"]
        try:
            if kind == "ENCOUNTER_RECORDED":
                out = _pew.post_bodies(client, payload)
                return "DELIVERED", 200, None, out.get("pew_reference")
            # every other kind is a provenance event for PEW's producer-event
            # inbox (Mnemosyne #344, POST /api/v1/events): body = {producer,
            # stream, seq, event_id, kind, payload[, envelope]}; answers
            # accepted | duplicate (both DELIVERED) | checkpoint_mismatch
            # (REJECTED: same seq, different digest -- never overwritten) |
            # rejected_malformed / 422 (REJECTED). gap/late are flags PEW
            # keeps; a gap is visible on both sides and healed by neither.
            body = {"producer": r["producer"], "stream": r["stream"], "seq": int(r["sequence"]),
                    "event_id": r["event_id"], "kind": kind, "payload": payload,
                    "envelope": {"source_attempt": str(r["source_attempt"]),
                                 "source_step": str(r["source_step"]) if r.get("source_step") else None,
                                 "source_experiment": str(r["source_experiment"]),
                                 "payload_digest": r["payload_digest"]}}
            status, ans = client._req("POST", "/events", body)          # noqa: SLF001
            res = (ans or {}).get("results") if isinstance(ans, dict) else None
            res = res if isinstance(res, dict) else {}
            st = res.get("status")
            if status in (200, 201) and st in ("accepted", "duplicate"):
                ref = "pew:event/%s/%s/%s" % (r["producer"], r["stream"], r["sequence"])
                return "DELIVERED", status, None, ref
            if status in (200, 201) and st in ("checkpoint_mismatch", "rejected_malformed"):
                return "REJECTED", status, json.dumps(res, default=str)[:500], None
            if 400 <= status < 500 and status not in (409, 429):
                return "REJECTED", status, json.dumps(ans, default=str)[:500], None
            return "PENDING", status, json.dumps(ans, default=str)[:500], None
        except _pew.PewError as exc:
            msg = str(exc)
            http = None
            for code in ("422", "400", "404", "409", "429", "500", "502", "503"):
                if code in msg:
                    http = int(code)
                    break
            if http in (409,):
                return "DELIVERED", http, None, None
            if http is not None and 400 <= http < 500 and http != 429:
                return "REJECTED", http, msg[:2000], None
            return "PENDING", http, msg[:2000], None
        except Exception as exc:                                       # noqa: BLE001
            return "PENDING", None, "%s: %s" % (type(exc).__name__, str(exc)[:500]), None

    # NOTE: the queue row's pew_reference is NOT stamped after delivery. A
    # terminal row is frozen by the transition trigger, and that invariant is
    # worth more than a convenience column: the reference lives on the outbox
    # row (pew_reference) and `viv.cli trace` reads it from there.

    def _park(self, conn, st, *, reason: str, stats: dict) -> dict:
        rec = {"schema": "loop_park.v1", "kind": "DELIVERER_BOUND", "loop": self.cfg.task_name,
               "producer": self.cfg.producer, "host": os.environ.get("COMPUTERNAME"), "parked_at": _utc(),
               "bound": self.cfg.bound, "park_backlog": self.cfg.park_backlog, "reason": reason, "outbox": stats,
               "accountable_seat": self.cfg.accountable_seat,
               "clearance": "delete %s, then schtasks /Change /TN %s /ENABLE" % (self.park_path, self.cfg.task_name)}
        self.park_path.write_text(json.dumps(rec, indent=2, default=str), encoding="utf-8")
        self._write_state(**dict(st, parked=True, parked_at=rec["parked_at"], park_record=str(self.park_path)))
        self._log("PARKED: %s" % reason)
        disabled = None
        if self.cfg.disable_task:
            disabled = (self.disable_hook or self._disable)(self.cfg.task_name)
        posted = None
        if self.cfg.post:
            body = self.park_path.with_suffix(".report.md")
            body.write_text("Vivarium outbox deliverer PARKED on %s (%s)\n\n%s\n\noutbox: %s\n\nrecord: %s\n"
                            % (rec["host"], rec["parked_at"], reason, json.dumps(stats, default=str), self.park_path),
                            encoding="utf-8")
            posted = (self.post_hook or self._post)(rec, body)
        return {"exit": 3, "verdict": "PARKED_DELIVERER", "park": rec, "disabled": disabled, "posted": posted}

    @staticmethod
    def _disable(task_name: str) -> bool:
        try:
            return subprocess.run(["schtasks", "/Change", "/TN", task_name, "/DISABLE"],
                                  capture_output=True, text=True, timeout=30).returncode == 0
        except Exception:                                              # noqa: BLE001
            return False

    def _post(self, rec: dict, body: Path) -> dict:
        cmd = [sys.executable, "-m", "comms", "post", "--from", SEAT_NAME, "--to", rec["accountable_seat"],
               "--kind", "report", "--subject", "Vivarium outbox deliverer PARKED: %s" % rec["reason"][:100],
               "--body-file", str(body)]
        try:
            out = subprocess.run(cmd, cwd=str(_daemon._workspace.REPO), capture_output=True, text=True, timeout=90)
            return {"posted": out.returncode == 0, "stderr": (out.stderr or "")[-300:]}
        except Exception as exc:                                       # noqa: BLE001
            return {"posted": False, "error": str(exc)[:300]}


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="viv.deliver", description="one outbox delivery tick")
    ap.add_argument("--producer", default="vivarium@m2")
    ap.add_argument("--task-name", default="VivariumOutboxDelivererM2")
    ap.add_argument("--batch", type=int, default=200)
    ap.add_argument("--bound", type=int, default=12)
    ap.add_argument("--park-backlog", type=int, default=10000)
    ap.add_argument("--var-dir", default=None)
    ap.add_argument("--no-post", action="store_true")
    ap.add_argument("--no-disable", action="store_true")
    a = ap.parse_args(argv)
    cfg = Config(producer=a.producer, task_name=a.task_name, batch=a.batch, bound=a.bound,
                 park_backlog=a.park_backlog, var_dir=Path(a.var_dir) if a.var_dir else None,
                 post=not a.no_post, disable_task=not a.no_disable)
    res = Deliverer(cfg).tick()
    print(json.dumps({k: v for k, v in res.items() if k != "state"}, indent=2, default=str))
    return int(res.get("exit", 1))


if __name__ == "__main__":
    sys.exit(main())
