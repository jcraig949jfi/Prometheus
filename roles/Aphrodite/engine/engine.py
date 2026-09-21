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
# The engine v1 task distribution, declared pre-data in
# science/campaign1/AMENDMENT_2_2026-09-21.md section C. Each class is
# scored separately; HEADROOM_FAMILIES are the two independently scored
# classes the base image cannot solve (R5 of the replacement rule).
FAMILIES = ("arith", "sortkey", "strops", "numtheory", "modexp")
HEADROOM_FAMILIES = ("numtheory", "modexp")
DEV_FAMILIES = FAMILIES          # the improver develops against all classes
DEV_PER_FAMILY = 2               # deliberately small: overfitting must stay
                                 # reachable so the held-out tests can catch it
MARKER_ENV_PREFIX = "APHRODITE_MARKER_"
MARKER_DIR = Path(tempfile.gettempdir()) / "aphrodite_engine_markers"
LOADER_PATH = "engine.Recipient.load/v1"     # the ONE loader path every arm uses


FROZEN_GENERATION = 8            # the positional extraction point

# ---------------------------------------------------------------- entropy domains
# Frozen derivation rule, AMENDMENT_3_2026-09-21.md section 1. Development and
# search entropy are derived from a preregistered lineage identifier. Tribunal
# entropy is drawn from a DISJOINT domain that contains no lineage identifier,
# so no lineage can influence or predict what will judge it.
def _h64(domain: str) -> int:
    return int(hashlib.sha256(domain.encode()).hexdigest()[:16], 16)


def dev_entropy(lineage_id: str, generation: int) -> int:
    return _h64("APHRODITE/ENGINE/DEV/v1/%s/%d" % (lineage_id, generation))


def search_entropy(lineage_id: str) -> int:
    return _h64("APHRODITE/ENGINE/SEARCH/v1/%s" % lineage_id)


def tribunal_entropy(capability_class: str, index: int) -> int:
    return _h64("APHRODITE/ENGINE/TRIBUNAL/v1/%s/%d" % (capability_class, index))


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
    if family == "modexp":
        a, b, m = rng.randint(2, 99), rng.randint(2, 12), rng.randint(7, 9999)
        return f"Give ({a} ** {b}) mod {m}.", str(pow(a, b) % m)
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
DISCOVERED = {}
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
    out = {"arith": arith, "sortkey": sortkey, "strops": strops}
    out.update(DISCOVERED)
    return out
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


POSITIVE_CONTROL_SOLVERS = '''
def _pc_numtheory(p):
    nums = re.findall(r"\\d+", p)
    a, b = int(nums[0]), int(nums[1])
    g = math.gcd(a, b)
    return str(g + a * b // g)
def _pc_modexp(p):
    nums = re.findall(r"\\d+", p)
    a, b, m = int(nums[0]), int(nums[1]), int(nums[2])
    return str(pow(a, b) % m)
DISCOVERED["numtheory"] = _pc_numtheory
DISCOVERED["modexp"] = _pc_modexp
'''


def positive_control_artifact() -> Artifact:
    """Hand-written, known-useful machinery: solvers for BOTH headroom classes.

    This is the SENSITIVITY gate (R2), not a discovery. It is written by the
    experimenter and proves only that the substrate can carry a transferable
    improvement -- never that a lineage can find one.
    """
    mods = base_image()
    mods["search"] = BASE_SEARCH + POSITIVE_CONTROL_SOLVERS
    return Artifact.from_modules(mods, generation=-1)


