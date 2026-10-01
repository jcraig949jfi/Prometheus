"""Residual decomposition from score.json (no new VM runs). Per side-1 interaction (17 x 60):
HALT outcome, HALT class, BO_OP outcome, and from SO_OP the partner's dropped writes into side 1 that would have
changed a byte, by kind (dHBC block, dHSC byte store). Writes decomp.json."""
import json, pathlib, collections
HERE = pathlib.Path(__file__).resolve().parent
d = json.loads(HERE.joinpath("score.json").read_text())
X = collections.Counter(); per = collections.Counter()
for g in d["genomes"]:
    if g["side"] != 1:
        continue
    for h, b, s in zip(g["HALT"]["inter"], g["BO_OP"]["inter"], g["SO_OP"]["inter"]):
        hc = ("BLOCK" if h["pblk"] else "BYTE") if h["pre"] else "CLEAN"
        kind = {(0, 0): "none", (1, 0): "block_only", (0, 1): "store_only", (1, 1): "block+store"}[(s["dHBC"] > 0, s["dHSC"] > 0)]
        X[("SO_kind", kind)] += 1
        X[("SO_kind", kind, "HALT_bad")] += not h["good"]
        X[("SO_kind", kind, "BO_bad")] += not b["good"]
        X[("HALTclass", hc, "HALT_bad")] += not h["good"]
        X[("HALTclass", hc, "BO_bad")] += not b["good"]
        X[("HALTclass", hc, "BO_pre")] += b["pre"]
        X[("HALT_bad_BO_good")] += (not h["good"]) and b["good"]
        X[("HALT_good_BO_bad")] += h["good"] and not b["good"]
        X[("HALT_harv0_fired")] += h["harv0"] > 0
        X[("SO_dHBC_bytes")] += s["dHBC"]; X[("SO_dHSC_bytes")] += s["dHSC"]
        X[("BO_dropped_block_bytes_changing")] += b["dHBC"]
out = {" | ".join(map(str, k)) if isinstance(k, tuple) else k: v for k, v in sorted(X.items(), key=str)}
HERE.joinpath("decomp.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
