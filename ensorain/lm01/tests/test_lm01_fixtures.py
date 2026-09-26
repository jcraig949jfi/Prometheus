import numpy as np

from ensorain.lm01.fixtures import calibrate


def test_instrument_separates_lossless_selective_blind():      # directive s11
    o = calibrate()
    assert o["PASS"], {k: v["verdict"] for k, v in o.items() if isinstance(v, dict)}


def test_D4_absolute_selectivity_readout_is_not_a_certificate():
    o = calibrate(n=6000)                                   # revisit-heavy: 11.7 visits/cell
    fb = o["F-B"]
    assert fb["HR2_signal"] - fb["HR2"] > 0.02          # a blind merge "looks selective" in absolute terms
    assert fb["verdict"] == "BLIND_LOSS"                 # ...and reads blind against the rate-matched reference
