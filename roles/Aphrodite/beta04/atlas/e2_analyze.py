"""E2 ANALYSIS (A1-B.5, A1-B.6, A1-B.7, A1-B.9). Runnable only after the screen completes.

  python -m atlas.e2_analyze [--root foundry/production] [--out runs/e2]   (from roles/Aphrodite/beta04)

Refuses (exit 2) if any planned qualification / K-calibration / run shard is missing or errored. Writes
<out>/E2_ANALYSIS.json. All hit counts below are the PRIMARY endpoint (A1-B.4: the first dev-consistent program of the
run qualifies on T0 + FINAL tribunals); secondary (any qualified within B) and CERTIFIER_ASSISTED counts are reported
beside, never substituted. A START_HIT (hit at a charge <= #starts) is excluded from discovery counts (it would mean a
generic start program already solves the family).

Per-family labels (A1-B.5), evaluated on primary hits out of the seeds run:
  REACHED            chain_neutral >= 1
  CREDIT_GRADIENT    chain_strict or chain_neutral beats credit_blind by >= 3 seeds
  CREDIT_MISLEADING  credit_blind beats BOTH credit chains by >= 3 (each credit chain that was run)
  DESERT_OR_HORIZON  every arm run on the family is 0
  UNRESOLVED         otherwise
  The A1-B.5 rules are not mutually exclusive (e.g. REACHED and CREDIT_GRADIENT). Reading used (flagged): every rule
  that holds is reported in `flags`; `label` is the FIRST that holds in the table order above, else UNRESOLVED.

RE-DERIVATION (C-013 D1 integrator requirement, Palamedes #2079): no runner-written success field is trusted. For every
run shard the analyzer rebuilds the library (sha256 must equal the shard's), re-reads the ARM VIEW dev and the
evaluator task, and independently re-judges each stored consultation and the hit program ALONE (archive off): dev
consistency on the arm-view dev, every test example, the generated tribunal at the search salt T0 and at the fresh
salt FINAL (value-or-FAIL agreement with the sealed expanded witness) and the task's own tribunal. primary / secondary /
CERTIFIER_ASSISTED / START_HIT are recomputed from these components; ANY disagreement with a stored component or a
runner field is a HARD ERROR (exit 3, E2_ANALYSIS_MISMATCH.json). Counts use the recomputed values only. A further
AUDIT-salt tribunal on the hit is reported descriptively (never changes a count).

FRONTIER_ARCHIVE_EFFECT (A1-B.6):
  population  R3/R4 families where D-BEH QUALIFIED (D1-X3 and X3G run); all others listed INSTRUMENT_UNVALIDATED.
  unit        skeleton cluster (e2_driver.cluster_of: the sealed witness skeleton label merged by the foundry's
              motif-control rules). Unit difference = MEAN over the cluster's population families of the per-family
              primary-hit difference (D1-X3 - chain_neutral; D1-X3 - X3G).
  informative a unit with >= 1 primary hit in ANY arm on any of its population families.
  test        exact one-sided sign-flip over the informative units' differences (all 2^n sign vectors; p = share
              with sum >= observed). Non-informative units have difference 0 and cannot change p.
  < 5 informative units -> INCONCLUSIVE_CENSORED; YES_SCREEN iff both one-sided p < 0.05 and both sums > 0;
  NO iff >= 5 informative units and the sum vs chain_neutral <= 0; otherwise INCONCLUSIVE.
  YES_SCREEN is a SCREEN result (directive: no significance from screening): final field mapping recorded as
  "INCONCLUSIVE (screen-positive; confirmation required)".
"""
import argparse
import itertools
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from tfs1 import core as C

from . import common as K
from . import e2_driver as D

ALPHA = 0.05
MIN_UNITS = 5
GAP = 3

