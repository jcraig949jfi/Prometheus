"""Fabric script Task: the NPE 1% production agreement sample (MWO-0001 ARCHAEON; operator decision 2026-09-28: a Fabric Task with
host affinity to the node holding the sample, no SSH trust between hosts). Committed BEFORE any sample content is read.

Stage 1: the pre-read verification. Task v2 uses npe_sample_verify_v2 (addendum 5: content identity; v1 efd7295a0 was strict
  on the gz bytes).
- Every file named in the pinned manifest (81895e729, sha256 e1584484...) must match its gz sha256, its uncompressed sha256 and
  its record count.
- On failure the Task writes VERIFY.txt and exits 1. Stage 2 never runs.

Stage 2 (only on PASS): the frozen reference (ref_tracer_npe.py 15737444...) against the owner's per-locus output in the sample.
- Rule: v4 s4.3, RAW, per class, >= 0.995, on label, addr, ctrl and exec. The same logic as npe_fresh_compare.
- **Accepted record schema, declared now:** one JSON object per line with
  * "pre" (the fuzz pre-state dict, or its repr);
  * "loci" ({"a": [...], "b": [...]} in the owner's export shape);
  * optional "k";
  * optional "wb_seed" + "mut_rate", as in the fresh sets.
- Any other key (for example persisted register labels or an RNG state) means SCHEMA_UNDECLARED. The Task exits 2 and reports
  KEY NAMES ONLY. The schema is then declared in a dated amendment before any rerun; no guessing.

Location: the sample directory is resolved from the allow-listed env var NPE_SAMPLE_DIR, set by whoever runs the host's worker.
- It is never guessed. If it is unset, the Task exits 3.

Outputs go to $FABRIC_OUT_DIR: VERIFY.txt, AGREEMENT.txt, DISCREPANCIES.jsonl and RESULT_SHA256.txt (sha256 of AGREEMENT.txt).
    python -m archaeon.attribution.probes.npe_sample_task
"""
import ast
import contextlib
import gzip
import hashlib
import io
import json
import os
import random
import sys
from collections import Counter

ALLOWED = {"pre", "loci", "k", "wb_seed", "mut_rate"}
# SCHEMA DECLARATION (2026-09-29, MWO-0004 G2 R1; after stage 1 PASSED and stage 2 stopped SCHEMA_UNDECLARED, Nestor #990;
# declared from the owner's committed writer tracer/run_trace.py sink(), with NO sample content read by Archaeon):
# the production 1% sample record is {run, iid, oids, pre, rng_state_at_writeback, accepted_sides, loci}.
#   - loci labels are POST-WRITE-BACK (run_trace.py: post[side][0]), so the reference replays the write-back from
#     rng_state_at_writeback ([version, state list, gauss]) at the reference's T-003 cell rate (MUT_RATE; its selftest F11
#     reproduces real T-003 interactions including the write-back and the RNG state).
#   - oids / run / iid / accepted_sides are identifiers or interaction-level outputs: carried in discrepancy records, not
#     compared (accepted_sides is not gated by v4 s4.3).
PRODUCTION = {"run", "iid", "oids", "pre", "rng_state_at_writeback", "accepted_sides", "loci"}
GATE = ("label", "addr", "ctrl", "exec")


