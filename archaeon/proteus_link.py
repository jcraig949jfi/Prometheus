"""The Proteus side of Archaeon's player identity.

Proteus is the Player Foundry. It answers the question Archaeon's three
player-dependent detectors could not previously ask: *which player was this?*

    organism_id = sha256(canonical_json(player_manifest))

Content-addressed, world-independent, stable forever. A frozen registry of 64
specimens lives at ``proteus/integration/PLAYER_REGISTRY.json``
(schema ``proteus.player_registry.v1``), and because Proteus posts that exact
serialization to SFE, an artifact's ``blob_hash`` EQUALS the ``organism_id``.
That equality is the join: an SFE world holding a
``kind='proteus_player_manifest'`` artifact tells us which player ran there,
with no new engine work and no invented convention.

Two things this module exists to keep straight.

**1. Coordinates, not taxonomy.** Proteus deliberately supplies no player
types, families, tags or quality scores, and has a test that fails if that
vocabulary ever appears in the registry. Archaeon respects that. What it reads
is the ``resource_envelope`` -- ``tape_words``, ``n_regs``,
``genome_instructions``, ``tick_budget`` and friends -- which are hard bounds
read off the manifest, not labels and not a ranking. A measured bound is a
COORDINATE. Archaeon never derives a semantic category from one, and never
attaches a meaning to a region of that space.

These are also far better coordinates than the live SFE chart's
``spec.candidate``, which is a hash-like integer whose adjacency is
meaningless. ``tape_words`` doubling from 16 to 1024 is a real axis, so D2's
neighbour radius and D6's boundary bisection finally refer to something.

**2. The neutrality caveat is load-bearing for Archaeon specifically.**
``reg["source_qualification"]`` says:

    deterministic_generation   QUALIFIED
    semantic_quarantine        QUALIFIED
    mutation_neutrality        NOT_QUALIFIED_AUTHORED_NONEQUILIBRIUM_CURRENT
    permitted_use              USE_A_FROZEN_SPECIMEN_SOURCE
    prohibited_use             USE_B_NEUTRAL_EVOLUTIONARY_OPERATOR

The 64 frozen specimens are safe to enumerate, instantiate, run, checkpoint and
replay. What is NOT established is that the machinery which would BREED new
generations samples neutrally -- it measurably does not, carrying an authored
probability current (1.4e-02 nats per mutation step, 11.3% of two-way flux
appearing as net imbalance, reproduced across two independent measurements).

Proteus's handoff states the consequence directly: *do not build a population
comparison that quietly relies on neutral sampling of structural states.*

Archaeon builds exactly such comparisons. D1 measures a cell against its
family's baseline; D4 compares players across related regions. If the
population were bred by a biased kernel, that baseline is not a neutral
reference and the comparison inherits the bias -- silently, because nothing in
the arithmetic would show it. So this module refuses to let a mutated organism
into a detector's evidence without the caller having said so: see
``assert_use_a_only``. Generation 0 specimens are USE A and always allowed.

That guard exists now, before any breeding has happened, because the failure it
prevents is one that leaves no trace in the result.
"""
from __future__ import annotations

import functools
from typing import Any, Dict, List, Optional, Set

# The envelope fields Archaeon treats as numeric coordinate axes. Chosen for
# being physical and ordered; `persist` and `code_writable` are categorical and
# are deliberately NOT axes (a distance between 'tape' and 'regs' is a fiction).
ENVELOPE_AXES = (
    "tape_words",
    "n_regs",
    "genome_instructions",
    "tick_budget",
    "out_cap",
    "max_state_footprint_words",
    "persistent_state_words",
    "max_ops_per_tick",
)

# SFE artifact kind that carries a player manifest.
PROTEUS_ARTIFACT_KIND = "proteus_player_manifest"

USE_A = "USE_A_FROZEN_SPECIMEN_SOURCE"
USE_B = "USE_B_NEUTRAL_EVOLUTIONARY_OPERATOR"


class ProteusUnavailable(Exception):
    """The registry could not be loaded. Archaeon degrades, never fabricates."""


