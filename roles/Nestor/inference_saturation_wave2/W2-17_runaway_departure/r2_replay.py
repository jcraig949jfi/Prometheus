"""W2-17 r2: deterministic REPLAY (same cell, seed, physics as the original campaign run; the subclass
only reads state and never touches self.rng) of existing 7ae3 BASE splice-off runs, truncated at
epoch EMAX (<= the 2000 epochs the original run already covered). Per-site tracking of the founder's
FAMILY (every accepted birth from a member, causal or not; == anc 0 descendants); gen = length of the
run of consecutive P-11-causal edges ending at the member (the world's depth ruler), ggen = all edges:
  * every member: birth epoch, generation, parent, genome + context at birth, causal children,
    q_live (members alive / pop) and q_act (members born in the last 6 epochs / pop) at birth;
  * every interaction of a member: member side, partner class (K kin member / T field-touched slot /
    B untouched background), outcomes (member credited with a causal birth; member relabelled away;
    member keeps its content, fid >= 0.9), binned by q_act at that epoch.
Sanity: world depth and p11 count at epochs 20/40/60/80/100 vs X-RUNAWAY's recorded series.
python -B r2_replay.py LABEL -> r2_out/LABEL.json"""
import json, pathlib, sys, time
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
C9 = HERE.parents[1] / "campaigns" / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
import world  # noqa: E402

SPEC = "7ae3f9c1437c8000-s54765-tL-a0"
# label: (seed, recorded final depth, physics)   all: C9 arm-B 7ae3, atlas_axis NONE, k = 1, BASE write-back
RUNS = {
    "XH2N_s1": (9_980_001, 179), "CNR_s22": (9_985_022, 126),
    "XTK_59": (9_998_059, 162), "XTK_121": (9_998_121, 189), "XTK_35": (9_998_035, 508),
    "CRW_1": (9_990_501, 176), "CRW_103": (9_990_603, 235), "CRW_145": (9_990_645, 262),
    "CRW_75": (9_990_575, 356), "CRW_78": (9_990_578, 437), "CRW_48": (9_990_548, 533), "CRW_126": (9_990_626, 549),
    # deep-but-died controls
    "CNR_s4": (9_985_004, 17), "XH2N_s9": (9_980_009, 18), "XTK_14": (9_998_014, 21),
    "CRW_35": (9_990_535, 11), "CRW_47": (9_990_547, 12), "CRW_71": (9_990_571, 12), "CRW_79": (9_990_579, 12),
    "CRW_107": (9_990_607, 12), "CRW_66": (9_990_566, 10), "CRW_91": (9_990_591, 10), "CRW_85": (9_990_585, 8),
}
XR = {"XH2N_s1": {20: (5, 48), 40: (9, 109), 60: (13, 272), 80: (19, 580), 100: (26, 796)},
      "CNR_s22": {20: (9, 45), 40: (12, 230), 60: (20, 747), 80: (26, 1056), 100: (35, 1623)}}


class Stop(Exception):
    pass


