"""A reduced generator CONFIG for fast tests (fewer mechanisms / families). Production uses generator.CONFIG."""
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import generator as G        # noqa: E402

SMALL = copy.deepcopy(G.CONFIG)
SMALL["mechanisms"] = {"f": 1, "p": 1, "s": 1}
SMALL["quota"] = {"R0": 3, "R1_per_mech": 2, "R2": 3, "R3": 3, "R4": 2, "R5": 2}
SMALL["mech_screen"]["regression_attempts_max"] = 30
TEST_SEED = "test-only-seed-not-a-world-seed-0001"
