"""T-003 (ops C-001/E-001): NPE provenance mapped onto WHO / WHERE / WHAT, in NPE's own terms. Standalone: NPE modules + stdlib only.

Replays NPE H2 RESERVOIR arms exactly as frozen (MANIFEST_FROZEN.json) with an OBSERVATION-ONLY copy of NPE's own tainted VM
(z8taint.run_tainted, the one RESERVOIR pair interactions use): the source is transformed at runtime to
  (1) note the address of the instruction being executed (`_ipc = pc` right after the fetch), and
  (2) log, for every permitted write, BEFORE it lands:
      (executing context `who`, target address, instruction address `_ipc`, prov[_ipc] = the context that last CHANGED the code byte, value).
Nothing the VM computes changes; the lineage hash per run is written so the verifier (M2, where the preserved replays live) can
check it against the earlier un-patched replay.

Per pair-tape birth, over the victim-half positions D (initial byte != donor byte, final byte == donor byte; P-11's definition),
the LAST write to each position is classified in NPE's terms:
  WHO   executing context: donor-context / victim-context
  WHERE instruction address: donor-half / victim-half / outside-both
  WHAT  code byte provenance at execution: original-of-its-half (prov 0) / changed-by-donor-context / changed-by-victim-context
  (VALUE: equals the donor's byte by construction of D.)
    python npe_b6_replay.py --npe <z80atlas-verify dir> --summary <NPE_LENS_SUMMARY.json> --out <out.json> [--workers 3] [--limit N]
"""
import hashlib
import inspect
import json
import os
import sys
import time
from collections import Counter
from multiprocessing import Pool

A = sys.argv[1:]
ARG = {k: A[A.index(k) + 1] for k in ("--npe", "--summary", "--out", "--workers", "--limit", "--smoke") if k in A}
Z2 = ARG["--npe"]
sys.path.insert(0, Z2)
_OBS = []
_PATCHED = []


def _patch():
    if _PATCHED: return                                                   # once per process: getsource cannot re-read a patched function
    import z8taint
    src = inspect.getsource(z8taint.run_tainted)
    a1 = "        op = mem[pc]\n"
    a2 = "            ctx.writes_blocked += 1\n            return\n        pv = ctx.prov\n"
    assert src.count(a1) == 1 and src.count(a2) == 1, "NPE z8taint source changed: refusing to patch"
    src = src.replace(a1, a1 + "        _ipc = pc\n", 1)
    src = src.replace(a2, a2 + "        _OBS.append((ctx.who, a, _ipc, (pv[_ipc] if pv is not None else -1), val & 0xFF))\n", 1)
    ns = dict(z8taint.__dict__); ns["_OBS"] = _OBS
    exec(compile(src, "z8taint_observed", "exec"), ns)
    z8taint.run_tainted = ns["run_tainted"]; _PATCHED.append(True)


def _pow2(n):
    p = 1
    while p < n: p <<= 1
    return p


def job_list(summary_path):
    man = json.load(open(os.path.join(Z2, "MANIFEST_FROZEN.json"), encoding="utf-8"))
    want = [k for k, v in json.load(open(summary_path, encoding="utf-8")).items() if v["by_kind"].get("PAIR_OVERWRITE", 0) > 0]
    jobs = []
    for name in want:
        spec, seed, arm = name.split("__"); seed = int(seed[1:])
        for b in man["bundles"]:
            if b["hypothesis_id"] != "H2" or b.get("specimen") != spec: continue
            for a in b["arms"]:
                c = a["cell"] if isinstance(a["cell"], dict) else eval(a["cell"])
                if a["arm"] == arm and int(a["seed"]) == seed and c.get("structure") == "RESERVOIR":
                    kw = a["kwargs"] if isinstance(a["kwargs"], dict) else eval(a["kwargs"])
                    jobs.append({"name": name, "cell": c, "seed": seed, "tier": a["tier"], "kwargs": kw})
    return jobs