CLAIM_LIMITS = [
    "Restricted to the motif-limited admitted set: 2 kind-pairings (fp, fs), 5 merged skeletons, 7 worlds "
    "(4 families from gate-failing worlds); E1 = WORLD_DEMAND_NOT_QUALIFIED (strict) is carried into every field.",
    "The library is the family's constituent mechanisms as FOUNDRY-ACQUIRED primitives (oracle decomposition, "
    "supplied developmental context): the screen asks whether credit / archives help cross the COMPOSITION step "
    "given stepping stones; it is not discovery of the stepping stones.",
    "Screening (8 seeds): no confirmatory significance; family labels are descriptive (P(|d| >= 3) ~ 0.21 per "
    "family for two Bin(8, 0.5) counts).",
    "X3 > X3G does NOT mean the descriptor kept stepping stones (C-013 D1 interpretive rule).",
    "E4 is BARRED on these worlds; the E3 2x2 requires E3-KP QUALIFIED AND E2 complete.",
]


def flip_p(diffs: Sequence[float]) -> Dict:
    """Exact one-sided sign-flip p over the given unit differences (zeros included; they do not change p)."""
    n = len(diffs)
    obs = sum(diffs)
    if n == 0:
        return {"n": 0, "sum": 0.0, "p_one_sided": 1.0, "attainable_min_p": 1.0}
    ge = 0
    for signs in itertools.product((1, -1), repeat=n):
        s = sum(sg * abs(d) for sg, d in zip(signs, diffs))
        ge += s >= obs - 1e-12
    nz = sum(1 for d in diffs if d != 0)
    return {"n": n, "nonzero": nz, "sum": round(obs, 6), "p_one_sided": ge / 2 ** n,
            "attainable_min_p": 1 / 2 ** nz if nz else 1.0, "diffs": [round(d, 6) for d in diffs]}


def label_family(hits: Dict[str, Optional[int]]) -> Dict:
    """hits: arm -> primary hits (None = not run on this family)."""
    g = lambda a: hits.get(a)                                              # noqa: E731
    ran = {a: v for a, v in hits.items() if v is not None}
    flags = []
    if g("chain_neutral") is not None and g("chain_neutral") >= 1:
        flags.append("REACHED")
    credit = [a for a in ("chain_strict", "chain_neutral") if g(a) is not None]
    blind = g("credit_blind")
    if blind is not None and any(g(a) - blind >= GAP for a in credit):
        flags.append("CREDIT_GRADIENT")
    if blind is not None and credit and all(blind - g(a) >= GAP for a in credit):
        flags.append("CREDIT_MISLEADING")
    if ran and all(v == 0 for v in ran.values()):
        flags.append("DESERT_OR_HORIZON")
    return {"label": flags[0] if flags else "UNRESOLVED", "flags": flags, "arms_considered": sorted(ran)}


def frontier(per_family: Dict[str, Dict], clusters: Dict[str, str]) -> Dict:
    pop = [f for f, r in per_family.items() if r["arms"].get("D1-X3", {}).get("status") == "RUN"
           and r["arms"].get("X3G", {}).get("status") == "RUN" and r["arms"].get("chain_neutral", {}).get("status")
           == "RUN"]
    excluded = sorted(f for f in per_family if f not in pop)
    units: Dict[str, List[str]] = {}
    for f in sorted(pop):
        units.setdefault(clusters[f], []).append(f)
    rows = []
    for u, fs in sorted(units.items()):
        h = lambda f, a: per_family[f]["arms"][a]["primary_hits"]       # noqa: E731
        d1 = sum(h(f, "D1-X3") - h(f, "chain_neutral") for f in fs) / len(fs)
        d2 = sum(h(f, "D1-X3") - h(f, "X3G") for f in fs) / len(fs)
        inf = any((per_family[f]["arms"][a].get("primary_hits") or 0) > 0 for f in fs
                  for a in per_family[f]["arms"] if per_family[f]["arms"][a].get("status") == "RUN")
        rows.append({"unit": u, "families": fs, "d_X3_minus_neutral": d1, "d_X3_minus_X3G": d2,
                     "informative": inf})
    info = [r for r in rows if r["informative"]]
    t1 = flip_p([r["d_X3_minus_neutral"] for r in info])
    t2 = flip_p([r["d_X3_minus_X3G"] for r in info])
    if len(info) < MIN_UNITS:
        verdict = "INCONCLUSIVE_CENSORED"
    elif t1["p_one_sided"] < ALPHA and t2["p_one_sided"] < ALPHA and t1["sum"] > 0 and t2["sum"] > 0:
        verdict = "YES_SCREEN"
    elif t1["sum"] <= 0:
        verdict = "NO"
    else:
        verdict = "INCONCLUSIVE"
    final_field = {"YES_SCREEN": "INCONCLUSIVE (screen-positive; confirmation required)",
                   "NO": "NO", "INCONCLUSIVE": "INCONCLUSIVE",
                   "INCONCLUSIVE_CENSORED": "INCONCLUSIVE"}[verdict]
    return {"FRONTIER_ARCHIVE_EFFECT": verdict, "final_field": final_field, "population": sorted(pop),
            "instrument_unvalidated_or_not_run": excluded, "units": rows, "informative_units": len(info),
            "test_vs_chain_neutral": t1, "test_vs_X3G": t2, "alpha": ALPHA, "min_informative_units": MIN_UNITS}


