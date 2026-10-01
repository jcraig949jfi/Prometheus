"""W2-35 s4: static assay (same harness/panel as s3) of the IN-WORLD rotated chain genomes (first child and last node of
each rotated deepest chain, a5) and of three pure rotations; plus frame heredity over 4 generations: from each genome, the
children (random side, 8 W2-14 BASE bank partners per donor, up to 40 donors per generation) are re-assayed as donors (8 W2-14 BASE bank partners each, as W2-24 q1c),
recording child frame == parent frame, and per-generation m_base. Also: which bytes differ between a pure-rotation donor
and its converted child (why exact_child = 0 for most s).
python -B s4_world_frames.py -> s4_world_frames.json"""
import json, sys, pickle, random, collections, time
sys.dont_write_bytecode = True
from frames import frame, HERE, W2
from s1_scan import fclass
from s3_frames_assay import assay, rot_of, panel, C

t0 = time.process_time()
r = C.runner_for_spec(C.run_ds.DONOR)
F = C.run_ds.donor_genome()
pan = panel()
banks = pickle.load(open(W2 / "W2-14_F_calibration" / "banks.pkl", "rb"))["BASE"]
a5 = json.loads((HERE / "a5_chains.json").read_text())
r3dir = W2 / "W2-17_runaway_departure" / "r3_out"
G = {}
for row in a5["deepest_chain_per_run"]:
    if row["frame_first"].startswith("ROT"):
        d = json.loads((r3dir / (row["label"] + ".json")).read_text())
        ch = d["deepest"][0]["chain"]
        G[row["label"] + "_first"] = bytes.fromhex(d["births"][str(ch[1])]["g"])
        G[row["label"] + "_last"] = bytes.fromhex(d["births"][str(ch[-1])]["g"])
for s in (0, 47, 62, 1):
    G["pure_s%d" % s] = rot_of(F, s)
out = {}
for name, x in G.items():
    a = assay(r, x, pan, F)
    a["frame"] = list(frame(x))
    # generations
    rng = random.Random("W2-35-gen:" + name)
    gens, cur = [], [x]
    for gen in range(4):
        kids, keep_same, m, trials = [], 0, 0, 0
        for donor in cur[:40]:
            fr = fclass(frame(donor))
            for _ in range(8):
                ep = rng.randrange(10, 300)
                y, cy = banks[ep][rng.randrange(len(banks[ep]))]
                o = C.outcome(r, donor, y, rng.randrange(2), C.ZERO, cy, 0.0, None)
                trials += 1
                m += o["m_base"]
                if o["conv"]:
                    kids.append(o["ny"])
                    keep_same += fclass(frame(o["ny"])) == fr
        gens.append({"gen": gen, "donors": min(len(cur), 40), "trials": trials, "m_base": round(m / max(trials, 1), 3),
                     "children": len(kids), "child_same_frame": keep_same,
                     "child_frame_classes": dict(collections.Counter(fclass(frame(k)) for k in kids).most_common(3))})
        if not kids:
            break
        cur = kids[::max(1, len(kids) // 40)]
    a["generations"] = gens
    out[name] = a
    print(name, a["frame"], a["m_base"], a["keep_s0"], a["keep_s1"], a["conv_s0"], a["conv_s1"],
          [(g["m_base"], g["children"], g["child_same_frame"]) for g in gens], flush=True)
# exact-child diff for pure s=47 vs s=0
diffs = {}
for s in (0, 47):
    x = rot_of(F, s)
    c = collections.Counter()
    for y, cy, cx, sd in pan[:300]:
        if sd != 1:
            continue
        o = C.outcome(r, x, y, 1, C.ZERO, cy, 0.0, None)
        if o["conv"]:
            for i in range(64):
                if o["ny"][i] != x[i]:
                    c[i] += 1
    diffs[s] = dict(c.most_common(6))
out["_child_diff_positions"] = diffs
out["_cpu_s"] = round(time.process_time() - t0, 1)
print(diffs, out["_cpu_s"])
(HERE / "s4_world_frames.json").write_text(json.dumps(out, indent=1))
