"""E3 s2: the lifetime organism, 2x2 promotion x archive, and the three controls.

A LIFETIME presents the families of ONE arm world in a presentation order (opaque ids), through the ARM VIEW only
(worlds.ArmWorld: opaque id + dev examples; the output type is inferred from the dev outputs). The organism never sees
test, tribunal, witness, rung, status or family_id; nothing on the evaluator side is opened during a lifetime (tested
with worlds.AccessLog).

Per family (identical base semantics and operator in every arm):
  search  = atlas.arms.Search arm A-FRESH (restart hill-climbing): the run starts by evaluating the START POOL once
            (1 charge each), then makes bursts of R mutation steps (neutral chain: move iff not all-FAIL and exact dev
            credit >= current); every burst restores a parent drawn UNIFORMLY from the start pool. CRN: the mutation
            RNG stream is rng_for(seed, "<arm_world>/<opaque>") -- identical in every arm. Budget B charges per family
            (1 charge per evaluated program, all dev examples evaluated). The FIRST dev-consistent program ends the
            family (no certifier is consulted during the lifetime).
  start pool = the generic starts of the output type (atlas.common.STARTS) + [archive arms] the archive programs of
            that output type (refactored modulo the current library when promotion is on; size <= max_size), in
            archive insertion order.

PROMOTION (developmental machinery), after each solved family:
  candidates = (a) every closed lambda subterm of the solved program (expanded to base form): no free variable, no
               reference to xs (contract v0.1-1), body references a parameter, body size >= 2, type Int->Int /
               Int->Bool / Int->Int->Int -> body over holes h0 (h1);
               (b) the TFS-1 compressor's proposals (compress.propose, arity <= 2) over ALL solved programs so far
               (expanded), minus any that reference xs (v0.1-1).
  uses       = number of distinct solved programs containing the candidate (lambda: alpha-equal closed lambda;
               compressor: programs_using after rewriting).  Every candidate has uses >= 1.
  selection  = top K by (-uses, -body size, canonical text) [deterministic tie-break].
  library    = rebuilt deterministically from the selection after every solved family: candidates are promoted in
               (body size, text) order, each body first REFACTORED modulo the entries promoted before it, so a
               candidate that contains an earlier entry's expansion becomes an entry at depth 2. Entries are
               content-addressed, so an entry that stays selected keeps its id. Solved programs and archive programs are
               stored EXPANDED (base form), so a library change never invalidates them.
  The library entries are extra typed operators/leaves for the mutator in later families.
ARCHIVE (search infrastructure): after each family, append the solved program (if any) and the top-k_partial
  partial-credit programs of that family's search (by exact dev credit, then partial credit; not all-FAIL; partial > 0;
  not already a start; ties by size then text), expanded, with their output type. Target-blind: dev feedback only.

ARMS  (promotion, archive, order):
  P0A0 (off, off, CURRICULUM)   P1A0 (on, off, CURRICULUM)   P0A1 (off, on, CURRICULUM)   P1A1 (on, on, CURRICULUM)
  RANDOM-LIBRARY   (random, off, CURRICULUM): at every rebuild each selected candidate is replaced by a random closed
                   lambda body with the same Int parameter count, result type and body size (uniform over the TFS-1 size
                   class; keyed by the candidate, so stable over the lifetime). Non-Int parameter candidates are
                   matched on arity only (recorded as param_mismatch).
  SHUFFLED-HISTORY (on, off, SHUFFLED_ANTI_<1 + seed % 3>)
  RANDOM-ARCHIVE   (off, random, CURRICULUM): every program the archive rule would add is replaced by a uniform random
                   base program of the same output type and size (keyed).
"""
import hashlib
import json
import os
import random
import time
from collections import Counter
from typing import Dict, List, Optional, Sequence

os.environ.setdefault("OMP_NUM_THREADS", "1")

from tfs1 import core as C                      # noqa: E402
from tfs1 import compress as CP                 # noqa: E402
from tfs1.enum import Enumerator, canon_comm    # noqa: E402
from tfs1.library import Library, lambda_to_body, references_xs  # noqa: E402
from tfs1.membrane import code_hashes           # noqa: E402
from atlas import arms as AA                    # noqa: E402
from atlas import common as AK                  # noqa: E402
from atlas.sample import sample_uniform         # noqa: E402

