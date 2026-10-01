"""W2-35 a5: frame of every deepest causal chain recorded by W2-17 r3 (r3_out/*.json, up to 5 deepest chains per run;
23 selected runs + the XTKU unselected X-TICKET seeds). Frame of a chain = frame class of its FIRST child's genome
(a P-11 child is FID >= 0.9 to the root at that moment, so it carries the root's frame then), also the last node's.
Cross with the world label (root_in_family = all-edge ancestry reaches the implant, i.e. the anc-0 label).
python -B a5_chains.py -> a5_chains.json"""
import json, glob, pathlib, collections
from frames import frame, W2, HERE
from s1_scan import fclass
rows = []
for f in sorted(glob.glob(str(W2 / "W2-17_runaway_departure" / "r3_out" / "*.json"))):
    d = json.loads(pathlib.Path(f).read_text())
    B = d["births"]
    for k, c in enumerate(d.get("deepest") or []):
        ch = c["chain"]
        if len(ch) < 2 or str(ch[1]) not in B:
            continue
        g1 = bytes.fromhex(B[str(ch[1])]["g"])
        gl = bytes.fromhex(B[str(ch[-1])]["g"])
        f1, fl = fclass(frame(g1)), fclass(frame(gl))
        rows.append({"label": d["label"], "k": k, "depth": d["depth_at_stop"], "rec_depth": d["recorded_final_depth"],
                     "root": c["root"], "in_family": c["root_in_family"], "frame_first": f1, "frame_last": fl,
                     "frame_first_full": list(frame(g1))})
deep = [r for r in rows if r["k"] == 0]
tab = collections.Counter()
for r in deep:
    grp = "runaway" if r["rec_depth"] >= 22 else ("deep_ctl" if not r["label"].startswith("XTKU") else "XTKU")
    rot = r["frame_first"].startswith("ROT")
    tab[(grp, "ROT" if rot else r["frame_first"], "family" if r["in_family"] else "unlabelled")] += 1
out = {"deepest_chain_per_run": deep, "all_chains": rows, "table": {str(k): v for k, v in sorted(tab.items())}}
(HERE / "a5_chains.json").write_text(json.dumps(out, indent=1))
for r in deep:
    if not r["label"].startswith("XTKU") or r["depth"] >= 3:
        print(r["label"], r["rec_depth"], r["depth"], r["in_family"], r["frame_first_full"], r["frame_first"], r["frame_last"])
for k, v in sorted(tab.items()):
    print(k, v)
