#!/usr/bin/env python
"""PEW fossil-chain writer for the first integration, per
evidence_wiki/docs/HARMONIA_PEW_WRITE_CONTRACT.md (pew.fossil.v2).
namespace=test throughout. Also runs negative controls C/D/E.
Never treats HTTP 200 as persistence; the read-back script is the proof."""

import json
import urllib.error
import urllib.request
from pathlib import Path

BASE = "http://192.168.1.202:8377/api/v1"
OUT = Path(__file__).parent
TOK = open(r"C:\ZeusD-var\harmonia\pew_token.txt").read().strip()
HDR = {"Authorization": f"Bearer {TOK}",
       "X-Prometheus-Machine": "M2",
       "X-Prometheus-Agent": "harmonia",
       "content-type": "application/json"}


def req(method, path, body=None):
    r = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers=HDR, method=method)
    try:
        resp = urllib.request.urlopen(r, timeout=30)
        return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def main():
    rec = json.load(open(OUT / "integration_record.json"))
    oid = rec["organism_id"]
    wid = rec["world"]["world_id"]
    enc = rec["encounter"]
    run_id = rec["run"]["run_id"]
    anchor = rec["anchor"]
    sel = json.load(open(OUT / "adventurer_selection.json"))
    out = {}

    # Step 1 -- world anchor
    s, r = req("POST", "/fossil/worlds", {
        "world_id": wid, "sfe_world_id": wid,
        "seed_root": "424242",
        "sfe_head_hash": rec["world"]["head_hash_final"],
        "world_binding_id": wid,
        "namespace": "test",
        "producer": {"component": "harmonia.first_integration.adapter",
                     "version": "v0",
                     "engine_source_hash":
                         rec["engine"]["engine_source_hash"]}})
    out["world_anchor"] = (s, r)
    print("world anchor:", s, r.get("status", r))

    # Step 2 -- player anchor (player_id = Proteus organism_id)
    s, r = req("POST", "/fossil/players", {
        "player_id": oid,
        "genome_hash": "sha256:" + oid,
        "runtime_hash": "sha256:" + sel["identity"]["runtime_hash"],
        "lineage_id": sel["lineage_id"],
        "generation": sel["generation"],
        "namespace": "test",
        "producer": {"component": "proteus.foundry", "version": "v0"}})
    out["player_anchor"] = (s, r)
    print("player anchor:", s, r.get("status", r))

    # Step 3 -- the encounter (the EXECUTION)
    enc_body = {
        "encounter_id": enc["encounter_id"],
        "run_id": run_id,
        "sfe_event_id": anchor["sfe_event_id"],
        "sfe_entry_hash": anchor["sfe_entry_hash"],
        "sfe_event_seq": anchor["sfe_event_seq"],
        "sfe_world_id": wid, "world_id": wid,
        "players": [oid],
        "seed": str(enc["seed"]),
        "outcome": rec["observation"]["outcome"],
        "resources_used": {"ticks": 16,
                           "ops_total": rec["execution"]["ops_total"]},
        "namespace": "test",
        "producer": {"component": "harmonia.first_integration.adapter",
                     "version": "v0",
                     "runtime_hash": sel["identity"]["runtime_hash"],
                     "grammar_hash": sel["identity"]["grammar_hash"],
                     "affordance_hash":
                         sel["identity"]["affordance_hash"]}}
    s, r = req("POST", "/fossil/encounters", enc_body)
    out["fossil_encounter"] = (s, r)
    print("fossil encounter:", s, r.get("status", r))
    assert s == 200, f"encounter write failed: {r}"

    # Step 4 -- ordinary evidence bound to the encounter
    s, r = req("POST", "/packets", {
        "uri": "genesis/harmonia_a/first_integration/"
               "FIRST_INTEGRATION_OBSERVATION.md",
        "kind": "doc", "namespace": "test"})
    out["packet"] = (s, r)
    packet_id = r.get("packet_id") or r.get("id")
    print("packet:", s, packet_id)
    quote = ("Identity was preserved at every hop. No score was "
             "produced, no selection occurred, no mutation occurred, "
             "phenotype remains UNKNOWN.")
    s, r = req("POST", "/claims", {
        "text_canonical": "First Prometheus end-to-end specimen trace: "
                          f"organism {oid} traversed Proteus->SFE->"
                          "encounter->PEW with identity preserved",
        "source_wording": quote,
        "status": "OBSERVED", "packet_id": packet_id,
        "write_stage": "SOURCE_BOUND", "namespace": "test"})
    out["claim"] = (s, r)
    claim_id = r.get("claim_id") or r.get("id")
    print("claim:", s, claim_id)
    s, r = req("POST", "/evidence", {
        "packet_id": packet_id, "claim_id": claim_id,
        "source_quote": quote,
        "evidence_type": "OBSERVATIONAL_ANALYSIS",
        "write_stage": "SOURCE_BOUND",
        "namespace": "test",
        "encounter_id": enc["encounter_id"],
        "encounter_run_id": run_id})
    out["evidence"] = (s, r)
    evidence_id = r.get("evidence_id")
    print("evidence:", s, evidence_id)

    # ---- negative controls ------------------------------------------
    # C: unsupported extra field on fossil path -> 422
    bad = dict(enc_body); bad["frobnicate"] = 1
    bad["run_id"] = run_id + ":x"
    s, r = req("POST", "/fossil/encounters", bad)
    out["neg_C_extra_field"] = (s, str(r)[:120])
    print("neg C (extra field):", s)
    # D: evidence bound to nonexistent encounter -> 422, no row
    s, r = req("POST", "/evidence", {
        "packet_id": packet_id, "claim_id": claim_id,
        "source_quote": quote,
        "evidence_type": "OBSERVATIONAL_ANALYSIS",
        "write_stage": "SOURCE_BOUND", "namespace": "test",
        "encounter_id": "0" * 64, "encounter_run_id": "exp_x:wrk_x"})
    out["neg_D_unknown_encounter"] = (s, str(r)[:120])
    print("neg D (unknown encounter):", s)
    # E: materially differing reuse of frozen fossil identity -> 409
    diff = dict(enc_body); diff["outcome"] = "INCONCLUSIVE"
    s, r = req("POST", "/fossil/encounters", diff)
    out["neg_E_conflict"] = (s, str(r)[:120])
    print("neg E (conflict):", s)
    # idempotent identical retry -> duplicate_identical
    s, r = req("POST", "/fossil/encounters", enc_body)
    out["idempotent_retry"] = (s, r.get("status"))
    print("idempotent retry:", s, r.get("status"))

    out["evidence_id"] = evidence_id
    json.dump(out, open(OUT / "pew_write_results.json", "w"), indent=1,
              default=str)
    print("EVIDENCE_ID:", evidence_id)


if __name__ == "__main__":
    main()
