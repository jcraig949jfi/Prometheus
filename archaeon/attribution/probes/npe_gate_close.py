"""Operator directive "CLOSE THE INDEPENDENCE GATES" (2026-09-28): G1 on K16b/K16c/K37 and G2 RAW on the frozen tracers.

Neither tracer is modified. The frozen reference is ops/.../npe_reftracer/ref_tracer_npe.py (commit 3757111de). Nestor's frozen
output is ops/.../npe_fixture_validation/nestor_v2_FUZZ_AGREEMENT_nestor.jsonl (his tracer e5af0cae1). Nestor's code is not read.

G2 is applied as PREREGISTERED (v4 s4.3): per locus, the data label and the three dependence sets (addr, ctrl primary, exec) must
agree on >= 99.5% of loci per class. The class is the NPE class key (v5 C6 A5): the performer's ENTITY relative to store_by
(self / other / none), plus unwritten loci. Comparison is RAW: no canonical equivalence. The C8 arbitrations A1/A2 were made after
seeing the discrepancies. They are NOT applied here. The directive's dependence categories are reported per class alongside
(descriptive; they do not rescue or replace the prereg gate).
    python -m archaeon.attribution.probes.npe_gate_close g1|g2 [OUTDIR]
"""
import ast
import json
import os
import sys
from collections import Counter, defaultdict

from archaeon.attribution.probes.npe_fixture_validate import load_ref, ARC
from archaeon.attribution.probes.npe_fuzz_agreement import nl, rl, ns, rs

FUZZ = ARC + "/npe_fixture_validation/nestor_v2_FUZZ_AGREEMENT_nestor.jsonl"
PREREG_FIELDS = ("label", "addr", "ctrl", "exec")                  # v4 s4.3


