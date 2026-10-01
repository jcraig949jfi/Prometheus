"""K3c: what part of the implant is the target? Per-interaction relabel rate (implant half promoted-
overwritten by the partner) at side 0 and side 1, random contexts, for: 7ae3 intact; 7ae3 with
52-53 zeroed; random bytes carrying only ED B0 at 52-53; random bytes carrying the 7ae3 prefix 0-4
(LD HL,5C00 sets HL = 0 mod 128) plus ED B0 at 52-53. Copy errors and mutation off."""
import json
import random
import time

import common as C
import k3_site_hazard as K

N = 3000


def main():
    t0 = time.time()
    res = {}
    x7 = C.run_ds.donor_genome()
    for sp in K.CELLS:
        r = C.runner_for_spec(sp)
        x = r._pad(x7)
        rng = random.Random("K3c" + sp[:4])
        ko = bytearray(x); ko[52] = ko[53] = 0
        out = {}
        for name in ("intact", "ko_52_53", "random+EDB0@52", "random+prefix0-4+EDB0@52"):
            cnt = {0: 0, 1: 0}
            for s in (0, 1):
                for _ in range(N):
                    if name == "intact":
                        g = x
                    elif name == "ko_52_53":
                        g = bytes(ko)
                    else:
                        g = bytearray(C.rand_genome(rng, r.L))
                        g[52], g[53] = 0xED, 0xB0
                        if "prefix" in name:
                            g[0:5] = x[0:5]
                        g = bytes(g)
                    y = C.rand_genome(rng, r.L)
                    cnt[s] += C.outcome(r, g, y, s, C.rand_ctx(rng), C.rand_ctx(rng), 0.0, rng)["imp_prom"]
            out[name] = {"side0": cnt[0] / N, "side1": cnt[1] / N}
        res[sp[:4]] = out
        print(sp[:4], out, round(time.time() - t0, 1), flush=True)
    res["cpu_s"] = round(time.time() - t0, 1)
    (C.HERE / "k3c_mechanism.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
