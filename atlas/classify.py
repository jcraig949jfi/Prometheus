"""Deterministic classifiers shared by the harvesters: commit subjects,
disposition words, machine evidence. No model in this path: every rule is
a regex or a lookup, so a recomb with a changed rule is diffable."""
from __future__ import annotations

import re
from typing import Iterable, List, Optional, Tuple

from atlas import db

# commits ------------------------------------------------------------------------

SEAT_INSTANCE = re.compile(
    r"^(?P<seat>[A-Z][A-Za-z]+)(?:-(?P<lane>[A-Z]))?\[(?P<inst>[A-Za-z0-9_-]+)\]:")
LANE_ROWS = re.compile(r"^(?P<lane>[A-Z])\[(?P<inst>m\d-[0-9a-z]{8}|[a-z]+-[0-9a-z]{8}|[A-Za-z0-9_-]+)\]:")
BARE_SEAT = re.compile(r"^(?P<seat>[A-Z][a-z]+)(?: [\w/ -]+?)?:")
ARCHAEON = re.compile(r"^(?:CMP\d|archaeon (?:c\d|frontier|campaign)|Archaeon)", re.I)
BELLEROPHON = re.compile(r"^Bellerophon overnight (?P<cyc>C\d+(?:-C\d+)?)")
TRAILER_SESSION = re.compile(r"^Claude-Session:\s*\S*?(session_[0-9A-Za-z]+)", re.M)
TRAILER_INSTANCE = re.compile(r"^[A-Z][a-z]+-Instance:\s*(\S+)", re.M)

ID_PATTERNS = [
    re.compile(r"\bC[1-6]-SFE-\d{2}\b"), re.compile(r"\bSFE-\d{2}\b"), re.compile(r"\bC[1-6]-\d{2}\b"),
    re.compile(r"\bC4-REH-\d\b"), re.compile(r"\bDF-\d{3}\b"), re.compile(r"\bD[4-6]-\d{3}\b"),
    re.compile(r"\bcw\d{2}-e\d{2}\b", re.I), re.compile(r"\bCW\d{2}\b"), re.compile(r"\bT-(?:X\d+|E\d+|ARCH\d(?:/[A-Z]\d)?)\b"),
    re.compile(r"\bP-[A-F]\d{2}\b"), re.compile(r"\b[A-HPQRTUW]-R\d+-[\w.-]+"), re.compile(r"\bLIN-[0-9a-f]{8}\b"),
    re.compile(r"\b(?:HARM|TALOS|LUDUS|THEO|PROTEUS|ARCH|RHAD|BELL|NYX|DIOM|ERGON|AC|NESTOR|ATLAS|APHRODITE)-\d+[A-Z]?\b"),
    re.compile(r"\bC\d{2,3}\b(?=[: ])"),
]

CLASS_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("MERGE", re.compile(r"^merge\b", re.I)),
    ("PREREG", re.compile(r"\bprereg(?:ister(?:ed)?|istration)?\b", re.I)),
    ("CORRECTION", re.compile(r"\bcorrect(?:ion|ed)\b", re.I)),
    ("AMENDMENT", re.compile(r"\bamend(?:ment|ed)?\b", re.I)),
    ("SUPERSEDED", re.compile(r"\bsupersed(?:ed|es|ing)\b", re.I)),
    ("REPLICA", re.compile(r"\breplica(?:te|ted|tion)?\b", re.I)),
    ("RETRACT", re.compile(r"\b(?:retract(?:ed|ion)?|withdrawn)\b", re.I)),
    ("RERUN", re.compile(r"\bre-?run\b", re.I)),
    ("RESULT", re.compile(r"\b(?:verdict|result|readout|closed|disposition|rows)\b", re.I)),
    ("REVIEW", re.compile(r"\breview packet\b", re.I)),
]


