"""W2-17 a3: genomes along the deepest causal chain of each replayed run (r3_out): fidelity and best
ring-rotation match to the implant, byte at founder position 49 (N17 side-0 morph: 0x59 / 0x5C),
generation time (epochs per causal generation) and the founder-family status of the chain root."""
import json, pathlib, sys
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from r2_replay import RUNS, C9, SPEC
import world
man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == SPEC)
imp = bytes.fromhex(next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")["kwargs"]["implant_hex"])


def rot(g):
    return max((sum(g[(i + s) % 64] == imp[i] for i in range(64)), s) for s in range(64))


res = {}
for label in RUNS:
    f = HERE / "r3_out" / (label + ".json")
    if not f.exists():
        continue
    d = json.loads(f.read_text())
    if not d.get("deepest"):
        continue
    c = d["deepest"][0]
    B = d["births"]
    rows = []
    for k, node in enumerate(c["chain"]):
        if str(node) not in B:
            rows.append({"k": k, "node": node, "g": None})
            continue
        g = bytes.fromhex(B[str(node)]["g"])
        r_, s_ = rot(g)
        rows.append({"k": k, "e": B[str(node)]["e"], "fid": round(world._fidelity(g, imp), 3), "rot": r_, "shift": s_,
                     "b49": "%02x" % g[49], "b49_rot": "%02x" % g[(49 + s_) % 64], "pside": B[str(node)]["pside"]})
    ep = [r["e"] for r in rows if r.get("e") is not None]
    runaway = d["recorded_final_depth"] >= 22
    res[label] = {"runaway": runaway, "rec_depth": d["recorded_final_depth"], "depth_at_stop": d["depth_at_stop"],
                  "root_in_family": c["root_in_family"], "root_rot": c["root_rot_match"], "root_fid": c["root_fid_imp"],
                  "epochs_per_gen": round((ep[-1] - ep[0]) / max(1, len(ep) - 1), 2) if len(ep) > 1 else None,
                  "parent_side_counts": [sum(r.get("pside") == 0 for r in rows), sum(r.get("pside") == 1 for r in rows)],
                  "fid_first_mid_last": [rows[1].get("fid") if len(rows) > 1 else None, rows[len(rows) // 2].get("fid"), rows[-1].get("fid")],
                  "shift_set": sorted({r.get("shift") for r in rows if r.get("shift") is not None}),
                  "b49_set": sorted({r.get("b49_rot") for r in rows if r.get("b49_rot")}),
                  "rows": rows}
    print(label, "RUN" if runaway else "ctl", d["recorded_final_depth"], "fam", c["root_in_family"],
          "eps/gen", res[label]["epochs_per_gen"], "psides", res[label]["parent_side_counts"],
          "fid 1/mid/last", res[label]["fid_first_mid_last"], "shifts", res[label]["shift_set"], "b49", res[label]["b49_set"])
(HERE / "a3_chain_genomes.json").write_text(json.dumps(res, indent=1))
