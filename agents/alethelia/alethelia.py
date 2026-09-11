"""Alethelia v0.1 -- the sensory cortex that is not allowed to imagine.

Charter (RATIFIED James 2026-08-17, aporia/docs/germline_infrastructure_2026-08-17.md
section 6): monitors and reports; performs no research, files no bottlenecks, spawns
nothing. Constitutional constraint: EVERY field in every report is traceable to a
query (Postgres, git, or file), and any field it cannot compute is rendered
UNKNOWN(reason) -- never narrated. The old M4 reporter's failure mode was
confabulation ("14 agents pending" fabricated from 43 UNKNOWNs); Alethelia is built
so a fabricated calm cannot pass: source failures surface as UNKNOWN + a DEGRADED
banner, and the report refuses to summarize what it could not query.

v0 scope (P29, built on M1; M4 deployment is a parked DECISION): one report,
stations/REPORT_latest.md + .json, from four source families:
  postgres  : agora.heartbeats (per-agent liveness)
  git       : HEAD, last commits, dirty state
  queues    : engine/queues/BACKLOG.jsonl status counts, GATE_ELI5 tail
  shadow    : WORKLOG/REVIEWS record counts, last pass ids, unanswered reviews

v0.1 (base-role adoption, 2026-09-11; roles/base-role/RESPONSIBILITIES.md
rules 2, 3, 7, 8 and WORKING_CONTRACT.md s1, s4):
  comms     : per-seat last comms sync and unseen-message count
              (comms.receipts / comms.messages) -- the liveness PROPERTY; the
              agora.agent_heartbeats status word is a LABEL and is kept only
              as the record of what that table still says.
  anomalies : a fixed set of deterministic rules evaluated over the fields,
              each FIRED / CLEAR / INDETERMINATE(reason). The banner can only
              read calm when zero rules fired and none is indeterminate;
              "all fields computed" is source reachability, not health, and
              is never printed alone (the 08-27 legibility defect: 33 stale
              agents under a calm banner).
  workspace : base_sha / branch / worktree_path / dirty on every report
              (D-23 s4), and the entry point refuses the canonical checkout
              (D-23 s1) because it writes stations/REPORT_latest.*.

Every value in the JSON is {"value": ..., "query": "<how it was computed>"} or
{"unknown": "<reason>", "query": ...}. The markdown renders UNKNOWN(n) inline.

Self-test (controls, section 6 + base rule 3): python agents/alethelia/test_alethelia.py
  positive control -- planted anomaly in fixture data MUST appear in the report
                      and MUST fire a rule
  cheat control    -- unreachable sources MUST yield UNKNOWNs + DEGRADED banner;
                      anomalies present MUST NOT render the calm banner
  negative control -- a fixture with nothing wrong reads calm (0 rules fired)
  guard control    -- the entry point refuses a main-worktree receipt
"""
from __future__ import annotations
import json
import pathlib
import subprocess
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]
GENERATOR = "alethelia v0.1 (M1 build; base role adopted 2026-09-11; M4 deployment pending DECISION)"
SHADOW_DORMANT_H = 48       # roles/base-role/MONITORS.md, Elenchus shadow row
COMMS_DORMANT_H = 24        # roles/base-role/MONITORS.md, comms queue row
HEARTBEAT_STALE_H = 6


def field(value=None, query="", unknown=None):
    return {"unknown": str(unknown), "query": query} if unknown is not None else {
        "value": value, "query": query}


def q_postgres(cfg=None):
    """agora.heartbeats snapshot. Never raises; failure is an UNKNOWN field."""
    out = {}
    qtext = "SELECT agent_name, machine, status, extract(epoch from now()-last_heartbeat) FROM agora.agent_heartbeats"
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        import agora_persist  # noqa: E402
        conn = agora_persist._connect()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT agent_name, machine, status, "
                            "extract(epoch from now()-last_heartbeat)::bigint "
                            "FROM agora.agent_heartbeats ORDER BY agent_name")
                rows = cur.fetchall()
        finally:
            conn.close()
        out["heartbeats"] = field(
            [{"agent": a, "machine": m, "status": s, "age_sec": int(g)} for a, m, s, g in rows],
            qtext)
        stale = [r[0] for r in rows if r[3] is not None and r[3] > HEARTBEAT_STALE_H * 3600 and str(r[2]).upper() != "DEAD"]
        out["stale_over_6h"] = field(stale, qtext + " WHERE age > 6h AND status != DEAD")
    except BaseException as e:  # noqa: BLE001 -- any failure is an honest UNKNOWN
        out["heartbeats"] = field(query=qtext, unknown=f"{type(e).__name__}: {e}"[:160])
        out["stale_over_6h"] = field(query=qtext, unknown="source unreachable")
    return out


