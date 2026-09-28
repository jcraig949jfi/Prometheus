"""Across-the-firewall runner for holdout D2 (M1 only; custody.py releases the key to the designated runner).

  COSMOS_BROKER=1 python -m prometheus.cosmos.c3_holdout_D2.runner \
      --package PKG.zip --package-sha256 HEX --runner-id ID \
      --key <key file released by custody.py release-key> \
      [--out DIR] [--phase all|predict|certify] [--predict-timeout SEC] [--max-episode-steps N]
      [--allow-flagged] [--gate-ref origin/main]
  COSMOS_BROKER=1 python -m prometheus.cosmos.c3_holdout_D2.runner --verify-receipts DIR/receipts.jsonl

Protocol (enforced in code, in this order):
 0. GATES    protocol.check_gates(..., "DESIGNATION") runs before the key file is touched: the sealed set is on
             the reference branch, a PASSING firewall audit is bound to this exact code, Cosmos's committed
             package hash equals --package-sha256, and this runner id + host are designated (never M2).
 1. OPEN     the manifest's spec_id and the ciphertext's sha256 are checked, the ciphertext is decrypted in
             memory only (never written), the plaintext's family_src_sha256 must equal the CURRENT
             holdout-D medium.py; the external FROZEN prediction package (one .zip file) is hashed and the
             run REFUSES unless sha256(zip bytes) equals the expected hash given on the command line. The
             package is statically audited (see AUDIT) and extracted. An "open" receipt is written.
 2. PREDICT  for EVERY hidden world i (0..N-1) the predictor is asked, in a SEPARATE process that never
             holds the key, plaintext or knob values, to predict. It sees the world ONLY through the public
             System interface (D_CONTRACT s3) served over a pipe (JSON + numpy .npy without pickle, so the
             child cannot inject code into the runner), plus Task(V, k). One "prediction" receipt per
             world (errors/timeouts are recorded as the prediction).
 3. SEAL     a "predictions_sealed" receipt commits to all N prediction receipt hashes. With --phase
             predict the run stops here and prints the chain head (post it before certifying).
 4. CERTIFY  refused (OrderViolation) unless the on-disk chain verifies AND holds exactly one prediction
             for every world AND the seal record matches them. Then prometheus/cosmos/c3/certify.py runs on
             the base world (seed = the world's hidden run seed) and on the package's intervention
             do(knob -> to) applied to that world. One "certify" receipt per world.
 5. CLOSE    a "close" receipt; RESULT.json (per-world results + chain head hash) beside receipts.jsonl.

Receipts: receipts.jsonl, append-only, one JSON record per line, record.hash =
sha256(canonical {seq, kind, prev, body}), prev = previous record's hash (genesis = sha256 of the run's
public identifiers). No knob value, run seed or key appears in any receipt; each world is identified by
its index and world_tag = HMAC-SHA256(key, canonical(world) || run_seed), checkable after reveal.

Prediction package (.zip): package.json = {"format": "c3-D2-prediction-package/1", "entry": "<file>.py",
"adjudication": <any JSON: Cosmos's frozen adjudication rules, recorded verbatim, not interpreted here>,
"intervention": {"knob": <medium.KNOBS name>, "to": <value in the declared range>}} and the entry module
defining predict(system, task, seed) -> {"class": C, "intervention": {"class": C, ...}, ...} with
C in NONE/PASSIVE/FUNCTIONAL/INCOHERENT/INDETERMINATE; extra JSON fields are recorded. The system given
to predict() implements init/noise/step/readout_features/full_state (noise() requires a
numpy.random.Generator). AUDIT: a heuristic AST scan (NOT a sandbox) refuses packages importing
filesystem/process/network/introspection modules or calling open/exec/eval/compile/__import__/getattr...
or touching dunder introspection attributes; --allow-flagged overrides and records the flags.
"""
from __future__ import annotations

import os

if os.environ.get("COSMOS_BROKER") != "1":
    raise ImportError("holdout D2 runner: set COSMOS_BROKER=1 (broker only)")

import argparse
import ast
import base64
import datetime as _dt
import hashlib
import hmac
import importlib.util
import io
import json
import multiprocessing as mp
import socket
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from prometheus.cosmos.c3.certify import certify
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task
from prometheus.cosmos.c3_holdout_D import medium
from prometheus.cosmos.c3_holdout_D2 import protocol, sealbox