class NeutralityNotEstablished(Exception):
    """A population comparison was attempted over bred organisms.

    Proteus's mutation machinery is NOT_QUALIFIED_AUTHORED_NONEQUILIBRIUM_CURRENT.
    A baseline built from a biased population is not a neutral reference, and
    the resulting comparison would be wrong in a way that leaves no trace in
    the arithmetic. Raised rather than warned for exactly that reason.
    """


@functools.lru_cache(maxsize=1)
def load_registry() -> Dict[str, Any]:
    """Load and validate the frozen registry. Fails closed, by Proteus's design."""
    try:
        from proteus.integration import registry as R
        return R.load_default()
    except Exception as exc:                        # pragma: no cover
        raise ProteusUnavailable(
            "Proteus player registry unavailable: {}. Archaeon will report "
            "player-dependent detectors as NOT ELIGIBLE rather than proceeding "
            "without player identity.".format(exc))


def organism_ids() -> Set[str]:
    reg = load_registry()
    return {e["organism_id"] for e in reg["entries"]}


def entries_by_id() -> Dict[str, Dict[str, Any]]:
    reg = load_registry()
    return {e["organism_id"]: e for e in reg["entries"]}


def qualification() -> Dict[str, Any]:
    """The registry's own qualification block, copied into every proposal.

    Carried verbatim so a reader of a stored proposal can see what was and was
    not established about the players it used, without reconstructing it from
    Proteus's history.
    """
    return dict(load_registry()["source_qualification"])


def envelope_coords(organism_id: str) -> Dict[str, float]:
    """Numeric coordinates for one organism, from its resource envelope."""
    e = entries_by_id().get(organism_id)
    if not e:
        return {}
    env = e.get("resource_envelope", {})
    out: Dict[str, float] = {}
    for axis in ENVELOPE_AXES:
        v = env.get(axis)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            out[axis] = float(v)
    return out


def generation(organism_id: str) -> Optional[int]:
    e = entries_by_id().get(organism_id)
    return None if e is None else e.get("generation")


def is_frozen_specimen(organism_id: str) -> bool:
    """True iff this organism is a generation-0 registry specimen (USE A)."""
    return generation(organism_id) == 0


def assert_use_a_only(organism_ids_seen, *, context: str = "detector evidence",
                      allow_unregistered: bool = True) -> Dict[str, Any]:
    """Refuse a population comparison that rests on unqualified breeding.

    ``allow_unregistered`` defaults True because an organism absent from the
    registry is not thereby a mutant -- it may come from a different producer
    entirely. Absence is unknown provenance, not a violation, and treating it
    as one would be its own fabricated claim. Registered organisms with
    ``generation > 0`` ARE bred by the machinery in question, and those are
    refused.

    Returns an audit block for provenance.
    """
    seen = sorted({o for o in organism_ids_seen if o})
    known = entries_by_id()
    registered = [o for o in seen if o in known]
    unregistered = [o for o in seen if o not in known]
    bred = [o for o in registered if (known[o].get("generation") or 0) > 0]

    if bred:
        raise NeutralityNotEstablished(
            "{} includes {} bred organism(s) (generation > 0): {}. Proteus "
            "reports mutation_neutrality = NOT_QUALIFIED_AUTHORED_"
            "NONEQUILIBRIUM_CURRENT, so a population baseline built from them "
            "is not a neutral reference and the comparison would inherit an "
            "authored probability current without showing it. permitted_use is "
            "{}.".format(context, len(bred), bred[:5], USE_A))

    return {
        "check": "proteus.use_a_only",
        "context": context,
        "organisms_seen": len(seen),
        "registered_generation_0": len(registered),
        "unregistered_provenance_unknown": len(unregistered),
        "bred_organisms": 0,
        "permitted_use": USE_A,
        "prohibited_use": USE_B,
        "note": ("Unregistered organisms are recorded as unknown provenance, "
                 "not as violations: absence from the Proteus registry does "
                 "not make an organism a mutant."),
    }
