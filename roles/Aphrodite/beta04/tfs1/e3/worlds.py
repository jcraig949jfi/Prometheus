"""E3 world access: the ARM VIEW (what a lifetime may read) and the EVALUATOR side (coordinator only), plus a file-access
log used to prove that a lifetime opened nothing but arm-view files.

Layout consumed (foundry OUTPUT files only; no foundry code is read or imported):
  <root>/arm_view/ARM_VIEW_MANIFEST.json          {"worlds": {A...: {"files": {relpath: sha256}}}}
  <root>/arm_view/<A...>/<opaque>.json            {"id": opaque, "dev": [[input, output], ...]}   (no type, no rung)
  <root>/WORLD_MANIFEST.json                      coordinator side: arm_world ids, presentation ORDERS, id_map
  <root>/evaluator/<W>/<family_id>.json           coordinator side: test, tribunal, witness, rung, provenance
  <root>/<W>/WORLD_SEALED.json                    coordinator side: mechanisms, families (mechanisms_used)

Information boundary. `ArmWorld` reads ONLY the arm-view manifest and the arm-view files of ONE arm world, verifying
each file's sha256 against the manifest. Presentation orders (lists of opaque ids) are extracted by the COORDINATOR
side (`presentation_order`) before a lifetime starts and passed in as a plain list. Everything else (`Evaluator`,
`Sealed`) is coordinator side and is used only by e3_known_positive, final_eval and dependency.
"""
import builtins
import hashlib
import io
import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, List, Optional

from tfs1 import core as C


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def infer_type(v) -> str:
    if isinstance(v, bool):
        return C.BOOL
    if isinstance(v, list):
        return C.LIST
    if isinstance(v, int):
        return C.INT
    raise ValueError("cannot infer contract type of %r" % (v,))


# ================================================================ access log
class AccessLog:
    """Records every path opened through builtins.open / io.open / os.open while active."""

    def __init__(self):
        self.paths: List[str] = []

    @contextmanager
    def active(self):
        orig_open, orig_io_open, orig_os_open = builtins.open, io.open, os.open
        log = self.paths

        def rec(p):
            try:
                log.append(str(Path(os.fsdecode(p)).resolve()) if not isinstance(p, int) else "fd:%d" % p)
            except Exception:                      # noqa: BLE001
                log.append(repr(p))

        def b_open(file, *a, **k):
            rec(file)
            return orig_open(file, *a, **k)

        def o_open(path, *a, **k):
            rec(path)
            return orig_os_open(path, *a, **k)
        builtins.open = b_open
        io.open = b_open
        os.open = o_open
        try:
            yield self
        finally:
            builtins.open, io.open, os.open = orig_open, orig_io_open, orig_os_open

    def outside(self, allowed_dir) -> List[str]:
        root = str(Path(allowed_dir).resolve())
        return [p for p in self.paths if not p.startswith(root)]


# ================================================================ arm view (lifetime side)
class ArmWorld:
    """One arm world: opaque id -> dev examples. Lazy, sha-verified, reads only <root>/arm_view."""

    def __init__(self, root, arm_world: str):
        self.root = Path(root)
        self.arm_world = arm_world
        self.view_dir = self.root / "arm_view"
        man = json.loads((self.view_dir / "ARM_VIEW_MANIFEST.json").read_bytes().decode())
        files = man["worlds"][arm_world]["files"]
        self.files = {Path(rel).stem: (self.root / rel, h) for rel, h in files.items()}
        self.reads = 0
        self._cache: Dict[str, Dict] = {}

    def ids(self) -> List[str]:
        return sorted(self.files)

    def family(self, opaque: str) -> Dict:
        if opaque in self._cache:
            return self._cache[opaque]
        path, h = self.files[opaque]
        b = path.read_bytes()
        if sha256_bytes(b) != h:
            raise ValueError("arm-view file hash mismatch: %s" % path)
        self.reads += 1
        d = json.loads(b.decode())
        if d["id"] != opaque:
            raise ValueError("opaque id mismatch in %s" % path)
        dev = [[list(i), o] for i, o in d["dev"]]
        types = {infer_type(o) for _i, o in dev}
        if len(types) != 1:
            raise ValueError("mixed output types in %s" % path)
        fam = {"opaque": opaque, "slot": "%s/%s" % (self.arm_world, opaque), "output_type": types.pop(), "dev": dev,
               "file_sha256": h}
        self._cache[opaque] = fam
        return fam


# ================================================================ coordinator side
def world_manifest(root) -> Dict:
    return json.loads((Path(root) / "WORLD_MANIFEST.json").read_text())


def presentation_order(root, world_id: str, order_name: str = "CURRICULUM") -> Dict:
    """Coordinator side: the arm world id and the presentation order (opaque ids only)."""
    w = world_manifest(root)["worlds"][world_id]
    return {"world_id": world_id, "arm_world": w["arm_world"], "order_name": order_name,
            "order": list(w["orders"][order_name]["order"])}


class Evaluator:
    """Coordinator side: opaque id -> family_id, rung, status, test, tribunal, witness (evaluator files)."""

    def __init__(self, root, world_id: str, override_dir: Optional[str] = None):
        self.root = Path(root)
        self.world_id = world_id
        w = world_manifest(root)["worlds"][world_id]
        self.id_map = w["id_map"]
        self.evaluator_files = w["evaluator_files"]
        self.dir = Path(override_dir) if override_dir else self.root / "evaluator" / world_id
        self._cache: Dict[str, Dict] = {}

    def meta(self, opaque: str) -> Dict:
        return self.id_map[opaque]

    def task(self, opaque: str) -> Dict:
        if opaque in self._cache:
            return self._cache[opaque]
        fid = self.id_map[opaque]["family_id"]
        d = json.loads((self.dir / ("%s.json" % fid)).read_text())
        d["dev"] = [[list(i), o] for i, o in d["dev"]]
        d["test"] = [[list(i), o] for i, o in d["test"]]
        d["tribunal"] = [[list(i), o] for i, o in d.get("tribunal", [])]
        if "output_type" not in d or d["output_type"] not in C.VALUE_TYPES:
            d["output_type"] = infer_type(d["dev"][0][1])
        self._cache[opaque] = d
        return d

    def admitted(self, rungs=("R3", "R4")) -> List[str]:
        return sorted(o for o, m in self.id_map.items() if m["status"] == "ADMITTED" and m["rung"] in rungs)


def _agree(fn, examples) -> bool:
    """Value-or-FAIL agreement: an expected output "FAIL" (the evaluator files' encoding) requires a FAIL."""
    for i, o in examples:
        v = C.run(fn, list(i))
        if not C.same_value(v, o):
            return False
    return True


def judge(program: str, task: Dict, lib=None) -> Dict:
    """Test + tribunal verdict (foundry definition: correct on every test AND every tribunal example; expected
    outputs are compared value-or-FAIL, "FAIL" == the interpreter's FAIL sentinel)."""
    t = C.parse(program)
    fn = C.compile_term(t, lib, None, swap=lib is not None)
    u = (C.U[0], C.U[1])
    test_ok = _agree(fn, task["test"])
    trib = [(list(i), o) for i, o in task.get("tribunal", [])]
    trib_ok = _agree(fn, trib) if trib else None
    C.U[0], C.U[1] = u
    return {"test_ok": test_ok, "tribunal_ok": trib_ok, "qualified": bool(test_ok and trib_ok is not False),
            "n_test": len(task["test"]), "n_tribunal": len(trib)}


def sealed(root, world_id: str) -> Dict:
    return json.loads((Path(root) / world_id / "WORLD_SEALED.json").read_text())
