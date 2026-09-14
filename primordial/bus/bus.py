"""The swarm bus: Redis Streams on the shared substrate (owner: lane A).

  pm:swarm            stream  chatter: claims, contract changes, asks, kills, anomalies
  pm:results          stream  receipts (validated JSON)
  pm:claims           hash    exp_id -> lane[tag]  (HSETNX: first claim wins)
  pm:board:<metric>   zset    board scores, only board-eligible receipts
  pm:tags             hash    lane -> registered instance tag (set by `hello`)
  pm:alive:<L>        hash    heartbeat {tag, ts, status}, TTL PM_ALIVE_TTL (180 s)
  pm:burst:<L>        string  announced CPU burst, TTL = its duration
  pm:anomalies        stream  ANOMALY queue (round 2 cohort D reads only this)
  pm:anomaly_status   hash    anomaly id -> OPEN / RESOLVED / REFUTED / INDETERMINATE
  pm:anomaly_events   stream  status changes with notes

Each lane reads pm:swarm through its OWN consumer group (lane-<L>), so every
lane sees every message exactly once regardless of how many instances run.
Only the lane's registered tag may consume that group; observers use tail().
Every call made as a lane refreshes the lane's heartbeat.

The bus is fast and ephemeral; the durable record is the committed JSONL
mirror under primordial/ledger/<lane>.jsonl plus primordial/ops/bus_export.

Receipt guard (round 1 lesson: SHAs rewritten by rebase after filing, and a
receipt announced but never filed): rec["git"] must be a commit already on
origin/<PM_INTEGRATION>, and every primordial/... path in rec["rows"] must
exist at that commit. PM_RECEIPT_GUARD=0 disables it (tests only).

Env: PM_BUS_URL (default redis://127.0.0.1:6390/0), PM_LANE (A..E), PM_TAG,
PM_ALIVE_TTL, PM_INTEGRATION, PM_RECEIPT_GUARD, PM_TAKEOVER.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import shutil
import subprocess
import time

import redis

from primordial.core.contract import LANES, ReceiptError, board_eligible, validate_receipt

URL = os.environ.get("PM_BUS_URL", "redis://127.0.0.1:6390/0")
SWARM, RESULTS, CLAIMS = "pm:swarm", "pm:results", "pm:claims"
TAGS = "pm:tags"
ANOMALIES, ANOM_STATUS, ANOM_EVENTS = "pm:anomalies", "pm:anomaly_status", "pm:anomaly_events"
ANOM_STATES = ("OPEN", "RESOLVED", "REFUTED", "INDETERMINATE")
KINDS = ("hello", "claim", "contract", "ask", "result", "kill", "note", "anomaly", "missing")
ALIVE_TTL = int(os.environ.get("PM_ALIVE_TTL", "180"))
INTEGRATION = os.environ.get("PM_INTEGRATION", "nestor/sidequest-graphworld-2026-09-14")
LEDGER_DIR = pathlib.Path(__file__).resolve().parents[1] / "ledger"
REPO = pathlib.Path(__file__).resolve().parents[2]


def conn() -> redis.Redis:
    return redis.Redis.from_url(URL, decode_responses=True)


def me() -> tuple[str, str]:
    lane = os.environ.get("PM_LANE", "")
    if lane not in LANES:
        raise SystemExit("set PM_LANE to one of A B C D E")
    return lane, os.environ.get("PM_TAG", "untagged")


# ------------------------------------------------------------------ liveness + identity

def beat(status: str = "", r=None) -> None:
    """Refresh this lane's heartbeat (every bus call does this)."""
    lane, tag = me()
    r = r or conn()
    key = f"pm:alive:{lane}"
    r.hset(key, mapping={"tag": tag, "ts": f"{time.time():.3f}", "status": status[:200]})
    r.expire(key, ALIVE_TTL)


def register(r=None) -> None:
    """Bind PM_TAG to PM_LANE. Refuses to replace a holder whose heartbeat is still
    live, unless PM_TAKEOVER=1."""
    lane, tag = me()
    r = r or conn()
    held = r.hget(TAGS, lane)
    alive = r.hgetall(f"pm:alive:{lane}")
    if held and held != tag and alive.get("tag") == held and os.environ.get("PM_TAKEOVER") != "1":
        raise SystemExit(f"lane {lane} is held by live tag {held}; PM_TAKEOVER=1 replaces a dead holder")
    r.hset(TAGS, lane, tag)
    beat("hello", r)


def _check_tag(r, lane: str, tag: str) -> None:
    held = r.hget(TAGS, lane)
    if held and held != tag:
        raise SystemExit(f"PM_TAG {tag} is not lane {lane}'s registered tag {held}; "
                         "observers use `python -m primordial.bus tail`")


