"""E3 s1: TFS1_INSTRUMENT_QUALIFIED -- the known-positive reachability chain replicated with the INDEPENDENT substrate.

For each admitted R3 / R4 family F (WORLD_MANIFEST id_map status ADMITTED) with constituent mechanisms M(F) (sealed
`mechanisms_used`):
  (i)   for each m in M(F): TFS-1 base keyed enumeration from scratch on m's R1 families (sealed R1 families whose
        mechanisms_used == [m], in family-index order; the next one is tried only if the previous gave no promotable
        mechanism), budget 1e6, stop at the FIRST dev-consistent program, which must then pass test + tribunal
        (evaluator view; no hindsight);
  (ii)  promote the FOUND program's mechanism: the first (pre-order) closed lambda of the mechanism kind's type
        (f: Int->Int, p: Int->Bool, s: Int->Int->Int) whose body references a parameter and not xs (contract v0.1-1),
        alias-collapsed (Library.promote_lambda). No f/p readout fallback (OPEN DECISION KP1);
  (iii) TFS-1 keyed enumeration on F with the library {promoted mechanisms of M(F)}, budget 1e6, first dev-consistent
        program, then the test + tribunal verdict (CHAIN success iff qualified);
  (iv)  from-scratch control: TFS-1 base enumeration on F, budget 1e6 (must NOT produce a qualified program).
TFS1_INSTRUMENT_QUALIFIED = YES iff chain success on >= 80% of admitted R3/R4 families AND scratch fails all of them.
Otherwise TFS1_REACHABILITY_INSTRUMENT = FAIL (no scientific rejection).

Static diagnostics per chain family (no evaluation): promoted-form size of the sealed witness rewritten with the
promoted entries (compress.refactor), and the hitting-cost bracket (cumulative(n-1), cumulative(n)] of its size class.

Each stage item runs in its own process (<= 15 CPU-min) and is cached in <out>/KP_<world>.json:
  python -m tfs1.e3.e3_known_positive --root <pilot_dir> --world W --stage r1|chain|scratch|all [--family FID] [--mech m]
  python -m tfs1.e3.e3_known_positive --root <pilot_dir> --world W --verdict
"""
import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional

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


def extract_mechanism(program: str, kind: str, lib=None) -> Optional[tuple]:
    """Returns (lambda, how) or None. how = 'closed_lambda' | 'readout_fallback'."""
    t = C.parse(program)
    want = KIND_TYPE[kind]
    for lam, ty in lambdas_in(t, 0, lib):
        if ty == want and body_refs_param(lam) and not references_xs(lam) and C.size(lam[2]) >= 2:
            return lam, "closed_lambda"
    lam = readout_fallback(t, kind)
    return (lam, "readout_fallback") if lam is not None else None


def _search(task, lib, budget=BUDGET, seed=SEED):
    E = Enumerator(lib)
    t0 = time.process_time()
    r = E.search(task["dev"], task["output_type"], seed, task["family_id"], budget, MAX_SIZE)
    r["cpu_s"] = round(time.process_time() - t0, 2)
    r["class_sizes"] = {n: E.count(task["output_type"], (), n) for n in range(1, 9)}
    del E
    return r


def _cache_path(out_dir, world):
    return Path(out_dir) / ("KP_%s.json" % world)


def _load(out_dir, world):
    p = _cache_path(out_dir, world)
    return json.loads(p.read_text()) if p.exists() else {"world": world, "r1": {}, "chain": {}, "scratch": {}}


def _save(out_dir, world, d):
    p = _cache_path(out_dir, world)
    p.parent.mkdir(parents=True, exist_ok=True)
    d["code_sha256"] = code_hashes()
    p.write_text(json.dumps(d, indent=1, sort_keys=True))


