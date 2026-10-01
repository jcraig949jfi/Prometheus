"""Deterministic classification rules for the fleet census.

Every rule here is documented in roles/Achilles/CLASSIFICATION_RULES.md and exercised by
achilles/census/tests/test_census.py (positive, negative and cheat controls). No model sits
in this path: the census is a deterministic function of git, files and database rows.
"""
from __future__ import annotations

import re

# ---------------------------------------------------------------- hosts

# instance-tag prefix -> host label (comms/api.py instance_tag; atlas/registry.json hosts)
HOST_PREFIX = {
    "m1": "M1", "skullport": "M1",
    "m2": "M2", "spectrex5": "M2",
    "m3": "M3", "gandalf": "M3",
    "m4": "M4", "harry1": "M4", "aletheia": "M4",
    "ubu001": "ubu001", "ubu002": "ubu002",
    "elsa": "ELSA", "desktop-ruapvai": "DESKTOP-RUAPVAI", "buckkeep": "BUCKKEEP",
}
MACHINE_TO_HOST = {"SKULLPORT": "M1", "SPECTREX5": "M2", "GANDALF": "M3", "HARRY1": "M4",
                   "ELSA": "ELSA", "DESKTOP-RUAPVAI": "DESKTOP-RUAPVAI", "BUCKKEEP": "BUCKKEEP",
                   "UBU001": "ubu001", "UBU002": "ubu002"}
INSTANCE_RE = re.compile(r"^([a-z0-9][a-z0-9-]*?)-([0-9a-f]{8})$")


def host_from_instance(tag: str | None) -> str | None:
    if not tag:
        return None
    m = INSTANCE_RE.match(tag.strip().lower())
    if not m:
        return None
    return HOST_PREFIX.get(m.group(1))


def host_from_machine(machine: str | None) -> str | None:
    if not machine:
        return None
    return MACHINE_TO_HOST.get(machine.strip().upper(), machine.strip())


# ---------------------------------------------------------------- commit attribution

PREFIX_RE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_]*(?:-[A-Za-z0-9]+)*)\s*(?:\[([^\]]+)\])?\s*:")
WORD_PREFIX_RE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_-]*)\s+[^:\n]{1,48}:")
LANE_RE = re.compile(r"^(.*?)-[A-Z]$")
TRAILER_INSTANCE_RE = re.compile(r"^([A-Z][a-z]+)-Instance:\s*(?:\S+\s+)?(\S+)", re.M)
SYSTEM_PREFIXES = ("auto:",)


class Roster:
    """Canonical names plus aliases, case-insensitive."""

    def __init__(self, seats, aliases=None):
        self.canon = {s.lower(): s for s in seats}
        self.alias = {}
        for name, target in (aliases or {}).items():
            self.alias[name.lower()] = target

    def resolve(self, token: str | None) -> str | None:
        if not token:
            return None
        t = token.strip().lower()
        if t in self.canon:
            return self.canon[t]
        if t in self.alias:
            return self.alias[t]
        m = LANE_RE.match(token.strip())
        if m and m.group(1).lower() in self.canon:  # Nestor-B, Harmonia-A
            return self.canon[m.group(1).lower()]
        return None


def attribute_commit(subject: str, body: str, files, author: str, roster: Roster, path_owner) -> dict:
    """Return {seat, basis, instance, host} for one non-merge commit.

    Precedence (CLASSIFICATION_RULES.md A1-A6): system prefix; 'Seat[instance]:'; 'Seat <topic>:';
    lane trailer (Nestor-Instance: G m1-...); path majority over roles/<Seat>/ and engine paths;
    seat-named author. Unattributed commits keep seat None -- they are counted, never guessed.
    """
    s = subject or ""
    if s.lower().startswith(SYSTEM_PREFIXES):
        return {"seat": "SYSTEM", "basis": "system-prefix", "instance": None, "host": None}
    inst = None
    m = PREFIX_RE.match(s)
    if m:
        inst = m.group(2)
        seat = roster.resolve(m.group(1))
        if seat:
            return {"seat": seat, "basis": "subject-prefix", "instance": inst, "host": host_from_instance(inst)}
    m2 = WORD_PREFIX_RE.match(s)
    if m2:
        seat = roster.resolve(m2.group(1))
        if seat:
            return {"seat": seat, "basis": "subject-word", "instance": None, "host": None}
    t = TRAILER_INSTANCE_RE.search(body or "")
    if t:
        seat = roster.resolve(t.group(1))
        if seat:
            return {"seat": seat, "basis": "instance-trailer", "instance": t.group(2),
                    "host": host_from_instance(t.group(2))}
    counts = {}
    for f in files or ():
        owner = path_owner(f)
        if owner:
            counts[owner] = counts.get(owner, 0) + 1
    if counts:
        best, n = max(counts.items(), key=lambda kv: kv[1])
        if n * 2 > sum(counts.values()):
            return {"seat": best, "basis": "path-majority", "instance": inst, "host": host_from_instance(inst)}
    a = roster.resolve((author or "").split("(")[0].strip())
    if a:
        return {"seat": a, "basis": "author-name", "instance": None, "host": None}
    return {"seat": None, "basis": "unattributed", "instance": inst, "host": host_from_instance(inst)}


