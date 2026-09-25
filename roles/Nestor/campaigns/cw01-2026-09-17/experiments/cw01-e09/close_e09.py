"""Close cw01-e09 in CAMPAIGN_STATE.json; totals derived from the ledger and gated."""
from __future__ import annotations

import collections
import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent


def _bootstrap_lib():
    for cand in [HERE] + list(HERE.parents):
        if (cand / "lib" / "repopath.py").exists():
            sys.path.insert(0, str(cand / "lib"))
            return cand / "lib"
    raise RuntimeError("cannot locate lib/repopath.py walking up from %s" % HERE)


_bootstrap_lib()
import repopath as RP          # noqa: E402
import recordsafety as RS      # noqa: E402

CAMPAIGN = RP.find_campaign_root(HERE)
STATE = CAMPAIGN / "CAMPAIGN_STATE.json"
LEDGER = CAMPAIGN / "DEFECTS.jsonl"


def main():
    st = json.loads(STATE.read_text(encoding="utf-8"))
    disp = json.loads((HERE / "DISPOSITION.json").read_text(encoding="utf-8"))
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    exp = next(e for e in st["experiments"] if e["id"] == "cw01-e09")
    exp["status"] = "COMPLETE"
    exp["attempts"] = [{"attempt_id": "cw01-e09-a01", "phase": "RECONCILE",
                        "disposition": "INCONCLUSIVE / DESIGN UNREACHABLE",
                        "started_local": "2026-09-18 10:25:00", "ended_local": now,
                        "preregistered": False, "executed_under_frozen_contract": False}]
    exp["disposition"] = "INCONCLUSIVE"
    exp["headline"] = {
        "reason": "closed at reconcile: the organism has no call/compose/reuse mechanism (one 3-bit nudge into one world register per tick); the only native chain form cannot exceed its primitive ceiling on held64, which is itself the abstain floor",
        "single_op_ceiling_held64": disp["probe"]["single_op_ceiling_held64"],
        "chain_arith_held64": disp["probe"]["chain_arith_held64"],
        "chain_scrambled_held64": disp["probe"]["chain_scrambled_held64"],
        "not_null_because": "no comparison was posed; there is no composition mechanism to give or withhold",
    }
    exp["limitations"] = disp["what_was_not_done_deliberately"]
    exp["what_a_future_attempt_would_need"] = disp["what_a_future_attempt_would_need"]
    st["active"] = {"experiment_id": "cw01-e09", "attempt_id": "cw01-e09-a01", "phase": "CLOSED_AT_RECONCILE",
                    "disposition": "INCONCLUSIVE / DESIGN UNREACHABLE", "phase_completed": ["RECONCILE"],
                    "next": "CONTINUE -> cw01-e10 mutable graph physics / semiring mutation (awaiting operator brief)"}
    st["updated_local"] = now
    st["owned_runtime_resources"] = []
    st["durable_artifacts"] += [
        "experiments/cw01-e09/SUBSTRATE_RECONCILE.md - the seven composition questions answered from code; probe table; decision",
        "experiments/cw01-e09/probe_e09.py + PROBE_E09.json - single-op ceiling (exhaustive 2400) and 3-op chain pilots, arithmetic and scrambled, on held64",
        "experiments/cw01-e09/DISPOSITION.json - INCONCLUSIVE / DESIGN UNREACHABLE at reconcile, with what a future attempt needs",
    ]
    st["factory_findings_so_far"].append(
        "e09 was rejected at RECONCILE in under an hour: reading the world's action semantics (one 3-bit nudge times 251 into "
        "one register per tick) answered the brief's seven composition questions from code, and a 32-second probe of the "
        "substrate's only native chain form showed every program policy at or below the abstain floor on held-out seeds, "
        "scrambled op tables included. No preregistration was written for an instrument the substrate cannot supply. The "
        "held64-vs-train8 decoupling seen in e08 (D065) recurred across three organism families (D069): w13's train "
        "fitness is a weak proxy for capability, which is a substrate screening finding rather than an experiment finding.")
    entries = [json.loads(l) for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()]
    per = collections.Counter(d.get("experiment_id") for d in entries)
    tot = st["campaign_totals"]
    tot["experiments_attempted"] = 9
    tot["inconclusive"] = tot.get("inconclusive", 0) + 1
    tot["defects_logged"] = len(entries)
    tot["defects_per_experiment"] = {str(k).replace("cw01-", ""): v for k, v in sorted(per.items())}
    STATE.write_text(json.dumps(st, indent=1, ensure_ascii=True), encoding="utf-8")
    RS.require_ascii_safe(STATE)
    RS.require_ascii_safe(HERE / "DISPOSITION.json")
    v = RS.require_tally_consistent(STATE, LEDGER)
    print("CAMPAIGN_STATE closed for e09 | tally %s (%d)" % (v["outcome"], v["derived"]["total"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
