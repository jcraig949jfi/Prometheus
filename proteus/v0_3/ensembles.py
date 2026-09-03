"""Independently generated probe ensembles from PUBLIC deterministic seeds (brief section 7).

Every seed below is a hash that already existed in the committed record before this file was
written, so no ensemble was chosen by Proteus for its outcome:

  E0  the first external review addendum   4a9fe0cb...   (the V0 ensemble, unchanged)
  E1  the V0 kickoff brief                 cacf303f...
  E2  the V0.3 crucible brief              78ed8284...
  E3  the published affordance table       f1607ee8...

E0-E3 share the V0 ensemble SHAPE so that the only difference is the seed. E4 and E5 change the
shape deliberately, to test whether phenotype structure is an artifact of ensemble RESOLUTION
rather than of any particular seed; their shapes are declared here, before any result is seen.

  E4  8 probes, otherwise identical to E0's shape, seeded by the V0.3 brief hash
  E5  2 probes, otherwise identical to E0's shape, seeded by the V0.3 brief hash

Ensembles are never merged. Each is reported on its own (brief section 7).
"""
from __future__ import annotations

from proteus.foundry.identity import hash_obj
from proteus.foundry.probes import DEFAULT_ENSEMBLE, build_probes

BRIEF_V0 = "cacf303f3a997e2172cac5ef39021ac194ab3ec82edea21f5dfc8579e70ec5b4"
ADDENDUM_V0 = "4a9fe0cb33fb88acbb64e3bcff23c609f80429ffb46b21040de81527d6510fab"
BRIEF_V0_3 = "78ed8284294b33abea3f7b1a4c0f89f3d95582ea22b337bb3b4e4357ff5679d9"
AFFORDANCE = "f1607ee8be680acc33288a95c1a25c09ad4c799a47b0975381be8ca02d7638ce"


def _cfg(seed_root: str, n_probes: int = 4) -> dict:
    c = dict(DEFAULT_ENSEMBLE)
    c["seed_root"] = seed_root
    c["n_probes"] = n_probes
    return c


ENSEMBLES = {
    "E0": _cfg(ADDENDUM_V0, 4),
    "E1": _cfg(BRIEF_V0, 4),
    "E2": _cfg(BRIEF_V0_3, 4),
    "E3": _cfg(AFFORDANCE, 4),
    "E4": _cfg(BRIEF_V0_3, 8),
    "E5": _cfg(BRIEF_V0_3, 2),
}

SEED_PROVENANCE = {
    "E0": "sha256 of ADDENDUM_EXTERNAL_REVIEW_V0_2026-09-02.txt (the V0 ensemble, unchanged)",
    "E1": "sha256 of PROMPT_PROTEUS_PLAYER_FOUNDRY_V0_2026-09-02.txt",
    "E2": "sha256 of PROMPT_PROTEUS_V0_3_NEUTRALITY_CRUCIBLE_2026-09-03.txt",
    "E3": "sha256 of the published affordance table",
    "E4": "same seed as E2, 8 probes (resolution up)",
    "E5": "same seed as E2, 2 probes (resolution down)",
}


def identity_table() -> dict:
    return {k: {"config": v, "ensemble_identity": hash_obj({"cfg": v, "probes": build_probes(v)}),
                "seed_provenance": SEED_PROVENANCE[k]}
            for k, v in sorted(ENSEMBLES.items())}


def get(name: str):
    cfg = ENSEMBLES[name]
    return cfg, build_probes(cfg)
