"""H-IMPL regression: campaign wave D must regenerate identical specs on resume.

campaign.main builds wave D from `prior = store.rows()` filtered to kind ==
"evolve". On a resume after part of D ran, D's own fresh-seed replicate rows
(wave "D", kind "evolve") are in that list and compete in promoted(); a
replicate that beats a promoted cell shifts pi, so cell ids and search seeds
change and the resume no longer skips what already ran (module docstring:
"resume is exact at cell granularity"). FAILS on the current code, PASSES with
patches/wave_d_resume_determinism.diff. PTE-C1 ran D in ONE attempt with no D
rows present (watchdog.log: 1 attempt), so the patch is neutral for C1.
"""
from prometheus.ananke import campaign as C


def _row(cid, fam, lo, wave):
    return {"cell_id": cid, "wave": wave, "kind": "evolve", "env": {"family": fam},
            "physics": {"p": cid}, "levels": {}, "env_levels": {},
            "result": {"held": {"lo99": lo, "comm_delta_lo99": 0.0}, "champion": [[0]]}}


def _ids(specs):
    return sorted(C.cell_id(dict(s)) for s in specs)


def _prior():
    return ([_row("a%d" % i, "RELAY", 0.60 + 0.01 * i, "A") for i in range(6)]
            + [_row("h%d" % i, "HOLD", 0.90, "B2") for i in range(2)])


def test_resume_regenerates_identical_d_specs():
    cfg = C.CampaignConfig()
    first = C.wave_D(cfg, _prior())
    resumed = C.wave_D(cfg, _prior() + [_row("drep0", "RELAY", 0.99, "D"),
                                        _row("drep1", "HOLD", 0.99, "D")])
    assert _ids(first) == _ids(resumed)


def test_first_attempt_unchanged():
    """Neutrality: with no D rows present (the C1 case) the specs are the
    promoted() order exactly as before."""
    cfg = C.CampaignConfig()
    specs = C.wave_D(cfg, _prior())
    prom = C.promoted(cfg, _prior())
    adj = [s for s in specs if s["kind"] == "adjudicate"]
    assert [s["extra"]["source_cell"] for s in adj] == [r["cell_id"] for r in prom]
    assert len(specs) == len(prom) * (1 + cfg.d_reps)
