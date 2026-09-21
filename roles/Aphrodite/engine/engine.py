"""The Aphrodite local engine: the smallest substrate in which a lineage can produce a
bounded artifact, the artifact can be extracted, and a FRESH recipient can either
benefit from it or not (operator directive, 2026-09-21).

Four hard boundaries: WORKER (does the task), IMPROVER (proposes edits to the five
modules), ARTIFACT VAULT (only the frozen generation-N module bytes), EVALUATOR
(invisible; returns a scalar). Everything else is disposable.

Offline by construction: no network, no model call. The worker is deterministic
code, so "machinery" (code that can solve a family) and "state" (cached answers to
instances) are separable by construction -- which is the distinction Campaign 1
exists to make. A model backend can replace the worker later without touching the
membrane.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import random
import re
import shutil
import tempfile
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

MODULE_NAMES = ("search", "verify", "allocate", "memory", "evidence")
FAMILIES = ("arith", "sortkey", "strops", "numtheory")
MARKER_ENV_PREFIX = "APHRODITE_MARKER_"
MARKER_DIR = Path(tempfile.gettempdir()) / "aphrodite_engine_markers"
LOADER_PATH = "engine.Recipient.load/v1"     # the ONE loader path every arm uses


def source_hash() -> str:
    """sha256 of this engine's own source, so a receipt names the engine it came from."""
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


class BoundaryViolation(Exception):
    """Something other than the hashed artifact tried to cross, or a hash lied."""


class EscrowExhausted(Exception):
    """The compute escrow, which lives beneath the improver, is spent."""


# ---------------------------------------------------------------- compute escrow
class Escrow:
    def __init__(self, limit: int):
        self.limit, self.spent = int(limit), 0

    def charge(self, n: int = 1) -> None:
        if self.spent + n > self.limit:
            raise EscrowExhausted(f"escrow {self.limit} exhausted at {self.spent}")
        self.spent += n

    def remaining(self) -> int:
        return self.limit - self.spent


