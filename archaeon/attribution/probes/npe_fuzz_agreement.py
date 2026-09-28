"""NPE gate G2 (Nestor #847; v4 s4.3): the independent reference tracer vs Nestor's FROZEN tracer (e5af0cae1) on 300 non-production
fuzz interactions (tracer/FUZZ_AGREEMENT_nestor.jsonl, seed 20260929). Nothing is adjusted; disagreements are listed for
arbitration with both readings.

Compared per locus, for both halves: data label (canonical form), written, store_by, performer, addr_deps, ctrl_deps (primary),
ctrl_deps_slice, exec_deps (at store). Unwritten loci: the data label and written only. Classes: written self (performer entity ==
store_by), written other (performer entity != store_by), written performer-none, unwritten. Gate: >= 99.5% per class.
    python -m archaeon.attribution.probes.npe_fuzz_agreement [FILE]
"""
import ast
import json
import sys
from collections import Counter

from archaeon.attribution.probes.npe_fixture_validate import load_ref, ARC

REGN = ("B", "C", "D", "E", "H", "L", "M", "A")
GATED = {"label", "written", "store_by", "performer", "addr", "ctrl", "exec"}     # v4 s4.3 data label + the three sets (+ roles)


def nb_str(s):
    """Nestor base-label string -> canonical tuple."""
    p = s.split("|")
    if p[0] == "E": return ("ENTITY", p[1], int(p[2]))
    if p[0] == "X": return ("CONTEXT", p[1])
    if p[0] == "P":
        r = p[2]
        return ("PREG", p[1], REGN[int(r)] if r.isdigit() else r)
    if p[0] == "M": return ("MUTATION",) + tuple(p[1:])
    return tuple(p)


def nl(lab):
    """Nestor data label -> canonical."""
    k = lab[0]
    if k == "E": return ("ENTITY", lab[1], lab[2])
    if k == "K": return ("CONST", lab[1])
    if k == "X": return ("CONTEXT", lab[1])
    if k == "P": return ("PREG", lab[1], REGN[lab[2]] if isinstance(lab[2], int) else lab[2])
    if k == "C": return ("COMPUTED", frozenset(nb_str(b) for b in lab[1]))
    if k == "F": return ("COMPUTED_FROM", nl(lab[1]))
    if k == "M": return ("MUTATION", repr(lab[1:]))
    return tuple(lab)


def rl(lab):
    """reference data label -> canonical."""
    k = lab[0]
    if k == "ENTITY": return ("ENTITY", lab[1], lab[2])
    if k == "COMPUTED": return ("COMPUTED", frozenset(rl(b) for b in lab[1]))
    if k == "COMPUTED_FROM": return ("COMPUTED_FROM", rl(lab[1]))
    if k == "MUTATION": return ("MUTATION", repr(lab[1:]))
    return tuple(lab)


def canon(lab):
    """ARBITRATION A1/A2 (Amendment C8): semantic canonical form. COMPUTED_FROM over a COMPUTED is that COMPUTED (the reference's
    SPEC_ISSUES B3 flattening, which Archaeon's C6 summary stated ambiguously); COMPUTED_FROM over a base-less label is CONST;
    CONST kinds are not compared (C6 did not name idiom kinds)."""
    if lab is None: return None
    k = lab[0]
    if k == "COMPUTED_FROM":
        inner = canon(lab[1])
        if inner[0] == "COMPUTED": return inner
        if inner[0] == "CONST": return ("CONST",)
        return ("COMPUTED_FROM", inner)
    if k == "CONST": return ("CONST",)
    return lab


def rs(s): return frozenset(rl(b) for b in s)


def ns(s): return frozenset(nb_str(b) for b in s)


def main(path):
    R = load_ref()
    tot = Counter(); bad = Counter(); examples = {}
    for line in open(path):
        rec = json.loads(line); pre = ast.literal_eval(rec["pre"]) if isinstance(rec["pre"], str) else rec["pre"]
        ga, gb = bytes.fromhex(pre["ga"]), bytes.fromhex(pre["gb"])
        st_a = (pre["regs_a"],) + tuple(pre["flags_a"]); st_b = (pre["regs_b"],) + tuple(pre["flags_b"])
        r = R.trace_interaction(ga, gb, st_a, st_b, budget=pre["budget"], ops_mask=pre["ops_mask"])
        for h, side in enumerate("ab"):
            for x in rec["loci"][side]:
                j = x["j"]; y = r["loci"][h * R.N + j]
                if not y["written"]: cls = "unwritten"
                elif y["performer_entity"] is None: cls = "written_perf_none"
                elif y["performer_entity"] == y["store_by"]: cls = "written_self"
                else: cls = "written_other"
                checks = {"label_raw": nl(x["label"]) == rl(y["label"]), "label": canon(nl(x["label"])) == canon(rl(y["label"])),
                          "written": x["written"] == y["written"]}
                if y["written"] and x["written"]:
                    checks["store_by"] = x["store_by"] == y["store_by"]
                    pn = nl(x["performer"]) if x.get("performer") is not None else None
                    pr = rl(y["performer"]) if y["performer"] is not None else None
                    checks["performer_raw"] = pn == pr
                    checks["performer"] = canon(pn) == canon(pr)
                    checks["addr"] = ns(x["addr"]) == rs(y["addr_deps"])
                    checks["ctrl"] = ns(x["ctrl"]) == rs(y["ctrl_deps"])
                    checks["ctrl_slice(secondary)"] = ns(x["ctrl_slice"]) == rs(y["ctrl_deps_slice"])
                    checks["exec"] = ns(x["exec"]) == rs(y["exec_deps"])
                for f, ok in checks.items():
                    tot[(cls, f)] += 1
                    if not ok:
                        bad[(cls, f)] += 1
                        if (cls, f) not in examples:
                            examples[(cls, f)] = {"k": rec["k"], "half": side, "j": j,
                                                  "nestor": str(x.get({"label": "label", "performer": "performer", "addr": "addr", "ctrl": "ctrl",
                                                                       "ctrl_slice": "ctrl_slice", "exec": "exec"}.get(f, "written"))),
                                                  "reference": str({"label": R.fmt_label(y["label"]), "performer": R.fmt_label(y["performer"]),
                                                                    "addr": R.fmt_set(y["addr_deps"]), "ctrl": R.fmt_set(y["ctrl_deps"]),
                                                                    "ctrl_slice": R.fmt_set(y["ctrl_deps_slice"]), "exec": R.fmt_set(y["exec_deps"]),
                                                                    "written": y["written"], "store_by": y["store_by"]}.get(f, y.get(f)))}
    classes = sorted({c for c, _ in tot})
    fields = sorted({f for _, f in tot})
    worst = 1.0
    print("per class x field agreement (loci):")
    for c in classes:
        row = []
        for f in fields:
            if (c, f) in tot:
                a = 1 - bad[(c, f)] / tot[(c, f)]
                if f in GATED: worst = min(worst, a)
                row.append("%s %d/%d" % (f, tot[(c, f)] - bad[(c, f)], tot[(c, f)]))
        print("  %-18s %s" % (c, "; ".join(row)))
    print("minimum agreement over class x GATED field (canonical labels): %.4f  (gate >= 0.995); raw and secondary fields reported" % worst)
    for k, v in examples.items(): print("  DISAGREE", k, json.dumps(v)[:600])
    return 0 if worst >= 0.995 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else ARC + "/npe_fixture_validation/nestor_v2_FUZZ_AGREEMENT_nestor.jsonl"))
