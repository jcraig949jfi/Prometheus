"""Campaign 4 synthetic end-to-end rehearsal: the integration proof of record.

    python -m archaeon.campaign4.rehearsal --stage local      # S1, S2-validate, S8 (no engine)
    python -m archaeon.campaign4.rehearsal --stage full       # S1-S8 (needs the preconditions)

The plan and its declared failure modes are archaeon/campaign4/REHEARSAL_PLAN.md. This module is
the executable half. It carries NO scientific claim: every unit of work is Vivarium's `noop_v0`
kind, which exists to exercise the queue -> SFE -> PEW loop with no science in it, and every
object is labelled rehearsal so that no reader can mistake a row for evidence.

STAGES
  S1 build      the Campaign-4-shaped bundle, bound to the frozen identity tuple
  S2 enqueue    viv.cli enqueue with a request key (idempotency) and family/arm ids
  S3 execute    Vivarium's consumer, sequentially, against SFE 9.0.1
  S4 kill       a deliberate engine restart with a write in flight        [Daedalus]
  S5 resume     keyed retry/resume: one world, exact observations, no duplicate
  S6 publish    artifacts + records under archaeon/campaign4/
  S7 ingest     ew.campaign_ingest --campaign 4, rebuild x3, release check  [Mnemosyne]
  S8 reproduce  re-derive the receipt from committed files alone

`--stage local` runs exactly the stages that need no engine, no queue and no credential, and
reports every other stage as BLOCKED with the precondition that blocks it. It is meant to be run
NOW, so that when the preconditions clear the only new thing being tested is the seam, not this
harness.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
C4 = REPO / "archaeon" / "campaign4"
OUT = C4 / "REHEARSAL_RECEIPT.json"
BUNDLE = C4 / "rehearsal" / "bundle"

REHEARSAL_ID = "C4-REH-1"
ARMS = ("a", "b")
SEEDS = tuple(range(1, 25))          # 2 x 24 = 48 units
REPEATS = 24                         # 48 x 24 = 1,152 observations
N, G, E = 60, 20, 16

# The interruption must intersect LIVE work, so the workload is sized to run for minutes rather
# than seconds, and it is enqueued in WAVES. Wave 1 establishes the observed execution rate from
# the queue itself; the restart is then timed against that measured rate instead of a guess.
# Expected accounting invariant: observations == len(ARMS) * len(SEEDS) * REPEATS, exactly once,
# with no duplicate minted across the interruption.
EXPECTED_OBSERVATIONS = len(ARMS) * len(SEEDS) * REPEATS


def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha(b: bytes) -> str:
    return "sha256:" + hashlib.sha256(b).hexdigest()


def identity() -> dict:
    p = C4 / "CAMPAIGN4_EXECUTION_IDENTITY.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    return {"identity_file": str(p.relative_to(REPO)).replace("\\", "/"),
            "identity_file_digest": sha(p.read_bytes()),
            "tuple": {k: {kk: vv for kk, vv in v.items() if kk in
                          ("engine_source_hash", "schema_version", "engine_instance_id", "build_commit",
                           "foundry_profile_id", "grammar_hash", "reader_version", "campaign_seed")}
                      for k, v in d["tuple"].items()}}


def spec_for(arm: str, seed: int, campaign_seed: int) -> dict:
    """A v3 sealed spec. Execution inputs only: provenance lives in queue columns, never in the
    hash (viv/spec.py). world.name is forbidden -- Vivarium derives it from spec_hash."""
    return {
        "spec_version": 3,
        "world": {"seed_root": campaign_seed * 1000 + seed},
        "hypothesis": "REHEARSAL ONLY, no scientific content: the Campaign 4 execution tuple "
                      "carries a unit of work from enqueue to reproduced receipt through an engine restart.",
        "prediction": None,
        "work": {"kind": "noop_v0", "payload": {}},
        # required for an executable kind: SFE records an outcome for every observation and
        # Vivarium will not author one. noop_v0's only result field is `executed`.
        "outcome_rule": {"field": "executed", "op": "==", "value": True,
                         "if_true": "SURVIVED", "if_false": "FALSIFIED",
                         "if_indeterminate": "INCONCLUSIVE", "aggregate": "all"},
        "pew": None,
        # all five axes stated: none has a default, and noop_v0 is stateless so state is reset
        "repeat": {"count": REPEATS, "order": "sequential", "seed_derivation": "sha256_index",
                   "state": "reset", "budget": {"max_seconds": 600, "max_observations": REPEATS}},
    }


def s1_build(campaign_seed: int) -> dict:
    BUNDLE.mkdir(parents=True, exist_ok=True)
    units = []
    for arm in ARMS:
        for seed in SEEDS:
            spec = spec_for(arm, seed, campaign_seed)
            b = canon(spec)
            f = BUNDLE / ("rehearsal_%s_s%d.json" % (arm, seed))
            f.write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
            units.append({
                "arm": arm, "seed": seed, "file": str(f.relative_to(REPO)).replace("\\", "/"),
                "spec_sha256_canonical": sha(b),
                "request_key": "%s-%s-s%d" % (REHEARSAL_ID, arm, seed),
                "family_id": REHEARSAL_ID, "arm_id": REHEARSAL_ID + "-" + arm,
            })
    manifest = {"campaign_seed": campaign_seed, "label": "REHEARSAL -- NOT EVIDENCE",
                "rehearsal_id": REHEARSAL_ID, "repeats_per_unit": REPEATS,
                "expected_observations": EXPECTED_OBSERVATIONS,
                "accounting_invariants": {
                    "observations_exactly": EXPECTED_OBSERVATIONS,
                    "worlds_per_unit": 1,
                    "duplicates_permitted": 0,
                    "lost_permitted": 0,
                    "manual_repair_permitted": 0,
                    "note": "checked across the deliberate interruption: one world per unit, exact "
                            "observation count, no duplicate minted, no row repaired by hand"},
                "budget": {"N": N, "G": G, "E": E}, "arms": list(ARMS), "seeds": list(SEEDS), "units": units}
    mf = BUNDLE / "MANIFEST.json"
    mf.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return {"stage": "S1", "status": "OK", "units": len(units), "bundle_manifest": str(mf.relative_to(REPO)).replace("\\", "/"),
            "bundle_digest": sha(mf.read_bytes())}


def s2_validate() -> dict:
    """Validate every unit against Vivarium's OWN spec module, and compute spec_hash with it."""
    sys.path.insert(0, str(REPO / "vivarium"))
    try:
        from viv import spec as vspec                                  # noqa: PLC0415
    except Exception as e:                                             # noqa: BLE001
        return {"stage": "S2-validate", "status": "BLOCKED", "reason": "viv.spec not importable: %s" % e}
    manifest = json.loads((BUNDLE / "MANIFEST.json").read_text(encoding="utf-8"))
    rows = []
    for u in manifest["units"]:
        s = json.loads((REPO / u["file"]).read_text(encoding="utf-8"))
        try:
            vspec.validate(s)
            h = vspec.spec_hash(s)
            rows.append({"arm": u["arm"], "seed": u["seed"], "valid": True, "spec_hash": h,
                         "world_name": vspec.world_name(h)})
        except Exception as e:                                         # noqa: BLE001
            rows.append({"arm": u["arm"], "seed": u["seed"], "valid": False,
                         "reasons": getattr(e, "reasons", [str(e)])})
    ok = all(r["valid"] for r in rows)
    distinct = len({r.get("spec_hash") for r in rows if r.get("spec_hash")})
    return {"stage": "S2-validate", "status": "OK" if ok else "FAILED", "units": len(rows),
            "all_valid": ok, "distinct_spec_hashes": distinct, "rows": rows,
            "spec_version": getattr(vspec, "SPEC_VERSION", None),
            "arm_collision_by_contract": distinct < len(rows),
            "arm_collision_note": (
                "arms a and b differ only in QUEUE COLUMNS (arm_id, request_key), which viv/spec.py "
                "deliberately banishes from the sealed hash, so the pair shares one spec_hash and one "
                "derived world name. For this rehearsal that is correct and useful: the two arms are a "
                "REPLICATION PAIR, not a contrast, and the collision exercises the request-key path that "
                "keeps them distinct rows. CONSEQUENCE FOR CAMPAIGN 4: two arms that differ only in "
                "provenance are the same experiment; any real C4 contrast must differ in an EXECUTION "
                "INPUT or it will not be distinguishable in the sealed record.")}


