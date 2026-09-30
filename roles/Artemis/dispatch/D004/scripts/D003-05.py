"""D003-05 decisive probe. Run from a checkout of Prometheus @ b960d1a42600e17128f6270282b30e8e6abb5086 (repo root on sys.path):
    python out/analysis.py
Inputs: archaeon/attribution/schema.py, fixtures.py, regression.py @ b960d1a42.
Also run:  pytest archaeon/tests/test_attribution_v0.py -k th014   (must all pass for the REPORT's "yes" to hold).

Decision rules (printed at the end):
  G1  transplant / inflow leaky variants (built exactly like fixtures.th014_leaky_variants) are ALL rejected
      -> coverage generalises beyond the 3 tested channels (REPORT s3.3 hand-trace confirmed).
  G2  mis-logged leak with a NON-infrastructure material via (provenance_log, by_construction, taint) is ACCEPTED (no violations)
      -> residual hole in REPORT s3.4 confirmed; if REJECTED, that claim is wrong.
"""
import copy

from archaeon.attribution import schema as S, fixtures as F

NI = S.NI


def infra_record(proc, kind, via="harness_log"):
    return F.base("probe." + proc, "C", [F.perf(kind, kind)], proc, F.mat(S.seg(0, 32, entity="P", src_lo=0, via=via)))


def leaky(r):
    out = {}
    a = copy.deepcopy(r); a["aggregation"] = [{"label": "SELF_COPY", "rule": "native_flag", "convention": False}]; out["SELF_LABEL"] = a
    b = copy.deepcopy(r); b["carrier"] = {"performers": [F.perf("organism_code", "P")], "exec_where": NI, "exec_what": NI}
    out["ORGANISM_CARRIER"] = b
    c = copy.deepcopy(b); c["production"] = {"process": "executed_write", "evidence": "mis-logged"}
    c["aggregation"] = [{"label": "SELF_COPY", "rule": "native_flag", "convention": False}]; out["MISLOGGED_CHANNEL"] = c
    return out


g1 = True
for proc, kind in (("transplant_insertion", "transplant"), ("inflow_injection", "inflow")):
    base = infra_record(proc, kind)
    print(proc, "clean:", S.check(base))
    for name, r in leaky(base).items():
        v = S.check(r)
        print("  +%s -> %s" % (name, v))
        g1 &= bool(v)

g2_accepted = []
for via in ("provenance_log", "by_construction", "taint"):
    r = F.base("probe.mislog." + via, "C", [F.perf("organism_code", "P")], "executed_write",
               F.mat(S.seg(0, 32, entity="P", src_lo=0, via=via)))
    r["aggregation"] = [{"label": "SELF_COPY", "rule": "native_flag", "convention": False}]
    v = S.check(r)
    print("mislogged via=%s -> %s" % (via, v))
    if not v: g2_accepted.append(via)

print("G1 transplant/inflow leaks all rejected:", g1)
print("G2 mis-logged leaks ACCEPTED for via:", g2_accepted, "(non-empty => residual hole confirmed)")
