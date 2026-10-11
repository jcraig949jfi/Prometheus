"""E3-ID: stepping-stone identifiability diagnostic (windows/E3ID_PREREG.md). A NEW diagnostic; it does not re-test or
relabel E3-KP (TFS1_INSTRUMENT_QUALIFIED = NO stays frozen) and nothing here counts as compositional discovery (the
stones come from sealed-family-indexed R1 tasks given to the organism).

INPUT. The E3-KP PRIMARY row of each world (`<kp-out>/KPA1_<world>.json`, row Config(budget=B)): its units (status,
`from`, attempts in procedure order) and chain rows. Same root (WORLD_MANIFEST / evaluator / WORLD_SEALED).

ID FAMILY of a unit (world, m) = "the R1 family used by the E3-KP primary":
  ACQUIRED unit     -> the family it was acquired from (`from`);
  NOT_ACQUIRED unit -> the FIRST attempted family (primary attempt order) whose first dev-consistent program exists
                       (the family that produced the rejected stone); none (every attempt censored) -> no ID family:
                       the unit keeps its primary link (a horizon is not an identifiability question).

ID-1 / ID-2 (per unit with an ID family; target-blind during search). TFS-1 base keyed enumeration with EXACTLY the
primary's order (seed 0, slot = R1 family_id, budget B = 1e6, max size 12) run to the FULL budget, collecting EVERY
dev-consistent program (charge order). Each program's stone = E3-KP extract_mechanism (fallback ON). Stones are grouped
into BEHAVIOUR CLASSES by value-or-FAIL ("FAIL" is a value) on fixed probe INPUTS only: Int->Int / Int->Bool on every
v in [-40, 40]; Int->Int->Int on every (a, b) in [-12, 12]^2. Classes are ranked by first appearance. Programs with no
extractable stone are counted (n_no_stone) and form no class.
  Post hoc (after the search; sealed data used only for SCORING): the sealed-equivalent class (same probe behaviour as
  the sealed mechanism), the charge and ordinal rank of its first program, its class rank, and whether its first program
  passes the R1 test + tribunal; also the R1 test + tribunal of every class's first program.
  The first enumerated program must equal the primary attempt's `found` at the same charge (consistency, asserted).
ID_IDENTIFIABILITY per unit used by a failed E3-KP family: AMBIGUOUS iff n_classes >= 2 and class 1 is not
  sealed-equivalent; UNIQUE otherwise (n_classes >= 1); NO_STONE if n_classes = 0 (reported, excluded from fractions).
  Pooled: AMBIGUOUS / n over the UNDERDETERMINED_STONE units (the units that set an UNDERDETERMINED_STONE first link of
  a not-chain-qualified primary family), with counts; also over every unit of a failed family.

ID-3 RETAIN-k, k in (1, 2, 4) (designated rows; PRE-REGISTERED):
  library = for every constituent, the first k behaviour classes of its ID-1 run (each represented by the stone of the
  class's first program), in class order; NO R1 test / tribunal and no sealed information selects them. A constituent
  without an ID family (or with 0 classes) is NOT_ACQUIRED (link = its primary link) -> CHAIN_C_FAIL.
  Chain: TFS-1 enumeration on the R3 / R4 family, base grammar + that library, budget 1e6, max size 12, seed 0,
  slot = family; the first dev-consistent program judged on test + tribunal (E3-KP rules). No budget compensation.
  The first entry of every constituent carries the E3-KP primary provenance, so RETAIN-1's library is BYTE-IDENTICAL
  to the primary's (same search key) whenever the primary acquired every constituent: RETAIN-1 then reproduces the
  primary chain exactly (tested). Where the primary did NOT acquire a constituent (its stone was rejected by the R1
  certifier), RETAIN-1 differs BY DESIGN (no certifier gate): it is reported, flagged `retain1_differs_by_design`.
RETAIN-k-CERT (secondary, NOT pre-registered; certifier-assisted): the primary's own certifier-guided walk with k
  hypotheses: for each attempted family in primary order, the first k SLOTS (behaviour classes in first-appearance
  order, programs without a stone forming one NO_STONE slot) are taken, and a slot is kept iff it has a stone and its
  first program passes the R1 test + tribunal; the first family with a kept slot supplies the library entries. At k = 1
  this IS the E3-KP primary for every family (exact reproduction tested, CHAIN_C_FAIL included).
First failing link of a RETAIN family: (1) a NOT_ACQUIRED constituent -> its primary link; (2) chain qualified -> none;
  (3) some constituent retained no sealed-equivalent stone -> UNDERDETERMINED_STONE (SEALED_EQUIVALENT_NOT_RETAINED);
  (4) first dev-consistent fails -> COMPOSITION_UNDERDETERMINED; (5) no hit, promoted-form witness class not completed
  -> COMPOSITION_HORIZON; otherwise UNDERDETERMINED_STONE (anomaly).

ID_RETENTION_REPAIR = YES iff RETAIN-4 (designated) is complete and 5 * chain_qualified >= 4 * n (>= 12/15); else NO
  with first-failing-link counts. Scratch is not re-run (E3-KP: 15/15 fail).
INTERPRETATION (prereg map; "mostly" = a STRICT majority of the UNDERDETERMINED_STONE units):
  mostly AMBIGUOUS + YES -> DEVELOPMENTAL_MACHINERY;  mostly AMBIGUOUS + NO -> WORLD_RULER_IDENTIFIABILITY;
  mostly UNIQUE -> INSTRUMENT;  no strict majority -> MIXED (no map entry applies);  no such units -> NOT_APPLICABLE.

Commands (from roles/Aphrodite/beta04, OMP_NUM_THREADS=1, one process per world file):
  python -m tfs1.e3.e3_identifiability --root foundry/<set> --kp-out <dir> --world W --stage id1|retain|all [--out D]
  python -m tfs1.e3.e3_identifiability --root foundry/<set> --kp-out <dir> --pooled [--worlds W1,..] [--out D]
Cache: <out>/ID_<world>.json (content-addressed: enumerations by (family, seed, B, max), chains by E3-KP search_key).
"""
import argparse
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional

os.environ.setdefault("OMP_NUM_THREADS", "1")

from tfs1 import core as C                     # noqa: E402
from tfs1.enum import Enumerator               # noqa: E402
from tfs1.library import Library               # noqa: E402
from tfs1.membrane import code_hashes          # noqa: E402
from tfs1.e3 import worlds as WD               # noqa: E402
from tfs1.e3 import e3_known_positive as KP    # noqa: E402

HERE = Path(__file__).resolve().parent
KS = (1, 2, 4)
DESIGNATED_K = 4
PROBE_1 = list(range(-40, 41))
PROBE_2 = [(a, b) for a in range(-12, 13) for b in range(-12, 13)]
NO_STONE = "NO_STONE"
MAX_JUDGED_CLASSES = 64          # R1 test + tribunal of class first programs: the first 64 classes + the sealed one


# ================================================================ behaviour on probes
def behaviour(lam) -> tuple:
    """value-or-FAIL of a closed lambda on the fixed probe inputs (inputs only: target-blind)."""
    fn = C.compile_term(lam, None, None, swap=False)(())
    u = (C.U[0], C.U[1])
    out = []
    args = [(v,) for v in PROBE_1] if lam[1] == 1 else PROBE_2
    for a in args:
        C.D[0] = 0
        try:
            v = fn(*a)
        except C.Fail as e:
            e.__traceback__ = None
            v = C.FAIL
        out.append(v)
    C.D[0] = 0
    C.U[0], C.U[1] = u
    return tuple(out)


def bkey(beh: tuple) -> str:
    return hashlib.blake2b(repr(beh).encode(), digest_size=12).hexdigest()