def run_one(job):
    _patch()
    import world as W
    births = []

    class Obs(W.Runner):
        def _pair_interact(self, i, a, b):
            ga, gb = self._genome(a), self._genome(b); n = self.L
            pre = {id(a): a.oid, id(b): b.oid}; n0 = len(self.lineage); del _OBS[:]
            super()._pair_interact(i, a, b)
            new = [e for e in self.lineage[n0:] if e.get("kind") == "birth"]
            if not new: return
            size = _pow2(2 * n); tape = bytearray(size); tape[0:len(ga)] = ga; tape[n:n + len(gb)] = gb
            init = bytes(tape); last = {}
            for rec in _OBS:
                tape[rec[1]] = rec[4]; last[rec[1]] = rec
            for e in new:
                body = a if a.oid == e["child"] else (b if b.oid == e["child"] else None)
                if body is None: continue
                vbase = 0 if body is a else n; dbase = n if body is a else 0
                donor_who = 2 if body is a else 1; victim_who = 1 if body is a else 2
                donor = (bytes(gb if body is a else ga) + bytes(n))[:n]
                D = [p for p in range(n) if init[vbase + p] != donor[p] and tape[vbase + p] == donor[p]]
                c = Counter(); unwritten = 0
                for p in D:
                    r = last.get(vbase + p)
                    if r is None: unwritten += 1; continue
                    who = "donor_ctx" if r[0] == donor_who else ("victim_ctx" if r[0] == victim_who else "ctx%d" % r[0])
                    ip = r[2]
                    where = "donor_half" if dbase <= ip < dbase + n else ("victim_half" if vbase <= ip < vbase + n else "outside")
                    what = "original" if r[3] == 0 else ("changed_by_donor" if r[3] == donor_who else ("changed_by_victim" if r[3] == victim_who else "prov%d" % r[3]))
                    c["%s|%s|%s" % (who, where, what)] += 1
                p11 = e.get("p11") or {}
                births.append({"child": e["child"], "victim_old_oid": pre[id(body)], "n": n, "D": len(D), "unwritten_D": unwritten,
                               "who_where_what": dict(c), "native_donor_authored_share": p11.get("donor_authored_share_ordinary"),
                               "native_C2": p11.get("C2"), "native_C4": p11.get("C4"), "native_C5": p11.get("C5"), "native_causal": e.get("causal"),
                               "writes_logged": len(_OBS)})

    kw = dict(job["kwargs"]); kw.pop("implant_source", None); hx = kw.pop("implant_hex", None)
    if hx: kw["implant_bytes"] = bytes.fromhex(hx)
    if "--smoke" in ARG: kw["max_epochs"] = int(ARG["--smoke"])
    t0 = time.time(); r = Obs(job["cell"], job["seed"], tier=job["tier"], **kw); r.run()
    lin = hashlib.sha256(json.dumps(r.lineage, sort_keys=True, default=str).encode()).hexdigest()
    return {"name": job["name"], "lineage_sha256": lin, "lineage_n": len(r.lineage), "births": births, "wall_s": round(time.time() - t0, 1)}


def main():
    jobs = job_list(ARG["--summary"])
    if "--limit" in ARG: jobs = jobs[:int(ARG["--limit"])]
    t0 = time.time()
    with Pool(int(ARG.get("--workers", 3))) as p:
        res = p.map(run_one, jobs, chunksize=1)
    out = {"task": "T-003", "runs": len(res), "wall_s": round(time.time() - t0, 1), "host": os.uname().nodename if hasattr(os, "uname") else "?",
           "python": sys.version.split()[0], "results": res}
    out["result_sha256"] = hashlib.sha256(json.dumps(res and [{k: v for k, v in r.items() if k != "wall_s"} for r in res], sort_keys=True).encode()).hexdigest()
    json.dump(out, open(ARG["--out"], "w", encoding="utf-8"))
    print(json.dumps({"runs": len(res), "births": sum(len(r["births"]) for r in res), "wall_s": out["wall_s"], "result_sha256": out["result_sha256"]}))


if __name__ == "__main__":
    main()