# ---------------------------------------------------------------- endogenous discovery
# The improver's mutation space includes SYNTHESIS: bottom-up enumerative
# program search over a fixed primitive set, with observational-equivalence
# pruning. The primitive set is declared in full in README.md and in
# AMENDMENT 2 section C. It contains NO primitive equal to either headroom
# target, so both are reachable by COMPOSITION and neither by lookup.
#
# Honest label, stated before the search was ever run: a solver found this
# way has mechanism class PROGRAM_COMPOSITION, not ALGORITHMIC_STRUCTURE --
# the search composes existing primitives, it does not invent control flow.
PRIMITIVES = {
    "add":  (lambda x, y: x + y,                     "({0} + {1})"),
    "sub":  (lambda x, y: x - y,                     "({0} - {1})"),
    "mul":  (lambda x, y: x * y,                     "({0} * {1})"),
    "fdiv": (lambda x, y: None if y == 0 else x // y, "({0} // {1})"),
    "mod":  (lambda x, y: None if y == 0 else x % y,  "({0} % {1})"),
    "gcd":  (lambda x, y: math.gcd(abs(x), abs(y)),  "math.gcd(abs({0}), abs({1}))"),
    "powr": (lambda x, y: None if not (0 <= y <= 32) else x ** y, "pow({0}, {1})"),
}
TERMINALS = 3                     # nums[0], nums[1], nums[2]
VALUE_CEILING = 10 ** 18          # candidates producing larger values are dropped
MAX_SYNTH_CANDIDATES = 40000      # hard cap per synthesis attempt


# ---------------------------------------------------------------- grammar v2
# SLICE 2C: repair of the asymmetric enumerator, versioned and hashed
# separately from the slice-2B grammar. v1 built each round as
# op(LEFT from the previous frontier, RIGHT from the pool), which can never
# construct op(terminal, deep) -- the gap the numtheory witness sat in.
# v2 enumerates BY SIZE: for size s, every split (i, j) with i + j = s - 1,
# both directions. Nothing else is expanded: same primitives, same task
# distribution, same tribunal.
GRAMMAR_VERSION = "v2-size-indexed-symmetric"
MAX_SIZE = 4                      # operator applications; terminals are size 0


def grammar_hash() -> str:
    """Identity of the exact search space, for the reachability certificate."""
    spec = json.dumps({
        "version": GRAMMAR_VERSION,
        "max_size": MAX_SIZE,
        "terminals": TERMINALS,
        "primitives": {k: v[1] for k, v in sorted(PRIMITIVES.items())},
        "value_ceiling": VALUE_CEILING,
        "loop_bound": LOOP_BOUND,
    }, sort_keys=True)
    return hashlib.sha256(spec.encode()).hexdigest()


def _compose_v2(vectors: List[List[int]], golds: List[str], escrow: Escrow, cap: int,
                extra: Optional[List[tuple]] = None,
                rng: Optional[random.Random] = None) -> Optional[tuple]:
    """Size-indexed bottom-up enumeration with observational-equivalence pruning.

    Returns (source, size, charges) or None.
    """
    def matches(vals):
        return all(str(v) == g for v, g in zip(vals, golds))

    terminals = [("nums[%d]" % i, tuple(v[i] for v in vectors)) for i in range(TERMINALS)]
    terminals += list(extra or [])
    if rng is not None:
        rng.shuffle(terminals)

    pools: Dict[int, List[tuple]] = {0: []}
    seen = set()
    for src, vals in terminals:
        if vals in seen:
            continue
        seen.add(vals)
        pools[0].append((src, vals))
        if matches(vals):
            return src, 0, 0

    ops = list(PRIMITIVES.items())
    spent = 0
    for s in range(1, MAX_SIZE + 1):
        pools[s] = []
        splits = [(i, s - 1 - i) for i in range(s)]     # includes (0, s-1) and (s-1, 0)
        if rng is not None:
            rng.shuffle(splits)
            rng.shuffle(ops)
        for _name, (fn, tmpl) in ops:
            for i, j in splits:
                for lsrc, lvals in pools[i]:
                    for rsrc, rvals in pools[j]:
                        if spent >= cap or escrow.remaining() <= 0:
                            return None
                        escrow.charge(1)
                        spent += 1
                        try:
                            vals = tuple(fn(a, b) for a, b in zip(lvals, rvals))
                        except Exception:      # noqa: BLE001
                            continue
                        if any(v is None or abs(v) > VALUE_CEILING for v in vals):
                            continue
                        if vals in seen:
                            continue
                        seen.add(vals)
                        src = tmpl.format(lsrc, rsrc)
                        if matches(vals):
                            return src, s, spent
                        pools[s].append((src, vals))
    return None


GRAMMAR_V1_VERSION = "v1-frontier-asymmetric"   # SLICE 2B, preserved for reproduction


def _compose(vectors: List[List[int]], golds: List[str], escrow: Escrow, cap: int,
             extra: Optional[List[tuple]] = None,
             rng: Optional[random.Random] = None) -> Optional[str]:
    """SLICE 2B GRAMMAR v1 -- retained ONLY to reproduce the 0/16 result.

    Its asymmetry (LEFT from the previous frontier only) is the defect that
    made the numtheory witness unreachable. Not used by slice 2C.

    Two combination rounds, so the deepest expression constructible is
    op(depth2, depth2). `extra` supplies additional TERMINALS -- this is how a
    discovered helper becomes an intermediate representation, and it is what
    makes add(h, fdiv(mul(a,b), h)) reachable when the helper-free form of the
    same program is depth 4 and is not.
    """
    def matches(vals):
        return all(str(v) == g for v, g in zip(vals, golds))

    pool, seen = [], set()
    terminals = [("nums[%d]" % i, tuple(v[i] for v in vectors)) for i in range(TERMINALS)]
    terminals += list(extra or [])
    if rng is not None:
        rng.shuffle(terminals)
    for src, vals in terminals:
        if vals in seen:
            continue
        seen.add(vals)
        pool.append((src, vals))
        if matches(vals):
            return src

    ops = list(PRIMITIVES.items())
    if rng is not None:
        rng.shuffle(ops)

    spent = 0
    frontier = list(pool)
    for _ in range(2):            # depth 2 then depth 3
        new = []
        for _name, (fn, tmpl) in ops:
            for lsrc, lvals in frontier:
                for rsrc, rvals in pool:
                    if spent >= cap or escrow.remaining() <= 0:
                        return None
                    escrow.charge(1)      # the search is metered beneath the improver
                    spent += 1
                    try:
                        vals = tuple(fn(a, b) for a, b in zip(lvals, rvals))
                    except Exception:     # noqa: BLE001 -- a bad composition is just wrong
                        continue
                    if any(v is None or abs(v) > VALUE_CEILING for v in vals):
                        continue
                    if vals in seen:      # observational equivalence
                        continue
                    seen.add(vals)
                    src = tmpl.format(lsrc, rsrc)
                    if matches(vals):
                        return src
                    new.append((src, vals))
        pool = pool + new
        frontier = new
    return None


def _synthesise(examples: List[Dict], escrow: Escrow, cap: int,
                rng: Optional[random.Random] = None) -> Optional[str]:
    """Composition-only search (v1 behaviour, unchanged in substance).

    `examples` are development instances ONLY; held-out and tribunal
    instances are never visible here.
    """
    vectors = []
    for t in examples:
        nums = [int(x) for x in re.findall(r"-?\d+", t["prompt"])]
        if len(nums) < TERMINALS:
            return None
        vectors.append(nums)
    got = _compose_v2(vectors, [t["gold"] for t in examples], escrow, cap, rng=rng)
    return got[0] if got else None


# ---------------------------------------------------------------- Tier-2 structure
# AMENDMENT 3 section 5. A helper with a BOUNDED loop whose update expressions
# are SEARCHED, not supplied: Euclid is E1 = y, E2 = (x % y), and is therefore
# discoverable rather than handed. Memoization and multi-subprocedure
# decomposition are permitted by the ruling but NOT implemented this slice.
LOOP_BOUND = 64
# SLICE 2C: the arbitrary truncation is removed. The helper space is bounded
# by the declared grammar (update expressions of depth <= 2 over {x, y}), which
# yields 48 distinct helpers on two development instances -- Euclid is rank 44,
# so a cap of 40 silently excluded the only witness for numtheory. This raises
# no budget: the full enumeration is measured in the reachability certificate.
HELPER_CANDIDATE_CAP = 1024       # effectively "all distinct helpers"
PER_HELPER_CANDIDATE_CAP = 120000
STRUCTURAL_ATTEMPTS_PER_LINEAGE = 2


def helper_solver_source(family: str, e1: str, e2: str, answer: str) -> str:
    """Bounded helper + the answer expression that calls it."""
    return (
        "\ndef _h_%s(x, y):\n"
        "    steps = 0\n"
        "    while y != 0 and steps < %d:\n"
        "        x, y = %s, %s\n"
        "        steps = steps + 1\n"
        "    return x\n"
        "def _disc_%s(p):\n"
        "    nums = [int(v) for v in re.findall(r\"-?\\d+\", p)]\n"
        "    h = _h_%s\n"
        "    return str(%s)\n"
        "DISCOVERED[\"%s\"] = _disc_%s\n"
        % (family, LOOP_BOUND, e1, e2, family, family, answer, family, family))


def shortcut_solver_source() -> str:
    """The v1 numtheory fossil: a*b + 1, preserved for tribunal fixtures."""
    return _discovered_solver_source(
        "numtheory", "((nums[0] * nums[1]) + (nums[0] // nums[0]))")


# ---------------------------------------------------------------- surrogate battery
# SLICE 2C: descriptive C6 is RETIRED. Presence, invocation, looping, AST depth
# and helper count are telemetry only. A structural component is credited as
# LOAD-BEARING only if no substantially simpler causal surrogate preserves the
# claimed capability: constant outputs, identity/passthrough, trivial
# expressions, simplified control flow, and removal/bypass.
def trivial_surrogates() -> List[tuple]:
    """(name, body) pairs for a helper of signature h(x, y). 'Trivial' means
    size <= 1 in the declared grammar: a terminal or a single primitive
    application, plus constants and passthrough."""
    out = [("const_0", "0"), ("const_1", "1"),
           ("identity_x", "x"), ("identity_y", "y")]
    for name, (_fn, tmpl) in sorted(PRIMITIVES.items()):
        for a in ("x", "y"):
            for b in ("x", "y"):
                out.append(("expr_%s(%s,%s)" % (name, a, b), tmpl.format(a, b)))
    return out


def _replace_helper(artifact: "Artifact", family: str, body: str) -> "Artifact":
    """Rebuild the artifact with the helper's computation replaced."""
    src = artifact.modules()["search"]
    pat = re.compile(r"def _h_%s\(x, y\):.*?\n    return x\n" % re.escape(family), re.S)
    new = "def _h_%s(x, y):\n    return %s\n" % (family, body)
    if not pat.search(src):
        return artifact
    return Artifact.from_modules(dict(artifact.modules(), search=pat.sub(new, src)),
                                 generation=artifact.generation)


def _single_iteration(artifact: "Artifact", family: str) -> "Artifact":
    """Simplified control flow: the loop runs at most once."""
    src = artifact.modules()["search"]
    new = src.replace("while y != 0 and steps < %d:" % LOOP_BOUND,
                      "while y != 0 and steps < 1:")
    return Artifact.from_modules(dict(artifact.modules(), search=new),
                                 generation=artifact.generation)


def surrogate_battery(artifact: "Artifact", family: str, instances: List[Dict]) -> Dict:
    """Run the intervention battery. Returns the verdict and every surrogate
    that preserved the capability."""
    def acc(art):
        r = Recipient.fresh(seed=31337)
        r.load(art)
        return r.run_tasks(instances, Escrow(10 ** 7))["accuracy"]

    original = acc(artifact)
    survivors = []
    for name, body in trivial_surrogates():
        s = _replace_helper(artifact, family, body)
        if s.sha256 == artifact.sha256:
            continue
        a = acc(s)
        if a >= original - 1e-9:
            survivors.append({"surrogate": name, "accuracy": a})
    s1 = _single_iteration(artifact, family)
    if s1.sha256 != artifact.sha256:
        a = acc(s1)
        if a >= original - 1e-9:
            survivors.append({"surrogate": "single_iteration", "accuracy": a})
    return {
        "original_accuracy": original,
        "surrogates_that_preserved_capability": survivors,
        "load_bearing": len(survivors) == 0 and original > 0.0,
    }


def structural_telemetry(artifact: "Artifact") -> Dict:
    """Telemetry ONLY -- never a criterion (slice 2C ruling)."""
    src = artifact.modules().get("search", "")
    helpers = re.findall(r"def (_h_\w+)\(x, y\):", src)
    return {"helper_count": len(helpers),
            "helpers": helpers,
            "contains_loop": "while " in src,
            "invoked": bool(re.search(r"h\(nums\[0\], nums\[1\]\)", src))}


def structural_change(artifact: "Artifact") -> bool:
    """C6: a helper with bounded control flow that the answer path calls.

    A single-expression dispatch does not qualify however accurate it is.
    """
    src = artifact.modules().get("search", "")
    for m in re.finditer(r"def (_h_\w+)\(x, y\):(.*?)\n(?=def |DISCOVERED|\Z)", src, re.S):
        name, body = m.group(1), m.group(2)
        if "while " not in body:
            continue
        fam = name[len("_h_"):]
        caller = re.search(r"def _disc_%s\(p\):(.*?)\nDISCOVERED" % re.escape(fam), src, re.S)
        if caller and ("h(" in caller.group(1) or name + "(" in caller.group(1)):
            return True
    return False


def _helper_values(e1: str, e2: str, pairs: List[tuple]) -> Optional[tuple]:
    """Execute the bounded loop directly (not via exec) during the search."""
    out = []
    for a, b in pairs:
        x, y, steps = a, b, 0
        try:
            while y != 0 and steps < LOOP_BOUND:
                x, y = (eval(e1, {"__builtins__": {}, "x": x, "y": y, "math": math}),
                        eval(e2, {"__builtins__": {}, "x": x, "y": y, "math": math}))
                steps += 1
                if abs(x) > VALUE_CEILING or abs(y) > VALUE_CEILING:
                    return None
        except Exception:      # noqa: BLE001 -- a bad helper is simply not a helper
            return None
        out.append(x)
    return tuple(out)


def _structural_search(examples: List[Dict], escrow: Escrow, cap: int,
                       rng: random.Random) -> Optional[tuple]:
    """Search helper(E1, E2) + an answer expression that uses it.

    Returns (e1, e2, answer_source) or None. Ordering is randomised from the
    lineage's search entropy: a permitted stochastic search decision, so
    different lineages examine different helpers first under the same budget.
    """
    vectors, golds = [], []
    for t in examples:
        nums = [int(v) for v in re.findall(r"-?\d+", t["prompt"])]
        if len(nums) < TERMINALS:
            return None
        vectors.append(nums)
        golds.append(t["gold"])
    pairs = [(v[0], v[1]) for v in vectors]

    # candidate update expressions over {x, y}, depth <= 2
    atoms = ["x", "y"]
    exprs = list(atoms)
    for _n, (_fn, tmpl) in PRIMITIVES.items():
        for a in atoms:
            for b in atoms:
                exprs.append(tmpl.format(a, b))
    rng.shuffle(exprs)

    helpers, seen_vec = [], set()
    for e1 in exprs:
        for e2 in exprs:
            if len(helpers) >= HELPER_CANDIDATE_CAP:
                break
            vals = _helper_values(e1, e2, pairs)
            if vals is None or vals in seen_vec:
                continue
            if all(v == vals[0] for v in vals):          # constant: computes nothing
                continue
            if any(vals == tuple(v[i] for v in vectors) for i in range(TERMINALS)):
                continue                                  # identical to an input
            seen_vec.add(vals)
            helpers.append((e1, e2, vals))
        if len(helpers) >= HELPER_CANDIDATE_CAP:
            break

    spent = 0
    for e1, e2, hvals in helpers:
        if spent >= cap or escrow.remaining() <= 0:
            return None
        sub = min(PER_HELPER_CANDIDATE_CAP, cap - spent)
        got = _compose_v2(vectors, golds, escrow, sub,
                          extra=[("h(nums[0], nums[1])", hvals)], rng=rng)
        spent += sub
        if got is not None and "h(" in got[0]:
            return e1, e2, got[0]
    return None


def _discovered_solver_source(family: str, expr: str) -> str:
    return (
        "\ndef _disc_%s(p):\n"
        "    nums = [int(x) for x in re.findall(r\"-?\\d+\", p)]\n"
        "    return str(%s)\n"
        "DISCOVERED[\"%s\"] = _disc_%s\n" % (family, expr, family, family))


# ---------------------------------------------------------------- hostile tribunal
def _counterexamples(cls: str, n: int) -> List[Dict]:
    """Regions where a KNOWN shortcut fails. AMENDMENT 3 section 4."""
    out = []
    for i in range(n):
        rng = random.Random(tribunal_entropy(cls, 10_000 + i))
        if cls == "numtheory":
            mode = i % 4
            if mode == 0:                                   # shared prime factor
                k = rng.choice([2, 3, 5, 7, 11, 13])
                a, b = k * rng.randint(2, 60), k * rng.randint(2, 60)
            elif mode == 1:                                 # one divides the other
                a = rng.randint(2, 60)
                b = a * rng.randint(2, 12)
            elif mode == 2:                                 # equal numbers
                a = b = rng.randint(2, 500)
            else:                                           # common multiple
                k = rng.randint(2, 20)
                a, b = k * rng.randint(2, 30), k * rng.randint(2, 30)
            g = math.gcd(a, b)
            out.append({"family": cls, "prompt": "Give gcd(%d, %d) + lcm(%d, %d)." % (a, b, a, b),
                        "gold": str(g + a * b // g), "key": "ce-%s-%d" % (cls, i)})
        else:
            mode = i % 4
            if mode == 0:
                a, b, m = rng.randint(2, 99), rng.randint(2, 12), 1
            elif mode == 1:
                m = rng.randint(2, 50)
                a, b = m * rng.randint(1, 20), rng.randint(2, 12)
            elif mode == 2:
                m = rng.randint(2, 500)
                a, b = m, rng.randint(2, 12)
            else:
                m = rng.randint(2, 40)
                a, b = rng.randint(m + 1, m + 500), rng.randint(2, 6)
            out.append({"family": cls, "prompt": "Give (%d ** %d) mod %d." % (a, b, m),
                        "gold": str(pow(a, b) % m), "key": "ce-%s-%d" % (cls, i)})
    return out


class Tribunal:
    """Independently seeded, constructed ONLY after a generation-8 freeze.

    No tribunal information flows back to the lineage that produced the
    artifact: there is no repair loop, and a failing artifact is recorded as
    failing.
    """

    def __init__(self, frozen_hash: str):
        self.frozen_hash = frozen_hash

    @classmethod
    def after_freeze(cls, artifact: Optional["Artifact"]) -> "Tribunal":
        if artifact is None:
            raise BoundaryViolation("tribunal requested before any artifact was frozen")
        if artifact.generation != FROZEN_GENERATION:
            raise ValueError("tribunal requires the frozen generation %d, got %s"
                             % (FROZEN_GENERATION, artifact.generation))
        return cls(artifact.sha256)

    def _instances(self, cls_: str, n: int) -> List[Dict]:
        out = []
        for i in range(n):
            rng = random.Random(tribunal_entropy(cls_, i))
            p, g = _task(cls_, rng)
            out.append({"family": cls_, "prompt": p, "gold": g, "key": "tb-%s-%d" % (cls_, i)})
        return out

    def _metamorphic(self, artifact: "Artifact", cls_: str, n: int = 40) -> bool:
        """Oracle-free consistency. A shortcut that happens to fit instances
        still has to obey the relation the capability itself obeys."""
        r = Recipient.fresh(seed=4242)
        r.load(artifact)
        for i in range(n):
            rng = random.Random(tribunal_entropy(cls_, 20_000 + i))
            if cls_ == "numtheory":
                a, b, k = rng.randint(2, 400), rng.randint(2, 400), rng.randint(2, 9)
                f = lambda x, y: r.answer("Give gcd(%d, %d) + lcm(%d, %d)." % (x, y, x, y), cls_)
                base, swapped, scaled = f(a, b), f(b, a), f(k * a, k * b)
                if base is None or swapped is None or scaled is None:
                    return False
                try:
                    if base != swapped or int(scaled) != k * int(base):
                        return False
                except (TypeError, ValueError):
                    return False
            else:
                m = rng.randint(2, 200)
                a, b = rng.randint(m + 1, m + 900), rng.randint(3, 10)
                g = lambda x, y, mm: r.answer("Give (%d ** %d) mod %d." % (x, y, mm), cls_)
                full, reduced, prev = g(a, b, m), g(a % m, b, m), g(a, b - 1, m)
                if full is None or reduced is None or prev is None:
                    return False
                try:
                    if full != reduced or int(full) != (int(prev) * a) % m:
                        return False
                except (TypeError, ValueError):
                    return False
        return True

    def score(self, artifact: "Artifact", cls_: str, n: int = 200) -> Dict:
        held = self._instances(cls_, n)
        ce = _counterexamples(cls_, n // 2)
        r1 = Recipient.fresh(seed=4242)
        r1.load(artifact)
        r2 = Recipient.fresh(seed=4242)
        r2.load(artifact)
        return {
            "held_out_accuracy": r1.run_tasks(held, Escrow(10 ** 7))["accuracy"],
            "counterexample_accuracy": r2.run_tasks(ce, Escrow(10 ** 7))["accuracy"],
            "metamorphic_pass": self._metamorphic(artifact, cls_),
        }


def memorised_state(seen: List[Dict]) -> Dict[str, str]:
    """Donor STATE: answers to the instances it saw. Useless on fresh instances."""
    return {t["key"]: t["gold"] for t in seen}


# ---------------------------------------------------------------- module loading (sandbox)
SAFE_BUILTINS = {"len": len, "range": range, "sorted": sorted, "sum": sum, "min": min, "max": max,
                 "int": int, "str": str, "isinstance": isinstance, "enumerate": enumerate,
                 "list": list, "dict": dict, "map": map, "zip": zip, "abs": abs, "any": any, "all": all,
                 "reversed": reversed, "tuple": tuple, "set": set, "float": float, "bool": bool,
                 "divmod": divmod, "round": round, "filter": filter, "pow": pow}


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

    def answer(self, prompt: str, family: str) -> Optional[str]:
        """Raw answer, used by the tribunal's oracle-free metamorphic checks."""
        if not self._loaded:
            raise RuntimeError("recipient has no modules loaded")
        fn = self._ns["search"]["solvers"]().get(family)
        if fn is None:
            return None
        try:
            return fn(prompt)
        except Exception:          # noqa: BLE001 -- an evolved solver may simply be wrong
            return None

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
    lineage_id: Optional[str] = None   # preregistered; drives independent entropy
    generation: int = 0
    modules: Dict[str, str] = field(default_factory=dict)
    state: _State = field(default_factory=_State)
    history: List[Dict] = field(default_factory=list)
    _structural_attempts: int = 0

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

    def _synthesis_variant(self, dev: List[Dict], escrow: Escrow, reserve: int) -> Optional[Dict[str, str]]:
        """Attempt endogenous discovery for the first class this lineage fails.

        Spends only what is left above `reserve`, so an improver on a small
        escrow simply cannot afford to search -- it never gets to raise its
        own budget, and never starves the dev evaluations it still owes.
        """
        probe = Recipient(self.seed)
        probe.load(Artifact.from_modules(dict(self.modules)))
        for fam in HEADROOM_FAMILIES:
            examples = [t for t in dev if t["family"] == fam]
            if not examples:
                continue
            if probe.run_tasks(examples, Escrow(len(examples) + 1))["accuracy"] == 1.0:
                continue                      # already solved; nothing to discover
            cap = min(MAX_SYNTH_CANDIDATES, max(0, escrow.remaining() - reserve))
            if cap <= 0:
                return None
            rng = self._search_rng()
            # Which mode is attempted first is a stochastic search decision
            # driven by the lineage's own search entropy (AMENDMENT 3 s1), so
            # independent lineages explore the space in different orders.
            modes = ["compose", "structural"]
            if rng.random() < 0.5:
                modes.reverse()
            for mode in modes:
                # Recomputed per mode: a failed search must not let the next
                # mode respend a budget that is already gone.
                cap = min(MAX_SYNTH_CANDIDATES, max(0, escrow.remaining() - reserve))
                if cap <= 0:
                    return None
                if mode == "compose":
                    expr = _synthesise(examples, escrow, cap, rng=rng)
                    if expr is not None:
                        v = dict(self.modules)
                        v["search"] = v["search"] + _discovered_solver_source(fam, expr)
                        return v
                elif self._structural_attempts < STRUCTURAL_ATTEMPTS_PER_LINEAGE:
                    self._structural_attempts += 1
                    # `cap` is already reserve-aware: the structural search may
                    # never spend the budget the dev evaluations still owe.
                    got = _structural_search(examples, escrow, cap, rng)
                    if got is not None:
                        e1, e2, ans = got
                        v = dict(self.modules)
                        v["search"] = v["search"] + helper_solver_source(fam, e1, e2, ans)
                        return v
        return None

    def _search_rng(self) -> random.Random:
        if self.lineage_id is not None:
            return random.Random(search_entropy(self.lineage_id) + self.generation)
        return random.Random(self.seed + self.generation)

    def evolve(self, generations: int, escrow: Escrow, dev_seed: int = 7) -> None:
        rng = random.Random(self.seed)
        for _ in range(generations):
            # RULING 1: an independently launched lineage draws its development
            # instances from its own preregistered entropy, so lineages are
            # independent experimental units rather than replays of one
            # trajectory. Lineages without an id keep the v1 behaviour.
            gen_seed = (dev_entropy(self.lineage_id, self.generation)
                        if self.lineage_id is not None else dev_seed + self.generation)
            dev = []
            for fam in DEV_FAMILIES:
                dev += tasks(family=fam, n=DEV_PER_FAMILY, seed=gen_seed)
            best, best_score = None, -1.0
            variants = self._variants(rng)
            reserve = (len(variants) + 1) * len(dev) * max(1, generations - self.generation)
            synth = self._synthesis_variant(dev, escrow, reserve)
            if synth is not None:
                variants.append(synth)
            for cand in variants:
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
            # `dev` is kept for audit only: history is donor state and never
            # crosses the boundary -- only the five module sources do.
            self.history.append({"generation": self.generation,
                                 "score": best_score / max(len(dev), 1),
                                 "dev": dev})

    def extract(self, generation: int) -> Artifact:
        if generation != self.generation:
            raise ValueError(f"extraction point is positional: only generation {self.generation} may be taken")
        return Artifact.from_modules(self.modules, generation=generation)
