#!/usr/bin/env python
"""INDEPENDENT READ-BACK. Input: ONE PEW evidence_id (argv[1]). No other
integration state is read. Reconstructs the full chain from the PEW
provenance endpoint, then verifies every recovered identity against the
SOURCE systems: the Proteus registry (local, authoritative) and the live
SFE engine. Every join is typed; nothing is guessed."""

import hashlib
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, r"D:\Prometheus")
sys.path.insert(0, r"D:\Prometheus\SerendipityFoundry\SerendipityFoundryClient")
from proteus.integration import registry as R                  # noqa: E402
from proteus.foundry.identity import canonical_json            # noqa: E402
from sfclient.client import EngineClient                       # noqa: E402

PEW = "http://192.168.1.202:8377/api/v1"
SFE = "https://192.168.1.202:8811"
CA = (r"D:\Prometheus\SerendipityFoundry\SerendipityFoundryClient"
      r"\config\m1.crt")


def pew_get(path):
    tok = open(r"C:\ZeusD-var\harmonia\pew_token.txt").read().strip()
    r = urllib.request.Request(PEW + path, headers={
        "Authorization": f"Bearer {tok}",
        "X-Prometheus-Machine": "M2", "X-Prometheus-Agent": "harmonia"})
    return json.loads(urllib.request.urlopen(r, timeout=30).read())


def main():
    evidence_id = sys.argv[1]
    v = {}                                  # verification ledger

    # ---- 1. the whole chain from ONE call ----------------------------
    prov = pew_get(f"/provenance/evidence/{evidence_id}")
    fe = prov["fossil_encounter"]
    sfe_ids = prov["sfe"]
    organisms = prov["proteus"]["organism_ids"]
    enc_id = fe["encounter_id"]
    run_id = fe["run_id"]
    world_id = sfe_ids["world_id"]
    event_id = sfe_ids["event_id"]
    entry_hash = sfe_ids["entry_hash"]
    event_seq = int(sfe_ids["event_seq"])
    oid = organisms[0]
    v["chain_recovered"] = dict(evidence_id=evidence_id,
                                encounter_id=enc_id, run_id=run_id,
                                world_id=world_id, players=organisms,
                                sfe_event_id=event_id,
                                sfe_entry_hash=entry_hash,
                                sfe_event_seq=event_seq)
    print("recovered chain:", json.dumps(v["chain_recovered"], indent=1))

    # ---- 2. verify against PROTEUS (canonical frozen registry) -------
    reg = R.load_default()
    entry = R.get_entry(reg, oid)           # raises if absent
    man = R.get_manifest(reg, oid)
    cj = canonical_json(man)
    cbytes = cj.encode() if isinstance(cj, str) else cj
    v["proteus_registry_contains_player"] = True
    v["proteus_manifest_rehashes_to_organism_id"] = (
        hashlib.sha256(cbytes).hexdigest() == oid)
    v["proteus_phenotype_still"] = entry["extrinsic"]["phenotype"]

    # ---- 3. verify against SFE (live reads) --------------------------
    tok = open(r"C:\ZeusD-var\harmonia\sfe_token.txt").read().strip()
    c = EngineClient(SFE, token=tok, cafile=CA, timeout=60.0)
    w = c.get_world(world_id)               # raises 404 if absent
    v["sfe_world_exists"] = w.get("world_id") == world_id
    evs = c.events(world_id, limit=200)
    evs = evs["events"] if isinstance(evs, dict) else evs
    match = [e for e in evs if e["event_id"] == event_id]
    v["sfe_event_exists"] = len(match) == 1
    if match:
        e = match[0]
        v["sfe_entry_hash_matches"] = e["entry_hash"] == entry_hash
        v["sfe_event_seq_matches"] = int(e["event_seq"]) == event_seq
        v["sfe_event_type"] = e["event_type"]
    # recover the artifact from the world's own ledger (typed join:
    # ARTIFACT_CREATED event whose blob_hash == sha256:organism_id)
    # ARTIFACT_CREATED events carry the blob hash as a bare string in
    # `artifacts` and the world-scoped envelope id in `refs.artifact_id`
    aid, ablob = None, None
    for e in evs:
        if e["event_type"] == "ARTIFACT_CREATED" and \
                "sha256:" + oid in (e.get("artifacts") or []):
            aid = (e.get("refs") or {}).get("artifact_id")
            ablob = "sha256:" + oid
            break
    v["sfe_artifact_recovered_from_ledger"] = bool(aid)
    if aid:
        content = c.artifact_bytes(world_id, aid)
        v["sfe_artifact_bytes_hash_to_organism_id"] = (
            hashlib.sha256(content).hexdigest() == oid)
        v["sfe_artifact_bytes_equal_registry_manifest"] = (
            content == cbytes)
        v["sfe_artifact_id"] = aid
        v["sfe_blob_hash"] = ablob

    checks = {k: val for k, val in v.items()
              if isinstance(val, bool)}
    ok = all(checks.values())
    v["READBACK_VERDICT"] = ("CHAIN_FULLY_RECONSTRUCTED_AND_VERIFIED"
                             if ok else "CHAIN_BROKEN")
    json.dump(v, open(Path(__file__).parent / "readback_result.json",
                      "w"), indent=1, default=str)
    print(json.dumps(checks, indent=1))
    print("VERDICT:", v["READBACK_VERDICT"])


if __name__ == "__main__":
    main()