def q_comms():
    """Per-seat comms liveness: when each seat last synced its inbox, and how
    many messages addressed to it (or broadcast) it has not seen. This is the
    property behind 'is the seat alive'; agora's status word is only a label."""
    out = {}
    qtext = ("per seat in comms.roster(): max(receipts.seen_at); count and oldest created_at of "
             "messages addressed to it or '*' with no seen receipt")
    try:
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from comms import api as capi  # noqa: E402
        seats = capi.roster()
        s = capi.schema()
        conn = capi.connect()
        try:
            cur = conn.cursor()
            cur.execute("""
                WITH seats AS (SELECT unnest(%s::text[]) AS agent),
                last AS (SELECT agent, max(seen_at) AS last_sync FROM {s}.receipts GROUP BY agent),
                unseen AS (
                    SELECT st.agent, count(*) AS n, min(m.created_at) AS oldest
                    FROM seats st
                    JOIN {s}.messages m
                      ON (st.agent = ANY(m.recipients) OR '*' = ANY(m.recipients))
                     AND m.sender <> st.agent
                     AND (m.expires_at IS NULL OR m.expires_at > now())
                    LEFT JOIN {s}.receipts r ON r.message_id = m.id AND r.agent = st.agent
                    WHERE r.seen_at IS NULL
                    GROUP BY st.agent)
                SELECT st.agent,
                       extract(epoch from now() - l.last_sync)::bigint,
                       coalesce(u.n, 0),
                       extract(epoch from now() - u.oldest)::bigint
                FROM seats st
                LEFT JOIN last l ON l.agent = st.agent
                LEFT JOIN unseen u ON u.agent = st.agent
                ORDER BY st.agent""".format(s=s), (seats,))
            rows = cur.fetchall()
        finally:
            conn.close()
        sync = [{"seat": a, "last_sync_age_sec": (int(g) if g is not None else None), "unseen": int(n),
                 "oldest_unseen_age_sec": (int(o) if o is not None else None)}
                for a, g, n, o in rows]
        out["seat_sync"] = field(sync, qtext)
        # The registry row (MONITORS.md, comms queue): dormant = a message has
        # waited unseen on the seat for more than COMMS_DORMANT_H. Seats with
        # unseen messages are the ELIGIBLE set; a seat cannot be dormant on a
        # message younger than the threshold, however long since it synced.
        eligible = [r["seat"] for r in sync if r["unseen"] > 0]
        dormant = [r["seat"] for r in sync
                   if r["oldest_unseen_age_sec"] is not None and r["oldest_unseen_age_sec"] > COMMS_DORMANT_H * 3600]
        out["comms_eligible"] = field(eligible, qtext + " WHERE unseen > 0 (seats the dormancy rule could fire on)")
        out["dormant_on_comms"] = field(
            dormant, qtext + f" WHERE oldest unseen message age > {COMMS_DORMANT_H}h")
    except BaseException as e:  # noqa: BLE001
        out["seat_sync"] = field(query=qtext, unknown=f"{type(e).__name__}: {e}"[:160])
        out["comms_eligible"] = field(query=qtext, unknown="source unreachable")
        out["dormant_on_comms"] = field(query=qtext, unknown="source unreachable")
    return out


def q_git(repo=ROOT):
    out = {}

    def run(args):
        return subprocess.run(["git", "-C", str(repo)] + args, capture_output=True,
                              text=True, timeout=30)
    try:
        head = run(["rev-parse", "--short", "HEAD"])
        out["head"] = (field(head.stdout.strip(), "git rev-parse --short HEAD")
                       if head.returncode == 0 else
                       field(query="git rev-parse", unknown=head.stderr.strip()[:120]))
        log = run(["log", "--oneline", "-5"])
        out["last_commits"] = (field(log.stdout.strip().splitlines(), "git log --oneline -5")
                               if log.returncode == 0 else
                               field(query="git log", unknown=log.stderr.strip()[:120]))
        st = run(["status", "--porcelain", "-uno"])
        out["dirty_files"] = (field(len(st.stdout.strip().splitlines()) if st.stdout.strip() else 0,
                                    "git status --porcelain -uno | wc -l")
                              if st.returncode == 0 else
                              field(query="git status", unknown=st.stderr.strip()[:120]))
    except BaseException as e:  # noqa: BLE001
        for k in ("head", "last_commits", "dirty_files"):
            out.setdefault(k, field(query="git", unknown=f"{type(e).__name__}"[:60]))
    return out


