"""B114 -- NO-LATTICE control for the B111/B113 copy-and-hash codes.

B113: B111's from-scratch codes copy pool 0's raw magnitude into the listeners' action. The world decodes
action % 3, and the static pools sit on a lattice {.1,1.1,2.1,3.0} whose milli-values have residues {1,2,0,0}.
JSpread: the same world, but each pool gets a deterministic jitter in [0, .3) (keyed by seed, ep, pool). This keeps
the pool ORDER (lattice gaps are 1.0) and scrambles residues mod 3.
PREDICTION (committed before running), hash-dependence hypothesis:
- the hand COMPLETE code (richest+1) keeps an ablation drop > .15 under jitter;
- MUTE_OP stays at 0;
- the B111 private-code genomes (11101/11104/11105) drop to <= .03 each.
B114 RESULT: COMPLETE .213, MUTE_OP 0, B111 .021/.014/.020 -- MET.
B114b (same script, on the B103b best SHARED genomes): are the EARLIER positives also lattice exploits?
PREDICTION (committed before running): the three restored signallers (10311/10312/10314; hand SIGNALS .064/.165/.304)
keep an off-lattice ablation drop > .05 each; the three non-restored (10313/10315/10316) stay <= .03.
"""
import json
import sys
from pathlib import Path

from archaeon.beta.b97_signal_headroom import Spread, world_static
from archaeon.beta.b112_kin_scratch_rep import self_group


class JSpread(Spread):
    def reset(self, seed, ep, shared=None):
        first = shared is None or "pools" not in shared
        st = super().reset(seed, ep, shared)
        if first:
            st["pools"][:] = [a + ((seed * 7919 + ep * 104729 + j * 31) % 300) / 1000 for j, a in enumerate(st["pools"])]
            st["max_reward"] = max(1e-9, self.w.ticks * max(st["pools"]))
        return st


def jw():
    from archaeon.beta.b25_noclock_world import NoClock
    w, s = world_static(); return NoClock(JSpread(w.w)), s


def main(argv):
    import archaeon.beta.b92_signal_ladder as B92
    from archaeon.beta.b95_signal_restore import COMPLETE, MUTE_OP
    w, s = jw(); rows = {}
    progs = {"COMPLETE": B92.man(list(COMPLETE)), "MUTE_OP": B92.man(list(MUTE_OP))}
    for f in argv:
        progs[Path(f).stem] = json.loads(Path(f).read_text(encoding="utf-8"))
    for k, m in progs.items():
        a, b = self_group(m, w, s, False), self_group(m, w, s, True); rows[k] = {"full": round(a, 4), "ablated": round(b, 4), "drop": round(a - b, 4)}
        print(k, json.dumps(rows[k]), flush=True)
    priv = [v["drop"] for k, v in rows.items() if k.startswith("best_")]
    pred = rows["COMPLETE"]["drop"] > .15 and abs(rows["MUTE_OP"]["drop"]) < 1e-9 and all(d <= .03 for d in priv)
    out = Path(__file__).resolve().parent / "results" / "B114_nolattice"; out.mkdir(parents=True, exist_ok=True)
    (out / "B114_result.json").write_text(json.dumps({"probe": "B114", "rows": rows, "pred": pred}, indent=1), encoding="utf-8")
    print("pred", pred); return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
