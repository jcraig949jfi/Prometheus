"""The Cycle-9 campaign runner: consume the FROZEN manifest, drain, stop.

    python run_campaign.py [--workers 6] [--observatory observatory]

REFUSES TO START unless the freeze succeeded: FREEZE.json exists, CALIBRATION.json says
PASS, and the protocol hash recomputed NOW from source equals the frozen one (any edit to
a campaign module or to PREREGISTRATION.md after freeze changes it). The manifest is read
from MANIFEST_FROZEN.json, never rebuilt, and its hash is re-verified.

AFTER LAUNCH, BY CONSTRUCTION: no human in the loop, no result-dependent allocation, no
threshold input (thresholds live in the hash-covered constants object), no replacement
jobs. The job list is exactly the manifest's (bundle, arm) pairs. A job whose worker
raised is retried ONCE with identical inputs (deterministic re-execution, not a
replacement); a second failure is recorded in ERRORS.jsonl and its bundle stays
INCOMPLETE, which the adjudicators report as such.

RESUME. The bundle store (P-7) is the only state. On start the runner opens every
bundle from disk and schedules only the arms not yet present. Only this process writes
the store, one atomic file per bundle, so a kill at any instant leaves every bundle file
either before or after a result, never torn. Re-delivering an identical result is
idempotent; a DIFFERENT result for a present arm raises (a determinism violation).

The observatory is created here, only after the freeze checks pass.
"""
from __future__ import annotations

import hashlib
import json
import multiprocessing as mp
import os
import pathlib
import sys
import time
import traceback

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import bundles as BD   # noqa: E402

KWARGS_KEY = "__run_kwargs__"
ROLES = {"H1": {"gate_on_cost_vm": "TREATMENT", "gate_off_cost_vm": "CONTROL"},
         "H2": {"B_reimplant_actual": "TREATMENT", "C_reimplant_random": "CONTROL"},
         "H3": {"A_easy_plus_migration": "TREATMENT", "B_homogeneous_same_migration": "CONTROL"}}


class FreezeError(Exception):
    pass


def spec_of(b):
    """Manifest bundle -> content-addressed BundleSpec. Run kwargs are folded into the
    hashed cell under KWARGS_KEY, so two arms differing only in kwargs (H1's gate, H2's
    implant bytes) have different identities."""
    roles = ROLES.get(b["hypothesis_id"], {})
    arms = [BD.ArmSpec(a["arm"], roles.get(a["arm"], "INTERVENTION"),
                       dict(a["cell"], **{KWARGS_KEY: a.get("kwargs") or {}}),
                       a["seed"], a["tier"]) for a in b["arms"]]
    return BD.BundleSpec(b["hypothesis_id"], b["pair_seed"], arms,
                         b.get("factor_deltas") or {}, b["expected_cardinality"])


def verify_freeze(root=HERE):
    """Every launch precondition, or FreezeError naming the first that fails."""
    fz = root / "FREEZE.json"
    if not fz.exists():
        raise FreezeError("FREEZE.json missing: the campaign is not frozen")
    freeze = json.loads(fz.read_text())
    cal = root / "CALIBRATION.json"
    if not cal.exists() or json.loads(cal.read_text()).get("gate") != "PASS":
        raise FreezeError("CALIBRATION.json missing or not PASS")
    import proposed_hashes as PH
    body, protocol, m, bad, panel = PH.compute()
    if protocol != freeze["protocol_hash"]:
        raise FreezeError("protocol hash drifted since freeze: %s != %s"
                          % (protocol[:16], freeze["protocol_hash"][:16]))
    mf = json.loads((root / "MANIFEST_FROZEN.json").read_text())
    if mf["manifest_hash"] != freeze["manifest_hash"] or m["manifest_hash"] != freeze["manifest_hash"]:
        raise FreezeError("frozen manifest hash mismatch")
    return freeze, mf


def _run_job(job):
    """Worker: run one arm. Returns (bundle_id, arm, summary | None, error | None)."""
    import world
    kw = dict(job["kwargs"])
    kw.pop("implant_source", None)
    hx = kw.pop("implant_hex", None)
    if hx:
        kw["implant_bytes"] = bytes.fromhex(hx)
    if job.get("max_epochs"):
        kw["max_epochs"] = job["max_epochs"]
    try:
        r = world.run_cell(job["cell"], job["seed"], tier=job["tier"], **kw)
        return job["bundle_id"], job["arm"], r["summary"], None
    except Exception as e:                                           # noqa: BLE001
        return job["bundle_id"], job["arm"], None, "%s: %s\n%s" % (
            type(e).__name__, e, traceback.format_exc()[-1200:])