# ---------------------------------------------------------------- commit categories

# Experiment vocabulary (base role s2, CWO-30C s10.3 prefixes, atlas/classify.py CLASS_PATTERNS).
# Case-sensitive on purpose: the fleet writes verdict words in capitals ("H1 hard test FAIL").
RESULT_RE = re.compile(r"\b(RESULT|VERDICT|KILL(?:ED)?|CLEAN_NULL|NULL|NOT_CONFIRMED|CONFIRMED|INDETERMINATE|"
                       r"INCONCLUSIVE|FAIL(?:ED)?|PASS(?:ED)?|RETRACT(?:ED|ION)?|SURVIVED?|REFUTED|"
                       r"VALIDATED|INADMISSIBLE|NEGATIVE|POSITIVE)\b(?!\.md)")
START_RE = re.compile(r"\b(PREREG(?:ISTRATION)?|PRE-?REGISTERED|FROZEN|FREEZE|SEAL(?:ED)?|LAUNCH(?:ED)?|RUNNING|"
                      r"AMENDMENT)\b(?!\.md)")
START_CI_RE = re.compile(r"\bpreregist", re.I)
# Things the charter says are NOT experiments even when they mention tests.
NOT_EXPERIMENT_RE = re.compile(r"(?i)\b(heartbeat|sync receipt|lint|typo|regenerat\w* (the )?dashboard|"
                               r"portfolio update|test[- ]suite|pytest|self-test|journal only|state READY|"
                               r"WORK_STATE)\b")
STATUS_PATHS_RE = re.compile(r"^roles/[^/]+/(WORK_STATE\.json|STATUS\.md|TODO\.md|journal/|calibration/LEDGER\.md|"
                             r"WAKE\.md|BACKLOG_H0H5\.md)")


def commit_category(subject: str, files) -> str:
    """experiment_result | experiment_start | status | work. (System commits are filtered earlier.)

    'status' = only seat bookkeeping files changed, or a heartbeat/WORK_STATE subject: an explicit
    progress update (charter signal 4), not substantive work by itself.
    """
    s = subject or ""
    files = list(files or ())
    bookkeeping = bool(files) and all(STATUS_PATHS_RE.match(f) for f in files)
    if NOT_EXPERIMENT_RE.search(s):
        return "status" if bookkeeping or re.search(r"(?i)heartbeat|state READY|WORK_STATE", s) else "work"
    if RESULT_RE.search(s):
        return "experiment_result"
    if START_RE.search(s) or START_CI_RE.search(s):
        return "experiment_start"
    if bookkeeping:
        return "status"
    return "work"


def verdict_token(subject: str) -> str | None:
    m = RESULT_RE.search(subject or "")
    return m.group(1) if m else None


# ---------------------------------------------------------------- comms messages

HEARTBEAT_RE = re.compile(r"(?i)\bheartbeat\b|\bvisibility\b.*\bping\b|^\s*hb\b")


def message_level(kind: str, subject: str) -> int:
    """Evidence level of a comms message (charter ranking; lower is stronger).

    3 = substantive message (report/ruling/delegation/prompt/question with content)
    4 = explicit status/progress update (a heartbeat carrying the CWO-30C s14 fields)
    7 = acknowledgement only (weak)
    """
    if kind == "ack":
        return 7
    if HEARTBEAT_RE.search(subject or ""):
        return 4
    return 3