def classify_commit(subject: str, body: str) -> dict:
    seat = lane = inst = None
    m = SEAT_INSTANCE.match(subject)
    if m:
        seat, lane, inst = m.group("seat"), m.group("lane"), m.group("inst")
    else:
        m = LANE_ROWS.match(subject)
        if m:
            seat, lane, inst = "Nestor", m.group("lane"), m.group("inst")
        elif BELLEROPHON.match(subject):
            seat = "Bellerophon"
        elif ARCHAEON.match(subject):
            seat = "Archaeon"
        else:
            m = BARE_SEAT.match(subject)
            if m and m.group("seat") not in ("Merge", "Revert", "Add", "Fix", "Update"):
                seat = m.group("seat")
    if not inst:
        t = TRAILER_INSTANCE.search(body or "")
        if t:
            inst = t.group(1)
    sess = TRAILER_SESSION.search(body or "")
    text = subject + "\n" + (body or "")
    ids = sorted({x for p in ID_PATTERNS for x in p.findall(text)})
    classes = [name for name, p in CLASS_PATTERNS if p.search(subject)]
    return {"seat": seat, "lane": lane, "instance_tag": inst,
            "session": sess.group(1) if sess else None, "ids": ids[:60], "classes": classes}


# machines -----------------------------------------------------------------------

def _machines():
    return db.registry()["hosts"]


def host_from_tag(tag: Optional[str]) -> Optional[str]:
    if not tag or "-" not in tag:
        return None
    prefix = tag.split("-", 1)[0].lower()
    for m in _machines():
        if prefix in [a.lower() for a in m["aliases"]]:
            return m["host_id"]
    return None


def host_from_text(*texts: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """(machine_id, basis) from IPs, hostnames or path roots found in texts."""
    for t in texts:
        if not t:
            continue
        for m in _machines():
            if m.get("lan_ip") and m["lan_ip"] in t:
                return m["host_id"], "ip {} in {!r}".format(m["lan_ip"], t[:80])
            for a in m["aliases"]:
                if (":" in a or len(a) > 3) and a.lower() in t.lower():
                    return m["host_id"], "alias {!r} in {!r}".format(a, t[:80])
    return None, None


# dispositions ---------------------------------------------------------------------

_STATUS = [
    ("INVALID", r"INVALID|INSTRUMENT_INVALID|VOID|DESIGN UNREACHABLE|UNREACHABLE"),
    ("FAILED", r"\bFAIL(?:ED|URE)?\b|CRASH|ERROR|ABORT"),
    ("WEAK_POSITIVE", r"WEAK_POSITIVE|WEAK POSITIVE|WEAK"),
    ("INCONCLUSIVE", r"INCONCLUSIVE|INDETERMINATE|NOT_REACHED|NOT_RUN|UNDERPOWERED"),
    ("NEGATIVE", r"NEGATIVE|REFUTED|KILL|FALSIFIED|NO_EFFECT"),
    ("NULL", r"\bNULL\b"),
    ("POSITIVE", r"POSITIVE|PASS|CONFIRMED|SURVIVED|QUALIFIED|COMPLETE|REPLICATED|SUPPORTED|ROBUST"),
    ("RUNNING", r"RUNNING|STARTED|IN_PROGRESS"),
    ("PLANNED", r"PENDING|PLANNED|PREREG|DESIGNED|QUEUED|OPEN"),
]


def status_class(native: Optional[str]) -> str:
    if not native:
        return "UNKNOWN"
    s = str(native).upper()
    for name, pat in _STATUS:
        if re.search(pat, s):
            return name
    return "UNKNOWN"


def dig(obj, path: str):
    """dig(d, 'a.b.c') -> value or None."""
    cur = obj
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def scalar(v) -> Tuple[Optional[str], Optional[float]]:
    if v is None:
        return None, None
    if isinstance(v, bool):
        return str(v).lower(), float(v)
    if isinstance(v, (int, float)):
        return str(v), float(v)
    if isinstance(v, str):
        try:
            return v[:2000], float(v) if re.fullmatch(r"-?\d+(?:\.\d+)?(?:e-?\d+)?", v.strip()) else None
        except ValueError:
            return v[:2000], None
    return None, None


def ids_in(values: Iterable[str]) -> List[str]:
    return sorted({x for v in values if v for p in ID_PATTERNS for x in p.findall(v)})
