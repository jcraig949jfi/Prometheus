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
PROBE_NARROW = list(range(-40, 41))
PROBE_WIDE = list(range(-200, 201, 3))


# ================================================================ rows
class Config:
    def __init__(self, fallback: bool = True, source: str = "tfs1", scope: str = "constituents", seed: int = SEED,
                 oe: bool = False, budget: int = BUDGET):
        assert source in ("tfs1", "foundry") and scope in ("constituents", "all")
        self.fallback, self.source, self.scope = bool(fallback), source, scope
        self.seed, self.oe, self.budget = int(seed), bool(oe), int(budget)

    def key(self) -> str:
        return "fb%d.src-%s.lib-%s.seed%d.oe%d.B%d" % (self.fallback, self.source, self.scope, self.seed, self.oe,
                                                       self.budget)

    def to_json(self) -> Dict:
        return {"fallback": self.fallback, "source": self.source, "scope": self.scope, "seed": self.seed,
                "oe": self.oe, "budget": self.budget, "key": self.key(), "row": self.row_name()}

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


def extract_mechanism(program: str, kind: str, lib=None, fallback: bool = True) -> Optional[tuple]:
    """Returns (lambda, how) or None. how = 'closed_lambda' | 'readout_fallback' (only if fallback=True)."""
    t = C.parse(program)
    want = KIND_TYPE[kind]
    for lam, ty in lambdas_in(t, 0, lib):
        if ty == want and body_refs_param(lam) and not references_xs(lam) and C.size(lam[2]) >= 2:
            return lam, "closed_lambda"
    if not fallback:
        return None
    lam = readout_fallback(t, kind)
    return (lam, "readout_fallback") if lam is not None else None


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
                    ex = extract_mechanism(r["program"], kind, fallback=cfg.fallback)
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
                "scratch_fails": None if sc is None else sc["status"] != "SOLVED_FROM_SCRATCH",
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
def run_stages(root, world, cfg: Config, stage: str, out_dir, family=None, mech=None, log=print) -> Dict:
    kp = KP(root, world)
    d = _load(out_dir, world)
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
                row["scratch"][f] = kp.run_scratch(d, f, cfg)
                _save(out_dir, world, d)
                log("scratch %s %s" % (f, row["scratch"][f]["status"]))
    row["descriptive"] = kp.describe(d, cfg)
    _save(out_dir, world, d)
    return d


def configs_from_args(a) -> List[Config]:
    seeds = [int(s) for s in a.seeds.split(",")] if a.seeds else [a.seed]
    return [Config(fallback=(a.fallback == "on"), source="foundry" if a.given_foundry_primitives else "tfs1",
                   scope="all" if a.all_acquired_library else "constituents", seed=s, oe=a.oe, budget=a.budget)
            for s in seeds]


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
    a = ap.parse_args()
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
                       log=lambda s: print(cfg.row_name(), s, flush=True))
        if a.verdict or not a.stage:
            kp = KP(a.root, a.world)
            desc = kp.describe(_load(a.out, a.world), cfg)
            print(json.dumps([{k: f[k] for k in ("family_id", "chain_status", "scratch_status", "first_failing_link",
                                                  "link_detail")} for f in desc["families"]], indent=1), flush=True)


if __name__ == "__main__":
    main()
