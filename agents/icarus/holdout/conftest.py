"""
Holdout test bootstrap. The candidate reasoner under test is located via the
ICARUS_CANDIDATE_DIR environment variable, set by tdd_runner at invocation
time. This keeps the holdout tests FROZEN (they live outside any cycle dir)
while pointing them at whichever candidate is being evaluated.
"""
import os
import sys

_cand = os.environ.get("ICARUS_CANDIDATE_DIR")
if _cand and _cand not in sys.path:
    sys.path.insert(0, _cand)
