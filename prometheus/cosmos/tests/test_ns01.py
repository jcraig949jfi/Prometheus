"""NS-01 / NS-02 instrument regression tests: frozen mechanism rules on planted witnesses, disguise equivalence,
and the FAILURE_15 relational witness (readout sees the cue, generic state decoders do not; gauge keeps it)."""
import numpy as np

from prometheus.cosmos.ns01 import signature as S1
from prometheus.cosmos.ns01 import signature2 as S2
from prometheus.cosmos.ns01 import transforms as T
from prometheus.cosmos.ns01.f15 import RelationalWitness, measure
from prometheus.cosmos.ns01.witnesses import WITNESSES


def _cls(name):
    return S1.classify(S1.signature(WITNESSES[name][0]))


def test_rules_on_planted_witnesses():
    assert "DEGENERATE" in _cls("nomemory")["fired"]
    assert _cls("signmasked")["fired"] == ["M-LINBLIND"]
    assert _cls("hidden")["fired"] == ["M-HIDDEN"]
    assert _cls("register") == {"fired": [], "viable": True}


def test_disguised_register_is_equivalent_and_unread_register_is_not():
    reg = S2.signature2(WITNESSES["register"][0])
    assert S2.equivalent(reg, S2.signature2(lambda t: T.Permute(WITNESSES["register"][0](t), seed=3)))
    assert not S2.equivalent(reg, S2.signature2(WITNESSES["register_unread"][0]))


def test_dual_cue_separates_first_write_from_latest_write():
    reg = S2.stress(WITNESSES["register"][0])
    stig = S2.stress(WITNESSES["stig_static"][0])
    assert reg["dual1"] > .9 and reg["dual2"] < .1
    assert stig["dual2"] > stig["dual1"]


def test_failure15_relational_witness():
    m = measure(lambda t: RelationalWitness(t), True)
    for k, r in m.items():
        assert r["rf"] > .95
        assert r["full_lin"] < .15 and r["full_rf"] < .5
        assert r["GAUGE"] > .95 and r["DESYNC"] < .1