class Mismatch(Exception):
    pass


class Rederiver:
    """Independent endpoint re-derivation from stored components (no runner verdict is read)."""

    def __init__(self, root):
        self.R = D.E2Root(root)
        self._fs: Dict[str, object] = {}
        self._lt: Dict[str, Dict] = {}
        self.audit_disagreements: List[Dict] = []
        self.judged = 0

    def setup(self, fid):
        if fid not in self._fs:
            self._fs[fid] = D.FamilySetup(self.R, fid)
            self._lt[fid] = self.R.learner_task(fid)
        return self._fs[fid], self._lt[fid]

    @staticmethod
    def _agree(fn, examples) -> bool:
        return all(C.same_value(C.run(fn, list(i)), o) for i, o in examples)

    def judge(self, fid: str, program: str, lib, salts=(D.CONFIG["search_salt"], D.CONFIG["final_salt"])) -> Dict:
        fs, lt = self.setup(fid)
        task = fs.task
        u = (C.U[0], C.U[1])
        fn = C.compile_term(C.parse(program), lib, None, swap=lib is not None)
        wfn = C.compile_term(C.parse(fs.witness), None, None, swap=False)
        out = {"dev_consistent": self._agree(fn, lt["dev"]), "test_ok": self._agree(fn, task["test"])}
        for salt in salts:
            ins = K.tribunal_inputs(task, salt)
            out["tribunal_%s_ok" % salt] = all(C.same_value(C.run(fn, list(i)), C.run(wfn, list(i))) for i in ins)
        tt = task.get("tribunal")
        out["task_tribunal_ok"] = self._agree(fn, tt) if isinstance(tt, list) and tt else None
        C.U[0], C.U[1] = u
        self.judged += 1
        out["qualified"] = bool(out["dev_consistent"] and out["test_ok"] and
                                all(out["tribunal_%s_ok" % sl] for sl in salts) and out["task_tribunal_ok"] is not False)
        return out

    def check(self, r: Dict) -> Dict:
        """Recompute the endpoint of one run shard; raise Mismatch on any disagreement."""
        sid = r.get("shard")
        fid, arm = r["family_id"], r["arm"]
        fs, _lt = self.setup(fid)
        lib = fs.lib if D.ARMS[arm]["library"] else None
        comp = r.get("components")
        if comp is None:
            raise Mismatch("%s: no stored components" % sid)
        if (lib.sha256() if lib is not None else None) != comp["library_sha256"]:
            raise Mismatch("%s: library sha256 differs from the shard's" % sid)
        errs = []
        cons = comp["consultations_stored"]
        rec = []
        for c in cons:
            j = self.judge(fid, c["program"], lib)
            rec.append(j)
            stored = {"dev_consistent": c.get("dev_consistent"), "test_ok": c["test_ok"],
                      "tribunal_T0_ok": c["tribunal_T0_ok"], "tribunal_FINAL_ok": c["tribunal_FINAL_ok"],
                      "task_tribunal_ok": c["task_tribunal_ok"], "qualified": c["qualified"]}
            for k, v in stored.items():
                if j[k] != v:
                    errs.append("consultation %d %s: stored %r recomputed %r" % (c["index"], k, v, j[k]))
        n = comp["n_consultations"]
        primary = bool(n and cons and cons[0]["index"] == 0 and rec[0]["qualified"])
        hit = comp["hit"]
        secondary = False
        if hit is not None:
            jh = self.judge(fid, hit["program"], lib)
            secondary = jh["qualified"]
            if not secondary:
                errs.append("hit program does not qualify on re-derivation")
            if hit["charge"] is None or hit["charge"] > comp["budget"]:
                errs.append("hit charge %r outside the budget" % hit["charge"])
            if cons and cons[-1]["index"] == n - 1 and (cons[-1]["program"] != hit["program"] or
                                                        cons[-1]["charge"] != hit["charge"]):
                errs.append("the hit is not the last consultation (the run must stop at its first qualified one)")
            a = self.judge(fid, hit["program"], lib, salts=("AUDIT",))
            if not a["qualified"]:
                self.audit_disagreements.append({"shard": sid, "program": hit["program"], "which": "hit"})
        for c, j in zip(cons, rec):
            if j["qualified"] and not (hit is not None and c["index"] == n - 1):
                errs.append("consultation %d qualifies but the run did not stop there" % c["index"])
        if n and not cons:
            errs.append("consultations were made but none stored")
        certifier_assisted = bool(secondary and not primary)
        start_hit = bool(secondary and hit["charge"] <= comp["n_starts"])
        for k, v in (("primary_hit", primary), ("secondary_hit", secondary), ("hit", secondary),
                     ("certifier_assisted", certifier_assisted), ("start_hit", start_hit)):
            if bool(r.get(k)) != v:
                errs.append("runner field %s=%r but re-derived %r" % (k, r.get(k), v))
        if errs:
            raise Mismatch("%s: %s" % (sid, "; ".join(errs[:10])))
        return {"primary_hit": primary, "secondary_hit": secondary, "certifier_assisted": certifier_assisted,
                "start_hit": start_hit, "hit_charge": hit["charge"] if hit else None,
                "first_charge": cons[0]["charge"] if cons else None}


