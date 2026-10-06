"""Genesis, spec derivation, semantic identity and manifests (CONTRACT s2)."""
from dataclasses import dataclass

MANIFEST_KEYS = frozenset({
    "schema", "chain_id", "epoch_index", "runtime", "input_checkpoint_sha256", "spec_sha256", "work_id",
    "trace_sha256", "trace_bytes", "output_checkpoint_sha256", "output_checkpoint_bytes", "epoch_digest",
})


@dataclass(frozen=True)
class Genesis:
    obj: dict
    bytes: bytes
    initial_checkpoint: bytes

    @property
    def chain_id(self) -> str:
        return self.obj["chain_id"]


@dataclass(frozen=True)
class EpochResult:
    chain_id: str
    epoch_index: int
    spec: dict
    spec_bytes: bytes
    trace: bytes
    checkpoint: bytes
    manifest: dict
    manifest_bytes: bytes
    work_id: str
    epoch_digest: str


def make_genesis(chain_id, *, epochs, params, approved_code_sha, initial_checkpoint, runtime=None) -> Genesis:
    raise NotImplementedError("C-008-T001")


def derive_spec(genesis_obj: dict, epoch_index: int) -> dict:
    raise NotImplementedError("C-008-T001")


def work_id(input_checkpoint_sha256: str, spec_sha256: str, runtime: dict) -> str:
    raise NotImplementedError("C-008-T001")


def epoch_digest(work_id_: str, trace_sha256: str, output_checkpoint_sha256: str) -> str:
    raise NotImplementedError("C-008-T001")


def execute(genesis_obj: dict, epoch_index: int, input_checkpoint: bytes, runner=None) -> EpochResult:
    raise NotImplementedError("C-008-T001")


def verify_epoch(files: dict, input_checkpoint_sha256=None) -> list:
    raise NotImplementedError("C-008-T001")


def replay_chain(genesis: Genesis, upto: int, runner=None) -> list:
    raise NotImplementedError("C-008-T001")
