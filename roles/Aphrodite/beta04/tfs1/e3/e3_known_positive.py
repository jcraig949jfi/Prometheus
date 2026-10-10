"""E3-KP: TFS1_INSTRUMENT_QUALIFIED -- the known-positive reachability chain replicated with the INDEPENDENT substrate.
Implements windows/E2_E3KP_PREREG.md s A as amended by AMENDMENT A1 (A1-A, A1-C). E3-KP is an INSTRUMENT TEST THAT IS
GIVEN THE DECOMPOSITION (oracle decomposition: the constituent mechanisms of each family and the R1 families that teach
each mechanism are read from WORLD_SEALED `mechanisms_used`). It is never discovery evidence.

FAMILIES. The admitted R3 / R4 families (WORLD_MANIFEST id_map status ADMITTED). Every claim is restricted to this
motif-limited admitted set.

PROCEDURE per family F with constituent mechanisms M(F) (WORLD_SEALED mechanisms_used, in that order). One ROW of the
prereg = one Config (below); the PRIMARY row is Config() = (fallback ON, TFS-1-acquired stones, constituents-only
library, keyed seed 0, OE off, budget 1e6).
  (i)   ACQUISITION UNIT (world, m) for each m: TFS-1 base keyed enumeration (no library), budget 1e6, slot = R1
        family_id, on m's R1 families (sealed R1 families with mechanisms_used == [m] that are in the id_map), in family
        index order. The FIRST dev-consistent program is taken (no hindsight) and judged on test + tribunal. The next
        R1 family is tried only if this one gives no promotable mechanism. The retry is CERTIFIER-GUIDED (a test /
        tribunal rejection moves to the next family; same as the foundry); every unit reports its attempts and
        `certifier_assisted_retry`.
  (ii)  PROMOTION: the first (pre-order) closed lambda of the kind's type (f: Int->Int, p: Int->Bool,
        s: Int->Int->Int) in the found program whose body references a parameter, not xs (contract v0.1-1), body
        size >= 2; alias-collapsed (Library.promote_lambda). READOUT FALLBACK (f / p only; the foundry QCONFIG
        chain_c_mode rule, re-implemented from its text): abstract a single (possibly repeated) readout (op xs),
        op in len/head/last/sum/max/min. PRIMARY: fallback ON (labelled); row `fallback_off` disables it.
  (iii) CHAIN: TFS-1 keyed enumeration on F (base grammar retained) with the library = the promoted stones of M(F)
        (row `all_acquired`: every acquired stone of the world), budget 1e6, slot = F. The first dev-consistent program
        is judged on test + tribunal: CHAIN-QUALIFIED iff it qualifies. The chain runs only when every constituent
        unit was acquired (otherwise CHAIN_C_FAIL; this gate is the same in every row).
  (iv)  SCRATCH control: TFS-1 enumeration on F, no library, budget 1e6, same seed / OE setting as the row.
        Scratch FAILS iff it does not produce a qualified program.

POOLED VERDICT (A1-A item 4; `--pooled`, over all admitted R3/R4 families of the given world set; n families):
  TFS1_INSTRUMENT_QUALIFIED = YES  iff every family is complete AND  5 * chain_qualified >= 4 * n  AND
  5 * scratch_fails >= 4 * n  (i.e. >= 80%, exact integer arithmetic; 12/15 for n = 15).
  Otherwise NO, and TFS1_REACHABILITY_INSTRUMENT = FAIL (not a scientific rejection). Per-world output is DESCRIPTIVE
  only (no per-world verdict). `scratch_fails_all` (the pre-production / red-team rule) is reported descriptively.

FIRST FAILING LINK per family (precise rules; LINKS):
  Attempt label for one R1 attempt (family r of unit m), witness size n_w = core.size(sealed witness of r):
    hit and NOT qualified on test + tribunal          -> UNDERDETERMINED_STONE  (R1_FIRST_DEV_CONSISTENT_FAILS_TEST)
    hit, qualified, no extractable mechanism         -> R1_ACQUISITION         (NO_EXTRACTABLE_MECHANISM)
    hit, qualified, stone rejected by promotion      -> R1_ACQUISITION         (PROMOTION_REJECTED)
    no hit and complete_through_size < n_w           -> HORIZON_R1  (CLASS_NOT_ENTERED if complete_through+1 < n_w,
                                                        else IN_CLASS: budget ran out inside the witness size class)
    no hit and complete_through_size >= n_w          -> R1_ACQUISITION (WITNESS_CLASS_COMPLETED_NO_HIT; witness not in
                                                        the walked space -- only possible with OE false merges)
    no R1 family available                           -> R1_ACQUISITION (NO_R1_FAMILY)
  Unit: ACQUIRED at the first attempt that yields a promotable stone; otherwise NOT_ACQUIRED with link = the label of
    its FIRST attempt in procedure order (all attempt labels are kept).
  Family, in chain order (the first failing link wins):
    1. some constituent unit NOT_ACQUIRED -> that unit's link (the first such unit in mechanisms_used order);
    2. chain SOLVED (qualified)           -> no failing link (CHAIN_QUALIFIED; a stone that disagrees with the sealed
                                             mechanism on probes is flagged, not failed);
    3. some constituent stone disagrees with the sealed mechanism on the probe set (agreement < 1.0)
                                          -> UNDERDETERMINED_STONE (STONE_DISAGREES_SEALED_PROBES);
    4. chain first dev-consistent program fails test / tribunal -> COMPOSITION_UNDERDETERMINED;
    5. chain no hit within budget, promoted-form witness size n_p (sealed witness_promoted with each mechanism name
       replaced by its library entry; core.size):  complete_through_size < n_p -> COMPOSITION_HORIZON
       (CLASS_NOT_ENTERED / IN_CLASS as above);  otherwise UNDERDETERMINED_STONE (WITNESS_CLASS_COMPLETED_NO_HIT:
       anomaly -- a stone that agrees on probes but not on dev values, or an OE false merge).
  The static hitting-cost bracket [cumulative(n-1)+1, cumulative(n)] of the witness size class (non-OE enumerator, the
  row's library) is reported beside every horizon label; IN_CLASS vs CLASS_NOT_ENTERED is the bracket reading.
  OE REPAIR TRIGGER (A1-A item 5; primary row only): verdict NO AND HORIZON_R1 + COMPOSITION_HORIZON form a STRICT
  MAJORITY of the families that are not chain-qualified. The plurality reading, and the literal "class not even
  entered" reading (only CLASS_NOT_ENTERED horizons count), are reported beside it. HORIZON here means "the witness
  size class was not COMPLETED within budget" (IN_CLASS included), matching prereg A1-A item 2 / red-team M1, where the
  predicted R1 failure (1e6 covers ~7% of the Int size-8 class) is called a horizon.

ROWS (each a separate cache key; all share one content-addressed search cache, so a search that is identical across
rows -- e.g. every scratch search, or every R1 search under fallback OFF that the primary already ran -- runs once):
  primary                --                                       Config()
  fallback_off           --fallback off                           Config(fallback=False)
  foundry_primitives     --given-foundry-primitives               Config(source="foundry"): stones = the foundry's
                         ACQUIRED primitives (WORLD_MANIFEST acquired_library, cross-checked against FINAL.jsonl
                         chain_c.primitive); skips TFS-1 R1 (isolates the composition step)
  seed1, seed2           --seeds 1,2                              Config(seed=s): (i), (iii) and (iv) re-keyed
  all_acquired           --all-acquired-library                   Config(scope="all"): library = every acquired stone of
                         the world (TFS-1 R1 is run on every world mechanism that has R1 families; with
                         --given-foundry-primitives: every foundry-acquired primitive)
  oe_repair              --oe                                     Config(oe=True): the single pre-registered repair,
                         run ONCE only if the primary triggers it (tfs1/enum.py OE pruning; scratch uses OE too)

E3-R (windows/E3R_PREREG.md; NOT part of the frozen E3-KP): extraction option X-ABS (`--extract xabs`; default
`frozen` = the rule above, byte-identical) and the 2x2 {OE off/on} x {X-FROZEN/X-ABS} with `--repair-class`. See
xabs_extract() for the exact rule. Frozen-row keys and records are unchanged (the extract component is added to a key
only when it is not `frozen`).

Commands (from roles/Aphrodite/beta04, OMP_NUM_THREADS=1; one process per world file at a time):
  python -m tfs1.e3.e3_known_positive --root foundry/<set> --world W --stage r1|chain|scratch|all [row flags]
         [--family F] [--mech m]
  python -m tfs1.e3.e3_known_positive --root foundry/<set> --world W --verdict [row flags]       (descriptive)
  python -m tfs1.e3.e3_known_positive --root foundry/<set> --pooled [--worlds W1,W2,..] [row flags]
Cache: <out>/KPA1_<world>.json.
"""
import argparse
import hashlib
import json
import os
import random
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

