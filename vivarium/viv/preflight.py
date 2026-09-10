"""Preflight -- resolve, verify, bound, freeze, and only then execute.

The order below is the contract, and it is the order for a reason. Every step
is a REJECTION CONDITION evaluated before the next one allocates anything:

  1. contract      exact slot keys, exact locator keys, resolved values only
  2. budget        debit the enforceable byte counter BEFORE the fetch
  3. resolve       through the engine's world-scoped read; a digest is not
                   authority and this seat has no route that pretends it is
  4. size          the bytes are the declared count, and within the per-
                   artifact and total limits
  5. digest        the bytes hash to the SEALED digest, or nothing runs
  6. codec         decodes, and re-encodes to the identical bytes
  7. type          the content's own header agrees with the slot's declaration
  8. interface     the shape check that owns this interface id passes
  9. closure       dependencies resolved the same way, depth/count bounded,
                   cycles refused, manifest hashed
 10. freeze        immutable inputs constructed; the kind is called with those
                   and with no client of any kind

A rejection at any step is an OPERATIONAL receipt. No observation is written,
because nothing was measured -- C1's own last line.

WHAT THE LOAD RECEIPT IS FOR. It is the document that lets a later reader
establish, without trusting this code, that the bytes an experiment consumed
were the bytes its sealed identity named: the digest verified, the size, the
authorization basis the engine reported (NATIVE or IMPORTED, with the import's
event seq), the closure manifest hash, and the limits in force. It travels with
the result and into the fossil; it is not a log line.

RETRY REVALIDATES. A new attempt runs all of this again from step 1. The
verified bytes are retained only for the attempt that verified them, so there
is no window in which attempt N+1 uses attempt N's trust.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Callable, Dict, List, Optional, Tuple

from . import artifacts as _a


class BudgetExhausted(RuntimeError):
    """The enforceable input-byte counter refused the load.

    A DISTINCT status, never folded into a rejection class: "we could not
    afford to look" and "we looked and it was wrong" are different facts about
    an experiment, and the second one is evidence while the first is not.
    """

    def __init__(self, message: str, *, detail: Optional[dict] = None):
        self.detail = dict(detail or {})
        super().__init__(message)


# --------------------------------------------------------------- immutable
def freeze(obj: Any) -> Any:
    """Deep-freeze decoded JSON: dict -> read-only mapping, list -> tuple.

    Not decoration. The kind is handed exactly this, and the receipt asserts
    the digest of exactly the bytes it came from; if the kind could mutate its
    inputs, the receipt would be describing something other than what ran.
    """
    if isinstance(obj, dict):
        return MappingProxyType({k: freeze(v) for k, v in obj.items()})
    if isinstance(obj, list):
        return tuple(freeze(v) for v in obj)
    return obj


def thaw(obj: Any) -> Any:
    """Frozen -> plain JSON types. For hashing and for receipts only."""
    if isinstance(obj, MappingProxyType):
        return {k: thaw(v) for k, v in obj.items()}
    if isinstance(obj, tuple):
        return [thaw(v) for v in obj]
    return obj


@dataclass(frozen=True)
class LoadedArtifact:
    """One verified artifact: its sealed identity, its frozen content, and the
    dependencies it declared -- each itself a LoadedArtifact."""
    digest: str
    artifact_type: str
    schema_version: str
    interface_id: str
    n_bytes: int
    data: Any                                  # frozen
    dependencies: Tuple["LoadedArtifact", ...] = ()
    shape: Any = None                          # frozen interface facts

    def all_items(self) -> tuple:
        """Root items followed by each dependency's, depth-first in DECLARED
        order. The order is part of the interface: boolean-inputs-v1 is an
        ORDERED set of cases and a consumer that reordered them would be
        running a different experiment."""
        out = list(self.data.get("items", ()))
        for dep in self.dependencies:
            out.extend(dep.all_items())
        return tuple(out)


# ---------------------------------------------------------------- resolver
class SfeResolver:
    """Resolve a locator through the engine's authorized, world-scoped read.

    There are exactly two paths and no third:

      NATIVE    the artifact already lives in the execution world.
      IMPORTED  it is imported from the producer world by the engine's own
                explicit import, which enforces ownership, the destination
                world's sharing policy and -- across clients -- a registered
                bilateral topology group.

    Both end at GET /worlds/{execution_world}/artifacts/{id}/content, which
    serves content only to a caller who owns that world. So authorization is
    the ENGINE's decision every time, and this class cannot widen it: the
    worst it can do is ask and be refused.
    """

    def __init__(self, client, *, execution_world: str, client_id: str,
                 log: Callable[..., None] = lambda *_a: None):
        self.c = client
        self.world = execution_world
        self.client_id = client_id
        self.log = log
        self.calls = 0
        self.imports = 0

    @property
    def principal(self) -> Tuple[str, str]:
        return (self.client_id, self.world)

    def resolve(self, digest: str, locator: dict, *,
                expected_bytes: Optional[int] = None) -> Tuple[bytes, dict]:
        """Resolve one locator, asserting WHICH object was meant AT THE ENGINE.

        TRACKA-PREFLIGHT-1. This used to fetch and then compare the digest in
        the client, which meant the bytes had already been served before
        anything noticed they were the wrong ones. The engine now takes the
        assertion on the read path and answers 422 with NO BYTES -- and it
        checks it only AFTER authorization and the world-scoped lookup, so a
        caller who knows only a hash still gets 404 and a digest still confers
        nothing.

        The client-side comparison in `Preflight.load` is KEPT. It is no longer
        the guarantee; it is defence in depth over the one span the engine
        cannot see, which is the wire between the engine and this process.
        """
        import base64
        from sfclient import EngineError                     # noqa: PLC0415

        src_world = locator["source_world"]
        src_art = locator["source_artifact"]
        self.calls += 1
        aid, imported = src_art, None
        try:
            if src_world != self.world:
                imp = self.c.import_artifact(self.world, src_world, src_art)
                self.imports += 1
                aid = imp["artifact_id"]
                imported = imp
            content = self.c.artifact_content(
                self.world, aid, expected_blob_hash=digest,
                expected_bytes=expected_bytes)
        except EngineError as exc:
            raise _engine_error_to_rejection(exc, digest, locator) from exc

        raw = base64.b64decode(content["content_b64"])
        record = {
            "execution_world": self.world,
            "execution_artifact_id": aid,
            "source_world": src_world,
            "source_artifact": src_art,
            "origin": content.get("origin"),
            "engine_blob_hash": content.get("blob_hash"),
            "engine_source_hash": content.get("source_hash"),
            "import_seq": content.get("import_seq"),
            "visibility_basis": content.get("visibility_basis"),
            "kind": content.get("kind"),
            "authorized_as": self.client_id,
            "imported_now": bool(imported),
            # WHERE the identity was enforced, recorded rather than assumed.
            # A receipt that said "digest verified" without saying by whom
            # would read the same before and after TRACKA-PREFLIGHT-1.
            "digest_gate": "engine (expected_blob_hash on the read path)",
            "size_gate": ("engine (expected_bytes)" if expected_bytes is not None
                          else "client only"),
            "engine_resolution": content.get("resolution"),
        }
        return raw, record


def _engine_error_to_rejection(exc, digest: str, locator: dict):
    """Map the engine's own typed status onto a rejection class. The engine
    decided; this only records WHICH decision it made."""
    detail = exc.detail if isinstance(exc.detail, dict) else {"detail": exc.detail}
    code = (detail.get("error") if isinstance(detail, dict) else None) or ""
    base = {"http": exc.status, "engine_code": code,
            "digest": digest, "locator": dict(locator),
            "engine_message": (detail or {}).get("message")}
    if exc.status == 404:
        return _a.PreflightRejected(
            _a.ABSENT, "the engine has no such artifact for this locator "
                       "(%s)" % base["engine_message"], detail=base)
    if exc.status == 403:
        return _a.PreflightRejected(
            _a.UNAUTHORIZED,
            "the engine refused this world/artifact to this client (%s). A "
            "digest is not authority: %s"
            % (code, base["engine_message"]), detail=base)
    if exc.status == 409 and code == "budget_exhausted":
        return BudgetExhausted(
            "the engine's budget refused the resolution: %s"
            % base["engine_message"], detail=base)
    if exc.status == 422:
        # The engine's read-path gate. It served NO BYTES, which is the whole
        # improvement over comparing after the fact -- and the rejection class
        # is the one the locator earned, not a generic contract failure.
        message = (base["engine_message"] or "").lower()
        if "byte" in message or "size" in message:
            return _a.PreflightRejected(
                _a.SIZE_MISMATCH,
                "the engine refused the read: %s" % base["engine_message"],
                detail=base)
        return _a.PreflightRejected(
            _a.DIGEST_MISMATCH,
            "the engine refused the read before serving any bytes: %s. The "
            "locator addressed an object; it did not address the one the spec "
            "sealed." % base["engine_message"], detail=base)
    return _a.PreflightRejected(
        _a.CONTRACT_INVALID,
        "the engine rejected the resolution (HTTP %s %s): %s"
        % (exc.status, code, base["engine_message"]), detail=base)


# --------------------------------------------------------------- the thing
@dataclass
class Preflight:
    """One attempt's hydration. Stateful only for the duration of one attempt.

    `debit` is the ENFORCEABLE counter. It is called BEFORE each fetch with the
    bytes that fetch is declared to cost, because a debit taken afterwards is
    an accounting entry and not a limit. It may raise BudgetExhausted; nothing
    is fetched when it does.

    TRACKA-DEBIT-1. It is called as `debit(resource, amount, act=...)`, where
    `act` names WHAT is being paid for: the slot, the digest, the locator and
    the ordinal of the fetch within this attempt. Without it the strongest
    idempotency key an integrator could build was the ordinal alone, which is
    a key on the POSITION rather than on the act -- so two attempts that
    fetched the same artifact in a different order would look like different
    spends, and two fetches of different artifacts at the same position would
    look like the same one. A `debit` that accepts only two arguments is still
    called correctly; the third is passed as a keyword and older hooks are
    detected rather than crashed into.
    """
    resolver: Any
    locators: Dict[str, dict]
    limits: _a.Limits = _a.ALPHA
    debit: Optional[Callable[[str, float], Any]] = None
    cache: _a.LoaderCache = field(default_factory=_a.LoaderCache)
    log: Callable[..., None] = lambda *_a: None

    _bytes_loaded: int = 0
    _bytes_debited: int = 0
    _closure: List[dict] = field(default_factory=list)
    _seen: Dict[str, LoadedArtifact] = field(default_factory=dict)
    _fetches: int = 0
    _seconds: float = 0.0
    #: True iff the supplied debit hook could not accept the act. Reported.
    _debit_hook_narrow: bool = False
    #: digest -> whatever the debit hook returned (a reservation, or None).
    #: Carried so the caller that RESERVED can settle the same act, rather
    #: than re-deriving which reservation belonged to which fetch.
    _reservations: Dict[str, Any] = field(default_factory=dict)

    # -- one artifact ------------------------------------------------------
    def _locator_for(self, digest: str, slot: str) -> dict:
        loc = self.locators.get(digest)
        if loc is None:
            raise _a.PreflightRejected(
                _a.LOCATOR_MISSING,
                "no locator was supplied for digest %s. The sealed spec names "
                "the bytes; the row must say where a copy of them is. An "
                "address book keyed by digest is how those two stay "
                "independent." % digest, slot=slot,
                detail={"digest": digest,
                        "locators_supplied": sorted(self.locators)})
        reasons = _a.check_locator(slot, loc)
        if reasons:
            cls = (_a.MUTABLE_LOOKUP if any("MUTABLE" in r for r in reasons)
                   else _a.CONTRACT_INVALID)
            raise _a.PreflightRejected(cls, "; ".join(reasons), slot=slot,
                                       detail={"digest": digest})
        return loc

    def _fetch(self, digest: str, slot: str, declared_bytes: int) -> Tuple[bytes, dict]:
        loc = self._locator_for(digest, slot)

        # BEFORE the fetch. See the class docstring.
        if self.debit is not None:
            act = {"slot": slot, "digest": digest,
                   "source_world": loc["source_world"],
                   "source_artifact": loc["source_artifact"],
                   "fetch_ordinal": self._fetches + 1,
                   "declared_bytes": declared_bytes}
            try:
                self._reservations[digest] = self.debit(
                    "artifact_bytes", declared_bytes, act=act)
            except TypeError as exc:
                # An older two-argument hook. Called correctly rather than
                # left to fail, and the fallback is NOT silent -- a caller
                # whose reservation is keyed on the ordinal alone should know
                # that is what it got.
                if "act" not in str(exc):
                    raise
                self.debit("artifact_bytes", declared_bytes)
                self._debit_hook_narrow = True
        self._bytes_debited += declared_bytes

        principal = self.resolver.principal
        cached = self.cache.get(digest, principal)
        if cached is not None:
            return cached, {"served_from": "attempt_cache",
                            "authorized_as": principal[0],
                            "execution_world": principal[1],
                            "source_world": loc["source_world"],
                            "source_artifact": loc["source_artifact"]}

        t0 = time.perf_counter()
        try:
            raw, record = self.resolver.resolve(digest, loc,
                                                expected_bytes=declared_bytes)
        except TypeError as exc:
            # A resolver from before the engine took the size assertion. It is
            # called correctly rather than left to fail, and the receipt says
            # the size gate was client-only for that fetch.
            if "expected_bytes" not in str(exc):
                raise
            raw, record = self.resolver.resolve(digest, loc)
        self._seconds += time.perf_counter() - t0
        self._fetches += 1
        record["served_from"] = "engine"
        # Authorization happened; only now may these bytes be reusable, and
        # only for the principal the engine actually authorized.
        self.cache.put(digest, raw, principal)
        return raw, record

    def load(self, slot_name: str, slot: dict, *, depth: int = 0,
             chain: Tuple[str, ...] = ()) -> LoadedArtifact:
        """Resolve and verify ONE slot and its closure. Recursive over
        dependencies; every step here is a rejection condition."""
        reasons = _a.check_slot(slot_name, slot)
        if reasons:
            raise _a.PreflightRejected(_a.CONTRACT_INVALID, "; ".join(reasons),
                                       slot=slot_name)
        digest = slot["digest"]

        if digest in chain:
            raise _a.PreflightRejected(
                _a.DEPENDENCY_CYCLE,
                "dependency cycle: %s reappears in its own closure (%s). Alpha "
                "forbids cycles -- a cycle has bounded semantics only inside a "
                "component language that declares them, and none is admitted "
                "here." % (digest, " -> ".join(chain + (digest,))),
                slot=slot_name, detail={"chain": list(chain + (digest,))})
        if depth > self.limits.max_depth:
            raise _a.PreflightRejected(
                _a.LIMIT_EXCEEDED,
                "closure depth %d exceeds the declared limit %d"
                % (depth, self.limits.max_depth), slot=slot_name,
                detail={"limit": "max_depth", "observed": depth})
        if len(self._closure) >= self.limits.max_closure:
            raise _a.PreflightRejected(
                _a.LIMIT_EXCEEDED,
                "closure would hold more than %d artifacts"
                % self.limits.max_closure, slot=slot_name,
                detail={"limit": "max_closure"})

        declared = slot["expected_bytes"]
        if declared > self.limits.per_artifact_bytes:
            # Refused on the DECLARATION, before a byte is fetched. A size
            # limit that only fires after the download is a measurement.
            raise _a.PreflightRejected(
                _a.OVERSIZE,
                "declares %d bytes; the per-artifact limit is %d. Refused "
                "before the fetch, not after it."
                % (declared, self.limits.per_artifact_bytes), slot=slot_name,
                detail={"limit": "per_artifact_bytes", "declared": declared})
        if self._bytes_loaded + declared > self.limits.total_bytes:
            raise _a.PreflightRejected(
                _a.OVERSIZE,
                "would take this attempt's inputs to %d bytes; the total limit "
                "is %d" % (self._bytes_loaded + declared,
                           self.limits.total_bytes),
                slot=slot_name, detail={"limit": "total_bytes",
                                        "already": self._bytes_loaded,
                                        "declared": declared})

        raw, record = self._fetch(digest, slot_name, declared)

        if len(raw) != declared:
            raise _a.PreflightRejected(
                _a.SIZE_MISMATCH,
                "resolved %d bytes; the slot declared %d. The declaration is "
                "inside the sealed hash, so this is a changed input, not a "
                "changed opinion about it." % (len(raw), declared),
                slot=slot_name,
                detail={"declared": declared, "resolved": len(raw), **record})
        if len(raw) > self.limits.per_artifact_bytes:
            raise _a.PreflightRejected(
                _a.OVERSIZE, "resolved %d bytes over the per-artifact limit %d"
                % (len(raw), self.limits.per_artifact_bytes), slot=slot_name,
                detail={"limit": "per_artifact_bytes"})

        actual = _a.digest_of(raw)
        if actual != digest:
            raise _a.PreflightRejected(
                _a.DIGEST_MISMATCH,
                "resolved bytes hash to %s, not the sealed %s. The locator "
                "found SOMETHING; it did not find what the spec sealed, and a "
                "locator is never allowed to decide that."
                % (actual, digest), slot=slot_name,
                detail={"sealed": digest, "resolved": actual, **record})

        decoder = _a.CODECS[slot["codec"]]
        try:
            obj = decoder(raw)
        except _a.PreflightRejected as exc:
            exc.slot = exc.slot or slot_name
            raise

        # The content's own header must agree with the slot's declaration.
        # Right bytes, wrong shape is still the wrong input.
        head_type = obj.get("artifact_type") if isinstance(obj, dict) else None
        head_schema = obj.get("schema_version") if isinstance(obj, dict) else None
        head_iface = obj.get("interface_id") if isinstance(obj, dict) else None
        if head_type != slot["artifact_type"]:
            raise _a.PreflightRejected(
                _a.WRONG_TYPE,
                "the slot declares artifact_type %r; the content says %r"
                % (slot["artifact_type"], head_type), slot=slot_name,
                detail={"declared": slot["artifact_type"], "content": head_type,
                        "digest": digest})
        if head_schema != slot["schema_version"]:
            raise _a.PreflightRejected(
                _a.WRONG_TYPE,
                "the slot declares schema_version %r; the content says %r"
                % (slot["schema_version"], head_schema), slot=slot_name,
                detail={"declared": slot["schema_version"],
                        "content": head_schema, "digest": digest})
        if head_iface != slot["interface_id"]:
            raise _a.PreflightRejected(
                _a.INCOMPATIBLE_INTERFACE,
                "the slot declares interface_id %r; the content implements "
                "%r. These bytes may be perfectly valid -- they are not this "
                "input." % (slot["interface_id"], head_iface), slot=slot_name,
                detail={"declared": slot["interface_id"],
                        "content": head_iface, "digest": digest})

        _owner, checker = _a.INTERFACES[slot["interface_id"]]
        try:
            shape = checker(obj, self.limits)
        except _a.PreflightRejected as exc:
            exc.slot = exc.slot or slot_name
            raise

        self._bytes_loaded += len(raw)

        # -- closure -------------------------------------------------------
        deps_declared = obj.get("dependencies", []) if isinstance(obj, dict) else []
        if not isinstance(deps_declared, list):
            raise _a.PreflightRejected(
                _a.MALFORMED, "dependencies must be a list", slot=slot_name)
        loaded_deps: List[LoadedArtifact] = []
        for i, dep in enumerate(deps_declared):
            dep_name = "%s.dependencies[%d]" % (slot_name, i)
            dep_reasons = _a.check_slot(dep_name, dep)
            if dep_reasons:
                raise _a.PreflightRejected(
                    _a.MISSING_DEPENDENCY,
                    "a declared dependency is not a resolvable slot: %s"
                    % "; ".join(dep_reasons), slot=dep_name,
                    detail={"parent": digest})
            if dep["digest"] not in self.locators:
                raise _a.PreflightRejected(
                    _a.MISSING_DEPENDENCY,
                    "dependency %s of %s has no locator; the closure is "
                    "incomplete and an incomplete closure is not an input"
                    % (dep["digest"], digest), slot=dep_name,
                    detail={"parent": digest, "dependency": dep["digest"]})
            loaded_deps.append(self.load(dep_name, dep, depth=depth + 1,
                                         chain=chain + (digest,)))

        art = LoadedArtifact(
            digest=digest, artifact_type=slot["artifact_type"],
            schema_version=slot["schema_version"],
            interface_id=slot["interface_id"], n_bytes=len(raw),
            data=freeze(obj), dependencies=tuple(loaded_deps),
            shape=freeze(shape))
        self._seen[digest] = art
        self._closure.append({
            "slot": slot_name, "digest": digest, "depth": depth,
            "bytes": len(raw), "artifact_type": slot["artifact_type"],
            "schema_version": slot["schema_version"],
            "interface_id": slot["interface_id"], "codec": slot["codec"],
            "shape": shape, "resolution": record,
            "reservation": self._reservations.get(digest),
            "dependencies": [d.digest for d in loaded_deps]})
        return art

    # -- the whole attempt -------------------------------------------------
    def hydrate(self, slots: Dict[str, dict]) -> Tuple[Dict[str, LoadedArtifact], dict]:
        """Load every declared slot in NAME ORDER and return (inputs, receipt).

        Name order, not dict order: two byte-identical specs must produce the
        same resolution sequence, and Python dict order is an artefact of how
        the JSON happened to be written.
        """
        inputs: Dict[str, LoadedArtifact] = {}
        t0 = time.perf_counter()
        try:
            for name in sorted(slots):
                inputs[name] = self.load(name, slots[name])
        except _a.PreflightRejected as exc:
            exc.reservations_open = [r for r in self._reservations.values()
                                     if r is not None]
            raise
        wall = time.perf_counter() - t0

        # NO UNUSED ADDRESSES. Admission cannot check this -- a closure is
        # discoverable only by reading the root's bytes -- but here the closure
        # is known, so an address nothing consumed is refused. An unread entry
        # travelling beside a sealed spec is a channel whether or not anyone
        # currently reads it, which is the same argument that makes an unknown
        # payload key a rejection rather than a comment.
        consumed = {c["digest"] for c in self._closure}
        unused = sorted(set(self.locators) - consumed)
        if unused:
            raise _a.PreflightRejected(
                _a.CONTRACT_INVALID,
                "the address book carries %d locator(s) nothing in the closure "
                "consumed: %s. An unread entry beside a sealed spec is a "
                "channel." % (len(unused), unused),
                detail={"unused": unused, "consumed": sorted(consumed)})

        manifest = [c["digest"] for c in self._closure]
        receipt = {
            "loaded": True,
            "slots": {n: {"digest": a.digest, "bytes": a.n_bytes,
                          "artifact_type": a.artifact_type,
                          "schema_version": a.schema_version,
                          "interface_id": a.interface_id,
                          "shape": thaw(a.shape),
                          "dependency_digests": [d.digest
                                                 for d in a.dependencies]}
                      for n, a in inputs.items()},
            "closure": self._closure,
            "closure_size": len(self._closure),
            "closure_manifest": manifest,
            "closure_manifest_hash": "sha256:" + hashlib.sha256(
                json.dumps(manifest, separators=(",", ":")).encode()
            ).hexdigest(),
            "bytes_loaded": self._bytes_loaded,
            "bytes_debited": self._bytes_debited,
            "engine_fetches": self._fetches,
            "cache": self.cache.stats(),
            "limits": self.limits.as_dict(),
            "resolve_seconds": round(self._seconds, 6),
            "wall_seconds": round(wall, 6),
            "verified": ["size", "digest", "codec_canonical", "artifact_type",
                         "schema_version", "interface_id", "closure"],
            "digest_gate": "engine+client",
            "debit_hook_carries_act": not self._debit_hook_narrow,
        }
        return inputs, receipt


def slots_of(spec: dict) -> Dict[str, dict]:
    """The artifact slots this spec's kind declares, taken from the KIND, never
    guessed from the payload's shape. A payload key that merely looks like a
    slot is not one."""
    from . import kinds as _kinds                            # noqa: PLC0415

    kind = _kinds.get(spec["work"]["kind"])
    if kind is None or not kind.artifact_slots:
        return {}
    payload = spec["work"]["payload"]
    # A slot declared `null` is a DECLARED ABSENCE: nothing to resolve, and
    # nothing to charge. It is not skipped as if it were missing -- the
    # admission contract already established that the key is present and that
    # this kind permits it to be empty.
    return {name: payload[name] for name in sorted(kind.artifact_slots)
            if payload.get(name) is not None}
