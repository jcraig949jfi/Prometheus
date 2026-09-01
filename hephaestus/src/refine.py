"""Queue refinement job (charter §10). What do we know now that we did not know three hours ago?

Recomputes derived fields from the attempt records, updates CHEAP_MODEL_FAILURES /
BEST_FAILED_CANDIDATE / KNOCKOUT_RESULTS, applies state transitions, re-renders packet.md.
Priority is raised only because evidence improved, never because an item is old.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hephaestus.src import packet as P  # noqa: E402

EXHAUST_MIN_ATTEMPTS = 4      # executed attempts (not NO_RESPONSE / JOB_ERROR)
EXHAUST_MIN_MODELS = 2        # distinct cheap models
EXHAUST_MIN_FAMILIES = 2      # distinct failure families observed


def _executed(a: dict) -> bool:
    """An attempt counts toward exhaustion only if the MODEL failed, not the harness.
    Attempts annotated harness_fault=True (e.g. a token budget that truncated before the code
    fence) are kept in the record but excluded from the exhaustion count."""
    if a.get("harness_fault"):
        return False
    v = str(a.get("verdict", ""))
    return v.startswith("PASS_DEV") or v in {"FAIL_DEV", "STATIC_REJECT", "IMPORT_ERROR", "NO_OP_FUNCTION",
                                             "RUNTIME_ERROR_ALL", "INTERFACE_VIOLATION", "TIMEOUT", "NO_CODE"}


def refine_packet(p: dict) -> dict:
    mint = p["MINT_ID"]
    attempts = p.get("CHEAP_MODEL_ATTEMPTS") or []
    executed = [a for a in attempts if _executed(a)]
    # PASS_DEV, PASS_DEV_WITH_UNTESTED_COMPONENT, PASS_DEV_UNVERIFIED_COVERAGE all count as dev passes
    # for state purposes; the qualifier travels with the record (Addendum 1, Q3).
    fails = [a for a in executed if not str(a.get("verdict", "")).startswith("PASS_DEV")]
    passes = [a for a in executed if str(a.get("verdict", "")).startswith("PASS_DEV")]
    fam = Counter()
    for a in fails:
        for f in a.get("failure_families") or [a.get("verdict")]:
            fam[f.split(":")[0]] += 1
    models = {a["model"] for a in executed}
    p["CHEAP_MODEL_FAILURES"] = [{"family": k, "count": v} for k, v in fam.most_common()]
    # best failed candidate: zero false-commits first, then holdout accuracy
    # A candidate that errors everywhere has 0 false-commits trivially; require some accuracy first.
    scored = [a for a in fails if a.get("holdout_acc") is not None and a["holdout_acc"] > 0]
    if scored:
        best = sorted(scored, key=lambda a: (a["holdout_acc"], (a.get("boundary_false_commit") or 0) == 0), reverse=True)[0]
        p["BEST_FAILED_CANDIDATE"] = {"attempt": best["n"], "model": best["model"], "holdout_acc": best["holdout_acc"],
                                      "boundary_false_commit": best.get("boundary_false_commit"),
                                      "failure_families": best.get("failure_families"), "file": best.get("file")}
    # knockout: for the harness, 'knockout' of the candidate op == abstention == the current registry's behaviour.
    p["KNOCKOUT_RESULTS"] = [{"note": "Baseline (no op) = Apollo's current behaviour: abstain on every item; accuracy_decidable 0.0. "
                                      "Any candidate's holdout accuracy is therefore its own knockout delta.",
                              "n_executed_attempts": len(executed), "n_pass_dev": len(passes)}]
    p["PRIORITY"]["dimensions"].update({
        "cheap_search_exhaustion": round(min(1.0, len(executed) / max(EXHAUST_MIN_ATTEMPTS, 1)), 2),
        "distinct_models": len(models), "distinct_failure_families": len(fam),
    })
    # ── Addendum 3 guards ─────────────────────────────────────────────────────────────────
    # (1) Closure before Apprentice: nothing enters APPRENTICE-TESTING / smith states unless the
    #     closure gauntlet classified the wall OPERATOR (or recorded that no typed spec is
    #     constructible, with the reason). SEARCH_ROUTING / REPRESENTATION are routed out.
    route = str(p.get("ROUTE_CLASS") or "")
    if p["STATUS"] in ("OBSERVED", "TRIAGE", "COMPOSITION-SUSPECTED", "EXPRESSIVITY-SUSPECTED"):
        if route.startswith("SEARCH_ROUTING") or route.startswith("REPRESENTATION"):
            P.set_status(p, "DORMANT", f"closure gauntlet: {route}; routed out of the mint path (Addendum 3)")
            p["_meta"]["routing"] = route.split()[0].lower()
    # (2) Unverified mechanism coverage never advances a candidate (Q6).
    def _promotable(a):
        return str(a.get("verdict", "")) in ("PASS_DEV", "PASS_DEV_WITH_UNTESTED_COMPONENT")
    # transitions
    if p["STATUS"] == "APPRENTICE-TESTING" and not (route == "OPERATOR" or p.get("CLOSURE_TEST") in (None, [], {}) and "not constructible" in str(p.get("ROUTE_CLASS"))):
        P.set_status(p, "TRIAGE", "Addendum 3: closure gauntlet must classify the wall OPERATOR before apprentice exploration")
    if p["STATUS"] == "APPRENTICE-TESTING":
        promotable = [a for a in passes if _promotable(a)]
        if passes and not promotable:
            P.log_event(mint, "blocked_promotion", reason="PASS_DEV_UNVERIFIED_COVERAGE does not advance state (Addendum 3, Q6)")
        if promotable:
            P.set_status(p, "CANDIDATE-PRODUCED", f"attempt {promotable[0]['n']} ({promotable[0]['model']}) passed dev with verified coverage; NOT admitted; independent eval required")
        elif len(executed) >= EXHAUST_MIN_ATTEMPTS and len(models) >= EXHAUST_MIN_MODELS and len(fam) >= EXHAUST_MIN_FAMILIES:
            P.set_status(p, "APPRENTICE-EXHAUSTED",
                         f"{len(executed)} executed attempts across {len(models)} cheap models, {len(fam)} failure families, no dev pass")
    if p["STATUS"] == "APPRENTICE-EXHAUSTED":
        missing = P.missing_for_ready(p)
        if not missing:
            P.set_status(p, "READY-FOR-DEEP-MINT", "packet complete; apprentice exhausted; awaiting OPERATOR invocation (charter §3/§20)")
        else:
            P.log_event(mint, "not_ready", missing=missing)
    P.log_event(mint, "refined", executed=len(executed), models=sorted(models), families=dict(fam))
    return p


def main() -> None:
    for p in P.iter_packets():
        if p["STATUS"] not in P.UNRESOLVED:
            continue
        before = p["STATUS"]
        p = refine_packet(p)
        P.save(p)
        print(p["MINT_ID"], before, "->", p["STATUS"], "| failures:", json.dumps(p["CHEAP_MODEL_FAILURES"]))


if __name__ == "__main__":
    main()
