"""AR-1 KP: the E3-KP known-positive causal chain run in AR-1's NATIVE terms (Beta-04 Experiment E, exploratory).

Same families, same given decomposition, same budget and the same first-dev-consistent rule as E3-KP
(tfs1/e3/e3_known_positive.py; prereg windows/E2_E3KP_PREREG.md s A + A1-A + A3); only the representation (AR-1
stack-tape machine), the search (MC-1 mutation chain) and the unit (a tape SEGMENT promoted to a macro token, rule X1)
differ. It is an INSTRUMENT TEST GIVEN THE DECOMPOSITION, never discovery evidence, and it carries NO gate.

Per admitted R3/R4 family F with constituent mechanisms M(F) (WORLD_SEALED mechanisms_used):
  (i)   ACQUISITION UNIT (world, m): MC-1 from the empty tape, budget 1e6, no macros, on m's R1 families in family
        index order; the FIRST dev-consistent tape is judged on test + tribunal; the next R1 family is tried only if
        no unit results (certifier-guided retry, as E3-KP; `certifier_assisted_retry` reported).
  (ii)  EXTRACTION X1 (alien/extract.py; target-blind; dev only + kind) -> macro '@u<sha8>'.
  (iii) CHAIN: MC-1 on F with the alphabet = base + the macros of M(F), budget 1e6; first dev-consistent tape judged.
  (iv)  SCRATCH: MC-1 on F, base alphabet only, budget 1e6.
The search sees ONLY the arm-view dev examples (tfs1.e3.worlds.ArmWorld; every file opened during a search is logged
by AccessLog and must lie under <root>/arm_view). Judging (test + tribunal) is coordinator side, with the AR-1
interpreter, value-or-FAIL.

FIRST FAILING LINK (the E3-KP labels, AR-1 reading; AR1_DESIGN.md s6):
  R1 attempt: hit & not qualified -> UNDERDETERMINED_STONE (R1_FIRST_DEV_CONSISTENT_FAILS_TEST);
              hit & qualified & X1 finds no segment -> R1_ACQUISITION (NO_EXTRACTABLE_UNIT);
              no hit within budget -> HORIZON_R1 (BUDGET_EXHAUSTED; best dev credit reported).
  Family: 1 a unit NOT_ACQUIRED -> its first attempt's label; 2 chain qualified -> CHAIN_QUALIFIED;
          3 a unit disagrees with the sealed mechanism on the probe frame -> UNDERDETERMINED_STONE
            (STONE_DISAGREES_SEALED_PROBES); 4 chain first dev-consistent fails test/tribunal ->
          COMPOSITION_UNDERDETERMINED; 5 chain no hit -> COMPOSITION_HORIZON (BUDGET_EXHAUSTED).
  A chain is not exhaustive, so the E3-KP sub-labels IN_CLASS / CLASS_NOT_ENTERED and WITNESS_CLASS_COMPLETED_NO_HIT
  have no AR-1 analogue.
GIVEN-TRUE-STONES row: NOT_DEFINABLE (a 'true' AR-1 stone needs a translation of the sealed lambda into a tape).
SECONDARY ROWS: --seed s (all stages re-keyed); --r1-seeds K (R1 acquisition retried over MC-1 seeds 0..K-1 for each R1
family, family-major, first qualified + extractable wins: CERTIFIER-ASSISTED, the native lambda-free way to give the
composition step working stones; chain / scratch use --seed).

Commands (from roles/Aphrodite/beta04, OMP_NUM_THREADS=1, ONE process at a time):
  python -m alien.ar1_kp --root foundry/<set> --world W --stage r1|chain|scratch|all [--seed s] [--cpu-cap 840]
  python -m alien.ar1_kp --root foundry/<set> --pooled [--worlds W1,W2] [--seed s]
Exit code 3 = the process stopped at its CPU cap before the stage finished (re-invoke; the cache resumes).
"""
import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

os.environ.setdefault("OMP_NUM_THREADS", "1")

from tfs1 import core as C                         # noqa: E402  (sealed-mechanism probes only; coordinator side)
from tfs1.e3 import worlds as WD                   # noqa: E402
from alien import machine as M                     # noqa: E402
from alien import search as S                      # noqa: E402
from alien import extract as X                     # noqa: E402

