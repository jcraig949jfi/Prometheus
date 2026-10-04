"""TEST-5 (Beta-01): R7 IMPROVER-MUTABILITY PROBE -- W4 GTC (genome transfer-correlation), bounded version.
Frozen spec: beta01/windows/T05_GTC_SPEC.md. Genomes in gtc.py; donor_g('g0') == a18.donor (gate passed 3/3 in DEV-5).

Supplies: T51's qualified LIN foundry (escrow 30k, same instruments). Strata by the body's top-level operator:
  DEV    = {+, -}
  UNSEEN = {*, //, %, gcd, pow}
Chain c (c = 0..3): generation 1 on seed c, generation 2 on seed c+4.
  gen 1: donor_g(genome), start PRISTINE (kind P, composition ON; LGG + nothing to compose), OBSERVE 4 (DEV floor
         0 < p <= .75) + VALIDATE 4 (DEV head) from seed c
  gen 2: donor_g(genome), start = gen-1 SELECTED library, OBSERVE 4 + VALIDATE 4 (DEV) from seed c+4
Scoring (both generations, on seed c+4 held-out families never used in any role):
  12 DEV-held + 8 UNSEEN families, 1 cell each, D endpoint (first T4-v1a-qualified program, cap 1M).
  value = number of families solved below the cap. PRISTINE is the reference.
Stages: plan | run [w] | score [w] | report.
"""
import os
os.environ["V2B_T51_DIR"] = "T04_T51"
import json  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402

import t51_natural as T  # noqa: E402  (escrow 30k worker init, foundry, panel)
import gtc  # noqa: E402
import a17  # noqa: E402
from a18 import FR  # noqa: E402
import identity as I  # noqa: E402
import instruments as INS  # noqa: E402
import walk  # noqa: E402
import apparatus  # noqa: E402

OUT = T.paths.ROOT / "beta01" / "runs" / os.environ.get("V2B_GTC_DIR", "T05_GTC")
GEN = ["g0", "g2", "g3", "g4", "g5"]
CHAINS = [(0, 4), (1, 5), (2, 6), (3, 7)]
CAP = int(os.environ.get("V2B_GTC_CAP", 1_000_000))
N_DEVH, N_UNS = 12, 8


def log(m):
    print("[GTC %s] %s" % (time.strftime("%H:%M:%S", time.gmtime()), m), flush=True)


def wr(n, o):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / n).write_text(json.dumps(o, sort_keys=True, default=str), encoding="utf-8")


def rd(n):
    return json.loads((OUT / n).read_text(encoding="utf-8"))


def rdl(n):
    p = OUT / n
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.exists() else []


def stratum(body):
    return "DEV" if gtc._top_op(body) in ("+", "-") else "UNSEEN"


def stage_plan():
    T.init_worker()
    rows = T.rdl("T51_FOUNDRY.jsonl")
    plan = {"chains": {}, "panel": T.rd("T51_PLAN.json")["panel"], "apparatus": apparatus.manifest("v1a", "v2.1"),
            "cap": CAP}
    for c, (s1, s2) in enumerate(CHAINS):
        roles = {}
        for s in (s1, s2):
            rng = random.Random(I._seed("APHRODITE/GTC/ROLES/%d" % s))
            q = sorted([r for r in rows if r.get("T4_qualified") and r["source"] == "LIN:%d" % s
                        and r.get("p_PRISTINE", 0) <= 0.75], key=lambda r: r["name"])
            dev = [r for r in q if stratum(r["body"]) == "DEV"]
            floor = [r for r in dev if r["p_PRISTINE"] > 0]
            rng.shuffle(floor)
            obs = floor[:4]
            rest = [r for r in dev if r["name"] not in {x["name"] for x in obs}]
            rng.shuffle(rest)
            val = rest[:4]
            fams = [dict(r, role="OBSERVE") for r in obs] + [dict(r, role="VALIDATE") for r in val]
            roles[s] = {"fams": fams, "ok": len(obs) == 4 and len(val) == 4}
            if s == s2:
                used = {x["name"] for x in fams}
                dh = [r for r in rest[4:] if r["name"] not in used]
                uns = [r for r in q if stratum(r["body"]) == "UNSEEN"]
                rng.shuffle(uns)
                roles["score"] = {"DEV": dh[:N_DEVH], "UNSEEN": uns[:N_UNS],
                                  "ok": len(dh) >= N_DEVH and len(uns) >= N_UNS}
        plan["chains"][str(c)] = {"s1": s1, "s2": s2, "roles": {str(k): v for k, v in roles.items()}}
    wr("GTC_PLAN.json", plan)
    log("plan: %s" % {c: (v["roles"][str(v["s1"])]["ok"], v["roles"][str(v["s2"])]["ok"], v["roles"]["score"]["ok"])
                      for c, v in plan["chains"].items()})


