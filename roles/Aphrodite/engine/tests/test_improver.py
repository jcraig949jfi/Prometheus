"""Viability and anti-overfitting tests for the IMPROVER.

History: committed RED on 2026-09-21 (commit 85b85b765) after measurement
showed engine v0's improver was inert -- 10 of 10 lineages returned
generation-8 artifacts byte-identical to the base image while all 12
membrane tests stayed green. Rewritten the same day under AMENDMENT 2
(science/campaign1/AMENDMENT_2_2026-09-21.md), again BEFORE the
implementation that is meant to satisfy it.

Two changes from the first red version, both from the operator's ruling:

  WITHDRAWN: ">= 3 distinct artifacts across 10 seeds". Diversity is
  trivially gameable and identical artifacts may represent CONVERGENT
  discovery. Diversity is now measured (qualify_engine.py), never
  required.

  REPLACEMENT: across preregistered seeds, at least one lineage must
  produce a non-base artifact that causally improves HELD-OUT capability
  relative to the base artifact, and that effect must survive
  fresh-recipient transplantation.

The named next adversary (AMENDMENT 2 section E) is an ACTIVE improver
that raises development score by exploiting the development distribution
while transferring nothing. Demanding mutation is insufficient; these
tests demand PRODUCTIVE MUTATION UNDER HELD-OUT CHALLENGE. The
development instance count is deliberately NOT raised to make
overfitting hard -- overfitting must stay reachable so these tests can
catch it.

Do not make these pass by weakening them.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import engine as E  # noqa: E402

SEEDS = (11, 12, 13, 14, 15)      # preregistered
GENERATIONS = 8
HELD_OUT_SEED = 987654            # never seen by any improver
BUDGET = 10 ** 7


def _evolved(seed, generations=GENERATIONS):
    lin = E.Lineage(seed=seed, base=E.base_image())
    lin.evolve(generations=generations, escrow=E.Escrow(BUDGET))
    return lin, lin.extract(generations)


def _held_out(family, n=40, seed=HELD_OUT_SEED):
    return E.tasks(family=family, n=n, seed=seed)


def _score(artifact, task_list):
    """Always through the ONE loader path, into a FRESH recipient."""
    r = E.Recipient.fresh(seed=2)
    r.load(artifact)
    return r.run_tasks(task_list, E.Escrow(BUDGET))["accuracy"]


def _base_artifact():
    return E.Artifact.from_modules(dict(E.base_image()))


# --------------------------------------------------------------- viability
def test_a_lineage_changes_its_machinery_at_all():
    _, art = _evolved(SEEDS[0])
    assert art.sha256 != _base_artifact().sha256


def test_evolution_improves_the_donor_on_its_own_development_distribution():
    lin, _ = _evolved(SEEDS[0])
    scores = [h["score"] for h in lin.history]
    assert max(scores) > scores[0]


# ------------------------------------- the replacement viability requirement
def test_some_lineage_causally_improves_held_out_capability_after_transplant():
    """AMENDMENT 2 section D. The whole program in miniature: variation ->
    selection -> discovered machinery -> hard isolation -> fresh recipient
    -> falsification. Evaluated on instances generated from a seed no
    improver ever saw, in a recipient that never met the donor."""
    held_out = []
    for fam in E.HEADROOM_FAMILIES:
        held_out += _held_out(fam)
    base_score = _score(_base_artifact(), held_out)

    best = 0.0
    for sd in SEEDS:
        _, art = _evolved(sd)
        if art.sha256 == _base_artifact().sha256:
            continue
        best = max(best, _score(art, held_out) - base_score)
    assert best >= 0.30


# --------------------------------------------------- anti-overfitting (E)
def test_development_gain_is_matched_by_held_out_gain():
    """The named adversary: dev score rises, held-out does not. A lineage
    may fail to discover anything, but it must not CLAIM a gain it cannot
    reproduce on unseen instances of the same classes."""
    for sd in SEEDS:
        lin, art = _evolved(sd)
        dev_gain = max(h["score"] for h in lin.history) - lin.history[0]["score"]
        if dev_gain <= 0:
            continue
        held = []
        for fam in E.HEADROOM_FAMILIES:
            held += _held_out(fam)
        held_gain = _score(art, held) - _score(_base_artifact(), held)
        assert held_gain >= 0.5 * dev_gain, (
            "seed %d: dev +%.3f but held-out +%.3f -- development-distribution "
            "exploitation" % (sd, dev_gain, held_gain))


# MOVED to tests/historical_regressions.py (slice-2C ruling: the main suite
# must not be knowingly red). The witness is preserved there as a strict
# xfail, so it still runs and will FAIL LOUDLY if it ever starts passing.

def test_the_artifact_does_not_encode_evaluation_instances():
    """Mutations encoding instance identifiers or memorised answers."""
    _, art = _evolved(SEEDS[0])
    body = art.bytes.decode()
    for fam in E.HEADROOM_FAMILIES:
        for t in _held_out(fam, n=10):
            assert t["gold"] not in body, "artifact contains a held-out answer"
            assert t["prompt"] not in body, "artifact contains a held-out prompt"


def test_the_gain_does_not_depend_on_the_evaluation_seed():
    """Selection exploiting deterministic seed structure."""
    _, art = _evolved(SEEDS[0])
    if art.sha256 == _base_artifact().sha256:
        return
    base = _base_artifact()
    for eval_seed in (11111, 22222, 33333):
        tl = []
        for fam in E.HEADROOM_FAMILIES:
            tl += E.tasks(family=fam, n=30, seed=eval_seed)
        assert _score(art, tl) - _score(base, tl) >= 0.30


def test_each_headroom_class_is_scored_independently():
    """R5 of AMENDMENT 2: headroom must span two independently scored
    classes, so a single-class win must not be reported as eligibility."""
    assert len(E.HEADROOM_FAMILIES) >= 2
    base = _base_artifact()
    for fam in E.HEADROOM_FAMILIES:
        assert _score(base, _held_out(fam)) == 0.0, (
            "%s is not a headroom class for the base image" % fam)
