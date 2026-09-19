"""The power register (roles/Bellerophon/science/POWER_REGISTER_2026-09-19.md) names, for every kernel instrument,
the test in which it says NO. This test keeps the register honest: every `test_file::test_name` it cites must exist
in the suite (C98). A register that cites a deleted test is decoration too."""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[3]
REGISTER = ROOT / "roles/Bellerophon/science/POWER_REGISTER_2026-09-19.md"
TESTS = pathlib.Path(__file__).resolve().parent


def test_every_cited_test_exists():
    text = REGISTER.read_text(encoding="utf-8")
    cited = set(re.findall(r"(test_[a-z0-9_]+)::(test_[a-z0-9_]+)", text))
    assert len(cited) >= 25, "the register lost its citations"
    missing = []
    for mod, fn in sorted(cited):
        src = TESTS / (mod + ".py")
        if not src.exists() or ("def %s(" % fn) not in src.read_text(encoding="utf-8"):
            missing.append("%s::%s" % (mod, fn))
    assert missing == [], "power register cites tests that do not exist: %s" % missing
