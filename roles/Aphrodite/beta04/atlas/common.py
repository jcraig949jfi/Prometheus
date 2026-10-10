"""ATLAS common layer: contract task JSON, target-free probe inputs, tribunal, qualifier, credit channels.

Information boundary (the archive-target-blindness contract of this package)
---------------------------------------------------------------------------
A task is split into two views:
  LearnerView  -- what search and archives may see: family_id, output_type, dev examples, the dev INPUTS, and the
                  target-free probe inputs derived from the dev inputs only. No test examples, no witness, no tribunal.
  Certifier    -- test examples, the witness (if any) and tribunal inputs. Used ONLY to decide whether a dev-consistent
                  candidate is QUALIFIED (and for final evaluation). Its answer can stop a search; it never feeds an
                  archive decision (tested by the perturbation test in tests/run_tests.py).

Definitions
-----------
  QUALIFIED(p)  := p correct on ALL test examples AND (if a witness exists) p agrees with the witness, value-or-FAIL,
                   on every tribunal input (OPEN DECISION O3: FAIL agreement required).
  exact credit  := number of dev examples on which p's output equals the target (type-exact; FAIL = wrong).
  partial credit:= mean over dev examples of a per-example score in [0,1]: Int/Bool -> 1 if exact else 0;
                   List -> (#positions i < min(len) with out[i] == t[i]) / max(len(out), len(t)) (1 if both empty);
                   FAIL or wrong type -> 0.
  magnitude credit (DIAGNOSTIC ONLY, never used by a search here): mean of 1 / (1 + log2(1 + |err|)) per Int output
                   or per List position (length mismatch positions score 0); Bool exact; FAIL 0.
"""
import hashlib
import json
import math
import random
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from tfs1 import core as C

ATLAS_VERSION = "atlas-v0"

# Target-blind generic start programs per output type (identical for every task of that type).
STARTS = {"Int": ["0", "(len xs)", "(sum xs)"], "List": ["xs"], "Bool": ["(lt 0 (len xs))"]}


def h64(s: str) -> int:
    return int.from_bytes(hashlib.blake2b(s.encode(), digest_size=8).digest(), "big")


def sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def rng(*parts) -> random.Random:
    return random.Random(h64("ATLAS/v0/" + "/".join(str(p) for p in parts)))


# ================================================================ task
def load_task(obj_or_path) -> Dict:
    """Contract task JSON (dict or path). Validates the fields the atlas needs; witness is optional."""
    if not isinstance(obj_or_path, dict):
        obj_or_path = json.loads(Path(obj_or_path).read_text())
    t = dict(obj_or_path)
    for k in ("family_id", "output_type", "dev", "test"):
        if k not in t:
            raise ValueError("task missing %r" % k)
    if t["output_type"] not in C.VALUE_TYPES:
        raise ValueError("output_type %r" % t["output_type"])
    t["dev"] = [[list(i), o] for i, o in t["dev"]]
    t["test"] = [[list(i), o] for i, o in t["test"]]
    devin = {tuple(i) for i, _ in t["dev"]}
    t["_dev_test_overlap"] = sum(tuple(i) in devin for i, _ in t["test"])
    return t


class LearnerView:
    """Everything a search/archive may see. Built from dev only (inputs AND outputs); never test/witness."""

    def __init__(self, task: Dict, n_probes: int = 8):
        self.family_id = task["family_id"]
        self.output_type = task["output_type"]
        self.dev = [(list(i), o) for i, o in task["dev"]]
        self.dev_inputs = [i for i, _ in self.dev]
        self.targets = [o for _, o in self.dev]
        self.probes = probe_inputs(self.dev_inputs, self.family_id, n_probes)

    def fingerprint(self) -> str:
        return sha({"f": self.family_id, "T": self.output_type, "dev": self.dev, "probes": self.probes})


def probe_inputs(dev_inputs: Sequence[List[int]], family_id: str, k: int = 8) -> List[List[int]]:
    """Target-free probe inputs: derived from the dev INPUT statistics only (length range, value range) with a fixed
    keyed RNG; two fixed edge probes ([] is excluded on purpose: it FAILs too many programs to be informative)."""
    lens = [len(i) for i in dev_inputs] or [3]
    vals = [v for i in dev_inputs for v in i] or [0, 1]
    lo, hi = min(vals), max(vals)
    lmin, lmax = max(1, min(lens)), max(1, max(lens))
    r = rng("PROBE", family_id)
    out = [[lo], [hi, lo, hi]]
    while len(out) < k:
        out.append([r.randint(lo, hi) for _ in range(r.randint(lmin, lmax))])
    return out[:k]


def tribunal_inputs(task: Dict, salt: str = "T0", n_random: int = 24) -> List[List[int]]:
    """Adversarial extra inputs: empty, length 1, extremes, max length 16, random lists over a widened range.
    Derived from dev+test input statistics (the certifier may see test)."""
    allin = [i for i, _ in task["dev"]] + [i for i, _ in task["test"]]
    vals = [v for i in allin for v in i] or [0, 1]
    lo, hi = min(vals), max(vals)
    wlo, whi = 2 * lo - 2 if lo < 0 else -2, 2 * hi + 2
    r = rng("TRIBUNAL", task["family_id"], salt)
    out = [[], [0], [1], [-1], [lo], [hi], [hi] * 16, [lo] * 16, list(range(lo, min(hi, lo + 15) + 1))[:16]]
    for _ in range(n_random):
        out.append([r.randint(wlo, whi) for _ in range(r.randint(0, 16))])
    return out


