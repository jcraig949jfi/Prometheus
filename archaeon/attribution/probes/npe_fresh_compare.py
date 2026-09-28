"""G2 FRESH-set comparison, exactly as declared in gate_close/FRESH_SET_COMPARISON_DECLARATION.md. Committed BEFORE Nestor's sealed
output is opened.

Both outputs are in Nestor's export shape, so both are parsed with the SAME parser (npe_fuzz_agreement.nl / ns).
- RAW equality; there is no canonicalization.
- Gate: v4 s4.3, per class (the reference's performer class), >= 0.995, on label, addr, ctrl and exec, for sets A and M
  separately.
- Diagnostics d1-d4 as declared.
    python -m archaeon.attribution.probes.npe_fresh_compare REF.jsonl.gz NESTOR.jsonl[.gz] OUTDIR
"""
import gzip
import hashlib
import json
import os
import sys
from collections import Counter

from archaeon.attribution.probes.npe_fuzz_agreement import nl, ns

GATE = ("label", "addr", "ctrl", "exec")
SEALED = {"ref": "9fd3bc4486ba8dc5445da7d1d1db2f26eae9765365cbaee3db4ff5a6fb90eeb5",
          "nestor": "c6aa5569a43321526e761904a158871f300b616500e3fedfbc8c9cad084f8e75"}


def set_sealed(path):
    """Set 2 onward: the sealed hashes come from a committed JSON {"ref": sha, "nestor": sha, "label": str}."""
    d = json.load(open(path)); SEALED.update({"ref": d["ref"], "nestor": d["nestor"]}); return d.get("label", "")


def load(path, who):
    raw = (gzip.open if path.endswith(".gz") else open)(path, "rb").read()
    h = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()
    assert h == SEALED[who], "%s output hash %s != sealed %s" % (who, h, SEALED[who])
    return {r["k"]: r for r in (json.loads(l) for l in raw.decode().splitlines() if l.strip())}


def cls_of(y):
    if not y["written"]: return "unwritten"
    p = y.get("performer")
    if p is None or p[0] != "E": return "written_perf_none"
    return "written_self" if p[1] == y["store_by"] else "written_other"


def mut_old(lab):
    """old_label of a MUTATION label in either declared encoding (for diagnostic d2 only)."""
    if lab[0] != "M": return None
    return lab[2] if isinstance(lab[1], list) else lab[4]


def main(refp, nesp, outdir):
    R = load(refp, "ref"); N = load(nesp, "nestor")
    assert sorted(R) == sorted(N) == list(range(400)), "record sets differ"
    tot = Counter(); bad = Counter(); disc = []
    for k in sorted(R):
        st = R[k]["set"]
        for side in "ab":
            for y, x in zip(R[k]["loci"][side], N[k]["loci"][side]):
                assert y["j"] == x["j"]
                c = cls_of(y); mut = bool(y.get("mutated")) or (x.get("label") or [None])[0] == "M"
                chk = {"label": nl(x["label"]) == nl(y["label"]), "addr": ns(x["addr"]) == ns(y["addr"]),
                       "written": x["written"] == y["written"]}
                if x["written"] and y["written"]:
                    chk.update({"ctrl": ns(x["ctrl"]) == ns(y["ctrl"]), "exec": ns(x["exec"]) == ns(y["exec"]),
                                "d4:store_by": x["store_by"] == y["store_by"],
                                "d4:performer": (nl(x["performer"]) if x.get("performer") else None) == (nl(y["performer"]) if y.get("performer") else None),
                                "d3:ctrl_slice": ns(x["ctrl_slice"]) == ns(y["ctrl_slice"])})
                elif x["written"] or y["written"]:
                    chk.update({"ctrl": False, "exec": False})
                else:
                    chk.update({"ctrl": True, "exec": True})
                keys = [(st, c, f) for f in chk]
                if not mut: keys += [(st + ":d1_nonmutated", c, f) for f in chk]
                else:
                    ym, xm = y["label"], x["label"]
                    d2 = ym[0] == "M" and xm[0] == "M" and nl(mut_old(ym)) == nl(mut_old(xm))
                    keys += [(st + ":d2_MUTATION_content", "mutated", "flag+side+pos+old_label")]
                    chk["flag+side+pos+old_label"] = d2
                for key in keys:
                    tot[key] += 1
                    if not chk[key[2]]: bad[key] += 1
                if not all(v for f, v in chk.items()):
                    disc.append({"k": k, "set": st, "half": side, "j": y["j"], "class": c, "mutated": mut,
                                 "fields": sorted(f for f, v in chk.items() if not v),
                                 "nestor": {f: x.get(f) for f in ("label", "performer", "ctrl_slice")},
                                 "reference": {f: y.get(f) for f in ("label", "performer", "ctrl_slice")}})
    lines = ["G2 FRESH SET: reference sha %s vs Nestor sha %s (sealed output hashes); RAW, as declared before opening" % (SEALED["ref"][:12], SEALED["nestor"][:12]), ""]
    fails = []
    for grp in sorted({g for g, _, _ in tot}):
        lines.append(grp)
        for c in sorted({c for g, c, _ in tot if g == grp}):
            row = []
            for f in sorted({f for g, cc, f in tot if g == grp and cc == c}):
                n = tot[(grp, c, f)]; a = 1 - bad[(grp, c, f)] / n
                gate = grp in ("A", "M") and f in GATE
                if gate and a < 0.995: fails.append("%s/%s/%s %.4f" % (grp, c, f, a))
                row.append("%s %d/%d%s" % (f, n - bad[(grp, c, f)], n, " FAIL" if gate and a < 0.995 else ""))
            lines.append("  %-18s %s" % (c, "; ".join(row)))
    lines += ["", "discrepant loci: %d (FRESH_DISCREPANCIES.jsonl)" % len(disc),
              "G2 FRESH (gate, raw, per class, sets A and M): %s" % ("PASS" if not fails else "FAIL on " + ", ".join(fails))]
    os.makedirs(outdir, exist_ok=True)
    open(os.path.join(outdir, "FRESH_AGREEMENT.txt"), "w", newline="\n").write("\n".join(lines) + "\n")
    with open(os.path.join(outdir, "FRESH_DISCREPANCIES.jsonl"), "w", newline="\n") as fh:
        for d in disc: fh.write(json.dumps(d, sort_keys=True) + "\n")
    print("\n".join(lines))
    return 0 if not fails else 1


if __name__ == "__main__":
    if len(sys.argv) > 4: set_sealed(sys.argv[4])                       # set 2+: SEALED_HASHES.json
    sys.exit(main(*sys.argv[1:4]))