def alive(r=None) -> dict:
    r = r or conn()
    out = {}
    for lane in LANES:
        h = r.hgetall(f"pm:alive:{lane}")
        if h:
            out[lane] = dict(h, ttl=r.ttl(f"pm:alive:{lane}"))
    return out


# ------------------------------------------------------------------ messages

def addressed_to(fields: dict, lane: str) -> bool:
    to = (fields.get("to") or "").strip()
    return bool(to) and (to == "ALL" or lane in [x.strip() for x in to.split(",")])


def post(kind: str, subject: str, body: str = "", ref: str = "", to: str = "", r=None) -> str:
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {KINDS}")
    lane, tag = me()
    r = r or conn()
    mid = r.xadd(SWARM, {"lane": lane, "tag": tag, "kind": kind, "subject": subject,
                         "body": body, "ref": ref, "to": to, "ts": f"{time.time():.3f}"},
                 maxlen=100_000, approximate=True)
    beat(kind, r)
    return mid


def _ensure_group(r: redis.Redis, lane: str) -> str:
    g = f"lane-{lane}"
    try:
        r.xgroup_create(SWARM, g, id="0", mkstream=True)
    except redis.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise
    return g


def read(count: int = 200, block_ms: int | None = None, r=None) -> list[tuple[str, dict]]:
    """Unseen swarm messages for MY lane; acked on return. Registered tag only."""
    lane, tag = me()
    r = r or conn()
    _check_tag(r, lane, tag)
    g = _ensure_group(r, lane)
    got = r.xreadgroup(g, tag, {SWARM: ">"}, count=count, block=block_ms)
    out = [(mid, f) for _, msgs in (got or []) for mid, f in msgs]
    if out:
        r.xack(SWARM, g, *[m for m, _ in out])
    beat("read", r)
    return out


def tail(n: int = 50, r=None) -> list[tuple[str, dict]]:
    """Last n swarm messages, oldest first. Read-only: acks nothing, needs no lane."""
    r = r or conn()
    return list(reversed(r.xrevrange(SWARM, count=n)))


def claim(exp_id: str, r=None) -> bool:
    lane, tag = me()
    r = r or conn()
    won = bool(r.hsetnx(CLAIMS, exp_id, f"{lane}[{tag}]"))
    if won:
        post("claim", exp_id, r=r)
    else:
        beat("claim-lost", r)
    return won


def burst(seconds: int, note: str, r=None) -> None:
    """Announce a CPU burst; timing harnesses and host_load() see it until it expires."""
    lane, tag = me()
    r = r or conn()
    r.set(f"pm:burst:{lane}", json.dumps({"tag": tag, "note": note, "until": time.time() + seconds}),
          ex=int(seconds))
    post("note", f"BURST {int(seconds)}s", note, r=r)


# ------------------------------------------------------------------ receipts

def guard_git(rec: dict, fetch: bool = True, ref: str | None = None, repo=REPO) -> list[str]:
    """-> problems (empty = ok). rec['git'] must be on `ref` and hold every rows path."""
    ref = ref or f"origin/{INTEGRATION}"
    g = rec.get("git")
    sha = str((g.get("sha") or g.get("rows") or "") if isinstance(g, dict) else (g or "")).strip()
    if not re.fullmatch(r"[0-9a-f]{7,40}", sha):
        return [f"git field {sha!r} is not a commit sha"]

    def git(*a):
        return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, timeout=120)

    if fetch and ref.startswith("origin/"):
        git("fetch", "-q", "origin", ref.split("/", 1)[1])
    problems = []
    if git("cat-file", "-e", f"{sha}^{{commit}}").returncode != 0:
        return [f"{sha} is not a commit in this repo"]
    if git("merge-base", "--is-ancestor", sha, ref).returncode != 0:
        problems.append(f"{sha} is not on {ref}: push first, then file (a rebase after filing rewrites SHAs)")
    paths = re.findall(r"primordial/[\w./-]+\.\w+", str(rec.get("rows", "")))
    if not paths:
        problems.append("rows names no primordial/... path")
    for p in paths:
        if git("cat-file", "-e", f"{sha}:{p}").returncode != 0:
            problems.append(f"rows {p} absent at {sha}")
    return problems


def host_load(r=None) -> dict:
    """Machine state at filing time: CPU, memory, GPU if visible, live bursts."""
    out: dict = {"ts": round(time.time(), 3)}
    try:
        import psutil
        per = psutil.cpu_percent(interval=0.3, percpu=True)
        out.update(cpu_pct=round(sum(per) / len(per), 1), cpu_max_core_pct=max(per),
                   mem_pct=psutil.virtual_memory().percent)
    except Exception as e:                                    # pragma: no cover
        out["cpu_error"] = type(e).__name__
    if shutil.which("nvidia-smi"):
        try:
            q = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used",
                                "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=5)
            out["gpu"] = [line.strip() for line in q.stdout.splitlines() if line.strip()]
        except Exception:                                     # pragma: no cover
            pass
    try:
        r = r or conn()
        out["bursts"] = {k: json.loads(v) for k in r.scan_iter("pm:burst:*") if (v := r.get(k))}
    except Exception:                                         # pragma: no cover
        pass
    return out


