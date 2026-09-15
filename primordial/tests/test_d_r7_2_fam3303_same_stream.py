"""D-R7-2: both axes and the planted controls on synthetic rows (the committed-row read is the job's)."""
from primordial.cohorts.d import r7_2_fam3303_same_stream as D

FLOOR = 166.46875


def rows(base_low=None, uses_low=True):
    """32 same-stream pairs; candidate below floor exactly at the filed 3303 keys with the filed values."""
    cand, base = [], []
    for f in D.ORDER:
        for rs in range(8):
            k = (f, rs)
            cv = D.FILED_LOW.get(k, 190.0 + rs)
            bv = (base_low if base_low is not None else 180.0 + rs) if k in D.FILED_LOW else 175.0 + rs + f % 7
            seed = [f + 1, rs, 13, 128]
            cand.append({"rng_family": f, "run_seed": rs, "held64_per_seed": cv, "sampler_seed": seed,
                         "control_obs_use": {"uses_observations": uses_low if k in D.FILED_LOW else True,
                                             "held64_w_zeroed": 100.0}})
            base.append({"rng_family": f, "run_seed": rs, "held64_per_seed": bv, "sampler_seed": seed})
    return cand, base


def test_shared_stream_and_obs_used():
    cand, base = rows(base_low=150.0)
    out = D.analyse(cand, base, FLOOR)
    assert out["decision"] == "SHARED_STREAM+OBS_USED" and out["stats"]["q_low_in_baseline_bottom8"] == 3


def test_not_stream_and_obs_unused():
    cand, base = rows(base_low=250.0, uses_low=False)
    assert D.analyse(cand, base, FLOOR)["decision"] == "NOT_STREAM+OBS_UNUSED"


def test_mixed_stream():
    cand, base = rows(base_low=250.0)
    for b in base:
        if (b["rng_family"], b["run_seed"]) in ((3303, 2), (3303, 6)):
            b["held64_per_seed"] = 150.0
    assert D.analyse(cand, base, FLOOR)["decision"].startswith("MIXED_STREAM+")


def test_controls_bind_and_i1():
    cand, base = rows()
    out = D.analyse(cand, base, FLOOR)
    assert out["checks"]["controls_ok"] and out["decision"] != "INDETERMINATE"
    cand[0]["held64_per_seed"] = 100.0                         # a fourth low run, not as filed
    assert D.analyse(cand, base, FLOOR)["decision"] == "INDETERMINATE"
    cand, base = rows()
    base[1]["sampler_seed"] = [0, 0, 0, 0]
    assert D.analyse(cand, base, FLOOR)["decision"] == "INDETERMINATE"
    cand, base = rows()
    assert D.analyse(cand, base, FLOOR, by_run=[0.0] * 32)["decision"] == "INDETERMINATE"


def test_obs_mixed():
    cand, base = rows()
    for c in cand:
        if (c["rng_family"], c["run_seed"]) == (3303, 2):
            c["control_obs_use"]["uses_observations"] = False
    assert D.analyse(cand, base, FLOOR)["stats"]["obs"] == "OBS_MIXED"