# ---------------------------------------------------------------- tasks (the world)
def _task(family: str, rng: random.Random):
    if family == "arith":
        a, b, c, d = (rng.randint(2, 99) for _ in range(4))
        return f"Compute ({a} + {b}) * {c} - {d}.", str((a + b) * c - d)
    if family == "sortkey":
        xs = [rng.randint(0, 999) for _ in range(8)]
        return ("Sort by last digit, ties ascending: " + ", ".join(map(str, xs)),
                ",".join(map(str, sorted(xs, key=lambda x: (x % 10, x)))))
    if family == "strops":
        ws = [rng.choice(["alpha", "delta", "sigma", "omega", "kappa"]) for _ in range(5)]
        return ("Reverse the words and capitalise each: " + " ".join(ws),
                " ".join(w.capitalize() for w in reversed(ws)))
    a, b = rng.randint(12, 999), rng.randint(12, 999)
    return f"Give gcd({a}, {b}) + lcm({a}, {b}).", str(math.gcd(a, b) + a * b // math.gcd(a, b))


def tasks(family: str, n: int, seed: int) -> List[Dict]:
    rng = random.Random((seed, family).__str__())
    out = []
    for _ in range(n):
        p, g = _task(family, rng)
        out.append({"family": family, "prompt": p, "gold": g,
                    "key": hashlib.sha256(p.encode()).hexdigest()[:16]})
    return out


# ---------------------------------------------------------------- the artifact and the vault
@dataclass(frozen=True)
class Artifact:
    bytes: bytes
    generation: int
    sha256: str

    @staticmethod
    def canonical(modules: Dict[str, str]) -> bytes:
        return json.dumps(modules, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True).encode("utf-8")

    @classmethod
    def from_modules(cls, modules: Dict[str, str], generation: int = 0) -> "Artifact":
        b = cls.canonical(modules)
        return cls(bytes=b, generation=generation, sha256=hashlib.sha256(b).hexdigest())

    @classmethod
    def from_bytes(cls, b: bytes, generation: int = 0) -> "Artifact":
        return cls(bytes=b, generation=generation, sha256=hashlib.sha256(b).hexdigest())

    def modules(self) -> Dict[str, str]:
        return json.loads(self.bytes.decode("utf-8"))


# ---------------------------------------------------------------- the base image (I_0)
BASE_SEARCH = '''
N_CANDIDATES = 1
def solvers():
    # math and re are provided by the loader namespace; modules never import
    def arith(p):
        m = re.search(r"\\((\\d+) \\+ (\\d+)\\) \\* (\\d+) - (\\d+)", p)
        a, b, c, d = (int(x) for x in m.groups())
        return str((a + b) * c - d)
    def sortkey(p):
        xs = [int(x) for x in re.findall(r"\\d+", p.split(":", 1)[1])]
        return ",".join(map(str, sorted(xs, key=lambda x: (x % 10, x))))
    def strops(p):
        ws = p.split(":", 1)[1].split()
        return " ".join(w.capitalize() for w in reversed(ws))
    return {"arith": arith, "sortkey": sortkey, "strops": strops}
'''

BASE_VERIFY = '''
STRICT = True
def accept(answer, task):
    return isinstance(answer, str) and len(answer) > 0
'''

BASE_ALLOCATE = '''
def budget(task, remaining):
    return 1
'''

BASE_MEMORY = '''
def lookup(state, task):
    return state.get(task["key"])
def store(state, task, answer):
    state[task["key"]] = answer
'''

BASE_EVIDENCE = '''
def summarise(results):
    n = len(results) or 1
    return {"n": n, "accuracy": sum(1 for r in results if r["correct"]) / n}
'''


def base_image() -> Dict[str, str]:
    return {"search": BASE_SEARCH, "verify": BASE_VERIFY, "allocate": BASE_ALLOCATE,
            "memory": BASE_MEMORY, "evidence": BASE_EVIDENCE}


def positive_control_artifact() -> Artifact:
    """A hand-written, known-useful module: the numtheory solver the base image lacks."""
    mods = base_image()
    mods["search"] = BASE_SEARCH.replace(
        '    return {"arith": arith, "sortkey": sortkey, "strops": strops}',
        '    def numtheory(p):\n'
        '        nums = re.findall(r"\\d+", p)\n'
        '        a, b = int(nums[0]), int(nums[1])\n'
        '        g = math.gcd(a, b)\n'
        '        return str(g + a * b // g)\n'
        '    return {"arith": arith, "sortkey": sortkey, "strops": strops, "numtheory": numtheory}')
    return Artifact.from_modules(mods, generation=-1)


def memorised_state(seen: List[Dict]) -> Dict[str, str]:
    """Donor STATE: answers to the instances it saw. Useless on fresh instances."""
    return {t["key"]: t["gold"] for t in seen}


# ---------------------------------------------------------------- module loading (sandbox)
SAFE_BUILTINS = {"len": len, "range": range, "sorted": sorted, "sum": sum, "min": min, "max": max,
                 "int": int, "str": str, "isinstance": isinstance, "enumerate": enumerate,
                 "list": list, "dict": dict, "map": map, "zip": zip, "abs": abs, "any": any, "all": all,
                 "reversed": reversed, "tuple": tuple, "set": set, "float": float, "bool": bool,
                 "divmod": divmod, "round": round, "filter": filter}


def _load_modules(modules: Dict[str, str]) -> Dict[str, Dict]:
    out = {}
    for name in MODULE_NAMES:
        ns: Dict = {"__builtins__": SAFE_BUILTINS, "math": math, "re": re}
        exec(modules[name], ns)          # noqa: S102 -- the engine's whole purpose is to run evolved code
        out[name] = ns
    return out


# ---------------------------------------------------------------- the recipient
class Recipient:
    def __init__(self, seed: int):
        self.seed = seed
        self.id = uuid.uuid4().hex[:12]
        self.workspace = MARKER_DIR / f"recipient_{self.id}"
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.state: Dict[str, str] = {}
        self._ns = None
        self._log: List[Dict] = []
        self._loaded = False

    # -- creation from the canonical base image, with every prior marker destroyed
    @classmethod
    def fresh(cls, seed: int) -> "Recipient":
        if MARKER_DIR.exists():
            shutil.rmtree(MARKER_DIR, ignore_errors=True)
        MARKER_DIR.mkdir(parents=True, exist_ok=True)
        for k in [k for k in os.environ if k.startswith(MARKER_ENV_PREFIX)]:
            del os.environ[k]
        return cls(seed)

    # -- the ONE loader path: scratch, transplant, sham and positive all come through here
    def load(self, artifact: Optional[Artifact], memory: Optional[Dict] = None,
             smuggle: Optional[Dict] = None) -> Dict:
        crossed, donor_reads = [], []
        if smuggle:
            for k in smuggle:
                self._log.append({"violation": f"extra_payload:{k}"})
            raise BoundaryViolation(f"extra payload offered to the recipient: {sorted(smuggle)}")
        if artifact is None:
            modules = base_image()
            h_ext = h_load = None
        else:
            h_ext = artifact.sha256
            h_load = hashlib.sha256(artifact.bytes).hexdigest()
            if h_ext != h_load:
                self._log.append({"violation": "hash_mismatch", "claimed": h_ext, "actual": h_load})
                raise BoundaryViolation("artifact hash at load differs from the hash at extraction")
            modules = artifact.modules()
            crossed.append("artifact_bytes")
            donor_reads.append(h_load)
        if memory is not None:
            self.state.update(memory)
            crossed.append("memory_state")
        self._ns = _load_modules(modules)
        self._loaded = True
        receipt = {"loader_path": LOADER_PATH, "recipient": self.id, "seed": self.seed,
                   "hash_at_extraction": h_ext, "hash_at_load": h_load,
                   "crossed": crossed, "donor_reads": donor_reads,
                   "modules": sorted(modules), "reset": self.reset_receipt()}
        self._log.append(receipt)
        return receipt

    # -- the evaluator is invisible: it returns a scalar, never its tasks or code
    def run_tasks(self, task_list: List[Dict], escrow: Escrow) -> Dict:
        if not self._loaded:
            raise RuntimeError("recipient has no modules loaded")
        solvers = self._ns["search"]["solvers"]()
        results, exhausted = [], False
        for t in task_list:
            try:
                escrow.charge(self._ns["allocate"]["budget"](t, escrow.remaining()))
            except EscrowExhausted:
                exhausted = True
                break
            ans = self._ns["memory"]["lookup"](self.state, t)
            if ans is None:
                fn = solvers.get(t["family"])
                try:
                    ans = fn(t["prompt"]) if fn else None
                except Exception:      # noqa: BLE001 -- an evolved solver may simply be wrong
                    ans = None
            ok = bool(ans) and self._ns["verify"]["accept"](ans, t) and ans == t["gold"]
            results.append({"correct": ok})
        ev = self._ns["evidence"]["summarise"](results)
        return {"evaluated": len(results), "accuracy": ev["accuracy"], "escrow_exhausted": exhausted}

    # -- reset integrity fixtures
    def plant_markers(self) -> None:
        (self.workspace / "marker.tmp").write_text("forbidden", encoding="utf-8")
        os.environ[MARKER_ENV_PREFIX + self.id] = "forbidden"
        self.state["__marker__"] = "forbidden"

    def markers_present(self) -> bool:
        return (any(MARKER_DIR.rglob("marker.tmp")) or
                any(k.startswith(MARKER_ENV_PREFIX) for k in os.environ) or
                "__marker__" in self.state)

    def reset_receipt(self) -> Dict:
        return {"markers_destroyed": not self.markers_present(), "workspace": str(self.workspace),
                "env_markers": [k for k in os.environ if k.startswith(MARKER_ENV_PREFIX)]}

    def boundary_log(self) -> List[Dict]:
        return self._log

    def dump_state(self) -> str:
        return json.dumps(self.state, sort_keys=True)


# ---------------------------------------------------------------- the lineage (donor side)
class _State(dict):
    def remember(self, k: str, v: str) -> None:
        self[k] = v


@dataclass
class Lineage:
    seed: int
    base: Dict[str, str]
    generation: int = 0
    modules: Dict[str, str] = field(default_factory=dict)
    state: _State = field(default_factory=_State)
    history: List[Dict] = field(default_factory=list)

    def __post_init__(self):
        self.modules = dict(self.base)

    # the improver: a fixed operator set over the five modules; it never touches the escrow
    def _variants(self, rng: random.Random) -> List[Dict[str, str]]:
        out = [dict(self.modules)]
        for k in (2, 3):
            v = dict(self.modules)
            v["search"] = re.sub(r"N_CANDIDATES = \d+", f"N_CANDIDATES = {k}", v["search"])
            out.append(v)
        v = dict(self.modules)
        v["verify"] = v["verify"].replace("STRICT = True", f"STRICT = {rng.choice([True, False])}")
        out.append(v)
        return out

    def evolve(self, generations: int, escrow: Escrow, dev_seed: int = 7) -> None:
        rng = random.Random(self.seed)
        for _ in range(generations):
            dev = tasks(family=rng.choice(["arith", "sortkey", "strops"]), n=5, seed=dev_seed + self.generation)
            best, best_score = None, -1.0
            for cand in self._variants(rng):
                r = Recipient(self.seed)          # an internal probe, not a Campaign 1 recipient
                r.load(Artifact.from_modules(cand))
                score = 0
                for t in dev:
                    escrow.charge(1)              # beneath the improver: propagates when exhausted
                    out = r.run_tasks([t], Escrow(4))
                    score += out["accuracy"]
                if score > best_score:
                    best, best_score = cand, score
            self.modules = best
            self.generation += 1
            self.history.append({"generation": self.generation, "score": best_score / max(len(dev), 1)})

    def extract(self, generation: int) -> Artifact:
        if generation != self.generation:
            raise ValueError(f"extraction point is positional: only generation {self.generation} may be taken")
        return Artifact.from_modules(self.modules, generation=generation)
