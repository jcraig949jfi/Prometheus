"""sys.path bootstrap for the W5P package. Import first.

Adds the same directories the v2b layer uses (v2b, engine, engine/accel, science/compounding/rb1). It does NOT set any
environment flag itself and imports no engine module: importing order matters for the v2b harness (t51_natural sets
A18_TAG=T51 before a18 is first imported; cell labels depend on it), so the harness controls that, not this file.
"""
import sys
from pathlib import Path

W5P = Path(__file__).resolve().parent
ENG = W5P.parent
V2B = ENG / "v2b"
ROOT = ENG.parent                                   # roles/Aphrodite
RB1 = ROOT / "science" / "compounding" / "rb1"

for p in (RB1, ENG / "accel", ENG, V2B):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
