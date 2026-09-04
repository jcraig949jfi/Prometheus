"""Build the frozen starter menagerie and its registry.

    python proteus/integration/run_build_menagerie.py

Writes PLAYER_REGISTRY.json (intrinsic, authoritative) and ABI_LIVENESS_OBSERVATIONS.json
(extrinsic, never part of identity). Deterministic: rebuilding on a listed runtime reproduces
both byte for byte.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))

from proteus.foundry.identity import canonical_json  # noqa: E402
from proteus.integration import menagerie, registry  # noqa: E402


def main():
    reg, _organisms = menagerie.build_population()
    rid = registry.save(reg, os.path.join(HERE, "PLAYER_REGISTRY.json"))
    obs = menagerie.observe_abi_liveness(reg)
    with open(os.path.join(HERE, "ABI_LIVENESS_OBSERVATIONS.json"), "w", encoding="utf-8",
              newline="\n") as f:
        f.write(canonical_json(obs))
        f.write("\n")

    b = reg["build"]
    print(f"registry_id       {rid}")
    print(f"specimens         {b['registered']} registered / {b['generated']} generated "
          f"/ {b['rejected_invalid_manifest']} rejected")
    print(f"population seed   {b['foundry_manifest']['seed']}")
    print(f"generation mfst   {b['generation_manifest_id'][:16]}")
    env = [e["resource_envelope"] for e in reg["entries"]]
    print(f"tape sizes        {sorted({x['tape_words'] for x in env})}")
    print(f"genome instrs     {min(x['genome_instructions'] for x in env)}"
          f"..{max(x['genome_instructions'] for x in env)}")
    print(f"persist policies  {sorted({x['persist'] for x in env})}")
    print(f"tick budgets      {sorted({x['tick_budget'] for x in env})}")
    print(f"code_writable     {sorted({x['code_writable'] for x in env})}")
    print(f"first-tick status {obs['aggregate_first_tick_status']}  (observed, NOT a filter)")
    print(f"emission          {obs['aggregate_emission']}  (observed, NOT a filter)")
    # prove the extrinsic store cannot touch identity
    again = registry.load(os.path.join(HERE, "PLAYER_REGISTRY.json"))
    assert again["registry_id"] == rid
    print("registry re-validated after writing the extrinsic store: identity unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
