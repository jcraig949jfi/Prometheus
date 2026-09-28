"""Ancestry-replay commission (Archaeon #812/#818/#823), step 1: PIN the E-001 T-003 harness and REPRODUCE its 11 runs.
Observation only. Nothing here changes NPE code or the frozen campaign.

Pin: git 53b1bc2b3989a0c6942e594b8d43f5f244e05076 (ops/campaigns/C-001/E-001/TASKS.md "T-003 inputs"):
  roles/Nestor/campaigns/z80atlas-verify-2026-09-22/  (NPE Cycle-9 engine + MANIFEST_FROZEN.json)
  archaeon/causal_lens/tools_npe/npe_b6_replay.py     (Archaeon's T-003 probe)
  archaeon/causal_lens/out/npe/NPE_LENS_SUMMARY.json  (run selection: the 11 H2 RESERVOIR runs with pair-tape births)
extracted with `git archive` into _scratch/pin53b1/ (never edited); sha256 of every pinned file -> PIN.json.

Checks (all must hold; each can fail):
  P1 pinned engine == the frozen campaign at HEAD (git diff empty) and probe/summary == origin/main;
  P2 the probe, run with T-003's exact command (3 workers), yields 11 runs and 34 pair births;
  P3 NON-PERTURBATION: for every run, lineage_sha256 with the probe == lineage_sha256 of an UN-PATCHED replay
     (NPE's own Runner, no source transform) computed here with the same job list;
  P4 CROSS-MACHINE: result_sha256 of the probe output starts with T-003's recorded efba5535 (TASKS.md A-001; the value
     hashes every run's lineage_sha256 and every birth record, so a prefix match means bit-identical lineages on M1 and
     ubu001);
  P5 the 34 birth records equal Archaeon's committed fixture archaeon/tests/fixtures_v03/npe_t003_births.json (as a
     multiset of canonical JSON records).

    python pin_reproduce.py            (M1, under the cpu8 host lease; ~15 min at 3 workers)
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import pathlib
import subprocess
import sys
import tarfile
import time
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[4]
PIN = "53b1bc2b3989a0c6942e594b8d43f5f244e05076"
PATHS = ["roles/Nestor/campaigns/z80atlas-verify-2026-09-22", "archaeon/causal_lens/tools_npe/npe_b6_replay.py",
         "archaeon/causal_lens/out/npe/NPE_LENS_SUMMARY.json"]
SCR = HERE / "_scratch"
PDIR = SCR / "pin53b1"
T003_PREFIX = "efba5535"
FIXTURE = "archaeon/tests/fixtures_v03/npe_t003_births.json"


def git(*a, binary=False):
    p = subprocess.run(["git", "-C", str(REPO), *a], capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode(errors="replace"))
    return p.stdout if binary else p.stdout.decode()


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def extract():
    if PDIR.exists():
        raise SystemExit("pinned dir exists: %s (never overwrite; remove by hand if intended)" % PDIR)
    PDIR.mkdir(parents=True)
    tar = git("archive", "--format=tar", PIN, *PATHS, binary=True)
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        t.extractall(PDIR, filter="data")
    files = {str(p.relative_to(PDIR)).replace("\\", "/"): sha(p.read_bytes()) for p in sorted(PDIR.rglob("*")) if p.is_file()}
    return files


def unpatched_lineages(jobs, zdir):
    """NPE's own Runner, no source transform: the reference lineage hash per run (same hash recipe as the probe)."""
    code = r'''
import hashlib, json, sys
sys.path.insert(0, sys.argv[1])
import world as W
job = json.loads(sys.argv[2])
kw = dict(job["kwargs"]); kw.pop("implant_source", None); hx = kw.pop("implant_hex", None)
if hx: kw["implant_bytes"] = bytes.fromhex(hx)
r = W.Runner(job["cell"], job["seed"], tier=job["tier"], **kw); r.run()
print(json.dumps({"name": job["name"], "lineage_sha256": hashlib.sha256(json.dumps(r.lineage, sort_keys=True, default=str).encode()).hexdigest(), "lineage_n": len(r.lineage)}))
'''
    from concurrent.futures import ThreadPoolExecutor

    def one(job):
        p = subprocess.run([sys.executable, "-c", code, str(zdir), json.dumps(job)], capture_output=True, text=True)
        if p.returncode:
            return {"name": job["name"], "error": p.stderr[-400:]}
        return json.loads(p.stdout.strip().splitlines()[-1])
    with ThreadPoolExecutor(3) as ex:
        return list(ex.map(one, jobs))


