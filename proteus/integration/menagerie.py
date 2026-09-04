"""The frozen starter menagerie: a deterministic specimen population for integration testing.

WHAT MAKES THIS POPULATION HONEST
---------------------------------
The population is EXACTLY `generate(FOUNDRY_MANIFEST)`, in generator order, with NO filter of any
kind applied afterwards. There is no scoring step, no behavioural screen, no "keep the
interesting ones", and no place in the code where one could be added without deleting a comment
that says so. That is the whole selection rule, and it is stated as a rule rather than as an
intention so a reviewer can check it by reading twenty lines.

Specifically NOT done here:
  * no hand-edited genomes -- every genome comes from the frozen Foundry PRNG
  * no world-informed or SFE-informed generation -- nothing in this module knows a world exists
  * no behavioural selection -- halters, yielders, budget exhausters, silent and noisy emitters
    are all retained exactly as they arise
  * no phenotype screening -- the ABI liveness probe below CANNOT remove a specimen

The only rejection rule is the authoritative manifest validator, and in practice it rejects
nothing because `sample_manifest` already validates before returning. The build report records
the rejection count so that "zero" is an observation rather than an assumption.

DETERMINISM
-----------
The population seed is derived from the sha256 of the integration directive, so it was fixed
before any specimen existed and could not have been chosen to produce a flattering population.
`generate` draws organism i from `root.derive("organism", i)`, and derive does not advance the
parent, so specimen i depends only on (seed, i) and is independent of population size. Rebuilding
with the same manifest on a listed runtime reproduces the population byte for byte.

ABI LIVENESS IS AN OBSERVATION, NOT A GATE
------------------------------------------
`observe_abi_liveness` runs a few synthetic ticks per specimen for one purpose only: to
demonstrate that the ABI functions across structurally different organisms, which the directive
permits as the one allowed form of screening. Its output goes to a SEPARATE extrinsic store keyed
by organism_id, never into a registry entry, and it never removes anything. Deleting that store
leaves every organism_id, entry_id and the registry_id unchanged -- there is a test for that.
"""
from __future__ import annotations

import hashlib
import os

from proteus.foundry.generate import (DEFAULT_FOUNDRY_MANIFEST, foundry_identity, generate,
                                      validate_foundry_manifest)
from proteus.foundry.identity import hash_obj
from proteus.foundry.prng import SplitMix64, seed_from
from proteus.foundry.vm import ManifestError, Meter, Player, validate_manifest
from proteus.integration import registry as R

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIRECTIVE = os.path.join("roles", "Proteus",
                         "PROMPT_PROTEUS_HARMONIA_INTEGRATION_READINESS_2026-09-03.txt")

#: Population size. Modest on purpose: large enough to exercise structural variation and consumer
#: plumbing, small enough that nobody can mistake it for an evolutionary campaign.
POPULATION_SIZE = 64


def directive_sha256() -> str:
    with open(os.path.join(ROOT, DIRECTIVE), "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def foundry_manifest() -> dict:
    """The committed defaults, with only seed and n set.

    Nothing else is tuned. Choosing narrower ranges would be an authored choice about what a
    starter population should look like, and this pass has no basis for one.
    """
    fm = dict(DEFAULT_FOUNDRY_MANIFEST)
    fm["seed"] = int(directive_sha256()[:16], 16)
    fm["n"] = POPULATION_SIZE
    validate_foundry_manifest(fm)
    return fm


def build_population():
    """Generate, validate, and register. The population IS the generator output, in order."""
    fm = foundry_manifest()
    organisms = generate(fm)                       # <-- the entire selection rule
    rejected = []
    entries = []
    gen_manifest_id = hash_obj(fm)
    for i, org in enumerate(organisms):
        try:
            validate_manifest(org["manifest"])     # authoritative; the ONLY rejection rule
        except ManifestError as e:                 # pragma: no cover - generate pre-validates
            rejected.append({"index": i, "organism_id": org["organism_id"], "error": str(e)})
            continue
        entries.append(R.build_entry(org, {
            "source": "proteus.foundry.generate.generate",
            "foundry_identity": foundry_identity(fm),
            "population_seed": fm["seed"],
            "index_in_population": i,
            "derivation": "SplitMix64(seed_from('proteus.generate.v0', seed, RUNTIME_HASH))"
                          ".derive('organism', i)",
            "generation_manifest_id": gen_manifest_id,
        }))
    build = {
        "builder": "proteus.integration.menagerie",
        "directive": DIRECTIVE,
        "directive_sha256": directive_sha256(),
        "foundry_manifest": fm,
        "generation_manifest_id": gen_manifest_id,
        "foundry_identity": foundry_identity(fm),
        "requested": POPULATION_SIZE,
        "generated": len(organisms),
        "registered": len(entries),
        "rejected_invalid_manifest": len(rejected),
        "rejections": rejected,
        "selection_rule": ("NONE beyond manifest validity. The population is generate(fm) in "
                           "generator order. No behavioural or phenotypic filter of any kind "
                           "was applied at any point."),
    }
    return R.build_registry(entries, build), organisms


# ---------------------------------------------------------------- extrinsic, never a gate

def observe_abi_liveness(reg: dict, ticks: int = 3, seed: int = 0xA51CE) -> dict:
    """Run a few synthetic ticks per specimen to show the ABI works. REMOVES NOTHING.

    The inputs are an ABI fixture and emphatically NOT a world: two channels of arbitrary
    constants, no semantics, no reward, no task. The result is extrinsic observation and lives in
    its own store keyed by organism_id.
    """
    obs = {}
    counts = {"halt": 0, "yield": 0, "budget": 0}
    emitters = {"silent": 0, "emitting": 0}
    for e in reg["entries"]:
        p = Player(e["manifest"])
        st = p.fresh_state()
        m = Meter()
        rng = SplitMix64(seed_from("proteus.integration.abi_fixture", seed, e["organism_id"]))
        statuses, total_out = [], 0
        for t in range(ticks):
            outs, status = p.run_tick(st, [[t, 7, 11], [0]], 2, rng, meter=m)
            statuses.append(status)
            total_out += sum(len(c) for c in outs)
        counts[statuses[0]] = counts.get(statuses[0], 0) + 1
        emitters["emitting" if total_out else "silent"] += 1
        obs[e["organism_id"]] = {
            "tick_statuses": statuses,
            "output_values_total": total_out,
            "ops": m.ops,
            "out_dropped": m.out_dropped,
            "phenotype": "UNKNOWN",
        }
    return {
        "schema_version": "proteus.abi_liveness_observations.v1",
        "kind": "EXTRINSIC OBSERVATION -- not part of any organism's identity",
        "not_a_world": ("The inputs are a fixed synthetic ABI fixture with no semantics. This is "
                        "NOT World 0, carries no task or reward, and nothing here ranks, selects "
                        "or classifies any specimen."),
        "fixture": {"inputs": [[0, 7, 11], [0]], "n_out": 2, "ticks": ticks, "seed": seed,
                    "note": "first input channel's leading value is the tick index"},
        "aggregate_first_tick_status": counts,
        "aggregate_emission": emitters,
        "observations": obs,
    }