os.environ.setdefault("OMP_NUM_THREADS", "1")

from tfs1 import core as C                     # noqa: E402
from tfs1 import compress as CP                # noqa: E402
from tfs1.enum import Enumerator               # noqa: E402
from tfs1.library import Library, references_xs  # noqa: E402
from tfs1.membrane import code_hashes          # noqa: E402
from tfs1.e3 import worlds as WD               # noqa: E402

KIND_TYPE = {"f": C.F_II, "p": C.F_IB, "s": C.F_III}
BUDGET = 1_000_000
MAX_SIZE = 12
SEED = 0
HERE = Path(__file__).resolve().parent
LINKS = ("R1_ACQUISITION", "UNDERDETERMINED_STONE", "HORIZON_R1", "COMPOSITION_HORIZON",
         "COMPOSITION_UNDERDETERMINED")
HORIZON_LINKS = ("HORIZON_R1", "COMPOSITION_HORIZON")
EXTRACT_MODES = ("frozen", "xabs")
PROBE_NARROW = list(range(-40, 41))
PROBE_WIDE = list(range(-200, 201, 3))


# ================================================================ rows
class Config:
    def __init__(self, fallback: bool = True, source: str = "tfs1", scope: str = "constituents", seed: int = SEED,
                 oe: bool = False, budget: int = BUDGET, extract: str = "frozen"):
        assert source in ("tfs1", "foundry") and scope in ("constituents", "all")
        assert extract in EXTRACT_MODES
        self.fallback, self.source, self.scope = bool(fallback), source, scope
        self.seed, self.oe, self.budget = int(seed), bool(oe), int(budget)
        self.extract = extract

    def key(self) -> str:
        k = "fb%d.src-%s.lib-%s.seed%d.oe%d.B%d" % (self.fallback, self.source, self.scope, self.seed, self.oe,
                                                    self.budget)
        return k if self.extract == "frozen" else k + ".x-" + self.extract   # frozen keys unchanged

    def to_json(self) -> Dict:
        out = {"fallback": self.fallback, "source": self.source, "scope": self.scope, "seed": self.seed,
               "oe": self.oe, "budget": self.budget, "key": self.key(), "row": self.row_name()}
        if self.extract != "frozen":
            out["extract"] = self.extract
        return out

    def row_name(self) -> str:
        d = []
        if not self.fallback:
            d.append("fallback_off")
        if self.source == "foundry":
            d.append("foundry_primitives")
        if self.scope == "all":
            d.append("all_acquired")
        if self.seed != SEED:
            d.append("seed%d" % self.seed)
        if self.oe:
            d.append("oe_repair")
        if self.extract != "frozen":
            d.append(self.extract)
        if self.budget != BUDGET:
            d.append("B%d" % self.budget)
        return "+".join(d) if d else "primary"


PRIMARY = Config()


# ================================================================ extraction (ii)
def lambdas_in(t, nvars: int = 0, lib=None, out=None):
    """(lambda subterm, its type) in pre-order, for lambdas with NO free variable (closed over own params)."""
    out = [] if out is None else out
    tag = t[0]
    if tag == "lam":
        if not C.free_var_min_escape(t):
            try:
                ty = C.type_of(t, 0, None, lib)
                out.append((t, ty))
            except C.TypeErr:
                pass
        lambdas_in(t[2], nvars + t[1], lib, out)
        return out
    for c in C.children(t):
        lambdas_in(c, nvars, lib, out)
    return out


def body_refs_param(lam) -> bool:
    return C.refs_range(lam[2], 0, lam[1])


READOUTS = ("len", "head", "last", "sum", "max", "min")


def _replace_all(t, old, new):
    if t == old:
        return new
    if t[0] in ("int", "var", "xs", "hole"):
        return t
    if t[0] == "lam":
        return ("lam", t[1], _replace_all(t[2], C.shift(old, t[1]), C.shift(new, t[1])))
    return (t[0],) + tuple(_replace_all(a, old, new) for a in t[1:])


def readout_fallback(t, kind: str) -> Optional[tuple]:
    """f/p fallback (mirrors the foundry chain_c_mode text in WORLD_MANIFEST QCONFIG, re-implemented from that text
    only): abstract a single (possibly repeated) readout r = (op xs), op in len/head/last/sum/max/min: the mechanism is
    (lam x P[r := x]) provided the result references x, no longer references xs, and has the kind's result type."""
    if kind not in ("f", "p"):
        return None
    seen = []

    def go(u):
        if u[0] in READOUTS and len(u) == 2 and u[1] == ("xs",):
            if u not in seen:
                seen.append(u)
        for c in C.children(u):
            go(c)
    go(t)
    want_ret = C.INT if kind == "f" else C.BOOL
    for r in seen:
        body = _replace_all(t, r, ("var", 0))
        if references_xs(body) or C.size(body) < 2:
            continue
        lam = ("lam", 1, body)
        try:
            if C.type_of(lam) == KIND_TYPE[kind] and C.type_of(body, 1) == want_ret:
                return lam
        except C.TypeErr:
            continue
    return None


def extract_mechanism(program: str, kind: str, lib=None, fallback: bool = True, mode: str = "frozen",
                      dev_inputs=None) -> Optional[tuple]:
    """Returns (lambda, how) or None. how = 'closed_lambda' | 'readout_fallback' (only if fallback=True)
    | 'xabs_absorbed' (mode='xabs' only). mode='frozen' (default) is the frozen E3-KP rule, unchanged."""
    if mode == "xabs":
        ab = xabs_extract(program, kind, dev_inputs)
        if ab is not None:
            return ab["stone"], "xabs_absorbed"
    elif mode != "frozen":
        raise ValueError("unknown extraction mode %r" % mode)
    t = C.parse(program)
    want = KIND_TYPE[kind]
    for lam, ty in lambdas_in(t, 0, lib):
        if ty == want and body_refs_param(lam) and not references_xs(lam) and C.size(lam[2]) >= 2:
            return lam, "closed_lambda"
    if not fallback:
        return None
    lam = readout_fallback(t, kind)
    return (lam, "readout_fallback") if lam is not None else None