# ================================================================ evaluation
def compile_p(t, lib=None):
    return C.compile_term(t, lib, None, swap=lib is not None)


def outs_of(t, inputs, lib=None, fn=None) -> list:
    """Outputs (value or FAIL) of term t on inputs. Saves/restores the global unit counters (C.U)."""
    u = (C.U[0], C.U[1])
    fn = fn or compile_p(t, lib)
    r = [C.run(fn, list(i)) for i in inputs]
    C.U[0], C.U[1] = u
    return r


def exact_credit(outs, targets) -> int:
    return sum(1 for v, o in zip(outs, targets) if C.same_value(v, o))


def _partial_one(v, o) -> float:
    if v == C.FAIL or type(v) is not type(o):
        return 0.0
    if isinstance(o, list):
        if not o and not v:
            return 1.0
        m = sum(1 for a, b in zip(v, o) if a == b and type(a) is type(b))
        return m / max(len(v), len(o))
    return 1.0 if v == o else 0.0


def partial_credit(outs, targets) -> float:
    return sum(_partial_one(v, o) for v, o in zip(outs, targets)) / max(1, len(targets))


def _mag(a, b) -> float:
    return 1.0 / (1.0 + math.log2(1 + abs(a - b)))


def _mag_one(v, o) -> float:
    if v == C.FAIL or type(v) is not type(o):
        return 0.0
    if isinstance(o, list):
        if not o and not v:
            return 1.0
        return sum(_mag(a, b) for a, b in zip(v, o)) / max(len(v), len(o))
    if isinstance(o, bool):
        return 1.0 if v == o else 0.0
    return _mag(v, o)


def magnitude_credit(outs, targets) -> float:
    return sum(_mag_one(v, o) for v, o in zip(outs, targets)) / max(1, len(targets))


CREDITS = {"exact": lambda o, t: exact_credit(o, t) / max(1, len(t)), "partial": partial_credit,
           "magnitude": magnitude_credit}


# ================================================================ certifier
class Certifier:
    """Test + tribunal qualifier. The ONLY holder of test outputs, witness and tribunal (target side)."""

    def __init__(self, task: Dict, lib=None, witness: Optional[str] = None, salt: str = "T0"):
        self.task = task
        self.lib = lib
        self.test = [(list(i), o) for i, o in task["test"]]
        w = witness if witness is not None else task.get("witness")
        self.witness = C.parse(w) if isinstance(w, str) else w
        self.tribunal = tribunal_inputs(task, salt) if self.witness is not None else []
        self.tribunal_ref = outs_of(self.witness, self.tribunal, lib) if self.witness is not None else []
        self.calls = 0

    def qualify(self, t) -> Dict:
        self.calls += 1
        fn = compile_p(t, self.lib)
        u = (C.U[0], C.U[1])
        test_ok = C.check_dev(fn, self.test)
        trib_ok = None
        if self.witness is not None:
            got = [C.run(fn, list(i)) for i in self.tribunal]
            trib_ok = all(C.same_value(a, b) for a, b in zip(got, self.tribunal_ref))
        C.U[0], C.U[1] = u
        return {"test_ok": test_ok, "tribunal_ok": trib_ok,
                "qualified": bool(test_ok and (trib_ok is None or trib_ok))}

    def verify(self, t) -> bool:
        return self.qualify(t)["qualified"]


def witness_existence(task: Dict, lib=None, witness: Optional[str] = None) -> Dict:
    """EXISTENCE: the witness parses, type-checks at the task's output type, and is correct on dev and test."""
    w = witness if witness is not None else task.get("witness")
    if w is None:
        return {"witness": None, "exists": None, "reason": "no witness supplied"}
    try:
        t = C.parse(w) if isinstance(w, str) else w
        ty = C.type_of(t, 0, None, lib)
    except Exception as e:                       # noqa: BLE001
        return {"witness": str(w), "exists": False, "reason": "parse/type error: %s" % e}
    if ty != task["output_type"]:
        return {"witness": C.to_str(t), "exists": False, "reason": "type %s != %s" % (ty, task["output_type"])}
    dev_o = outs_of(t, [i for i, _ in task["dev"]], lib)
    test_o = outs_of(t, [i for i, _ in task["test"]], lib)
    dev_ok = exact_credit(dev_o, [o for _, o in task["dev"]]) == len(task["dev"])
    test_ok = exact_credit(test_o, [o for _, o in task["test"]]) == len(task["test"])
    sizes = lib.static_sizes(t) if lib is not None else {"size_promoted": C.size(t), "size_expanded": C.size(t)}
    return {"witness": C.to_str(t), "exists": bool(dev_ok and test_ok), "dev_ok": dev_ok, "test_ok": test_ok,
            "type": ty, **sizes}


def final_evaluation(program: str, task: Dict, lib=None, witness: Optional[str] = None,
                     salt: str = "FINAL") -> Dict:
    """AUTONOMOUS competence: the program ALONE (no archive object exists in this call) on the test set and on a
    FRESH tribunal (different salt from the one used during search)."""
    cert = Certifier(task, lib, witness, salt=salt)
    q = cert.qualify(C.parse(program))
    return {"program": program, "autonomous_pass": q["qualified"], "test_ok": q["test_ok"],
            "fresh_tribunal_ok": q["tribunal_ok"], "tribunal_salt": salt, "archive": "OFF (not an argument)"}
