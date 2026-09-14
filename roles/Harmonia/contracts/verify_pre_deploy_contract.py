"""Verify a pre-deploy candidate contract in both directions, with controls.

Harmonia[m2-54a6d694], 2026-09-14, comms #215. Runs against two LOOPBACK
scratch engines only (deploy/scratch_contract_engine.py): one serving the
DEPLOYED build, one serving the CANDIDATE (--tree). Production is read (GET
/v2/version, /v2/openapi.json) and never written; the gate's probe-client
registration lands on the scratch ledgers.

The gate pins engine_instance_id to the contract, so each case runs on a
temporary copy whose instance id is set to the scratch engine under test. That
rewrite is the only change and is recorded per row.

    python roles/Harmonia/contracts/verify_pre_deploy_contract.py \\
        --candidate roles/Harmonia/contracts/candidates/<h12>/sfe_contract.json \\
        --deployed-port 8901 --candidate-port 8911 --cacert <m1.crt> \\
        --ledger <dir>/verify_rows.jsonl

Every row: case, control class, command, expected, observed, pass. Written
with a flush per row so a crash leaves the rows already measured.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
GATE = os.path.join(HERE, "conformance_check.py")
GEN = os.path.join(HERE, "generate_sfe_contract.py")
PROMOTE = os.path.join(HERE, "promote_candidate_contract.py")
LIVE_CONTRACT = os.path.join(HERE, "sfe_contract.json")


def ver(port):
    with urllib.request.urlopen("http://127.0.0.1:%d/v2/version" % port,
                                timeout=15) as z:
        return json.loads(z.read().decode())


def _declared(relpath, name):
    """A consumer's declared route tuple, READ from its source, not imported.

    Importing a consumer runs its code and its dependencies; the auditor reads
    the declaration. Matches a module-level `NAME = (...)` or `NAME: T = (...)`,
    or a dataclass field `name: T = (...)`.
    """
    import ast
    tree = ast.parse(open(os.path.join(REPO, relpath), encoding="utf-8").read())
    for node in ast.walk(tree):
        tgt = val = None
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            tgt, val = node.target.id, node.value
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            tgt, val = node.targets[0].id, node.value
        if tgt == name and val is not None:
            if isinstance(val, ast.Name):     # e.g. consumer_routes = CONSUMER_ROUTES
                return _declared(relpath, val.id)
            return list(ast.literal_eval(val))
    raise SystemExit("could not find %s in %s" % (name, relpath))


def consumer_routes():
    return {"vivarium": _declared("vivarium/viv/conformance.py", "CONSUMER_ROUTES")}


def archaeon_routes():
    return _declared("archaeon/conformance.py", "consumer_routes")


def with_instance(contract_path, instance, tmp):
    C = json.load(open(contract_path, encoding="utf-8"))
    C["engine"]["engine_instance_id"] = instance
    p = os.path.join(tmp, "c_%s_%s.json" % (
        os.path.basename(os.path.dirname(contract_path)) or "live", instance[-8:]))
    json.dump(C, open(p, "w", encoding="utf-8"), indent=1)
    return p


LAST_OUTPUT = [""]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
    LAST_OUTPUT[0] = r.stdout + r.stderr
    return r.returncode, LAST_OUTPUT[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--deployed-port", type=int, default=8901)
    ap.add_argument("--candidate-port", type=int, default=8911)
    ap.add_argument("--cacert", required=True)
    ap.add_argument("--ledger", required=True)
    a = ap.parse_args()

    dep, cand = ver(a.deployed_port), ver(a.candidate_port)
    K = json.load(open(a.candidate, encoding="utf-8"))
    cand_hash = K["engine"]["pre_deploy"]["candidate_engine_source_hash"]
    live_hash = K["engine"]["pre_deploy"]["live_engine_source_hash_at_generation"]
    assert dep["engine_source_hash"] == live_hash, "deployed scratch != live build"
    assert cand["engine_source_hash"] == cand_hash, "candidate scratch != candidate"
    DB = "http://127.0.0.1:%d/v2" % a.deployed_port
    CB = "http://127.0.0.1:%d/v2" % a.candidate_port
    tmp = tempfile.mkdtemp(prefix="harm-predeploy-")
    routes = {"vivarium": consumer_routes()["vivarium"],
              "archaeon": archaeon_routes()}

    os.makedirs(os.path.dirname(os.path.abspath(a.ledger)), exist_ok=True)
    out = open(a.ledger, "w", encoding="utf-8")
    n_pass = n = 0

    def row(case, klass, cmd, expected, observed, note=""):
        nonlocal n_pass, n
        ok = observed == expected
        n += 1
        n_pass += ok
        if not ok:
            # run 1 lost P3's evidence because only the exit code was kept
            note = (note + " | output tail: " + LAST_OUTPUT[0][-600:]).strip()
        rec = {"case": case, "control": klass, "expected_exit": expected,
               "observed_exit": observed, "pass": ok, "note": note,
               "cmd": [os.path.relpath(c, REPO).replace(os.sep, "/")
                       if os.path.isabs(c) and c.startswith(REPO) else c
                       for c in cmd]}
        out.write(json.dumps(rec) + "\n")
        out.flush()
        print("  [%s] %-58s exp %s obs %s" % ("PASS" if ok else "FAIL", case,
                                               expected, observed))

    cand_on_c = with_instance(a.candidate, cand["engine_instance_id"], tmp)
    cand_on_d = with_instance(a.candidate, dep["engine_instance_id"], tmp)
    live_on_c = with_instance(LIVE_CONTRACT, cand["engine_instance_id"], tmp)
    live_on_d = with_instance(LIVE_CONTRACT, dep["engine_instance_id"], tmp)

    # C1 POSITIVE: the candidate contract describes the candidate build
    cmd = [sys.executable, GATE, "--contract", cand_on_c, "--base", CB]
    rc, txt = run(cmd)
    row("C1 candidate contract vs candidate engine", "positive", cmd, 0, rc,
        "CONFORMANT" if "CONFORMANT -- safe" in txt else txt[-300:])

    # C2 NEGATIVE: the DRIFT window -- candidate contract vs the deployed build
    cmd = [sys.executable, GATE, "--contract", cand_on_d, "--base", DB]
    rc, txt = run(cmd)
    row("C2 candidate contract vs DEPLOYED build (pre-restart window)",
        "negative", cmd, 1, rc,
        "removed route named" if "GET', '/v2/health" in txt else txt[-300:])

    # C3 BASELINE: live contract vs deployed build is CONFORMANT
    cmd = [sys.executable, GATE, "--contract", live_on_d, "--base", DB]
    rc, txt = run(cmd)
    row("C3 live contract vs deployed build", "baseline", cmd, 0, rc)

    # C4/C5/C6: the delegation's premise -- live contract vs the candidate
    cmd = [sys.executable, GATE, "--contract", live_on_c, "--base", CB]
    rc, txt = run(cmd)
    row("C4 live contract vs candidate, NO routes declared", "premise", cmd,
        3, rc)
    for who in ("vivarium", "archaeon"):
        cmd = [sys.executable, GATE, "--contract", live_on_c, "--base", CB,
               "--consumer-routes", *routes[who]]
        rc, txt = run(cmd)
        row("C5 live contract vs candidate, %s's %d routes" % (who,
            len(routes[who])), "premise", cmd, 0, rc,
            "INCOMPLETE-covered" if "Every route you declared IS" in txt
            else txt[-300:])
    cmd = [sys.executable, GATE, "--contract", live_on_c, "--base", CB,
           "--consumer-routes", "GET /v2/version", "GET /v2/health"]
    rc, txt = run(cmd)
    row("C6 live contract vs candidate, a consumer that calls /v2/health",
        "negative", cmd, 3, rc)

    # P1-P3 promotion: refuses before the deploy, promotes after
    target = os.path.join(tmp, "promoted.json")
    cmd = [sys.executable, PROMOTE, "--candidate", cand_on_d, "--base", DB,
           "--target", target]
    rc, _ = run(cmd)
    row("P1 promote against the DEPLOYED build (not yet restarted)", "cheat",
        cmd, 2, rc, "target written" if os.path.exists(target) else
        "nothing written")
    cmd = [sys.executable, PROMOTE, "--candidate", live_on_c, "--base", CB,
           "--target", target]
    rc, _ = run(cmd)
    row("P2 promote a contract with no pre_deploy block", "cheat", cmd, 2, rc,
        "target written" if os.path.exists(target) else "nothing written")
    cmd = [sys.executable, PROMOTE, "--candidate", cand_on_c, "--base", CB,
           "--target", target]
    rc, _ = run(cmd)
    promoted = json.load(open(target)) if os.path.exists(target) else {}
    row("P3 promote against the CANDIDATE build (post-restart)", "positive",
        cmd, 0, rc, "promoted block present, pre_deploy removed"
        if promoted.get("engine", {}).get("promoted")
        and "pre_deploy" not in promoted.get("engine", {}) else "bad target")

    # G1-G2 generator refusals (cheat: the wrong engine offered as candidate)
    live_base = K["engine"]["base_url"][:-3]
    for case, port, h, why in (
            ("G1 generator: candidate hash asserted on the DEPLOYED engine",
             a.deployed_port, cand_hash, "probe build is not the candidate"),
            ("G2 generator: --candidate-hash equal to live",
             a.deployed_port, live_hash, "candidate IS live")):
        cmd = [sys.executable, GEN, "--base", live_base, "--cacert", a.cacert,
               "--probe-base", "http://127.0.0.1:%d" % port,
               "--candidate-hash", h, "--outdir", os.path.join(tmp, "g")]
        rc, txt = run(cmd)
        row(case, "cheat", cmd, 2, rc, why if "REFUSING" in txt else txt[-200:])

    out.close()
    print("\n%d/%d rows as expected; ledger %s" % (n_pass, n, a.ledger))
    return 0 if n_pass == n else 1


if __name__ == "__main__":
    sys.exit(main())