# ================================================================ X-ABS (E3-R; not frozen E3-KP)
ELEMENT_REDUCERS = ("max", "min", "head", "last")
REDUCER_DUAL = {"max": "min", "min": "max", "head": "head", "last": "last"}
XABS_SEED = "TFS1/XABS/v0"
XABS_N_PROBES = 200


def xabs_probe_lists(dev_inputs) -> List[List[int]]:
    """The fixed target-blind probe set: 200 lists from one fixed seed; elements uniform in [lo, hi], the union of the
    R1 dev input element range; lengths uniform in [0, the longest dev input]. Uses dev INPUTS only."""
    els = [int(v) for i in dev_inputs for v in i]
    lo, hi = (min(els), max(els)) if els else (0, 0)
    lmax = max((len(i) for i in dev_inputs), default=1)
    rng = random.Random(XABS_SEED)
    return [[rng.randint(lo, hi) for _ in range(rng.randint(0, lmax))] for _ in range(XABS_N_PROBES)]


def _value(t, inp):
    v = C.evaluate(t, list(inp))[0]
    return v


def _agree_all(p, q, inputs) -> bool:
    for inp in inputs:
        if not C.same_value(_value(p, inp), _value(q, inp)):
            return False
    return True


def _plug(t, path, filler):
    if not path:
        return filler
    i = path[0]
    return t[:i] + (_plug(t[i], path[1:], filler),) + t[i + 1:]


def xabs_candidates(t) -> List[Dict]:
    """Every absorbed candidate of a program t (kind f). N = (map L xs) with L a closed Int->Int lambda (body references
    its parameter, no xs, body size >= 2) whose parent R is max / min / head / last, with R(N) and every ancestor used
    NOT under any lambda. For each proper ancestor A of R(N) (A = C[R(N)], C an Int context on the path), the
    candidate L' = (lam x C[body(L)]); it must be closed, xs-free and of type Int->Int."""
    out = []

    def walk(u, path):
        if u[0] == "lam":
            return                                   # nothing under a lambda (absorbed contexts must be closed)
        if (u[0] in ELEMENT_REDUCERS and len(u) == 2 and u[1][0] == "map" and u[1][1][0] == "lam"
                and u[1][1][1] == 1 and u[1][2] == ("xs",)):
            L = u[1][1]
            if (not C.free_var_min_escape(L) and body_refs_param(L) and not references_xs(L)
                    and C.size(L[2]) >= 2):
                for j in range(len(path)):            # ancestors: path[:j] addresses A; path[j:] = hole inside A
                    A = _get(t, path[:j])
                    body = _plug(A, path[j:], L[2])
                    lam = ("lam", 1, body)
                    try:
                        ok = (C.type_of(lam) == C.F_II and not references_xs(lam)
                              and not C.free_var_min_escape(lam))
                    except C.TypeErr:
                        ok = False
                    if ok:
                        out.append({"L": L, "reducer": u[0], "stone": lam, "absorbed": C.size(A) - C.size(u),
                                    "ancestor_path": list(path[:j])})
        for i, c in enumerate(u[1:], 1):
            if isinstance(c, tuple):
                walk(c, path + [i])
    walk(t, [])
    return out


def _get(t, path):
    for i in path:
        t = t[i]
    return t


def xabs_extract(program: str, kind: str, dev_inputs) -> Optional[Dict]:
    """X-ABS (E3R_PREREG): kind f only. A candidate L' is VALID iff P' = R'(map L' xs) agrees with P (value-or-FAIL) on
    every dev input AND on the 200 fixed probe lists, for R' = R (tried first) or, failing that, the dual reducer
    (max <-> min; head / last are self-dual) -- the dual covers a sign-flipping context (e.g. (sub 1 (min ..)) =
    (max (map (lam x (sub 1 ..)) xs))); the check uses P's own outputs, never the sealed mechanism. The MAXIMALLY
    absorbed valid candidate is the stone (ties: the smaller term, then its text). None if no absorbed candidate is
    valid (the caller then applies the frozen rule, readout fallback included)."""
    if kind != "f":
        return None
    if dev_inputs is None:
        raise ValueError("X-ABS needs the R1 dev inputs")
    t = C.parse(program)
    cands = xabs_candidates(t)
    if not cands:
        return None
    inputs = [list(i) for i in dev_inputs] + xabs_probe_lists(dev_inputs)
    valid = []
    for c in cands:
        for r in (c["reducer"], REDUCER_DUAL[c["reducer"]]):
            p2 = (r, ("map", c["stone"], ("xs",)))
            if _agree_all(t, p2, inputs):
                valid.append(dict(c, reducer_used=r))
                break
            if REDUCER_DUAL[c["reducer"]] == c["reducer"]:
                break
    if not valid:
        return None
    best = sorted(valid, key=lambda c: (-c["absorbed"], C.size(c["stone"]), C.to_str(c["stone"])))[0]
    return best


# ================================================================ search + cache
def _search(task, lib, seed=SEED, budget=BUDGET, oe=False) -> Dict:
    E = Enumerator(lib, oe=oe)
    t0 = time.process_time()
    r = E.search(task["dev"], task["output_type"], seed, task["family_id"], budget, MAX_SIZE)
    r["cpu_s"] = round(time.process_time() - t0, 2)
    top = 8 if not oe else min(8, (r["complete_through_size"] or 0) + 1)   # OE: only classes already built
    r["class_sizes"] = {n: E.count(task["output_type"], (), n) for n in range(1, top + 1)}
    r.pop("hits", None)
    r["false_hits"] = len(r.get("false_hits", []))
    del E
    return r


def search_key(fid, lib, cfg: Config) -> str:
    return "%s|seed=%d|lib=%s|oe=%d|B=%d|max=%d" % (fid, cfg.seed, lib.sha256()[:16] if lib is not None else "-",
                                                     cfg.oe, cfg.budget, MAX_SIZE)


def _cache_path(out_dir, world):
    return Path(out_dir) / ("KPA1_%s.json" % world)


def _load(out_dir, world) -> Dict:
    p = _cache_path(out_dir, world)
    d = json.loads(p.read_text()) if p.exists() else {}
    d.setdefault("world", world)
    d.setdefault("searches", {})
    d.setdefault("rows", {})
    return d


def e3_code_hashes() -> Dict[str, str]:
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.glob("*.py"))}


def _save(out_dir, world, d):
    p = _cache_path(out_dir, world)
    p.parent.mkdir(parents=True, exist_ok=True)
    d["code_sha256"] = code_hashes()
    d["e3_code_sha256"] = e3_code_hashes()
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, indent=1, sort_keys=True))
    os.replace(tmp, p)


def _row(d, cfg: Config) -> Dict:
    r = d["rows"].setdefault(cfg.key(), {})
    r["config"] = cfg.to_json()
    r.setdefault("units", {})
    r.setdefault("chain", {})
    r.setdefault("scratch", {})
    return r


def _horizon(complete_through, n_w) -> Optional[str]:
    """None if the witness class was completed; else CLASS_NOT_ENTERED / IN_CLASS."""
    ct = complete_through or 0
    if ct >= n_w:
        return None
    return "CLASS_NOT_ENTERED" if ct + 1 < n_w else "IN_CLASS"