class KP:
    def __init__(self, root, world):
        self.root, self.world = Path(root), world
        self.ev = WD.Evaluator(root, world)
        self.sealed = WD.sealed(root, world)
        self.mech = {m["name"]: m for m in self.sealed["mechanisms"]}
        self.fams = {f["family_id"]: f for f in self.sealed["families"]}
        self.by_fid = {m["family_id"]: o for o, m in self.ev.id_map.items()}

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

    # ---- (i) + (ii)
    def run_r1(self, m) -> Dict:
        attempts = []
        for fid in self.r1_families(m):
            task = self.task(fid)
            r = _search(task, None)
            row = {"family_id": fid, "found": r["program"], "charge": r["hit_charge"], "charges": r["charges"],
                   "cpu_s": r["cpu_s"], "complete_through_size": r["complete_through_size"]}
            if r["hit"]:
                row["verdict"] = WD.judge(r["program"], task)
                if row["verdict"]["qualified"]:
                    ex = extract_mechanism(r["program"], self.mech[m]["kind"])
                    row["mechanism_lambda"] = C.to_str(ex[0]) if ex is not None else None
                    row["extraction"] = ex[1] if ex is not None else None
            attempts.append(row)
            if row.get("mechanism_lambda"):
                return {"mechanism": m, "kind": self.mech[m]["kind"], "status": "ACQUIRED",
                        "lambda": row["mechanism_lambda"], "extraction": row["extraction"], "from": fid,
                        "agrees_with_sealed_on_probe": self.agree_sealed(m, row["mechanism_lambda"]),
                        "attempts": attempts}
        return {"mechanism": m, "kind": self.mech[m]["kind"], "status": "NOT_ACQUIRED", "attempts": attempts}

    def agree_sealed(self, m, lam_text) -> float:
        """Diagnostic only: share of probe arguments on which the acquired lambda equals the sealed mechanism."""
        a, b = C.parse(lam_text), C.parse(self.mech[m]["term"])
        k = a[1]
        vals = list(range(-40, 41))
        args = [(v,) for v in vals] if k == 1 else [(u, v) for u in vals[::4] for v in vals[::4]]
        same = 0
        for xs in args:
            ra = C.evaluate(("app", a) + tuple(("int", v) for v in xs), [])[0]
            rb = C.evaluate(("app", b) + tuple(("int", v) for v in xs), [])[0]
            same += C.same_value(ra, rb)
        return round(same / len(args), 4)

    def library_for(self, fid, r1: Dict) -> Optional[Library]:
        lib = Library(closed_args=True)
        for m in self.constituents(fid):
            rec = r1.get(m)
            if rec is None or rec["status"] != "ACQUIRED":
                return None
            lib.promote_lambda(C.parse(rec["lambda"]), {"mechanism_slot": m, "from": rec["from"],
                                                        "procedure": "E3 s1 (ii)"})
        return lib

    # ---- (iii)
    def run_chain(self, fid, r1: Dict) -> Dict:
        lib = self.library_for(fid, r1)
        task = self.task(fid)
        if lib is None:
            return {"family_id": fid, "status": "CHAIN_C_FAIL",
                    "missing": [m for m in self.constituents(fid) if r1.get(m, {}).get("status") != "ACQUIRED"]}
        diag = self.static_diag(fid, lib)
        r = _search(task, lib)
        row = {"family_id": fid, "rung": self.fams[fid]["rung"], "library": lib.to_json(),
               "found": r["program"], "charge": r["hit_charge"], "charges": r["charges"], "cpu_s": r["cpu_s"],
               "complete_through_size": r["complete_through_size"], "units_expanded": r["units_expanded"],
               "units_promoted": r["units_promoted"], "static": diag}
        if r["hit"]:
            row["verdict"] = WD.judge(r["program"], task, lib)
            row["uses_library"] = C.has_call(C.parse(r["program"]))
            row["status"] = "SOLVED" if row["verdict"]["qualified"] else "FIRST_DEV_CONSISTENT_FAILS_TEST"
        else:
            row["status"] = "NOT_FOUND_AT_BUDGET"
        return row

    def static_diag(self, fid, lib) -> Dict:
        w = C.parse(self.task(fid)["witness"])
        rw = CP.refactor(w, lib)
        E = Enumerator(lib)
        T = self.task(fid)["output_type"]
        n = C.size(rw)
        out = {"witness": C.to_str(w), "witness_refactored": C.to_str(rw), "size_promoted_form": n,
               "uses_entries": sorted(set(C.calls_in(rw))),
               "hitting_cost_bracket": [E.cumulative(T, n - 1) + 1, E.cumulative(T, n)]}
        return out

    # ---- (iv)
    def run_scratch(self, fid) -> Dict:
        task = self.task(fid)
        r = _search(task, None)
        row = {"family_id": fid, "found": r["program"], "charge": r["hit_charge"], "charges": r["charges"],
               "cpu_s": r["cpu_s"], "complete_through_size": r["complete_through_size"]}
        if r["hit"]:
            row["verdict"] = WD.judge(r["program"], task)
            row["status"] = "SOLVED_FROM_SCRATCH" if row["verdict"]["qualified"] else "FIRST_DEV_CONSISTENT_FAILS_TEST"
        else:
            row["status"] = "NOT_FOUND_AT_BUDGET"
        return row


