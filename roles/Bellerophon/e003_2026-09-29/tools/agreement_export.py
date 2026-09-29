"""E-003 s4.3 agreement: export this seat's FROZEN tracer (bee_tracer.py sha256 823cbef1...) on Archaeon's sealed fresh set
(gate_close/BEE_FRESH_PRE.jsonl, sha256 937ffb58...; seed commit fefefe07...) in the declared exchange serialization
(archaeon/attribution/probes/bee_fresh.py docstring; only the docstring was read, not the code).

The driver adds NO semantics. Per pre-state:
- memory = mem, inputs = inputs, entry 0, budget 256, COPYALL allowed, L 64;
- initial labels = bee_tracer.initial_labels, with the window set to (CONST, "empty") when occupied is false (ruled
  reading 2);
- one bee_tracer.trace call, value-checked against the frozen VM (check=True).
It is a one-to-one relabelling of the tracer's output:
  ("E",X,j) -> ["E",X,j]; ("INPUT",k) -> ["INPUT",k]; ("CONST",kind) -> ["CONST",kind];
  ("COMPUTED",S) -> ["C", sorted base strings]; ("COMPUTED_FROM",x) -> ["F", sorted base strings of x];
  base ("E",X,j) -> "E|X|j"; ("INPUT",k) -> "INPUT|k".
  addr / ctrl / exec are AT STORE (the record of the locus's last store); they are omitted for unwritten loci.
PERFORMER (declared difference; not a gated field): the frozen tracer records the ENTITY BASES of the store opcode
byte's label. The export gives ["E",X,j] when that set has exactly one member, else null. So an opcode byte whose label
is COMPUTED from a single entity byte is exported as ENTITY here, where the exchange definition says null.
    python agreement_export.py PRE.jsonl OUT.jsonl
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
HARNESS = "C:/Users/James/e003_harness_16fc6c2a"
sys.path.insert(0, HARNESS)
from prometheus.z80atlas import vm  # noqa: E402
import bee_tracer as BT  # noqa: E402

L = 64; BUDGET = 256


def bstr(b):
    return "E|%s|%d" % (b[1], b[2]) if b[0] == "E" else "INPUT|%d" % b[1]


def lab(x):
    k = x[0]
    if k == "E":
        return ["E", x[1], x[2]]
    if k == "INPUT":
        return ["INPUT", x[1]]
    if k == "CONST":
        return ["CONST", x[1]]
    if k == "COMPUTED":
        return ["C", sorted(bstr(b) for b in x[1])]
    if k == "COMPUTED_FROM":
        return ["F", sorted(bstr(b) for b in BT.bases(x[1]))]
    raise ValueError(x)


def main() -> int:
    pre_p, out_p = sys.argv[1], sys.argv[2]
    with open(out_p, "w", encoding="utf-8", newline="\n") as fh:
        for line in open(pre_p, encoding="utf-8"):
            if not line.strip():
                continue
            r = json.loads(line)
            mem = bytearray.fromhex(r["mem"]); inputs = list(r["inputs"])
            labels = BT.initial_labels(L, len(inputs), vm.IN_BASE)
            if not r["occupied"]:
                for a in range(L, 2 * L):
                    labels[a] = ("CONST", "empty")
            _, recs, _ = BT.trace(vm, mem, L, BUDGET, inputs, allow_copyall=True, labels=labels, check=True)
            loci = []
            for i in range(L):
                x = recs[i]; o = {"i": i, "written": bool(x["written"]), "label": lab(x["data"])}
                if x["written"]:
                    o["addr"] = sorted(bstr(b) for b in x["addr"])
                    o["ctrl"] = sorted(bstr(b) for b in x["ctrl"])
                    o["exec"] = sorted(bstr(b) for b in x["exec"])
                    p = sorted(x["performer"])
                    o["performer"] = ["E", p[0][1], p[0][2]] if len(p) == 1 else None
                loci.append(o)
            fh.write(json.dumps({"k": r["k"], "kind": r["kind"], "loci": loci}, sort_keys=True) + "\n")
    print(json.dumps({"out": out_p, "sha256_lf": hashlib.sha256(pathlib.Path(out_p).read_bytes().replace(b"\r\n", b"\n")).hexdigest()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
