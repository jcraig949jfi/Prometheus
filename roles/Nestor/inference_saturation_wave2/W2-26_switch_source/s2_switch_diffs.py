"""W2-26 s2: classify the genotype source of every side-1 -> side-0 switch edge in the s1 replays.
Switch edge = causal birth kk whose parent k (copying at side 0, pside(kk) = 0) was itself S1-born
(pside(k) = 1, causal). Same definition as W2-17 a4 'trans 10' (window: k born <= stop-15 for the a4 count).
Genotype comparison: P@E1 (k's parent's genome at k's birth interaction, = B[k].dg) vs k@E2 (k's genome at the
switch interaction, = B[kk].dg). Per differing byte, the source:
  CE  copy error at birth: donor-authored (prov = donor ctx), 1-bit from the donor byte, donor ctx copy_errors > 0
  DW  donor-authored but not a 1-bit copy error (offset / rotated / partial copy, donor code writing elsewhere)
  VW  written by the victim's own ctx during the birth interaction (partner-constructed)
  RS  victim residue (byte untouched during execution, survives from the victim's old genome)
  MB  _mutate at the birth (post-execution operand mutation)
  IM  in-place _mutate in a later non-relabelling interaction (between E1 and E2)
  IX  in-place execution write (self or partner ctx) in a later non-relabelling interaction; IXc if 1-bit + copy err
python -B s2_switch_diffs.py -> s2_switch_diffs.json"""
import json, pathlib, sys, collections
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-17_runaway_departure"))
from r2_replay import RUNS  # noqa: E402

RUNAWAY = {k for k, v in RUNS.items() if v[1] >= 22}


def pc(x):
    return bin(x).count("1")


def birth_sources(b):
    """per position source of child final vs donor pre-genome at a birth"""
    dg, xg, g, vg = (bytes.fromhex(b[k]) for k in ("dg", "xg", "g", "vg"))
    prov = bytes.fromhex(b["prov"])
    did = b["pside"] + 1
    src = {}
    for j in range(len(g)):
        if g[j] == dg[j]:
            continue
        if xg[j] == dg[j]:
            src[j] = "MB"
        elif prov[j] == 0:
            src[j] = "RS"
        elif prov[j] == did:
            src[j] = "CE" if (pc(xg[j] ^ dg[j]) == 1 and b["cerr_d"] > 0) else "DW"
        else:
            src[j] = "VW"
    return src


def main():
    out = {"edges": [], "per_run": {}}
    for label in RUNS:
        d = json.loads((HERE / "s1_out" / (label + ".json")).read_text())
        B = {int(k): v for k, v in d["births"].items()}
        H = {int(k): v for k, v in d["hist"].items()}
        stop = d["epochs_replayed"]
        cls = "RUN" if label in RUNAWAY else "CTL"
        kids = collections.defaultdict(list)
        for k, v in B.items():
            if v["c"]:
                kids[v["p"]].append(k)
        n10 = n1x = 0
        for k, v in B.items():
            if not v["c"] or v["pside"] != 1:
                continue
            inwin = v["e"] <= stop - 15
            for kk in kids.get(k, []):
                if inwin:
                    n1x += 1
                if B[kk]["pside"] != 0:
                    continue
                if inwin:
                    n10 += 1
                Pg = bytes.fromhex(v["dg"])           # parent P's genome at k's birth
                kb = bytes.fromhex(v["g"])            # k at birth (final)
                kE2 = bytes.fromhex(B[kk]["dg"])      # k at the switch interaction
                bs = birth_sources(v)
                # in-place events of k between its birth and kk's birth
                inpl = {}
                for ev in H.get(k, []):
                    if v["e"] <= ev["e"] <= B[kk]["e"]:
                        for j, old, new, pv in ev["ex"]:
                            inpl.setdefault(j, set()).add("IXc" if pc(old ^ new) == 1 and (ev["cerr_self"] + ev["cerr_other"]) > 0 else "IX")
                        for j, old, new in ev["mu"]:
                            inpl.setdefault(j, set()).add("IM")
                diff = [j for j in range(64) if kE2[j] != Pg[j]]
                pos = {}
                for j in diff:
                    s = set()
                    if kb[j] != Pg[j]:
                        s.add(bs.get(j, "?"))
                    if kE2[j] != kb[j]:
                        s |= inpl.get(j, {"I?"})
                    pos[j] = sorted(s)
                out["edges"].append({"run": label, "cls": cls, "k": k, "kk": kk, "P": v["p"], "e1": v["e"], "e2": B[kk]["e"],
                                     "inwin": inwin, "Pg": Pg.hex(), "kb": kb.hex(), "kE2": kE2.hex(),
                                     "ndiff": len(diff), "pos": {str(j): pos[j] for j in diff},
                                     "P_pside": B[v["p"]]["pside"] if v["p"] in B else None,
                                     "kk_dctx": B[kk]["dctx"], "kk_vg": B[kk]["vg"], "kk_cerr_d": B[kk]["cerr_d"],
                                     "kk_g": B[kk]["g"]})
        out["per_run"][label] = {"cls": cls, "trans10_win": n10, "trans1x_win": n1x}
    agg = collections.defaultdict(lambda: [0, 0])
    for r, v in out["per_run"].items():
        agg[v["cls"]][0] += v["trans10_win"]; agg[v["cls"]][1] += v["trans1x_win"]
    out["a4_reproduction"] = dict(agg)
    print("a4 trans 10 / (10+11), window:", dict(agg))
    print("switch edges total:", len(out["edges"]), collections.Counter(e["cls"] for e in out["edges"]))
    (HERE / "s2_switch_diffs.json").write_text(json.dumps(out))


if __name__ == "__main__":
    main()
