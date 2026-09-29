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
import re
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
DEFAULT_OUT_ROOT = protocol.RUN_OUT_ROOT                       # v6: one value, shared with custody's preflight check
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
    # v4 (Odysseus v3 F-AST / F-NET): file-capable and network-capable modules
    "codecs", "fileinput", "gzip", "bz2", "lzma", "logging", "xmlrpc", "imaplib", "poplib", "telnetlib", "nntplib",
    "socketserver", "ssl", "select", "selectors", "xml", "wsgiref", "_socket", "_io", "_thread",
}
ALLOWED_PROMETHEUS = ("prometheus.cosmos.c3", "prometheus.cosmos.c3.")
FORBIDDEN_CALLS = {"open", "exec", "eval", "compile", "__import__", "globals", "locals", "vars",
                   "breakpoint", "input", "getattr", "setattr", "delattr", "memoryview"}
# v2 (Odysseus F2): file/process access through attributes (np.fromfile, Path.read_text, ...) and ANY reference to a
# forbidden builtin name (aliasing such as f = [open][0]) are flagged. The audit remains a heuristic: the gate that
# matters is the child isolation probe (the child must be unable to open the key and secret paths).
FORBIDDEN_ATTRS = {"fromfile", "load", "loads", "loadtxt", "genfromtxt", "memmap", "save", "savez",
                   "savez_compressed", "savetxt", "tofile", "fromregex", "DataSource", "open", "read_text",
                   "read_bytes", "write_text", "write_bytes", "system", "popen", "spawn", "fork", "ctypeslib",
                   "f2py", "lib", "testing", "load_library", "dlopen"}
ALLOWED_MEMBER_SUFFIXES = (".py", ".json", ".txt")
WINDOWS_RESERVED = {"CON", "PRN", "AUX", "NUL"} | {"COM%d" % i for i in range(1, 10)} | {"LPT%d" % i for i in range(1, 10)}


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


class PredictorChildFailed(RunnerRefusal):
    """v5 (Odysseus v4 S-1): the predictor child did not start or died before answering the isolation probe."""


class ChildNotIsolated(RunnerRefusal):
    pass


SECRET_PATHS = ("C:/Users/jcrai/nestor_secrets/holdout_D2/hidden_D2.key.hex",
                "C:/Users/jcrai/nestor_secrets/holdout_D2/hidden_D2.salt.hex",
                "C:/Users/jcrai/nestor_secrets/holdout_D2/hidden_D2.plain.json")


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


def _probe_write(paths):
    """v3: try to open each path for APPEND without writing anything; 'writable' / 'denied' / 'missing' / 'error:<t>'.
    A child that can append to the receipts could rewrite the run's evidence chain."""
    out = []
    for pth in paths:
        try:
            with open(pth, "ab"):
                pass
            out.append([pth, "writable"])
        except PermissionError:
            out.append([pth, "denied"])
        except (FileNotFoundError, NotADirectoryError):
            out.append([pth, "missing"])
        except OSError as e:
            out.append([pth, "error:%s" % type(e).__name__])
    return out


def os_account() -> str:
    """v3 (F-ACCT): the OS account from the OS, not from USERNAME/USER. v5: one implementation, in protocol."""
    return protocol.os_account()


