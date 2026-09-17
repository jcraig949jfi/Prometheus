"""Point-release live check against the deployed service (order s17):
producer-event inbox semantics, campaign observation queries, projection
registry and rows, release identity. Run from a task worktree AFTER
migration 014, restart and Campaign 3 ingestion.

    python integration/campaign_release_check.py --machine M2

Gates (each named for the order's list):
    R0  /api/v1/release carries migration 014, schema 5, canonical db id
    E1  event accepted (new stream)                       -> accepted, gap false
    E2  duplicate delivery (same event again)             -> duplicate, nothing new
    E3  same seq, different payload                       -> checkpoint_mismatch + conflict row
    E4  seq skipped (3 after 1)                           -> accepted, gap true, checkpoint gap recorded
    E5  late seq (2 after 3)                              -> accepted, late true, checkpoint stays 3
    E6  malformed (extra field)                           -> 422, nothing stored
    E7  unregistered identity cannot post events          -> 401, nothing stored
    Q1  observations need a selector (400); bad stratum 422
    Q2  query by campaign / harness / attempt returns C3 rows
    Q3  query by stratum (jsonb containment) returns only that stratum
    Q4  UNKNOWN identities survive in the rows (never NULL-ed)
    P1  projections registry lists reach_level v1 and corridor_edge v1
        with definition, thresholds, owner, code identity, digest
    P2  projection rows: the pooled W2_K2 4-bit N200 G60 stratum reads
        0 SUMMIT / 0 confirmed summits at the pinned definition, as every
        campaign report says at that budget
    P3  a projection row cites evidence ids that resolve to observations
"""
import argparse
import json
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
R = []


