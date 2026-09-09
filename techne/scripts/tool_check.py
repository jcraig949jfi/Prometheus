"""Run a tool's first useful check in its isolated env, under a budget, with a receipt.

    python -m techne.scripts.tool_check --entry z3
    python -m techne.scripts.tool_check --entry hypothesis
    python -m techne.scripts.tool_check --entry pyribs
    python -m techne.scripts.tool_check --entry stitch
    python -m techne.scripts.tool_check --all

Each check script lives in techne/acquisition/checks/ and imports NOTHING from techne, so
it runs under the isolated env's interpreter rather than the live one. The harness launches
it, captures the JSON it prints, and writes a FIRST_USEFUL_CHECK receipt whose
`does_not_establish` field names the stages the check says nothing about.

The profile is offline_check, which FORBIDS network. A check that needs to download is an
acquisition step wearing a check's name, and the budget refuses it.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

from techne.acquisition import budget as _budget
from techne.acquisition import manifest_io, paths, pypi, receipt

CHECKS = {
    "z3": {
        "script": "z3_first_check.py",
        "args": lambda e: [],
        "requirement": "SAT / UNSAT / UNKNOWN distinct, resource exhaustion distinct, and a "
                       "returned counterexample independently validated",
    },
    "hypothesis": {
        "script": "hypothesis_first_check.py",
        "args": lambda e: [
            "--work", str(paths.tool_cache() / "checkwork" / "hypothesis"),
            "--fixture-out", str(paths.ACQ_ROOT / "fixtures" / "hypothesis_minimized.json"),
        ],
        "requirement": "minimise a known defect, persist the explicit fixture, isolate the "
                       "example database by scope",
        # The storage side channel defaults to .hypothesis in the CWD. Contain it so a check
        # run never writes into whatever directory it happened to start in.
        "env": lambda e: {"HYPOTHESIS_STORAGE_DIRECTORY":
                          str(paths.tool_cache() / "checkwork" / "hypothesis" / "storage")},
    },
    "pyribs": {
        "script": "pyribs_first_check.py",
        "args": lambda e: [],
        "requirement": "identical frozen stream inserted directly into archives, no emitters "
                       "or schedulers, known collision and tie outcomes, identical retained ids",
    },
    "stitch": {
        "script": "stitch_first_check.py",
        "args": lambda e: [
            "--fixture", str(paths.tool_cache() / "fixtures" / "stitch" / "nuts-bolts.json"),
            "--manifest", str(paths.ACQ_ROOT / "reproduction" / "stitch_nuts_bolts.manifest.json"),
            "--library-out", str(paths.ACQ_ROOT / "exports" / "stitch_nuts_bolts_library.json"),
        ],
        "requirement": "the documented nuts-bolts fixture as an UPSTREAM check, then "
                       "semantics-preserving expansion verified independently",
    },
}


def run_check(entry: dict, profile: str) -> dict:
    spec = CHECKS[entry["id"]]
    script = paths.ACQ_ROOT / "checks" / spec["script"]
    py = pypi.env_python(entry["env"])
    rec = receipt.new("FIRST_USEFUL_CHECK", entry["id"], tool=entry.get("distribution"))
    rec["check_script"] = str(script.relative_to(paths.REPO_ROOT)).replace("\\", "/")
    rec["design_requirement"] = spec["requirement"]
    rec["manifest_first_useful_check"] = entry["first_useful_check"]
    rec["named_consumer"] = entry["named_consumer"]
    prof = _budget.get_profile(profile)
    rec["budget_profile"] = prof

    if not py.exists():
        rec["status"] = "BLOCKED_ENV_ABSENT"
        rec["unrun_or_blocked"].append(
            f"isolated env interpreter {py} does not exist; run "
            f"`python -m techne.scripts.acquire --entry {entry['id']} --profile light_probe`")
        return rec

    env = None
    if "env" in spec:
        import os
        env = dict(os.environ)
        extra = spec["env"](entry)
        env.update(extra)
        rec["environment_overrides"] = extra

    with _budget.Budget(profile=prof) as b:
        argv = [str(py), str(script)] + spec["args"](entry)
        kw = {"env": env} if env else {}
        # cwd is the tool cache, not the repository: a check must not write into the checkout
        workdir = paths.tool_cache() / "checkwork"
        workdir.mkdir(parents=True, exist_ok=True)
        r = b.run(argv, cwd=str(workdir), **kw)
        rec["resource_receipt"] = b.resource_receipt()
    receipt.record_command(rec, {**r, "stdout": ""})   # stdout is the payload, stored below

    payload = None
    for line in reversed((r["stdout"] or "").strip().splitlines()):
        try:
            payload = json.loads(line)
            break
        except ValueError:
            continue
    rec["observations"] = payload if payload is not None else {}
    if payload is None:
        rec["status"] = "FAILED_NO_JSON_FROM_CHECK"
        rec["unrun_or_blocked"].append("check produced no parsable JSON on stdout")
        rec["stdout_tail"] = (r["stdout"] or "")[-3000:]
        rec["stderr_tail"] = (r["stderr"] or "")[-3000:]
        return rec

    # A check reports its own verdict; the harness does not reinterpret it. A check may also
    # leave cases UNDECIDED -- a probe that did not fire is neither a pass nor a failure --
    # and that is carried in the status rather than collapsed into one of the two.
    passed = payload.get("all_passed")
    if passed is None:
        passed = payload.get("all_decided_passed")
    if passed is None:
        passed = payload.get("first_useful_check", {}).get("all_passed")
    cases_all = (payload.get("cases")
                 or payload.get("first_useful_check", {}).get("cases") or [])
    undecided = [c.get("case") for c in cases_all if c.get("pass") is None]
    if passed is True:
        rec["status"] = ("CHECK_PASSED" if not undecided
                         else "CHECK_PASSED_WITH_UNDECIDED_CASES")
    elif passed is False:
        rec["status"] = "CHECK_FAILED"
    else:
        rec["status"] = "CHECK_INDETERMINATE"
    if undecided:
        rec["undecided_cases"] = undecided
    rec["check_exit_code"] = r["returncode"]
    if r["stderr"]:
        rec["stderr_tail"] = r["stderr"][-3000:]
    return rec


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--entry", help=f"one of {sorted(CHECKS)}")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--profile", default="offline_check")
    a = ap.parse_args(argv)

    man = manifest_io.load()
    ids = sorted(CHECKS) if a.all else ([a.entry] if a.entry else [])
    if not ids:
        ap.error("pass --entry <id> or --all")

    rc = 0
    for eid in ids:
        if eid not in CHECKS:
            print(f"no check defined for {eid!r}")
            rc = 3
            continue
        rec = run_check(manifest_io.entry(man, eid), a.profile)
        out = receipt.write(rec)
        obs = rec["observations"]
        print(f"\n=== FIRST_USEFUL_CHECK {eid} -> {rec['status']} ===")
        print(f"requirement     {rec['design_requirement']}")
        cases = obs.get("cases") or obs.get("first_useful_check", {}).get("cases") or []
        for c in cases:
            verdict = {True: "PASS", False: "FAIL", None: "UNDECIDED"}[c.get("pass")]
            print(f"  {verdict:<9} {c.get('case')}")
        for asn in obs.get("assertions", []):
            print(f"  {'PASS' if asn['pass'] else 'FAIL':<9} {asn['claim']}")
        if "reproduction" in obs:
            print(f"  reproduction status: {obs['reproduction']['status']}")
        rr = rec.get("resource_receipt", {})
        print(f"resources       {rr.get('wall_seconds')}s / {rr.get('wall_ceiling')}s, "
              f"network {rr.get('network_policy')}, downloaded "
              f"{rr.get('downloaded_bytes')}B")
        print(f"receipt         {out}")
        if rec.get("undecided_cases"):
            print(f"undecided       {rec['undecided_cases']} -- a probe that did not fire is "
                  f"not a pass and not a failure")
        if rec["status"] not in ("CHECK_PASSED", "CHECK_PASSED_WITH_UNDECIDED_CASES"):
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