# ================================================================ ID-1 enumeration (all dev-consistent programs)
def enumerate_all(task, budget, seed=KP.SEED, max_size=KP.MAX_SIZE) -> Dict:
    E = Enumerator(None)
    t0 = time.process_time()
    r = E.search(task["dev"], task["output_type"], seed, task["family_id"], budget, max_size, max_hits=10 ** 12)
    out = {"hits": [[h["charge"], h["program"]] for h in r["hits"]], "charges": r["charges"], "budget": budget,
           "complete_through_size": r["complete_through_size"], "cpu_s": round(time.process_time() - t0, 2)}
    del E, r
    return out


def classify(hits, kind, sealed_term, task, judge=True) -> Dict:
    t0 = time.process_time()
    classes: Dict[str, Dict] = {}
    order: List[str] = []            # first-appearance order of slots (classes and the NO_STONE slot)
    cache: Dict[str, tuple] = {}
    n_no_stone = 0
    no_stone_first = None
    for ordinal, (charge, prog) in enumerate(hits, 1):
        ex = KP.extract_mechanism(prog, kind, fallback=True)
        if ex is None:
            n_no_stone += 1
            if no_stone_first is None:
                no_stone_first = {"charge": charge, "ordinal": ordinal, "program": prog}
                order.append(NO_STONE)
            continue
        lam_s = C.to_str(ex[0])
        if lam_s not in cache:
            cache[lam_s] = bkey(behaviour(ex[0]))
        k = cache[lam_s]
        c = classes.get(k)
        if c is None:
            classes[k] = {"key": k, "class_rank": len(classes) + 1, "stone": lam_s, "extraction": ex[1],
                          "first_program": prog, "first_charge": charge, "first_ordinal": ordinal, "n_programs": 1}
            order.append(k)
        else:
            c["n_programs"] += 1
    sk = bkey(behaviour(C.parse(sealed_term)))
    sealed_cls = classes.get(sk)
    if judge:
        for c in classes.values():
            if c["class_rank"] <= MAX_JUDGED_CLASSES or c["key"] == sk:
                v = WD.judge(c["first_program"], task)
                c["r1_qualified"] = v["qualified"]
    for c in classes.values():
        c["sealed_equivalent"] = c["key"] == sk
    ranked = sorted(classes.values(), key=lambda c: c["class_rank"])
    n = len(ranked)
    first_seq = bool(ranked and ranked[0]["sealed_equivalent"])
    label = "NO_STONE" if n == 0 else ("AMBIGUOUS" if (n >= 2 and not first_seq) else "UNIQUE")
    return {"n_dev_consistent_programs": len(hits), "n_no_stone_programs": n_no_stone, "no_stone_first": no_stone_first,
            "n_classes": n, "slot_order": order, "classes": ranked, "sealed_key": sk,
            "first_class_sealed_equivalent": first_seq,
            "sealed_equivalent_found": sealed_cls is not None,
            "sealed_equivalent_first_charge": sealed_cls["first_charge"] if sealed_cls else None,
            "sealed_equivalent_first_ordinal": sealed_cls["first_ordinal"] if sealed_cls else None,
            "sealed_equivalent_class_rank": sealed_cls["class_rank"] if sealed_cls else None,
            "sealed_equivalent_first_program_r1_qualified": sealed_cls.get("r1_qualified") if sealed_cls else None,
            "ID_IDENTIFIABILITY": label, "classify_cpu_s": round(time.process_time() - t0, 2)}


# ================================================================ per world
def _load(out_dir, world) -> Dict:
    p = Path(out_dir) / ("ID_%s.json" % world)
    d = json.loads(p.read_text()) if p.exists() else {}
    d.setdefault("world", world)
    d.setdefault("enumerations", {})
    d.setdefault("id1", {})
    d.setdefault("searches", {})
    d.setdefault("retain", {})
    return d