# ================================================================ the procedure for one world
class KP:
    def __init__(self, root, world):
        self.root, self.world = Path(root), world
        self.ev = WD.Evaluator(root, world)
        self.sealed = WD.sealed(root, world)
        self.mech = {m["name"]: m for m in self.sealed["mechanisms"]}
        self.fams = {f["family_id"]: f for f in self.sealed["families"]}
        self.by_fid = {m["family_id"]: o for o, m in self.ev.id_map.items()}
        self._bracket_cache: Dict[Tuple, List[int]] = {}

    # ---- coordinator-side facts
    def admitted(self) -> List[str]:
        return [self.ev.meta(o)["family_id"] for o in self.ev.admitted(("R3", "R4"))]

    def task(self, fid):
        return self.ev.task(self.by_fid[fid])

    def r1_families(self, m) -> List[str]:
        out = [f for f in self.sealed["families"] if f["rung"] == "R1" and f["mechanisms_used"] == [m]
               and f["family_id"] in self.by_fid]
        return [f["family_id"] for f in sorted(out, key=lambda f: f["index"])]

    def constituents(self, fid) -> List[str]:
        return list(self.fams[fid]["mechanisms_used"])

    def needed_units(self, cfg: Config) -> List[str]:
        need = {m for f in self.admitted() for m in self.constituents(f)}
        if cfg.scope == "all":
            if cfg.source == "foundry":
                need |= set(self.foundry_acquired())
            else:
                need |= {m for m in self.mech if self.r1_families(m)}
        return sorted(need)

    def witness_size(self, fid) -> int:
        return C.size(C.parse(self.fams[fid]["witness"]))

    def bracket(self, T, n, lib=None) -> List[int]:
        k = (T, n, lib.sha256() if lib is not None else None)
        if k not in self._bracket_cache:
            E = Enumerator(lib)
            self._bracket_cache[k] = [E.cumulative(T, n - 1) + 1, E.cumulative(T, n)]
        return self._bracket_cache[k]

    # ---- probes (diagnostic only; never used to select a stone)
    def agree_sealed(self, m, lam_text, vals=None) -> float:
        a, b = C.parse(lam_text), C.parse(self.mech[m]["term"])
        vals = PROBE_NARROW if vals is None else vals
        k = a[1]
        if k != b[1]:
            return 0.0
        args = [(v,) for v in vals] if k == 1 else [(u, v) for u in vals[::4] for v in vals[::4]]
        same = 0
        for xs in args:
            ra = C.evaluate(("app", a) + tuple(("int", v) for v in xs), [])[0]
            rb = C.evaluate(("app", b) + tuple(("int", v) for v in xs), [])[0]
            same += C.same_value(ra, rb)
        return round(same / len(args), 4)

    # ---- cached search
    def search(self, d, fid, lib, cfg: Config) -> Dict:
        k = search_key(fid, lib, cfg)
        if k not in d["searches"]:
            r = _search(self.task(fid), lib, cfg.seed, cfg.budget, cfg.oe)
            if r["hit"]:
                r["verdict"] = WD.judge(r["program"], self.task(fid), lib)
            d["searches"][k] = r
        return d["searches"][k]

    # ---- (i) + (ii) TFS-1 acquisition unit
    def run_unit(self, d, m, cfg: Config) -> Dict:
        if cfg.source == "foundry":
            return self.foundry_unit(m)
        kind = self.mech[m]["kind"]
        attempts = []
        fams = self.r1_families(m)
        for fid in fams:
            r = self.search(d, fid, None, cfg)
            n_w = self.witness_size(fid)
            T = self.task(fid)["output_type"]
            row = {"family_id": fid, "found": r["program"], "charge": r["hit_charge"], "charges": r["charges"],
                   "cpu_s": r["cpu_s"], "complete_through_size": r["complete_through_size"],
                   "witness_size": n_w, "witness_bracket": self.bracket(T, n_w)}
            if cfg.oe:
                row["oe_stats"] = r.get("oe_stats")
            if r["hit"]:
                row["verdict"] = r["verdict"]
                if not r["verdict"]["qualified"]:
                    row["label"], row["detail"] = "UNDERDETERMINED_STONE", "R1_FIRST_DEV_CONSISTENT_FAILS_TEST"
                else:
                    if cfg.extract == "frozen":
                        ex = extract_mechanism(r["program"], kind, fallback=cfg.fallback)
                    else:
                        ex = extract_mechanism(r["program"], kind, fallback=cfg.fallback, mode=cfg.extract,
                                               dev_inputs=[i for i, _o in self.task(fid)["dev"]])
                    if ex is None:
                        row["label"] = "R1_ACQUISITION"
                        row["detail"] = "NO_EXTRACTABLE_MECHANISM" + ("" if cfg.fallback else "_FALLBACK_OFF")
                    else:
                        lam_s = C.to_str(ex[0])
                        try:
                            Library(closed_args=True).promote_lambda(ex[0], {})
                            row.update({"label": None, "detail": "ACQUIRED", "mechanism_lambda": lam_s,
                                        "extraction": ex[1]})
                        except (ValueError, C.TypeErr) as e:
                            row.update({"label": "R1_ACQUISITION", "detail": "PROMOTION_REJECTED",
                                        "mechanism_lambda": lam_s, "promotion_error": repr(e)})
            else:
                h = _horizon(r["complete_through_size"], n_w)
                if h is not None:
                    row["label"], row["detail"] = "HORIZON_R1", h
                else:
                    row["label"], row["detail"] = "R1_ACQUISITION", "WITNESS_CLASS_COMPLETED_NO_HIT"
            attempts.append(row)
            if row["detail"] == "ACQUIRED":
                lam = row["mechanism_lambda"]
                return {"mechanism": m, "kind": kind, "status": "ACQUIRED", "source": "tfs1", "lambda": lam,
                        "extraction": row["extraction"], "from": fid, "n_attempts": len(attempts),
                        "certifier_assisted_retry": any(a.get("detail") == "R1_FIRST_DEV_CONSISTENT_FAILS_TEST"
                                                        for a in attempts[:-1]),
                        "agrees_with_sealed_on_probe": self.agree_sealed(m, lam),
                        "agrees_with_sealed_wide": self.agree_sealed(m, lam, PROBE_WIDE),
                        "attempts": attempts}
        first = attempts[0] if attempts else {"label": "R1_ACQUISITION", "detail": "NO_R1_FAMILY"}
        return {"mechanism": m, "kind": kind, "status": "NOT_ACQUIRED", "source": "tfs1", "n_attempts": len(attempts),
                "certifier_assisted_retry": any(a.get("detail") == "R1_FIRST_DEV_CONSISTENT_FAILS_TEST"
                                                for a in attempts[:-1]),
                "link": first["label"], "link_detail": first["detail"],
                "attempt_labels": [a["label"] for a in attempts], "attempts": attempts}

    # ---- foundry-acquired primitives (row foundry_primitives)
    def foundry_acquired(self) -> Dict[str, Dict]:
        w = WD.world_manifest(self.root)["worlds"][self.world]
        return dict(w.get("acquired_library", {}).get("acquired", {}))

    def _final_chain_c(self, fid) -> Optional[Dict]:
        p = self.root / self.world / "FINAL.jsonl"
        if not p.exists():
            return None
        for line in p.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                if r.get("family_id") == fid:
                    return r.get("chain_c")
        return None

    def foundry_unit(self, m) -> Dict:
        acq = self.foundry_acquired().get(m)
        kind = self.mech[m]["kind"]
        if acq is None:
            return {"mechanism": m, "kind": kind, "status": "NOT_ACQUIRED", "source": "foundry",
                    "link": "R1_ACQUISITION", "link_detail": "FOUNDRY_NOT_ACQUIRED", "attempts": []}
        cc = self._final_chain_c(acq["from"])
        cross = None if cc is None else (cc.get("primitive") == acq["term"] and cc.get("status") == "ACQUIRED")
        if cross is False:
            raise ValueError("foundry acquired_library disagrees with FINAL.jsonl chain_c for %s/%s" % (self.world, m))
        rec = {"mechanism": m, "kind": kind, "status": "ACQUIRED", "source": "foundry", "lambda": acq["term"],
               "extraction": (cc or {}).get("extraction", "foundry"), "from": acq["from"],
               "final_jsonl_crosscheck": cross,
               "foundry_agree_with_sealed": acq.get("agree_with_sealed"),
               "agrees_with_sealed_on_probe": self.agree_sealed(m, acq["term"]),
               "agrees_with_sealed_wide": self.agree_sealed(m, acq["term"], PROBE_WIDE), "attempts": []}
        try:
            Library(closed_args=True).promote_lambda(C.parse(acq["term"]), {})
        except (ValueError, C.TypeErr) as e:
            rec.update({"status": "NOT_ACQUIRED", "link": "R1_ACQUISITION", "link_detail": "PROMOTION_REJECTED",
                        "promotion_error": repr(e)})
        return rec

    # ---- library for (iii)
    def library_for(self, fid, units: Dict, cfg: Config) -> Tuple[Optional[Library], Dict[str, str]]:
        for m in self.constituents(fid):
            if units.get(m, {}).get("status") != "ACQUIRED":
                return None, {}
        ms = self.constituents(fid) if cfg.scope == "constituents" else \
            sorted(m for m, u in units.items() if u.get("status") == "ACQUIRED")
        lib = Library(closed_args=True)
        slot = {}
        for m in ms:
            u = units[m]
            e, _st = lib.promote_lambda(C.parse(u["lambda"]), {"mechanism_slot": m, "from": u["from"],
                                                               "source": u["source"], "procedure": "E3-KP (ii)"})
            slot[m] = e.alias_of or e.id
        return lib, slot

    def promoted_witness(self, fid, lib, slot) -> Tuple[tuple, str]:
        """The sealed witness in promoted form with each mechanism replaced by ITS library entry (by slot);
        falls back to compress.refactor of the expanded witness when witness_promoted is absent."""
        wp = self.fams[fid].get("witness_promoted")
        if wp:
            t = C.parse(wp)

            def ren(u):
                if u[0] in ("int", "var", "xs", "hole"):
                    return u
                if u[0] == "lam":
                    return ("lam", u[1], ren(u[2]))
                head = slot.get(u[0], u[0])
                return (head,) + tuple(ren(a) for a in u[1:])
            if all(c in slot or c in C.PRIM_SIGS for c in self._ops(t)):
                return ren(t), "witness_promoted_by_slot"
        return CP.refactor(C.parse(self.task(fid)["witness"]), lib), "refactor"

    def _ops(self, t, out=None):
        out = set() if out is None else out
        if t[0] in ("int", "var", "xs", "hole"):
            return out
        if t[0] == "lam":
            return self._ops(t[2], out)
        out.add(t[0])
        for a in t[1:]:
            self._ops(a, out)
        return out

    def static_diag(self, fid, lib, slot) -> Dict:
        pw, how = self.promoted_witness(fid, lib, slot)
        T = self.task(fid)["output_type"]
        n = C.size(pw)
        return {"witness": self.task(fid)["witness"], "witness_promoted_form": C.to_str(pw), "promoted_form_how": how,
                "size_promoted_form": n, "uses_entries": sorted(set(C.calls_in(pw))),
                "hitting_cost_bracket": self.bracket(T, n, lib)}

    # ---- (iii)
    def run_chain(self, d, fid, units: Dict, cfg: Config) -> Dict:
        lib, slot = self.library_for(fid, units, cfg)
        if lib is None:
            return {"family_id": fid, "status": "CHAIN_C_FAIL",
                    "missing": [m for m in self.constituents(fid) if units.get(m, {}).get("status") != "ACQUIRED"]}
        diag = self.static_diag(fid, lib, slot)
        r = self.search(d, fid, lib, cfg)
        row = {"family_id": fid, "rung": self.fams[fid]["rung"], "library_sha256": lib.sha256(),
               "library_entries": [{"id": e["id"], "body": e["body"], "slot": e["provenance"].get("mechanism_slot")}
                                   for e in lib.to_json()["entries"]],
               "found": r["program"], "charge": r["hit_charge"], "charges": r["charges"], "cpu_s": r["cpu_s"],
               "complete_through_size": r["complete_through_size"], "units_expanded": r["units_expanded"],
               "units_promoted": r["units_promoted"], "static": diag}
        if cfg.oe:
            row["oe_stats"] = r.get("oe_stats")
        if r["hit"]:
            row["verdict"] = r["verdict"]
            row["uses_library"] = C.has_call(C.parse(r["program"]))
            row["status"] = "SOLVED" if r["verdict"]["qualified"] else "FIRST_DEV_CONSISTENT_FAILS_TEST"
        else:
            row["status"] = "NOT_FOUND_AT_BUDGET"
        return row

    # ---- (iv)
    def run_scratch(self, d, fid, cfg: Config) -> Dict:
        r = self.search(d, fid, None, cfg)
        row = {"family_id": fid, "found": r["program"], "charge": r["hit_charge"], "charges": r["charges"],
               "cpu_s": r["cpu_s"], "complete_through_size": r["complete_through_size"],
               "witness_size": self.witness_size(fid)}
        if r["hit"]:
            row["verdict"] = r["verdict"]
            row["status"] = "SOLVED_FROM_SCRATCH" if r["verdict"]["qualified"] else "FIRST_DEV_CONSISTENT_FAILS_TEST"
        else:
            row["status"] = "NOT_FOUND_AT_BUDGET"
        return row

    # ---- link classification (pure function of cached rows)
    def family_link(self, fid, units: Dict, chain: Optional[Dict]) -> Dict:
        cons = self.constituents(fid)
        for m in cons:
            u = units.get(m)
            if u is None:
                return {"link": None, "detail": "INCOMPLETE"}
            if u["status"] != "ACQUIRED":
                return {"link": u["link"], "detail": u["link_detail"], "unit": m,
                        "all_missing_unit_links": {mm: units[mm].get("link") for mm in cons
                                                   if units.get(mm, {}).get("status") != "ACQUIRED"}}
        if chain is None:
            return {"link": None, "detail": "INCOMPLETE"}
        disagree = [m for m in cons if units[m].get("agrees_with_sealed_on_probe", 1.0) < 1.0]
        if chain["status"] == "SOLVED":
            return {"link": None, "detail": "CHAIN_QUALIFIED", "stone_disagrees_sealed": disagree}
        if chain["status"] == "CHAIN_C_FAIL":       # library build failed although every unit is ACQUIRED
            return {"link": "R1_ACQUISITION", "detail": "PROMOTION_REJECTED"}
        if disagree:
            return {"link": "UNDERDETERMINED_STONE", "detail": "STONE_DISAGREES_SEALED_PROBES", "units": disagree}
        if chain["status"] == "FIRST_DEV_CONSISTENT_FAILS_TEST":
            return {"link": "COMPOSITION_UNDERDETERMINED", "detail": "CHAIN_FIRST_DEV_CONSISTENT_FAILS_TEST"}
        n_p = chain["static"]["size_promoted_form"]
        h = _horizon(chain["complete_through_size"], n_p)
        if h is not None:
            return {"link": "COMPOSITION_HORIZON", "detail": h, "size_promoted_form": n_p,
                    "bracket": chain["static"]["hitting_cost_bracket"]}
        return {"link": "UNDERDETERMINED_STONE", "detail": "WITNESS_CLASS_COMPLETED_NO_HIT", "anomaly": True}

    # ---- per-world descriptive table for one row
    def describe(self, d, cfg: Config) -> Dict:
        row = d.get("rows", {}).get(cfg.key(), {})
        units, chain, scratch = row.get("units", {}), row.get("chain", {}), row.get("scratch", {})
        fams = []
        for fid in self.admitted():
            ln = self.family_link(fid, units, chain.get(fid))
            sc = scratch.get(fid)
            ch = chain.get(fid)
            r1_cpu = sum(a.get("cpu_s", 0) or 0 for m in self.constituents(fid)
                         for a in units.get(m, {}).get("attempts", []))
            fams.append({
                "world": self.world, "family_id": fid, "rung": self.fams[fid]["rung"],
                "skeleton": self.fams[fid].get("skeleton"), "constituents": self.constituents(fid),
                "chain_status": ch["status"] if ch else None, "chain_qualified": bool(ch and ch["status"] == "SOLVED"),
                "scratch_status": sc["status"] if sc else None,
                "scratch_fails": None if sc is None else sc["status"] not in ("SOLVED_FROM_SCRATCH", "CENSORED"),
                "complete": ch is not None and sc is not None and all(m in units for m in self.constituents(fid)),
                "first_failing_link": ln["link"], "link_detail": ln["detail"], "link_info": ln,
                "extraction": {m: units.get(m, {}).get("extraction") for m in self.constituents(fid)},
                "cpu_s": {"r1_units_attributed": round(r1_cpu, 2), "chain": (ch or {}).get("cpu_s", 0.0),
                          "scratch": (sc or {}).get("cpu_s", 0.0)}})
        unit_rows = [{"world": self.world, "mechanism": m, "status": u.get("status"), "link": u.get("link"),
                      "link_detail": u.get("link_detail"), "from": u.get("from"), "lambda": u.get("lambda"),
                      "extraction": u.get("extraction"), "n_attempts": u.get("n_attempts"),
                      "certifier_assisted_retry": u.get("certifier_assisted_retry"),
                      "agrees_with_sealed_on_probe": u.get("agrees_with_sealed_on_probe"),
                      "agrees_with_sealed_wide": u.get("agrees_with_sealed_wide"),
                      "cpu_s": round(sum(a.get("cpu_s", 0) or 0 for a in u.get("attempts", [])), 2)}
                     for m, u in sorted(units.items())]
        return {"world": self.world, "row": cfg.to_json(), "families": fams, "units": unit_rows,
                "descriptive_only": "per-world output is descriptive; the verdict is POOLED (A1-A item 4)"}


