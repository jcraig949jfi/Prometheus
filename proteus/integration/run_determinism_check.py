"""Cross-runtime determinism check for the registry and the starter population.

    python proteus/integration/run_determinism_check.py

Rebuilds the population in memory and prints the identities a consumer would pin. Run it on every
supported runtime; the digests must agree. This is the integration-surface analogue of the V0.6
replay contract, and it exercises the same guarantee the seed contract promises: same foundry
manifest plus same runtime gives a byte-identical population.
"""
from __future__ import annotations

import hashlib
import os
import platform
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))

from proteus.foundry.identity import canonical_json  # noqa: E402
from proteus.integration import menagerie, registry  # noqa: E402


def main():
    reg, _ = menagerie.build_population()
    blob = canonical_json(reg)
    on_disk = None
    p = os.path.join(HERE, "PLAYER_REGISTRY.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            on_disk = canonical_json(registry.load(p))
    print(f"python            {sys.version.split()[0]} {platform.system()}")
    print(f"registry_id       {reg['registry_id']}")
    print(f"serialized sha256 {hashlib.sha256(blob.encode()).hexdigest()}")
    print(f"specimens         {len(reg['entries'])}")
    print(f"first organism    {reg['entries'][0]['organism_id']}")
    print(f"last  organism    {reg['entries'][-1]['organism_id']}")
    print(f"matches committed registry: {on_disk == blob if on_disk else 'no file on disk'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
