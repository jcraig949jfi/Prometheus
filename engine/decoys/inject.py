"""Decoy injector — plant/remove typed decoys from engine/decoys/DECOY_SET.jsonl.

Decoy law (germline_infrastructure section 6, RATIFIED): planted anomalies in the
tables MUST appear in monitor reports; a monitor that misses its decoys is itself
reported. This tool automates the plantable classes (HB-STALE-ONLINE,
QUEUE-ZOMBIE-RUNNING, CONSUMPTION-ORPHAN, GATE-WITHOUT-ELI5). CITATION-PHANTOM and
ATTESTATION-TERTIARY-AS-PRIMARY are manual classes for blind planting by
Charon/James (see blind_note fields).

Every plant is recorded in engine/decoys/PLANTED.jsonl (the ground-truth ledger)
with a removal receipt when removed. NOTE the v0 blindness limitation, stated
plainly: this ledger lives in the same repo the monitor reads, so a cheating
monitor COULD key on it. Enforced blindness = Charon/James plant manually and keep
the ledger off-repo until scoring. The in-repo ledger is for the NON-blind
self-test cycles and for audit trail.

Usage:
  python engine/decoys/inject.py plant-hb | remove-hb
  python engine/decoys/inject.py plant-zombie | remove-zombie
  python engine/decoys/inject.py plant-orphan | remove-orphan
  python engine/decoys/inject.py plant-gate | remove-gate
  python engine/decoys/inject.py status
"""
from __future__ import annotations
import json
import pathlib
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]
LEDGER = pathlib.Path(__file__).parent / "PLANTED.jsonl"
HB_NAME = "Decoy-Erebus-P30"
ZOMB_ID = "ZOMB-DEC002-P30"
ORPHAN_KEY = "DEC-004 orphan-consumption decoy P30"
GATE_ID = "GATED-DEC005-P30"


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def ledger_write(rec):
    with LEDGER.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _pg():
    sys.path.insert(0, str(ROOT / "scripts"))
    import agora_persist  # noqa: E402
    return agora_persist._connect()


def plant_hb():
    conn = _pg()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO agora.agent_heartbeats (agent_name, machine, status, last_heartbeat) "
                "VALUES (%s, 'M9', 'online', now() - interval '30 days') "
                "ON CONFLICT (agent_name) DO UPDATE SET last_heartbeat = now() - interval '30 days', "
                "status = 'online'", (HB_NAME,))
        conn.commit()
    finally:
        conn.close()
    ledger_write({"decoy": "DEC-001", "planted": now(), "key": HB_NAME, "surface": "agora.agent_heartbeats"})
    print(f"planted DEC-001 as {HB_NAME}")


def remove_hb():
    conn = _pg()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM agora.agent_heartbeats WHERE agent_name = %s", (HB_NAME,))
            n = cur.rowcount
        conn.commit()
    finally:
        conn.close()
    ledger_write({"decoy": "DEC-001", "removed": now(), "key": HB_NAME, "rows": n})
    print(f"removed DEC-001 ({n} row)")


def plant_zombie():
    bl = ROOT / "engine/queues/BACKLOG.jsonl"
    rec = {"id": ZOMB_ID, "title": "Decoy: zombie running thread (DEC-002)", "source": "decoy",
           "consumer": "decoy law", "priority": 10, "gate": None, "bottleneck": None,
           "status": "RUNNING", "parked_reason": None, "meta": {"decoy": True},
           "generated": "2026-07-21T00:00:00+00:00"}
    with bl.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    ledger_write({"decoy": "DEC-002", "planted": now(), "key": ZOMB_ID, "surface": "BACKLOG.jsonl"})
    print(f"planted DEC-002 as {ZOMB_ID}")


def _remove_line(path, key_field, key_value, decoy):
    lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    kept = [l for l in lines if json.loads(l).get(key_field) != key_value]
    path.write_text("\n".join(kept) + "\n", encoding="utf-8")
    n = len(lines) - len(kept)
    ledger_write({"decoy": decoy, "removed": now(), "key": key_value, "rows": n})
    print(f"removed {decoy} ({n} line)")


def remove_zombie():
    _remove_line(ROOT / "engine/queues/BACKLOG.jsonl", "id", ZOMB_ID, "DEC-002")


def plant_orphan():
    co = ROOT / "engine/queues/CONSUMPTION.jsonl"
    rec = {"ts": now(), "object": ORPHAN_KEY,
           "consumed_by": "aporia/docs/NONEXISTENT_ARTIFACT_zzz.md",
           "effect": {"reading": "decoy"}, "summary": "DEC-004: consumed_by names a path that does not exist"}
    with co.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    ledger_write({"decoy": "DEC-004", "planted": now(), "key": ORPHAN_KEY, "surface": "CONSUMPTION.jsonl"})
    print("planted DEC-004")


def remove_orphan():
    _remove_line(ROOT / "engine/queues/CONSUMPTION.jsonl", "object", ORPHAN_KEY, "DEC-004")


def plant_gate():
    bl = ROOT / "engine/queues/BACKLOG.jsonl"
    rec = {"id": GATE_ID, "title": "Decoy: parked gate with no ELI5 (DEC-005)", "source": "decoy",
           "consumer": "decoy law", "priority": 10,
           "gate": "decoy gate string absent from GATE_ELI5 (DEC-005)", "bottleneck": None,
           "status": "PARKED", "parked_reason": "decoy", "meta": {"decoy": True}, "generated": now()}
    with bl.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    ledger_write({"decoy": "DEC-005", "planted": now(), "key": GATE_ID, "surface": "BACKLOG.jsonl"})
    print(f"planted DEC-005 as {GATE_ID}")


def remove_gate():
    _remove_line(ROOT / "engine/queues/BACKLOG.jsonl", "id", GATE_ID, "DEC-005")


def status():
    if not LEDGER.exists():
        print("no plants recorded")
        return
    recs = [json.loads(l) for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()]
    open_keys = {}
    for r in recs:
        if "planted" in r:
            open_keys[r["key"]] = r
        elif "removed" in r:
            open_keys.pop(r["key"], None)
    print(f"{len(recs)} ledger records; {len(open_keys)} decoys currently OPEN:")
    for k, r in open_keys.items():
        print(f"  {r['decoy']} {k} on {r['surface']} since {r['planted']}")


CMDS = {"plant-hb": plant_hb, "remove-hb": remove_hb, "plant-zombie": plant_zombie,
        "remove-zombie": remove_zombie, "plant-orphan": plant_orphan,
        "remove-orphan": remove_orphan, "plant-gate": plant_gate,
        "remove-gate": remove_gate, "status": status}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd not in CMDS:
        print(__doc__)
        sys.exit(2)
    CMDS[cmd]()
