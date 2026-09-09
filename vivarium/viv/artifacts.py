"""C1 -- the immutable artifact slot, and the preflight that hydrates it.

THE ONE-SENTENCE CONTRACT. A slot names bytes by their DIGEST; a locator says
where a copy of them might be found; and preflight is the thing that refuses to
let the second decide anything the first did not already fix.

WHY THAT SENTENCE MATTERS TO THIS SEAT. Vivarium's whole reason to exist is
that a difference between two arms must be attributable to SELECTION, not to
execution. An artifact input is the first thing that has ever reached the
executor from outside the sealed spec, so it is the first real chance to
reopen that hole. The closure is arithmetic rather than diligence:

  * the DIGEST is inside work.payload, therefore inside spec_hash. Change the
    bytes an experiment consumes and you have changed its sealed identity.
  * the LOCATOR (which world, which artifact id) is NOT in the spec. It rides
    on the queue row beside created_by and arm_id, and reaches preflight only.
  * preflight verifies the resolved bytes against the sealed digest. So a
    locator has exactly two possible effects: the declared bytes arrive, or
    the run is REJECTED. There is no third outcome in which a locator changes
    what the experiment computes.

That is the property tests/test_h0h5_artifacts.py asserts directly: two rows
with different locators over byte-identical artifacts produce identical results
and identical spec hashes.

A DIGEST IS NOT AUTHORITY. Nothing here fetches bytes by digest. Resolution
goes through the engine's world-scoped read (F1), which serves content only to
a caller who owns a world the artifact is native to or was legally imported
into. Knowing a hash confers nothing -- and neither does having loaded those
same bytes a moment ago for somebody else, which is why the cache below is
keyed by authorization and not by digest.

A DIGEST IS NOT COMPATIBILITY EITHER. The right bytes in the wrong shape are
still the wrong input. The slot declares artifact_type, schema_version, codec,
expected_bytes and interface_id, and every one of them is a REJECTION
CONDITION checked against the content itself before any kind is called.

LOAD ONCE, THEN USE WHAT WAS VERIFIED. The verified bytes are retained for the
attempt and handed to the kind directly. Preflight never verifies one fetch and
then executes a second one -- that check/use gap is the classic way a
content-addressed store still ends up running unverified bytes.

THE KIND GETS NO CLIENTS. What crosses into the executor is a frozen mapping of
slot name to decoded, immutable data. No SFE client, no PEW client, no file
handle, no socket. See viv/executors.py, where the hand-off is a single call
with no client in scope.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

#: The EXACT keys of an artifact slot. Not a minimum -- the same rule the kind
#: parameter contract already applies one level up, applied one level down.
SLOT_FIELDS = ("digest", "artifact_type", "schema_version", "codec",
               "expected_bytes", "interface_id")

#: Rejection classes. Named constants because a receipt, a test and an inbox
#: finding must be able to say the same word about the same event.
ABSENT = "ARTIFACT_ABSENT"
DIGEST_MISMATCH = "ARTIFACT_DIGEST_MISMATCH"
SIZE_MISMATCH = "ARTIFACT_SIZE_MISMATCH"
UNAUTHORIZED = "ARTIFACT_UNAUTHORIZED_WORLD"
CACHE_WITHOUT_PERMISSION = "ARTIFACT_CACHE_WITHOUT_PERMISSION"
WRONG_TYPE = "ARTIFACT_WRONG_TYPE"
INCOMPATIBLE_INTERFACE = "ARTIFACT_INCOMPATIBLE_INTERFACE"
MISSING_DEPENDENCY = "ARTIFACT_MISSING_DEPENDENCY"
DEPENDENCY_CYCLE = "ARTIFACT_DEPENDENCY_CYCLE"
OVERSIZE = "ARTIFACT_OVERSIZE"
MALFORMED = "ARTIFACT_MALFORMED"
MUTABLE_LOOKUP = "ARTIFACT_MUTABLE_LOOKUP"
LIMIT_EXCEEDED = "ARTIFACT_LIMIT_EXCEEDED"
CONTRACT_INVALID = "ARTIFACT_CONTRACT_INVALID"
LOCATOR_MISSING = "ARTIFACT_LOCATOR_MISSING"

REJECTION_CLASSES = (ABSENT, DIGEST_MISMATCH, SIZE_MISMATCH, UNAUTHORIZED,
                     CACHE_WITHOUT_PERMISSION, WRONG_TYPE,
                     INCOMPATIBLE_INTERFACE, MISSING_DEPENDENCY,
                     DEPENDENCY_CYCLE, OVERSIZE, MALFORMED, MUTABLE_LOOKUP,
                     LIMIT_EXCEEDED, CONTRACT_INVALID, LOCATOR_MISSING)


class PreflightRejected(RuntimeError):
    """Preflight refused. Carries the class, the slot and what was seen.

    A rejection is an OPERATIONAL receipt and never a scientific observation:
    nothing was measured, so nothing is recorded as measured. See C1's last
    line -- "rejection creates an operational receipt and no scientific
    success observation".
    """

    def __init__(self, rejection_class: str, message: str, *,
                 slot: Optional[str] = None, detail: Optional[dict] = None):
        if rejection_class not in REJECTION_CLASSES:
            raise ValueError("unknown rejection class %r" % (rejection_class,))
        self.rejection_class = rejection_class
        self.slot = slot
        self.detail = dict(detail or {})
        super().__init__("%s%s: %s"
                         % (rejection_class,
                            " [slot %s]" % slot if slot else "", message))

    def as_receipt(self) -> dict:
        return {"rejected": True, "rejection_class": self.rejection_class,
                "slot": self.slot, "message": str(self), "detail": self.detail}


# ------------------------------------------------------------------ limits
@dataclass(frozen=True)
class Limits:
    """The alpha operational profile, or lower. Section C4 proposes 16 MiB of
    total input artifacts per job; the rest are this seat's own, set low
    because an alpha limit that never fires teaches nothing about enforcement.

    Every one of these is checked BEFORE runtime state is constructed, which is
    the whole point: a limit applied after the allocation is a description.
    """
    total_bytes: int = 16 * 1024 * 1024
    per_artifact_bytes: int = 4 * 1024 * 1024
    max_items: int = 4096
    max_depth: int = 3            # closure nesting, root = depth 0
    max_closure: int = 16         # artifacts in one attempt's closure
    max_trace_bytes: int = 8 * 1024 * 1024

    def as_dict(self) -> dict:
        return {"total_bytes": self.total_bytes,
                "per_artifact_bytes": self.per_artifact_bytes,
                "max_items": self.max_items, "max_depth": self.max_depth,
                "max_closure": self.max_closure,
                "max_trace_bytes": self.max_trace_bytes}


ALPHA = Limits()


# ------------------------------------------------------------------ codecs
def _decode_canonical_json(raw: bytes) -> Any:
    """canonical-json-v1: the ONLY encoding this alpha accepts.

    Round-trip strict. A payload that parses but does not re-encode to the
    identical bytes is REFUSED, because then two different byte strings would
    denote the same object -- and two digests for one input is exactly the
    ambiguity a content-addressed contract exists to remove.
    """
    try:
        obj = json.loads(raw.decode("utf-8"))
    except Exception as exc:                        # noqa: BLE001
        raise PreflightRejected(
            MALFORMED, "content is not valid UTF-8 canonical JSON: %s" % exc
        ) from exc
    again = canonical_bytes(obj)
    if again != raw:
        raise PreflightRejected(
            MALFORMED,
            "content parses but is not CANONICAL: re-encoding gives %d bytes, "
            "not the %d supplied. Two byte strings denoting one object means "
            "two digests for one input." % (len(again), len(raw)))
    return obj


CODECS = {"canonical-json-v1": _decode_canonical_json}


def canonical_bytes(obj: Any) -> bytes:
    """Produce canonical-json-v1 bytes. Shared with the producer side so a
    fixture and the loader cannot disagree about what canonical means."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def digest_of(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