HERE = Path(__file__).resolve().parent
BUDGET = S.BUDGET
SEED = 0
LINKS = ("R1_ACQUISITION", "UNDERDETERMINED_STONE", "HORIZON_R1", "COMPOSITION_HORIZON",
         "COMPOSITION_UNDERDETERMINED")
PROBE_NARROW = list(range(-40, 41))
PROBE_WIDE = list(range(-200, 201, 3))
SEARCH_CPU_EST = 300.0          # pessimistic CPU-s of one censored 1e6 search (pilot-measured: ~120-200 s)


class CpuCap(Exception):
    pass


class Config:
    def __init__(self, seed: int = SEED, scope: str = "constituents", budget: int = BUDGET, r1_seeds: int = 1):
        assert scope in ("constituents", "all") and r1_seeds >= 1
        self.seed, self.scope, self.budget, self.r1_seeds = int(seed), scope, int(budget), int(r1_seeds)

    def key(self) -> str:
        k = "ar1.mc1.lib-%s.seed%d.B%d" % (self.scope, self.seed, self.budget)
        return k + (".r1seeds%d" % self.r1_seeds if self.r1_seeds > 1 else "")

    def row_name(self) -> str:
        d = []
        if self.scope == "all":
            d.append("all_acquired")
        if self.seed != SEED:
            d.append("seed%d" % self.seed)
        if self.budget != BUDGET:
            d.append("B%d" % self.budget)
        if self.r1_seeds > 1:
            d.append("r1_multiseed%d" % self.r1_seeds)
        return "+".join(d) if d else "primary"

    def to_json(self):
        return {"seed": self.seed, "scope": self.scope, "budget": self.budget, "r1_seeds": self.r1_seeds,
                "key": self.key(), "row": self.row_name()}


PRIMARY = Config()


# ================================================================ coordinator-side judge (AR-1 interpreter)
def _agree(prog, examples, out_type) -> bool:
    for i, o in examples:
        if not M.same_value(M.run_compiled(prog, list(i), out_type), o):
            return False
    return True


def judge(program: str, task: Dict, macros=None) -> Dict:
    prog = M.compile_tape(M.parse(program), macros)
    T = task["output_type"]
    test_ok = _agree(prog, task["test"], T)
    trib = task.get("tribunal", [])
    trib_ok = _agree(prog, trib, T) if trib else None
    return {"test_ok": test_ok, "tribunal_ok": trib_ok, "qualified": bool(test_ok and trib_ok is not False),
            "n_test": len(task["test"]), "n_tribunal": len(trib)}


def tape_cost(program: str, macros, dev, out_type) -> Dict:
    """Both ledgers: promoted / expanded tape length and execution units summed over dev."""
    t = M.parse(program)

    def expand(tt):
        out = []
        for tok in tt:
            out += expand(macros[tok]) if M.is_macro(tok) else [tok]
        return out
    led = [0, 0]
    prog = M.compile_tape(t, macros)
    for xs, _y in dev:
        M.run_compiled(prog, xs, out_type, led)
    return {"len_promoted": len(t), "len_expanded": len(expand(t)), "units_expanded_dev": led[0],
            "units_promoted_dev": led[1], "macro_calls": sum(M.is_macro(x) for x in t)}


# ================================================================ cache
def _cache_path(out_dir, world):
    return Path(out_dir) / ("AR1_%s.json" % world)


def _load(out_dir, world) -> Dict:
    p = _cache_path(out_dir, world)
    d = json.loads(p.read_text()) if p.exists() else {}
    d.setdefault("world", world)
    d.setdefault("searches", {})
    d.setdefault("rows", {})
    return d


def code_hashes() -> Dict[str, str]:
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.glob("*.py"))}


def _save(out_dir, world, d):
    p = _cache_path(out_dir, world)
    p.parent.mkdir(parents=True, exist_ok=True)
    d["alien_code_sha256"] = code_hashes()
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, indent=1, sort_keys=True))
    os.replace(tmp, p)


def _label(root) -> str:
    return "EXPOSED DEV DATA (pilot)" if "pilot" in str(root) else "PRODUCTION"


