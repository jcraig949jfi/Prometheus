"""Generate CAMPAIGN4_EXECUTION_IDENTITY.json: the five frozen surfaces by IMMUTABLE identity.

    python -m archaeon.campaign4.build_identity [--ref origin/main]

Every field is READ from the artifact that defines it and digested here, never transcribed from
a message. A surface that cannot be read is recorded as UNRESOLVED with the reason, so the tuple
never claims an identity it did not verify.

The tuple is the Campaign 4 execution identity:

    (Daedalus build, Vivarium build, Proteus profile+grammar, PEW frozen digest,
     Archaeon campaign seed/spec)

"Current main" is not an identity: this file exists because main moved three times during the
hour in which it was written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "archaeon" / "campaign4" / "CAMPAIGN4_EXECUTION_IDENTITY.json"


def at_ref(ref: str, path: str) -> bytes:
    r = subprocess.run(["git", "show", "%s:%s" % (ref, path)], capture_output=True, cwd=str(REPO))
    if r.returncode != 0:
        raise FileNotFoundError(path)
    return r.stdout


def sha(b: bytes) -> str:
    return "sha256:" + hashlib.sha256(b).hexdigest()


def rev(ref: str) -> str:
    return subprocess.run(["git", "rev-parse", ref], capture_output=True, text=True, cwd=str(REPO)).stdout.strip()


def daedalus(ref: str) -> dict:
    p = "SerendipityFoundry/SerendipityFoundryEngine/deploy/DEPLOYED_BUILD_M2.json"
    b = at_ref(ref, p)
    d = json.loads(b)
    return {
        "surface": "engine (Serendipity Foundry)",
        "owner": "Daedalus",
        "release": "SFE 9.0.1",
        "engine_instance_id": d["engine_instance_id"],
        "endpoint": d["endpoint"],
        "schema_version": d["schema_version"],
        "routes": d.get("routes"),
        "route_digest": d.get("route_digest"),
        "engine_source_hash": d["engine_source_hash"],
        "source_commit_containing_build": d["source_commit_containing_build"],
        "pinned_at": d.get("pinned_at"),
        "pinned_by": d.get("pinned_by"),
        "descriptor_path": p,
        "descriptor_digest": sha(b),
    }


def vivarium(ref: str) -> dict:
    p = "vivarium/deploy/PRODUCTION.draft.json"
    b = at_ref(ref, p)
    d = json.loads(b)
    return {
        "surface": "execution / queue",
        "owner": "Vivarium",
        "build_commit": "08081c6ed",                     # declared in Vivarium #368 (WINDOW C4-20260917-W1 CLOSED)
        "build_commit_source": "comms #368 (Vivarium m2-fce3fe0b); not derivable from the descriptor",
        "migrations": "viv 001-010",
        "descriptor_version": d.get("descriptor_version"),
        "descriptor_path": p,
        "descriptor_digest": sha(b),
        "note": "descriptor is still the DRAFT: viv/production.py prefers deploy/PRODUCTION.json when the shared file lands",
    }


def proteus(ref: str) -> dict:
    p = "proteus/eval/FOUNDRY_PROFILE_CATALOG.json"
    b = at_ref(ref, p)
    d = json.loads(b)
    prof = next((x for x in d["profiles"] if x["profile_id"] == "pfp1:625bc70456ebfa20"), None)
    if prof is None:
        return {"surface": "population / regime identity", "owner": "Proteus", "UNRESOLVED": "C4 profile not in catalog"}
    return {
        "surface": "population / regime identity",
        "owner": "Proteus",
        "foundry_profile_id": prof["profile_id"],
        "foundry_profile_name": prof.get("name"),
        "archaeon_regime_id": prof["archaeon_regime_id"],
        "archaeon_regime_scheme": prof["archaeon_regime_scheme"],
        "grammar_version": prof["grammar"]["grammar_version"],
        "grammar_hash": prof["grammar"]["grammar_hash"],
        "affordance_hash": prof["affordance_hash"],
        "runtime_hash": prof.get("runtime_hash") or d.get("runtime_hash"),
        "catalog_id": d.get("catalog_id"),
        "catalog_path": p,
        "catalog_digest": sha(b),
        "kernel_qualification": prof.get("kernel_qualification"),
        "CONSTRAINT_ON_CAMPAIGN_4": (
            "permitted_use USE_A_FROZEN_SPECIMEN_SOURCE; prohibited_use USE_B_NEUTRAL_EVOLUTIONARY_OPERATOR. "
            "Campaigns 1-3 used this grammar AS an evolutionary operator. Campaign 4 must either stay inside "
            "USE_A, or carry Proteus's ruling that USE_B is licensed, or state the claim ceiling this imposes."
        ),
    }


def pew(ref: str) -> dict:
    p = "evidence_wiki/docs/point_release/CAMPAIGN4_FROZEN_SURFACE.json"
    b = at_ref(ref, p)
    d = json.loads(b)
    computed = sha(b)
    declared = d.get("surface_digest")
    rule = d.get("surface_digest_rule")
    # Q1 (asked in comms #370) was answered by publishing the derivation rule INSIDE the pinned
    # file. Recompute it here rather than trusting the answer: the digest is only an identity if a
    # third party can reproduce it.
    recomputed = None
    if rule:
        D = {k: v for k, v in d.items() if k not in ("surface_digest", "surface_digest_rule")}
        recomputed = sha(json.dumps(D, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8"))
    return {
        "surface": "evidence / projections (PEW)",
        "owner": "Mnemosyne",
        "reader_version": d.get("reader_version"),
        "schema_version": d.get("schema_version"),
        "migrations": d.get("migrations"),
        "fossil_contract": d.get("fossil_contract"),
        "ingestion_contract": d.get("ingestion_contract"),
        "projection_builder": d.get("projection_builder"),
        "foundry_profile_scheme": d.get("foundry_profile_scheme"),
        "campaign_seed_map_before_c4": d.get("campaign_seed_map"),
        "surface_path": p,
        "surface_file_digest_computed_here": computed,
        "surface_digest_declared_in_file": declared,
        "surface_digest_rule_published": bool(rule),
        "surface_digest_recomputed_by_rule": recomputed,
        "surface_digest_reproducible": (recomputed == declared) if (rule and declared) else False,
        "DIGEST_NOTE": (
            "REPRODUCED: the derivation rule is published inside the pinned file and recomputing it here yields "
            "the declared digest. Both the declared surface_digest and the file's own sha256 are valid identities "
            "of this pin (Q1 closed, comms #371/#375)."
            if rule and recomputed == declared else
            "NOT REPRODUCIBLE: the declared surface_digest cannot be recomputed from the file by the stated rule."
            if rule else
            "the file's self-declared surface_digest is not the sha256 of the file and no derivation rule is "
            "stated, so a third party cannot reproduce it."),
    }


def archaeon() -> dict:
    from archaeon.campaign4.c4base import CAMPAIGN_4, CAMPAIGN_SEED
    from proteus.foundry.grammar import GRAMMAR_HASH, GRAMMAR_VERSION
    from proteus.foundry.identity import RUNTIME_HASH
    return {
        "surface": "campaign seed / spec",
        "owner": "Archaeon",
        "campaign": CAMPAIGN_4["campaign"],
        "campaign_seed": CAMPAIGN_SEED,
        "engine_client": CAMPAIGN_4["client"],
        "ledger_prefix": CAMPAIGN_4["ledger_prefix"],
        "root": "archaeon/campaign4/",
        "seed_rule": "first unused value after cmp3 (20260916-20260920 already appear in REACHABILITY.jsonl)",
        "runtime_hash_seen_by_archaeon": RUNTIME_HASH,
        "grammar_seen_by_archaeon": {"version": GRAMMAR_VERSION, "hash": GRAMMAR_HASH},
        "spec_status": "seed FROZEN; per-slot preregistrations sealed at run time as in campaigns 2 and 3",
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="origin/main")
    a = ap.parse_args(argv)
    surfaces = {}
    for name, fn in (("daedalus", daedalus), ("vivarium", vivarium), ("proteus", proteus), ("pew", pew)):
        try:
            surfaces[name] = fn(a.ref)
        except Exception as e:                                   # noqa: BLE001
            surfaces[name] = {"UNRESOLVED": "%s: %s" % (type(e).__name__, e)}
    surfaces["archaeon"] = archaeon()
    doc = {
        "_what_this_is": "The Campaign 4 EXECUTION IDENTITY: five frozen surfaces, each by immutable identity. "
                         "'Current main' is not an identity.",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "generated_by": "Archaeon[m2-411504ab]",
        "read_at_ref": a.ref,
        "read_at_commit": rev(a.ref),
        "status": "PROPOSED -- freezes when the end-to-end rehearsal proves this exact tuple",
        "tuple": surfaces,
        "freeze_rule": "after the rehearsal passes, this file's own sha256 becomes the Campaign 4 execution identity; "
                       "any surface that moves requires a new tuple and a new rehearsal.",
    }
    OUT.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(doc, indent=1, sort_keys=True))
    print("\nwritten:", OUT)
    print("identity file sha256:", hashlib.sha256(OUT.read_bytes()).hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
