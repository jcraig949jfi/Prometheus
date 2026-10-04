#!/usr/bin/env python3
"""new_seat.py -- create a conformant Prometheus seat in about a minute.

Runs the whole creation pass that used to take a seat several minutes by hand
(Epimetheus f0baa84aa is the pattern): name archaeology, a SPARSE worktree from a
recorded origin/main SHA, the seat's files from roles/base-role/seat_kit/templates/,
the operator's directive verbatim with a MANIFEST, the two INHERITANCE rows, a
validator, the base-role self-tests, comms boot, one commit, and (with --push) a
fast-forward push that survives a busy origin/main.

Run it straight from origin/main, so a brand-new seat needs nothing checked out:

    cd <canonical checkout>
    git fetch origin
    git show origin/main:roles/base-role/seat_kit/new_seat.py | python - <Seat> \
        --model <exact runtime model id> --directive-file <operator words file> --push

The canonical checkout only ever sees `git fetch` and `git worktree add`
(WORKING_CONTRACT.md s1-s3). Nothing here pulls, resets, force-pushes or touches
another seat's files. It never decides a charter: the seat is created in HOLD,
charter PENDING. Pure stdlib; Python 3.8+.
"""
import argparse
import concurrent.futures as cf
import datetime
import json
import os
import pathlib
import re
import socket
import subprocess
import sys
import tempfile
import time

BANNER = "Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md"
KIT = "roles/base-role/seat_kit/templates"
# A cone checkout: everything directly in the root, plus these trees. Enough for the
# tool, comms, and the base-role self-tests; the seat can `git sparse-checkout disable`.
# attacks + ergon/probe: a host-local pre-commit hook (Charon preflight, seen on M1) runs
# `python attacks/preflight.py --probes`, whose probes read ergon/probe. evidence_wiki: comms imports it.
# Measured: this set is 776 files, a few seconds, and the hook passes 3/3 in it.
CONE = ["roles/base-role", "comms", "archaeon/tests", "aporia/doctrine", "ops/work_orders",
        "attacks", "evidence_wiki", "ergon/probe"]
RECOVERY = {}
NL = chr(10)
REVALIDATE_PREFIXES = ("roles/base-role/", "comms/", "archaeon/", ".gitignore", "ops/work_orders/CURRENT.md")
RESERVED = {"base-role", "generic-worker-role", "rso-builder-role"}
NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9]*(-[A-Za-z0-9]+)*$")


class SeatError(Exception):
    pass


def roster_patterns(cone, seat):
    """Non-cone sparse patterns: what the cone checks out (root files, parent-dir files, the cone dirs) PLUS every
    seat's top-level *.md, so comms' roster (the directories under roles/) is complete and neighbours' entry
    files are readable. Applied AFTER the self-tests: a complete roster makes one self-test O(seats), ~65 s."""
    dirs = list(cone) + ["roles/" + seat]
    ancestors = sorted({"/".join(d.split("/")[:i]) for d in dirs for i in range(1, len(d.split("/")))})
    pats = ["/*", "!/*/"]
    for a in ancestors:
        pats += ["/%s/*" % a, "!/%s/*/" % a]
    pats += ["/%s/" % d for d in dirs]
    pats.append("/roles/*/*.md")
    return pats


def expand_roster(wt, seat):
    git(wt, "sparse-checkout", "set", "--no-cone", *roster_patterns(CONE, seat), timeout=300)
    roles = pathlib.Path(wt) / "roles"
    return len([p for p in roles.iterdir() if p.is_dir() and not p.name.endswith("-role")])


def ascii_safe(s):
    return str(s).encode("ascii", "backslashreplace").decode("ascii")


def run(cmd, cwd=None, timeout=180, check=True, env=None, input_text=None):
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, timeout=timeout, env=env,
                           input=input_text.encode() if input_text is not None else None)
    except subprocess.TimeoutExpired:
        raise SeatError("timeout after %ss: %s" % (timeout, " ".join(map(str, cmd))[:200]))
    out = p.stdout.decode("utf-8", "replace")
    err = p.stderr.decode("utf-8", "replace")
    if check and p.returncode != 0:
        raise SeatError("exit %d: %s\n%s" % (p.returncode, " ".join(map(str, cmd))[:200], (err or out)[-600:]))
    return p.returncode, out, err


def git(repo, *args, **kw):
    return run(["git", "-C", str(repo)] + list(args), **kw)