def summarize_arm(results: List[Dict]) -> Dict:
    if not results:
        return {"status": "NOT_IN_PLAN"}
    st = {r.get("status") for r in results}
    if st == {"INSTRUMENT_UNVALIDATED"}:
        return {"status": "INSTRUMENT_UNVALIDATED", "descriptor_verdict": results[0].get("descriptor_verdict")}
    if st == {"LIBRARY_UNAVAILABLE"}:
        return {"status": "LIBRARY_UNAVAILABLE"}
    ok = [r for r in results if r.get("status") == "COMPLETE"]
    if any("_rederived" not in r for r in ok):
        raise Mismatch("summarize_arm called on a shard that was not re-derived")
    rd = lambda r: r["_rederived"]                                      # noqa: E731  (recomputed values ONLY)
    prim = [r for r in ok if rd(r)["primary_hit"] and not rd(r)["start_hit"]]
    sec = [r for r in ok if rd(r)["secondary_hit"] and not rd(r)["start_hit"]]
    return {"status": "RUN" if len(ok) == len(results) else "INCOMPLETE", "seeds_run": len(ok),
            "primary_hits": len(prim), "secondary_hits": len(sec),
            "certifier_assisted_hits": sum(1 for r in sec if rd(r)["certifier_assisted"]),
            "start_hits": sum(1 for r in ok if rd(r)["start_hit"]),
            "autonomous_pass_of_hits": len(sec),
            "primary_hit_charges": sorted(rd(r)["hit_charge"] for r in prim),
            "consultations_total": sum(r.get("n_consultations", 0) for r in ok),
            "cpu_s_total": round(sum(r.get("cpu_s", 0) for r in ok), 1),
            "seeds_hit_primary": sorted(r["seed"] for r in prim)}