HERE = Path(__file__).resolve().parent
D_DIR = HERE.parent / "c3_holdout_D"
RECEIPT_FORMAT = "c3-holdout-D2-receipts/1"
PACKAGE_FORMAT = "c3-D2-prediction-package/1"
CLASSES = ("NONE", "PASSIVE", "FUNCTIONAL", "INCOHERENT", "INDETERMINATE")
DEFAULT_OUT_ROOT = Path("C:/Users/jcrai/nestor_receipts/holdout_D2")
# Protocol gates are read from the COMMITTED tree of this repository's reference branch (protocol.py). The
# selftest points these at a throwaway git repository it builds; the gates themselves are never skipped.
DEFAULT_GATE_REPO = HERE.parents[2]
DEFAULT_GATE_REF = protocol.DEFAULT_REF
MAX_E_PER_CALL = 200_000
MAX_PRED_BYTES = 65_536
BIT_GENERATORS = ("PCG64", "PCG64DXSM", "MT19937", "Philox", "SFC64")

FORBIDDEN_MODULES = {
    "os", "sys", "subprocess", "socket", "pathlib", "io", "shutil", "importlib", "ctypes", "gc", "inspect",
    "multiprocessing", "threading", "concurrent", "asyncio", "builtins", "pickle", "marshal", "shelve",
    "urllib", "http", "ftplib", "smtplib", "requests", "glob", "fnmatch", "tempfile", "cryptography",
    "runpy", "code", "codeop", "signal", "mmap", "winreg", "_winapi", "nt", "posix", "platform",
    "sqlite3", "zipfile", "tarfile", "zipimport", "pkgutil", "site", "sysconfig", "traceback", "types",
    "weakref", "dis", "linecache", "tokenize", "webbrowser", "secrets", "hashlib", "hmac", "base64",
}
ALLOWED_PROMETHEUS = ("prometheus.cosmos.c3", "prometheus.cosmos.c3.")
FORBIDDEN_CALLS = {"open", "exec", "eval", "compile", "__import__", "globals", "locals", "vars",
                   "breakpoint", "input", "getattr", "setattr", "delattr", "memoryview"}


class RunnerRefusal(Exception):
    pass


class PackageHashMismatch(RunnerRefusal):
    pass


class PackageInvalid(RunnerRefusal):
    pass


class PackageAuditRefusal(RunnerRefusal):
    pass


class OrderViolation(RunnerRefusal):
    pass


class ChainBroken(RunnerRefusal):
    pass


class HiddenSetMismatch(RunnerRefusal):
    pass


def _utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def inside_git_repo(path: Path) -> bool:
    p = Path(path).resolve()
    return any((q / ".git").exists() for q in [p] + list(p.parents))


