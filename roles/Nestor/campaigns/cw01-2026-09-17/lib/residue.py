"""One residue scanner, used by BOTH reconcile and verify-absence.

CW01-D017: e01's RECONCILE scanned only `pm:jobs:*`, cleaned 8 dead consumers and
reported the listener check complete. VERIFY ABSENCE later found 53 more ghosts on
`pm:swarm`, idle 69.4 h. The bug was not the cleaning, it was the SCOPE: I cleaned
where I looked and then claimed clean everywhere.

The structural fix is that the two phases must not be able to disagree, so they
call the same function. Anything enumerated at RECONCILE is enumerated at VERIFY
ABSENCE by construction.

Design rules learned the hard way:
  * enumerate, never hand-list a prefix -- scan_iter over the whole namespace
  * type-guard every key: iterating pm:round:* once crashed on WRONGTYPE
  * a delete call returning OK is not proof; verify() re-reads
  * never reap on resemblance: pending>0 or a fresh idle time means someone may
    still own it, so it is KEPT and reported
"""
from __future__ import annotations

import time

DEFAULT_IDLE_MIN_MS = 60 * 60 * 1000          # 1 hour


def scan(r, pattern="pm:*", count=1000):
    """Full, type-guarded census of the substrate. No mutation."""
    out = {"scanned_local": time.strftime("%Y-%m-%d %H:%M:%S"), "pattern": pattern,
           "keys_by_type": {}, "keys_by_family": {}, "streams": [], "consumers": [], "errors": []}
    for k in r.scan_iter(match=pattern, count=count):
        try:
            t = r.type(k)
        except Exception as e:                 # WRONGTYPE and friends must not abort the scan
            out["errors"].append({"key": k, "err": str(e)})
            continue
        out["keys_by_type"][t] = out["keys_by_type"].get(t, 0) + 1
        fam = ":".join(k.split(":")[:2])
        out["keys_by_family"][fam] = out["keys_by_family"].get(fam, 0) + 1
        if t != "stream":
            continue
        try:
            groups = r.xinfo_groups(k)
        except Exception as e:
            out["errors"].append({"key": k, "err": str(e)})
            continue
        out["streams"].append({"key": k, "xlen": r.xlen(k), "groups": len(groups)})
        for g in groups:
            try:
                cons = r.xinfo_consumers(k, g["name"])
            except Exception as e:
                out["errors"].append({"key": k, "group": g["name"], "err": str(e)})
                continue
            for c in cons:
                out["consumers"].append({
                    "stream": k, "group": g["name"], "consumer": c["name"],
                    "idle_ms": int(c.get("idle", 0)), "pending": int(c.get("pending", 0))})
    return out


def dead_consumers(census, idle_min_ms=DEFAULT_IDLE_MIN_MS):
    """Consumers safe to reap: no pending work AND idle beyond the threshold."""
    return [c for c in census["consumers"]
            if c["pending"] == 0 and c["idle_ms"] > idle_min_ms]


def live_consumers(census, idle_min_ms=DEFAULT_IDLE_MIN_MS):
    """Everything dead_consumers refuses to touch, with the reason."""
    out = []
    for c in census["consumers"]:
        if c["pending"] > 0:
            out.append({**c, "kept_because": "pending > 0 -- work may still be owed"})
        elif c["idle_ms"] <= idle_min_ms:
            out.append({**c, "kept_because": f"idle {c['idle_ms']/1000:.0f}s <= threshold"})
    return out


def reap(r, consumers):
    """Delete exactly the consumers handed in. Never pattern-matches, never guesses."""
    done, failed = [], []
    for c in consumers:
        try:
            r.xgroup_delconsumer(c["stream"], c["group"], c["consumer"])
            done.append(c)
        except Exception as e:
            failed.append({**c, "err": str(e)})
    return {"removed": done, "failed": failed}


def verify(r, namespace=None, pattern="pm:*"):
    """Re-read the substrate and assert absence. A successful delete is not proof."""
    census = scan(r, pattern=pattern)
    owned = []
    if namespace:
        owned = [k for k in r.scan_iter(match=namespace + "*", count=1000)]
    return {
        "namespace": namespace, "owned_keys": len(owned), "owned_sample": owned[:10],
        "live_consumers": len(census["consumers"]),
        "consumer_detail": census["consumers"][:20],
        "streams": len(census["streams"]), "errors": census["errors"],
        "clean": (not owned) and not census["consumers"],
    }


