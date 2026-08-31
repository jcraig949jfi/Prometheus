"""The donor adapter contract. Techne Gen-0, 2026-08-31.

Every donor exposes the same method surface so that downstream benches can consume external
machinery without re-learning each library's conventions -- and, more importantly, without
losing the information needed to tell an inherited result from a measured one.

DESIGN NOTE ON `native_selection_relation`
    This is the load-bearing field. Prior art arrives pre-committed to an objective: pyribs
    fills a behavioural archive by an objective the caller supplies, POET-style world
    generation selects environments by regret against a specific agent, tensorly minimises
    reconstruction error. If a downstream experiment scores a donor's output with a Prometheus
    metric Z, and the donor already ranked its own output by Y, then any apparent Z-success may
    be Y wearing a different label. The adapter therefore records Y explicitly, machine-
    readably, so an experiment can be designed to BREAK it rather than inherit it.
    `NO_SELECTION` is a real answer -- a decision procedure such as cvc5 ranks nothing -- and
    must be stated, never fabricated for API uniformity.

DESIGN NOTE ON STRICTNESS
    Unknown configuration keys raise. A wrapper that silently ignores a key the caller believed
    was applied is a measurement-error generator: the experiment records a configuration that
    never took effect. Failures are typed and preserved for the same reason -- a donor error
    converted into an empty success is indistinguishable, downstream, from a genuine null.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import platform
import sys
from typing import Any, Callable, Mapping, Sequence


class DonorError(RuntimeError):
    """A donor failed. Typed and preserved -- never converted into an empty success (T10).

    `donor` and `stage` say which adapter and which phase; `cause` keeps the upstream exception
    so a downstream reader can tell a licence problem from a numerical one.
    """

    def __init__(self, donor: str, stage: str, message: str, cause: BaseException | None = None):
        self.donor, self.stage, self.cause = donor, stage, cause
        super().__init__(f"[{donor}:{stage}] {message}"
                         + (f" (cause: {type(cause).__name__}: {cause})" if cause else ""))


@dataclasses.dataclass(frozen=True)
class DonorIdentity:
    """Who this actually is. Resolved, never inferred from the distribution name.

    `upstream` is the canonical repository. `identity_evidence` records how that was
    established: 'declared_url' (the distribution's own metadata names the repo),
    'description_only' (weaker -- the repo appears only in prose), or 'unresolved'.
    """
    name: str
    distribution: str
    version: str
    upstream: str
    license: str
    identity_evidence: str

    def as_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True)
class SelectionRelation:
    """What the donor itself values, stated machine-readably.

    kind:        'objective' | 'ordering' | 'constraint' | 'none'
    direction:   'maximize' | 'minimize' | 'satisfy' | 'none'
    over:        what the relation ranks (e.g. 'archive elites', 'reconstruction error')
    supplied_by: 'donor' if baked in; 'caller' if the donor requires the caller to provide it.
                 pyribs takes its objective from the caller, which means the selection relation
                 IS WHATEVER THE CALLER PASSES -- a fact that must reach the ledger, because it
                 moves responsibility for the confound from the donor to the experiment.
    """
    kind: str
    direction: str
    over: str
    supplied_by: str
    note: str = ""

    def as_dict(self) -> dict:
        return dataclasses.asdict(self)


#: The legitimate "this donor ranks nothing" value. A decision procedure decides; it does not
#: prefer. Stating this is required; leaving the field unset is not allowed (T8).
NO_SELECTION = SelectionRelation(
    kind="none", direction="none", over="", supplied_by="donor",
    note="decision procedure: returns a verdict/model, imposes no preference order",
)


@dataclasses.dataclass(frozen=True)
class DonorCapability:
    """One mechanically-available operation. `deterministic` is a claim about THIS wrapper's
    behaviour under a fixed seed and config, and is exercised by T3."""
    name: str
    summary: str
    deterministic: bool
    inputs: str
    outputs: str


@dataclasses.dataclass(frozen=True)
class DonorArtifact:
    """Whatever a donor produced, carrying enough to answer "exactly what produced this?"
    without trusting a narrative.

    `payload` is the donor's actual output; everything else is provenance.
    """
    donor: str
    donor_version: str
    upstream: str
    capability: str
    config: Mapping[str, Any]
    seed: int | None
    input_digest: str
    output_digest: str
    native_selection_relation: Mapping[str, Any]
    native_score: float | None
    payload: Any = None
    environment: Mapping[str, Any] = dataclasses.field(default_factory=dict)

    def provenance(self) -> dict:
        """The replayable record. Deliberately excludes `payload`: provenance must be small
        enough to store beside every row, and the payload is the thing being explained."""
        return {
            "donor": self.donor,
            "donor_version": self.donor_version,
            "upstream": self.upstream,
            "capability": self.capability,
            "config": dict(self.config),
            "seed": self.seed,
            "input_digest": self.input_digest,
            "output_digest": self.output_digest,
            "native_selection_relation": dict(self.native_selection_relation),
            "native_score": self.native_score,
            "environment": dict(self.environment),
        }

    def replay_seed(self) -> dict:
        """The minimum needed to re-run this invocation: which donor at which version, which
        capability, the effective config, and the seed."""
        return {"donor": self.donor, "donor_version": self.donor_version,
                "capability": self.capability, "config": dict(self.config), "seed": self.seed,
                "input_digest": self.input_digest}


def canonical_digest(obj: Any) -> str:
    """Stable SHA-256 over a canonical JSON projection. Used for input/output identity.

    numpy arrays and anything exposing `tolist` are projected through it; mappings are sorted;
    sets are ordered. Objects with no projection fall back to their repr, which is weaker --
    adapters holding opaque payloads should digest something meaningful instead.
    """
    def norm(o: Any) -> Any:
        if o is None or isinstance(o, (bool, int, str)):
            return o
        if isinstance(o, float):
            # Round-trip through repr so a float digests identically across platforms.
            return repr(o)
        if hasattr(o, "tolist"):
            return norm(o.tolist())
        if isinstance(o, Mapping):
            return {str(k): norm(v) for k, v in sorted(o.items(), key=lambda kv: str(kv[0]))}
        if isinstance(o, (list, tuple)):
            return [norm(v) for v in o]
        if isinstance(o, (set, frozenset)):
            return sorted(norm(v) for v in o)
        return "<repr>" + repr(o)
    blob = json.dumps(norm(obj), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def environment_stamp() -> dict:
    """Coarse environment identity. Enough to notice that a replay ran somewhere else."""
    return {"python": sys.version.split()[0], "platform": platform.platform(),
            "machine": platform.machine()}


class DonorAdapter:
    """Base class. Subclasses implement `_identity`, `_capabilities`, and `_propose`.

    Subclasses MUST set `native_selection_relation` to a SelectionRelation or to NO_SELECTION.
    The class body is checked at subclass creation, so a donor cannot reach the registry with
    the field unset.
    """

    #: Set by each subclass. Checked in __init_subclass__.
    native_selection_relation: SelectionRelation | None = None
    #: Config keys this adapter understands. Anything else raises (T7).
    accepted_config: frozenset = frozenset()

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        rel = getattr(cls, "native_selection_relation", None)
        if not isinstance(rel, SelectionRelation):
            raise TypeError(
                cls.__name__ + " must declare native_selection_relation as a SelectionRelation "
                "(use NO_SELECTION if the donor imposes no preference order). This field is "
                "load-bearing: without it a downstream experiment cannot tell a measured "
                "result from one inherited from the donor's own objective."
            )

    # -- subclass hooks -------------------------------------------------------------------
    def _identity(self) -> DonorIdentity:
        raise NotImplementedError

    def _capabilities(self) -> Sequence[DonorCapability]:
        raise NotImplementedError

    def _propose(self, capability: str, payload: Any, config: Mapping[str, Any],
                 seed: int | None) -> tuple:
        """Run the donor. Return (payload, native_score_or_None). Raise DonorError on failure."""
        raise NotImplementedError

    # -- public surface -------------------------------------------------------------------
    def identity(self) -> DonorIdentity:
        return self._identity()

    def capabilities(self) -> list:
        return list(self._capabilities())

    def capability_names(self) -> list:
        return [c.name for c in self.capabilities()]

    def check_config(self, config: Mapping[str, Any]) -> dict:
        """Strict (T7). An unknown key is a caller error, not something to ignore: a wrapper
        that drops a key records a configuration that never took effect."""
        unknown = sorted(set(config) - set(self.accepted_config))
        if unknown:
            raise DonorError(self.identity().name, "config",
                             "unknown configuration key(s) " + repr(unknown)
                             + "; accepted: " + repr(sorted(self.accepted_config)))
        return dict(config)

    def propose(self, capability: str, payload: Any, config: Mapping[str, Any] | None = None,
                seed: int | None = None) -> DonorArtifact:
        """Invoke one capability and return a provenance-carrying artifact."""
        ident = self.identity()
        if capability not in self.capability_names():
            raise DonorError(ident.name, "capability",
                             "unknown capability " + repr(capability)
                             + "; available: " + repr(self.capability_names()))
        cfg = self.check_config(config or {})
        try:
            out, native = self._propose(capability, payload, cfg, seed)
        except DonorError:
            raise
        except Exception as e:                                        # noqa: BLE001
            # T10: typed and preserved. Never an empty success.
            raise DonorError(ident.name, "propose",
                             "donor raised during " + repr(capability), e)
        return DonorArtifact(
            donor=ident.name, donor_version=ident.version, upstream=ident.upstream,
            capability=capability, config=cfg, seed=seed,
            input_digest=canonical_digest(payload), output_digest=canonical_digest(out),
            native_selection_relation=self.native_selection_relation.as_dict(),
            native_score=native, payload=out, environment=environment_stamp(),
        )

    def manifest(self) -> dict:
        """Machine-readable description of this adapter, for the donor inventory."""
        return {
            "identity": self.identity().as_dict(),
            "native_selection_relation": self.native_selection_relation.as_dict(),
            "accepted_config": sorted(self.accepted_config),
            "capabilities": [dataclasses.asdict(c) for c in self.capabilities()],
        }


# -- registry -----------------------------------------------------------------------------
registry: dict = {}


def register(name: str) -> Callable:
    def deco(cls):
        registry[name] = cls
        return cls
    return deco


def get(name: str) -> DonorAdapter:
    if name not in registry:
        raise KeyError("no donor adapter " + repr(name) + "; registered: " + repr(sorted(registry)))
    return registry[name]()


def available() -> list:
    """Adapters whose donor actually imports here. An adapter may be registered and its donor
    absent; that is VETTED_NOT_INSTALLED, not an error."""
    ok = []
    for name in sorted(registry):
        try:
            get(name).identity()
            ok.append(name)
        except Exception:                                             # noqa: BLE001
            continue
    return ok