from . import worlds as WD                      # noqa: E402

ORGANISM_VERSION = "tfs1-e3-organism-v0"
ARMS = {
    "P0A0": {"promotion": "off", "archive": "off", "order": "CURRICULUM"},
    "P1A0": {"promotion": "on", "archive": "off", "order": "CURRICULUM"},
    "P0A1": {"promotion": "off", "archive": "on", "order": "CURRICULUM"},
    "P1A1": {"promotion": "on", "archive": "on", "order": "CURRICULUM"},
    "RANDOM-LIBRARY": {"promotion": "random", "archive": "off", "order": "CURRICULUM"},
    "SHUFFLED-HISTORY": {"promotion": "on", "archive": "off", "order": "SHUFFLED_ANTI"},
    "RANDOM-ARCHIVE": {"promotion": "off", "archive": "random", "order": "CURRICULUM"},
}
DEFAULTS = {"B": 200_000, "R": 100, "K": 8, "k_partial": 3, "max_fill": 3, "max_size": 16}
LAMBDA_RET = {C.F_II: C.INT, C.F_IB: C.BOOL, C.F_III: C.INT}


def order_name(arm: str, seed: int) -> str:
    o = ARMS[arm]["order"]
    return "SHUFFLED_ANTI_%d" % (1 + seed % 3) if o == "SHUFFLED_ANTI" else o


def keyed_rng(*parts) -> random.Random:
    h = hashlib.blake2b(("TFS1/E3/v0/" + "/".join(str(p) for p in parts)).encode(), digest_size=8).digest()
    return random.Random(int.from_bytes(h, "big"))


def sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


# ================================================================ search
class LifetimeSearch(AA.Search):
    """A-FRESH with (i) stop at the first dev-consistent program (no certifier), (ii) restore-origin tracking,
    (iii) top-k partial-credit tracking. The RNG consumption is identical to A-FRESH."""

    def __init__(self, view, E, seed, budget, burst, starts, k_partial, max_fill, max_size):
        self.hit = None
        self.cur_origin = None
        self.origin_counts = Counter()
        self.k_partial = k_partial
        self.top: Dict[str, tuple] = {}
        self.start_texts = set()
        super().__init__(view, None, E, "A-FRESH", seed, budget, burst=burst, starts=starts,
                         max_fill=max_fill, max_size=max_size)
        self.start_texts = {s["text"] for s in self.starts}
        for s in self.starts:
            self.top.pop(s["text"], None)

    def _restore(self):
        self.restores += 1
        self.burst_idx += 1
        self.burst_left = self.L
        i = self.rng.randrange(len(self.starts))
        s = self.starts[i]
        self.cur = (s["term"], s["key"])
        self.anchor = None
        self.cur_origin = i
        self.origin_counts[i] += 1

    def _post_eval(self, t, rec, anchor_entry):
        if rec["score"] == self.n_dev:
            if self.hit is None:
                # during __init__ the start being evaluated was just appended to self.starts
                origin = self.cur_origin if self.burst_idx >= 0 else len(self.starts) - 1
                self.hit = {"charge": self.charges, "program": rec["text"], "origin_start": origin}
                self.done = True
            return
        if rec["allfail"] or rec["partial"] <= 0 or rec["text"] in self.start_texts:
            return
        key = (-rec["score"], -rec["partial"], C.size(t), rec["text"])
        if rec["text"] in self.top:
            return
        self.top[rec["text"]] = key
        if len(self.top) > 4 * self.k_partial + 8:
            keep = sorted(self.top.items(), key=lambda kv: kv[1])[:self.k_partial]
            self.top = dict(keep)

    def top_partial(self) -> List[str]:
        return [t for t, _k in sorted(self.top.items(), key=lambda kv: kv[1])[:self.k_partial]]


