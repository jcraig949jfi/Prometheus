"""Genesis, spec derivation, semantic identity and manifests (CONTRACT s2).

work_id names the question (inputs + spec + runtime); epoch_digest is THE semantic identity of a
completed epoch (work_id + canonical outputs). Neither involves git, hosts, clocks or attempts."""
import re
from dataclasses import dataclass

from . import canonical as C
from . import runtime as R

GENESIS_SCHEMA = "moonshot.epoch.genesis.v1"
SPEC_SCHEMA = "moonshot.epoch.spec.v1"
MANIFEST_SCHEMA = "moonshot.epoch.manifest.v1"

MANIFEST_KEYS = frozenset({
    "schema", "chain_id", "epoch_index", "runtime", "input_checkpoint_sha256", "spec_sha256", "work_id",
    "trace_sha256", "trace_bytes", "output_checkpoint_sha256", "output_checkpoint_bytes", "epoch_digest",
})

# Identifiers become git ref components: keep them boring.
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")


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

    def files(self) -> dict:
        return {"manifest": self.manifest_bytes, "spec": self.spec_bytes, "trace": self.trace,
                "checkpoint": self.checkpoint}


def make_genesis(chain_id, *, epochs, params, approved_code_sha, initial_checkpoint, runtime=None) -> Genesis:
    """A chain's genesis. The runtime is NOT checked against the registry here: a worker refuses an
    unapproved runtime at execution time (CONTRACT s8), which is what D3 case 11 attacks."""
    if not isinstance(chain_id, str) or not ID_RE.match(chain_id):
        raise ValueError("chain_id must match {}".format(ID_RE.pattern))
    if isinstance(epochs, bool) or not isinstance(epochs, int) or epochs < 1:
        raise ValueError("epochs must be a positive integer")
    if not isinstance(initial_checkpoint, (bytes, bytearray)):
        raise TypeError("initial_checkpoint must be bytes")
    obj = {"schema": GENESIS_SCHEMA, "chain_id": chain_id, "epochs": epochs,
           "runtime": dict(runtime or R.SYNTHETIC_V1), "params": dict(params),
           "approved_code_sha": approved_code_sha,
           "initial_checkpoint_sha256": C.sha256_hex(bytes(initial_checkpoint))}
    return Genesis(obj, C.canonical_bytes(obj), bytes(initial_checkpoint))


def derive_spec(genesis_obj: dict, epoch_index: int) -> dict:
    if isinstance(epoch_index, bool) or not isinstance(epoch_index, int) or \
            not 1 <= epoch_index <= genesis_obj["epochs"]:
        raise ValueError("epoch_index {} outside 1..{}".format(epoch_index, genesis_obj["epochs"]))
    return {"schema": SPEC_SCHEMA, "chain_id": genesis_obj["chain_id"], "epoch_index": epoch_index,
            "runtime": genesis_obj["runtime"], "params": genesis_obj["params"]}


def work_id(input_checkpoint_sha256: str, spec_sha256: str, runtime: dict) -> str:
    return C.tagged_digest(C.TAG_WORK, {"input_checkpoint_sha256": input_checkpoint_sha256,
                                        "spec_sha256": spec_sha256, "runtime": runtime})


def epoch_digest(work_id_: str, trace_sha256: str, output_checkpoint_sha256: str) -> str:
    return C.tagged_digest(C.TAG_RESULT, {"work_id": work_id_, "trace_sha256": trace_sha256,
                                          "output_checkpoint_sha256": output_checkpoint_sha256})


