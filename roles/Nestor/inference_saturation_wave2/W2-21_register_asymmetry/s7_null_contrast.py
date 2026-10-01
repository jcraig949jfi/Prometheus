"""Step 7: world corpus vs random-screened null (s4), per side: share of copiers that set BOTH address operands
explicitly, random-register good rate, register-robust share (>= 27/30). Fisher exact two-sided."""
import json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from s2_fragility_decomposition import fisher_2x2
s2 = json.loads((HERE / "s2_fragility_decomposition.json").read_text())
s4 = json.loads((HERE / "s4_random_null.json").read_text())
s1 = json.loads((HERE / "s1_operand_taint.json").read_text())
out = {}
for s in (0, 1):
    w = s2["operand_contrast"]["side%d" % s]; nl = s4["summary"]["side%d" % s]
    wr = [v["all_random_good"] for k, v in s2["per_genome"].items() if k in s1["side%d" % s]]
    robust_w = sum(x >= 27 for x in wr)
    out["side%d" % s] = {
        "world_both_addr_set": [w["both_addr_from_code_or_ctx"], w["n"]],
        "null_both_addr_set": [nl["both_addr_set"], nl["n"]],
        "p_both_addr_set_world_vs_null": fisher_2x2(w["both_addr_from_code_or_ctx"], w["n"] - w["both_addr_from_code_or_ctx"],
                                                    nl["both_addr_set"], nl["n"] - nl["both_addr_set"]),
        "world_randregs_rate": round(sum(wr) / (30 * len(wr)), 3),
        "null_randregs_rate": round(nl["randregs_good"] / nl["trials"], 3),
        "world_robust_ge27": [robust_w, len(wr)], "null_robust_ge27": [nl["randregs_ge_0.9"], nl["n"]],
        "p_robust_world_vs_null": fisher_2x2(robust_w, len(wr) - robust_w, nl["randregs_ge_0.9"], nl["n"] - nl["randregs_ge_0.9"]),
    }
n0, n1 = s4["summary"]["side0"], s4["summary"]["side1"]
out["null_side0_vs_side1_both_set_p"] = fisher_2x2(n0["both_addr_set"], n0["n"] - n0["both_addr_set"], n1["both_addr_set"], n1["n"] - n1["both_addr_set"])
print(json.dumps(out, indent=1))
(HERE / "s7_null_contrast.json").write_text(json.dumps(out, indent=1))
