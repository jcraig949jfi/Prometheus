"""TH-013 (+ directive item 8): function vs material through time in ONE lineage. One deterministic replay of ENVGATE-01 block 13
(BLOCK_128 arm) to epoch 20,000. The frozen engine is untouched; a World subclass observes.

It FIXES the deep-block probe defect: founder material is counted wherever it sits (any id f*32+q, with its source position q), not
only at the same position. The founder (arrival 447492) is a NEAR_COPIER that copies with an offset, so same-position counting read
0.0 falsely.

Every SNAP epochs after the tracked founder's lineage (glin) exists, for up to MEMB living members:
  material  per position: founder material? (any founder id); its source position q; else the new-material kind (mutation / input /
            constant / computed) or other-lineage material
  state     per position: byte equal to the founder's byte at the same position (IBS_same) / at the source position q (IBS_src)
  execution addresses executed during the member's own copy attempt on the arm's inputs (the "machinery" of THIS member)
  ability   (a) frozen copier ruler class in isolation (all 256 inputs, zero neighbour); (b) able to self-copy exactly under at least one
            input the arm allows (x != 128); (c) knockout (for one member per snapshot): each executed position set to 0x00 -> is (b)
            lost?
Item 8: a systematic sample of births whose child is NOT a copier by the ruler (every 40th birth checked); their material ids are
followed. At each snapshot: how many of their material ids are still present in living cells, and in which lineages.
    python -m archaeon.attribution.probes.th013_block13 OUT.json [--until 20000]
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

ARRIVAL = 447492; SNAP = 100; MEMB = 12; G = LC.G
ARM = M1.ARMS["BLOCK_128"]; ALLOWED = [x for x in range(256) if x not in set(ARM["blocked"])]; T0 = 13900
KIND = {1: "mutation", 2: "input", 3: "constant", 4: "computed"}


def exact_self_copy(tape):
    """(b), in isolation (zero neighbour) over the arm's allowed inputs. Returns (exact, birth, x, executed): exact = writes an exact
    copy of itself on some allowed input; birth = writes >=0.9 of the window on some allowed input (the world's birth rule). x and the
    executed mask come from the first exact input, else the first birth input."""
    xb = eb = None
    for x in ALLOWED:
        r = vm.execute(tape, LC.ZERO, (x,), LC.STEP_CAP, True, -1.0)
        if sum(r["nbr_mask"]) / G >= 0.9:
            if r["nbr_window"] == tape: return True, True, x, r["executed"]
            if xb is None: xb, eb = x, r["executed"]
    return False, xb is not None, xb, eb


class Obs(LC.World):
    def __init__(self, *a, **k):
        super().__init__(*a, **k); self.T = None; self.snaps = []; self.track = {}; self.nbirth_checked = 0

    def _birth(self, i, j, child, res0, nbr, x, epoch):
        super()._birth(i, j, child, res0, nbr, x, epoch)
        if epoch >= T0 and self.births % 40 == 0 and len(self.track) < 400:
            tape = bytes(self.genomes[j]); cls = R.measure(tape)["class"]; self.nbirth_checked += 1
            if cls not in R.HIT:
                self.track[self.oid[j]] = {"epoch": epoch, "glin": self.glin[j], "class": cls, "ids": [m for m in self.orig[j] if m is not None]}

    def snapshot(self, epoch):
        if self.T is None:
            for g, st in self.gl.items():
                if st.get("arrival") == ARRIVAL or (ARRIVAL is None and "arrival" in st): self.T = g; break
        if self.T is None: return
        st = self.gl[self.T]; fid = st["founder_oid"]; ftape = bytes.fromhex(st["tape"])
        cells = [c for c in range(LC.N) if self.genomes[c] is not None and self.glin[c] == self.T]
        rec = {"epoch": epoch, "alive": len(cells), "members": []}
        for n, c in enumerate(cells[:MEMB]):
            tape = bytes(self.genomes[c]); o = self.orig[c]
            pos = []
            for p in range(G):
                m = o[p]
                if m is not None and m >= 0 and m // 32 == fid: mat = "F@%d" % (m % 32); q = m % 32
                elif m is not None and m < 0: mat = KIND.get((-m) % 8, "new"); q = None
                else: mat = "other"; q = None
                pos.append({"mat": mat, "ibs_same": tape[p] == ftape[p], "ibs_src": (q is not None and tape[p] == ftape[q])})
            ok, bok, x, exe = exact_self_copy(tape)
            m = {"cell": c, "oid": self.oid[c], "ggen": self.ggen[c], "tape": tape.hex(), "pos": pos, "ruler": R.measure(tape)["class"], "self_copy_allowed": ok,
                 "birth_allowed": bok, "input": x, "executed": [p for p in range(G) if exe and exe[p]]}
            if n < 2 and bok:                                                  # knockout: (position, exact kept, birth kept)
                ko = []
                for p in m["executed"]:
                    t2 = bytearray(tape); t2[p] = 0; r2 = exact_self_copy(bytes(t2)); ko.append((p, r2[0], r2[1]))
                m["knockout"] = ko
            rec["members"].append(m)
        alive_ids = Counter()
        for c in range(LC.N):
            if self.genomes[c] is not None:
                for mm in self.orig[c]: alive_ids[mm] += 1
        rec["tracked_noncopier_material_alive"] = sum(1 for t in self.track.values() if any(alive_ids[i] for i in t["ids"]))
        self.last_alive_ids = alive_ids
        rec["tracked_total"] = len(self.track)
        self.snaps.append(rec)


def main(out_path, until):
    t0 = time.time(); AB.World = Obs
    orig_step = Obs.step
    def step(self, epoch, memo):
        orig_step(self, epoch, memo)
        if epoch % SNAP == 0: self.snapshot(epoch)
    Obs.step = step
    try:
        r = AB.run_block("envgate", 13, {"K_chambers": 2048, "dwell": 64, "refills": 1024}, {"BLOCK_128": M1.ARMS["BLOCK_128"]},
                         until_epoch=until, keep_worlds=True)
    finally:
        AB.World = LC.World
    w = r["arms"]["BLOCK_128"]["_world"]
    for k, t in w.track.items():                                                 # final fate of each tracked non-copier child's material
        ids = set(t["ids"]); holders = [c for c in range(LC.N) if w.genomes[c] is not None and ids & set(w.orig[c])]
        t["holders_final"] = len(holders); t["holder_glins"] = sorted({w.glin[c] for c in holders})[:10]
        t["holder_classes"] = [R.measure(bytes(w.genomes[c]))["class"] for c in holders[:3]]
        t["max_ids_retained"] = max((len(ids & set(w.orig[c])) for c in holders), default=0); t["n_ids"] = len(ids)
    st = w.gl.get(w.T) if w.T else None
    out = {"probe": "TH-013 block13", "until": until, "wall_s": round(time.time() - t0, 1), "births": w.births, "tracked_glin": w.T,
           "founder": {"oid": st["founder_oid"], "tape": st["tape"], "first_birth_epoch": st.get("first_birth_epoch"),
                       "first_birth_input": st.get("first_birth_input"), "first_birth_mech": st.get("first_birth_mech")} if st else None,
           "births_by_mechanism": dict(w.births_mech), "noncopier_births_checked": w.nbirth_checked,
           "tracked_noncopiers": {str(k): {kk: vv for kk, vv in v.items() if kk != "ids"} for k, v in list(w.track.items())[:400]},
           "snapshots": w.snaps}
    json.dump(out, open(out_path, "w"))
    print(json.dumps({"wall_s": out["wall_s"], "births": w.births, "tracked_glin": w.T, "snapshots": len(w.snaps)}))


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--smoke" in a: ARRIVAL = None; T0 = 0                                   # smoke test: first registered arrival lineage
    main(a[0], int(a[a.index("--until") + 1]) if "--until" in a else 20000)
