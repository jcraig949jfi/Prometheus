"""W2-17 r3: deterministic REPLAY (read-only subclass, no rng use) of existing 7ae3 BASE splice-off runs,
truncated at the epoch where the world's P-11 depth first reaches DSTOP (or EMAX), well inside the 2000
epochs each original run already covered. Records every accepted birth: child/parent oid, causal flag,
epoch, child genome + context at birth, parent genome at the interaction, parent side, child anc.
At the end: the world's deepest causal chain, its root, whether the root is in the founder's FAMILY
(anc 0: the implant or an accepted-birth descendant of it) and the root genome's best ring-rotation
match to the implant (a frameshifted 7ae3 derivative has a high rotated match at shift != 0).
Sanity: world depth / p11 at 20..100 vs X-RUNAWAY's recorded series (2 runs).
python -B r3_chains.py LABEL [EMAX] [DSTOP] -> r3_out/LABEL.json"""
import json, pathlib, sys, time
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from r2_replay import RUNS, XR, C9, SPEC, Stop  # noqa: E402
import world  # noqa: E402


def rot_match(g, imp):
    return max((sum(g[(i + s) % len(imp)] == imp[i] for i in range(len(imp))), s) for s in range(len(imp)))


def main(label, EMAX=130, DSTOP=24, QUIET=0):
    if label.startswith("XTKU_"):      # unselected X-TICKET seed (recorded depth from x_ticket/results)
        s_ = int(label[5:])
        rec = json.loads((C9.parent / "c9x-explore-2026-09-24" / "x_ticket" / "results" / ("%03d.json" % s_)).read_text())
        RUNS[label] = (9_998_000 + s_, rec["depth"])
    seed, rec_depth = RUNS[label]
    man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
    b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == SPEC)
    arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
    imp = bytes.fromhex(arm["kwargs"]["implant_hex"])
    cell = dict(arm["cell"], atlas_axis="NONE")
    B, P, CK = {}, [], {}
    first_parent_genome = {}

    class R(world.Runner):
        def _lin_birth(self, child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
            P.append((child, parent, bool(causal)))
            super()._lin_birth(child, parent, niche, fid, span, causal, causal_pred, p11_rec)

        def _pair_interact(self, i, a, b):
            pre = {id(a): (a.oid, self._genome(a), 0), id(b): (b.oid, self._genome(b), 1)}
            P.clear()
            super()._pair_interact(i, a, b)
            for child, parent, causal in P:
                org = a if a.oid == child else b
                src = b if org is a else a
                poid, pg, pside = pre[id(src)]
                if poid != parent:     # parent itself relabelled earlier in this call: use its pre genome anyway
                    pass
                B[child] = {"p": parent, "c": causal, "e": self.epoch, "anc": org.anc,
                            "g": self._genome(org).hex(),
                            "ctx": [None if org.regs is None else list(org.regs), int(bool(org.fz)), int(bool(org.fc))],
                            "pside": pside}
                if parent not in B and parent not in first_parent_genome:
                    first_parent_genome[parent] = {"g": pg.hex(), "e": self.epoch, "side": pside,
                                                   "anc": src.anc if src.oid == parent else None}

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
                raise Stop      # no causal birth anywhere for QUIET epochs: lineage done (unselected-sample mode)
            return out

    t0 = time.time()
    r = R(cell, seed, tier=arm["tier"], implant="ACTUAL_GENOME", implant_bytes=imp)
    try:
        r.run()
    except Stop:
        pass
    cp = {k: v["p"] for k, v in B.items() if v["c"]}
    allp = {k: v["p"] for k, v in B.items()}
    d, per = r._depths(cp)
    out = {"label": label, "seed": seed, "recorded_final_depth": rec_depth, "epochs_replayed": r.epoch,
           "depth_at_stop": d, "checks": CK, "wall_s": None}
    if label in XR:
        out["sanity"] = {e: [XR[label][e], CK.get(e)] for e in XR[label] if e in CK}
        out["sanity_ok"] = all(tuple(v[0]) == tuple(v[1]) for v in out["sanity"].values())
    if d:
        # all chains of maximal depth: roots
        deepest = [n for n, v in per.items() if v == d]
        chains = []
        for node in deepest[:5]:
            ch = [node]
            while ch[-1] in cp:
                ch.append(cp[ch[-1]])
            root = ch[-1]
            up = [root]
            while up[-1] in allp:
                up.append(allp[up[-1]])
            fam = up[-1] == 0
            rg = B[root]["g"] if root in B else first_parent_genome.get(root, {}).get("g")
            rgb = bytes.fromhex(rg) if rg else None
            chains.append({"node": node, "root": root, "root_born": B.get(root, {}).get("e"),
                           "root_first_parent_epoch": first_parent_genome.get(root, {}).get("e"),
                           "root_all_edge_ancestry": up, "root_in_family": fam,
                           "root_genome": rg, "root_fid_imp": round(world._fidelity(rgb, imp), 3) if rgb else None,
                           "root_rot_match": rot_match(rgb, imp) if rgb else None,
                           "chain": ch[::-1], "chain_epochs": [B[c]["e"] for c in ch[::-1] if c in B]})
        out["deepest"] = chains
    out["births"] = B
    out["first_parent_genome"] = {str(k): v for k, v in first_parent_genome.items()}
    out["wall_s"] = round(time.time() - t0, 1)
    (HERE / "r3_out").mkdir(exist_ok=True)
    (HERE / "r3_out" / (label + ".json")).write_text(json.dumps(out))
    c0 = out.get("deepest", [{}])[0]
    print(label, "rec", rec_depth, "ep", r.epoch, "depth", d, "root", c0.get("root"), "fam", c0.get("root_in_family"),
          "rot", c0.get("root_rot_match"), "fid", c0.get("root_fid_imp"), "sanity", out.get("sanity_ok"),
          "wall", out["wall_s"], flush=True)


if __name__ == "__main__":
    main(sys.argv[1], *(int(x) for x in sys.argv[2:]))