# ---------------------------------------------------------------- state rules

STATE_WORDS = ("WORKING", "ACTIVE", "READY", "IDLE", "BLOCKED", "HOLD", "PARKED", "DORMANT", "RETIRED",
               "CLOSED", "DEPRECATED", "PAUSED")
STATE_WORD_RE = re.compile(r"\b(" + "|".join(STATE_WORDS) + r")\b")


def normalise_state(raw: str | None) -> str | None:
    """First recognised state word in a free-text state string ('BLOCKED (promexec); P0 CLOSED' -> BLOCKED)."""
    if not raw:
        return None
    m = STATE_WORD_RE.search(str(raw).upper())
    if not m:
        return None
    w = m.group(1)
    return {"CLOSED": "RETIRED", "DEPRECATED": "RETIRED", "PAUSED": "PARKED"}.get(w, w)


STATUS_LINE_RE = re.compile(r"(?im)^\W*(?:#+\s*)?seat[ _]state\s*[:|]?\s*\**\s*([A-Za-z_ /()-]+)")


def status_md_state(text: str) -> tuple[str | None, str | None]:
    """(normalised state, raw line) from the first 'seat state:' line of a STATUS.md."""
    if not text:
        return None, None
    m = STATUS_LINE_RE.search(text[:6000])
    if not m:
        m2 = re.search(r"(?im)^\s*state\s*:\s*([A-Za-z_ /()-]+)", text[:3000])
        if not m2:
            return None, None
        return normalise_state(m2.group(1)), m2.group(0).strip()[:160]
    return normalise_state(m.group(1)), m.group(0).strip()[:160]


# Activity windows (hours). Documented in CLASSIFICATION_RULES.md s3.
FRESH_H = 24.0
RECENT_H = 72.0
IDLE_LIMIT_H = 24.0 * 7
DECLARED_FRESH_H = 72.0


