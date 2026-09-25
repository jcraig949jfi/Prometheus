"""ACCEL_CANARY_RUNPOD_v1 runner + comparator.

Executes the frozen canary (ACCEL_CANARY_RUNPOD_v1.md) for the accelerated
backend in fasteval.py and writes ACCEL_EQUIVALENCE_<backend>_<host>.json with
verdict EQUIVALENT / NOT_EQUIVALENT and indicative speedups.

    python run_canary.py --host M4 --workers 2
    python run_canary.py --host runpod-<pod> --workers 8 --out /app/out

Parts:
  (a) evaluator differential  fasteval.run_program vs basis_v4.run_program
  (b) search equivalence      fasteval.search_collect vs run_tier3c.search_collect
                              on all 480 Tier-3C transplant cells
  (c) end-to-end              full run_tier3c.main with fasteval installed, into a
                              scratch dir, compared to the committed JSONs
Any mismatch => NOT_EQUIVALENT.
"""
import argparse
import hashlib
import json
import multiprocessing as mp
import os
import platform
import random
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ACCEL = Path(__file__).resolve().parent
ENGINE = ACCEL.parent
for p in (str(ENGINE), str(ACCEL)):
    if p not in sys.path:
        sys.path.insert(0, p)

BACKEND = "runpod-backend"
PINNED = {
    "basis_v4.py": "221d4c62a20939a5e1d5e4ca8e31006a8e0d04917e801a328675c02e1b8c40aa",
    "run_tier3c.py": "9f4912474b68842416c401a54e65ba1127877c4f4a7302ea6ee350e5a386e751",
    "tier3c.py": "38647cae5f8e3868683c252706e0c40c49a93aadd84c1a497402f3c5ba4ace93",
    "conformance.py": "ab04d1ebe0098a2d0fda741d481420e72cc1c159cbb01fe244683af3f78840bc",
    "engine.py": "cb3e91ebf4e4d30e9a52d58d72d8859a30deeb015771e6d7a9e683954f74764c",
    "meta_tribunal.py": "3a7dcfedc5bd2eda9650b08dbc0bdddc642f8941051c48c8b709c30e1f20549d",
    "semantics.py": "5312f052cc7d19861d598825efd3565ac0d3697efa202ba6bf73e2e709674f94",
    "TIER3C_RESULTS_2026-09-22.json":
        "bdeb3ad831d25fca53b7297a6b8ecee450726e419f119177c3076c6ed9321bbd",
    "TIER3C_ARTIFACT_2026-09-22.json":
        "afe040e960a0ee056160347c633553606a1bb848a611721699c928c1b7eb075e",
}
# ADDENDUM 1: portable pins -- sha256 of the git blob (LF) at science SHA cf601fa3e.
PINNED_LF = {
    "basis_v4.py": "bdc601f2b0fae23bde5d1b9c2e0648d38d7d0400162aa85cfcfdcb001c34a1e4",
    "run_tier3c.py": "96ee9332627dc49176bd1a008c7927f3c451a69a8e801f7498268a6e360260f0",
    "tier3c.py": "a7d2b6d16472acf206d94b466e114348298822d2aff065ccf5ec8436c530fb79",
    "conformance.py": "db7c48be67cee2dd452e3e45dbabcda81be43a13838a69c626d21fa0a33caef2",
    "engine.py": "93bb1a259bbd90d0bf65b6753327a09bd189dafd9da41478ce072ad7d8a2adbe",
    "meta_tribunal.py": "43ee32067d27bc339bf87b598d221777adb9554703c5ed467f2205f8eba202db",
    "semantics.py": "775032a838e6805f5fadc7bf316c72689d5fcb8d260887bb5730521d39c181be",
    "TIER3C_RESULTS_2026-09-22.json":
        "b21bbbd86a342102252707e0991ad192a4609037fc786712521583388d56ee6c",
    "TIER3C_ARTIFACT_2026-09-22.json":
        "ccd36cf4f4278e0e6e4c856ae9724a2539dee38609620b879fc08b258bcf7aca",
}
REF_RESULTS = ENGINE / "TIER3C_RESULTS_2026-09-22.json"
REF_ARTIFACT = ENGINE / "TIER3C_ARTIFACT_2026-09-22.json"
REF_SERIAL_SECONDS = 1196.7
WALL_FIELDS = ("written_utc", "total_seconds")

