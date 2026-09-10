"""H1 three arms and H0 four cells, executed end to end on the DEV build.

WHAT THIS IS. A Vivarium demonstration that `cegis_boolean_v1` executes the
comparison families Archaeon will issue: every row goes through the real queue,
the real loader, a real engine and the real work lifecycle, and the counts
below come out of the register rather than out of this script's memory.

WHAT THIS IS NOT, and the distinction matters more than the numbers.

  It is NOT the H1 alpha and it is NOT the H0 alpha. Archaeon issues those --
  the task set, the arm assignment, the frozen retrieval policy, the source
  packs and the seeds are theirs. Harmonia owns the analysis. Running the
  machinery is what this file establishes.

  In particular there is NO RELEVANCE POLICY HERE. H1's third arm is
  "relevant compatible source inputs", and relevance must be ranked by a
  declared structural signature visible equally to every arm -- never by the
  target's own labels, which is the one thing a demo author sitting next to
  the truth table is most likely to do by accident. So the two pack arms below
  are labelled `pack_a` and `pack_b` and NEITHER is claimed to be relevant.
  Substituting Archaeon's frozen policy for those labels is the whole of what
  turns this into H1.

  No contrast is computed. G = S11 - S00 and I = S11 - S10 - S01 + S00 are
  Harmonia's analyses under Harmonia's rules; a per-arm count table is the
  executor's evidence and stops there.

USAGE
    VIV_SCHEMA=viv_dev_h0h5 VIV_PEW_NAMESPACE=test VIV_IDENTITY_ROLE=test \\
        python tools/h1_h0_alpha_demo.py --sfe http://127.0.0.1:8899
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
for extra in (str(HERE), str(HERE / "tests"),
              str(HERE.parent), str(HERE.parent / "SerendipityFoundry"
                                    / "SerendipityFoundryClient")):
    if extra not in sys.path:
        sys.path.insert(0, extra)

from artifact_fixtures import input_set                       # noqa: E402
from viv import artifacts as _a                               # noqa: E402
from viv import db as _db                                     # noqa: E402
from viv import queue as _q                                   # noqa: E402
from viv.loop import Vivarium                                 # noqa: E402
from viv.runner import SfeRunner                              # noqa: E402

# --------------------------------------------------------------- the tasks
def _tt(fn):
    return "".join(str(fn((k >> 2) & 1, (k >> 1) & 1, k & 1)) for k in range(8))


TASKS = {
    "and01":  _tt(lambda a, b, c: a & b),
    "or12":   _tt(lambda a, b, c: b | c),
    "xor3":   _tt(lambda a, b, c: a ^ b ^ c),
    "maj3":   _tt(lambda a, b, c: 1 if a + b + c >= 2 else 0),
    "x0nx2":  _tt(lambda a, b, c: a & (1 - c)),
    "parity2": _tt(lambda a, b, c: a ^ c),
}

#: Two fixed input packs. NEITHER is a relevance policy; see the module
#: docstring. They differ in which assignments they carry, which is exactly the
#: axis a real retrieval policy would vary along.
PACK_A = [[0, 0, 0], [1, 1, 1], [0, 1, 0], [1, 0, 1]]
PACK_B = [[1, 1, 0], [0, 0, 1], [1, 0, 0], [0, 1, 1]]

#: HAND-BUILT, and therefore an INSTRUMENT CONTROL. These are the subterms of
#: MAJ3; that they help is arithmetic, not evidence that an extracted library
#: would. H0's design says the same of its own library fixtures.
INSTRUMENT_LIBRARY = [
    {"name": "ab", "expr": ["and", ["input", 0], ["input", 1]]},
    {"name": "ac", "expr": ["and", ["input", 0], ["input", 2]]},
    {"name": "bc", "expr": ["and", ["input", 1], ["input", 2]]},
]

BASE = {
    "grammar_version": "proteus.boolean_grammar.v0",
    "candidate_policy": "seeded_enumeration_v1",
    "candidate_seed": 20260910,
    "max_expr_size": 5,
    "max_candidates": 100000,
    "oracle_call_cap": 100000,
    # The cap that BINDS. Chosen so the task set spreads across solved,
    # space-exhausted and budget-stopped rather than all landing in one bucket
    # -- a comparison in which every arm saturates measures nothing, which the
    # design says of eight inputs in as many words.
    "vm_op_cap": 6000,
    "trace_bound": 32,
    "vm_ticks": 2,
    "case_ordering": "proteus_declared",
    "termination": "first_solution",
    "seed_probe_count": 4,
    "shortfall_rule": "report_and_proceed",
}


def library_bytes(components):
    obj = {"artifact_type": "component_library", "schema_version": "1",
           "interface_id": "boolean-components-v1",
           "components": [dict(c) for c in components]}
    raw = _a.canonical_bytes(obj)
    slot = {"digest": _a.digest_of(raw), "artifact_type": "component_library",
            "schema_version": "1", "codec": "canonical-json-v1",
            "expected_bytes": len(raw),
            "interface_id": "boolean-components-v1"}
    return raw, slot


def spec_for(target, *, pack_slot, lib_slot):
    payload = dict(BASE, target_truth_table=target,
                   source_pack=pack_slot, component_library=lib_slot)
    return {"spec_version": 3, "world": {"seed_root": 20260910},
            "hypothesis": "a bounded search finds a Boolean program under a "
                          "fixed op cap, or reports why it did not",
            "prediction": None,
            "work": {"kind": "cegis_boolean_v1", "payload": payload},
            "outcome_rule": {"field": "solved", "op": "==", "value": True,
                             "if_true": "SURVIVED", "if_false": "FALSIFIED",
                             "if_indeterminate": "INCONCLUSIVE",
                             "aggregate": "first"},
            "pew": None,
            "repeat": {"count": 1, "order": "sequential",
                       "seed_derivation": "constant", "state": "reset",
                       "budget": {"max_seconds": 300, "max_observations": 1}}}


EMPTY_COUNTS = {"assigned": 0, "attempted": 0, "solved": 0,
                "exhausted_space": 0, "budget_vm_ops": 0,
                "budget_oracle_calls": 0, "budget_candidates": 0,
                "invalid": 0, "infrastructure_failure": 0}


def main() -> int:                                            # noqa: C901
    ap = argparse.ArgumentParser()
    ap.add_argument("--sfe", required=True)
    ap.add_argument("--out", default=None)
    # DECLARED, not tuned. The cap is the axis the design says the comparison
    # lives on, so it is an argument and every run records the value it used.
    # Two settings are run because an instrument that can only produce a tie
    # has not been shown able to show anything -- that is the positive control
    # on the DEMONSTRATION, and it is not a licence to retune an experiment.
    ap.add_argument("--vm-op-cap", type=int, default=6000)
    args = ap.parse_args()
    BASE["vm_op_cap"] = args.vm_op_cap

    cfg = _db.load_config()
    schema = cfg["schema"]
    if schema == "viv":
        print("refusing: VIV_SCHEMA is the production register", file=sys.stderr)
        return 2
    if "192.168" in args.sfe:
        print("refusing: --sfe looks like production", file=sys.stderr)
        return 2

    from sfclient import EngineClient
    client = EngineClient(args.sfe)
    client.register("vivarium-h1h0-demo-%s" % uuid.uuid4().hex[:6])
    version = client.version()

    conn = _db.connect()
    _db.apply_migrations(conn, target_schema=schema)

    # -- the producer publishes the packs and the instrument library ---------
    sid = client.create_session("h1h0-producer")
    pw = client.create_world(sid, "h1h0-producer-%s" % uuid.uuid4().hex[:8],
                             seed_root=20260910,
                             sharing_policy="EXPLICIT_IMPORT_ONLY")
    producer = pw["world_id"]
    client.start(producer)

    artifacts = {}
    for name, rows in (("pack_a", PACK_A), ("pack_b", PACK_B)):
        _obj, raw, slot = input_set(rows)
        aid = client.artifact(producer, "failure_input_set", raw,
                              expected_blob_hash=slot["digest"])["artifact_id"]
        artifacts[name] = (slot, aid)
    lraw, lslot = library_bytes(INSTRUMENT_LIBRARY)
    laid = client.artifact(producer, "component_library", lraw,
                           expected_blob_hash=lslot["digest"])["artifact_id"]
    artifacts["library"] = (lslot, laid)

    def locators(*names):
        out = {}
        for n in names:
            slot, aid = artifacts[n]
            out[slot["digest"]] = {"source_world": producer,
                                   "source_artifact": aid}
        return out

    # -- the two families ---------------------------------------------------
    h1_family = "h1-alpha-demo-%s" % uuid.uuid4().hex[:8]
    h0_family = "h0-alpha-demo-%s" % uuid.uuid4().hex[:8]
    plan = []
    for task, tt in sorted(TASKS.items()):
        plan.append((h1_family, "fresh", task, tt, None, None, ()))
        plan.append((h1_family, "pack_a", task, tt, "pack_a", None, ("pack_a",)))
        plan.append((h1_family, "pack_b", task, tt, "pack_b", None, ("pack_b",)))
        plan.append((h0_family, "S00", task, tt, None, None, ()))
        plan.append((h0_family, "S10", task, tt, "pack_a", None, ("pack_a",)))
        plan.append((h0_family, "S01", task, tt, None, "library", ("library",)))
        plan.append((h0_family, "S11", task, tt, "pack_a", "library",
                     ("pack_a", "library")))

    rows = []
    for family, arm, task, tt, pack, lib, needed in plan:
        pack_slot = artifacts[pack][0] if pack else None
        lib_slot = artifacts[lib][0] if lib else None
        spec = spec_for(tt, pack_slot=pack_slot, lib_slot=lib_slot)
        try:
            eid = _q.enqueue(
                conn, created_by="vivarium:h1h0-demo",
                source_reason="executability demonstration for the arms "
                              "Archaeon will issue",
                source_evidence={"family": family, "arm": arm, "task": task},
                experiment_spec=spec, schema=schema,
                family_id=family, arm_id=arm,
                artifact_locators=locators(*needed))
            conn.commit()
            rows.append((family, arm, task, eid, None))
        except Exception as exc:                              # noqa: BLE001
            # Refused at ADMISSION: the row never existed, so it is `invalid`
            # for this arm and is still counted in its denominator.
            rows.append((family, arm, task, None, str(exc)[:200]))

    runner = SfeRunner(base_url=args.sfe, token=client.token,
                       client_id=getattr(client, "client_id", None),
                       worker_id="vivarium@h1h0-demo", lease_s=180.0,
                       log=lambda *a: None)
    viv = Vivarium(worker_id="vivarium@h1h0-demo", schema=schema,
                   runner=runner, pew_client=None, log=lambda *a: None)

    counts = {}
    per_row = []
    for family, arm, task, eid, admission_error in rows:
        key = (family, arm)
        c = counts.setdefault(key, dict(EMPTY_COUNTS))
        c["assigned"] += 1
        if eid is None:
            c["invalid"] += 1
            per_row.append({"family": family, "arm": arm, "task": task,
                            "outcome": "ADMISSION_REFUSED",
                            "error": admission_error})
            continue
        report = viv.tick(conn)
        conn.commit()
        row = _q.get(conn, eid, schema=schema)
        summary = row["result_summary"] or {}
        if report.outcome == "EXECUTED":
            c["attempted"] += 1
            res = summary["result"]["repeats"][0]["result"]
            st = res["status"]
            if st == "SOLVED":
                c["solved"] += 1
            elif st == "EXHAUSTED_CANDIDATES":
                c["exhausted_space"] += 1
            elif st == "BUDGET_VM_OPS":
                c["budget_vm_ops"] += 1
            elif st == "BUDGET_ORACLE_CALLS":
                c["budget_oracle_calls"] += 1
            elif st == "BUDGET_CANDIDATES":
                c["budget_candidates"] += 1
            per_row.append({"family": family, "arm": arm, "task": task,
                            "experiment_id": str(eid), "status": st,
                            "solved": res["solved"], "vm_ops": res["vm_ops"],
                            "oracle_calls": res["oracle_calls"],
                            "candidates_tried": res["candidates_tried"],
                            "constraints_seeded": res["constraints_seeded"],
                            "shortfall": res["seed_probe_shortfall"],
                            "solution": res.get("solution")})
        else:
            fc = summary.get("failure_class") or report.failure_class
            if fc == "PREFLIGHT_REJECTED":
                c["invalid"] += 1
            else:
                c["attempted"] += 1
                c["infrastructure_failure"] += 1
            per_row.append({"family": family, "arm": arm, "task": task,
                            "experiment_id": str(eid),
                            "outcome": report.outcome, "failure_class": fc})

    receipt = {
        "what_this_is": "Vivarium executability demonstration on the DEV "
                        "build. NOT the H1 or H0 alpha: Archaeon issues those "
                        "and Harmonia analyses them. No relevance policy is "
                        "implemented here and no contrast is computed.",
        "queue_schema": schema,
        "engine": {"base_url": args.sfe, **version},
        "producer_world": producer,
        "artifacts": {n: {"digest": s["digest"], "artifact_id": a}
                      for n, (s, a) in sorted(artifacts.items())},
        "families": {"h1": h1_family, "h0": h0_family},
        "caps": {k: BASE[k] for k in ("vm_op_cap", "oracle_call_cap",
                                      "max_candidates", "max_expr_size",
                                      "seed_probe_count")},
        "tasks": sorted(TASKS),
        "counts_per_arm": {"%s/%s" % k: v for k, v in sorted(counts.items())},
        "rows": per_row,
    }
    blob = json.dumps(receipt, indent=2, default=str)
    if args.out:
        Path(args.out).write_text(blob + "\n", encoding="utf-8")

    print("family/arm                          assigned attempted solved "
          "exh_space budget_ops budget_orc budget_cand invalid infra")
    for k, c in sorted(counts.items()):
        print("%-34s %8d %9d %6d %9d %10d %10d %11d %7d %5d"
              % ("%s/%s" % (k[0].split("-")[0] + "-" + k[1], ""),
                 c["assigned"], c["attempted"], c["solved"],
                 c["exhausted_space"], c["budget_vm_ops"],
                 c["budget_oracle_calls"], c["budget_candidates"],
                 c["invalid"], c["infrastructure_failure"]))

    # THE PER-TASK MATRIX, printed because the aggregate hid the finding.
    # At vm_op_cap=30000 every arm scored 5 of 6 -- and underneath, the
    # instrument library SOLVED maj3 (unreachable without it) and LOST xor3
    # (its extra leaves enlarge the space and push xor3's solution further
    # down the same enumeration). A solve-rate contrast can net to zero while
    # both cells move in opposite directions on different tasks. That is a
    # caution about the H0 alpha's denominator, not a result.
    print()
    arms = sorted({(r["family"], r["arm"]) for r in per_row})
    print("%-9s %s" % ("task", " ".join("%-14s" % a[1] for a in arms)))
    for task in sorted(TASKS):
        cells = []
        for fam, arm in arms:
            hit = [r for r in per_row if r["task"] == task
                   and r["arm"] == arm and r["family"] == fam]
            label = (hit[0].get("status") or hit[0].get("outcome") or "-")
            cells.append("%-14s" % label[:14])
        print("%-9s %s" % (task, " ".join(cells)))

    if args.out:
        print("\nreceipt: %s" % args.out)
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
