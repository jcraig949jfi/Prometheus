"""W2-17 a5: W2-3 K2 method (common.outcome, copy errors off, 7ae3 own cell, stock VM; partners fresh random
genomes; ZERO and RAND contexts; NP partners per side) applied to:
  * the founder; N17's side-0 point morphs 49->59, 49->5C; the byte-63 variants seen at in-world side switches;
  * genomes ON the deepest causal chain of every replayed run (r3_out), at chain indices 2, 6, 12, 18, last,
    tagged with the side the node actually copied from in the world (its chain child's parent side).
Per genome: conv/keep per side, m_BASE (mean over sides of #x-like halves), m_ATOMIC, keep_wrong
(keep at the side with the lower conversion rate), copy side s* (argmax conv).
Plus mixed-side kin (RAND contexts): every ordered pairing of {founder, 49->5C, in-world S0 morph}."""
import json, pathlib, random, sys, time
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-3_no_vocabulary"))
import common as C  # noqa: E402

NP = int(sys.argv[1]) if len(sys.argv) > 1 else 30


def k2(r, x, rng):
    out = {}
    for cm in ("ZERO", "RAND"):
        acc = {s: {"conv": 0, "keep": 0, "m_base": 0, "m_atomic": 0, "conv_prom": 0} for s in (0, 1)}
        for s in (0, 1):
            for _ in range(NP):
                y = C.rand_genome(rng, r.L)
                sx = C.ZERO if cm == "ZERO" else C.rand_ctx(rng)
                sy = C.ZERO if cm == "ZERO" else C.rand_ctx(rng)
                o = C.outcome(r, x, y, s, sx, sy, 0.0, rng)
                for f in acc[s]:
                    acc[s][f] += o[f]
        a = {s: {f: v / NP for f, v in acc[s].items()} for s in (0, 1)}
        ss = 0 if a[0]["conv"] > a[1]["conv"] else 1
        out[cm] = {"conv0": a[0]["conv"], "conv1": a[1]["conv"], "keep0": a[0]["keep"], "keep1": a[1]["keep"],
                   "m_base": round((a[0]["m_base"] + a[1]["m_base"]) / 2, 3),
                   "m_atomic": round((a[0]["m_atomic"] + a[1]["m_atomic"]) / 2, 3),
                   "s_star": ss, "keep_wrong": a[1 - ss]["keep"], "keep_right": a[ss]["keep"]}
    return out


def mixed(r, gens, rng):
    """x at side 0 vs y at side 1 (RAND contexts): fraction of the 2 halves that end x-like / y-like."""
    res = {}
    for nx, x in gens.items():
        for ny, y in gens.items():
            xs = ys = cx = cy = 0
            for _ in range(NP):
                o = C.pair(r, x, y, C.rand_ctx(rng), C.rand_ctx(rng), 0.0, rng)
                halves = (o["na"], o["nb"])
                xs += sum(C.FID(x, h) >= 0.9 for h in halves)
                ys += sum(C.FID(y, h) >= 0.9 for h in halves)
                cx += C.FID(x, o["nb"]) >= 0.9 and C.FID(y, o["nb"]) < 0.9   # x converted y's half
                cy += C.FID(y, o["na"]) >= 0.9 and C.FID(x, o["na"]) < 0.9
            res["%s@0|%s@1" % (nx, ny)] = {"x_like_halves": round(xs / NP, 3), "y_like_halves": round(ys / NP, 3),
                                           "x_converts_y": round(cx / NP, 3), "y_converts_x": round(cy / NP, 3)}
    return res


def main():
    t0 = time.time()
    r = C.runner_for_spec(C.run_ds.DONOR)
    F = C.run_ds.donor_genome()
    rng = random.Random("W2-17-a5")
    gens = {"founder": F}
    for pos, b in ((49, 0x59), (49, 0x5C), (63, 0xAC), (63, 0xFF), (63, 0x01), (63, 0x9A)):
        g = bytearray(F); g[pos] = b; gens["%d>%02x" % (pos, b)] = bytes(g)
    res = {"NP": NP, "named": {}, "chain": []}
    for k, g in gens.items():
        res["named"][k] = k2(r, g, rng)
        print(k, json.dumps(res["named"][k]["RAND"]), flush=True)
    s0_morph = None
    for f in sorted((HERE / "r3_out").glob("*.json")):
        d = json.loads(f.read_text())
        if not d.get("deepest"):
            continue
        ch = d["deepest"][0]["chain"]
        B = d["births"]
        for idx in sorted({i for i in (2, 6, 12, 18, len(ch) - 2) if 0 < i < len(ch) - 1}):
            node = str(ch[idx])
            if node not in B:
                continue
            g = bytes.fromhex(B[node]["g"])
            side_used = B[str(ch[idx + 1])]["pside"]
            m = k2(r, g, rng)
            row = {"run": d["label"], "runaway": d["recorded_final_depth"] >= 22, "idx": idx, "side_used": side_used,
                   "fid_founder": round(C.FID(F, g), 3), "hex": g.hex(), **m}
            res["chain"].append(row)
            if s0_morph is None and side_used == 0 and m["RAND"]["s_star"] == 0 and m["RAND"]["conv0"] >= 0.5 \
                    and row["fid_founder"] >= 0.9:
                s0_morph = (d["label"] + ":%d" % idx, g)
        print(d["label"], "done", round(time.time() - t0), flush=True)
    kin = {"founder": F, "49>5c": gens["49>5c"]}
    if s0_morph:
        kin["S0world"] = s0_morph[1]
        res["S0world_source"] = s0_morph[0]
    res["mixed_side_kin_RAND"] = mixed(r, kin, rng)
    res["cpu_s"] = round(time.time() - t0, 1)
    (HERE / "a5_k2_morphs.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res["mixed_side_kin_RAND"], indent=1), res["cpu_s"])


if __name__ == "__main__":
    main()
