"""Q1 cost checks for 43->C3 vs founder on the N17e panel:
(a) children: every converted partner half (FID>=0.9) is re-tested as a donor against 8 fresh realized partners
    (W2-14 BASE bank, random side, child context ZERO): conversion rate, keep, m_base; split exact vs non-exact children.
(b) side-0 side effects: partner-half fate when the variant sits at side 0 (does the JP into the partner half harm
    or help the partner?), and the variant's own writes into the partner half."""
import json, pickle, random, pathlib, collections
from q1_trace import panel, mk, HERE
from tvm import C

r = C.runner_for_spec(C.run_ds.DONOR)
F = C.run_ds.donor_genome()
pan = panel()
banks = pickle.load(open(HERE.parent / "W2-14_F_calibration" / "banks.pkl", "rb"))["BASE"]
out = {}
for name, muts in (("founder", {}), ("43-c3", {43: 0xC3})):
    x = mk(F, muts)
    rng = random.Random("W2-24-children")
    st = collections.defaultdict(lambda: collections.Counter())
    side0 = collections.Counter()
    for y, cy, cx, s in pan:
        o = C.outcome(r, x, y, s, C.ZERO, cy, 0.0, None)
        if s == 0:
            side0["N"] += 1
            side0["partner_half_unchanged"] += o["ny"] == y
            side0["partner_half_fid>=0.9_to_itself"] += C.FID(y, o["ny"]) >= 0.9
            side0["donor_writes_other"] += o["raw"]["wo"][0]
            side0["partner_writes_other"] += o["raw"]["wo"][1]
        if not o["conv"]:
            continue
        ch = o["ny"]
        cls = "exact" if ch == x else "nonexact"
        st[cls]["children"] += 1
        for _ in range(8):
            ep = rng.randrange(10, 300)
            y2, cy2 = banks[ep][rng.randrange(len(banks[ep]))]
            s2 = rng.randrange(2)
            o2 = C.outcome(r, ch, y2, s2, C.ZERO, cy2, 0.0, None)
            st[cls]["trials"] += 1
            st[cls]["trials_side1"] += s2
            st[cls]["conv_side1"] += o2["conv"] and s2 == 1
            st[cls]["conv_side0"] += o2["conv"] and s2 == 0
            st[cls]["keep"] += o2["keep"]
            st[cls]["m_base"] += o2["m_base"]
    res = {}
    for cls, c in st.items():
        t = c["trials"]
        res[cls] = {"children": c["children"], "trials": t,
                    "conv_rate_side1": round(c["conv_side1"] / max(c["trials_side1"], 1), 3),
                    "conv_rate_side0": round(c["conv_side0"] / max(t - c["trials_side1"], 1), 3),
                    "keep": round(c["keep"] / t, 3), "m_base": round(c["m_base"] / t, 3)}
    out[name] = {"children": res, "side0_effects": {k: (v if k == "N" else round(v / side0["N"], 3)) for k, v in side0.items()}}
(HERE / "q1c_children.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
