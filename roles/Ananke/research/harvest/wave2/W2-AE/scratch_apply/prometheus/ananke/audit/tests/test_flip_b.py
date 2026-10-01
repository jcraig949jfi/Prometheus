"""audit.flip_b: the B certificate separates P-FLIP (infers the mapping) from RELAY_LATCH (copy class) on recorded
C1 FLIP cells, reproducing W2-S t1_balanced.json; overall accuracy and SIGNAL do not separate them."""
from __future__ import annotations

import pytest

from prometheus.ananke import assays, envs
from prometheus.ananke.audit import certify as C
from prometheus.ananke.audit import flip_b as FB
from prometheus.ananke.audit import programs as PG
from prometheus.ananke.audit import rulers as R
from prometheus.ananke.audit.tests import _data as D
from prometheus.ananke.physics import Physics
from prometheus.ananke.rng import H_int
from prometheus.ananke.search import HELD_NS
from prometheus.explib.outcomes import FAIL, NOT_VERIFIED, PASS

T1B = "roles/Ananke/research/harvest/wave2/W2-S/out/t1_balanced.json"


def held64(r):
    return assays.world_seeds(H_int(r["search_seed"], HELD_NS), 64)       # W2-S held_seeds (evolve rows)


def setup(prefix, prog):
    r = D.row(prefix, kind="evolve", family="FLIP")
    ph, env = Physics.from_dict(r["physics"]).validate(), envs.EnvSpec(**r["env"])
    if prog == "P-FLIP":
        return r, ph, env, PG.p_flip(ph)
    p = ph if ph.prog_len >= 14 else ph.replace(prog_len=14).validate()
    return r, p, env, PG.relay_latch(p)


@D.need(D.ROWS, D.REPO / T1B)
def test_B_certificate_separates_P_FLIP_from_RELAY_LATCH():
    rec = {(o["cell"][:8], o["program"]): o for o in D.load_json(T1B)["rows"]}
    got = {}
    for c8, prog in (("6f82f9c7", "P-FLIP"), ("6f82f9c7", "RELAY_LATCH"), ("996716ac", "RELAY_LATCH")):
        r, ph, env, g = setup(c8, prog)
        o = FB.flip_eval(ph, g, env, held64(r))
        want = rec[(c8, prog)]
        for k in ("acc", "lo99", "chg", "chg_lo99", "same", "bal", "bal_lo99", "chg_frac"):
            assert o[k] == pytest.approx(want[k], abs=1e-12), (c8, prog, k)
        got[(c8, prog)] = o
    assert FB.b_certificate(got[("6f82f9c7", "P-FLIP")]).outcome == PASS
    assert FB.b_certificate(got[("6f82f9c7", "RELAY_LATCH")]).outcome == FAIL
    # the copy-class reference passes SIGNAL on overall accuracy (.766, lo99 .719) but not B (lo99 .710 < .75)
    rl = got[("996716ac", "RELAY_LATCH")]
    assert rl["lo99"] > 0.55 and FB.b_certificate(rl).outcome == FAIL
    assert FB.flip_change(rl).outcome == FAIL
    assert FB.b_certificate({"acc": 0.9}).outcome == NOT_VERIFIED          # undefined B is never a pass


@D.need(D.ROWS)
def test_FLIP_B_ruler_family_is_sound():
    r = D.row("6f82f9c7", kind="evolve", family="FLIP")
    ph, env = Physics.from_dict(r["physics"]).validate(), envs.EnvSpec(**r["env"])
    seeds = held64(r)[:32]
    cell = [C.Cell(ph, env, "6f82")]
    b = C.certify(R.FLIP_B, cell, C.flip_b_programs(), seeds)
    assert b.verdict == "SOUND", b.summary()
    assert {r["program"]: r["passed"] for r in b.rows} == {"P_FLIP": True, "RELAY_LATCH": False}