def jobs_for(store, specs, max_epochs=None):
    out = []
    for spec in specs:
        st = store.open(spec)
        for a in spec.arms:
            if a.name in st.results:
                continue
            cell = dict(a.cell)
            kwargs = cell.pop(KWARGS_KEY, {})
            out.append({"bundle_id": spec.bundle_id, "arm": a.name, "cell": cell,
                        "seed": a.seed, "tier": a.tier, "kwargs": kwargs,
                        "max_epochs": max_epochs})
    return out


def run(manifest, obs, workers=6, max_epochs=None, stop_after=None, log=print):
    """Drain the manifest into the bundle store at `obs`. `stop_after` (tests only) makes
    the process exit abruptly after that many stored results - the kill-injection hook."""
    obs = pathlib.Path(obs)
    store = BD.BundleStore(obs / "bundles")
    specs = {}
    for b in manifest["bundles"]:
        s = spec_of(b)
        specs[s.bundle_id] = s
    pending = jobs_for(store, specs.values(), max_epochs)
    log("jobs total %d, pending %d" % (sum(len(s.arms) for s in specs.values()), len(pending)))
    t0 = time.time()
    done = 0
    retried = set()
    errors = obs / "ERRORS.jsonl"
    state_p = obs / "STATE.json"
    queue = list(pending)
    with mp.Pool(workers) as pool:
        while queue:
            batch, queue = queue, []
            for bid, arm, summary, err in pool.imap_unordered(_run_job, batch):
                if err is not None:
                    key = (bid, arm)
                    retry = key not in retried
                    if retry:
                        retried.add(key)
                        queue.append(next(j for j in batch
                                          if j["bundle_id"] == bid and j["arm"] == arm))
                    with errors.open("a") as fh:
                        fh.write(json.dumps({"bundle_id": bid, "arm": arm, "error": err,
                                             "retry_scheduled": retry,
                                             "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}) + "\n")
                    continue
                st = store.open(specs[bid])
                st.add_result(arm, summary)
                store.put(st)
                done += 1
                if done % 10 == 0 or not queue:
                    state_p.write_text(json.dumps({"stored_this_session": done,
                                                   "pending_at_start": len(pending),
                                                   "elapsed_s": round(time.time() - t0, 1),
                                                   "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}))
                    log("stored %d/%d  %.0fs" % (done, len(pending), time.time() - t0))
                if stop_after is not None and done >= stop_after:
                    pool.terminate()
                    os._exit(3)                                # abrupt, like a kill
    complete = sum(1 for s in specs.values() if store.open(s).is_complete())
    log("drained: %d of %d bundles complete" % (complete, len(specs)))
    return complete, len(specs)


def main(argv):
    workers = int(argv[argv.index("--workers") + 1]) if "--workers" in argv else 6
    obs = HERE / (argv[argv.index("--observatory") + 1] if "--observatory" in argv else "observatory")
    freeze, mf = verify_freeze()
    # Record the launch commit, and refuse to launch from a tree whose campaign files
    # differ from that commit: the record must name code that actually ran.
    import subprocess
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=HERE, capture_output=True,
                          text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--", ".", ":!observatory"],
                           cwd=HERE, capture_output=True, text=True).stdout.strip()
    if dirty:
        raise FreezeError("refusing to launch from an uncommitted campaign tree: " + dirty[:800])
    freeze["launch_commit"] = head
    obs.mkdir(parents=True, exist_ok=True)
    launch = obs / "LAUNCH.json"
    if not launch.exists():
        launch.write_text(json.dumps({"protocol_hash": freeze["protocol_hash"],
                                      "manifest_hash": freeze["manifest_hash"],
                                      "launch_commit": freeze.get("launch_commit"),
                                      "workers": workers,
                                      "launched": time.strftime("%Y-%m-%dT%H:%M:%S")}, indent=1))
    complete, total = run(mf, obs, workers=workers)
    (obs / "DONE.json").write_text(json.dumps({"complete_bundles": complete, "bundles": total,
                                               "drained": time.strftime("%Y-%m-%dT%H:%M:%S")}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
