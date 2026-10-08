"""X-ARCH-COMPETE reducer: CT_W-family share of final competent organisms (nearer construct by Hamming)."""
import gzip, json, pathlib, sys
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import exp, fh
CTUA, CTW = fh.PLANTS["CT_UA"], exp.CT_W


def ham(a, b):
    return sum(x != y for x, y in zip(a, b))


def main():
    d = HERE / "runs" / "X-ARCH-COMPETE"
    out = {}
    for p in sorted(d.glob("AC_*.json")):
        if p.name.endswith(".detail.json.gz") or p.name == "AC_REDUCED.json":
            continue
        r = json.loads(p.read_text())
        det = json.load(gzip.open(d / ("%s_%d.detail.json.gz" % (r["arm"], r["seed"])), "rt"))
        w = u = 0
        for h, c in det["competent_genomes_final"].items():
            g = bytes.fromhex(h)
            if ham(g, CTW) < ham(g, CTUA):
                w += c
            else:
                u += c
        tot = w + u
        out.setdefault(r["arm"], []).append({"seed": r["seed"], "first_plant": "CT_UA" if r["seed"] % 2 == 0 else "CT_W",
                                             "CS": r["CS"], "ctw_share": round(w / tot, 3) if tot else None,
                                             "n_comp": tot})
    res = {}
    for arm, rows in out.items():
        ok = [x for x in rows if x["ctw_share"] is not None]
        res[arm] = {"runs": rows, "runs_with_final_competence": len(ok),
                    "ctw_majority": sum(x["ctw_share"] > 0.5 for x in ok),
                    "median_ctw_share": sorted(x["ctw_share"] for x in ok)[len(ok) // 2] if ok else None}
    (d / "AC_REDUCED.json").write_text(json.dumps(res, indent=1))
    for arm, v in res.items():
        print(arm, "runs w/ competence", v["runs_with_final_competence"], "CT_W majority", v["ctw_majority"],
              "median CT_W share", v["median_ctw_share"],
              [(x["first_plant"], x["ctw_share"]) for x in v["runs"]])


if __name__ == "__main__":
    main()
