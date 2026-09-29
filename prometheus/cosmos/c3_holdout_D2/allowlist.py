"""Custodian allow-list for the D2 protocol records (v2; Odysseus S1: records are unauthenticated in git).

    python <repo>/prometheus/cosmos/c3_holdout_D2/allowlist.py add --role AUDIT|COMMITMENT|DESIGNATION \
        --record <file name in protocol/> --comms-id N [--ref refs/remotes/origin/main]
    python <repo>/prometheus/cosmos/c3_holdout_D2/allowlist.py show

A record governs ONLY if its sha256 (LF-normalised bytes as committed on the reference) is in this list. The custodian
(Nestor, on M1) adds it after the record's author has confirmed exactly that sha256 over comms:
    AUDIT       -> sender Odysseus (the operator-designated auditor)
    COMMITMENT  -> sender Cosmos
    DESIGNATION -> sender operator or Nestor (the custodian writes the designation)
This script checks the comms message's SENDER and that its subject or body contains the full sha256, and refuses
otherwise. It never touches the key, salt or plaintext, and it is not part of any key-holding process. The list lives
outside git on M1 (DEFAULT path below); every change is appended, never rewritten.
"""
import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PROTO_REL = "prometheus/cosmos/c3_holdout_D2/protocol"
ALLOWLIST = Path("C:/Users/jcrai/nestor_receipts/holdout_D2/ALLOWLIST.json")
SENDERS = {"AUDIT": {"Odysseus"}, "COMMITMENT": {"Cosmos"}, "DESIGNATION": {"operator", "Nestor"}}


def record_bytes(ref, name):
    p = subprocess.run(["git", "-C", str(REPO), "show", "%s:%s/%s" % (ref, PROTO_REL, name)], capture_output=True)
    if p.returncode != 0:
        raise SystemExit("REFUSED: %s/%s is not committed on %s" % (PROTO_REL, name, ref))
    return p.stdout


def comms_message(mid):
    sys.path.insert(0, str(REPO))
    from comms import api                                        # the comms bus (outside the audited package)
    conn = api.connect()
    cur = conn.cursor()
    cur.execute("SELECT sender, subject, body FROM {s}.messages WHERE id = %s".format(s=api.schema()), (mid,))
    row = cur.fetchone()
    if not row:
        raise SystemExit("REFUSED: no comms message %d" % mid)
    return {"sender": row[0], "subject": row[1] or "", "body": row[2] or ""}


def load(path):
    if not path.exists():
        return {"format": "c3-D2-allowlist/1", "entries": []}
    return json.loads(path.read_text(encoding="utf-8"))


def add(role, name, mid, ref, path=ALLOWLIST, message=None):
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
    ap.add_argument("--ref", default="refs/remotes/origin/main")
    a = ap.parse_args(argv)
    if a.cmd == "show":
        print(json.dumps(load(ALLOWLIST), indent=1))
        return 0
    h = add(a.role, a.record, a.comms_id, a.ref)
    print(json.dumps({"added": a.record, "role": a.role, "sha256": h}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
