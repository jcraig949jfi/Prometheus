"""W2-1 check K: can the RT-measured single-interaction founder-overwrite rate in 9cba/e160 (1/400 zero context,
6/400 random context, per side-0 pairing; REDTEAM_SYNTHESIS_REVIEW.md:62-67) account for the C-SWAP-ACQUIRE outcome
'founder label lost in 100/240 GENOME runs vs 0/240 RANDOM' once compounded over a run? Pure arithmetic.
Assumes one pairing per organism per epoch (world.py _pair_epoch), side 0 with probability 1/2, hazard constant while
the founder's code is intact. Also the X-TICKET epoch-1 check for 7ae3's own SELF-enabled cell (200/400)."""
import math, json, pathlib
out = {}
for label, r in (("zero_ctx 1/400", 1 / 400), ("random_ctx 6/400", 6 / 400)):
    h = 0.5 * r
    out[label] = {"per_epoch_hazard": h,
                  "P_lost_by": {T: round(1 - (1 - h) ** T, 3) for T in (50, 100, 200, 436, 1000, 2000)},
                  "epochs_needed_for_0.417": round(math.log(1 - 100 / 240) / math.log(1 - h), 1)}
out["X-TICKET epoch-1 (7ae3 own cell)"] = {"predicted": 0.5 * 200 / 400, "observed": "36/128 = %.3f" % (36 / 128)}
lo = sum(math.comb(128, i) * 0.25 ** i * 0.75 ** (128 - i) for i in range(36, 129))
out["X-TICKET epoch-1 (7ae3 own cell)"]["P(X>=36 | p=0.25)"] = round(lo, 3)
print(json.dumps(out, indent=1))
pathlib.Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1))