def _save(out_dir, world, d):
    p = Path(out_dir) / ("ID_%s.json" % world)
    p.parent.mkdir(parents=True, exist_ok=True)
    d["code_sha256"] = code_hashes()
    d["e3_code_sha256"] = KP.e3_code_hashes()
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, indent=1, sort_keys=True))
    os.replace(tmp, p)


class ID:
    def __init__(self, root, world, kp_out, budget=KP.BUDGET):
        self.root, self.world, self.budget = root, world, int(budget)
        self.kp = KP.KP(root, world)
        self.cfg = KP.Config(budget=self.budget)
        kd = KP._load(kp_out, world)
        row = kd.get("rows", {}).get(self.cfg.key())
        if not row:
            raise ValueError("no E3-KP primary row %s for %s in %s" % (self.cfg.key(), world, kp_out))
        self.kpd = kd
        self.prim = row
        self.desc = self.kp.describe(kd, self.cfg)

    # ---- which family, which units
    def id_family(self, m) -> Optional[str]:
        u = self.prim["units"][m]
        if u["status"] == "ACQUIRED":
            return u["from"]
        for a in u.get("attempts", []):
            if a.get("found"):
                return a["family_id"]
        return None

    def failed_families(self) -> List[str]:
        return [f["family_id"] for f in self.desc["families"] if not f["chain_qualified"]]

    def underdetermined_units(self) -> List[str]:
        out = []
        for f in self.desc["families"]:
            if f["first_failing_link"] == "UNDERDETERMINED_STONE":
                li = f["link_info"]
                for m in ([li["unit"]] if li.get("unit") else li.get("units", [])):
                    if m not in out:
                        out.append(m)
        return sorted(out)

    def units(self) -> List[str]:
        return sorted(self.prim["units"])

    # ---- ID-1
    def enum(self, d, fid) -> Dict:
        key = "%s|seed=%d|B=%d|max=%d" % (fid, KP.SEED, self.budget, KP.MAX_SIZE)
        if key not in d["enumerations"]:
            d["enumerations"][key] = enumerate_all(self.kp.task(fid), self.budget)
        return d["enumerations"][key]

    def id1_family(self, d, m, fid) -> Dict:
        k = "%s|%s" % (m, fid)
        if k not in d["id1"]:
            e = self.enum(d, fid)
            rec = classify(e["hits"], self.kp.mech[m]["kind"], self.kp.mech[m]["term"], self.kp.task(fid))
            prim_att = next((a for a in self.prim["units"][m].get("attempts", []) if a["family_id"] == fid), None)
            first = e["hits"][0] if e["hits"] else [None, None]
            rec.update({"mechanism": m, "family_id": fid, "charges": e["charges"], "enum_cpu_s": e["cpu_s"],
                        "complete_through_size": e["complete_through_size"],
                        "primary_first_hit": None if prim_att is None else [prim_att.get("charge"),
                                                                             prim_att.get("found")],
                        "first_hit": first})
            rec["primary_first_hit_matches"] = (prim_att is None or
                                                [prim_att.get("charge"), prim_att.get("found")] == list(first))
            if not rec["primary_first_hit_matches"]:
                raise AssertionError("ID-1 enumeration diverges from the E3-KP primary on %s %s" % (m, fid))
            d["id1"][k] = rec
        return d["id1"][k]

    def needed_id1(self) -> List[tuple]:
        """(m, fid): the ID family of every unit, plus every attempted family with a dev-consistent program (CERT)."""
        out = []
        for m in self.units():
            fam = self.id_family(m)
            if fam:
                out.append((m, fam))
            for a in self.prim["units"][m].get("attempts", []):
                if a.get("found") and (m, a["family_id"]) not in out:
                    out.append((m, a["family_id"]))
        return out

    # ---- ID-3 hypotheses
    def hyps(self, d, m, k, cert: bool):
        """-> (list of class records, family) ; [] if none."""
        if not cert:
            fam = self.id_family(m)
            if fam is None:
                return [], None
            rec = self.id1_family(d, m, fam)
            return rec["classes"][:k], fam
        for a in self.prim["units"][m].get("attempts", []):
            if not a.get("found"):
                continue
            rec = self.id1_family(d, m, a["family_id"])
            by = {c["key"]: c for c in rec["classes"]}
            slots = rec["slot_order"][:k]
            kept = [by[s] for s in slots if s != NO_STONE and by[s].get("r1_qualified")]
            if kept:
                return kept, a["family_id"]
        return [], None

    def library(self, fid, hyp: Dict[str, tuple]):
        lib = Library(closed_args=True)
        slot = {}
        for m in self.kp.constituents(fid):
            cl, fam = hyp[m]
            for j, c in enumerate(cl):
                prov = ({"mechanism_slot": m, "from": fam, "source": "tfs1", "procedure": "E3-KP (ii)"} if j == 0 else
                        {"mechanism_slot": m, "from": fam, "source": "tfs1", "procedure": "E3-ID RETAIN",
                         "hypothesis": j})
                e, _st = lib.promote_lambda(C.parse(c["stone"]), prov)
                if c.get("sealed_equivalent") or m not in slot:
                    slot[m] = e.alias_of or e.id
        return lib, slot

    def run_retain(self, d, fid, k, cert=False) -> Dict:
        hyp = {m: self.hyps(d, m, k, cert) for m in self.kp.constituents(fid)}
        row = {"family_id": fid, "k": k, "certified": cert, "rung": self.kp.fams[fid]["rung"],
               "hypotheses": {m: {"family": fam, "stones": [c["stone"] for c in cl],
                                  "sealed_equivalent": [c["sealed_equivalent"] for c in cl]}
                              for m, (cl, fam) in hyp.items()}}
        missing = [m for m, (cl, _f) in hyp.items() if not cl]
        if missing:
            row["status"] = "CHAIN_C_FAIL"
            row["missing"] = missing
            u = self.prim["units"][missing[0]]
            row["link"] = u.get("link") if u["status"] != "ACQUIRED" else "R1_ACQUISITION"
            row["link_detail"] = u.get("link_detail") if u["status"] != "ACQUIRED" else "NO_STONE_CLASS"
            return self._consistency(row, fid, k, cert)
        lib, slot = self.library(fid, hyp)
        key = KP.search_key(fid, lib, self.cfg)
        if key not in d["searches"]:
            r = KP._search(self.kp.task(fid), lib, KP.SEED, self.budget, False)
            if r["hit"]:
                r["verdict"] = WD.judge(r["program"], self.kp.task(fid), lib)
            d["searches"][key] = r
        r = d["searches"][key]
        diag = self.kp.static_diag(fid, lib, slot)
        row.update({"library_sha256": lib.sha256(), "library_entries": len(lib), "search_key": key,
                    "found": r["program"], "charge": r["hit_charge"], "charges": r["charges"], "cpu_s": r["cpu_s"],
                    "complete_through_size": r["complete_through_size"], "static": diag})
        if r["hit"]:
            row["verdict"] = r["verdict"]
            row["status"] = "SOLVED" if r["verdict"]["qualified"] else "FIRST_DEV_CONSISTENT_FAILS_TEST"
        else:
            row["status"] = "NOT_FOUND_AT_BUDGET"
        no_seq = [m for m, (cl, _f) in hyp.items() if not any(c["sealed_equivalent"] for c in cl)]
        if row["status"] == "SOLVED":
            row["link"], row["link_detail"] = None, "CHAIN_QUALIFIED"
        elif no_seq:
            row["link"], row["link_detail"], row["units_without_sealed_equivalent"] = (
                "UNDERDETERMINED_STONE", "SEALED_EQUIVALENT_NOT_RETAINED", no_seq)
        elif row["status"] == "FIRST_DEV_CONSISTENT_FAILS_TEST":
            row["link"], row["link_detail"] = "COMPOSITION_UNDERDETERMINED", "CHAIN_FIRST_DEV_CONSISTENT_FAILS_TEST"
        else:
            h = KP._horizon(r["complete_through_size"], diag["size_promoted_form"])
            row["link"], row["link_detail"] = (("COMPOSITION_HORIZON", h) if h else
                                               ("UNDERDETERMINED_STONE", "WITNESS_CLASS_COMPLETED_NO_HIT"))
        return self._consistency(row, fid, k, cert)

    def _consistency(self, row, fid, k, cert) -> Dict:
        """k = 1: does the row reproduce the E3-KP primary chain outcome exactly (status, program, charge, charges)?"""
        if k != 1:
            return row
        pc = self.prim["chain"].get(fid, {})
        all_acq = all(self.prim["units"][m]["status"] == "ACQUIRED" for m in self.kp.constituents(fid))
        same = (pc.get("status") == row["status"] and pc.get("found") == row.get("found")
                and pc.get("charge") == row.get("charge") and pc.get("charges") == row.get("charges"))
        row["primary_chain"] = {"status": pc.get("status"), "found": pc.get("found"), "charge": pc.get("charge"),
                                "charges": pc.get("charges"), "library_sha256": pc.get("library_sha256")}
        row["reproduces_primary"] = same and (pc.get("library_sha256") == row.get("library_sha256"))
        row["primary_family_link"] = next((f["first_failing_link"] for f in self.desc["families"]
                                           if f["family_id"] == fid), None)
        row["retain1_differs_by_design"] = (not cert) and not all_acq and not row["reproduces_primary"]
        return row