def receipt(rec: dict, board: dict | None = None, r=None) -> str:
    """Guard, validate, mirror to the committed ledger (flush), publish.
    board: {metric: score} is applied only with PM_BOARD_SCORING=1 and a board-eligible receipt."""
    rec = validate_receipt(dict(rec))
    lane, tag = me()
    if rec["lane"] != lane:
        raise ValueError("a lane files only its own receipts")
    if os.environ.get("PM_RECEIPT_GUARD", "1") != "0":
        problems = guard_git(rec)
        if problems:
            raise ReceiptError("receipt guard: " + "; ".join(problems))
    r = r or conn()
    eng = dict(rec["engineering"])
    eng.setdefault("host_load", host_load(r))
    rec["engineering"] = eng
    validate_receipt(rec)
    rec.setdefault("tag", tag)
    rec.setdefault("ts", time.time())
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    with open(LEDGER_DIR / f"{lane}.jsonl", "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")
        fh.flush()
    mid = r.xadd(RESULTS, {"json": json.dumps(rec, sort_keys=True)})
    eligible = board_eligible(rec)
    if os.environ.get("PM_BOARD_SCORING") == "1":      # round 1 behaviour; OFF in round 2 (SWARM_R2 s0):
        if board and eligible:                         # no session scores its own receipt; a scorer
            for metric, score in board.items():        # program over rows replaces boards (backlog F12)
                r.zincrby(f"pm:board:{metric}", float(score), f"{lane}:{rec['exp_id']}")
        if rec["status"] == "KILL" and eligible:
            r.zincrby("pm:board:kills", 1.0, lane)
    post("kill" if rec["status"] == "KILL" else "result",
         f"{rec['exp_id']} {rec['status']}{'' if eligible else ' (not board-eligible)'}",
         body=rec["claim"], ref=str(rec["rows"]), r=r)
    return mid


def standings(metric: str, n: int = 10, r=None) -> list[tuple[str, float]]:
    r = r or conn()
    return r.zrevrange(f"pm:board:{metric}", 0, n - 1, withscores=True)


# ------------------------------------------------------------------ ANOMALY queue

def anomaly_add(subject: str, observation: str, expected: str = "", surprise: str = "",
                discriminator: str = "", source: str = "", r=None) -> str:
    lane, tag = me()
    r = r or conn()
    aid = r.xadd(ANOMALIES, {"subject": subject, "observation": observation, "expected": expected,
                             "surprise": surprise, "discriminator": discriminator, "source": source,
                             "lane": lane, "tag": tag, "ts": f"{time.time():.3f}"})
    r.hset(ANOM_STATUS, aid, "OPEN")
    post("anomaly", subject, observation, ref=aid, r=r)
    return aid


def anomaly_list(status: str | None = None, r=None) -> list[tuple[str, dict, str]]:
    r = r or conn()
    st = r.hgetall(ANOM_STATUS)
    return [(aid, f, st.get(aid, "OPEN")) for aid, f in r.xrange(ANOMALIES)
            if status is None or st.get(aid, "OPEN") == status]


def anomaly_resolve(aid: str, status: str, note: str, exp_id: str = "", r=None) -> None:
    if status not in ANOM_STATES:
        raise ValueError(f"status must be one of {ANOM_STATES}")
    lane, tag = me()
    r = r or conn()
    if not r.xrange(ANOMALIES, aid, aid):
        raise KeyError(f"no anomaly {aid}")
    r.hset(ANOM_STATUS, aid, status)
    r.xadd(ANOM_EVENTS, {"id": aid, "status": status, "note": note, "exp_id": exp_id,
                         "lane": lane, "tag": tag, "ts": f"{time.time():.3f}"})
    post("note", f"ANOMALY {aid} -> {status}", note, ref=exp_id, r=r)


def anomaly_seed(path, r=None) -> list[str]:
    """Add each JSONL record {subject, observation, expected, surprise, discriminator,
    source} unless an anomaly with the same subject already exists."""
    r = r or conn()
    have = {f.get("subject") for _, f in r.xrange(ANOMALIES)}
    added = []
    for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        if d["subject"] in have:
            continue
        added.append(anomaly_add(d["subject"], d["observation"], d.get("expected", ""),
                                 d.get("surprise", ""), d.get("discriminator", ""), d.get("source", ""), r=r))
        have.add(d["subject"])
    return added
