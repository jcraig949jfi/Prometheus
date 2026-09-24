"""
Test-infrastructure only (not production code, not a test oracle):
makes the `production` package (Aether/production/) importable from
any test module in this directory, regardless of pytest's invocation
cwd. `reference` (Aether/test/reference/) is already importable via
pytest's normal rootdir-insertion for files collected directly under
Aether/test/; this file does not change that.
"""

import os
import sys

_AETHER_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _AETHER_ROOT not in sys.path:
    sys.path.insert(0, _AETHER_ROOT)