class Steps:
    """Timed step log; the journal and the receipt are built from it."""

    def __init__(self):
        self.rows = []
        self.t0 = time.monotonic()

    def timed(self, name, fn, *a, **kw):
        t = time.monotonic()
        try:
            r = fn(*a, **kw)
        finally:
            self.rows.append((name, time.monotonic() - t))
        return r

    def note(self, name, text):
        self.rows.append((name + ": " + text, None))

    def render(self):
        out = []
        for n, d in self.rows:
            out.append("- %-34s %s" % (n, "" if d is None else "%5.1fs" % d))
        return "\n".join(out)

    def total(self):
        return time.monotonic() - self.t0


# ----------------------------------------------------------------- archaeology
def archaeology(canonical, sha, name):
    low = name.lower()
    refs = [r for r in git(canonical, "for-each-ref", "--format=%(refname:short)", "refs/remotes")[1].split() if r]

    def roles_on(ref):
        rc, out, _ = git(canonical, "ls-tree", "--name-only", "%s:roles" % ref, check=False)
        return ref, [x.strip() for x in out.split()] if rc == 0 else []

    def grep():
        rc, out, _ = git(canonical, "grep", "-l", "-i", "-w", "-I", "-e", name, sha, "--", ".", check=False, timeout=240)
        hits = [l.split(":", 1)[1] for l in out.splitlines() if ":" in l]
        return [h for h in hits if not h.lower().startswith("roles/%s/" % low)]

    def log():
        rc, out, _ = git(canonical, "log", "--all", "-i", "--grep=" + name, "--format=%h %s", check=False)
        return [l for l in out.splitlines() if l.strip()]

    def paths():
        found = []
        for base in ("", "agents/"):
            rc, out, _ = git(canonical, "ls-tree", "--name-only", sha, base, check=False)
            for e in out.split():
                if os.path.basename(e.rstrip("/")).lower() == low and e.rstrip("/") != "roles":
                    found.append(e)
        return found

    with cf.ThreadPoolExecutor(8) as ex:
        f_grep, f_log, f_paths = ex.submit(grep), ex.submit(log), ex.submit(paths)
        role_hits = [r for r, names in ex.map(roles_on, refs) if any(n.lower() == low for n in names)]
        hits, commits, pths = f_grep.result(), f_log.result(), f_paths.result()
    if role_hits:
        raise SeatError("roles/%s already exists on %d ref(s): %s. Pick another name (a seat that lives only on a "
                        "branch still counts: that is how Chiron was nearly offered as free)."
                        % (name, len(role_hits), ", ".join(role_hits[:5])))
    return {"refs": len(refs), "grep": hits, "log": commits, "paths": pths}


def archaeology_text(name, sha, a):
    def lst(items, cap):
        s = ", ".join(ascii_safe(i) for i in items[:cap])
        return s + (" (+%d more)" % (len(items) - cap) if len(items) > cap else "")
    g, lg, pt = a["grep"], a["log"], a["paths"]
    lines = [
        "- Content: `git grep -l -i -w %s %s` -> %d file(s)%s" % (name, sha[:9], len(g), (": " + lst(g, 8)) if g else "."),
        "- Commit messages: `git log --all -i --grep=%s` -> %d commit(s)%s" % (
            name, len(lg), (": " + lst([l.split(" ", 1)[0] + " " + l.split(" ", 1)[1][:60] if " " in l else l for l in lg], 4)) if lg else "."),
        "- Paths named like the seat at the root or under agents/: %s" % (lst(pt, 5) if pt else "none."),
        "- Roles: no roles/%s on any of the %d remote refs (git ls-tree on each ref's roles/)." % (name, a["refs"]),
    ]
    return "\n".join(lines)


def archaeology_summary(a):
    n = len(a["grep"]) + len(a["log"]) + len(a["paths"])
    if n == 0:
        return "no prior use of the name as a seat or agent (zero hits in the tree or in commit messages)"
    return ("no prior use of the name as a seat or agent (%d file mention(s), %d commit message(s), %d path(s); "
            "recorded and not inherited, see RESPONSIBILITIES.md s1)" % (len(a["grep"]), len(a["log"]), len(a["paths"])))


# ------------------------------------------------------------------ file work
def render(text, mapping):
    for k, v in mapping.items():
        text = text.replace("@@%s@@" % k, v)
    left = re.findall(r"@@[A-Z_]+@@", text)
    if left:
        raise SeatError("unfilled template tokens: %s" % sorted(set(left)))
    return text


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        data = text.replace("\r\n", "\n").encode("ascii")
    except UnicodeEncodeError as e:
        raise SeatError("non-ASCII text for %s: %s" % (path.name, e))
    path.write_bytes(data)