# -------------------------------------------------------------- interfaces
def _check_boolean_inputs_v1(obj: Any, limits: "Limits") -> dict:
    """boolean-inputs-v1: an ORDERED list of fixed-width Boolean input rows.

    Ordered, because H1's first-witness semantics are defined by the order the
    cases are tried; a set would silently destroy that. Fixed width, because a
    ragged row is a different interface wearing the same name.
    """
    if not isinstance(obj, dict):
        raise PreflightRejected(MALFORMED, "content must be an object")
    n_bits = obj.get("n_bits")
    items = obj.get("items")
    if (not isinstance(n_bits, int) or isinstance(n_bits, bool)
            or not 1 <= n_bits <= 16):
        raise PreflightRejected(
            MALFORMED, "n_bits must be an integer in 1..16, got %r" % (n_bits,))
    if not isinstance(items, list):
        raise PreflightRejected(MALFORMED, "items must be a list")
    if len(items) > limits.max_items:
        raise PreflightRejected(
            LIMIT_EXCEEDED, "item count %d exceeds the declared limit %d"
            % (len(items), limits.max_items),
            detail={"limit": "max_items", "observed": len(items)})
    for i, row in enumerate(items):
        if not isinstance(row, list) or len(row) != n_bits:
            raise PreflightRejected(
                MALFORMED, "item %d is not a list of %d bits: %r"
                % (i, n_bits, row))
        for b in row:
            if isinstance(b, bool) or b not in (0, 1):
                raise PreflightRejected(
                    MALFORMED, "item %d contains %r; rows are 0/1 integers "
                    "(and not booleans, which JSON round-trips as true/false "
                    "and would change the bytes)" % (i, b))
    return {"n_bits": n_bits, "item_count": len(items)}


