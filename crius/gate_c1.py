"""Campaign 1 pre-search gate (operator ruling 2026-09-19 item 7; DESIGN_C1 s7).

Runs witnesses A-H on the sealed 'gate' streams with the frozen controls
and writes crius/runs/gate_c1/GATE.json + GATE.md. Exit code 1 if any
witness fails: then no search runs and the world is redesigned.

CLI: python -m crius.gate_c1 --config crius/configs/c1.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time

from . import baselines_c1 as bl, evaluate, receipts, streams

REL = 0.05


def _charged(r, cfg):
    return evaluate.task_cost(r, cfg)


def _stage_idx(tasks, stages):
    return [i for i, t in enumerate(tasks) if t.stage in stages]


def run_gate(cfg: dict, config_path: str, out_dir: str, positive: str = "PROCEDURE_REUSE_C1") -> dict:
    os.makedirs(out_dir, exist_ok=True)
    from . import vm as _vm
    _vm.set_substrate(cfg.get("substrate", {}))
    meta = receipts.run_meta(cfg, config_path)
    seeds = cfg["seeds"]["gate"]
    W = {}   # witness -> {"pass": bool, "evidence": ...}
    per_seed = {}
    t0 = time.time()
    for seed in seeds:
        tasks = streams.lifetime(cfg, seed, "gate")
        S = {"n_tasks": len(tasks)}
        # controls
        quit_m = evaluate.run_lifetime(bl.make_baseline("QUIT_C1"), tasks, cfg, "ACCUMULATED", seed=seed)["metrics"]
        enum = evaluate.run_lifetime(bl.make_baseline("ENUMERATE_C1"), tasks, cfg, "ACCUMULATED", seed=seed)
        nocal = evaluate.run_lifetime(bl.make_baseline("PROCEDURE_NOCAL_C1"), tasks, cfg, "ACCUMULATED", seed=seed)
        memo = evaluate.full_battery(bl.make_baseline("TABLE_MEMO_C1"), tasks, cfg, seed=seed)
        proc = evaluate.full_battery(bl.make_baseline(positive), tasks, cfg, seed=seed)
        receipts.write_json(os.path.join(out_dir, "%s_seed%d.json" % (positive, seed)),
                            receipts.battery_receipt(meta, bl.make_baseline(positive), tasks, seed, "gate", proc))
        receipts.write_json(os.path.join(out_dir, "TABLE_MEMO_C1_seed%d.json" % seed),
                            receipts.battery_receipt(meta, bl.make_baseline("TABLE_MEMO_C1"), tasks, seed, "gate", memo))
        # A: abstention cannot dominate competence
        S["A"] = {"QUIT": quit_m["fitness"], "ENUMERATE": enum["metrics"]["fitness"],
                  "QUIT_solved": quit_m["successes"], "ENUM_solved": enum["metrics"]["successes"],
                  "pass": quit_m["fitness"] < enum["metrics"]["fitness"]}
        # B: unsolved pays full budget
        unsolved = [r for r in enum["task_results"] if not r["success"]]
        ok_b = all(abs(_charged(r, cfg) - (r["vm_steps_used"] + r["ws_cost_units"]) / 100.0 - r["interaction_budget"]) < 1e-9 for r in unsolved)
        S["B"] = {"unsolved": len(unsolved), "pass": ok_b and len(unsolved) > 0}
        # D: static memorisation defeated
        # TABLE_MEMO keeps an explicit replay counter in cell 255: read it from a lifetime run with a kept workspace
        from .artifacts import BlockStore
        from .player import run_task
        from .workspace import Workspace
        ws_m, bl_m = Workspace.empty(cfg), BlockStore.empty(cfg)
        memo_player = bl.make_baseline("TABLE_MEMO_C1")
        memo_chain_solved = 0
        for i, t in enumerate(tasks):
            before = ws_m.read(255) or 0
            r = run_task(memo_player, t, i, ws_m, bl_m)
            after = ws_m.read(255) or 0
            if after > before and r["success"] and t.depth >= 2:
                memo_chain_solved += 1
        memo_replays_total = ws_m.read(255) or 0
        proc_chain = [r for r in proc["ACCUMULATED"]["task_results"] if r["depth"] >= 2]
        proc_proc_solved = sum(1 for r in proc_chain if r["success_in_block"])
        nocal_chain = [r for r in nocal["task_results"] if r["depth"] >= 2]
        nocal_proc_solved = sum(1 for r in nocal_chain if r["success_in_block"])
        S["D"] = {"TABLE_MEMO_chain_solved_by_replay": memo_chain_solved, "TABLE_MEMO_replays_total": memo_replays_total,
                  "PROCEDURE_chain_solved_by_invocation": proc_proc_solved, "n_chain": len(proc_chain),
                  "NOCAL_chain_solved_by_invocation": nocal_proc_solved,
                  "pass": memo_chain_solved == 0 and nocal_proc_solved <= 0.1 * max(1, proc_proc_solved)}
        # E: accumulated positive control gains from experience
        acc, fr = proc["ACCUMULATED"], proc["FRESH"]
        idx = _stage_idx(tasks, ("C", "D", "E"))
        gain = sum(proc["reuse_gain"][i] for i in idx)
        fresh_cost = sum(_charged(fr["task_results"][i], cfg) for i in idx)
        S["E"] = {"ACC_solved": acc["metrics"]["successes"], "FRESH_solved": fr["metrics"]["successes"],
                  "reuse_gain_CDE": round(gain, 1), "FRESH_cost_CDE": round(fresh_cost, 1),
                  "pass": acc["metrics"]["successes"] >= fr["metrics"]["successes"] and gain > 0.2 * fresh_cost}
        # F: ARTIFACT_TRANSPLANT beats CODE_ONLY
        cz = proc["causal"]
        art, code = cz["ARTIFACT_TRANSPLANT"], cz["CODE_ONLY"]
        S["F"] = {"ART_solved": art["successes"], "CODE_solved": code["successes"],
                  "ART_mean_cost": art["mean_cost"], "CODE_mean_cost": code["mean_cost"],
                  "FULL_solved": cz["FULL_WORKSPACE_TRANSPLANT"]["successes"],
                  "pass": art["successes"] > code["successes"] and art["mean_cost"] < (1 - REL) * code["mean_cost"]}
        # G: ablation removes the advantage
        abl = cz.get("ARTIFACT_ABLATION_ALL")
        S["G"] = {"ABL_ALL_mean_cost": abl["mean_cost"] if abl else None, "ABL_ALL_solved": abl["successes"] if abl else None,
                  "pass": abl is not None and abs(abl["mean_cost"] - code["mean_cost"]) <= REL * code["mean_cost"]
                  and abl["successes"] <= code["successes"]}
        # H: the transferred object is procedural
        det = cz["ARTIFACT_TRANSPLANT_detail"]
        snap_hash = {k: hashlib.sha256(json.dumps(v).encode()).hexdigest()[:12] for k, v in det["snapshot_blocks"].items()}
        final_hash = {str(b["block_id"]): hashlib.sha256(json.dumps([list(i) for i in b["instructions"]]).encode()).hexdigest()[:12] for b in det["final_blocks"]}
        unchanged = all(final_hash.get(k) == v for k, v in snap_hash.items())
        by_block = {}
        for e in det["invocation_log"]:
            b = by_block.setdefault(e["block"], {"args": set(), "seqs": set()})
            b["args"].add(e["entry"][0] if isinstance(e["entry"][0], int) else str(e["entry"][0]))
            b["seqs"].add(tuple(e["actions"]))
        template_blocks = [k for k, v in det["snapshot_blocks"].items() if len(v) > 0]
        rich = [k for k in template_blocks if len(by_block.get(int(k), {"args": set()})["args"]) >= 3
                and len(by_block.get(int(k), {"seqs": set()})["seqs"]) >= 3]
        memo_cz = memo["causal"]
        memo_no_adv = memo_cz["FULL_WORKSPACE_TRANSPLANT"]["successes"] <= memo_cz["CODE_ONLY"]["successes"]
        S["H"] = {"blocks_unchanged": unchanged, "template_blocks": len(template_blocks), "blocks_with_3plus_args_and_seqs": len(rich),
                  "TABLE_MEMO_FULL_solved": memo_cz["FULL_WORKSPACE_TRANSPLANT"]["successes"], "TABLE_MEMO_CODE_solved": memo_cz["CODE_ONLY"]["successes"],
                  "pass": unchanged and len(template_blocks) >= 2 and len(rich) >= 2 and memo_no_adv}
        per_seed[str(seed)] = S
    # C: integrity, from the test suite (pytest must pass); recorded by running the two micro-checks inline
    from .tests import test_c1_integrity as tci
    try:
        cfg0 = receipts.load_config(os.path.join(os.path.dirname(config_path), "c0.json"))
        tci.test_store_failure_cannot_become_an_action(cfg0)
        tci.test_out_of_range_values_are_not_actions(cfg0)
        fx = receipts.read_json(os.path.join(os.path.dirname(os.path.dirname(config_path)), "fixtures", "c0_failure_families.json"))["families"]
        tci.test_fixture_empty_block_clock_signature_and_integrity(cfg0, fx)
        c_pass = True
    except AssertionError as e:
        c_pass = False
    for wname in "ABDEFGH":
        W[wname] = {"pass": all(per_seed[s][wname]["pass"] for s in per_seed), "per_seed": {s: per_seed[s][wname] for s in per_seed}}
    W["C"] = {"pass": c_pass, "evidence": "crius/tests/test_c1_integrity.py micro-tests and clock fixture"}
    all_pass = all(W[k]["pass"] for k in "ABCDEFGH")
    out = {"meta": meta, "witnesses": W, "all_pass": all_pass, "positive_control": positive, "elapsed_s": round(time.time() - t0, 1)}
    receipts.write_json(os.path.join(out_dir, "GATE.json"), out)
    lines = ["PRE-SEARCH GATE  campaign=%s positive_control=%s config_hash=%s world=%s generator=%s code=%s" % (
        cfg.get("campaign"), positive, meta["config_hash"], meta["world_fingerprint"], meta["partitions_fingerprint"], meta["code_commit"][:9]),
        "witness  pass  evidence (per gate seed %s)" % seeds]
    for k in "ABCDEFGH":
        w = W[k]
        ev = w.get("evidence") or "; ".join("%s: %s" % (s, json.dumps({kk: vv for kk, vv in v.items() if kk != "pass"})) for s, v in w["per_seed"].items())
        lines.append("  %s      %-5s %s" % (k, "PASS" if w["pass"] else "FAIL", ev))
    lines.append("ALL PASS: %s" % all_pass)
    text = "\n".join(lines)
    with open(os.path.join(out_dir, "GATE.md"), "w", encoding="ascii", newline="\n") as f:
        f.write(text + "\n")
    print(text)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join("crius", "configs", "c1.json"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--positive-control", default=None)
    args = ap.parse_args(argv)
    cfg = receipts.load_config(args.config)
    positive = args.positive_control
    if positive is None:
        from . import parts_c2
        positive = parts_c2.POSITIVE_CONTROL.get(cfg.get("campaign"), "PROCEDURE_REUSE_C1")
    out_dir = args.out or os.path.join("crius", "runs", "gate_%s" % cfg.get("campaign", "c1"))
    out = run_gate(cfg, args.config, out_dir, positive)
    return 0 if out["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