def insert_rows(path, rows):
    """Append one row to each of the two register tables, byte-safe (keeps CRLF)."""
    raw = pathlib.Path(path).read_bytes()
    eol = b"\r\n" if b"\r\n" in raw else b"\n"
    lines = raw.split(eol)
    for header, row in rows:
        idx = next((i for i, l in enumerate(lines) if l.startswith(header)), None)
        if idx is None:
            raise SeatError("INHERITANCE.md table header not found: %r" % header)
        end = idx + 1
        while end < len(lines) and lines[end].startswith(b"|"):
            end += 1
        lines.insert(end, row.encode("ascii"))
    out = eol.join(lines)
    if not all(b < 0x80 for b in out):
        raise SeatError("non-ASCII introduced into INHERITANCE.md")
    pathlib.Path(path).write_bytes(out)


def validate(wt, seat, creation_dir):
    wt = pathlib.Path(wt)
    sd = wt / "roles" / seat
    bad = []
    need = ["RESPONSIBILITIES.md", "WORK_STATE.json", "WAKE.md", "STATUS.md", "TODO.md", "BACKLOG_H0H5.md",
            "calibration/LEDGER.md", creation_dir + "/00_README.md", creation_dir + "/MANIFEST.md"]
    for n in need:
        if not (sd / n).is_file():
            bad.append("missing roles/%s/%s" % (seat, n))
    if bad:
        return bad
    if BANNER not in (sd / "RESPONSIBILITIES.md").read_text(encoding="utf-8").splitlines()[2]:
        bad.append("banner not on line 3 of RESPONSIBILITIES.md")
    try:
        ws = json.loads((sd / "WORK_STATE.json").read_text(encoding="utf-8"))
        for k in ("schema", "seat", "mwo_id", "mwo_commit", "state", "current_objective", "next_actions",
                  "operator_decisions_required", "last_push_sha", "model"):
            if k not in ws:
                bad.append("WORK_STATE.json lacks %s" % k)
        if ws.get("seat") != seat or ws.get("state") != "HOLD":
            bad.append("WORK_STATE.json seat/state wrong")
    except ValueError as e:
        bad.append("WORK_STATE.json invalid: %s" % e)
    for p in sd.rglob("*"):
        if p.is_file():
            b = p.read_bytes()
            verb = "_verbatim" in p.name
            if b"\r" in b:
                bad.append("CR in %s" % p.relative_to(wt))
            if not verb and any(x > 0x7F for x in b):
                bad.append("non-ASCII in %s" % p.relative_to(wt))
    for fname in ("STATUS.md", "WORK_STATE.json"):
        txt = (sd / fname).read_text(encoding="utf-8")
        if "Traceback" in txt or 'File "' in txt or "ModuleNotFoundError" in txt:
            bad.append("traceback fragment inside %s" % fname)
    inh = (wt / "roles/base-role/INHERITANCE.md").read_bytes().replace(b"\r\n", b"\n").decode("ascii")
    if len(re.findall(r"^\| %s \|" % re.escape(seat), inh, re.M)) != 2:
        bad.append("INHERITANCE.md must carry exactly two '| %s |' rows" % seat)
    if not re.search(r"^\| %s \| RESPONSIBILITIES\.md \|$" % re.escape(seat), inh, re.M):
        bad.append("INHERITANCE.md entry-file row missing")
    rc, out, _ = run([sys.executable, "-m", "comms.manifest", "verify", str(sd / creation_dir)], cwd=wt, check=False)
    if rc != 0 or " 0 mismatches" not in out:
        bad.append("manifest verify failed: %s" % out.strip()[-200:])
    rc, out, _ = git(wt, "ls-files", "--others", "--exclude-standard", "roles/" + seat, check=False)
    committable = len([l for l in out.splitlines() if l.strip()])
    ondisk = len([p for p in sd.rglob("*") if p.is_file()])
    tracked = len([l for l in git(wt, "ls-files", "roles/" + seat, check=False)[1].splitlines() if l.strip()])
    if committable + tracked != ondisk:
        bad.append("%d file(s) under roles/%s are git-ignored (would not be committed)" % (ondisk - committable - tracked, seat))
    return bad