# ================================================================ safe pipe codec (no pickle)
def _enc(x):
    if isinstance(x, np.ndarray):
        if x.dtype == object:
            raise TypeError("object arrays are not transferable")
        buf = io.BytesIO()
        np.save(buf, x, allow_pickle=False)
        return {"__nd__": base64.b64encode(buf.getvalue()).decode("ascii")}
    if isinstance(x, dict):
        return {str(k): _enc(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_enc(v) for v in x]
    if isinstance(x, np.generic):
        return x.item()
    if x is None or isinstance(x, (bool, int, float, str)):
        return x
    raise TypeError("type %s is not transferable" % type(x).__name__)


def _dec(x):
    if isinstance(x, dict):
        if set(x) == {"__nd__"}:
            return np.load(io.BytesIO(base64.b64decode(x["__nd__"])), allow_pickle=False)
        return {k: _dec(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_dec(v) for v in x]
    return x


def _send(conn, obj) -> None:
    conn.send_bytes(json.dumps(_enc(obj)).encode("utf-8"))


def _recv(conn):
    return _dec(json.loads(conn.recv_bytes().decode("utf-8")))


def _rng_from_state(state: dict):
    name = state.get("bit_generator")
    if name not in BIT_GENERATORS:
        raise TypeError("unsupported bit generator")
    bg = getattr(np.random, name)()
    bg.state = state
    return np.random.Generator(bg)


# ================================================================ child side (predictor process)
class _HiddenWorldStub(System):
    """The ONLY handle the predictor gets: the public System interface, served over the pipe."""
    name = "D2-hidden-world"

    def __init__(self, conn):
        self.__conn = conn

    def __call(self, method, *args):
        _send(self.__conn, ["call", method, list(args)])
        tag, val = _recv(self.__conn)
        if tag != "ret":
            raise RuntimeError("hidden-world call %s refused: %s" % (method, val))
        return val

    def init(self, E):
        return self.__call("init", int(E))

    def noise(self, n, rng):
        if not isinstance(rng, np.random.Generator):
            raise TypeError("noise() requires a numpy.random.Generator")
        nz, st = self.__call("noise", int(n), rng.bit_generator.state)
        rng.bit_generator.state = st                   # advance the caller's rng as a local call would
        return nz

    def step(self, state, obs_t, noise):
        return self.__call("step", state, np.asarray(obs_t, dtype=np.int64), noise)

    def readout_features(self, state):
        return self.__call("readout_features", state)

    def full_state(self, state):
        return self.__call("full_state", state)


def _worker_main(conn, pkg_dir: str, entry: str) -> None:
    sys.path.insert(0, pkg_dir)
    spec = importlib.util.spec_from_file_location("c3_d2_predictor", os.path.join(pkg_dir, entry))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    while True:
        msg = _recv(conn)
        if msg[0] == "stop":
            return
        _tag, i, V, k, seed = msg
        try:
            pred = mod.predict(_HiddenWorldStub(conn), Task(V=int(V), k=int(k)), int(seed))
            _send(conn, ["done", i, pred])
        except Exception as e:                          # noqa: BLE001 -- recorded as the prediction
            _send(conn, ["fail", i, "%s: %s" % (type(e).__name__, str(e)[:300])])


# ================================================================ receipts (append-only hash chain)
def record_hash(seq: int, kind: str, prev: str, body: dict) -> str:
    return sealbox.sha256_hex(sealbox.canon_bytes({"seq": seq, "kind": kind, "prev": prev, "body": body}))


class Receipts:
    def __init__(self, path: Path, genesis: str, create: bool):
        self.path = Path(path)
        self.genesis = genesis
        if create:
            with open(self.path, "x", encoding="utf-8", newline="\n"):
                pass
            self.records: List[dict] = []
        else:
            ok, recs, why = verify_receipts(self.path)
            if not ok:
                raise ChainBroken(why)
            if recs and recs[0]["prev"] != genesis:
                raise ChainBroken("genesis mismatch (different run identifiers)")
            self.records = recs

    @property
    def head(self) -> str:
        return self.records[-1]["hash"] if self.records else self.genesis

    def append(self, kind: str, body: dict) -> dict:
        seq, prev = len(self.records), self.head
        rec = {"seq": seq, "kind": kind, "prev": prev, "body": body, "hash": record_hash(seq, kind, prev, body)}
        with open(self.path, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")
            f.flush()
            os.fsync(f.fileno())
        self.records.append(rec)
        return rec


def verify_receipts(path) -> tuple:
    """(ok, records, reason). Recomputes every hash and prev link; the first prev must be the genesis
    recorded in the open record's body."""
    recs = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    recs.append(json.loads(line))
    except (OSError, ValueError) as e:
        return False, [], "unreadable: %s" % type(e).__name__
    prev = None
    for n, r in enumerate(recs):
        if r.get("seq") != n:
            return False, recs, "seq break at %d" % n
        if n == 0:
            if r.get("kind") != "open" or r["body"].get("genesis") != r["prev"]:
                return False, recs, "bad open record"
        elif r["prev"] != prev:
            return False, recs, "prev link break at %d" % n
        if record_hash(r["seq"], r["kind"], r["prev"], r["body"]) != r.get("hash"):
            return False, recs, "hash mismatch at %d" % n
        prev = r["hash"]
    return True, recs, "ok"


def predictions_digest(pred_hashes: List[str]) -> str:
    return sealbox.sha256_hex("\n".join(pred_hashes).encode("ascii"))


# ================================================================ package
def audit_source(src: str, fname: str) -> List[str]:
    flags = []
    try:
        tree = ast.parse(src, filename=fname)
    except SyntaxError as e:
        return ["%s: syntax error line %s" % (fname, e.lineno)]
    for node in ast.walk(tree):
        mods = []
        if isinstance(node, ast.Import):
            mods = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                continue                                  # package-relative import of its own files
            mods = [node.module or ""]
        for m in mods:
            top = m.split(".")[0]
            if top in FORBIDDEN_MODULES:
                flags.append("%s:%d import %s" % (fname, node.lineno, m))
            elif top == "prometheus" and not (m == ALLOWED_PROMETHEUS[0] or m.startswith(ALLOWED_PROMETHEUS[1])):
                flags.append("%s:%d import %s (only prometheus.cosmos.c3.* allowed)" % (fname, node.lineno, m))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_CALLS:
            flags.append("%s:%d call %s()" % (fname, node.lineno, node.func.id))
        if isinstance(node, ast.Attribute) and node.attr.startswith("__") and node.attr.endswith("__") \
                and node.attr not in ("__init__", "__name__"):
            flags.append("%s:%d attribute %s" % (fname, node.lineno, node.attr))
        if isinstance(node, ast.Name) and node.id.startswith("__") and node.id not in ("__name__",):
            flags.append("%s:%d name %s" % (fname, node.lineno, node.id))
    return flags


def load_package(zip_path, expected_sha256: str, extract_to: Path, allow_flagged: bool = False) -> dict:
    """Refuses (PackageHashMismatch) unless sha256 of the exact bytes used equals expected_sha256."""
    data = Path(zip_path).read_bytes()
    actual = sealbox.sha256_hex(data)
    if actual != str(expected_sha256).strip().lower():
        raise PackageHashMismatch("package sha256 mismatch: expected %s got %s" % (expected_sha256, actual))
    zf = zipfile.ZipFile(io.BytesIO(data))
    files = {}
    for info in zf.infolist():
        n = info.filename
        if info.is_dir():
            continue
        if n.startswith(("/", "\\")) or ".." in Path(n).parts or ":" in n:
            raise PackageInvalid("unsafe member path")
        files[n] = zf.read(info)
    if "package.json" not in files:
        raise PackageInvalid("package.json missing")
    try:
        meta = json.loads(files["package.json"].decode("utf-8"))
    except ValueError:
        raise PackageInvalid("package.json is not JSON")
    if meta.get("format") != PACKAGE_FORMAT:
        raise PackageInvalid("package format must be %s" % PACKAGE_FORMAT)
    entry = meta.get("entry")
    if not isinstance(entry, str) or entry not in files or not entry.endswith(".py"):
        raise PackageInvalid("entry module missing")
    if "adjudication" not in meta:
        raise PackageInvalid("adjudication rules missing")
    iv = meta.get("intervention")
    if not isinstance(iv, dict) or iv.get("knob") not in medium.KNOBS or "to" not in iv:
        raise PackageInvalid("intervention must be {knob: <declared knob>, to: <value>}")
    _u, _m, (lo, hi), typ = medium.KNOBS[iv["knob"]]
    to = iv["to"]
    if isinstance(to, bool) or not isinstance(to, (int, float)) or (typ is int and int(to) != to) \
            or not (lo <= to <= hi):
        raise PackageInvalid("intervention value outside the knob's declared type/range")
    flags = []
    for n, b in sorted(files.items()):
        if n.endswith(".py"):
            flags += audit_source(b.decode("utf-8", errors="replace"), n)
    if flags and not allow_flagged:
        raise PackageAuditRefusal("package audit flags: %s" % "; ".join(flags[:20]))
    extract_to = Path(extract_to)
    extract_to.mkdir(parents=True, exist_ok=False)
    for n, b in files.items():
        p = extract_to / n
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b)
    return {"sha256": actual, "dir": str(extract_to), "meta": meta, "entry": entry, "audit_flags": flags,
            "allow_flagged": bool(allow_flagged),
            "files": {n: sealbox.sha256_hex(b) for n, b in sorted(files.items())}}


def validate_prediction(p) -> Optional[str]:
    if not isinstance(p, dict):
        return "prediction is not an object"
    try:
        if len(sealbox.canon_bytes(p)) > MAX_PRED_BYTES:
            return "prediction too large"
    except (TypeError, ValueError):
        return "prediction not JSON-serialisable"
    if p.get("class") not in CLASSES:
        return "class missing/invalid"
    iv = p.get("intervention")
    if not isinstance(iv, dict) or iv.get("class") not in CLASSES:
        return "intervention.class missing/invalid"
    return None


# ================================================================ the run
def _summ(r: dict) -> dict:
    """certify() result WITHOUT r['system'] (its name encodes the knobs)."""
    a, b = r["P1"], r["P2"]
    return {"class": r["class"],
            "P1": {k: a[k] for k in ("D_bits", "D_generic", "D_readout", "null_max", "p", "held", "indeterminate")},
            "P2": {k: b[k] for k in ("J_intact", "J_ablated", "effect", "se", "z", "held", "indeterminate")}}


class FirewallRun:
    PHASES = ("INIT", "OPEN", "SEALED", "CLOSED")

    def __init__(self, manifest_path, ciphertext_path, key_path, package_zip, package_sha256, out_dir,
                 allow_flagged: bool = False, certify_kwargs: Optional[dict] = None,
                 predict_timeout: float = 1800.0, max_episode_steps: Optional[int] = None,
                 resume: bool = False, require_out_outside_git: bool = True, runner_id: Optional[str] = None,
                 gate_repo=None, gate_ref: Optional[str] = None):
        self.manifest_path, self.ciphertext_path = Path(manifest_path), Path(ciphertext_path)
        self.key_path, self.package_zip = Path(key_path), Path(package_zip)
        self.package_sha256 = str(package_sha256).lower()
        self.out = Path(out_dir)
        self.allow_flagged, self.certify_kwargs = allow_flagged, dict(certify_kwargs or {})
        self.predict_timeout, self.max_episode_steps = predict_timeout, max_episode_steps
        self.resume, self.require_out_outside_git = resume, require_out_outside_git
        self.runner_id = runner_id
        self.gate_repo = Path(gate_repo) if gate_repo is not None else DEFAULT_GATE_REPO
        self.gate_ref = gate_ref or DEFAULT_GATE_REF
        self.phase = "INIT"
        self._proc = self._conn = None

    # ------------------------------------------------------------ open
    def open(self) -> dict:
        # Protocol order (protocol.py): seal < PASSING firewall audit of this exact code < Cosmos's committed
        # package hash < designation of THIS runner on THIS host. Checked before the key file is touched.
        if not self.runner_id:
            raise protocol.RunnerNotDesignated("a runner id is required")
        self.gates = protocol.check_gates(self.gate_repo, "DESIGNATION", ref=self.gate_ref,
                                          package_sha256=self.package_sha256, runner_id=self.runner_id)
        if inside_git_repo(self.key_path):
            raise RunnerRefusal("key file is inside a git repository: refusing")
        if self.require_out_outside_git and inside_git_repo(self.out if self.out.exists() else self.out.parent):
            raise RunnerRefusal("output directory is inside a git repository: refusing")
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        if sealbox.manifest_spec_id(manifest) != manifest.get("spec_id"):
            raise HiddenSetMismatch("manifest spec_id does not match its contents")
        if manifest["spec_id"] != self.gates["spec_id"]:
            raise HiddenSetMismatch("manifest is not the sealed one the protocol gates refer to")
        ct = self.ciphertext_path.read_bytes()
        if sealbox.sha256_hex(ct) != manifest["ciphertext_sha256"]:
            raise HiddenSetMismatch("ciphertext sha256 != manifest")
        fam = sealbox.src_sha_lf(D_DIR / "medium.py")
        if fam != manifest["family_src_sha256"]:
            raise HiddenSetMismatch("holdout-D medium.py changed since the draw")
        key = sealbox.read_hex_file(self.key_path, sealbox.KEY_BYTES)
        plain = sealbox.decrypt(key, bytes.fromhex(manifest["iv_hex"]), ct, fam)
        hidden = json.loads(plain.decode("utf-8"))
        if hidden["family_src_sha256"] != fam or hidden["n_worlds"] != manifest["n_worlds"] \
                or len(hidden["worlds"]) != hidden["n_worlds"] or len(hidden["run_seeds"]) != hidden["n_worlds"]:
            raise HiddenSetMismatch("decrypted hidden set inconsistent with manifest")
        self._worlds = [medium.world_from_dict(w) for w in hidden["worlds"]]
        self._seeds = [int(s) for s in hidden["run_seeds"]]
        self._tags = [hmac.new(key, sealbox.canon_bytes([w, s]), hashlib.sha256).hexdigest()
                      for w, s in zip(hidden["worlds"], self._seeds)]
        del key, plain, hidden
        self.N = len(self._worlds)
        self.manifest = manifest
        genesis = sealbox.sha256_hex(sealbox.canon_bytes({
            "format": RECEIPT_FORMAT, "spec_id": manifest["spec_id"],
            "ciphertext_sha256": manifest["ciphertext_sha256"], "commitment": manifest["commitment"],
            "package_sha256": self.package_sha256}))
        rpath = self.out / "receipts.jsonl"
        if self.resume:
            self.receipts = Receipts(rpath, genesis, create=False)
            pkg_dir = self.out / "package"
            data = self.package_zip.read_bytes()
            if sealbox.sha256_hex(data) != self.package_sha256 or \
                    self.receipts.records[0]["body"]["package"]["sha256"] != self.package_sha256:
                raise PackageHashMismatch("package sha256 mismatch on resume")
            self.pkg = dict(self.receipts.records[0]["body"]["package"], dir=str(pkg_dir))
            kinds = [r["kind"] for r in self.receipts.records]
            self.phase = "CLOSED" if "close" in kinds else "SEALED" if "predictions_sealed" in kinds else "OPEN"
            return manifest
        self.out.mkdir(parents=True, exist_ok=True)
        if rpath.exists():
            raise RunnerRefusal("receipts.jsonl exists: use resume, never overwrite")
        self.pkg = load_package(self.package_zip, self.package_sha256, self.out / "package", self.allow_flagged)
        self.receipts = Receipts(rpath, genesis, create=True)
        self.receipts.append("open", {
            "genesis": genesis, "utc": _utc(), "host": socket.gethostname(),
            "manifest_sha256": sealbox.sha256_file(self.manifest_path), "spec_id": manifest["spec_id"],
            "ciphertext_sha256": manifest["ciphertext_sha256"], "commitment": manifest["commitment"],
            "n_worlds": self.N, "runner_id": self.runner_id,
            "protocol_gates": {k: v for k, v in self.gates.items() if k.endswith("_commit") or k in ("ref", "auditor")},
            "package": {k: self.pkg[k] for k in ("sha256", "meta", "entry", "audit_flags", "allow_flagged", "files")},
            "runner_src_sha256": sealbox.src_sha_lf(Path(__file__)),
            "certify_src_sha256": sealbox.src_sha_lf(HERE.parent / "c3" / "certify.py"),
            "certify_kwargs": self.certify_kwargs, "predict_timeout_s": self.predict_timeout,
            "max_episode_steps_per_world": self.max_episode_steps,
            "python": sys.version.split()[0], "numpy": np.__version__})
        self.phase = "OPEN"
        return manifest

    # ------------------------------------------------------------ predict
    def _start_worker(self):
        ctx = mp.get_context("spawn")
        self._conn, child = ctx.Pipe(duplex=True)
        self._proc = ctx.Process(target=_worker_main, args=(child, self.pkg["dir"], self.pkg["entry"]), daemon=True)
        self._proc.start()
        child.close()

    def _stop_worker(self, kill: bool = False):
        if self._proc is None:
            return
        try:
            if not kill:
                _send(self._conn, ["stop"])
                self._proc.join(10)
        except (OSError, EOFError, BrokenPipeError):
            pass
        if self._proc.is_alive():
            self._proc.kill()
            self._proc.join(10)
        self._proc = self._conn = None

    def _serve(self, sysobj, method, args, usage):
        if method == "init":
            E = int(args[0])
            if not 0 < E <= MAX_E_PER_CALL:
                raise ValueError
            return sysobj.init(E)
        if method == "noise":
            n, st = int(args[0]), args[1]
            if not 0 < n <= MAX_E_PER_CALL:
                raise ValueError
            rng = _rng_from_state(st)
            nz = sysobj.noise(n, rng)
            return [nz, rng.bit_generator.state]
        if method == "step":
            state, obs, nz = args
            obs = np.asarray(obs, dtype=np.int64)
            usage["episode_steps"] += int(obs.shape[0])
            if self.max_episode_steps is not None and usage["episode_steps"] > self.max_episode_steps:
                usage["budget_exceeded"] = True
                raise OverflowError
            if not isinstance(state, dict) or set(state) != {"c"}:
                raise ValueError
            return sysobj.step(state, obs, nz)
        if method in ("readout_features", "full_state"):
            return getattr(sysobj, method)(args[0])
        raise AttributeError

    def _predict_one(self, i: int, seed: int) -> dict:
        w = self._worlds[i]
        sysobj = medium.ReactiveChannel(w)
        usage = {"calls": 0, "episode_steps": 0, "budget_exceeded": False}
        if self._proc is None:
            self._start_worker()
        _send(self._conn, ["predict", i, w.V, w.k, seed])
        deadline = _dt.datetime.now().timestamp() + self.predict_timeout
        while True:
            left = deadline - _dt.datetime.now().timestamp()
            if left <= 0 or not self._conn.poll(max(left, 0.0)):
                self._stop_worker(kill=True)
                return {"status": "TIMEOUT", "usage": usage}
            try:
                msg = _recv(self._conn)
            except (EOFError, OSError, ValueError):
                self._stop_worker(kill=True)
                return {"status": "PREDICTOR_CRASH", "usage": usage}
            if msg[0] == "call":
                usage["calls"] += 1
                try:
                    _send(self._conn, ["ret", self._serve(sysobj, msg[1], msg[2], usage)])
                except Exception as e:                       # noqa: BLE001 -- type name only: no knob leak
                    _send(self._conn, ["err", type(e).__name__])
            elif msg[0] == "done" and msg[1] == i:
                why = validate_prediction(msg[2])
                if why:
                    return {"status": "INVALID_PREDICTION", "reason": why, "usage": usage}
                return {"status": "OK", "prediction": msg[2], "usage": usage}
            elif msg[0] == "fail" and msg[1] == i:
                return {"status": "PREDICTOR_ERROR", "error": str(msg[2])[:400], "usage": usage}
            else:
                self._stop_worker(kill=True)
                return {"status": "PROTOCOL_ERROR", "usage": usage}

    def predictor_seed(self, i: int) -> int:
        return int(sealbox.sha256_hex(("%s|%d" % (self.package_sha256, i)).encode())[:8], 16)

    def predict_all(self) -> None:
        if self.phase != "OPEN":
            raise OrderViolation("predict requires phase OPEN (now %s)" % self.phase)
        done = {r["body"]["i"] for r in self.receipts.records if r["kind"] == "prediction"}
        try:
            for i in range(self.N):
                if i in done:
                    continue
                out = self._predict_one(i, self.predictor_seed(i))
                self.receipts.append("prediction", dict(out, i=i, world_tag=self._tags[i], utc=_utc()))
        finally:
            self._stop_worker()

    def seal_predictions(self) -> str:
        if self.phase != "OPEN":
            raise OrderViolation("seal requires phase OPEN (now %s)" % self.phase)
        preds = [r for r in self.receipts.records if r["kind"] == "prediction"]
        idx = sorted(r["body"]["i"] for r in preds)
        if idx != list(range(self.N)):
            raise OrderViolation("cannot seal: predictions recorded for %d/%d worlds" % (len(set(idx)), self.N))
        head_before = self.receipts.head
        self.receipts.append("predictions_sealed", {
            "n_predictions": len(preds), "head_before_seal": head_before,
            "predictions_digest": predictions_digest([r["hash"] for r in preds]), "utc": _utc()})
        self.phase = "SEALED"
        return self.receipts.head

    # ------------------------------------------------------------ certify
    def _gate(self, i: int) -> None:
        """The firewall order gate. Re-verifies the chain ON DISK before EVERY certification."""
        if self.phase != "SEALED":
            raise OrderViolation("certify refused: predictions not sealed (phase %s)" % self.phase)
        ok, recs, why = verify_receipts(self.receipts.path)
        if not ok:
            raise OrderViolation("certify refused: receipt chain does not verify (%s)" % why)
        if [r["hash"] for r in recs] != [r["hash"] for r in self.receipts.records]:
            raise OrderViolation("certify refused: on-disk chain differs from the runner's")
        kinds = [r["kind"] for r in recs]
        if "predictions_sealed" not in kinds:
            raise OrderViolation("certify refused: no seal record on disk")
        s = kinds.index("predictions_sealed")
        preds = [r for r in recs[:s] if r["kind"] == "prediction"]
        if sorted(r["body"]["i"] for r in preds) != list(range(self.N)):
            raise OrderViolation("certify refused: not every world has exactly one prediction before the seal")
        seal = recs[s]["body"]
        if seal["predictions_digest"] != predictions_digest([r["hash"] for r in preds]) or \
                seal["head_before_seal"] != recs[s - 1]["hash"]:
            raise OrderViolation("certify refused: seal does not commit to the recorded predictions")
        if any(r["kind"] == "prediction" for r in recs[s + 1:]):
            raise OrderViolation("certify refused: prediction recorded after the seal")
        if any(r["kind"] == "certify" and r["body"]["i"] == i for r in recs):
            raise OrderViolation("certify refused: world %d already certified" % i)

    def certify_world(self, i: int) -> dict:
        self._gate(i)
        w, seed = self._worlds[i], self._seeds[i]
        base = _summ(certify(medium.ReactiveChannel(w), w.task(), seed=seed, **self.certify_kwargs))
        iv = self.pkg["meta"]["intervention"]
        knob = iv["knob"]
        val = medium.KNOBS[knob][3](iv["to"])
        body = {"i": i, "world_tag": self._tags[i], "base": base}
        try:
            w2 = medium.intervene(w, **{knob: val})
        except ValueError:
            body["intervention"] = {"knob": knob, "to": iv["to"], "status": "INVALID_AT_WORLD"}
        else:
            if w2 == w:
                post, noop = base, True
            else:
                post, noop = _summ(certify(medium.ReactiveChannel(w2), w2.task(), seed=seed,
                                           **self.certify_kwargs)), False
            body["intervention"] = {"knob": knob, "to": iv["to"], "status": "OK", "noop": noop, "result": post,
                                    "delta_J_intact": post["P2"]["J_intact"] - base["P2"]["J_intact"]}
        body["utc"] = _utc()
        return self.receipts.append("certify", body)

    def certify_all(self) -> None:
        done = {r["body"]["i"] for r in self.receipts.records if r["kind"] == "certify"}
        for i in range(self.N):
            if i not in done:
                self.certify_world(i)

    def close(self) -> dict:
        certs = {r["body"]["i"]: r for r in self.receipts.records if r["kind"] == "certify"}
        if sorted(certs) != list(range(self.N)):
            raise OrderViolation("close refused: %d/%d worlds certified" % (len(certs), self.N))
        preds = {r["body"]["i"]: r["body"] for r in self.receipts.records if r["kind"] == "prediction"}
        per_world = []
        for i in range(self.N):
            c = certs[i]["body"]
            ivr = c["intervention"]
            per_world.append({
                "i": i, "world_tag": c["world_tag"], "prediction_status": preds[i]["status"],
                "prediction": preds[i].get("prediction"), "base_class": c["base"]["class"],
                "intervention_status": ivr["status"],
                "intervention_class": ivr.get("result", {}).get("class"),
                "delta_J_intact": ivr.get("delta_J_intact"), "certify_receipt": certs[i]["hash"]})
        self.receipts.append("close", {"n_certified": self.N, "utc": _utc()})
        self.phase = "CLOSED"
        seal = next(r for r in self.receipts.records if r["kind"] == "predictions_sealed")
        result = {"format": RECEIPT_FORMAT, "spec_id": self.manifest["spec_id"],
                  "package_sha256": self.package_sha256, "predictions_seal_hash": seal["hash"],
                  "chain_head": self.receipts.head, "n_records": len(self.receipts.records),
                  "per_world": per_world}
        (self.out / "RESULT.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n",
                                              encoding="utf-8", newline="\n")
        return result


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="holdout D2 across-the-firewall runner")
    ap.add_argument("--package")
    ap.add_argument("--package-sha256")
    ap.add_argument("--key")
    ap.add_argument("--out")
    ap.add_argument("--manifest", default=str(HERE / "MANIFEST_D2.json"))
    ap.add_argument("--ciphertext", default=str(HERE / "hidden_D2.enc"))
    ap.add_argument("--phase", choices=("all", "predict", "certify"), default="all")
    ap.add_argument("--predict-timeout", type=float, default=1800.0)
    ap.add_argument("--max-episode-steps", type=int, default=None)
    ap.add_argument("--allow-flagged", action="store_true")
    ap.add_argument("--runner-id", help="must equal protocol/RUNNER_DESIGNATION.json runner_id")
    ap.add_argument("--gate-ref", default=DEFAULT_GATE_REF)
    ap.add_argument("--verify-receipts")
    a = ap.parse_args(argv)
    if a.verify_receipts:
        ok, recs, why = verify_receipts(a.verify_receipts)
        print(json.dumps({"ok": ok, "reason": why, "n_records": len(recs),
                          "head": recs[-1]["hash"] if recs else None}))
        return 0 if ok else 1
    if not (a.package and a.package_sha256 and a.key and a.runner_id):
        ap.error("--package, --package-sha256, --key and --runner-id are required")
    if a.phase == "certify" and not a.out:
        ap.error("--phase certify resumes an existing run: give its --out")
    out = Path(a.out) if a.out else DEFAULT_OUT_ROOT / ("run_" + _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    run = FirewallRun(a.manifest, a.ciphertext, a.key, a.package, a.package_sha256, out,
                      allow_flagged=a.allow_flagged, predict_timeout=a.predict_timeout,
                      max_episode_steps=a.max_episode_steps, resume=(a.phase == "certify"),
                      runner_id=a.runner_id, gate_ref=a.gate_ref)
    run.open()
    if a.phase in ("all", "predict"):
        run.predict_all()
        head = run.seal_predictions()
        print(json.dumps({"predictions_sealed": True, "chain_head": head, "out": str(out)}))
        if a.phase == "predict":
            return 0
    if run.phase != "SEALED":
        raise OrderViolation("certify phase requires sealed predictions (phase %s)" % run.phase)
    run.certify_all()
    res = run.close()
    print(json.dumps({"closed": True, "chain_head": res["chain_head"], "out": str(out)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
