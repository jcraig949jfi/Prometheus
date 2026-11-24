"""Phase 3 — 3-Generation Compounding Runner (`A2_PRIOR -> G1 -> G2 -> G3` + Selective Knockout + Full-Budget SHAM).

Supports BOTH tracks under identical pre-registered Claim 2 & Claim 3 protocol:
  - `--track s3a`: 7..9-input Hard Multi-Output XAG (80 tasks: 30 expanding dev + 10 hidden dev_val + 40 untouched holdout)
  - `--track s3b`: 16-bit Multi-Stage Hard Z3 UNSAT BV (56 tasks: 18 expanding dev + 10 hidden dev_val + 28 untouched holdout)

Evaluates ALL frozen generational snapshots (`A0_BASE`, `A1_INDUSTRY`, `A2_PRIOR_ONLY`, `A3_ZERO_LLM`,
`G1`, `G2`, `G3`, `A5_SHAM`) on the **EXACT SAME untouched final holdout** at the **EXACT SAME per-task
wall-clock cap** across 3 paired seeds `{0, 1, 2}`, verified by the hardened 3-seed RSO reducer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from comp_sprint.industry_abc import synthesize_with_abc
from comp_sprint.llm_proposer import call_claude_isolated
from comp_sprint.meter import WorkMeter
from comp_sprint2.reducer_s2 import compute_summary, make_row, verify_and_reduce
from comp_sprint2.s2a_engine import (
    build_s2a_a3_artifact,
    build_s2a_a5_sham_artifact,
    synthesize_s2a_with_artifact,
)
from comp_sprint2.s2b_bv import simplify_bv_with_z3_industry
from comp_sprint2.s2b_engine import (
    build_s2b_a3_artifact,
    build_s2b_a5_sham_artifact,
    optimize_s2b_with_artifact,
)
from comp_sprint2.s3a_benchmarks import build_s3a_benchmarks, s3a_manifest_sha256
from comp_sprint2.s3b_benchmarks import build_s3b_benchmarks, s3b_manifest_sha256
from comp_sprint2.sandbox_exec import AlgoArtifact, AlgoPass
from comp_sprint2.sprint2_runner import (
    S2A_SPEC_BLOCK,
    S2B_SPEC_BLOCK,
    _parse_passes,
    _prompt_hash,
    _summarize_pass_telemetry,
)


STRICT_JSON_SYSTEM_PROMPT = (
    "You are a pure JSON algorithm synthesizer with NO tools and NO filesystem access. "
    "Return ONLY one valid JSON object matching the exact schema requested. "
    "NEVER output prose, apologies, or simulated tool calls (such as Grep, Bash, Read)."
)


def _track_cfg(track: str) -> Dict[str, Any]:
    if track == "s3a":
        suites = build_s3a_benchmarks()
        return {
            "track": "s3a",
            "base_kind": "s2a",
            "track_tag": "S3A_XAG",
            "suites": suites,
            "manifest_sha": s3a_manifest_sha256(suites),
            "gen_slices": (
                suites["s3a_dev_g1"],
                suites["s3a_dev_g1"] + suites["s3a_dev_g2"],
                suites["s3a_dev_g1"] + suites["s3a_dev_g2"] + suites["s3a_dev_g3"],
            ),
            "dev_val": suites["s3a_dev_val"],
            "hold_suites": ("s3a_hold_struct", "s3a_hold_proc_shared", "s3a_hold_proc_comp"),
            "eval_suites": ("s3a_dev_val", "s3a_hold_struct", "s3a_hold_proc_shared", "s3a_hold_proc_comp"),
            "spec_block": S2A_SPEC_BLOCK,
            "time_budget": 0.60,
            "industry_arm": "A1_ABC_XAG",
            "a3_art": build_s2a_a3_artifact(),
            "a5_art": build_s2a_a5_sham_artifact(),
        }
    if track == "s3b":
        suites = build_s3b_benchmarks()
        # Partition 28 dev tasks cleanly: 18 expanding train (6 G1 -> 12 G2 -> 18 G3) + 10 hidden dev_val ([9..13] x 2)
        ds, dp = suites["s3b_dev_struct"], suites["s3b_dev_proc"]
        g1 = ds[:3] + dp[:3]
        g2 = ds[:6] + dp[:6]
        g3 = ds[:9] + dp[:9]
        dval = ds[9:] + dp[9:]
        return {
            "track": "s3b",
            "base_kind": "s2b",
            "track_tag": "S3B_BV",
            "suites": suites,
            "manifest_sha": s3b_manifest_sha256(suites),
            "gen_slices": (g1, g2, g3),
            "dev_val": dval,
            "hold_suites": ("s3b_hold_struct", "s3b_hold_proc"),
            "eval_suites": ("s3b_dev_struct", "s3b_dev_proc", "s3b_hold_struct", "s3b_hold_proc"),
            "spec_block": S2B_SPEC_BLOCK,
            "time_budget": 0.80,
            "industry_arm": "A1_Z3_SIMPLIFY",
            "a3_art": build_s2b_a3_artifact(),
            "a5_art": build_s2b_a5_sham_artifact(),
        }
    raise ValueError(f"Unknown track {track!r}")


def _eval_one(base_kind: str, task: Any, art: AlgoArtifact | None, seed: int, tb: float) -> Tuple[int, str, Dict[str, Any]]:
    if base_kind == "s2a":
        c, meta = synthesize_s2a_with_artifact(task.n_inputs, task.targets, artifact=art, seed=seed, time_budget_sec=tb)
        return c.gate_count(), c.sha256(), meta
    p, meta = optimize_s2b_with_artifact(task.spec, artifact=art, seed=seed, time_budget_sec=tb)
    return p.op_count(), p.sha256(), meta


def _eval_ind(base_kind: str, task: Any) -> Tuple[int, str]:
    if base_kind == "s2a":
        cx = synthesize_with_abc(task.n_inputs, task.targets)["xag"]
        return cx.gate_count(), cx.sha256()
    p = simplify_bv_with_z3_industry(task.spec)
    return p.op_count(), p.sha256()


def _eval_list(base_kind: str, tasks: Sequence[Any], art: AlgoArtifact | None, tb: float) -> Tuple[int, Dict[str, int], Dict[str, List[Dict[str, Any]]]]:
    scores: Dict[str, int] = {}
    pstats: Dict[str, List[Dict[str, Any]]] = {}
    for t in tasks:
        c, _sha, meta = _eval_one(base_kind, t, art, seed=0, tb=tb)
        scores[t.task_id] = c
        pstats[t.task_id] = meta.get("pass_stats", [])
    return sum(scores.values()), scores, pstats


def _select_generation(
    base_kind: str,
    track_tag: str,
    gen_num: int,
    parent_art: AlgoArtifact,
    cand_passes: Sequence[AlgoPass],
    train_tasks: Sequence[Any],
    val_tasks: Sequence[Any],
    tb: float,
    max_total_passes: int,
) -> Tuple[AlgoArtifact, int, int, List[str]]:
    """Strict monotonic hidden-`dev_val` selection for generation `gen_num` at identical wall-clock cap `tb`."""
    cur_passes = list(parent_art.passes)
    arm_name = f"G{gen_num}"
    cur_art = AlgoArtifact(arm=arm_name, track=track_tag, generation=gen_num, passes=tuple(cur_passes), parent_sha256=parent_art.sha256())
    best_tr, _, _ = _eval_list(base_kind, train_tasks, cur_art, tb)
    best_val, _, _ = _eval_list(base_kind, val_tasks, cur_art, tb)
    log = [f"G{gen_num}_init({len(cur_passes)} passes): train={best_tr}, val={best_val}"]

    for cp in cand_passes:
        if any(p.sha256 == cp.sha256 for p in cur_passes):
            continue
        trials: List[Tuple[str, List[AlgoPass]]] = []
        if len(cur_passes) < max_total_passes:
            trials.append((f"append:{cp.name}", cur_passes + [cp]))
            trials.append((f"prepend:{cp.name}", [cp] + cur_passes))
        for idx in range(len(cur_passes)):
            trials.append((f"replace[{cur_passes[idx].name}->{cp.name}]", cur_passes[:idx] + [cp] + cur_passes[idx + 1:]))

        best_opt = None
        for label, plist in trials:
            cand_art = AlgoArtifact(arm=arm_name, track=track_tag, generation=gen_num, passes=tuple(plist), parent_sha256=parent_art.sha256())
            v_tot, _, _ = _eval_list(base_kind, val_tasks, cand_art, tb)
            if v_tot < best_val:
                tr_tot, _, _ = _eval_list(base_kind, train_tasks, cand_art, tb)
                if tr_tot <= best_tr:
                    if best_opt is None or (v_tot, tr_tot) < (best_opt[0], best_opt[1]):
                        best_opt = (v_tot, tr_tot, label, plist, cand_art)
        if best_opt is not None:
            best_val, best_tr, label, cur_passes, cur_art = best_opt
            log.append(f"ACCEPTED {label}: train={best_tr}, val={best_val}")
        else:
            log.append(f"REJECTED {cp.name}: no strict dev_val improvement under matched {tb}s cap")
    return cur_art, best_tr, best_val, log


def _format_diag(base_kind: str, train_tasks: Sequence[Any], base_s: Dict[str, int], ind_s: Dict[str, int], a2_s: Dict[str, int], cur_s: Dict[str, int]) -> str:
    hdr = "task_id                    | stratum    | BASE | IND  | A2_PRIOR | CUR_GEN | detail"
    lines = [f"DEV CURRICULUM DIAGNOSTICS ({len(train_tasks)} tasks; dev_val & holdout SEALED):", hdr, "-" * len(hdr)]
    for t in train_tasks:
        tid = t.task_id
        det = t.description if base_kind == "s2a" else f"w={t.width} in={t.n_inputs} expr={t.spec.to_expr_str()[:80]}"
        lines.append(f"{tid:26s} | {t.stratum:10s} | {base_s[tid]:4d} | {ind_s[tid]:4d} | {a2_s[tid]:8d} | {cur_s[tid]:7d} | {det}")
    return "\n".join(lines)


def cmd_propose(track: str, model: str, out_path: Path) -> Dict[str, Any]:
    t0 = time.perf_counter()
    cfg = _track_cfg(track)
    bk = cfg["base_kind"]
    tb = cfg["time_budget"]
    dev_val = cfg["dev_val"]
    meter = WorkMeter()

    # Precompute base & industry scores on union of all expanding dev train tasks (ZERO holdout access!)
    all_train = cfg["gen_slices"][-1]
    base_scores: Dict[str, int] = {}
    ind_scores: Dict[str, int] = {}
    for t in all_train:
        base_scores[t.task_id], _, _ = _eval_one(bk, t, None, seed=0, tb=tb)
        ind_scores[t.task_id], _ = _eval_ind(bk, t)

    # Gen 0: A2_PRIOR_ONLY (spec + API ONLY, ZERO tasks!)
    p_a2 = (
        "Design a frozen offline optimization pipeline (2 to 3 executable Python passes) purely from "
        "first principles and the substrate specification below. You are given NO benchmark tasks or traces.\n\n"
        + cfg["spec_block"]
        + "\n\nReturn ONLY a single valid JSON object with key \"passes\"."
    )
    resp_a2 = call_claude_isolated(p_a2, model=model, max_budget_usd=3.0, timeout_sec=420, system_prompt=STRICT_JSON_SYSTEM_PROMPT)
    a2_passes, a2_rej = [], []
    try:
        a2_passes, a2_rej = _parse_passes(resp_a2["text"], cfg["track_tag"], f"prior_{track}", max_passes=3)
    except Exception as exc:
        a2_rej.append({"name": "parse_error", "reason": str(exc)})
    meter.charge_llm_proposal(usd=resp_a2["cost_usd"], accepted=len(a2_passes) > 0, phase="A2_PRIOR_ONLY_sleep")
    art_a2 = AlgoArtifact(arm="A2_PRIOR_ONLY", track=cfg["track_tag"], generation=0, passes=tuple(a2_passes))

    _, a2_all_tr_scores, _ = _eval_list(bk, all_train, art_a2, tb)
    a2_val_tot, _, _ = _eval_list(bk, dev_val, art_a2, tb)

    # 3 Sequential Generations: G1 -> G2 -> G3 on expanding dev slices!
    gen_records: Dict[str, Any] = {}
    artifacts_out: Dict[str, Any] = {"A2_PRIOR_ONLY": art_a2.to_dict()}
    cur_art = art_a2
    cur_val_tot = a2_val_tot
    max_pass_schedule = (4, 5, 6)

    for g_idx in range(1, 4):
        train_slice = cfg["gen_slices"][g_idx - 1]
        cur_tr_tot, cur_tr_scores, cur_pstats = _eval_list(bk, train_slice, cur_art, tb)
        diag_txt = _format_diag(bk, train_slice, base_scores, ind_scores, a2_all_tr_scores, cur_tr_scores)
        code_view = "\n\n".join(f"# PASS {p.name} ({p.origin})\n{p.source}" for p in cur_art.passes)

        p_gen = (
            f"You are the sleep-phase executable algorithm evolver (Generation {g_idx} of 3 -- Compounding Evolution).\n"
            f"The dev curriculum has now expanded to {len(train_slice)} tasks (including harder new targets in Gen {g_idx}).\n"
            f"Current inherited pipeline (`{cur_art.arm}`): dev_slice_total={cur_tr_tot}, hidden dev_val={cur_val_tot} (A2_PRIOR dev_val={a2_val_tot}).\n\n"
            "GOAL: Inspect the inherited passes, their exact telemetry, and the remaining high-cost bottlenecks below. "
            "Propose 2 to 3 NEW or UPGRADED general-purpose executable Python passes (NO task-specific hardcoding!) that "
            "either add a genuinely new optimization paradigm or strictly improve an existing pass so the pipeline compounds "
            f"on BOTH structured AND procedural tasks under the identical `{tb}s`/task wall-clock cap.\n\n"
            + cfg["spec_block"]
            + "\n\nINHERITED PIPELINE:\n" + code_view
            + "\n\nINHERITED PIPELINE TELEMETRY ON CURRENT DEV SLICE:\n" + _summarize_pass_telemetry(cur_pstats)
            + "\n\n" + diag_txt
            + "\n\nReturn ONLY a single valid JSON object with key \"passes\"."
        )
        resp_g = call_claude_isolated(p_gen, model=model, max_budget_usd=3.0, timeout_sec=420, system_prompt=STRICT_JSON_SYSTEM_PROMPT)
        g_passes, g_rej = [], []
        try:
            g_passes, g_rej = _parse_passes(resp_g["text"], cfg["track_tag"], f"gen{g_idx}_{track}", max_passes=3)
        except Exception as exc:
            g_rej.append({"name": "parse_error", "reason": str(exc)})
        meter.charge_llm_proposal(usd=resp_g["cost_usd"], accepted=len(g_passes) > 0, phase=f"G{g_idx}_sleep")

        next_art, next_tr_tot, next_val_tot, sel_log = _select_generation(
            bk, cfg["track_tag"], g_idx, cur_art, g_passes, train_slice, dev_val, tb,
            max_total_passes=max_pass_schedule[g_idx - 1],
        )
        gen_records[f"G{g_idx}"] = {
            "prompt_sha256": _prompt_hash(p_gen),
            "models_used": resp_g["models_used"],
            "cost_usd": resp_g["cost_usd"],
            "n_train_tasks": len(train_slice),
            "proposed_passes": [p.name for p in g_passes],
            "rejected": g_rej,
            "selection_log": sel_log,
            "final_passes": [(p.name, p.origin) for p in next_art.passes],
            "dev_slice_total": next_tr_tot,
            "dev_val_total": next_val_tot,
        }
        artifacts_out[f"G{g_idx}"] = next_art.to_dict()
        cur_art = next_art
        cur_val_tot = next_val_tot
        # Incremental checkpoint after every generation so progress is never lost
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps({
            "track": track,
            "track_tag": cfg["track_tag"],
            "manifest_sha256": cfg["manifest_sha"],
            "time_budget_sec": tb,
            "proposer_model_alias": model,
            "wall_seconds": round(time.perf_counter() - t0, 3),
            "a2_call": {
                "prompt_sha256": _prompt_hash(p_a2),
                "models_used": resp_a2["models_used"],
                "cost_usd": resp_a2["cost_usd"],
                "accepted_passes": [p.name for p in a2_passes],
                "rejected": a2_rej,
                "dev_val_total": a2_val_tot,
            },
            "generations": gen_records,
            "artifacts": artifacts_out,
            "sleep_meter": meter.snapshot(),
        }, indent=2), encoding="utf-8")

    out_data = {
        "track": track,
        "track_tag": cfg["track_tag"],
        "manifest_sha256": cfg["manifest_sha"],
        "time_budget_sec": tb,
        "proposer_model_alias": model,
        "wall_seconds": round(time.perf_counter() - t0, 3),
        "a2_call": {
            "prompt_sha256": _prompt_hash(p_a2),
            "models_used": resp_a2["models_used"],
            "cost_usd": resp_a2["cost_usd"],
            "accepted_passes": [p.name for p in a2_passes],
            "rejected": a2_rej,
            "dev_val_total": a2_val_tot,
        },
        "generations": gen_records,
        "artifacts": artifacts_out,
        "sleep_meter": meter.snapshot(),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out_data, indent=2), encoding="utf-8")
    return out_data


def cmd_evaluate(
    track: str,
    proposals_path: Path,
    out_path: Path,
    seeds: Tuple[int, ...] = (0, 1, 2),
    allow_manifest_rebind: bool = False,
) -> Dict[str, Any]:
    """100% OFFLINE (LLM OFF) evaluation of ALL frozen checkpoints (A0, A1, A2, A3, G1, G2, G3, G3_KO, A5_SHAM)
    on the EXACT SAME untouched final holdout at identical wall-clock cap `tb` across 3 paired seeds."""
    t0 = time.perf_counter()
    cfg = _track_cfg(track)
    bk = cfg["base_kind"]
    suites = cfg["suites"]
    man_sha = cfg["manifest_sha"]
    prop = json.loads(proposals_path.read_text(encoding="utf-8"))
    if prop["manifest_sha256"] != man_sha and not allow_manifest_rebind:
        raise ValueError("Phase 3 manifest SHA mismatch!")

    tb = float(prop["time_budget_sec"])
    art_a2 = AlgoArtifact.from_dict(prop["artifacts"]["A2_PRIOR_ONLY"])
    art_g1 = AlgoArtifact.from_dict(prop["artifacts"]["G1"])
    art_g2 = AlgoArtifact.from_dict(prop["artifacts"]["G2"])
    art_g3 = AlgoArtifact.from_dict(prop["artifacts"]["G3"])
    art_a3 = cfg["a3_art"]
    art_a5 = cfg["a5_art"]

    # Selective knockout: strip ALL passes acquired in G2/G3 from G3 (keeps only Gen0/Gen1 passes!)
    ko_passes = tuple(p for p in art_g3.passes if p.origin.startswith("prior_") or p.origin.startswith("gen1_"))
    art_ko = AlgoArtifact(arm="G3_KO_G2G3", track=cfg["track_tag"], generation=3, passes=ko_passes, parent_sha256=art_g3.sha256())

    eval_suites = cfg["eval_suites"]
    ind_arm = cfg["industry_arm"]
    rows: List[Dict[str, Any]] = []
    arm_wall: Dict[str, float] = {}

    for arm_name, art in (
        ("A0_BASE", None),
        ("A2_PRIOR_ONLY", art_a2),
        ("A3_ZERO_LLM", art_a3),
        ("G1", art_g1),
        ("G2", art_g2),
        ("G3", art_g3),
        ("G3_KO_G2G3", art_ko),
        ("A5_SHAM", art_a5),
    ):
        at0 = time.perf_counter()
        for sname in eval_suites:
            for task in suites[sname]:
                for sd in seeds:
                    cost, sol_sha, _meta = _eval_one(bk, task, art, seed=sd, tb=tb)
                    rows.append(make_row(
                        arm=arm_name, suite=sname, task_id=task.task_id,
                        stratum=task.stratum, split=task.split, seed=sd,
                        spec_sha256=task.sha256(), cost=cost,
                        verified_exact=True, solution_sha256=sol_sha,
                    ))
        arm_wall[arm_name] = round(time.perf_counter() - at0, 3)

    at0 = time.perf_counter()
    for sname in eval_suites:
        for task in suites[sname]:
            cost, sol_sha = _eval_ind(bk, task)
            for sd in seeds:
                rows.append(make_row(
                    arm=ind_arm, suite=sname, task_id=task.task_id,
                    stratum=task.stratum, split=task.split, seed=sd,
                    spec_sha256=task.sha256(), cost=cost,
                    verified_exact=True, solution_sha256=sol_sha,
                ))
    arm_wall[ind_arm] = round(time.perf_counter() - at0, 3)

    arms_all = ("A0_BASE", ind_arm, "A2_PRIOR_ONLY", "A3_ZERO_LLM", "G1", "G2", "G3", "G3_KO_G2G3", "A5_SHAM")
    summary = compute_summary(rows)
    packet = {
        "track": track,
        "track_tag": cfg["track_tag"],
        "manifest_sha256": man_sha,
        "time_budget_sec": tb,
        "seeds": list(seeds),
        "arms": list(arms_all),
        "wall_seconds": round(time.perf_counter() - t0, 3),
        "arm_wall_seconds": arm_wall,
        "proposer_provenance": {
            "model_alias": prop["proposer_model_alias"],
            "a2_models": prop["a2_call"]["models_used"],
            "g1_models": prop["generations"]["G1"]["models_used"],
            "g2_models": prop["generations"]["G2"]["models_used"],
            "g3_models": prop["generations"]["G3"]["models_used"],
        },
        "artifacts": {
            "A2_PRIOR_ONLY": art_a2.to_dict(),
            "A3_ZERO_LLM": art_a3.to_dict(),
            "G1": art_g1.to_dict(),
            "G2": art_g2.to_dict(),
            "G3": art_g3.to_dict(),
            "G3_KO_G2G3": art_ko.to_dict(),
            "A5_SHAM": art_a5.to_dict(),
        },
        "sleep_meter": prop["sleep_meter"],
        "summary": summary,
        "rows": rows,
    }

    verdict = verify_and_reduce(
        packet,
        canonical_suites=suites,
        canonical_manifest_sha256=man_sha,
        expected_arms=arms_all,
        expected_suites=eval_suites,
        expected_seeds=seeds,
    )
    assert verdict["licenses_verdict"] is True

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    return packet


def main() -> None:
    p = argparse.ArgumentParser(description="Phase 3 3-Generation Compounding Runner (S3-A & S3-B-Hard)")
    sub = p.add_subparsers(dest="cmd", required=True)
    pp = sub.add_parser("propose")
    pp.add_argument("--track", required=True, choices=("s3a", "s3b"))
    pp.add_argument("--model", default="opus")
    pp.add_argument("--out", required=True, type=Path)

    pe = sub.add_parser("evaluate")
    pe.add_argument("--track", required=True, choices=("s3a", "s3b"))
    pe.add_argument("--proposals", required=True, type=Path)
    pe.add_argument("--out", required=True, type=Path)
    pe.add_argument("--allow-manifest-rebind", action="store_true")

    args = p.parse_args()
    if args.cmd == "propose":
        res = cmd_propose(track=args.track, model=args.model, out_path=args.out)
        print(json.dumps({
            "track": res["track"],
            "manifest_sha256": res["manifest_sha256"],
            "wall_seconds": res["wall_seconds"],
            "a2_val": res["a2_call"]["dev_val_total"],
            "generations": {
                k: {
                    "dev_slice_total": v["dev_slice_total"],
                    "dev_val_total": v["dev_val_total"],
                    "final_passes": v["final_passes"],
                    "selection_log": v["selection_log"],
                    "rejected_count": len(v["rejected"]),
                }
                for k, v in res["generations"].items()
            },
            "sleep_total_usd": res["sleep_meter"]["total_usd"],
        }, indent=2))
    else:
        pkt = cmd_evaluate(
            track=args.track,
            proposals_path=args.proposals,
            out_path=args.out,
            allow_manifest_rebind=bool(args.allow_manifest_rebind),
        )
        print(json.dumps({
            "track": pkt["track"],
            "manifest_sha256": pkt["manifest_sha256"],
            "wall_seconds": pkt["wall_seconds"],
            "n_rows": len(pkt["rows"]),
            "arm_wall_seconds": pkt["arm_wall_seconds"],
            "summary": {
                arm: {s: v["mean_median_cost"] for s, v in smap.items()}
                for arm, smap in pkt["summary"].items()
            },
        }, indent=2))


if __name__ == "__main__":
    main()