def q_queues(root=None):
    root = pathlib.Path(root) if root else ROOT
    out = {}
    bl = root / "engine/queues/BACKLOG.jsonl"
    try:
        threads = [json.loads(l) for l in bl.read_text(encoding="utf-8").splitlines() if l.strip()]
        counts = {}
        for t in threads:
            counts[str(t.get("status"))] = counts.get(str(t.get("status")), 0) + 1
        out["backlog_status_counts"] = field(counts, f"parse {bl.name}, count by status")
        live = sorted((t for t in threads if t.get("status") == "QUEUED" and not t.get("gate")),
                      key=lambda t: -t.get("priority", 0))
        out["top_unblocked"] = field([t["id"] for t in live[:3]],
                                     f"parse {bl.name}, QUEUED+ungated, top-3 by priority")
        # zombie detection (DEC-002 gap, closed P30): RUNNING threads whose
        # generated timestamp is >7 days old have no plausible live worker.
        from datetime import datetime, timezone as _tz
        zombies = []
        for t in threads:
            if t.get("status") != "RUNNING":
                continue
            try:
                gen = datetime.fromisoformat(str(t.get("generated")).replace("Z", "+00:00"))
                age_d = (datetime.now(_tz.utc) - gen).total_seconds() / 86400
                if age_d > 7:
                    zombies.append({"id": t["id"], "age_days": round(age_d, 1)})
            except (ValueError, TypeError):
                zombies.append({"id": t.get("id"), "age_days": None, "note": "unparseable generated ts"})
        out["zombie_running"] = field(zombies,
                                      f"parse {bl.name}, RUNNING with generated age > 7d (or unparseable)")
    except BaseException as e:  # noqa: BLE001
        out["backlog_status_counts"] = field(query=str(bl), unknown=f"{type(e).__name__}: {e}"[:120])
        out["top_unblocked"] = field(query=str(bl), unknown="source unreadable")
        out["zombie_running"] = field(query=str(bl), unknown="source unreadable")
    ge = root / "engine/queues/GATE_ELI5.jsonl"
    try:
        gates = [json.loads(l) for l in ge.read_text(encoding="utf-8").splitlines() if l.strip()]
        out["open_gates"] = field(len(gates), f"count lines in {ge.name}")
    except BaseException as e:  # noqa: BLE001
        out["open_gates"] = field(query=str(ge), unknown=f"{type(e).__name__}"[:60])
    # W-006 consumer leg (P31): the DR event ledger the dispatcher emits into.
    dr = root / "engine/ledger/DR_EVENTS.jsonl"
    try:
        evs = [json.loads(l) for l in dr.read_text(encoding="utf-8").splitlines() if l.strip()]
        out["dr_events"] = field(
            {"count": len(evs), "last": evs[-1] if evs else None},
            f"parse {dr.name}: count + last record")
    except FileNotFoundError:
        out["dr_events"] = field({"count": 0, "last": None},
                                 f"{dr.name} absent (no events emitted yet)")
    except BaseException as e:  # noqa: BLE001
        out["dr_events"] = field(query=str(dr), unknown=f"{type(e).__name__}: {e}"[:120])
    return out


