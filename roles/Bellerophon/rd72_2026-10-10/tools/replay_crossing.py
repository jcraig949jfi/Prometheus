"""BEL-RD-72: deterministic replay of the F2 crossing world under byte tags (EXPLORATORY forensics, post hoc).
    python3 replay_crossing.py F2_PLAN F2_RESULTS RUN_ID OUT.json
Runs HalvesWorld (byte-origin tags) with the SAME paired-halves payment wrapper as tools/paired_pay.py (identical
code path and rng derivation) to the original's first FUNC-BOTH census tick. Validity: alive and FUNC-halves counts must
equal the original light census at every common tick. Output: the first FUNC BOTH event (birth or census), its
critical-byte anatomy (founder bytes vs later changes, by tick), and the census."""
import json, random, sys, pathlib
_H = pathlib.Path(__file__).resolve()
for _p in (_H.parent, _H.parents[1].parent / "bel48h_2026-10-08" / "tools", _H.parents[4]):
    sys.path.insert(0, str(_p))
from halves import HalvesWorld
from paired_pay import PairedPayWorld
from prometheus.z80atlas.world import Config


class PairedHalvesWorld(HalvesWorld):
    _ok = PairedPayWorld._ok

    def __init__(self, cfg, seed, census_every=100):
        super().__init__(cfg, seed, census_every=census_every)
        self.pp_rng = random.Random(seed ^ 0x5A5A_0F0F); self.pp = {"pp_correct": 0, "pp_denied": 0}
        inner = self.ledger.after_interaction

        def wrapped(world, o, task, inputs, outputs, fos, fis, correct):
            if correct:
                self.pp["pp_correct"] += 1
                x = inputs[0]
                y = self.pp_rng.randrange(128) if x >= 128 else 128 + self.pp_rng.randrange(128)
                if not self._ok(self._pre_tape, y):
                    correct = False; self.pp["pp_denied"] += 1
            return inner(world, o, task, inputs, outputs, fos, fis, correct)
        self.ledger.after_interaction = wrapped


def main(planp, resp, rid, outp):
    p = next(x for x in json.load(open(planp)) if x["id"] == rid)
    r = next(json.loads(l) for l in open(resp) if json.loads(l)["id"] == rid)
    t_end = next(c["tick"] for c in r["census"] if (c.get("halves_func") or {}).get("BOTH"))
    cfg = Config(**dict(p["cfg"], ticks=t_end))
    w = PairedHalvesWorld(cfg, p["seed"], census_every=100); w.run()
    orig = {c["tick"]: (c["alive"], c.get("halves_func")) for c in r["census"]}
    mism = [c["tick"] for c in w.census if c["tick"] in orig and (c["alive"], c["halves_func"]) != orig[c["tick"]]]
    out = {"id": rid, "replayed_to": t_end, "census_mismatch_ticks": mism, "valid": not mism, "first_both": w.first_both,
           "census": w.census, "pp": w.pp}
    json.dump(out, open(outp, "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in out.items() if k != "census"}, indent=1, default=str)[:6000])


if __name__ == "__main__":
    main(*sys.argv[1:5])