def execute(genesis_obj: dict, epoch_index: int, input_checkpoint: bytes, runner=None) -> EpochResult:
    spec = derive_spec(genesis_obj, epoch_index)
    spec_bytes = C.canonical_bytes(spec)
    run = runner or R.lookup(spec["runtime"])
    if run is None:
        raise LookupError("runtime {} is not registered".format(spec["runtime"]))
    trace, checkpoint = run(input_checkpoint, spec)
    if not isinstance(trace, bytes) or not isinstance(checkpoint, bytes):
        raise TypeError("a runtime returns (bytes, bytes)")
    in_sha, spec_sha = C.sha256_hex(input_checkpoint), C.sha256_hex(spec_bytes)
    wid = work_id(in_sha, spec_sha, spec["runtime"])
    t_sha, c_sha = C.sha256_hex(trace), C.sha256_hex(checkpoint)
    digest = epoch_digest(wid, t_sha, c_sha)
    manifest = {"schema": MANIFEST_SCHEMA, "chain_id": spec["chain_id"], "epoch_index": epoch_index,
                "runtime": spec["runtime"], "input_checkpoint_sha256": in_sha, "spec_sha256": spec_sha,
                "work_id": wid, "trace_sha256": t_sha, "trace_bytes": len(trace),
                "output_checkpoint_sha256": c_sha, "output_checkpoint_bytes": len(checkpoint),
                "epoch_digest": digest}
    return EpochResult(spec["chain_id"], epoch_index, spec, spec_bytes, trace, checkpoint, manifest,
                       C.canonical_bytes(manifest), wid, digest)


def verify_epoch(files: dict, input_checkpoint_sha256=None) -> list:
    """Every digest in the manifest recomputes from the bytes it names; [] means valid. With
    input_checkpoint_sha256, also check the lineage link to the previous output."""
    try:
        m = C.parse_canonical(files["manifest"])
        spec = C.parse_canonical(files["spec"])
    except (C.CanonicalError, KeyError) as e:
        return ["manifest or spec unreadable: {}".format(e)]
    errs = []
    if not isinstance(m, dict) or set(m) != MANIFEST_KEYS or m.get("schema") != MANIFEST_SCHEMA:
        return ["manifest keys or schema are wrong"]
    trace, ckpt = files.get("trace"), files.get("checkpoint")
    if not isinstance(trace, bytes) or not isinstance(ckpt, bytes):
        return ["trace or checkpoint missing"]
    if C.sha256_hex(files["spec"]) != m["spec_sha256"]:
        errs.append("spec_sha256 does not match SPEC")
    if not isinstance(spec, dict) or spec.get("schema") != SPEC_SCHEMA or \
            (spec.get("chain_id"), spec.get("epoch_index"), spec.get("runtime")) != \
            (m["chain_id"], m["epoch_index"], m["runtime"]):
        errs.append("SPEC does not agree with the manifest")
    if C.sha256_hex(trace) != m["trace_sha256"] or len(trace) != m["trace_bytes"]:
        errs.append("TRACE does not match the manifest")
    if C.sha256_hex(ckpt) != m["output_checkpoint_sha256"] or len(ckpt) != m["output_checkpoint_bytes"]:
        errs.append("CHECKPOINT does not match the manifest")
    try:
        wid = work_id(m["input_checkpoint_sha256"], m["spec_sha256"], m["runtime"])
        if wid != m["work_id"]:
            errs.append("work_id does not recompute")
        if epoch_digest(m["work_id"], m["trace_sha256"], m["output_checkpoint_sha256"]) != m["epoch_digest"]:
            errs.append("epoch_digest does not recompute")
    except C.CanonicalError as e:
        errs.append("identity fields not canonical: {}".format(e))
    if input_checkpoint_sha256 is not None and m["input_checkpoint_sha256"] != input_checkpoint_sha256:
        errs.append("input checkpoint does not link to the previous output")
    return errs


def replay_chain(genesis: Genesis, upto: int, runner=None) -> list:
    """Uninterrupted, transport-free execution of epochs 1..upto: the reference every chain must equal."""
    out, inp = [], genesis.initial_checkpoint
    for k in range(1, upto + 1):
        r = execute(genesis.obj, k, inp, runner)
        out.append(r)
        inp = r.checkpoint
    return out
