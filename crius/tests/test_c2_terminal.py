"""Terminal-round grounding fixtures (CRIUS_C2_TERMINAL_PREREG.md s II-III).

Each control must test its intended contrast on rung C's substrate, the typed
argument must be what the invocation log records, streams must be paired,
allocation must not be rewarded, and a typed-substrate receipt must replay.
"""

import json
import os

import pytest

from crius import artifacts, baselines_c1, evaluate, parts_c2, receipts, search, streams, vm, workspace
from crius.player import VMPlayer, run_task

HERE = os.path.dirname(os.path.abspath(__file__))
C2C = os.path.join(HERE, "..", "configs", "c2c.json")


@pytest.fixture(scope="module")
def cfg():
    return receipts.load_config(C2C)


@pytest.fixture(scope="module")
def tasks(cfg):
    return streams.lifetime(cfg, 301, "gate")


def _battery(name, cfg, tasks, seed=301):
    vm.set_substrate(cfg["substrate"])
    return evaluate.full_battery(baselines_c1.make_baseline(name), tasks, cfg, seed=seed)


def _E(bat, cfg, tasks):
    idx = [i for i, t in enumerate(tasks) if t.stage in ("C", "D", "E")]
    gain = sum(bat["reuse_gain"][i] for i in idx)
    fresh = sum(evaluate.task_cost(bat["FRESH"]["task_results"][i], cfg) for i in idx)
    acc, fr = bat["ACCUMULATED"]["metrics"]["successes"], bat["FRESH"]["metrics"]["successes"]
    return acc >= fr and gain > 0.2 * fresh, (acc, fr, round(gain, 1), round(fresh, 1))


def _F(bat):
    cz = bat["causal"]
    art, code = cz["ARTIFACT_TRANSPLANT"], cz["CODE_ONLY"]
    return art["successes"] > code["successes"] and art["mean_cost"] < 0.95 * code["mean_cost"], (art["successes"], code["successes"], art["mean_cost"], code["mean_cost"])


def _H_rich(bat):
    det = bat["causal"]["ARTIFACT_TRANSPLANT_detail"]
    by = {}
    for e in det["invocation_log"]:
        b = by.setdefault(e["block"], {"args": set(), "seqs": set()})
        b["args"].add(e.get("arg", e["entry"][0]))
        b["seqs"].add(tuple(e["actions"]))
    templ = [k for k, v in det["snapshot_blocks"].items() if len(v) > 0]
    return sum(1 for k in templ if len(by.get(int(k), {"args": set()})["args"]) >= 3 and len(by.get(int(k), {"seqs": set()})["seqs"]) >= 3), len(templ)


# ---------------------------------------------------------------- the two controls test their contrasts


def test_accessibility_control_passes_E_and_a_table_control_fails_it(cfg, tasks):
    ok, ev = _E(_battery("PROCEDURE_REUSE_C1", cfg, tasks), cfg, tasks)
    assert ok, ev
    ok2, ev2 = _E(_battery("TABLE_MEMO_C1", cfg, tasks), cfg, tasks)
    assert not ok2, ev2


def test_causal_control_passes_F_and_a_decorative_artifact_control_fails_it(cfg, tasks):
    ok, ev = _F(_battery("P_REC_INV_PLAN", cfg, tasks))
    assert ok, ev
    # P_REC records procedures and never invokes them: its transplant must carry nothing
    ok2, ev2 = _F(_battery("P_REC", cfg, tasks))
    assert not ok2, ev2


def test_H_argument_diversity_reads_the_effective_argument(cfg, tasks):
    task = next(t for t in tasks if t.depth == 1)
    vm.set_substrate(cfg["substrate"])
    ws, bs = workspace.Workspace.empty(cfg), artifacts.BlockStore.empty(cfg)
    # record a one-step procedure at action 3, then invoke it with arguments 0..3 while R0 is held at 9
    src = "\n".join(["PREC_BEGIN", "ACTI 3", "PREC_END R2", "CONST R0, 9",
                     "CONST R4, 0", "PINVOKE R2, R4", "CONST R4, 1", "PINVOKE R2, R4",
                     "CONST R4, 2", "PINVOKE R2, R4", "CONST R4, 3", "PINVOKE R2, R4", "HALT"])
    run_task(VMPlayer(vm.assemble(src, max_len=96)), task, 0, ws, bs)
    args = [e["arg"] for e in bs.invocation_log]
    assert args == [0, 1, 2, 3]                       # the effective arguments, not R0 (= 9)
    assert all(e["entry"][0] == 9 for e in bs.invocation_log)