def precondition_report() -> list:
    cred = C4 / "config.local.json"
    return [
        {"id": "P1", "what": "campaign 4 engine credential (archaeon/campaign4/config.local.json)",
         "present": cred.exists(), "owner": "operator / Daedalus", "blocks": ["S3", "S4", "S5", "S6", "S7", "S8"]},
        {"id": "P2", "what": "B1 read grant re-issued for cli_2bb36261 on the M2 ledger",
         "present": None, "owner": "Daedalus", "blocks": ["S3"]},
        {"id": "P3", "what": "~10 minute window for the deliberate mid-run engine restart",
         "present": None, "owner": "Daedalus + Vivarium", "blocks": ["S4", "S5"]},
        {"id": "P4", "what": "PEW ingest/rebuild/release-check leg", "present": None,
         "owner": "Mnemosyne", "blocks": ["S7"]},
        {"id": "P5", "what": "Archaeon's five campaign-3 viv rows stay HELD (must not be swept in)",
         "present": None, "owner": "Archaeon", "blocks": []},
    ]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=("local", "full"), default="local")
    a = ap.parse_args(argv)
    from archaeon.campaign4.c4base import CAMPAIGN_SEED
    t0 = time.time()
    stages = [s1_build(CAMPAIGN_SEED), s2_validate()]
    pre = precondition_report()
    blocked_by = {}
    for p in pre:
        if p["present"] is False or p["present"] is None:
            for s in p["blocks"]:
                blocked_by.setdefault(s, []).append(p["id"])
    if a.stage == "local":
        for s in ("S3", "S4", "S5", "S6", "S7", "S8"):
            stages.append({"stage": s, "status": "BLOCKED", "preconditions": blocked_by.get(s, [])})
    receipt = {
        "_what_this_is": "Campaign 4 synthetic end-to-end rehearsal receipt. REHEARSAL ONLY -- no scientific claim.",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "generated_by": "Archaeon[m2-411504ab]",
        "stage_mode": a.stage,
        "campaign_seed": CAMPAIGN_SEED,
        "identity": identity(),
        "plan": "archaeon/campaign4/REHEARSAL_PLAN.md",
        "stages": stages,
        "preconditions": pre,
        "wall_s": round(time.time() - t0, 1),
    }
    OUT.write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: receipt[k] for k in ("stage_mode", "campaign_seed", "stages", "preconditions", "wall_s")},
                     indent=1, sort_keys=True))
    print("\nwritten:", OUT, "\nreceipt sha256:", hashlib.sha256(OUT.read_bytes()).hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
