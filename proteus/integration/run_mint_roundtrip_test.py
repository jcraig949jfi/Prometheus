"""PROTEUS-36: test-namespace rehearsal of the fossil_players mint route (Mnemosyne #292, contract
evidence_wiki/docs/PROTEUS_MINT_WRITE_CONTRACT.md).

One rule-table child is derived through Herakles's operator (herakles.evca.derive), minted with
proteus.eval.rule_table_mint into a SCRATCH ledger (never proteus/mint/RULE_TABLE_MINTS.jsonl,
which holds real mints only), registered through Mnemosyne's route as agent Proteus in namespace
"test", read back by player_id, and compared column by column against the stated mapping. Then:
the identical registration again (must be duplicate_identical), and a DIFFERING re-registration
(must be refused 409; nothing overwritten). Result: proteus/integration/RESULT_MINT_ROUNDTRIP_TEST.json.

This is a rehearsal. No prod row is written; a prod mint waits for a real derivation request.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from proteus.eval import rule_table_mint as M  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "RESULT_MINT_ROUNDTRIP_TEST.json")
PARENT_HEX = "005f005f005f005f005fff5f005fff5f"   # the fixture parent of test_rule_table_mint.py
NAMESPACE = "test"

# mint record field -> fossil_players column (contract, "The mapping")
MAPPING = {
    "player_id": "player_id",
    "organism_ref": "genome_hash",
    "parent_player": "parent_player",
    "mate_player": "mate_player",
    "mutation_ref": "mutation_ref",
    "family": "family",
    "representation_version": "representation_version",
    "semantic_version": "semantic_version",
}


def row_for(rec: dict) -> dict:
    fields = {MAPPING[k]: rec[k] for k in MAPPING if k != "player_id"}
    fields["producer"] = {
        "component": "proteus.rule_table_mint", "version": "v1", "mint_id": rec["mint_id"],
        "operator": rec["operator"], "params": rec["operator_params"],
        "verified": rec["verified_by_semantic_owner"], "rehearsal": True,
    }
    fields["namespace"] = NAMESPACE
    return fields


def main() -> int:
    from herakles.evca import derive as HD
    from ew.client import EvidenceWiki

    os.environ.setdefault("PROMETHEUS_MACHINE", "M2")
    os.environ.setdefault("EW_SERVICE_URL", "http://127.0.0.1:8377")

    # 1. a child that CHANGES an entry (an edit to the current value is an identity derivation)
    cur = int(HD.decode_table(PARENT_HEX)[11])
    derivation = HD.derive_edit(PARENT_HEX, [(11, 1 - cur)])

    # 2. mint into a scratch ledger, never the real one
    with tempfile.TemporaryDirectory() as td:
        ledger = os.path.join(td, "SCRATCH_MINTS.jsonl")
        rec = M.append_mint(derivation, ledger)
        chain_ok = M.verify_ledger(ledger)
    assert rec["mint_id"] == M._mint_id(rec)
    fields = row_for(rec)

    result = {
        "schema_version": "proteus.mint_roundtrip_rehearsal.v1",
        "namespace": NAMESPACE, "service": os.environ["EW_SERVICE_URL"],
        "mint_record": rec, "ledger": "SCRATCH (temporary directory); proteus/mint/RULE_TABLE_MINTS.jsonl untouched",
        "ledger_chain_verified": bool(chain_ok),
        "steps": [], "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    ew = EvidenceWiki(agent="Proteus")

    # 3. register (namespace test)
    t0 = time.time()
    posted = ew.register_fossil_player(rec["player_id"], **fields)
    result["steps"].append({"step": "register", "ms": round(1000 * (time.time() - t0)), "response": posted})

    # 4. read back, compare every mapped column + producer.mint_id
    got = ew.get_fossil_player(rec["player_id"])
    mismatches = {}
    for k, col in MAPPING.items():
        if got.get(col) != rec[k]:
            mismatches[col] = {"sent": rec[k], "stored": got.get(col)}
    if (got.get("producer") or {}).get("mint_id") != rec["mint_id"]:
        mismatches["producer.mint_id"] = {"sent": rec["mint_id"], "stored": (got.get("producer") or {}).get("mint_id")}
    if got.get("namespace") != NAMESPACE:
        mismatches["namespace"] = {"sent": NAMESPACE, "stored": got.get("namespace")}
    result["steps"].append({"step": "read_back", "row": got, "mismatches": mismatches})

    # 5. identical registration again -> duplicate_identical
    again = ew.register_fossil_player(rec["player_id"], **fields)
    result["steps"].append({"step": "register_identical_again", "response": again})

    # 6. differing re-registration -> 409, nothing overwritten (the cheat)
    differing = dict(fields, mutation_ref="sha256:" + "f" * 64)
    try:
        ew.register_fossil_player(rec["player_id"], **differing)
        refused = None
    except ValueError as e:
        refused = str(e)
    after = ew.get_fossil_player(rec["player_id"])
    result["steps"].append({"step": "register_differing", "refused": refused,
                            "row_unchanged": after.get("mutation_ref") == rec["mutation_ref"]})

    ok = (not mismatches and refused is not None and "409" in refused
          and after.get("mutation_ref") == rec["mutation_ref"]
          and str(again).find("duplicate") >= 0)
    result["verdict"] = "ROUNDTRIP_OK" if ok else "ROUNDTRIP_FAILED"
    result["player_id"], result["mint_id"] = rec["player_id"], rec["mint_id"]
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, indent=1, sort_keys=True)
        f.write("\n")
    print(OUT)
    print("verdict", result["verdict"], "| player_id", rec["player_id"], "| mint_id", rec["mint_id"][:23])
    print("register:", posted, "| again:", again, "| differing refused:", (refused or "")[:80])
    print("mismatches:", mismatches)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
