"""POST-HOC probe P3 (labelled, unscored; written AFTER S5 was observed, committed BEFORE it runs). C-016-T040, Pallas.

S5 (learns_pre, theta0 = -0.1) came out REVISION_NOT_SHOWN, not the predicted REVISION_HISTORY_DEPENDENT: its FROZEN arm
is the -s policy, i.e. the Smuggler, which is perfect on the late window, so K1 (full vs frozen, late) is lost on
every pair although the full arm learns the pre-switch law in-life and revises it at the switch. K1 therefore measures
"the plastic configuration beats its own INNATE configuration on the late window", not world demand: trivial when the
innate value is on the pre-switch side (B1: noise suffices), impossible when it is on the post-switch side (S5).
This probe completes the trichotomy with the innate value at ZERO (theta0 = 0.0: the frozen arm acts +1 at every gate,
chance on both laws).

PREDICTION (before running): innate_zero at the 200 challenge seeds -> G_PRE holds (block 0 at chance, then the law is
learned), K1 wins a clear but not total majority (frozen late = 1/2 against a learned ~.6: roughly 120-160 of 200),
K2 significant, verdict REVISION_HISTORY_DEPENDENT. The three innate positions then give REVISION_NOT_HISTORY_DEPENDENT
(noise, B1), REVISION_HISTORY_DEPENDENT (zero) and REVISION_NOT_SHOWN (learned, S5) for the SAME learning rule.

    python -B rso/ensorain/challenge/posthoc_p3.py
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rso.ensorain.challenge import cases, subjects_c as C      # noqa: E402

if __name__ == "__main__":
    rows, v, sec = cases.run_subject("innate_zero", C.ref_like(0.0, 1.0, 0.5), C.N_DEV)
    cases.emit("POSTHOC_P3_INNATE_ZERO", kind="posthoc_probe", n=C.N_DEV, seconds=sec, **cases.summary(v),
               scored="RECORDED_POSTHOC")
