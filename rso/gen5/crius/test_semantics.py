"""EXTERNAL_FILTER semantics test: the filter changes ONLY the label the organism sees. Trajectories (every action and resulting
object), success flags and replay hashes of every player are byte-identical with and without the filter; the filter does hide the label.
    python -B -m rso.gen5.crius.test_semantics
"""
import json

from crius import baselines_c1 as bl, evaluate, streams
from rso.gen5.crius import adapt

SEED = 19020002
PLAYERS = ("PROCEDURE_REUSE_C1", "PROCEDURE_NOCAL_C1", "TABLE_MEMO_C1", "QUIT_C1", "ENUMERATE_C1")


def lifetime(world, name):
    with adapt.world_context(world) as cfg:
        tasks = streams.lifetime(cfg, SEED, "gate")
        r = evaluate.run_lifetime(bl.make_baseline(name), tasks, cfg, "ACCUMULATED", seed=SEED, keep_trajectories=True)
        return json.dumps([x["trajectory"] if "trajectory" in x else x for x in r["task_results"]], sort_keys=True, default=str), r["replay_hash"]


def test_filter_leaves_transitions_byte_identical():
    for n in PLAYERS:
        assert lifetime("W1", n) == lifetime("W2", n), n
        assert lifetime("W1", n) == lifetime("W5b", n), n          # CF-nocal == original C1 (calibration is already off in c1.json)
        assert lifetime("W2", n) == lifetime("W5c", n), n


def test_filter_hides_label():
    from crius import env, tasks_c1, world_c1  # noqa: F401
    with adapt.world_context("W2") as cfg:
        t = streams.lifetime(cfg, SEED, "gate")[0]
        e = adapt.crius_player.TaskRun(t, 0)
        e.act(0)
        assert e.last_primitive == -1 and e.observation()["last_primitive"] == -1
    with adapt.world_context("W1") as cfg:
        e = adapt.crius_player.TaskRun(t, 0)
        e.act(0)
        assert e.observation()["last_primitive"] >= 0


if __name__ == "__main__":
    test_filter_leaves_transitions_byte_identical()
    test_filter_hides_label()
    print("OK")
