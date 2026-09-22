"""Mint proteus.population_manifest.v1 over Archaeon's EXACT Campaign 4 starting population.

Input (Archaeon's, read-only, never edited by Proteus): archaeon/campaign4/STARTING_POPULATION.json
-- 57 distinct organisms in four strata (gen0_random 12 foundry draws under the C4 recipe seed
20260921; delay_general 11, shelf 19, w0_solver 15 campaign-3 specimens), each with ancestries.
Output: proteus/eval/C4_STARTING_POPULATION_MANIFEST.json, bound to the declaration by its CANONICAL
digest (Archaeon's published population_digest_rule: sorted compact JSON minus volatile keys), which
is line-ending invariant; the raw-byte digest of this checkout is kept beside it as evidence of the
CRLF/LF defect (#389/#400) and is not what the gate binds.

What the mint checks (all refused on failure): every organism_id hashes from its manifest under
the frozen runtime; no duplicates; the 12 gen0 draws are exactly reproduced by the recipe
(generate(seed 20260921)[index]); the declaration's identity block equals the live runtime /
grammar / affordance identities and the catalog profile pfp1:625bc70456ebfa20; composition sums
to 57. The 45 campaign-3 specimens are IMPORTS relative to the recipe and are listed with their
ancestries verbatim. Nothing is scored.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from proteus.eval import foundry_profile as FP  # noqa: E402
from proteus.eval import population_manifest as PM  # noqa: E402
from proteus.foundry import affordances as A  # noqa: E402
from proteus.foundry import grammar as G  # noqa: E402
from proteus.foundry.generate import generate  # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH, hash_obj  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DECL = os.path.join(ROOT, "archaeon", "campaign4", "STARTING_POPULATION.json")
OUT = os.path.join(ROOT, "proteus", "eval", "C4_STARTING_POPULATION_MANIFEST.json")
GEN0_CLASS = "gen0_random"


CANONICAL_EXCLUDE = ("generated_at", "wall_s", "population_digest", "population_digest_rule",
                     "superseded_raw_byte_digests")


def canonical_digest(decl: dict) -> str:
    """Archaeon's published rule (STARTING_POPULATION.json population_digest_rule): sha256 over
    json.dumps(D, sort_keys=True, separators=(',',':'), ensure_ascii=False) with the volatile keys
    removed. Line-ending invariant, unlike the raw-byte digest (which differs between a CRLF and an
    LF checkout of the same content -- the defect #389/#400 report)."""
    D = {k: v for k, v in decl.items() if k not in CANONICAL_EXCLUDE}
    return "sha256:" + hashlib.sha256(
        json.dumps(D, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def load_declaration(path=DECL):
    raw = open(path, "rb").read()
    decl = json.loads(raw.decode("utf-8"))
    canon = canonical_digest(decl)
    if decl.get("population_digest") != canon:
        raise ValueError("declaration's published population_digest does not recompute under its own rule: %s vs %s"
                         % (decl.get("population_digest"), canon))
    return decl, "sha256:" + hashlib.sha256(raw).hexdigest()


def recipe_of(decl: dict) -> dict:
    """The one foundry recipe behind every gen0 draw; n = max index + 1 (organism i depends on
    the seed and i only, never on n)."""
    recipes, max_index = set(), -1
    for o in decl["organisms"]:
        if o["class"] != GEN0_CLASS:
            continue
        for a in o["ancestries"]:
            if a["kind"] != "foundry_draw":
                raise ValueError("gen0_random organism with a non-draw ancestry")
            recipes.add(json.dumps(a["foundry_recipe"], sort_keys=True))
            max_index = max(max_index, int(a["index"]))
    if len(recipes) != 1:
        raise ValueError("expected exactly one gen0 recipe, found %d" % len(recipes))
    fm = json.loads(recipes.pop())
    fm["n"] = max_index + 1
    return fm


def check_identity(decl: dict, fm: dict) -> dict:
    ident = decl["identity"]
    prof = FP.build_profile(fm)
    expect = {"runtime_hash": RUNTIME_HASH, "grammar_hash": G.GRAMMAR_HASH, "grammar_version": G.GRAMMAR_VERSION,
              "affordance_hash": A.AFFORDANCE_HASH, "foundry_profile_id": prof["profile_id"],
              "archaeon_regime_id": prof["archaeon_regime_id"]}
    bad = {k: (ident.get(k), v) for k, v in expect.items() if ident.get(k) != v}
    if bad:
        raise ValueError("declaration identity disagrees with the live substrate: %s" % bad)
    return prof


def check_gen0_draws(decl: dict, fm: dict) -> int:
    pop = generate(fm)
    by_index = {i: o["organism_id"] for i, o in enumerate(pop)}
    n = 0
    for o in decl["organisms"]:
        if o["class"] != GEN0_CLASS:
            continue
        for a in o["ancestries"]:
            if by_index.get(int(a["index"])) != o["organism_id"]:
                raise ValueError("gen0 draw index %s does not regenerate to %s" % (a["index"], o["organism_id"][:12]))
        n += 1
    return n


def members_of(decl: dict) -> tuple:
    members, sources = [], {}
    for o in decl["organisms"]:
        m = o["manifest"]
        if hash_obj(m) != o["organism_id"]:
            raise ValueError("organism_id does not hash from its manifest: " + o["organism_id"][:12])
        if o["class"] == GEN0_CLASS:
            origins = ["gen0"]
        else:
            origins = ["campaign3_specimen", o["class"]]
            sources[o["organism_id"]] = {"multiplicity": o["multiplicity"], "ancestries": o["ancestries"]}
        members.append({"organism_id": o["organism_id"], "manifest": m, "origins": origins})
    return members, sources


def main() -> int:
    from proteus.workspace import assert_not_canonical
    assert_not_canonical("run emit_c4_starting_population.py")
    decl, digest = load_declaration()
    canon = canonical_digest(decl)
    fm = recipe_of(decl)
    prof = check_identity(decl, fm)
    n_gen0 = check_gen0_draws(decl, fm)
    members, sources = members_of(decl)
    pm = PM.build_population_manifest(
        members, foundry_manifest=fm,
        gen0_provenance={"fill": "proteus.foundry.generate.generate", "campaign_seed": decl["campaign_seed"],
                         "recipe_seed": fm["seed"], "n": fm["n"], "declared_by": decl["generated_by"],
                         "declaration": "archaeon/campaign4/STARTING_POPULATION.json",
                         "declaration_canonical_digest": canon, "collapsed_duplicates": decl["collapsed_duplicates"]},
        imported_sources=sources, selection_criteria="NONE", sealed_at=decl["generated_at"],
        population_label="campaign4 starting population (Archaeon declaration %s)" % canon[7:23])
    doc = {
        "schema_version": "proteus.c4_starting_population_mint.v1",
        "minted_by": "Proteus[m2-7d051790]",
        "declaration": "archaeon/campaign4/STARTING_POPULATION.json",
        "declaration_digest": digest,
        "declaration_digest_note": "raw bytes of this checkout; NOT checkout-invariant (CRLF vs LF); superseded for the gate by declaration_canonical_digest",
        "declaration_canonical_digest": canon,
        "declaration_canonical_digest_rule": decl["population_digest_rule"],
        "declaration_generated_at": decl["generated_at"],
        "foundry_profile": prof["profile_id"],
        "archaeon_regime_id": prof["archaeon_regime_id"],
        "checks": {"organism_ids_hash_from_manifests": len(members), "gen0_draws_regenerated": n_gen0,
                   "identity_block_matches_live_substrate": True, "distinct": len({m["organism_id"] for m in members})},
        "population_manifest": pm,
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
        f.write("\n")
    print(OUT)
    print("declaration_digest (raw bytes)", digest)
    print("declaration_canonical_digest", canonical_digest(decl), "== published:", canonical_digest(decl) == decl["population_digest"])
    print("population_manifest_id", pm["population_manifest_id"], "| manifest_hash", pm["manifest_hash"])
    print("profile", pm["foundry_profile"], "| count", pm["count"], "| composition", pm["lineage_composition"])
    print("gen0 draws regenerated:", n_gen0, "| imports listed:", len(pm["imported"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
