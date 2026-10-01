"""W2-35 s1: deterministic read-only REPLAY (same subclass pattern as W2-17 r3: reads state, never touches self.rng)
of the W2-17 7ae3 BASE runs, to the same epoch r3 stopped at. Logs
  * every half whose content ENTERS a rotated 7ae3 frame (best ring shift s != 0, rot >= 16) in an interaction,
    with: relabelled or not, partner frame, and (for events whose frame is not the partner's frame: CREATION) a
    copy-error-free re-execution on the traced stock VM (W2-24 tvm.pair_t) giving every LDIR (context, pc, whose
    code, HL, DE, BC/n) and the last writer of the victim's frame-matching bytes;
  * every accepted birth: parent anc, parent/child frame, causal flag;
  * per 5 epochs: alive census by (anc==0, frame class).
python -B s1_scan.py LABEL [LABEL ...] -> s1_out/LABEL.json"""
import json, sys, time, collections, pathlib
sys.dont_write_bytecode = True
from frames import world, ARM, IMP, frame, HERE, W2, N
sys.path.insert(0, str(W2 / "W2-24_keep_variant"))
sys.path.insert(0, str(W2 / "W2-17_runaway_departure"))
import tvm  # noqa: E402  (imports W2-3 common; world.z8 is the same stock z8 module)
from r2_replay import RUNS  # noqa: E402
T = 16


class Stop(Exception):
    pass


def fclass(fr):
    s, c, c0 = fr
    if s != 0 and c >= T:
        return "ROT%d" % s
    if c0 >= T:
        return "F0"
    return "none"