def self_tests(wt, env):
    """Run the base-role self-tests; returns (failed node ids, last summary line), or (None, why) if pytest is absent.

    A sparse worktree lacks the other seats and campaigns that some of these tests audit, so they are run
    once BEFORE the seat exists (baseline) and once after; only NEW failures count against the seat."""
    rc, out, err = run([sys.executable, "-m", "pytest", "archaeon/tests/test_base_role.py",
                        "archaeon/tests/test_shared_roles.py", "-q", "-rf", "-p", "no:cacheprovider"],
                       cwd=wt, check=False, timeout=400, env=env)
    if rc != 0 and "No module named pytest" in (out + err):
        return None, "SKIPPED (pytest not installed)"
    failed = set(re.findall(r"^FAILED (\S+)", out, re.M))
    tail = (out.strip().splitlines() or ["(no output)"])[-1]
    return failed, tail


# ------------------------------------------------------------------------ main
def main(argv=None):
    ap = argparse.ArgumentParser(description="Create a conformant Prometheus seat (HOLD, charter PENDING).")
    ap.add_argument("seat")
    ap.add_argument("--model", required=True, help="exact runtime model id, e.g. claude-sonnet-5-5 (not guessed)")
    ap.add_argument("--directive-file", action="append", default=[], help="operator's words, verbatim (repeatable)")
    ap.add_argument("--directive", action="append", default=[], help="operator's words as text (prefer --directive-file)")
    ap.add_argument("--stated", action="append", default=[], help="what the operator said about the seat, in their words (repeatable)")
    ap.add_argument("--note", action="append", default=[], help="a sentence for the creation README (repeatable)")
    ap.add_argument("--host-label", default=socket.gethostname().upper())
    ap.add_argument("--capabilities", default="", help="comms capabilities to advertise (default none)")
    ap.add_argument("--trailer", action="append", default=[], help="commit trailer line, e.g. 'Co-Authored-By: ...' (repeatable)")
    ap.add_argument("--worktrees-dir", default=None)
    ap.add_argument("--no-comms", action="store_true")
    ap.add_argument("--skip-hooks", action="store_true",
                    help="commit with --no-verify. ONLY if the operator says so: a host hook rejected the seat commit")
    ap.add_argument("--tests", choices=["quick", "none"], default="quick")
    ap.add_argument("--push", action="store_true", help="fast-forward push to origin/main (outward-facing; off by default)")
    ap.add_argument("--dry-run", action="store_true", help="fetch + name archaeology only; nothing is created")
    ap.add_argument("--date", default=None, help="override the UTC date (YYYY-MM-DD)")
    a = ap.parse_args(argv)
    seat = a.seat
    if not NAME_RE.match(seat) or not (3 <= len(seat) <= 40) or seat.lower() in RESERVED or seat.lower().endswith("-role"):
        raise SeatError("bad seat name %r (letters/digits/hyphens, 3-40 chars, not a shared-role name)" % seat)
    if not a.dry_run and not (a.directive_file or a.directive):
        raise SeatError("give the operator's creation directive verbatim: --directive-file PATH (or --directive TEXT)")

    S = Steps()
    now = datetime.datetime.now(datetime.timezone.utc)
    date = a.date or now.strftime("%Y-%m-%d")
    nowz = now.strftime("%Y-%m-%dT%H:%MZ")
    host = socket.gethostname().lower()
    instance = "%s-%s" % (host, (os.environ.get("CLAUDE_CODE_SESSION_ID", "")[:8] or "nosession"))
    env = dict(os.environ)
    # The M1 store (SKULLPORT, 192.168.1.202), per roles/base-role/WAKE_DIRECTIVE.md. comms/environments.json
    # is keyed by environment and deliberately holds no host; comms' own identity guard (WRONG_ENVIRONMENT)
    # refuses any other cluster, and the preflight below exercises it before anything is written.
    if "EW_DB_HOST" not in env and host.upper() != "SKULLPORT":
        env["EW_DB_HOST"] = "192.168.1.202"

    rc, common, _ = git(".", "rev-parse", "--path-format=absolute", "--git-common-dir")
    canonical = pathlib.Path(common.strip()).parent
    S.timed("fetch origin (canonical)", git, canonical, "fetch", "origin", "--quiet", timeout=240)
    sha = git(canonical, "rev-parse", "origin/main")[1].strip()
    mwo_head = git(canonical, "show", "%s:ops/work_orders/CURRENT.md" % sha)[1].splitlines()[:3]
    mwo_id = (re.search(r"MWO-\d{4}", " ".join(mwo_head)) or [None])[0] or "UNKNOWN"
    mwo_commit = git(canonical, "log", "-1", "--format=%H", sha, "--", "ops/work_orders/CURRENT.md")[1].strip()

    branch = "%s/base-role-adopt-%s" % (seat.lower(), date)
    wtdir = pathlib.Path(a.worktrees_dir) if a.worktrees_dir else canonical.parent / (canonical.name + "-worktrees")
    wt = wtdir / ("%s-base-role-adopt-%s" % (seat.lower(), date))
    creation_dir = "prompts/%s_creation" % date

    RECOVERY.update({"canonical": canonical, "wt": wt, "branch": branch})

    def make_worktree():
        if wt.exists():
            raise SeatError("worktree path exists: %s (remove it or pass --date)" % wt)
        git(canonical, "worktree", "add", "--no-checkout", "-b", branch, str(wt), sha, timeout=300)
        git(wt, "sparse-checkout", "set", "--cone", *(CONE + ["roles/" + seat]), timeout=120)
        git(wt, "checkout", "-f", "HEAD", timeout=600)

    def cleanup():
        git(canonical, "worktree", "remove", "--force", str(wt), check=False)
        git(canonical, "branch", "-D", branch, check=False)

    t = time.monotonic()
    with cf.ThreadPoolExecutor(2) as ex:
        f_arch = ex.submit(archaeology, canonical, sha, seat)
        f_wt = None if a.dry_run else ex.submit(make_worktree)
        try:
            arch = f_arch.result()
        except SeatError:
            if f_wt:
                try:
                    f_wt.result()
                except SeatError:
                    pass
                cleanup()
            raise
        if f_wt:
            f_wt.result()
    S.rows.append(("archaeology || sparse worktree", time.monotonic() - t))
    arch_text = archaeology_text(seat, sha, arch)
    if a.dry_run:
        print("DRY RUN: roles/%s is free on all %d remote refs at %s.\n%s\n(nothing created)\n" % (seat, arch["refs"], sha[:9], arch_text))
        return 0
    if not a.no_comms:
        rc, out, err = S.timed("comms preflight (read-only who)", run, [sys.executable, "-m", "comms", "who", "--minutes", "1"],
                               cwd=wt, env=env, timeout=120, check=False)
        if rc != 0:
            last = [l for l in (err or out).strip().splitlines() if l.strip()]
            cleanup()
            raise SeatError("comms preflight failed; NOTHING was created and the worktree was discarded: %s. Usual causes: "
                            "psycopg2 not installed; EW_DB_HOST set to something other than the M1 store (when it is unset "
                            "the tool sets 192.168.1.202 off M1); M1 unreachable. Fix it, or re-run with --no-comms to "
                            "create the seat without a comms boot (its files then record NOT PRESENT)."
                            % ((last[-1].strip()[:200]) if last else "no output"))
    base_fail = None  # sparse-baseline failures, measured before the seat exists
    if a.tests == "quick":
        base_fail, base_tail = S.timed("baseline self-tests (no seat yet)", self_tests, wt, env)

    # ---- seat files (everything that does not depend on comms boot)
    sd = wt / "roles" / seat
    tdir = wt / KIT
    if not tdir.is_dir():  # kit not on this origin/main yet: fall back to the templates beside this script
        beside = pathlib.Path(globals().get("__file__", "")).resolve().parent / "templates"
        if not beside.is_dir():
            raise SeatError("no templates at %s on origin/main and none beside the script" % KIT)
        tdir = beside

    def tpl(name):
        return (tdir / name).read_text(encoding="ascii")

    files = []
    for i, f in enumerate(a.directive_file, 1):
        files.append(pathlib.Path(f).read_bytes())
    for txt in a.directive:
        files.append(txt.encode("utf-8"))
    dnames = []
    for i, raw in enumerate(files, 1):
        raw = raw.replace(b"\r\n", b"\n")
        if not raw.endswith(b"\n"):
            raw += b"\n"
        n = "%02d_OPERATOR_CREATION_verbatim.md" % i
        (sd / creation_dir).mkdir(parents=True, exist_ok=True)
        (sd / creation_dir / n).write_bytes(raw)
        dnames.append(n)
    stated = "\n".join("- " + ascii_safe(s) for s in a.stated) or "- (nothing beyond the name and the instruction to set the seat up)"
    m = {
        "SEAT": seat, "SEAT_UPPER": seat.upper(), "DATE": date, "NOW": nowz, "HOST": ascii_safe(a.host_label),
        "INSTANCE": instance, "BASE_SHA": sha, "BASE_SHORT": sha[:9], "BRANCH": branch,
        "WORKTREE": ascii_safe(wt.name if not a.worktrees_dir else wt), "MODEL": a.model, "MWO_ID": mwo_id,
        "MWO_SHORT": mwo_commit[:9], "CREATION_DIR": creation_dir, "STATED": stated, "ARCHAEOLOGY": arch_text,
        "DIRECTIVE_FILES": "\n".join("- %s -- the operator's words, byte for byte" % n for n in dnames),
        "NOTES": ("".join(ascii_safe(n) + "\n\n" for n in a.note)),
    }
    write_text(sd / "RESPONSIBILITIES.md", render(tpl("RESPONSIBILITIES.md.tmpl"), m))
    write_text(sd / "WAKE.md", render(tpl("WAKE.md.tmpl"), m))
    write_text(sd / "TODO.md", render(tpl("TODO.md.tmpl"), m))
    write_text(sd / "BACKLOG_H0H5.md", render(tpl("BACKLOG_H0H5.md.tmpl"), m))
    write_text(sd / "calibration/LEDGER.md", render(tpl("LEDGER.md.tmpl"), m))
    write_text(sd / creation_dir / "00_README.md", render(tpl("creation_README.md.tmpl"), m))
    S.note("seat files rendered", "%d directive file(s)" % len(dnames))

    # ---- comms boot (needs roles/<Seat>/ on the tree it runs from)
    boot_line, boot_ok = "comms boot not run (--no-comms)", False
    if not a.no_comms:
        cmd = [sys.executable, "-m", "comms", "boot", seat, "--model", a.model]
        if a.capabilities:
            cmd += ["--capabilities", a.capabilities]
        try:
            rc, out, err = S.timed("comms boot", run, cmd, cwd=wt, env=env, timeout=150, check=False)
            boot_ok = rc == 0 and out.startswith("booted")
            if boot_ok:
                boot_line = out.strip().splitlines()[0]
            else:
                last = [l for l in (err or out).strip().splitlines() if l.strip()]
                boot_line = "comms boot failed: " + (last[-1].strip() if last else "no output")[:200]
            if boot_ok:
                rc2, out2, _ = S.timed("comms sync", run, [sys.executable, "-m", "comms", "sync", seat], cwd=wt, env=env, timeout=150, check=False)
                S.note("comms sync", ascii_safe((out2.strip().splitlines() or ["(no output)"])[0])[:110])
        except SeatError as e:
            boot_line = "comms boot failed: %s" % str(e)[:160]
    tier = (re.search(r"\((light|heavy)\)", boot_line) or [None, "?"])[1]
    presence = ("PRESENT (comms boot %s[%s] on the M1 store, %s tier, %s)" % (seat, instance, tier, a.model)
                if boot_ok else "NOT PRESENT (%s)" % ascii_safe(boot_line)[:140])
    blockers = ("none; waiting on the charter is not a block (no lane yet)." if boot_ok or a.no_comms else
                "comms boot not achieved (%s); recorded, not worked around." % ascii_safe(boot_line)[:140])
    m.update({"PRESENCE": presence, "BLOCKERS": blockers, "STEPLOG": ""})
    write_text(sd / "STATUS.md", render(tpl("STATUS.md.tmpl"), m))

    ws = {
        "schema": "prometheus.work_state.v1", "seat": seat, "mwo_id": mwo_id, "mwo_commit": mwo_commit,
        "updated_at_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "state": "HOLD",
        "instance": "%s (%s)" % (instance, ascii_safe(a.host_label)), "branch": branch, "base_sha": sha,
        "head_sha": "(this commit; see git log -1 -- roles/%s/WORK_STATE.json)" % seat,
        "model": a.model, "host": ascii_safe(a.host_label),
        "work_order": "%s (ops/work_orders/CURRENT.md) + CWO-2026-09-30C. Direct operator instruction (chat, %s): "
                      "create %s (roles/%s/%s/)." % (mwo_id, date, seat, seat, creation_dir),
        "current_objective": "none (charter PENDING)",
        "current_step": "creation pass complete; awaiting the operator's charter",
        "in_flight": [], "progress": "creation pass only; no domain work started or implied",
        "finish_condition": "charter committed verbatim with MANIFEST; RESPONSIBILITIES.md rewritten; backlog filed",
        "next_expected_milestone": "charter adoption commit",
        "expected_next_artifact": "roles/%s/prompts/<date>_charter/MANIFEST.md" % seat,
        "threads": [], "campaigns": [], "experiments": [], "fabric_tasks": [], "running": [], "blocked": [], "blocked_on": [],
        "resource_status": "none held; no Fabric lease, no compute, no worker, no process started",
        "last_receipt": "roles/%s/journal/%s.md (creation pass)" % (seat, date),
        "last_push_sha": "UNKNOWN (set on the seat's first state commit after the push)", "last_push_utc": "UNKNOWN",
        "session_started_utc": "UNKNOWN (not inferred)",
        "next": "awaiting the operator's charter. Not awaiting Aporia dispatch: HOLD with no lane is not READY (CWO-C s1.3), "
                "and a new seat charter is the operator's (CWO-C s9).",
        "next_actions": ["Seat created %s, charter PENDING. HOLD because no READY work exists without a charter (base role 2a F), "
                         "not a block on any seat. When the charter arrives: commit verbatim with MANIFEST under "
                         "roles/%s/prompts/<date>_charter/, rewrite RESPONSIBILITIES.md (pre-charter body to superseded/), "
                         "file BACKLOG_H0H5.md, leave HOLD." % (date, seat)],
        "operator_decisions_required": [], "latest_reports": ["roles/%s/journal/%s.md (creation pass)" % (seat, date)],
    }
    write_text(sd / "WORK_STATE.json", json.dumps(ws, indent=2) + "\n")

    # ---- register, manifest
    row1 = ("| %s | RESPONSIBILITIES.md (created %s on the seat's creation pass on %s; new seat named by the operator, "
            "charter PENDING; creation directive verbatim in roles/%s/%s/ with MANIFEST; %s; "
            "self-service row per Archaeon ruling #39) |" % (seat, date, ascii_safe(a.host_label), seat, creation_dir, archaeology_summary(arch)))
    row2 = "| %s | RESPONSIBILITIES.md |" % seat
    insert_rows(wt / "roles/base-role/INHERITANCE.md", [(b"| role | stamped document(s) |", row1), (b"| role | entry file |", row2)])
    S.timed("manifest write", run, [sys.executable, "-m", "comms.manifest", "write", str(sd / creation_dir)], cwd=wt)

    # ---- journal (before validation so it is validated and committed; commit/push are in the receipt)
    S.note("(commit and push follow; see the tool receipt)", "")
    write_text(sd / "journal" / ("%s.md" % date), render(tpl("journal.md.tmpl"), dict(m, STEPLOG=S.render())))

    bad = S.timed("validate", validate, wt, seat, creation_dir)
    if bad:
        raise SeatError("validation failed (worktree kept at %s):\n  - %s" % (wt, "\n  - ".join(bad)))
    test_line = "tests: none (--tests none)"
    if a.tests == "quick":
        if base_fail is None:
            test_line = "tests: SKIPPED (pytest not installed)"
        else:
            fail, tail = S.timed("self-tests (with seat)", self_tests, wt, env)
            new = sorted(fail - base_fail)
            if new:
                raise SeatError("the seat introduced %d new self-test failure(s) (worktree kept at %s): %s" % (len(new), wt, new))
            test_line = "tests: %s; %d failure(s) already present in the sparse baseline (they audit other seats), 0 new" % (tail, len(base_fail))

    # ---- commit by explicit paths with a message file
    subject = "%s[%s]: creation pass -- seat created on %s, base role adopted, charter PENDING" % (seat, instance, ascii_safe(a.host_label))
    body = ("New seat, named by the operator. Created by roles/base-role/seat_kit/new_seat.py from the Epimetheus pattern "
            "(f0baa84aa): directive verbatim with MANIFEST, WORK_STATE HOLD, two INHERITANCE rows, base %s.\n\n"
            "Archaeology at base: %s.\n%s. %s. Sparse worktree. Not done on purpose: heartbeat, comms post, any science.\n"
            % (sha[:9], archaeology_summary(arch), ascii_safe(boot_line)[:200], test_line))
    msg = subject + "\n\n" + body + ("\n" + "\n".join(a.trailer) + "\n" if a.trailer else "")
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="ascii", errors="replace") as fh:
        fh.write(msg)
    git(wt, "add", "roles/" + seat, "roles/base-role/INHERITANCE.md")
    try:
        S.timed("commit", git, wt, "commit", "-q", *(["--no-verify"] if a.skip_hooks else []), "-F", fh.name)
    except SeatError as e:
        raise SeatError(str(e) + NL + "The commit failed after validation passed; a host git hook (they live in the canonical .git "
                        "and run in every worktree) is the usual cause. Fix what the hook needs, or - only if the "
                        "operator says so - re-run with --skip-hooks.")
    finally:
        os.unlink(fh.name)
    head = git(wt, "rev-parse", "HEAD")[1].strip()

    pushed = "NOT PUSHED (no --push)"
    if a.push:
        pushed = S.timed("push (ff, race-safe)", push_ff, wt, seat, creation_dir, a.trailer, env, base_fail)
    try:
        n = S.timed("roster expansion (all seats' *.md)", expand_roster, wt, seat)
        roster_line = "worktree now has all %d seat dirs (comms can address any seat; every seat's top-level *.md readable)" % n
    except SeatError as e:
        roster_line = "roster expansion FAILED (%s); comms post to other seats needs `git sparse-checkout disable`" % str(e)[:120]
    receipt(seat, S, sha, branch, wt, head, boot_line, test_line, pushed, arch, a, roster_line)
    return 0