def run_stages(root, world, kp_out, out_dir, stage, budget=KP.BUDGET, ks=KS, cert=True, log=print) -> Dict:
    I = ID(root, world, kp_out, budget)
    d = _load(out_dir, world)
    d.update({"label": KP._label(root), "kp_row": I.cfg.key(), "budget": I.budget})
    if stage in ("id1", "all", "retain"):
        for m, fam in I.needed_id1():
            k = "%s|%s" % (m, fam)
            if k not in d["id1"]:
                rec = I.id1_family(d, m, fam)
                _save(out_dir, world, d)
                log("id1 %s %s classes=%d programs=%d sealed_rank=%s %s" % (
                    m, fam, rec["n_classes"], rec["n_dev_consistent_programs"], rec["sealed_equivalent_class_rank"],
                    rec["ID_IDENTIFIABILITY"]))
    if stage in ("retain", "all"):
        for cflag in ((False, True) if cert else (False,)):
            for k in ks:
                rk = "RETAIN-%d%s" % (k, "-CERT" if cflag else "")
                rows = d["retain"].setdefault(rk, {})
                for fid in I.kp.admitted():
                    if fid not in rows:
                        rows[fid] = I.run_retain(d, fid, k, cflag)
                        _save(out_dir, world, d)
                        log("%s %s %s %s %s" % (rk, fid, rows[fid]["status"], rows[fid].get("charge"),
                                                rows[fid].get("link")))
    d["summary"] = summarize_world(I, d)
    _save(out_dir, world, d)
    return d


