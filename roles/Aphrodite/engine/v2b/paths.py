"""sys.path bootstrap for the v2b layer. Import this first. It sets the fast-path flags the frozen engine
gates itself on (A17_FASTEVAL, A18_FASTCOST). Both were admitted by their differential gates and are re-checked
by v2b conformance."""
import os
import sys
from pathlib import Path

V2B = Path(__file__).resolve().parent
ENG = V2B.parent
ROOT = ENG.parent                                   # roles/Aphrodite
RB1 = ROOT / "science" / "compounding" / "rb1"

os.environ.setdefault("A17_FASTEVAL", "1")
os.environ.setdefault("A18_FASTCOST", "1")
os.environ.setdefault("A18_TAG", "V2B")
for p in (V2B, ENG, ENG / "accel", RB1):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
