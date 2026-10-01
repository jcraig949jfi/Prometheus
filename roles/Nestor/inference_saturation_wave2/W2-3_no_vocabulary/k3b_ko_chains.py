"""K3b: the K3 single-site chain with the implant's block-copy bytes (52, 53) zeroed, and with a
random implant. Prediction (site-field frame): hazard ~0 in both, because the relabelling is done by
partner contexts executing the implant's own block-copy op. Same chain code as K3."""
import json
import random
import sys
import time

import common as C
import k3_site_hazard as K

CH = int(sys.argv[1]) if len(sys.argv) > 1 else 20


def main():
    t0 = time.time()
    res = {}
    x7 = C.run_ds.donor_genome()
    for sp in K.CELLS:
        r = C.runner_for_spec(sp)
        x = r._pad(x7)
        ko = K.variants(x)["ko_ldir_52_53"]
        out = {}
        for name, mk in (("ko_ldir", lambda c: ko), ("random_implant", lambda c: C.rand_genome(random.Random("RI%d" % c), r.L))):
            ch = [K.chain(r, mk(c), random.Random("K3b-%s-%s-%d" % (sp[:4], name, c))) for c in range(CH)]
            lost = [e for e, _ in ch if e is not None]
            out[name] = {"n": CH, "relabelled_by_T": len(lost), "epochs": sorted(lost)}
        res[sp[:4]] = out
        print(sp[:4], out, round(time.time() - t0, 1), flush=True)
    res["cpu_s"] = round(time.time() - t0, 1)
    (C.HERE / "k3b_ko_chains.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
