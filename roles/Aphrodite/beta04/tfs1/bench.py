"""TFS-1 throughput: enumeration and mutation candidates/sec by size, and memory. Single process, OMP_NUM_THREADS=1.
Run from beta04/:  python -m tfs1.bench   -> tfs1/TFS1_THROUGHPUT.json
A candidate = one program evaluated on 8 dev examples with early exit (the charged unit). The target is unreachable,
so whole size classes are walked (size 8 capped at CAP8 candidates)."""
import json
import os
import platform
import random
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
import psutil                                   # noqa: E402

from tfs1 import core as C                      # noqa: E402
from tfs1.enum import Enumerator                # noqa: E402
from tfs1.library import Library                # noqa: E402
from tfs1.mutate import Mutator, rng_for        # noqa: E402
from tfs1.membrane import code_hashes           # noqa: E402

HERE = Path(__file__).resolve().parent
CAP8 = 1_000_000


def rss_mb():
    return round(psutil.Process(os.getpid()).memory_info().rss / 1e6, 1)


def dev_set():
    r = random.Random(1)
    ins = [[r.randint(-5, 9) for _ in range(r.randint(1, 8))] for _ in range(8)]
    return [(i, 10 ** 15 + 7) for i in ins]         # unreachable output: forces full walks


def small_library():
    lib = Library()
    a, _ = lib.promote_lambda(C.parse("(lam x (add (mul x x) 1))"))
    lib.promote_lambda(C.parse("(lam a (lam b (sub (mul a 2) b)))"))
    lib.promote_body(C.parse("(sum (map h0 h1))"))
    lib.promote_body(C.parse("(div (head h0) (len h0))"))
    lib.promote_body(C.parse("(sum (map (lam x (%s (%s x))) h0))" % (a.id, a.id)))
    return lib


def bench_enum(lib, label):
    E = Enumerator(lib)
    dev = dev_set()
    rows = []
    for n in range(4, 9):
        size_n = E.count("Int", (), n)
        before = E.cumulative("Int", n - 1)
        # walk earlier classes first (not timed) so tables exist; then time class n alone
        E.search(dev, "Int", 0, "bench", before, max_size=n - 1)
        lim = min(size_n, CAP8)
        t0 = time.perf_counter()
        cpu0 = time.process_time()
        C.U[0] = C.U[1] = 0
        k = 0
        for _key, t in E.keyed_iter("Int", n, 0, "bench", limit=lim):
            fn = E.compile_root(t)
            C.check_dev(fn, dev)
            k += 1
        dt = time.perf_counter() - t0
        cpu = time.process_time() - cpu0
        rows.append({"size": n, "class_size": size_n, "walked": k, "wall_s": round(dt, 2), "cpu_s": round(cpu, 2),
                     "cand_per_s": round(k / dt), "units_expanded_per_cand": round(C.U[0] / k, 2),
                     "rss_mb_after": rss_mb()})
        print(label, rows[-1], flush=True)
    return rows


def bench_mut(lib, label, n_children=20000):
    E = Enumerator(lib)
    mut = Mutator(E, max_fill=3, max_size=16)
    dev = dev_set()
    rows = []
    for n in range(4, 9):
        rng = rng_for(0, "bench-mut-%d" % n)
        parents = [t for t, _s in E.terms("Int", (), min(n, 7))][:50000]
        if n == 8:   # size-8 parents: one insertion over size-7 terms is cheaper than materialising class 8
            parents = [p for p in (mut._insert(t, mut.sites(t, "Int")[0], rng) for t in parents[:5000]) if p][:2000]
        t0 = time.perf_counter()
        k = rej = 0
        while k < n_children:
            p = parents[rng.randrange(len(parents))]
            c = mut.mutate(p, "Int", rng)
            if c is None:
                rej += 1
                continue
            fn = C.compile_term(c, E.lib, None, swap=E.swap)
            C.check_dev(fn, dev)
            k += 1
        dt = time.perf_counter() - t0
        rows.append({"parent_size": n, "children": k, "rejected": rej, "wall_s": round(dt, 2),
                     "cand_per_s": round(k / dt), "rss_mb_after": rss_mb()})
        print(label, rows[-1], flush=True)
    return rows


if __name__ == "__main__":
    out = {"host": platform.node(), "python": platform.python_version(), "processor": platform.processor(),
           "omp_num_threads": os.environ.get("OMP_NUM_THREADS"), "code_sha256": code_hashes(),
           "rss_mb_start": rss_mb()}
    out["enumeration_pristine"] = bench_enum(None, "enum/pristine")
    out["enumeration_lib5"] = bench_enum(small_library(), "enum/lib5")
    out["mutation_pristine"] = bench_mut(None, "mut/pristine")
    out["mutation_lib5"] = bench_mut(small_library(), "mut/lib5")
    out["rss_mb_peak_end"] = rss_mb()
    (HERE / "TFS1_THROUGHPUT.json").write_text(json.dumps(out, indent=1, sort_keys=True))
    print("written")
