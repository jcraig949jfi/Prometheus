"""H5 alpha on eca_rule_eval_v1 (Track C).

Vivarium's kind reports the OBSERVABLE (terminal-behaviour digest and the
equivalence class at the payload's scope), never a score. That fixes what
the H5 alpha on this kind is: ONE exhaustive campaign of the 256 rules at
the fixture scope (7-ring, 8 steps) establishes the rule -> class map on
the live consumer; every H5 quantity (reach, neutrality, accessible
variation per decoder, the direct-vs-permuted access gap) is then exact
producer-side arithmetic over that live map (archaeon/producer/h5_reference,
h5_decoders), collapsed to classes. Nothing adaptive; a decoder is applied
to genomes offline and the phenotype is a rule number.

Not issued without the operator's word. 256 rows, one observation each.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from typing import Any, Dict, List, Optional, Sequence

from . import specbuild

KIND = "eca_rule_eval_v1"
CAMPAIGN_ID = "H5-1"
SEED_ROOT = 950_001
N_CELLS = 7
STEPS = 8
SCOPE = "terminal behaviour at {} steps on the {}-ring".format(STEPS, N_CELLS)


def spec_for(rule: int) -> Dict[str, Any]:
    return {"spec_version": 3, "world": {"seed_root": SEED_ROOT},
            "hypothesis": "rule {} at the fixture scope: the live consumer reproduces the published class".format(rule),
            "prediction": None,
            "work": {"kind": KIND, "payload": {"rule_number": rule, "n_cells": N_CELLS, "steps": STEPS}},
            "outcome_rule": {"field": "on_fixture_scope", "op": "==", "value": True,
                             "if_true": "SURVIVED", "if_false": "FALSIFIED",
                             "if_indeterminate": "INCONCLUSIVE", "aggregate": "first"},
            "pew": {"required": True,
                    "encounter_id": "ENC-archaeon-h5-" + hashlib.sha256("{}|{}|{}|{}".format(rule, N_CELLS, STEPS, SEED_ROOT).encode()).hexdigest()[:16],
                    "players": []},
            "repeat": {"count": 1, "order": "sequential", "seed_derivation": "constant",
                       "state": "reset", "budget": {"max_seconds": 120, "max_observations": 1}}}


def plan() -> List[Dict[str, Any]]:
    return [{"index": r + 1, "family_id": "fam-H5-1", "arm_id": "map", "rule": r, "label": "rule_{:03d}".format(r),
             "request_key": "{}-{:03d}".format(CAMPAIGN_ID, r), "spec": spec_for(r)} for r in range(256)]


def check(rows: Optional[Sequence[Dict[str, Any]]] = None) -> Dict[str, Any]:
    rows = rows or plan()
    out: Dict[str, Any] = {"campaign": CAMPAIGN_ID, "rows": len(rows), "scope": SCOPE, "kind_registered": None,
                           "invalid": [], "blockers": []}
    from .contract import ensure_viv_importable
    ensure_viv_importable()
    from viv import kinds as vk
    k = vk.get(KIND)
    out["kind_registered"] = bool(k and k.implemented)
    if not out["kind_registered"]:
        out["blockers"].append({"lane": "vivarium", "what": "eca_rule_eval_v1 is not registered in this tree"})
        return out
    for r in rows:
        try:
            specbuild.validate(r["spec"])
        except specbuild.SpecInvalid as exc:
            out["invalid"].append({"index": r["index"], "reason": str(exc)[:240]})
    from viv import executors as X
    ran, refused = {}, {}
    for r in (rows[0], rows[90], rows[255]):            # rule 0, rule 90, rule 255 executed offline
        try:
            o = X.run(r["spec"], seed=0)
            ran[r["label"]] = {"class_size": o.get("equivalence_class_size"), "on_fixture_scope": o.get("on_fixture_scope"),
                               "fixture_class_agrees": o.get("fixture_class_agrees")}
        except Exception as exc:                                 # noqa: BLE001
            refused[r["label"]] = "{}: {}".format(type(exc).__name__, str(exc)[:200])
    out["executor_preflight"] = {"ran": ran, "refused": refused}
    if out["invalid"]:
        out["blockers"].append({"lane": "archaeon", "what": "specs rejected by Vivarium's validator", "n": len(out["invalid"])})
    if refused:
        out["blockers"].append({"lane": "archaeon", "what": "executor refuses a payload", "detail": refused})
    out["ok_to_issue"] = not out["invalid"] and not refused
    return out


def live_class_map(results: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
    """From 256 live results, the rule -> class map (class id = smallest
    member, as the fixture), compared with the published fixture."""
    from . import h5_reference as R
    by_digest: Dict[str, List[int]] = {}
    for rule, res in results.items():
        by_digest.setdefault(res["behaviour_digest"], []).append(rule)
    live = {}
    for members in by_digest.values():
        cid = min(members)
        for m in members:
            live[m] = cid
    published = R.load_class_map()["equivalence"]
    return {"n_rules": len(live), "n_classes": len(set(live.values())), "equivalence": live,
            "agrees_with_published": live == published if len(live) == 256 else None,
            "disagreements": sorted(r for r in live if published.get(r) != live[r]),
            "scope": SCOPE}


def h5_readout(equivalence: Dict[int, int], instruments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """The H5 quantities, exact, collapsed to the (live) classes.

    `instruments`: outside decoders loaded from table artifacts
    (h5_decoders.load_table_decoder), reported under out["instruments"] in a
    SEPARATE block with their scrambled twin beside each -- an instrument row
    (a hand-designed structured decoder) is never evidence for learned
    evolvability (design v0.1 s5). Contract: Polyhymnia #67 reply."""
    from . import h5_decoders as H
    from . import h5_reference as R
    decs = {"direct": H.direct, "balanced_7": H.make_balanced(7), "scrambled_direct_3": H.make_scrambled(H.direct, 3)}
    out: Dict[str, Any] = {}
    if instruments:
        out["instruments"] = {}
        for name, dec in instruments.items():
            block = {}
            for sub, dd in (("member", dec), ("scrambled_3", H.make_scrambled(dec, 3))):
                raw = R.exact_reference(dd); col = R.exact_reference(dd, equivalence=equivalence)
                block[sub] = {"mean_reach_rules": raw["mean_reach"], "mean_reach_classes": col["mean_reach"],
                              "max_reach_classes": col["max_reach"], "mean_neutral": raw.get("mean_neutral")}
            block["structure_gain_classes"] = block["member"]["mean_reach_classes"] - block["scrambled_3"]["mean_reach_classes"]
            block["drop_rule"] = "DROPPED from the readout if structure_gain_classes <= 0 on the live map (the structure adds no class-reach beyond its multiplicity histogram)"
            block["table_sha256"] = getattr(dec, "table_sha256", None); block["decoder_id"] = getattr(dec, "decoder_id", name)
            out["instruments"][name] = block
    for name, dec in decs.items():
        raw = R.exact_reference(dec)
        col = R.exact_reference(dec, equivalence=equivalence)
        out[name] = {"mean_reach_rules": raw["mean_reach"], "mean_reach_classes": col["mean_reach"],
                     "max_reach_rules": raw["max_reach"], "max_reach_classes": col["max_reach"],
                     "mean_neutral": raw.get("mean_neutral"), "digest_classes": col["reference_digest"]}
    out["construction_fact"] = "direct reach <= 8 and permuted up to 12 is analytic; only the excess over that bound is evidence (Harmonia)"
    out["scope"] = SCOPE
    return out


