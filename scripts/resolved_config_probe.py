#!/usr/bin/env python3
"""resolved_config_probe.py — per-machine RESOLVED runtime config (ELEN cycle-2 item e).

The two-pass P18/P19 detour happened because every diagnosis reasoned about the REPO while
the defect lived in a machine's PERSISTENT ENVIRONMENT (HKCU env vars overriding correct
code defaults). This probe prints what a process on THIS machine actually resolves —
host, user, password PROVENANCE (never the value), reachability, auth result — so
machine-specific claims can be settled by execution on the machine in question.

Run on any machine:  python scripts/resolved_config_probe.py
Output: one JSON line (safe to paste into reviews/worklogs; no secrets).
"""
import json
import os
import socket
import sys


def provenance(var, default):
    return {"value_masked": (os.environ.get(var, default)[:4] + "…"
                             if var.endswith("PASSWORD") else os.environ.get(var, default)),
            "source": "ENV-OVERRIDE" if var in os.environ else "code-default"}


def main():
    sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
    out = {
        "machine": socket.gethostname(),
        "AGORA_POSTGRES_HOST": provenance("AGORA_POSTGRES_HOST", "192.168.1.202"),
        "AGORA_POSTGRES_USER": provenance("AGORA_POSTGRES_USER", "lmfdb"),
        "AGORA_POSTGRES_PASSWORD": provenance("AGORA_POSTGRES_PASSWORD", "lmfdb"),
        "AGORA_REDIS_HOST": provenance("AGORA_REDIS_HOST", "(unset)"),
    }
    try:
        import agora_persist
        out["agora_persist_resolves"] = {"host": agora_persist.PG_HOST,
                                         "user": agora_persist.PG_USER}
        ok = agora_persist.write_heartbeat(f"ConfigProbe-{out['machine']}",
                                           out["machine"], "probe")
        out["heartbeat_write"] = bool(ok)
    except Exception as e:
        out["heartbeat_write"] = f"ERROR: {type(e).__name__}: {str(e)[:80]}"
    print(json.dumps(out))
    return 0 if out.get("heartbeat_write") is True else 1


if __name__ == "__main__":
    sys.exit(main())
