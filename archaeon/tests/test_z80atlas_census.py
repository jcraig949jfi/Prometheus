"""COPIER-CENSUS-01 instrument checks: rulers classify correctly; the input-skip is exact; the census streams are disjoint."""
from __future__ import annotations

import pytest

from archaeon.z80atlas.census import copier_census as C

KEYS = ("writes", "cov", "birth", "fid", "exact", "span", "k", "steps", "halted", "in_read", "hist", "exec_addrs", "window")


def test_rulers_classify_as_known():
    r = C.rulers()
    assert all(v["PASS"] for v in r.values()), r


@pytest.mark.parametrize("substrate", ["vmcopy", "z80"])
def test_input_skip_is_exact_against_full_sweep(substrate):
    cp = substrate == "vmcopy"; n_skipped = 0
    for tape in C.stream_tapes("TEST-SKIP-" + substrate, 0, 150, 32):
        a, b = C.sweep(tape, cp), C.sweep(tape, cp, force_full=True)
        n_skipped += not a[0]["in_read"]
        assert C.classify(a, 32) == C.classify(b, 32)
        for pa, pb in zip(a, b):
            assert pa["x"] == pb["x"] and all(pa[k] == pb[k] for k in KEYS), (tape.hex(), pa["x"])
    assert n_skipped > 50, "fixture must exercise the skip"


def test_specimen_gating_is_measured_not_assumed():
    ph = C.sweep(bytes.fromhex(C.SPECIMEN), True)
    assert [p["x"] for p in ph if p["exact"]] == [121]
    assert sum(p["birth"] for p in ph) == 26


def test_streams_are_disjoint_by_label():
    a = list(C.stream_tapes("vmcopy32", 0, 5, 32)); b = list(C.stream_tapes("PILOT-vmcopy32", 0, 5, 32)); c = list(C.stream_tapes("vmcopy32", 1, 5, 32))
    assert not set(a) & set(b) and not set(a) & set(c)