def _fl(fams):
    fl = [dict(f, qualified_dev_size=f["Q2_size"]) for f in fams]
    return fl, {f["name"]: (f["body"], f["final"], f["init"]) for f in fl}


def _chain(a):
    T.init_worker()
    c, genome, ch, panel = a
    fl1, sp1 = _fl(ch["roles"][str(ch["s1"])]["fams"])
    d1 = gtc.donor_g(genome, ("GTC%d" % ch["s1"], "P", ch["s1"], fl1, sp1, panel, True))
    fl2, sp2 = _fl(ch["roles"][str(ch["s2"])]["fams"])
    d2 = gtc.donor_g(genome, ("GTC%d" % ch["s2"], "P", ch["s2"], fl2, sp2, panel, True, d1["selected_entries"]))
    strip = lambda d: {k: d[k] for k in ("selected", "selected_schema", "selected_entries", "n_derived",  # noqa: E731
                                         "n_observed", "classes", "meta_charges", "seconds")}
    return {"chain": c, "genome": genome, "gen1": strip(d1), "gen2": strip(d2)}


def stage_run(w=4):
    plan = rd("GTC_PLAN.json")
    done = {(x["chain"], x["genome"]) for x in rdl("GTC_CHAINS.jsonl")}
    jobs = [(int(c), g, ch, plan["panel"]) for c, ch in plan["chains"].items() for g in GEN
            if (int(c), g) not in done]
    log("chain jobs %d" % len(jobs))
    with open(OUT / "GTC_CHAINS.jsonl", "a", encoding="utf-8") as fh, \
            ProcessPoolExecutor(max_workers=w, initializer=T.init_worker) as ex:
        for r in ex.map(_chain, jobs):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()
            log("chain %d %s gen1=%s gen2=%s" % (r["chain"], r["genome"], r["gen1"]["selected_schema"],
                                                r["gen2"]["selected_schema"]))


def _walk(a):
    T.init_worker()
    key, entries, f = a
    prov = a17.Prov({f["name"]: (f["body"], f["final"], f["init"])})
    a17.M.use_provider(prov)
    c = FR.Cell(prov, f["name"], 0, f["Q2_size"], label="GTC-score")
    r = walk.first_qualified(FR.KLib(entries), c, CAP, INS.qualifier(prov, f["name"], "v1a", "BOTH"))
    return {"lib": key, "family": f["name"], "result": r}


def stage_score(w=4):
    import hashlib
    plan = rd("GTC_PLAN.json")
    chains = rdl("GTC_CHAINS.jsonl")
    libs, jobs, index = {}, [], []

    def key(e):
        k = hashlib.sha256(json.dumps(e, sort_keys=True).encode()).hexdigest()[:16]
        libs.setdefault(k, e)
        return k
    P = key(FR.pristine().entries)
    for ch in chains:
        sc = plan["chains"][str(ch["chain"])]["roles"]["score"]
        for gen in ("gen1", "gen2"):
            k = key(ch[gen]["selected_entries"])
            for stt in ("DEV", "UNSEEN"):
                for f in sc[stt]:
                    index.append({"chain": ch["chain"], "genome": ch["genome"], "gen": gen, "stratum": stt,
                                  "family": f["name"], "lib": k})
                    jobs.append((k, f))
        for stt in ("DEV", "UNSEEN"):
            for f in sc[stt]:
                index.append({"chain": ch["chain"], "genome": "PRISTINE", "gen": "ref", "stratum": stt,
                              "family": f["name"], "lib": P})
                jobs.append((P, f))
    wr("GTC_SCORE_INDEX.json", {"index": index})
    done = {(x["lib"], x["family"]) for x in rdl("GTC_WALKS.jsonl")}
    uniq = {}
    for k, f in jobs:
        uniq.setdefault((k, f["name"]), (k, libs[k], f))
    todo = [v for kk, v in sorted(uniq.items()) if kk not in done]
    log("score walks %d todo %d" % (len(uniq), len(todo)))
    with open(OUT / "GTC_WALKS.jsonl", "a", encoding="utf-8") as fh, \
            ProcessPoolExecutor(max_workers=w, initializer=T.init_worker) as ex:
        for r in ex.map(_walk, todo, chunksize=2):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()
    log("score done")


