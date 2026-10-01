"""K3 (frame A, site field): is the foreign-cell 'victim magnet' (U-N5) a per-epoch hazard on ONE site,
integrated over the run, that the per-interaction view dismissed?

Record: C-SWAP-ACQUIRE (ATOMIC, cells 9cba / e160, 2000 epochs). 7ae3 implant label lost in 55/120 and
45/120 runs; label stays on the implant slot only in 45 and 51; spread in 20 and 24. A random implant
is never overwritten (0/240). The RT dismissed the SELF hijack because the single-interaction rate is
<= 1.5%. Site-field frame: the relevant quantity is the per-epoch hazard h on the site; over T = 2000
epochs, P(site relabelled) = 1 - (1-h)^T, so h ~ 3e-4/epoch already gives ~0.45.

Part 1: per-interaction rates (fresh partners, ZERO / RAND contexts, side 0 / 1), intact vs knockouts.
Part 2: a single-SITE chain (not a world run): the implant site meets one partner per epoch for up to
T epochs, its context carried; partners are drawn from a fixed pool of 255 random genomes whose
contexts are carried and refreshed by one random-random call before each meeting (approximating
their own epoch). ATOMIC rule: the implant half is replaced only if promoted. Mutation applied with
the world's own _mutate. Output: survival of the implant content on its site, compared to the record.
Spread of the implant into partners is NOT modelled (that needs a world run).
"""
import json
import random
import sys
import time

import common as C

CELLS = ("9cba7113df39009e-s3882-tL-a0", "e16055dd06cff594-s37315-tL-a0")
N1 = 600
CHAINS = int(sys.argv[1]) if len(sys.argv) > 1 else 40
T = 2000


def variants(x):
    ko_ldir = bytearray(x)
    ko_ldir[52] = ko_ldir[53] = 0
    ko_self = bytearray(x)
    ko_self[23] = ko_self[24] = 0
    return {"intact": x, "ko_ldir_52_53": bytes(ko_ldir), "ko_self_23_24": bytes(ko_self)}


def part1(r, x, rng):
    out = {}
    for name, g in variants(x).items():
        out[name] = {}
        for cm in ("ZERO", "RAND"):
            for s in (0, 1):
                k = kp = cv = 0
                for _ in range(N1):
                    y = C.rand_genome(rng, r.L)
                    sx = C.ZERO if cm == "ZERO" else C.rand_ctx(rng)
                    sy = C.ZERO if cm == "ZERO" else C.rand_ctx(rng)
                    o = C.outcome(r, g, y, s, sx, sy, 0.0, rng)
                    kp += o["imp_prom"]
                    cv += o["conv_prom"]
                out[name]["%s_side%d" % (cm, s)] = {"relabelled": kp / N1, "converts": cv / N1}
    # a random implant, for the 0/240 contrast
    rr = {"ZERO": 0, "RAND": 0}
    for cm in rr:
        for _ in range(N1):
            g = C.rand_genome(rng, r.L)
            y = C.rand_genome(rng, r.L)
            sx = C.ZERO if cm == "ZERO" else C.rand_ctx(rng)
            sy = C.ZERO if cm == "ZERO" else C.rand_ctx(rng)
            rr[cm] += C.outcome(r, g, y, rng.randrange(2), sx, sy, 0.0, rng)["imp_prom"]
    out["random_implant_relabel_rate"] = {k: v / N1 for k, v in rr.items()}
    return out


def chain(r, x, rng):
    """Returns (epoch at which the implant site was relabelled or None, n conversions made by implant)."""
    n = r.L
    pool = [C.rand_genome(rng, n) for _ in range(255)]
    pctx = [C.ZERO] * 255
    sx = C.ZERO
    conv = 0
    for e in range(T):
        j = rng.randrange(255)
        # partner's own epoch-mate first (refresh its carried context), contents restored (ATOMIC, unpromoted)
        k = rng.randrange(255)
        o0 = C.pair(r, pool[j], pool[k], pctx[j], pctx[k], r.copy_mut, rng)
        pctx[j], pctx[k] = o0["ctx"][0], o0["ctx"][1]
        y = pool[j]
        s = rng.randrange(2)
        o = C.outcome(r, x, y, s, sx, pctx[j], r.copy_mut, rng)
        sx, pctx[j] = o["cx"], o["cy"]
        if o["imp_prom"]:
            return e, conv
        if o["conv_prom"]:
            conv += 1
            pool[j] = o["ny"]
        x = r._mutate(x)
        pool[j] = r._mutate(pool[j])
    return None, conv


def main():
    t0 = time.time()
    res = {}
    x7 = C.run_ds.donor_genome()
    for sp in CELLS:
        r = C.runner_for_spec(sp)
        x = r._pad(x7)
        rng = random.Random("K3-" + sp[:4])
        rec = {"part1": part1(r, x, rng)}
        ch = []
        for c in range(CHAINS):
            ch.append(chain(r, x, random.Random("K3-chain-%s-%d" % (sp[:4], c))))
        lost = [e for e, _ in ch if e is not None]
        rec["chains"] = {"n": CHAINS, "relabelled_by_T": len(lost), "share": len(lost) / CHAINS,
                         "median_epoch": sorted(lost)[len(lost) // 2] if lost else None,
                         "epochs": sorted(lost), "converted_any": sum(cv > 0 for _, cv in ch)}
        res[sp[:4]] = rec
        print(sp[:4], json.dumps(rec["chains"])[:300], round(time.time() - t0, 1), flush=True)
    res["record_C_SWAP_ACQUIRE"] = {"9cba": {"label_lost": 55, "slot_only": 45, "spread": 20, "n": 120},
                                    "e160": {"label_lost": 45, "slot_only": 51, "spread": 24, "n": 120}}
    res["cpu_s"] = round(time.time() - t0, 1)
    (C.HERE / "k3_site_hazard.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v["part1"] for k, v in res.items() if isinstance(v, dict) and "part1" in v}, indent=1))


if __name__ == "__main__":
    main()