def analyze(out: Path, allow_incomplete: bool = False) -> Dict:
    plan = D._read_json(out / "PLAN.json")
    if plan is None:
        raise SystemExit("no PLAN.json in %s" % out)
    st = D.status(plan, out)
    incomplete = any(st[ph]["done"] < st[ph]["total"] or st[ph]["errors"] for ph in ("qual", "kcal", "run"))
    if incomplete and not allow_incomplete:
        print("SCREEN INCOMPLETE: refusing to analyze", json.dumps(st), file=sys.stderr)
        sys.exit(2)
    per_family = {}
    rdv = Rederiver(plan["root"])
    mism = []
    for f in plan["screen_families"]:
        arms = {}
        for a in D.ARM_ORDER:
            sids = [s for s in plan["run_shards"] if s.startswith("run/%s/%s/" % (f, a))]
            res = [r for r in (D._read_json(D.shard_path(out, s)) for s in sids) if r is not None]
            bad = False
            for r in res:
                if r.get("run") and r.get("status") == "COMPLETE":
                    try:
                        r["_rederived"] = rdv.check(r)
                    except Mismatch as e:
                        mism.append(str(e))
                        bad = True
            if bad:
                continue
            arms[a] = summarize_arm(res) if sids else {"status": "NOT_IN_PLAN"}
        if mism:
            continue
        q = D._read_json(D.shard_path(out, D.shard_id("qual", f))) or {}
        kc = D._read_json(D.shard_path(out, D.shard_id("kcal", f))) or {}
        hits = {a: (v["primary_hits"] if v.get("status") == "RUN" else None) for a, v in arms.items()}
        lab = label_family(hits)
        per_family[f] = {"cluster": plan["clusters"][f], "descriptor_verdict": q.get("verdict"),
                         "descriptor_R1": q.get("R1"), "descriptor_R1c": q.get("R1c"), "descriptor_R2": q.get("R2"),
                         "X3G_K": kc.get("K"), "K_matched_within_5pct": (kc.get("calibration") or {}).get(
                             "matched_within_5pct"), "arms": arms, **lab}
    if mism:
        D._write_json(out / "E2_ANALYSIS_MISMATCH.json", {"mismatches": mism})
        print("RE-DERIVATION MISMATCH (hard error): %d shard(s); see E2_ANALYSIS_MISMATCH.json" % len(mism),
              file=sys.stderr)
        sys.exit(3)
    fr = frontier(per_family, plan["clusters"])
    esc = sorted([f, a] for f, r in per_family.items() for a, v in r["arms"].items()
                 if v.get("status") == "RUN" and v["primary_hits"] >= 1 and f in plan["screen_families"])
    esc_sec = sorted([f, a] for f, r in per_family.items() for a, v in r["arms"].items()
                     if v.get("status") == "RUN" and v["secondary_hits"] >= 1)
    atl = D.status(plan, out)["atlas"]
    pre = D._read_json(out.parent / "E2_PRELAUNCH.json")
    complete = {"atlas_all_admitted": atl["done"] == atl["total"] and not atl["errors"],
                "screen_complete_1x": not incomplete,
                "prelaunch_pass": bool(pre and pre.get("pass"))}
    rep = {"driver": D.DRIVER_VERSION, "root_label": plan["root_label"], "truncation": plan["truncation"],
           "arms_in_plan": plan["arms"], "seeds": plan["seeds"], "status": st, "per_family": per_family,
           "label_counts": {lab: sum(1 for r in per_family.values() if r["label"] == lab) for lab in
                            ("REACHED", "CREDIT_GRADIENT", "CREDIT_MISLEADING", "DESERT_OR_HORIZON", "UNRESOLVED")},
           "frontier": fr, "escalation_4x_eligible_primary": esc,
           "escalation_4x_eligible_secondary_descriptive": esc_sec,
           "REACHABILITY_ATLAS_COMPLETE": "YES" if all(complete.values()) else "NO", "completeness": complete,
           "claim_limits": CLAIM_LIMITS, "endpoint": "PRIMARY = first dev-consistent program qualifies (T0 + FINAL)",
           "rederivation": {"programs_judged": rdv.judged, "mismatches": 0,
                            "audit_salt_disagreements_descriptive": rdv.audit_disagreements},
           "incomplete_override": bool(incomplete)}
    D._write_json(out / "E2_ANALYSIS.json", rep)
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(D.BETA04 / "foundry" / "production"))
    ap.add_argument("--out", default=str(D.BETA04 / "runs" / "e2"))
    ap.add_argument("--allow-incomplete", action="store_true", help="tests / dev only; the report is flagged")
    a = ap.parse_args(argv)
    rep = analyze(Path(a.out), a.allow_incomplete)
    print(json.dumps({"labels": rep["label_counts"], "frontier": rep["frontier"]["FRONTIER_ARCHIVE_EFFECT"],
                      "REACHABILITY_ATLAS_COMPLETE": rep["REACHABILITY_ATLAS_COMPLETE"]}))


if __name__ == "__main__":
    main()
