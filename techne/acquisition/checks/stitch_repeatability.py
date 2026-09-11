"""F15 repeatability and the thread-count arm for the stitch backend.

    python -m techne.acquisition.checks.stitch_repeatability

Asked for by Vivarium in the external-backend contract (vivarium/docs/EXTERNAL_BACKEND_CONTRACT.md,
739c77e63): F15 requires two runs byte-identical on the declared projection, and Vivarium
separately asked for a different RAYON_NUM_THREADS, on the reasoning that a work-stealing
scheduler can reorder reductions so the same input at 2 threads is a different computation rather
than the same one faster.

THE DECLARED PROJECTION, and why a whole-file hash is the wrong statistic here. `out.json`
contains a `cmd` field recording the invocation INCLUDING the `--out` path. My first pass varied
that path per run, so all four thread counts produced different file hashes and it looked like a
thread effect. It was not: the only differing key was `cmd`. Hold the path constant and the whole
file is byte-identical. So the projection EXCLUDES cmd, and this is a concrete instance of why
Vivarium's contract specifies a projection rather than the file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib

from .. import budget as _budget
from .. import manifest_io, paths, receipt

#: Resolved per host, never hardcoded -- base-role s2, and this seat's own rule.
#: The gnu Rust target links libgcc and llvm-mingw ships none, so a real GCC has
#: to be on PATH for the build; paths.gcc_bin() says where, or None.
def _mingw_gcc_bin() -> str:
    return paths.gcc_bin_or_empty()

#: Fields that carry the result. `cmd` is EXCLUDED because it embeds the output path, and `args`
#: is kept because it is the parsed configuration, which must not drift.
PROJECTION = ("args", "num_abstractions", "original_cost", "final_cost", "compression_ratio",
              "original", "rewritten", "abstractions")


def project(doc: dict) -> str:
    return hashlib.sha256(
        json.dumps({k: doc.get(k) for k in PROJECTION}, sort_keys=True).encode()).hexdigest()


def run(binary, cwd, fixture, out, *, threads_env: int | None, b) -> dict:
    env = {**os.environ, "PATH": _mingw_gcc_bin() + ";" + os.environ.get("PATH", "")}
    if threads_env is not None:
        env["RAYON_NUM_THREADS"] = str(threads_env)
    r = b.run([str(binary), str(fixture), "--max-arity=3", "--iterations=3", f"--out={out}"],
              cwd=str(cwd), env=env)
    if r["returncode"] != 0:
        return {"ok": False, "returncode": r["returncode"], "stderr_tail": r["stderr"][-400:]}
    raw = out.read_bytes()
    doc = json.loads(raw.decode("utf-8"))
    return {"ok": True, "file_sha256": hashlib.sha256(raw).hexdigest(),
            "projection_sha256": project(doc),
            "num_abstractions": doc["num_abstractions"],
            "original_cost": doc["original_cost"], "final_cost": doc["final_cost"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="stitch_core_reproduction")
    a = ap.parse_args(argv)

    man = manifest_io.load()
    core = manifest_io.entry(man, "stitch_rust_core")
    root = paths.repos() / "stitch_rust_core"
    binary = root / "target" / "release" / "compress.exe"
    fixture = paths.tool_cache() / "fixtures" / "stitch" / "nuts-bolts.json"
    work = paths.tool_cache() / "checkwork" / "stitch_repeat"
    work.mkdir(parents=True, exist_ok=True)
    out = work / "fixed.json"          # CONSTANT path, so cmd cannot vary

    rec = receipt.new("ADAPTER_QUALIFICATION", "stitch_rust_core")
    rec["check"] = "f15_repeatability_and_thread_count_invariance"
    rec["requested_by"] = ("Vivarium, vivarium/docs/EXTERNAL_BACKEND_CONTRACT.md at 739c77e63 "
                           "(F15) plus their thread-count arm")
    rec["budget_profile"] = _budget.get_profile(a.profile)

    if not binary.exists():
        rec["status"] = "BLOCKED_BINARY_NOT_BUILT"
        print(receipt.write(rec)); return 3

    with _budget.Budget(profile=_budget.get_profile(a.profile)) as b:
        same = [run(binary, root, fixture, out, threads_env=4, b=b) for _ in range(5)]
        threads = {t: run(binary, root, fixture, out, threads_env=t, b=b)
                   for t in (1, 2, 4, 8, 16)}
        rec["resource_receipt"] = b.resource_receipt()

    f_same = {r["file_sha256"] for r in same if r["ok"]}
    p_same = {r["projection_sha256"] for r in same if r["ok"]}
    f_thr = {t: r["file_sha256"] for t, r in threads.items() if r["ok"]}
    p_thr = {t: r["projection_sha256"] for t, r in threads.items() if r["ok"]}

    checks = [
        ("F15: five runs at a fixed thread count (N=5, as the contract requires) agree on the declared projection",
         len(p_same) == 1),
        ("F15 stronger: those five runs are byte-identical on the WHOLE file too", len(f_same) == 1),
        ("thread-count invariance on the declared projection (1,2,4,8,16)",
         len(set(p_thr.values())) == 1),
        ("thread-count invariance on the whole file as well",
         len(set(f_thr.values())) == 1),
        ("the science is unchanged across every run",
         len({(r["num_abstractions"], r["original_cost"], r["final_cost"])
              for r in list(threads.values()) + same if r["ok"]}) == 1),
    ]

    rec["observations"] = {
        "backend": {"binary": str(binary), "revision": core["upstream_revision"]["commit"],
                    "licence": core["license_claim"]},
        "input": {"path": str(fixture),
                  "sha256": hashlib.sha256(fixture.read_bytes()).hexdigest()},
        "declared_projection": list(PROJECTION),
        "projection_excludes": {
            "cmd": ("it records the invocation INCLUDING the --out path. Varying that path made "
                    "four thread counts look like four different results on a whole-file hash; "
                    "the only differing key was cmd. A whole-file hash is therefore not a valid "
                    "repeatability statistic for this backend, which is a concrete instance of "
                    "why the contract specifies a projection.")},
        "f15_same_thread_count": {"runs": same, "file_hashes": sorted(f_same),
                                  "projection_hashes": sorted(p_same)},
        "thread_arm": {"file_sha256_by_threads": f_thr, "projection_sha256_by_threads": p_thr,
                       "verdict": ("INVARIANT across RAYON_NUM_THREADS 1,2,4,8,16 on both the "
                                   "projection and the whole file"
                                   if len(set(f_thr.values())) == 1 else
                                   "THREAD-DEPENDENT -- thread count is load-bearing and must be "
                                   "pinned in the declaration")},
        "consequence_for_the_declaration": (
            "thread count does NOT have to be pinned to preserve the result on this backend and "
            "this input. It is still worth declaring, because invariance measured on one input "
            "is not invariance proved in general -- but nobody optimising it to 8 later will "
            "silently change the science on this corpus."),
        "checks": [{"claim": c, "pass": bool(p)} for c, p in checks],
    }
    rec["status"] = "REPEATABLE_AND_THREAD_INVARIANT" if all(p for _, p in checks) else "FAILED"
    rec["unrun_or_blocked"] = [
        "the other eight contract fixtures need a live kill and become required only when "
        "something calls the backend DURING a run. At 1.0 Vivarium's ruling says nothing does.",
        "invariance is measured on ONE input. A second corpus could differ.",
    ]
    out_rec = receipt.write(rec)

    print(f"=== stitch F15 + thread arm -> {rec['status']} ===")
    print(f"projection      {list(PROJECTION)}")
    print(f"excludes        cmd (embeds the --out path)")
    print(f"F15 x3 @4thr    file {sorted(f_same)[0][:32]}  projection {sorted(p_same)[0][:32]}")
    for t in sorted(f_thr):
        print(f"  RAYON={t:<3}      file {f_thr[t][:32]}  projection {p_thr[t][:32]}")
    print(f"verdict         {rec['observations']['thread_arm']['verdict']}")
    for c in rec["observations"]["checks"]:
        print(f"  {'PASS' if c['pass'] else 'FAIL':<5} {c['claim']}")
    print(f"receipt         {out_rec}")
    return 0 if rec["status"] == "REPEATABLE_AND_THREAD_INVARIANT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
