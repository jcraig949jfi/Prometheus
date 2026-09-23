"""Slice 2C: lineages that can discover a fold, and a tribunal that judges at
lengths they never saw.

Frozen by AMENDMENT_6_2026-09-21.md. The membrane is UNCHANGED and reused as
qualified: engine.Artifact, engine.Recipient, engine.Escrow. Grammar v1 and
the slice-2B lineage remain untouched so the impaired 2B result stays
reproducible.
"""
import random
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import basis_v2 as B
import engine as E

DEV_FAMILIES = ("arith", "sortkey", "strops", "list_sum", "list_prod_mod")
HEADROOM = ("list_sum", "list_prod_mod")
BASE_FAMILIES = ("arith", "sortkey", "strops")
DEV_PER_FAMILY = 2
FOLD_SEARCH_CAP = 5000


def tasks(family: str, n: int, seed: int, length_range=B.SEARCH_LENGTHS) -> List[Dict]:
    if family in BASE_FAMILIES:
        return E.tasks(family=family, n=n, seed=seed)
    return B.tasks(family, n, seed, length_range=length_range)


# ---------------------------------------------------------------- the lineage
@dataclass
class Lineage2C:
    lineage_id: str
    base: Dict[str, str]
    generation: int = 0
    modules: Dict[str, str] = field(default_factory=dict)
    history: List[Dict] = field(default_factory=list)

    def __post_init__(self):
        self.modules = dict(self.base)

    def _rng(self) -> random.Random:
        return random.Random(E.search_entropy(self.lineage_id) + self.generation)

    def _solved(self, modules: Dict[str, str], dev: List[Dict], family: str) -> bool:
        ex = [t for t in dev if t["family"] == family]
        if not ex:
            return True
        r = E.Recipient(7)
        r.load(E.Artifact.from_modules(dict(modules)))
        return r.run_tasks(ex, E.Escrow(len(ex) + 2))["accuracy"] == 1.0

    def _variants(self, dev: List[Dict], escrow: E.Escrow, reserve: int) -> List[Dict[str, str]]:
        """Composition and M2-fold variants. Neither receives a witness."""
        out = []
        rng = self._rng()
        modes = ["compose", "fold"]
        if rng.random() < 0.5:
            modes.reverse()
        for fam in HEADROOM:
            if self._solved(self.modules, dev, fam):
                continue
            ex = [t for t in dev if t["family"] == fam]
            for mode in modes:
                cap = min(FOLD_SEARCH_CAP, max(0, escrow.remaining() - reserve))
                if cap <= 0:
                    return out
                if mode == "fold":
                    mech = B.search_fold(fam, ex, escrow, escrow.spent + cap)
                    if mech:
                        v = dict(self.modules)
                        v["search"] = v["search"] + mech["source"]
                        out.append(v)
                        break
                else:
                    vecs, golds = [], []
                    for t in ex:
                        nums = [int(x) for x in re.findall(r"-?\d+", t["prompt"])]
                        while len(nums) < E.TERMINALS:
                            nums.append(0)
                        vecs.append(nums[:E.TERMINALS])
                        golds.append(t["gold"])
                    got = E._compose_v2(vecs, golds, escrow, cap, rng=rng)
                    if got:
                        v = dict(self.modules)
                        v["search"] = v["search"] + E._discovered_solver_source(fam, got[0])
                        out.append(v)
                        break
        return out

    def evolve(self, generations: int, escrow: E.Escrow) -> None:
        for _ in range(generations):
            gen_seed = E.dev_entropy(self.lineage_id, self.generation)
            dev = []
            for fam in DEV_FAMILIES:
                dev += tasks(fam, DEV_PER_FAMILY, gen_seed)
            reserve = 4 * len(dev) * max(1, generations - self.generation)
            cands = [dict(self.modules)] + self._variants(dev, escrow, reserve)
            best, best_score = None, -1.0
            for cand in cands:
                r = E.Recipient(7)
                r.load(E.Artifact.from_modules(cand))
                score = 0.0
                for t in dev:
                    escrow.charge(1)
                    score += r.run_tasks([t], E.Escrow(4))["accuracy"]
                if score > best_score:
                    best, best_score = cand, score
            self.modules = best
            self.generation += 1
            self.history.append({"generation": self.generation,
                                 "score": best_score / max(len(dev), 1)})

    def extract(self, generation: int) -> E.Artifact:
        if generation != self.generation:
            raise ValueError("positional extraction only: at generation %d" % self.generation)
        return E.Artifact.from_modules(dict(self.modules), generation=generation)


