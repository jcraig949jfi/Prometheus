"""H-IMPL regression: engine.Controls.label().

label() tests `getattr(self, f) not in (False, (), None, -1)`: with a
reset_state_mask array the tuple membership test compares elementwise and
raises ValueError, and distractor_chan=0 is hidden because 0 == False.
FAILS on the current code, PASSES with patches/controls_label_mask.diff.
label() feeds no frozen result (no caller in prometheus/ananke).
"""
import numpy as np

from prometheus.ananke.engine import Controls


def test_label_with_reset_mask_does_not_raise():
    c = Controls(reset_state_at=(3,), reset_state_mask=np.ones((2, 8), bool))
    lab = c.label()
    assert "reset_state_at" in lab and "reset_state_mask" in lab


def test_distractor_channel_zero_is_labelled():
    assert Controls(distractor_chan=0).label() == "distractor_chan"


def test_legacy_labels_unchanged():
    assert Controls().label() == "none"
    assert Controls(zero_comm=True).label() == "zero_comm"
    assert Controls(distractor_chan=1).label() == "distractor_chan"
    assert Controls(drop_packets_at=(1, 2)).label() == "drop_packets_at"
    assert Controls(reset_state_at=(1,), reset_parts=("S", "inbox")).label() == \
        "reset_state_at+reset_parts=S,inbox"
