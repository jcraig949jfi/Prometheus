# Deviation wrapper: analyze.main() reads pre["blocks"]; the frozen PREREG keeps the list at pre["spec"]["blocks"].
# This calls the FROZEN analyze.analyze() unchanged with the correct count; the output file and printout are identical to main()'s.
import json
from archaeon.envgate2 import analyze as A
pre = json.loads((A.HERE / "PREREG.json").read_text(encoding="utf-8")); pf = json.loads((A.HERE / "PREFLIGHT.json").read_text(encoding="utf-8"))
blocks = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(A.RUNS.glob("block_*.json"))]
res = A.analyze(blocks, len(pre["spec"]["blocks"]), pre["attribution_tests"]["passed"], pf["verdict"] == "PASS")
(A.HERE / "RESULTS.json").write_text(json.dumps(res, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
print(json.dumps({k: res[k] for k in ("verdict", "phase_c_gate_passed", "totals_genetic")}))
print(json.dumps(res["phase_c_gate"])); print(json.dumps({k: {x: v[x] for x in ("pos", "neg", "p", "holm_significant")} for k, v in res["primary"].items()}), res["ordering_page"]["p"])
print("failures", res["failures"]); print("falsifiers", json.dumps({k: v for k, v in res["falsifiers"].items() if k != "label_dependence"}))
print("label_dependence", json.dumps(res["falsifiers"]["label_dependence"])); print("mcnemar", json.dumps(res["arrival_level_mcnemar"]))
print("takeover_worlds", len(res["takeover_worlds"]) if hasattr(res["takeover_worlds"], "__len__") else res["takeover_worlds"], "est_in_takeover", res["establishments_in_takeover_worlds"])
print("per_block", json.dumps(res["per_block"]))