# ================================================================ the procedure for one world
class AR1KP:
    def __init__(self, root, world, cpu_cap: Optional[float] = None):
        self.root, self.world = Path(root), world
        self.ev = WD.Evaluator(root, world)
        self.sealed = WD.sealed(root, world)
        self.mech = {m["name"]: m for m in self.sealed["mechanisms"]}
        self.fams = {f["family_id"]: f for f in self.sealed["families"]}
        self.by_fid = {m["family_id"]: o for o, m in self.ev.id_map.items()}
        self.arm_world = WD.world_manifest(root)["worlds"][world]["arm_world"]
        self.aw = None
        self.cpu_cap = cpu_cap

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
            need |= {m for m in self.mech if self.r1_families(m)}
        return sorted(need)

    # ---- the search: arm-view dev only, access-logged
    def search(self, d, fid, macros, cfg: Config) -> Dict:
        k = "%s|seed=%d|lib=%s|B=%d|mc1" % (fid, cfg.seed, S.lib_sha(macros), cfg.budget)
        if k in d["searches"]:
            return d["searches"][k]
        if self.cpu_cap is not None and time.process_time() + SEARCH_CPU_EST > self.cpu_cap:
            raise CpuCap(k)
        log = WD.AccessLog()
        with log.active():
            if self.aw is None:
                self.aw = WD.ArmWorld(self.root, self.arm_world)
            fam = self.aw.family(self.by_fid[fid])
            r = S.chain(fam["dev"], fam["output_type"], fam["slot"], cfg.seed, cfg.budget, macros)
        outside = log.outside(self.root / "arm_view")
        if outside:
            raise RuntimeError("information boundary violated during search: %s" % outside[:3])
        r["arm_view_files_opened"] = len(log.paths)
        r["output_type"] = fam["output_type"]
        if r["hit"]:
            task = self.task(fid)
            r["verdict"] = judge(r["program"], task, macros)
            r["cost"] = tape_cost(r["program"], macros or {}, task["dev"], task["output_type"])
        d["searches"][k] = r
        return r

    # ---- probes (diagnostic only; never select a unit)
    def agree_sealed(self, m, segment: str, vals=None) -> float:
        kind = self.mech[m]["kind"]
        lam = C.parse(self.mech[m]["term"])
        vals = PROBE_NARROW if vals is None else vals
        seg = M.parse(segment)
        args = [(v,) for v in vals] if kind in ("f", "p") else [(u, v) for u in vals[::4] for v in vals[::4]]
        sealed = [C.evaluate(("app", lam) + tuple(("int", v) for v in a), [])[0] for a in args]
        exc = getattr(C, "_FAIL_EXC", None)
        if exc is not None:
            exc.__traceback__ = None
        best = 0.0
        for swap in ((False, True) if kind == "s" else (False,)):      # P-A1: s-kind max over the two bindings
            same = sum(M.same_value(rs, X.unit_value(seg, kind, a, None, swap)) for rs, a in zip(sealed, args))
            best = max(best, same / len(args))
        return round(best, 4)

    # ---- (i) + (ii)
    def run_unit(self, d, m, cfg: Config) -> Dict:
        kind = self.mech[m]["kind"]
        attempts = []
        tries = [(fid, s) for fid in self.r1_families(m)
                 for s in ([cfg.seed] if cfg.r1_seeds == 1 else range(cfg.r1_seeds))]
        for fid, s in tries:
            r = self.search(d, fid, None, Config(s, cfg.scope, cfg.budget))
            row = {"family_id": fid, "r1_seed": s, "found": r["program"], "charge": r["hit_charge"], "charges": r["charges"],
                   "cpu_s": r["cpu_s"], "best_credit": r["best_credit"], "n_dev": r["n_dev"],
                   "restarts": r["restarts"]}
            if r["hit"]:
                row["verdict"] = r["verdict"]
                if not r["verdict"]["qualified"]:
                    row["label"], row["detail"] = "UNDERDETERMINED_STONE", "R1_FIRST_DEV_CONSISTENT_FAILS_TEST"
                else:
                    task = self.task(fid)
                    dev = self.aw.family(self.by_fid[fid])["dev"] if self.aw else task["dev"]
                    ex = X.extract(M.parse(r["program"]), dev, r["output_type"], kind)
                    row["minimised"] = ex["minimised"]
                    row["minimised_verdict"] = judge(ex["minimised"], task)
                    row["n_candidates"] = ex["n_candidates"]
                    if ex["segment"] is None:
                        row["label"], row["detail"] = "R1_ACQUISITION", "NO_EXTRACTABLE_UNIT"
                    else:
                        row.update({"label": None, "detail": "ACQUIRED", "segment": ex["segment"],
                                    "span": ex["span"]})
            else:
                row["label"], row["detail"] = "HORIZON_R1", "BUDGET_EXHAUSTED"
                row["best_tape"] = r.get("best_tape")
            attempts.append(row)
            if row["detail"] == "ACQUIRED":
                seg = row["segment"]
                return {"mechanism": m, "kind": kind, "status": "ACQUIRED", "segment": seg, "r1_seed": row["r1_seed"],
                        "macro": X.macro_name(seg), "from": fid, "n_attempts": len(attempts),
                        "certifier_assisted_retry": any(a.get("detail") == "R1_FIRST_DEV_CONSISTENT_FAILS_TEST"
                                                        for a in attempts[:-1]),
                        "agrees_with_sealed_on_probe": self.agree_sealed(m, seg),
                        "agrees_with_sealed_wide": self.agree_sealed(m, seg, PROBE_WIDE),
                        "attempts": attempts}
        first = attempts[0] if attempts else {"label": "R1_ACQUISITION", "detail": "NO_R1_FAMILY"}
        return {"mechanism": m, "kind": kind, "status": "NOT_ACQUIRED", "n_attempts": len(attempts),
                "certifier_assisted_retry": any(a.get("detail") == "R1_FIRST_DEV_CONSISTENT_FAILS_TEST"
                                                for a in attempts[:-1]),
                "link": first["label"], "link_detail": first["detail"],
                "attempt_labels": [a["label"] for a in attempts], "attempts": attempts}

    # ---- library for (iii)
    def macros_for(self, fid, units: Dict, cfg: Config) -> Tuple[Optional[Dict], Dict]:
        for m in self.constituents(fid):
            if units.get(m, {}).get("status") != "ACQUIRED":
                return None, {}
        ms = self.constituents(fid) if cfg.scope == "constituents" else \
            sorted(m for m, u in units.items() if u.get("status") == "ACQUIRED")
        macros, slot = {}, {}
        for m in ms:
            u = units[m]
            macros[u["macro"]] = M.parse(u["segment"])
            slot[m] = u["macro"]
        return macros, slot

    # ---- (iii)
    def run_chain(self, d, fid, units: Dict, cfg: Config) -> Dict:
        macros, slot = self.macros_for(fid, units, cfg)
        if macros is None:
            return {"family_id": fid, "status": "CHAIN_C_FAIL",
                    "missing": [m for m in self.constituents(fid) if units.get(m, {}).get("status") != "ACQUIRED"]}
        r = self.search(d, fid, macros, cfg)
        row = {"family_id": fid, "rung": self.fams[fid]["rung"],
               "macros": {k: M.to_str(v) for k, v in macros.items()}, "slot": slot,
               "found": r["program"], "charge": r["hit_charge"], "charges": r["charges"], "cpu_s": r["cpu_s"],
               "best_credit": r["best_credit"], "n_dev": r["n_dev"], "restarts": r["restarts"]}
        if r["hit"]:
            row["verdict"] = r["verdict"]
            row["cost"] = r["cost"]
            row["uses_macro"] = r["cost"]["macro_calls"] > 0
            row["status"] = "SOLVED" if r["verdict"]["qualified"] else "FIRST_DEV_CONSISTENT_FAILS_TEST"
        else:
            row["status"] = "NOT_FOUND_AT_BUDGET"
            row["best_tape"] = r.get("best_tape")
        return row

    # ---- (iv)
    def run_scratch(self, d, fid, cfg: Config) -> Dict:
        r = self.search(d, fid, None, cfg)
        row = {"family_id": fid, "found": r["program"], "charge": r["hit_charge"], "charges": r["charges"],
               "cpu_s": r["cpu_s"], "best_credit": r["best_credit"], "n_dev": r["n_dev"]}
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
                return {"link": u["link"], "detail": u["link_detail"], "unit": m}
        if chain is None:
            return {"link": None, "detail": "INCOMPLETE"}
        disagree = [m for m in cons if units[m].get("agrees_with_sealed_on_probe", 1.0) < 1.0]
        if chain["status"] == "SOLVED":
            return {"link": None, "detail": "CHAIN_QUALIFIED", "stone_disagrees_sealed": disagree,
                    "uses_macro": chain.get("uses_macro")}
        if disagree:
            return {"link": "UNDERDETERMINED_STONE", "detail": "STONE_DISAGREES_SEALED_PROBES", "units": disagree}
        if chain["status"] == "FIRST_DEV_CONSISTENT_FAILS_TEST":
            return {"link": "COMPOSITION_UNDERDETERMINED", "detail": "CHAIN_FIRST_DEV_CONSISTENT_FAILS_TEST"}
        return {"link": "COMPOSITION_HORIZON", "detail": "BUDGET_EXHAUSTED",
                "best_credit": chain.get("best_credit"), "n_dev": chain.get("n_dev")}

    def describe(self, d, cfg: Config) -> Dict:
        row = d.get("rows", {}).get(cfg.key(), {})
        units, chain, scratch = row.get("units", {}), row.get("chain", {}), row.get("scratch", {})
        fams = []
        for fid in self.admitted():
            ln = self.family_link(fid, units, chain.get(fid))
            sc, ch = scratch.get(fid), chain.get(fid)
            r1_cpu = sum(a.get("cpu_s", 0) or 0 for m in self.constituents(fid)
                         for a in units.get(m, {}).get("attempts", []))
            fams.append({
                "world": self.world, "family_id": fid, "rung": self.fams[fid]["rung"],
                "skeleton": self.fams[fid].get("skeleton"), "constituents": self.constituents(fid),
                "chain_status": ch["status"] if ch else None, "chain_qualified": bool(ch and ch["status"] == "SOLVED"),
                "chain_uses_macro": (ch or {}).get("uses_macro"), "chain_found": (ch or {}).get("found"),
                "scratch_status": sc["status"] if sc else None,
                "scratch_fails": None if sc is None else sc["status"] != "SOLVED_FROM_SCRATCH",
                "complete": ch is not None and sc is not None and all(m in units for m in self.constituents(fid)),
                "first_failing_link": ln["link"], "link_detail": ln["detail"], "link_info": ln,
                "cpu_s": {"r1_units_attributed": round(r1_cpu, 2), "chain": (ch or {}).get("cpu_s", 0.0),
                          "scratch": (sc or {}).get("cpu_s", 0.0)}})
        unit_rows = [{"world": self.world, "mechanism": m, "kind": u.get("kind"), "status": u.get("status"),
                      "link": u.get("link"), "link_detail": u.get("link_detail"), "from": u.get("from"),
                      "segment": u.get("segment"), "macro": u.get("macro"), "n_attempts": u.get("n_attempts"),
                      "certifier_assisted_retry": u.get("certifier_assisted_retry"),
                      "agrees_with_sealed_on_probe": u.get("agrees_with_sealed_on_probe"),
                      "agrees_with_sealed_wide": u.get("agrees_with_sealed_wide"),
                      "r1_seed": u.get("r1_seed"),
                      "attempts": [{k: a.get(k) for k in ("family_id", "r1_seed", "found", "minimised", "label", "detail",
                                                          "charge", "cpu_s", "best_credit")}
                                   for a in u.get("attempts", [])],
                      "cpu_s": round(sum(a.get("cpu_s", 0) or 0 for a in u.get("attempts", [])), 2)}
                     for m, u in sorted(units.items())]
        return {"world": self.world, "row": cfg.to_json(), "families": fams, "units": unit_rows}


