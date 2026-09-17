"""proteus.population_manifest.v1 -- the exact identity of a starting population.

Why (point release P2 / PROTEUS-30, repair order s3, 2026-09-17). Campaign 1's L-008/L-030
(harness-seeded fills replaced generation 0), campaign 2's L2-037/48 and campaign 3's C3-SFE-10
(any substituted material takes the population over) all turn on WHICH organisms a run started
from, and no field anywhere names that today: Vivarium's start bundle carries
`population: "UNKNOWN until Proteus defines it"`. This module defines it.

A population manifest names a population two ways that must agree:
    members   the sorted organism refs (organism_id = sha256 over each canonical player manifest)
              -> manifest_hash pins exactly these organisms
    recipe    (generator, foundry_manifest seed, n, foundry_profile) -> the frozen generator
              REPRODUCES the generation-0 base population; every member whose origin is "gen0"
              must be in that regenerated population (same profile + seed => same declared
              population); members with any other origin are the imports and are listed with
              their identities under `imported`
plus the facts a comparison needs: lineage_composition by origin tag (sums to count),
gen0_provenance (the producer's fill block VERBATIM or "UNKNOWN"), selection_criteria ("NONE" or
a declared treatment) with selection_evidence_ref (required iff not NONE; its recorded_at may not
be later than the seal), and a structural_summary computed by ONE function so "matched structure,
unmatched capability" is a mechanical diff on both sides.

Nothing here scores an organism, reads a world, or changes the runtime. The structural
descriptor is a pure function of the player manifest (static opcode categories of the genome
words; no execution).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from proteus.eval import foundry_profile as FP  # noqa: E402
from proteus.foundry import generate as GEN  # noqa: E402
from proteus.foundry.affordances import CATEGORY, N_OPCODES  # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH, canonical_json, hash_obj, sha256_hex  # noqa: E402
from proteus.foundry.vm import validate_manifest  # noqa: E402

POPULATION_SCHEMA = "proteus.population_manifest.v1"
DESCRIPTOR_SCHEMA = "proteus.structural_descriptor.v1"
GENERATOR = "proteus.foundry.generate.generate"
GEN0 = "gen0"
UNKNOWN = "UNKNOWN"

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "proteus" / "integration" / "PLAYER_REGISTRY.json"
REGISTRY_MANIFEST_PATH = ROOT / "proteus" / "eval" / "REGISTRY_POPULATION_MANIFEST.json"


# ------------------------------------------------------------------ structural descriptor (P3, minimal)
def structural_descriptor(manifest: dict) -> dict:
    """Pure function of a player manifest. Static: every genome word is decoded as an opcode
    (word mod N_OPCODES) whether or not it is ever reached; no execution, no world."""
    validate_manifest(manifest)
    g = manifest["genome"]
    cats: dict = {}
    for w in g:
        c = CATEGORY[w % N_OPCODES]
        cats[c] = cats.get(c, 0) + 1
    return {
        "schema_version": DESCRIPTOR_SCHEMA,
        "genome_words": len(g),
        "genome_instructions": len(g) // 4,
        "opcode_category_counts_static": dict(sorted(cats.items())),
        "persist": manifest["persist"],
        "tape_words": manifest["tape_words"],
        "n_regs": manifest["n_regs"],
        "code_writable": bool(manifest["code_writable"]),
        "tick_budget": manifest["tick_budget"],
        "out_cap": manifest["out_cap"],
    }


def _quantiles(xs: list) -> dict:
    s = sorted(xs)
    n = len(s)
    if n == 0:
        return {"min": None, "q25": None, "median": None, "q75": None, "max": None}
    q = lambda f: s[min(n - 1, int(f * (n - 1)))]  # noqa: E731  (nearest-rank; integers stay integers)
    return {"min": s[0], "q25": q(0.25), "median": q(0.5), "q75": q(0.75), "max": s[-1]}


def structural_summary(manifests: list) -> dict:
    ds = [structural_descriptor(m) for m in manifests]
    cats: dict = {}
    for d in ds:
        for c, k in d["opcode_category_counts_static"].items():
            cats[c] = cats.get(c, 0) + k

    def mix(key):
        out: dict = {}
        for d in ds:
            v = str(d[key])
            out[v] = out.get(v, 0) + 1
        return dict(sorted(out.items()))

    return {
        "count": len(ds),
        "genome_instructions": _quantiles([d["genome_instructions"] for d in ds]),
        "opcode_category_counts_static": dict(sorted(cats.items())),
        "persist_mix": mix("persist"),
        "tape_words_mix": mix("tape_words"),
        "n_regs_mix": mix("n_regs"),
        "code_writable_share": (sum(1 for d in ds if d["code_writable"]) / len(ds)) if ds else None,
    }


# ------------------------------------------------------------------ members
def _member(org: dict) -> tuple:
    """(organism_id, manifest, origins) from an organism record as generate()/common_fill() emit it,
    or from a bare player manifest. A record whose organism_id does not hash from its manifest is
    refused: the ref must be earned, not declared."""
    if "manifest" in org:
        m = org["manifest"]
        oid = hash_obj(m)
        if "organism_id" in org and org["organism_id"] != oid:
            raise ValueError("organism_id does not hash from its manifest")
        origins = list(org.get("origins", [GEN0]))
    else:
        m = org
        oid = hash_obj(m)
        origins = [GEN0]
    validate_manifest(m)
    if not origins:
        raise ValueError("empty origins")
    return oid, m, origins


def manifest_hash_of(refs: list) -> str:
    return sha256_hex(canonical_json(sorted(refs)))


# ------------------------------------------------------------------ build / verify
def build_population_manifest(members: list, *, foundry_manifest: dict | None = None,
                              foundry_profile: str | None = None, gen0_provenance=UNKNOWN,
                              imported_sources: dict | None = None, selection_criteria: str = "NONE",
                              selection_evidence_ref: dict | None = None, sealed_at: str | None = None,
                              population_label: str | None = None) -> dict:
    """members: organism records (generate()/common_fill() output) or bare manifests.
    foundry_manifest: the SEEDED foundry manifest (with seed and n) that produced the gen0 base;
    when given, the recipe is recorded and CHECKED by regeneration. imported_sources: optional
    {organism_id: {"source_world"|"source_artifact"|...}} for non-gen0 members (verbatim)."""
    parsed = [_member(o) for o in members]
    refs = [p[0] for p in parsed]
    if len(set(refs)) != len(refs):
        raise ValueError("duplicate member")
    count = len(refs)
    if count == 0:
        raise ValueError("empty population")

    composition: dict = {}
    for _oid, _m, origins in parsed:
        tag = origins[-1]
        composition[tag] = composition.get(tag, 0) + 1
    if sum(composition.values()) != count:
        raise ValueError("lineage_composition does not sum to count")

    recipe = UNKNOWN
    profile_id = foundry_profile or UNKNOWN
    if foundry_manifest is not None:
        GEN.validate_foundry_manifest(foundry_manifest)
        prof = FP.build_profile(foundry_manifest)
        if foundry_profile is not None and foundry_profile != prof["profile_id"]:
            raise ValueError("declared foundry_profile disagrees with the foundry manifest")
        profile_id = prof["profile_id"]
        base = {o["organism_id"] for o in GEN.generate(foundry_manifest)}
        gen0_refs = [oid for oid, _m, origins in parsed if origins[-1] == GEN0]
        missing = [r for r in gen0_refs if r not in base]
        if missing:
            raise ValueError("%d gen0 member(s) are not produced by the recipe" % len(missing))
        recipe = {
            "generator": GENERATOR,
            "runtime_hash": RUNTIME_HASH,
            "foundry_profile": profile_id,
            "foundry_manifest_seed": foundry_manifest["seed"],
            "n": foundry_manifest["n"],
            "gen0_members_in_recipe": len(gen0_refs),
            "recipe_population_hash": manifest_hash_of(sorted(base)),
        }

    imported = []
    src = imported_sources or {}
    for oid, _m, origins in parsed:
        if origins[-1] != GEN0:
            imported.append({"organism_ref": oid, "tag": origins[-1],
                             "origins": origins, "source": src.get(oid, UNKNOWN)})
    imported.sort(key=lambda r: r["organism_ref"])

    if selection_criteria == "NONE":
        if selection_evidence_ref is not None:
            raise ValueError("selection_evidence_ref given with selection_criteria NONE")
    else:
        if not isinstance(selection_evidence_ref, dict) or "ref" not in selection_evidence_ref \
                or "recorded_at" not in selection_evidence_ref:
            raise ValueError("a declared selection needs selection_evidence_ref {ref, recorded_at}")
        if sealed_at is not None and str(selection_evidence_ref["recorded_at"]) > str(sealed_at):
            raise ValueError("selection evidence recorded after the seal (future information)")

    body = {
        "schema_version": POPULATION_SCHEMA,
        "population_label": population_label or UNKNOWN,
        "foundry_profile": profile_id,
        "runtime_hash": RUNTIME_HASH,
        "count": count,
        "members": sorted(refs),
        "manifest_hash": manifest_hash_of(refs),
        "recipe": recipe,
        "lineage_composition": dict(sorted(composition.items())),
        "gen0_provenance": gen0_provenance if gen0_provenance is not None else UNKNOWN,
        "imported": imported,
        "selection_criteria": selection_criteria,
        "selection_evidence_ref": selection_evidence_ref,
        "sealed_at": sealed_at if sealed_at is not None else UNKNOWN,
        "structural_summary": structural_summary([p[1] for p in parsed]),
    }
    body["population_manifest_id"] = hash_obj(body)
    return body


def verify_population_manifest(pm: dict, members: list | None = None,
                               foundry_manifest: dict | None = None) -> None:
    """Recompute the ids from the record; optionally re-check the members and the recipe."""
    if pm.get("schema_version") != POPULATION_SCHEMA:
        raise ValueError("schema mismatch")
    body = {k: v for k, v in pm.items() if k != "population_manifest_id"}
    if hash_obj(body) != pm["population_manifest_id"]:
        raise ValueError("population_manifest_id does not recompute")
    if pm["manifest_hash"] != manifest_hash_of(pm["members"]):
        raise ValueError("manifest_hash does not recompute")
    if pm["members"] != sorted(pm["members"]) or len(set(pm["members"])) != len(pm["members"]):
        raise ValueError("members not sorted/unique")
    if sum(pm["lineage_composition"].values()) != pm["count"] or len(pm["members"]) != pm["count"]:
        raise ValueError("count disagrees")
    if members is not None:
        refs = sorted(_member(o)[0] for o in members)
        if refs != pm["members"]:
            raise ValueError("members do not match the manifest")
    if foundry_manifest is not None:
        if pm["recipe"] == UNKNOWN:
            raise ValueError("manifest has no recipe to check")
        prof = FP.build_profile(foundry_manifest)
        if prof["profile_id"] != pm["recipe"]["foundry_profile"] or prof["profile_id"] != pm["foundry_profile"]:
            raise ValueError("foundry profile disagrees")
        base = sorted(o["organism_id"] for o in GEN.generate(foundry_manifest))
        if manifest_hash_of(base) != pm["recipe"]["recipe_population_hash"]:
            raise ValueError("recipe does not regenerate the recorded base population")


# ------------------------------------------------------------------ the frozen registry as a population
def registry_population_manifest(registry_path: Path = REGISTRY_PATH) -> dict:
    r = json.loads(registry_path.read_text(encoding="utf-8"))
    members = [{"organism_id": e["organism_id"], "manifest": e["manifest"], "origins": [GEN0]}
               for e in r["entries"]]
    fm = dict(r["build"]["foundry_manifest"])
    prov = {"fill": "proteus.foundry.generate.generate", "registry_id": r["registry_id"],
            "generation_manifest_id": r["build"]["generation_manifest_id"],
            "selection_rule": r["build"]["selection_rule"]}
    return build_population_manifest(members, foundry_manifest=fm, gen0_provenance=prov,
                                     population_label="proteus.player_registry.v1 " + r["registry_id"][:16],
                                     sealed_at=r["build"].get("generated", UNKNOWN))


def main() -> int:
    pm = registry_population_manifest()
    REGISTRY_MANIFEST_PATH.write_text(json.dumps(pm, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(REGISTRY_MANIFEST_PATH)
    print("population_manifest_id", pm["population_manifest_id"][:16], "| manifest_hash", pm["manifest_hash"][:16],
          "| profile", pm["foundry_profile"], "| count", pm["count"], "| composition", pm["lineage_composition"])
    print("recipe regenerates base:", pm["recipe"]["recipe_population_hash"] == pm["manifest_hash"])
    print("structural_summary.genome_instructions", pm["structural_summary"]["genome_instructions"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
