"""Harmonia instance identity: one seat, many concurrent instances.

Currency: 2026-09-11 (Harmonia[m1-486e595f]). Convention file:
roles/Harmonia/INSTANCES.md. Inherits roles/base-role/RESPONSIBILITIES.md.

Several Harmonia instances can run at once (2026-09-11: one on M1 in the
harmonia-hygiene worktree, one on M2 writing packet 02, and this one). The
comms queue, the journal directory, STATUS.md, commit subjects and branch
names all key on the SEAT name alone, so two instances are indistinguishable
in every log unless each one carries a tag it cannot share with another.

The tag is derived, never chosen: machine label + the first 8 hex of the
harness session id (CLAUDE_CODE_SESSION_ID). Two sessions cannot share it;
one session always regenerates the same one. No session id means NO tag --
this module refuses rather than emit a tag that could collide.

    python roles/Harmonia/instance.py tag        -> m1-486e595f
    python roles/Harmonia/instance.py name       -> Harmonia[m1-486e595f]
    python roles/Harmonia/instance.py subject "text"
                                                 -> Harmonia[m1-486e595f]: text
    python roles/Harmonia/instance.py trailer    -> the commit trailer line(s)
    python roles/Harmonia/instance.py branch <task>
                                                 -> harmonia/m1-486e595f-<task>-<date>
    python roles/Harmonia/instance.py journal    -> roles/Harmonia/journal/<date>_m1-486e595f.md
    python roles/Harmonia/instance.py selftest   -> exit 0 or 1

Machine labels are the program's (M1 = SKULLPORT, M2 = SPECTREX5, per
comms/environments.json descriptions); an unknown host falls back to its
lowercased hostname so the tag is still unique, still derived.
"""
from __future__ import annotations

import datetime as _dt
import os
import platform
import re
import sys

SEAT = "Harmonia"
MACHINES = {"SKULLPORT": "m1", "SPECTREX5": "m2"}
SESSION_ENV = "CLAUDE_CODE_SESSION_ID"
BRIDGE_ENV = "CLAUDE_CODE_BRIDGE_SESSION_ID"


class NoSession(RuntimeError):
    """No harness session id: an instance tag would not be unique, so none is
    issued. Set CLAUDE_CODE_SESSION_ID (the harness does) or pass one."""


def machine_label(hostname: str | None = None) -> str:
    h = (hostname or platform.node() or "unknown-host").strip()
    return MACHINES.get(h.upper(), re.sub(r"[^a-z0-9]+", "-", h.lower()) or "unknown-host")


def tag(session_id: str | None = None, hostname: str | None = None) -> str:
    # None means "ask the harness"; an explicit empty string is an absent id and is refused.
    sid = (os.environ.get(SESSION_ENV, "") if session_id is None else session_id).strip().lower()
    if not re.fullmatch(r"[0-9a-f]{8}[0-9a-f-]*", sid):
        raise NoSession("no usable {} (got {!r}); refusing to mint an instance tag".format(SESSION_ENV, sid))
    return "{}-{}".format(machine_label(hostname), sid[:8])


def name(session_id: str | None = None, hostname: str | None = None) -> str:
    return "{}[{}]".format(SEAT, tag(session_id, hostname))


def subject(text: str, session_id: str | None = None, hostname: str | None = None) -> str:
    return "{}: {}".format(name(session_id, hostname), text)


def trailer(session_id: str | None = None, hostname: str | None = None) -> str:
    """The commit trailer. Pairs with the mandated Claude-Session trailer: that
    one carries the bridge session, this one carries the tag every other
    artifact uses, so `git log --grep` finds an instance by either."""
    sid = os.environ.get(SESSION_ENV, "") if session_id is None else session_id
    return "Harmonia-Instance: {} (host {}, harness session {})".format(
        tag(session_id, hostname), platform.node() if hostname is None else hostname, sid)


def branch(task: str, session_id: str | None = None, hostname: str | None = None, date: str | None = None) -> str:
    d = date or _dt.date.today().isoformat()
    t = re.sub(r"[^a-z0-9]+", "-", task.lower()).strip("-")
    return "harmonia/{}-{}-{}".format(tag(session_id, hostname), t, d)


def journal_path(session_id: str | None = None, hostname: str | None = None, date: str | None = None) -> str:
    d = date or _dt.date.today().isoformat()
    return "roles/Harmonia/journal/{}_{}.md".format(d, tag(session_id, hostname))


def selftest() -> int:
    """Positive: two sessions differ, one session repeats. Negative: no
    session refuses. Cheat: a caller who passes the same session on two
    machines still gets two tags (the machine is part of the tag)."""
    checks = []
    a = tag("486e595f-e8dd-4327-be91-de876aef42c8", "SKULLPORT")
    b = tag("0a1b2c3d-0000-0000-0000-000000000000", "SKULLPORT")
    checks.append(("two sessions differ", a != b))
    checks.append(("same session repeats", a == tag("486e595f-e8dd-4327-be91-de876aef42c8", "SKULLPORT")))
    checks.append(("expected form", a == "m1-486e595f"))
    checks.append(("machine is part of the tag", tag("486e595f-e8dd-4327-be91-de876aef42c8", "SPECTREX5") == "m2-486e595f"))
    checks.append(("unknown host still unique", tag("486e595f-e8dd-4327-be91-de876aef42c8", "Some Host") == "some-host-486e595f"))
    try:
        tag("", "SKULLPORT"); refused = False
    except NoSession:
        refused = True
    checks.append(("empty session refused", refused))
    try:
        tag("session_011b9Gdn4tBoFbuAMXSM2vrH", "SKULLPORT"); refused = False
    except NoSession:
        refused = True
    checks.append(("bridge id (not hex) refused, so the two id spaces cannot be confused", refused))
    checks.append(("branch form", branch("boot", "486e595f-e8dd-4327-be91-de876aef42c8", "SKULLPORT", "2026-09-11") == "harmonia/m1-486e595f-boot-2026-09-11"))
    checks.append(("journal form", journal_path("486e595f-e8dd-4327-be91-de876aef42c8", "SKULLPORT", "2026-09-11") == "roles/Harmonia/journal/2026-09-11_m1-486e595f.md"))
    ok = True
    for label, passed in checks:
        print("{} {}".format("PASS" if passed else "FAIL", label)); ok = ok and passed
    print("selftest {}/{}".format(sum(1 for _, p in checks if p), len(checks)))
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__); return 0
    cmd, rest = argv[0], argv[1:]
    try:
        if cmd == "tag":
            print(tag())
        elif cmd == "name":
            print(name())
        elif cmd == "subject":
            print(subject(" ".join(rest)))
        elif cmd == "trailer":
            print(trailer())
        elif cmd == "branch":
            print(branch(rest[0] if rest else "task"))
        elif cmd == "journal":
            print(journal_path())
        elif cmd == "selftest":
            return selftest()
        else:
            print("unknown command {!r}".format(cmd), file=sys.stderr); return 2
    except NoSession as exc:
        print("REFUSED: {}".format(exc), file=sys.stderr); return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