# ================================================================ pooled readout (exploratory; no gate)
def pooled_readout(families: List[Dict]) -> Dict:
    n = len(families)
    complete = n > 0 and all(f["complete"] for f in families)
    q = sum(f["chain_qualified"] for f in families)
    sf = sum(bool(f["scratch_fails"]) for f in families)
    failing = [f for f in families if not f["chain_qualified"]]
    links = {k: sum(f["first_failing_link"] == k for f in failing) for k in LINKS}
    links["INCOMPLETE"] = sum(f["first_failing_link"] is None and not f["chain_qualified"] for f in failing)
    top = max(LINKS, key=lambda k: (links[k], -LINKS.index(k))) if failing else None
    parity = "INCOMPLETE" if not complete else ("YES" if (5 * q >= 4 * n and 5 * sf >= 4 * n) else "NO")
    return {"n_admitted_R3_R4": n, "chain_qualified": q, "scratch_fails": sf, "complete": complete,
            "AR1_KP_PARITY": parity,
            "rule": "the E3-KP pooled rule applied to AR-1 (>= 80% chain-qualified AND >= 80% scratch fails); "
                    "EXPLORATORY readout, no gate",
            "chain_qualified_using_macro": sum(bool(f["chain_qualified"] and f["chain_uses_macro"]) for f in families),
            "first_failing_link_counts": links, "dominant_link_plurality": top}


