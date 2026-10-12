"""INTEGRATION_READY notification sidecar (C-016-T011; operator Continuous Observatory directive s7).

READS workgraph task state (ops/campaigns/*/tasks/*/TASK.json) and WRITES only comms messages. It never merges,
never changes task state, never edits workgraph/ or comms/. The idempotency record is the comms message itself
(a row in the program's one Postgres queue, found by task_ref + a marker in the subject): durable, shared by every
host, and the same fact a second scanner reads. A local temp file is deliberately not used.

One notice per (task_id, attempt key). The attempt key is the branch head sha stated in the INTEGRATION_READY
history note, else the end_sha of the newest attempts/*/RECEIPT.json, else the transition's own timestamp.
"""
import contextlib
import datetime
import json
import re
from pathlib import Path

SHA_RE = re.compile(r"\b([0-9a-f]{40})\b")
NOTICE_MARK = "[notify:{}]"
DISP_MARK = "[notify-disp:{}]"


def _load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def _parse(ts):
    return datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)


def _now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _receipt_sha(task_dir):
    best = None
    for f in sorted(Path(task_dir).glob("attempts/*/RECEIPT.json")):
        try:
            sha = _load(f).get("end_sha")
        except (ValueError, OSError):
            continue
        if sha:
            best = sha
    return best


def integration_entries(task_dir, task):
    """Every INTEGRATION_READY entry in the task history, with its key and the history entry that followed it."""
    hist = task.get("history", [])
    last_ir = max([j for j, x in enumerate(hist) if x.get("status") == "INTEGRATION_READY"] or [-1])
    out = []
    for i, h in enumerate(hist):
        if h.get("status") != "INTEGRATION_READY":
            continue
        m = SHA_RE.search(h.get("note", ""))
        sha = m.group(1) if m else None
        if sha is None and i == last_ir:
            sha = _receipt_sha(task_dir)
        ident = sha or "ts:" + h.get("at_utc", "?")
        nxt = hist[i + 1] if i + 1 < len(hist) else None
        out.append({"key": "{}@{}".format(task["task_id"], ident), "sha": sha, "at_utc": h.get("at_utc"),
                    "by": h.get("by"), "note": h.get("note", ""), "next": nxt})
    return out


def disposition_of(entry):
    nxt = entry["next"]
    if nxt is None:
        return None
    s = nxt.get("status")
    return "SENT_BACK" if s == "IMPLEMENTING" else s


def _pick_campaigns(root, campaigns, coordinator):
    chosen = []
    for f in sorted(Path(root).glob("*/CAMPAIGN.json")):
        c = _load(f)
        cid = c.get("campaign_id", f.parent.name)
        if campaigns is not None and cid not in campaigns:
            continue
        if coordinator is not None and c.get("coordinator_role") != coordinator:
            continue
        chosen.append(cid)
    return chosen


def _tasks(root, campaigns, coordinator):
    for cid in _pick_campaigns(root, campaigns, coordinator):
        for f in sorted((Path(root) / cid).glob("tasks/*/TASK.json")):
            yield f.parent, _load(f)


def _locked(sink, key):
    fn = getattr(sink, "locked", None)
    return fn(key) if fn else contextlib.nullcontext()


def _subject(task, entry):
    return "INTEGRATION_READY {} @{} {}".format(task["task_id"], (entry["sha"] or "no-sha")[:12],
                                                 NOTICE_MARK.format(entry["key"]))