def issue(conn, rows: Optional[Sequence[Dict[str, Any]]] = None, config=None) -> Dict[str, Any]:
    """Human path on the registered candidate-set route (execution-only
    check, negative-authority check, one transaction per row). Operator
    2026-09-10 (F-19): ISSUE NOW."""
    from .. import config as cfg
    from .. import vivqueue as vq
    from . import costs as C
    rows = list(rows or plan()); config = config or cfg.DEFAULT
    c = check(rows)
    if not c.get("ok_to_issue"):
        raise RuntimeError("H5-1 does not validate: {}".format(c["blockers"] or c["invalid"]))
    csid = "cs-h5-1"
    ids = []
    with C.Meter() as m:
        for r in rows:
            cand = vq.make_candidate(r["spec"], family_id=r["family_id"], arm_id=r["arm_id"], request_key=r["request_key"],
                                     source_evidence={"schema": "archaeon.campaign.v0", "campaign": CAMPAIGN_ID, "mode": "human",
                                                      "policy_version": "campaign.H5.v0", "template_id": "campaign.H5-1",
                                                      "label": r["label"], "rule": r["rule"], "scope": SCOPE,
                                                      "selection_basis": "operator_directed_family",
                                                      "authority": "H5 alpha: the exhaustive 256-rule map at the fixture scope on the live "
                                                                   "consumer; every H5 quantity is producer-side arithmetic over it",
                                                      "upstream_selection_history": "UNKNOWN",
                                                      vq.CAMPAIGN_SET_KEY: csid})
            # Every member executes: NOT a candidate set (Vivarium #181 item 4), so no
            # candidate_set_id; the campaign grouping rides in source_evidence.campaign_set.
            res = vq.submit(conn, candidates=[cand], selected_index=0, source_reason="human",
                            created_by="archaeon", config=config)
            ids.append(res["selected_experiment_id"])
    cost = C.CostEvent("generation", csid, m.resources([C.Resource("items", len(ids), "count", "count", "measured")]), output_refs=ids)
    return {"campaign": CAMPAIGN_ID, "candidate_set_id": csid, "experiment_ids": ids, "registered": len(ids),
            "cost_event": cost.to_json(), "engine_entries": C.to_engine_entries(cost, scope="campaign")}


