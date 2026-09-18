"""Campaign 0B generator checks: the pathologies preserve mean effects and the assay is unchanged."""
import hashlib
import random
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import worlds_0b as W0B  # noqa: E402

HERE = Path(__file__).resolve().parents[1]


def test_family_multipliers_have_mean_one_and_change_sign():
    assert abs(sum(W0B.FAMILY_MULT) / len(W0B.FAMILY_MULT) - 1.0) < 1e-12
    assert min(W0B.FAMILY_MULT) < 0 < max(W0B.FAMILY_MULT)


def test_jackpot_preserves_mean_and_null_is_mean_zero():
    assert abs(W0B.JACKPOT_P * W0B.JACKPOT_X - 1.0) < 1e-12
    assert abs(W0B.JACKPOT_P * 1.0 + (1 - W0B.JACKPOT_P) * (-1.0 / 9.0)) < 1e-12


def test_student_t_is_heavy_tailed_and_centred():
    rng = random.Random(3)
    xs = [W0B.student_t(rng) for _ in range(40000)]
    assert abs(statistics.median(xs)) < 0.05
    assert sum(abs(x) > 4 for x in xs) / len(xs) > 0.01  # a normal gives ~6e-5


def test_campaign0_generator_and_assay_are_untouched():
    # the files the 0B run relies on must be byte-identical to the Campaign 0 code commit
    import subprocess
    for f in ("assay.py", "worlds.py"):
        head = subprocess.run(["git", "show", f"6195af410:roles/Aphrodite/science/campaign0/{f}"],
                              capture_output=True, cwd=HERE).stdout
        now = (HERE / f).read_bytes().replace(b"\r\n", b"\n")
        assert hashlib.sha256(head.replace(b"\r\n", b"\n")).hexdigest() == hashlib.sha256(now).hexdigest(), f
