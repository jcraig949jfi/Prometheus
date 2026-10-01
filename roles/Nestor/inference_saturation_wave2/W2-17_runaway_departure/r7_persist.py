"""W2-17 r7: persistence accounting after saturation (W2-14 reframe). Deterministic REPLAY (read-only subclass,
no rng use) of existing 7ae3 BASE splice-off runs to EMAX (<= the original 2000 epochs).
Tagged = any org born by a P-11 causal birth; type S0/S1 = the side its parent copied from (heritable 0.93, a4).
Per interaction, for each tagged party X (pre-interaction oid), binned by (type, q_act bin 0.1), q_act = tagged
orgs born within the last 6 epochs / pop:
  n        interactions
  conv     X credited with a causal birth this call
  conv_kin   ... onto a tagged victim (re-conversion);  conv_repair ... onto a tagged victim that was ERODED
             (victim's pre-call content fid < 0.9 to X's pre-call content)
  ow_kin   X relabelled by a tagged partner (cost-free overwrite: the slot stays copier-born)
  ow_for   X relabelled by an untagged partner
  erode    X neither relabelled nor kept (fid(pre, post) < 0.9): BASE erosion
python -B r7_persist.py LABEL [EMAX] -> r7_out/LABEL.json"""
import json, pathlib, sys, time
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from r2_replay import RUNS, C9, SPEC, Stop  # noqa: E402
import world  # noqa: E402


def main(label, EMAX=150):
    seed, rec_depth = RUNS[label]
    man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
    b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == SPEC)
    arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
    imp = bytes.fromhex(arm["kwargs"]["implant_hex"])
    cell = dict(arm["cell"], atlas_axis="NONE")
    FID = world._fidelity
    T = {}            # oid -> (type, born)
    P = []
    A = {}
    H = []
    st = {"q": 0.0}

    class R(world.Runner):
        def _lin_birth(self, child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
            P.append((child, parent, bool(causal)))
            super()._lin_birth(child, parent, niche, fid, span, causal, causal_pred, p11_rec)

        def _pair_interact(self, i, a, b):
            pre = [(a.oid, self._genome(a)), (b.oid, self._genome(b))]
            P.clear()
            super()._pair_interact(i, a, b)
            orgs = (a, b)
            # register causal births (type = side of the parent)
            for child, parent, causal in P:
                if causal:
                    side_parent = 0 if pre[0][0] == parent or (a.oid != child and a.oid == parent) else 1
                    if pre[1][0] == parent:
                        side_parent = 1
                    if pre[0][0] == parent:
                        side_parent = 0
                    T[child] = ("S%d" % side_parent, self.epoch)
            qb = min(int(st["q"] * 10), 9)
            for s in (0, 1):
                oid, g = pre[s]
                if oid not in T or T[oid][1] == self.epoch:
                    continue
                poid, pg = pre[1 - s]
                key = "%s|%d" % (T[oid][0], qb)
                v = A.setdefault(key, {"n": 0, "conv": 0, "conv_kin": 0, "conv_repair": 0, "ow_kin": 0, "ow_for": 0, "erode": 0})
                v["n"] += 1
                conv = any(c[1] == oid and c[2] for c in P)
                if conv:
                    v["conv"] += 1
                    if poid in T:
                        v["conv_kin"] += 1
                        if FID(pg, g) < 0.9:
                            v["conv_repair"] += 1
                o = orgs[s]
                if o.oid != oid:
                    if poid in T:
                        v["ow_kin"] += 1
                    else:
                        v["ow_for"] += 1
                elif FID(g, self._genome(o)) < 0.9:
                    v["erode"] += 1

        def step(self):
            alive = [o for o in self.orgs if o.alive]
            act = [T[o.oid][0] for o in alive if o.oid in T and T[o.oid][1] >= self.epoch - 6]
            st["q"] = len(act) / max(1, len(alive))
            H.append((self.epoch, act.count("S0"), act.count("S1"), sum(o.oid in T for o in alive)))
            out = super().step()
            if self.epoch >= EMAX:
                raise Stop
            return out

    t0 = time.time()
    r = R(cell, seed, tier=arm["tier"], implant="ACTUAL_GENOME", implant_bytes=imp)
    try:
        r.run()
    except Stop:
        pass
    out = {"label": label, "seed": seed, "recorded_final_depth": rec_depth, "epochs": r.epoch, "acc": A,
           "hist_epoch_activeS0_activeS1_tagged": H, "wall_s": round(time.time() - t0, 1)}
    (HERE / "r7_out").mkdir(exist_ok=True)
    (HERE / "r7_out" / (label + ".json")).write_text(json.dumps(out))
    print(label, "epochs", r.epoch, "wall", out["wall_s"], "last hist", H[-1], flush=True)


if __name__ == "__main__":
    main(sys.argv[1], *(int(x) for x in sys.argv[2:]))