# extra boundary / extreme input shapes for (a) A1 (declared in the frozen spec)
EXTRA_SHAPES = [[0], [0, 0, 0], [-1, 2], [1, -1, 1], [-5, -7, -9], [10 ** 12, 3],
                [3, 10 ** 12, 7], [999, 97, 999], [2, 0, 5], [12, 30, 7, 3]]


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _sha_lf(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def check_pins():
    """A file matches iff its LF-normalised bytes hash to the pinned git blob
    (ADDENDUM 1); the original M4 CRLF pin is also accepted."""
    drift = {}
    for n in PINNED:
        if _sha(ENGINE / n) != PINNED[n] and _sha_lf(ENGINE / n) != PINNED_LF[n]:
            drift[n] = _sha_lf(ENGINE / n)
    return drift


def _same(a, b):
    return (a is None and b is None) or (type(a) is type(b) and a == b)


# ---------------------------------------------------------------- shared setup
def reference_setup():
    """Libraries and cell parameters exactly as the reference run built them."""
    import run_tier3c as R
    ref = json.loads(REF_RESULTS.read_text(encoding="utf-8"))
    art = json.loads(REF_ARTIFACT.read_text(encoding="utf-8"))
    evolved = R.Lib(art["evolved_entries"])
    assert evolved.sha256() == art["evolved_sha256"] == ref["evolved_sha256"]
    base = R.pristine()
    assert base.sha256() == art["pristine_sha256"]
    arms = [("EVOLVED", evolved), ("PRISTINE", base)]
    arms += [("SHAM_%d" % k, R.Lib(s)) for k, s in enumerate(R.stage_shams())]
    sizes = {f: ref["generator_qualification"][f]["size"] for f in ref["families"]}
    return ref, arms, sizes


def cell_inputs(fam, arm, i, size):
    import engine as E
    import tier3c as T
    rng = random.Random(E.search_entropy("T3C-%s-%s-%03d" % (fam, arm, i)))
    dev = T.tasks(fam, size, E.dev_entropy("T3C-rx-%s-%03d" % (fam, i), 0))
    return rng, dev


# ---------------------------------------------------------------- (a)
def part_a(head=2000, stride=97, stream_len=250_000):
    import basis_v4 as G
    import conformance as C
    import fasteval as F
    import tier3c as T
    mism, n1, n2 = [], 0, 0
    progs = [("fold", i, b, f) for i in C.INITS for b in C.BODIES for f in C.FINALS]
    progs += [("expr", e) for e in C.FINALS + C.BODIES]
    inputs = [xs + [m] for xs in C.SEQ_SHAPES for m in C.TRAILING] + EXTRA_SHAPES
    for prog in progs:
        for nums in inputs:
            for trailing in (True, False):
                n1 += 1
                a = G.run_program(prog, nums, trailing)
                b = F.run_program(prog, nums, trailing)
                if not _same(a, b):
                    mism.append({"part": "A1", "program": list(prog), "nums_len": len(nums),
                                 "trailing": trailing, "ref": repr(a)[:80], "fast": repr(b)[:80]})
    ref, arms, sizes = reference_setup()
    for fam in ref["families"]:
        for arm, lib in arms:
            rng, dev = cell_inputs(fam, arm, 0, sizes[fam])
            nums_l = [T.nums_of(t) for t in dev]
            for pos, (prog, _c) in enumerate(lib.candidates(rng)):
                if pos >= stream_len:
                    break
                if pos >= head and pos % stride:
                    continue
                for nums in nums_l:
                    n2 += 1
                    a = G.run_program(prog, nums, True)
                    b = F.run_program(prog, nums, True)
                    if not _same(a, b):
                        mism.append({"part": "A2", "family": fam, "arm": arm, "pos": pos,
                                     "program": list(prog), "ref": repr(a)[:80],
                                     "fast": repr(b)[:80]})
    return {"A1_pairs": n1, "A2_pairs": n2, "pairs_total": n1 + n2,
            "A2_meets_200k": n2 >= 200_000, "mismatches": len(mism),
            "mismatch_list": mism[:50]}


# ---------------------------------------------------------------- (b)
_CTX = {}


def _init_worker():
    ref, arms, sizes = reference_setup()
    _CTX.update(arms=dict(arms), sizes=sizes)


def _cell(job):
    import engine as E
    import fasteval as F
    import run_tier3c as R
    fam, arm, i = job
    lib, size = _CTX["arms"][arm], _CTX["sizes"][fam]
    out = {"family": fam, "arm": arm, "recipient": i}
    res = {}
    for name, fnc in (("ref", R.search_collect), ("fast", F.search_collect)):
        rng, dev = cell_inputs(fam, arm, i, size)
        esc = E.Escrow(R.ESCROW)
        t0 = time.perf_counter()
        hits = fnc(lib, dev, esc, R.ESCROW, rng)
        dt = time.perf_counter() - t0
        res[name] = ([[list(p), c, ch] for p, c, ch in hits], esc.spent)
        out[name + "_seconds"] = dt
        out[name + "_spent"] = esc.spent
    out["hits_equal"] = res["ref"][0] == res["fast"][0]
    out["spent_equal"] = res["ref"][1] == res["fast"][1]
    out["n_hits"] = len(res["ref"][0])
    if not (out["hits_equal"] and out["spent_equal"]):
        out["ref_hits"], out["fast_hits"] = res["ref"][0], res["fast"][0]
    return out


def part_b(workers):
    ref = json.loads(REF_RESULTS.read_text(encoding="utf-8"))
    arm_names = list(next(iter(ref["detail"].values())).keys())
    jobs = [(f, a, i) for f in ref["families"] for a in arm_names for i in range(16)]
    t0 = time.perf_counter()
    with mp.get_context("spawn").Pool(workers, initializer=_init_worker) as pool:
        rows = pool.map(_cell, jobs, chunksize=4)
    wall = time.perf_counter() - t0
    bad = [r for r in rows if not (r["hits_equal"] and r["spent_equal"])]
    ref_s = sum(r["ref_seconds"] for r in rows)
    fast_s = sum(r["fast_seconds"] for r in rows)
    cands = sum(r["ref_spent"] for r in rows)
    # cross-check against the committed transplant rows' escrow_spent
    committed = {(r["family"], r["arm"], r["recipient"]): r["escrow_spent"]
                 for f in ref["detail"] for a in ref["detail"][f] for r in ref["detail"][f][a]}
    spent_vs_committed = sum(1 for r in rows
                             if committed[(r["family"], r["arm"], r["recipient"])]
                             != r["fast_spent"])
    return {"cells": len(rows), "mismatches": len(bad), "mismatch_list": bad[:20],
            "fast_spent_vs_committed_escrow_mismatches": spent_vs_committed,
            "total_hits": sum(r["n_hits"] for r in rows),
            "candidates_charged": cands,
            "ref_search_cpu_seconds": round(ref_s, 2),
            "fast_search_cpu_seconds": round(fast_s, 2),
            "ref_candidates_per_second": round(cands / ref_s, 1),
            "fast_candidates_per_second": round(cands / fast_s, 1),
            "search_speedup_x": round(ref_s / fast_s, 2),
            "part_b_wall_seconds": round(wall, 1), "workers": workers}


# ---------------------------------------------------------------- (c)
E2E_DRIVER = r'''
import sys, time
sys.path.insert(0, %(engine)r); sys.path.insert(0, %(accel)r)
from pathlib import Path
import fasteval as F
import run_tier3c as R
F.install()
R.HERE = Path(%(out)r)
t0 = time.perf_counter()
rc = R.main()
print("E2E_WALL %%.1f rc=%%s" %% (time.perf_counter() - t0, rc), flush=True)
sys.exit(rc)
'''


def _diff(a, b, path="", out=None):
    out = [] if out is None else out
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append({"path": path + "/" + k, "ref": repr(a.get(k))[:120],
                            "accel": repr(b.get(k))[:120]})
            else:
                _diff(a[k], b[k], path + "/" + k, out)
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            _diff(x, y, "%s[%d]" % (path, i), out)
    elif not (type(a) is type(b) and a == b):
        out.append({"path": path, "ref": repr(a)[:120], "accel": repr(b)[:120]})
    return out


def part_c(scratch):
    scratch = Path(scratch)
    scratch.mkdir(parents=True, exist_ok=True)
    drv = scratch / "e2e_driver.py"
    drv.write_text(E2E_DRIVER % {"engine": str(ENGINE), "accel": str(ACCEL),
                                 "out": str(scratch)}, encoding="utf-8")
    t0 = time.perf_counter()
    proc = subprocess.run([sys.executable, "-u", str(drv)], cwd=str(ENGINE),
                          capture_output=True, text=True)
    wall = time.perf_counter() - t0
    (scratch / "e2e_stdout.log").write_text(proc.stdout + "\n--stderr--\n" + proc.stderr,
                                            encoding="utf-8")
    res_p = scratch / "TIER3C_RESULTS_2026-09-22.json"
    art_p = scratch / "TIER3C_ARTIFACT_2026-09-22.json"
    if proc.returncode != 0 or not res_p.exists() or not art_p.exists():
        return {"ran": False, "returncode": proc.returncode, "mismatches": 1,
                "mismatch_list": [{"path": "<run>", "stderr_tail": proc.stderr[-600:]}]}
    ref_r = json.loads(REF_RESULTS.read_text(encoding="utf-8"))
    acc_r = json.loads(res_p.read_text(encoding="utf-8"))
    ref_a = json.loads(REF_ARTIFACT.read_text(encoding="utf-8"))
    acc_a = json.loads(art_p.read_text(encoding="utf-8"))
    for d in (ref_r, acc_r):
        for k in WALL_FIELDS:
            d.pop(k, None)
    d_res = _diff(ref_r, acc_r)
    d_art = _diff(ref_a, acc_a)
    rows = sum(len(v) for f in acc_r.get("detail", {}).values() for v in f.values())
    canon = lambda o: json.dumps(o, sort_keys=True, separators=(",", ":")).encode()
    return {"ran": True, "returncode": proc.returncode, "detail_rows": rows,
            "artifact_canonical_sha256_ref": hashlib.sha256(canon(ref_a)).hexdigest(),
            "artifact_canonical_sha256_accel": hashlib.sha256(canon(acc_a)).hexdigest(),
            "results_mismatches": len(d_res), "artifact_mismatches": len(d_art),
            "mismatches": len(d_res) + len(d_art),
            "mismatch_list": (d_res + d_art)[:50],
            "e2e_wall_seconds": round(wall, 1),
            "ref_serial_seconds_committed": REF_SERIAL_SECONDS,
            "e2e_speedup_vs_committed_x": round(REF_SERIAL_SECONDS / wall, 2)}


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="M4")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--out", default=str(ACCEL))
    ap.add_argument("--scratch", default=None)
    ap.add_argument("--parts", default="abc")
    args = ap.parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    scratch = args.scratch or str(out_dir / ("e2e_scratch_" + args.host))

    rep = {"canary": "ACCEL_CANARY_RUNPOD_v1", "backend": BACKEND, "host": args.host,
           "started_utc": _now(), "python": sys.version.split()[0],
           "platform": platform.platform(), "cpu_count": os.cpu_count(),
           "workers": args.workers, "parts_run": args.parts}
    try:
        rep["git_head"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ACCEL),
                                         capture_output=True, text=True).stdout.strip()
    except Exception:          # noqa: BLE001
        rep["git_head"] = None
    rep["pinned_sha_env"] = os.environ.get("ACCEL_PINNED_SHA")
    rep["fasteval_sha256_lf"] = _sha_lf(ACCEL / "fasteval.py")
    drift = check_pins()
    rep["reference_drift"] = drift
    if drift:
        rep["verdict"] = "NOT_EQUIVALENT"
        rep["reason"] = "reference_drift"
    else:
        for part, fnc in (("a", lambda: part_a()), ("c", lambda: part_c(scratch)),
                          ("b", lambda: part_b(args.workers))):
            if part not in args.parts:
                continue
            t0 = time.perf_counter()
            print("[canary] part (%s) ..." % part, flush=True)
            rep["part_" + part] = fnc()
            rep["part_" + part]["seconds"] = round(time.perf_counter() - t0, 1)
            print("[canary] part (%s) mismatches=%s" % (part, rep["part_" + part]["mismatches"]),
                  flush=True)
        ran = [p for p in "abc" if p in args.parts]
        ok = all(rep["part_" + p]["mismatches"] == 0 for p in ran)
        ok = ok and ("a" not in ran or rep["part_a"]["A2_meets_200k"])
        ok = ok and ("c" not in ran or rep["part_c"].get("ran"))
        full = ran == ["a", "b", "c"]
        rep["verdict"] = "EQUIVALENT" if (ok and full) else (
            "NOT_EQUIVALENT" if not ok else "INCOMPLETE_PARTIAL_RUN")
    rep["finished_utc"] = _now()
    rep["timing_caveat"] = (
        "Timings are indicative only: on M4 the science seat and a sibling accel "
        "track share the 8-core CPU concurrently and this runner is capped at %d "
        "worker process(es). Timing never affects the verdict." % args.workers)
    dest = out_dir / ("ACCEL_EQUIVALENCE_%s_%s.json" % (BACKEND, args.host))
    dest.write_text(json.dumps(rep, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("[canary] VERDICT %s -> %s" % (rep["verdict"], dest), flush=True)
    return 0 if rep["verdict"] == "EQUIVALENT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
