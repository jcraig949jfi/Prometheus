"""Viability tests for the IMPROVER -- RED BY DESIGN as of 2026-09-21.

The 12 membrane tests all passed while the improver was completely inert:
across 10 seeds, every lineage's generation-8 artifact was byte-identical
to the base image. The membrane suite could not see this, because it only
ever asks whether a bounded artifact crosses the boundary correctly --
never whether the donor produced one worth crossing.

These tests encode the missing requirement. They are committed FAILING, as
the record of a defect found by measurement rather than by assertion. A
Campaign 1 run on an engine that fails them would transplant the base
image and measure the null by construction.

Do not make them pass by weakening them.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import engine as E  # noqa: E402


def _evolved(seed, generations=8):
    lin = E.Lineage(seed=seed, base=E.base_image())
    lin.evolve(generations=generations, escrow=E.Escrow(10 ** 7))
    return lin, lin.extract(generations)


def test_a_lineage_changes_its_machinery_at_all():
    """The donor must produce an artifact that is not just the base image."""
    base_hash = E.Artifact.from_modules(dict(E.base_image())).sha256
    _, art = _evolved(seed=11)
    assert art.sha256 != base_hash


def test_lineages_are_distinguishable_from_one_another():
    """Lineage is the experimental unit. If every seed yields the same bytes,
    the lineages are not independent and C1's statistics do not hold."""
    hashes = {_evolved(seed=s)[1].sha256 for s in range(11, 21)}
    assert len(hashes) >= 3


def test_the_improver_can_acquire_a_capability_the_base_lacks():
    """The whole causal question is whether evolved MACHINERY transfers. The
    improver must be able to reach the family the base image cannot solve --
    otherwise only a hand-written positive control ever can, and Campaign 1
    would be testing the experimenter's code, not the lineage's."""
    _, art = _evolved(seed=11)
    r = E.Recipient.fresh(seed=2)
    r.load(art)
    fresh = E.tasks(family="numtheory", n=40, seed=99)
    acc = r.run_tasks(fresh, E.Escrow(10 ** 6))["accuracy"]
    assert acc >= 0.30


def test_evolution_improves_the_donor_on_its_own_development_distribution():
    """A lineage that never improves on the tasks it CAN see is not evolving."""
    lin, _ = _evolved(seed=11)
    scores = [h["score"] for h in lin.history]
    assert max(scores) > scores[0]