def summarize_world(I: ID, d) -> Dict:
    failed = I.failed_families()
    used = sorted({m for f in failed for m in I.kp.constituents(f)})
    und = I.underdetermined_units()
    units = []
    for m in I.units():
        fam = I.id_family(m)
        rec = d["id1"].get("%s|%s" % (m, fam)) if fam else None
        units.append({"world": I.world, "mechanism": m, "id_family": fam,
                      "primary_status": I.prim["units"][m]["status"], "primary_link": I.prim["units"][m].get("link"),
                      "used_by_failed_family": m in used, "underdetermined_stone_unit": m in und,
                      "ID_IDENTIFIABILITY": rec["ID_IDENTIFIABILITY"] if rec else "NO_ID_FAMILY",
                      **({k: rec[k] for k in ("n_classes", "n_dev_consistent_programs", "n_no_stone_programs",
                                              "first_class_sealed_equivalent", "sealed_equivalent_first_charge",
                                              "sealed_equivalent_first_ordinal", "sealed_equivalent_class_rank",
                                              "sealed_equivalent_first_program_r1_qualified", "enum_cpu_s")}
                         if rec else {})})
    fams = []
    for f in I.desc["families"]:
        fid = f["family_id"]
        row = {"world": I.world, "family_id": fid, "rung": f["rung"], "skeleton": f["skeleton"],
               "primary_chain_qualified": f["chain_qualified"], "primary_link": f["first_failing_link"]}
        for rk, rows in d["retain"].items():
            r = rows.get(fid)
            if r:
                row[rk] = {"status": r["status"], "qualified": r["status"] == "SOLVED", "link": r.get("link"),
                           "detail": r.get("link_detail"), "charge": r.get("charge"), "cpu_s": r.get("cpu_s", 0.0),
                           "reproduces_primary": r.get("reproduces_primary"),
                           "retain1_differs_by_design": r.get("retain1_differs_by_design")}
        fams.append(row)
    return {"units": units, "families": fams}


