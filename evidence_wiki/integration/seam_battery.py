"""PEW world-provenance SEAM battery A-J (charter s7, 2026-09-03).

Proves the frozen seam: what sfe_entry_hash means, how ordinary evidence binds
to a fossil encounter, that unsupported fields fail loudly, and that the whole
chain traverses mechanically in both directions.

Usage (from evidence_wiki/):
    python integration/seam_battery.py
    python integration/seam_battery.py --host 192.168.1.202 --machine M2 --no-sql

Exit 0 = every scored gate PASS. Results -> integration/seam_results.json.
"""
import argparse
import json
import sqlite3
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
FIX = json.loads((HERE / "integration" / "fixture_harmonia_v1.json")
                 .read_text(encoding="utf-8"))
SFE_DB = (HERE.parent / "SerendipityFoundry" / "SerendipityFoundryEngine" /
          "var" / "engine.db")
R = []


def gate(name, ok, detail, skipped=False):
    R.append({"gate": name, "pass": bool(ok), "skipped": skipped,
              "detail": detail})
    print(f"[{'SKIP' if skipped else ('PASS' if ok else 'FAIL')}] {name}: {detail}")
    return bool(ok)


class C:
    def __init__(self, host, port, token, machine, agent):
        self.base = f"http://{host}:{port}/api/v1"
        self.h = {"Authorization": f"Bearer {token}",
                  "X-Prometheus-Machine": machine, "X-Prometheus-Agent": agent}

    def get(self, p, **q):
        return requests.get(f"{self.base}/{p}", headers=self.h, params=q,
                            timeout=60)

    def post(self, p, b):
        return requests.post(f"{self.base}/{p}", headers=self.h, json=b,
                             timeout=90)


