"""Slots on a dedicated remote, under refs/moonshot/<namespace>/ (CONTRACT s3).

PER_CHAIN: one ref per slot. SINGLE_REF: one index ref whose tree holds every slot's pointer
(workgraph's claim-is-a-push-to-main, emulated off the production repository)."""
from dataclasses import dataclass
from typing import Optional

from .gitio import ForbiddenRef, ForbiddenRemote  # noqa: F401  (re-exported)

PER_CHAIN = "per_chain"
SINGLE_REF = "single_ref"
LAYOUTS = (PER_CHAIN, SINGLE_REF)

WORKER = "worker"
COORDINATOR = "coordinator"
VALIDATOR = "validator"
RESOLVER = "resolver"
ROLES = (WORKER, COORDINATOR, VALIDATOR, RESOLVER)

# OP-LC1 #1: never the Prometheus repository. A remote is refused if its normalized URL (lowercase, "\\" and ":"
# as "/", no trailing "/" or ".git") contains a denylisted path, OR its last path segment is "prometheus" -- which
# also refuses a local clone such as D:\Prometheus used by mistake as the data-plane remote.
DEFAULT_DENYLIST = ("jcraig949jfi/prometheus",)


@dataclass(frozen=True)
class PublishedEpoch:
    epoch_index: int
    commit: str
    manifest: dict
    work_id: str
    epoch_digest: str


@dataclass(frozen=True)
class ChainView:
    chain_id: str
    head_commit: str
    head_index: int
    genesis_obj: dict
    contest: Optional[dict]


class Store:
    def __init__(self, remote_url, *, namespace, layout, local_dir, role=WORKER, actor="",
                 denylist=DEFAULT_DENYLIST, push_hook=None):
        self.remote_url = remote_url
        self.namespace = namespace
        self.layout = layout
        self.local_dir = local_dir
        self.role = role
        self.actor = actor
        self.denylist = tuple(denylist)
        self.push_hook = push_hook

    def close(self):
        pass

    def create_chain(self, genesis) -> str:
        raise NotImplementedError("C-008-T001")

    def chain_view(self, chain_id) -> ChainView:
        raise NotImplementedError("C-008-T001")

    def lineage(self, chain_id) -> list:
        raise NotImplementedError("C-008-T001")

    def epoch_bytes(self, commit) -> dict:
        raise NotImplementedError("C-008-T001")

    def contest(self, chain_id):
        raise NotImplementedError("C-008-T001")

    def validation(self, chain_id):
        raise NotImplementedError("C-008-T001")

    def read_receipts(self) -> list:
        raise NotImplementedError("C-008-T001")