# ================================================================ promotion machinery
def closed_lambda_candidates(t) -> List[Dict]:
    out = []

    def go(u):
        if u[0] == "lam":
            if not C.free_var_min_escape(u) and not references_xs(u) and C.refs_range(u[2], 0, u[1]) \
                    and C.size(u[2]) >= 2:
                try:
                    ty = C.type_of(u)
                except C.TypeErr:
                    ty = None
                if ty in LAMBDA_RET:
                    body, k = lambda_to_body(u)
                    out.append({"kind": "lambda", "body": body, "params": [C.INT] * k, "ret": LAMBDA_RET[ty],
                                "lambda_text": C.to_str(canon_comm(u))})
        for c in C.children(u):
            go(c)
    go(t)
    return out


def lambda_texts(t) -> set:
    return {c["lambda_text"] for c in closed_lambda_candidates(t)}


class Developmental:
    """Candidate store + deterministic library rebuild. mode: 'on' | 'random'."""

    def __init__(self, mode: str, K: int, seed: int):
        self.mode, self.K, self.seed = mode, K, seed
        self.corpus: List[tuple] = []             # expanded solved programs
        self.cands: Dict[str, Dict] = {}
        self.cost = {"compressor_calls": 0, "compressor_pairs": 0, "compressor_cpu_s": 0.0, "rebuilds": 0,
                     "promotion_attempts": 0, "entries_promoted_new": 0, "rebuild_cpu_s": 0.0}
        self.base_E = None
        self.seen_ids = set()

    def _pairs(self) -> int:
        heads = Counter()
        for p in self.corpus:
            for o, _d in CP.occurrences(p):
                heads[o[0]] += 1
        return sum(n * (n - 1) // 2 for n in heads.values())

    def update(self, program_expanded) -> None:
        self.corpus.append(program_expanded)
        for c in closed_lambda_candidates(program_expanded):
            key = "lam:" + C.to_str(c["body"])
            self.cands.setdefault(key, c)
        t0 = time.process_time()
        self.cost["compressor_calls"] += 1
        self.cost["compressor_pairs"] += self._pairs()
        props = CP.propose(self.corpus, Library(), max_candidates=50, refactor_first=False, min_uses=2)
        self.cost["compressor_cpu_s"] += time.process_time() - t0
        for p in props:
            if references_xs(p["body_t"]) or len(p["params"]) > 2:
                continue
            key = "cmp:" + p["body"]
            c = {"kind": "compress", "body": p["body_t"], "params": p["params"], "ret": p["ret"],
                 "gain": p["gain"]}
            self.cands[key] = c                   # refresh (gain changes with the corpus)

    def _uses(self, key, c, lam_sets) -> int:
        if c["kind"] == "lambda":
            return sum(1 for s in lam_sets if c["lambda_text"] in s)
        n = 0
        k = C.max_hole(c["body"]) + 1
        for p in self.corpus:
            cnt = [0]
            CP.rewrite(p, c["body"], "L_CAND", k, cnt)
            n += cnt[0] > 0
        return n

    def selection(self) -> List[Dict]:
        lam_sets = [lambda_texts(p) for p in self.corpus]
        rows = []
        for key in sorted(self.cands):
            c = self.cands[key]
            u = self._uses(key, c, lam_sets)
            if u >= 1:
                rows.append((-u, -C.size(c["body"]), key, c, u))
        rows.sort(key=lambda r: (r[0], r[1], r[2]))
        return [dict(r[3], key=r[2], uses=r[4]) for r in rows[:self.K]]

    def _sham_body(self, c) -> Dict:
        if self.base_E is None:
            self.base_E = Enumerator(None)
        k = len(c["params"])
        int_params = all(p == C.INT for p in c["params"])
        ctx = {0: (), 1: ("x",), 2: ("a", "b")}[k]
        ret = c["ret"] if c["ret"] in (C.INT, C.BOOL) else C.INT
        n = C.size(c["body"])
        rng = keyed_rng(self.seed, "RANDOM-LIBRARY", c["key"])
        for _ in range(500):
            b = sample_uniform(self.base_E, ret, ctx, n, rng)
            if b is None:
                n -= 1
                continue
            if references_xs(b) or (k and not C.refs_range(b, 0, k)):
                continue
            body, _k = lambda_to_body(("lam", k, b)) if k else (b, 0)
            return {"body": body, "params": [C.INT] * k, "ret": ret,
                    "param_mismatch": not int_params or ret != c["ret"]}
        return None

    def rebuild(self) -> Library:
        t0 = time.process_time()
        self.cost["rebuilds"] += 1
        sel = self.selection()
        lib = Library(closed_args=True)
        if self.mode == "random":
            items = []
            for c in sel:
                s = self._sham_body(c)
                if s is not None:
                    items.append(dict(s, key=c["key"], uses=c["uses"]))
            sel = items
        for c in sorted(sel, key=lambda c: (C.size(c["body"]), C.to_str(c["body"]))):
            self.cost["promotion_attempts"] += 1
            body = CP.refactor(c["body"], lib) if self.mode == "on" else c["body"]
            try:
                e, st = lib.promote_body(body, c["params"], {"candidate": c["key"], "uses": c["uses"],
                                                             "mode": self.mode})
            except (ValueError, C.TypeErr, KeyError):
                continue
            if st == "new" and e.id not in self.seen_ids:
                self.seen_ids.add(e.id)
                self.cost["entries_promoted_new"] += 1
        self.cost["rebuild_cpu_s"] += time.process_time() - t0
        return lib


# ================================================================ lifetime
class Organism:
    def __init__(self, arm_world: WD.ArmWorld, order: Sequence[str], arm: str, seed: int, **cfg):
        self.W, self.order, self.arm, self.seed = arm_world, list(order), arm, seed
        self.spec = ARMS[arm]
        self.cfg = dict(DEFAULTS, **cfg)
        self.dev = Developmental(self.spec["promotion"], self.cfg["K"], seed) \
            if self.spec["promotion"] != "off" else None
        self.lib = Library(closed_args=True)
        self.lib_snapshots: Dict[str, Dict] = {}
        self.archive: List[Dict] = []
        self.base_E = None
        self._E_cache: Dict[str, Enumerator] = {}
        self.ledger = Counter()

    def _E(self) -> Enumerator:
        key = self.lib.sha256()
        E = self._E_cache.get(key)
        if E is None:
            self._E_cache.clear()                 # one live enumerator (memory)
            E = self._E_cache[key] = Enumerator(self.lib if len(self.lib) else None)
        return E

    def _archive_starts(self, T) -> List[str]:
        out, seen = [], set()
        for a in self.archive:
            if a["T"] != T:
                continue
            t = C.parse(a["text"])
            if len(self.lib) and self.spec["promotion"] == "on":
                t = CP.refactor(t, self.lib)
            if C.size(t) > self.cfg["max_size"]:
                continue
            s = C.to_str(t)
            if s not in seen:
                seen.add(s)
                out.append(s)
        return out

    def _add_archive(self, slot, T, texts_expanded: List[str], kinds: List[str]):
        for i, (s, kd) in enumerate(zip(texts_expanded, kinds)):
            if self.spec["archive"] == "random":
                if self.base_E is None:
                    self.base_E = Enumerator(None)
                n = C.size(C.parse(s))
                rng = keyed_rng(self.seed, "RANDOM-ARCHIVE", slot, i)
                r = None
                while r is None and n >= 1:
                    r = sample_uniform(self.base_E, T, (), n, rng)
                    n -= 1
                s = C.to_str(r)
                kd = "random"
            self.archive.append({"text": s, "T": T, "kind": kd, "family": slot, "size": C.size(C.parse(s))})
            self.ledger["archive_admissions"] += 1

    def run_family(self, opaque: str) -> Dict:
        fam = self.W.family(opaque)
        T = fam["output_type"]
        view = AK.LearnerView({"family_id": fam["slot"], "output_type": T, "dev": fam["dev"]})
        generic = list(AK.STARTS[T])
        arch = self._archive_starts(T) if self.spec["archive"] != "off" else []
        arch = [a for a in arch if a not in generic]
        starts = generic + arch
        E = self._E()
        libsha = self.lib.sha256()
        if len(self.lib):
            self.lib_snapshots.setdefault(libsha, self.lib.to_json())
        t0 = time.process_time()
        s = LifetimeSearch(view, E, self.seed, self.cfg["B"], self.cfg["R"], starts, self.cfg["k_partial"],
                           self.cfg["max_fill"], self.cfg["max_size"])
        s.run()
        cpu = time.process_time() - t0
        hit = s.hit
        origin = None
        if hit is not None:
            o = hit["origin_start"]
            origin = "generic" if o < len(generic) else "archive"
        from_archive_restores = sum(c for i, c in s.origin_counts.items() if i >= len(generic))
        rec = {"opaque": opaque, "slot": fam["slot"], "T": T, "solved": hit is not None,
               "hit_charge": hit["charge"] if hit else None, "program": hit["program"] if hit else None,
               "origin": origin, "origin_start_text": starts[hit["origin_start"]] if hit else None,
               "charges": s.charges, "budget": self.cfg["B"], "n_starts": len(starts),
               "n_archive_starts": len(arch), "archive_starts": arch, "restores": s.restores,
               "restores_from_archive": from_archive_restores, "rejected": s.rejected,
               "units_expanded": s.units_dev[0], "units_promoted": s.units_dev[1],
               "library_sha256": libsha if len(self.lib) else None, "library_ids": self.lib.ids(),
               "uses_library": bool(hit and C.has_call(C.parse(hit["program"]))),
               "cpu_s": round(cpu, 3)}
        for k in ("charges", "units_expanded", "units_promoted", "restores", "restores_from_archive", "rejected"):
            self.ledger[k] += rec[k]
        self.ledger["start_evaluations"] += len(starts)
        # ---- consolidation (after the family)
        top = [C.to_str(self.lib.expand(C.parse(x))) for x in s.top_partial()]
        if hit is not None:
            pe = self.lib.expand(C.parse(hit["program"]))
            rec["program_expanded"] = C.to_str(pe)
            if self.dev is not None:
                self.dev.update(pe)
                self.lib = self.dev.rebuild()
        if self.spec["archive"] != "off":
            texts = ([rec["program_expanded"]] if hit else []) + top
            kinds = (["solved"] if hit else []) + ["partial"] * len(top)
            self._add_archive(fam["slot"], T, texts, kinds)
        return rec

    def lifetime(self) -> Dict:
        t0 = time.process_time()
        fams = [self.run_family(o) for o in self.order]
        decisions = [(f["slot"], f["hit_charge"], f["program"], f["origin"], f["library_sha256"], f["charges"])
                     for f in fams]
        led = dict(self.ledger)
        if self.dev is not None:
            led.update({"promotion_" + k: (round(v, 3) if isinstance(v, float) else v)
                        for k, v in self.dev.cost.items()})
        out = {"version": ORGANISM_VERSION, "arm": self.arm, "spec": self.spec, "seed": self.seed, "config": self.cfg,
               "arm_world": self.W.arm_world, "order": self.order, "families": fams,
               "final_library": self.lib.to_json(), "final_library_sha256": self.lib.sha256(),
               "library_snapshots": self.lib_snapshots, "archive_final": self.archive,
               "ledger": led, "solved": sum(f["solved"] for f in fams), "arm_view_reads": self.W.reads,
               "decision_sha256": sha(decisions), "cpu_s": round(time.process_time() - t0, 2)}
        return out


def run_lifetime(root, world_id: str, arm: str, seed: int, n_families: Optional[int] = None, **cfg) -> Dict:
    """Coordinator-side wrapper: resolve the arm world and presentation order, then run the lifetime."""
    po = WD.presentation_order(root, world_id, order_name(arm, seed))
    order = po["order"][:n_families] if n_families else po["order"]
    W = WD.ArmWorld(root, po["arm_world"])
    rec = Organism(W, order, arm, seed, **cfg).lifetime()
    rec["world_id"] = world_id
    rec["order_name"] = po["order_name"]
    rec["code_sha256"] = e3_code_hashes()           # after the lifetime (reads code files, not data)
    return rec


def e3_code_hashes() -> Dict[str, str]:
    from pathlib import Path
    h = dict(code_hashes())
    here = Path(__file__).resolve().parent
    for p in sorted(here.glob("*.py")):
        h["e3/" + p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    return h