def _probe_mkfile(dirs):
    """v5 (S-1 preflight): try to CREATE a file in each directory (then remove it); 'writable' / 'denied' / 'missing'."""
    out = []
    for d in dirs:
        p = os.path.join(d, ".c3d2_probe_%d" % os.getpid())
        try:
            fd = os.open(p, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            os.remove(p)
            out.append([d, "writable"])
        except PermissionError:
            out.append([d, "denied"])
        except (FileNotFoundError, NotADirectoryError):
            out.append([d, "missing"])
        except OSError as e:
            out.append([d, "error:%s" % type(e).__name__])
    return out


def _probe_paths(paths):
    """Try to open each path for reading; report 'opened' / 'denied' / 'missing' / 'error:<type>'."""
    out = []
    for pth in paths:
        try:
            with open(pth, "rb") as fh:
                fh.read(1)
            out.append([pth, "opened"])
        except PermissionError:
            out.append([pth, "denied"])
        except (FileNotFoundError, NotADirectoryError):
            out.append([pth, "missing"])
        except OSError as e:
            out.append([pth, "error:%s" % type(e).__name__])
    return out


def _disable_network() -> None:
    """v4 (Odysseus v3 F-NET): HEURISTIC in-process block of new sockets in the predictor child before any package code
    runs. NOT a boundary (a package can reach the OS by other means); the boundary is an outbound firewall rule for the
    separate child account (host capability request, FIREWALL.md v4)."""
    import socket as _s
    import _socket

    def _refused(*_a, **_k):
        raise OSError("network is disabled in the holdout D2 predictor child")
    for m in (_s, _socket):
        for n in ("socket", "create_connection", "create_server", "socketpair", "fromfd", "getaddrinfo",
                  "gethostbyname", "gethostbyname_ex"):
            if hasattr(m, n):
                setattr(m, n, _refused)


def _worker_main(conn, pkg_dir: str, entry: str) -> None:
    # v2 (F2): before ANY package code is imported, the runner makes this process try the secret paths.
    msg = _recv(conn)
    if msg[0] != "probe":
        return
    _send(conn, ["probe_result", _probe_paths(msg[1]) + _probe_write(msg[2] if len(msg) > 2 else [])
                 + _probe_mkfile(msg[3] if len(msg) > 3 else [])])
    if _recv(conn)[0] != "go":
        return
    _disable_network()
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
            for a in node.names:                          # v4 (F-AST): `from numpy import fromfile as ff`
                if a.name in FORBIDDEN_ATTRS or a.name in FORBIDDEN_CALLS or a.name == "*":
                    flags.append("%s:%d from %s import %s" % (fname, node.lineno, node.module, a.name))
        for m in mods:
            top = m.split(".")[0]
            if top in FORBIDDEN_MODULES:
                flags.append("%s:%d import %s" % (fname, node.lineno, m))
            elif top == "prometheus" and not (m == ALLOWED_PROMETHEUS[0] or m.startswith(ALLOWED_PROMETHEUS[1])):
                flags.append("%s:%d import %s (only prometheus.cosmos.c3.* allowed)" % (fname, node.lineno, m))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_CALLS:
            flags.append("%s:%d call %s()" % (fname, node.lineno, node.func.id))
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_CALLS:
            flags.append("%s:%d reference to %s" % (fname, node.lineno, node.id))
        if isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_ATTRS:
            flags.append("%s:%d attribute .%s" % (fname, node.lineno, node.attr))
        if isinstance(node, ast.Attribute) and node.attr.startswith("_") and not node.attr.startswith("__"):
            flags.append("%s:%d private attribute .%s" % (fname, node.lineno, node.attr))   # v7: e.g. _Stub__conn
        if isinstance(node, ast.Attribute) and node.attr.startswith("__") and node.attr.endswith("__") \
                and node.attr not in ("__init__", "__name__"):
            flags.append("%s:%d attribute %s" % (fname, node.lineno, node.attr))
        if isinstance(node, ast.Name) and node.id.startswith("__") and node.id not in ("__name__",):
            flags.append("%s:%d name %s" % (fname, node.lineno, node.id))
    return flags


def load_package(zip_path, expected_sha256: str, extract_to, allow_flagged: bool = False, data: bytes = None) -> dict:
    """Refuses (PackageHashMismatch) unless sha256 of the exact bytes used equals expected_sha256.
    v6 (Odysseus v5 BP-1): extract_to=None VALIDATES ONLY (hash, members, meta, AST audit), so every package check runs
    BEFORE the key is read; `data` passes the exact bytes already validated, so extraction uses the same bytes."""
    data = Path(zip_path).read_bytes() if data is None else data
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
        if not n.endswith(ALLOWED_MEMBER_SUFFIXES):          # v2 (F2): no .pyc / binaries: unaudited code
            raise PackageInvalid("member %r is not .py/.json/.txt" % n)
        # v7 (Odysseus v6 1): a name that validates must also STAGE on every host: portable characters, no reserved
        # device names, no trailing dot/space, bounded length, no case-insensitive or file/directory collision
        parts = n.split("/")
        if len(n) > 180 or any(not re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", p) or p.endswith(".")
                               or p.split(".")[0].upper() in WINDOWS_RESERVED for p in parts):
            raise PackageInvalid("member name %r is not portable" % n)
        low = n.lower()
        if low in {k.lower() for k in files} or any(k.lower().startswith(low + "/") or low.startswith(k.lower() + "/")
                                                    for k in files):
            raise PackageInvalid("member name %r collides with another member" % n)
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
    if extract_to is None:
        return {"sha256": actual, "meta": meta, "entry": entry, "audit_flags": flags, "allow_flagged": bool(allow_flagged),
                "files": {n: sealbox.sha256_hex(b) for n, b in sorted(files.items())}}
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
                 gate_repo=None, gate_ref: Optional[str] = None, account: Optional[str] = None,
                 allowlist=None, gate_pins: Optional[dict] = None, delete_key: bool = False,
                 extra_probe_paths=(), verify_loaded: bool = True, secret_paths=SECRET_PATHS,
                 enforce_run_dir: bool = True, write_probe_paths=None, preflight_mkfile_dirs=None,
                 preflight: bool = True):
        self.manifest_path, self.ciphertext_path = Path(manifest_path), Path(ciphertext_path)
        self.key_path, self.package_zip = Path(key_path), Path(package_zip)
        self.package_sha256 = str(package_sha256).lower()
        self.out = Path(out_dir)
        self.allow_flagged, self.certify_kwargs = allow_flagged, dict(certify_kwargs or {})
        self.predict_timeout, self.max_episode_steps = predict_timeout, max_episode_steps
        self.resume, self.require_out_outside_git = resume, require_out_outside_git
        self.runner_id = runner_id
        self.account = account
        self.allowlist = protocol.DEFAULT_ALLOWLIST if allowlist is None else allowlist
        self.gate_pins, self.delete_key, self.verify_loaded = gate_pins, delete_key, verify_loaded
        self.probe_paths = [str(self.key_path)] + [str(x) for x in secret_paths] + [str(x) for x in extra_probe_paths]
        # v3: the child must not be able to APPEND to the receipts (default: this run's receipts file). With a child running
        # as the runner's own account this ALWAYS fails closed -- intentionally: the designation must provide a separate
        # child account (documented in FIREWALL.md v3).
        self.write_probe_paths = [str(self.out / "receipts.jsonl")] if write_probe_paths is None else \
            [str(x) for x in write_probe_paths]
        # v5 (Odysseus v4 S-1): the PREFLIGHT child, started before the key is read and before the run directory exists,
        # must not be able to create files in the output root (default) -- a same-account child fails HERE, harmlessly
        self.preflight_mkfile_dirs = [str(self.out.parent)] if preflight_mkfile_dirs is None else \
            [str(x) for x in preflight_mkfile_dirs]
        # constructor-only switch for in-process tests of later stages (a same-account child always fails the
        # preflight); the CLI never sets it
        self.do_preflight = preflight
        self.enforce_run_dir = enforce_run_dir
        self.gate_repo = Path(gate_repo) if gate_repo is not None else DEFAULT_GATE_REPO
        self.gate_ref = gate_ref or DEFAULT_GATE_REF
        self.phase = "INIT"
        self._prepared = None
        self.receipts = None
        self._proc = self._conn = None

    # ------------------------------------------------------------ open
    def prepare(self) -> dict:
        """v7 (Odysseus v6 items 1-2): EVERY check that can refuse, and every probe, BEFORE anything is consumed:
        gates, run-directory and manifest checks, package validation, STAGING of the package into the run directory,
        and the child isolation probe including a receipts STAND-IN in the run directory (read + append) and file
        creation in the run directory and its root. receipts.jsonl is the consumption marker, not the run directory:
        a refusal here leaves the key copy and the run retryable."""
        if not self.runner_id:
            raise protocol.RunnerNotDesignated("a runner id is required")
        if self.resume:
            raise RunnerRefusal("v2: resume is refused; a run is ONE invocation (predict -> seal -> certify -> close)")
        run_params = {"predict_timeout": self.predict_timeout, "max_episode_steps": self.max_episode_steps,
                      "certify_kwargs": self.certify_kwargs}
        self.gates = protocol.check_gates(self.gate_repo, "DESIGNATION", ref=self.gate_ref,
                                          package_sha256=self.package_sha256, runner_id=self.runner_id,
                                          account=self.account, run_params=run_params, allowlist=self.allowlist,
                                          verify_loaded=self.verify_loaded, pins=self.gate_pins)
        if self.enforce_run_dir and self.out.name != "run_" + str(self.gates.get("run_nonce")):
            raise protocol.RunParamsMismatch("the run directory must be run_<designation nonce> (one run per designation)")
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
        self.validate_package()                              # v6 (BP-1): every package check BEFORE the key is read
        rpath = self.out / "receipts.jsonl"
        if rpath.exists():
            raise RunnerRefusal("receipts.jsonl exists: this designation's run was already consumed")
        try:
            self.out.mkdir(parents=True, exist_ok=True)
            self.pkg = self._stage_package()                 # v7: staged BEFORE the key is read
            stand = self.out / "receipts.preflight"
            stand.write_text("", encoding="utf-8")
        except OSError as e:
            raise RunnerRefusal("staging failed before the key was read (%s): nothing consumed" % type(e).__name__)
        if self.do_preflight:
            dirs = self.preflight_mkfile_dirs + ([str(self.out)] if self.preflight_mkfile_dirs else [])
            self.out.parent.mkdir(parents=True, exist_ok=True)
            self._spawn_probe("", "", self.probe_paths, [str(stand)], dirs)
            self._stop_worker(kill=False)
            self._proc = self._conn = None
        stand.unlink()
        self._prepared = (manifest, ct, fam)
        return {"prepared": True, "run_dir": str(self.out)}

    def _stage_package(self) -> dict:
        """Extract the VALIDATED bytes into <run>/package. An existing staging (an earlier pre-key refusal) is reused
        only if it holds exactly the validated members, byte for byte."""
        d = self.out / "package"
        if d.exists():
            v = load_package(self.package_zip, self.package_sha256, None, self.allow_flagged, data=self._pkg_bytes)
            on_disk = {str(p.relative_to(d)).replace("\\", "/"): sealbox.sha256_file(p) for p in d.rglob("*")
                       if p.is_file()}
            if on_disk != v["files"]:
                raise RunnerRefusal("an earlier staged package differs from this package: the custodian must inspect "
                                    "and remove %s by hand" % d)
            return dict(v, dir=str(d))
        return load_package(self.package_zip, self.package_sha256, d, self.allow_flagged, data=self._pkg_bytes)

    def open(self) -> dict:
        """v7: prepare() (nothing consumed) -> receipts + open record (the consumption marker) -> key read. From the
        open record on, every failure ends in a TERMINAL receipt (close or abort), never an unsealed exit (run_all)."""
        if self._prepared is None:
            self.prepare()
        manifest, ct, fam = self._prepared
        self.manifest = manifest
        genesis = sealbox.sha256_hex(sealbox.canon_bytes({
            "format": RECEIPT_FORMAT, "spec_id": manifest["spec_id"],
            "ciphertext_sha256": manifest["ciphertext_sha256"], "commitment": manifest["commitment"],
            "package_sha256": self.package_sha256}))
        # the key is READ first (a missing or malformed key file refuses with nothing consumed), then the consumption
        # marker is written, then the released copy is deleted
        key = sealbox.read_hex_file(self.key_path, sealbox.KEY_BYTES)
        rpath = self.out / "receipts.jsonl"
        self.receipts = Receipts(rpath, genesis, create=True)
        self.N = int(manifest["n_worlds"])
        self.receipts.append("open", {
            "genesis": genesis, "utc": _utc(), "host": socket.gethostname(),
            "manifest_sha256": sealbox.sha256_file(self.manifest_path), "spec_id": manifest["spec_id"],
            "ciphertext_sha256": manifest["ciphertext_sha256"], "commitment": manifest["commitment"],
            "n_worlds": self.N, "runner_id": self.runner_id, "run_nonce": self.gates.get("run_nonce"),
            "account": self.account,
            "protocol_gates": {k: v for k, v in self.gates.items() if k.endswith("_commit") or k in ("ref", "auditor")},
            "package": {k: self.pkg[k] for k in ("sha256", "meta", "entry", "audit_flags", "allow_flagged", "files")},
            "runner_src_sha256": sealbox.src_sha_lf(Path(__file__)),
            "certify_src_sha256": sealbox.src_sha_lf(HERE.parent / "c3" / "certify.py"),
            "certify_kwargs": self.certify_kwargs, "predict_timeout_s": self.predict_timeout,
            "max_episode_steps_per_world": self.max_episode_steps,
            "python": sys.version.split()[0], "numpy": np.__version__})
        self.phase = "OPEN"
        if self.delete_key:                                  # v2 (S5): the released copy is gone before any child exists
            self.key_path.unlink()
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
        if self.N != len(self._worlds):
            raise HiddenSetMismatch("decrypted world count differs from the manifest")
        return manifest

    # ------------------------------------------------------------ predict
    def _spawn_probe(self, pkg_dir, entry, read_paths, write_paths, mkfile_dirs):
        ctx = mp.get_context("spawn")
        self._conn, child = ctx.Pipe(duplex=True)
        self._proc = ctx.Process(target=_worker_main, args=(child, pkg_dir, entry), daemon=True)
        self._proc.start()
        child.close()
        _send(self._conn, ["probe", list(read_paths), list(write_paths), list(mkfile_dirs)])
        try:                                                  # v5 (S-1): a child that cannot start is a refusal
            if not self._conn.poll(120):
                raise EOFError("no probe answer within 120 s")
            tag, res = _recv(self._conn)
        except (EOFError, OSError, ValueError, MemoryError, RecursionError) as e:
            self._stop_worker(kill=True)
            raise PredictorChildFailed("the predictor child did not start or answer the probe (%s)" % type(e).__name__)
        opened = [p for p, r in res if r not in ("denied", "missing")]      # 'opened' / 'writable' / 'error:*'
        if tag != "probe_result" or opened:
            self._stop_worker(kill=True)
            raise ChildNotIsolated("the predictor child can open: %s" % ", ".join(opened))

    def abort(self, exc: BaseException) -> dict:
        """v7 (Odysseus v6 item 2): after the consumption marker exists, ANY failure (package-induced or not) ends in a
        TERMINAL 'abort' receipt and a RESULT.json with status ABORTED, which custody can result-seal. Adjudication
        (Harmonia Addendum E): package-attributable -> FORFEIT; infrastructure -> VOID. Type name only, no text."""
        if self.receipts is None:
            raise RunnerRefusal("abort before the consumption marker: nothing to seal")
        if self.phase in ("CLOSED", "ABORTED"):
            return {"status": self.phase}
        try:
            self._stop_worker(kill=True)
        except Exception:                                    # noqa: BLE001
            pass
        n_pred = sum(1 for r in self.receipts.records if r["kind"] == "prediction")
        self.receipts.append("abort", {"phase": self.phase, "error_type": type(exc).__name__,
                                       "n_predictions_recorded": n_pred, "utc": _utc()})
        self.phase = "ABORTED"
        result = {"format": RECEIPT_FORMAT, "status": "ABORTED", "spec_id": self.manifest["spec_id"],
                  "run_nonce": self.gates.get("run_nonce"), "package_sha256": self.package_sha256,
                  "abort_phase": self.receipts.records[-1]["body"]["phase"], "error_type": type(exc).__name__,
                  "chain_head": self.receipts.head, "n_records": len(self.receipts.records)}
        (self.out / "RESULT.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n",
                                              encoding="utf-8", newline="\n")
        return result

    def run_all(self) -> dict:
        """prepare (refusal consumes nothing) -> open -> predict -> seal -> certify -> close; after the open record any
        exception becomes a terminal abort (v7)."""
        self.prepare()
        try:
            self.open()
            self.predict_all()
            self.seal_predictions()
            self.certify_all()
            return self.close()
        except BaseException as e:                           # noqa: BLE001 -- incl. KeyboardInterrupt / MemoryError
            if self.receipts is None:
                raise
            return self.abort(e)

    def validate_package(self) -> dict:
        """v6 (BP-1): read the package ONCE, verify its hash, members, metadata and AST audit, and keep those exact bytes
        for the later extraction. A refusal here happens before anything is consumed."""
        self._pkg_bytes = self.package_zip.read_bytes()
        return load_package(self.package_zip, self.package_sha256, None, self.allow_flagged, data=self._pkg_bytes)

    def write_preflight_record(self, out_dir) -> Path:
        """v6: the PUBLIC-FIELDS record custody requires before it releases the key (protocol.preflight_ok)."""
        rec = {"format": protocol.PREFLIGHT_FORMAT, "verdict": "PASS", "run_nonce": self.gates.get("run_nonce"),
               "spec_id": self.gates.get("spec_id"), "package_sha256": self.package_sha256,
               "runner_id": self.runner_id, "account": self.account, "host": socket.gethostname(), "utc": _utc()}
        p = Path(out_dir) / ("PREFLIGHT_%s.json" % rec["run_nonce"])
        p.write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        return p

    def preflight(self) -> dict:
        """v5 (Odysseus v4 S-1): start a predictor child exactly as a run would (spawn, same interpreter, same import
        guard) and run the isolation probe -- the released key path, every secret path, and file creation in the output
        root -- BEFORE the key is read, deleted or the run directory created. Refusal here consumes nothing: the key
        copy stays where custody put it. Also the check to run before custody releases the key (entry.py runner
        --preflight, no key needed)."""
        self.out.parent.mkdir(parents=True, exist_ok=True)
        self._spawn_probe("", "", self.probe_paths, [], self.preflight_mkfile_dirs)
        self._stop_worker(kill=False)
        self._proc = self._conn = None
        return {"preflight": "PASS", "probed": len(self.probe_paths) + len(self.preflight_mkfile_dirs)}

    def _start_worker(self):
        # v2 (F2): isolation probe. The child must be unable to open the released key path, every secret path and
        # this run's receipts; otherwise the package could read them. Fail closed.
        self._spawn_probe(self.pkg["dir"], self.pkg["entry"], self.probe_paths, self.write_probe_paths, [])
        _send(self._conn, ["go"])

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
            except (EOFError, OSError, ValueError, MemoryError, RecursionError):     # v4: hostile reply shapes
                self._stop_worker(kill=True)
                return {"status": "PREDICTOR_CRASH", "usage": usage}
            # v7 (Odysseus v6 item 2, V6-B2): the child controls these bytes; ANY malformed message or failed reply is
            # this world's PROTOCOL_ERROR (recorded, sealed, run continues), never an exception in the parent
            try:
                if not isinstance(msg, list) or not msg:
                    raise ValueError("malformed message")
                if msg[0] == "call":
                    usage["calls"] += 1
                    try:
                        reply = ["ret", self._serve(sysobj, msg[1], msg[2], usage)]
                    except Exception as e:                   # noqa: BLE001 -- type name only: no knob leak
                        reply = ["err", type(e).__name__]
                    _send(self._conn, reply)
                elif msg[0] == "done" and len(msg) == 3 and msg[1] == i:
                    why = validate_prediction(msg[2])
                    if why:
                        return {"status": "INVALID_PREDICTION", "reason": why, "usage": usage}
                    return {"status": "OK", "prediction": msg[2], "usage": usage}
                elif msg[0] == "fail" and len(msg) == 3 and msg[1] == i:
                    return {"status": "PREDICTOR_ERROR", "error": str(msg[2])[:400], "usage": usage}
                else:
                    raise ValueError("unexpected message")
            except Exception:                                # noqa: BLE001
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
                try:
                    self.certify_world(i)
                except OrderViolation:
                    raise
                except Exception as e:                       # noqa: BLE001 -- v7: recorded per world, type name only
                    self._gate(i)
                    self.receipts.append("certify", {"i": i, "world_tag": self._tags[i], "status": "CERTIFY_ERROR",
                                                     "error_type": type(e).__name__, "utc": _utc()})

    def close(self) -> dict:
        certs = {r["body"]["i"]: r for r in self.receipts.records if r["kind"] == "certify"}
        if sorted(certs) != list(range(self.N)):
            raise OrderViolation("close refused: %d/%d worlds certified" % (len(certs), self.N))
        preds = {r["body"]["i"]: r["body"] for r in self.receipts.records if r["kind"] == "prediction"}
        per_world = []
        for i in range(self.N):
            c = certs[i]["body"]
            ivr = c.get("intervention") or {"status": c.get("status", "CERTIFY_ERROR")}
            per_world.append({
                "i": i, "world_tag": c["world_tag"], "prediction_status": preds[i]["status"],
                "prediction": preds[i].get("prediction"), "base_class": (c.get("base") or {}).get("class"),
                "intervention_status": ivr["status"],
                "intervention_class": ivr.get("result", {}).get("class"),
                "delta_J_intact": ivr.get("delta_J_intact"), "certify_receipt": certs[i]["hash"]})
        self.receipts.append("close", {"n_certified": self.N, "utc": _utc()})
        self.phase = "CLOSED"
        seal = next(r for r in self.receipts.records if r["kind"] == "predictions_sealed")
        result = {"format": RECEIPT_FORMAT, "status": "CLOSED", "spec_id": self.manifest["spec_id"],
                  "run_nonce": self.gates.get("run_nonce"),
                  "package_sha256": self.package_sha256, "predictions_seal_hash": seal["hash"],
                  "chain_head": self.receipts.head, "n_records": len(self.receipts.records),
                  "per_world": per_world}
        (self.out / "RESULT.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n",
                                              encoding="utf-8", newline="\n")
        return result


