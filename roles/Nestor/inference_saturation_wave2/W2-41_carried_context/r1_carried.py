"""W2-41 r1: deterministic REPLAY of the W2-17/W2-26 7ae3 runs (same cell/seed/stop rule as W2-26 s1_replay:
EMAX 130, DSTOP 24; read-only subclass, never touches self.rng) recording the CARRIED context of every
7ae3-family organism (>= 51/64 bytes equal to the implant at shift 0) at EVERY interaction it takes part in,
not only at births (W2-26 s1_out stores dctx only for birth events, i.e. conditioned on conversion).

Per row: epoch, oid, age (epoch - birth epoch; founder born 0; pre-existing background None), side,
pre-genome id, pre (regs, fz, fc), partner genome id + partner pre-context, and outcome: any / causal births
credited to this oid as parent in this interaction, keep (own half FID>=0.9 to pre-genome and not relabelled).
Bit-exactness: births (child, parent, causal, epoch) equal W2-26 s1_out/LABEL.json.
python -B r1_carried.py LABEL [LABEL ...] -> r1_out/LABEL.json.gz"""
import gzip, json, pathlib, sys, time
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
W17 = HERE.parent / "W2-17_runaway_departure"
W26 = HERE.parent / "W2-26_switch_source"
sys.path.insert(0, str(W17))
from r2_replay import RUNS, C9, SPEC, Stop  # noqa: E402
import world  # noqa: E402

FID = world._fidelity


def main(label, EMAX=130, DSTOP=24):
    seed, rec_depth = RUNS[label]
    man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
    b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == SPEC)
    arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
    imp = bytes.fromhex(arm["kwargs"]["implant_hex"])
    cell = dict(arm["cell"], atlas_axis="NONE")
    B, P = {}, []
    born = {0: 0}
    GT, GL = {}, []          # genome table
    ROWS = []

    def gid(g):
        h = g.hex()
        if h not in GT:
            GT[h] = len(GL); GL.append(h)
        return GT[h]

    def fam(g):
        return sum(x == y for x, y in zip(g, imp)) >= 51

    class R(world.Runner):
        def _lin_birth(self, child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
            P.append((child, parent, bool(causal)))
            super()._lin_birth(child, parent, niche, fid, span, causal, causal_pred, p11_rec)

        def _pair_interact(self, i, a, b):
            pre = []
            for side, o in enumerate((a, b)):
                g = self._genome(o)
                pre.append((o, o.oid, g, side, None if o.regs is None else list(o.regs), int(bool(o.fz)), int(bool(o.fc))))
            P.clear()
            super()._pair_interact(i, a, b)
            nb_any, nb_c = {}, {}
            for child, parent, causal in P:
                B[child] = {"p": parent, "c": causal, "e": self.epoch}
                born[child] = self.epoch
                nb_any[parent] = nb_any.get(parent, 0) + 1
                if causal:
                    nb_c[parent] = nb_c.get(parent, 0) + 1
            for k in (0, 1):
                o, oid, g, side, regs, fz, fc = pre[k]
                if not fam(g):
                    continue
                po, poid, pg, _, pregs, pfz, pfc = pre[1 - k]
                keep = int(o.oid == oid and FID(g, self._genome(o)) >= 0.9)
                ROWS.append([self.epoch, oid, born.get(oid), side, gid(g), regs, fz, fc,
                             gid(pg), pregs, pfz, pfc, nb_any.get(oid, 0), nb_c.get(oid, 0), keep])

        def step(self):
            out = super().step()
            if self.epoch % 5 == 0:
                cp = {k: v["p"] for k, v in B.items() if v["c"]}
                d = self._depths(cp)[0]
                if d >= DSTOP:
                    raise Stop
            if self.epoch >= EMAX:
                raise Stop
            return out

    t0, c0 = time.time(), time.process_time()
    r = R(cell, seed, tier=arm["tier"], implant="ACTUAL_GENOME", implant_bytes=imp)
    try:
        r.run()
    except Stop:
        pass
    ref = json.loads((W26 / "s1_out" / (label + ".json")).read_text())
    rb = ref["births"]
    exact = (len(rb) == len(B) and all(str(k) in rb and rb[str(k)]["p"] == v["p"] and rb[str(k)]["c"] == v["c"]
                                       and rb[str(k)]["e"] == v["e"] for k, v in B.items())
             and ref["epochs_replayed"] == r.epoch)
    out = {"label": label, "seed": seed, "epochs_replayed": r.epoch, "exact_vs_w26": exact, "implant": imp.hex(),
           "cols": ["e", "oid", "born", "side", "g", "regs", "fz", "fc", "pg", "pregs", "pfz", "pfc", "births", "cbirths", "keep"],
           "genomes": GL, "rows": ROWS, "wall_s": round(time.time() - t0, 1), "cpu_s": round(time.process_time() - c0, 1)}
    (HERE / "r1_out").mkdir(exist_ok=True)
    with gzip.open(HERE / "r1_out" / (label + ".json.gz"), "wt") as f:
        json.dump(out, f)
    print(label, "ep", r.epoch, "rows", len(ROWS), "genomes", len(GL), "exact", exact, "cpu", out["cpu_s"], flush=True)


if __name__ == "__main__":
    for lab in sys.argv[1:]:
        main(lab)