TRANSPORT_MARKERS = ("timed out", "ENGINE_TRANSPORT", "HTTP 500", "handshake")


def failed_transport_labels(conn, csid: str = "cs-h5-1") -> Dict[str, List[str]]:
    """Failed rows of the set, split into transport failures (reissuable:
    the spec never ran or its result never came back) and everything else
    (a producer or engine-semantics error, never reissued blind)."""
    cur = conn.cursor()
    from .. import vivqueue as vq
    cur.execute("select request_key, error from viv.research_experiment_queue where " + vq.campaign_rows_filter() + " and status='failed'", (csid, csid))
    by_key = {r["request_key"]: r["label"] for r in plan()}
    out = {"transport": [], "other": [], "unknown_keys": []}
    for key, err in cur.fetchall():
        label = by_key.get(key.split("-R")[0])
        if label is None:
            out["unknown_keys"].append(key); continue
        out["transport" if any(m in (err or "") for m in TRANSPORT_MARKERS) else "other"].append(label)
    for k in out:
        out[k] = sorted(set(out[k]))
    return out


def plan_reissue(labels: Sequence[str], suffix: str = "R1") -> List[Dict[str, Any]]:
    """Pure: the plan rows for `labels` with a suffixed request key and the
    reissue provenance attached; spec and hash unchanged."""
    rows = [r for r in plan() if r["label"] in set(labels)]
    missing = sorted(set(labels) - {r["label"] for r in rows})
    if missing:
        raise RuntimeError("labels not in the plan: {}".format(missing))
    out = []
    for r in rows:
        r = dict(r)
        r["reissue_of_request_key"] = r["request_key"]
        r["request_key"] = "{}-{}".format(r["request_key"], suffix)
        out.append(r)
    return out


def reissue(conn, labels: Sequence[str], suffix: str = "R1", config=None) -> Dict[str, Any]:
    """Re-issue TRANSPORT-failed rows under a new request key and candidate
    set cs-h5-1-<suffix>; the failed rows stay as their own record (C3
    precedent, campaign_c3.reissue). Never call on a producer error."""
    from .. import config as cfg
    from .. import vivqueue as vq
    config = config or cfg.DEFAULT
    rows = plan_reissue(labels, suffix)
    csid = "cs-h5-1-" + suffix.lower()
    ids = []
    for r in rows:
        cand = vq.make_candidate(r["spec"], family_id=r["family_id"], arm_id=r["arm_id"], request_key=r["request_key"],
                                 source_evidence={"schema": "archaeon.campaign.v0", "campaign": CAMPAIGN_ID, "mode": "human",
                                                  "policy_version": "campaign.H5.v0", "template_id": "campaign.H5-1",
                                                  "label": r["label"], "rule": r["rule"], "scope": SCOPE,
                                                  "reissue_of_request_key": r["reissue_of_request_key"],
                                                  "reissue_reason": "ENGINE_TRANSPORT / HTTP 500 failure on the first attempt; same spec, same hash",
                                                  "selection_basis": "operator_directed_family",
                                                  "authority": "re-attempt of a transport-failed row of the operator-issued H5-1 (F-19)",
                                                  "upstream_selection_history": "UNKNOWN",
                                                  vq.CAMPAIGN_SET_KEY: csid})
        res = vq.submit(conn, candidates=[cand], selected_index=0, source_reason="human",
                        created_by="archaeon", config=config)
        ids.append(res["selected_experiment_id"])
    return {"campaign": CAMPAIGN_ID, "candidate_set_id": csid, "experiment_ids": ids, "labels": list(labels)}