def main(argv=None) -> int:
    """v2 CLI. Only through entry.py (which verifies the audited code BEFORE importing it). ONE invocation per
    designation: predict -> seal predictions -> certify -> close. The run parameters are READ FROM the designation
    record (no command-line knobs to cherry-pick, S4); the run directory is <out-root>/run_<designation nonce>; the
    released key file is deleted as soon as it has been read (S5)."""
    ap = argparse.ArgumentParser(description="holdout D2 across-the-firewall runner (v2)")
    ap.add_argument("--package")
    ap.add_argument("--package-sha256")
    ap.add_argument("--key")
    ap.add_argument("--out-root", default=str(DEFAULT_OUT_ROOT))
    ap.add_argument("--manifest", default=str(HERE / "MANIFEST_D2.json"))
    ap.add_argument("--ciphertext", default=str(HERE / "hidden_D2.enc"))
    ap.add_argument("--allow-flagged", action="store_true")
    ap.add_argument("--runner-id", help="must equal protocol/RUNNER_DESIGNATION.json runner_id")
    ap.add_argument("--gate-ref", default=DEFAULT_GATE_REF)
    ap.add_argument("--verify-receipts")
    ap.add_argument("--preflight", action="store_true",
                    help="v5: gates + a predictor child's isolation probe, no key needed; run BEFORE custody releases")
    a = ap.parse_args(argv)
    if a.verify_receipts:
        ok, recs, why = verify_receipts(a.verify_receipts)
        print(json.dumps({"ok": ok, "reason": why, "n_records": len(recs),
                          "head": recs[-1]["hash"] if recs else None}))
        return 0 if ok else 1
    if os.environ.get("C3D2_ENTRY") != "verified":
        raise RunnerRefusal("start the runner through entry.py (pre-import code verification)")
    if a.gate_ref != DEFAULT_GATE_REF:                         # v5 (Odysseus v4 S-4)
        print(json.dumps({"refused": True, "reason": "records are read from %s only" % DEFAULT_GATE_REF}))
        return 3
    if not (a.package and a.package_sha256 and a.runner_id and (a.key or a.preflight)):
        ap.error("--package, --package-sha256, --runner-id and (--key or --preflight) are required")
    try:
        return _run_cli(a)
    except (RunnerRefusal, protocol.GateRefusal) as e:          # v5: a refusal is reported, not a traceback
        print(json.dumps({"refused": True, "reason": "%s: %s" % (type(e).__name__, e)}))
        return 3


