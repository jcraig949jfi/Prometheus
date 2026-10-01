"""N17b (v2: exact identity for the M-vs-F contact, FID>=0.9 is blind to a 1-byte difference): does the 49->5C/59 side-0 morph of 7ae3 beat the side-1 founder on contact?
Single interactions (copy errors off), ZERO and RAND contexts, both placements, plus each against
random partners. Reports, per placement: P(founder converts morph), P(morph converts founder),
and each one's own-half survival (keep). Static, seconds of CPU."""
import json, random, sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-3_no_vocabulary"))
import common as C

N = 400


def main():
    r = C.runner_for_spec(C.run_ds.DONOR)
    F = C.run_ds.donor_genome()
    out = {}
    for mv in (0x5C, 0x59):
        g = bytearray(F); g[49] = mv; M = bytes(g)
        res = {}
        for cm in ("ZERO", "RAND"):
            rng = random.Random("N17b-%s-%x" % (cm, mv))
            for side_m in (0, 1):            # morph at side_m, founder at the other side
                k = {"M_converts_F": 0, "F_converts_M": 0, "M_keep": 0, "F_keep": 0}
                for _ in range(N):
                    sm = C.ZERO if cm == "ZERO" else C.rand_ctx(rng)
                    sf = C.ZERO if cm == "ZERO" else C.rand_ctx(rng)
                    o = C.outcome(r, M, F, side_m, sm, sf, 0.0, rng)
                    # one-byte difference: FID cannot separate M from F; score exact identity
                    k["M_converts_F"] += o["ny"] == M
                    k["M_keep"] += o["nx"] == M
                    k["F_converts_M"] += o["nx"] == F
                    k["F_keep"] += o["ny"] == F
                res["%s_morph_side%d" % (cm, side_m)] = {a: b / N for a, b in k.items()}
            # each vs random partners, random side: expected offspring (m_base) and keep
            for name, x in (("founder", F), ("morph", M)):
                mb, kp = 0, 0
                for _ in range(N):
                    y = C.rand_genome(rng, r.L)
                    s = rng.randrange(2)
                    sx = C.ZERO if cm == "ZERO" else C.rand_ctx(rng)
                    sy = C.ZERO if cm == "ZERO" else C.rand_ctx(rng)
                    o = C.outcome(r, x, y, s, sx, sy, 0.0, rng)
                    mb += o["m_base"]; kp += o["keep"]
                res["%s_%s_vs_random" % (cm, name)] = {"m_base": mb / N, "keep": kp / N}
        out["%02x" % mv] = res
    (HERE / "contact.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
