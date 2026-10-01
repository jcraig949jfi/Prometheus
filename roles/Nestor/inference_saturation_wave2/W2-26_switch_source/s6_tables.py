"""W2-26 s6: aggregate s3 (switch-edge assay) into the source table; JSON only, no VM calls."""
import json, collections, pathlib
HERE = pathlib.Path(__file__).resolve().parent
R = json.loads((HERE / "s3_assay.json").read_text())["rows"]


def cat(r):
    if r["ndiff"] == 0:
        return "A no genotype change"
    if r["P_c0"] >= 0.5:
        return "B parent already side-0 converter (diffs irrelevant)"
    if r["k_c0"] < 0.5:
        return "C child not a static side-0 converter (context)"
    c = r["cause"]
    if c == "multi":
        return "D multi-byte (no single causal byte)"
    s = c["src"] if isinstance(c["src"], str) else "+".join(c["src"])
    if s == "CE" and c["bits"] == 1:
        return "E single-bit copy error at birth"
    if s in ("MB", "IM"):
        return "F _mutate"
    if s.startswith("IX"):
        return "G in-place execution write (partner/self, no relabel)"
    return "H partner-constructed / donor offset write at birth (%s)" % s


out = {}
for cls, sel in (("CTL", lambda r: r["cls"] == "CTL"), ("RUN_win", lambda r: r["cls"] == "RUN" and r["inwin"]),
                 ("RUN_all", lambda r: r["cls"] == "RUN")):
    rs = [r for r in R if sel(r)]
    t = collections.Counter()
    for r in rs:
        fam = "7ae3" if r["P_fam"] == "7ae3" else "non-7ae3"
        t[(fam, cat(r))] += 1
    out[cls] = {"n": len(rs), "table": {"%s | %s" % k: v for k, v in sorted(t.items())}}
    print("==", cls, len(rs))
    for k, v in sorted(t.items()):
        print("  %4d  %s | %s" % (v, k[0], k[1]))
# control in-context check: category C edges with actual ctx
for r in R:
    if r["cls"] == "CTL" and cat(r).startswith("C"):
        print("CTL C:", r["run"], r["k"], r["kk"], "k_c0", r["k_c0"], "k_c0_actctx", r["k_c0_actctx"], "k_c1", r["k_c1"], "P_c1", r["P_c1"])
(HERE / "s6_tables.json").write_text(json.dumps(out, indent=1))
