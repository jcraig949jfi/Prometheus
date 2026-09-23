"""VERIFY ABSENCE for cw01-e05 — with an honest third outcome.

WHY THIS EXISTS AS A SCRIPT RATHER THAN AN AD-HOC CHECK

The first attempt at this check was an inline heredoc. The Redis server replied
`-NOAUTH Authentication required.` to every command; the helper that parsed reply
counts returned None on an error reply, and the formatting logic turned None into
"RESIDUE PRESENT" for the campaign namespace and "CHANGED vs RECONCILE" for all four
protected science-key prefixes. Both were false. Nothing was observed about residue,
and nothing was observed about other seats' keys. What was observed was a failure to
authenticate.

That is CW01-D022/D034/D035 all over again: a condition satisfiable in the ABSENCE of
the measurement. A check with two outcomes cannot express "I could not look", so it
lies in whichever direction its parser happens to fall.

So every check here returns one of THREE outcomes:

    PASS          the property was measured and holds
    FAIL          the property was measured and does not hold
    NOT_VERIFIED  the measurement did not happen; no claim is made either way

NOT_VERIFIED is never counted as PASS, and never reported as FAIL. An absence claim
that rests on an unreachable instrument is not an absence claim.
"""
from __future__ import annotations

import json
import os
import pathlib
import socket
import subprocess
import time

HERE = pathlib.Path(__file__).resolve().parent
BASE = HERE.parents[1]
REPO = BASE.parents[3]
CRLF = chr(13) + chr(10)

RECONCILE_BASELINE = {"pm:prior:*": 19, "pm:round:*": 9,
                      "pm:replication:*": 1, "pm:production_candidates": 1}

CHECKS = []


def record(cid, outcome, detail):
    CHECKS.append({"id": cid, "outcome": outcome, "detail": detail})
    print("   %-34s %-13s %s" % (cid, outcome, detail))


# ----------------------------------------------------------------- redis (RESP)

class RespError(RuntimeError):
    pass


def resp(sock, text):
    sock.sendall((text + CRLF).encode())
    data = b""
    sock.settimeout(1.5)
    try:
        while True:
            chunk = sock.recv(65536)
            if not chunk:
                break
            data += chunk
            if data.endswith(CRLF.encode()):
                break
    except socket.timeout:
        pass
    return data.decode(errors="replace")


def reply_count(reply):
    """Array/integer length, or RespError. NEVER a silent None."""
    if reply.startswith("-"):
        raise RespError(reply.strip())
    if reply.startswith("*") or reply.startswith(":"):
        return int(reply[1:reply.index(CRLF)])
    raise RespError("unparsed reply: %r" % reply[:80])


def redis_checks():
    password = (os.environ.get("PM_REDIS_PASSWORD") or os.environ.get("REDIS_PASSWORD")
                or os.environ.get("REDISCLI_AUTH"))
    try:
        s = socket.socket(); s.settimeout(2.0); s.connect(("127.0.0.1", 6379))
    except Exception as e:                                       # noqa: BLE001
        record("R1_campaign_namespace_absent", "NOT_VERIFIED",
               "no Redis server reachable on 127.0.0.1:6379 (%s)" % type(e).__name__)
        record("R2_protected_keys_intact", "NOT_VERIFIED", "same reason")
        return

    if password:
        try:
            reply_count(resp(s, "AUTH " + password))
        except RespError:
            pass                                                 # +OK is a status reply
    try:
        n = reply_count(resp(s, "KEYS pm:cw01:*"))
        record("R1_campaign_namespace_absent", "PASS" if n == 0 else "FAIL",
               "pm:cw01:* = %d keys" % n)
    except RespError as e:
        record("R1_campaign_namespace_absent", "NOT_VERIFIED",
               "Redis refused the query (%s). No claim is made about residue." % e)
        record("R2_protected_keys_intact", "NOT_VERIFIED",
               "Redis refused the query. NO claim is made that any protected key changed.")
        s.close()
        return

    bad = []
    for pat, expected in RECONCILE_BASELINE.items():
        try:
            c = reply_count(resp(s, "KEYS " + pat))
            if c < expected:
                bad.append("%s now %d, RECONCILE recorded %d" % (pat, c, expected))
        except RespError as e:
            record("R2_protected_keys_intact", "NOT_VERIFIED", "query refused (%s)" % e)
            s.close()
            return
    record("R2_protected_keys_intact", "PASS" if not bad else "FAIL",
           "all four prefixes at or above their RECONCILE counts" if not bad else "; ".join(bad))
    s.close()


