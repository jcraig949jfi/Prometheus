"""S2: fair meta-selection by common random numbers.

Frozen by AMENDMENT_13_2026-09-23.md (commit 4a6bbf55d) before this was
written.

Every ordered list the search walks is sorted by a KEY that depends only on
(cell seed, slot, item) -- never on the library, its name, its entries or the
arm. Byte-identical libraries therefore walk identical candidate sequences,
shared items keep their relative order across libraries, and permuting an
entry's lists changes nothing. Charging is unchanged: one per candidate.
"""
import hashlib
import json
import math
import statistics
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import basis_v4 as G
import engine as E

ESCROW = 250_000


def key(seed: int, slot: str, item: str) -> str:
    return hashlib.sha256(("APHRODITE/S2/ORDER/v1/%d/%s/%s" % (seed, slot, item))
                          .encode()).hexdigest()


def keyed(items: Sequence[str], seed: int, slot: str) -> List[str]:
    return sorted(dict.fromkeys(items), key=lambda it: key(seed, slot, it))


# ---------------------------------------------------------------- libraries
LEVEL1 = list(G.BODY_ATOMS) + [tmpl.format(a, b)
                               for _n, (_f, tmpl) in sorted(E.PRIMITIVES.items())
                               for a in G.BODY_ATOMS for b in G.BODY_ATOMS]
_BODY_SET = set(G.BODY_SPACE)


def expand_schema(schema: str) -> List[str]:
    """A one-hole body schema's instantiations: every LEVEL1 filler whose body
    lies inside the declared BODY_SPACE (the Tier-3C filler rule)."""
    out = []
    for f in LEVEL1:
        b = schema.replace("{H}", f)
        if b in _BODY_SET:
            out.append(b)
    return out


def entry_bodies(entry: Dict) -> List[str]:
    out = list(entry.get("bodies", []))
    for s in entry.get("schemas", []):
        out += expand_schema(s)
    return list(dict.fromkeys(out))


class KLib:
    """A proposal library (entries are DATA) walked in keyed order, followed by
    the complete G4 fallback: every library has identical expressive power."""

    def __init__(self, entries: List[Dict]):
        self.entries = entries
        self._bodies = [entry_bodies(e) for e in entries]

    def canonical(self) -> bytes:
        return json.dumps(self.entries, sort_keys=True, separators=(",", ":")).encode()

    def content(self) -> bytes:
        """Content WITHOUT names: what the search actually walks."""
        return json.dumps([{"inits": sorted(set(e.get("inits", []))), "bodies": sorted(b),
                            "finals": sorted(set(e.get("finals", [])))}
                           for e, b in zip(self.entries, self._bodies)],
                          sort_keys=True, separators=(",", ":")).encode()

    def sha256(self) -> str:
        return hashlib.sha256(self.canonical()).hexdigest()

    def size(self) -> int:
        return sum(len(e.get("inits", [])) * len(b) * len(e.get("finals", []))
                   for e, b in zip(self.entries, self._bodies))

    def desugars(self) -> Tuple[bool, List[str]]:
        bad = []
        for e, bodies in zip(self.entries, self._bodies):
            bad += [b for b in bodies if b not in _BODY_SET]
            bad += [i for i in e.get("inits", []) if i not in G.INIT_SPACE]
            bad += [f for f in e.get("finals", []) if f not in G.FINAL_SPACE]
        return (not bad), bad[:5]

    def candidates(self, seed: int):
        for e, bodies in zip(self.entries, self._bodies):
            inits = keyed(e["inits"], seed, "init")
            bl = keyed(bodies, seed, "body")
            finals = keyed(e["finals"], seed, "final")
            for i in inits:
                for b in bl:
                    for f in finals:
                        yield ("fold", i, b, f), e["name"]
        fs = keyed(G.FINAL_SPACE, seed, "g4final")
        for f in fs:
            yield ("expr", f), "g4_fallback"
        inits = keyed(G.INIT_SPACE, seed, "g4init")
        bodies = keyed(G.BODY_SPACE, seed, "g4body")
        for i in inits:
            for b in bodies:
                for f in fs:
                    yield ("fold", i, b, f), "g4_fallback"


def pristine() -> KLib:
    return KLib([{"name": "organ_fold", "inits": list(G.H1_SPACE),
                  "bodies": list(G.H2_SPACE), "finals": list(G.FINAL_SPACE)}])


# ---------------------------------------------------------------- search
def parse_examples(examples: List[Dict], nums_of: Callable) -> List[Tuple[List[int], str]]:
    return [(nums_of(t), t["gold"]) for t in examples]


def search_collect(lib: KLib, parsed, escrow: E.Escrow, cap: int, seed: int,
                   max_hits: int = 1):
    """As run_tier3c.search_collect, walking the KEYED order."""
    hits = []
    for prog, coord in lib.candidates(seed):
        if escrow.remaining() <= 0 or escrow.spent >= cap:
            break
        escrow.charge(1)
        ok = True
        for nums, gold in parsed:
            got = G.run_program(prog, nums, True)
            if got is None or str(got) != gold:
                ok = False
                break
        if ok:
            hits.append((prog, coord, escrow.spent))
            if len(hits) >= max_hits:
                break
    return hits


# ---------------------------------------------------------------- paired cells
class Cell:
    """(family, replicate). Its development set and its order seed are
    functions of the cell alone -- never of a library or an arm."""

    def __init__(self, provider, family: str, r: int, size: int, label: str = "S2-cell"):
        self.family, self.r, self.size = family, r, size
        self.examples = provider.tasks(family, size,
                                       E.dev_entropy("%s/%s" % (label, family), r))
        self.parsed = parse_examples(self.examples, provider.nums_of)
        self.seed = E.search_entropy("%s/%s/%d" % (label, family, r))

    def cost(self, lib: KLib, escrow: int = ESCROW) -> Tuple[int, Optional[Tuple]]:
        esc = E.Escrow(escrow)
        hits = search_collect(lib, self.parsed, esc, escrow, self.seed, max_hits=1)
        return (hits[0][2], hits[0][0]) if hits else (escrow, None)


def paired_summary(pristine_costs: List[int], costs: List[int]) -> Dict:
    d = [p - c for p, c in zip(pristine_costs, costs)]
    n = len(d)
    mean = statistics.mean(d)
    se = statistics.stdev(d) / math.sqrt(n) if n > 1 else float("inf")
    return {"n_cells": n, "mean_paired_saving": round(mean, 2), "se": round(se, 2),
            "lower95_one_sided": round(mean - 1.645 * se, 2),
            "mean_cost": round(statistics.mean(costs), 2)}


def select(candidates: Dict[str, KLib], pristine_name: str, cells: List[Cell]) -> Dict:
    """AMENDMENT 13 s3. Eligible: one-sided 95% lower bound of mean paired
    saving vs PRISTINE > 0. Select the eligible library with the largest mean
    saving; ties -> smaller size, then sha256. None eligible -> PRISTINE."""
    costs = {name: [c.cost(lib)[0] for c in cells] for name, lib in candidates.items()}
    base = costs[pristine_name]
    table = {}
    for name, lib in candidates.items():
        row = paired_summary(base, costs[name])
        row.update({"sha256": lib.sha256(), "size": lib.size(), "costs": costs[name],
                    "eligible": name != pristine_name and row["lower95_one_sided"] > 0})
        table[name] = row
    elig = [n for n in table if table[n]["eligible"]]
    chosen = (min(elig, key=lambda n: (-table[n]["mean_paired_saving"], table[n]["size"],
                                       table[n]["sha256"])) if elig else pristine_name)
    return {"selected": chosen, "table": table}