#: interface_id -> (artifact_type it belongs to, checker). An interface is
#: owned by exactly one type: "the same bytes under another name" is precisely
#: the confusion the interface id exists to prevent.
INTERFACES = {
    "boolean-inputs-v1": ("failure_input_set", _check_boolean_inputs_v1),
}

#: artifact_type -> the schema versions this build can read.
ARTIFACT_TYPES = {"failure_input_set": {"1"}}


# ------------------------------------------------------------------- cache
@dataclass
class LoaderCache:
    """Bytes already verified in this attempt, keyed by AUTHORIZATION.

    THE DEFECT THIS SHAPE EXISTS TO PREVENT. The obvious cache is
    digest -> bytes, and it is a permission bypass: once any caller has loaded
    an artifact, the next caller gets a hit and the world-scoped read that was
    the entire authorization mechanism is never performed. C1 says it in one
    line -- "verify authorization before serving a shared cache hit" -- and a
    digest-keyed dictionary cannot do that, whatever checks surround it.

    So an entry records WHO was authorized for it. A caller not in that set
    misses, re-resolves through the engine, and is refused there. `refused_hits`
    counts exactly those events, so the receipt can show the bypass being
    declined rather than merely asserting it cannot happen.
    """
    _bytes: Dict[str, bytes] = field(default_factory=dict)
    _authorized: Dict[str, set] = field(default_factory=dict)
    hits: int = 0
    misses: int = 0
    refused_hits: int = 0

    def get(self, digest: str, principal: Tuple[str, str]) -> Optional[bytes]:
        if digest not in self._bytes:
            self.misses += 1
            return None
        if principal not in self._authorized.get(digest, set()):
            self.refused_hits += 1
            self.misses += 1
            return None
        self.hits += 1
        return self._bytes[digest]

    def put(self, digest: str, raw: bytes, principal: Tuple[str, str]) -> None:
        self._bytes[digest] = raw
        self._authorized.setdefault(digest, set()).add(principal)

    def stats(self) -> dict:
        return {"hits": self.hits, "misses": self.misses,
                "refused_hits": self.refused_hits,
                "distinct_artifacts": len(self._bytes)}


