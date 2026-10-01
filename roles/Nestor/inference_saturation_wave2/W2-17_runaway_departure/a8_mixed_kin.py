"""W2-17 a8: mixed-side kin contacts (N17 request), founder vs side-0 morphs, copy errors off, RAND and ZERO
contexts, NP calls per ordered placement. Halves are attributed by the bytes where x and y differ (majority over
the diagnostic positions; 'other' if neither matches majority or fid to both < 0.9). Readout per placement:
expected halves ending x-type / y-type, and m_BASE-in-contact for each.
Also: the diffs of in-world S0-chain genomes (fid >= 0.85 to the founder) vs the founder."""
import json, pathlib, random, sys
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-3_no_vocabulary"))
import common as C  # noqa: E402

NP = 40


def attrib(h, x, y, diag):
    if C.FID(x, h) < 0.9 and C.FID(y, h) < 0.9:
        return "other"
    vx = sum(h[i] == x[i] for i in diag); vy = sum(h[i] == y[i] for i in diag)
    return "x" if vx > vy else ("y" if vy > vx else "other")


def main():
    r = C.runner_for_spec(C.run_ds.DONOR)
    F = C.run_ds.donor_genome()
    a5 = json.loads((HERE / "a5_k2_morphs.json").read_text())
    g5c = bytearray(F); g5c[49] = 0x5C
    s0w = next(bytes.fromhex(c["hex"]) for c in a5["chain"] if c["run"] + ":%d" % c["idx"] == a5["S0world_source"])
    gens = {"founder": F, "49>5c": bytes(g5c), "S0world(" + a5["S0world_source"] + ")": s0w}
    rng = random.Random("W2-17-a8")
    out = {"contacts": {}}
    names = list(gens)
    for i, nx in enumerate(names):
        for ny in names:
            if nx == ny:
                continue
            x, y = gens[nx], gens[ny]
            diag = [p for p in range(64) if x[p] != y[p]]
            for cm in ("RAND", "ZERO"):
                cnt = {"x": 0, "y": 0, "other": 0}
                for _ in range(NP):
                    sx = C.ZERO if cm == "ZERO" else C.rand_ctx(rng)
                    sy = C.ZERO if cm == "ZERO" else C.rand_ctx(rng)
                    o = C.pair(r, x, y, sx, sy, 0.0, rng)
                    for h in (o["na"], o["nb"]):
                        cnt[attrib(h, x, y, diag)] += 1
                out["contacts"]["%s@0 | %s@1 | %s" % (nx, ny, cm)] = {k: round(v / NP, 3) for k, v in cnt.items()}
    for k, v in out["contacts"].items():
        print(k, v)
    diffs = {}
    for c in a5["chain"]:
        if c["side_used"] == 0 and c["RAND"]["s_star"] == 0 and c["fid_founder"] >= 0.85:
            g = bytes.fromhex(c["hex"])
            diffs["%s:%d" % (c["run"], c["idx"])] = ["%d:%02x>%02x" % (p, F[p], g[p]) for p in range(64) if g[p] != F[p]]
    out["S0_chain_diffs_vs_founder"] = diffs
    for k, v in diffs.items():
        print(k, v)
    (HERE / "a8_mixed_kin.json").write_text(json.dumps(out, indent=1))


main()
