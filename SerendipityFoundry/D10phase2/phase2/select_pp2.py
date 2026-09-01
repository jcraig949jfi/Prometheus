"""Freeze the single PP2 candidate for the gate, by a PRE-DECLARED rule
applied to DEV results only.

Rule, in order:
  1. maximise dev (PP2 - R2)
  2. tie-break: maximise dev PP2
  3. tie-break: candidate order as listed in pp2_dev.py
No tuning after selection; the gate runs this candidate and nothing else.
"""
import json

SPEC = {
    "C1 bytevalue_bitset3 x output_bitset8":
        ("ka_bytevalue_bitset", [3], "kq_output_bitset", [8]),
    "C2 bytevalue_bitset2 x output_bitset8":
        ("ka_bytevalue_bitset", [2], "kq_output_bitset", [8]),
    "C3 opcode_bitset3 x output_bitset8":
        ("ka_opcode_bitset", [3], "kq_output_bitset", [8]),
    "C4 constant_bitset3 x output_bitset8":
        ("ka_constant_bitset", [3], "kq_output_bitset", [8]),
    "C5 bytevalue_bitset3 x out+in_bitset5":
        ("ka_bytevalue_bitset", [3], "kq_output_and_input_bitset", [5]),
}

recs = json.load(open("d10/phase2/pp2_dev.json"))
order = {r["name"]: i for i, r in enumerate(recs)}
best = sorted(recs, key=lambda r: (-r["PP2_minus_R2"], -r["PP2"],
                                   order[r["name"]]))[0]
ka_fn, ka_args, kq_fn, kq_args = SPEC[best["name"]]
sel = {"name": best["name"], "note": best["note"],
       "ka_fn": ka_fn, "ka_args": ka_args,
       "kq_fn": kq_fn, "kq_args": kq_args,
       "dev_PP2": best["PP2"], "dev_R2": best["R2"],
       "dev_PP2_minus_R2": best["PP2_minus_R2"],
       "selection_rule": "max dev (PP2-R2), then max dev PP2, then order",
       "n_candidates_evaluated_on_dev": len(recs)}
json.dump(sel, open("d10/phase2/pp2_selection.json", "w"), indent=1)
print(json.dumps(sel, indent=1))
