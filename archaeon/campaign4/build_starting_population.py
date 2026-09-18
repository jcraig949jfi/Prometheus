"""Declare the EXACT Campaign 4 starting organisms (launch gate G5, Archaeon's half).

    python -m archaeon.campaign4.build_starting_population

The directive: "Campaign population manifests and structural descriptors exist for the exact
Campaign-4 starting organisms. No organism of unknown ancestry enters an experimental arm."

This file is the declaration. Every organism carries:

  organism_id           content address of the manifest (hash_obj)
  manifest              verbatim
  ancestry              how it came to exist, sufficient to RE-DERIVE it, never "evolved"
  structural_descriptor Archaeon's own genome summary (instruction count, opcode classes,
                        persistence, register/tape configuration)
  class                 the structural stratum it represents

C4-01 asks for parents "spanning the existing structural population", so four strata are
declared rather than one:

  gen0_random     unevolved draws from the frozen foundry; ancestry = (foundry recipe, seed,
                  index). The structural floor: no selection has touched them.
  w0_solver       single-cell solvers; ancestry = (harvest procedure, cell seed, generation)
  delay_general   the delay-invariant readers; ancestry = (experiment, attempt, arm, seed)
  shelf           the one-value memories; ancestry = (experiment, attempt, arm, seed)

minted_by_proteus stays false until Proteus mints population_manifest.v1 over this exact set.
The launch gate reads that flag and refuses while it is false, so this declaration cannot pass
itself.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

from proteus.foundry import generate as G
from proteus.foundry.identity import hash_obj, RUNTIME_HASH
from proteus.foundry.grammar import GRAMMAR_HASH, GRAMMAR_VERSION
from proteus.foundry.affordances import AFFORDANCE_HASH

from archaeon.wse.telemetry import genome_summary
from archaeon.campaign2.c2base import FOUNDRY_C2
from archaeon.campaign4.c4base import CAMPAIGN_SEED

REPO = Path(__file__).resolve().parents[2]
C4 = REPO / "archaeon" / "campaign4"
OUT = C4 / "STARTING_POPULATION.json"
SPECIMENS = C4 / "SPECIMENS_FOR_PROTEUS.json"
N_GEN0 = 12


def entry(manifest: dict, klass: str, ancestry: dict) -> dict:
    return {"organism_id": hash_obj(manifest), "class": klass, "manifest": manifest,
            "ancestry": ancestry, "structural_descriptor": genome_summary(manifest)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-gen0", type=int, default=N_GEN0)
    a = ap.parse_args(argv)
    t0 = time.time()
    orgs = []

    # ---- stratum 1: unevolved draws from the frozen foundry (the structural floor)
    fm = dict(FOUNDRY_C2)
    fm["seed"] = CAMPAIGN_SEED
    fm["n"] = a.n_gen0
    for i, o in enumerate(G.generate(fm)):
        orgs.append(entry(o["manifest"], "gen0_random",
                          {"kind": "foundry_draw", "foundry_recipe": {k: v for k, v in fm.items() if k != "n"},
                           "index": i, "campaign_seed": CAMPAIGN_SEED,
                           "rederive": "proteus.foundry.generate.generate(recipe)[index]"}))

    # ---- strata 2-4: the campaign-3 specimens, already provenance-carrying
    spec = json.loads(SPECIMENS.read_text(encoding="utf-8"))
    for klass in ("w0_solver", "delay_general", "shelf"):
        for s in spec["specimens"][klass]:
            orgs.append(entry(s["manifest"], klass, {"kind": "campaign3_specimen", **s["provenance"]}))

    # DEDUPLICATE by content address. 5 of the campaign-3 "shelf" specimens are literally the
    # SAME organism: C3-SFE-01's shelf arm was taken over by identical imported material in every
    # seed (C3-SFE-10 measured that takeover directly), so its final elites coincide. Counting
    # them as independent parents would inflate n and correlate the census outcomes. One entry
    # per distinct organism, with every provenance that produced it recorded as multiplicity.
    merged = {}
    for o in orgs:
        m = merged.get(o["organism_id"])
        if m is None:
            o["ancestries"] = [o.pop("ancestry")]
            o["multiplicity"] = 1
            merged[o["organism_id"]] = o
        else:
            m["ancestries"].append(o["ancestry"])
            m["multiplicity"] += 1
            if o["class"] != m["class"]:
                m.setdefault("also_in_classes", []).append(o["class"])
    dup_note = {oid: m["multiplicity"] for oid, m in merged.items() if m["multiplicity"] > 1}
    orgs = list(merged.values())
    ids = [o["organism_id"] for o in orgs]
    doc = {
        "_what_this_is": "The EXACT Campaign 4 starting organisms (launch gate G5). No organism of unknown ancestry.",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "generated_by": "Archaeon[m2-411504ab]",
        "campaign_seed": CAMPAIGN_SEED,
        "identity": {"foundry_profile_id": "pfp1:625bc70456ebfa20", "archaeon_regime_id": "instr1-16:6528b9dc",
                     "grammar_version": GRAMMAR_VERSION, "grammar_hash": GRAMMAR_HASH,
                     "affordance_hash": AFFORDANCE_HASH, "runtime_hash": RUNTIME_HASH},
        "strata": {k: sum(1 for o in orgs if o["class"] == k) for k in ("gen0_random", "w0_solver", "delay_general", "shelf")},
        "n_organisms": len(orgs),
        "n_distinct_organism_ids": len(set(ids)),
        "collapsed_duplicates": dup_note,
        "collapsed_duplicates_note": "organism_id -> how many campaign-3 provenances yielded that SAME organism; "
                                     "the shelf arm's takeover by identical imported material is why",
        "all_have_ancestry": all(o.get("ancestries") for o in orgs),
        "minted_by_proteus": False,
        "minted_by_proteus_note": "set true only when Proteus has minted population_manifest.v1 over THIS exact set "
                                  "(by the digest below). The launch gate refuses while it is false.",
        "organisms": orgs,
        "wall_s": round(time.time() - t0, 1),
    }
    # CANONICAL POPULATION DIGEST -- identity-definition repair, 2026-09-17.
    #
    # The first rule was "sha256 of the declaration file's raw bytes". That is NOT invariant to
    # checkout: this repo sets core.autocrlf=true, so Proteus's worktree read CRLF where this one
    # writes LF, and the two seats computed different digests for IDENTICAL content
    # (a3f9816f vs 3c2ebfd9). The population content was never in dispute; the identity rule was.
    #
    # The digest is now taken over a canonical semantic representation, excluding the keys that
    # change on every regeneration without changing the population (generated_at, wall_s) and the
    # digest fields themselves. No platform, checkout setting, indentation or key order can move
    # it, and any seat reproduces it in one line.
    VOLATILE = ("generated_at", "wall_s", "population_digest", "population_digest_rule",
                "superseded_raw_byte_digests")
    RULE = ("population_digest = 'sha256:' + sha256( json.dumps(D, sort_keys=True, "
            "separators=(',',':'), ensure_ascii=False).encode('utf-8') ).hexdigest() where D is "
            "this object WITHOUT the keys %s. Invariant to line endings, indentation, key order "
            "and regeneration time. A raw-byte digest of this file is NOT an identity of the "
            "population." % (list(VOLATILE),))
    D = {k: v for k, v in doc.items() if k not in VOLATILE}
    canon = "sha256:" + hashlib.sha256(
        json.dumps(D, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
    doc["population_digest"] = canon
    doc["population_digest_rule"] = RULE
    doc["superseded_raw_byte_digests"] = {
        "lf_worktree": "sha256:3c2ebfd9de7bd14409bda6a1417ca9ebc8fdc1521eea6301450863f0df9199b1",
        "crlf_worktree": "sha256:a3f9816fada5a5edde6ac1d56100df078944e50f30c53b6c52160026c06dd6a4",
        "proteus_minted_over": "sha256:a3f9816fada5a5edde6ac1d56100df078944e50f30c53b6c52160026c06dd6a4",
        "note": "same 57-organism content, two checkouts. Preserved as evidence of the "
                "identity-definition defect that this canonical rule repairs.",
    }
    OUT.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
    print("population_digest (canonical, checkout-invariant):", canon)
    print(json.dumps({k: doc[k] for k in ("campaign_seed", "strata", "n_organisms", "n_distinct_organism_ids",
                                          "collapsed_duplicates", "all_have_ancestry", "minted_by_proteus", "wall_s")},
                     indent=1, sort_keys=True))
    print("written:", OUT, "\nsha256:", digest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
