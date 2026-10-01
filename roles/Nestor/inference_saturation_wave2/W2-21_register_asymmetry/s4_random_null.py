"""Step 4: a random-screened null. Draw uniform random 64-byte genomes (seeded), screen each from FRESH in its own
context on side 0 and on side 1 exactly like s10 (HALT partner, good = victim half >= 0.9 identical), and for every
screen-passing genome measure what s1/s2 measure for the world corpus: operand provenance (taint), random-register
good rate (30 sets), and number of inherited copy operands. Question: is the side-1 'free zero' leaning already
present in unselected FRESH-screened copiers (structural), or is it world side-0 copiers that are unusual (selection)?
Cell: 7ae3 DENSE environment (the VM does not depend on the cell; params identical: n 64, budget 300, mask 42)."""
import json, pathlib, random, sys, collections, time
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-16_side1_heredity"))
sys.path.insert(0, str(HERE))
from _env import A                                   # noqa: E402
from s10_side0_register_dependence import trial      # noqa: E402
from s1_operand_taint import own_run, child_copy     # noqa: E402
from _taint import REGSET                            # noqa: E402

N = int(sys.argv[1]) if len(sys.argv) > 1 else 150000

if __name__ == "__main__":
    t0 = time.time()
    P = A.params("DENSE", "7ae3"); _, _, z = A.env("DENSE", "7ae3")
    rng = random.Random("W2-21-null")
    found = {0: [], 1: []}
    for i in range(N):
        G = bytes(rng.randrange(256) for _ in range(64))
        for s in (0, 1):
            if trial(z, P, G, s, None):
                found[s].append(G.hex())
    print("screened", N, {s: len(v) for s, v in found.items()}, round(time.time() - t0))
    out = {"N": N, "found": {s: len(v) for s, v in found.items()}, "summary": {}, "genomes": {}}
    for s in (0, 1):
        c = collections.Counter(); both = 0
        for h in found[s]:
            G = bytes.fromhex(h)
            other = trial(z, P, G, 1 - s, None)
            both += other
            res = own_run(G, s); cp, _ = child_copy(res, s)
            rr = random.Random("W2-16-regs-null-" + h)
            k = sum(trial(z, P, G, s, ([rr.randrange(256) for _ in range(8)], rr.randrange(2), rr.randrange(2)))
                    for _ in range(30))
            inh = {o: bool(set(cp["t_" + o]) & REGSET) for o in ("src", "dst", "cnt")}
            c["randregs_good"] += k; c["trials"] += 30; c["n"] += 1
            for o in ("src", "dst", "cnt"):
                c[o + "_inherited"] += inh[o]
            c["both_addr_set"] += (not inh["src"] and not inh["dst"])
            c["n_inh_addr=%d" % (inh["src"] + inh["dst"])] += 1
            c["op_" + cp["op"]] += 1
            c["geom_%d->%d" % (cp["src"], cp["dst"])] += 1
            c["randregs_ge_0.9"] += k >= 27
            out["genomes"].setdefault("side%d" % s, []).append({"hex": h, "copies_other_side": other, "op": cp["op"],
                                                                "src": cp["src"], "dst": cp["dst"], "inh": inh,
                                                                "randregs_good_of_30": k})
        c["also_copies_other_side"] = both
        out["summary"]["side%d" % s] = dict(sorted(c.items()))
        print(s, out["summary"]["side%d" % s])
    out["seconds"] = round(time.time() - t0)
    (HERE / "s4_random_null.json").write_text(json.dumps(out, indent=1))
