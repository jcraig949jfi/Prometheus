"""atlas_bee: the light shim that instantiates Atlas-indexed scientific questions inside the Bellerophon
   Emergence Engine (BEE = prometheus/toolbox), for the Atlas -> BEE pilot (roles/Bellerophon/atlas_bee/).

   The shim lives BESIDE the kernel and never changes the five core ids. It emits BEE Experiment IRs and search
   runs; BEE keeps its own receipts, replay, admission and failure semantics. Each adaptation (a1..a6) carries a
   machine-readable translation manifest and a frozen, hashed preregistration written BEFORE it is run."""
from prometheus.atlas_bee.freeze import freeze, verify, sha256_of, canonical_bytes
from prometheus.atlas_bee.manifest import Manifest, Entry, RELATIONS, refusal

__all__ = ["freeze", "verify", "sha256_of", "canonical_bytes", "Manifest", "Entry", "RELATIONS", "refusal"]
