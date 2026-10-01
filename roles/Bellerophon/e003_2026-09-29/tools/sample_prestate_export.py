"""E-003 production s4.3 agreement PACKAGING (BEE GO condition 3). Declared before production; adds no semantics.

For every s4-sampled birth, write one pre-state record in the fresh-set record shape that the frozen agreement driver
(agreement_export.py, a320d94b) reads, plus the persisted origin data condition 3 asks for:
    {"k": birth_index, "kind": "production", "mem": 256-byte hex pre-state, "inputs": [...], "occupied": bool,
     "pre_labels": {"writer": [...64 origin labels], "occupant": [...64] | null},
     "entity_origins": {"W": writer org id, "P": occupant org id | null}, "tick": t, "child": child org id}
Origin labels are the persisted vectors exported by traced_world.py: ["ORIG", org, i], ["NEW", tick, org, addr, kind]
or ["MUT", tick, seq].
The frozen driver then produces the per-locus exchange-format output from the same records
(agreement_export.py PRE OUT; it reads only k, kind, mem, inputs, occupied).
    python sample_prestate_export.py <births_export.jsonl.gz> <sample.json> <out PRE.jsonl>
"""
import gzip
import json
import sys


def main() -> int:
    exp, samp, out = sys.argv[1], sys.argv[2], sys.argv[3]
    keep = set(json.load(open(samp, encoding="utf-8"))["sample"])
    n = 0
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        for line in gzip.open(exp, "rt", encoding="utf-8"):
            r = json.loads(line)
            if r["birth_index"] not in keep:
                continue
            ps = r["pre_state"]
            rec = {"k": r["birth_index"], "kind": "production", "mem": ps["mem"], "inputs": ps["inputs"],
                   "occupied": not ps.get("window_empty"),
                   "pre_labels": {"writer": r["vec_writer_pre"], "occupant": r["vec_occupant_pre"]},
                   "entity_origins": {"W": r["writer"], "P": r["occupant"]}, "tick": r["tick"], "child": r["child"]}
            fh.write(json.dumps(rec, sort_keys=True) + "\n"); n += 1
    if n != len(keep):
        raise SystemExit("sampled births missing from the export: %d of %d" % (n, len(keep)))
    print(json.dumps({"records": n, "out": out}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
