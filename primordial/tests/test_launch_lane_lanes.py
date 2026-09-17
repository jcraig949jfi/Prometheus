"""launch_lane.ps1 must accept exactly the lanes the contract defines.

Round 5 (09-15): lane R (predictor) was added to contract.LANES, but launch_lane.ps1 kept its own
ValidateSet without R. PowerShell rejected `-Lane R` before the script's first log line, the scheduled
task sat "Running" behind -NoExit, and the predictor never booted. This cost ~11 minutes of a pilot clock
that code does not extend. Two lane lists must not drift.
"""
from __future__ import annotations

import pathlib
import re

from primordial.core.contract import LANES

PS1 = pathlib.Path(__file__).resolve().parents[1] / "ops" / "launch_lane.ps1"


def test_launch_lane_validateset_equals_contract_lanes():
    text = PS1.read_text(encoding="utf-8")
    m = re.search(r"ValidateSet\(([^)]*)\)\]\[string\]\$Lane", text)
    assert m, "launch_lane.ps1 must declare a ValidateSet on -Lane"
    ps1_lanes = set(re.findall(r"'([A-Z])'", m.group(1)))
    assert ps1_lanes == set(LANES), f"ps1 {sorted(ps1_lanes)} != contract {sorted(LANES)}"