def sql(q, args=()):
    from ew import db as ewdb
    conn = ewdb.connect()
    try:
        with ewdb.dict_cur(conn) as cur:
            cur.execute(q, args)
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def sfe_objects():
    """One real object of each SFE hash class, straight from the live ledger
    (read-only). This is what makes gate A a real class test."""
    if not SFE_DB.exists():
        return None
    c = sqlite3.connect(f"file:{SFE_DB}?mode=ro", uri=True)
    c.row_factory = sqlite3.Row
    o = {}
    r = c.execute("SELECT event_id, entry_hash, event_seq, world_id FROM events "
                  "ORDER BY event_seq DESC LIMIT 1").fetchone()
    o["event"] = dict(r) if r else None
    r = c.execute("SELECT artifact_id, blob_hash, world_id FROM artifacts "
                  "LIMIT 1").fetchone()
    o["artifact"] = dict(r) if r else None
    r = c.execute("SELECT world_id, head_hash, seed_root FROM worlds WHERE "
                  "head_hash IS NOT NULL LIMIT 1").fetchone()
    o["world"] = dict(r) if r else None
    c.close()
    return o


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=None)
    ap.add_argument("--machine", default="M1")
    ap.add_argument("--agent", default="seam-battery")
    ap.add_argument("--no-sql", action="store_true")
    a = ap.parse_args()
    cfg = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
    port = a.port or cfg["port"]
    tok = cfg["machine_tokens"].get(a.machine) or cfg["auth_token"]
    c = C(a.host, port, tok, a.machine, a.agent)
    enc, world, player = FIX["encounter"], FIX["world"], FIX["player"]

    # --- I: live migration state -------------------------------------------
    h = c.get("health").json()
    ct = c.get("fossil/contract").json()
    mig = {}
    if not a.no_sql:
        pk = sql("SELECT pg_get_constraintdef(oid) d FROM pg_constraint WHERE "
                 "conrelid='ew.fossil_encounters'::regclass AND contype='p'")
        fk = sql("SELECT pg_get_constraintdef(oid) d FROM pg_constraint WHERE "
                 "conname='evidence_fossil_encounter_fk'")
        cols = sql("SELECT column_name FROM information_schema.columns WHERE "
                   "table_schema='ew' AND table_name='evidence' AND "
                   "column_name LIKE 'encounter%%'")
        mig = {"fossil_pk": pk[0]["d"] if pk else None,
               "evidence_fk": fk[0]["d"] if fk else None,
               "evidence_cols": sorted(r["column_name"] for r in cols)}
        ok = (mig["fossil_pk"] == "PRIMARY KEY (encounter_id, run_key)" and
              mig["evidence_fk"] is not None and
              h["schema_version"] == 4)
    else:
        ok = h["schema_version"] == 4
    gate("I_live_migration_state", ok,
         f"health.schema_version={h['schema_version']} "
         f"contract={h['fossil_contract']} | {mig}")

    # --- A: hash semantics --------------------------------------------------
    o = sfe_objects()
    if not o or not o["event"]:
        gate("A_hash_semantics", False, "no SFE ledger available", skipped=True)
        real_enc = None
    else:
        ev, art, wld = o["event"], o["artifact"], o["world"]
        base = {"encounter_id": f"SEAM-{ev['event_id']}",
                "run_id": "seam-A", "world_id": ev["world_id"],
                "players": [player["player_id"]], "namespace": "test",
                "outcome": "committed"}
        good = c.post("fossil/encounters", dict(
            base, sfe_entry_hash=ev["entry_hash"], sfe_event_id=ev["event_id"],
            sfe_event_seq=ev["event_seq"]))
        # wrong CLASS, right shape: artifact blob_hash / artifact_id, and a
        # world head_hash -- all sha256:-shaped, none is an event entry_hash.
        wrong = {}
        for label, val in (("blob_hash", art and art["blob_hash"]),
                           ("artifact_id", art and art["artifact_id"]),
                           ("world_head_hash", wld and wld["head_hash"])):
            if not val:
                continue
            r = c.post("fossil/encounters", dict(
                base, encounter_id=f"SEAM-WRONGCLASS-{label}", run_id="seam-A",
                sfe_entry_hash=val))          # NO sfe_event_id available
            wrong[label] = r.status_code
        r_shape = c.post("fossil/encounters", dict(
            base, encounter_id="SEAM-BADSHAPE", run_id="seam-A",
            sfe_entry_hash="sha256:NOT-HEX", sfe_event_id=ev["event_id"]))
        r_evshape = c.post("fossil/encounters", dict(
            base, encounter_id="SEAM-BADEVT", run_id="seam-A",
            sfe_entry_hash=ev["entry_hash"], sfe_event_id=art["artifact_id"]))
        ok = (good.status_code == 200 and
              all(v == 422 for v in wrong.values()) and
              r_shape.status_code == 422 and r_evshape.status_code == 422)
        gate("A_hash_semantics", ok,
             f"sanctioned event entry_hash+event_id -> {good.status_code}; "
             f"wrong-class unpaired {wrong}; bad hash shape -> "
             f"{r_shape.status_code}; non-evt event_id -> {r_evshape.status_code}")
        real_enc = base | {"sfe_entry_hash": ev["entry_hash"],
                           "sfe_event_id": ev["event_id"],
                           "sfe_event_seq": ev["event_seq"],
                           "encounter_id": f"SEAM-{ev['event_id']}"}

    # anchors + the fixture encounter the binding will point at
    c.post("fossil/worlds", world)
    c.post("fossil/players", player)
    c.post("fossil/encounters", enc)

    # a packet + claim to hang ordinary evidence on
    pk = c.post("packets", {"uri": "evidence_wiki/integration/seam_battery.py",
                            "kind": "code"})
    pid = pk.json().get("packet_id")
    cl = c.post("claims", {
        "text_canonical": "SEAM battery: bound evidence for the fixture encounter.",
        "source_wording": "SEAM battery: bound evidence for the fixture encounter.",
        "status": "OBSERVED", "packet_id": pid, "write_stage": "SOURCE_BOUND",
        "namespace": "test"})
    cid = cl.json().get("claim_id")

    # --- B: evidence -> fossil binding + forward traversal ------------------
    e = c.post("evidence", {
        "packet_id": pid, "claim_id": cid,
        "source_quote": "SEAM battery bound-evidence quote.",
        "evidence_type": "OBSERVATIONAL_ANALYSIS", "write_stage": "SOURCE_BOUND",
        "namespace": "test",
        "encounter_id": enc["encounter_id"],
        "encounter_run_id": enc["run_id"]})
    eid = e.json().get("evidence_id") if e.status_code == 200 else None
    prov = c.get(f"provenance/evidence/{eid}") if eid else None
    p = prov.json() if prov is not None and prov.status_code == 200 else {}
    fe = p.get("fossil_encounter", {})
    recovered = {
        "encounter_id": fe.get("encounter_id"), "run_id": fe.get("run_id"),
        "world_id": fe.get("world_id"), "players": fe.get("players"),
        "sfe_entry_hash": fe.get("sfe_entry_hash"),
        "sfe_event_id": fe.get("sfe_event_id"),
        "sfe_event_seq": fe.get("sfe_event_seq")}
    ok = (e.status_code == 200 and p.get("bound") is True and
          recovered["encounter_id"] == enc["encounter_id"] and
          recovered["run_id"] == enc["run_id"] and
          recovered["world_id"] == enc["world_id"] and
          recovered["players"] == enc["players"] and
          recovered["sfe_entry_hash"] == enc["sfe_entry_hash"] and
          recovered["sfe_event_seq"] == enc["sfe_event_seq"] and
          p.get("proteus", {}).get("organism_ids") == enc["players"])
    gate("B_evidence_to_fossil_traversal", ok,
         f"evidence={eid} -> {json.dumps(recovered)}")

    # --- C: reverse query ---------------------------------------------------
    rev = c.get(f"fossil/encounters/{enc['encounter_id']}/evidence",
                run_id=enc["run_id"])
    ids = [x["evidence_id"] for x in rev.json().get("evidence", [])] \
        if rev.status_code == 200 else []
    gate("C_reverse_query", rev.status_code == 200 and eid in ids,
         f"encounter -> {len(ids)} evidence row(s); contains {eid}: {eid in ids}")

    # --- D: silent-loss negative control on all five closed models ----------
    d = {}
    d["PacketIn"] = c.post("packets", {
        "uri": "evidence_wiki/integration/seam_battery.py", "kind": "code",
        "world_id": "wld_UNSUPPORTED"}).status_code
    d["ExperimentIn"] = c.post("experiments", {
        "agent": "Mnemosyne", "project": "seam", "title": "neg control",
        "world_id": "wld_UNSUPPORTED"}).status_code
    d["ClaimIn"] = c.post("claims", {
        "text_canonical": "neg control", "source_wording": "neg control",
        "status": "OBSERVED", "packet_id": pid,
        "world_id": "wld_UNSUPPORTED"}).status_code
    d["EvidenceIn"] = c.post("evidence", {
        "packet_id": pid, "source_quote": "neg control",
        "evidence_type": "OBSERVATIONAL_ANALYSIS",
        "world_id": "wld_UNSUPPORTED"}).status_code
    d["RelationIn"] = c.post("relations", {
        "src_type": "claim", "src_id": cid, "relation_type": "SUPPORTS",
        "dst_type": "claim", "dst_id": cid, "epistemic_class": "OBSERVED",
        "creation_method": "MODEL_EXTRACTED", "packet_id": pid,
        "world_id": "wld_UNSUPPORTED"}).status_code
    gate("D_unsupported_field_fails_closed",
         all(v == 422 for v in d.values()), json.dumps(d))

    # --- D2: a binding to a NON-EXISTENT encounter is refused ---------------
    bad = c.post("evidence", {
        "packet_id": pid, "source_quote": "binding to a ghost encounter.",
        "evidence_type": "OBSERVATIONAL_ANALYSIS",
        "encounter_id": "NO-SUCH-ENCOUNTER", "encounter_run_id": "nope"})
    leaked = [] if a.no_sql else sql(
        "SELECT 1 FROM ew.evidence WHERE encounter_id=%s", ("NO-SUCH-ENCOUNTER",))
    gate("D2_unknown_encounter_binding_refused",
         bad.status_code == 422 and not leaked,
         f"HTTP {bad.status_code} {bad.text[:90]}; rows left behind: {len(leaked)}")

    # --- E: duplicate / replay ---------------------------------------------
    again = c.post("fossil/encounters", enc)
    e2 = c.post("evidence", {
        "packet_id": pid, "claim_id": cid,
        "source_quote": "SEAM battery bound-evidence quote.",
        "evidence_type": "OBSERVATIONAL_ANALYSIS", "write_stage": "SOURCE_BOUND",
        "namespace": "test",
        "encounter_id": enc["encounter_id"], "encounter_run_id": enc["run_id"]})
    same_id = e2.json().get("evidence_id") == eid if e2.status_code == 200 else False
    n_ev = None if a.no_sql else len(sql(
        "SELECT 1 FROM ew.evidence WHERE evidence_id=%s", (eid,)))
    gate("E_duplicate_replay",
         again.json().get("status") == "duplicate_identical" and same_id and
         (a.no_sql or n_ev == 1),
         f"encounter replay={again.json().get('status')}; evidence replay "
         f"returns same content-addressed id={same_id}; stored copies={n_ev}")

    # --- F: conflict --------------------------------------------------------
    conf = c.post("fossil/encounters", dict(enc, outcome="SEAM-DIFFERENT"))
    conf2 = c.post("fossil/worlds", dict(world, seed_root="999"))
    gate("F_conflict_fails_overtly",
         conf.status_code == 409 and conf2.status_code == 409,
         f"encounter differing -> {conf.status_code} {conf.text[:70]}; "
         f"world anchor differing -> {conf2.status_code}")

    # --- G: namespace firewall ---------------------------------------------
    if a.no_sql:
        gate("G_namespace_firewall", False, "requires DB access", skipped=True)
    else:
        leak = sql("SELECT count(*) n FROM ew.fossil_encounters WHERE "
                   "namespace='prod' AND (encounter_id LIKE 'TESTFIX%%' OR "
                   "encounter_id LIKE 'SEAM%%' OR encounter_id LIKE 'SFEREAL%%')")
        prod = sql("SELECT count(*) n FROM ew.fossil_encounters WHERE namespace='prod'")
        evp = sql("SELECT count(*) n FROM ew.evidence_prod WHERE evidence_id=%s", (eid,))
        ns = sql("SELECT namespace FROM ew.object_namespace WHERE "
                 "object_type='evidence' AND object_id=%s", (eid,))
        gate("G_namespace_firewall",
             leak[0]["n"] == 0 and evp[0]["n"] == 0 and
             [r["namespace"] for r in ns] == ["test"],
             f"test/seam rows in prod fossil namespace: {leak[0]['n']}; prod "
             f"encounters still {prod[0]['n']}; seam evidence rows visible in "
             f"ew.evidence_prod: {evp[0]['n']} (must be 0); classification="
             f"{[r['namespace'] for r in ns]}")

    # --- G2: an unknown namespace is refused (a typo must not land in prod)
    typo = c.post("claims", {
        "text_canonical": "namespace typo control", "status": "OBSERVED",
        "source_wording": "namespace typo control", "packet_id": pid,
        "namespace": "tset"})
    gate("G2_unknown_namespace_refused", typo.status_code == 422,
         f"namespace='tset' -> HTTP {typo.status_code} {typo.text[:80]}")

    # --- H: independent read-back ------------------------------------------
    if a.no_sql:
        gate("H_independent_read_back", False, "requires DB access", skipped=True)
    else:
        row = sql("SELECT evidence_id, encounter_id, encounter_run_id, "
                  "encounter_run_key FROM ew.evidence WHERE evidence_id=%s", (eid,))
        ok = (len(row) == 1 and row[0]["encounter_id"] == enc["encounter_id"]
              and row[0]["encounter_run_id"] == enc["run_id"])
        gate("H_independent_read_back", ok,
             f"direct SQL (never through the writing function): {row}")

    # --- J: fresh-consumer contract check ----------------------------------
    need = {"sfe_entry_hash", "evidence_binding", "identifier_mapping",
            "write_outcomes", "required"}
    have = need.issubset(ct.keys())
    says_event = "events.entry_hash" in json.dumps(ct.get("sfe_entry_hash", {}))
    binds = "encounter_id" in json.dumps(ct.get("evidence_binding", {}))
    gate("J_contract_is_self_describing", have and says_event and binds,
         f"contract keys present={have}; defines entry_hash as events.entry_hash="
         f"{says_event}; documents the binding={binds}")

    scored = [r for r in R if not r.get("skipped")]
    out = {"ran_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "host": a.host, "machine": a.machine,
           "service": h, "n_scored": len(scored),
           "n_pass": sum(r["pass"] for r in scored),
           "skipped": [r["gate"] for r in R if r.get("skipped")],
           "all_pass": bool(scored) and all(r["pass"] for r in scored),
           "bound_evidence_id": eid,
           "fixture_encounter": enc["encounter_id"],
           "fixture_run": enc["run_id"],
           "real_sfe_encounter": (real_enc or {}).get("encounter_id"),
           "gates": R}
    (HERE / "integration" / "seam_results.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "gates"}, indent=1))
    return 0 if out["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
