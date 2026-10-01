"""H-IMPL regression: lens_swap.handoff (frozen KA7 rule) must not pass on
offsets it never measured.

Rule (b) "every offset in [ro_off-4, ro_off-1] is SITE" was coded as
all(... for o in range(ro_off-4, ro_off) if o in os_): if none of those
offsets were scanned it is vacuously True, and the "final SITE run" is taken
from whatever the last scanned offset is (not anchored at ro_off-1). A scan
that stops at offset 5 of a 10-tick readout PASSES the handoff. FAILS on the
current code, PASSES with patches/handoff_coverage.diff. Neutrality: every
recorded W-M census (workers/W-M/out/census_*.json, both modes) scanned
offsets -1 .. ro_off-1 and gets the identical result under both codes.
"""
import glob
import json
import pathlib

from prometheus.ananke import lens_swap as L

REPO = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "roles" / "Ananke").is_dir())


def _mk(cls, fC=0.0):
    return {"class": cls, "fC": fC}


def _legacy(offsets, ro_off):
    """Verbatim copy of the pre-patch rule, for the neutrality check."""
    os_ = sorted(int(o) for o in offsets)
    get = lambda o: offsets[o] if o in offsets else offsets[str(o)]
    chan = [o for o in os_ if get(o)["class"] == "CHANNEL" or (get(o)["fC"] or 0) >= 0.60]
    run_start = None
    for o in reversed(os_):
        if get(o)["class"] != "SITE":
            break
        run_start = o
    a = any(2 <= o <= 7 for o in chan)
    b = all(get(o)["class"] == "SITE" for o in range(ro_off - 4, ro_off) if o in os_)
    c = bool(chan) and run_start is not None and max(chan) < run_start
    d = run_start is not None and ro_off - 8 <= run_start <= ro_off - 4
    return {"channel_offsets": chan, "site_run_start": run_start, "a": a, "b": b, "c": c, "d": d,
            "pass": bool(a and b and c and d)}


def test_unmeasured_final_offsets_do_not_pass():
    h = L.handoff({3: _mk("CHANNEL", .9), 5: _mk("SITE")}, 10)
    assert not h["b"] and not h["pass"], h


def test_site_run_is_anchored_at_readout_minus_one():
    # offsets 6..9 are SITE but 10 (the readout itself, not part of the rule) is NEITHER
    offs = {o: _mk("SITE") for o in range(-1, 11)}
    offs[3] = _mk("CHANNEL", .9)
    offs[10] = _mk("NEITHER")
    h = L.handoff(offs, 10)
    assert h["site_run_start"] == 4 and h["pass"], h


def test_recorded_wm_census_results_unchanged():
    files = sorted(glob.glob(str(REPO / "roles/Ananke/research/workers/W-M/out/census_*.json")))
    assert files
    n = 0
    for p in files:
        d = json.load(open(p))
        for mode in ("every", "single"):
            if mode in d:
                assert L.handoff(d[mode]["offsets"], d["ro_off"]) == _legacy(d[mode]["offsets"], d["ro_off"]), (p, mode)
                n += 1
    assert n >= 18
