"""thr-c64dca3118a1 recurrence test in the worlds that were actually taken over. ENVGATE-01's LINEAGES.json labels takeovers by
the parent chain (the host's arrival), so it cannot say which MATERIAL founder the takeover genome descends from.

This replays one block/arm with the frozen engine (an observer only). Every CHECK epochs it records the top-3 genetic lineages
(glin: material-majority descent) by living cells. For each one:
- the founder's tape, frozen-ruler class, whether it is an exact self-copier, and whether its copy map reaches one (orbit depth,
  as in fixedpoint_census);
- the first-birth epoch and mechanism;
- the frozen-ruler class of up to 8 living members.
    python -m archaeon.attribution.probes.dominant_founders OUT.json --block 15 --arm U [--until 30000] [--check 2000]
"""
import json
import sys
import time
from collections import Counter

from archaeon.lineage import core as LC
from archaeon.lineage import assay_block as AB
from archaeon.envgate import mechanism as M1
from archaeon.envgate import ruler as R
from archaeon.attribution.probes.fixedpoint_census import orbit

CHECK = 2000


def top(w, epoch):
    alive = Counter(w.glin[c] for c in range(LC.N) if w.genomes[c] is not None and w.glin[c] >= 0)
    out = []
    for g, n in alive.most_common(3):
        st = w.gl[g]; ft = bytes.fromhex(st["tape"]) if st.get("tape") else None
        mem = [c for c in range(LC.N) if w.genomes[c] is not None and w.glin[c] == g][:8]
        rec = {"glin": g, "alive": n, "root": st.get("root"), "origin": st.get("origin"), "arrival": st.get("arrival"),
               "founder_oid": st.get("founder_oid"), "first_birth_epoch": st.get("first_birth_epoch"), "first_birth_mech": st.get("first_birth_mech"),
               "births": st.get("births"), "births_hosted": st.get("births_hosted"), "member_classes": dict(Counter(R.measure(bytes(w.genomes[c]))["class"] for c in mem))}
        if ft:
            rec["founder_tape"] = ft.hex(); rec["founder_class"] = R.measure(ft)["class"]; rec["orbit"] = orbit(ft, 3, 16)
        out.append(rec)
    return {"epoch": epoch, "top": out}


def main(out, block, arm, until):
    t0 = time.time(); snaps = []
    class Obs(LC.World):
        pass
    orig = Obs.step
    def step(self, epoch, memo):
        orig(self, epoch, memo)
        if epoch % CHECK == 0 and epoch > 0: snaps.append(top(self, epoch))
    Obs.step = step; AB.World = Obs
    try:
        r = AB.run_block("envgate", block, {"K_chambers": 2048, "dwell": 64, "refills": 1024}, {arm: M1.ARMS[arm]}, until_epoch=until, keep_worlds=True)
    finally:
        AB.World = LC.World
    w = r["arms"][arm]["_world"]
    json.dump({"block": block, "arm": arm, "until": until, "wall_s": round(time.time() - t0, 1), "births": w.births,
               "births_by_mechanism": dict(w.births_mech), "snaps": snaps}, open(out, "w"), indent=1)
    print(json.dumps({"wall_s": round(time.time() - t0, 1), "births": w.births, "last": snaps[-1] if snaps else None}, indent=1)[:3000])


if __name__ == "__main__":
    a = sys.argv[1:]
    g = lambda k, d: a[a.index(k) + 1] if k in a else d
    CHECK = int(g("--check", 2000))
    main(a[0], int(g("--block", 15)), g("--arm", "U"), int(g("--until", 30000)))