def _run_cli(a) -> int:
    account = os_account()
    g = protocol.check_gates(DEFAULT_GATE_REPO, "DESIGNATION", ref=a.gate_ref, package_sha256=a.package_sha256,
                             runner_id=a.runner_id, account=account, verify_loaded=True)
    rp = g["run_params"]
    out = Path(a.out_root) / ("run_" + g["run_nonce"])
    if (out / "receipts.jsonl").exists():                   # v7: receipts are the consumption marker
        raise RunnerRefusal("this designation's run was already consumed (receipts exist): one run per designation")
    run = FirewallRun(a.manifest, a.ciphertext, a.key or str(out.parent / "no_key_in_preflight.hex"), a.package,
                      a.package_sha256, out,
                      allow_flagged=a.allow_flagged, certify_kwargs=rp.get("certify_kwargs") or {},
                      predict_timeout=rp["predict_timeout"], max_episode_steps=rp["max_episode_steps"],
                      runner_id=a.runner_id, gate_ref=a.gate_ref, account=account, delete_key=True,
                      extra_probe_paths=[str(out / "receipts.jsonl")])
    if a.preflight:
        r = run.prepare()                                     # v7: validation, staging and every probe
        r["preflight"] = "PASS"
        r["record"] = str(run.write_preflight_record(out.parent))
        print(json.dumps(r))
        return 0
    res = run.run_all()
    print(json.dumps({"status": res["status"], "chain_head": res["chain_head"], "out": str(out)}))
    return 0 if res["status"] == "CLOSED" else 4


if __name__ == "__main__":
    sys.exit(main())
