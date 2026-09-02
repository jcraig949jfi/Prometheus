"""PP2 construction on the DEV set. The GATE set is never touched here.

For each candidate (KA, KQ) pair we measure, downstream and at matched
budget/seeds:
    PP2      retrieval by Hamming on the candidate's keys
    R2(PP2)  the SAME artifact keys, but each task's query key is replaced
             by another task's query key under a fixed derangement --
             identical machinery, task-conditional coupling destroyed
Anything that does not beat its own query-shuffled twin has demonstrated
no task-conditional relevance, whatever it does against U.
"""
import sys, json, random, time
import numpy as np
sys.path.insert(0, "d10")
from lib import organizer as og, pp2 as PP
from lib.acquire import acquire
from lib.objective import primary_objective
from foundry.tasks.base import ExactTask
from foundry.engines.gp.stackvm.adapter import StackVMAdapter
from foundry.engines.base import EngineLimits
from foundry.core.seeds import derive_seed

eng = StackVMAdapter()
LIM = EngineLimits(max_steps=200, timeout_s=5.0)
K, B_EVAL, N_SEEDS = 4, 400, 4

D = json.load(open("d10/phase2/dataset.json"))
corpus = [bytes.fromhex(h) for h in D["corpus_hex"]]
ids = [f"a{i}" for i in range(len(corpus))]
dev = [(d["family"],
        ExactTask(train_cases=[(list(a), b) for a, b in d["train"]],
                  test_cases=[(list(a), b) for a, b in d["test"]]))
       for d in D["dev_tasks"]]
fams = [f for f, _ in dev]
print(f"corpus={len(corpus)} dev={len(dev)}", flush=True)


def family_block_derangement(fams, seed):
    """sigma(i) is never in i's own family; fixed, seeded, and asserted."""
    n = len(fams)
    rng = random.Random(seed)
    for _ in range(10000):
        perm = list(range(n))
        rng.shuffle(perm)
        if all(fams[perm[i]] != fams[i] for i in range(n)):
            return perm
    raise RuntimeError("no family-disjoint derangement found")


SIGMA = family_block_derangement(fams, derive_seed(555, "sigma", "dev"))
assert all(fams[SIGMA[i]] != fams[i] for i in range(len(dev)))


def evaluate_pair(name, ka, kq, note=""):
    """PP2 is packaged as a REAL organizer genome and driven through the same
    decode -> build -> query path an evolved organizer would use. Passing a
    bare KA program to build_organization would silently DECODE it as a
    genome and truncate it (this bug invalidated an earlier dev run)."""
    t0 = time.perf_counter()
    genome = PP.make_genome(ka, kq)
    dka, dkq = og.decode(genome)
    assert dka == ka and dkq == kq, "genome round-trip failed"
    org = og.build_organization(genome, ids, corpus)
    st = org.stats()
    qkeys = [og.query_key(genome, t.evidence()) for _, t in dev]
    kq_steps = og.key_and_steps(kq, og.evidence_words(dev[0][1].evidence()))[1]
    res = {}
    for arm, keyfn in (("PP2", lambda j: qkeys[j]),
                       ("R2", lambda j: qkeys[SIGMA[j]])):
        out = []
        for j, (fi, task) in enumerate(dev):
            got = og.retrieve(org, keyfn(j), K, derive_seed(96, "ret", f"{j}"))
            seeds_g = [corpus[ids.index(a)] for a, _ in got]
            for s in range(N_SEEDS):
                out.append(acquire(eng, task,
                                   derive_seed(93, "devcap", f"{j}", f"{s}"),
                                   B_EVAL, seeds_g, LIM))
        res[arm] = primary_objective(out)
    rec = {"name": name, "note": note,
           "ka_bytes": len(ka), "kq_bytes": len(kq),
           "ka_steps_per_artifact": org.build_steps / max(len(corpus), 1),
           "kq_steps": kq_steps,
           "n_distinct_keys": st["n_distinct_keys"],
           "live_bits": st["live_bits"],
           "key_entropy_bits": round(st["key_entropy_bits"], 3),
           "n_distinct_query_keys": len(set(qkeys)),
           "PP2": round(res["PP2"], 4), "R2": round(res["R2"], 4),
           "PP2_minus_R2": round(res["PP2"] - res["R2"], 4),
           "seconds": round(time.perf_counter() - t0, 1)}
    print(f"{name:34s} PP2={rec['PP2']:.4f} R2={rec['R2']:.4f} "
          f"diff={rec['PP2_minus_R2']:+.4f} keys={rec['n_distinct_keys']:5d} "
          f"qkeys={rec['n_distinct_query_keys']:2d} "
          f"[{rec['seconds']}s]", flush=True)
    return rec


CANDS = [
    ("C1 bytevalue_bitset3 x output_bitset8",
     PP.ka_bytevalue_bitset(3), PP.kq_output_bitset(8),
     "byte values of the genotype head vs train output values, mod 64"),
    ("C2 bytevalue_bitset2 x output_bitset8",
     PP.ka_bytevalue_bitset(2), PP.kq_output_bitset(8),
     "shorter artifact scan, more headroom under the step cap"),
    ("C3 opcode_bitset3 x output_bitset8",
     PP.ka_opcode_bitset(3), PP.kq_output_bitset(8),
     "decoded opcodes rather than raw byte values"),
    ("C4 constant_bitset3 x output_bitset8",
     PP.ka_constant_bitset(3), PP.kq_output_bitset(8),
     "only bytes following a PUSH1, i.e. literal constants"),
    ("C5 bytevalue_bitset3 x out+in_bitset5",
     PP.ka_bytevalue_bitset(3), PP.kq_output_and_input_bitset(5),
     "query signature uses inputs as well as outputs"),
]

recs = []
for n, ka, kq, note in CANDS:
    recs.append(evaluate_pair(n, ka, kq, note))
    json.dump(recs, open("d10/phase2/pp2_dev.json", "w"), indent=1)
print("DONE")
