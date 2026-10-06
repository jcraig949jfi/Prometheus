"""Canonical bytes and digests (CONTRACT s1). The only place identity bytes are defined.

Canonical JSON: strings, integers, booleans, null, lists and objects only (no floats), UTF-8 with sorted
keys, separators "," and ":", ASCII escapes. Bytes that do not round-trip to themselves are refused."""
import hashlib
import json

TAG_WORK = "moonshot.epoch.work.v1"
TAG_RESULT = "moonshot.epoch.result.v1"


class CanonicalError(ValueError):
    """An object or byte string that is not canonical."""


def _check(o, path="$"):
    if o is None or isinstance(o, (bool, str, int)):          # a float is never an int
        return
    if isinstance(o, float):
        raise CanonicalError("float at {}: canonical objects are integer-only".format(path))
    if isinstance(o, (list, tuple)):
        for i, v in enumerate(o):
            _check(v, "{}[{}]".format(path, i))
        return
    if isinstance(o, dict):
        for k, v in o.items():
            if not isinstance(k, str):
                raise CanonicalError("non-string key at {}".format(path))
            _check(v, "{}.{}".format(path, k))
        return
    raise CanonicalError("{} at {} is not canonical".format(type(o).__name__, path))


def canonical_bytes(obj) -> bytes:
    _check(obj)
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("ascii")


def parse_canonical(data: bytes):
    try:
        obj = json.loads(data.decode("ascii"))
    except (UnicodeDecodeError, ValueError) as e:
        raise CanonicalError("not canonical JSON: {}".format(e)) from None
    if canonical_bytes(obj) != data:
        raise CanonicalError("bytes are not in canonical form")
    return obj


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tagged_digest(tag: str, obj) -> str:
    """Domain-separated SHA-256: sha256(TAG || 0x00 || canonical_json(obj))."""
    return hashlib.sha256(tag.encode("ascii") + b"\x00" + canonical_bytes(obj)).hexdigest()
