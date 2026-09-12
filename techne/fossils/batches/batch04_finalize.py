"""Batch 04 finalize (2026-09-12): fill observability + nyx_handoff from the records+receipts,
and set the two SOURCE_ONLY specimens honestly. Run ONCE after batch04.py and after all runs;
do NOT re-run batch04.py afterward (its main() would reset observability/nyx_handoff).

    python -m techne.fossils.batches.batch04_finalize

Observability flags are acquisition facts, never a decomposition. ORACLE_BACKED is set per
specimen from whether the receipt checked the result against an independent expectation.
"""
from __future__ import annotations

import json
from .. import record as R
from .. import vault
from . import batch04

# specimens whose receipt grades the machine against an independent expectation (an oracle),
# vs those that only demonstrate activity. uart2bus self-checks against a reg-file model but we
# do not pin a reference decoded byte, so it is marked activity-only (no) -- honest.
ORACLE = {
    "willemt-raft": True, "arduino-pid": True, "python-control": True,
    "simple-kalman-denyssene": True, "filterpy-labbe": True, "viterbi-hmm-xukmin": True,
    "lru-cache-goldsborough": True, "buddy-alloc-spaskalev": True,
    "verilog-rr-arbiter": True, "verilog-generic-fifo": True, "verilog-uart2bus": False,
    "genann": True, "minisom": True, "hopfield-takyamamoto": True,
    "linux-tcp-congestion": False, "do-mpc": False,
}
SOURCE_ONLY = {
    "linux-tcp-congestion": "SOURCE_ONLY: CUBIC and BBR are Linux-kernel congestion modules "
        "(tcp_cubic.c, tcp_bbr.c) that link against the kernel's TCP stack; running them means "
        "booting a kernel with a network under load. Preserved + tree-hashed for Nyx to read the "
        "avoidance/backoff logic; no in-vault runner.",
    "do-mpc": "SOURCE_ONLY: do-mpc builds on CasADi + IPOPT (heavy nonlinear-optimisation stack). "
        "Preserved + tree-hashed; a runnable MPC receipt is deferred to a world with CasADi/IPOPT.",
}


def fill(sid: str) -> list[str]:
    rec = R.load(sid)
    rc = rec.get("run_classification", "NOT_ATTEMPTED")
    if sid in SOURCE_ONLY:
        rec["run_classification"] = "SOURCE_ONLY"
        rec["test_classification"] = "NO_TESTS"
        rc = "SOURCE_ONLY"
    runnable = rc.startswith("RUNNABLE")
    # newest receipt with ok=True, if any
    good = [x for x in rec.get("receipts", []) if x.get("ok")]
    receipt_ref = good[-1]["receipt"] if good else (rec["receipts"][-1]["receipt"] if rec.get("receipts") else "")
    obs = {
        "EXECUTABLE": "yes" if runnable else "no",
        "OBSERVABLE": "yes" if runnable else "no",         # every runnable specimen captured stdout
        "ORACLE_BACKED": "yes" if (runnable and ORACLE.get(sid)) else "no",
        "INTERVENTION_READY": "yes" if (runnable and rec.get("behavioral_entry_point")) else "unknown",
        "PATCH_INTERVENTION": "unknown",                   # not exercised this batch
        "OPAQUE": "no",                                    # source is inspectable for all
    }
    rec["observability"] = obs
    origin = rec.get("source_origin", {})
    arts = origin.get("artifacts", [{}])
    a0 = arts[0] if arts else {}
    where = "%s ; %s" % (a0.get("url") or a0.get("repo") or json.dumps(origin)[:80], rec.get("source_type", ""))
    if a0.get("commit_resolved") or a0.get("commit"):
        where += " @ " + (a0.get("commit_resolved") or a0.get("commit"))
    if runnable:
        how_run = "recipe.json (runner %s); python -m techne.fossils.harvest run %s" % (
            json.loads((vault.specimen_dir(sid) / "recipe.json").read_text()).get("runner", "?"), sid)
        how_know = "%s / %s ; receipt %s" % (rec["run_classification"], rec["test_classification"], receipt_ref)
    else:
        how_run = SOURCE_ONLY.get(sid, "not executed; source pinned + tree-hashed")
        how_know = "not executed; body tree_sha256 %s pinned in UPSTREAM_HASHES.txt" % rec.get("hashes", {}).get("tree_sha256", "")[:16]
    rec["nyx_handoff"] = {
        "here_is_the_machine": "vault body %s ; tracked techne/fossils/specimens/%s" % (vault.body_dir(sid), sid),
        "where_it_came_from": where,
        "how_to_run_it": how_run,
        "how_we_know_it_runs": how_know,
        "what_humans_used_it_for": rec.get("human_capability_summary", {}).get("built_to", ""),
    }
    probs = R.validate(rec)
    R.save(rec)
    return probs


def main():
    ids = [r["specimen_id"] for r in batch04.S]
    for sid in ids:
        probs = fill(sid)
        rec = R.load(sid)
        print("%-28s %-20s obs=%s %s" % (sid, rec["run_classification"],
              "".join("1" if v == "yes" else ("0" if v == "no" else "?") for v in rec["observability"].values()),
              "ok" if not probs else probs))


if __name__ == "__main__":
    main()
