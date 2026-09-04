"""Mnemosyne Evidence Wiki / Evidence Tensor — canonical substrate package.

One knowledge substrate, many representations. The `ew` schema in
prometheus_fire is authoritative; everything under evidence_wiki/derived/ is
a rebuildable projection. See docs/ARCHITECTURE_V0.md.
"""
SCHEMA_VERSION = 4          # 4: migration 007, evidence->fossil binding
ONTOLOGY_VERSION = 2
# The shape Harmonia/Proteus/SFE code against. Bump when the fossil ingest or
# query contract changes; docs/FIRST_INTEGRATION_EVIDENCE_CONTRACT.md is its
# normative description.
FOSSIL_CONTRACT_VERSION = "pew.fossil.v2"
COMPILER_VERSION = "ew-compiler-0.2"
COORD_GENERATOR_VERSION = "coordgen-0.2"
