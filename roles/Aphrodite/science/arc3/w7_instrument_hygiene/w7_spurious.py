"""W7 PKG-6 (3): spurious fallback first hits -- cost/benefit of two
Q2-beyond-coverage discriminators, on a sample of W2's 4M-escrow NAT cells.

Sample (from w2_escrow16_NAT_*.jsonl, C2 foundry, label A19-pilot-PRISTINE):
  all fallback first hits that were NOT T4-qualified (spurious), all coverage
  first hits that were not T4-qualified, and 10 fallback first hits that were
  T4-qualified (controls: a discriminator must not cost them anything).
Variants (each re-walks the cell with a18.fast_cost, exact, escrow 4M):
  HOLD8  post-hit hold-out battery: a hit counts only if it also matches 8
         held-out examples from a SEPARATE stream (label W7-holdout-...);
         a failing hit is discarded and the walk continues. Charge-equivalent
         to walking with dev + hold-out as the consistency set.
  DEV+4  Q2 widened beyond coverage: the dev set is extended along the SAME
         dev stream by 4 examples (what a Q2 whose wrong-set included the
         fallback's early wrong programs would buy at the next ladder rungs).
Also, per spurious hit: the minimal number of extra same-stream dev examples
(1..40) that rejects it (analytic; no walk).
Usage: python w7_spurious.py [workers]   -> W7_SPURIOUS.json
"""
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor

from w7_common import *              # noqa: F401,F403
import tribunal_t4 as T4             # noqa: E402
import tribunal_t4_v1a as T4A        # noqa: E402

W2 = ROOT / "science" / "arc3" / "w2_learnability"
ESC = 4_000_000


class _Cell:
    def __init__(self, parsed, seed):
        self.parsed, self.seed = parsed, seed


def sample():
    seen = {}
    for f in ("w2_escrow16_NAT_s0.jsonl", "w2_escrow16_NAT_s1.jsonl", "w2_escrow16_NAT_s1r.jsonl"):
        for x in open(W2 / f, encoding="utf-8"):
            r = json.loads(x)
            seen[r["name"]] = r
    byname = {r["name"]: r for r in rows("A19")}
    out, ctrl = [], []
    for n in sorted(seen):
        for i, c in enumerate(seen[n]["cells"]):
            if c["prog"] is None:
                continue
            kind = ("spurious_fallback" if c["segment"] == "fallback" and not c["T4"] else
                    "spurious_cov" if c["segment"] == "cov" and not c["T4"] else
                    "true_fallback" if c["segment"] == "fallback" else None)
            if kind == "true_fallback":
                ctrl.append((byname[n], i, c, kind))
            elif kind:
                out.append((byname[n], i, c, kind))
    return out + ctrl[:10]


def job(args):
    a18.worker_init()
    r, i, c0, kind = args
    prov = prov_of(r)
    T4.use_provider(prov)
    w = ("fold", r["init"], r["body"], r["final"])
    lib = FR.KLib(FR.pristine().entries)
    lab = "%s-pilot-PRISTINE" % r["_tag"]
    dev = FR.Cell(prov, r["name"], i, r["Q2_size"], label=lab)
    rec = {"name": r["name"], "cell": i, "kind": kind, "Q2_size": r["Q2_size"], "orig_charge": c0["charge"],
           "orig_prog": c0["prog"], "orig_T4": c0["T4"]}
    # reproduction of W2's walk
    t = time.time()
    ch, prog = a18.fast_cost(lib, dev, ESC)
    rec["repro_ok"] = (ch == c0["charge"] and list(prog or []) == list(c0["prog"] or []))
    rec["sec_base"] = round(time.time() - t, 1)
    # analytic: minimal extra same-stream dev examples rejecting the original hit
    ext = FR.Cell(prov, r["name"], i, r["Q2_size"] + 40, label=lab)
    assert ext.parsed[:r["Q2_size"]] == dev.parsed
    k_rej = None
    for k, (nums, gold) in enumerate(ext.parsed[r["Q2_size"]:], 1):
        if str(G.run_program(tuple(c0["prog"]), nums, True)) != gold:
            k_rej = k
            break
    rec["extra_examples_to_reject"] = k_rej
    hold = FR.Cell(prov, r["name"], i, 8, label="W7-holdout-" + lab)
    variants = {"HOLD8": _Cell(dev.parsed + hold.parsed, dev.seed),
                "DEV+4": FR.Cell(prov, r["name"], i, r["Q2_size"] + 4, label=lab)}
    for vn, cell in variants.items():
        t = time.time()
        ch, prog = a18.fast_cost(lib, cell, ESC)
        q = bool(prog) and T4A.direct_score(tuple(prog), r["name"], w, "v1")["qualified"]
        qa = bool(prog) and T4A.direct_score(tuple(prog), r["name"], w, "v1a")["qualified"]
        rec[vn] = {"charge": ch, "prog": list(prog) if prog else None, "T4_v1": q, "T4_v1a": qa,
                   "sec": round(time.time() - t, 1)}
    # confirm direct scoring vs the real tribunal on the original hit
    rec["orig_T4_direct"] = T4A.direct_score(tuple(c0["prog"]), r["name"], w, "v1")["qualified"]
    return rec


if __name__ == "__main__":
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    lim = int(sys.argv[2]) if len(sys.argv) > 2 else None
    S = sample()
    if lim:
        S = S[:lim]
    print("sample", len(S), flush=True)
    with ProcessPoolExecutor(max_workers=workers, initializer=a18.worker_init) as ex:
        res = list(ex.map(job, S))
    (HERE / ("W7_SPURIOUS%s.json" % ("_test" if lim else ""))).write_text(json.dumps(res, indent=1))
    print("done", flush=True)