def gate(name, ok, detail):
    R.append({"gate": name, "pass": bool(ok), "detail": detail})
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    return bool(ok)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8377)
    ap.add_argument("--machine", default="M2")
    a = ap.parse_args()
    cfg = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
    tok = cfg["machine_tokens"].get(a.machine) or cfg["auth_token"]
    base = f"http://{a.host}:{a.port}/api/v1"
    h = {"Authorization": f"Bearer {tok}", "X-Prometheus-Machine": a.machine, "X-Prometheus-Agent": "release-check"}
    get = lambda p, **kw: requests.get(f"{base}/{p}", headers=h, params=kw, timeout=60)
    post = lambda p, body: requests.post(f"{base}/{p}", headers=h, json=body, timeout=60)

    rel = get("release").json()
    gate("R0_release_identity", any(m["migration_id"] == "014" for m in rel.get("migrations_applied", []))
         and rel.get("schema_version_constant") == 5 and rel.get("db_system_id") == "7628127204585430828",
         f"schema={rel.get('schema_version_constant')} migrations={[m['migration_id'] for m in rel.get('migrations_applied', [])]} db={rel.get('db_system_id')} routes={len(rel.get('routes', []))}")

    stream = f"rc-{int(time.time())}"
    ev = lambda seq, x, eid=None: {"producer": "release-check", "stream": stream, "seq": seq,
                                   "event_id": eid or f"{stream}-{seq}", "kind": "CAPABILITY_MEASURED",
                                   "logical_time": seq, "actor": "release-check",
                                   "payload": {"x": x}, "envelope": {"campaign_id": "cmp-check"}}
    r1 = post("events", ev(1, 1)).json()["results"]
    gate("E1_accepted", r1["status"] == "accepted" and r1["gap"] is False, json.dumps(r1))
    r2 = post("events", ev(1, 1)).json()["results"]
    gate("E2_duplicate_noop", r2["status"] == "duplicate", json.dumps(r2))
    r3 = post("events", ev(1, 999, eid=f"{stream}-1b")).json()["results"]
    conf = get("ingestion/conflicts", producer="release-check").json()
    gate("E3_checkpoint_mismatch_refused_and_recorded", r3["status"] == "checkpoint_mismatch"
         and any(c["stream"] == stream and c["seq"] == 1 for c in conf["conflicts"]), json.dumps(r3))
    r4 = post("events", ev(3, 3)).json()["results"]
    cps = {c["stream"]: c for c in get("ingestion/checkpoints", producer="release-check").json()["checkpoints"]}
    gate("E4_gap_visible", r4["status"] == "accepted" and r4["gap"] is True and cps[stream]["last_seq"] == 3
         and cps[stream]["gaps"] and cps[stream]["gaps"][0]["from"] == 2, json.dumps(r4) + " gaps=" + json.dumps(cps[stream]["gaps"]))
    r5 = post("events", ev(2, 2)).json()["results"]
    cps = {c["stream"]: c for c in get("ingestion/checkpoints", producer="release-check").json()["checkpoints"]}
    gate("E5_late_delivery_accepted_checkpoint_kept", r5["status"] == "accepted" and r5.get("late") is True
         and cps[stream]["last_seq"] == 3, json.dumps(r5))
    r6 = post("events", dict(ev(4, 4), extra="no"))
    evs = get("events", producer="release-check", stream=stream).json()
    gate("E6_malformed_422_nothing_stored", r6.status_code == 422 and evs["n"] == 3 and [e["seq"] for e in evs["events"]] == [1, 2, 3],
         f"{r6.status_code} stored_seqs={[e['seq'] for e in evs['events']]}")
    r7 = requests.post(f"{base}/events", headers={"Authorization": "Bearer not-a-registered-token",
                                                  "X-Prometheus-Machine": a.machine, "X-Prometheus-Agent": "nobody"},
                       json=ev(9, 9), timeout=30)
    evs2 = get("events", producer="release-check", stream=stream).json()
    gate("E7_unregistered_identity_cannot_post", r7.status_code == 401 and evs2["n"] == 3,
         f"{r7.status_code} stored={evs2['n']} (read-only scope refusal is tests/test_agent_identity.py cheat control)")

    q0 = get("campaign/observations")
    q0b = get("campaign/observations", stratum="{not json")
    gate("Q1_selector_required_and_stratum_validated", q0.status_code == 400 and q0b.status_code == 422, f"{q0.status_code} {q0b.status_code}")
    qc = get("campaign/observations", campaign_id="cmp3", kind="receipt", limit=100).json()
    qh = get("campaign/observations", harness_id="C3-SFE-03", kind="run").json()
    qa = get("campaign/observations", attempt_id="C3-SFE-03/a05", kind="generation", limit=2000).json()
    gate("Q2_query_by_campaign_harness_attempt", qc["n"] >= 10 and qh["n"] >= 12 and qa["n"] > 100,
         f"cmp3 receipts={qc['n']} C3-SFE-03 runs={qh['n']} a05 generations={qa['n']}")
    qs = get("campaign/observations", kind="reachability", stratum=json.dumps({"cell": "W2_K2", "budget_class": "N200G60E16", "row_kind": "baseline"}), limit=2000).json()
    gate("Q3_query_by_stratum", qs["n"] > 0 and all(o["cell"] == "W2_K2" and o["g_budget"] == 60 for o in qs["observations"]),
         f"n={qs['n']} all W2_K2 G60")
    qu = get("campaign/summary", campaign_id="cmp3").json()
    gate("Q4_unknown_survives", qu["unknown_identity_counts"].get("foundry_profile", 0) > 0 or qu["unknown_identity_counts"].get("engine_instance_id", 0) > 0,
         json.dumps(qu["unknown_identity_counts"]))

    pl = get("projections").json()
    names = {(p["projection_name"], p["projection_version"]): p for p in pl["projections"]}
    ok = all(k in names for k in (("reach_level", "v1"), ("corridor_edge", "v1")))
    p = names.get(("reach_level", "v1"), {})
    gate("P1_registry", ok and p.get("thresholds", {}).get("SUMMIT_MIN") == 0.9 and p.get("owner_seat") == "Archaeon"
         and "archaeon.wse.reachability@" in (p.get("source_code_identity") or "") and p.get("rebuild_digest"),
         f"projections={sorted(names)} owner={p.get('owner_seat')} code={str(p.get('source_code_identity'))[:60]}")
    pr = get("projections/reach_level/v1", row_key_prefix="pool:W2_K2|4|N200G60E16", limit=50).json()
    pools = [r for r in pr["rows"]]     # every campaign / row kind in this stratum
    tot = {"n": sum(r["payload"]["n"] for r in pools), "SHELF": sum(r["payload"]["levels"].get("SHELF", 0) for r in pools),
           "SUMMIT": sum(r["payload"]["levels"].get("SUMMIT", 0) for r in pools), "confirmed_summits": sum(r["payload"]["confirmed_summits"] for r in pools)}
    gate("P2_pooled_row_reads_like_the_report", tot["SUMMIT"] == 0 and tot["confirmed_summits"] == 0 and tot["n"] > 0,
         f"W2_K2 4-bit N200G60E16 pools={len(pools)} {json.dumps(tot)} (the reports' 0-summit reading at this budget; the producer's monotone budget lookup is not reproduced, so n differs from the report's 27)")
    row = pr["rows"][0] if pr["rows"] else None
    ev_ok = False
    if row and row["evidence_ids"]:
        oid = row["evidence_ids"][0]
        q = get("campaign/observations", kind="reachability", cell="W2_K2", limit=2000).json()
        ev_ok = any(o["observation_id"] == oid for o in q["observations"])
    gate("P3_projection_evidence_resolves", ev_ok, f"first evidence id of {row['row_key'] if row else None} resolves")

    ok = all(r["pass"] for r in R)
    out = {"all_pass": ok, "machine": a.machine, "service": base, "ran_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "release": {k: rel.get(k) for k in ("schema_version_constant", "ontology_registry_version", "fossil_contract",
                                                "reader_version", "ingestion_contract", "projection_builder",
                                                "projection_registry_digest", "route_digest", "db_system_id")},
           "gates": R}
    (HERE / "integration" / "campaign_release_results.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({"all_pass": ok, "n_gates": len(R)}))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
