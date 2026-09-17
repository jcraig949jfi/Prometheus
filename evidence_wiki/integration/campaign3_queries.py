"""Order s18: factual questions over the ingested Campaign 3, answered through
the READ API only (no SQL), each with the evidence rows it reads. PEW
answers WHICH / WHEN / HOW MANY; it does not answer WHY.

    python integration/campaign3_queries.py --machine M2
Writes integration/campaign3_queries_results.json.
"""
import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent.parent
A = {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8377)
    ap.add_argument("--machine", default="M2")
    a = ap.parse_args()
    cfg = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
    tok = cfg["machine_tokens"].get(a.machine) or cfg["auth_token"]
    base = f"http://{a.host}:{a.port}/api/v1"
    h = {"Authorization": f"Bearer {tok}", "X-Prometheus-Machine": a.machine, "X-Prometheus-Agent": "campaign3-queries"}

    def obs(**kw):
        kw.setdefault("limit", 2000)
        r = requests.get(f"{base}/campaign/observations", headers=h, params=kw, timeout=120)
        r.raise_for_status()
        return r.json()["observations"]

    # Q1 which measurements support the delay-invariance projection?
    runs = obs(harness_id="C3-SFE-03", kind="run", attempt_id="C3-SFE-03/a05")
    gen = [r for r in runs if (r["measured"].get("general_survives") is True) or (r["measured"].get("general_heldout") or 0) >= 1.0]
    A["Q1_delay_invariance_measurements"] = {
        "question": "which measurements support the delay-invariance projection?",
        "runs_of_record": len(runs), "runs_general_on_trained_delays": len(gen),
        "fields_read": ["general_heldout", "general_gen", "general_gen_ladder", "heldout_by_rung", "rung_at_general", "general_survives"],
        "per_seed": [{"seed": r["seed"], "general_gen": r["measured"].get("general_gen"), "rung_at_general": r["measured"].get("rung_at_general"),
                      "general_heldout": r["measured"].get("general_heldout"), "heldout_by_rung": r["measured"].get("heldout_by_rung")} for r in runs],
        "evidence_ids": [r["observation_id"] for r in runs],
        "not_answered_here": "why the ladder produces invariance (analysis, Archaeon)"}
    # unseen delays d8/d16: C3-SFE-04 rows carry target/family
    r04 = obs(harness_id="C3-SFE-04", kind="run")
    unseen = [r for r in r04 if str(r["measured"].get("target", "")).startswith("W1_d8") or str(r["measured"].get("target", "")).startswith("W1_d16")]
    A["Q1b_unseen_delay_measurements"] = {
        "runs_at_d8_or_d16": len(unseen),
        "by_family_target": dict(Counter(f"{r['measured'].get('family')}->{r['measured'].get('target')}" for r in unseen)),
        "heldout_by_family_target": {k: [r["measured"].get("competence_heldout") for r in unseen if f"{r['measured'].get('family')}->{r['measured'].get('target')}" == k][:12]
                                     for k in set(f"{r['measured'].get('family')}->{r['measured'].get('target')}" for r in unseen)},
        "evidence_ids": [r["observation_id"] for r in unseen][:50]}

    # Q2 which evidence shows the organism was present before delay-1 selection?
    A["Q2_present_before_delay1_selection"] = {
        "question": "which evidence shows the organism promoted at delay 1 was already present?",
        "fields_read": ["hold_released_by", "rung_at_general", "general_gen", "general_gen_ladder", "reached_r0_by_rung_end", "p_switched_at"],
        "per_seed": [{"seed": r["seed"], "hold_released_by": r["measured"].get("hold_released_by"), "rung_at_general": r["measured"].get("rung_at_general"),
                      "general_gen": r["measured"].get("general_gen"), "general_gen_ladder": r["measured"].get("general_gen_ladder"),
                      "reached_r0_by_rung_end": r["measured"].get("reached_r0_by_rung_end")} for r in runs],
        "evidence_ids": [r["observation_id"] for r in runs],
        "note": "PEW carries the producer's per-run fields; 'already present' is the analyst's reading of rung_at_general == 1 with general_gen at the ladder release"}

    # Q3 mature vs incompetent imports; realized dose
    r10 = obs(harness_id="C3-SFE-10", kind="run", limit=2000)
    tab = Counter((r["strata"].get("quality"), str(r["strata"].get("dose")), str(r["strata"].get("n_imported")), str(r["strata"].get("cap"))) for r in r10)
    A["Q3_imports_mature_vs_control_and_realized_dose"] = {
        "question": "which runs used mature versus incompetent imports, and what was the realized dose?",
        "runs": len(r10), "quality_counts": dict(Counter(r["strata"].get("quality") for r in r10)),
        "intended_vs_realized_dose": [{"quality": q, "dose_intended": d, "dose_realized": n, "cap": c, "runs": k} for (q, d, n, c), k in sorted(tab.items(), key=lambda t: str(t[0]))],
        "intended_equals_realized_in_every_run": all(str(r["strata"].get("dose")) == str(r["strata"].get("n_imported")) for r in r10),
        "import_share_final_by_quality": {q: sorted({round(r["measured"].get("import_share_final") or 0, 3) for r in r10 if r["strata"].get("quality") == q})[:6]
                                          for q in set(r["strata"].get("quality") for r in r10)},
        "evidence_ids": [r["observation_id"] for r in r10][:50],
        "not_answered_here": "whether an import 'worked' (takeover_v1 is not built; capability benefit is a separate measurement)"}

    # Q4 which runs were censored?
    cens = obs(kind="reachability", campaign_id="cmp3", limit=2000)
    by_h = Counter((r["harness_id"], bool(r["summit_censored"])) for r in cens)
    A["Q4_censored_runs"] = {
        "question": "which runs were censored before a confirmed summit?",
        "cmp3_reachability_rows": len(cens), "censored": sum(1 for r in cens if r["summit_censored"]),
        "by_harness": {f"{k[0]}": {"censored": by_h.get((k[0], True), 0), "not_censored": by_h.get((k[0], False), 0)} for k in {(x[0], True) for x in by_h} | {(x[0], False) for x in by_h}},
        "horizons_G": sorted({r["g_budget"] for r in cens}),
        "example_evidence_ids": [r["observation_id"] for r in cens if r["summit_censored"]][:20]}

    # Q5 which basin measurements belong to each stratum?
    r06 = obs(harness_id="C3-SFE-06", kind="run", limit=2000)
    strata = Counter((r["strata"].get("table"), r["strata"].get("climber")) for r in r06)
    A["Q5_basin_measurements_by_stratum"] = {
        "question": "which basin measurements belong to each stratum?",
        "runs": len(r06), "strata": [{"table": t, "climber": c, "runs": n} for (t, c), n in sorted(strata.items(), key=str)],
        "fields_read": ["basin_share", "deceptive_share", "median_first_hit", "table", "climber", "encoding"],
        "within_stratum_example": {f"{t}/{c}": [{"encoding": r["measured"].get("encoding"), "basin_share": r["measured"].get("basin_share"),
                                                "median_first_hit": r["measured"].get("median_first_hit")} for r in r06
                                               if (r["strata"].get("table"), r["strata"].get("climber")) == (t, c)][:3]
                                   for (t, c) in strata},
        "evidence_ids": [r["observation_id"] for r in r06][:50],
        "not_answered_here": "the pooled-vs-stratified rank correlation itself (analysis; D3-021/L3-029)"}

    # Q6 which projections changed definition/version?
    pr = requests.get(f"{base}/projections", headers=h, timeout=60).json()["projections"]
    A["Q6_projection_versions"] = {
        "question": "which projections changed definition or version?",
        "registry": [{"name": p["projection_name"], "version": p["projection_version"], "status": p["status"],
                      "thresholds": p["thresholds"], "code_identity": p["source_code_identity"], "rebuild_digest": p["rebuild_digest"]} for p in pr]}
    v0 = requests.get(f"{base}/projections/reach_level/v0", headers=h, params={"row_key_prefix": "obs:", "limit": 5000}, timeout=120).json()["rows"]
    v1 = {r["row_key"]: r for r in requests.get(f"{base}/projections/reach_level/v1", headers=h, params={"row_key_prefix": "obs:", "limit": 5000}, timeout=120).json()["rows"]}
    xt = Counter((r["payload"]["level_v0"], v1[r["row_key"]]["payload"]["level_as_written"]) for r in v0 if r["row_key"] in v1)
    A["Q6b_v0_vs_v1_same_rows"] = {"cross_tab_v0_v1": [{"v0": k[0], "v1": k[1], "rows": n} for k, n in sorted(xt.items())],
                                   "training_only_full_solves_not_confirmed_in_v1": sum(1 for r in v0 if r["payload"]["training_only_full_solve_not_confirmed_in_v1"])}

    # Q7 instrument failures / restarts / successful resume (attempts)
    att = obs(campaign_id="cmp3", kind="attempt", limit=2000)
    A["Q7_attempts_resumes"] = {
        "attempts": len(att), "resumed": [{"attempt_id": r["attempt_id"], "resumed_from": r["resumed_from_attempt"], "replayed_steps": r["measured"].get("replayed_steps")}
                                          for r in att if r["resumed_from_attempt"] is not None],
        "dispositions_candidate": dict(Counter(str(r["measured"].get("disposition_candidate")) for r in att if r["measured"].get("of_record")))}

    out = {"ran_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "service": base, "answers": A}
    (HERE / "integration" / "campaign3_queries_results.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    for k, v in A.items():
        short = {kk: vv for kk, vv in v.items() if kk not in ("per_seed", "evidence_ids", "example_evidence_ids", "within_stratum_example", "heldout_by_family_target", "registry", "fields_read")}
        print(k, json.dumps(short, default=str)[:600])
    return 0


if __name__ == "__main__":
    sys.exit(main())