def trace_event(r, ga, gb, sa, sb, vside, s_new):
    na, nb, ctxs, tr, wl, after0, ld = tvm.pair_t(r, ga, gb, sa, sb)
    nv = na if vside == 0 else nb
    fr = frame(nv)
    base = vside * N
    last = {}
    for who, pc, a, old, new in wl:
        last[a % 128] = (who, pc % 128)
    auth = collections.Counter()
    for i in range(N):
        j = (i + s_new) % N
        if nv[j] == IMP[i]:
            w = last.get(base + j)
            auth["unwritten" if w is None else "ctx%d@%d(%s)" % (w[0], w[1], "H0" if w[1] < N else "H1")] += 1
    starts = {}
    for who in (0, 1):
        pcs = [t[1] for t in tr if t[0] == who]
        own = range(who * N, who * N + N)
        fx = next((k for k, p in enumerate(pcs) if p % 128 not in own), None)
        starts[who] = {"steps": len(pcs), "first_foreign_pc": None if fx is None else pcs[fx] % 128,
                       "halted": bool(ctxs[who].halted)}
    lds = [{"ctx": w, "pc": pc % 128, "code_half": "H%d" % ((pc % 128) // N), "HL": src, "DE": dst, "n": n,
            "src_mod": src % 128, "dst_mod": dst % 128, "d_minus_s_mod128": (dst - src) % 128,
            "regs": list(regs)} for w, pc, src, dst, n, regs in ld]
    return {"retrace_frame": list(fr), "retrace_reproduces": fclass(fr) == "ROT%d" % s_new,
            "auth_of_frame_bytes": dict(auth.most_common()), "ldirs": lds, "paths": starts,
            "ctx_in": [None if sa[0] is None else list(sa[0]), None if sb[0] is None else list(sb[0])]}


def main(label):
    seed, rec_depth = RUNS[label]
    r3 = json.loads((W2 / "W2-17_runaway_departure" / "r3_out" / (label + ".json")).read_text())
    EMAX = r3["epochs_replayed"]
    cell = dict(ARM["cell"], atlas_axis="NONE")
    EV, BIRTHS, CENSUS = [], [], {}
    PB = []
    cnt = collections.Counter()

    class R(world.Runner):
        def _lin_birth(self, child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
            PB.append((child, parent, bool(causal)))
            super()._lin_birth(child, parent, niche, fid, span, causal, causal_pred, p11_rec)

        def _pair_interact(self, i, a, b):
            pre = []
            for o in (a, b):
                g = self._genome(o)
                pre.append({"oid": o.oid, "anc": o.anc, "g": g, "fr": frame(g),
                            "st": (None if o.regs is None else list(o.regs), o.fz, o.fc)})
            PB.clear()
            super()._pair_interact(i, a, b)
            for side, o in enumerate((a, b)):
                p, q = pre[side], pre[1 - side]
                g = self._genome(o)
                if g == p["g"]:
                    continue
                fr = frame(g)
                fc = fclass(fr)
                cnt["changed_halves"] += 1
                if not fc.startswith("ROT"):
                    continue
                if fclass(p["fr"]) == fc:
                    cnt["rot_rewritten_same_frame"] += 1
                    continue
                relab = o.oid != p["oid"]
                pf = fclass(q["fr"])
                kind = "PROPAGATE" if pf == fc else "CREATE"
                ev = {"e": self.epoch, "i": i, "vside": side, "victim_oid": p["oid"], "victim_anc": p["anc"],
                      "victim_old_frame": list(p["fr"]), "victim_old_class": fclass(p["fr"]),
                      "new_frame": list(fr), "new_oid": o.oid, "new_anc": o.anc, "relabelled": relab,
                      "partner_oid": q["oid"], "partner_anc": q["anc"], "partner_frame": list(q["fr"]),
                      "partner_class": pf, "kind": kind, "g": g.hex(), "partner_g": q["g"].hex(),
                      "victim_old_g": p["g"].hex()}
                if kind == "CREATE":
                    ga, gb = pre[0]["g"], pre[1]["g"]
                    ev["trace"] = trace_event(self, ga, gb, pre[0]["st"], pre[1]["st"], side, fr[0])
                EV.append(ev)
            for child, parent, causal in PB:
                org = a if a.oid == child else b
                src = b if org is a else a
                ps = 0 if src is a else 1
                BIRTHS.append({"e": self.epoch, "child": child, "parent": parent, "c": causal,
                               "parent_anc": pre[ps]["anc"], "parent_class": fclass(pre[ps]["fr"]),
                               "child_class": fclass(frame(self._genome(org))), "pside": ps})

        def step(self):
            out = super().step()
            if self.epoch % 5 == 0:
                c = collections.Counter()
                for o in self.orgs:
                    if o.alive:
                        c["%s|%s" % ("anc0" if o.anc == 0 else "other", fclass(frame(self._genome(o))))] += 1
                CENSUS[self.epoch] = dict(c)
            if self.epoch >= EMAX:
                raise Stop
            return out

    t0 = time.process_time()
    r = R(cell, seed, tier=ARM["tier"], implant="ACTUAL_GENOME", implant_bytes=IMP)
    try:
        r.run()
    except Stop:
        pass
    # sanity: our birth list must equal r3's (same replay)
    r3b = {int(k): v for k, v in r3["births"].items()}
    mine = {b["child"]: b for b in BIRTHS}
    same = set(mine) == set(r3b) and all(mine[k]["parent"] == r3b[k]["p"] and mine[k]["c"] == r3b[k]["c"] for k in r3b)
    out = {"label": label, "seed": seed, "rec_depth": rec_depth, "epochs": r.epoch, "sanity_births_equal_r3": same,
           "counts": dict(cnt), "events": EV, "births": BIRTHS, "census": CENSUS,
           "cpu_s": round(time.process_time() - t0, 1)}
    (HERE / "s1_out").mkdir(exist_ok=True)
    (HERE / "s1_out" / (label + ".json")).write_text(json.dumps(out))
    k = collections.Counter(e["kind"] + ("_lab" if e["relabelled"] else "") for e in EV)
    print(label, "ep", r.epoch, "sane", same, dict(k), "births", len(BIRTHS), "cpu", out["cpu_s"], flush=True)


if __name__ == "__main__":
    for lab in sys.argv[1:]:
        main(lab)
