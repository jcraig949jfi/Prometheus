"""Custodian allow-list for the D2 protocol records (v2; Odysseus S1: records are unauthenticated in git).

    python -I -B <repo>/prometheus/cosmos/c3_holdout_D2/entry.py allowlist add --role AUDIT|COMMITMENT|DESIGNATION|RESULT_SEAL \
        --record <file name in protocol/> --comms-id N
    python -I -B <repo>/prometheus/cosmos/c3_holdout_D2/entry.py allowlist show

A record governs ONLY if its sha256 (LF-normalised bytes as committed on refs/remotes/origin/main) is in this list. The
custodian (Nestor, on M1) adds it after the record's author has confirmed exactly that sha256 over comms:
    AUDIT       -> sender Odysseus (the operator-designated auditor)
    COMMITMENT  -> sender Cosmos
    DESIGNATION -> sender operator or Nestor (the custodian writes the designation)
    RESULT_SEAL -> sender operator or Nestor
This checks the comms message's SENDER and that its subject or body contains the full sha256, and refuses otherwise.

v5 (Odysseus v4 re-audit B-2 / S-4): runs ONLY through entry.py (bound by the governing PASS audit, or before one exists
by the custodian-pinned pre-audit binding); git goes through protocol (absolute path, hardened environment); the record
is read from refs/remotes/origin/main only; and NO repository code outside the binding runs: the comms message is read
with psycopg2 directly (site-packages; declared residual F-3P) using the evidence_wiki connection settings as DATA
(config.json / config.local.json / EW_DB_* environment), not by importing comms or evidence_wiki.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import sys
from pathlib import Path

from prometheus.cosmos.c3_holdout_D2 import protocol

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PROTO_REL = "prometheus/cosmos/c3_holdout_D2/protocol"
ALLOWLIST = Path("C:/Users/jcrai/nestor_receipts/holdout_D2/ALLOWLIST.json")
SENDERS = {"AUDIT": {"Odysseus"}, "COMMITMENT": {"Cosmos"}, "DESIGNATION": {"operator", "Nestor"},
           "RESULT_SEAL": {"operator", "Nestor"}}
# v3 STATUS (Odysseus v2 re-audit FAIL, decisive finding): the comms `sender` field is supplied by the posting client, so
# this check does NOT authenticate the author. The root of trust for protocol records is an OPEN OPERATOR DECISION
# (#925: signed commits + pinned keys / operator-confirmed hashes / accept). v5 does not claim S1 repaired.


def record_bytes(ref, name):
    b = protocol._show(REPO, ref, "%s/%s" % (PROTO_REL, name))
    if b is None:
        raise SystemExit("REFUSED: %s/%s is not committed on %s" % (PROTO_REL, name, ref))
    return b


def _db_settings() -> dict:
    """The evidence_wiki connection settings, read as DATA (no evidence_wiki / comms code is imported)."""
    cfg_dir = REPO / "evidence_wiki"
    cfg = json.loads((cfg_dir / "config.json").read_text(encoding="utf-8"))
    local = cfg_dir / "config.local.json"
    if local.exists():
        cfg.update(json.loads(local.read_text(encoding="utf-8")))
    # v6 (Odysseus v5 F2/SF-3): WHICH database is asked is never taken from committed repository config: the custodian
    # supplies host and database name in the environment; the repository config only supplies credentials
    host, dbname = os.environ.get("EW_DB_HOST"), os.environ.get("EW_DB_NAME")
    if not host or not dbname:
        raise SystemExit("REFUSED: set EW_DB_HOST and EW_DB_NAME (the comms database is chosen by the custodian, not by "
                         "committed configuration)")
    return {"host": host, "dbname": dbname, "user": cfg.get("db_user"),
            "password": os.environ.get("EW_DB_PASSWORD", cfg.get("db_password"))}


def comms_message(mid):
    import psycopg2                                               # site-packages (declared residual F-3P)
    schema = os.environ.get("COMMS_SCHEMA", "comms")
    if not schema.replace("_", "").isalnum():
        raise SystemExit("REFUSED: unsafe comms schema name")
    conn = psycopg2.connect(**_db_settings())
    try:
        cur = conn.cursor()
        cur.execute("SELECT sender, subject, body FROM {s}.messages WHERE id = %s".format(s=schema), (mid,))
        row = cur.fetchone()
    finally:
        conn.close()
    if not row:
        raise SystemExit("REFUSED: no comms message %d" % mid)
    return {"sender": row[0], "subject": row[1] or "", "body": row[2] or ""}


def load(path):
    if not path.exists():
        return {"format": "c3-D2-allowlist/1", "entries": []}
    return json.loads(path.read_text(encoding="utf-8"))


def add(role, name, mid, ref=protocol.DEFAULT_REF, path=ALLOWLIST, message=None):
    if role not in SENDERS:
        raise SystemExit("REFUSED: unknown role %r" % role)
    b = record_bytes(ref, name)
    h = hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest()
    m = message if message is not None else comms_message(mid)
    if m["sender"] not in SENDERS[role]:
        raise SystemExit("REFUSED: comms #%d is from %r, not from %s" % (mid, m["sender"], sorted(SENDERS[role])))
    if h not in m["subject"] and h not in m["body"]:
        raise SystemExit("REFUSED: comms #%d does not contain the record's sha256 %s" % (mid, h))
    data = load(path)
    data["entries"].append({"role": role, "record": name, "sha256": h, "comms_id": mid, "sender": m["sender"],
                            "added_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    return h


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("add", "show"))
    ap.add_argument("--role")
    ap.add_argument("--record")
    ap.add_argument("--comms-id", type=int)
    a = ap.parse_args(argv)
    if not str(os.environ.get("C3D2_ENTRY", "")).startswith("verified"):
        print(json.dumps({"refused": True, "reason": "start allowlist through entry.py (v5 B-2)"}))
        return 3
    if a.cmd == "show":
        print(json.dumps(load(ALLOWLIST), indent=1))
        return 0
    h = add(a.role, a.record, a.comms_id, protocol.DEFAULT_REF)
    print(json.dumps({"added": a.record, "role": a.role, "sha256": h}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