# ------------------------------------------------------------ slot contract
def check_slot(name: str, slot: Any) -> list:
    """Reasons this slot value is not a well-formed artifact slot.

    Exact keys, no defaults, no placeholders. C1: "All values must be resolved
    before admission; placeholders never enter a queue." This runs at ADMISSION
    (through viv.kinds) as well as in preflight, so an unresolvable slot is
    refused before it is ever claimed.
    """
    if not isinstance(slot, dict):
        return ["artifact slot %r must be an object with exactly %s"
                % (name, list(SLOT_FIELDS))]
    reasons = []
    missing = sorted(set(SLOT_FIELDS) - set(slot))
    if missing:
        reasons.append("artifact slot %r is missing %s" % (name, missing))
    extra = sorted(set(slot) - set(SLOT_FIELDS))
    if extra:
        reasons.append(
            "artifact slot %r carries unknown key(s) %s; the slot contract is "
            "exact, and an unread key inside a hashed spec is a channel"
            % (name, extra))
    if reasons:
        return reasons

    digest = slot["digest"]
    if (not isinstance(digest, str) or not digest.startswith("sha256:")
            or len(digest) != 71
            or any(c not in "0123456789abcdef" for c in digest[7:])):
        reasons.append(
            "artifact slot %r digest must be 'sha256:' + 64 lowercase hex "
            "digits, got %r" % (name, digest))
    atype = slot["artifact_type"]
    if atype not in ARTIFACT_TYPES:
        reasons.append("artifact slot %r declares unknown artifact_type %r "
                       "(known: %s)"
                       % (name, atype, sorted(ARTIFACT_TYPES)))
    elif slot["schema_version"] not in ARTIFACT_TYPES[atype]:
        reasons.append(
            "artifact slot %r declares schema_version %r, which this build "
            "cannot read for %s (readable: %s)"
            % (name, slot["schema_version"], atype,
               sorted(ARTIFACT_TYPES[atype])))
    if slot["codec"] not in CODECS:
        reasons.append("artifact slot %r declares unknown codec %r (known: %s)"
                       % (name, slot["codec"], sorted(CODECS)))
    iface = slot["interface_id"]
    if iface not in INTERFACES:
        reasons.append("artifact slot %r declares unknown interface_id %r "
                       "(known: %s)" % (name, iface, sorted(INTERFACES)))
    elif atype in ARTIFACT_TYPES and INTERFACES[iface][0] != atype:
        reasons.append(
            "artifact slot %r pairs interface_id %r with artifact_type %r, but "
            "that interface belongs to %r; the same bytes under another name "
            "is the confusion an interface id exists to prevent"
            % (name, iface, atype, INTERFACES[iface][0]))
    n = slot["expected_bytes"]
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        reasons.append("artifact slot %r expected_bytes must be a positive "
                       "integer, got %r" % (name, n))
    return reasons


# ---------------------------------------------------------------- locators
#: A locator addresses a COPY. Exactly two fields, and neither may be a
#: pattern, a URL or a moving name: C1 forbids "latest, glob, mutable URL or
#: directory scan", and the only way to keep that promise is to refuse the
#: syntax outright rather than hope no producer uses it.
LOCATOR_FIELDS = ("source_world", "source_artifact")

_MUTABLE_TOKENS = ("latest", "*", "?", "://", "HEAD", "head", "current",
                   "newest", "..")


def check_locator(name: str, loc: Any) -> list:
    if not isinstance(loc, dict):
        return ["locator for slot %r must be an object with exactly %s"
                % (name, list(LOCATOR_FIELDS))]
    reasons = []
    missing = sorted(set(LOCATOR_FIELDS) - set(loc))
    extra = sorted(set(loc) - set(LOCATOR_FIELDS))
    if missing:
        reasons.append("locator for slot %r is missing %s" % (name, missing))
    if extra:
        reasons.append("locator for slot %r carries unknown key(s) %s"
                       % (name, extra))
    for f in LOCATOR_FIELDS:
        v = loc.get(f)
        if v is None:
            continue
        if not isinstance(v, str) or not v:
            reasons.append("locator for slot %r: %s must be a non-empty "
                           "string, got %r" % (name, f, v))
            continue
        for tok in _MUTABLE_TOKENS:
            if tok in v:
                reasons.append(
                    "locator for slot %r: %s contains %r, which is a MUTABLE "
                    "lookup (a moving name, a pattern or a URL). A locator "
                    "names one immutable row; anything that can resolve "
                    "differently tomorrow is refused here rather than "
                    "discovered later." % (name, f, tok))
                break
    return reasons