# ================================================================ pooled verdict
def pooled_verdict(families: List[Dict], primary: bool) -> Dict:
    n = len(families)
    complete = n > 0 and all(f["complete"] for f in families)
    q = sum(f["chain_qualified"] for f in families)
    sf = sum(bool(f["scratch_fails"]) for f in families)
    ok = complete and 5 * q >= 4 * n and 5 * sf >= 4 * n
    failing = [f for f in families if not f["chain_qualified"]]
    links = {k: sum(f["first_failing_link"] == k for f in failing) for k in LINKS}
    links["INCOMPLETE"] = sum(f["first_failing_link"] is None and not f["chain_qualified"] for f in failing)
    hz = links["HORIZON_R1"] + links["COMPOSITION_HORIZON"]
    top = max(LINKS, key=lambda k: (links[k], -LINKS.index(k))) if failing else None
    verdict = "INCOMPLETE" if not complete else ("YES" if ok else "NO")
    out = {"n_admitted_R3_R4": n, "chain_qualified": q, "scratch_fails": sf, "complete": complete,
           "TFS1_INSTRUMENT_QUALIFIED": verdict,
           "TFS1_REACHABILITY_INSTRUMENT": "FAIL" if verdict == "NO" else None,
           "rule": "YES iff 5*chain_qualified >= 4*n AND 5*scratch_fails >= 4*n (>= 80%, pooled over the admitted "
                   "R3/R4 families of the world set); else NO => TFS1_REACHABILITY_INSTRUMENT = FAIL",
           "scratch_fails_all_descriptive": complete and sf == n,
           "first_failing_link_counts": links, "dominant_link_plurality": top,
           "horizon_links": hz, "n_not_chain_qualified": len(failing),
           "horizon_in_class_vs_not_entered": {
               "IN_CLASS": sum(f["first_failing_link"] in HORIZON_LINKS and f["link_detail"] == "IN_CLASS"
                               for f in failing),
               "CLASS_NOT_ENTERED": sum(f["first_failing_link"] in HORIZON_LINKS
                                        and f["link_detail"] == "CLASS_NOT_ENTERED" for f in failing)},
           "by_rung": {rg: {"n": sum(f["rung"] == rg for f in families),
                            "chain_qualified": sum(f["chain_qualified"] for f in families if f["rung"] == rg)}
                       for rg in ("R3", "R4")},
           "by_skeleton": {}, "by_world": {}}
    for f in families:
        for key, val in (("by_skeleton", f.get("skeleton")), ("by_world", f["world"])):
            b = out[key].setdefault(str(val), {"n": 0, "chain_qualified": 0})
            b["n"] += 1
            b["chain_qualified"] += int(f["chain_qualified"])
    if primary:
        trig = verdict == "NO" and len(failing) > 0 and 2 * hz > len(failing)
        out["oe_repair_trigger"] = {
            "triggered": trig,
            "rule": "primary NO AND HORIZON_R1 + COMPOSITION_HORIZON > 50% of the families not chain-qualified "
                    "(strict-majority reading of 'dominant'); run --oe ONCE; if still NO: "
                    "TFS1_REACHABILITY_INSTRUMENT = FAIL",
            "plurality_reading": verdict == "NO" and top in HORIZON_LINKS,
            "not_entered_only_reading": verdict == "NO" and len(failing) > 0 and 2 * out[
                "horizon_in_class_vs_not_entered"]["CLASS_NOT_ENTERED"] > len(failing)}
    return out


