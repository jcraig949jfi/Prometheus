"""Q2: decompose the founder's side-1 deficits (keep 0.907, conv 0.874) by whether the donor half was already
damaged by the first-moving partner before the donor ran (run-first exposure, W2-7 S10), versus failures with an
intact donor half at the moment it ran. Same for each genome's converter side. From q1_trace.pkl."""
import pickle, json, collections
from q1_trace import panel, HERE
d = pickle.load(open(HERE / "q1_trace.pkl", "rb"))
pan = panel()
out = {}
for name, s in (("founder", 1), ("43-c3", 1), ("49-5c", 0), ("44-ac", 0), ("founder", 0), ("49-5c", 1)):
    c = collections.Counter()
    for i, (y, cy, cx, side) in enumerate(pan):
        if side != s:
            continue
        q = d[name][i]
        pre = "damaged_before_donor_ran" if (s == 1 and not q["after0_donor_half_intact"]) else "intact_when_donor_ran"
        c["N"] += 1
        c[pre] += 1
        c["keep_fail|" + pre] += not q["keep"]
        c["conv_fail|" + pre] += not q["conv"]
    out["%s_side%d" % (name, s)] = dict(c)
(HERE / "q2_runfirst.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