def reconcile(r, namespace=None, pattern="pm:*", idle_min_ms=DEFAULT_IDLE_MIN_MS,
              protect_families=(), dry_run=False):
    """RECONCILE: census -> reap dead consumers -> verify. Returns an auditable record.

    protect_families guards science keys (e.g. 'pm:prior', 'pm:replication'); they
    are reported but never touched. Consumers are runtime residue; keys are not.
    """
    before = scan(r, pattern=pattern)
    dead = dead_consumers(before, idle_min_ms)
    kept = live_consumers(before, idle_min_ms)
    result = {"before": {"keys_by_family": before["keys_by_family"],
                         "consumers": len(before["consumers"]),
                         "streams": len(before["streams"]), "errors": before["errors"]},
              "dead_found": len(dead), "kept": kept, "dry_run": dry_run,
              "protected_families": {f: before["keys_by_family"].get(f, 0) for f in protect_families}}
    result["reaped"] = {"removed": [], "failed": []} if dry_run else reap(r, dead)
    result["after"] = verify(r, namespace=namespace, pattern=pattern)
    result["clean"] = result["after"]["clean"] if not dry_run else None
    return result


# --------------------------------------------------------------------------
# PROCESS RESIDUE
#
# CW01-D018: an e02 RECONCILE reported "stray workers: 8". All 8 were Windows
# desktop processes -- four RuntimeBroker.exe, UserOOBEBroker.exe, NVIDIA
# Overlay.exe and two GOG Galaxy QtWebEngineProcess.exe -- caught because
# "broker" is a substring of "RuntimeBroker" and "epoch" appears inside browser
# command lines. Three of my own bash shells matched ALL five tokens, because the
# Bash tool's command string contains the whole script being run.
#
# The rule (already in the notes, violated anyway): match the INTERPRETER process
# and EXACT argv tokens. Never substring-match a joined command line, and never
# match on generic English words.
# --------------------------------------------------------------------------

INTERPRETERS = ("python.exe", "python", "pythonw.exe", "claude.exe", "node.exe")


def _argv_tokens(cmdline):
    """Split argv entries into comparable tokens: path segments and module names."""
    toks = set()
    for a in cmdline or []:
        a = a.replace("\\", "/")
        for part in a.split("/"):
            for piece in part.replace(":", " ").replace("=", " ").split():
                toks.add(piece.lower())
                if piece.endswith(".py"):
                    toks.add(piece[:-3].lower())
        for piece in a.split("."):
            toks.add(piece.lower())
    return toks


def process_census(tokens, session_root=None, interpreters=INTERPRETERS, own_pid=None):
    """Processes that are OURS by evidence, not by resemblance.

    tokens       exact argv tokens to look for (e.g. {"world_e02", "execute_e02"})
    session_root pid whose descendants are this agent's own shells -- excluded
    """
    import os
    import psutil

    own_pid = own_pid or os.getpid()
    chain = set()
    try:
        p = psutil.Process(own_pid)
        while p:
            chain.add(p.pid)
            p = p.parent()
    except Exception:
        pass
    kin = set()
    if session_root:
        try:
            rp = psutil.Process(session_root)
            kin = {c.pid for c in rp.children(recursive=True)} | {session_root}
        except Exception:
            pass

    want = {t.lower() for t in tokens}
    out = {"matched": [], "excluded_self": 0, "scanned": 0}
    for q in psutil.process_iter(["pid", "ppid", "name", "create_time"]):
        out["scanned"] += 1
        try:
            nm = (q.info["name"] or "").lower()
            if nm not in interpreters:            # only real interpreters, never system exes
                continue
            if q.info["pid"] in chain or q.info["pid"] in kin:
                out["excluded_self"] += 1
                continue
            if not (_argv_tokens(q.cmdline()) & want):
                continue
            out["matched"].append({"pid": q.info["pid"], "ppid": q.info["ppid"], "name": nm,
                                   "cmdline": " ".join(q.cmdline() or [])[:160]})
        except Exception:
            continue
    return out
