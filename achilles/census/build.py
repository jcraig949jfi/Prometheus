"""Assemble the canonical fleet snapshot (schema prometheus.fleet_census.v2).

v2 extends Aporia's prometheus.fleet_census.v1 (ops/fleet/CENSUS.json): every v1 column
(host_instance, uptime, model, state, current_work, blocker, last_heartbeat) is present per seat,
and every important field is also carried as a provenance object {value, source, source_time,
observed_at, confidence}. HTML and email are renderings of this object and nothing else.

Incremental by design: per-seat aggregates (latest commit / experiment / message / assignment)
are carried forward from the previous snapshot and updated only with commits not reachable from
the previous ref tips and messages above the previous comms cursor. A deep pass (no previous
snapshot, roster or registry change, or 7 days since the last deep pass) rebuilds them from all
history.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from . import classify as C
from . import sources as S
from . import util
from .util import field, iso, parse_time, age_hours, human_age

SCHEMA = "prometheus.fleet_census.v2"
DEEP_EVERY_H = 24 * 7
SEAT_KINDS = ("SEAT", "BRANCH_ONLY_SEAT")
REPO_URL = "https://github.com/jcraig949jfi/Prometheus"


# ---------------------------------------------------------------- registry

def load_registry(root: Path) -> tuple:
    reg_dir = root / "roles" / "Achilles" / "census" / "registry"
    seats, engines = {}, {}
    for p in sorted(reg_dir.glob("seats_part*.json")):
        doc = util.read_json(p, {}) or {}
        for s in doc.get("seats", []):
            if s.get("seat"):
                s["_registry_file"] = "roles/Achilles/census/registry/" + p.name
                seats[s["seat"]] = s
    doc = util.read_json(reg_dir / "engines.json", {}) or {}
    for e in doc.get("engines", []):
        if e.get("engine_id"):
            engines[e["engine_id"]] = e
    h = hashlib.sha256()
    for p in sorted(reg_dir.glob("*.json")):
        h.update(p.read_bytes().replace(b"\r\n", b"\n"))
    return seats, engines, h.hexdigest()[:16]


# ---------------------------------------------------------------- aggregates

def _newer(a: dict | None, b: dict | None) -> dict | None:
    """The later of two events by 'time'."""
    if not a:
        return b
    if not b:
        return a
    ta, tb = parse_time(a.get("time")), parse_time(b.get("time"))
    if ta is None:
        return b
    if tb is None:
        return a
    return b if tb > ta else a


def _push_recent(lst: list, ev: dict, n: int = 6, key="sha") -> list:
    lst = [x for x in (lst or []) if x.get(key) != ev.get(key)] + [ev]
    lst.sort(key=lambda x: parse_time(x.get("time")) or parse_time("1970-01-01"), reverse=True)
    return lst[:n]


def apply_commits(aggs: dict, eng_aggs: dict, commits: list, roster: C.Roster, path_owner, engine_of, stats: dict):
    for c in commits:
        attr = C.attribute_commit(c["subject"], c["trailers"], c["files"], c["author"], roster, path_owner)
        seat = attr["seat"]
        ev = {"sha": c["sha"][:10], "time": iso(parse_time(c["time"])), "subject": c["subject"][:200], "basis": attr["basis"],
              "instance": attr["instance"], "host": attr["host"]}
        for eid in {engine_of(f) for f in c["files"]} - {None}:
            ea = eng_aggs.setdefault(eid, {})
            ea["last"] = _newer(ea.get("last"), dict(ev, seat=seat))
            ea["recent"] = _push_recent(ea.get("recent"), {"sha": ev["sha"], "time": ev["time"], "seat": seat}, n=12)
        if seat is None:
            stats["unattributed"] = stats.get("unattributed", 0) + 1
            stats.setdefault("unattributed_sample", [])
            if len(stats["unattributed_sample"]) < 8:
                stats["unattributed_sample"].append("{} {}".format(ev["sha"], ev["subject"][:80]))
            continue
        if seat == "SYSTEM":
            stats["system"] = stats.get("system", 0) + 1
            a = aggs.setdefault("SYSTEM", {})
            a["commit_last"] = _newer(a.get("commit_last"), ev)
            continue
        cat = C.commit_category(c["subject"], c["files"])
        ev["category"] = cat
        a = aggs.setdefault(seat, {})
        a["commit_last"] = _newer(a.get("commit_last"), ev)
        a["recent_commits"] = _push_recent(a.get("recent_commits"), ev)
        if cat == "status":
            a["status_commit_last"] = _newer(a.get("status_commit_last"), ev)
        else:
            a["work_last"] = _newer(a.get("work_last"), ev)
        if cat in ("experiment_result", "experiment_start"):
            x = dict(ev, type=cat, verdict=C.verdict_token(c["subject"]))
            a["exp_last"] = _newer(a.get("exp_last"), x)
            a["recent_experiments"] = _push_recent(a.get("recent_experiments"), x)
            if cat == "experiment_result":
                a["exp_result_last"] = _newer(a.get("exp_result_last"), x)


def apply_messages(aggs: dict, msgs: list, roster: C.Roster, stats: dict, unknown_senders: set):
    for m in msgs:
        sender = roster.resolve(m["sender"])
        t = iso(m["created_at"])
        ev = {"id": m["id"], "time": t, "kind": m["kind"], "subject": (m["subject"] or "")[:200],
              "to": ",".join(m["recipients"] or [])[:80], "instance": m.get("sender_instance")}
        if sender is None:
            unknown_senders.add(m["sender"])
        else:
            a = aggs.setdefault(sender, {})
            lvl = C.message_level(m["kind"], m["subject"])
            ev["level"] = lvl
            if lvl == 3:
                a["msg_sub_last"] = _newer(a.get("msg_sub_last"), ev)
                a["recent_messages"] = _push_recent(a.get("recent_messages"), ev, key="id")
            elif lvl == 4:
                a["msg_status_last"] = _newer(a.get("msg_status_last"), ev)
            else:
                a["msg_ack_last"] = _newer(a.get("msg_ack_last"), ev)
        if m["kind"] in ("prompt", "delegation"):
            for r in m["recipients"] or []:
                if r == "*":
                    continue
                seat = roster.resolve(r)
                if seat:
                    b = aggs.setdefault(seat, {})
                    b["assign_last"] = _newer(b.get("assign_last"), dict(ev, sender=m["sender"]))
        stats["messages"] = stats.get("messages", 0) + 1


# ---------------------------------------------------------------- per-seat assembly

def _ws_task(ws: dict | None):
    if not ws:
        return None
    for k in ("current_objective", "current", "CURRENT"):
        v = ws.get(k)
        if v:
            return v if isinstance(v, str) else json.dumps(v)[:300]
    na = ws.get("next_actions")
    if isinstance(na, list) and na:
        return str(na[0])
    return None


def _ws_blocker(ws: dict | None):
    if not ws:
        return None
    for k in ("blocked_on", "blocked"):
        v = ws.get(k)
        if v and v not in ("none", "None", [], {}):
            return v if isinstance(v, str) else json.dumps(v)[:300]
    return None


def _status_next_action(text: str | None):
    if not text:
        return None
    import re
    m = re.search(r"(?im)^\s*next executable action\s*:\s*(.+(?:\n\s{2,}.+)*)", text)
    return " ".join(m.group(1).split())[:300] if m else None


def _ev_text(ev: dict | None, kind: str) -> str | None:
    if not ev:
        return None
    if kind == "commit":
        return "commit {} {}".format(ev["sha"], ev["subject"])
    return "comms #{} {} to {}: {}".format(ev["id"], ev["kind"], ev.get("to") or "?", ev["subject"])


def assemble_seat(name, kind, reg, files, ws, ws_src, agg, comms_row, ew_row, agora_row, ledgers, oprompt,
                  status_time, now, base_sha):
    """One census row. Every value that matters is a provenance field."""
    flags = []
    evidence = []
    domain = (reg or {}).get("domain") or "unknown"

    # ---- activity
    work = agg.get("work_last")
    msg = agg.get("msg_sub_last")
    ewx = None
    if ew_row:
        ewx = {"time": iso(ew_row["created_at"]), "title": ew_row.get("title"), "id": ew_row.get("experiment_id"),
               "git_commit": ew_row.get("git_commit")}
    cands = []
    if work:
        cands.append(("commit", work))
    if msg:
        cands.append(("message", msg))
    if ewx:
        cands.append(("ew", ewx))
    sub_kind, sub_ev = (None, None)
    for k, ev in cands:
        if sub_ev is None or (parse_time(ev["time"]) or parse_time("1970-01-01")) > parse_time(sub_ev["time"]):
            sub_kind, sub_ev = k, ev
    status_evs = [e for e in (agg.get("status_commit_last"), agg.get("msg_status_last")) if e]
    ws_t = parse_time((ws or {}).get("updated_at_utc") or (ws or {}).get("updated_at"))
    if ws_t:
        status_evs.append({"time": iso(ws_t), "subject": "WORK_STATE updated", "src": ws_src})
    status_ev = None
    for e in status_evs:
        status_ev = _newer(status_ev, e)
    pres_times = []
    if comms_row:
        for k in ("last_sync_at", "last_active_at"):
            if comms_row.get(k):
                pres_times.append((comms_row[k], "comms.agents." + k))
    if agora_row and agora_row.get("last_heartbeat"):
        pres_times.append((agora_row["last_heartbeat"], "agora.agent_heartbeats (legacy, weak)"))
    pres = max(pres_times, key=lambda p: p[0]) if pres_times else None

    sub_t = parse_time(sub_ev["time"]) if sub_ev else None
    activity = {"substantive_age_h": age_hours(sub_t, now),
                "status_age_h": age_hours(parse_time(status_ev["time"]), now) if status_ev else None,
                "presence_age_h": age_hours(pres[0], now) if pres else None}

    # ---- declared states (newest first)
    declared = []
    if ws and ws.get("state"):
        declared.append({"state": C.normalise_state(ws["state"]), "raw": str(ws["state"])[:120], "source": ws_src,
                         "time": iso(ws_t), "age_h": age_hours(ws_t, now)})
    v1 = (ledgers["census_v1"].get("seats") or {}).get(name)
    v1_t = parse_time(ledgers["census_v1"].get("as_of_utc") or (ledgers["census_v1"].get("discovery") or {}).get("at_utc"))
    if v1:
        raw = (v1.get("forward") or {}).get("state") or v1.get("state")
        if raw:
            declared.append({"state": C.normalise_state(raw), "raw": str(raw)[:120],
                             "source": "ops/fleet/CENSUS.json (Aporia v1)", "time": iso(v1_t), "age_h": age_hours(v1_t, now)})
    if comms_row and comms_row.get("status") in ("parked", "retired", "idle", "paused"):
        ct = comms_row.get("updated_at")
        declared.append({"state": C.normalise_state(comms_row["status"]), "raw": comms_row["status"],
                         "source": "comms.agents.status", "time": iso(ct), "age_h": age_hours(ct, now)})
    st_state, st_line = C.status_md_state(files.get("status_text"))
    if st_state:
        declared.append({"state": st_state, "raw": st_line, "source": "roles/{}/STATUS.md".format(name),
                         "time": iso(status_time), "age_h": age_hours(status_time, now)})
    declared.sort(key=lambda d: d["age_h"] if d.get("age_h") is not None else 1e12)

    marker = dict((reg or {}).get("lifecycle_marker") or {})
    if marker.get("date") and sub_t:
        mt = parse_time(marker["date"])
        marker["after_marker_activity"] = bool(mt and (sub_t - mt).total_seconds() > 86400)
    if kind == "HISTORICAL_ROLE_DOC" and not marker.get("state"):
        marker["state"] = None
    cls = C.classify_seat(kind, declared, activity, marker)
    flags += cls["flags"]

    # ---- task set
    tcands = []
    q = (ledgers["queue"].get("seats") or {}).get(name)
    qt = parse_time(ledgers["queue"].get("updated_at_utc"))
    if q and q.get("current"):
        tcands.append({"value": str(q["current"])[:300], "source": "ops/fleet/QUEUE.json seats.{}.current".format(name),
                       "time": iso(qt), "rank": 1})
    if v1 and (v1.get("forward") or {}).get("current_objective"):
        tcands.append({"value": str(v1["forward"]["current_objective"])[:300],
                       "source": "ops/fleet/CENSUS.json seats.{}.forward.current_objective".format(name),
                       "time": iso(v1_t), "rank": 1})
    if oprompt:
        tcands.append({"value": "operator directive {}: {}".format(oprompt["path"].rsplit("/", 1)[-1], oprompt["excerpt"])[:300],
                       "source": oprompt["path"], "time": oprompt.get("committed") or oprompt["date"], "rank": 2})
    al = agg.get("assign_last")
    if al:
        tcands.append({"value": "{} from {}: {}".format(al["kind"], al.get("sender"), al["subject"])[:300],
                       "source": "comms #{}".format(al["id"]), "time": al["time"], "rank": 3})
    task = None
    for c in tcands:
        if task is None or (parse_time(c["time"]) or parse_time("1970-01-01")) > (parse_time(task["time"]) or parse_time("1970-01-01")):
            task = c
    if task is None and _ws_task(ws):
        task = {"value": _ws_task(ws)[:300], "source": ws_src + " (seat's own state)", "time": iso(ws_t), "rank": 4}
    if task is None and _status_next_action(files.get("status_text")):
        task = {"value": _status_next_action(files.get("status_text")), "source": "roles/{}/STATUS.md next executable action".format(name),
                "time": iso(status_time), "rank": 6}
    if task and sub_t and parse_time(task["time"]) and cls["state"] in ("WORKING", "ACTIVE", "BLOCKED"):
        tt = parse_time(task["time"])
        if (now - tt).total_seconds() > 86400 and sub_t < tt:
            flags.append("ASSIGNMENT_NO_PROGRESS")

    # ---- last experiment
    exp = agg.get("exp_last")
    exp_field = None
    if exp:
        exp_field = field("{} {}".format(exp["sha"], exp["subject"]), "git commit {}".format(exp["sha"]), exp["time"], now,
                          "HIGH" if exp.get("basis") == "subject-prefix" else "MEDIUM",
                          type=exp["type"], verdict=exp.get("verdict"), sha=exp["sha"],
                          url="{}/commit/{}".format(REPO_URL, exp["sha"]))
    if ewx and (exp is None or parse_time(ewx["time"]) > parse_time(exp["time"])):
        exp_field = field("ew {}: {}".format(ewx["id"], ewx["title"]), "ew.experiments", ewx["time"], now, "MEDIUM",
                          type="evidence_wiki", verdict=None, sha=ewx.get("git_commit"))
    if exp_field is None and domain in ("infrastructure", "reporting", "coordination", "audit"):
        exp_field = field("N/A ({})".format(domain), "registry domain", None, now, "MEDIUM", type="na", verdict=None)
    exp_result = None
    if exp_field and exp_field.get("type") == "experiment_result":
        exp_result = exp_field.get("verdict") or "see subject"
    elif exp_field and exp_field.get("type") == "experiment_start":
        exp_result = "started/preregistered; no result commit yet"

    # ---- last commit
    lc = agg.get("commit_last")
    lc_field = field("{} {}".format(lc["sha"], lc["subject"]), "git ({})".format(lc.get("basis")), lc["time"], now,
                     "HIGH" if lc.get("basis") in ("subject-prefix", "instance-trailer") else "MEDIUM",
                     sha=lc["sha"], url="{}/commit/{}".format(REPO_URL, lc["sha"])) if lc else None

    # ---- host
    host = None
    if comms_row and comms_row.get("newest_instance"):
        ni = comms_row["newest_instance"]
        h = C.host_from_machine(ni.get("machine")) or C.host_from_instance(ni.get("instance"))
        if h:
            host = field(h, "comms.agent_instances {}".format(ni.get("instance")), ni.get("last_sync_at") or ni.get("last_active_at"), now, "HIGH",
                         instance=ni.get("instance"), machine=ni.get("machine"))
    if host is None and lc and lc.get("host"):
        host = field(lc["host"], "instance tag in commit {}".format(lc["sha"]), lc["time"], now, "MEDIUM", instance=lc.get("instance"))
    dh = ((reg or {}).get("documented_host") or {})
    if host is None and dh.get("value"):
        host = field(dh["value"], dh.get("source") or "registry", None, now, "LOW")
    elif host and dh.get("value") and dh["value"] != host["value"]:
        host["documented"] = dh["value"]
        host["documented_source"] = dh.get("source")

    # ---- branch / worktree
    bw = None
    if comms_row and (comms_row.get("last_sync_branch") or comms_row.get("branch")):
        bw = field("{} @ {}".format(comms_row.get("last_sync_branch") or comms_row.get("branch"),
                                    comms_row.get("last_sync_worktree") or comms_row.get("worktree_path")),
                   "comms.agents last sync", comms_row.get("last_sync_at"), now, "MEDIUM")
    elif ws and ws.get("branch"):
        bw = field(ws["branch"], ws_src, ws_t, now, "MEDIUM")

    # ---- blocker
    blk = None
    if _ws_blocker(ws):
        blk = field(_ws_blocker(ws), ws_src, ws_t, now, "MEDIUM")
    elif q and q.get("blocked"):
        blk = field(json.dumps(q["blocked"])[:300], "ops/fleet/QUEUE.json seats.{}.blocked".format(name), qt, now, "MEDIUM")
    elif v1 and v1.get("blocker") and str(v1["blocker"]).lower() not in ("none", "-", "null"):
        blk = field(str(v1["blocker"])[:300], "ops/fleet/CENSUS.json seats.{}.blocker".format(name), v1_t, now, "MEDIUM")

    # ---- heartbeat (v1 column; weak evidence)
    hb = agg.get("msg_status_last")

    # ---- role
    reg = reg or {}
    dr = reg.get("declared_role") or {}
    orole = reg.get("observed_role") or {}
    role_desc = dr.get("text") or None
    if not role_desc:
        flags.append("MISSING_ROLE_DESCRIPTION")
    if not files.get("entry_file") and kind == "SEAT":
        flags.append("NO_ROLE_DOCUMENT")

    # ---- evidence list (strongest first)
    if sub_ev:
        evidence.append({"what": "last substantive activity", "ref": _ev_text(sub_ev, "commit" if sub_kind == "commit" else "msg")
                         if sub_kind != "ew" else "ew experiment {}".format(sub_ev.get("id")), "time": sub_ev["time"]})
    if exp:
        evidence.append({"what": "last experiment commit", "ref": exp["sha"], "time": exp["time"]})
    if ws_src:
        evidence.append({"what": "declared state", "ref": ws_src, "time": iso(ws_t)})
    if task:
        evidence.append({"what": "task source", "ref": task["source"], "time": task["time"]})
    if pres:
        evidence.append({"what": "presence (weak)", "ref": pres[1], "time": iso(pres[0])})
    if files.get("entry_file"):
        evidence.append({"what": "role document", "ref": files["entry_file"], "time": files.get("currency")})

    la = field(sub_ev["time"], {"commit": "git", "message": "comms", "ew": "ew.experiments"}[sub_kind], sub_ev["time"], now,
               "HIGH" if sub_kind == "commit" else "MEDIUM") if sub_ev else None
    last_activity_text = None
    if sub_ev:
        last_activity_text = _ev_text(sub_ev, "commit") if sub_kind == "commit" else (
            _ev_text(sub_ev, "msg") if sub_kind == "message" else "evidence wiki experiment: {}".format(sub_ev.get("title")))
    elif status_ev:
        last_activity_text = "status only: {}".format(status_ev.get("subject"))

    row = {
        # v1 columns (ops/fleet/CENSUS.json compatibility)
        "host_instance": "{} {}".format((host or {}).get("machine") or (host or {}).get("value") or "", (host or {}).get("instance") or "").strip() or None,
        "uptime": "UNKNOWN",
        "model": (comms_row or {}).get("model"),
        "state": cls["state"],
        "current_work": (task or {}).get("value"),
        "blocker": (blk or {}).get("value"),
        "last_heartbeat": "#{} {}".format(hb["id"], hb["time"]) if hb else None,
        # v2
        "kind": kind,
        "short_role": reg.get("short_role"),
        "role_description": field(role_desc, dr.get("source") or "registry", dr.get("source_currency"), now,
                                  "HIGH" if dr.get("source") else "LOW"),
        "observed_role": orole if orole.get("differs") else None,
        "domain": domain,
        "lifecycle_marker": reg.get("lifecycle_marker"),
        "aliases": reg.get("aliases") or [],
        "engines": reg.get("engines") or [],
        "state_detail": {"value": cls["state"], "rule": cls["rule"], "why": cls["why"], "declared": declared,
                         "activity": {k: (None if v is None else round(v, 2)) for k, v in activity.items()},
                         "confidence": cls["confidence"]},
        "active": cls["active"],
        "last_active": la,
        "activity_age": human_age(activity["substantive_age_h"]),
        "last_activity": last_activity_text,
        "last_status_update": status_ev,
        "presence": {"value": iso(pres[0]), "source": pres[1]} if pres else None,
        "task": field(task["value"], task["source"], task["time"], now, "HIGH" if task["rank"] <= 2 else "MEDIUM",
                      candidates=tcands) if task else None,
        "last_experiment": exp_field,
        "experiment_result": exp_result,
        "last_commit": lc_field,
        "branch_worktree": bw,
        "host": host,
        "blocker_detail": blk,
        "evidence": evidence,
        "confidence": cls["confidence"],
        "flags": sorted(set(flags)),
        "entry_file": files.get("entry_file"),
        "role_doc_currency": files.get("currency"),
    }
    return row


# ---------------------------------------------------------------- whole fleet

def build(root: Path, prev: dict | None, conn, conn_err: str | None, now, run_info: dict, force_deep=False) -> dict:
    git = util.Git(root)
    tips = S.ref_tips(git)
    base_sha = tips.get("origin/main")
    reg_seats, reg_engines, reg_hash = load_registry(root)
    main_roles = set(S.roles_on_ref(git, "origin/main"))
    branch_only = S.branch_only_roles(git, tips, main_roles)

    # entity universe: roles/ on main, roles/ on branches only, registry non-seat entities
    kinds = {}
    for n in main_roles:
        kinds[n] = (reg_seats.get(n) or {}).get("kind") or "SEAT"
        if kinds[n] == "BRANCH_ONLY_SEAT":
            kinds[n] = "SEAT"
    for n in branch_only:
        kinds[n] = "BRANCH_ONLY_SEAT"
    for n, r in reg_seats.items():
        if n not in kinds and r.get("kind") == "AGENT_TOOL":
            kinds[n] = "AGENT_TOOL"
    roster_hash = hashlib.sha256("\n".join(sorted(kinds)).encode()).hexdigest()[:16]

    # Aliases only when the alias is a single bare token (free-text alias notes never match a subject),
    # and never over a canonical name (Roster.resolve checks canonical names first).
    aliases = {}
    for n, r in reg_seats.items():
        for a in r.get("aliases") or []:
            nm = (a.get("name") or "").strip()
            if a.get("relation") in ("lane", "instance") and re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{2,}", nm):
                aliases[nm] = n
    roster = C.Roster(list(kinds), aliases)

    # path -> owner seat (roles/<Seat>/ and engine primary seats, longest prefix)
    eng_paths = []
    for eid, e in reg_engines.items():
        for p in e.get("paths") or [eid]:
            eng_paths.append((p.rstrip("/").lower(), eid, e.get("primary_seat")))
    eng_paths.sort(key=lambda t: -len(t[0]))
    lower_roles = {n.lower(): n for n in kinds}

    def engine_of(f):
        fl = f.lower()
        for p, eid, _ in eng_paths:
            if fl == p or fl.startswith(p + "/"):
                return eid
        return None

    def path_owner(f):
        parts = f.split("/")
        if len(parts) > 2 and parts[0] == "roles" and parts[1].lower() in lower_roles:
            n = lower_roles[parts[1].lower()]
            return n if kinds.get(n) in SEAT_KINDS else None
        fl = f.lower()
        for p, _eid, owner in eng_paths:
            if owner and (fl == p or fl.startswith(p + "/")):
                return owner
        return None

    prev = prev if (prev and prev.get("schema") == SCHEMA) else None
    pc = (prev or {}).get("cursors") or {}
    last_deep = parse_time(pc.get("last_deep_utc"))
    deep = force_deep or prev is None or pc.get("roster_hash") != roster_hash or pc.get("registry_hash") != reg_hash \
        or last_deep is None or age_hours(last_deep, now) > DEEP_EVERY_H
    stats = {"mode": "deep" if deep else "incremental"}

    aggs = {} if deep else json.loads(json.dumps((prev or {}).get("aggregates") or {}))
    eng_aggs = {} if deep else json.loads(json.dumps((prev or {}).get("engine_aggregates") or {}))
    include = sorted(tips.values()) if tips else ["origin/main"]
    exclude = None if deep else [t for t in (pc.get("ref_tips") or {}).values() if git.ok("cat-file", "-e", t + "^{commit}")]
    commits = S.read_commits(git, include, exclude)
    stats["commits_scanned"] = len(commits)
    apply_commits(aggs, eng_aggs, commits, roster, path_owner, engine_of, stats)

    # windowed counts (cheap, every run)
    window = S.read_commits(git, include, None, since="24 hours ago")
    commits_24h = len(window)
    exp_24h = sum(1 for c in window if C.commit_category(c["subject"], c["files"]) == "experiment_result"
                  and not c["subject"].lower().startswith("auto:"))

    # database
    db_status = {"comms": "UNAVAILABLE: " + str(conn_err) if conn is None else "ok"}
    comms_rows, ew_rows, agora_rows, mail = {}, {}, {}, []
    unknown_senders = set()
    comms_cursor = 0 if deep else int(pc.get("comms_max_id") or 0)
    if conn is not None:
        try:
            comms_rows = S.comms_agents(conn)
            msgs = S.comms_messages(conn, comms_cursor)
            apply_messages(aggs, msgs, roster, stats, unknown_senders)
            if msgs:
                comms_cursor = max(m["id"] for m in msgs)
        except Exception as e:
            db_status["comms"] = "ERROR: {}".format(str(e)[:200])
        try:
            ew_rows = S.ew_experiments(conn)
            db_status["ew"] = "ok"
        except Exception as e:
            db_status["ew"] = "ERROR: {}".format(str(e)[:200])
        agora_rows = S.agora_heartbeats(conn)
        mail = S.mailer_events(conn)
        db_status["agora"] = "ok" if agora_rows else "empty/unavailable"
    else:
        # comms aggregates carried from the previous snapshot are still valid history; say so
        db_status["note"] = "comms-derived fields carried from previous snapshot (cursor {})".format(comms_cursor)

    ledgers = S.ops_ledgers(root)
    mons = S.monitors(root)

    # STATUS.md commit times (one cheap git call per seat with a STATUS.md)
    seats_out = {}
    for name in sorted(kinds, key=str.lower):
        kind = kinds[name]
        files = S.seat_files(root, name) if kind != "AGENT_TOOL" else {"dir_exists": False}
        if kind == "BRANCH_ONLY_SEAT":
            ref = branch_only[name][0]
            files["entry_file"] = "{}:roles/{}/".format(ref, name)
        ws, ws_src = (S.newest_work_state(git, root, name, tips) if kind in SEAT_KINDS else (None, None))
        st_time = None
        if files.get("status_text"):
            out = git.run("log", "-1", "--format=%cI", "origin/main", "--", "roles/{}/STATUS.md".format(name), check=False).strip()
            st_time = parse_time(out)
        oprompt = S.operator_prompt(git, root, name) if kind in SEAT_KINDS else None
        reg = reg_seats.get(name)
        ew_row = ew_rows.get(name)
        seats_out[name] = assemble_seat(name, kind, reg, files, ws, ws_src, aggs.get(name, {}), comms_rows.get(name),
                                        ew_row, agora_rows.get(name), ledgers, oprompt, st_time, now, base_sha)
        if reg is None:
            seats_out[name]["flags"].append("NOT_IN_REGISTRY")
        # registered loops this seat owns (process state, kept apart from productive work)
        seats_out[name]["monitors"] = [{"name": m["name"], "state": m.get("state", "")[:120], "host": m.get("host"),
                                        "kind": m.get("kind")} for m in mons
                                       if re.search(r"{}".format(re.escape(name)), m.get("owner") or "")]

    # engines
    engines_out = {}
    for eid, e in sorted(reg_engines.items()):
        ea = eng_aggs.get(eid, {})
        last = ea.get("last")
        if deep or last is None:
            lc = S.last_commit_for_paths(git, e.get("paths") or [eid])
            if lc:
                last = _newer(last, {"sha": lc["sha"][:10], "time": iso(parse_time(lc["time"])), "subject": lc["subject"][:200], "seat": None})
                ea["last"] = last
                eng_aggs[eid] = ea
        recent = ea.get("recent") or []
        contrib = {}
        for r in recent:
            if r.get("seat") and r["seat"] != "SYSTEM":
                contrib[r["seat"]] = contrib.get(r["seat"], 0) + 1
        eflags = []
        prim = e.get("primary_seat")
        known = {prim} | {o.get("seat") for o in e.get("other_seats") or []}
        if prim and sum(contrib.values()) >= 5:
            top, n = max(contrib.items(), key=lambda kv: kv[1])
            if top not in known and n * 2 > sum(contrib.values()):
                eflags.append("OWNERSHIP_DRIFT: {} of last {} attributed commits by {} (docs: {})".format(n, sum(contrib.values()), top, prim))
        lt = parse_time((last or {}).get("time"))
        if not prim and lt and age_hours(lt, now) < 24 * 7 and e.get("kind") != "data":
            eflags.append("ENGINE_NO_OWNER: commits in the last 7 days but no primary seat")
        engines_out[eid] = dict(e, last_change=last, recent_contributors=contrib, flags=eflags,
                                last_change_age=human_age(age_hours(lt, now)))

    # anomalies
    anomalies = []
    for n, row in seats_out.items():
        for f in row["flags"]:
            anomalies.append({"type": f.split(":")[0], "subject": n, "detail": "; ".join(row["state_detail"]["why"])[:300]})
    for eid, e in engines_out.items():
        for f in e["flags"]:
            anomalies.append({"type": f.split(":")[0], "subject": eid, "detail": f})
    for s in sorted(unknown_senders):
        anomalies.append({"type": "UNKNOWN_COMMS_SENDER", "subject": s, "detail": "posts to comms but has no roles/ dir or alias"})
    for a in sorted(set(comms_rows) - set(kinds) - set(aliases)):
        anomalies.append({"type": "UNKNOWN_COMMS_AGENT", "subject": a, "detail": "registered in comms.agents but no roles/ dir"})
    for led, label in ((ledgers["queue"], "ops/fleet/QUEUE.json"), (ledgers["census_v1"], "ops/fleet/CENSUS.json")):
        for s in (led.get("seats") or {}):
            if s not in kinds:
                anomalies.append({"type": "UNFAMILIAR_SEAT_IN_WORK_ORDER", "subject": s, "detail": label})
    for n in branch_only:
        anomalies.append({"type": "BRANCH_ONLY_SEAT", "subject": n, "detail": "roles/{}/ exists only on {}".format(n, ", ".join(branch_only[n][:3]))})
    if stats.get("unattributed"):
        anomalies.append({"type": "UNATTRIBUTED_COMMITS", "subject": "git", "detail": "{} scanned commits had no seat; sample: {}".format(
            stats["unattributed"], " | ".join(stats.get("unattributed_sample", [])))})
    prev_seats = (prev or {}).get("seats") or {}
    for n in sorted(set(prev_seats) - set(seats_out)):
        anomalies.append({"type": "SEAT_DISAPPEARED", "subject": n, "detail": "present in previous snapshot, absent now"})
    for n in sorted(set(seats_out) - set(prev_seats)) if prev else []:
        anomalies.append({"type": "NEW_SEAT", "subject": n, "detail": "first seen this run"})

    # mailer health (the existing mailer's own receipts)
    mail_ok = [m for m in mail if m.get("success")]
    mailer = {
        "path": "scripts/send_brief_email.py (run by scripts/intelligence_loop.py on M4)",
        "last_success": iso(mail_ok[0]["finished_at"]) if mail_ok else None,
        "last_attempt": iso(mail[0]["finished_at"]) if mail else None,
        "last_summary": S.redact(mail[0].get("output_summary") if mail else None),
        "census_included_last": bool(mail_ok and re.search(r"census=\d{4}-", mail_ok[0].get("output_summary") or "")),
        "failures_72h": sum(1 for m in mail if not m.get("success")),
        "source": "agora.intelligence_outputs stage=email_dispatched" if conn is not None else "UNAVAILABLE",
    }
    if conn is not None and not mail_ok:
        anomalies.append({"type": "EMAIL_NOT_SENT_72H", "subject": "mailer", "detail": "no successful email_dispatched event in 72h"})

    # summary
    seat_rows = {n: r for n, r in seats_out.items() if r["kind"] in SEAT_KINDS}
    counts = {}
    for r in seat_rows.values():
        counts[r["state"]] = counts.get(r["state"], 0) + 1

    def active_within(h):
        return sum(1 for r in seat_rows.values()
                   if r["state_detail"]["activity"]["substantive_age_h"] is not None and r["state_detail"]["activity"]["substantive_age_h"] <= h)

    summary = {"seats_total": len(seat_rows), "entities_total": len(seats_out), "counts_by_state": counts,
               "active_6h": active_within(6), "active_24h": active_within(24), "active_72h": active_within(72),
               "experiments_24h": exp_24h, "commits_24h": commits_24h,
               "non_seat_entities": len(seats_out) - len(seat_rows)}

    snap = {
        "schema": SCHEMA,
        "extends": "prometheus.fleet_census.v1 (ops/fleet/CENSUS.json, Aporia, CWO-2026-09-30C); v1 columns kept per seat",
        "maintainer": "Achilles (roles/Achilles; charter roles/Achilles/prompts/2026-09-30_charter/)",
        "rules": "roles/Achilles/CLASSIFICATION_RULES.md",
        "generated_at_utc": iso(now),
        "base_sha": base_sha,
        "current_mwo": ledgers["current_mwo"],
        "latest_cwo": ledgers["latest_cwo"],
        "run": run_info,
        "sources_status": dict(db_status, git="ok", registry=reg_hash, monitors_rows=len(mons)),
        "summary": summary,
        "mailer": mailer,
        "seats": seats_out,
        "engines": engines_out,
        "anomalies": anomalies,
        "stats": stats,
        "cursors": {"ref_tips": tips, "comms_max_id": comms_cursor, "roster_hash": roster_hash,
                    "registry_hash": reg_hash, "last_deep_utc": iso(now) if deep else pc.get("last_deep_utc")},
        "aggregates": aggs,
        "engine_aggregates": eng_aggs,
    }
    snap["delta"] = delta(prev, snap)
    return snap


# ---------------------------------------------------------------- delta

def delta(prev: dict | None, cur: dict) -> dict:
    out = {"previous_generated_at": (prev or {}).get("generated_at_utc"), "seats_activated": [], "seats_went_quiet": [],
           "state_changes": [], "new_assignments": [], "experiments_completed": [], "blockers_added": [],
           "blockers_cleared": [], "new_seats": [], "engine_ownership_changes": [], "new_anomalies": []}
    if not prev:
        out["note"] = "first run: no previous snapshot"
        return out
    ps = prev.get("seats") or {}
    for n, r in cur["seats"].items():
        p = ps.get(n)
        if p is None:
            out["new_seats"].append(n)
            continue
        if p.get("state") != r["state"]:
            out["state_changes"].append("{}: {} -> {}".format(n, p.get("state"), r["state"]))
            if r["state"] in ("WORKING", "ACTIVE") and p.get("state") not in ("WORKING", "ACTIVE"):
                out["seats_activated"].append(n)
            if r["state"] in ("IDLE", "DORMANT") and p.get("state") not in ("IDLE", "DORMANT"):
                out["seats_went_quiet"].append(n)
        if (p.get("current_work") or "") != (r.get("current_work") or "") and r.get("current_work"):
            out["new_assignments"].append("{}: {}".format(n, r["current_work"][:140]))
        pe = ((p.get("last_experiment") or {}).get("sha"))
        ce = r.get("last_experiment") or {}
        if ce.get("sha") and ce.get("sha") != pe and ce.get("type") == "experiment_result":
            out["experiments_completed"].append("{}: {}".format(n, ce["value"][:140]))
        if not p.get("blocker") and r.get("blocker"):
            out["blockers_added"].append("{}: {}".format(n, r["blocker"][:140]))
        if p.get("blocker") and not r.get("blocker"):
            out["blockers_cleared"].append(n)
    pe = prev.get("engines") or {}
    for eid, e in cur["engines"].items():
        if eid in pe and pe[eid].get("primary_seat") != e.get("primary_seat"):
            out["engine_ownership_changes"].append("{}: {} -> {}".format(eid, pe[eid].get("primary_seat"), e.get("primary_seat")))
    prev_an = {(a["type"], a["subject"]) for a in prev.get("anomalies") or []}
    out["new_anomalies"] = ["{} {}".format(a["type"], a["subject"]) for a in cur["anomalies"] if (a["type"], a["subject"]) not in prev_an]
    return out
