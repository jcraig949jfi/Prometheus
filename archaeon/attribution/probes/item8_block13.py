"""Directive item 8: the ~16% 'material without capacity' births of block 13 (BLOCK_128 arm) followed forward. Replaces the
item-8 tracking in th013_block13, which had two defects (TH013_RESULT.md s4):
- it tracked ALL of a child's material ids, which are mostly lineage material shared with its parent;
- it matched copier classes by wrong names.

Design:
- Sample: from epoch T0, every 40th birth is checked with the frozen copier ruler.
  * Up to NMAX non-copier children are tracked.
  * Up to NMAX copier children are tracked as the CONTRAST group.
- Descent: every cell carries the set of tracked ancestors it descends from. A child inherits the tags of its TEMPLATE cell:
  whichever of executor / overwritten occupant supplied more of its material ids, measured before the overwrite.
- Birth-created material: the ids first created in that birth (mutation / input / constant / computed).
- Fate at the end (per tracked child):
  * DEAD_ON_ARRIVAL: never a template for any birth;
  * TRANSIENT: had descendants, none alive at the end;
  * PERSISTS_NO_CAPABILITY: descendants alive, none of the sampled (<= 5) is a copier;
  * CAPABILITY_IN_DESCENDANTS: descendants alive and some sampled descendant is a copier.
  Also reported: how many of its birth-created ids live in NON-descendants (moved by recombination / host writes), and in how
  many cells.
Usage:
    python -m archaeon.attribution.probes.item8_block13 OUT.json [--until 20000]
"""
import json
import sys
import time
from collections import Counter

from archaeon.lineage import core as LC
from archaeon.lineage import assay_block as AB
from archaeon.envgate import mechanism as M1
from archaeon.envgate import ruler as R

T0 = 13900; NMAX = 300; EVERY = 40


class Obs(LC.World):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.tags = {}; self.track = {}; self.ncheck = Counter(); self.ever_desc = Counter(); self.series = []

    def _birth(self, i, j, child, res0, nbr, x, epoch):
        oi = set(self.orig[i] or ()); oj = set(self.orig[j] or ()) if self.genomes[j] is not None else set()
        ti = self.tags.get(i, frozenset()); tj = self.tags.get(j, frozenset()) if self.genomes[j] is not None else frozenset()
        mat0 = self.next_mat
        super()._birth(i, j, child, res0, nbr, x, epoch)
        o = self.orig[j]; ce = sum(1 for m in o if m in oi); cn = sum(1 for m in o if m in oj)
        tags = ti if ce >= cn else tj
        if ce == 0 and cn == 0: tags = frozenset()
        for t in tags: self.ever_desc[t] += 1
        self.tags[j] = tags
        if epoch >= T0 and self.births % EVERY == 0:
            cls = R.measure(bytes(child))["class"]; grp = "copier" if cls in R.HIT else "noncopier"
            self.ncheck[grp] += 1
            if sum(1 for t in self.track.values() if t["group"] == grp) < NMAX:
                k = self.oid[j]
                new = [m for m in o if m is not None and m < 0 and (-m) // 8 >= mat0]
                self.track[k] = {"epoch": epoch, "group": grp, "class": cls, "glin": self.glin[j], "mech_template_exec": ce >= cn,
                                 "new_ids": new, "n_new": len(new)}
                self.tags[j] = tags | {k}

    def census(self, epoch):
        alive = [c for c in range(LC.N) if self.genomes[c] is not None]
        d = Counter(t for c in alive for t in self.tags.get(c, ()))
        self.series.append((epoch, {g: sum(1 for k, t in self.track.items() if t["group"] == g and d[k]) for g in ("copier", "noncopier")},
                            {g: sum(1 for t in self.track.values() if t["group"] == g) for g in ("copier", "noncopier")}))


def main(out_path, until):
    t0 = time.time(); AB.World = Obs; orig_step = Obs.step
    def step(self, epoch, memo):
        orig_step(self, epoch, memo)
        if epoch % 200 == 0 and epoch >= T0: self.census(epoch)
    Obs.step = step
    try:
        r = AB.run_block("envgate", 13, {"K_chambers": 2048, "dwell": 64, "refills": 1024}, {"BLOCK_128": M1.ARMS["BLOCK_128"]},
                         until_epoch=until, keep_worlds=True)
    finally:
        AB.World = LC.World
    w = r["arms"]["BLOCK_128"]["_world"]; alive = [c for c in range(LC.N) if w.genomes[c] is not None]
    desc = {}
    for c in alive:
        for t in w.tags.get(c, ()): desc.setdefault(t, []).append(c)
    cache = {}
    def cls(c):
        tp = bytes(w.genomes[c])
        if tp not in cache: cache[tp] = R.measure(tp)["class"]
        return cache[tp]
    fates = {"copier": Counter(), "noncopier": Counter()}; rows = []
    for k, t in w.track.items():
        ds = desc.get(k, [])
        if not w.ever_desc[k] and not ds: f = "DEAD_ON_ARRIVAL"
        elif not ds: f = "TRANSIENT"
        else: f = "CAPABILITY_IN_DESCENDANTS" if any(cls(c) in R.HIT for c in ds[:5]) else "PERSISTS_NO_CAPABILITY"
        new = set(t["new_ids"])
        holders = [c for c in alive if new & set(w.orig[c])] if new else []
        nondesc = [c for c in holders if c not in set(ds)]
        fates[t["group"]][f] += 1
        rows.append({"oid": k, "group": t["group"], "class": t["class"], "epoch": t["epoch"], "fate": f, "ever_descendants": w.ever_desc[k],
                     "alive_descendants": len(ds), "n_new": t["n_new"], "new_id_holders": len(holders), "new_id_holders_nondescendant": len(nondesc),
                     "template_exec": t["mech_template_exec"]})
    out = {"probe": "item8 block13", "until": until, "wall_s": round(time.time() - t0, 1), "births": w.births, "checked": dict(w.ncheck),
           "fates": {g: dict(v) for g, v in fates.items()}, "series": w.series, "rows": rows}
    json.dump(out, open(out_path, "w"))
    print(json.dumps({"wall_s": out["wall_s"], "checked": out["checked"], "fates": out["fates"]}))


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--t0" in a: T0 = int(a[a.index("--t0") + 1])                         # smoke tests only
    main(a[0], int(a[a.index("--until") + 1]) if "--until" in a else 20000)