def pooled(root, worlds: Optional[List[str]], cfg: Config, out_dir) -> Dict:
    man = WD.world_manifest(root)
    worlds = worlds or sorted(man["worlds"])
    fams, units, per_world = [], [], {}
    for w in worlds:
        kp = KP(root, w)
        if not kp.admitted():
            continue
        d = _load(out_dir, w)
        desc = kp.describe(d, cfg)
        fams += desc["families"]
        units += desc["units"]
        per_world[w] = {"n": len(desc["families"]), "chain_qualified": sum(f["chain_qualified"] for f in desc["families"])}
    v = pooled_verdict(fams, primary=(cfg.key() == PRIMARY.key()))
    res = {"row": cfg.to_json(), "root": str(root), "worlds": worlds, "label": _label(root),
           "claim_limits": "INSTRUMENT TEST GIVEN THE DECOMPOSITION (oracle decomposition); restricted to the "
                           "motif-limited admitted R3/R4 set; not discovery evidence",
           "verdict": v, "families": fams, "units": units, "per_world_descriptive": per_world}
    if cfg.key() in (PRIMARY.key(), Config(fallback=False).key()):
        other = Config(fallback=not cfg.fallback)
        of = []
        for w in worlds:
            kp = KP(root, w)
            if kp.admitted():
                of += kp.describe(_load(out_dir, w), other)["families"]
        ov = pooled_verdict(of, primary=False)
        a, b = (v, ov) if cfg.fallback else (ov, v)
        res["A1_C"] = {"primary_fallback_on": a["TFS1_INSTRUMENT_QUALIFIED"],
                       "fallback_off": b["TFS1_INSTRUMENT_QUALIFIED"],
                       "agree": a["TFS1_INSTRUMENT_QUALIFIED"] == b["TFS1_INSTRUMENT_QUALIFIED"],
                       "recommendation_uses": "fallback_off row" if a["TFS1_INSTRUMENT_QUALIFIED"] !=
                       b["TFS1_INSTRUMENT_QUALIFIED"] else "both rows agree (state both)"}
    return res