def classify_seat(kind: str, declared: list, activity: dict, marker: dict | None) -> dict:
    """Return {state, active, confidence, rule, flags, why}.

    declared: [{'state','source','time','age_h'}] newest first (WORK_STATE, Aporia census, comms
              status, STATUS.md); activity: {'substantive_age_h','status_age_h','presence_age_h'};
    marker:   registry lifecycle marker {'state','date','source','after_marker_activity'}.
    Rules S0-S6 in CLASSIFICATION_RULES.md; the first that applies wins, and its id is recorded.
    """
    flags, why = [], []
    sub = activity.get("substantive_age_h")
    st = activity.get("status_age_h")
    pres = activity.get("presence_age_h")

    def active_word():
        if sub is not None and sub <= FRESH_H:
            return "Yes"
        if (sub is not None and sub <= RECENT_H) or (st is not None and st <= FRESH_H) or \
                (pres is not None and pres <= FRESH_H):
            return "Uncertain"
        return "No"

    act = active_word()
    fresh_decl = [d for d in declared if d.get("state") and d.get("age_h") is not None and d["age_h"] <= DECLARED_FRESH_H]
    decl = fresh_decl[0] if fresh_decl else (declared[0] if declared and declared[0].get("state") else None)
    states = {d["state"] for d in fresh_decl if d.get("state")}
    if len(states - {"WORKING", "ACTIVE"}) > 1 or (len(states) > 1 and not states <= {"WORKING", "ACTIVE"}):
        flags.append("CONFLICTING_STATES")
        why.append("fresh declared states disagree: " + ", ".join(
            "{}={}".format(d["source"], d["state"]) for d in fresh_decl))

    def out(state, rule, conf):
        if "CONFLICTING_STATES" in flags and conf == "HIGH":
            conf = "MEDIUM"
        return {"state": state, "active": act, "confidence": conf, "rule": rule, "flags": flags, "why": why}

    # S0 non-seat entities: historical role documents and pre-seat agents/tools
    if kind in ("HISTORICAL_ROLE_DOC", "AGENT_TOOL"):
        ms = normalise_state((marker or {}).get("state"))
        if ms in ("RETIRED", "PARKED"):
            why.append("registry marker {} ({})".format(ms, (marker or {}).get("source")))
            return out(ms, "S0-marker", "MEDIUM")
        if sub is not None and sub <= IDLE_LIMIT_H:
            why.append("non-seat entity with recent attributed activity")
            return out("ACTIVE", "S0-activity", "LOW")
        why.append("non-seat entity, no recent activity, no lifecycle marker")
        return out("DORMANT", "S0-quiet", "MEDIUM")

    # S1 retired/closed/deprecated marker, unless work after it
    ms = normalise_state((marker or {}).get("state"))
    decl_state = decl["state"] if decl else None
    if ms == "RETIRED" and decl_state not in ("WORKING", "ACTIVE", "READY") :
        if marker.get("after_marker_activity"):
            flags.append("ACTIVITY_AFTER_RETIREMENT")
            why.append("retirement marker but attributed activity after its date")
            return out("RETIRED", "S1-retired-conflict", "LOW")
        why.append("lifecycle marker {} at {}".format(marker.get("state"), marker.get("source")))
        return out("RETIRED", "S1-retired", "HIGH" if sub is None or sub > IDLE_LIMIT_H else "MEDIUM")

    # S2 parked (operator act), from a fresh declaration or the marker when nothing fresher
    if decl_state == "PARKED" or (decl is None and ms == "PARKED"):
        if sub is not None and sub <= FRESH_H:
            flags.append("PARKED_BUT_ACTIVE")
            why.append("declared PARKED but substantive activity {:.0f}h ago".format(sub))
            return out("PARKED", "S2-parked-active", "LOW")
        why.append("declared PARKED ({})".format(decl["source"] if decl else (marker or {}).get("source")))
        return out("PARKED", "S2-parked", "HIGH" if decl and decl.get("age_h", 1e9) <= DECLARED_FRESH_H else "MEDIUM")

    # S3 a fresh declaration of a working-family state, checked against activity
    if decl and decl.get("age_h") is not None and decl["age_h"] <= DECLARED_FRESH_H:
        why.append("declared {} by {} {:.0f}h ago".format(decl_state, decl["source"], decl["age_h"]))
        if decl_state in ("WORKING", "ACTIVE"):
            if sub is not None and sub <= FRESH_H:
                why.append("substantive activity {:.0f}h ago".format(sub))
                return out("WORKING", "S3-working", "HIGH")
            if sub is not None and sub <= 48:
                flags.append("VISIBILITY_STALE")
                return out("WORKING", "S3-working-stale", "MEDIUM")
            flags.append("ACTIVE_NO_WORK_48H")
            why.append("declared working but no substantive work in 48h")
            return out("IDLE", "S3-declared-active-no-work", "LOW")
        if decl_state in ("READY", "BLOCKED", "HOLD", "IDLE"):
            return out(decl_state, "S3-declared", "HIGH" if decl["age_h"] <= FRESH_H else "MEDIUM")
        if decl_state == "DORMANT":
            return out("DORMANT", "S3-declared", "MEDIUM")

    # S4 stale or missing declaration: activity decides, declaration recorded
    if decl:
        why.append("newest declaration {} by {} is {} old".format(
            decl_state, decl["source"], "?" if decl.get("age_h") is None else "{:.0f}h".format(decl["age_h"])))
    if sub is not None and sub <= FRESH_H:
        why.append("substantive activity {:.0f}h ago".format(sub))
        if decl_state in ("BLOCKED", "HOLD", "READY"):
            return out(decl_state, "S4-stale-declared-with-activity", "LOW")
        return out("ACTIVE", "S4-activity", "MEDIUM")
    if sub is not None and sub <= IDLE_LIMIT_H:
        why.append("last substantive activity {:.0f}h ago".format(sub))
        if decl_state in ("BLOCKED", "HOLD", "READY", "IDLE"):
            return out(decl_state, "S4-stale-declared", "LOW")
        return out("IDLE", "S4-idle", "MEDIUM")
    if sub is not None:
        why.append("no substantive activity for {:.0f}d".format(sub / 24))
        if decl_state in ("BLOCKED", "HOLD"):
            flags.append("STALE_TASK")
            return out(decl_state, "S4-stale-declared-old", "LOW")
        return out("DORMANT", "S5-dormant", "MEDIUM" if decl_state is None else "LOW")
    # S6 no evidence at all
    why.append("no attributable activity found in git, comms or evidence wiki")
    return out("UNKNOWN", "S6-no-evidence", "LOW")