def q_shadow(root=None):
    root = pathlib.Path(root) if root else ROOT
    out = {}
    try:
        wl = [json.loads(l) for l in (root / "engine/shadow/WORKLOG.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        rv = [json.loads(l) for l in (root / "engine/shadow/REVIEWS.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        answered = {r.get("review_id") for w in wl for r in w.get("review_responses", [])}
        out["worklog_entries"] = field(len(wl), "count WORKLOG.jsonl records")
        out["last_pass"] = field(wl[-1]["pass_id"] if wl else None, "last WORKLOG record pass_id")
        out["reviews"] = field(len(rv), "count REVIEWS.jsonl records")
        out["unanswered_reviews"] = field(
            [r.get("review_id") for r in rv if r.get("review_id") not in answered],
            "REVIEWS ids minus review_responses ids across WORKLOG")
        wl_ids = {w["pass_id"] for w in wl}
        reviewed = set()
        for r in rv:
            t = r.get("target_pass_id")
            if t:
                reviewed.add(t)
        out["unreviewed_passes"] = field(
            sorted(i for i in wl_ids if i not in reviewed and not i.endswith("SEED"))[-5:],
            "last 5 WORKLOG pass_ids absent from REVIEWS target_pass_id")
    except BaseException as e:  # noqa: BLE001
        for k in ("worklog_entries", "last_pass", "reviews", "unanswered_reviews", "unreviewed_passes"):
            out.setdefault(k, field(query="shadow files", unknown=f"{type(e).__name__}: {e}"[:120]))
    return out


def q_workspace():
    """D-23 s4: where this report was built. Inherits archaeon/workspace.py."""
    qtext = "archaeon.workspace.receipt(): base_sha, branch, worktree_path, dirty, main_worktree"
    try:
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from archaeon.workspace import receipt  # noqa: E402
        r = receipt()
        return {"receipt": field({k: r[k] for k in ("base_sha", "branch", "worktree_path", "dirty", "main_worktree")}, qtext)}
    except BaseException as e:  # noqa: BLE001
        return {"receipt": field(query=qtext, unknown=f"{type(e).__name__}: {e}"[:120])}


def count_unknowns(section):
    return sum(1 for v in section.values() if "unknown" in v)


# ---------------------------------------------------------------------------
# Anomaly rules (v0.1). Each is a pure function of the computed fields and
# returns FIRED / CLEAR / INDETERMINATE(reason). A rule over an UNKNOWN field
# is INDETERMINATE, never CLEAR: "nothing fired" and "nothing could have
# fired" are different facts (base role s2).
# ---------------------------------------------------------------------------

def _get(sections, sec, key):
    f = sections.get(sec, {}).get(key)
    if f is None:
        return None, f"field {sec}.{key} absent"
    if "unknown" in f:
        return None, f"field {sec}.{key} UNKNOWN({f['unknown']})"
    return f["value"], None


def _rule(name, sections, sec, key, predicate, describe, query):
    val, why = _get(sections, sec, key)
    if why:
        return {"rule": name, "state": "INDETERMINATE", "reason": why, "query": query}
    try:
        fired = bool(predicate(val))
    except Exception as e:  # noqa: BLE001
        return {"rule": name, "state": "INDETERMINATE", "reason": f"{type(e).__name__}: {e}"[:120], "query": query}
    return {"rule": name, "state": "FIRED" if fired else "CLEAR",
            "detail": describe(val) if fired else None, "query": query}


def _pass_age_hours(pass_id, now=None):
    """Aporia pass ids embed their UTC timestamp: '2026-09-01T00:00Z-P177'."""
    stamp = str(pass_id).split("Z")[0]
    ts = datetime.fromisoformat(stamp).replace(tzinfo=timezone.utc)
    return ((now or datetime.now(timezone.utc)) - ts).total_seconds() / 3600


def evaluate_rules(sections, now=None):
    rules = [
        _rule("stale_heartbeats", sections, "postgres", "stale_over_6h",
              lambda v: len(v) > 0,
              lambda v: f"{len(v)} heartbeat rows older than {HEARTBEAT_STALE_H}h and not DEAD",
              "len(postgres.stale_over_6h) > 0"),
        _rule("zombie_running", sections, "queues", "zombie_running",
              lambda v: len(v) > 0,
              lambda v: f"{len(v)} RUNNING threads with no plausible live worker",
              "len(queues.zombie_running) > 0"),
        _rule("no_unblocked_work", sections, "queues", "top_unblocked",
              lambda v: len(v) == 0,
              lambda v: "no QUEUED+ungated thread in BACKLOG.jsonl",
              "len(queues.top_unblocked) == 0"),
        _rule("shadow_input_dormant", sections, "shadow", "last_pass",
              lambda v: _pass_age_hours(v, now) > SHADOW_DORMANT_H,
              lambda v: f"last Aporia pass {v} is {_pass_age_hours(v, now) / 24:.1f} days old (threshold {SHADOW_DORMANT_H}h)",
              f"age(shadow.last_pass) > {SHADOW_DORMANT_H}h, timestamp parsed from the pass id"),
        _rule("unanswered_reviews", sections, "shadow", "unanswered_reviews",
              lambda v: len(v) > 0,
              lambda v: f"{len(v)} reviews with no review_response in WORKLOG",
              "len(shadow.unanswered_reviews) > 0"),
        _rule("unreviewed_passes", sections, "shadow", "unreviewed_passes",
              lambda v: len(v) > 0,
              lambda v: f"{len(v)} of the last passes have no review targeting them",
              "len(shadow.unreviewed_passes) > 0"),
        _rule("dormant_on_comms", sections, "comms", "dormant_on_comms",
              lambda v: len(v) > 0,
              lambda v: f"{len(v)} of {len(_get(sections, 'comms', 'comms_eligible')[0] or [])} eligible seats "
                        f"hold a message unseen for more than {COMMS_DORMANT_H}h: {v}",
              f"len(comms.dormant_on_comms) > 0; eligible = comms.comms_eligible"),
    ]
    tally = {s: sum(1 for r in rules if r["state"] == s) for s in ("FIRED", "CLEAR", "INDETERMINATE")}
    return {"rules": rules, "fired": tally["FIRED"], "clear": tally["CLEAR"],
            "indeterminate": tally["INDETERMINATE"], "total": len(rules)}


def build_report(pg=q_postgres, git=q_git, queues=q_queues, shadow=q_shadow,
                 comms=q_comms, workspace=q_workspace, now=None):
    sections = {"postgres": pg(), "comms": comms(), "git": git(), "queues": queues(),
                "shadow": shadow(), "workspace": workspace()}
    n_unknown = sum(count_unknowns(s) for s in sections.values())
    n_fields = sum(len(s) for s in sections.values())
    anomalies = evaluate_rules(sections, now=now)
    degraded = n_unknown > 0
    calm = (not degraded) and anomalies["fired"] == 0 and anomalies["indeterminate"] == 0
    report = {
        "generated_utc": (now or datetime.now(timezone.utc)).isoformat(timespec="seconds"),
        "generator": GENERATOR,
        "constitutional_note": ("every field carries its query; UNKNOWN is never narrated over; "
                                "calm requires zero fired and zero indeterminate rules"),
        "degraded": degraded,
        "unknown_fields": n_unknown,
        "total_fields": n_fields,
        "anomalies": anomalies,
        "calm": calm,
        "sections": sections,
    }
    return report


def banner_text(report):
    a = report["anomalies"]
    fired = [r["rule"] for r in a["rules"] if r["state"] == "FIRED"]
    indet = [r["rule"] for r in a["rules"] if r["state"] == "INDETERMINATE"]
    rules_part = "%d of %d anomaly rules FIRED%s%s" % (
        a["fired"], a["total"],
        (" (" + ", ".join(fired) + ")") if fired else "",
        ("; %d INDETERMINATE (%s)" % (len(indet), ", ".join(indet))) if indet else "")
    if report["degraded"]:
        return ("!! DEGRADED: %d/%d fields UNKNOWN -- this report is PARTIAL and says so; "
                "calm is not implied by silence !! %s" % (report["unknown_fields"], report["total_fields"], rules_part))
    if report["calm"]:
        return "CALM: all %d fields computed from live queries; %s" % (report["total_fields"], rules_part)
    return "!! ANOMALIES: all %d fields computed, %s !!" % (report["total_fields"], rules_part)


def render_md(report):
    lines = []
    lines.append("# Alethelia report -- " + report["generated_utc"])
    lines.append("")
    lines.append("**" + banner_text(report) + "**")
    lines.append("")
    lines.append("## anomalies")
    for r in report["anomalies"]["rules"]:
        extra = r.get("detail") if r["state"] == "FIRED" else (r.get("reason") if r["state"] == "INDETERMINATE" else "")
        lines.append(f"- {r['rule']}: {r['state']}" + (f" -- {extra}" if extra else "") + f"  <- rule: `{r['query']}`")
    lines.append("")
    for sec, fields in report["sections"].items():
        lines.append(f"## {sec}")
        for k, v in fields.items():
            if "unknown" in v:
                lines.append(f"- {k}: UNKNOWN({v['unknown']})  <- query: `{v['query']}`")
            else:
                val = v["value"]
                if isinstance(val, list) and len(val) > 6:
                    val = f"[{len(val)} items] " + json.dumps(val[:3], ensure_ascii=False) + " ..."
                else:
                    val = json.dumps(val, ensure_ascii=False)
                lines.append(f"- {k}: {val}  <- query: `{v['query']}`")
        lines.append("")
    return "\n".join(lines)


def guard(receipt_fn=None):
    """D-23 s1: refuse to write the report from the canonical checkout. Takes
    an injectable receipt so the self-test can prove the refusal fires."""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from archaeon.workspace import CanonicalCheckoutRefused, receipt  # noqa: E402
    r = (receipt_fn or receipt)()
    if r.get("main_worktree"):
        raise CanonicalCheckoutRefused(
            "refusing to write stations/REPORT_latest.* from the canonical checkout %s; "
            "run Alethelia from a linked worktree (D-23, 2026-09-11)" % r.get("worktree_path"))
    return r


def main():
    guard()
    report = build_report()
    outdir = ROOT / "stations"
    outdir.mkdir(exist_ok=True)
    (outdir / "REPORT_latest.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    (outdir / "REPORT_latest.md").write_text(render_md(report), encoding="utf-8")
    print(banner_text(report))
    print("-> stations/REPORT_latest.md")


if __name__ == "__main__":
    main()