def test_block_control_argument_is_R0_and_H_counts_it(cfg, tasks):
    bat = _battery("PROCEDURE_REUSE_C1", cfg, tasks)
    rich, templ = _H_rich(bat)
    assert templ >= 2 and rich >= 2


# ---------------------------------------------------------------- no reward for allocation; no table shortcut


def test_allocation_is_not_rewarded(cfg, tasks):
    base = parts_c2.program("P_BASE")
    alloc = [(vm.OP["WS_REC_NEW"], 7, 0, 0), (vm.OP["BLK_NEW"], 7, 0, 0)] + base
    vm.set_substrate(cfg["substrate"])
    mb = evaluate.run_lifetime(VMPlayer(base), tasks, cfg, "ACCUMULATED", seed=301)["metrics"]
    ma = evaluate.run_lifetime(VMPlayer(alloc), tasks, cfg, "ACCUMULATED", seed=301)["metrics"]
    assert ma["successes"] == mb["successes"]
    assert ma["fitness"] < mb["fitness"]


def test_table_control_fails_H_transplant_clause(cfg, tasks):
    bat = _battery("TABLE_MEMO_C1", cfg, tasks)
    cz = bat["causal"]
    assert cz["FULL_WORKSPACE_TRANSPLANT"]["successes"] <= cz["CODE_ONLY"]["successes"]


# ---------------------------------------------------------------- paired streams; replay; PARTS accounting


def test_paired_streams_are_aligned_within_an_iteration(cfg, tmp_path):
    out = search.run_search(cfg, C2C, iterations=2, seed=11, arm="seeded", workers=1, run_id="t_pair", out_root=str(tmp_path))
    by_it = {}
    with open(os.path.join(out, "candidates.jsonl"), "r", encoding="ascii") as f:
        for line in f:
            r = json.loads(line)
            by_it.setdefault(r["iteration"], set()).add(tuple(r["stream_seeds"]))
    for it, seeds in by_it.items():
        assert len(seeds) == 1, (it, seeds)           # every candidate of an iteration saw the same paired streams
        assert len(next(iter(seeds))) == cfg["streams"]["paired"]
    assert os.path.exists(os.path.join(out, "takeovers.jsonl"))


def test_typed_receipt_replays(cfg, tasks):
    p = parts_c2.player("P_REC_INV_PLAN")
    meta = receipts.run_meta(cfg, C2C)
    life = evaluate.run_lifetime(p, tasks, cfg, "ACCUMULATED", seed=301)
    rec = receipts.lifetime_receipt(meta, p, tasks, 301, "gate", life)
    p2 = VMPlayer(vm.program_from_json(rec["candidate_spec"]["program"]))
    t2 = streams.lifetime(cfg, rec["seed"], rec["search_or_qualification"])
    life2 = evaluate.run_lifetime(p2, t2, cfg, rec["condition"], seed=rec["seed"])
    assert life2["replay_hash"] == rec["replay_hash"]


def test_parts_accounting_recorder_and_invoker(cfg, tasks):
    vm.set_substrate(cfg["substrate"])
    rec = evaluate.run_lifetime(parts_c2.player("P_REC"), tasks, cfg, "ACCUMULATED", seed=301)
    inv = evaluate.run_lifetime(parts_c2.player("P_INV"), tasks, cfg, "ACCUMULATED", seed=301)
    n_proc = sum(1 for e in rec["artifact_history"]["events"] if e["kind"] == "create" and e.get("origin") == "procedure")
    assert n_proc >= 3 and rec["metrics"]["artifacts_invoked_total"] == 0
    assert inv["metrics"]["blocks_created_total"] <= 1     # the calibration object only