def main(label, EMAX=120, DSTOP=40):
    seed, rec_depth = RUNS[label]
    man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
    b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == SPEC)
    arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
    implant = bytes.fromhex(arm["kwargs"]["implant_hex"])
    cell = dict(arm["cell"], atlas_axis="NONE")
    FID = world._fidelity
    S = {"mem": {}, "kids": {}, "inter": {}, "touched": set(), "checks": {}, "births_pending": [],
         "maxgen": 0, "gen_epoch": {}, "qhist": []}

    class R(world.Runner):
        def _lin_birth(self, child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
            S["births_pending"].append((child, parent, bool(causal)))
            super()._lin_birth(child, parent, niche, fid, span, causal, causal_pred, p11_rec)

        def _pair_interact(self, i, a, b):
            mem = S["mem"]
            if not mem:
                return super()._pair_interact(i, a, b)
            pre = [(o, o.oid, self._genome(o), o.slot) for o in (a, b)]
            S["births_pending"] = []
            super()._pair_interact(i, a, b)
            # register causal births from members
            for child, parent, causal in S["births_pending"]:
                if parent in mem:
                    org = a if a.oid == child else b
                    g = self._genome(org)
                    gen = mem[parent]["gen"] + 1 if causal else 0
                    mem[child] = {"gen": gen, "born": self.epoch, "parent": parent, "hex": g.hex(),
                                  "ctx": [None if org.regs is None else list(org.regs), int(bool(org.fz)), int(bool(org.fc))],
                                  "q_live": S["q_live"], "q_act": S["q_act"], "kids": 0, "kids_nc": 0, "n_int": 0,
                                  "causal": causal, "ggen": mem[parent]["ggen"] + 1}
                    mem[parent]["kids" if causal else "kids_nc"] += 1
                    if gen > S["maxgen"]:
                        S["maxgen"] = gen
                        S["gen_epoch"][gen] = self.epoch
            # interactions of pre-existing members
            qb = min(int(S["q_act"] * 20), 10)   # q_act bins of 0.05
            for side, (o, oid, g, slot) in enumerate(pre):
                if oid not in mem:
                    continue
                po, poid, pg, pslot = pre[1 - side]
                cls = "K" if poid in mem else ("T" if pslot in S["touched"] else "B")
                mem[oid]["n_int"] += 1
                conv = any(c[1] == oid and c[2] for c in S["births_pending"])
                away = o.oid != oid
                keep = FID(g, self._genome(o)) >= 0.9
                key = "%s|%d|%d" % (cls, side, qb)
                v = S["inter"].setdefault(key, [0, 0, 0, 0])
                v[0] += 1; v[1] += conv; v[2] += away; v[3] += keep
                S["touched"].add(pslot)

        def step(self):
            if not S["mem"]:
                f = next(o for o in self.orgs if o.anc == 0)
                S["mem"][f.oid] = {"gen": 0, "born": 0, "parent": None, "hex": self._genome(f).hex(), "ctx": None,
                                   "q_live": 1 / 256, "q_act": 1 / 256, "kids": 0, "kids_nc": 0, "n_int": 0,
                                   "causal": True, "ggen": 0}
            alive = [o for o in self.orgs if o.alive]
            mem = S["mem"]
            S["q_live"] = sum(o.oid in mem for o in alive) / len(alive)
            S["q_act"] = sum(o.oid in mem and mem[o.oid]["born"] >= self.epoch - 6 for o in alive) / len(alive)
            S["qhist"].append((self.epoch, round(S["q_live"], 4), round(S["q_act"], 4), S["maxgen"]))
            out = super().step()
            if self.epoch % 20 == 0:
                cp = {e["child"]: e["parent"] for e in self.lineage if e["kind"] == "birth" and e["causal"]}
                S["checks"][self.epoch] = (self._depths(cp)[0], self.ct["p11_events"], S["maxgen"])
            if self.epoch >= EMAX or S["maxgen"] >= DSTOP:
                raise Stop
            # extinction of the active lineage for 40 epochs -> stop (died)
            if self.epoch > 40 and all(m["born"] < self.epoch - 40 for m in mem.values()):
                raise Stop
            return out

    t0 = time.time()
    r = R(cell, seed, tier=arm["tier"], implant="ACTUAL_GENOME", implant_bytes=implant)
    try:
        r.run()
    except Stop:
        pass
    sanity = None
    if label in XR:
        sanity = {e: {"recorded": XR[label][e], "replay": S["checks"].get(e, [None])[:2]} for e in XR[label] if e <= r.epoch}
        sanity["ok"] = all(tuple(v["replay"]) == tuple(v["recorded"]) for k, v in sanity.items() if k != "ok")
    out = {"label": label, "seed": seed, "recorded_final_depth": rec_depth, "epochs_replayed": r.epoch,
           "maxgen": S["maxgen"], "gen_epoch": S["gen_epoch"], "checks": S["checks"], "sanity": sanity,
           "members": S["mem"], "inter": S["inter"], "qhist": S["qhist"], "wall_s": round(time.time() - t0, 1)}
    (HERE / "r2_out").mkdir(exist_ok=True)
    (HERE / "r2_out" / (label + ".json")).write_text(json.dumps(out))
    print(label, "epochs", r.epoch, "maxgen", S["maxgen"], "members", len(S["mem"]), "sanity", sanity and sanity["ok"],
          "wall", out["wall_s"], flush=True)


if __name__ == "__main__":
    main(sys.argv[1], *(int(x) for x in sys.argv[2:]))