def stage_report():
    """Frozen rules: T05_GTC_SPEC.md s4."""
    idx = rd("GTC_SCORE_INDEX.json")["index"]
    W = {(w["lib"], w["family"]): w["result"] for w in rdl("GTC_WALKS.jsonl")}
    val = {}
    for e in idx:
        r = W.get((e["lib"], e["family"]))
        k = (e["chain"], e["genome"], e["gen"], e["stratum"])
        val.setdefault(k, 0)
        val[k] += int(bool(r) and not r.get("censored", True))
    chains = sorted({e["chain"] for e in idx})
    tab, adv = {}, {}
    for g in GEN:
        for gen in ("gen1", "gen2"):
            for stt in ("DEV", "UNSEEN"):
                xs = [val.get((c, g, gen, stt), 0) for c in chains]
                tab["%s|%s|%s" % (g, gen, stt)] = xs
    for g in GEN[1:]:
        for gen in ("gen1", "gen2"):
            for stt in ("DEV", "UNSEEN"):
                adv["%s|%s|%s" % (g, gen, stt)] = [a - b for a, b in zip(tab["%s|%s|%s" % (g, gen, stt)],
                                                                         tab["g0|%s|%s" % (gen, stt)])]
    def beats_unseen(g):          # beats I_0 on UNSEEN at gen 2 in >= 3 of 4 chains, and in total
        a = adv["%s|gen2|UNSEEN" % g]
        return sum(1 for x in a if x > 0) >= 3 and sum(a) > 0
    def growth(g):                # (gen2 - gen1) advantage on UNSEEN > 0 in total
        return sum(adv["%s|gen2|UNSEEN" % g]) - sum(adv["%s|gen1|UNSEEN" % g]) > 0
    # genome variance share on UNSEEN gen2: between-genome variance / total (chains x genomes)
    import statistics
    M = [[tab["%s|gen2|UNSEEN" % g][i] for g in GEN] for i in range(len(chains))]
    allv = [x for row in M for x in row]
    gm = [statistics.fmean([M[i][j] for i in range(len(chains))]) for j in range(len(GEN))]
    tot = statistics.pvariance(allv) if len(set(allv)) > 1 else 0.0
    share = (statistics.pvariance(gm) / tot) if tot else 0.0
    g5_dev = sum(adv["g5|gen2|DEV"]) + sum(adv["g5|gen1|DEV"])
    g5_uns = sum(adv["g5|gen2|UNSEEN"]) + sum(adv["g5|gen1|UNSEEN"])
    overfit_seen = g5_dev > 0 and g5_uns < 0
    winners = [g for g in GEN[1:4] if beats_unseen(g) and growth(g)]
    floor = all(v == 0 for k, v in val.items() if k[1] in GEN)
    if floor:
        verdict = "INCONCLUSIVE_FLOOR"
    elif not overfit_seen:
        verdict = "INCONCLUSIVE_INSTRUMENT (planted overfitter g5 not seen)"
    elif winners and share >= 0.10:
        verdict = "GO"
    elif not any(beats_unseen(g) for g in GEN[1:4]) or not any(growth(g) for g in GEN[1:4]):
        verdict = "STOP (improver levers transfer-inert or one-shot only)"
    else:
        verdict = "INCONCLUSIVE"
    res = {"table": tab, "advantage_vs_g0": adv, "genome_variance_share_unseen_gen2": round(share, 3),
           "g5_dev_adv": g5_dev, "g5_unseen_adv": g5_uns, "overfit_seen": overfit_seen, "winners": winners,
           "verdict": verdict}
    wr("GTC_RESULT.json", res)
    log("verdict %s winners %s share %.3f g5 dev %+d unseen %+d" % (verdict, winners, share, g5_dev, g5_uns))
    return res


if __name__ == "__main__":
    st = sys.argv[1]
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    {"plan": stage_plan, "run": lambda: stage_run(w), "score": lambda: stage_score(w), "report": stage_report}[st]()
