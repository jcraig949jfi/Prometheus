"""B93b -- hand ladder in a NON-RIVAL information world. (follow-up to B92/B93)

B92/B93: in the regenerating world the group's total is capped by regeneration, so any signal only REDISTRIBUTES
(group gain <= .008) and costs the scout ~.2 -- zero-sum. Here pools are STATIC (deplete = 0, regen = 0): each
episode draws pool amounts (1.0-1.75) that do not change, so every agent on the richest pool gains fully and the scout
loses nothing when others join it.
Same groups, programs and held-out scoring as B92.
PREDICTION (committed before running):
- SCOUT+3 LISTENER group mean exceeds SILENT+3 LISTENER by >= .05;
- the scout's own reward is >= .95 x SILENT's.
If both hold, this world makes honest signalling free for the signaller and valuable for the group. The evolution
question then becomes whether signalling evolves under individual vs group (shared) reward.
"""
import copy
import json
import sys
from pathlib import Path

from archaeon.beta.b25_noclock_world import NoClock
from archaeon.campaign6.worlds.runtime import ComposedWorld
import archaeon.beta.b92_signal_ladder as B92

RES = Path(__file__).resolve().parent / "results"


def world_static():
    c = json.loads((RES / "B71_world.json").read_text(encoding="utf-8")); p = copy.deepcopy(c["params"])
    p["locality"] = {"on": False}; p["resources"] = dict(p["resources"], deplete=0.0, regen=0.0)
    return NoClock(ComposedWorld(p)), c["seed"]


def main():
    w, s = world_static()
    S, Q, L = B92.man(B92.scout(True)), B92.man(B92.scout(False)), B92.man(B92.LISTENER)
    def avg(ms):
        v = [B92.group(ms, w, s + 1000 + k, 16) for k in range(4)]
        return [round(sum(x[i] for x in v) / 4, 4) for i in range(len(ms))]
    rows = {"SCOUT+3L": avg([S, L, L, L]), "SILENT+3L": avg([Q, L, L, L]), "solo_SCOUT": avg([S]), "solo_LISTENER_nosignal": avg([L])}
    for k, v in rows.items():
        print(k, v, "mean", round(sum(v) / len(v), 4), flush=True)
    m = lambda k: sum(rows[k]) / len(rows[k])
    pred = {"signal_pays_group_ge_.05": m("SCOUT+3L") - m("SILENT+3L") >= .05, "free_for_scout": rows["SCOUT+3L"][0] >= .95 * rows["SILENT+3L"][0]}
    print(json.dumps(pred))
    (RES / "B93b_result.json").write_text(json.dumps({"probe": "B93b", "rows": rows, "pred": pred}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