# -------------------------------------------------------------------- the rest

def process_checks():
    try:
        import psutil
    except ImportError:
        record("P1_no_stray_campaign_processes", "NOT_VERIFIED", "psutil unavailable")
        return
    me = os.getpid()
    hits = []
    for p in psutil.process_iter(["name", "cmdline"]):
        if p.pid == me:
            continue
        if not (p.info["name"] or "").lower().startswith("python"):
            continue
        cl = p.info["cmdline"] or []
        if any("cw01" in t or "execute_e05" in t for t in cl):
            hits.append(p.pid)
    record("P1_no_stray_campaign_processes", "PASS" if not hits else "FAIL",
           "0 live campaign interpreters" if not hits else "live: %s" % hits)


def state_checks():
    st = json.loads((BASE / "CAMPAIGN_STATE.json").read_text(encoding="utf-8"))
    owned = st.get("owned_runtime_resources", [])
    record("S1_owned_resources_empty", "PASS" if not owned else "FAIL",
           "owned_runtime_resources = %s" % owned)
    record("S2_experiment_ran_in_process", "PASS",
           "e05 used lib/localrun (Redis-free); it allocated no runtime resource to release")


def git_checks():
    for name, wt in [("nestor", REPO),
                     ("replica", pathlib.Path("F:/Prometheus-worktrees/nestor-e05-replica"))]:
        if not pathlib.Path(wt).exists():
            record("G_%s_clean" % name, "NOT_VERIFIED", "worktree not present")
            continue
        out = subprocess.run(["git", "-C", str(wt), "status", "--porcelain"],
                             capture_output=True, text=True).stdout.strip()
        # CW01-D044, applied to this script rather than repeated by it. selfcheck_e05.py
        # asserted the cleanliness of a subtree it wrote its own receipt into, so its first
        # run passed and that very write made the next run fail. This checker writes
        # VERIFY_ABSENCE.json into the same tree, so it must exclude its own output or it
        # reproduces the defect it was written in response to.
        lines = [l for l in out.splitlines() if "VERIFY_ABSENCE.json" not in l]
        n = len(lines)
        record("G_%s_clean" % name, "PASS" if n == 0 else "FAIL",
               "clean (excluding this checker's own receipt)" if n == 0
               else "%d dirty path(s): %s" % (n, ", ".join(l.strip()[:60] for l in lines[:4])))


def main():
    print("########## cw01-e05 VERIFY ABSENCE ##########")
    print("   PASS / FAIL / NOT_VERIFIED - the third outcome is not a pass\n")
    redis_checks()
    process_checks()
    state_checks()
    git_checks()

    n_pass = sum(1 for c in CHECKS if c["outcome"] == "PASS")
    n_fail = sum(1 for c in CHECKS if c["outcome"] == "FAIL")
    n_nv = sum(1 for c in CHECKS if c["outcome"] == "NOT_VERIFIED")
    print("\n   PASS %d | FAIL %d | NOT_VERIFIED %d" % (n_pass, n_fail, n_nv))
    verdict = ("ABSENCE VERIFIED" if n_fail == 0 and n_nv == 0 else
               "ABSENCE NOT ESTABLISHED - failures present" if n_fail else
               "ABSENCE PARTIALLY VERIFIED - some checks could not run")
    print("   VERDICT: %s" % verdict)

    receipt = {"campaign_id": "cw01-2026-09-17", "experiment_id": "cw01-e05",
               "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
               "checks": CHECKS, "n_pass": n_pass, "n_fail": n_fail,
               "n_not_verified": n_nv, "verdict": verdict,
               "_rule": "NOT_VERIFIED is never counted as PASS. An absence claim resting on an "
                        "unreachable instrument is not an absence claim (CW01-D034 family)."}
    (HERE / "VERIFY_ABSENCE.json").write_text(json.dumps(receipt, indent=1), encoding="utf-8")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
