"""cw01-e05 pre-EXECUTE self-check: verify the COMMITTED state, not the working tree.

Nothing here may bypass the committed-state re-read. The working tree is not
evidence: a green run against uncommitted files says nothing about what was
actually recorded. So this extracts the campaign subtree from HEAD with
`git archive` into a temporary directory and runs the COMMITTED consistency gate
and the COMMITTED fixtures against the COMMITTED specifications, in isolation.

Emits SELFCHECK.json: commit SHA, the contract hash recomputed from committed
bytes, F1-F7 outcomes, the consistency-gate outcome, the binding specification
fields, and one verdict -- whether the driver would admit EXECUTE.
"""
from __future__ import annotations

import hashlib
import io
import json
import pathlib
import subprocess
import sys
import tarfile
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
BASE = HERE.parents[1]
REPO = BASE.parents[3]
SUBTREE = "roles/Nestor/campaigns/cw01-2026-09-17"
REL = SUBTREE + "/experiments/cw01-e05"
EXPECTED_HASH = "c80b5bfd348f7b87418166061f39c1446bd45c6e74ff060f9c5927e24b2c5619"
PY = sys.executable


def git(*args):
    r = subprocess.run(["git", "-C", str(REPO)] + list(args),
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), r.stderr.strip()))
    return r.stdout.strip()


