"""Canonical bytes and digests (CONTRACT s1). The only place identity bytes are defined."""

TAG_WORK = "moonshot.epoch.work.v1"
TAG_RESULT = "moonshot.epoch.result.v1"


class CanonicalError(ValueError):
    """An object or byte string that is not canonical."""


def canonical_bytes(obj) -> bytes:
    raise NotImplementedError("C-008-T001")


def parse_canonical(data: bytes):
    raise NotImplementedError("C-008-T001")


def sha256_hex(data: bytes) -> str:
    raise NotImplementedError("C-008-T001")


def tagged_digest(tag: str, obj) -> str:
    raise NotImplementedError("C-008-T001")
