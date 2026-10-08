"""DEF-FH-4 post-hoc rescoring: corrected on-tape homotypic ruler on the SAVED final genomes (offline-competent +
tape-only). Organisms in the old 'neither' class were not saved, so corrected TCS is a LOWER BOUND.
Frozen verdicts are not changed; this is reported beside them."""
import gzip, json, pathlib, sys
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arch, fh

C = fh.UseCache()


def rescore(exp):
    d = HERE / "runs" / exp
    out = []
    for p in sorted(d.glob("*.json")):
        if p.name.startswith(("RECEIPT", "VERDICT", "REDUCED", "RESCORE")) or p.name.endswith(".gz"):
            continue
        r = json.loads(p.read_text())
        if r.get("TCS") is None:
            continue
        det = json.load(gzip.open(d / ("%s_%d.detail.json.gz" % (r["arm"], r["seed"])), "rt"))
        saved = dict(det["competent_genomes_final"])
        for h, c in det.get("tape_only_genomes_final", {}).items():
            saved[h] = saved.get(h, 0) + c
        cache = {}
        n_ok = n_tonly = n_offonly = 0
        for h, c in saved.items():
            g = bytes.fromhex(h)
            if h not in cache:
                cache[h] = arch.tape_use(g, g) >= fh.COMP_MIN
            off = C.competent(g)
            if cache[h]:
                n_ok += c
                n_tonly += c * (not off)
            elif off:
                n_offonly += c
        a = r["alive"]
        out.append({"arm": r["arm"], "seed": r["seed"], "TCS_old": r["TCS"], "TCS_corrected_lb": round(n_ok / a, 4),
                    "tape_only_corrected_lb": round(n_tonly / a, 4), "offline_only_corrected": round(n_offonly / a, 4),
                    "CS": r["CS"], "established": r["depth"] >= 20})
    (d / "RESCORE_DEF-FH-4.json").write_text(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    for exp in sys.argv[1:]:
        rows = rescore(exp)
        for x in rows:
            if x["arm"].startswith(("ONTAPE", "ONTAPE_LONG")) and x["established"]:
                print(exp, x["arm"], x["seed"], "TCS old", x["TCS_old"], "corrected>=", x["TCS_corrected_lb"],
                      "tape_only>=", x["tape_only_corrected_lb"], "offline_only", x["offline_only_corrected"], "CS", x["CS"])
        neg = [x for x in rows if x["arm"].startswith("NEG")]
        if neg:
            print(exp, "negatives corrected TCS max:", max(x["TCS_corrected_lb"] for x in neg))