def completed_results(conn, sets: Sequence[str] = ("cs-h5-1", "cs-h5-1-r1")) -> Dict[str, Any]:
    """The 256 live results, one per rule, from the completed rows of the
    campaign and its reissues. When a rule has more than one completed row
    (a first attempt AND a reissue both completed) the rows are checked for
    the same spec_hash and the same behaviour_digest, and the EARLIEST
    completed row is the one read; every rule records which attempt it came
    from. Rows are matched in both shapes (candidate_set_id, or
    source_evidence.campaign_set after 2026-09-11 evening)."""
    from .. import vivqueue as vq
    cur = conn.cursor()
    cur.execute("SELECT request_key, spec_hash, source_evidence->>'rule', result_summary->'result'->'repeats'->0->'result', "
                "finished_at, COALESCE(candidate_set_id, source_evidence->>'campaign_set') "
                "FROM viv.research_experiment_queue WHERE (candidate_set_id = ANY(%s) OR source_evidence->>'campaign_set' = ANY(%s)) "
                "AND status = 'completed' ORDER BY finished_at", (list(sets), list(sets)))
    by_rule: Dict[int, List[Dict[str, Any]]] = {}
    for rk, sh, rule, res, fin, cs in cur.fetchall():
        by_rule.setdefault(int(rule), []).append({"request_key": rk, "spec_hash": sh, "result": res, "finished_at": str(fin), "set": cs})
    results, attempts, conflicts = {}, {}, []
    for rule, rows in sorted(by_rule.items()):
        first = rows[0]
        for other in rows[1:]:
            if other["spec_hash"] != first["spec_hash"] or other["result"]["behaviour_digest"] != first["result"]["behaviour_digest"]:
                conflicts.append({"rule": rule, "rows": [r["request_key"] for r in rows]})
        results[rule] = first["result"]
        attempts[rule] = {"read": first["request_key"], "also_completed": [r["request_key"] for r in rows[1:]], "set": first["set"]}
    missing = sorted(set(range(256)) - set(results))
    return {"results": results, "attempts": attempts, "missing_rules": missing, "conflicts": conflicts,
            "n_completed_rows": sum(len(v) for v in by_rule.values())}


def full_readout(conn, instruments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """F-24 / ARCH-28: the 256-rule readout. Refuses to compute the H5
    quantities on a partial map (wrong-population rule); reports the attempt
    read per rule and the first attempts that stay failed on the record."""
    import datetime as _dt
    got = completed_results(conn)
    out: Dict[str, Any] = {"schema": "archaeon.h5.readout.v1", "campaign": CAMPAIGN_ID, "sets_read": ["cs-h5-1", "cs-h5-1-r1"],
                           "generated_at": _dt.datetime.now(_dt.timezone.utc).isoformat(), "scope": SCOPE,
                           "n_completed_rows": got["n_completed_rows"], "missing_rules": got["missing_rules"],
                           "conflicts": got["conflicts"], "attempts": {str(k): v for k, v in got["attempts"].items()}}
    if got["missing_rules"] or got["conflicts"]:
        out["status"] = "INCOMPLETE"
        out["note"] = "H5 quantities NOT computed: a partial or inconsistent map is a different population from the 256-rule fixture"
        return out
    lm = live_class_map(got["results"])
    out["status"] = "COMPLETE"
    out["live_class_map"] = {k: v for k, v in lm.items() if k != "equivalence"}
    out["equivalence"] = {str(k): v for k, v in sorted(lm["equivalence"].items())}
    out["h5"] = h5_readout(lm["equivalence"], instruments=instruments)
    from . import h5_reference as R
    pub = R.load_class_map()["equivalence"]
    out["published_map"] = {"n_classes": len(set(pub.values())), "agrees": lm["agrees_with_published"], "disagreements": lm["disagreements"]}
    out["h5_on_published_map"] = h5_readout(pub) if not lm["agrees_with_published"] else "identical to h5 (maps agree)"
    return out


def main(argv=None) -> int:
    from .. import workspace as _ws
    _ws.assert_not_canonical("run a campaign CLI")               # D-23
    ap = argparse.ArgumentParser(prog="archaeon.producer.campaign_h5")
    ap.add_argument("--check", action="store_true"); ap.add_argument("--issue", action="store_true")
    ap.add_argument("--reissue-transport", action="store_true", help="re-issue the transport-failed rows of cs-h5-1 under suffix")
    ap.add_argument("--suffix", default="R1")
    ap.add_argument("--readout", action="store_true", help="the 256-rule readout from the completed rows (F-24)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    if a.readout:
        from evidence_wiki.ew import db as ewdb
        conn = ewdb.connect()
        try:
            r = full_readout(conn)
        finally:
            conn.close()
        text = json.dumps(r, indent=1, default=str)
        if a.out:
            from pathlib import Path as _P
            _P(a.out).write_text(text, encoding="utf-8")
        print(text if not a.out else json.dumps({k: r[k] for k in ("status", "n_completed_rows", "missing_rules", "conflicts", "live_class_map", "published_map") if k in r}, indent=1, default=str))
        return 0
    if a.reissue_transport:
        from evidence_wiki.ew import db as ewdb
        conn = ewdb.connect()
        try:
            split = failed_transport_labels(conn)
            print(json.dumps({"split": split}, indent=1))
            if split["transport"]:
                print(json.dumps(reissue(conn, split["transport"], a.suffix), indent=1, default=str))
        finally:
            conn.close()
        return 0
    if a.check:
        print(json.dumps(check(), indent=1, default=str)); return 0
    if a.issue:
        from evidence_wiki.ew import db as ewdb
        conn = ewdb.connect()
        try:
            print(json.dumps(issue(conn), indent=2, default=str))
        finally:
            conn.close()
        return 0
    ap.print_help(); return 1


if __name__ == "__main__":
    raise SystemExit(main())
