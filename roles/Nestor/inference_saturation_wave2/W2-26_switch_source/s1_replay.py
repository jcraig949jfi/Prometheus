"""W2-26 s1: deterministic REPLAY of the W2-17 r3 runs (same cell/seed/stop rule as r3_chains.py; read-only
subclass, never touches self.rng) with per-birth byte provenance, so every side-1 -> side-0 switch can be
traced to its genotype source.

Per accepted birth (causal or not):
  donor pre-genome (= the parent's genome at the interaction), victim pre-genome, child half after execution
  (pre-_mutate), child final genome (post-_mutate), prov of the child half (0 = unchanged during execution,
  1 = last changed by the side-0 ctx, 2 = by the side-1 ctx), copy_errors of both ctxs, donor carried state.
Per tracked org (founder + every org born by an accepted birth), every interaction in which its genome
changed without relabel: exec diff (with prov) and _mutate diff (in-place drift).
Per tracked org per interaction: counts keyed (pre-genome, side) -> [n, causal births credited, any birth].
Bit-exactness check: births (child, parent, causal, epoch, pside, final genome) must equal r3_out/LABEL.json.
python -B s1_replay.py LABEL -> s1_out/LABEL.json"""
import json, pathlib, sys, time
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
W17 = HERE.parent / "W2-17_runaway_departure"
sys.path.insert(0, str(W17))
from r2_replay import RUNS, C9, SPEC, Stop  # noqa: E402
import world  # noqa: E402
import z8  # noqa: E402

REC = []
_orig_init = z8.Ctx.__init__


def _init(self, *a, **k):
    _orig_init(self, *a, **k)
    REC.append(self)


z8.Ctx.__init__ = _init


def main(label, EMAX=130, DSTOP=24, QUIET=0):
    if label.startswith("XTKU_"):
        s_ = int(label[5:])
        rec = json.loads((C9.parent / "c9x-explore-2026-09-24" / "x_ticket" / "results" / ("%03d.json" % s_)).read_text())
        RUNS[label] = (9_998_000 + s_, rec["depth"])
    seed, rec_depth = RUNS[label]
    man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
    b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == SPEC)
    arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
    imp = bytes.fromhex(arm["kwargs"]["implant_hex"])
    cell = dict(arm["cell"], atlas_axis="NONE")
    B, P, CK, MUT = {}, [], {}, []
    tracked = {0}
    hist = {}        # oid -> list of in-place change events
    cnt = {}         # "hex|side" -> [n, causal, any]
    st = {"mut_on": False}

    class R(world.Runner):
        def _mutate(self, g):
            out = super()._mutate(g)
            if st["mut_on"]:
                MUT.append((bytes(g), out))
            return out

        def _lin_birth(self, child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
            P.append((child, parent, bool(causal)))
            super()._lin_birth(child, parent, niche, fid, span, causal, causal_pred, p11_rec)

        def _pair_interact(self, i, a, b):
            pre = {id(a): (a.oid, self._genome(a), 0, None if a.regs is None else list(a.regs), int(bool(a.fz)), int(bool(a.fc))),
                   id(b): (b.oid, self._genome(b), 1, None if b.regs is None else list(b.regs), int(bool(b.fz)), int(bool(b.fc)))}
            P.clear(); MUT.clear(); REC.clear()
            st["mut_on"] = True
            super()._pair_interact(i, a, b)
            st["mut_on"] = False
            cx = REC[:2]
            n = self.L
            prov = cx[0].prov
            cerr = [cx[0].copy_errors, cx[1].copy_errors]
            born = {}
            for child, parent, causal in P:
                org = a if a.oid == child else b
                src = b if org is a else a
                poid, pg, pside, pregs, pfz, pfc = pre[id(src)]
                _, vg, vside, _, _, _ = pre[id(org)]
                h0 = 0 if org is a else n
                mi = 0 if org is a else 1
                execd, fin = MUT[mi]
                B[child] = {"p": parent, "c": causal, "e": self.epoch, "anc": org.anc, "g": fin.hex(),
                            "pside": pside, "dg": pg.hex(), "vg": vg.hex(), "xg": execd.hex(),
                            "prov": bytes(prov[h0:h0 + n]).hex(), "cerr_d": cerr[pside], "cerr_v": cerr[vside],
                            "dctx": [pregs, pfz, pfc], "void": pre[id(org)][0]}
                tracked.add(child)
                born[poid] = born.get(poid, 0) + 1
                born.setdefault(("c", poid), 0)
                if causal:
                    born[("c", poid)] += 1
            # tracked orgs: per-(genome, side) counts and in-place drift
            for org, mi in ((a, 0), (b, 1)):
                oid0, g0, side, *_ = pre[id(org)]
                if oid0 not in tracked:
                    continue
                k = g0.hex() + "|%d" % side
                v = cnt.setdefault(k, [0, 0, 0])
                v[0] += 1; v[1] += born.get(("c", oid0), 0); v[2] += born.get(oid0, 0)
                if org.oid == oid0:          # not relabelled: any change is in-place
                    execd, fin = MUT[mi]
                    if fin != g0:
                        h0 = 0 if mi == 0 else n
                        ex = [(j, g0[j], execd[j], prov[h0 + j]) for j in range(n) if execd[j] != g0[j]]
                        mu = [(j, execd[j], fin[j]) for j in range(n) if fin[j] != execd[j]]
                        hist.setdefault(oid0, []).append({"e": self.epoch, "side": side, "ex": ex, "mu": mu,
                                                          "cerr_self": cerr[side], "cerr_other": cerr[1 - side]})

        def step(self):
            out = super().step()
            if self.epoch % 5 == 0:
                cp = {k: v["p"] for k, v in B.items() if v["c"]}
                d = self._depths(cp)[0]
                CK[self.epoch] = (d, self.ct["p11_events"])
                if d >= DSTOP:
                    raise Stop
            if self.epoch >= EMAX:
                raise Stop
            if QUIET and self.epoch > 30 and not any(v["c"] and v["e"] > self.epoch - QUIET for v in B.values()):
                raise Stop
            return out

    t0 = time.time()
    r = R(cell, seed, tier=arm["tier"], implant="ACTUAL_GENOME", implant_bytes=imp)
    try:
        r.run()
    except Stop:
        pass
    # bit-exactness vs W2-17 r3
    ref = W17 / "r3_out" / (label + ".json")
    exact = None
    if ref.exists():
        R3 = json.loads(ref.read_text())
        rb = R3["births"]
        exact = (len(rb) == len(B) and all(
            str(k) in rb and rb[str(k)]["p"] == v["p"] and rb[str(k)]["c"] == v["c"] and rb[str(k)]["e"] == v["e"]
            and rb[str(k)]["pside"] == v["pside"] and rb[str(k)]["g"] == v["g"] for k, v in B.items())
            and R3["epochs_replayed"] == r.epoch)
    out = {"label": label, "seed": seed, "recorded_final_depth": rec_depth, "epochs_replayed": r.epoch,
           "checks": CK, "exact_vs_r3": exact, "implant": imp.hex(), "births": B, "hist": hist, "cnt": cnt,
           "wall_s": round(time.time() - t0, 1)}
    (HERE / "s1_out").mkdir(exist_ok=True)
    (HERE / "s1_out" / (label + ".json")).write_text(json.dumps(out))
    print(label, "ep", r.epoch, "births", len(B), "exact", exact, "wall", out["wall_s"], flush=True)


if __name__ == "__main__":
    main(sys.argv[1], *(int(x) for x in sys.argv[2:]))
