"""Historical regression fixtures: defects that are still real.

Kept OUT of the main suite so that a green run means green (slice-2C ruling),
and kept EXECUTABLE as strict xfails so that if a defect silently repairs
itself the suite fails loudly and someone has to look.

Each fixture carries the measurement that created it.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import engine as E  # noqa: E402

SEEDS = (11, 12, 13, 14, 15)
GENERATIONS = 8
BUDGET = 10 ** 7


def _evolved(seed, generations=GENERATIONS):
    lin = E.Lineage(seed=seed, base=E.base_image())
    lin.evolve(generations=generations, escrow=E.Escrow(BUDGET))
    return lin, lin.extract(generations)


def _score(artifact, task_list):
    r = E.Recipient.fresh(seed=2)
    r.load(artifact)
    return r.run_tasks(task_list, E.Escrow(BUDGET))["accuracy"]


@pytest.mark.xfail(strict=True, reason=(
    "SLICE 2 DEFECT, still real: on the legacy non-lineage_id path a lineage "
    "claims numtheory mastery on development (1.00) while scoring 0.635 on "
    "held-out instances -- 6/pi^2 = 0.6079 is the density of coprime pairs, so "
    "the number is the coprime shortcut's exact reach. Per AMENDMENT 2 section "
    "C the development instance count may NOT be raised to cure it."))
def test_each_headroom_class_that_looks_solved_on_dev_generalises():
    for sd in SEEDS:
        lin, art = _evolved(sd)
        dev_final = lin.history[-1]
        for fam in E.HEADROOM_FAMILIES:
            dev_tasks = [t for t in dev_final.get("dev", []) if t["family"] == fam]
            if not dev_tasks:
                continue
            r = E.Recipient.fresh(seed=2)
            r.load(art)
            dev_acc = r.run_tasks(dev_tasks, E.Escrow(BUDGET))["accuracy"]
            if dev_acc < 1.0:
                continue                      # never claimed this class
            held = _score(art, _held_out(fam, n=200))
            assert held >= 0.90, (
                "seed %d: %s scores %.3f on development but %.3f on held-out "
                "instances -- development-distribution exploitation"
                % (sd, fam, dev_acc, held))