def push_ff(wt, seat, creation_dir, trailers, env, base_fail):
    for attempt in range(1, 6):
        git(wt, "fetch", "origin", "--quiet", timeout=240)
        tip = git(wt, "rev-parse", "origin/main")[1].strip()
        rc, _, _ = git(wt, "merge-base", "--is-ancestor", tip, "HEAD", check=False)
        if rc != 0:
            changed = git(wt, "diff", "--name-only", "HEAD...%s" % tip)[1].split()
            msg = "Merge origin/main %s into %s\n\n%s\n" % (tip[:9], git(wt, "branch", "--show-current")[1].strip(), "\n".join(trailers))
            rc, out, err = git(wt, "merge", "--no-edit", "-m", msg, tip, check=False, timeout=600)
            if rc != 0:
                git(wt, "merge", "--abort", check=False)
                raise SeatError("merge of origin/main %s conflicted; nothing pushed: %s" % (tip[:9], (err or out)[-300:]))
            if any(c.startswith(REVALIDATE_PREFIXES) for c in changed):
                bad = validate(wt, seat, creation_dir)
                if bad:
                    raise SeatError("validation failed after merging %s: %s" % (tip[:9], bad))
                if base_fail is not None:
                    fail, tail = self_tests(wt, env)
                    new = sorted((fail or set()) - base_fail)
                    if new:
                        raise SeatError("new self-test failure(s) after merging %s; committed locally, nothing pushed: %s" % (tip[:9], new))
        mine = git(wt, "rev-parse", "HEAD")[1].strip()
        rc, out, err = git(wt, "push", "origin", "HEAD:main", check=False, timeout=300)
        if rc == 0:
            git(wt, "fetch", "origin", "--quiet", timeout=240)
            if git(wt, "merge-base", "--is-ancestor", mine, "origin/main", check=False)[0] == 0:
                return "PUSHED %s to origin/main (verified an ancestor; attempt %d)" % (mine[:9], attempt)
            raise SeatError("pushed %s but it is not an ancestor of origin/main" % mine[:9])
    raise SeatError("origin/main kept moving; gave up after 5 attempts; committed locally, nothing lost")