def _label(root) -> str:
    return "EXPOSED DEV DATA (pilot)" if "pilot" in str(root) else "PRODUCTION"


# ================================================================ stages
def seed_cache(d, seed_dir, world) -> bool:
    """E3-R: import the frozen E3-KP cache (every search + the PRIMARY row, marked copied_from) into a fresh world file,
    so the OE-off x X-FROZEN cell IS the frozen primary and every shared search (R1, non-OE scratch) is re-used."""
    if seed_dir is None or d.get("seeded_from"):
        return False
    src = _load(seed_dir, world)
    if PRIMARY.key() not in src.get("rows", {}):
        raise ValueError("no frozen E3-KP primary row for %s in %s" % (world, seed_dir))
    for k, v in src["searches"].items():
        d["searches"].setdefault(k, v)
    if PRIMARY.key() not in d["rows"]:
        d["rows"][PRIMARY.key()] = dict(src["rows"][PRIMARY.key()], copied_from=str(seed_dir))
    d["seeded_from"] = {"dir": str(seed_dir), "n_searches": len(src["searches"]),
                        "code_sha256_of_source": src.get("e3_code_sha256")}
    return True


def _scratch_child(root, world, fid, cfg_json, q):
    os.environ["OMP_NUM_THREADS"] = "1"
    kp = KP(root, world)
    cfg = Config(**{k: cfg_json[k] for k in ("fallback", "source", "scope", "seed", "oe", "budget")},
                 extract=cfg_json.get("extract", "frozen"))
    r = _search(kp.task(fid), None, cfg.seed, cfg.budget, cfg.oe)
    if r["hit"]:
        r["verdict"] = WD.judge(r["program"], kp.task(fid))
    q.put(r)


def run_scratch_capped(kp, d, fid, cfg: Config, cap_s: float) -> Dict:
    """Development only: the scratch search in ONE child process; if its CPU exceeds cap_s it is stopped (it is this
    process's own child) and the row is CENSORED, which counts as NOT failed (prereg A3.6)."""
    k = search_key(fid, None, cfg)
    if k in d["searches"]:
        return kp.run_scratch(d, fid, cfg)
    cen = d.setdefault("censored_searches", {}).get(k)
    if cen is not None and cen["cap_s"] >= cap_s:            # the same search was already censored at >= this cap
        return dict(cen["row"], reused_censored_search=k)
    import multiprocessing as mp
    import psutil
    q = mp.get_context("spawn").Queue()
    pr = mp.get_context("spawn").Process(target=_scratch_child, args=(str(kp.root), kp.world, fid, cfg.to_json(), q))
    pr.start()
    ps = psutil.Process(pr.pid)
    cpu = 0.0
    while True:
        try:
            r = q.get(timeout=2.0)
            pr.join()
            d["searches"][k] = r
            return kp.run_scratch(d, fid, cfg)
        except Exception:                      # noqa: BLE001 (queue.Empty)
            pass
        try:
            t = ps.cpu_times()
            cpu = t.user + t.system
        except psutil.NoSuchProcess:
            pass
        if cpu > cap_s:
            pr.terminate()
            pr.join()
            row = {"family_id": fid, "status": "CENSORED", "cpu_s": round(cpu, 1), "cap_s": cap_s,
                   "found": None, "charge": None, "charges": None, "complete_through_size": None,
                   "witness_size": kp.witness_size(fid), "censored_reason": "development CPU cap"}
            d["censored_searches"][k] = {"cap_s": cap_s, "row": row}
            return row
        if not pr.is_alive() and q.empty():
            raise RuntimeError("scratch child died: %s %s" % (kp.world, fid))


def run_stages(root, world, cfg: Config, stage: str, out_dir, family=None, mech=None, log=print, seed_from=None,
               scratch_cpu_cap=None) -> Dict:
    kp = KP(root, world)
    d = _load(out_dir, world)
    if seed_cache(d, seed_from, world):
        log("seeded cache from %s (%d searches)" % (seed_from, d["seeded_from"]["n_searches"]))
    adm = kp.admitted()
    d["admitted"] = adm
    d["label"] = _label(root)
    row = _row(d, cfg)
    if stage in ("r1", "chain", "all"):
        todo = [mech] if (mech and stage == "r1") else kp.needed_units(cfg)
        for m in todo:
            if m not in row["units"]:
                row["units"][m] = kp.run_unit(d, m, cfg)
                _save(out_dir, world, d)
                u = row["units"][m]
                log("unit %s %s %s %s" % (m, u["status"], u.get("lambda"), u.get("link")))
    if stage in ("chain", "all"):
        for f in ([family] if family else adm):
            if f not in row["chain"]:
                row["chain"][f] = kp.run_chain(d, f, row["units"], cfg)
                _save(out_dir, world, d)
                log("chain %s %s %s" % (f, row["chain"][f]["status"], row["chain"][f].get("charge")))
    if stage in ("scratch", "all"):
        for f in ([family] if family else adm):
            if f not in row["scratch"]:
                row["scratch"][f] = (kp.run_scratch(d, f, cfg) if scratch_cpu_cap is None
                                     else run_scratch_capped(kp, d, f, cfg, scratch_cpu_cap))
                _save(out_dir, world, d)
                log("scratch %s %s" % (f, row["scratch"][f]["status"]))
    row["descriptive"] = kp.describe(d, cfg)
    _save(out_dir, world, d)
    return d


def configs_from_args(a) -> List[Config]:
    seeds = [int(s) for s in a.seeds.split(",")] if a.seeds else [a.seed]
    return [Config(fallback=(a.fallback == "on"), source="foundry" if a.given_foundry_primitives else "tfs1",
                   scope="all" if a.all_acquired_library else "constituents", seed=s, oe=a.oe, budget=a.budget,
                   extract=a.extract)
            for s in seeds]


# ================================================================ E3-R 2x2 and REPAIR_CLASS (windows/E3R_PREREG.md)
def e3r_cells(budget=BUDGET, seed=SEED) -> Dict[str, Config]:
    return {"off_frozen": Config(budget=budget, seed=seed),
            "on_frozen": Config(oe=True, budget=budget, seed=seed),
            "off_xabs": Config(extract="xabs", budget=budget, seed=seed),
            "on_xabs": Config(oe=True, extract="xabs", budget=budget, seed=seed)}


