"""B118e -- constant-twin INFORMATION check for B118d type readers (the B115 lesson applied to type words).

Zeroing the type words (Blind) measures DEPENDENCE. Information = lift(full) - max over c in {0, 1} of lift with
EVERY type word replaced by c. A constant type word carries no information about which pool is toxic.
Calibration: CHK3 must show info > .02; GEN3 info ~ 0.
Applied to every saved B118d best genome. Readout defined 04:30Z after seeing 2 TOXIC cells; it is a robustness
check on the prereg readout, not a replacement (both are reported).
"""
import json
import sys
from pathlib import Path

from archaeon.beta.b118_toxic import lift
from archaeon.beta.b118c_interleaved import chk, gen
from archaeon.beta.b118d_seeded_forager import heldout

OUT = Path(__file__).resolve().parent / "results" / "B118d_seeded_forager"


class ConstType:
    def __init__(self, w, c):
        self.w = w; self.c = c; self.K = w.K; self.features = getattr(w, "features", None)

    def __getattr__(self, k):
        return getattr(self.w, k)

    def observe(self, st):
        obs = self.w.observe(st); R = self.w.w.w.R; ch = list(obs[0])
        for i in range(R):
            ch[2 * i + 1] = self.c
        return [ch] + obs[1:]


def info(m, ho):
    full = sum(lift(m, w, s) for w, s in ho) / len(ho)
    consts = {c: sum(lift(m, ConstType(w, c), s) for w, s in ho) / len(ho) for c in (0, 1)}
    return {"full": round(full, 4), "const0": round(consts[0], 4), "const1": round(consts[1], 4), "info": round(full - max(consts.values()), 4)}


def main(argv):
    ho = heldout(); rows = {"CHK3": info(chk(3), ho), "GEN3": info(gen(3), ho)}
    print("CHK3", rows["CHK3"], "GEN3", rows["GEN3"], flush=True)
    for f in sorted(OUT.glob("best_*.json")):
        rows[f.stem] = info(json.loads(f.read_text(encoding="utf-8")), ho); print(f.stem, rows[f.stem], flush=True)
    (OUT / "B118e_type_info.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