def job_list(zdir, summary):
    """The probe's own job_list, re-stated (it parses sys.argv at import, so it is not imported)."""
    man = json.load(open(zdir / "MANIFEST_FROZEN.json", encoding="utf-8"))
    want = [k for k, v in json.load(open(summary, encoding="utf-8")).items() if v["by_kind"].get("PAIR_OVERWRITE", 0) > 0]
    jobs = []
    for name in want:
        spec, seed, arm = name.split("__"); seed = int(seed[1:])
        for b in man["bundles"]:
            if b["hypothesis_id"] != "H2" or b.get("specimen") != spec:
                continue
            for a in b["arms"]:
                c = a["cell"] if isinstance(a["cell"], dict) else eval(a["cell"])            # noqa: S307 (frozen manifest)
                if a["arm"] == arm and int(a["seed"]) == seed and c.get("structure") == "RESERVOIR":
                    kw = a["kwargs"] if isinstance(a["kwargs"], dict) else eval(a["kwargs"])  # noqa: S307
                    jobs.append({"name": name, "cell": c, "seed": seed, "tier": a["tier"], "kwargs": kw})
    return jobs


def canon(x) -> str:
    return json.dumps(x, sort_keys=True, separators=(",", ":"))


def main():
    t0 = time.time()
    SCR.mkdir(exist_ok=True)
    files = extract()
    zdir = PDIR / PATHS[0]
    summary = PDIR / PATHS[2]
    p1 = (git("diff", "--stat", PIN, "HEAD", "--", PATHS[0]).strip() == ""
          and git("diff", "--stat", PIN, "origin/main", "--", PATHS[1], PATHS[2]).strip() == "")
    probe_out = SCR / "t003_probe_out.json"
    pr = subprocess.run([sys.executable, str(PDIR / PATHS[1]), "--npe", str(zdir), "--summary", str(summary),
                         "--out", str(probe_out), "--workers", "3"], capture_output=True, text=True)
    if pr.returncode:
        raise SystemExit("probe failed: " + pr.stderr[-1500:])
    out = json.load(open(probe_out, encoding="utf-8"))
    res = out["results"]
    births = [b for r in res for b in r["births"]]
    jobs = job_list(zdir, summary)
    un = {u["name"]: u for u in unpatched_lineages(jobs, zdir)}
    per_run = [{"name": r["name"], "births": len(r["births"]), "lineage_n": r["lineage_n"],
                "probe_lineage_sha256": r["lineage_sha256"], "unpatched_lineage_sha256": un.get(r["name"], {}).get("lineage_sha256"),
                "equal": r["lineage_sha256"] == un.get(r["name"], {}).get("lineage_sha256")} for r in res]
    fx = json.loads(git("show", "origin/main:" + FIXTURE))["births"]
    p5 = Counter(canon(b) for b in births) == Counter(canon(b) for b in fx)
    checks = {"P1_pin_equals_frozen_and_main": p1,
              "P2_11_runs_34_births": len(res) == 11 and len(births) == 34,
              "P3_probe_does_not_perturb_11_of_11": len(per_run) == 11 and all(x["equal"] for x in per_run),
              "P4_result_sha256_matches_T003_prefix": out["result_sha256"].startswith(T003_PREFIX),
              "P5_births_equal_committed_fixture": p5}
    rec = {"task": "ancestry-replay step 1 (pin + reproduce)", "pin": PIN, "pinned_files_sha256": files,
           "host": os.environ.get("COMPUTERNAME", "?"), "python": sys.version.split()[0],
           "probe_result_sha256": out["result_sha256"], "probe_out_sha256": sha(probe_out.read_bytes()),
           "t003_recorded_prefix": T003_PREFIX, "per_run": per_run, "checks": checks, "all_pass": all(checks.values()),
           "wall_s": round(time.time() - t0, 1), "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    (HERE / "PIN_REPRODUCE.json").write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"checks": checks, "all_pass": rec["all_pass"], "result_sha256": out["result_sha256"],
                      "wall_s": rec["wall_s"]}, indent=1))
    return 0 if rec["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
