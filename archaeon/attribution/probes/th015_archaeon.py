"""TH-015 (Archaeon leg): what has to cross a generation for copying competence to stay above chance?

Input: member tapes of the block-13 dominant lineage recorded by th013_block13 (capable members only). For each tape T, find its
machinery M = executed loci whose single knockout (-> 0x00) removes birth ability, then intervene separately:

  MATERIAL_ONLY        T with M's bytes re-randomised (everything else T's material)          -> is the copied material enough?
  MACHINERY_ONLY       random background with M's bytes of T written in place                 -> is the machinery enough?
  EXECUTED_ONLY        random background with ALL executed loci X of T in place               -> machinery plus its executed context
  RANDOM_SAME_SIZE     random background with |M| random loci of T in place (control)          -> chance for a transplant of that size
  NEIGHBOUR_CONTEXT    T itself, facing a random neighbour window instead of zero              -> does copying need a clean neighbour?
  CONTROL_STATE        T itself, started at a random pc instead of 0                          -> does it need the start state?
  INPUT_SCAFFOLD       fraction of allowed inputs on which T gives a birth; and whether the input 128 (blocked in this arm) is used
  CHANCE               random tapes                                                            -> the floor
"capable" = a birth (>= 0.9 of the neighbour window written) on at least one of the arm's allowed inputs, zero neighbour unless
stated; "exact" = an exact self-copy. K backgrounds per intervention, fixed seed.
    python -m archaeon.attribution.probes.th015_archaeon TH013_OUT.json OUT.json [--k 40] [--tapes 24]
"""
import json
import random
import sys
import time

from archaeon.lineage import core as LC
from archaeon.z80atlas import vm
from archaeon.attribution.probes.th013_block13 import ALLOWED, G


def run(tape, nbr=LC.ZERO, pc0=0, inputs=ALLOWED):
    """(birth_any, exact_any, n_birth_inputs, executed mask of the first birth)"""
    nb = 0; ex = False; mask = None
    for x in inputs:
        r = vm.execute(tape, nbr, (x,), LC.STEP_CAP, True, -1.0, pc0)
        if sum(r["nbr_mask"]) / G >= 0.9:
            nb += 1; mask = mask or r["executed"]
            if r["nbr_window"] == tape: ex = True
    return nb > 0, ex, nb, mask


def machinery(tape):
    b, _, _, mask = run(tape)
    if not b: return None, None
    # full scan: the VM's `executed` mask marks opcode addresses only, not operand bytes, so knockouts are tried at every locus
    M = [p for p in range(G) if not run(bytes(tape[:p]) + b"\0" + tape[p + 1:])[0]]
    X = sorted(set(M) | {p for p in range(G) if mask[p]})
    return M, X


def graft(tape, loci, rng):
    t = bytearray(rng.randrange(256) for _ in range(G))
    for p in loci: t[p] = tape[p]
    return bytes(t)


def scramble(tape, loci, rng):
    t = bytearray(tape)
    for p in loci: t[p] = rng.randrange(256)
    return bytes(t)


def rate(tapes_fn, k):
    res = [run(tapes_fn())[:2] for _ in range(k)]
    return {"birth": sum(r[0] for r in res) / k, "exact": sum(r[1] for r in res) / k}


def main(inp, out, k, ntapes):
    t0 = time.time(); d = json.load(open(inp)); rng = random.Random(15)
    seen = {};
    for s in d["snapshots"]:
        for m in s["members"]:
            if m.get("birth_allowed") and m["tape"] not in seen: seen[m["tape"]] = (s["epoch"], m["ggen"])
    tapes = list(seen.items()); step = max(1, len(tapes) // ntapes); tapes = tapes[::step][:ntapes]
    rows = []
    for hx, (ep, gg) in tapes:
        T = bytes.fromhex(hx); M, X = machinery(T)
        if M is None: continue
        others = [p for p in range(G) if p not in M]
        row = {"tape": hx, "epoch": ep, "ggen": gg, "M": M, "X": X,
               "MATERIAL_ONLY": rate(lambda: scramble(T, M, rng), k),
               "MACHINERY_ONLY": rate(lambda: graft(T, M, rng), k),
               "EXECUTED_ONLY": rate(lambda: graft(T, X, rng), k),
               "RANDOM_SAME_SIZE": rate(lambda: graft(T, rng.sample(range(G), len(M)), rng), k),
               "NEIGHBOUR_CONTEXT": {"birth": sum(run(T, nbr=bytes(rng.randrange(256) for _ in range(G)))[0] for _ in range(k)) / k},
               "CONTROL_STATE": {"birth": sum(run(T, pc0=rng.randrange(1, G))[0] for _ in range(k)) / k}}
        b, e, nb, _ = run(T); row["INPUT_SCAFFOLD"] = {"birth_inputs": nb, "of_allowed": len(ALLOWED), "exact": e,
                                                        "birth_with_128": run(T, inputs=[128])[0]}
        rows.append(row)
    chance = rate(lambda: bytes(rng.randrange(256) for _ in range(G)), max(k * 10, 200))
    json.dump({"probe": "TH-015 archaeon", "input": inp, "k": k, "rows": rows, "chance": chance, "wall_s": round(time.time() - t0, 1)},
              open(out, "w"), indent=1)
    keys = ["MATERIAL_ONLY", "MACHINERY_ONLY", "EXECUTED_ONLY", "RANDOM_SAME_SIZE", "NEIGHBOUR_CONTEXT", "CONTROL_STATE"]
    print(json.dumps({"tapes": len(rows), "chance": chance,
                      "mean_birth": {kk: round(sum(r[kk]["birth"] for r in rows) / max(1, len(rows)), 3) for kk in keys},
                      "wall_s": round(time.time() - t0, 1)}))


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], a[1], int(a[a.index("--k") + 1]) if "--k" in a else 40, int(a[a.index("--tapes") + 1]) if "--tapes" in a else 24)