def _body(task, entry, now):
    age = int((_parse(now) - _parse(entry["at_utc"])).total_seconds() // 60)
    return "\n".join([
        "Integration-ready notice (rso.scale.notify; idempotency key {}).".format(entry["key"]),
        "task: {} -- {}".format(task["task_id"], task.get("title", "")),
        "campaign: {}   owner: {}   entered INTEGRATION_READY by {} at {} ({} min ago)".format(
            task.get("campaign_id"), task.get("owner_role"), entry["by"], entry["at_utc"], age),
        "head sha: {}".format(entry["sha"] or "(not stated; keyed by transition timestamp)"),
        "builder note: {}".format(entry["note"]),
        "",
        "This notice is information only. It does not merge, change task state, or waive any test, ownership or",
        "frozen-evidence check; integrate through the normal required validation. Queue: python -m rso.scale.notify queue",
    ])


def scan(root, sink, campaigns=None, coordinator=None, now=None, dry_run=False):
    """Post one notice per pending INTEGRATION_READY (task, attempt key); record dispositions of earlier ones."""
    now = now or _now()
    res = {"posted": [], "already": [], "dispositions": [], "dry_run": dry_run}
    for tdir, task in _tasks(root, campaigns, coordinator):
        for e in integration_entries(tdir, task):
            tid = task["task_id"]
            disp = disposition_of(e)
            if disp is None:                                   # still pending: notify once
                with _locked(sink, e["key"]):
                    if sink.find(tid, NOTICE_MARK.format(e["key"])):
                        res["already"].append(e["key"])
                    elif dry_run:
                        res["posted"].append({"key": e["key"], "id": None})
                    else:
                        mid = sink.post(_subject(task, e), _body(task, e, now), tid)
                        res["posted"].append({"key": e["key"], "id": mid})
            else:                                              # decided: record only if we had notified it
                if not sink.find(tid, NOTICE_MARK.format(e["key"])):
                    continue
                with _locked(sink, "disp:" + e["key"]):
                    if sink.find(tid, DISP_MARK.format(e["key"])):
                        continue
                    n = e["next"]
                    rec = {"key": e["key"], "disposition": disp, "by": n.get("by"), "at_utc": n.get("at_utc"), "id": None}
                    if not dry_run:
                        rec["id"] = sink.post(
                            "DISPOSITION {} {} {}".format(tid, disp, DISP_MARK.format(e["key"])),
                            "{} -> {} by {} at {}: {}\nnotice key {}".format(
                                tid, disp, n.get("by"), n.get("at_utc"), n.get("note", ""), e["key"]),
                            tid)
                    res["dispositions"].append(rec)
    return res


def queue(root, sink, campaigns=None, coordinator=None, now=None):
    """The pending integration queue, oldest first. notified is None when no sink is available."""
    now = now or _now()
    rows = []
    for tdir, task in _tasks(root, campaigns, coordinator):
        if task.get("status") != "INTEGRATION_READY":
            continue
        e = [x for x in integration_entries(tdir, task) if x["next"] is None][-1]
        rows.append({"task_id": task["task_id"], "campaign_id": task.get("campaign_id"), "owner": task.get("owner_role"),
                     "sha": e["sha"], "since_utc": e["at_utc"], "by": e["by"], "key": e["key"],
                     "age_minutes": int((_parse(now) - _parse(e["at_utc"])).total_seconds() // 60),
                     "notified": None if sink is None else bool(sink.find(task["task_id"], NOTICE_MARK.format(e["key"])))})
    rows.sort(key=lambda r: r["since_utc"])
    return rows


class DbSink:
    """The comms queue as the idempotency record. Needs EW_DB_HOST on a host that is not M1."""

    def __init__(self, sender="Eupalamus", to=("Palamedes",), kind="report"):
        from comms import api
        self.api, self.sender, self.to, self.kind = api, sender, list(to), kind
        self.conn = api.connect()

    def find(self, task_ref, marker):
        cur = self.conn.cursor()
        cur.execute("SELECT id FROM {}.messages WHERE task_ref = %s AND strpos(subject, %s) > 0 ORDER BY id".format(
            self.api.schema()), (task_ref, marker))
        rows = cur.fetchall()
        self.conn.commit()
        return [r[0] for r in rows]

    def post(self, subject, body, task_ref):
        return self.api.post(self.conn, self.sender, self.to, self.kind, subject, body, task_ref=task_ref)

    @contextlib.contextmanager
    def locked(self, key):
        """Session advisory lock so two scanners cannot both pass find() before either posts."""
        cur = self.conn.cursor()
        cur.execute("SELECT pg_advisory_lock(hashtextextended(%s, 0))", ("rso.notify:" + key,))
        self.conn.commit()
        try:
            yield
        finally:
            cur.execute("SELECT pg_advisory_unlock(hashtextextended(%s, 0))", ("rso.notify:" + key,))
            self.conn.commit()