def verdict(d: Dict, admitted: List[str]) -> Dict:
    n = len(admitted)
    ok = [f for f in admitted if d["chain"].get(f, {}).get("status") == "SOLVED"]
    done_chain = [f for f in admitted if f in d["chain"]]
    done_scr = [f for f in admitted if f in d["scratch"]]
    scratch_solves = [f for f in admitted if d["scratch"].get(f, {}).get("status") == "SOLVED_FROM_SCRATCH"]
    complete = len(done_chain) == n and len(done_scr) == n
    frac = len(ok) / n if n else None
    q = complete and n > 0 and frac >= 0.8 and not scratch_solves
    return {"admitted_R3_R4": n, "chain_solved": len(ok), "chain_fraction": frac,
            "scratch_solved": len(scratch_solves), "complete": complete,
            "TFS1_INSTRUMENT_QUALIFIED_world": ("YES" if q else ("INCOMPLETE" if not complete else "NO")),
            "rule": ">= 80% chain success AND from-scratch fails every admitted R3/R4 family (1e6 each)"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--world", required=True)
    ap.add_argument("--stage", choices=["r1", "chain", "scratch", "all"])
    ap.add_argument("--family")
    ap.add_argument("--mech")
    ap.add_argument("--out", default=str(HERE / "runs"))
    ap.add_argument("--verdict", action="store_true")
    a = ap.parse_args()
    kp = KP(a.root, a.world)
    d = _load(a.out, a.world)
    adm = kp.admitted()
    d["admitted"] = adm
    d["label"] = "EXPOSED DEV DATA (pilot_v2)" if "pilot" in a.root else "PRODUCTION"
    needed = sorted({m for f in adm for m in kp.constituents(f)})
    if a.stage in ("r1", "all"):
        for m in ([a.mech] if a.mech else needed):
            if m not in d["r1"]:
                d["r1"][m] = kp.run_r1(m)
                _save(a.out, a.world, d)
                print("r1", m, d["r1"][m]["status"], d["r1"][m].get("lambda"), flush=True)
    if a.stage in ("chain", "all"):
        for f in ([a.family] if a.family else adm):
            if f not in d["chain"]:
                d["chain"][f] = kp.run_chain(f, d["r1"])
                _save(a.out, a.world, d)
                print("chain", f, d["chain"][f]["status"], d["chain"][f].get("charge"), flush=True)
    if a.stage in ("scratch", "all"):
        for f in ([a.family] if a.family else adm):
            if f not in d["scratch"]:
                d["scratch"][f] = kp.run_scratch(f)
                _save(a.out, a.world, d)
                print("scratch", f, d["scratch"][f]["status"], flush=True)
    d["verdict"] = verdict(d, adm)
    _save(a.out, a.world, d)
    print(json.dumps(d["verdict"]))


if __name__ == "__main__":
    main()
