"""Deep block probe (TH-007 cargo vs machinery; TH-009 capacity transmission) on ONE deterministic replay: ENVGATE-01 block 13,
BLOCK_128 arm, to epoch 14,800 (the same fossil as PORTABILITY-01 A4). The frozen engine is untouched; a World subclass observes.

TH-007  at the end, for the dominant genetic lineage: per genome position, the fraction of living members whose byte at that position is
        still the FOUNDER's own material (material id == founder_fid*32 + position). "Machinery" positions = the addresses the FOUNDER
        executes when it copies (vm.execute(...)["executed"] on its birth input); "cargo" = all other positions.
TH-009  for a systematic sample of births (every 25th, plus every non-SELF_COPY birth): the child tape is classified with the FROZEN
        copier ruler (archaeon/envgate/ruler.py measure). Capacity transmitted = the child is a HIT-class copier on its own.
    python -m archaeon.causal_lens.deep_block.block13_probe OUT.json      (from a checkout root; stdlib + repo only)
"""
import json
import sys
import time
from collections import Counter

from archaeon.lineage import core as LC
from archaeon.lineage import assay_block as AB
from archaeon.envgate import mechanism as M1
from archaeon.envgate import ruler as R
from archaeon.z80atlas import vm

SAMPLE = []


class Obs(LC.World):
    def _birth(self, i, j, child, res0, nbr, x, epoch):
        before = dict(self.births_mech)
        super()._birth(i, j, child, res0, nbr, x, epoch)
        mech = next((m for m, c in self.births_mech.items() if c != before.get(m, 0)), "?")
        if self.births % 25 == 0 or not mech.startswith("SELF_COPY"):
            SAMPLE.append((mech, bytes(self.genomes[j]), self.glin[j], self.glin[i]))


def main(out_path):
    t0 = time.time(); AB.World = Obs
    try:
        r = AB.run_block("envgate", 13, {"K_chambers": 2048, "dwell": 64, "refills": 1024}, {"BLOCK_128": M1.ARMS["BLOCK_128"]},
                         until_epoch=14800, keep_worlds=True)
    finally:
        AB.World = LC.World
    w = r["arms"]["BLOCK_128"]["_world"]; wall = time.time() - t0
    dom = max(w.alive.items(), key=lambda kv: kv[1])[0]; st = w.gl[dom]; fid = st.get("founder_oid")
    members = [c for c in range(LC.N) if w.genomes[c] is not None and w.glin[c] == dom]
    founder_tape = bytes.fromhex(st["tape"]) if st.get("tape") else None
    fx = st.get("first_birth_input") or 0
    exe = vm.execute(founder_tape, LC.ZERO, (fx,), LC.STEP_CAP, True, -1.0)["executed"] if founder_tape else None
    machinery = [p for p in range(LC.G) if exe and exe[p]]
    share = [sum(1 for c in members if w.orig[c][p] == fid * 32 + p) / max(1, len(members)) for p in range(LC.G)]
    th007 = {"dominant_glin": dom, "founder_oid": fid, "arrival": st.get("arrival"), "members_alive": len(members),
             "machinery_positions": machinery, "per_position_founder_share": [round(s, 3) for s in share],
             "machinery_mean_share": round(sum(share[p] for p in machinery) / max(1, len(machinery)), 3) if machinery else None,
             "cargo_mean_share": round(sum(share[p] for p in range(LC.G) if p not in machinery) / max(1, LC.G - len(machinery)), 3)}
    memo = LC.Memo(True); cap = Counter(); tot = Counter()
    for mech, tape, cg, eg in SAMPLE:
        cls = R.measure(tape)["class"]; key = mech.split("+")[0]
        tot[key] += 1; cap[key] += cls in R.HIT
    th009 = {"sampled_births": len(SAMPLE), "by_mechanism": {m: {"n": tot[m], "child_is_copier": cap[m], "frac": round(cap[m] / tot[m], 3)} for m in tot}}
    out = {"probe": "deep_block block13", "wall_s": round(wall, 1), "births": w.births, "TH-007": th007, "TH-009": th009}
    json.dump(out, open(out_path, "w"), indent=1)
    print(json.dumps({"wall_s": out["wall_s"], "births": w.births, "TH-007": {k: th007[k] for k in ("members_alive", "machinery_positions", "machinery_mean_share", "cargo_mean_share")}, "TH-009": th009}))


if __name__ == "__main__":
    main(sys.argv[1])
