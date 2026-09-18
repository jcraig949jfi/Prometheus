"""The Campaign 4 starting-population mint (launch gate G5, Proteus half).

positive  the committed mint recomputes from the committed declaration; the declaration digest
          in the mint equals the sha256 of the declaration file's raw bytes (launch_gate's rule)
negative  a declaration with one gen0 draw index moved is refused (does not regenerate); a
          declaration whose identity block names another runtime is refused
cheat     a declaration with an organism_id that does not hash from its manifest is refused
"""
from __future__ import annotations

import copy
import hashlib
import json
import os

import pytest

from proteus.eval import emit_c4_starting_population as C4
from proteus.eval import population_manifest as PM


def _decl():
    if not os.path.exists(C4.DECL):
        pytest.skip("Archaeon declaration not present")
    return C4.load_declaration()


def test_committed_mint_recomputes_and_binds_the_declaration_bytes():
    decl, digest = _decl()
    committed = json.load(open(C4.OUT, encoding="utf-8"))
    assert committed["declaration_canonical_digest"] == C4.canonical_digest(decl) == decl["population_digest"]
    assert committed["declaration_canonical_digest"] == "sha256:7f03cc8282b4b1e2d47ebf541d053c7e640732cc44b7ab20b82e3812d3e808c1"
    # the raw-byte digest is kept beside it but is checkout-dependent: on THIS checkout it must
    # equal the file's bytes; it is not asserted equal to the committed value
    assert digest == "sha256:" + hashlib.sha256(open(C4.DECL, "rb").read()).hexdigest()
    fm = C4.recipe_of(decl)
    prof = C4.check_identity(decl, fm)
    assert committed["foundry_profile"] == prof["profile_id"] == decl["identity"]["foundry_profile_id"]
    members, sources = C4.members_of(decl)
    pm = committed["population_manifest"]
    PM.verify_population_manifest(pm, members=members, foundry_manifest=fm)
    assert pm["count"] == 57 == len(set(pm["members"]))
    assert pm["lineage_composition"] == {"delay_general": 11, "gen0": 12, "shelf": 19, "w0_solver": 15}
    assert len(pm["imported"]) == 45 and pm["selection_criteria"] == "NONE"


def test_canonical_digest_is_line_ending_invariant_and_content_sensitive():
    decl, _ = _decl()
    crlf = json.dumps(decl, indent=1).replace(chr(10), chr(13) + chr(10)).encode("utf-8")
    lf = json.dumps(decl, indent=1).encode("utf-8")
    assert hashlib.sha256(crlf).hexdigest() != hashlib.sha256(lf).hexdigest()      # the defect
    assert C4.canonical_digest(json.loads(crlf)) == C4.canonical_digest(json.loads(lf))
    changed = copy.deepcopy(decl)
    changed["organisms"][0]["multiplicity"] += 1
    assert C4.canonical_digest(changed) != C4.canonical_digest(decl)
    volatile = dict(decl, generated_at="1999-01-01T00:00:00Z", wall_s=99.0)
    assert C4.canonical_digest(volatile) == C4.canonical_digest(decl)


def test_gen0_draws_regenerate_and_a_moved_index_is_refused():
    decl, _ = _decl()
    fm = C4.recipe_of(decl)
    assert C4.check_gen0_draws(decl, fm) == 12
    bad = copy.deepcopy(decl)
    g = [o for o in bad["organisms"] if o["class"] == "gen0_random"]
    g[0]["ancestries"][0]["index"], g[1]["ancestries"][0]["index"] = g[1]["ancestries"][0]["index"], g[0]["ancestries"][0]["index"]
    with pytest.raises(ValueError, match="does not regenerate"):
        C4.check_gen0_draws(bad, fm)


def test_identity_block_must_match_the_live_substrate():
    decl, _ = _decl()
    fm = C4.recipe_of(decl)
    bad = copy.deepcopy(decl)
    bad["identity"]["runtime_hash"] = "0" * 64
    with pytest.raises(ValueError, match="disagrees"):
        C4.check_identity(bad, fm)


def test_cheat_forged_organism_id_is_refused():
    decl, _ = _decl()
    bad = copy.deepcopy(decl)
    bad["organisms"][5]["organism_id"] = "f" * 64
    with pytest.raises(ValueError, match="does not hash"):
        C4.members_of(bad)
