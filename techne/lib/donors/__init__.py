"""techne.lib.donors -- the donor adapter surface.

A DONOR is external machinery Prometheus did not write: tensorly, pyribs, egglog (live
adapters); DisCoPy and cvc5 (adapters RETIRED 2026-09-12, see retired/). Standing Order #1
says wrap rather than rewrite. This package is where wrapping happens when a consumer needs
an interface Prometheus does not already have -- and ONLY then, since the operator's ruling
of 2026-09-12 (roles/Techne/prompts/2026-09-12_techne51_ruling/OPERATOR.md): "the donor
foundry survives; the universal adapter contract does not." Eleven days with zero external
importers of this package was the evidence. Direct donor consumption is acceptable where it
is cleaner; Techne's durable product is the acquisition RECEIPT, not the adapter. The
distinction this package still enforces, for the adapters that remain:

    what the donor can GENERATE          -- capabilities() / propose()
    what the donor itself VALUES         -- native_score() / native_selection_relation
    what Prometheus independently MEASURES -- not here, and deliberately not here

A donor arrives carrying its own selection criterion. pyribs ranks by an objective inside a
behavioural archive; cvc5 ranks nothing and simply decides; tensorly minimises reconstruction
error. If an adapter normalises those away, a downstream experiment can no longer tell whether
an apparent result came from the Prometheus measurement or was inherited from the donor's own
objective -- which is a control drawn from the treatment's selection relation, i.e. the
treatment. So `native_selection_relation` is a REQUIRED, machine-readable field, and `NONE` is
a legitimate value that must be stated rather than left blank.

WHAT AN ADAPTER MAY NOT DO
  - alias donor-native quality to a Prometheus scientific score (T9)
  - silently swallow an unknown configuration key (T7)
  - convert a donor failure into a successful empty result (T10)
  - claim a donor is scientifically better than another (not this seat's call at all)

Adapters are CONTESTANTS. Installation is not adoption; a passing smoke test is not evidence
that a donor earns rent. That judgement belongs to whichever bench consumes the capability.
"""
from .contract import (
    DonorAdapter,
    DonorArtifact,
    DonorCapability,
    DonorError,
    DonorIdentity,
    SelectionRelation,
    NO_SELECTION,
    registry,
    register,
    get,
    available,
)

__all__ = [
    "DonorAdapter", "DonorArtifact", "DonorCapability", "DonorError", "DonorIdentity",
    "SelectionRelation", "NO_SELECTION", "registry", "register", "get", "available",
]


# Adapter modules register themselves on import. Each guards its donor import lazily, so a
# missing donor produces a status (VETTED_NOT_INSTALLED) rather than breaking this package.
# RETIRED 2026-09-12 (operator ruling TECHNE-51): cvc5_adapter and discopy_adapter moved
# verbatim to techne/lib/donors/retired/ and are NOT imported here. The donors are not
# retired; the unused adapters are. Evidence: techne/lib/donors/retired/RETIREMENT.md.
from . import egglog_adapter as _egglog      # noqa: E402,F401
from . import pyribs_adapter as _pyribs      # noqa: E402,F401
from . import tensorly_adapter as _tensorly  # noqa: E402,F401