def repair_class_from(cells: Dict[str, Dict]) -> Dict:
    """Pure: cells name -> pooled_verdict(...) dict. A cell COUNTS as >= 80% iff complete, 5q >= 4n AND
    5 * scratch_fails >= 4n; a cell with 5q >= 4n but too few scratch failures is TRIVIALISED (not counted)."""
    st = {}
    for name, v in cells.items():
        n, q, sf = v["n_admitted_R3_R4"], v["chain_qualified"], v["scratch_fails"]
        hi = v["complete"] and n > 0 and 5 * q >= 4 * n
        st[name] = {"n": n, "chain_qualified": q, "scratch_fails": sf, "complete": v["complete"],
                    "chain_ge_80pct": hi, "trivialised": hi and not (5 * sf >= 4 * n),
                    "counts": hi and 5 * sf >= 4 * n,
                    "first_failing_link_counts": v["first_failing_link_counts"]}
    c = {k: st[k]["counts"] for k in st}
    if not all(st[k]["complete"] for k in st):
        label = "INCOMPLETE"
    elif c["on_frozen"] and c["off_xabs"]:
        label = "EITHER"
    elif c["on_frozen"]:
        label = "SEARCH"
    elif c["off_xabs"]:
        label = "DEVELOPMENTAL"
    elif c["on_xabs"]:
        label = "BOTH_REQUIRED"
    else:
        label = "NONE"
    order = ["on_xabs", "on_frozen", "off_xabs", "off_frozen"]       # tie-break for the best cell
    best = max(order, key=lambda k: (st[k]["chain_qualified"], -order.index(k)))
    lk = {k: v for k, v in st[best]["first_failing_link_counts"].items() if k in LINKS}
    nf = sum(lk.values())
    hz = lk.get("HORIZON_R1", 0) + lk.get("COMPOSITION_HORIZON", 0)
    ud = lk.get("UNDERDETERMINED_STONE", 0) + lk.get("COMPOSITION_UNDERDETERMINED", 0)
    dom = (None if nf == 0 else "HORIZON" if 2 * hz > nf else "UNDERDETERMINED" if 2 * ud > nf else "MIXED")
    if label in ("SEARCH", "DEVELOPMENTAL", "BOTH_REQUIRED", "EITHER"):
        rec = "CHANGE_SEARCH_OR_DEVELOPMENTAL_MACHINERY (class %s)" % label
    elif label == "NONE" and dom == "HORIZON":
        rec = "CHANGE_SEARCH (a larger search change is needed)"
    elif label == "NONE" and dom == "UNDERDETERMINED":
        rec = "toward WORLD (foundry identifiability) or MIGRATE; state with the AR-1 result"
    else:
        rec = "no fixed reading (%s / %s)" % (label, dom)
    return {"REPAIR_CLASS": label, "cells": st, "best_cell": best,
            "best_cell_first_failing_links": lk, "best_cell_dominant": dom, "recommendation_reading": rec,
            "rule": "SEARCH: on_frozen counts AND off_xabs not; DEVELOPMENTAL: off_xabs counts AND on_frozen not; "
                    "EITHER: both single-factor cells count; BOTH_REQUIRED: only on_xabs counts; NONE: no cell counts. "
                    "A cell counts iff 5q >= 4n AND 5*scratch_fails >= 4n (else TRIVIALISED if 5q >= 4n); "
                    "CENSORED scratch = not failed (A3.6)"}


def repair_class(root, worlds, out_dir, budget=BUDGET, seed=SEED) -> Dict:
    man = WD.world_manifest(root)
    worlds = worlds or sorted(w for w in man["worlds"] if KP(root, w).admitted())
    cells = {}
    for name, cfg in e3r_cells(budget, seed).items():
        fams = []
        for w in worlds:
            kp = KP(root, w)
            if kp.admitted():
                fams += kp.describe(_load(out_dir, w), cfg)["families"]
        cells[name] = pooled_verdict(fams, primary=False)
        cells[name]["families"] = [{k: f[k] for k in ("world", "family_id", "chain_status", "scratch_status",
                                                      "first_failing_link", "link_detail", "extraction")}
                                   for f in fams]
    res = repair_class_from(cells)
    res.update({"root": str(root), "worlds": worlds, "label": _label(root), "budget": budget, "seed": seed,
                "claim_limits": "informs the recommendation only; no frozen Beta-04 label is relabelled; not "
                                "COMPOSITIONAL_DISCOVERY (stones from sealed-decomposition-indexed R1 tasks)",
                "cell_verdicts": {k: {kk: v[kk] for kk in ("chain_qualified", "scratch_fails", "n_admitted_R3_R4",
                                                          "complete", "first_failing_link_counts")}
                                  for k, v in cells.items()},
                "cell_families": {k: v["families"] for k, v in cells.items()}})
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--world")
    ap.add_argument("--worlds", help="comma list for --pooled (default: every world with admitted R3/R4)")
    ap.add_argument("--stage", choices=["r1", "chain", "scratch", "all"])
    ap.add_argument("--family")
    ap.add_argument("--mech")
    ap.add_argument("--out", default=str(HERE / "runs"))
    ap.add_argument("--verdict", action="store_true", help="per-world DESCRIPTIVE table for the row")
    ap.add_argument("--pooled", action="store_true", help="POOLED verdict over the world set for the row")
    ap.add_argument("--fallback", choices=["on", "off"], default="on")
    ap.add_argument("--given-foundry-primitives", action="store_true")
    ap.add_argument("--all-acquired-library", action="store_true")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--seeds", help="comma list of keyed seeds (e.g. 1,2); one row per seed")
    ap.add_argument("--oe", action="store_true", help="the pre-registered OE repair row (NOT the default)")
    ap.add_argument("--budget", type=int, default=BUDGET, help="development only; the prereg budget is 1e6")
    ap.add_argument("--extract", choices=list(EXTRACT_MODES), default="frozen",
                    help="E3-R: stone extraction (frozen = E3-KP rule; xabs = X-ABS)")
    ap.add_argument("--seed-cache-from", help="E3-R: import the frozen E3-KP cache (searches + primary row) first")
    ap.add_argument("--scratch-cpu-cap", type=float, help="development only: CENSOR a scratch search above this CPU-s")
    ap.add_argument("--repair-class", action="store_true", help="E3-R: pooled REPAIR_CLASS over the 2x2 cells")
    a = ap.parse_args()
    if a.repair_class:
        res = repair_class(a.root, a.worlds.split(",") if a.worlds else None, a.out, a.budget, a.seed)
        p = Path(a.out) / ("E3R_REPAIR_CLASS_seed%d_B%d.json" % (a.seed, a.budget))
        p.write_text(json.dumps(res, indent=1, sort_keys=True))
        print(json.dumps({k: res[k] for k in ("REPAIR_CLASS", "cell_verdicts", "best_cell", "best_cell_dominant",
                                              "recommendation_reading")}, indent=1), flush=True)
        return
    for cfg in configs_from_args(a):
        if a.pooled:
            res = pooled(a.root, a.worlds.split(",") if a.worlds else None, cfg, a.out)
            p = Path(a.out) / ("KPA1_POOLED_%s.json" % cfg.key())
            p.write_text(json.dumps(res, indent=1, sort_keys=True))
            print(json.dumps({"row": cfg.row_name(), **{k: res["verdict"][k] for k in (
                "TFS1_INSTRUMENT_QUALIFIED", "chain_qualified", "scratch_fails", "n_admitted_R3_R4",
                "first_failing_link_counts")}, "A1_C": res.get("A1_C"),
                "oe_repair_trigger": res["verdict"].get("oe_repair_trigger")}), flush=True)
            continue
        if not a.world:
            ap.error("--world is required unless --pooled")
        if a.stage:
            run_stages(a.root, a.world, cfg, a.stage, a.out, a.family, a.mech,
                       log=lambda s: print(cfg.row_name(), s, flush=True), seed_from=a.seed_cache_from,
                       scratch_cpu_cap=a.scratch_cpu_cap)
        if a.verdict or not a.stage:
            kp = KP(a.root, a.world)
            desc = kp.describe(_load(a.out, a.world), cfg)
            print(json.dumps([{k: f[k] for k in ("family_id", "chain_status", "scratch_status", "first_failing_link",
                                                  "link_detail")} for f in desc["families"]], indent=1), flush=True)


if __name__ == "__main__":
    main()