# ---------------------------------------------------------------- the tribunal
def _counterexamples(cls_: str, n: int) -> List[Dict]:
    out = []
    for i in range(n):
        rng = random.Random(E.tribunal_entropy("2c-" + cls_, 10_000 + i))
        if cls_ == "list_sum":
            k = rng.choice([2, 2, 100, 150, 200])
            xs = ([rng.randint(2, 99)] * k if i % 3 == 0
                  else [rng.randint(2, 99) for _ in range(k)])
            out.append({"family": cls_, "prompt": "Add all of: " + ", ".join(map(str, xs)) + ".",
                        "gold": str(sum(xs)), "key": "ce2c-%s-%d" % (cls_, i)})
        else:
            k = rng.choice([2, 40, 120])
            xs = [rng.randint(2, 30) for _ in range(k)]
            mode = i % 4
            if mode == 0:
                m = 1
            elif mode == 1:
                import math as _m
                m = max(2, _m.prod(xs[:2]))
            elif mode == 2:
                m = 10 ** 30
            else:
                xs = [1] * (k // 2) + xs
                m = rng.randint(7, 9973)
            import math as _m
            out.append({"family": cls_,
                        "prompt": ("Multiply all of: " + ", ".join(map(str, xs))
                                   + " then give the remainder mod %d." % m),
                        "gold": str(_m.prod(xs) % m), "key": "ce2c-%s-%d" % (cls_, i)})
    return out


class Tribunal2C:
    def __init__(self, frozen_hash: str):
        self.frozen_hash = frozen_hash

    @classmethod
    def after_freeze(cls, artifact: Optional[E.Artifact]) -> "Tribunal2C":
        if artifact is None:
            raise E.BoundaryViolation("tribunal requested before any artifact was frozen")
        if artifact.generation != E.FROZEN_GENERATION:
            raise ValueError("tribunal requires the frozen generation")
        return cls(artifact.sha256)

    def _held_out(self, cls_, n, length_range):
        seed = E.tribunal_entropy("2c-" + cls_, 1)
        return B.tasks(cls_, n, seed, length_range=length_range)

    def _metamorphic(self, artifact: E.Artifact, cls_: str, n: int = 30) -> bool:
        r = E.Recipient.fresh(seed=4242)
        r.load(artifact)
        for i in range(n):
            rng = random.Random(E.tribunal_entropy("2c-" + cls_, 20_000 + i))
            xs = [rng.randint(2, 30) for _ in range(rng.randint(5, 40))]
            perm = xs[:]
            rng.shuffle(perm)
            k = rng.randint(2, 30)
            if cls_ == "list_sum":
                f = lambda ys: r.answer("Add all of: " + ", ".join(map(str, ys)) + ".", cls_)
                a, b, c = f(xs), f(perm), f(xs + [k])
                if a is None or b is None or c is None:
                    return False
                try:
                    if a != b or int(c) != int(a) + k:
                        return False
                except ValueError:
                    return False
            else:
                m = rng.randint(7, 9973)
                f = lambda ys: r.answer("Multiply all of: " + ", ".join(map(str, ys))
                                        + " then give the remainder mod %d." % m, cls_)
                a, b, c = f(xs), f(perm), f(xs + [k])
                if a is None or b is None or c is None:
                    return False
                try:
                    if a != b or int(c) != (int(a) * k) % m:
                        return False
                except ValueError:
                    return False
        return True

    def score(self, artifact: E.Artifact, cls_: str, n: int = 200) -> Dict:
        def acc(instances):
            r = E.Recipient.fresh(seed=4242)
            r.load(artifact)
            return r.run_tasks(instances, E.Escrow(10 ** 7))["accuracy"]
        return {
            "held_out_extrapolation": acc(self._held_out(cls_, n, B.EXTRAPOLATION_LENGTHS)),
            "stress_length_200": acc(self._held_out(cls_, 60, (B.STRESS_LENGTH, B.STRESS_LENGTH))),
            "counterexample_accuracy": acc(_counterexamples(cls_, 60)),
            "metamorphic_pass": self._metamorphic(artifact, cls_),
        }


# ---------------------------------------------------------------- adjudication
FOLD_RE = (r"def _fold_(\w+)\(p\):\n.*?vals = nums\[:-1\] if (True|False).*?"
           r"acc = (.*?)\n    for v in vals:\n        acc = (.*?)\n    return str\((.*?)\)\n")


def parse_folds(artifact: E.Artifact) -> Dict[str, Dict]:
    out = {}
    for fam, trailing, init, body, final in re.findall(FOLD_RE, artifact.modules()["search"], re.S):
        out[fam] = {"init": init, "body": body, "final": final,
                    "trailing": trailing == "True"}
    return out


def adjudicate_structure(artifact: E.Artifact, cls_: str, mech: Dict) -> Dict:
    """INVARIANT 1, post-freeze, no feedback to search. Surrogates are scored on
    EXTRAPOLATION-length instances, where a bounded unrolling cannot hide."""
    seed = E.tribunal_entropy("2c-" + cls_, 7)
    inst = B.tasks(cls_, 150, seed, length_range=B.EXTRAPOLATION_LENGTHS)

    def acc(src_artifact):
        r = E.Recipient.fresh(seed=31337)
        r.load(src_artifact)
        return r.run_tasks(inst, E.Escrow(10 ** 7))["accuracy"]

    original = acc(artifact)
    base_src = artifact.modules()["search"]
    survivors = []
    for name, src in B.fold_surrogates(cls_, mech):
        stripped = re.sub(FOLD_RE % () if False else
                          r"def _fold_%s\(p\):.*?DISCOVERED\[\"%s\"\] = _fold_%s\n"
                          % (cls_, cls_, cls_), "", base_src, flags=re.S)
        cand = E.Artifact.from_modules(dict(artifact.modules(), search=stripped + src),
                                       generation=artifact.generation)
        try:
            a = acc(cand)
        except Exception:      # noqa: BLE001
            continue
        if a >= original - 1e-9:
            survivors.append({"surrogate": name, "accuracy": a})
    return {"original_accuracy": original, "survivors": survivors,
            "load_bearing": len(survivors) == 0 and original > 0.0}
