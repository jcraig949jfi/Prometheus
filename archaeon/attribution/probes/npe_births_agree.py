"""E-003 NPE: the PREREGISTERED production tracer-agreement check (v4 s4.3 on the s4 sample; v4 s4-s5: every birth is in the
sample). The frozen reference (ref_tracer_npe.py, sha256 15737444...) is run against the owner's per-locus output for every
production birth of run 2 (Nestor 81895e729, exports/*.births.jsonl, committed in git).

Committed BEFORE its first run. Declared:
- **Scope:** the victim half's 32 loci per birth, BEFORE write-back mutation (C7.3). The reference runs each record's "pre"
  without an RNG.
- **Engine sanity:** the reference's post bytes for the victim half must equal "victim_final_pre_mutation". Otherwise the birth
  is an ENGINE MISMATCH and stops the check.
- **Class key per locus:** as G2, performer entity vs store_by (self / other / written_perf_none / unwritten). The owner's
  store_by is "store_side".
- **Gate (v4 s4.3):** RAW, per class, >= 0.995, on label, addr, ctrl and exec. The owner's fields are ctrl_at_store and
  exec_at_store. written, store_by and performer are reported.
- **Unit (C7.4):** the gate is evaluated on the 29 DISTINCT births (duplicate simulations s9200006 C and s9200008 C are
  excluded). All 34 are reported alongside.
- **Secondary:** ctrl_slice_at_store is reported, not gated (S3 is open).
- **Stated limit:** this check does not read any Q, verdict or layer field; only the pre-state, loci and victim bytes.
    python -m archaeon.attribution.probes.npe_births_agree EXPORTS_DIR OUTDIR
"""
import json
import os
import sys
from collections import Counter

from archaeon.attribution.probes.npe_fresh_ref import R, lab, b
from archaeon.attribution.probes.npe_fresh_compare import cls_of
from archaeon.attribution.probes.npe_fuzz_agreement import nl, ns

GATE = ("label", "addr", "ctrl", "exec")
DUP = ("__s9200006__C_", "__s9200008__C_")


def main(d, outdir):
    files = sorted(f for f in os.listdir(d) if f.endswith(".births.jsonl"))
    tot = {"distinct": Counter(), "all34": Counter()}; bad = {"distinct": Counter(), "all34": Counter()}
    disc = []; nb = Counter()
    for f in files:
        dup = any(t in f for t in DUP)
        for n, line in enumerate(open(os.path.join(d, f))):
            rec = json.loads(line); p = rec["pre"]
            r = R.trace_interaction(bytes.fromhex(p["ga"]), bytes.fromhex(p["gb"]), (p["regs_a"],) + tuple(p["flags_a"]),
                                    (p["regs_b"],) + tuple(p["flags_b"]), budget=p["budget"], ops_mask=p["ops_mask"])
            h = "ab".index(rec["victim_side"])
            post = bytes(r["loci"][h * R.N + j]["post"] for j in range(R.N)).hex()
            if post != rec["victim_final_pre_mutation"]:
                print("ENGINE MISMATCH", f, n); return 3
            nb["all34"] += 1; nb["distinct"] += not dup
            for x in rec["loci"]:
                y0 = r["loci"][h * R.N + x["j"]]
                y = {"written": y0["written"], "store_by": y0["store_by"], "performer": lab(y0["performer"]),
                     "label": lab(y0["label"])}
                c = cls_of(y)
                chk = {"label": nl(x["label"]) == nl(y["label"]),
                       "addr": ns(x["addr"]) == ns(sorted(b(q) for q in y0["addr_deps"])),
                       "written": x["written"] == y["written"]}
                if x["written"] and y["written"]:
                    chk.update({"ctrl": ns(x["ctrl_at_store"]) == ns(sorted(b(q) for q in y0["ctrl_deps"])),
                                "exec": ns(x["exec_at_store"]) == ns(sorted(b(q) for q in y0["exec_deps"])),
                                "store_by": x.get("store_side") == y["store_by"],
                                "performer": (nl(x["performer"]) if x.get("performer") else None) == (nl(y["performer"]) if y["performer"] else None),
                                "ctrl_slice(secondary)": ns(x["ctrl_slice_at_store"]) == ns(sorted(b(q) for q in y0["ctrl_deps_slice"]))})
                else:
                    chk.update({"ctrl": x["written"] == y["written"], "exec": x["written"] == y["written"]})
                for scope in (("all34", "distinct") if not dup else ("all34",)):
                    for k, ok in chk.items():
                        tot[scope][(c, k)] += 1; bad[scope][(c, k)] += not ok
                if not all(chk.values()):
                    disc.append({"file": f, "line": n, "dup": dup, "j": x["j"], "class": c,
                                 "fields": sorted(k for k, ok in chk.items() if not ok),
                                 "owner": {k: x.get(k) for k in ("label", "performer", "store_side")},
                                 "reference": {"label": R.fmt_label(y0["label"]), "store_by": y0["store_by"],
                                               "performer": R.fmt_label(y0["performer"]) if y0["performer"] else None}})
    lines = ["E-003 NPE production tracer agreement (v4 s4.3): frozen reference vs owner run 2, RAW, victim half pre-mutation",
             "births: %d distinct / %d all" % (nb["distinct"], nb["all34"])]
    fails = []
    for scope in ("distinct", "all34"):
        lines.append("[%s]" % scope)
        for c in sorted({c for c, _ in tot[scope]}):
            row = []
            for k in sorted({k for cc, k in tot[scope] if cc == c}):
                t = tot[scope][(c, k)]; a = 1 - bad[scope][(c, k)] / t
                if scope == "distinct" and k in GATE and a < 0.995: fails.append("%s/%s %.4f" % (c, k, a))
                row.append("%s %d/%d" % (k, t - bad[scope][(c, k)], t))
            lines.append("  %-18s %s" % (c, "; ".join(row)))
    lines += ["discrepant loci (all 34): %d" % len(disc),
              "s4.3 GATE on distinct births: %s" % ("PASS" if not fails else "FAIL on " + ", ".join(fails))]
    os.makedirs(outdir, exist_ok=True)
    open(os.path.join(outdir, "BIRTHS_AGREEMENT.txt"), "w", newline="\n").write("\n".join(lines) + "\n")
    with open(os.path.join(outdir, "BIRTHS_DISCREPANCIES.jsonl"), "w", newline="\n") as fh:
        for x in disc: fh.write(json.dumps(x, sort_keys=True) + "\n")
    print("\n".join(lines))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