def extract_head(dest):
    """Materialise the committed campaign subtree. HEAD is the only source."""
    r = subprocess.run(["git", "-C", str(REPO), "archive", "--format=tar", "HEAD", SUBTREE],
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git archive failed: %s" % r.stderr.decode(errors="replace"))
    with tarfile.open(fileobj=io.BytesIO(r.stdout)) as tf:
        tf.extractall(dest)
    return pathlib.Path(dest) / SUBTREE


def run(script, cwd):
    r = subprocess.run([PY, str(script)], capture_output=True, text=True, cwd=str(cwd))
    return r.returncode, r.stdout, r.stderr


def main():
    print("########## e05 pre-EXECUTE self-check (COMMITTED state) ##########")
    sha = git("rev-parse", "HEAD")
    short = git("rev-parse", "--short", "HEAD")
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    dirty = git("status", "--porcelain", "--", SUBTREE)
    print("    commit %s on %s" % (short, branch))

    tmp = tempfile.mkdtemp(prefix="e05_head_")
    campaign = extract_head(tmp)
    exp = campaign / "experiments" / "cw01-e05"
    print("    extracted committed subtree -> %s" % exp)

    findings = []

    def note(cid, passed, detail):
        findings.append({"id": cid, "passed": bool(passed), "detail": detail})
        print("    %-30s %-6s %s" % (cid, "PASS" if passed else "FAIL", detail))
        return passed

    # --- the contract, recomputed from COMMITTED bytes ---------------------
    committed_contract = json.loads((exp / "VERDICT_CONTRACT.json").read_text(encoding="utf-8"))
    sys.path.insert(0, str(campaign / "lib"))
    import contract as CT                                    # noqa: E402
    body_hash = CT.contract_hash(committed_contract["contract"])
    note("S1_contract_hash_from_commit", body_hash == EXPECTED_HASH,
         "recomputed %s from committed bytes" % body_hash[:16])
    note("S2_stored_hash_matches_body",
         committed_contract.get("contract_sha256") == body_hash,
         "stored %s" % str(committed_contract.get("contract_sha256"))[:16])

    # --- run the COMMITTED gate and COMMITTED fixtures ---------------------
    g_rc, g_out, g_err = run(exp / "consistency_e05.py", exp)
    note("S3_committed_gate", g_rc == 0, "consistency_e05.py rc=%d%s"
         % (g_rc, "" if g_rc == 0 else " :: " + (g_err.strip().splitlines() or [""])[-1][:120]))

    f_rc, f_out, f_err = run(exp / "fixtures_e05.py", exp)
    note("S4_committed_fixtures", f_rc == 0, "fixtures_e05.py rc=%d%s"
         % (f_rc, "" if f_rc == 0 else " :: " + (f_err.strip().splitlines() or [""])[-1][:120]))

    gate = json.loads((exp / "CONSISTENCY_RECEIPT.json").read_text(encoding="utf-8"))
    fix = json.loads((exp / "FIXTURE_RESULTS.json").read_text(encoding="utf-8"))

    note("S5_gate_parts", gate["part_a_specification_consistency"]["passed"]
         and gate["part_b_empirical_reconstruction"]["passed"],
         "Part A %s, Part B %s" % (gate["part_a_specification_consistency"]["passed"],
                                   gate["part_b_empirical_reconstruction"]["passed"]))
    n_fix = sum(1 for f in fix["fixtures"] if f["passed"])
    note("S6_fixtures_all", n_fix == len(fix["fixtures"]),
         "%d/%d fixtures passed under committed code" % (n_fix, len(fix["fixtures"])))

    recon = gate["part_b_empirical_reconstruction"]["reconstructed"]
    binding = gate["part_b_empirical_reconstruction"]["binding_invariants"]
    note("S7_reconstruction_binding",
         recon["n_subsets"] == binding["n_subsets"]
         and list(recon["BEST"]) == list(binding["BEST"])
         and list(recon["WORST"]) == list(binding["WORST"]),
         "committed code reconstructs %d subsets, BEST %s, WORST %s"
         % (recon["n_subsets"], recon["BEST"], recon["WORST"]))

    # --- would the driver admit EXECUTE? ----------------------------------
    sys.path.insert(0, str(exp))
    admit, admit_detail = False, ""
    try:
        import importlib
        import execute_e05 as X                              # noqa: E402
        importlib.reload(X)
        c = X.bind_contract()
        admit = (c.hash == EXPECTED_HASH)
        admit_detail = "bind_contract() succeeded and froze %s" % c.hash[:16]
    except Exception as e:                                   # noqa: BLE001
        admit_detail = "%s: %s" % (type(e).__name__, str(e)[:120])
    note("S8_driver_admits_execute", admit, admit_detail)

    note("S9_subtree_clean_at_commit", dirty == "",
         "no uncommitted campaign changes" if dirty == ""
         else "uncommitted: %s" % dirty.replace("\n", " | ")[:160])

    ok = all(f["passed"] for f in findings)
    print("\n    %d/%d self-check findings passed" % (sum(f["passed"] for f in findings), len(findings)))
    print("    EXECUTE ADMISSIBLE: %s" % ("YES" if ok else "NO"))

    spec = committed_contract["contract"]
    receipt = {
        "campaign_id": "cw01-2026-09-17", "experiment_id": "cw01-e05",
        "attempt_id": spec["attempt_id"],
        "verified_against": "COMMITTED state extracted from HEAD via git archive; the working tree was not used",
        "commit_sha": sha, "commit_short": short, "branch": branch,
        "verdict_contract_sha256": body_hash,
        "binding_specification": {
            "budget_B": spec["budget_B"],
            "statistic_name": spec["statistic_name"],
            "statistic_formula": spec["statistic_formula"],
            "normalisation": spec["normalisation"],
            "null_construction": spec["null_construction"],
            "effect_clearing_rule": spec["effect_clearing_rule"],
            "set_selection_procedure": spec["set_selection_procedure"],
            "baseline_law_rule": spec["baseline_law_rule"],
            "BEST": recon["BEST"], "WORST": recon["WORST"],
            "n_subsets": recon["n_subsets"]},
        "fixtures": fix["fixtures"],
        "consistency_gate": {"part_a": gate["part_a_specification_consistency"]["checks"],
                             "part_b": gate["part_b_empirical_reconstruction"]["checks"],
                             "gate": gate["gate"]},
        "findings": findings,
        "execute_admissible": ok,
        "freeze_rule": spec["freeze_rule"]}
    (HERE / "SELFCHECK.json").write_text(json.dumps(receipt, indent=1), encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