def main():
    out = os.environ.get("FABRIC_OUT_DIR") or "."
    d = os.environ.get("NPE_SAMPLE_DIR")
    if not d or not os.path.isdir(d):
        open(os.path.join(out, "VERIFY.txt"), "w").write("NPE_SAMPLE_DIR unset or not a directory: %r\n" % d)
        return 3
    from archaeon.attribution.probes import npe_sample_verify_v2 as V        # addendum 5 content identity (Task v2)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = V.main(d)
    open(os.path.join(out, "VERIFY.txt"), "w").write(buf.getvalue())
    if rc != 0:
        return 1
    # ---- stage 2: only after verification passed
    from archaeon.attribution.probes.npe_fresh_ref import R, lab, b
    from archaeon.attribution.probes.npe_fresh_compare import cls_of
    from archaeon.attribution.probes.npe_fuzz_agreement import nl, ns
    files = sorted(f for f in os.listdir(d) if f.endswith(".sample1pct.jsonl.gz"))
    tot = Counter(); bad = Counter(); disc = []
    for f in files:
        for n, line in enumerate(gzip.open(os.path.join(d, f), "rt")):
            rec = json.loads(line)
            prod = set(rec) == PRODUCTION
            extra = set(rec) - (PRODUCTION if prod else ALLOWED)
            if extra or "pre" not in rec or "loci" not in rec:
                open(os.path.join(out, "AGREEMENT.txt"), "w").write(
                    "SCHEMA_UNDECLARED in %s line %d: keys %s (declared %s)\n" % (f, n, sorted(rec), sorted(ALLOWED)))
                return 2
            p = ast.literal_eval(rec["pre"]) if isinstance(rec["pre"], str) else rec["pre"]
            if prod:
                st = rec["rng_state_at_writeback"]; g = random.Random(); g.setstate((st[0], tuple(st[1]), st[2]))
                kw = {"rng": g}                                  # reference default cell rate (T-003)
            else:
                kw = {"rng": random.Random(rec["wb_seed"]), "mut_rate": rec["mut_rate"]} if "wb_seed" in rec else {}
            r = R.trace_interaction(bytes.fromhex(p["ga"]), bytes.fromhex(p["gb"]), (p["regs_a"],) + tuple(p["flags_a"]),
                                    (p["regs_b"],) + tuple(p["flags_b"]), budget=p["budget"], ops_mask=p["ops_mask"], **kw)
            for h, side in enumerate("ab"):
                for x in rec["loci"][side]:
                    y0 = r["loci"][h * R.N + x["j"]]
                    y = {"written": y0["written"], "store_by": y0["store_by"], "performer": lab(y0["performer"]),
                         "label": lab(y0["label"]), "addr": sorted(b(q) for q in y0["addr_deps"]),
                         "ctrl": sorted(b(q) for q in y0["ctrl_deps"]), "exec": sorted(b(q) for q in y0["exec_deps"])}
                    c = cls_of(y)
                    chk = {"label": nl(x["label"]) == nl(y["label"]), "addr": ns(x["addr"]) == ns(y["addr"]),
                           "written": x["written"] == y["written"]}
                    if x["written"] and y["written"]:
                        chk.update({"ctrl": ns(x["ctrl"]) == ns(y["ctrl"]), "exec": ns(x["exec"]) == ns(y["exec"])})
                    else:
                        chk.update({"ctrl": x["written"] == y["written"], "exec": x["written"] == y["written"]})
                    for k, ok in chk.items():
                        tot[(c, k)] += 1; bad[(c, k)] += not ok
                    if not all(chk.values()):
                        disc.append({"file": f, "line": n, "iid": rec.get("iid"), "half": side, "j": x["j"], "class": c,
                                     "fields": sorted(k for k, ok in chk.items() if not ok)})
    lines = ["NPE 1% production agreement sample: frozen reference vs owner, RAW per class (v4 s4.3)"]
    fails = []
    for c in sorted({c for c, _ in tot}):
        row = []
        for k in sorted({k for cc, k in tot if cc == c}):
            a = 1 - bad[(c, k)] / tot[(c, k)]
            if k in GATE and a < 0.995: fails.append("%s/%s %.4f" % (c, k, a))
            row.append("%s %d/%d" % (k, tot[(c, k)] - bad[(c, k)], tot[(c, k)]))
        lines.append("  %-18s %s" % (c, "; ".join(row)))
    lines.append("discrepant loci: %d" % len(disc))
    lines.append("AGREEMENT (gate): %s" % ("PASS" if not fails else "FAIL on " + ", ".join(fails)))
    txt = "\n".join(lines) + "\n"
    open(os.path.join(out, "AGREEMENT.txt"), "w", newline="\n").write(txt)
    with open(os.path.join(out, "DISCREPANCIES.jsonl"), "w", newline="\n") as fh:
        for x in disc: fh.write(json.dumps(x, sort_keys=True) + "\n")
    open(os.path.join(out, "RESULT_SHA256.txt"), "w").write(hashlib.sha256(txt.encode()).hexdigest() + "  AGREEMENT.txt\n")
    return 0 if not fails else 4


if __name__ == "__main__":
    sys.exit(main())
