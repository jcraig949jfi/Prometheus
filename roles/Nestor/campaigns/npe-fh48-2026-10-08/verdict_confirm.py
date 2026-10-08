"""Apply a CONFIRM node's frozen rule (as declared in exp.py at the protocol commit).  python -B verdict_confirm.py <EXP>"""
import gzip, json, pathlib, sys
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def rows(exp):
    d = HERE / "runs" / exp
    return [json.loads(p.read_text()) for p in sorted(d.glob("*.json"))
            if not p.name.startswith(("RECEIPT", "REDUCED", "VERDICT", "AC_", "LONG_", "SURFACE", "ARCH_", "MINE_"))]


def c_ontape():
    rr = rows("C-ONTAPE-MAINTAIN")
    by = {}
    for r in rr:
        by.setdefault(r["arm"], []).append(r)
    est = {a: [r for r in v if r["depth"] >= 20] for a, v in by.items()}
    on = sum(r["TCS"] >= 0.10 for r in est["ONTAPE"])
    rnd = sum(r["TCS"] >= 0.10 for r in est["ONTAPE_RND"])
    neg = {a: sum(r["TCS"] >= 0.10 or r["CS"] >= 0.10 for r in by[a]) for a in ("NEG_CTU_ONTAPE", "NEG_COPY_ONTAPE")}
    ok = on >= 0.75 * len(est["ONTAPE"]) and rnd <= 1 and not any(neg.values())
    return {"verdict": "CONFIRMED" if ok else "NOT_CONFIRMED",
            "ONTAPE_established": len(est["ONTAPE"]), "ONTAPE_TCS_maintained": on,
            "ONTAPE_RND_established": len(est["ONTAPE_RND"]), "ONTAPE_RND_TCS_maintained": rnd, "negatives_failing": neg,
            "ONTAPE_final_TCS": sorted(round(r["TCS"], 3) for r in est["ONTAPE"]),
            "ONTAPE_final_CS_offline": sorted(round(r["CS"], 3) for r in est["ONTAPE"]),
            "ONTAPE_tape_only_final": sorted(round(r["tape_classes"]["tape_only"], 3) for r in est["ONTAPE"]),
            "rule": "ONTAPE TCS>=0.10 in >=75% established; ONTAPE_RND <=1; no negative with TCS or CS >=0.10"}


def c_arch():
    import ac_analyze, exp, fh
    CTUA, CTW = fh.PLANTS["CT_UA"], exp.CT_W
    d = HERE / "runs" / "C-ARCH-COMPETE"
    res = []
    for r in rows("C-ARCH-COMPETE"):
        det = json.load(gzip.open(d / ("%s_%d.detail.json.gz" % (r["arm"], r["seed"])), "rt"))
        w = u = 0
        for h, c in det["competent_genomes_final"].items():
            g = bytes.fromhex(h)
            if ac_analyze.ham(g, CTW) < ac_analyze.ham(g, CTUA):
                w += c
            else:
                u += c
        res.append({"seed": r["seed"], "CS": r["CS"], "ctw_share": round(w / (w + u), 3) if w + u else None})
    comp = [x for x in res if x["ctw_share"] is not None]
    maj = sum(x["ctw_share"] > 0.5 for x in comp)
    ok = len(comp) >= 6 and maj >= 8
    return {"verdict": "CONFIRMED" if ok else "NOT_CONFIRMED", "runs_with_competence": len(comp), "ctw_majority": maj,
            "runs": res, "rule": "CT_W family > 0.5 in >= 8 runs ending with competence (>= 6 such runs)"}


if __name__ == "__main__":
    exp = sys.argv[1]
    v = {"C-ONTAPE-MAINTAIN": c_ontape, "C-ARCH-COMPETE": c_arch}[exp]()
    (HERE / "runs" / exp / "VERDICT.json").write_text(json.dumps(v, indent=1))
    print(json.dumps(v, indent=1))