# ================================================================ pooled
def _retain_verdict(fams, rk) -> Dict:
    rows = [f.get(rk) for f in fams]
    n = len(fams)
    complete = n > 0 and all(r is not None for r in rows)
    q = sum(bool(r and r["qualified"]) for r in rows)
    links = {}
    for r in rows:
        if r and not r["qualified"]:
            links[r["link"]] = links.get(r["link"], 0) + 1
    return {"n": n, "complete": complete, "chain_qualified": q, "first_failing_link_counts": links,
            "meets_80pct": complete and 5 * q >= 4 * n}


def pooled(root, kp_out, out_dir, worlds=None, budget=KP.BUDGET) -> Dict:
    man = WD.world_manifest(root)
    worlds = worlds or sorted(man["worlds"])
    units, fams = [], []
    for w in worlds:
        kp = KP.KP(root, w)
        if not kp.admitted():
            continue
        I = ID(root, w, kp_out, budget)
        s = summarize_world(I, _load(out_dir, w))
        units += s["units"]
        fams += s["families"]
    res = outcomes(units, fams)
    res.update({"label": KP._label(root), "worlds": worlds, "budget": budget})
    return res


def outcomes(units: List[Dict], fams: List[Dict]) -> Dict:
    """Pure function: the pre-registered pooled outputs from per-unit and per-family summaries."""
    und = [u for u in units if u["underdetermined_stone_unit"]]
    und_lab = [u for u in und if u["ID_IDENTIFIABILITY"] in ("AMBIGUOUS", "UNIQUE")]
    n_amb = sum(u["ID_IDENTIFIABILITY"] == "AMBIGUOUS" for u in und_lab)
    used = [u for u in units if u["used_by_failed_family"]]
    used_lab = [u for u in used if u["ID_IDENTIFIABILITY"] in ("AMBIGUOUS", "UNIQUE")]
    ident = {"underdetermined_stone_units": len(und), "labelled": len(und_lab), "AMBIGUOUS": n_amb,
             "UNIQUE": len(und_lab) - n_amb, "fraction_ambiguous": (round(n_amb / len(und_lab), 4) if und_lab else None),
             "not_labelled": {u["world"] + "/" + u["mechanism"]: u["ID_IDENTIFIABILITY"] for u in und
                              if u not in und_lab},
             "all_units_of_failed_families": {
                 "n": len(used), "AMBIGUOUS": sum(u["ID_IDENTIFIABILITY"] == "AMBIGUOUS" for u in used_lab),
                 "UNIQUE": sum(u["ID_IDENTIFIABILITY"] == "UNIQUE" for u in used_lab),
                 "other": {u["world"] + "/" + u["mechanism"]: u["ID_IDENTIFIABILITY"] for u in used
                           if u not in used_lab}}}
    rkeys = ["RETAIN-%d" % k for k in KS] + ["RETAIN-%d-CERT" % k for k in KS]
    rv = {rk: _retain_verdict(fams, rk) for rk in rkeys}
    des = rv["RETAIN-%d" % DESIGNATED_K]
    repair = "INCOMPLETE" if not des["complete"] else ("YES" if des["meets_80pct"] else "NO")
    if not und_lab:
        mostly = None
    elif 2 * n_amb > len(und_lab):
        mostly = "AMBIGUOUS"
    elif 2 * (len(und_lab) - n_amb) > len(und_lab):
        mostly = "UNIQUE"
    else:
        mostly = "MIXED"
    if mostly is None:
        interp = "NOT_APPLICABLE"
    elif mostly == "UNIQUE":
        interp = "INSTRUMENT"
    elif mostly == "MIXED":
        interp = "MIXED"
    elif repair == "INCOMPLETE":
        interp = "INCOMPLETE"
    else:
        interp = "DEVELOPMENTAL_MACHINERY" if repair == "YES" else "WORLD_RULER_IDENTIFIABILITY"
    r1 = [f.get("RETAIN-1") for f in fams]
    cons = {"RETAIN-1_reproduces_primary_where_all_constituents_acquired":
            all(r["reproduces_primary"] for r in r1 if r and not r["retain1_differs_by_design"]),
            "RETAIN-1_differs_by_design (primary R1 certifier rejected a constituent)":
            sorted(f["family_id"] for f in fams if f.get("RETAIN-1") and f["RETAIN-1"]["retain1_differs_by_design"]),
            "RETAIN-1-CERT_reproduces_primary_all": all(f["RETAIN-1-CERT"]["reproduces_primary"] for f in fams
                                                        if f.get("RETAIN-1-CERT"))}
    return {
            "claim_limits": "diagnostic; does not relabel TFS1_INSTRUMENT_QUALIFIED (= NO, frozen); not compositional "
                            "discovery (stones from sealed-family-indexed R1 tasks); motif-limited admitted set",
            "ID_IDENTIFIABILITY": ident, "ID_RETENTION_REPAIR": repair,
            "ID_RETENTION_REPAIR_rule": "RETAIN-%d chain-qualified >= 80%% (5q >= 4n; 12/15)" % DESIGNATED_K,
            "retain_rows": rv, "interpretation": interp, "mostly": mostly, "consistency": cons,
            "units": units, "families": fams}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--kp-out", required=True, help="dir with the E3-KP KPA1_<world>.json caches (primary row)")
    ap.add_argument("--out", default=str(HERE / "runs"))
    ap.add_argument("--world")
    ap.add_argument("--worlds")
    ap.add_argument("--stage", choices=["id1", "retain", "all"])
    ap.add_argument("--no-cert", action="store_true", help="skip the secondary RETAIN-k-CERT rows")
    ap.add_argument("--pooled", action="store_true")
    ap.add_argument("--budget", type=int, default=KP.BUDGET, help="development only; prereg budget is 1e6")
    a = ap.parse_args()
    if a.pooled:
        res = pooled(a.root, a.kp_out, a.out, a.worlds.split(",") if a.worlds else None, a.budget)
        p = Path(a.out) / ("ID_POOLED_B%d.json" % a.budget)
        p.write_text(json.dumps(res, indent=1, sort_keys=True))
        print(json.dumps({k: res[k] for k in ("ID_IDENTIFIABILITY", "ID_RETENTION_REPAIR", "interpretation",
                                              "consistency")}, indent=1))
        print(json.dumps({k: {kk: v[kk] for kk in ("chain_qualified", "n", "first_failing_link_counts")}
                          for k, v in res["retain_rows"].items()}))
        return
    if not (a.world and a.stage):
        ap.error("--world and --stage are required unless --pooled")
    run_stages(a.root, a.world, a.kp_out, a.out, a.stage, a.budget, KS, not a.no_cert,
               log=lambda s: print(s, flush=True))


if __name__ == "__main__":
    main()
