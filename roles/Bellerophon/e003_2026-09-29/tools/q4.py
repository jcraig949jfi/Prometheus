"""E-003 Q4: material without capability (v4 s2.3 Q4 + v5 Amendment C4.5), per UNIQUE child tape.

Capable = the child, as the writer, in isolation (frozen VM, the run's SHARED layout, entry 0, budget 256, COPYALL as the
run allows), makes an exact copy of its own PRE-execution tape BY ITS OWN STORES in >= 50% of 320 trials (8 occupants
x 40 inputs). "By its own stores" is read from this seat's tracer: every window locus is written in the trial, the
final window equals the child's pre-execution tape, and the last store to every window locus has performer entity set
== {W}, i.e. its opcode byte was the child's own material (overlap-aware; no source-address or code-location criterion).

- ISOLATED (primary): 8 random 64-byte occupants x 40 random task inputs.
- HOST-ASSISTED (C4.5): 8 occupants drawn from the run's own SELF-PERFORMED children (real hosts) x 40 random inputs.
  This separates "incapable" from "capable only with a host".
Draws are deterministic: random.Random(int(sha256(tape_hex + '|' + arm)[:16], 16)).
    python q4.py --export <births_export.jsonl.gz> --out <q4.jsonl.gz> --workers 12
"""
from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import json
import multiprocessing as mp
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
HARNESS = "C:/Users/James/e003_harness_16fc6c2a"
L = 64; BUDGET = 256; N_OCC = 8; N_IN = 40
_G = {}


def _init(hosts, allow):
    sys.path.insert(0, HARNESS)
    from prometheus.z80atlas import vm
    import bee_tracer as BT
    _G.update(vm=vm, BT=BT, hosts=hosts, allow=allow)


def _trial(tape: bytes, occ: bytes, x: int) -> bool:
    vm = _G["vm"]; BT = _G["BT"]
    mem = bytearray(256); mem[:L] = tape; mem[L:2 * L] = occ; mem[vm.IN_BASE] = x
    after, recs, _ = BT.trace(vm, mem, L, BUDGET, [x], allow_copyall=_G["allow"], check=False)
    if after[L:2 * L] != tape:
        return False
    for i in range(L):
        r = recs[i]
        if not r["written"] or {b[1] for b in r["performer"]} != {"W"}:
            return False
    return True


def _one(tape_hex: str) -> dict:
    tape = bytes.fromhex(tape_hex); out = {"tape": tape_hex}
    for arm in ("isolated", "host"):
        rng = random.Random(int(hashlib.sha256((tape_hex + "|" + arm).encode()).hexdigest()[:16], 16))
        if arm == "isolated":
            occs = [bytes(rng.randrange(256) for _ in range(L)) for _ in range(N_OCC)]
        else:
            H = _G["hosts"]
            occs = [bytes.fromhex(H[rng.randrange(len(H))]) for _ in range(N_OCC)] if H else []
        k = 0; n = 0
        for occ in occs:
            for _ in range(N_IN):
                x = rng.randrange(256); n += 1; k += _trial(tape, occ, x)
        out[arm] = {"k": k, "n": n, "capable": (n > 0 and k >= 0.5 * n)}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", required=True); ap.add_argument("--out", required=True); ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    tapes = collections.OrderedDict(); hosts = []; allow = None
    for line in gzip.open(a.export, "rt", encoding="utf-8"):
        r = json.loads(line)
        allow = r["pre_state"]["allow_copyall"]
        tapes.setdefault(r["child_tape"], 0); tapes[r["child_tape"]] += 1
        W = [x for x in r["loci"] if x["written"]]
        perf = collections.Counter(p[0] for x in W for p in x["performer"])
        if W and perf and perf.most_common(1)[0][0] == "W":
            hosts.append(r["child_tape"])
    hosts = sorted(set(hosts))
    todo = list(tapes)[: a.limit] if a.limit else list(tapes)
    with mp.Pool(a.workers, initializer=_init, initargs=(hosts, allow)) as pool, gzip.open(a.out, "wt", encoding="utf-8", newline="\n") as fh:
        for res in pool.imap(_one, todo, chunksize=16):
            fh.write(json.dumps(res, sort_keys=True) + "\n")
    print(json.dumps({"unique_tapes": len(todo), "host_pool": len(hosts), "out": a.out,
                      "sha256": hashlib.sha256(pathlib.Path(a.out).read_bytes()).hexdigest()}))
    return 0


if __name__ == "__main__":
    mp.freeze_support()
    raise SystemExit(main())
