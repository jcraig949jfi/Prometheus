"""B93 -- hand ladder: does a COORDINATING signal pay the group? (follow-up to B92)

B92: a 'richest pool' signal is near zero-sum (group +.008). Listeners converge on the scout's pool; the scout loses .20.
Here the scout harvests the richest pool i but signals a DIFFERENT pool, (i+1) mod 3, so listeners spread away from it.
Same world, groups and held-out scoring as B92.
  SCOUT_OTHER + 3 LISTENER  vs  SILENT + 3 LISTENER (B92 baseline, mean .266)  vs  SCOUT + 3 LISTENER (B92, .274)
PREDICTION (committed before running):
- the SCOUT_OTHER+3L group mean exceeds SILENT+3L by >= .02;
- the scout's own reward is >= .9 x SILENT's (.708) -- coordination costs the scout little.
If both hold, there is a world where honest coordination signalling pays both the group and (nearly) the signaller:
a precondition for testing whether communication evolves.
"""
import json
import sys
from pathlib import Path

from archaeon.beta.b01_w2k2_existence import HALT, IN, JZ, LDC, MOV, OUT_, _prog
import archaeon.beta.b92_signal_ladder as B92

RES = Path(__file__).resolve().parent / "results"
ADD, EQ, LT = 7, 16, 17


def scout_other():
    return _prog([(IN, 1, 0), (IN, 2, 0), (IN, 3, 0), (LDC, 4, 0), (MOV, 5, 1),
                  (LT, 6, 5, 2), (JZ, 6, 3), (MOV, 5, 2), (LDC, 4, 1),
                  (LT, 6, 5, 3), (JZ, 6, 3), (MOV, 5, 3), (LDC, 4, 2),
                  (OUT_, 4, 0),
                  (LDC, 7, 1), (ADD, 8, 4, 7), (LDC, 9, 3), (EQ, 6, 8, 9), (JZ, 6, 2), (LDC, 8, 0),
                  (ADD, 8, 8, 7), (OUT_, 8, 9), (HALT,)])


def main():
    w, s = B92.world()
    O, Q, S, L = B92.man(scout_other()), B92.man(B92.scout(False)), B92.man(B92.scout(True)), B92.man(B92.LISTENER)
    def avg(ms):
        v = [B92.group(ms, w, s + 1000 + k, 16) for k in range(4)]
        return [round(sum(x[i] for x in v) / 4, 4) for i in range(len(ms))]
    rows = {"SCOUT_OTHER+3L": avg([O, L, L, L]), "SILENT+3L": avg([Q, L, L, L]), "SCOUT+3L": avg([S, L, L, L])}
    for k, v in rows.items():
        print(k, v, "mean", round(sum(v) / len(v), 4), flush=True)
    m = lambda k: sum(rows[k]) / len(rows[k])
    pred = {"coord_pays_group": m("SCOUT_OTHER+3L") - m("SILENT+3L") >= .02, "coord_cheap_for_scout": rows["SCOUT_OTHER+3L"][0] >= .9 * rows["SILENT+3L"][0]}
    print(json.dumps(pred))
    (RES / "B93_result.json").write_text(json.dumps({"probe": "B93", "rows": rows, "pred": pred}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