def receipt(seat, S, sha, branch, wt, head, boot_line, test_line, pushed, arch, a, roster_line=""):
    L = [
        "=" * 78,
        "SEAT CREATED: %s   (HOLD, charter PENDING)   total %.1fs" % (seat, S.total()),
        "=" * 78,
        "base_sha   %s" % sha,
        "branch     %s" % branch,
        "worktree   %s   (sparse; `git sparse-checkout disable` for the full tree)" % ascii_safe(wt),
        "roster     %s" % ascii_safe(roster_line)[:160],
        "commit     %s" % head,
        "archaeology: %d file mention(s), %d commit(s), %d path(s), no role on %d refs" % (
            len(arch["grep"]), len(arch["log"]), len(arch["paths"]), arch["refs"]),
        "comms      %s" % ascii_safe(boot_line)[:150],
        "%s" % test_line[:150],
        "push       %s" % pushed,
        "-" * 78,
        S.render(),
        "-" * 78,
        "NEXT: the operator's charter. Not done on purpose: heartbeat to Aporia, any comms post, any science.",
    ]
    print("\n".join(L))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SeatError as e:
        print("SEAT CREATION STOPPED: %s" % e, file=sys.stderr)
        r = RECOVERY
        if r and pathlib.Path(r["wt"]).exists():
            print(NL + "Kept for inspection: worktree %s, local branch %s. Nothing was pushed unless a PUSHED line printed above."
                  % (r["wt"], r["branch"]), file=sys.stderr)
            print("To discard and start over:" + NL + "  git -C %s worktree remove --force %s" % (r["canonical"], r["wt"]) + NL +
                  "  git -C %s branch -D %s" % (r["canonical"], r["branch"]), file=sys.stderr)
        sys.exit(2)
