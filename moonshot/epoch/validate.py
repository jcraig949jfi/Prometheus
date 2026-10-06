"""Validation, audit replay, contest / taint resolution (CONTRACT s6, s7). Never a worker's act."""
from enum import Enum


class Resolution(str, Enum):
    UPHELD = "UPHELD"
    OVERTURNED = "OVERTURNED"
    UNRESOLVED = "UNRESOLVED"


def validate_chain(store, chain_id, *, replay_indices=(), runner=None) -> dict:
    raise NotImplementedError("C-008-T001")


def audit(store, chain_id, epoch_index, *, runner=None, auditor_id="") -> dict:
    raise NotImplementedError("C-008-T001")


def resolve(store, chain_id, *, runners) -> Resolution:
    raise NotImplementedError("C-008-T001")


def chain_status(store, chain_id) -> str:
    raise NotImplementedError("C-008-T001")