def pooled(root, worlds: Optional[List[str]], cfg: Config, out_dir) -> Dict:
    man = WD.world_manifest(root)
    worlds = worlds or sorted(man["worlds"])
    fams, units = [], []
    for w in worlds:
        kp = AR1KP(root, w)
        if not kp.admitted():
            continue
        desc = kp.describe(_load(out_dir, w), cfg)
        fams += desc["families"]
        units += desc["units"]
    return {"row": cfg.to_json(), "root": str(root), "worlds": worlds, "label": _label(root),
            "claim_limits": "EXPLORATORY alien-representation reserve; INSTRUMENT TEST GIVEN THE DECOMPOSITION; "
                            "motif-limited admitted R3/R4 set; not discovery evidence; no gate",
            "given_true_stones_row": "NOT_DEFINABLE (needs a lambda -> tape translation)",
            "readout": pooled_readout(fams), "families": fams, "units": units}


# ================================================================ stages
def run_stages(root, world, cfg: Config, stage: str, out_dir, cpu_cap=None, log=print) -> int:
    kp = AR1KP(root, world, cpu_cap)
    d = _load(out_dir, world)
    adm = kp.admitted()
    d["admitted"], d["label"] = adm, _label(root)
    r = d["rows"].setdefault(cfg.key(), {})
    r["config"] = cfg.to_json()
    for k in ("units", "chain", "scratch"):
        r.setdefault(k, {})
    try:
        if stage in ("r1", "chain", "all"):
            for m in kp.needed_units(cfg):
                if m not in r["units"]:
                    r["units"][m] = kp.run_unit(d, m, cfg)
                    _save(out_dir, world, d)
                    u = r["units"][m]
                    log("unit %s %s %s %s" % (m, u["status"], u.get("segment"), u.get("link")))
        if stage in ("chain", "all"):
            for f in adm:
                if f not in r["chain"]:
                    r["chain"][f] = kp.run_chain(d, f, r["units"], cfg)
                    _save(out_dir, world, d)
                    log("chain %s %s %s %s" % (f, r["chain"][f]["status"], r["chain"][f].get("charge"),
                                               r["chain"][f].get("found")))
        if stage in ("scratch", "all"):
            for f in adm:
                if f not in r["scratch"]:
                    r["scratch"][f] = kp.run_scratch(d, f, cfg)
                    _save(out_dir, world, d)
                    log("scratch %s %s" % (f, r["scratch"][f]["status"]))
    except CpuCap as e:
        _save(out_dir, world, d)
        log("CPU cap reached before search %s; re-invoke to resume" % e)
        return 3
    r["descriptive"] = kp.describe(d, cfg)
    _save(out_dir, world, d)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--world")
    ap.add_argument("--worlds")
    ap.add_argument("--stage", choices=["r1", "chain", "scratch", "all"])
    ap.add_argument("--out")
    ap.add_argument("--pooled", action="store_true")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--all-acquired-library", action="store_true")
    ap.add_argument("--budget", type=int, default=BUDGET)
    ap.add_argument("--r1-seeds", type=int, default=1, help="secondary row: R1 acquisition retried over seeds "
                    "0..K-1 per R1 family (certifier-assisted); chain / scratch keep --seed")
    ap.add_argument("--cpu-cap", type=float, default=840.0, help="per-process CPU-s guard (lead build rule)")
    a = ap.parse_args()
    out = a.out or str(HERE / "runs" / Path(a.root).name)
    cfg = Config(a.seed, "all" if a.all_acquired_library else "constituents", a.budget, a.r1_seeds)
    if a.pooled:
        res = pooled(a.root, a.worlds.split(",") if a.worlds else None, cfg, out)
        p = Path(out) / ("AR1_POOLED_%s.json" % cfg.key())
        p.write_text(json.dumps(res, indent=1, sort_keys=True))
        print(json.dumps({"row": cfg.row_name(), **res["readout"]}), flush=True)
        return 0
    if not a.world or not a.stage:
        ap.error("--world and --stage are required unless --pooled")
    return run_stages(a.root, a.world, cfg, a.stage, out, a.cpu_cap,
                      log=lambda s: print(cfg.row_name(), a.world, s, flush=True))


if __name__ == "__main__":
    sys.exit(main())