def g1():
    R = load_ref()
    sys.path.insert(0, os.path.join(ARC, "npe_fixture_validation"))
    import importlib
    NF = importlib.import_module("nestor_v2_npe_fixtures")
    F = {f["name"]: f for f in NF.fixtures()}; n = NF.N
    out = {}
    for name in ("K16b_occupant_code_run_in_writer_half", "K16c_writer_code_run_by_occupant", "K37_painting_one_source"):
        f = F[name]; vside = f.get("vside", 0)
        st_a = (f["regs_a"],) + tuple(f["flags_a"]); st_b = (f["regs_b"],) + tuple(f["flags_b"])
        r = R.trace_interaction(f["ga"], f["gb"], st_a, st_b, budget=f["budget"], ops_mask=f["mask"])
        rows = []
        for j, e in sorted(f["expect"].items()):
            y = r["loci"][vside * n + j]; sp = y["store_pc"]
            rows.append({"locus": "%s[%d]" % ("ab"[vside], j), "value": y["post"], "expect": {k: v for k, v in e.items() if k != "note"},
                         "label": R.fmt_label(y["label"]), "store_by": y["store_by"], "store_pc": sp,
                         "store_pc_location_half": None if sp is None else "ab"[sp // n],
                         "performer": R.fmt_label(y["performer"]) if y["performer"] else None,
                         "performer_entity": y["performer_entity"]})
        out[name] = rows
    return out, R


def g2(outdir):
    R = load_ref()
    tot = Counter(); bad = Counter(); recs = []; ntot = Counter(); nbad = Counter()
    def flagy(s): return any(b[0] == "PREG" and b[2] in ("fz", "fc") for b in s)
    for line in open(FUZZ):
        rec = json.loads(line); pre = ast.literal_eval(rec["pre"]) if isinstance(rec["pre"], str) else rec["pre"]
        ga, gb = bytes.fromhex(pre["ga"]), bytes.fromhex(pre["gb"])
        st_a = (pre["regs_a"],) + tuple(pre["flags_a"]); st_b = (pre["regs_b"],) + tuple(pre["flags_b"])
        r = R.trace_interaction(ga, gb, st_a, st_b, budget=pre["budget"], ops_mask=pre["ops_mask"])
        for h, side in enumerate("ab"):
            for x in rec["loci"][side]:
                j = x["j"]; y = r["loci"][h * R.N + j]
                def cls_of(written, pe, sb):
                    if not written: return "unwritten"
                    if pe is None: return "written_perf_none"
                    return "written_self" if pe == sb else "written_other"
                cls = cls_of(y["written"], y["performer_entity"], y["store_by"])
                npf = nl(x["performer"]) if x.get("performer") is not None else None
                ncls = cls_of(x["written"], npf[1] if npf and npf[0] == "ENTITY" else None, x.get("store_by"))
                LN, LR = nl(x["label"]), rl(y["label"])
                c = {"label": LN == LR, "written": x["written"] == y["written"],
                     "addr": ns(x["addr"]) == rs(y["addr_deps"])}
                both = x["written"] and y["written"]
                if both:
                    PR = rl(y["performer"]) if y["performer"] is not None else None
                    c.update({"ctrl": ns(x["ctrl"]) == rs(y["ctrl_deps"]), "exec": ns(x["exec"]) == rs(y["exec_deps"]),
                              "store_by": x["store_by"] == y["store_by"], "performer": npf == PR,
                              "performer_entity": (npf[1] if npf and npf[0] == "ENTITY" else None) == y["performer_entity"],
                              "ctrl_slice(secondary)": ns(x["ctrl_slice"]) == rs(y["ctrl_deps_slice"])})
                elif y["written"] or x["written"]:
                    c.update({"ctrl": False, "exec": False})
                else:
                    c.update({"ctrl": True, "exec": True})       # both empty by definition for unwritten loci
                # directive categories (descriptive)
                c["cat:source_locus"] = (LN[:3] if LN[0] == "ENTITY" else None) == (LR[:3] if LR[0] == "ENTITY" else None)
                c["cat:identification_input(ENTITY-MOVE side,src)"] = c["cat:source_locus"]
                c["cat:class_key"] = ncls == cls
                if LN[0] == "MUTATION" or LR[0] == "MUTATION": c["cat:mutation"] = c["label"]
                if LR == ("CONST", "in_exhausted") or LN == ("CONST", "in_exhausted"): c["cat:IN"] = c["label"] and c["addr"]
                sets_r = [LR[1]] if LR[0] == "COMPUTED" else []
                if flagy(frozenset().union(*sets_r) if sets_r else ()) or flagy(rs(y["addr_deps"])) or (both and flagy(rs(y["ctrl_deps"]))):
                    c["cat:carry/flag"] = all(c[k] for k in ("label", "addr", "ctrl"))
                for f, ok in c.items():
                    tot[(cls, f)] += 1
                    if f in PREREG_FIELDS:
                        ntot[(ncls, f)] += 1
                        if not ok: nbad[(ncls, f)] += 1
                    if not ok:
                        bad[(cls, f)] += 1
                if not all(ok for f, ok in c.items() if not f.startswith("cat:")):          # every disagreement, gated or not
                    recs.append({"k": rec["k"], "half": side, "j": j, "class_ref": cls, "class_nestor": ncls,
                                 "fields": sorted(f for f, ok in c.items() if not ok and not f.startswith("cat:")),
                                 "input": {"ga": pre["ga"], "gb": pre["gb"], "regs_a": pre["regs_a"], "regs_b": pre["regs_b"],
                                           "flags_a": pre["flags_a"], "flags_b": pre["flags_b"], "budget": pre["budget"],
                                           "ops_mask": pre["ops_mask"]},
                                 "nestor": {"label": x["label"], "performer": x.get("performer"), "ctrl_slice": x.get("ctrl_slice")},
                                 "reference": {"label": R.fmt_label(y["label"]),
                                               "performer": R.fmt_label(y["performer"]) if y["performer"] else None,
                                               "ctrl_slice": R.fmt_set(y["ctrl_deps_slice"]) if y["written"] else None}})
    lines = ["G2 RAW (v4 s4.3 as preregistered; no A1/A2), frozen reference 3757111de vs Nestor e5af0cae1 export, 300 interactions",
             "class = reference's performer class (C6 A5); agreement = loci agreeing / loci in class", ""]
    worst = {}
    for cl in sorted({k for k, _ in tot}):
        lines.append(cl)
        for f in sorted({f for k, f in tot if k == cl}):
            a = 1 - bad[(cl, f)] / tot[(cl, f)]
            tag = "  PREREG GATE %s" % ("PASS" if a >= 0.995 else "FAIL") if f in PREREG_FIELDS else ""
            if f in PREREG_FIELDS: worst[(cl, f)] = a
            lines.append("  %-48s %6d/%-6d %.4f%s" % (f, tot[(cl, f)] - bad[(cl, f)], tot[(cl, f)], a, tag))
    lines += ["", "robustness: prereg fields with the class taken from NESTOR's export (same verdict required):"]
    for (cl, f) in sorted(ntot):
        lines.append("  %-18s %-6s %6d/%-6d %.4f" % (cl, f, ntot[(cl, f)] - nbad[(cl, f)], ntot[(cl, f)], 1 - nbad[(cl, f)] / ntot[(cl, f)]))
    fail = sorted(k for k, a in worst.items() if a < 0.995)
    lines += ["", "not exercised by this set: MUTATION (no write-back RNG in the fuzz export), OUT (no locus; C6 B8), "
              "pdom scope (Nestor's export has no ctrl_pdom; non-gating per C7.1) -> INCONCLUSIVE for those categories",
              "discrepancy records: %d loci (G2_DISCREPANCIES_RAW.jsonl)" % len(recs),
              "G2 (prereg rule): %s" % ("PASS" if not fail else "FAIL on " + ", ".join("%s/%s %.4f" % (c, f, worst[(c, f)]) for c, f in fail))]
    os.makedirs(outdir, exist_ok=True)
    open(os.path.join(outdir, "G2_RAW_AGREEMENT.txt"), "w", newline="\n").write("\n".join(lines) + "\n")
    with open(os.path.join(outdir, "G2_DISCREPANCIES_RAW.jsonl"), "w", newline="\n") as fh:
        for x in recs: fh.write(json.dumps(x, sort_keys=True) + "\n")
    print("\n".join(lines))
    return 0 if not fail else 1


if __name__ == "__main__":
    od = sys.argv[2] if len(sys.argv) > 2 else ARC + "/gate_close"
    if sys.argv[1] == "g1":
        o, R = g1(); os.makedirs(od, exist_ok=True)
        json.dump(o, open(os.path.join(od, "G1_FIXTURES_K16b_K16c_K37.json"), "w", newline="\n"), indent=1, default=str)
        print(json.dumps(o, indent=1, default=str))
    else:
        sys.exit(g2(od))
